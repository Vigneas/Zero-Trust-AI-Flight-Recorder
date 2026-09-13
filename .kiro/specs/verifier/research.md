# Research & Discovery: Verifier CLI

## Summary
- **Domain**: Standalone offline cryptographic verification CLI for EU AI Act Article 19 audit receipts.
- **Tech Stack**: Python 3.12+, `hashlib`, `cbor2`, `cryptography.hazmat.primitives.asymmetric.ed25519`, `argparse`.
- **Environment**: 100% offline, zero network dependencies, runs in air-gapped regulatory environments.

## Architectural Discoveries & Decisions

### 1. Zero-Network Air-Gapped Verification
- **Decision**: The CLI strictly imports only standard library and local crypto/cbor dependencies. No HTTP, socket, or external DNS calls are made.
- **Auditor Workflow**: The auditor downloads `receipt.json` and obtains the bank's published Ed25519 public key (hex or base64). The CLI runs locally and outputs a definitive verdict.

### 2. Hash & Canonicalization Check
- **Verification Flow**:
  1. Base64-decode `cbor_payload` to recover `raw_bytes`.
  2. Compute `computed_hash = hashlib.sha256(raw_bytes).hexdigest()`.
  3. Compare `computed_hash == receipt["sha256_hash"]`. Any single-bit modification fails here.

### 3. Signature Verification
- **Classical (Ed25519)**:
  - Load `Ed25519PublicKey.from_public_bytes(...)` from base64/hex argument.
  - Verify signature over `raw_bytes`.
- **Post-Quantum (ML-DSA-65)**:
  - Decode base64 signature and verify compliance with ML-DSA-65 signature envelope (supporting mock/simulated specification for hackathon scope).

### 4. Merkle Inclusion Proof
- **RFC 6962 Node Hashing**:
  - Traverses `merkle_inclusion_proof` array of sibling hashes.
  - Reconstructs intermediate root and compares with expected tree head.

### 5. Article 19 Field Extraction
- **Payload Inspection**:
  - `cbor2.loads(raw_bytes)` restores the dictionary.
  - Verifies presence of `identity`, `data_classification`, `policy_version`, and `model_version`.
  - Verifies that `identity` contains no machine/service tokens.
