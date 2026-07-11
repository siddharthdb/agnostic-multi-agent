"""In-process pub/sub so SSE listeners get execution events live, in addition
to the durable ExecutionEvent rows written for replay/reconnect. Per-process
only -- fine for the single-instance MVP; a multi-instance deployment would
need a shared broker (e.g. Redis pub/sub) instead."""

import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, execution_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._listeners[execution_id].append(queue)
        return queue

    def unsubscribe(self, execution_id: str, queue: asyncio.Queue) -> None:
        listeners = self._listeners.get(execution_id)
        if listeners and queue in listeners:
            listeners.remove(queue)

    def publish(self, execution_id: str, event: dict[str, Any]) -> None:
        for queue in self._listeners.get(execution_id, []):
            queue.put_nowait(event)


event_bus = EventBus()
