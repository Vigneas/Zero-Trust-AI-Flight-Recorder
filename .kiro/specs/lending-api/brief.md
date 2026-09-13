# Brief: lending-api

## Problem
We need a realistic demonstration of an AI application generating decisions that need cryptographic sealing to prove the `evidence-engine` works in a production-like scenario.

## Current State
No application currently exists.

## Desired Outcome
A mock FastAPI service that accepts loan application data, makes a deterministic decision, and asynchronously triggers the `evidence-engine` to record the decision without blocking the API response.

## Approach
Use Python and FastAPI. The API will have a simple endpoint `/evaluate_loan` that processes a JSON payload and uses Python's `asyncio.Queue` or `BackgroundTasks` to send the payload to the `evidence-engine`.

## Scope
- **In**: FastAPI server setup, dummy credit decision logic, asynchronous hooking into the `evidence-engine`.
- **Out**: Real AI models, database persistence for the application itself.

## Boundary Candidates
- API Routing
- Mock Decision Logic
- Async Queue Integration

## Out of Boundary
- Cryptographic signing logic (this is delegated to `evidence-engine`).

## Upstream / Downstream
- **Upstream**: Depends on `autonomous-lending-capture-hook` for the SDK capabilities.
- **Downstream**: None.

## Existing Spec Touchpoints
- **Extends**: None.
- **Adjacent**: `autonomous-lending-capture-hook` (uses its API).

## Constraints
- The integration must add zero latency to the critical path of the loan evaluation response.
