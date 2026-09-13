# Roadmap

## Overview
The goal is to build a "Zero-Trust AI Flight Recorder," a cryptographic evidence engine for algorithmic credit decisioning. This transforms mutable AI logs into mathematically provable cryptographic receipts to comply with stringent regulations (EU AI Act, DPDP Act, RBI). 

## Approach Decision
- **Chosen**: Python-based microservice architecture (FastAPI) and offline SDK.
- **Why**: Python has mature cryptographic libraries (`cryptography`, `hashlib`, `cbor2`) and is standard for AI/ML enterprise applications. It supports rapid prototyping.
- **Rejected alternatives**: Rust/Go were considered for performance, but Python is more accessible for rapid ML/AI integration and the hackathon timeline.

## Scope
- **In**: Out-of-band capture agent, CBOR canonicalization, SHA-256 hashing, hybrid post-quantum signatures (simulated/actual ML-DSA-65 + Ed25519), append-only Merkle transparency log, offline verifier CLI, and a mock AI lending API for demonstration.
- **Out**: Actual hardware attestation (TEE enclaves) and independent multi-party witnesses, which will be simulated/noted as absent for this phase.

## Constraints
- Must align with the Northwind Cipher `cool-sdk` principles (Never sit in the critical path, sensitive data stays in customer's boundary).
- Hybrid cryptography is required (Classical + Post-Quantum).

## Boundary Strategy
- **Why this split**: Separating the mock API, the core SDK engine, and the offline verifier allows parallel development, ensures the SDK remains independent of the business logic, and guarantees the verifier can run purely offline without server dependencies.
- **Shared seams to watch**: The `receipt.json` format is the contract between the `autonomous-lending-capture-hook` and the `verifier`.

## Specs (dependency order)
- [x] autonomous-lending-capture-hook -- Core cryptographic SDK for canonicalization, hashing, hybrid signatures, and Merkle log appending. Dependencies: none
- [x] lending-api -- Mock FastAPI agent simulating credit decisions that hooks into the autonomous-lending-capture-hook asynchronously. Dependencies: autonomous-lending-capture-hook
- [x] verifier -- Offline CLI tool to validate `receipt.json` files against public keys and transparency logs. Dependencies: autonomous-lending-capture-hook
