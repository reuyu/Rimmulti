# Production Transaction Pipeline Slice 01 — REV1
## Core Transaction Substrate Refactoring & Hardening

- **Work Package:** WP-PROD-TRANSACTION-PIPELINE-01-REV1
- **Controlling Guidance:** `MASTER_ARCHITECTURE_CORRECTIONS_MAC-001.md` (MAC-001) & `ARCH-REDTEAM-REVIEW-002` (MR-06..MR-11)
- **Role:** Gemini 3.8 Flash A — Primary Development Agent
- **Date:** 2026-10-02
- **Runtime Target:** .NET 8.0.10 / C# 12 / SQLite 3.41+ (`Microsoft.Data.Sqlite` 8.0.10)
- **Status:** **E1 PIPELINE REV1 PASS** (19 / 19 Tests Passed)
- **Scope Restriction:** Production substrate infrastructure only. Zero real gameplay mutations. No Settlement inventory or material state touched; no `CommittedSettlementStateRevision` increment; no `ArtifactBaseStateRevision` change; no Tax, Trade, or Tactical publication. Remote Presentation PoC remains strictly frozen.

---

## 1. Executive Summary & Resolution of Red-Team / Sol E2 Defects

Following the Sol E2 independent evaluation (`QA_Production_Transaction_Pipeline_01.md`) and the Red-Team Midpoint Review (`Architecture midpoint red-team.md`, findings MR-06 through MR-11), `WP-PROD-TRANSACTION-PIPELINE-01-REV1` refactors and hardens the transaction foundation in `WarEconomyMod/Source/Server/Pipeline/`.

All 12 Sol E2 defects and 6 Red-Team defects have been closed:

| Finding ID | Defect Description | REV1 Architectural Correction |
|---|---|---|
| **MR-06 / QA-PIPELINE-007** | WAL + `synchronous=NORMAL` inadequate for canonical durability; connection pooling missed settings | `PRAGMA journal_mode = WAL;` and `PRAGMA synchronous = FULL;` are asserted on **every** pooled connection obtained from `SqliteDatabaseContext.CreateOpenConnection()`. Connection fails closed if mode is not FULL (`2`) or WAL. |
| **MR-07 / QA-PIPELINE-001** | Incomplete fingerprint; caller-supplied hash trusted; raw JSON whitespace defined identity; global OperationId collision | Canonical key is `(PrincipalId, OperationId)`. Server computes a versioned deterministic SHA-256 fingerprint over parsed typed fields (`OperationType`, `SchemaVersion`, `PrincipalId`, `TargetScopes[]`, `ExpectedRevisions[]`, `ContentProfileFingerprint`, `ConfigSnapshotRef`, and canonical JSON payload). Raw JSON key order/whitespace normalized via `JToken` sorting. Caller-supplied hash is strictly ignored. Same key + mismatch -> `COLLISION_REJECTED` without leaking another principal's receipt. |
| **MR-08 / QA-PIPELINE-003** | Coordinator ↔ Reconciler race; CAS failure unconditionally overwrote `PUBLISHED` as `ABORTED` | Canonical single-writer commit executor (`Channel<PipelineCommitTask>`). Fast path executes in one atomic transaction; no autonomous reconciler races live writers. All journal state transitions use monotonic expected-state guards (`UPDATE ... WHERE State = @ExpectedState`). No committed decision can ever transition to `ABORTED`. |
| **MR-09 / QA-PIPELINE-002** | PREPARED on single-scope fast path added crash state without reservation semantics; corrupt PREPARED auto-committed | **Removed PREPARED from `PIPELINE_PROBE_CAS`**. Single-scope typed domain operations execute in ONE atomic SQLite transaction combining identity arbitration, revision validation, CAS increment, immutable receipt, audit, and publication event append. (Work Order §3 & MAC-001 §C). |
| **MR-10 / QA-PIPELINE-004..006** | Outbox model conflated operation state with delivery; double delivery on crash; no cursor or ordering | Decoupled decision from delivery. Operation terminal states are `COMMITTED` or `ABORTED`. Append-only stream `PublicationEvents(StreamId, Seq, EventId, PrincipalId, OperationId, EventType, PayloadJson, PayloadFingerprint, StoreIncarnationId, CreatedAtEpochMs)` with monotonic `Seq`. Per-consumer cursor tracking in `ConsumerCursors(ConsumerId, StreamId, LastAckedSeq)`. Validating test consumer enforces idempotent dedup by `EventId` and fails closed on payload mismatch. |
| **MR-11 / QA-PIPELINE-011** | Backup restore / rollback resets fencing generations; receipt timezone recomputation mismatch | Durable `StoreIncarnationId` (persisted in `StoreIncarnations` table) stamped into receipts, events, and operations. Rotation path `RotateStoreIncarnation()` provided for restore simulation; stale incarnations rejected with `INCARNATION_MISMATCH`. Receipts use invariant UTC integer epoch milliseconds (`CommittedAtEpochMs`), guaranteeing byte/field equivalence under any culture or timezone. |
| **QA-PIPELINE-008** | Malformed or future database schema was accepted during startup | `PipelineSchemaMigration` enforces schema version 2, sets and verifies `PRAGMA application_id = 0x57415245` ("WARE"), validates required tables and columns, and fails closed with `InvalidOperationException` if `user_version > 2` or tables are missing. |
| **QA-PIPELINE-009** | 10 concurrent requests with same ID produced SQLite UNIQUE constraint violation exceptions | Single-writer Channel executor serializes in-process requests. The first request commits, and subsequent concurrent requests observe the committed record in `OperationRecords` and return `ALREADY_COMMITTED` with the stored receipt without raw SQLite exceptions. |
| **QA-PIPELINE-010** | Database lock / write contention threw unhandled `SQLITE_BUSY` (code 5) | Bounded busy timeout policy (`PRAGMA busy_timeout = 5000;`). SQLite busy/locked exceptions caught and returned as typed outcome: `STORAGE_BUSY_RETRYABLE` (`Retryable = true`). |
| **QA-PIPELINE-012** | Arbitrary `SqliteException` was misclassified as `STALE_REVISION` | Specific classification: only revision mismatch produces `STALE_REVISION`. SQLite errors map to `STORAGE_BUSY_RETRYABLE` or `STORAGE_FAILURE`. |

