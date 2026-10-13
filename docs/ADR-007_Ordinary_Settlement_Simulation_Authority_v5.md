ADR-007_Ordinary_Settlement_Simulation_Authority_v4.md
Status: ACCEPTED — Core Authority/Lease Contract; G-Q1, G-Q2, G-Q6 remain OPEN
Decision Owner: Master (GPT-5.6 Sol)
Project: WarEconomy / RimMulti
1. Context & Baseline
   This ADR establishes execution authority, the lease state machine, and the handoff boundaries for ordinary settlement simulation. It ensures that the Dedicated Server retains final canonical custody while correctly delegating simulation via strict leases. It aligns fully with the ACCEPTED ADR-003 baseline, treating owner checkpoints as untrusted input and enforcing strict fencing to protect the canonical graph.
2. Writer Lease Binding Fields
   A valid writer lease grants submission authority, not truth authority. Every lease must strictly bind the following fields to ensure temporal and spatial consistency:
SettlementId / Material Scope: The specific settlement subgraph authorized for simulation.
LocalClockId: The temporal domain identity.
WriterLeaseId: The unique identifier of the active lease instance.
FencingGeneration: A monotonic, server-issued value used exclusively for canonical write fencing and rejecting stale data.
Holder Identity: The SessionEpoch (for clients) or WorkerGeneration (for Tactical Workers) owning the lease.
BaseCommittedSettlementStateRevision: The exact canonical head revision the writer is simulating from.
Allowed Write Scope: The boundaries of what the leased writer is permitted to mutate.
3. Lease State Machine
   The settlement execution topology transitions through explicit states to guarantee at most one active writer:
UNLEASED: Settlement is frozen; no engine is authorized to submit simulation progress.
LEASED_CLIENT: An online owner client holds the lease and submits ordinary checkpoints.
LEASED_WORKER: A Tactical Worker holds the lease for an active battle or visit.
DELTA_BARRIER: A transitional state triggered by server-authored online economy mutations (e.g., Auto Shop, Tax) to safely mutate the graph of an active writer.
HANDOFF_BARRIER: A transitional state during eviction (Client → Worker) or rematerialization (Worker → Client).
4. Barrier Admission & Handoff
   During any HANDOFF_BARRIER or DELTA_BARRIER, the server enforces strict admission rules to prevent data loss or duplicate writers.
For DELTA_BARRIER, a responsive current writer is first frozen at a barrier boundary and may submit exactly one designated barrier checkpoint candidate under the still-valid lease. If that checkpoint is accepted, the Server-authored operation is evaluated against the resulting committed canonical head. If the writer is unavailable, the Server must fence it and may proceed only against the last committed canonical head if the operation remains valid against that head; otherwise the operation is deferred or rejected according to its domain contract.
Checkpoint Blocking: All normal ordinary checkpoints are blocked, except for the single designated barrier candidate.
Exclusive Writer: No second writer lease may be granted while a barrier is active.
Fencing: Checkpoints with stale FencingGenerations are immediately rejected.
Failure Fallback: If the client is dead, unresponsive, or fails to upload the final candidate, the server does not wait indefinitely. The lease is revoked, the client is fenced, and the server falls back to the last known committed canonical head to construct the next MaterializationManifest.
5. Online Server-Authored Delta Flow (DELTA_BARRIER)
   To process an external server-authored mutation (e.g., online trade, tax) against a settlement currently being simulated by a leased writer, the server utilizes a DELTA_BARRIER. This flow is strictly separated into pre-commit and post-commit phases.
