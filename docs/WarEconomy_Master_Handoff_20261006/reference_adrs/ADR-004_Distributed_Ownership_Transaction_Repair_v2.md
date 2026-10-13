# ADR-004_Distributed_Ownership_Transaction_Repair_v2.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the durable transaction and recovery contract for operations that mutate canonical custody across different authority scopes (e.g., world layer ingress/egress, ownership transfers, tactical publication). Because the Dedicated Server's database commit and physical RimWorld artifact publication cannot be achieved in a single hardware atomic write, this contract ensures strict determinism and idempotency.

The architecture integrates with accepted upstream constraints:
*   **ADR-001:** Server Domain Authority, authenticated persistence, and idempotency[cite: 16].
*   **ADR-003:** Canonical material-state representation, Artifact Base Revisions, and `EntityId`[cite: 18].
*   **ADR-006A / 006B:** Temporal schema classification and `ContentProfileFingerprint` limits[cite: 17, 18].
*   **ADR-007:** Writer lease fencing and admission barriers[cite: 19].
*   **ADR-008:** Shared World layer projection and one-owner transit custody invariants[cite: 23].

## 2. Required Operation Identity
To ensure idempotency and stable auditability, every operation must be tracked via a strict identity record[cite: 16].
*   `OperationId`: A globally unique UUID for the transaction.
*   Operation Type: Semantic intent (e.g., `CaravanIngress`, `TaxCollection`).
*   Immutable Payload Hash / Intent Hash.
*   Principal / Authority Context.
*   Source Scope + Expected Source Revision.
*   Destination Scope + Expected Destination Revision.
*   `ContentProfileFingerprint` / Codec Versions (where needed for typed payload interpretation)[cite: 18].
*   `ConfigRevision` / Snapshotted effective config (where deterministic replay demands it)[cite: 18].
*   Creation/Commit timestamps and semantic WorldTick ($W$) coordinates[cite: 17].

**Idempotency Rule:** Same `OperationId` + same payload hash yields an idempotent replay returning the prior terminal receipt[cite: 16]. Same `OperationId` + different payload hash forces rejection[cite: 16].

## 3. Two Commit Classes & Staged-Result Contract
A transaction commit must exclusively bind to recoverable material; it must never depend on volatile Worker or client memory[cite: 16, 20]. The architecture distinguishes two commit classes:

**A. Replayable Typed Operation Commit**
The post-commit material state is entirely reconstructible by replaying committed typed operations onto the last valid artifact watermark (e.g., simple fungible tax deductions)[cite: 18].

**B. Staged Material Result Commit**
The operation requires engine-produced material state that cannot be fully encoded as simple typed operations (e.g., a Tactical Worker combat outcome). Before a `COMMITTED` state is reached, the Server must durably register an immutable **staged result**. This non-canonical, staged material must contain at minimum:
*   `OperationId` and `ResultManifestId`.
*   Candidate artifact/package hash.
*   Source/base artifact identity.
*   `BaseCommittedSettlementStateRevision`.
*   Expected resulting `CommittedSettlementStateRevision` (canonical head).
*   `ContentProfileFingerprint` and `SchemaVersion` / `CodecVersion`[cite: 18].
*   `WorkerGeneration` or lease/fencing context where relevant[cite: 19].
*   `EntityId` / custody result manifest.
*   Validation status.
*This staged result remains strictly non-canonical until the DB reaches `COMMITTED`.*

## 4. Required Transaction States & `PREPARED` Semantics
Operations progress through a durable state machine designed for crash recovery[cite: 16].
1.  `RECEIVED / VALIDATING`: Preflight identity and payload checks.
2.  `PREPARED`: The durable reservation record is created. 
    *   *Semantics:* Enforces deterministic multi-scope lock ordering to avoid deadlocks. Defines reservation expiry and tracks the lease ownership. Distinct from ADR-007 writer fencing, this is a transaction lock[cite: 19].
    *   *Provisional Entities:* `EntityId`s created in `PREPARED` are provisional/reserved only. They become canonical visible entities only at `COMMITTED`[cite: 18].
3.  `COMMITTING / COMMITTED`: The **Authoritative Decision Point and Durable Commit Point**[cite: 16]. The DB binds to the typed operations or exact durable staged result.
4.  `PUBLISH_PENDING`: Canonical decision is committed, but derivative outbox or artifact publication is ongoing.
5.  `PUBLISHED / APPLIED`: The **Publication Point**. The material artifact watermark and projections are successfully updated[cite: 18].
6.  `ABORTED`: Failed or expired before `COMMITTED`. Rollback of locks.
7.  `REPAIR_REQUIRED / QUARANTINED`: A post-commit forward failure that cannot be automatically resolved (e.g., a promoted artifact became corrupted).

## 5. Promotion, Validation & Semantic Failure Split
Validation failures are split strictly by their relation to the `COMMITTED` boundary.

**Pre-Commit Semantic Validation Failure:** 
If candidate semantic validation fails *before* `COMMIT` (e.g., a Tactical Worker submits an invalid candidate), the candidate is rejected/quarantined. The transaction is `ABORTED`, and canonical state remains unchanged[cite: 18, 20].