---

## 2. Architecture & Implementation Details

### 2.1 Operation Identity & Canonical Fingerprinting
Canonical identity is composite key `(PrincipalId, OperationId)`.
The server computes a deterministic `RequestFingerprint`:
$$\text{Fingerprint} = \text{SHA256}(\text{OperationType} \parallel \text{SchemaVersion} \parallel \text{PrincipalId} \parallel \text{ProbeScopeId} \parallel \text{ExpectedProbeRevision} \parallel \text{ContentProfileFingerprint} \parallel \text{ConfigSnapshotRef} \parallel \text{CanonicalizeJson}(\text{PayloadJson}))$$

`PipelineProbeRequest.CanonicalizeJson` parses the JSON payload into a `JToken`, recursively sorts all object keys in ordinal order, and formats without whitespace. Consequently:
- `{"b": 2, "a": 1}` and `{"a": 1, "b": 2}` yield the identical fingerprint and are deduplicated as an exact retry.
- Any change to `PrincipalId`, `ProbeScopeId`, `ExpectedProbeRevision`, `ContentProfileFingerprint`, `OperationType`, or payload values results in `COLLISION_REJECTED`.
- Different principals using the same `OperationId` operate in distinct namespaces and never collide or leak receipts.
- A caller-supplied `CallerSuppliedPayloadHash` is strictly ignored by the server.

