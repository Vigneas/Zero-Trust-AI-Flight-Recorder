# Requirements Document: Offline Auditor Verifier CLI

## Introduction
The Verifier is a standalone, zero-trust command-line utility for regulatory authorities, auditors, and compliance officers (e.g., EU AI Office, RBI, internal risk reviewers). It mathematically validates cryptographic loan evaluation receipts (`receipt.json`) produced by the Evidence Engine completely offline, with zero trust placed in the issuing bank's servers or internal databases.

## Boundary Context
- **In scope**:
  - Offline command-line interface accepting `receipt.json` and verification parameters (e.g. public key, expected root).
  - Base64 payload decoding and deterministic SHA-256 digest recomputation to detect any tampering.
  - Classical Ed25519 signature verification using the bank's published public key.
  - Post-quantum ML-DSA-65 signature structure and cryptographic validation.
  - Merkle inclusion proof traversal from the receipt leaf hash to the Signed Tree Head (STH) root hash.
  - EU AI Act Article 19 compliance audit check on the decoded payload (`identity` natural person, `data_classification`, `policy_version`, `model_version`).
  - Clear CLI reporting (human-readable and JSON format) with standard exit codes (0 = VALID, 1 = INVALID / TAMPERED).
- **Out of scope**:
  - Network requests or calls to remote servers (must operate 100% offline).
  - Generating new receipts or mutating transparency logs.
  - Managing private signing keys (only uses public keys).
- **Adjacent expectations**:
  - Relies on the receipt schema established by `autonomous-lending-capture-hook`.

## Requirements

### Requirement 1: Offline Receipt Ingestion and Schema Parsing
**Objective:** As an auditor, I want to provide a `receipt.json` file to the verifier CLI, so that the cryptographic evidence is extracted and checked for structural integrity.

#### Acceptance Criteria
1. When an auditor provides a valid path to `receipt.json`, the Verifier shall parse the document and extract `cbor_payload`, `sha256_hash`, `ed25519_signature`, `ml_dsa_65_signature`, and `merkle_inclusion_proof`.
2. If the file does not exist, is not valid JSON, or is missing required receipt fields, the Verifier shall output an error message and exit with non-zero status.
3. The Verifier shall execute entirely in an offline environment without attempting any external network connection or DNS resolution.

### Requirement 2: Canonical Payload Integrity & SHA-256 Verification
**Objective:** As an auditor, I want to verify the cryptographic hash of the canonical payload, so that I can guarantee the decision data has not been altered by even a single bit.

#### Acceptance Criteria
1. When verifying the payload, the Verifier shall decode the base64 `cbor_payload` to obtain raw canonical bytes and compute its SHA-256 digest.
2. If the computed SHA-256 digest matches the receipt's `sha256_hash`, the Verifier shall mark the payload integrity check as `PASSED`.
3. If the computed digest does not match `sha256_hash`, the Verifier shall mark the check as `FAILED: HASH_MISMATCH` and abort verification.

### Requirement 3: Hybrid Post-Quantum and Classical Signature Verification
**Objective:** As a cryptographic auditor, I want to verify both classical and post-quantum digital signatures against the bank's public keys, so that non-repudiation is mathematically proven.

#### Acceptance Criteria
1. When provided with the bank's Ed25519 public key, the Verifier shall verify the `ed25519_signature` over the raw canonical bytes.
2. If the Ed25519 signature is cryptographically valid for the given public key, the Verifier shall mark classical signature verification as `PASSED`.
3. If the Ed25519 signature is forged or invalid, the Verifier shall mark the signature as `FAILED: ED25519_INVALID`.
4. The Verifier shall verify the `ml_dsa_65_signature` against post-quantum specification standards and report verification status `PASSED` or `SIMULATED_VALID`.

### Requirement 4: Merkle Inclusion Proof Validation
**Objective:** As a compliance officer, I want to verify the Merkle audit path against the root hash (Signed Tree Head), so that I know the decision was logged in an immutable, append-only log.

#### Acceptance Criteria
1. When provided with an expected Merkle root hash (or tree head), the Verifier shall traverse the `merkle_inclusion_proof` sibling hashes starting from the leaf hash.
2. If the recalculated root matches the expected root, the Verifier shall mark the inclusion proof as `PASSED`.
3. If the recalculated root differs from the expected root, the Verifier shall mark the proof as `FAILED: MERKLE_ROOT_MISMATCH`.

### Requirement 5: EU AI Act Article 19 Audit Compliance Inspection
**Objective:** As a regulatory inspector, I want the verifier to inspect the decoded payload for all mandatory Article 19 fields, so that I can confirm regulatory completeness.

#### Acceptance Criteria
1. When the payload is decoded, the Verifier shall decode the CBOR structure and inspect for the 4 mandatory fields: `identity`, `data_classification`, `policy_version`, and `model_version`.
2. When inspecting `identity`, the Verifier shall verify that it represents a natural person rather than a machine or service credential.
3. If all 4 mandatory fields are present and valid, the Verifier shall mark the Article 19 audit check as `COMPLIANT`.
4. If any mandatory field is missing, the Verifier shall list the missing field and mark the check as `NON_COMPLIANT`.

### Requirement 6: CLI Interface and Structured Reporting
**Objective:** As an automated compliance scanner or human auditor, I want clear CLI terminal output and optional JSON export, so that results can be integrated into audit reports.

#### Acceptance Criteria
1. When invoked from the command line, the Verifier shall support flags: `--receipt <path>`, `--public-key <path/base64>`, `--root <hash>`, and `--json`.
2. When verification succeeds for all checks, the Verifier shall exit with exit code `0`.
3. When any verification check fails, the Verifier shall exit with exit code `1` and highlight the specific failure reason.
4. Where the `--json` flag is provided, the Verifier shall output a machine-parseable JSON validation summary containing individual test verdicts and overall status.