**Post-Commit Promotion/Publication Validation:**
Before promoting a staged artifact/result to canonical status, the Server must verify: `OperationId` match, immutable hash match, profile/schema/codec match, base revision match, expected committed head match, fencing generation/session/worker identity validity, and result/custody manifest match[cite: 18, 19].
*   If validation fails *post-commit* (e.g., the staged file was corrupted on disk after DB commit): The server must **not** undo the canonical decision[cite: 16]. It enters forward repair/quarantine and must rebuild from another recoverable source where possible[cite: 16, 18].

## 6. Disconnect Semantics & DB Crash Classification
**Disconnect Semantics:**
A pre-commit disconnect does not automatically equal `ABORTED`.
*   If required facts or staged material are incomplete upon disconnect: the transaction is aborted/expired.
*   If the Server already holds a complete, durable `PREPARED` package and the specific operation policy allows autonomous completion: the Server may continue to `COMMIT`[cite: 16].
*   If product policy requires live principal confirmation, abort according to that specific operation contract.

**Deterministic DB Crash Classification:**
A crash during the DB transaction is never left "ambiguous" to canonical truth. After restart, the durable store must strictly resolve:
*   `COMMITTED` record present $\rightarrow$ Operation is committed. Proceed to forward recovery/publication.
*   `COMMITTED` record absent $\rightarrow$ Operation is not committed (treat as `PREPARED` or `ABORTED` based on journal state)[cite: 16].

## 7. Canonical Revisions vs. Projection Revisions
It is critical to distinguish authoritative domain revisions from derived projections.
*   **Canonical Revisions:** `CommittedSettlementStateRevision` and `ArtifactBaseStateRevision` dictate absolute material truth and historical fold watermarks[cite: 18].
*   **Projection Revisions:** `SettlementProjectionRevision` and outbox cursors are derived projections[cite: 18]. They may lag behind the canonical commit and can be repaired or rebuilt. Under no circumstances may `SettlementProjectionRevision` serve as a substitute for the canonical material-state head[cite: 18].

## 8. Cross-Custody Transfer
When `EntityId` graphs transfer between domains (e.g., Shared World Caravan $\rightarrow$ Settlement LocalClock), the ADR-008 one-owner invariant applies[cite: 23].
*   Source custody remains fully canonical until the transaction's exact authoritative `COMMITTED` boundary.
*   Destination custody must not become independently canonical early.
*   After `COMMITTED`, crash recovery must deterministically converge to exactly one canonical owner[cite: 23].
*   *(Note: Exact partial-collection semantics for tax, as outlined in TBD-05, are explicitly deferred to product policy)[cite: 14, 22].*

## 9. Lease / Fencing Interaction
Transactions involving actively simulated scopes enforce ADR-007 contracts[cite: 19].
*   Before entering `PREPARED`, the relevant `WriterLeaseId`, `FencingGeneration`, and `BaseCommittedSettlementStateRevision` must be evaluated and frozen via `HANDOFF_BARRIER` or `DELTA_BARRIER`[cite: 19].
*   After transaction `COMMIT`, the `FencingGeneration` advances. Any stale checkpoint or worker publication carrying the old generation is strictly rejected[cite: 19].
*   To resume, the writer must rematerialize from the newly advanced `CommittedSettlementStateRevision`[cite: 19].

## 10. Failure Matrix

| Failure Scenario | Canonical Truth | Retry Behavior | Compensation? | Operator Repair? |
| :--- | :--- | :--- | :--- | :--- |
| **Before validation** | Unchanged | Free retry | No | No |
| **After `PREPARED`** | Unchanged | Wait/Query or Abort | No (Release locks) | No |
| **During DB canonical commit** | DB recovery resolves | Determinist Replay (Receipt vs Abort) | No | No |
| **Staged result durably written, crash before COMMIT** | Unchanged | Rollback to `ABORTED` (or resume `PREPARED`) | No | No |
| **Staged result lost/corrupt before COMMIT** | Unchanged | Operation `ABORTED` | No | No |
| **COMMIT references staged result, crash before promotion** | **New State** (`PUBLISH_PENDING`) | Forward recovery (promote staged result) | No | No |
| **After DB commit, before artifact write** | **New State** (`PUBLISH_PENDING`) | Forward recovery (replay log or promote result) | No | No |
| **Promotion candidate hash/base/profile mismatch** | **New State** (`REPAIR_REQUIRED`) | Forward repair / Rebuild | No | Yes (Investigate quarantine) |
| **During artifact write** | **New State** (`PUBLISH_PENDING`) | Forward recovery (rewrite) | No | No |
| **After artifact write, before projection/outbox** | **New State** (`PUBLISH_PENDING`) | Forward recovery (rebuild index/dispatch) | No | No |
| **During ingress/egress custody publication** | **New State** | Forward recovery | No | No |
| **Client/Worker disconnect pre-commit** | Unchanged (unless autonomous allowed) | `ABORTED` or Server autonomous commit | No | No |
| **Client/Worker disconnect post-commit** | **New State** | Client fenced; must rematerialize | No | No |
| **PREPARED lock owner disappears** | Unchanged | Autonomous commit (if valid) or expire lock | No | No |
| **Duplicate retry while operation is `PREPARED`** | Unchanged | Return pending status | No | No |
| **Duplicate retry while `PUBLISH_PENDING`** | **New State** | Return terminal receipt | No | No |
| **Duplicate / Replayed operation (Post-Publish)** | **New State** | Idempotent terminal receipt | No | No |
| **Stale source/destination revision** | Unchanged | Operation `ABORTED` | No | No |
| **Semantic validation failure after candidate materialization (Pre-Commit)**| Unchanged | Reject candidate / Quarantine Worker | No | No |
| **Process restart** | Driven by DB Journal | Reconciler advances `PREPARED`/`PENDING` | No | No |
| **Post-commit projection/outbox permanently unavailable**| **New State** (`REPAIR_REQUIRED`) | Rebuild index from canonical log/artifacts | No | No |
| **Recovery: Typed Replay vs Staged Result** | **New State** | Apply logs vs Promote existing staged file | No | No |

