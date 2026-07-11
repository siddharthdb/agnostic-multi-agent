"""Minimal JSONPath-lite resolver against the execution context
{"input": <execution input>, "nodes": {<node_id>: <node output>, ...}}.
A full JSONPath library is unneeded given this constrained, known shape."""

from typing import Any

_OPS = {
    "eq": lambda a, b: a == b,
    "neq": lambda a, b: a != b,
    "gt": lambda a, b: a > b,
    "gte": lambda a, b: a >= b,
    "lt": lambda a, b: a < b,
    "lte": lambda a, b: a <= b,
    "in": lambda a, b: a in b,
    "contains": lambda a, b: b in a,
}


def resolve_jsonpath(path: str, context: dict[str, Any]) -> Any:
    parts = path.lstrip("$").strip(".").split(".")
    value: Any = context
    for part in parts:
        if not part:
            continue
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def evaluate_condition(condition: dict[str, Any] | None, context: dict[str, Any]) -> bool:
    if condition is None:
        return True
    value = resolve_jsonpath(condition["field"], context)
    return _OPS[condition["op"]](value, condition["value"])


def resolve_input_mapping(mapping: dict[str, str], context: dict[str, Any]) -> dict[str, Any]:
    return {key: resolve_jsonpath(path, context) for key, path in mapping.items()}
