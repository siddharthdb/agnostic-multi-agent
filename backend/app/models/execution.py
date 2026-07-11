from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class ExecutionStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class Execution(SQLModel, table=True):
    """`node_states` is a JSON dict keyed by node_id holding *current* per-node
    state (status/input/output/error/timestamps) — cheap to overwrite on each
    transition. The append-only event history lives in ExecutionEvent instead,
    so a crash mid-run still leaves a replayable log even though node_states
    only reflects the latest snapshot."""

    id: str = Field(default_factory=lambda: f"exec_{uuid4().hex[:12]}", primary_key=True)
    workflow_id: str = Field(foreign_key="workflow.id", index=True)
    status: ExecutionStatus = ExecutionStatus.QUEUED
    input_payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    node_states: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    cancel_requested: bool = False
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)


class ExecutionEvent(SQLModel, table=True):
    """Append-only event log, one row per event, ordered by `seq` within an
    execution. Kept as its own table (not a JSON array on Execution) so it can
    be queried/replayed for SSE reconnects without a read-modify-write race."""

    id: int | None = Field(default=None, primary_key=True)
    execution_id: str = Field(foreign_key="execution.id", index=True)
    seq: int
    event_type: str
    node_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow)
