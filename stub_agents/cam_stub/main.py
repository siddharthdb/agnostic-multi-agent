from fastapi import FastAPI
from pydantic import BaseModel

from common.canned import simulate_latency, stable_hash

app = FastAPI(title="CAM Stub (Customer Account Manager)")


class CamRequest(BaseModel):
    customer_id: str


@app.post("/invoke")
async def invoke(req: CamRequest) -> dict:
    await simulate_latency()
    h = stable_hash(req.customer_id)
    status = "approved" if h % 2 == 0 else "declined"
    account_tier = "gold" if h % 3 == 0 else "standard"
    print(f"[CAM] customer_id={req.customer_id} -> status={status} account_tier={account_tier}")
    return {"customer_id": req.customer_id, "status": status, "account_tier": account_tier}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
