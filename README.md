# Northwind Cipher // Zero-Trust AI Flight Recorder

> **Cryptographic Evidence Engine for Autonomous High-Risk Credit Decisioning**  
> Compliant with **EU AI Act Article 19**, **DPDP Act (India)**, and **NIST Post-Quantum Cryptography** standards. Built with the **CooL SDK** architecture.

---

## 1. The Problem We Are Solving

As financial institutions transition from traditional credit scoring to autonomous AI lending agents, they face an existential **Accountability Gap**:
* **Mutable Logs Fail Regulatory Scrutiny:** Standard observability tools (Datadog, Langfuse, ELK) store logs in mutable, admin-editable databases. In a hostile regulatory audit or court dispute (e.g., *Air Canada v. Moffatt*), editable log lines are mere assertions—not admissible cryptographic evidence.
* **EU AI Act Article 19 Mandate:** Autonomous high-risk credit underwriting systems are legally required to maintain continuous, tamper-evident logs tied to natural human identities throughout their operational lifetime. Violations trigger catastrophic fines of up to **€35 Million or 7% of global annual turnover**.
* **The Critical-Path Dilemma:** Banks cannot afford compliance tools that add latency to loan approvals or crash the primary transaction path.

---

## 2. What We Built

We built the **Zero-Trust AI Flight Recorder**, an enterprise-grade cryptographic compliance engine and interactive dashboard for autonomous lending:
* **Upstream Ingestion Gateway (`src/lending_api/`):** A high-throughput FastAPI underwriting service with sub-2ms critical path response and strict EU AI Act natural person validation.
* **Out-of-Band Capture Engine (`src/autonomous_lending_capture_hook/`):** A non-blocking, fail-open capture hook that asynchronously ingests loan decisions into a bounded ring buffer, serializes with RFC 8949 Canonical CBOR, signs with hybrid post-quantum cryptography, and seals commitments into an RFC 6962 Merkle tree.
* **Interactive 4-Page Web Dashboard (`src/lending_api/static/`):** A Phenomenon Studio-styled interface featuring an animated aero wallpaper with scroll parallax, home hub metrics, loan intake portal, live transparency stream, and an in-browser zero-trust verifier with a **1-Bit Tamper Fraud Simulator**.
* **Offline Auditor CLI Verifier (`src/verifier/`):** An air-gapped, zero-dependency CLI tool that validates the Seven Verification Domains and returns standard exit codes (`0` = PASS, `1` = FAIL).
* **Comprehensive Executive PDF:** A publication-grade 4-page pitch document (`Northwind_Cipher_Executive_Presentation.pdf`) downloadable directly from the dashboard.

---

## 3. How the CooL SDK Is Being Used

The **CooL SDK** (Cryptographic Evidence for AI Change by Northwind Cipher) serves as the core cryptographic and architectural backbone:
1. **Asynchronous Gateway Hook:** Intercepts loan evaluation requests and outputs at the API gateway level without wrapping or slowing down the core underwriting model.
2. **Deterministic Serialization (RFC 8949 CBOR):** Enforces canonical byte-level determinism (Canonical CBOR) so any two independent auditors compute the exact same byte representation of the credit decision.
3. **Binding Hash Commitment:** Computes an unalterable SHA-256 fingerprint over the canonical bytes, binding the borrower data, model version, APR tier, and decision reason.
4. **Hybrid Post-Quantum Cryptographic Sealing:** Implements dual signatures pairing classical **Ed25519** (64-byte fast verification) with post-quantum **ML-DSA-65** (NIST FIPS 204 lattice-based scheme) to ensure a 10-year regulatory retention horizon against quantum harvesting.
5. **RFC 6962 Merkle Transparency Tree:** Appends decision leaf hashes into an append-only Merkle tree, issuing Signed Tree Heads (STH) and logarithmic $O(\log n)$ audit paths for inclusion proofs.
6. **Seven Verification Domains:** Powers the 100% in-browser Web Crypto audit studio and offline CLI verifier across Canonical, Binding, Signature, Inclusion, Consistency, Attestation, and Witnesses domains.

---

## 4. Why CooL Is Critical to the Solution

Without CooL, financial institutions must either trust their database administrators not to alter records, or hand-roll fragile cryptographic logging:
* **Mathematical Non-Repudiation:** CooL eliminates the need to trust server logs. Regulators verify decision authenticity using purely mathematical proofs.
* **1-Bit Tamper Detection:** Any retroactive modification to credit scores, applicant names, or APR rates immediately breaks the SHA-256 binding and Merkle inclusion proof.
* **Zero Overhead on Critical Path:** CooL's bounded ring buffer guarantees that borrower loan decisions return in `< 2ms` with fail-open safety.
* **Data Sovereignty:** All raw applicant data, PII, and financial inputs remain strictly within the customer's secure boundary (VPC/On-Premise). Only the cryptographic hashes enter the transparency log.

---

## 5. Architecture & Workflow

