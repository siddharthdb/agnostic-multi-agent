import asyncio
from typing import Any

from sqlmodel import Session, select

from app.adapters.registry import get_adapter
from app.adapters.result import AdapterResult
from app.core.exceptions import NotFoundError
from app.core.time import utcnow
from app.db import engine
from app.models.agent import Agent
from app.models.execution import Execution, ExecutionEvent, ExecutionStatus, NodeStatus
from app.models.workflow import Workflow
from app.services.condition_eval import evaluate_condition, resolve_input_mapping
from app.services.event_bus import event_bus
from app.services.workflow_service import get_workflow

# Tracks in-flight background tasks so a sweep at startup can tell a truly
# crashed execution (task gone, status still RUNNING) apart from one still
# legitimately in progress.
RUNNING_TASKS: dict[str, asyncio.Task] = {}


async def start_execution(
    session: Session, workflow_id: str, input_payload: dict[str, Any]
) -> Execution:
    workflow = get_workflow(session, workflow_id)

    execution = Execution(
        workflow_id=workflow.id, input_payload=input_payload, status=ExecutionStatus.QUEUED
    )
    session.add(execution)
    session.commit()
    session.refresh(execution)

    task = asyncio.create_task(run_execution(execution.id))
    RUNNING_TASKS[execution.id] = task
    task.add_done_callback(lambda _t, eid=execution.id: RUNNING_TASKS.pop(eid, None))
    return execution


async def run_execution(execution_id: str) -> None:
    with Session(engine) as session:
        execution = session.get(Execution, execution_id)
        workflow = session.get(Workflow, execution.workflow_id)

        nodes_by_id = {n["id"]: n for n in workflow.definition.get("nodes", [])}
        adjacency: dict[str, list[dict[str, Any]]] = {}
        incoming: set[str] = set()
        for edge in workflow.definition.get("edges", []):
            adjacency.setdefault(edge["from"], []).append(edge)
            incoming.add(edge["to"])
        entry_nodes = [n for n in nodes_by_id if n not in incoming]

        seq = _next_seq(session, execution_id)

        execution.status = ExecutionStatus.RUNNING
        execution.started_at = utcnow()
        session.add(execution)
        session.commit()
        seq = _emit_event(session, execution_id, seq, "execution_started", None, {})

        context: dict[str, Any] = {"input": execution.input_payload, "nodes": {}}
        queue: list[str] = list(entry_nodes)

        while queue:
            session.refresh(execution)
            if execution.cancel_requested:
                execution.status = ExecutionStatus.CANCELLED
                execution.ended_at = utcnow()
                session.add(execution)
                session.commit()
                _emit_event(session, execution_id, seq, "execution_cancelled", None, {})
                return

            node_id = queue.pop(0)
            node = nodes_by_id[node_id]

            _update_node_state(
                session, execution, node_id, status=NodeStatus.RUNNING.value,
                started_at=utcnow().isoformat(),
            )
            seq = _emit_event(session, execution_id, seq, "node_started", node_id, {})

            agent = session.get(Agent, node["agent_id"])
            if agent is None:
                result = AdapterResult(
                    success=False, error=f"agent '{node['agent_id']}' not found", latency_ms=0
                )
            else:
                payload = resolve_input_mapping(node.get("input_mapping", {}), context)
                result = await get_adapter(agent.protocol).invoke(agent, payload)

            if result.success:
                _update_node_state(
                    session, execution, node_id, status=NodeStatus.SUCCEEDED.value,
                    output=result.output, ended_at=utcnow().isoformat(),
                )
                context["nodes"][node_id] = result.output
                seq = _emit_event(
                    session, execution_id, seq, "node_completed", node_id,
                    {"output": result.output},
                )
            else:
                _update_node_state(
                    session, execution, node_id, status=NodeStatus.FAILED.value,
                    error=result.error, ended_at=utcnow().isoformat(),
                )
                execution.status = ExecutionStatus.FAILED
                execution.ended_at = utcnow()
                session.add(execution)
                session.commit()
                seq = _emit_event(
                    session, execution_id, seq, "node_failed", node_id, {"error": result.error}
                )
                _emit_event(session, execution_id, seq, "execution_failed", node_id, {})
                return

            for edge in adjacency.get(node_id, []):
                to = edge["to"]
                if evaluate_condition(edge.get("condition"), context):
                    queue.append(to)
                else:
                    _update_node_state(session, execution, to, status=NodeStatus.SKIPPED.value)
                    seq = _emit_event(
                        session, execution_id, seq, "edge_skipped", to, {"from": node_id}
                    )

        execution.status = ExecutionStatus.COMPLETED
        execution.ended_at = utcnow()
        session.add(execution)
        session.commit()
        _emit_event(session, execution_id, seq, "execution_completed", None, {})


