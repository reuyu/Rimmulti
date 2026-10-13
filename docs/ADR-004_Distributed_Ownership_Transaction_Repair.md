# ADR-004_Distributed_Ownership_Transaction_Repair.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the durable transaction and recovery contract for operations that mutate canonical custody across different authority scopes (e.g., Shared World vs. Settlement LocalClock). Because the Dedicated Server's database commit and the physical write of a RimWorld materialization artifact (`.rws` or custom package) cannot be achieved in a single atomic hardware operation, a distributed transaction state machine is required to guarantee no double-custody, no zero-custody, idempotent retries, and deterministic crash recovery.

This contract integrates deeply with upstream constraints:
*   **ADR-001:** Dedicated Server Domain Authority and idempotency rules[cite: 16].
*   **ADR-003:** Canonical state separation into Artifact, Index, and Operations[cite: 18].
*   **ADR-006A & 006B:** Temporal schema classification and Content Profile bindings[cite: 17].
*   **ADR-007:** Writer lease fencing and admission barriers[cite: 19].
*   **ADR-008:** Shared World layer projection and transit custody invariants[cite: 23].

## 2. Required Operation Identity
To ensure idempotency and auditability, every cross-custody or domain mutation must be tracked via a strict identity record[cite: 16].
*   **`OperationId`:** A globally unique UUID for the transaction.
*   **Operation Type:** The semantic intent (e.g., `CaravanIngress`, `OwnershipTransfer`, `TaxCollection`).
*   **Payload / Intent Hash:** An immutable hash of the operation's semantic payload to detect tampering on retry.
*   **Principal / Authority Context:** The authenticated actor initiating the request.
*   **Source Scope & Revision:** `SourceId` (e.g., `CaravanId`) and expected `SourceRevision` (e.g., `WorldObjectRevision`).
*   **Destination Scope & Revision:** `DestinationId` (e.g., `SettlementId`) and expected `SettlementStateRevision`[cite: 18, 23].
*   **`ContentProfileFingerprint` / Codec:** The exact gameplay content profile required to interpret the operation[cite: 18].
*   **`ConfigRevision` / Snapshotted Config:** The effective configuration values at the time of intent generation[cite: 18].
*   **Coordinates:** Creation/Commit timestamps and relevant WorldTick ($W$) coordinates[cite: 17].

**Idempotency Rule (from ADR-001):**
*   Same `OperationId` + same Payload Hash $\rightarrow$ Idempotent replay; return prior terminal receipt[cite: 16].
*   Same `OperationId` + different Payload Hash $\rightarrow$ Reject (Operation ID Collision)[cite: 16].

## 3. Required Transaction States
Operations progress through a durable state machine to survive server crashes.

1.  **`RECEIVED / VALIDATING`:** The request is in memory. Preflight checks (schema, identity, profile) are performed.
2.  **`PREPARED`:** The server durably reserves the operation. Source and destination scopes are locked/fenced against concurrent mutations[cite: 19].
3.  **`COMMITTING / COMMITTED`:** The **Authoritative Decision Point and Durable Commit Point**. The server database atomically records the domain mutation in the `CommittedOperationLog` and updates the canonical index/projection[cite: 18].
4.  **`PUBLISH_PENDING`:** The operation is committed, but derivative side-effects (e.g., writing the new RimWorld artifact, dispatching outbox messages) are ongoing.
5.  **`PUBLISHED / APPLIED`:** The **Publication Point**. All derivative artifacts and network projections are finalized.
6.  **`ABORTED`:** The operation failed validation or preparation and was rolled back before the commit point. No domain effects occurred.
7.  **`REPAIR_REQUIRED / QUARANTINED`:** An operation reached `COMMITTED`, but forward publication is permanently blocked (e.g., storage corruption). Manual operator intervention or explicit domain compensation is required[cite: 16, 18].

## 4. Canonical Commit vs. Artifact Publication
The Dedicated Server Database is the ultimate **Recovery Source of Truth**[cite: 16]. The RimWorld artifact is a downstream projection.
*   **DB Commit:** Advances `CommittedSettlementStateRevision` and `SettlementProjectionRevision`[cite: 18].
*   **Artifact Write:** Only after a successful file write does the server advance the `ArtifactBaseStateRevision` and `ArtifactRevision` to fold the operations into the new base watermark[cite: 18].
*   **Crash during Artifact Write:** If the DB commits but the artifact write fails or the process crashes, the `ArtifactBaseStateRevision` remains older than the `CommittedSettlementStateRevision`. Upon restart, the Server detects this gap, ignores the corrupted/missing file, loads the last valid artifact, and *replays the `CommittedOperationLog`* to rebuild the state[cite: 18].
*   **Prevention of 2nd Source of Truth:** An artifact candidate floating in storage without a corresponding `COMMITTED` database record is orphaned data and strictly ignored.