```
[Borrower / Loan Portal] 
          │  (POST /evaluate_loan)
          ▼
┌────────────────────────────────────────────────────────┐
│  Lending API (FastAPI Engine)                          │
│  • Natural Person Identifier Validation (Art. 19)      │
│  • Deterministic Underwriting Rules (< 2ms)            │
└─────────┬──────────────────────────────────────────────┘
          │
          ├─────────────────────────────────────────────► [Returns Loan Decision < 2ms]
          │ (Asynchronous Out-of-Band Dispatch)
          ▼
┌────────────────────────────────────────────────────────┐
│  CooL Capture Hook (Bounded Ring Buffer / Fail-Open)   │
│  • Drops zero loans: logs signed loss entry if full    │
└─────────┬──────────────────────────────────────────────┘
          ▼
┌────────────────────────────────────────────────────────┐
│  CryptoSealer Engine                                   │
│  • RFC 8949 Canonical CBOR Deterministic Encoding      │
│  • SHA-256 Binding Hash Fingerprint                   │
│  • Hybrid ML-DSA-65 (Post-Quantum) + Ed25519 Signatures│
└─────────┬──────────────────────────────────────────────┘
          ▼
┌────────────────────────────────────────────────────────┐
│  RFC 6962 Merkle Transparency Log                     │
│  • Append-only leaf commitments                        │
│  • Signed Tree Head (STH) & Logarithmic Audit Paths    │
└─────────┬──────────────────────────────────────────────┘
          │ (Generates receipt.json)
          ▼
┌────────────────────────────────────────────────────────┐
│  Zero-Trust Verification (Auditor Studio & CLI)        │
│  • In-Browser Web Crypto API / Offline CLI Verifier    │
│  • Evaluates the Seven Verification Domains            │
└────────────────────────────────────────────────────────┘
```

---

## 6. Important Technical Decisions

1. **Fail-Open Concurrency with Signed Loss Entries:** In high-volume financial systems, backpressure must never block customer transactions. If the queue is saturated, the system fails open and records an unalterable signed loss entry, preserving mathematical accountability of failure states.
2. **Hybrid Classical + Post-Quantum Cryptography:** Rather than relying exclusively on unproven PQC schemes, we combine classical Ed25519 with NIST FIPS 204 ML-DSA-65. If either algorithm family is compromised, the record remains cryptographically secure.
3. **100% In-Browser Web Crypto Audit:** Regulators should not have to install software or trust the lender's backend. The Auditor Studio uses the native browser Web Crypto API to recompute SHA-256 digests and audit paths on the client machine.
4. **Radical Transparency in Verification:** We deliberately model the 7 verification domains with strict honesty: Hardware Attestation (Intel TDX) reports as `SIMULATED` and Public Witness Anchoring reports as `ABSENT`, demonstrating adherence to verifiable truth over superficial claims.

---

## 7. How to Run the Project

### Option A: Quickstart with Docker (Recommended)

```bash
# Build and launch all containers
docker compose up --build -d

# Verify service health
curl http://localhost:8000/health

# Open dashboard in browser
http://localhost:8000
```

### Option B: Local Development (Python 3.11+)

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell
source .venv/bin/activate    # Linux / macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated test suite (19/19 passing)
$env:PYTHONPATH="src"; pytest tests/ -v   # Windows
PYTHONPATH=src pytest tests/ -v           # Linux / macOS

# 4. Start the server
uvicorn lending_api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option C: Run Offline Verifier CLI

```bash
# Verify the latest generated decision receipt offline
python -m verifier.cli --receipt receipt.json

# Export verification report as structured JSON
python -m verifier.cli --receipt receipt.json --json
```

---

## 8. Limitations & Future Improvements

* **Hardware TEE Attestation:** Currently simulated; future work will bind cryptographic receipts directly to Intel TDX or AMD SEV hardware enclave quotes.
* **Decentralized Multi-Party Witnesses:** Transitioning the transparency log from a single operator tree to an independent, distributed witness pool (using C2SP signed notes).
* **Zero-Knowledge Underwriting Proofs:** Integrating zk-SNARKs (e.g., Groth16 / Plonky2) to allow applicants to mathematically prove they meet credit thresholds without revealing their exact income or social security numbers.

---

## 9. Test Suite Verification

The repository contains 19 comprehensive unit and integration tests covering all critical components:

```
tests/test_crypto.py::test_cbor_canonicalization PASSED
tests/test_crypto.py::test_hash_and_hybrid_sealing PASSED
tests/test_hook.py::test_capture_hook_fail_open_and_loss_entry PASSED
tests/test_lending_api.py::test_models_import_and_natural_person_validation PASSED
tests/test_lending_api.py::test_credit_decision_engine_rules PASSED
tests/test_lending_api.py::test_article_19_audit_record_builder PASSED
tests/test_lending_api.py::test_audit_dispatcher_fail_open PASSED
tests/test_lending_api.py::test_api_health_and_stats PASSED
tests/test_lending_api.py::test_api_evaluate_loan_flow PASSED
tests/test_lending_api.py::test_dashboard_and_transparency_endpoints PASSED
tests/test_merkle.py::test_merkle_log_append_and_proof PASSED
tests/test_payload.py::test_valid_payload_extraction PASSED
tests/test_payload.py::test_missing_field_raises_error PASSED
tests/test_payload.py::test_invalid_identity_raises_error PASSED
tests/test_receipt.py::test_receipt_generation PASSED
tests/test_verifier.py::test_crypto_verification_module PASSED
tests/test_verifier.py::test_merkle_inclusion_proof_verification PASSED
tests/test_verifier.py::test_article_19_compliance_auditor PASSED
tests/test_verifier.py::test_verifier_cli_e2e PASSED
============================= 19 passed in 1.05s ==============================
```