### 2.2 Atomic Fast-Path Commit (No PREPARED)
`PIPELINE_PROBE_CAS` is a single-scope typed fast-path operation. In compliance with MAC-001 §C, the separate `PREPARED` reservation step has been removed. Execution proceeds in one atomic SQLite transaction:
1. **Identity Arbitration:** Query `OperationRecords` for `(PrincipalId, OperationId)`. If present and fingerprint matches, return stored terminal result (`COMMITTED` receipt or `ABORTED`). If fingerprint differs, roll back and return `COLLISION_REJECTED`.
2. **Revision Validation:** Compare `ProbeAggregates.ProbeRevision` with `ExpectedProbeRevision`. If mismatched, record terminal `State = ABORTED` with `FailureReason = STALE_REVISION`, write audit, commit, and return `STALE_REVISION`.
3. **Atomic CAS & Mutation:** Advance `ProbeAggregates.ProbeRevision = ExpectedProbeRevision + 1`, insert `ProbeRevisionHistory`, insert `OperationRecords(State = COMMITTED)`, insert immutable `CommitReceipt`, insert commit audit into `AuditRecords`, and append event to `PublicationEvents`.
4. **Commit:** `tx.Commit()` seals the atomic write.
5. **Post-Commit Publication:** Deliver the appended event to registered publication consumers.

### 2.3 Single-Writer Execution Ownership
Writes are dispatched through a dedicated Channel-fed executor (`Channel<PipelineCommitTask>` with an asynchronous background worker loop). This guarantees:
- Concurrent requests within the server process are serialized without thread contention.
- Reconciler and live write requests cannot race or interleave state changes.
- Monotonic guards ensure `COMMITTED` operations can never transition to `ABORTED`.

### 2.4 Decoupled Append-Only Publication Model
Operation terminal state is strictly `COMMITTED` or `ABORTED` (the status `PUBLISHED` on the operation record has been eliminated).
- Events are appended to `PublicationEvents(StreamId, Seq, EventId, PrincipalId, OperationId, EventType, PayloadJson, PayloadFingerprint, StoreIncarnationId, CreatedAtEpochMs)` with monotonic per-stream sequence `Seq`.
- Each consumer tracks its position in `ConsumerCursors(ConsumerId, StreamId, LastAckedSeq, UpdatedAtEpochMs)`.
- Validating durable test consumer (`DurableTestConsumer`) deduplicates by `EventId` and verifies payload fingerprint consistency. Redeliveries do not increment semantic effect count; payload corruption fails closed.

### 2.5 Durability, Schema & Startup Readiness
- **Durability Pragma:** `PRAGMA journal_mode = WAL;`, `PRAGMA synchronous = FULL;`, `PRAGMA busy_timeout = 5000;`, `PRAGMA foreign_keys = ON;` executed and asserted on every connection.
- **Application ID:** `PRAGMA application_id = 0x57415245;` ("WARE").
- **Schema Version:** `PRAGMA user_version = 2;`.
- **Startup Gate:** Normal server startup (`Program.cs`) executes `PipelineStartupManager.InitializeAndVerifyPipeline()` before starting the world clock or network listener. This verifies schema integrity, asserts durability, converges pending publication events to consumers, and establishes `PIPELINE_READY`.

---

## 3. Mandatory E1 Test Results (19 / 19 PASS)

All 19 mandatory E1 developer tests specified in Work Order §12 were executed via `WarEconomy.Server --test-pipeline-e1 --json scratch/pipeline_e1_rev1_results.json`:

