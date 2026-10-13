# EB_Live_Barrier_Delta_Acceptance_Brief_01.md

**Status:** DECISION / TRACEABILITY BRIEF — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Actors and State Definitions

To execute a live material mutation safely, the architecture must distinctively track the following identities and revisions without collapsing them:

*   **Dedicated Server Domain Authority:** The absolute source of truth for transactions, political boundaries, and canonical ownership.
*   **Owner Client Simulation Authority:** The transient right granted to an owner to advance the material simulation ($L_s$) and propose checkpoints.
*   **WriterLease / LeaseGeneration:** The server-side lock binding simulation authority to a specific execution island for a specific duration.
*   **Execution Island / LocalClock Domain:** The physical RimWorld engine runtime instance tracking a discrete `LocalClockId` ($L_s$).
*   **Settlement Scope Set:** The list of `SettlementId`s currently materialized and actively ticking within the execution island.
*   **SessionEpoch:** The ephemeral transport/network connection identifier representing a continuous socket state.
*   **FencingGeneration:** A strict monotonic counter used to fence out stale writers. It advances *only* upon explicit lease revocation, replacement, or incarnation change—not on ordinary commits or transient disconnects.
*   **CommittedSettlementStateRevision:** The canonical database revision of the Settlement's material and conceptual state.
*   **ArtifactBaseStateRevision:** The physical fingerprint/identity of the `.rws` fold that the client is currently building upon.
*   **Pending Typed Delta / `OperationId`:** The idempotent transaction identifier tracking the exact server-authored mutation (e.g., an Auto-Shop transfer).

## 2. Barrier State Machine

The ordinary client `DELTA_BARRIER` lifecycle operates as a strict state machine:

1.  **`ACTIVE`**: Client is simulating normally.
2.  **`BARRIER_REQUESTED`**: Server issues halt command with `OperationId`.
3.  **`QUIESCING`**: Client receives command, halts mutation, flushes pending jobs.
4.  **`BARRIER_ACKED`**: Client confirms halt to Server. Server locks lease state.
5.  **`DELTA_APPLYING`**: Server/Client applies the material mutation to the frozen state.
6.  **`VALIDATING`**: The candidate mutation is staged and semantically validated.
7.  **`RESUMING`**: Canonical commit succeeds, Server broadcasts new `ArtifactBaseStateRevision` and releases lock.
8.  **`ACTIVE`**: Client resumes simulation.

**Failure Branches:**
*   **`SUSPENDED_GRACE`**: Socket drops during any phase. State machine pauses until reconnect or timeout.
*   **`REVOKED/FENCED`**: Timeout expires, lease is transferred, or a stale client attempts illegal progress. Transaction aborts.
*   **`REPAIR_REQUIRED`**: Enters *only* if a catastrophic failure occurs post-commit (after Domain Authority has updated, but the `RESUMING` artifact fold is permanently corrupted).

## 3. Quiescence Definition

When transitioning to `BARRIER_ACKED`, the client must absolutely halt:
*   Native engine ticks ($G$) and LocalClock advancement ($L_s$) for the scoped execution island.
*   Processing of queued jobs, AI routines, or player commands that mutate the scoped `SettlementAssetGraph`.
*   Submission of any further `Checkpoint` publications.
*   Local material mutations.

**Permitted Activity:**
*   UI rendering, camera panning, opening static menus, inspecting entity stats.

**Server-Side Evidence:**
Client ACK is not blindly trusted. The Server enforces quiescence by dropping any checkpoint or material command arriving from that `WriterLease` after the `BARRIER_REQUESTED` timestamp, strictly holding the lease in a locked state until `RESUMING`.

## 4. Typed Delta Boundary

The mechanism for applying the mutation must be chosen from the following:

| Characteristic | A. Engine-Free Typed Delta | B. Server Engine Host Transform | C. Forced Handoff / Rematerialization |
| :--- | :--- | :--- | :--- |
| **Authority Source** | Server XML Codec | Server headless RimWorld instance | Server (Client acts as dumb viewer) |
| **Base Revision Binding** | Client memory / Staged patch | Server re-loads `ArtifactBaseStateRevision` | Server materializes, Client downloads |
| **EntityId / Rebinding** | High risk (requires XML heuristics) | Native engine stack merging/splitting | Native engine handles perfectly |
| **Application-Totality**| Validated via strict schema parser | Validated via `Load()` and semantic check | Validated via `Load()` |
| **Resume Contract** | Client receives fast patch | Client receives delta or full state sync | Client endures full loading screen |

*(Note: Direct, arbitrary XML mutation without schema validation is strictly prohibited.)*

## 5. Revision Ordering

