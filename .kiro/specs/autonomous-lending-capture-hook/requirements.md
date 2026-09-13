# Requirements Document: autonomous-lending-capture-hook

## Project Description (Input)
Standard AI logs are mutable and cannot cryptographically prove what an AI system decided, leaving enterprises vulnerable to regulatory fines under the EU AI Act and DPDP Act. We need a reusable SDK (autonomous-lending-capture-hook) that can intercept AI decisions out-of-band, canonicalize them to CBOR, hash them, sign them with hybrid cryptography (Ed25519 + ML-DSA-65), and commit them to an append-only Merkle transparency log.

## Requirements

### 1. Application Payload Definition
- **1.1** The `autonomous-lending-capture-hook` MUST extract and include specific context fields in the JSON payload before canonicalization to comply with EU AI Act Article 19. These fields SHALL include:
  - **Identity Resolution**: Who requested the decision. Must be a resolved natural human identifier (e.g., customer ID or employee ID), not a generic system account or API key.
  - **Payload Classification**: Data class (e.g., PII, financial data).
  - **Policy Version**: The specific internal risk parameters/policy used for the decision.
  - **Model Version**: The identifier of the AI model executed.

### 2. Canonicalization
- **2.1** The `autonomous-lending-capture-hook` MUST serialize the defined JSON/dict record into deterministic CBOR (RFC 8949 CDE).
- **2.2** WHEN two identical dictionary structures with different key orderings are provided, the `autonomous-lending-capture-hook` SHALL produce the exact same CBOR byte output.

### 3. Fail-Open Architecture
- **3.1** The `autonomous-lending-capture-hook` MUST operate out-of-band and never sit in the critical path of the AI model call.
- **3.2** IF the Merkle log or queuing system becomes unreachable, the system MUST fail open, allowing the AI to return the loan decision to the user without adding latency.
- **3.3** WHEN a fail-open event occurs and the queue is unreachable, the system SHALL maintain a local memory counter of dropped events. Upon recovery, the system MUST generate and sign a specific "loss entry" containing the count of missed events, appending this to the Merkle log to ensure transparent documentation of failure modes.

### 4. Cryptographic Hashing & Sealing
- **4.1** The `autonomous-lending-capture-hook` MUST generate a SHA-256 hash of the canonicalized CBOR bytes.
- **4.2** The `autonomous-lending-capture-hook` MUST sign the SHA-256 hash using an Ed25519 classical private key.
- **4.3** The `autonomous-lending-capture-hook` MUST sign the SHA-256 hash using an ML-DSA-65 (FIPS 204) post-quantum private key (or a mathematically sound simulated equivalent if native ML-DSA-65 is unavailable).
- **4.4** The `autonomous-lending-capture-hook` SHALL bundle the original record, the SHA-256 hash, and both signatures into a cohesive "receipt" structure.

### 5. Merkle Transparency Log & Simulated Domains
- **5.1** WHEN a receipt is generated, the `autonomous-lending-capture-hook` SHALL asynchronously append the receipt's hash to a local append-only Merkle tree (RFC 6962 compliant).
- **5.2** The `autonomous-lending-capture-hook` SHALL generate a Merkle inclusion proof for every appended receipt.
- **5.3** The `autonomous-lending-capture-hook` SHALL explicitly acknowledge that hardware enclave attestation (e.g., Intel TDX) and independent multi-party witnesses are currently simulated/absent. The generated receipts MUST correctly allow these domains to be flagged as simulated or absent by the verifier to adhere to zero vendor trust principles.

### 6. Output Format
- **6.1** The `autonomous-lending-capture-hook` MUST save the final complete record, including the CBOR bytes, hashes, signatures, and proofs, to a file named `receipt.json`.

## Boundary Exclusions
- The `autonomous-lending-capture-hook` explicitly DOES NOT expose a REST or HTTP API itself (it is an SDK/library).
- The `autonomous-lending-capture-hook` DOES NOT handle offline verification (this is owned by the `verifier` spec).