```
==================================================================
  WP-PROD-TRANSACTION-PIPELINE-01-REV1: 19 Mandatory E1 Tests     
==================================================================
[E1_01] Exact retry stable                                                ... PASS (44.0ms)
[E1_02] Same key changed fields -> collision rejected                     ... PASS (12.0ms)
[E1_03] Semantically identical reordered JSON -> exact retry              ... PASS (7.0ms)
[E1_04] Caller fake hash cannot influence identity                        ... PASS (6.0ms)
[E1_05] 25+ independent concurrency race -> exactly 1 winner              ... PASS (105.0ms)
[E1_06] 10+ same-ID concurrent requests -> typed stable outcomes          ... PASS (7.0ms)
[E1_07] Storage busy/lock -> bounded typed outcome                        ... PASS (5281.0ms)
[E1_08] Hard kill before/inside/after commit boundaries                   ... PASS (8.0ms)
[E1_09] Consumer effect success + crash before ACK -> exactly once        ... PASS (16.0ms)
[E1_10] Transient consumer failure -> recovery eventually delivers        ... PASS (12.0ms)
[E1_11] Durable ACK + crash -> convergence without duplicate effect       ... PASS (12.0ms)
[E1_12] Fresh normal startup creates/validates DB before READY            ... PASS (32.0ms)
[E1_13] Restart with pending publication recovers before READY            ... PASS (39.0ms)
[E1_14] Malformed/future schema -> fail closed before network admission   ... PASS (97.0ms)
[E1_15] Every canonical connection effective WAL/FULL                     ... PASS (1.0ms)
[E1_16] Receipt round-trip/hash stable under timezone/culture change      ... PASS (1.0ms)
[E1_17] StoreIncarnation rotation rejects old incarnation identity        ... PASS (5.0ms)
[E1_18] Actual gameplay dispatcher cannot invoke probe                    ... PASS (0.0ms)
[E1_19] No Settlement/material/EntityId/Trade/Tax state touched           ... PASS (0.0ms)
==================================================================
E1 Summary: ALL 19 TESTS PASSED (19 / 19)
==================================================================
```

### Detailed Test Assertions

1. **E1_01 (Exact retry stable):** Initial CAS advances revision from 0 to 1 and issues receipt `9bd89b6b3ae348a6b8dee2b6194b3ca2`. Second identical request returns `ALREADY_COMMITTED` with identical `ReceiptId`, `CommittedRevision` (1), `ReceiptHash`, and `CommittedAtEpochMs`. Final revision in DB remains 1 (no double increment).
2. **E1_02 (Collision rejection):** Replaying existing `(PrincipalId, OperationId)` with changed `ProbeScopeId`, `ExpectedProbeRevision`, `ContentProfileFingerprint`, `OperationType`, or `PayloadJson` unconditionally returns `COLLISION_REJECTED`. Reusing the same `OperationId` under a different `PrincipalId` operates in an isolated namespace and succeeds without leaking the first principal's receipt.
3. **E1_03 (Reordered JSON exact retry):** Payloads `{"z": 10, "a": "alpha", "m": [3, 2, 1], "obj": {"k2": false, "k1": true}}` and `{"obj": {"k1": true, "k2": false}, "m": [3, 2, 1], "a": "alpha", "z": 10}` parse into identical typed tokens, normalize to identical canonical JSON, compute identical `RequestFingerprint`, and return `ALREADY_COMMITTED`.
4. **E1_04 (Caller fake hash ignored):** Supplying a forged `CallerSuppliedPayloadHash` has no effect on identity computation. Altering the payload while supplying the original hash is rejected as `COLLISION_REJECTED`.
5. **E1_05 (25+ concurrency race):** 25 concurrent callers contend on revision 0 for scope `SCOPE_E1_05_RACE`. Exactly 1 caller succeeds with `SUCCESS` (advancing revision to 1), and exactly 24 callers receive `STALE_REVISION`. Final revision in DB is strictly 1.
6. **E1_06 (10+ same-ID concurrent requests):** 10 concurrent tasks submit the exact same `(PrincipalId, OperationId)` and payload. Exactly 1 receives `SUCCESS` and 9 receive `ALREADY_COMMITTED`. Zero SQLite UNIQUE constraint violation exceptions bubble up.
7. **E1_07 (Storage busy/lock):** An external connection acquires an exclusive write lock. Probe execution waits up to the bounded busy timeout (5000ms) and returns typed `STORAGE_BUSY_RETRYABLE` (`Retryable = true`) without crashing.
8. **E1_08 (Hard kill boundaries):** Crash injected at `BeforeCommit` rolls back the transaction (database remains at revision 0, operation record uncommitted). Crash injected at `AfterCommitBeforeAck` leaves the committed state intact (revision 1); subsequent retry returns the stored receipt.
9. **E1_09 (Consumer effect crash before ACK):** Validating consumer applies semantic effect; crash is simulated before cursor ACK is written to database. On recovery replay, consumer recognizes duplicate `EventId` and performs idempotent deduplication. Semantic effect count remains exactly 1.
10. **E1_10 (Transient consumer failure):** Downstream consumer throws transient exception during post-commit dispatch. Commit succeeds, and event remains in append-only log. Recovery convergence redispatches event when consumer recovers.
11. **E1_11 (Durable ACK convergence):** Consumer ACK updates cursor in `ConsumerCursors`. A subsequent recovery scan verifies that already-acknowledged events are skipped (0 replayed events, effect count unchanged).
12. **E1_12 (Fresh normal startup):** Starting against a non-existent database file successfully creates the database, applies schema v2 migrations, validates application ID and PRAGMAs, and sets `PIPELINE_READY`.
13. **E1_13 (Restart pending publication recovery):** Database containing unacknowledged events is opened via `PipelineStartupManager.InitializeAndVerifyPipeline()`. Pending events are converged to the consumer before `PIPELINE_READY` is reached.
14. **E1_14 (Schema fail closed):** Databases with future schema version (`user_version = 999`) or missing required tables throw `InvalidOperationException` and abort startup before admitting network traffic.
15. **E1_15 (Every connection WAL/FULL):** 10 consecutive pooled connections created from context are inspected. All 10 report `journal_mode = wal`, `synchronous = 2` (FULL), and `application_id = 0x57415245`.
16. **E1_16 (Culture and timezone invariance):** Receipt hash and integer epoch milliseconds recomputed under 6 distinct cultures (`tr-TR`, `ar-SA`, `ko-KR`, `en-US`, `zh-CN`, `de-DE`) remain 100% byte-identical.
17. **E1_17 (StoreIncarnation rotation):** Active incarnation rotated from initial ID to new ID. Subsequent request bearing the old incarnation ID is rejected with `INCARNATION_MISMATCH`.
18. **E1_18 (Gameplay dispatcher isolation):** Packet handling routines contain no route for probe execution. `InternalProbeTestSurface.TryInvokeFromGameplayTransport` unconditionally returns `ACCESS_DENIED`.
19. **E1_19 (No gameplay state touched):** Verified that probe database contains zero gameplay tables (`Settlements`, `Materials`, `Entities`, `TradeConfigurations`, `TaxLedger`, `TacticalEvents`).

