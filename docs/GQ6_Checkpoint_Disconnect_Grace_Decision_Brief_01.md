# GQ6_Checkpoint_Disconnect_Grace_Decision_Brief_01.md

**Status:** DECISION BRIEF — DO NOT RESOLVE G-Q6
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Objective
This brief defines the policy and architectural option space for G-Q6: determining the grace period, data-loss window, and recovery mechanics when an owner-client holding an ordinary Settlement `WriterLeaseId` disconnects or crashes. It maintains strict adherence to ADR-003 (Canonical Custody) and ADR-007 (Writer Fencing).

## 2. Disconnect Scenario Analysis

The architecture must distinctively handle various failure modes, as the Server cannot always discern the client's physical state from a dropped socket:

*   **Clean Voluntary Disconnect:** The client intentionally logs out. The client uploads a final checkpoint, the Server acknowledges, and the lease transitions cleanly to `UNLEASED`. Zero data loss.
*   **Transient Network Loss:** The client process is healthy, but the socket drops (e.g., Wi-Fi flap). The client retains the uncommitted material state in memory and may attempt to reconnect.
*   **Client Process / Machine Crash:** The client game or OS terminates instantly. The in-memory material state is permanently destroyed. The Server only sees a socket drop. All progress since the last accepted checkpoint is irrevocably lost.
*   **Checkpoint Upload In Flight:** The socket drops while transmitting a `.rws` package. The Server possesses an incomplete or corrupted file. It must be discarded.
*   **`DELTA_BARRIER` In Flight:** The Server has frozen the client for a barrier but the socket drops before the client can upload the designated barrier checkpoint. The Server must fall back to the last committed canonical head.
*   **Server-Authored Operation Committed, Client ACK Absent:** The Server has successfully executed a `COMMITTED` transaction (e.g., Offline Tax) against the canonical database, but the client disconnects before applying the delta or ACKing. The operation remains canonical; the client must be fenced and forced to rematerialize upon reconnect.
*   **Reconnect (Same PlayerId, New SessionEpoch):** A legitimate player restarts their game and reconnects. The Server must issue a new `SessionEpoch` and a new `FencingGeneration`, permanently invalidating the old lease.
*   **Stale Old Process Reconnecting:** A "zombie" client process regains network connectivity after the Server has already issued a replacement `WriterLeaseId` to a new session (or Tactical Worker). The old process must be violently rejected by the `FencingGeneration` mismatch.

## 3. Candidate Grace Policies (Option Space)

### Policy 1: Immediate Revoke & Fence (Zero Grace)
*   **Mechanic:** The exact millisecond the socket drops, the `WriterLeaseId` is revoked, and the `FencingGeneration` is advanced.
*   **Data-Loss Window:** High. All progress since the last periodic autosave/checkpoint is lost on any micro-disconnect.
*   **Stale-Writer Risk:** Zero.
*   **Exploit Surface:** None.
*   **Server Complexity:** Very Low.
*   **Relation to ADR-007 / ADR-004:** Cleanest integration. Barrier failures are resolved instantly.

### Policy 2: Short Configurable Reconnect Grace (Simulation Paused)
*   **Mechanic:** Socket drop starts a timer (e.g., 30 seconds). The client *must* pause its local simulation upon detecting the drop. If it reconnects with the same `SessionEpoch` before expiry, the lease continues. If expiry hits, the lease is revoked.
*   **Data-Loss Window:** Low for network flaps; still loses data on hard process crashes.
*   **Stale-Writer Risk:** Mitigated by the strict timer and `SessionEpoch` validation.
*   **User Experience:** Highly tolerant of unstable network connections.
*   **Exploit Surface:** Client could intentionally throttle connection to buy "frozen time" during critical events, though ADR-007 limits this.
*   **Relation to ADR-007:** Delays `DELTA_BARRIER` fallback logic until the grace timer expires.

### Policy 3: Resumable Lease Token Bound to Immutable Epoch
*   **Mechanic:** A disconnected client retains a cryptographic or secure lease token. They may reconnect and resume at *any* time (e.g., 5 minutes later) provided no other process (like a Tactical Worker) has requested and obtained a lease for that Settlement.
*   **Data-Loss Window:** Very Low.
*   **Stale-Writer Risk:** High, requires perfect `FencingGeneration` implementation to avoid race conditions.
*   **User Experience:** Excellent for client crashes, allowing recovery if the game can somehow recover state, or just pausing the world safely.
*   **Server Complexity:** High. Requires tracking "suspended" leases vs "active" leases.

