# Brief: evidence-engine

## Problem
Standard AI logs are mutable and cannot cryptographically prove what an AI system decided, leaving enterprises vulnerable to regulatory fines under the EU AI Act and DPDP Act.

## Current State
The project is greenfield. No current state.

## Desired Outcome
A reusable SDK that can intercept AI decisions, canonicalize them to CBOR, hash them, sign them with hybrid cryptography (Ed25519 + ML-DSA-65), and commit them to an append-only Merkle transparency log.

## Approach
Implement the core logic in Python using `cbor2` for serialization, `hashlib` for SHA-256, and `cryptography` (or a suitable PQ mock library) for the hybrid seal. Implement a basic in-memory or file-backed Merkle tree.

## Scope
- **In**: CBOR canonicalization, SHA-256 hashing, hybrid signing, Merkle tree management, and generating the final `receipt.json`.
- **Out**: The actual AI lending business logic, the offline verification process.

## Boundary Candidates
- Canonicalization Module
- Cryptographic Sealing Module
- Transparency Log Module

## Out of Boundary
- Exposing an HTTP API (the engine should just be a library/SDK).

## Upstream / Downstream
- **Upstream**: None.
- **Downstream**: `lending-api` will consume this SDK to seal records. `verifier` will consume the output format (`receipt.json`).

## Existing Spec Touchpoints
- **Extends**: None.
- **Adjacent**: `verifier` (must agree on data formats).

## Constraints
- Must be asynchronous to avoid blocking the main execution path.
- Must produce deterministic CBOR.
