# Production Transaction Pipeline Slice 01 — REV2
## Core Transaction Substrate Refactoring, Ingress Fencing & Storage Hardening

- **Work Package:** WP-PROD-TRANSACTION-PIPELINE-01-REV2
- **Role:** Gemini 3.8 Flash A — Primary Development Agent
- **Independent Verifier:** GPT-6.1 Sol
- **Controlling Guidance:** `MPC-002`, `MAC-001`, `MD-060`, `QA Pipeline REV1 E2`
- **Date:** 2026-10-02 / 2026-10-03
- **Runtime Target:** .NET 8.0.10 / C# 12 / SQLite 3.41+ (`Microsoft.Data.Sqlite` 8.0.10)
- **Status:** **E1 PIPELINE REV2 PASS** (22 / 22 Mandatory Categories Passed)
- **Scope Restriction:** Production transaction foundation only. Zero gameplay mutation. Zero Trade, Tax, Auto-Shop, Caravan, or Settlement material state mutation; zero `CommittedSettlementStateRevision` increment; zero `ArtifactBaseStateRevision` change. Remote Tactical PoC remains frozen.

---

## 1. Executive Summary & Controlling Architecture Corrections

In accordance with Work Order `WP-PROD-TRANSACTION-PIPELINE-01-REV2`, the transaction pipeline foundation in `WarEconomyMod/Source/Server/Pipeline/` has been refactored, hardened, and bounded to produce the smallest trustworthy Production transaction foundation. 

Production Pipeline 1 (P1) terminates strictly at the **canonical `COMMITTED` or `ABORTED` decision + durable ordered event append**. All external consumer execution, automatic replays, durable cursor acknowledgments, and claims of external exactly-once delivery have been excised from the Production P1 core.

### 1.1 Resolution of Controlling Defects (MPC-002, MAC-001, MD-060, QA Pipeline REV1 E2)

| Control Ref | Defect / Vulnerability in Prior Revision | REV2 Architectural Correction |
|---|---|---|
| **Work Order §1 / MD-060** | Mutable caller request object after admission could modify state in-flight | **Immutable Admission Boundary**: At API admission, requests validate mandatory fields (`StoreIncarnationId`, `PrincipalId`, `OperationId`, etc.), deep-copy payload and scopes, compute canonical Fingerprint V2 immediately, and construct an immutable `ImmutablePipelineProbeCommand`. Caller mutations after enqueue have 0 effect. |
| **Work Order §2 / MPC-002** | Delimiter concatenation (`\|`) vulnerable to field injection, Unicode variance, empty/null bleeding | **Unambiguous Fingerprint V2**: Tagged, length-prefixed UTF-8 and fixed-width binary encoding (`FingerprintV2.Compute()`). Delimiters eliminated. Full coverage of operation type, schema version, principal, scopes, revisions, profile fingerprint, config snapshot ref, canonical JSON payload (sorted keys), and StoreIncarnationId. Server computes; caller hash strictly ignored. |
| **Work Order §3 / MAC-001** | Production APIs or direct DB writes could mutate terminal `COMMITTED` ↔ `ABORTED` | **Physical Immutability Triggers**: `OperationRecords` is insert-only. Removed `TryUpdateState` from `OperationJournal`. Enforced SQLite DB triggers `trg_operation_records_no_update` and `trg_operation_records_no_delete` raising `ABORT` on any update/delete. |
| **Work Order §4 / QA REV1 E2** | Incarnation checked before transaction allowed TOCTOU rotation race | **In-Transaction Incarnation Fencing**: `StoreIncarnationId` is read and validated inside the `BEGIN IMMEDIATE` transaction that commits the operation. Incarnation rotation uses the same exclusive writer discipline. Stale requests rejected with `INCARNATION_MISMATCH`. |
| **Work Order §5 / MPC-002** | Consumer callbacks, cursor tracking, and replay complicated commit path | **Publication P1 Simplification**: Appends strictly ordered `PublicationEvents` (`StreamId`, `Seq`, `EventId`, `PrincipalId`, `OperationId`, `EventType`, `CanonicalPayload`, `PayloadFingerprint`, `StoreIncarnationId`, `CreatedAt`) in the same canonical transaction. All callback dispatch, cursor tables, consumer loops, and durable ACK tracking removed from P1. |
| **Work Order §6 / MD-060** | Unbounded ingress could exhaust memory; worker depended on ThreadPool scheduler | **Bounded Admission & Safe Shutdown**: `Channel<PipelineCommitTask>` with bounded capacity (1000) and deterministic `STORAGE_BUSY_RETRYABLE` backpressure. Writer runs on a dedicated background `Thread`. Safe shutdown drains queued work, resolves every `TaskCompletionSource`, and cleanly joins thread. |
| **Work Order §7 / QA REV1 E2** | Arbitrary SQLite exceptions could masquerade as `STALE_REVISION` | **Strict Storage Error Typing**: Revision conflicts verified against actual aggregate version. Busy/locked returns `STORAGE_BUSY_RETRYABLE`. Schema/constraint failures return typed `STORAGE_FAILURE` preserving SQLite exception details. |
| **Work Order §8 / MAC-001** | Unsafe implicit DROP or alteration of existing legacy database tables | **Schema V3 Fail-Closed Migration**: Schema bumped to V3 (`application_id = 0x57415245`, `user_version = 3`). Existing V1/V2 databases with durable records fail closed with `LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET` without modifying disk bytes. Foreign DBs rejected with `FOREIGN_DATABASE_REJECTED`. |
| **Work Order §9 / MD-060** | Startup readiness waited on consumer catch-up | **P1 Startup Readiness**: `PIPELINE_READY` signifies DB schema validated, WAL/FULL enforced, StoreIncarnation active, dedicated writer running, and journal/event consistency verified. Zero consumer catch-up blocking. |
| **Work Order §10 / MPC-002** | Test batteries, crash workers, and test CLI options shipped in Production Server | **Release Assembly Isolation**: Destructive test battery, crash workers, fault injection, and test CLI flags moved to separate `WarEconomy.Pipeline.TestHarness` project. Release `WarEconomy.Server.dll` contains zero test CLI flags or test controls. |

