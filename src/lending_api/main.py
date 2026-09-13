import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from fastapi import FastAPI, BackgroundTasks, status, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from lending_api.models import LoanApplicationRequest, LoanEvaluationResponse
from lending_api.decision import evaluate_credit_risk
from lending_api.audit import build_article_19_audit_record, dispatch_audit_event
from autonomous_lending_capture_hook.hook import CaptureHook

logger = logging.getLogger("lending_api")
logging.basicConfig(level=logging.INFO)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
RECEIPT_FILE = "receipt.json"

# Operational metrics counters
metrics = {
    "total_evaluated": 0,
    "total_approved": 0,
    "total_rejected": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize out-of-band CaptureHook
    hook = CaptureHook(queue_size=1000)
    await hook.start()
    app.state.hook = hook
    logger.info("Lending API initialized with active CaptureHook.")
    try:
        yield
    finally:
        logger.info("Stopping CaptureHook worker...")
        await hook.stop()
        logger.info("CaptureHook successfully stopped.")

app = FastAPI(
    title="Autonomous Lending Credit Evaluation API",
    description="Algorithmic credit decision service with out-of-band EU AI Act Article 19 cryptographic audit capture.",
    version="0.1.0",
    lifespan=lifespan
)

# Ensure static folder exists
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=FileResponse)
async def serve_dashboard():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Dashboard UI not found")
    return FileResponse(index_path)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "lending-api",
        "version": "0.1.0"
    }

@app.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats() -> Dict[str, Any]:
    hook: CaptureHook = getattr(app.state, "hook", None)
    hook_stats = {}
    if hook:
        hook_stats = {
            "queue_active": hook.is_running,
            "loss_counter": hook.dropped_events_counter,
            "processed_events": len(hook.memory_log)
        }
    return {
        **metrics,
        "hook_status": hook_stats
    }

@app.get("/transparency-log", status_code=status.HTTP_200_OK)
async def get_transparency_log() -> Dict[str, Any]:
    hook: CaptureHook = getattr(app.state, "hook", None)
    leaves: List[str] = hook.memory_log if hook else []
    return {
        "leaves": leaves,
        "tree_size": len(leaves),
        "latest_root": leaves[-1] if leaves else None
    }

@app.get("/receipt/latest", status_code=status.HTTP_200_OK)
async def get_latest_receipt() -> Dict[str, Any]:
    if os.path.exists(RECEIPT_FILE):
        with open(RECEIPT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"Failed to read receipt: {exc}")
    raise HTTPException(status_code=404, detail="No receipt generated yet.")

@app.post("/evaluate_loan", response_model=LoanEvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_loan(
    request: LoanApplicationRequest,
    background_tasks: BackgroundTasks
) -> LoanEvaluationResponse:
    # 1. Deterministic credit underwriting evaluation
    decision = evaluate_credit_risk(request)

    # 2. Update observability metrics
    metrics["total_evaluated"] += 1
    if decision.status == "APPROVED":
        metrics["total_approved"] += 1
    else:
        metrics["total_rejected"] += 1

    # 3. Build EU AI Act Article 19 compliant audit record
    audit_record = build_article_19_audit_record(request, decision)

    # 4. Out-of-band dispatch via FastAPI background tasks (zero critical path latency)
    hook = getattr(app.state, "hook", None)
    background_tasks.add_task(dispatch_audit_event, hook, audit_record)

    # 5. Return immediate response to client
    return decision
