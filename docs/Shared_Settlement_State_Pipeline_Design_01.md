# Shared_Settlement_State_Pipeline_Design_01.md

**Status:** DESIGN PROPOSAL — NOT Production Authorization
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Objective & Scope
This document provides an implementable architecture design package for the first Shared Settlement State Pipeline Production vertical slice. It composes the accepted contracts from ADR-001, ADR-003, ADR-004, ADR-006A/B, ADR-007, and ADR-008 into a cohesive, failure-resilient data pipeline.

**First Vertical Slice:** 
A Server-authored, typed inventory deduction (e.g., an offline Tax payment or Auto-Shop purchase) against a frozen, unleased Settlement, relying exclusively on known indexed canonical facts.
*Why this slice is safe:* It completely avoids the complexities of `DELTA_BARRIER` handoffs, active Tactical Worker staging, full RimWorld semantic loading, multi-party trade consensus, and unresolved policy decisions (TBD-05, G-Q1, G-Q2, G-Q6)[cite: 24]. It strictly exercises the core transaction plumbing: idempotency, revision CAS, DB commits, outbox delivery, and recovery.

## 2. Required Production Components

### 2.1 Operation Journal (ADR-004)
*   **Responsibility:** Durable state machine for multi-phase operations[cite: 29].
*   **Data Owned:** `OperationId`, Payload Hash, Actor, State (`VALIDATING`, `PREPARED`, `COMMITTED`, `PUBLISHED`, `ABORTED`), and receipts.
*   **Failure Behavior:** Reconciler scans for `PREPARED` or `COMMITTED` states on restart and drives them forward or rolls back[cite: 29].

### 2.2 Canonical State Store / Revision Store (ADR-003)
*   **Responsibility:** Single source of truth for the domain state and revision locks[cite: 28].
*   **Data Owned:** `CommittedSettlementStateRevision`, `ArtifactBaseStateRevision`, `SettlementProjectionRevision`[cite: 28].
*   **Inputs/Outputs:** Receives CAS updates from the Operation Journal during `COMMIT`.

### 2.3 Settlement Projection / Index Store (ADR-003)
*   **Responsibility:** Durable, rebuildable server-side representation of fungible assets (e.g., total steel, active pawns)[cite: 28].
*   **Data Owned:** Typed key-value pairs per settlement.
*   **Failure Behavior:** Can be rebuilt from the Artifact Base + `CommittedOperationLog` if corrupted[cite: 28].

### 2.4 Artifact Store (ADR-003)
*   **Responsibility:** Immutable blob storage for logical Settlement Materialization Packages (`.rws` or equivalent)[cite: 28].
*   **Data Owned:** The physical file bound to an `ArtifactRevision` and `ContentProfileFingerprint`[cite: 31].
*   **Failure Behavior:** Writes may fail or tear. The canonical DB pointer only advances after a successful write and hash verification[cite: 29].

### 2.5 Staged Result Store (ADR-004)
*   **Responsibility:** Temporary blob storage for Worker-produced outcomes *prior* to canonical commit[cite: 29].
*   **Data Owned:** Candidate artifacts and result manifests.
*   **Failure Behavior:** Orphaned blobs are garbage-collected if no `PREPARED` operation references them[cite: 29]. *(Not exercised in this slice)*.

### 2.6 Publication Outbox (ADR-004)
*   **Responsibility:** Durable queue for derivative side-effects (e.g., UI letters, socket broadcasts) post-commit[cite: 29].
*   **Failure Behavior:** At-least-once delivery; consumers must deduplicate using the `OperationId`[cite: 29].

### 2.7 Recovery Reconciler (ADR-004)
*   **Responsibility:** Background or startup scanner that sweeps the Operation Journal[cite: 29].
*   **Action:** Pushes `PREPARED` to `ABORTED` (if lock expired) or `COMMITTED` $\rightarrow$ `PUBLISHED` (via forward recovery)[cite: 29].

### 2.8 Writer Lease / Fencing Registry (ADR-007)
*   **Responsibility:** Manages the `WriterLeaseId` and `FencingGeneration` to guarantee 1-writer concurrency[cite: 32].
*   **Failure Behavior:** Revokes leases on timeout or explicit fencing[cite: 32].

### 2.9 Content / Profile Admission (ADR-006B)
*   **Responsibility:** Validates that incoming artifacts match the server's pinned `ContentProfileFingerprint`[cite: 31].

### 2.10 MaterializationManifest Builder (ADR-003)
*   **Responsibility:** Constructs the payload sent to an engine load, combining the base artifact with unapplied operations from the `CommittedOperationLog`[cite: 28].

### 2.11 EntityId Registry (ADR-003)
*   **Responsibility:** Allocates stable canonical IDs for cross-boundary objects[cite: 28].

## 3. Data Contract Sketches
*(Conceptual structures; not overfitted to final SQL schemas)*

**OperationRecord**
```text
UUID OperationId (PK)
Enum Type (e.g., TypedInventoryDeduction)
String PayloadHash
UUID ActorId
UUID TargetSettlementId
Long ExpectedSettlementRevision
String ContentProfileFingerprint
Enum State (RECEIVED, PREPARED, COMMITTED, PUBLISHED, ABORTED)
Timestamp CreatedAt