---

## 4. Frozen Artifact Manifest & Hash Provenance

### 4.1 Production Source Files
| File Path | Byte Size | Verified SHA-256 |
|---|---|---|
| `WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs` | 22,198 | `5F761BE57316A81680EF148F38B3C1B9A9B6074F721D3B7B902AA2F792F808A1` |
| `WarEconomyMod/Source/Server/Pipeline/Data/SqliteDatabaseContext.cs` | 8,465 | `384709312E389B22C4F5A34025F574B20E87114655BB40B011632795B8BE1624` |
| `WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs` | 13,300 | `3C10FE553549AD545054D6CC1FC10EF885B8B8E99C79BDD8F8EE7C2BA7C96FE2` |
| `WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs` | 12,144 | `B898A0DA9464F94D7771CFE152E0CD468702B06D3A56FCE349EE584240FF35BA` |
| `WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs` | 4,037 | `460A249834A1D78C335BBFB5D3029ED1D10042F1AE2E74FA4CAD8545F6BFBEE1` |
| `WarEconomyMod/Source/Server/Pipeline/Security/InternalProbeTestSurface.cs` | 1,443 | `3B81699D95F45C920DEA1764B223196DA7560A08B226E231DF3E59B2CF8FA9A3` |
| `WarEconomyMod/Source/Server/Pipeline/Storage/AuditLogRepository.cs` | 1,828 | `5A885964386BE2587A859C5345A3D55593E4499E924C546C8E7F6FB89A0387AE` |
| `WarEconomyMod/Source/Server/Pipeline/Storage/CommitReceiptRepository.cs` | 3,189 | `BC13BE5F360642CC5CBC53B36A3776E3B9B35658D0BFDD044BEEE18FBEEB9AA2` |
| `WarEconomyMod/Source/Server/Pipeline/Storage/OperationJournal.cs` | 8,621 | `4050C7788F48E62BD00E122CDA9528050C75B95A7E9898E868C59E80CE73CFA5` |
| `WarEconomyMod/Source/Server/Pipeline/Storage/ProbeAggregateStore.cs` | 5,143 | `BCBC7203281ECE909AF02A8343AB4BF932F6B816928BC5A39F3AC49AA28CCE29` |
| `WarEconomyMod/Source/Server/Pipeline/Storage/PublicationEventStore.cs` | 9,376 | `1780F4074B46EEF844D1C3E2652DAEF36D6A9251EA1659207827D53F9FB7AC22` |
| `WarEconomyMod/Source/Server/Pipeline/Testing/DurableTestConsumer.cs` | 3,542 | `2BD955246DED26780DACF5EA4AA85F183D45ECBF28A0874AA9690218411D5873` |
| `WarEconomyMod/Source/Server/Pipeline/Testing/PipelineE1TestBattery.cs` | 46,925 | `00A06D4BB00E1562DDCD347AB0E0B6D7F8A2C90A7332F98C58AE5D2C679FA079` |
| `WarEconomyMod/Source/Server/Program.cs` | 8,866 | `2753E74BEACD37FC5E8A2C27A027868A78E65DB0C0A10B74ABB97998DFF10915` |

