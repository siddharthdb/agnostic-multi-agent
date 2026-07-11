from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.schemas.workflow import ValidationResult, WorkflowCreate, WorkflowRead, WorkflowUpdate
from app.services import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowRead, status_code=201)
def create_workflow(
    data: WorkflowCreate, session: Session = Depends(get_session)
) -> WorkflowRead:
    return workflow_service.create_workflow(session, data)


@router.get("", response_model=list[WorkflowRead])
def list_workflows(session: Session = Depends(get_session)) -> list[WorkflowRead]:
    return workflow_service.list_workflows(session)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(workflow_id: str, session: Session = Depends(get_session)) -> WorkflowRead:
    return workflow_service.get_workflow(session, workflow_id)


@router.put("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(
    workflow_id: str, data: WorkflowUpdate, session: Session = Depends(get_session)
) -> WorkflowRead:
    return workflow_service.update_workflow(session, workflow_id, data)


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: str, session: Session = Depends(get_session)) -> None:
    workflow_service.delete_workflow(session, workflow_id)


@router.post("/{workflow_id}/validate", response_model=ValidationResult)
def validate_workflow(workflow_id: str, session: Session = Depends(get_session)) -> ValidationResult:
    workflow = workflow_service.get_workflow(session, workflow_id)
    return workflow_service.validate_workflow_definition(session, workflow.definition)
