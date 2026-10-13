"""
FastAPI REST API Server for Ipss R Myelodysplastic Calculator.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ipss_r import calculate_metrics
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ipss R Myelodysplastic Calculator API",
    description="IPSS-R scoring and optional audit workflow API",
    version="3.0.0-ENTERPRISE",
)


class CalculationRequest(BaseModel):
    cytogenetic_risk: str
    blast_pct: float
    hemoglobin: float
    platelets: float
    anc: float


# The same standalone HTML and JS work from FastAPI and GitHub Pages.
WEB_DIR = Path(__file__).resolve().parents[1] / "web"
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(WEB_DIR / "index.html")


@app.post("/api/calculate")
def api_calculate(payload: CalculationRequest):
    try:
        return calculate_metrics(**payload.model_dump())
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "ipss-r-myelodysplastic-calculator"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