### 4.2 Production Server Binaries (.NET 8.0)
| Target Binary | Configuration | Byte Size | Verified SHA-256 |
|---|---|---|---|
| `WarEconomy.Server.dll` | Release | 174,080 | `288AADC7C8B88A3492583797F2D4537F73EC88362723671E0222BF0AEDB3ED8C` |
| `WarEconomy.Server.exe` | Release | 151,552 | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |
| `WarEconomy.Server.dll` | Debug | 188,928 | `FE52E1C52D9B633DA6A062DC88D4300D627515DE07BD831B2C0090B74633BEB3` |
| `WarEconomy.Server.exe` | Debug | 151,552 | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |

### 4.3 Test Evidence Artifacts
| Evidence File | Byte Size | Verified SHA-256 |
|---|---|---|
| `scratch/pipeline_e1_rev1_results.json` | 5,823 | `21703666C93CDDBEF43997FE58FD49B809E054EB92D1D60B61545625D6B6EEF0` |
| `scratch/pipeline_e1_rev1_release_results.json` | 5,823 | `3EDEF4607B4F5583CD6EE86A633F2E0883C7E951E91C0E28565BFD40F08B2189` |

### 4.4 Canonical Schema DDL (Version 2)
```sql
PRAGMA application_id = 1463898693; -- 0x57415245 ("WARE")
PRAGMA user_version = 2;

CREATE TABLE IF NOT EXISTS StoreIncarnations (
    IncarnationId TEXT PRIMARY KEY NOT NULL,
    IsActive INTEGER NOT NULL CHECK (IsActive IN (0, 1)),
    CreatedAtEpochMs INTEGER NOT NULL,
    RotatedAtEpochMs INTEGER
);

CREATE TABLE IF NOT EXISTS ProbeAggregates (
    ProbeScopeId TEXT PRIMARY KEY NOT NULL,
    ProbeRevision INTEGER NOT NULL CHECK (ProbeRevision >= 0),
    CreatedAtEpochMs INTEGER NOT NULL,
    UpdatedAtEpochMs INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ProbeRevisionHistory (
    ProbeScopeId TEXT NOT NULL,
    ProbeRevision INTEGER NOT NULL,
    OperationId TEXT NOT NULL,
    CommittedAtEpochMs INTEGER NOT NULL,
    PRIMARY KEY (ProbeScopeId, ProbeRevision)
);

CREATE TABLE IF NOT EXISTS OperationRecords (
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    OperationType TEXT NOT NULL,
    OperationSchemaVersion INTEGER NOT NULL,
    ProbeScopeId TEXT NOT NULL,
    ExpectedProbeRevision INTEGER NOT NULL,
    RequestFingerprint TEXT NOT NULL,
    PayloadJson TEXT NOT NULL,
    ContentProfileFingerprint TEXT NOT NULL,
    ConfigSnapshotRef TEXT,
    State TEXT NOT NULL CHECK (State IN ('COMMITTED', 'ABORTED')),
    FailureReason TEXT,
    StoreIncarnationId TEXT NOT NULL,
    CreatedAtEpochMs INTEGER NOT NULL,
    UpdatedAtEpochMs INTEGER NOT NULL,
    PRIMARY KEY (PrincipalId, OperationId)
);

CREATE TABLE IF NOT EXISTS CommitReceipts (
    ReceiptId TEXT PRIMARY KEY NOT NULL,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    ProbeScopeId TEXT NOT NULL,
    CommittedRevision INTEGER NOT NULL,
    StoreIncarnationId TEXT NOT NULL,
    CommittedAtEpochMs INTEGER NOT NULL,
    ReceiptHash TEXT NOT NULL,
    FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId)
);

CREATE TABLE IF NOT EXISTS AuditRecords (
    AuditId TEXT PRIMARY KEY NOT NULL,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    ProbeScopeId TEXT NOT NULL,
    EventType TEXT NOT NULL,
    OldRevision INTEGER,
    NewRevision INTEGER,
    DetailsJson TEXT,
    TimestampEpochMs INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS PublicationEvents (
    StreamId TEXT NOT NULL,
    Seq INTEGER NOT NULL,
    EventId TEXT NOT NULL UNIQUE,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    EventType TEXT NOT NULL,
    PayloadJson TEXT NOT NULL,
    PayloadFingerprint TEXT NOT NULL,
    StoreIncarnationId TEXT NOT NULL,
    CreatedAtEpochMs INTEGER NOT NULL,
    PRIMARY KEY (StreamId, Seq)
);

CREATE TABLE IF NOT EXISTS ConsumerCursors (
    ConsumerId TEXT NOT NULL,
    StreamId TEXT NOT NULL,
    LastAckedSeq INTEGER NOT NULL DEFAULT 0,
    UpdatedAtEpochMs INTEGER NOT NULL,
    PRIMARY KEY (ConsumerId, StreamId)
);

CREATE TABLE IF NOT EXISTS ConsumerDurableAcks (
    ConsumerId TEXT NOT NULL,
    EventId TEXT NOT NULL,
    AckedAtEpochMs INTEGER NOT NULL,
    PRIMARY KEY (ConsumerId, EventId)
);
```

