from app.adapters.base import AgentAdapter
from app.adapters.rest_adapter import RestAdapter
from app.core.exceptions import UnsupportedProtocolError
from app.models.agent import Protocol

_ADAPTERS: dict[Protocol, type[AgentAdapter]] = {
    Protocol.REST: RestAdapter,
    # Protocol.A2A: A2aAdapter,   # add later, zero changes elsewhere
    # Protocol.MCP: McpAdapter,
    # Protocol.GRPC: GrpcAdapter,
}


def get_adapter(protocol: Protocol) -> AgentAdapter:
    cls = _ADAPTERS.get(protocol)
    if cls is None:
        raise UnsupportedProtocolError(str(protocol))
    return cls()
