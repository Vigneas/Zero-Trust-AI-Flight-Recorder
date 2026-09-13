# Design Document: autonomous-lending-capture-hook

## Overview 
This feature delivers a mathematically provable, out-of-band cryptographic evidence SDK for enterprise AI lending systems. 
Financial institutions and regulatory auditors will utilize this to verify the exact parameters and outcomes of algorithmic credit decisions.
It changes the current state of mutable, untrustworthy AI logging by producing deterministic, hybrid post-quantum sealed Merkle receipts (`receipt.json`) without adding latency to the critical path.

### Goals
- Extract specific compliance fields (Identity, Classification, Policy, Model) from AI decisions.
- Serialize the payload deterministically to CBOR and hash it with SHA-256.
- Seal the hash using hybrid cryptography (Ed25519 + ML-DSA-65).
- Append the hash to an RFC 6962 compliant Merkle transparency log.
- Ensure the capture hook fails open if logging or queuing infrastructure is unreachable.

### Non-Goals
- We will not build the actual AI credit decisioning models.
- We will not implement the offline verifier logic in this spec.
- We will not integrate actual hardware enclaves (Intel TDX) or multi-party witnesses; these will be simulated.

## Boundary Commitments

### This Spec Owns
- The out-of-band capture interface (`CaptureHook`).
- The canonicalization logic (JSON -> CBOR).
- The cryptographic sealing pipeline (Hashing and Hybrid Signatures).
- The local Merkle Transparency Log state.
- The formatting and generation of `receipt.json`.

### Out of Boundary
- The HTTP API layer for the mock lending app (handled by `lending-api`).
- The offline verification CLI (handled by `verifier`).
- Long-term remote storage of `receipt.json` (assume local file system drop for this phase).

### Allowed Dependencies
- Python standard library (`hashlib`, `json`).
- `cbor2` library for deterministic serialization.
- `cryptography` library for Ed25519 signing.
- A simulated or third-party library for ML-DSA-65.

### Revalidation Triggers
- Any changes to the `receipt.json` schema.
- Switching cryptographic algorithms.

## Architecture

### Architecture Pattern & Boundary Map
We are using an **Asynchronous Out-of-Band Middleware** pattern.
- The `CaptureHook` exposes an async `.record_decision()` method.
- It pushes the raw decision dict onto an internal `asyncio.Queue`.
- A background worker (`EvidenceWorker`) pops from the queue and coordinates the pipeline: Extraction -> Canonicalization -> Hashing -> Signing -> Merkle Append -> Receipt Generation.
- If the queue is full or the worker fails, the `record_decision()` method catches the error, logs it locally, and returns immediately (Fail-Open).

### Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Backend | Python 3.10+ | Core language | Rich crypto ecosystem |
| Data | `cbor2` | Deterministic Canonicalization | RFC 8949 CDE |
| Crypto | `cryptography` | Classical signatures | Ed25519 |
| State | File-backed JSON | Merkle Tree State | Simple persistence for demo |

## File Structure Plan

```
src/
└── autonomous_lending_capture_hook/
    ├── __init__.py           
    ├── hook.py               # Boundary: CaptureHook and fail-open queue logic
    ├── payload.py            # Boundary: Extraction of required EU AI Act fields
    ├── crypto.py             # Boundary: CBOR, SHA-256, Ed25519, ML-DSA-65
    ├── merkle.py             # Boundary: RFC 6962 append-only log and inclusion proofs
    └── receipt.py            # Boundary: Bundling everything into receipt.json
```

## Requirements Traceability

| Requirement | Summary | Components |
|-------------|---------|------------|
| 1.1 | Extract Context Fields | `payload.py` |
| 2.1, 2.2 | CBOR Canonicalization | `crypto.py` |
| 3.1, 3.2, 3.3 | Fail-Open Architecture | `hook.py` |
| 4.1, 4.2, 4.3, 4.4 | Hash and Hybrid Sealing | `crypto.py`, `receipt.py` |
| 5.1, 5.2, 5.3 | Merkle Log & Simulated Domains | `merkle.py`, `receipt.py` |
| 6.1 | Output `receipt.json` | `receipt.py` |

## Components and Interfaces

### Core Engine

#### CaptureHook (`hook.py`)
| Field | Detail |
|-------|--------|
| Intent | Asynchronous entry point for the lending API. |
| Requirements | 3.1, 3.2, 3.3 |

**Responsibilities & Constraints**
- Maintain an internal `asyncio.Queue` and a counter for dropped events.
- Expose an async `record(decision: dict)` method.
- If queue is full/unreachable, increment the drop counter and return (fail-open).
- When the queue recovers/worker processes, if the drop counter > 0, generate a signed "loss entry" with the missed count, reset the counter, and append to the Merkle log.
- Run a background task to process the queue.

##### Service Interface
```python
class CaptureHook:
    async def record(self, decision: dict) -> None:
        pass
    async def _worker(self) -> None:
        pass
```

#### PayloadExtractor (`payload.py`)
| Field | Detail |
|-------|--------|
| Intent | Ensure mandatory EU AI Act fields are present. |
| Requirements | 1.1 |

**Implementation Notes**
- Extract `identity`, `data_classification`, `policy_version`, `model_version`.
- Enforce strict validation on `identity`: Must be a natural person identifier. Reject generic service credentials or OAuth client IDs.
- Raise an internal exception if fields are missing or invalid (caught by the worker and logged).

#### CryptoSealer (`crypto.py`)
| Field | Detail |
|-------|--------|
| Intent | Handle canonicalization, hashing, and signatures. |
| Requirements | 2.1, 2.2, 4.1, 4.2, 4.3 |

**Implementation Notes**
- Use `cbor2.dumps` with deterministic flags if available.
- Use `hashlib.sha256`.
- Provide a mock for ML-DSA-65 that returns a dummy byte string if a real library is not used.

#### MerkleLog (`merkle.py`)
| Field | Detail |
|-------|--------|
| Intent | Maintain transparency log state. |
| Requirements | 5.1, 5.2 |

**Implementation Notes**
- File-backed list of hashes.
- Function to generate an inclusion proof (list of sibling hashes) for a given leaf index.

#### ReceiptBuilder (`receipt.py`)
| Field | Detail |
|-------|--------|
| Intent | Construct the final JSON output. |
| Requirements | 4.4, 5.3, 6.1 |

**Implementation Notes**
- Must explicitly set `"hardware_attestation": "SIMULATED"` and `"witness_signatures": []`.
- Must base64 encode large byte strings (such as the ~3,300-byte ML-DSA-65 signature and the CBOR payload) to ensure clean JSON serialization and prevent breaking the downstream verifier.
- Writes to `receipt.json`.

## Testing Strategy
- Unit Tests: Verify `cbor2` produces identical outputs for shuffled dictionary keys.
- Unit Tests: Verify `CaptureHook` does not block or raise exceptions when the queue is intentionally broken (Fail-open test).
- Integration Tests: Submit a payload to `CaptureHook`, wait for the queue to process, and verify `receipt.json` exists with all required fields.