### Policy 4: Server-Side Emergency Handoff
*   **Mechanic:** Upon client disconnect, the Server immediately spins up a headless Tactical Worker to load the last `ArtifactBaseStateRevision` and take over the simulation to prevent the Settlement from pausing.
*   **Data-Loss Window:** Loses the client's uncommitted progress, but world time continues seamlessly.
*   **Server Complexity / Cost:** Extreme. Spawning full RimWorld instances on socket drops is a massive DoS vector.
*   **Relation to G-Q1 / G-Q2:** Fully shifts ordinary simulation to server-hosted models.

### Policy 5: Hybrid Policy by Operation/Barrier State
*   **Mechanic:** Variable grace. If the client is in a normal `LEASED_CLIENT` state, grant a 30-second grace. If the client drops while locked in a `DELTA_BARRIER` waiting for a server-authored commit, grant 0 seconds grace (immediate fallback to prevent locking the global transaction).
*   **Data-Loss Window:** Variable.
*   **Server Complexity:** Medium-High. Requires the lease state machine to dictate network timeout behaviors.

## 4. Hard Architecture Invariants

Regardless of the policy chosen, the following rules must not be weakened:
1.  **No Timeout-Only Dual Writer:** A new lease may *never* be granted while an old lease is theoretically alive. `FencingGeneration` must strictly advance before a new writer is admitted.
2.  **Server Retains Canonical Custody:** The untrusted client never owns final truth.
3.  **No Rollback of Committed Server Operations:** If an ADR-004 operation reaches `COMMITTED`, it is canonical. It is *never* rolled back merely because the client failed to ACK or upload a checkpoint.
4.  **Absolute Fencing:** An old `SessionEpoch` or stale `FencingGeneration` must be rejected with 100% reliability if a replacement writer exists.
5.  **Artifact Watermark Immutability:** `ArtifactBaseStateRevision` changes *only* when an accepted materialization/fold successfully completes static and semantic validation (ADR-003). It never advances implicitly.
6.  **No Hidden Simulation Progress:** Grace periods must not grant the client the right to simulate offline indefinitely and bulk-upload later.

## 5. Evidence Plan (Runtime Probes)

Before integrating ordinary clients into Production, Dev A and Sol must execute these specific fault probes against the Server Pipeline:
1.  **Cable/Socket Loss + Reconnect:** Kill the TCP connection. Reconnect *before* grace expiry (verify resumption) and *after* grace expiry (verify hard rejection).
2.  **Process Kill at Ordinary Tick:** `kill -9` the client. Ensure the server gracefully recovers the lease state after the configured timeout without deadlocking the `SettlementId`.
3.  **Kill During Checkpoint Upload:** Terminate client mid-upload. Verify the Server's artifact parser rejects the torn file and does not advance `ArtifactBaseStateRevision`.
4.  **Kill After Server `COMMITTED` before ACK:** Inject a Server-authored operation (e.g., tax). Terminate the client immediately after the DB `COMMITTED` log but before the socket dispatches. Reconnect the client and verify it is forced to rematerialize the new state.
5.  **Stale Checkpoint Publication:** Connect Client A, simulate. Kill Client A's connection. Server grants lease to Worker B. Client A reconnects and attempts to upload an old checkpoint. Verify immediate strict rejection via `FencingGeneration`.
6.  **Repeated Flap/Reconnect:** Rapidly drop and reconnect the socket 50 times to test for memory leaks or lease-state race conditions.
7.  **Server Restart During Grace:** Client is in grace period; Server process is restarted. Verify Reconciler resets the lease to `UNLEASED` properly.

## 6. End State

*   **Options Presented:** Zero grace, Paused grace, Resumable tokens, Server-fallback, and Hybrid states.
*   **Mandatory Invariants:** Server custody, strict `FencingGeneration` invalidation, immutable `COMMITTED` transactions, and non-implicit artifact folds.
*   **Product/Config Choices:** The exact duration of the grace period (e.g., 0s vs 30s) and the UX messaging for a paused simulation.
*   **Runtime Facts Needed:** The actual reliability of socket-drop detection vs TCP keepalive latency in the Unity/C# networking stack.
*   **Freeze Point:** G-Q6 must be explicitly resolved by Master **before Ordinary-Client Production Integration** begins (i.e., before writing the client-side network state machine and auto-save publisher). It does not block backend transaction infrastructure or Server-authored metadata mutations.