---

## 2. Architecture & Implementation Blueprint

```
                      +-------------------------------------------------------+
                      |                 API Ingress Boundary                  |
                      +-------------------------------------------------------+
                                                  |
                    [Validate Required Fields & Mandatory StoreIncarnationId]
                                                  |
                                                  v
                      +-------------------------------------------------------+
                      |         Immutable Admission (Command Freeze)          |
                      |  - Deep-copy payload & scopes                         |
                      |  - Compute Fingerprint V2 (Tagged Length-Prefixed)    |
                      |  - Freeze into ImmutablePipelineProbeCommand          |
                      +-------------------------------------------------------+
                                                  |
                             [Bounded Queue Ingress: Cap = 1000]
                               /                             \
                (Queue Full / Busy)                  (Admitted Task)
                        |                                     |
                        v                                     v
             [STORAGE_BUSY_RETRYABLE]              +---------------------+
                                                   |  Dedicated Writer   |
                                                   |   Worker Thread     |
                                                   +---------------------+
                                                              |
                                                    BEGIN IMMEDIATE (WAL)
                                                              |
                                           +------------------+------------------+
                                           |                                     |
                                           v                                     v
                              [1. Validate In-Tx Incarnation]       [2. Check Existing Record]
                              ActiveIncarnation == RequestInc?      - Found + Same FP -> ALREADY_COMMITTED
                                           |                        - Found + Diff FP -> COLLISION_REJECTED
                                          YES                                    |
                                           |                                   (NEW)
                                           v                                     |
                              [3. Validate Aggregate Rev] <----------------------+
                              ExpectedRev == AggregateRev?
                               /                        \
                             (NO)                      (YES)
                              |                          |
                              v                          v
                      [Insert ABORTED]          [Insert COMMITTED Record]
                              |                 [Advance Aggregate Rev]
                              |                 [Insert CommitReceipt]
                              |                 [Append PublicationEvent]
                              |                          |
                              +------------+-------------+
                                           |
                                      [COMMIT TX]
                                           |
                                           v
                              [Complete TaskCompletionSource]
```

### 2.1 Unambiguous Fingerprint V2 (`FingerprintV2.cs`)
Fingerprint V2 strictly rejects delimiter concatenation (`|` or `:`). Instead, it implements a tagged, length-prefixed UTF-8 and fixed-width binary encoding over an explicit field hierarchy:
- Field 1: `0x01` (Tag) + `Int32 LE` Length + UTF-8 `OperationType`
- Field 2: `0x02` (Tag) + `Int32 LE` `OperationSchemaVersion`
- Field 3: `0x03` (Tag) + `Int32 LE` Length + UTF-8 `PrincipalId`
- Field 4: `0x04` (Tag) + `Int32 LE` ArrayCount + each scope (`Int32 LE` Length + UTF-8 bytes)
- Field 5: `0x05` (Tag) + `Int32 LE` ArrayCount + each revision (`Int64 LE`)
- Field 6: `0x06` (Tag) + `Int32 LE` Length + UTF-8 `ContentProfileFingerprint`
- Field 7: `0x07` (Tag) + `0x00` (null) or `0x01` + `Int32 LE` Length + UTF-8 `ConfigSnapshotRef`
- Field 8: `0x08` (Tag) + `Int32 LE` Length + UTF-8 `CanonicalPayload` (normalized JSON with sorted keys)
- Field 9: `0x09` (Tag) + `0x00` (null) or `0x01` + `Int32 LE` Length + UTF-8 `StoreIncarnationId`