## 5. Cross-Custody Transfer
At any commit boundary, an `EntityId` graph must have exactly one authoritative custody owner (ADR-008 invariant)[cite: 23].
*   **Source Canonicality:** The source scope remains canonical and retains custody up until the precise `COMMITTED` boundary in the server DB.
*   **Destination Canonicality:** The destination scope does not acquire canonical custody until that same `COMMITTED` boundary.
*   **Nested Inventories / Split & Merge:** Transferred entities move as a complete graph root. If a split is required, the split operation allocates new `EntityIds` during the `PREPARED` phase and executes the semantic transfer atomically at `COMMITTED`. Arbitrary field-level object merging is prohibited[cite: 18].
*   *(Note: TBD-05 regarding partial tax collection semantics remains explicitly unresolved and deferred to Product Policy)[cite: 22].*

## 6. Lease & Fencing Interaction
Transactions involving actively simulated settlements must interact with the ADR-007 writer lease contracts[cite: 19].
*   **Barrier Activation:** Before reaching `PREPARED`, operations modifying an active settlement trigger a `HANDOFF_BARRIER` or `DELTA_BARRIER`[cite: 19].
*   **Freezing Revisions:** The `WriterLeaseId`, `FencingGeneration`, and current `BaseCommittedSettlementStateRevision` are frozen[cite: 19].
*   **Stale Rejection:** Once the operation is `COMMITTED`, the `FencingGeneration` advances. Any subsequent stale checkpoints or late worker publications carrying the old generation are strictly rejected[cite: 19].
*   **Resumption:** The leased writer is fenced and must acknowledge the delta or rematerialize from the newly advanced `CommittedSettlementStateRevision` to resume operations[cite: 19].

## 7. Worker / Tactical Publication
A Tactical Worker's success response is **not** the canonical commit[cite: 20].
1.  **Candidate Submission:** Worker submits a candidate artifact, an egress/outcome manifest, and a `WorkerGeneration` token[cite: 20].
2.  **Validation:** The Server performs static preflight and server-controlled semantic validation (ADR-006B)[cite: 18].
3.  **Domain Decision & Commit:** The Dedicated Server approves the outcome and atomically writes the transaction to `COMMITTED` in the DB.
4.  **Artifact Publication:** The Server promotes the candidate artifact to the canonical store and advances `ArtifactBaseStateRevision`[cite: 18].
*   *Crash Handling:* If the Worker crashes before `COMMITTED`, the session is `ABORTED` (or resumes if the worker recovers before timeout)[cite: 20]. If the Server crashes *after* `COMMITTED` but before artifact promotion, the Server executes Forward Recovery to finalize the artifact promotion based on the durable DB record[cite: 16].

## 8. Outbox / Journal / Repair Architecture
*   **Operation Journal:** The durable SQL table (or equivalent) storing the state machine (`OperationId`, `State`, `Payload`).
*   **Canonical Commit Record:** Atomic updates to the Domain Aggregates (e.g., Ownership, Factions, Revisions).
*   **Publication Outbox:** A durable queue for side-effects (e.g., dispatching UI notifications, pushing World projections to clients).
*   **Recovery Reconciler:** A background scanner that sweeps for operations stuck in `PREPARED` or `PUBLISH_PENDING` upon server restart, driving them forward to `PUBLISHED` or rolling back `PREPARED` locks.

## 9. Failure Matrix

| Phase of Failure | Canonical Truth | Retry Behavior | Compensation Needed? | Operator Repair? |
| :--- | :--- | :--- | :--- | :--- |
| **1. Before Validation** | Unchanged | Client may retry freely | No | No |
| **2. After `PREPARED`** | Unchanged | Wait for timeout or Reconciler abort | No (Rollback DB locks) | No |
| **3. During DB Commit** | Ambiguous | Reconciler evaluates DB state on restart | No (DB transaction semantics) | No |
| **4. After DB Commit, before Artifact Write** | **New State** | Forward Recovery (Replay Log) | No | No |
| **5. During Artifact Write** | **New State** | Forward Recovery (Discard partial, rewrite) | No | No |
| **6. After Artifact, before Outbox** | **New State** | Forward Recovery (Re-process Outbox) | No | No |
| **7. During Ingress/Egress Publication** | **New State** | Forward Recovery (Update Projections) | No | No |
| **8. Disconnect (Pre-Commit)** | Unchanged | Client session `ABORTED` | No | No |
| **8. Disconnect (Post-Commit)** | **New State** | Client fenced; must rematerialize | No | No |
| **9. Duplicate / Replay Op** | Existing State | Idempotent Return of terminal receipt | No | No |
| **10. Stale Source/Dest Revision** | Unchanged | Operation `ABORTED` | No | No |
| **11. Process Restart** | DB Record | Reconciler drives pending states | No | No |
| **12. Semantic Validation Failure** | Unchanged | Operation `ABORTED` / Worker Quarantined | No | Yes (Investigate Quarantine) |