Phase A — Pre-Commit Barrier
The current writer is placed behind a DELTA_BARRIER; ordinary progress admission is stopped.
If the writer is responsive, it may submit exactly one designated barrier checkpoint candidate while the current lease/fencing generation is still valid. If accepted, this checkpoint becomes the new committed head before the external material mutation is evaluated.
The external operation is then proposed, authorized, validated, and serialized against the current committed canonical head.
If the Server-authored operation itself fails to commit durably, no operation effect becomes canonical. The barrier may clear and the writer may resume from the then-current committed head, which may already include an accepted barrier checkpoint.
Phase B — Post-Commit Application
Once the server-authored operation is durably committed to the CommittedOperationLog and canonical projection/index, it is canonical regardless of client ACK.
Client ACK and local engine application are required only before that leased writer may resume ordinary simulation.
After successful application, the lease's BaseCommittedSettlementStateRevision advances to the new CommittedSettlementStateRevision. ArtifactBaseStateRevision changes only when a new artifact fold/checkpoint that actually contains that state is canonically accepted.
If the client fails to ACK, disconnects, or crashes after Server commit, the Server revokes/fences that writer. The committed operation remains canonical.
Any subsequent rematerialization—by the same client or a Tactical Worker—must reconstruct from the current canonical head: artifact state through ArtifactBaseStateRevision plus every committed operation after that watermark. It must never silently fall back to the pre-operation head.
Note: The exact durable transaction mechanics, retry logic, compensation, and recovery procedure are explicitly deferred to ADR-004.
6. Master Decisions Required (Explicitly OPEN)
   The following decisions define the product bounds of ordinary simulation and must not be silently resolved by implementation:
G-Q1: Multi-Settlement Topology
Option A: Player-scoped clock.
Option B: One active settlement per client.
Option C: Per-map clock virtualization.
Option D: Separate execution islands / remote ordinary simulation.
G-Q2: Ordinary Simulation Anti-Cheat & Residual Trust Posture
Option A: Plausibility bounds & audit (accepting residual cheat risk).
Option B: Server-hosted ordinary simulation.
G-Q6: Checkpoint Loss Window & Disconnect Grace
Option A: Strict upload interval (bounds data loss, increases network overhead).
Option B: Immediate server-side lease revocation/fencing on socket drop. The disconnected client may continue simulating locally, but all subsequent progress is uncommittable unless a new authorized recovery/rematerialization flow admits it. This is highly sensitive to micro-disconnects.
Shared Terminology Contract
This document strictly relies on the terminology defined and owned by ACCEPTED ADR-003, with exact parity required for:
LocalClockId
WriterLeaseId
FencingGeneration
CommittedSettlementStateRevision
ArtifactRevision
ArtifactBaseStateRevision
SettlementProjectionRevision
CheckpointParentRevision
PendingOperationQueue
CommittedOperationLog
MaterializationManifest
EntityId
Contract Contradictions Check: Following the explicit Phase A and Phase B separation of the DELTA_BARRIER, there are no remaining contract contradictions with ADR-001, ACCEPTED ADR-003, or ADR-006A. All execution and canonical state boundaries are strictly partitioned and safely fenced.
7. Master Acceptance Clarifications
The following interpretations are controlling:
1. Canonical custody remains on the Dedicated Server. A writer lease grants simulation/submission authority only.
2. All barriers are server admission barriers. A stale or disconnected client may continue local computation, but cannot publish after fencing.
3. DELTA_BARRIER preserves current committed progress when possible. A responsive writer may provide one designated barrier checkpoint before the external operation is evaluated.
4. Client ACK never determines canonicality of an already committed Server-authored operation. ACK only gates resumption of that writer lease.
5. Lease base revision is not artifact watermark. BaseCommittedSettlementStateRevision advances when the writer is synchronized to the new canonical head. ArtifactBaseStateRevision advances only on a canonical artifact fold.
6. Post-commit failure never reverts the committed operation. The writer is fenced and later rematerialized from artifact watermark + committed operation log.
7. G-Q1, G-Q2, and G-Q6 remain OPEN Decision Requests. Their unresolved status limits dependent Production topology/policy, but does not invalidate this accepted core lease/handoff contract.
Master Status: ACCEPTED