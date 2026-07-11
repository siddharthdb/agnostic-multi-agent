from typing import Any

from pydantic import BaseModel


class AdapterResult(BaseModel):
    success: bool
    output: dict[str, Any] = {}
    status_code: int | None = None
    latency_ms: float
    error: str | None = None
