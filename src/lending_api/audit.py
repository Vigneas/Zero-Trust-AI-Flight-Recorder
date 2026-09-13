import logging
from typing import Any, Dict
from lending_api.models import LoanApplicationRequest, LoanEvaluationResponse

logger = logging.getLogger("lending_api.audit")

DEFAULT_POLICY_VERSION = "POLICY-CREDIT-2026.1"
DEFAULT_MODEL_VERSION = "MODEL-CREDIT-EVAL-v1.4"
DATA_CLASSIFICATION_FINANCIAL = "PII_FINANCIAL_RECORDS"

def build_article_19_audit_record(
    request: LoanApplicationRequest,
    decision: LoanEvaluationResponse,
    policy_version: str = DEFAULT_POLICY_VERSION,
    model_version: str = DEFAULT_MODEL_VERSION
) -> Dict[str, Any]:
    """
    Constructs an EU AI Act Article 19 compliant audit record.
    Enforces the presence and validity of all 4 mandatory points:
    1. identity (natural human identifier)
    2. data_classification
    3. policy_version
    4. model_version
    """
    identity = request.applicant_id.strip() if request.applicant_id else ""
    if not identity:
        raise ValueError("Article 19 violation: Natural person identity is missing.")

    if not DATA_CLASSIFICATION_FINANCIAL:
        raise ValueError("Article 19 violation: Data classification is missing.")

    if not policy_version.strip():
        raise ValueError("Article 19 violation: Policy version is missing.")

    if not model_version.strip():
        raise ValueError("Article 19 violation: Model version is missing.")

    return {
        "identity": identity,
        "data_classification": DATA_CLASSIFICATION_FINANCIAL,
        "policy_version": policy_version,
        "model_version": model_version,
        "applicant_name": request.name,
        "annual_income": request.annual_income,
        "requested_amount": request.requested_amount,
        "credit_score": request.credit_score,
        "decision_id": decision.decision_id,
        "status": decision.status,
        "risk_tier": decision.risk_tier,
        "interest_rate": decision.interest_rate,
        "rejection_reason": decision.rejection_reason,
        "timestamp": decision.timestamp
    }

async def dispatch_audit_event(hook: Any, record: Dict[str, Any]) -> bool:
    """
    Asynchronously dispatches the audit record to the cryptographic CaptureHook out-of-band.
    Guarantees fail-open resilience: queue saturation or capture errors are logged
    without raising exceptions to ensure zero impact on the critical API response path.
    """
    try:
        if hook is not None and hasattr(hook, "capture_event"):
            await hook.capture_event(record)
            return True
        else:
            logger.warning("CaptureHook is not configured or lacks capture_event method.")
            return False
    except Exception as exc:
        logger.warning(
            "Failed to capture audit event to CaptureHook (fail-open engaged): %s",
            exc,
            exc_info=True
        )
        return False
