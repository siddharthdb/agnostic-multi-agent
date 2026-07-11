from sqlmodel import Session

from app.db import create_db_and_tables, engine
from app.models.execution import Execution, ExecutionStatus
from app.models.workflow import Workflow
from app.services.execution_service import sweep_stale_executions


def test_sweep_marks_stuck_running_execution_as_failed():
    create_db_and_tables()
    with Session(engine) as session:
        workflow = Workflow(name="wf", definition={"nodes": [], "edges": []})
        session.add(workflow)
        session.commit()
        session.refresh(workflow)

        stuck = Execution(workflow_id=workflow.id, status=ExecutionStatus.RUNNING)
        session.add(stuck)
        session.commit()
        session.refresh(stuck)
        stuck_id = stuck.id

    swept = sweep_stale_executions()
    assert swept >= 1

    with Session(engine) as session:
        reloaded = session.get(Execution, stuck_id)
        assert reloaded.status == ExecutionStatus.FAILED
        assert reloaded.ended_at is not None