## 10. Compensation vs. Forward Recovery
*   **Abort (Rollback):** Used strictly *before* the DB canonical commit. Reserves and locks are released.
*   **Forward Recovery:** Used strictly *after* the DB canonical commit. The server will persistently attempt to write the artifact and clear the outbox.
*   **Domain Compensation:** A committed political or economic event (e.g., a tax collection that logically succeeded but the assets were later corrupted) must **not** be resolved by erasing the database record. It requires a true compensating domain operation (e.g., a "Refund" or "Asset Correction" transaction) to ensure auditability[cite: 16].

## 11. Revision Model Updates
*   **Canonical Revisions:** Source and Destination revisions (e.g., `WorldObjectRevision`, `SettlementProjectionRevision`, `CommittedSettlementStateRevision`) advance atomically exactly at the `COMMITTED` phase[cite: 18, 23].
*   **Artifact Watermarks:** `ArtifactBaseStateRevision` advances *only* during the `PUBLISHED` phase when a physical artifact fold successfully completes and passes hash validation[cite: 18].

## 12. Proof / Test Obligations
The following scenarios require explicit E1/E2/E3 runtime failure injection evidence:
1.  `kill -9` / process termination at each state machine phase.
2.  Duplicate retry of the exact same `OperationId`.
3.  Submission of the same `OperationId` with a mutated payload.
4.  Concurrent cross-domain transfer races (e.g., two attacks arriving simultaneously).
5.  Stale lease publication (Worker submitting an artifact after its generation was fenced).
6.  Restart recovery evaluating a torn artifact write against a committed log.
7.  Artifact hash corruption detection.
8.  Outbox replay idempotency.
9.  Split/merge of nested custody (e.g., a Pawn transferring while carrying items).
10. Semantic validator failure after candidate materialization, ensuring safe quarantine.

---

## 13. Deliverable End Sections

### Acceptance Readiness
*   **Safe E0 Architecture Decisions:** The 7-step state machine, separation of DB Commit from Artifact Write, Forward Recovery mandates, and Idempotency hash constraints are safe for Master acceptance.
*   **Decisions Needing Runtime Proof:** Explicit SQLite (or equivalent) transactional boundaries surviving a `kill -9` during the `PUBLISH_PENDING` phase.
*   **Product-Policy Questions:** Exact semantics of partial compensations or refunds.
*   **Dependencies:** Dependent on unresolved TBD-05 (partial tax collection)[cite: 22].

### Transaction Invariant Table
| Invariant | Owner | Commit Point | Recovery Source | Failure Handling |
| :--- | :--- | :--- | :--- | :--- |
| **No Double Custody** | Dedicated Server | DB Transaction (`COMMITTED`) | DB `CommittedOperationLog` | Forward Recovery forces convergence |
| **No Zero Custody** | Dedicated Server | DB Transaction (`COMMITTED`) | DB `CommittedOperationLog` | Forward Recovery forces convergence |
| **Idempotency** | Dedicated Server | Preflight (`VALIDATING`) | DB Operation Journal | Return terminal receipt |
| **Stale Writer Rejection**| Dedicated Server | `PREPARED` Barrier | Lease / Fencing Registry | `ABORTED` |

### Cross-ADR Contract Matrix
| ADR | Contract Integration |
| :--- | :--- |
| **ADR-001** | Provides `OperationId` idempotency rules and final Server Domain Authority constraints[cite: 16]. |
| **ADR-002** | Defines the Tactical Worker candidate pipeline evaluated by the transaction validation phase[cite: 20]. |
| **ADR-003** | Supplies `CommittedSettlementStateRevision`, `ArtifactBaseStateRevision`, and `PendingOperationQueue` semantics[cite: 18]. |
| **ADR-006A** | Ensures distinct temporal coordinates ($W$, $L_s$) are correctly recorded in the operation metadata[cite: 17]. |
| **ADR-006B** | Enforces the `ContentProfileFingerprint` to prevent unsupported schema commits[cite: 18]. |
| **ADR-007** | Manages the `WriterLeaseId` and `FencingGeneration` barriers invoked during `PREPARED`[cite: 19]. |
| **ADR-008** | Demands the 1-owner invariant for `WorldObjects` and Caravans crossing into local domains[cite: 23]. |