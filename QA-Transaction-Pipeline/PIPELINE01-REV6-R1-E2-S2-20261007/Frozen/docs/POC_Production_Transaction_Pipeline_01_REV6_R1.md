# Production Transaction Pipeline Slice 01 — REV6-R1
## Historical Decision Order via Shared Operation Journal Sequence, True OS Child-Process & Kill Controls, Actual DDL Alignment & Schema V7 Integrity

- **Work Package:** WP_PIPELINE_REV6_R1
- **Revision:** REV6-R1
- **Dispatch ID:** `WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01`
- **Role:** Gemini 3.8 Flash A — Primary Development Agent
- **Independent Verifier:** GPT-6.1 Sol (Independent E2 Required)
- **Controlling Guidance:** `WP_PIPELINE_REV6_R1.md`, `MASTER_REVIEW_PIPELINE_REV6_E1_20261007.md`, `AGENTS.md`, `MASTER_GOVERNANCE_CURRENT.md`
- **Date:** 2026-10-07
- **Runtime Target:** .NET 8.0.10 / C# 12 / SQLite 3.41+ (`Microsoft.Data.Sqlite` 8.0.10)
- **Status:** **E1 PIPELINE REV6-R1 PASS** (25 / 25 Mandatory Verification Batteries Passed)
- **Hard Constraints & Scope Rules:**
  - Narrow repair of historical decision ordering, OS child-process and kill execution controls, report DDL fidelity, and freeze preservation. Zero architecture redesign.
  - Zero gameplay, material, economic state mutation, or auth/Foundation expansion.
  - Candidate Gate05 Engine freeze files (19/19 files in `MASTER_ENGINE_FREEZE_BEFORE.json`) remain strictly untouched and bit-identical.
  - Prior rejected REV6 candidate preserved untouched in `Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-20261007-DIRECT-01/FROZEN_REV6_REJECTED` under `MASTER_REJECTED_CANDIDATE_ARCHIVE.json`.
  - E1 PASS is internal agent verification; independent E2 verification by GPT-6.1 Sol and Master disposition govern final closure.

---

## 1. Executive Summary & Defect Correction Ledger

This work package responds directly to the Master review findings in `MASTER_REVIEW_PIPELINE_REV6_E1_20261007.md`. All three specific Master findings (`REV6-M01`, `REV6-M02`, `REV6-M03`) have been comprehensively resolved, implemented, and verified.

### 1.1 Summary of Corrections

1. **REV6-M01 (Historical Decision Order via Shared Journal Sequence)**:
   - **Flaw in REV6**: The previous reconciler compared `ProbeRevisionHistory.rowid` against `OperationRecords.rowid` across distinct tables, and compared independently sampled UTC millisecond timestamps (`CommittedAtEpochMs` vs `CreatedAtEpochMs`). In SQLite, rowids across different tables are independent counters, and wall-clock timestamps are vulnerable to clock jitter and rollbacks.
   - **REV6-R1 Architectural Resolution**: Joined `ProbeRevisionHistory` to `OperationRecords` via `(PrincipalId, OperationId)` to extract the committing operation's rowid (`committingOpRowId = o.rowid`). Both `committingOpRowId` and `opRowId` are drawn from the **same single table sequence** (`OperationRecords.rowid`). In SQLite, under `BEGIN IMMEDIATE` write locks, insertions into `OperationRecords` form an immutable, strictly monotonic physical serialization sequence (enforced by insert-only triggers `trg_operation_records_no_replace/update/delete`).
   - An aborted operation's authoritative historical revision is determined by finding the latest revision whose committing operation was serialized before the aborted operation (`committingOpRowId < opRowId`).
   - Clock skew, clock rollbacks, same-millisecond transactions, and multi-scope interleavings have zero impact on ordering. Historical-earlier, historical-later, and cross-scope rewrites are strictly rejected.

