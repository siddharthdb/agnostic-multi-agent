from abc import ABC, abstractmethod
from typing import Any

from app.adapters.result import AdapterResult
from app.models.agent import Agent


class AgentAdapter(ABC):
    """Protocol-specific transport for invoking an agent described by its
    Agent Card. The execution engine only ever talks to this interface, so
    onboarding a new protocol (A2A, MCP, gRPC, ...) means adding an
    implementation here and registering it in adapters/registry.py --
    no changes to the execution engine, routers, or models."""

    @abstractmethod
    async def invoke(
        self, card: Agent, payload: dict[str, Any], *, timeout_s: float = 30.0
    ) -> AdapterResult:
        ...

    @abstractmethod
    async def health_check(self, card: Agent, *, timeout_s: float = 5.0) -> AdapterResult:
        ...
