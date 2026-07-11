from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db import get_session
from app.schemas.agent import AgentCreate, AgentHealthResult, AgentRead, AgentUpdate
from app.services import agent_service, health_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentRead, status_code=201)
def create_agent(data: AgentCreate, session: Session = Depends(get_session)) -> AgentRead:
    return agent_service.create_agent(session, data)


@router.get("", response_model=list[AgentRead])
def list_agents(
    status: str | None = Query(default=None),
    capability_tag: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[AgentRead]:
    return agent_service.list_agents(session, status=status, capability_tag=capability_tag)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: str, session: Session = Depends(get_session)) -> AgentRead:
    return agent_service.get_agent(session, agent_id)


@router.put("/{agent_id}", response_model=AgentRead)
def update_agent(
    agent_id: str, data: AgentUpdate, session: Session = Depends(get_session)
) -> AgentRead:
    return agent_service.update_agent(session, agent_id, data)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: str, session: Session = Depends(get_session)) -> None:
    agent_service.delete_agent(session, agent_id)


@router.get("/{agent_id}/health", response_model=AgentHealthResult)
async def check_agent_health(
    agent_id: str, session: Session = Depends(get_session)
) -> AgentHealthResult:
    return await health_service.check_agent_health(session, agent_id)
