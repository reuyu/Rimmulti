ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v3.md
Status: ACCEPTED
Decision Owner: Master (GPT-5.6 Sol)
Project: WarEconomy / RimMulti
1. Context & Baseline
This ADR defines the canonical representation of a RimWorld settlement, stable cross-process identity, and layered provenance validation. The accepted architecture relies on the B2-lite baseline: an immutable engine-produced material-state artifact, a durable server-maintained index/projection, and ordered typed operations. Arbitrary field-level RimWorld object merging is strictly rejected.
2. Canonical Settlement Material-State Representation
The Canonical Settlement State consists of three structural pillars:
- Logical Settlement Materialization Artifact/Package: An immutable, hash-verified snapshot of the target settlement. The concrete storage format (e.g., target-only .rws or custom package) remains validation-required.
- Server Projection / Index: A strictly durable, server-side representation of essential data (e.g., wealth, active pawns). This is not merely an in-memory cache; it must be completely rebuildable and verifiable from the canonical artifact plus committed operations.
- Three-Layer Operation State: Operations altering the settlement (trades, tax, tactical ingress) must pass through a strict state machine to prevent checkpoint staling and data loss.
3. The Three-Layer Operation State
- PendingOperationQueue: Holds uncommitted requests/intents. Operations here are not canonical, do not increment the CommittedSettlementStateRevision, and are never materialized into engine state as if they were already committed.
- CommittedOperationLog: The durable, ordered log of canonical operations that have occurred after the current artifact base. Each operation receives a committed revision. These exist canonically before the next artifact fold/checkpoint.
- MaterializationManifest: The generated instruction set for a single engine materialization. It must contain:
  - The current artifact identity and ArtifactBaseStateRevision.
  - The CommittedOperationLog entries that occurred after the artifact watermark.
  - Authorized ingress/context data.
  - Expected revisions, clock, and lease metadata.
  - Constraint: It must never contain arbitrary pending requests from the PendingOperationQueue.
4. Revision Hierarchy & Watermark Rules
- ArtifactBaseStateRevision: Defines the applied-through watermark of an artifact.
  - Invariant: The artifact represents the exact canonical material state through revision R.
  - Deterministic Replay: A materialization replays only the committed operations from the CommittedOperationLog with a revision > R.
  - Artifact Fold Rule: When a new artifact is canonically accepted, its ArtifactBaseStateRevision advances to the exact CommittedSettlementStateRevision represented by that artifact fold.
- CommittedSettlementStateRevision: The unified canonical head revision. Increments only when operations or checkpoints are durably committed.
- ArtifactRevision: The identity/revision of the physical materialization package.
- SettlementProjectionRevision: The revision of the durable server projection/index.
- CheckpointParentRevision: The revision an incoming checkpoint claims to build upon.
5. Online Ordinary Economy & DELTA_BARRIER
To prevent online Auto Shop or Tax operations from silently incrementing the canonical head and rendering an online owner's ongoing simulation (and next checkpoint) stale, the architecture relies on the DELTA_BARRIER contract (jointly defined with ADR-007).
- Server-Authored Delta Flow: When an ordinary online mutation occurs, the server triggers a DELTA_BARRIER.
- The material mutation is serialized and bound to the current writer lease and FencingGeneration.
- Once authorized and durably committed by the Server, the operation becomes canonical independently of whether the current client remains connected.
- The current client must then either acknowledge and apply the committed authoritative delta, or be fenced/revoked and later rematerialize from the committed canonical head.
- Client acknowledgement controls writer resumption/base advancement, not whether the Server-authored operation is canonical.
- Only after the client has applied the committed delta and the lease base/watermark is advanced may ordinary progress checkpoints resume under that lease.
- If the client crashes or does not acknowledge, the operation remains committed; the old writer is fenced and the next materialization replays from the last artifact watermark plus committed operations.
- Note: The detailed durable failure, compensation, retry, and recovery mechanics for this flow are deferred to ADR-004.
6. Cross-Process Entity Identity
Native loadID values independently minted by multiple engines cannot serve as global identifiers.
- Canonical EntityId: A stable, server-issued identifier. Required for entities that are server-addressable, cross-boundary, or externally referenced/persistent (Factions, Pawns, Animals, traded items).
- Native loadID Rebinding: Native loadID is strictly per-materialization. It may be safely rebound upon loading into a different engine context, provided the EntityId mapping and canonical reference graph remain unique and collision-free. Canonical manifests reference EntityId only.
- Ephemeral Entities: Internal engine ephemeral objects remain native to the artifact and are not journaled for every split/merge/destroy unless they explicitly cross a canonical boundary.
7. Layered Hostile-Input Validation
Owner client checkpoints are untrusted, hostile input. Validation requires a three-layer approach:
1. Server / Static Preflight: Validates content/version manifest, XML schema, serialized type allowlist, size/complexity bounds, EntityId namespace integrity, and lease/provenance (CheckpointParentRevision).
2. Server-Controlled Engine Semantic Validation: Validates typed RimWorld references, load semantics, and deep graph integrity inside a sandboxed/controlled engine instance.
3. Canonical Acceptance: The checkpoint becomes canonical (and updates the CommittedSettlementStateRevision) only after passing both preflight and semantic validation.
8. Master Acceptance Clarification
ADR-003 is accepted with the following controlling interpretation:
1. A server-authored canonical operation never depends on an untrusted client ACK for its durability or canonical status.
2. DELTA_BARRIER ACK is a lease-resumption condition only.
3. Pending operations are never materialized as committed state.
4. Cross-boundary manifests reference canonical EntityId, never native loadID.
5. RimWorld-specific semantic validation may run in a server-controlled validation engine/sandbox, but canonical acceptance remains a Dedicated Server authority action.
6. Exact transaction/recovery mechanics remain ADR-004 scope.
Master Status: ACCEPTED