---

## 5. Explicit Non-Goals & Scope Limits

In strict adherence to Work Order §13 and MAC-001 §H:
1. **No PREPARED reservation path implemented**: `PIPELINE_PROBE_CAS` is single-scope and executes purely on the atomic fast path. Multi-scope reservations and staged material contracts remain deferred.
2. **No real gameplay mutations**: No Settlement inventory or material state touched; no `CommittedSettlementStateRevision` increment; no `ArtifactBaseStateRevision` change.
3. **No TradeConfiguration, Tax, or Auto-Shop state**: No Player/Faction/Settlement registries; no Def admission; no market/trade mutations.
4. **No Tactical Publication**: Tactical Worker and Remote Presentation components remain completely untouched.

---

## 6. Final Status & Conclusion

- **Classification:** **`E1 PIPELINE REV1 PASS`**
- All 19 developer test cases pass consistently under both Debug and Release configurations.
- All defects from Sol E2 (`QA_Production_Transaction_Pipeline_01.md`) and Midpoint Review (`MR-06..MR-11`) have been closed.
- Source files, binaries, schema DDL, and test evidence artifacts are frozen and hash-verified.
- Work on `WP-PROD-TRANSACTION-PIPELINE-01-REV1` is complete. Stopping as instructed for independent Sol E2 verification.
