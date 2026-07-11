from typing import Any

from sqlmodel import Session, select

from app.core.exceptions import NotFoundError, ValidationFailedError
from app.core.time import utcnow
from app.models.agent import Agent
from app.models.workflow import Workflow
from app.schemas.workflow import ValidationResult, WorkflowCreate, WorkflowUpdate
from app.services.dag_validator import validate_definition


def _agents_by_id(session: Session) -> dict[str, Agent]:
    return {a.id: a for a in session.exec(select(Agent)).all()}


def validate_workflow_definition(session: Session, definition: dict[str, Any]) -> ValidationResult:
    return validate_definition(definition, _agents_by_id(session))


def create_workflow(session: Session, data: WorkflowCreate) -> Workflow:
    result = validate_workflow_definition(session, data.definition)
    if not result.valid:
        raise ValidationFailedError([e.model_dump() for e in result.errors])
    workflow = Workflow(**data.model_dump())
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


def list_workflows(session: Session) -> list[Workflow]:
    return list(session.exec(select(Workflow)).all())


def get_workflow(session: Session, workflow_id: str) -> Workflow:
    workflow = session.get(Workflow, workflow_id)
    if workflow is None:
        raise NotFoundError("Workflow", workflow_id)
    return workflow


def update_workflow(session: Session, workflow_id: str, data: WorkflowUpdate) -> Workflow:
    workflow = get_workflow(session, workflow_id)
    updates = data.model_dump(exclude_unset=True)
    if "definition" in updates:
        result = validate_workflow_definition(session, updates["definition"])
        if not result.valid:
            raise ValidationFailedError([e.model_dump() for e in result.errors])
        workflow.version += 1
    for field, value in updates.items():
        setattr(workflow, field, value)
    workflow.updated_at = utcnow()
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


def delete_workflow(session: Session, workflow_id: str) -> None:
    workflow = get_workflow(session, workflow_id)
    session.delete(workflow)
    session.commit()
