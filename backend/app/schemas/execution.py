from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.execution import ExecutionStatus


class ExecutionRead(BaseModel):
    id: str
    workflow_id: str
    status: ExecutionStatus
    input_payload: dict[str, Any]
    node_states: dict[str, Any]
    cancel_requested: bool
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime


class EventOut(BaseModel):
    seq: int
    event_type: str
    node_id: str | None
    payload: dict[str, Any]
    created_at: datetime


class ExecutionDetail(ExecutionRead):
    event_log: list[EventOut] = []
