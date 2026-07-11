# Agent Card schema

Loosely inspired by the A2A protocol's `agent-card.json` concept — a small metadata document
describing how to reach an agent, decoupled from the orchestrator's own code. Registered via
`POST /agents`; see `backend/app/schemas/agent.py` for the authoritative Pydantic definitions and
`backend/app/models/agent.py` for the persisted SQLModel table.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Server-generated (`agent_<hex12>`), not settable on create. |
| `name` | string | Required. |
| `description` | string | Optional, defaults to `""`. |
| `protocol` | `REST \| A2A \| MCP \| GRPC` | Resolves which `AgentAdapter` implementation handles this agent. Only `REST` is implemented today. |
| `endpoint_url` | string | Where `AgentAdapter.invoke` sends the request. |
| `auth_type` | `none \| api_key \| bearer` | Determines how `auth_config` is interpreted. |
| `auth_config` | object | `api_key` expects `{"header_name"?: string, "api_key": string}`; `bearer` expects `{"token": string}`. |
| `input_schema` | object (JSON Schema) | Advisory/documentation only — not enforced at invoke time in this MVP. |
| `output_schema` | object (JSON Schema) | Same. |
| `capability_tags` | string[] | Free-form tags for discovery/filtering (`GET /agents?capability_tag=...`). |
| `status` | `active \| inactive \| unhealthy` | Set manually or by `GET /agents/{id}/health`. `inactive`/missing agents referenced by a workflow are a validation *warning*, not a hard error — a workflow can be saved as a draft ahead of the agent going live. |
| `health_check_url` | string \| null | Defaults to `endpoint_url` if unset. |
| `created_at` / `updated_at` | datetime | Server-managed. |

## Example — CAM stub's card (`stub_agents/agent_cards/cam.json`)

```json
{
  "name": "CAM",
  "description": "Customer Account Manager (stub)",
  "protocol": "REST",
  "endpoint_url": "http://localhost:9001/invoke",
  "auth_type": "none",
  "auth_config": {},
  "input_schema": {
    "type": "object",
    "required": ["customer_id"],
    "properties": { "customer_id": { "type": "string" } }
  },
  "output_schema": {
    "type": "object",
    "properties": { "status": { "type": "string" }, "account_tier": { "type": "string" } }
  },
  "capability_tags": ["account", "customer-lookup"],
  "health_check_url": "http://localhost:9001/health"
}
```

## Onboarding a new agent (real or stub)

1. Write the Agent Card JSON for the agent (see above).
2. `POST /agents` with that JSON (or add it to `stub_agents/agent_cards/` and run
   `scripts/seed_agents.py` for a repeatable seed).
3. Reference the returned `id` as a node's `agent_id` in a workflow `definition`.

No execution-engine code changes are required — this is the entire point of the Agent Card +
adapter pattern (see [architecture.md](architecture.md)).

## Adding a new protocol

1. Implement `class XAdapter(AgentAdapter)` in `backend/app/adapters/` with `invoke` and
   `health_check`.
2. Register it in `backend/app/adapters/registry.py`'s `_ADAPTERS` map.
3. Register agents with `protocol: "X"`.

Nothing else changes — `execution_service.py` and `health_service.py` only ever call
`get_adapter(card.protocol)`.
