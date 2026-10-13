ADR-007_Ordinary_Settlement_Simulation_Authority_v4.md
Status: PROPOSED (Not Accepted)
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
During any HANDOFF_BARRIER, the server enforces strict admission rules to prevent data loss or duplicate writers:

Checkpoint Blocking: All normal ordinary checkpoints are blocked, except for the single designated barrier candidate.

Exclusive Writer: No second writer lease may be granted while a barrier is active.

Fencing: Checkpoints with stale FencingGenerations are immediately rejected.

Failure Fallback: If the client is dead, unresponsive, or fails to upload the final candidate, the server does not wait indefinitely. The lease is revoked, the client is fenced, and the server falls back to the last known committed canonical head to construct the next MaterializationManifest.

5. Online Server-Authored Delta Flow (DELTA_BARRIER)
To process an external server-authored mutation (e.g., online trade, tax) against a settlement currently being simulated by a leased writer, the server utilizes a DELTA_BARRIER. This flow is strictly separated into pre-commit and post-commit phases.

Phase A — Pre-Commit Barrier

The external operation is proposed, validated, and serialized on the Dedicated Server.

Ordinary checkpoint admission for the currently leased writer is immediately stopped.

If the Server operation fails to commit durably (e.g., a database constraint or internal error), the barrier is aborted. The writer's lease is maintained, and simulation resumes from the previous committed canonical head.

Phase B — Post-Commit Application

Once the server-authored operation is durably committed to the CommittedOperationLog and the canonical index, it is officially canonical regardless of client ACK.

Client ACK and local engine application of the delta are required only before that specific leased writer is permitted to resume ordinary simulation from the newly advanced ArtifactBaseStateRevision.

If the client fails to ACK, disconnects, or crashes after the server commit, the server immediately revokes the lease and fences the writer (incrementing the FencingGeneration).

Crucially, any subsequent rematerialization for that settlement (whether by the same client or a Tactical Worker) must use the new committed canonical head that includes the committed operation. It must never silently fall back to the pre-operation head.

Note: The exact durable transaction mechanics, retry logic, and compensation for partial failures are explicitly deferred to ADR-004.

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

Option B: Immediate hard stop on socket drop (prevents uncommittable progress, highly sensitive to micro-disconnects).

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