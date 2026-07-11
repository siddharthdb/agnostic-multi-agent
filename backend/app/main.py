from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnsupportedProtocolError,
    ValidationFailedError,
)
from app.db import create_db_and_tables
from app.models import Agent, Execution, ExecutionEvent, Workflow  # noqa: F401  (registers tables)
from app.routers import agents, executions, workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Multi-Agent Registry & Workflow Orchestrator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ValidationFailedError)
def handle_validation_failed(request: Request, exc: ValidationFailedError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc), "errors": exc.errors})


@app.exception_handler(UnsupportedProtocolError)
def handle_unsupported_protocol(request: Request, exc: UnsupportedProtocolError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(executions.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
