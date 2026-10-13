# Shared_Settlement_State_Pipeline_Design_02.md

**Status:** DESIGN PROPOSAL — NOT Production Authorization
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Objective & Scope
This document specifies the implementable architecture and data contracts for the first Production vertical slice of the Shared Settlement State Pipeline. It synthesizes the accepted upstream contracts (ADR-001, 003, 004, 006A/B, 007, 008) into a cohesive sequence. 

**First Vertical Slice Strategy:**
To strictly prevent policy leakage into infrastructure, the first slice will use a **policy-neutral internal pipeline probe operation**. It will *not* use Tax, Auto-Shop, or Faction Join semantics because those depend on unresolved Master decisions (G-Q8, G-Q9, TBD-05). The probe operation (`TEST_TYPED_NOOP_SYNC`) will be executed entirely in Production infrastructure to prove `OperationId` idempotency, revision CAS, `PREPARED` locking, DB commits, outbox delivery, and restart recovery. It will advance the `CommittedSettlementStateRevision` but perform no actual RimWorld semantic mutation.

## 2. Component Architecture

### 2.1 Operation Journal (ADR-004)
*   **Authoritative Data:** `OperationId`, Payload Hash, Actor, Expected Revisions, State (`RECEIVED`, `PREPARED`, `COMMITTED`, `PUBLISHED`, `ABORTED`, `REPAIR_REQUIRED`).
*   **State Type:** Strictly Durable.
*   **Inputs/Outputs:** Receives intent; outputs terminal receipt or drives `COMMITTED` side-effects.
*   **Restart Behavior:** Scanned by Reconciler. `PREPARED` $\rightarrow$ Abort (or autonomous completion); `COMMITTED` $\rightarrow$ Forward Recovery.

### 2.2 Canonical State / Revision Store (ADR-003)
*   **Authoritative Data:** `CommittedSettlementStateRevision`, `ArtifactBaseStateRevision`, `SettlementProjectionRevision`.
*   **State Type:** Strictly Durable.
*   **Inputs/Outputs:** Receives CAS atomic updates from the Journal.
*   **Restart Behavior:** Source of truth for identifying the canonical material head.

### 2.3 Settlement Projection / Index Store (ADR-003)
*   **Authoritative Data:** Durable, typed extraction of fungible assets (e.g., wealth, item counts). *Derived* from Artifact + Operations, but durable for immediate query.
*   **State Type:** Durable (Rebuildable).
*   **Inputs/Outputs:** Updated atomically with `COMMITTED` operations or rebuilt from `Artifact`.

### 2.4 Artifact Store (ADR-003)
*   **Authoritative Data:** The physical `.rws` or logical materialization packages.
*   **State Type:** Durable.
*   **Restart Behavior:** Orphaned files (unreferenced by an `ArtifactRevision` or staged commit) are ignored or GC'd.

### 2.5 Staged Result Store (ADR-004)
*   **Authoritative Data:** Immutable, non-canonical packages produced by Workers *prior* to canonical commit.
*   **State Type:** Durable.
*   **Restart Behavior:** Retained until the referencing `COMMITTED` operation is successfully `PUBLISHED`.

### 2.6 Publication Outbox (ADR-004)
*   **Authoritative Data:** Post-commit side-effects (e.g., client UI letters, network broadcasts).
*   **State Type:** Durable (Derived).
*   **Restart Behavior:** At-least-once replay of un-ACK'd messages.

### 2.7 Recovery Reconciler (ADR-004)
*   **Authoritative Data:** None (Worker process).
*   **State Type:** Ephemeral.
*   **Inputs/Outputs:** Scans Journal $\rightarrow$ Triggers Aborts, Promotion, or Outbox dispatches.

### 2.8 Writer Lease / Fencing Registry (ADR-007)
*   **Authoritative Data:** `WriterLeaseId`, `FencingGeneration`, Holder Identity, Expiry/State.
*   **State Type:** Durable.
*   **Restart Behavior:** Restores fencing boundaries. Expired active leases revert to `UNLEASED`.

### 2.9 Content / Profile Admission (ADR-006B)
*   **Authoritative Data:** `ContentProfileFingerprint`, allowed schema/types.
*   **State Type:** Durable configuration.

### 2.10 Semantic Validation Adapter (ADR-006B)
*   **Authoritative Data:** None (Validator Engine).
*   **State Type:** Ephemeral.
*   **Inputs/Outputs:** Takes staged artifact + required `ContentProfileFingerprint` $\rightarrow$ Outputs Pass/Fail (Quarantine).

### 2.11 MaterializationManifest Builder (ADR-003)
*   **Authoritative Data:** None (Assembler).
*   **Inputs/Outputs:** Combines Artifact Base + `CommittedOperationLog` (post-watermark) + `ContentBinding` $\rightarrow$ JSON payload for Engine load.

### 2.12 EntityId Registry (ADR-003)
*   **Authoritative Data:** Stable `EntityId` mapping to Factions/Caravans/Pawns.
*   **State Type:** Durable.
*   **Inputs/Outputs:** Generates namespaces for leased writers.

### 2.13 Audit / Commit Receipt Surface (ADR-001)
*   **Authoritative Data:** EventID, immutable transaction outcome summary.
*   **State Type:** Durable.

## 3. Preserving Typed vs. Staged Recovery Paths

The transaction architecture explicitly diverges after `COMMITTED` based on the operation class:

*   **Path A (Typed Operation):** The domain `COMMITTED` record contains explicit typed mutations (e.g., deduct 50 steel). Recovery = Load base artifact matching `ArtifactBaseStateRevision` + replay the typed `CommittedOperationLog` up to `CommittedSettlementStateRevision`.
*   **Path B (Staged Material Result):** The domain `COMMITTED` record references a durable staged result manifest. Recovery = Identify the staged candidate $\rightarrow$ Promote/Publish it $\rightarrow$ Advance `ArtifactBaseStateRevision`. If the file is corrupt post-commit, state becomes `REPAIR_REQUIRED`.

## 4. `PREPARED` Recovery Policy
A transaction at `PREPARED` is a durable lock, strictly separated from writer fencing.
*   **Policy:** 
    1.  If the Server crashes and restarts to find a `PREPARED` record that lacks the complete required facts/staged candidate $\rightarrow$ `ABORTED`.
    2.  If the Server finds a *complete* durable `PREPARED` package and the operation policy (e.g., Server-authored periodic tick) is autonomous $\rightarrow$ Server resumes to `COMMITTING`.
    3.  If the policy explicitly requires live multi-party consent (e.g., P2P Trade) that was lost $\rightarrow$ `ABORTED`.

## 5. Data Contracts

**`OperationRecord`**
```text
UUID OperationId (PK)
String PayloadHash
String OperationType (e.g., "TEST_TYPED_NOOP_SYNC", "STAGED_TACTICAL_PUBLISH")
UUID ActorId
UUID TargetScopeId (SettlementId or CaravanId)
Long ExpectedDestinationRevision
String ContentProfileFingerprint
Enum State (VALIDATING, PREPARED, COMMITTED, PUBLISHED, ABORTED, REPAIR_REQUIRED)
UUID StagedResultManifestId (Nullable)
Timestamp CreatedAt
