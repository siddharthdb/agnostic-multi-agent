from app.models.agent import Agent, AgentStatus
from app.services.dag_validator import validate_definition


def make_agent(agent_id: str, status: AgentStatus = AgentStatus.ACTIVE) -> Agent:
    return Agent(id=agent_id, name=agent_id, endpoint_url="http://example.com/invoke", status=status)


AGENTS = {aid: make_agent(aid) for aid in ("a1", "a2", "a3")}


def test_valid_linear_workflow():
    definition = {
        "nodes": [{"id": "n1", "agent_id": "a1"}, {"id": "n2", "agent_id": "a2"}],
        "edges": [{"from": "n1", "to": "n2"}],
    }
    result = validate_definition(definition, AGENTS)
    assert result.valid
    assert result.errors == []
    assert result.topo_order == ["n1", "n2"]


def test_valid_branching_workflow():
    definition = {
        "nodes": [
            {"id": "n1", "agent_id": "a1"},
            {"id": "n2", "agent_id": "a2"},
            {"id": "n3", "agent_id": "a3"},
        ],
        "edges": [
            {"from": "n1", "to": "n2"},
            {
                "from": "n2",
                "to": "n3",
                "condition": {"field": "$.nodes.n2.risk_level", "op": "neq", "value": "high"},
            },
        ],
    }
    result = validate_definition(definition, AGENTS)
    assert result.valid
    assert result.topo_order == ["n1", "n2", "n3"]


def test_cyclic_workflow_rejected():
    definition = {
        "nodes": [{"id": "n1", "agent_id": "a1"}, {"id": "n2", "agent_id": "a2"}],
        "edges": [{"from": "n1", "to": "n2"}, {"from": "n2", "to": "n1"}],
    }
    result = validate_definition(definition, AGENTS)
    assert not result.valid
    assert any(e.code == "cycle_detected" for e in result.errors)


def test_dangling_edge_rejected():
    definition = {
        "nodes": [{"id": "n1", "agent_id": "a1"}],
        "edges": [{"from": "n1", "to": "n2"}],
    }
    result = validate_definition(definition, AGENTS)
    assert not result.valid
    assert any(e.code == "dangling_edge" for e in result.errors)


def test_no_entry_node_rejected():
    definition = {
        "nodes": [{"id": "n1", "agent_id": "a1"}, {"id": "n2", "agent_id": "a2"}],
        "edges": [{"from": "n1", "to": "n2"}, {"from": "n2", "to": "n1"}],
    }
    result = validate_definition(definition, AGENTS)
    assert not result.valid
    codes = {e.code for e in result.errors}
    assert "no_entry_node" in codes


def test_unknown_agent_reference_rejected():
    definition = {"nodes": [{"id": "n1", "agent_id": "does-not-exist"}], "edges": []}
    result = validate_definition(definition, AGENTS)
    assert not result.valid
    assert any(e.code == "unknown_agent" for e in result.errors)


def test_inactive_agent_is_warning_not_error():
    agents = dict(AGENTS)
    agents["a1"] = make_agent("a1", status=AgentStatus.INACTIVE)
    definition = {"nodes": [{"id": "n1", "agent_id": "a1"}], "edges": []}
    result = validate_definition(definition, agents)
    assert result.valid
    assert any(w.code == "inactive_agent" for w in result.warnings)


def test_invalid_condition_shape_rejected():
    definition = {
        "nodes": [{"id": "n1", "agent_id": "a1"}, {"id": "n2", "agent_id": "a2"}],
        "edges": [{"from": "n1", "to": "n2", "condition": {"field": "x"}}],
    }
    result = validate_definition(definition, AGENTS)
    assert not result.valid
    assert any(e.code == "invalid_condition" for e in result.errors)


def test_unsupported_condition_op_rejected():
    definition = {
        "nodes": [{"id": "n1", "agent_id": "a1"}, {"id": "n2", "agent_id": "a2"}],
        "edges": [
            {"from": "n1", "to": "n2", "condition": {"field": "x", "op": "bogus", "value": 1}}
        ],
    }
    result = validate_definition(definition, AGENTS)
    assert not result.valid
    assert any(e.code == "invalid_condition_op" for e in result.errors)


def test_empty_workflow_rejected():
    result = validate_definition({"nodes": [], "edges": []}, AGENTS)
    assert not result.valid
    assert any(e.code == "empty_workflow" for e in result.errors)


def test_diamond_shaped_dag_topo_order_waits_for_all_parents():
    definition = {
        "nodes": [
            {"id": "n1", "agent_id": "a1"},
            {"id": "n2", "agent_id": "a2"},
            {"id": "n3", "agent_id": "a3"},
            {"id": "n4", "agent_id": "a1"},
        ],
        "edges": [
            {"from": "n1", "to": "n2"},
            {"from": "n1", "to": "n3"},
            {"from": "n2", "to": "n4"},
            {"from": "n3", "to": "n4"},
        ],
    }
    result = validate_definition(definition, AGENTS)
    assert result.valid
    assert result.topo_order[0] == "n1"
    assert result.topo_order[-1] == "n4"
    assert set(result.topo_order) == {"n1", "n2", "n3", "n4"}
