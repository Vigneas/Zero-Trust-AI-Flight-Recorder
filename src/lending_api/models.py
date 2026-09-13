from typing import Optional, Literal
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator

REJECTED_PREFIXES = (
    "svc:",
    "client:",
    "oauth:",
    "bot:",
    "system:",
    "service_account:",
)

class LoanApplicationRequest(BaseModel):
    applicant_id: str = Field(..., min_length=6, max_length=64, description="Natural human identifier of applicant")
    name: str = Field(..., min_length=2, max_length=100, description="Full legal name of applicant")
    annual_income: float = Field(..., gt=0, description="Verified annual income in currency units")
    requested_amount: float = Field(..., gt=0, description="Requested principal loan amount")
    credit_score: int = Field(..., ge=300, le=850, description="Applicant credit score (300-850)")

    @field_validator("applicant_id")
    def validate_natural_person(cls, v: str) -> str:
        clean = v.strip().lower()
        for prefix in REJECTED_PREFIXES:
            if clean.startswith(prefix):
                raise ValueError(
                    "applicant_id must represent a natural human person; "
                    "machine/service accounts and OAuth client credentials are prohibited under EU AI Act Article 19."
                )
        return v

class LoanEvaluationResponse(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: Literal["APPROVED", "REJECTED"]
    risk_tier: Literal["PRIME", "NEAR_PRIME", "SUBPRIME", "HIGH"]
    interest_rate: Optional[float] = None
    rejection_reason: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
