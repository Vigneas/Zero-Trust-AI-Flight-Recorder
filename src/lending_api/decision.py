from lending_api.models import LoanApplicationRequest, LoanEvaluationResponse

def evaluate_credit_risk(request: LoanApplicationRequest) -> LoanEvaluationResponse:
    """
    Deterministic credit risk underwriting rule engine.
    Applies explainable thresholds for automated lending compliance.
    """
    # 1. Minimum credit score check
    if request.credit_score < 600:
        return LoanEvaluationResponse(
            status="REJECTED",
            risk_tier="HIGH",
            rejection_reason="CREDIT_SCORE_BELOW_THRESHOLD: Credit score 600+ required for automated underwriting."
        )

    # 2. Maximum debt-to-income threshold (60% of annual income)
    max_allowable_principal = request.annual_income * 0.60
    if request.requested_amount > max_allowable_principal:
        return LoanEvaluationResponse(
            status="REJECTED",
            risk_tier="HIGH",
            rejection_reason="EXCESSIVE_DEBT_TO_INCOME: Requested loan exceeds 60% allowable debt-to-income ratio."
        )

    # 3. Risk-tier and interest rate assignment for approved loans
    if request.credit_score >= 750:
        tier = "PRIME"
        rate = 5.5
    elif request.credit_score >= 670:
        tier = "NEAR_PRIME"
        rate = 7.9
    else:
        tier = "SUBPRIME"
        rate = 11.5

    return LoanEvaluationResponse(
        status="APPROVED",
        risk_tier=tier,
        interest_rate=rate,
        rejection_reason=None
    )
