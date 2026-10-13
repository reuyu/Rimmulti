# ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v3.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the canonical representation of a RimWorld settlement, stable cross-process identity, and layered provenance validation. The accepted architecture relies on the B2-lite baseline: an immutable engine-produced material-state artifact, a durable server-maintained index/projection, and ordered typed operations. Arbitrary field-level RimWorld object merging is strictly rejected.

## 2. Canonical Settlement Material-State Representation
The Canonical Settlement State consists of three structural pillars:
*   **Logical Settlement Materialization Artifact/Package:** An immutable, hash-verified snapshot of the target settlement. The concrete storage format (e.g., target-only `.rws` or custom package) remains validation-required.
*   **Server Projection / Index:** A strictly durable, server-side representation of essential data (e.g., wealth, active pawns). This is *not* merely an in-memory cache; it must be completely rebuildable and verifiable from the canonical artifact plus committed operations.
*   **Three-Layer Operation State:** Operations altering the settlement (trades, tax, tactical ingress) must pass through a strict state machine to prevent checkpoint staling and data loss.

## 3. The Three-Layer Operation State
*   **`PendingOperationQueue`:** Holds uncommitted requests/intents. Operations here are *not* canonical, do *not* increment the `CommittedSettlementStateRevision`, and are never materialized into engine state as if they were already committed.
*   **`CommittedOperationLog`:** The durable, ordered log of canonical operations that have occurred *after* the current artifact base. Each operation receives a committed revision. These exist canonically before the next artifact fold/checkpoint.
*   **`MaterializationManifest`:** The generated instruction set for a single engine materialization. It must contain:
    *   The current artifact identity and `ArtifactBaseStateRevision`.
    *   The `CommittedOperationLog` entries that occurred *after* the artifact watermark.
    *   Authorized ingress/context data.
    *   Expected revisions, clock, and lease metadata.
    *   *Constraint:* It must never contain arbitrary pending requests from the `PendingOperationQueue`.

## 4. Revision Hierarchy & Watermark Rules
*   **`ArtifactBaseStateRevision`:** Defines the applied-through watermark of an artifact. 
    *   *Invariant:* The artifact represents the exact canonical material state through revision *R*.
    *   *Deterministic Replay:* A materialization replays *only* the committed operations from the `CommittedOperationLog` with a revision > *R*.
    *   *Artifact Fold Rule:* When a new artifact is canonically accepted, its `ArtifactBaseStateRevision` advances to the exact `CommittedSettlementStateRevision` represented by that artifact fold.
*   **`CommittedSettlementStateRevision`:** The unified canonical head revision. Increments only when operations or checkpoints are durably committed.
*   **`ArtifactRevision`:** The identity/revision of the physical materialization package.
*   **`SettlementProjectionRevision`:** The revision of the durable server projection/index.
*   **`CheckpointParentRevision`:** The revision an incoming checkpoint claims to build upon.

## 5. Online Ordinary Economy & `DELTA_BARRIER`
To prevent online Auto Shop or Tax operations from silently incrementing the canonical head and rendering an online owner's ongoing simulation (and next checkpoint) stale, the architecture relies on the `DELTA_BARRIER` contract (jointly defined with ADR-007).
*   **Server-Authored Delta Flow:** When an ordinary online mutation occurs, the server triggers a `DELTA_BARRIER`.
*   The material mutation is serialized and bound to the current writer lease and `FencingGeneration`.
*   The client is forced to either acknowledge and apply the authoritative delta, or rematerialize.
*   Only after the client confirms application does the server move the writer's accepted base/watermark and resume accepting ordinary progress checkpoints.
*   *Note:* The detailed durable failure and compensation mechanics for this flow are deferred to ADR-004.

## 6. Cross-Process Entity Identity
Native `loadID` values independently minted by multiple engines cannot serve as global identifiers.
*   **Canonical `EntityId`:** A stable, server-issued identifier. Required for entities that are server-addressable, cross-boundary, or externally referenced/persistent (Factions, Pawns, Animals, traded items).
*   **Native `loadID` Rebinding:** Native `loadID` is strictly per-materialization. It may be safely rebound upon loading into a different engine context, provided the `EntityId` mapping and canonical reference graph remain unique and collision-free. Canonical manifests reference `EntityId` only.
*   **Ephemeral Entities:** Internal engine ephemeral objects remain native to the artifact and are *not* journaled for every split/merge/destroy unless they explicitly cross a canonical boundary.

## 7. Layered Hostile-Input Validation
Owner client checkpoints are untrusted, hostile input. Validation requires a three-layer approach:
1.  **Server / Static Preflight:** Validates content/version manifest, XML schema, serialized type allowlist, size/complexity bounds, `EntityId` namespace integrity, and lease/provenance (`CheckpointParentRevision`).
2.  **Server-Controlled Engine Semantic Validation:** Validates typed RimWorld references, load semantics, and deep graph integrity inside a sandboxed/controlled engine instance.
3.  **Canonical Acceptance:** The checkpoint becomes canonical (and updates the `CommittedSettlementStateRevision`) *only* after passing both preflight and semantic validation.