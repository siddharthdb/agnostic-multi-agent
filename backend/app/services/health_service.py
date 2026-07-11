from sqlmodel import Session

from app.adapters.registry import get_adapter
from app.core.time import utcnow
from app.models.agent import AgentStatus
from app.schemas.agent import AgentHealthResult
from app.services.agent_service import get_agent


async def check_agent_health(session: Session, agent_id: str) -> AgentHealthResult:
    agent = get_agent(session, agent_id)
    adapter = get_adapter(agent.protocol)
    result = await adapter.health_check(agent)

    agent.status = AgentStatus.ACTIVE if result.success else AgentStatus.UNHEALTHY
    agent.updated_at = utcnow()
    session.add(agent)
    session.commit()

    return AgentHealthResult(
        agent_id=agent.id,
        status=agent.status,
        reachable=result.success,
        latency_ms=result.latency_ms,
        error=result.error,
    )