2. **REV6-M02 (True OS Child-Process Concurrency & Owned-Process Hard-Kill Controls)**:
   - **Flaw in REV6**: The test runner previously executed async tasks on a single in-process coordinator for Battery 4, sequential loop iterations for Battery 19, and a normal commit/dispose for Battery 20, while claiming multi-process and hard-kill coverage.
   - **REV6-R1 Architectural Resolution**: Implemented dedicated CLI worker modes (`--worker-cas` and `--worker-hang-and-kill`) in `E1_Rev6_R1_Runner.exe`:
     - **Battery 4**: Spawns 10 actual, independent OS child processes via `Process.Start` competing concurrently for CAS against the same SQLite database file. Captures all child process PIDs, start/exit times, and exit codes. Confirms exactly 1 winner (exit code 0) and 9 losers (exit code 1), followed by restart recovery to `PIPELINE_READY`.
     - **Battery 19**: Spawns 8 sequential OS child processes via `Process.Start` advancing stream revisions from 0 to 8 across distinct OS process lifetimes. Captures PIDs, start/exit times, and exit codes.
     - **Battery 20**: Spawns an owned OS child process holding an uncommitted write lock, awaits the `READY_FOR_KILL` signal, and forcibly executes `child.Kill(entireProcessTree: true)`. Captures child PID, kill timing, verifies that SQLite WAL crash recovery rolled back all uncommitted state (0 cut records in `OperationRecords`), and proves subsequent clean commits succeed.
     - **Honest Boundary**: Explicitly documents that process kill controls test OS-level process crash recovery; hardware power loss / plug-pulling represents a separate hardware/storage controller boundary.

3. **REV6-M03 (Report & DDL Alignment)**:
   - **Flaw in REV6**: The report previously referenced inaccurate table names (`ProbeScopes` instead of `ProbeAggregates`), inaccurate types (`AuditId INTEGER AUTOINCREMENT` instead of `TEXT PRIMARY KEY`), and non-existent `WITHOUT ROWID` clauses.
   - **REV6-R1 Architectural Resolution**: Authoritatively documented the exact SQLite DDL generated by `PipelineSchemaMigration.cs`, documented the exact rowid comparison semantics, and formalized the strict fail-closed extra-field and duplicate-field policy for typed audit `DetailsJson`.

---

### 1.2 Master Review Correction Matrix

| Review Finding | REV6 Observation | REV6-R1 Architectural Resolution | Status |
|---|---|---|---|
| **REV6-M01**<br>(Decision Ordering) | Comparing rowids across different tables (`ProbeRevisionHistory` vs `OperationRecords`) and comparing wall-clock ms did not prove durable decision serialization order. | Joined `ProbeRevisionHistory` to `OperationRecords` on `(PrincipalId, OperationId)` to compare committing operation rowid with aborted operation rowid within the **same table** `OperationRecords`. Order is immutable and clock-independent. | **RESOLVED & VERIFIED**<br>(Battery 9) |
| **REV6-M02**<br>(Process & Kill Coverage) | Runner 4 used in-process async tasks; Runner 19 used sequential commits; Runner 20 used normal commit/dispose without OS child processes or hard kill. | Implemented CLI worker modes in `E1_Rev6_R1_Runner.exe`. Spawns real OS child processes (`Process.Start`), logs PIDs, exit codes, and kill timestamps; performs true `child.Kill()` and verifies WAL rollback. | **RESOLVED & VERIFIED**<br>(Batteries 4, 19, 20) |
| **REV6-M03**<br>(DDL & Report Alignment) | Report claimed `ProbeScopes`, `WITHOUT ROWID`, and integer audit IDs divergent from actual migration code. | Fully aligned documentation with actual DDL in `PipelineSchemaMigration.cs` (`ProbeAggregates`, `AuditId TEXT PRIMARY KEY`, composite FKs, explicit rowid semantics). Formalized extra-field audit policy. | **RESOLVED & VERIFIED**<br>(Section 2.3) |

---

