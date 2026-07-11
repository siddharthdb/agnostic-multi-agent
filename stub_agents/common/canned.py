import asyncio
import hashlib
import random


def stable_hash(value: str) -> int:
    """Deterministic per-value hash so the same customer_id always produces
    the same canned outputs across CAM/FSR/BSA -- makes the demo repeatable."""
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)


async def simulate_latency(low: float = 0.2, high: float = 0.8) -> None:
    await asyncio.sleep(random.uniform(low, high))
