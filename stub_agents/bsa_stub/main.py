from fastapi import FastAPI
from pydantic import BaseModel

from common.canned import simulate_latency, stable_hash

app = FastAPI(title="BSA Stub (Booking Service Agent)")


class BsaRequest(BaseModel):
    customer_id: str
    risk_level: str | None = None


@app.post("/invoke")
async def invoke(req: BsaRequest) -> dict:
    await simulate_latency()
    h = stable_hash(req.customer_id)
    booking_status = "held" if req.risk_level == "high" else "confirmed"
    reference = f"BSA-{h % 1_000_000:06d}"
    print(
        f"[BSA] customer_id={req.customer_id} risk_level={req.risk_level} "
        f"-> booking_status={booking_status} reference={reference}"
    )
    return {"booking_status": booking_status, "reference": reference}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
