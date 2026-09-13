import pytest
from pydantic import ValidationError
from httpx import ASGITransport, AsyncClient

def test_models_import_and_natural_person_validation():
    from lending_api.models import LoanApplicationRequest, LoanEvaluationResponse

    # Valid human applicant
    valid_req = LoanApplicationRequest(
        applicant_id="citizen-in-98721",
        name="Aarav Sharma",
        annual_income=85000.0,
        requested_amount=25000.0,
        credit_score=760
    )
    assert valid_req.applicant_id == "citizen-in-98721"
    assert valid_req.credit_score == 760

    # Rejected machine / service accounts
    invalid_identities = [
        "svc:payment-bot",
        "client:oauth-enterprise-id",
        "oauth:token-holder-9",
        "bot:auto-crawler",
        "system:cron-evaluator",
        "service_account:backend-worker"
    ]
    for bad_id in invalid_identities:
        with pytest.raises(ValidationError) as exc_info:
            LoanApplicationRequest(
                applicant_id=bad_id,
                name="Bot Operator",
                annual_income=50000.0,
                requested_amount=10000.0,
                credit_score=700
            )
        assert "natural human person" in str(exc_info.value).lower()

def test_credit_decision_engine_rules():
    from lending_api.models import LoanApplicationRequest
    from lending_api.decision import evaluate_credit_risk

    # 1. Below minimum credit score (< 600) -> REJECTED
    req_low_score = LoanApplicationRequest(
        applicant_id="person-001",
        name="John Doe",
        annual_income=100000.0,
        requested_amount=10000.0,
        credit_score=550
    )
    res_low = evaluate_credit_risk(req_low_score)
    assert res_low.status == "REJECTED"
    assert res_low.risk_tier == "HIGH"
    assert "CREDIT_SCORE_BELOW_THRESHOLD" in res_low.rejection_reason

    # 2. Excessive debt-to-income (> 60% of annual income) -> REJECTED
    req_excess_debt = LoanApplicationRequest(
        applicant_id="person-002",
        name="Jane Smith",
        annual_income=50000.0,
        requested_amount=35000.0,  # 70% of annual income
        credit_score=720
    )
    res_debt = evaluate_credit_risk(req_excess_debt)
    assert res_debt.status == "REJECTED"
    assert res_debt.risk_tier == "HIGH"
    assert "EXCESSIVE_DEBT_TO_INCOME" in res_debt.rejection_reason

    # 3. Prime tier (score >= 750) -> APPROVED
    req_prime = LoanApplicationRequest(
        applicant_id="person-003",
        name="Alice Walker",
        annual_income=120000.0,
        requested_amount=30000.0,
        credit_score=780
    )
    res_prime = evaluate_credit_risk(req_prime)
    assert res_prime.status == "APPROVED"
    assert res_prime.risk_tier == "PRIME"
    assert res_prime.interest_rate == 5.5
    assert res_prime.rejection_reason is None

    # 4. Near Prime (670 <= score < 750) -> APPROVED
    req_near_prime = LoanApplicationRequest(
        applicant_id="person-004",
        name="Bob Martin",
        annual_income=80000.0,
        requested_amount=20000.0,
        credit_score=690
    )
    res_near_prime = evaluate_credit_risk(req_near_prime)
    assert res_near_prime.status == "APPROVED"
    assert res_near_prime.risk_tier == "NEAR_PRIME"
    assert res_near_prime.interest_rate == 7.9

    # 5. Subprime (600 <= score < 670) -> APPROVED
    req_subprime = LoanApplicationRequest(
        applicant_id="person-005",
        name="Charlie Day",
        annual_income=60000.0,
        requested_amount=15000.0,
        credit_score=620
    )
    res_subprime = evaluate_credit_risk(req_subprime)
    assert res_subprime.status == "APPROVED"
    assert res_subprime.risk_tier == "SUBPRIME"
    assert res_subprime.interest_rate == 11.5

