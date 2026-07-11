# Architecture

## Problem

Three independent agents (CAM, FSR, BSA) need to be chained into workflows without hard-coding
each one's integration details into an orchestrator. The industry pattern for this (A2A protocol,
Microsoft Agent Framework, gateway products like TrueFoundry) is to decouple *agent discovery*
from *orchestration logic* via a registry + small metadata document ("Agent Card") describing how
to reach an agent. The orchestrator only ever talks to that document, never to the agent directly.

## Control plane

```
Frontend (React + Vite) — Agent CRUD, Workflow DAG Builder, Execution Monitor
        | REST/JSON + SSE
Control Plane API (FastAPI)
  |- Agent Registry Service    (CRUD + health check)
  |- Workflow Registry Service (CRUD + DAG validation: cycles, dangling refs, conditions)
  \- Execution Service         (async orchestration loop, incremental state, event log, SSE)
        | AgentAdapter.invoke(card, payload)  <- protocol-agnostic seam
   CAM stub (:9001) / FSR stub (:9002) / BSA stub (:9003)
```

Every agent is represented by an **Agent Card**: `{id, name, protocol, endpoint_url, auth_type,
auth_config, input_schema, output_schema, capability_tags, status, health_check_url, ...}`. See
[agent-card-schema.md](agent-card-schema.md) for the full field reference.

The Execution Service never branches on which agent it's calling. It only ever does:

```python
adapter = get_adapter(card.protocol)
result = await adapter.invoke(card, payload)
```

`backend/app/adapters/registry.py` maps `Protocol -> Adapter class`. Today only `RestAdapter`
exists. Adding A2A/MCP/gRPC support later means writing `A2aAdapter(AgentAdapter)` etc. and
registering it — zero changes to the execution engine, routers, or models. This is the concrete
mechanism behind "onboard a new agent by registering a card."

## Data model

- **Agent** — the Agent Card, persisted.
- **Workflow** — `{name, definition, version, status}`. `definition` is a JSON blob
  (`{nodes: [...], edges: [...]}`) rather than normalized tables, so the DAG shape can evolve
  without migrations. Validated by `backend/app/services/dag_validator.py` at save-time and via
  `POST /workflows/{id}/validate`.
- **Execution** — one row per run. `node_states` is a JSON dict of *current* per-node state
  (cheap to overwrite on every transition).
- **ExecutionEvent** — a separate append-only table, one row per event, ordered by `seq`. Kept
  separate from `Execution` (not a JSON array column) specifically so a crash mid-run still leaves
  a queryable, replayable event history, and so `GET /executions/{id}/events` (SSE) can replay
  from any point without a read-modify-write race against the writer.

## Execution engine

`backend/app/services/execution_service.py` runs each execution as an `asyncio.create_task`
kicked off from `POST /workflows/{id}/execute` — single-process, in-memory task tracking
(`RUNNING_TASKS`), not Celery/RQ. This is an intentional MVP simplification: **executions are not
durable across a backend restart.** `sweep_stale_executions()` runs at startup and marks any
execution still `QUEUED`/`RUNNING` as `FAILED` with an `"interrupted by restart"` event, since
`RUNNING_TASKS` is always empty right after a restart.

The loop resolves each node's `input_mapping` against `{input: <execution input>, nodes: {<node_id>:
<output>, ...}}` using a minimal JSONPath-lite resolver (`services/condition_eval.py`), invokes the
agent via its adapter, and evaluates each outgoing edge's `condition` the same way to decide
whether to enqueue or skip the downstream node. On the first node failure, the whole execution
fails fast — no retries, no partial-success semantics in this MVP.

Every node transition and every event is an immediate DB commit — crash-inspectable, not batched.
Events are also pushed to an in-process `event_bus` (`services/event_bus.py`, an `asyncio.Queue`
per execution) for live SSE delivery; `GET /executions/{id}/events` replays persisted events first,
then switches to live delivery, closing automatically after a terminal event.

Cancellation is cooperative: `POST /executions/{id}/cancel` sets a `cancel_requested` DB column,
checked at the top of each loop iteration. An in-flight adapter call is allowed to finish rather
than hard-aborted, avoiding half-applied side effects on the external agent.

## Frontend

React Flow (`@xyflow/react`) powers the workflow DAG builder (`frontend/src/components/workflow-builder/DagCanvas.tsx`).
Agents are dragged from a palette onto the canvas; connecting handles creates edges; clicking an
edge opens an inline condition editor. `definitionToFlow`/`flowToDefinition` in that file are the
two functions responsible for lossless round-tripping between the backend's JSON `definition` and
React Flow's node/edge state (including `input_mapping`, which has no dedicated editor UI in this
MVP but is preserved through load/save so existing workflows aren't silently truncated).

The execution monitor (`ExecutionDetailPage`) combines a live SSE event log (`hooks/useSse.ts`)
with a polling fallback (`hooks/usePolling.ts`) that kicks in whenever SSE isn't connected on an
active execution — the page re-fetches the full execution (source of truth for `node_states` and
`status`) on every new SSE event rather than deriving state client-side from the log alone.

## Known MVP limitations

- Executions are not durable across a backend process restart (no external job queue).
- No retries or partial-success semantics on node failure — first failure fails the whole run.
- `event_bus` is in-process only; a multi-instance deployment would need a shared broker (e.g.
  Redis pub/sub) for SSE to work across replicas.
- `input_mapping` has no dedicated editor in the DAG builder UI yet (existing mappings are
  preserved through save, just not editable visually).
- SQLite for local dev; see [adr/0001-db-choice.md](adr/0001-db-choice.md) for the Postgres path.