The stream is hashed via SHA-256 and converted to a lowercase hexadecimal string. Caller-provided hash fields are discarded during immutable normalization.

### 2.2 Physical Immutability Triggers
To guarantee that `OperationRecords` is physically insert-only and that no application bug or administrative query can alter a terminal decision, SQLite database-level triggers are created in Schema V3:
```sql
CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_update
BEFORE UPDATE ON OperationRecords
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords rows are physically immutable: updates are forbidden.');
END;

CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_delete
BEFORE DELETE ON OperationRecords
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords rows are physically immutable: deletes are forbidden.');
END;
```

### 2.3 Publication P1 Event Store (`PublicationEventStore.cs`)
Production P1 provides an append-only, strictly ordered event log:
```sql
CREATE TABLE IF NOT EXISTS PublicationEvents (
    StreamId TEXT NOT NULL,
    Seq INTEGER NOT NULL,
    EventId TEXT PRIMARY KEY NOT NULL,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    EventType TEXT NOT NULL,
    CanonicalPayload TEXT NOT NULL,
    PayloadFingerprint TEXT NOT NULL,
    StoreIncarnationId TEXT NOT NULL,
    CreatedAt TEXT NOT NULL,
    CreatedAtEpochMs INTEGER NOT NULL,
    UNIQUE (StreamId, Seq)
);
```
- In-transaction `Seq` computation ensures strict monotonicity without gaps within each `StreamId`.
- Reader API `ReadAfter(streamId, afterSeq, limit, conn, tx)` returns events in strictly ascending sequence order.
- Consumer loops, callback dispatches, cursor tracking tables, and durable acknowledgments have been excised from the Production server.

### 2.4 Bounded Writer & Dedicated Worker Lifetime
`PipelineTransactionCoordinator` provisions:
- Ingress channel: `Channel.CreateBounded<PipelineCommitTask>(new BoundedChannelOptions(1000) { FullMode = BoundedChannelFullMode.Wait })`.
- Non-blocking try-write at admission: returns `STORAGE_BUSY_RETRYABLE` (`SERVER_BUSY_RETRYABLE`) if full.
- Dedicated Worker Thread: `new Thread(WriterThreadMain) { IsBackground = true, Name = "PipelineTransactionWriter" }`. Bypasses .NET ThreadPool task scheduling starvation under async workload.
- Safe Shutdown: `Dispose()` closes writer admission, drains remaining queued requests, resolves every caller's `TaskCompletionSource`, joins the worker thread with timeout, and only then disposes the `CancellationTokenSource`.

### 2.5 Schema V3 Fail-Closed Migration Policy
Schema migration adheres to a strict fail-closed, non-destructive policy:
1. `PRAGMA application_id = 0x57415245;` ("WARE"). Foreign databases with a non-zero, mismatched `application_id` are rejected immediately with `FOREIGN_DATABASE_REJECTED`.
2. `PRAGMA user_version`:
   - `0`: Brand new database. Initialized directly to Schema V3.
   - `3`: Validated against structural invariants (tables, columns, types, nullability, PK order, FKs, triggers, and active incarnation).
   - `1` or `2`: Checked for existing durable records in `OperationRecords` or `ProbeAggregates`. If any records exist, startup fails closed with `LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET`. Zero bytes on disk are modified.

---

## 3. Mandatory E1 Test Suite & Verification Evidence

The 22 mandatory E1 test categories specified in Work Order §11 were executed via `WarEconomy.Pipeline.TestHarness --test-pipeline-e1 --json scratch/pipeline_e1_rev2_results.json`:

