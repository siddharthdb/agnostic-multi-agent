"""Pure functions for validating a workflow `definition` JSON blob:
{"nodes": [{"id", "agent_id", ...}], "edges": [{"from", "to", "condition"}]}.
Run at workflow save-time and via POST /workflows/{id}/validate, and reused
by the frontend's ValidationPanel (same error/warning shape over the wire).
"""

from typing import Any

from app.models.agent import Agent, AgentStatus
from app.schemas.workflow import ValidationIssue, ValidationResult

SUPPORTED_CONDITION_OPS = {"eq", "neq", "gt", "gte", "lt", "lte", "in", "contains"}


def validate_definition(
    definition: dict[str, Any], agents_by_id: dict[str, Agent]
) -> ValidationResult:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    nodes = definition.get("nodes", [])
    edges = definition.get("edges", [])
    node_ids = [n.get("id") for n in nodes]
    node_id_set = set(node_ids)

    if not nodes:
        errors.append(ValidationIssue(code="empty_workflow", message="Workflow has no nodes"))
    if len(node_ids) != len(node_id_set):
        errors.append(
            ValidationIssue(code="duplicate_node_id", message="Duplicate node ids in definition")
        )

    for node in nodes:
        node_id = node.get("id")
        agent_id = node.get("agent_id")
        agent = agents_by_id.get(agent_id)
        if agent is None:
            errors.append(
                ValidationIssue(
                    code="unknown_agent",
                    message=f"Node '{node_id}' references unknown agent '{agent_id}'",
                    node_id=node_id,
                )
            )
        elif agent.status != AgentStatus.ACTIVE:
            warnings.append(
                ValidationIssue(
                    code="inactive_agent",
                    message=f"Node '{node_id}' references agent '{agent_id}' which is not active",
                    node_id=node_id,
                )
            )

    adjacency: dict[str, list[dict[str, Any]]] = {}
    incoming: set[str] = set()
    for edge in edges:
        frm, to = edge.get("from"), edge.get("to")
        if frm not in node_id_set:
            errors.append(
                ValidationIssue(
                    code="dangling_edge",
                    message=f"Edge references unknown source node '{frm}'",
                    edge=edge,
                )
            )
        if to not in node_id_set:
            errors.append(
                ValidationIssue(
                    code="dangling_edge",
                    message=f"Edge references unknown target node '{to}'",
                    edge=edge,
                )
            )
        else:
            incoming.add(to)

        condition = edge.get("condition")
        if condition is not None:
            if not isinstance(condition, dict) or not {"field", "op", "value"} <= condition.keys():
                errors.append(
                    ValidationIssue(
                        code="invalid_condition",
                        message="Condition must have field/op/value keys",
                        edge=edge,
                    )
                )
            elif condition["op"] not in SUPPORTED_CONDITION_OPS:
                errors.append(
                    ValidationIssue(
                        code="invalid_condition_op",
                        message=f"Unsupported condition op '{condition['op']}'",
                        edge=edge,
                    )
                )

        adjacency.setdefault(frm, []).append(edge)

    entry_nodes = [n for n in node_ids if n not in incoming]
    if nodes and not entry_nodes:
        errors.append(
            ValidationIssue(
                code="no_entry_node",
                message="Workflow has no entry node (every node has an incoming edge)",
            )
        )

    cycle_path = _detect_cycle(node_id_set, adjacency)
    if cycle_path:
        errors.append(
            ValidationIssue(
                code="cycle_detected", message=f"Cycle detected: {' -> '.join(cycle_path)}"
            )
        )

    topo_order: list[str] = []
    if not errors:
        topo_order = _topological_order(node_id_set, adjacency)
        unreachable = node_id_set - set(topo_order)
        for node_id in unreachable:
            warnings.append(
                ValidationIssue(
                    code="unreachable_node",
                    message=f"Node '{node_id}' is unreachable from any entry node",
                    node_id=node_id,
                )
            )

    return ValidationResult(
        valid=len(errors) == 0, errors=errors, warnings=warnings, topo_order=topo_order
    )


def _detect_cycle(
    node_ids: set[str], adjacency: dict[str, list[dict[str, Any]]]
) -> list[str] | None:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in node_ids}
    path: list[str] = []

    def dfs(node: str) -> list[str] | None:
        color[node] = GRAY
        path.append(node)
        for edge in adjacency.get(node, []):
            nxt = edge.get("to")
            if nxt not in color:
                continue  # dangling edge, already reported separately
            if color[nxt] == GRAY:
                return path[path.index(nxt):] + [nxt]
            if color[nxt] == WHITE:
                result = dfs(nxt)
                if result:
                    return result
        path.pop()
        color[node] = BLACK
        return None

    for node in node_ids:
        if color[node] == WHITE:
            result = dfs(node)
            if result:
                return result
    return None


def _topological_order(
    node_ids: set[str], adjacency: dict[str, list[dict[str, Any]]]
) -> list[str]:
    """Kahn's algorithm so nodes with multiple parents wait until all
    parents are processed (a plain multi-source BFS would not guarantee
    that for diamond-shaped DAGs)."""
    in_degree = {n: 0 for n in node_ids}
    for edges in adjacency.values():
        for edge in edges:
            to = edge.get("to")
            if to in in_degree:
                in_degree[to] += 1

    queue = [n for n in node_ids if in_degree[n] == 0]
    order: list[str] = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for edge in adjacency.get(node, []):
            to = edge.get("to")
            if to not in in_degree:
                continue
            in_degree[to] -= 1
            if in_degree[to] == 0:
                queue.append(to)
    return order