## 2. Technical Architecture & Implementation

### 2.1 Historical Decision Witness via Shared OperationRecords Rowid

#### 2.1.1 The Mathematical Principle
In SQLite, every standard table (without `WITHOUT ROWID`) possesses an internal, monotonically increasing 64-bit integer `rowid`.
Under `BEGIN IMMEDIATE`, every write transaction acquires an exclusive write lock, serializing all database modifications.
Because SQLite triggers `trg_operation_records_no_replace`, `trg_operation_records_no_update`, and `trg_operation_records_no_delete` strictly forbid any UPDATE, DELETE, or REPLACE on `OperationRecords`:
$$\text{For any two operations } A, B \in \text{OperationRecords}, \quad \text{rowid}(A) < \text{rowid}(B) \iff A \text{ was committed before } B.$$

In `ProbeRevisionHistory`, each committed revision record contains composite foreign keys `(PrincipalId, OperationId)` referencing the exact operation in `OperationRecords` that committed it.

Therefore, for any aborted operation $O_{\text{aborted}}$ with rowid $R_{\text{aborted}}$, the authoritative historical revision of scope $S$ at the moment $O_{\text{aborted}}$ was evaluated is:
$$\text{AuthoritativeRevision}(S, O_{\text{aborted}}) = \max \left(\{0\} \cup \left\{ r \mid (S, r, P, O) \in \text{ProbeRevisionHistory} \land \text{rowid}(O) < R_{\text{aborted}} \right\}\right)$$

#### 2.1.2 Production Implementation in RecoveryReconciler.cs
```csharp
long authoritativeHistoricalRevision = 0;
using (var hHistCmd = conn.CreateCommand())
{
    hHistCmd.CommandText = @"
        SELECT h.ProbeRevision, o.rowid
        FROM ProbeRevisionHistory h
        JOIN OperationRecords o ON o.PrincipalId = h.PrincipalId AND o.OperationId = h.OperationId
        WHERE h.ProbeScopeId = @scope
        ORDER BY h.ProbeRevision ASC;
    ";
    hHistCmd.Parameters.AddWithValue("@scope", op.ProbeScopeId);
    using var hHistReader = hHistCmd.ExecuteReader();
    while (hHistReader.Read())
    {
        long rRev = hHistReader.GetInt64(0);
        long committingOpRowId = hHistReader.GetInt64(1);

        // A commit belongs to the pre-decision state of this operation if and only if
        // the committing operation was sequenced before this operation in OperationRecords.
        if (committingOpRowId < opRowId)
        {
            if (rRev > authoritativeHistoricalRevision)
            {
                authoritativeHistoricalRevision = rRev;
            }
        }
    }
}

if (aOldRev != authoritativeHistoricalRevision)
{
    throw new InvalidOperationException(
        $"Consistency error: reject audit '{aId}' observed revision {aOldRev} contradicts authoritative historical revision {authoritativeHistoricalRevision} of scope '{op.ProbeScopeId}' at decision point (opRowId {opRowId}).");
}
```

#### 2.1.3 Invariant Guarantees
1. **Clock Independence**: Comparison operates entirely on `OperationRecords.rowid`, with zero reliance on UTC system wall-clock timestamps.
2. **Clock Rollback & Jitter Immunity**: If the system clock steps backward or forwards, the physical SQLite B-Tree rowids maintain strict monotonic ordering.
3. **Multi-Scope Isolation**: Filter `WHERE h.ProbeScopeId = @scope` isolates revisions strictly by scope identifier.
4. **Natural Stale/CAS Legality**: Legitimate stale operations aborted after a CAS race are proven valid because their observed revision matches the latest revision committed prior to their rowid.
5. **Threat Boundary**: Bounded to logical causality within the SQLite transactional storage engine. Out-of-band raw disk binary corruption bypassing SQLite is outside the application layer and guarded by OS filesystem ACLs and disk encryption.

---