```
================================================================================
   WarEconomy Pipeline REV2 E1 Test Battery (22 Mandatory Categories)           
================================================================================
[E1] Starting 22 Mandatory E1 Test Categories in: TestRuns_REV2\4061ddddddf34dec9d9591f75ccea8a9
  [PASS] Test 01: FingerprintCollisionMatrix (36 ms)
  [PASS] Test 02: MutableRequestImmunity (98 ms)
  [PASS] Test 03: ExactRetryAndCollision (36 ms)
  [PASS] Test 04: MultiProcessRevisionRace (1116 ms)
  [PASS] Test 05: MultiProcessSameIdRace (146 ms)
  [PASS] Test 06: TerminalRecordImmutability (36 ms)
  [PASS] Test 07: IncarnationRotationToctouRace (32 ms)
  [PASS] Test 08: OverloadBoundedAdmission (874 ms)
  [PASS] Test 09: SafeShutdownQueueDrain (783 ms)
  [PASS] Test 10: StorageErrorClassification (29 ms)
  [PASS] Test 11: SameTransactionEventAppendAtomicity (34 ms)
  [PASS] Test 12: PerStreamSeqMonotonicity (275 ms)
  [PASS] Test 13: EventReadAfterOrdering (37 ms)
[Pipeline] PIPELINE_READY reached. Active StoreIncarnation: a6f2e829863d43ae822ae220063a5542
  [PASS] Test 14: FreshV3Startup (31 ms)
  [PASS] Test 15: LegacySchemaV1V2FailClosed (188 ms)
  [PASS] Test 16: ForeignDatabaseRejection (38 ms)
  [PASS] Test 17: MalformedV3SchemaRejection (119 ms)
  [PASS] Test 18: FailingValidationPreservesDatabase (49 ms)
  [PASS] Test 19: EveryConnectionWalAndFull (29 ms)
  [PASS] Test 20: ReleaseBinaryDoesNotExposeTestCli (2 ms)
  [PASS] Test 21: GameplayDispatcherCannotInvokeProbe (27 ms)
  [PASS] Test 22: NoGameplayMaterialMutation (0 ms)
================================================================================
[E1] Finished 22 Tests in 4027 ms: 22 PASSED, 0 FAILED.
[E1] Overall Result: PASS (E1 PIPELINE REV2 PASS)
================================================================================
```

### 3.1 Detailed Test Verification Matrix

| # | Test Category | Execution Duration | Verified Invariant & Proof Details | Status |
|---|---|---|---|:---:|
| **01** | `FingerprintCollisionMatrix` | 36 ms | Tested 17 adversarial inputs: delimiter injections (`\|`, `:::`, `;;;`), null vs empty strings, international Unicode (Korean, Cyrillic, Arabic RTL, Emojis, French accents), escape sequences (`\0`, `\n\r`, quotes), canonical JSON key sorting, and 100KB large payloads. **0 collisions generated**. | **PASS** |
| **02** | `MutableRequestImmunity` | 98 ms | Request mutated post-enqueue (PrincipalId, Scope, Payload modified by caller). Executed transaction reflected 100% original admitted values. Caller mutations had zero effect. | **PASS** |
| **03** | `ExactRetryAndCollision` | 36 ms | Resubmitting exact command returned idempotent `ALREADY_COMMITTED` with original receipt. Resubmitting same `(PrincipalId, OperationId)` with altered payload returned `COLLISION_REJECTED`. | **PASS** |
| **04** | `MultiProcessRevisionRace` | 1116 ms | 25 concurrent callers competed to increment revision `0 -> 1`. Exactly 1 request `COMMITTED` (winner); remaining 24 failed with typed `STALE_REVISION`. Zero data corruption. | **PASS** |
| **05** | `MultiProcessSameIdRace` | 146 ms | 12 concurrent submissions of the identical `(PrincipalId, OperationId)`. Exactly 1 committed initial transaction; 11 returned idempotent `ALREADY_COMMITTED`. Exactly 1 record, receipt, and event written to disk. | **PASS** |
| **06** | `TerminalRecordImmutability` | 36 ms | Direct repository and raw SQL `UPDATE` and `DELETE` attempts on `OperationRecords` blocked by database triggers `trg_operation_records_no_update` and `trg_operation_records_no_delete`. | **PASS** |
| **07** | `IncarnationRotationToctouRace` | 32 ms | Admitted request with incarnation $I_1$ attempted commit after background rotation to $I_2$. In-transaction fence rejected commit with `INCARNATION_MISMATCH`. | **PASS** |
| **08** | `OverloadBoundedAdmission` | 874 ms | 1000 rapid requests submitted against bounded capacity (50) with delayed writer. 944 requests cleanly received `STORAGE_BUSY_RETRYABLE` backpressure without memory bloat or crash. | **PASS** |
| **09** | `SafeShutdownQueueDrain` | 783 ms | Shutdown initiated while 50 requests were queued. All 50 requests were safely drained and completed before coordinator disposal; worker thread joined cleanly. | **PASS** |
| **10** | `StorageErrorClassification` | 29 ms | Verified true revision mismatch yields `STALE_REVISION`, while direct SQLite constraint violations yield typed `STORAGE_FAILURE` preserving inner SQLite exceptions. | **PASS** |
| **11** | `SameTransactionEventAppendAtomicity` | 34 ms | Publication event appended atomically inside commit transaction. Aborted transactions resulted in exactly 0 publication events. | **PASS** |
| **12** | `PerStreamSeqMonotonicity` | 275 ms | 50 sequential events written to stream. Verified strictly monotonic sequence numbers (`1` to `50`) with zero gaps and zero duplicate sequences. | **PASS** |
| **13** | `EventReadAfterOrdering` | 37 ms | `ReadAfter(StreamId, afterSeq, limit)` verified ascending sequence ordering and pagination boundaries across stream events. | **PASS** |
| **14** | `FreshV3Startup` | 31 ms | Initialized empty database. Created Schema V3 (`application_id=0x57415245`, `user_version=3`), generated active `StoreIncarnation`, and reached `PIPELINE_READY`. | **PASS** |
| **15** | `LegacySchemaV1V2FailClosed` | 188 ms | Legacy V2 database with durable records failed closed with `LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET`. Raw database file size and bytes verified completely unmodified. | **PASS** |
| **16** | `ForeignDatabaseRejection` | 38 ms | SQLite database with foreign `application_id` rejected with `FOREIGN_DATABASE_REJECTED` before adoption. | **PASS** |
| **17** | `MalformedV3SchemaRejection` | 119 ms | V3 database missing immutability trigger detected by structural schema validator and rejected with `InvalidOperationException`. | **PASS** |
| **18** | `FailingValidationPreservesDatabase` | 49 ms | Defective database validation failure verified to leave disk bytes 100% unchanged. | **PASS** |
| **19** | `EveryConnectionWalAndFull` | 29 ms | Verified 5 distinct connections enforce `journal_mode=WAL` and `synchronous=FULL` (2). | **PASS** |
| **20** | `ReleaseBinaryDoesNotExposeTestCli` | 2 ms | Reflection scan of `WarEconomy.Server.dll` confirmed zero test CLI verbs, zero test battery types, and zero destructive fault injection hooks. | **PASS** |
| **21** | `GameplayDispatcherCannotInvokeProbe` | 27 ms | Probe CAS invocation via gameplay network transport rejected with `ACCESS_DENIED`. | **PASS** |
| **22** | `NoGameplayMaterialMutation` | 0 ms | Verified pipeline touches only probe tables (`ProbeAggregates`, `ProbeRevisionHistory`). Zero gameplay Settlement/EntityId/Tax/Trade tables touched. | **PASS** |

