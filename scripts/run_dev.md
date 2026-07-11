# Running the full stack locally

Five processes, four terminals (stub agents can share one via backgrounding, or use four
terminals — either works):

```bash
# 1. Backend (FastAPI control plane) — from backend/
uv run uvicorn app.main:app --reload --port 8000

# 2-4. Stub agents (CAM/FSR/BSA) — from stub_agents/, one each
uv run uvicorn cam_stub.main:app --port 9001
uv run uvicorn fsr_stub.main:app --port 9002
uv run uvicorn bsa_stub.main:app --port 9003

# 5. Frontend — from frontend/
npm run dev
```

First-time setup: `uv sync` in `backend/` and `stub_agents/`; `npm install` in `frontend/`.

## Seed the stub agents into the registry

Once the backend and all three stubs are running:

```bash
python scripts/seed_agents.py
```

This POSTs `stub_agents/agent_cards/{cam,fsr,bsa}.json` to `http://localhost:8000/agents`. Pass a
different backend URL as the first argument if it's not running on the default port.

## Build the demo workflow

Either use the frontend's Workflow Builder (`http://localhost:5173/workflows/new`) — drag CAM,
FSR, BSA from the palette onto the canvas, connect `CAM -> FSR -> BSA`, click the `FSR -> BSA`
edge to set a condition (`field: $.nodes.n2.risk_level`, `op: neq`, `value: "high"`), then
Save/Validate/Publish — or create it directly via the API (see `docs/architecture.md` and
`backend/tests/test_dag_validator.py` for the `definition` JSON shape).

## Run it

From the Workflow Builder's "Run workflow" panel, or:

```bash
curl -X POST http://localhost:8000/workflows/{workflow_id}/execute \
  -H "Content-Type: application/json" \
  -d '{"input_payload": {"customer_id": "cust-42"}}'
```

Watch it live at `http://localhost:5173/executions/{execution_id}`, or stream it directly:

```bash
curl -N http://localhost:8000/executions/{execution_id}/events
```

`customer_id: "cust-5"` deterministically produces a `high` risk score from the FSR stub, which
demonstrates the conditional edge skipping the BSA node.