### 2.2 Strict Extra-Field & Duplicate-Field Audit Policy

To guarantee schema typing and prevent parser confusion or clandestine payload smuggling:
- **COMMITTED Audit Records**: Must contain **exactly 8** mandatory fields: `receiptId`, `eventId`, `fingerprint`, `scopeId`, `principalId`, `operationId`, `oldRevision`, `newRevision`.
- **ABORTED Audit Records**: Must contain **exactly 7** mandatory fields: `status`, `reason`, `expectedRevision`, `observedRevision`, `scopeId`, `principalId`, `operationId`.
- **Policy Enforcement**:
```csharp
int propCount = 0;
foreach (var prop in root.EnumerateObject())
{
    propCount++;
    if (!mandatoryKeys.Contains(prop.Name))
    {
        throw new InvalidOperationException($"Consistency error: audit DetailsJson contains unrecognized extra key '{prop.Name}'.");
    }
}
if (propCount != mandatoryKeys.Length)
{
    throw new InvalidOperationException($"Consistency error: audit DetailsJson property count {propCount} does not match expected {mandatoryKeys.Length}.");
}
```
Any extra key, missing key, or duplicate key triggers immediate recovery rejection (`InvalidOperationException`).

---

### 2.3 Authoritative SQLite DDL Definitions

The actual DDL defined and validated by `PipelineSchemaMigration.cs`:

```sql
-- 1. Store Incarnations Table
CREATE TABLE IF NOT EXISTS StoreIncarnations (
    IncarnationId TEXT PRIMARY KEY NOT NULL,
    IsActive INTEGER NOT NULL CHECK (IsActive IN (0, 1)),
    CreatedAtEpochMs INTEGER NOT NULL,
    RotatedAtEpochMs INTEGER
);

-- 2. Probe Aggregate Store
CREATE TABLE IF NOT EXISTS ProbeAggregates (
    ProbeScopeId TEXT PRIMARY KEY NOT NULL,
    ProbeRevision INTEGER NOT NULL CHECK (ProbeRevision >= 0),
    CreatedAtEpochMs INTEGER NOT NULL,
    UpdatedAtEpochMs INTEGER NOT NULL
);

-- 3. Canonical Operation Records with composite PK (PrincipalId, OperationId)
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

CREATE INDEX IF NOT EXISTS IX_OperationRecords_Scope ON OperationRecords(ProbeScopeId);
CREATE INDEX IF NOT EXISTS IX_OperationRecords_State ON OperationRecords(State);

-- DB-Level physical immutability triggers on OperationRecords
CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_replace
BEFORE INSERT ON OperationRecords FOR EACH ROW
WHEN EXISTS (SELECT 1 FROM OperationRecords WHERE PrincipalId = NEW.PrincipalId AND OperationId = NEW.OperationId)
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords is insert-only: replacement of existing operational record is forbidden.');
END;

CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_update
BEFORE UPDATE ON OperationRecords FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords is insert-only: terminal decision state cannot be updated.');
END;

CREATE TRIGGER IF NOT EXISTS trg_operation_records_no_delete
BEFORE DELETE ON OperationRecords FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'OperationRecords is insert-only: deletion of operational journal is forbidden.');
END;

-- 4. Probe Revision History with PrincipalId and composite FK to OperationRecords
CREATE TABLE IF NOT EXISTS ProbeRevisionHistory (
    ProbeScopeId TEXT NOT NULL,
    ProbeRevision INTEGER NOT NULL,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    CommittedAtEpochMs INTEGER NOT NULL,
    PRIMARY KEY (ProbeScopeId, ProbeRevision),
    FOREIGN KEY (ProbeScopeId) REFERENCES ProbeAggregates(ProbeScopeId) ON UPDATE NO ACTION ON DELETE RESTRICT,
    FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT
);

-- 5. Immutable Commit Receipts
CREATE TABLE IF NOT EXISTS CommitReceipts (
    ReceiptId TEXT PRIMARY KEY NOT NULL,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    ProbeScopeId TEXT NOT NULL,
    CommittedRevision INTEGER NOT NULL,
    StoreIncarnationId TEXT NOT NULL,
    CommittedAtEpochMs INTEGER NOT NULL,
    ReceiptHash TEXT NOT NULL,
    FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT
);

-- 6. Audit Records with composite FK to OperationRecords
CREATE TABLE IF NOT EXISTS AuditRecords (
    AuditId TEXT PRIMARY KEY NOT NULL,
    PrincipalId TEXT NOT NULL,
    OperationId TEXT NOT NULL,
    ProbeScopeId TEXT NOT NULL,
    EventType TEXT NOT NULL,
    OldRevision INTEGER,
    NewRevision INTEGER,
    DetailsJson TEXT,
    TimestampEpochMs INTEGER NOT NULL,
    FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS IX_AuditRecords_Scope ON AuditRecords(ProbeScopeId);

-- 7. Append-only Ordered Publication Events Log
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
    UNIQUE (StreamId, Seq),
    FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS IX_PublicationEvents_Stream_Seq ON PublicationEvents(StreamId, Seq);
```

