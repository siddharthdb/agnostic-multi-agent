from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.agent import AgentStatus, AuthType, Protocol


class AgentCreate(BaseModel):
    name: str
    description: str = ""
    protocol: Protocol = Protocol.REST
    endpoint_url: str
    auth_type: AuthType = AuthType.NONE
    auth_config: dict[str, Any] = {}
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    capability_tags: list[str] = []
    status: AgentStatus = AgentStatus.ACTIVE
    health_check_url: str | None = None


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    protocol: Protocol | None = None
    endpoint_url: str | None = None
    auth_type: AuthType | None = None
    auth_config: dict[str, Any] | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    capability_tags: list[str] | None = None
    status: AgentStatus | None = None
    health_check_url: str | None = None


class AgentRead(BaseModel):
    id: str
    name: str
    description: str
    protocol: Protocol
    endpoint_url: str
    auth_type: AuthType
    auth_config: dict[str, Any]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    capability_tags: list[str]
    status: AgentStatus
    health_check_url: str | None
    created_at: datetime
    updated_at: datetime


class AgentHealthResult(BaseModel):
    agent_id: str
    status: AgentStatus
    reachable: bool
    latency_ms: float | None = None
    error: str | None = None
