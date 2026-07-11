from fastapi import FastAPI
from pydantic import BaseModel

from common.canned import simulate_latency, stable_hash

app = FastAPI(title="FSR Stub (Fraud/Risk Scoring)")


class FsrRequest(BaseModel):
    customer_id: str
    account_tier: str | None = None


@app.post("/invoke")
async def invoke(req: FsrRequest) -> dict:
    await simulate_latency()
    h = stable_hash(req.customer_id)
    risk_score = (h % 100) / 100.0
    if risk_score < 0.34:
        risk_level = "low"
    elif risk_score < 0.7:
        risk_level = "medium"
    else:
        risk_level = "high"
    print(
        f"[FSR] customer_id={req.customer_id} account_tier={req.account_tier} "
        f"-> risk_score={risk_score} risk_level={risk_level}"
    )
    return {"risk_score": risk_score, "risk_level": risk_level}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