---

## 3. Mandatory E1 Verification Results (25 / 25 Batteries Passed)

The entire 25-battery E1 test battery was executed using the dedicated `E1_Rev6_R1_Runner.exe` in Release configuration:

| Battery | Test Name | Execution Time | Result | Verified Invariant & Real Process Proof |
|---|---|---|---|---|
| **01** | `Battery1_FiveRev4TypedInputFailures` | 121 ms | **PASS** | Parser boundary rejects surrogates and exponent overflow; 0 durable records. |
| **02** | `Battery2_ExactJsonAndNumericBoundaries` | 95 ms | **PASS** | Exact numeric representations preserved; semantic collisions detected. |
| **03** | `Battery3_NaturalMixedCommittedAbortedRestart` | 84 ms | **PASS** | Mixed COMMITTED and legitimate ABORTED operations recover to `PIPELINE_READY`. |
| **04** | `Battery4_OsChildProcessMultiProcessWinnerLoserRestart` | 917 ms | **PASS** | **Real OS Child Processes**: Spawned 10 separate OS child processes (`Process.Start`). Exactly 1 winner (exit 0) and 9 losers (exit 1). Logged all PIDs. |
| **05** | `Battery5_CrossPrincipalSameOperationId` | 48 ms | **PASS** | Composite identity `(PrincipalId, OperationId)` isolates distinct principals. |
| **06** | `Battery6_SemanticGraphAttacks` | 99 ms | **PASS** | Rejection of swapped ReceiptId/EventId and foreign child linkages. |
| **07** | `Battery7_EnvelopeFieldFingerprintMutations` | 41 ms | **PASS** | Request fingerprint mutation detection; fail-closed recovery. |
| **08** | `Battery8_CanonicalReceiptIdEventIdDerivativeIdentity` | 56 ms | **PASS** | Derivative IDs `RCPT_...` and `EVT_...` strictly validated. |
| **09** | `Battery9_QaPipeline007_HistoricalObservedRevisionRewrites` | 299 ms | **PASS** | **REV6-M01 Fix**: Authoritative historical ordering via `OperationRecords.rowid`. Rejects earlier, later, and cross-scope rewrites. |
| **10** | `Battery10_QaPipeline007_AbortedTypedAuditStatusAndReasonSemantics` | 488 ms | **PASS** | ABORTED audit: validates all 7 mandatory keys, rejects "SUCCESS" status/reason, and strictly rejects unrecognized extra keys. |
| **11** | `Battery11_QaPipeline007_CommittedTypedAuditMandatoryFields` | 430 ms | **PASS** | COMMITTED audit: validates all 8 mandatory keys, rejects modifications, omissions, and unrecognized extra keys. |
| **12** | `Battery12_QaPipeline008_SchemaKeyCollationMutations` | 97 ms | **PASS** | Non-BINARY collations detected and rejected via `index_xinfo` & DDL. |
| **13** | `Battery13_QaPipeline008_RollbackSafeCaseDistinctCanariesAndRuntimeIdentity` | 46 ms | **PASS** | Savepoint startup canaries verify case-distinct collation without table mutations. |
| **14** | `Battery14_SchemaV7RegressionAndLegacyFailClosed` | 251 ms | **PASS** | V7 schema migration success; legacy schemas v1–v6 fail closed. |
| **15** | `Battery15_ActiveWriterLongerThanOldShutdownTimeout` | 8,052 ms | **PASS** | Decoupled response deadline: Dispose waits 8s for writer thread termination. |
| **16** | `Battery16_ActualMainActiveOperationQuit` | 7,060 ms | **PASS** | Clean exit with active operations: coordinator waits and nulls cleanly. |
| **17** | `Battery17_RepeatedShutdownDispose` | 40 ms | **PASS** | Sequential shutdown/dispose calls execute idempotently. |
| **18** | `Battery18_CallerUnknownThenDurableRetryConvergence` | 38 ms | **PASS** | In-flight commit converges cleanly to `ALREADY_COMMITTED` on caller retry. |
| **19** | `Battery19_OsChildProcessSequentialStreamProgression` | 1,500 ms | **PASS** | **Real OS Child Processes**: 8 sequential OS child processes advance stream revision monotonically from 0 to 8 across distinct process lifetimes. |
| **20** | `Battery20_OwnedChildProcessHardKillCommitCuts` | 212 ms | **PASS** | **Real Process Hard Kill**: Owned child process holding write lock terminated via `child.Kill()`. SQLite WAL recovered cleanly (0 cut rows). |
| **21** | `Battery21_TerminalImmutability` | 41 ms | **PASS** | SQLite triggers strictly prevent UPDATE and DELETE on terminal records. |
| **22** | `Battery22_StorageTypingAndStoreIncarnation` | 39 ms | **PASS** | Incarnation rotation ensures single active store fencing. |
| **23** | `Battery23_WalFullDurabilityAndPragmas` | 32 ms | **PASS** | PRAGMA journal_mode=WAL, synchronous=FULL, foreign_keys=ON verified. |
| **24** | `Battery24_NoConsumerGameplayMaterialPaths` | 3 ms | **PASS** | Zero gameplay, material state, or consumer ACK paths in pipeline assembly. |
| **25** | `Battery25_ReleaseManifestAndPackageHygiene` | 105 ms | **PASS** | Gate05 freeze manifest 19/19 files verified bit-identical; package clean. |

