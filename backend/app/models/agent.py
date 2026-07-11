from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class Protocol(str, Enum):
    REST = "REST"
    A2A = "A2A"
    MCP = "MCP"
    GRPC = "GRPC"


class AuthType(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNHEALTHY = "unhealthy"


class Agent(SQLModel, table=True):
    id: str = Field(default_factory=lambda: f"agent_{uuid4().hex[:12]}", primary_key=True)
    name: str
    description: str = ""
    protocol: Protocol = Protocol.REST
    endpoint_url: str
    auth_type: AuthType = AuthType.NONE
    auth_config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    input_schema: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_schema: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    capability_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: AgentStatus = AgentStatus.ACTIVE
    health_check_url: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