The exact intended sequence for a successful barrier is:
1.  Barrier requested targeting the client's current `ArtifactBaseStateRevision` ($R$).
2.  Client achieves quiescence and issues ACK.
3.  Mutation is applied; staged result/delta validation occurs.
4.  Canonical DB commit advances `CommittedSettlementStateRevision` (Domain Authority).
5.  Material application / artifact fold is finalized.
6.  Client is issued a `RESUMING` command with the new canonical state hash.
7.  **Crucial Rule:** `FencingGeneration` **does not increment** here. The same client continues to hold the same `WriterLease`.

## 6. Race Matrix

| Scenario | Resolution |
| :--- | :--- |
| Command sent post-request, pre-ACK | Processed normally or queued by client. |
| Command arrives at Server post-ACK | Server rejects/drops as barrier violation. |
| Disconnect during Quiesce | Enters `SUSPENDED_GRACE`. Barrier pauses. |
| Reconnect (same `SessionEpoch`) | `SUSPENDED_GRACE` ends, Barrier resumes. |
| New `SessionEpoch` arrives | Evaluated for lease transfer. If transferring, old lease is `REVOKED`, `FencingGeneration` increments, Barrier aborts. |
| Tactical Takeover Request | Queued until barrier finishes, or triggers `REVOKE`. |
| Timeout pre-ACK | Lease is `REVOKED/FENCED`. Transaction aborts. |
| Timeout post-stage, pre-commit | Transaction aborts. Lease `REVOKED`. |
| Commit succeeds, disconnect pre-resume | Operation committed. Client enters `SUSPENDED_GRACE`. On reconnect, client must rebase/re-download. |
| Client resumes from stale artifact | Server rejects next checkpoint via `CheckpointParentRevision`. |
| Duplicate barrier `OperationId` | Pipeline intercepts via idempotency cache. |
| Two concurrent server deltas | Command router queues sequentially. |
| Ownership transfer during barrier | Epoch increments. Barrier transaction fails validation and aborts. |

## 7. G-Q6 Interaction

The sequence `ACTIVE` $\rightarrow$ `SUSPENDED_GRACE` $\rightarrow$ `{ACTIVE, REVOKED/FENCED}` remains absolute.
*   A loss of transport (socket drop) does not immediately grant a replacement writer or advance `FencingGeneration`.
*   If transport is lost during an active `DELTA_BARRIER`, the barrier execution suspends.
*   If `SUSPENDED_GRACE` expires, explicit `REVOKE` is triggered. The server aborts the transaction (if pre-commit) or marks the new artifact canonical and forces the client to download it upon eventual replacement.

## 8. LocalClock / G-Q1 Boundary

E-B must operate under the current Vanilla-first hypothesis without solving the final multi-settlement topology:
*   The scoped execution island's local progression must completely freeze.
*   Upon resume, there must be no "catch-up burst" of ticks (preventing physics/job chaos).
*   Applying the delta must not inadvertently advance the engine state of unrelated settlements running on the same island (if G-Q1 multi-map is active).
*   Global `TicksGame` contamination remains a separate architectural blocker; E-B must document if the barrier interacts poorly with global tick caches.

## 9. E-B Runtime Evidence Plan (PoC Battery)

Before authorizing full online mutation implementation, the following minimal PoC battery must pass (using a narrow, harmless delta like a Silver decrement):
1.  **Live Delta Application:** Live owner client ticking $\rightarrow$ Server requests Barrier $\rightarrow$ Client ACKs $\rightarrow$ Server deducts 100 Silver $\rightarrow$ Client resumes with exact result.
2.  **Queued Command Integrity:** Queue player commands immediately around the barrier edge. Verify they execute cleanly upon `RESUMING` without crashing the UI.
3.  **Transport Resilience:** Trigger disconnect/reconnect (same epoch) exactly during `QUIESCING`. Verify seamless recovery.
4.  **Timeout / Revoke Path:** Force an ACK timeout. Verify the transaction aborts and the lease is strictly `FENCED`.
5.  **Tick Verification:** Use internal logs to prove zero `LocalClockId` ticks occurred between ACK and RESUME.
6.  **Scope Isolation:** If possible, run two settlements in one client. Prove the barrier targets only the scoped `SettlementId`.
7.  **Idempotency:** Replay the exact barrier network packet. Verify duplicate rejection.

## 10. Stop Line

**Narrowest Proof Boundary:**
The E-B slice ends when Dev A and Sol can reliably prove that a live RimWorld client can completely freeze its simulation, accept a narrow, server-authored state mutation (e.g., deducting an item), and cleanly resume execution without breaking active pawn jobs, global caches, or pipeline revisions.

**Explicit Non-Goals:**
This boundary does NOT authorize or imply completion of:
*   Full ordinary multiplayer Production.
*   Final G-Q1 (Multi-Settlement Topology) resolution.
*   Final G-Q6 (Grace Timeouts) resolution.
*   Actual Trade or Tax execution semantics.
*   Remote Tactical Worker Production.