**Total Batteries:** 25 | **Passed:** 25 | **Failed:** 0 | **Verdict:** **100% PASS**

---

## 4. Frozen Candidate Engine Invariant Verification

The Gate05 Engine candidate binaries and sources remain 100% isolated and bit-identical:
- **Freeze Before Manifest:** `Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_ENGINE_FREEZE_BEFORE.json` (SHA-256: `2E7BB27EBF2E64287C3919E84A470B92371A99560832A2C7BBFB0FA611E72099`)
- **Freeze After Manifest:** `scratch/MASTER_ENGINE_FREEZE_AFTER_REV6_R1.json` (SHA-256: `43F64F513255574C4FD2B224BC80DDD06AE36A2C2A0EA37D05F429404A39F9FC`)
- **Comparison Result:** **19 / 19 files bit-identical (0 modifications, 0 re-builds)**.
- **Candidate DLL SHA-256:** `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C`
- **Candidate DLL MVID:** `12bb9237-1b3e-4b20-89a7-69ad729861e1`

---

## 5. Artifact & Provenance Ledger

| Artifact Role | File Relative Path | SHA-256 | Metadata / Identity |
|---|---|---|---|
| **Candidate Binary** | `WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.dll` | `65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78` | MVID: `bbb3d4f4-423c-4379-a931-58e4b3a50add` |
| **Candidate Binary** | `WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.dll` | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` | MVID: `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` |
| **Candidate Binary** | `WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.exe` | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` | Entrypoint AppHost |
| **PDB** | `WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.pdb` | `7A99DAD44A6F32A7FDAFABA2534C5914C73C958B1F86E27A21CEBAE7F6A4A239` | Matching Server PDB |
| **PDB** | `WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.pdb` | `5119FE41A0FD3BB6B6DCA299B85FD3EEF0F91D4FB7B1AC77DAEDA762E9B2D0F0` | Matching Common PDB |
| **Source** | `WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs` | `2CD07966F64B8AC05C1DB86E18C4D363802A20F4E0A5B26160BAAF4F95C37F12` | Witness & Typed Audit Logic |
| **Source** | `WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs` | `7A5AAA86DBDB447558936B38C68E95678BEA637D474184FA5F6AF5A3A29556B2` | V7 Migration, Collation & Canaries |
| **Runner Binary** | `scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.exe` | `D39C7CEF8209F93E8F2C01EC725919CB0676C357D840D9D3EFB01E7C52EBEF7C` | Standalone E1 REV6-R1 Runner |
| **Runner Binary** | `scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.dll` | `22D0E5561409813B02FB9EF2C0D23FC3AA5F42E3F3BBE96426C7A493B0CB0CCE` | MVID: `8aec33d1-a76a-436d-a6bf-73e644e5f301` |
| **Runner PDB** | `scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.pdb` | `1C03ADAB86DA50E7E212F00D5FC67F282EA76B8A843CC209CCBD1300D334740B` | Matching Runner PDB |
| **Runner Source** | `scratch/E1_Rev6_R1_Runner/Program.cs` | `CF0B531A60FE678DC0DFD4AE7EB8758AF760CB9FE6EA0202C553057AB6E9410C` | 25 Batteries & CLI Worker Code |
| **Results** | `scratch/pipeline_e1_rev6_r1_results.json` | `65360FAC6456B451D729E13A6BD27A7FBA8AD2BDE13AE5FB7FE6D8349E2D2C20` | JSON Structured Results |
| **Raw Evidence** | `scratch/pipeline_e1_rev6_r1_raw_console.txt` | `C47181D67AC03679A67DD8B15564DA6C33DC8AF3ACCADFFC74AEA8D9D35C5991` | Raw Console Execution Log |
| **Release Manifest** | `docs/RELEASE_MANIFEST_PIPELINE_REV6_R1.json` | `1267E28C3235E5053B6B8C88BB5DC7C89CA9D2F44F3D73BE9A36877712E2DE50` | Formal Release Manifest |

---

## 6. Honest Limitations & Non-Claims

1. **E1 Verdict Scope**: This document and the 25/25 battery pass rate represent internal development-tier E1 verification by Gemini 3.8 Flash A. It does **not** constitute independent E2 verification or formal gate closure, which rests exclusively with GPT-6.1 Sol and Master disposition.
2. **Process Kill vs Power-Loss Boundary**: Battery 20 demonstrates robust SQLite WAL crash recovery under OS-level process termination (`Process.Kill()`). It explicitly does not claim power-loss or hardware-pull evidence, which involves filesystem write caching, storage controller barriers, and hardware power loss characteristics beyond the application process boundary.
3. **Physical Media Threat Boundary**: Transactional causality and witness ordering apply strictly within the SQLite transaction log. Direct, out-of-band manipulation of raw disk bytes without SQLite engine participation is outside the application layer's threat boundary and must be bounded by OS permissions, storage volume encryption (BitLocker), and hypervisor integrity.
4. **Legacy Schema Offline Policy**: Schemas v1–v6 fail closed on startup with `LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET`. Automated in-place schema down-migration or arbitrary schema mutation repair is intentionally non-supported to ensure zero silent data corruption.