---

## 4. Codebase Artifacts & Structural Mapping

```
WarEconomyMod/
├── Source/
│   ├── Common/                               # Shared contracts and models
│   │   └── Pipeline/Models/
│   │       ├── FingerprintV2.cs              # Tagged length-prefixed canonical fingerprint
│   │       └── PipelineProbeModels.cs        # Immutable commands & normalized envelopes
│   ├── Server/                               # Production Server Assembly (Clean)
│   │   ├── Pipeline/
│   │   │   ├── Coordinator/
│   │   │   │   └── PipelineTransactionCoordinator.cs  # Dedicated writer, bounded ingress, in-tx fence
│   │   │   ├── Data/
│   │   │   │   ├── SqliteDatabaseContext.cs           # WAL/FULL enforcement, active incarnation lookup
│   │   │   │   └── Migrations/
│   │   │   │       └── PipelineSchemaMigration.cs     # Schema V3, fail-closed validation, triggers
│   │   │   ├── Recovery/
│   │   │   │   └── RecoveryReconciler.cs              # P1 startup consistency validation
│   │   │   └── Storage/
│   │   │       ├── OperationJournal.cs                # Insert-only terminal journal
│   │   │       └── PublicationEventStore.cs           # Append-only ordered event stream
│   │   └── Program.cs                        # Production server entrypoint (Zero test CLI)
│   └── Testing/
│       └── WarEconomy.Pipeline.TestHarness/  # Separate Isolated Test Assembly
│           ├── PipelineE1TestBattery.cs      # 22 Mandatory E1 Test Categories
│           └── Program.cs                    # Test runner CLI & crash worker harness
```

---

## 5. Final Classification & Conclusion

All 10 Work Order requirements have been satisfied.
All 22 Mandatory E1 Test Categories have been executed and passed (100% pass rate).
Source code, Release binaries, and Schema V3 specifications are frozen.

### Final Classification:
# **E1 PIPELINE REV2 PASS**

**STATUS: FROZEN. STOPPING FOR INDEPENDENT SOL E2 VERIFICATION.**