def test_article_19_audit_record_builder():
    from lending_api.models import LoanApplicationRequest
    from lending_api.decision import evaluate_credit_risk
    from lending_api.audit import build_article_19_audit_record

    req = LoanApplicationRequest(
        applicant_id="citizen-eu-41908",
        name="Elena Rossi",
        annual_income=95000.0,
        requested_amount=20000.0,
        credit_score=790
    )
    dec = evaluate_credit_risk(req)
    record = build_article_19_audit_record(req, dec)

    # Validate 4 mandatory Article 19 points
    assert record["identity"] == "citizen-eu-41908"
    assert record["data_classification"] == "PII_FINANCIAL_RECORDS"
    assert record["policy_version"] == "POLICY-CREDIT-2026.1"
    assert record["model_version"] == "MODEL-CREDIT-EVAL-v1.4"
    assert record["decision_id"] == dec.decision_id
    assert record["status"] == "APPROVED"
    assert record["risk_tier"] == "PRIME"

@pytest.mark.asyncio
async def test_audit_dispatcher_fail_open():
    from lending_api.audit import dispatch_audit_event

    class MockFailingHook:
        async def capture_event(self, record):
            raise RuntimeError("Queue buffer saturated!")

    class MockSucceedingHook:
        def __init__(self):
            self.captured = []
        async def capture_event(self, record):
            self.captured.append(record)

    # 1. Success case
    ok_hook = MockSucceedingHook()
    test_rec = {"identity": "user1", "status": "APPROVED"}
    await dispatch_audit_event(ok_hook, test_rec)
    assert len(ok_hook.captured) == 1

    # 2. Fail-open case: should NOT raise exception
    fail_hook = MockFailingHook()
    await dispatch_audit_event(fail_hook, test_rec)

@pytest.mark.asyncio
async def test_api_health_and_stats():
    from lending_api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health check
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

        # Stats endpoint
        stats_resp = await client.get("/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert "total_evaluated" in stats
        assert "total_approved" in stats
        assert "total_rejected" in stats

@pytest.mark.asyncio
async def test_api_evaluate_loan_flow():
    from lending_api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Approved loan request
        payload = {
            "applicant_id": "citizen-de-99881",
            "name": "Greta Weber",
            "annual_income": 90000.0,
            "requested_amount": 20000.0,
            "credit_score": 770
        }
        res = await client.post("/evaluate_loan", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "APPROVED"
        assert data["risk_tier"] == "PRIME"
        assert data["interest_rate"] == 5.5
        assert "decision_id" in data

        # 2. Rejection for low credit score
        payload_rejected = {
            "applicant_id": "citizen-de-99882",
            "name": "Hans Becker",
            "annual_income": 50000.0,
            "requested_amount": 10000.0,
            "credit_score": 520
        }
        res_rej = await client.post("/evaluate_loan", json=payload_rejected)
        assert res_rej.status_code == 200
        assert res_rej.json()["status"] == "REJECTED"

        # 3. Machine / OAuth ID rejected with 422
        payload_machine = {
            "applicant_id": "svc:cron-job-runner",
            "name": "Automated Process",
            "annual_income": 100000.0,
            "requested_amount": 5000.0,
            "credit_score": 800
        }
        res_err = await client.post("/evaluate_loan", json=payload_machine)
        assert res_err.status_code == 422
        assert "natural human person" in str(res_err.json()).lower()

@pytest.mark.asyncio
async def test_dashboard_and_transparency_endpoints():
    from lending_api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Dashboard index.html
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "NORTHWIND CIPHER" in resp.text
        assert "Applicant Loan Portal" in resp.text

        # Transparency Log
        log_resp = await client.get("/transparency-log")
        assert log_resp.status_code == 200
        log_data = log_resp.json()
        assert "leaves" in log_data
        assert "tree_size" in log_data

        # Latest Receipt
        receipt_resp = await client.get("/receipt/latest")
        # Should be 200 if receipt.json exists, or 404
        assert receipt_resp.status_code in (200, 404)
