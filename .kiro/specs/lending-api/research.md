# Research & Discovery: Lending API

## Summary
- **Domain**: Algorithmic credit decisioning microservice complying with EU AI Act Article 19 & DPDP Act.
- **Tech Stack**: Python 3.12+, FastAPI, Pydantic v2, `autonomous_lending_capture_hook`.
- **Primary Integration**: Asynchronous, non-blocking hook attachment into `CaptureHook` out-of-band pipeline.

## Architectural Discoveries & Decisions

### 1. Framework & Concurrency Model
- **Choice**: FastAPI with ASGI async handlers.
- **Rationale**: FastAPI provides high throughput, automatic OpenAPI documentation, and native Pydantic v2 validation.
- **Non-blocking Dispatch**: FastAPI's `BackgroundTasks` executes post-response work on the event loop, ensuring the client receives their HTTP 200 loan evaluation in `< 5ms` without blocking on cryptographic operations.

### 2. Natural Person Identity Enforcement
- **Requirement**: EU AI Act Article 19 requires that automated high-risk credit decisions identify the natural human person affected.
- **Decision**: Pydantic validator on `applicant_id` ensuring:
  - Rejects machine tokens or service identifiers matching prefixes `svc:`, `client:`, `oauth:`, `bot:`, or `system:`.
  - Enforces natural person string format (alphanumeric, min length 6, max length 64).

### 3. EU AI Act Article 19 Audit Context Injection
- **Decision**: Every credit decision automatically constructs an audit payload containing:
  - `identity`: validated `applicant_id`
  - `data_classification`: `PII_FINANCIAL_RECORDS`
  - `policy_version`: `POLICY-CREDIT-2026.1`
  - `model_version`: `MODEL-CREDIT-EVAL-v1.4`
  - `evaluation`: input factors, risk score, decision (`APPROVED`/`REJECTED`), reason codes, interest rate.

### 4. Zero-Latency Fail-Open Contract
- **Decision**: The background task wraps the hook call in a try/except block. If the hook's queue is full, `CaptureHook` records a loss entry in memory while the API layer increments an internal failure metric without raising an uncaught exception.
