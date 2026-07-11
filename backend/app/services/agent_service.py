from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.core.time import utcnow
from app.models.agent import Agent
from app.models.workflow import Workflow, WorkflowStatus
from app.schemas.agent import AgentCreate, AgentUpdate


def create_agent(session: Session, data: AgentCreate) -> Agent:
    agent = Agent(**data.model_dump())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def list_agents(
    session: Session, *, status: str | None = None, capability_tag: str | None = None
) -> list[Agent]:
    agents = list(session.exec(select(Agent)).all())
    if status is not None:
        agents = [a for a in agents if a.status == status]
    if capability_tag is not None:
        agents = [a for a in agents if capability_tag in a.capability_tags]
    return agents


def get_agent(session: Session, agent_id: str) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError("Agent", agent_id)
    return agent


def update_agent(session: Session, agent_id: str, data: AgentUpdate) -> Agent:
    agent = get_agent(session, agent_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    agent.updated_at = utcnow()
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def delete_agent(session: Session, agent_id: str) -> None:
    agent = get_agent(session, agent_id)
    referencing = session.exec(
        select(Workflow).where(Workflow.status == WorkflowStatus.PUBLISHED)
    ).all()
    for workflow in referencing:
        node_agent_ids = {n.get("agent_id") for n in workflow.definition.get("nodes", [])}
        if agent_id in node_agent_ids:
            raise ConflictError(
                f"Agent '{agent_id}' is referenced by published workflow '{workflow.id}'"
            )
    session.delete(agent)
    session.commit()