## 11. Compensation vs. Forward Recovery
*   **Abort:** Prior to canonical commit, rolling back drops locks and invalidates provisional `EntityId`s.
*   **Forward Recovery:** Post-commit, the server persistently attempts to reach `PUBLISHED` using typed replay or staged material promotion.
*   **Domain Compensation:** A committed political/economic event must *not* be "rolled back" by erasing DB records due to a delayed artifact publication. If necessary, it requires a true compensating domain operation (e.g., an explicit refund transaction) according to product policy contracts[cite: 16].

---

## 12. Deliverable End Sections

### Acceptance Readiness
**Safe E0 Architecture Decisions:**
*   Idempotency payload constraints, two-class commit model (Typed vs. Staged), deterministic DB crash resolution, the `PREPARED` lock boundary, and post-commit forward-recovery invariants are safe for Master acceptance.

**E1/E2/E3 Crash/Failure Proof Obligations:**
*   `kill -9` termination at `PREPARED`, `COMMITTING`, and `PUBLISH_PENDING`.
*   Duplicate retry execution under heavy concurrency.
*   Stale lease publication rejection (Worker submitting after fencing generation increment).
*   Restart recovery successfully differentiating a torn artifact write from a complete DB commit.
*   Outbox replay idempotency.
*   Split/merge of nested custody (verifying 1-owner invariant post-recovery).
*   Semantic validator failure/quarantine handling without canonical damage.

**Open Product-Policy Questions & Unresolved Dependencies:**
*   Whether a pre-commit disconnect during a multi-party trade allows autonomous server completion vs. mandatory abort.
*   Does not resolve existing TBD-01..05 (including partial tax semantics)[cite: 14, 22].

### Transaction Invariant Table

| Invariant | Owner | Commit Point | Recovery Source | Failure Handling |
| :--- | :--- | :--- | :--- | :--- |
| **No Double Custody** | Dedicated Server | DB `COMMITTED` | DB `CommittedOperationLog` | Forward Recovery forces strict convergence |
| **No Zero Custody** | Dedicated Server | DB `COMMITTED` | DB `CommittedOperationLog` | Forward Recovery / Staged Promotion forces convergence |
| **Idempotency** | Dedicated Server | Preflight `VALIDATING` | DB Operation Journal | Return stable terminal receipt |
| **Stale Writer Rejection** | Dedicated Server | `PREPARED` Barrier | Lease/Fencing Registry | Pre-commit `ABORTED` |
| **Deterministic DB Crash** | Dedicated Server | DB `COMMITTED` | DB Journal Record | Record Present $\rightarrow$ Forward Recovery; Absent $\rightarrow$ Abort/Prepared |
| **No Volatile Memory Commits**| Dedicated Server | DB `COMMITTED` | Typed Logs / Staged Material | Fallback to durable inputs; never client RAM |

### Cross-ADR Contract Matrix

| ADR | Contract Integration |
| :--- | :--- |
| **ADR-001** | Mandates `OperationId` idempotency rules and server-final domain authority limits[cite: 16]. |
| **ADR-002** | Defines the Tactical Worker material candidate flow, which is evaluated during transaction preflight/semantic validation[cite: 20]. |
| **ADR-003** | Defines the `CommittedSettlementStateRevision`, `ArtifactBaseStateRevision`, and `CommittedOperationLog` updated at the `COMMITTED` and `PUBLISHED` boundaries[cite: 18]. |
| **ADR-006A** | Ensures $W$ and $L_s$ coordinates are strictly captured in transaction metadata[cite: 17]. |
| **ADR-006B** | Enforces the `ContentProfileFingerprint` mapping required to validate a staged material candidate before commit[cite: 18]. |
| **ADR-007** | Informs `HANDOFF_BARRIER` and `DELTA_BARRIER` logic executed at `PREPARED` to fence writers[cite: 19]. |
| **ADR-008** | Demands the 1-owner canonical invariant for entities transferring to/from the Shared World layer[cite: 23]. |