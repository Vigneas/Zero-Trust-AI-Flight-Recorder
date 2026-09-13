# Brief: verifier

## Problem
Regulators and auditors need a way to mathematically verify the `receipt.json` produced by the `evidence-engine` without trusting or connecting to the enterprise's internal systems.

## Current State
No verifier exists.

## Desired Outcome
An offline, standalone CLI tool that takes a `receipt.json` file and public keys, and verifies the canonicalization, hash, hybrid signatures, and Merkle inclusion proofs.

## Approach
A Python CLI script (using `argparse` or `click`) that reads the JSON receipt, reconstructs the CBOR bytes, computes the SHA-256 hash, verifies the Ed25519 and ML-DSA-65 signatures, and recalculates the Merkle path up to the Signed Tree Head.

## Scope
- **In**: CLI interface, JSON parsing, cryptographic verification logic, Merkle proof validation.
- **Out**: Generating new receipts, modifying existing logs.

## Boundary Candidates
- CLI Interface
- Cryptographic Verification Engine
- Merkle Proof Validator

## Out of Boundary
- Network calls (must operate 100% offline).

## Upstream / Downstream
- **Upstream**: Depends on `autonomous-lending-capture-hook` to establish the exact structure of `receipt.json`.
- **Downstream**: None.

## Existing Spec Touchpoints
- **Extends**: None.
- **Adjacent**: `autonomous-lending-capture-hook` (must exactly mirror the canonicalization and hashing algorithms used for creation).

## Constraints
- Must run completely offline.
