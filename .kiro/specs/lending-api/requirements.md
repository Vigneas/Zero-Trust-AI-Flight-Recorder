# Requirements Document: Lending API

## Introduction
The Lending API is a mock enterprise loan evaluation service simulating an algorithmic credit decisioning system. It accepts credit applications, computes risk assessments, returns evaluation decisions to applicants with minimal latency, and asynchronously dispatches EU AI Act Article 19 compliant audit records to the out-of-band `autonomous-lending-capture-hook` for cryptographic sealing.

## Boundary Context
- **In scope**:
  - Ingestion of loan application data via a RESTful HTTP endpoint (`POST /evaluate_loan`).
  - Validation of mandatory EU AI Act and DPDP Act identity fields (`natural_person_id`, financial attributes).
  - Deterministic evaluation logic producing loan approval/rejection outcomes, risk tiers, and assigned rates.
  - Asynchronous, non-blocking dispatch of decision payloads into the `autonomous-lending-capture-hook`.
  - Service health check and status reporting endpoints.
- **Out of scope**:
  - Real neural network / proprietary ML model training.
  - Relational database persistence for loan contracts (delegated to enterprise core banking).
  - Cryptographic signing and Merkle tree generation (delegated to `autonomous-lending-capture-hook`).
- **Adjacent expectations**:
  - Relies on `autonomous-lending-capture-hook` installed as a dependency to asynchronously capture events and seal `receipt.json`.

## Requirements

### Requirement 1: Loan Application Ingestion and Natural Person Validation
**Objective:** As an API consumer, I want to submit loan application details via an HTTP endpoint, so that I receive an immediate credit decision while ensuring high-risk AI regulatory compliance.

#### Acceptance Criteria
1. When a client sends a `POST /evaluate_loan` request, the Lending API shall validate that `applicant_id` represents a natural human person identifier and reject machine credentials, service accounts, or OAuth client IDs with HTTP 422 Unprocessable Entity.
2. When a client sends a valid `POST /evaluate_loan` request with natural person identity (`applicant_id`, `name`), financial attributes (`annual_income`, `requested_amount`, `credit_score`), and risk metadata, the Lending API shall validate all required fields and return an HTTP 200 response containing the evaluation decision.
3. If any required field is missing, invalid, or fails natural person identity constraints, the Lending API shall return an HTTP 422 Unprocessable Entity with descriptive error messages.
4. The Lending API shall include `decision_id`, `status` (`APPROVED` or `REJECTED`), `risk_tier`, and `timestamp` in the response payload.

### Requirement 2: Algorithmic Credit Decisioning and Article 19 Context Injection
**Objective:** As a risk and compliance officer, I want credit applications evaluated deterministically and enriched with all four mandatory EU AI Act Article 19 context points, so that decisions are fair, explainable, and pass regulatory audit review.

#### Acceptance Criteria
1. When evaluating an application, if the applicant's `credit_score` is below the minimum threshold (e.g., 600) or debt-to-income ratio exceeds limits, the Lending API shall mark the decision as `REJECTED` with an explainability reason code.
2. When evaluating an application, if the applicant's financial attributes meet underwriting thresholds, the Lending API shall mark the decision as `APPROVED` and assign an interest rate corresponding to their risk tier.
3. The Lending API shall inject all four mandatory EU AI Act Article 19 audit fields into the evaluation decision record before dispatching to the capture hook:
   - `identity`: the verified natural person identifier (`applicant_id`),
   - `data_classification`: the data classification tag (e.g., `PII_FINANCIAL_RECORDS`),
   - `policy_version`: the specific risk policy ruleset utilized (e.g., `POLICY-CREDIT-2026.1`),
   - `model_version`: the specific algorithmic scoring model version utilized (e.g., `MODEL-CREDIT-EVAL-v1.4`).
4. If any of the four mandatory Article 19 context fields (`identity`, `data_classification`, `policy_version`, `model_version`) is absent or malformed, the Lending API shall refuse to dispatch the record to the capture hook and log a compliance alert.

### Requirement 3: Out-of-Band Cryptographic Capture Hook Integration
**Objective:** As a compliance engineer, I want the decision event captured and sealed without adding latency to the client response, so that enterprise operations remain resilient and fast.

#### Acceptance Criteria
1. When a credit decision is generated, the Lending API shall construct an audit payload with the applicant identity, policy version, model version, data classification, and decision details.
2. The Lending API shall dispatch the audit payload to the `autonomous-lending-capture-hook` asynchronously out-of-band using background workers or non-blocking queues.
3. If the capture hook buffer is unavailable or saturated, the Lending API shall fail open without degrading or failing the client's HTTP response.
4. The critical path response time of `POST /evaluate_loan` shall not be blocked or delayed by the downstream cryptographic hashing, signing, or Merkle tree operations.

### Requirement 4: Observability and Health
**Objective:** As a DevOps engineer, I want health check and operational metric endpoints, so that I can monitor service status and capture queue health.

#### Acceptance Criteria
1. When a `GET /health` request is received, the Lending API shall return an HTTP 200 OK status indicating service operational readiness.
2. When a `GET /stats` request is received, the Lending API shall return metrics including total loan applications processed, total decisions approved, total decisions rejected, and capture hook queue status.
