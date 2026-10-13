# ADR-007_Ordinary_Settlement_Simulation_Authority_v3.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR establishes execution authority, the lease state machine, and the handoff boundaries for ordinary settlement simulation. It ensures that the Dedicated Server retains final canonical custody while correctly delegating simulation via strict leases.

## 2. Writer Lease Binding Fields
A valid writer lease grants submission authority, not truth authority. Every lease must strictly bind the following fields:
1.  **SettlementId / Material Scope:** The specific settlement subgraph authorized for simulation.
2.  **`LocalClockId`:** The temporal domain identity.
3.  **`WriterLeaseId`:** The unique identifier of the active lease instance.
4.  **`FencingGeneration`:** A monotonic, server-issued value used for canonical write fencing and rejecting stale data.
5.  **Holder Identity:** The `SessionEpoch` (for clients) or `WorkerGeneration` (for Tactical Workers) owning the lease.
6.  **`BaseCommittedSettlementStateRevision`:** The exact canonical head revision the writer is simulating from.
7.  **Allowed Write Scope:** The boundaries of what the leased writer is permitted to mutate.

## 3. Lease State Machine
The settlement execution topology transitions through explicit states:
*   **`UNLEASED`:** Settlement is frozen; no engine is authorized to submit simulation progress.
*   **`LEASED_CLIENT`:** An online owner client holds the lease and submits ordinary checkpoints.
*   **`LEASED_WORKER`:** A Tactical Worker holds the lease for an active battle or visit.
*   **`DELTA_BARRIER`:** A transitional state triggered by server-authored online economy mutations (Auto Shop / Tax).
*   **`HANDOFF_BARRIER`:** A transitional state during eviction (Client → Worker) or rematerialization (Worker → Client).

## 4. Barrier Admission & Handoff
During any `DELTA_BARRIER` or `HANDOFF_BARRIER`, the server enforces strict admission rules:
*   **Checkpoint Blocking:** All normal ordinary checkpoints are blocked, except for the single designated barrier candidate.
*   **Exclusive Writer:** No second writer lease may be granted while a barrier is active.
*   **Fencing:** Checkpoints with stale `FencingGeneration`s are immediately rejected.
*   **Failure Fallback:** If the client is dead, unresponsive, or fails to upload the final candidate, the server does *not* wait indefinitely. The lease is revoked, the client is fenced, and the server falls back to the *last known committed canonical head* to construct the next `MaterializationManifest`.

## 5. Online Server-Authored Delta Flow
Integrated with ADR-003, when an online settlement receives a canonical external mutation (e.g., Tax):
1.  The state transitions to `DELTA_BARRIER`.
2.  The server generates the delta and binds it to the current `WriterLeaseId` and `FencingGeneration`.
3.  The client must acknowledge application of the delta.
4.  Upon application, the writer's base watermark is advanced, the barrier clears, and `LEASED_CLIENT` resumes.
5.  Failure to apply results in a fallback to the last committed head and client rematerialization.

## 6. Master Decisions Required (Explicitly OPEN)
The following decisions must not be silently resolved by implementation:

*   **G-Q1: Multi-Settlement Topology**
    *   *Option A:* Player-scoped clock.
    *   *Option B:* One active settlement per client.
    *   *Option C:* Per-map clock virtualization.
    *   *Option D:* Separate execution islands / remote ordinary simulation.
*   **G-Q2: Ordinary Simulation Anti-Cheat & Residual Trust Posture**
    *   *Option A:* Plausibility bounds & audit (accepting residual cheat risk).
    *   *Option B:* Server-hosted ordinary simulation.
*   **G-Q6: Checkpoint Loss Window & Disconnect Grace**
    *   *Option A:* Strict upload interval.
    *   *Option B:* Immediate hard stop on socket drop.