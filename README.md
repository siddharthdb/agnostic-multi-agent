# Agnostic Multi-Agent Orchestrator

A control plane for registering agents behind a protocol-agnostic **Agent Card**, wiring them
into DAG workflows, and running/observing those workflows live. MVP built around three demo
agents (CAM, FSR, BSA) chained into a customer-onboarding-style workflow.

```
Frontend (React + Vite) — Agent CRUD, Workflow DAG Builder, Execution Monitor
        | REST/JSON + SSE
Control Plane API (FastAPI) — Agent Registry, Workflow Registry, Execution engine
        | AgentAdapter.invoke(card, payload)  <- protocol-agnostic seam
   CAM stub (:9001) / FSR stub (:9002) / BSA stub (:9003)
```

See [docs/architecture.md](docs/architecture.md) for the full design (data model, execution
engine, SSE event log, known MVP limitations) and [docs/agent-card-schema.md](docs/agent-card-schema.md)
for how to onboard a new agent or protocol.

## Quickstart — Docker

Requires Docker with Compose v2 (`docker compose`, not the old `docker-compose`).

```bash
docker compose up --build
```

This builds and starts everything: the three stub agents, the backend API, the frontend, and a
one-shot `seed` job that registers the CAM/FSR/BSA agent cards against the backend once it's
healthy. Then:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (docs at `/docs`)
- Stub agents: http://localhost:9001 (CAM), :9002 (FSR), :9003 (BSA)

Build the demo workflow (`CAM -> FSR -> BSA`, with a conditional edge skipping BSA on high risk)
from the Workflow Builder at http://localhost:5173/workflows/new, or via the API — see
[scripts/run_dev.md](scripts/run_dev.md#build-the-demo-workflow) for the exact shape.

The backend's SQLite database persists in a named Docker volume (`backend_data`) across
restarts. To reset all state:

```bash
docker compose down -v
```

To rebuild a single service after code changes: `docker compose up --build backend` (etc).

## Quickstart — local dev (no Docker)

Five processes: backend, three stub agents, frontend. Requires [`uv`](https://docs.astral.sh/uv/)
and Node 22+.

```bash
# first-time setup
cd backend && uv sync && cd ..
cd stub_agents && uv sync && cd ..
cd frontend && npm install && cd ..
```

Full run/seed/build-a-workflow instructions: [scripts/run_dev.md](scripts/run_dev.md).

## Repo layout

| Path | What |
|---|---|
| `backend/` | FastAPI control plane — Agent/Workflow/Execution services, DAG validator, SQLModel + SQLite |
| `frontend/` | React + Vite UI — Agent CRUD, React Flow DAG builder, live execution monitor (SSE) |
| `stub_agents/` | Three canned FastAPI agents (CAM/FSR/BSA) standing in for real downstream agents |
| `scripts/` | `seed_agents.py` (registers stub agent cards), `run_dev.md` (local dev walkthrough) |
| `docs/` | Architecture, Agent Card schema reference, ADRs |
| `docker-compose.yml` | Containerized version of the same five processes, plus a seed job |

## Tests

```bash
cd backend && uv run pytest
```
