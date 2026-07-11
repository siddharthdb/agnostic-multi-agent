from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.workflow import WorkflowStatus


class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    definition: dict[str, Any] = {"nodes": [], "edges": []}
    status: WorkflowStatus = WorkflowStatus.DRAFT


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    definition: dict[str, Any] | None = None
    status: WorkflowStatus | None = None


class WorkflowRead(BaseModel):
    id: str
    name: str
    description: str
    definition: dict[str, Any]
    version: int
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime


class ValidationIssue(BaseModel):
    code: str
    message: str
    node_id: str | None = None
    edge: dict[str, Any] | None = None


class ValidationResult(BaseModel):
    valid: bool
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    topo_order: list[str] = []


class ExecuteRequest(BaseModel):
    input_payload: dict[str, Any] = {}