def _update_node_state(session: Session, execution: Execution, node_id: str, **fields: Any) -> None:
    node_states = dict(execution.node_states)
    node_states[node_id] = {**node_states.get(node_id, {}), **fields}
    execution.node_states = node_states
    session.add(execution)
    session.commit()
    session.refresh(execution)


def _next_seq(session: Session, execution_id: str) -> int:
    last = session.exec(
        select(ExecutionEvent.seq)
        .where(ExecutionEvent.execution_id == execution_id)
        .order_by(ExecutionEvent.seq.desc())
    ).first()
    return (last + 1) if last is not None else 0


def _emit_event(
    session: Session,
    execution_id: str,
    seq: int,
    event_type: str,
    node_id: str | None,
    payload: dict[str, Any],
) -> int:
    event = ExecutionEvent(
        execution_id=execution_id, seq=seq, event_type=event_type, node_id=node_id, payload=payload
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    event_bus.publish(
        execution_id,
        {
            "seq": event.seq,
            "event_type": event.event_type,
            "node_id": event.node_id,
            "payload": event.payload,
            "created_at": event.created_at.isoformat(),
        },
    )
    return seq + 1


def get_execution(session: Session, execution_id: str) -> Execution:
    execution = session.get(Execution, execution_id)
    if execution is None:
        raise NotFoundError("Execution", execution_id)
    return execution


def list_executions(
    session: Session, *, workflow_id: str | None = None, status: str | None = None
) -> list[Execution]:
    executions = list(session.exec(select(Execution)).all())
    if workflow_id is not None:
        executions = [e for e in executions if e.workflow_id == workflow_id]
    if status is not None:
        executions = [e for e in executions if e.status == status]
    return executions


def list_execution_events(
    session: Session, execution_id: str, since_seq: int = -1
) -> list[ExecutionEvent]:
    return list(
        session.exec(
            select(ExecutionEvent)
            .where(ExecutionEvent.execution_id == execution_id, ExecutionEvent.seq > since_seq)
            .order_by(ExecutionEvent.seq)
        ).all()
    )


def request_cancel(session: Session, execution_id: str) -> Execution:
    execution = get_execution(session, execution_id)
    if execution.status in (ExecutionStatus.QUEUED, ExecutionStatus.RUNNING):
        execution.cancel_requested = True
        session.add(execution)
        session.commit()
        session.refresh(execution)
    return execution


def sweep_stale_executions() -> int:
    """Startup-time cleanup: RUNNING_TASKS is always empty right after a
    process restart, so any execution still QUEUED/RUNNING at startup could
    not have a live task backing it -- it was interrupted by a crash or
    restart. Mark it FAILED instead of leaving it stuck forever."""
    with Session(engine) as session:
        stale = list(
            session.exec(
                select(Execution).where(
                    Execution.status.in_([ExecutionStatus.QUEUED, ExecutionStatus.RUNNING])
                )
            ).all()
        )
        for execution in stale:
            execution.status = ExecutionStatus.FAILED
            execution.ended_at = utcnow()
            session.add(execution)
        session.commit()

        for execution in stale:
            seq = _next_seq(session, execution.id)
            _emit_event(
                session, execution.id, seq, "execution_failed", None,
                {"error": "execution interrupted by restart"},
            )
    return len(stale)
