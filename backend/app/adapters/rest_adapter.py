import time
from typing import Any

import httpx

from app.adapters.base import AgentAdapter
from app.adapters.result import AdapterResult
from app.models.agent import Agent, AuthType


class RestAdapter(AgentAdapter):
    async def invoke(
        self, card: Agent, payload: dict[str, Any], *, timeout_s: float = 30.0
    ) -> AdapterResult:
        headers = self._build_auth_headers(card.auth_type, card.auth_config)
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            try:
                resp = await client.post(card.endpoint_url, json=payload, headers=headers)
                latency = (time.monotonic() - start) * 1000
                resp.raise_for_status()
                return AdapterResult(
                    success=True,
                    output=resp.json(),
                    status_code=resp.status_code,
                    latency_ms=latency,
                )
            except httpx.HTTPStatusError as e:
                return AdapterResult(
                    success=False,
                    status_code=e.response.status_code,
                    error=f"http_error: {e}",
                    latency_ms=(time.monotonic() - start) * 1000,
                )
            except httpx.RequestError as e:
                return AdapterResult(
                    success=False,
                    error=f"connection_error: {e}",
                    latency_ms=(time.monotonic() - start) * 1000,
                )

    async def health_check(self, card: Agent, *, timeout_s: float = 5.0) -> AdapterResult:
        url = card.health_check_url or card.endpoint_url
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            try:
                resp = await client.get(url)
                latency = (time.monotonic() - start) * 1000
                return AdapterResult(
                    success=resp.status_code < 500,
                    output=self._safe_json(resp),
                    status_code=resp.status_code,
                    latency_ms=latency,
                )
            except httpx.RequestError as e:
                return AdapterResult(
                    success=False,
                    error=f"connection_error: {e}",
                    latency_ms=(time.monotonic() - start) * 1000,
                )

    @staticmethod
    def _safe_json(resp: httpx.Response) -> dict[str, Any]:
        try:
            return resp.json()
        except ValueError:
            return {}

    @staticmethod
    def _build_auth_headers(auth_type: AuthType, cfg: dict[str, Any]) -> dict[str, str]:
        if auth_type == AuthType.API_KEY:
            return {cfg.get("header_name", "X-API-Key"): cfg["api_key"]}
        if auth_type == AuthType.BEARER:
            return {"Authorization": f"Bearer {cfg['token']}"}
        return {}
