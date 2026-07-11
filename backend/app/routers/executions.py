from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db import get_session
from app.schemas.execution import ExecutionDetail, ExecutionRead
from app.services import execution_service

router = APIRouter(prefix="/executions", tags=["executions"])


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
