# ADR 0001: SQLite for MVP, path to Postgres

## Status

Accepted.

## Context

The control plane needs a database for Agent/Workflow/Execution/ExecutionEvent. The MVP has no
production data yet and needs to be trivially runnable by anyone cloning the repo — no external
service dependency for local development.

## Decision

Use SQLite (`sqlite:///./backend/dev.db`) for the MVP, via `DATABASE_URL` in
`backend/app/config.py` (`Settings.database_url`). Tables are created via
`SQLModel.metadata.create_all()` at startup (`backend/app/db.py::create_db_and_tables`,
called from the FastAPI `lifespan`), not Alembic migrations — there's no migration history to
manage yet.

## Consequences

- Zero setup: clone, `uv run uvicorn app.main:app`, done. `rm dev.db` resets state entirely.
- Fine for the demo's write concurrency (one writer per execution, single-process).
- **Path to Postgres**: change `DATABASE_URL` (env var or `.env`) to a `postgresql://...` URL.
  All JSON columns (`Agent.auth_config`, `Workflow.definition`, `Execution.node_states`, etc.) use
  SQLAlchemy's generic `JSON` type, which maps sensibly on both SQLite and Postgres; no column
  type changes required for the swap itself.
- What *would* be needed before running against Postgres in anything resembling production: real
  Alembic migrations (the `create_all()`-at-startup approach doesn't apply schema changes to an
  existing database with data in it), and moving off the in-process `RUNNING_TASKS` /
  `event_bus` singletons if running more than one backend instance (see
  [architecture.md](../architecture.md#known-mvp-limitations)).
