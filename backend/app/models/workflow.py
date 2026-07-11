from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Workflow(SQLModel, table=True):
    """`definition` shape: {"nodes": [{"id", "agent_id", "label", "input_mapping"}],
    "edges": [{"from", "to", "condition"}]}. Kept as a JSON blob (not normalized
    tables) so DAG structure can evolve without migrations."""

    id: str = Field(default_factory=lambda: f"wf_{uuid4().hex[:12]}", primary_key=True)
    name: str
    description: str = ""
    definition: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    version: int = 1
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
