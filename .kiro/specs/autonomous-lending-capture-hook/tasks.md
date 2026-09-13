# Implementation Plan: autonomous-lending-capture-hook

## Tasks

### 1. Payload Extraction
- [x] 1.1 Implement `PayloadExtractor` in `payload.py`
  - Extract the four mandatory compliance fields: `identity`, `data_classification`, `policy_version`, `model_version`.
  - Enforce strict validation that `identity` is a natural person identifier (not generic service credential or OAuth client ID). Raise internal exception on validation failure.
  - Observable completion: Unit tests pass confirming validation accepts human IDs and rejects generic service accounts.
  - _Requirements: 1.1_
  - _Boundary: payload.py_

### 2. Cryptographic Engine
- [x] 2.1 Implement CBOR canonicalization in `crypto.py`
  - Write serialization logic using `cbor2` to produce deterministic RFC 8949 CDE byte outputs.
  - Observable completion: Unit test proves two identical dicts with shuffled keys produce the exact same CBOR hash.
  - _Requirements: 2.1, 2.2_
  - _Boundary: crypto.py_

- [x] 2.2 Implement SHA-256 and Hybrid Sealing in `crypto.py`
  - Hash canonical bytes with `hashlib.sha256`.
  - Sign the hash with Ed25519 using `cryptography` library.
  - Provide a mock signature for ML-DSA-65 (FIPS 204) since a real implementation might not be available.
  - Observable completion: Calling the signer returns the raw payload hash and both signature strings.
  - _Requirements: 4.1, 4.2, 4.3_
  - _Boundary: crypto.py_
  - _Depends: 2.1_

### 3. Merkle Transparency Log
- [x] 3.1 Implement `MerkleLog` in `merkle.py`
  - Create a file-backed append-only Merkle tree structure (RFC 6962 compliant).
  - Implement appending of hashes and generating inclusion proofs for leaves.
  - Observable completion: A test can append a hash, receive an inclusion proof, and verify it against the STH.
  - _Requirements: 5.1, 5.2_
  - _Boundary: merkle.py_

### 4. Receipt Generation
- [x] 4.1 Implement `ReceiptBuilder` in `receipt.py`
  - Bundle the CBOR payload, SHA-256 hash, Ed25519 signature, ML-DSA-65 signature, and Merkle inclusion proof.
  - Base64 encode the CBOR payload and large signatures (ML-DSA-65) for clean JSON serialization.
  - Explicitly hardcode `"hardware_attestation": "SIMULATED"` and `"witness_signatures": []`.
  - Save the final JSON object to `receipt.json`.
  - Observable completion: Generated `receipt.json` passes a JSON schema validation.
  - _Requirements: 4.4, 5.3, 6.1_
  - _Boundary: receipt.py_
  - _Depends: 1.1, 2.2, 3.1_

### 5. Out-of-Band Capture Hook
- [x] 5.1 Implement `CaptureHook` and fail-open queuing in `hook.py`
  - Implement an `asyncio.Queue` and a background worker task.
  - Expose async `.record(decision: dict)` method that pushes to queue. If queue is full/unreachable, increment drop counter and return safely.
  - Implement the background worker: pop from queue, invoke extraction, sealing, logging, and receipt generation.
  - If the drop counter is > 0 when the worker processes a new event, create a signed "loss entry", append it to the log, and reset the counter.
  - Observable completion: A simulated full queue drops events without raising exceptions to the caller, and upon recovery, generates a signed loss entry.
  - _Requirements: 3.1, 3.2, 3.3_
  - _Boundary: hook.py_
  - _Depends: 1.1, 2.2, 3.1, 4.1_
