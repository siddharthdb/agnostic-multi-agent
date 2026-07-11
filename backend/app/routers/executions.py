import asyncio
import json
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.db import engine, get_session
from app.schemas.execution import ExecutionDetail, ExecutionRead
from app.services import execution_service
from app.services.event_bus import event_bus

router = APIRouter(prefix="/executions", tags=["executions"])

TERMINAL_EVENT_TYPES = {"execution_completed", "execution_failed", "execution_cancelled"}


@router.get("", response_model=list[ExecutionRead])
def list_executions(
    workflow_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[ExecutionRead]:
    return execution_service.list_executions(session, workflow_id=workflow_id, status=status)


@router.get("/{execution_id}", response_model=ExecutionDetail)
def get_execution(execution_id: str, session: Session = Depends(get_session)) -> ExecutionDetail:
    execution = execution_service.get_execution(session, execution_id)
    events = execution_service.list_execution_events(session, execution_id)
    return ExecutionDetail(**execution.model_dump(), event_log=[e.model_dump() for e in events])


@router.post("/{execution_id}/cancel", response_model=ExecutionRead)
def cancel_execution(execution_id: str, session: Session = Depends(get_session)) -> ExecutionRead:
    return execution_service.request_cancel(session, execution_id)


@router.get("/{execution_id}/events")
async def stream_execution_events(
    execution_id: str,
    request: Request,
    since: int = Query(default=-1),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    execution_service.get_execution(session, execution_id)  # 404s before streaming starts

    # Subscribe before reading persisted events so nothing published in the
    # gap between the snapshot read and the live loop is lost; last_seq
    # dedupes anything the queue and the snapshot both delivered.
    queue = event_bus.subscribe(execution_id)

    async def event_generator():
        last_seq = since
        try:
            with Session(engine) as replay_session:
                persisted = execution_service.list_execution_events(
                    replay_session, execution_id, since_seq=since
                )
            for event in persisted:
                last_seq = event.seq
                yield _format_sse(
                    {
                        "seq": event.seq,
                        "event_type": event.event_type,
                        "node_id": event.node_id,
                        "payload": event.payload,
                        "created_at": event.created_at.isoformat(),
                    }
                )
                if event.event_type in TERMINAL_EVENT_TYPES:
                    return

            while True:
                if await request.is_disconnected():
                    return
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                if event["seq"] <= last_seq:
                    continue
                last_seq = event["seq"]
                yield _format_sse(event)
                if event["event_type"] in TERMINAL_EVENT_TYPES:
                    return
        finally:
            event_bus.unsubscribe(execution_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _format_sse(event: dict[str, Any]) -> str:
    return f"event: {event['event_type']}\ndata: {json.dumps(event)}\n\n"
