# POC_EngineHost_Gate05_R24_M04_Preparation.md
**Work Package**: `WP_ENGINE_GATE05_R24_ROLE_LAUNCH_CONTRACT_PREPARATION`  
**Revision**: `GATE05-R24-M04-PREP`  
**Envelope**: `envelope27`  
**Dispatch ID**: `WE-A-ENGINE-GATE05-R24-M04-PREP-20261011-DIRECT-bccd2404`  
**Role**: Antigravity A (Primary Engine Host Development Agent)  
**Authority & Disposition**: Master (`01a1156b-97ec-7ce0-9e4a-dfc4a3acb174`)  
**Independent Verifier Reference**: Sol QA (`01a11583-ff90-73e0-8916-d021e2bb038d`)  
**Status**: COMPLETED (Read-Only Preparation)  
**Final Technical Verdict**: `PREPARATION_COMPLETE_NATIVE_UNTESTED`  
**Execution Timestamp**: 2026-10-11 18:26:30 UTC+9  

---

## 1. Executive Summary & Administrative Context

Under Master instruction for **Work Package WP_ENGINE_GATE05_R24_ROLE_LAUNCH_CONTRACT_PREPARATION** (Envelope 27), this deliverable presents a formal, pure read-only architectural analysis and specification for milestone **M04: Role-Aware UserData Directory Routing and Validator Frontend Launch Contracts**.

### 1.1 Acceptance of Prior Baseline
- **R23 Milestone Accepted**: Independent QA verification by Sol QA (`QA_EngineHost_Gate05_R23_Identifier_Mapping_Independent_S1_20261011.md`) verified all 20 receipts and 16 snapshots (`PASS`), and Master accepted closure of the CLI and factory identifier trimming defects.
- **R24 Scope Constraints**:
  - **STRICT READ-ONLY PREPARATION**: Zero production source code edits, zero candidate builds, zero test runner builds or execution, zero native process launches, zero file installations or copies.
  - **ALL 9 Engine Files Fixed**: The 9 core candidate artifacts (source files, MSBuild project, Debug/Release DLLs, PDBs, and Assemblies distribution files) remain 100% frozen and byte-identical to `MASTER_R24_ALL9_FIXED_BASELINE.json`.
  - **Scope Demarcation**: M04 is strictly limited to role-aware UserData directory routing and frontend launch contracts. Future milestones M05 (task tuple/channel protocol), M06 (content-context live XML census), and M07 (control plane promotion) remain strictly unaddressed and uncommitted.

---

## 2. Defect Analysis & Baseline State (R23 Frozen Codebase)

A comprehensive source trace across [WorkerBridge.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs) (size 227,009 bytes, SHA-256 `2076E3A88B57A55CDDB5F25950ED26EB2310224A43A91C8917EEC6588CD5983F`) revealed critical gaps in how the Engine handles role-specific UserData paths and launches child validators.

### 2.1 The `SafeSaveDataFolderPath` Defect (Lines 443–445)
In the current R23 implementation:
```csharp
private static string SafeSaveDataFolderPath =>
    _activeStartupConfig != null && !string.IsNullOrEmpty(_activeStartupConfig.WorkerUserDataDirectory)
        ? _activeStartupConfig.WorkerUserDataDirectory
        : GenFilePaths.SaveDataFolderPath;
```
- **Analysis**: When an Engine instance runs with role `READ_ONLY` (a validator host instance), it queries `SafeSaveDataFolderPath` during operations like staging, task folder creation, and saves directory resolution.
- **Defect**: The current implementation unconditionally evaluates `_activeStartupConfig.WorkerUserDataDirectory`. As a result, an instance operating in the `READ_ONLY` role inadvertently writes tasks, stages saves, and resolves paths into the `WorkerUserDataDirectory` rather than `ValidatorUserDataDirectory`.
- **Impact**: Cross-contamination of simulation worker and read-only validator directories, violating the process-isolation and storage-isolation invariants mandated by ADR-006B.

### 2.2 The `Awake` Diagnostic Logging Gap (Line 580)
In `WorkerBridge.Awake()`:
```csharp
Log.Message($"[WorkerBridge] Awake initialized. WorkerUserDataDirectory: {_activeStartupConfig.WorkerUserDataDirectory}");
```
- **Defect**: Logging prints `WorkerUserDataDirectory` unconditionally, failing to indicate whether the instance is initialized under `READ_ONLY` or `SIMULATION`, obscuring diagnostic visibility into effective role routing.

### 2.3 The `HandleLaunchOperatorValidator` Launch Argument Defect (Lines 2264–2281)
In `WorkerBridge.HandleLaunchOperatorValidator()`:
```csharp
string arguments = string.IsNullOrWhiteSpace(baseArgs)
    ? $"--task-file \"{taskFile}\" --nonce \"{nonce}\""
    : $"{baseArgs} --task-file \"{taskFile}\" --nonce \"{nonce}\"";
```
- **Defect**: The launch argument builder assumes a standalone CLI frontend accepting `--task-file` and `--nonce`. However:
  1. For native RimWorld child instances running `WorkerBridgeMod`, RimWorld does not recognize `--task-file`. It requires `-savedatafolder="<path>"` to isolate UserData.
  2. If the child process is an isolated `WorkerBridgeMod` instance, it requires the 7 mandatory operator CLI flags (`-operatorconfig`, `-operatorrole`, `-operatorcapability`, `-operatortaskid`, `-operatorclaimnonce`, `-operatorworkeruserdata`, `-operatorvalidatoruserdata`) and a distinct `-bridgeport` to prevent socket collisions with the simulation host.

---

## 3. Role-Aware Directory Routing Matrix (M04 Architecture)

The formal routing matrix established in `ROUTE_MATRIX.json` specifies how each engine component must resolve UserData paths:

| Consumer Component | Source Lines | Active Role: `SIMULATION` | Active Role: `READ_ONLY` | Fallback Resolution |
| :--- | :--- | :--- | :--- | :--- |
| `SafeSaveDataFolderPath` | 443–445 | `_activeStartupConfig.WorkerUserDataDirectory` | `_activeStartupConfig.ValidatorUserDataDirectory` | `GenFilePaths.SaveDataFolderPath` |
| `Awake` Log Output | 580 | Log `WorkerUserDataDirectory` with `Role=SIMULATION` | Log `ValidatorUserDataDirectory` with `Role=READ_ONLY` | Log `GenFilePaths.SaveDataFolderPath` with `Role=UNCONFIGURED` |
| `HandleStageSave` | 1342–1347 | Isolated under `SafeSaveDataFolderPath/Saves` | Rejected (read-only instances cannot stage saves) | Fail-closed (`STAGING_DISABLED_FOR_ROLE`) |
| `HandleExecuteValidatorTask` | 1583–1610 | Fallback/compatibility task directory | Primary isolated validator directory | Fail-closed if path cannot be resolved |
| `HandleLaunchOperatorValidator` | 2264–2281 | Resolves child UserData to `ValidatorUserDataDirectory` | N/A (read-only instance cannot launch child validators) | Fail-closed if `ValidatorUserDataDirectory` empty |

---

## 4. Frontend Execution Contracts & Prerequisites

The execution contracts cataloged in `FRONTEND_PREREQUISITES.json` distinguish between two distinct execution topologies:

### 4.1 Mode A: Native RimWorld Child Worker (Engine Host)
- **Target Executable**: `RimWorldWin64.exe` (or `RimWorldWin.exe`).
- **Required Arguments**:
  1. `-savedatafolder="<ValidatorUserDataDirectory>"` (Native RimWorld command-line argument redirecting save, config, and log roots).
  2. `-operatorconfig="<PathToOperatorConfigJson>"` (Points to validated 14-field operator bootstrap configuration).
  3. `-operatorrole="READ_ONLY"` (Declares immutable read-only validator role).
  4. `-operatorcapability="<CapabilitySignature>"` (Cryptographic capability signature).
  5. `-operatortaskid="<TaskId>"` (Specific task identifier).
  6. `-operatorclaimnonce="<Nonce>"` (Task claim nonce).
  7. `-operatorworkeruserdata="<WorkerUserDataDirectory>"` (Worker directory reference).
  8. `-operatorvalidatoruserdata="<ValidatorUserDataDirectory>"` (Validator directory reference).
  9. `-bridgeport=<UniquePort>` (Explicit distinct loopback TCP port to avoid binding collision with the simulation host).
  10. `-batchmode -nographics` (Optional headless execution flags for automated validation).
- **Frontend Prerequisites**:
  - Validated child executable path in `_activeStartupConfig.OperatorValidatorExecutablePath`.
  - Child process must load `WorkerBridgeMod` from a shared or referenced mod directory.
  - Verification that the child process does not attempt to bind the same TCP bridge port as the parent worker.

### 4.2 Mode B: Standalone Validator CLI Frontend
- **Target Executable**: `WarEconomy.ValidatorCli.exe` (or equivalent external validation tool).
- **Required Arguments**:
  1. `--task-file "<PathToTaskJson>"` (Absolute path to sealed validator task file).
  2. `--nonce "<CapabilityNonce>"` (Single-use execution nonce).
  3. `--user-data-dir "<ValidatorUserDataDirectory>"` (Explicit UserData isolation path).
  4. `--role "READ_ONLY"` (Explicit role constraint).
- **Frontend Prerequisites**:
  - CLI binary must support JSON result serialization matching the schema expected by `HandleCompleteStageValidation`.
  - Result file must be written to `<taskDir>/<taskId>.result.json` with matching task ID and process PID.

---

## 5. Minimal Proposed Patch Contract

As detailed in `IMPLEMENTATION_CONTRACT.md`, the minimal patch contract modifies exactly three contiguous spans in `WorkerBridge.cs` without altering any public schemas or external contracts:

### Span A: `SafeSaveDataFolderPath` (Lines 443–445)
```csharp
<<<< CURRENT R23 >>>>
private static string SafeSaveDataFolderPath =>
    _activeStartupConfig != null && !string.IsNullOrEmpty(_activeStartupConfig.WorkerUserDataDirectory)
        ? _activeStartupConfig.WorkerUserDataDirectory
        : GenFilePaths.SaveDataFolderPath;

<<<< PROPOSED M04 >>>>
private static string SafeSaveDataFolderPath
{
    get
    {
        if (_activeStartupConfig == null)
            return GenFilePaths.SaveDataFolderPath;

        if (string.Equals(_activeStartupConfig.Role, "READ_ONLY", StringComparison.OrdinalIgnoreCase))
        {
            return !string.IsNullOrEmpty(_activeStartupConfig.ValidatorUserDataDirectory)
                ? _activeStartupConfig.ValidatorUserDataDirectory
                : GenFilePaths.SaveDataFolderPath;
        }

        return !string.IsNullOrEmpty(_activeStartupConfig.WorkerUserDataDirectory)
            ? _activeStartupConfig.WorkerUserDataDirectory
            : GenFilePaths.SaveDataFolderPath;
    }
}
```

### Span B: `Awake` Diagnostic Logging (Lines 579–581)
```csharp
<<<< CURRENT R23 >>>>
Log.Message($"[WorkerBridge] Awake initialized. WorkerUserDataDirectory: {_activeStartupConfig.WorkerUserDataDirectory}");

<<<< PROPOSED M04 >>>>
string effectiveUserData = SafeSaveDataFolderPath;
Log.Message($"[WorkerBridge] Awake initialized. Role: {_activeStartupConfig.Role}, EffectiveUserDataDirectory: {effectiveUserData}");
```

### Span C: `HandleLaunchOperatorValidator` Argument Construction (Lines 2264–2281)
```csharp
<<<< CURRENT R23 >>>>
string arguments = string.IsNullOrWhiteSpace(baseArgs)
    ? $"--task-file \"{taskFile}\" --nonce \"{nonce}\""
    : $"{baseArgs} --task-file \"{taskFile}\" --nonce \"{nonce}\"";

<<<< PROPOSED M04 >>>>
string validatorUserData = !string.IsNullOrEmpty(_activeStartupConfig?.ValidatorUserDataDirectory)
    ? _activeStartupConfig.ValidatorUserDataDirectory
    : SafeSaveDataFolderPath;

StringBuilder argsBuilder = new StringBuilder();
if (!string.IsNullOrWhiteSpace(baseArgs))
{
    argsBuilder.Append(baseArgs.Trim()).Append(" ");
}
argsBuilder.Append($"-savedatafolder=\"{validatorUserData}\" ");
argsBuilder.Append($"--task-file \"{taskFile}\" ");
argsBuilder.Append($"--nonce \"{nonce}\"");
string arguments = argsBuilder.ToString().Trim();
```

### Schema Backward-Compatibility Proof
- **Zero Schema Additions**: The 14-field `WE-OPERATOR-BOOTSTRAP-V1` configuration schema (`OperatorStartupConfig`) already declares both `workerUserDataDirectory` and `validatorUserDataDirectory`.
- **Public Snapshot & Receipt Invariance**: Public snapshot dictionaries (15 properties) and stage validation receipts (11 properties) remain 100% unchanged. No schema version increment is required.

---

## 6. Prospective M04 Normal Oracle Specification

As specified in `PROSPECTIVE_M04_NORMAL_ORACLE.json`, the prospective test suite for M04 requires 7 pure, deterministic test cases:

1. **TC-M04-01 (`ORACLE_ROLE_SIMULATION_DIR`)**: Config with `Role="SIMULATION"`, verifies `SafeSaveDataFolderPath == WorkerUserDataDirectory`.
2. **TC-M04-02 (`ORACLE_ROLE_READ_ONLY_DIR`)**: Config with `Role="READ_ONLY"`, verifies `SafeSaveDataFolderPath == ValidatorUserDataDirectory`.
3. **TC-M04-03 (`ORACLE_ROLE_CASE_INSENSITIVE`)**: Config with `Role="read_only"`, verifies case-insensitive match returns `ValidatorUserDataDirectory`.
4. **TC-M04-04 (`ORACLE_FALLBACK_MISSING_DIR`)**: Config with `Role="READ_ONLY"` but `ValidatorUserDataDirectory=null`, verifies fallback to `GenFilePaths.SaveDataFolderPath`.
5. **TC-M04-05 (`ORACLE_NULL_CONFIG_FALLBACK`)**: `_activeStartupConfig=null`, verifies fallback to `GenFilePaths.SaveDataFolderPath`.
6. **TC-M04-06 (`ORACLE_ARGV_QUOTED_UNICODE_SPACES`)**: Launch validator with spaces and Unicode in `ValidatorUserDataDirectory` (e.g. `C:\RimWorld Data\검증자_데이터`), verifies exact quoting `-savedatafolder="..."`.
7. **TC-M04-07 (`ORACLE_CALLER_IMMUTABILITY`)**: Verifies that resolving `SafeSaveDataFolderPath` does not mutate `_activeStartupConfig` properties or create unwanted directories on disk.

---

## 7. Explicit Scope Demarcation

As formally established in `ACTUAL_PREPARATION_SCOPE.json`:

| Scope Boundary | Included in Milestone M04 | Strictly Deferred / Excluded |
| :--- | :--- | :--- |
| **Directory Routing** | Role-based selection between `WorkerUserDataDirectory` and `ValidatorUserDataDirectory`. | Dynamic multi-tenant folder switching, cross-drive symlink resolution. |
| **Launch Contracts** | Argument formatting for `-savedatafolder`, `--task-file`, `--nonce`. | **M05**: Multi-task tuples, streaming channel protocols, heartbeat channels. |
| **Content Census** | Preservation of existing ADR-006B-v3 static census. | **M06**: Live XML def patching, dynamic def injection, in-memory mod reloads. |
| **Control Plane** | Maintenance of existing fail-closed authority checks. | **M07**: Autonomous cluster election, dynamic promotion, leader failover. |

---

## 8. Cryptographic Deliverable Manifest & Baseline Freeze Audit

### 8.1 Preparation Artifacts (`scratch\EngineGate05R24RoleLaunchPreparation\`)

| Artifact Name | Size (Bytes) | SHA-256 Checksum | Description |
| :--- | :--- | :--- | :--- |
| [ROUTE_MATRIX.json](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/ROUTE_MATRIX.json) | 5,689 | `7C918A1EA35C2AE9376A2A8C22F9970DD9C9E7E7B8D28B7803EA7FAF61B13D88` | Role-based UserData directory routing matrix |
| [FRONTEND_PREREQUISITES.json](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/FRONTEND_PREREQUISITES.json) | 6,787 | `D8CB969848CB40CCA6749CA38B0BB98CE5DD88873F5705F76EF4E2894975A319` | Native RimWorld & CLI frontend prerequisites |
| [IMPLEMENTATION_CONTRACT.md](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/IMPLEMENTATION_CONTRACT.md) | 7,106 | `299C8E36D1157D00F39B53BBEE884D205559A5E01E5B357BD76A64481551DAA9` | Source-anchored patch contract & byte ranges |
| [PROSPECTIVE_M04_NORMAL_ORACLE.json](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/PROSPECTIVE_M04_NORMAL_ORACLE.json) | 5,085 | `EC6FDE3E8C165330086CF96EDC63AC01B1F8DB66FBA50E2381F203F8E030866B` | Normal test cases and expected values |
| [ACTUAL_PREPARATION_SCOPE.json](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/ACTUAL_PREPARATION_SCOPE.json) | 2,160 | `786A267A5461972003E51F30BFF94CA760631469444E9B7DC9DC4C18FA1267DA` | Bounded scope demarcation (M04 vs M05..M07) |
| [RESULT_INDEX.json](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/RESULT_INDEX.json) | 2,924 | `671E2DBF9B912C890D227FCBD1693D183BD9BBBC7F39DBE7BC9FEB0AE75FA07E` | Machine-readable deliverable index |
| [EVIDENCE_MANIFEST.json](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/EVIDENCE_MANIFEST.json) | 2,805 | `2B6810B9EC4DF55E3C824DC837BF493064937876823505C9CFBD680468EC08AF` | Cryptographic evidence manifest |

### 8.2 Engine Candidate Baseline Freeze Verification (ALL 9 Identical)

| Path | Size (Bytes) | SHA-256 Checksum | Freeze Status |
| :--- | :--- | :--- | :--- |
| `scratch/WorkerBridgeMod/Source/WorkerBridge.cs` | 227,009 | `2076E3A88B57A55CDDB5F25950ED26EB2310224A43A91C8917EEC6588CD5983F` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/Source/EngineHostCensus.cs` | 170,135 | `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/Source/WorkerBridge.csproj` | 1,774 | `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll` | 303,104 | `4379BE35700337F797BB17F25D5BAC2A8014FAA9332D9878E587A12E5758A9C4` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb` | 72,628 | `2309CEC04514B58E23FC1885DDED87FAAF30F1BDEECA4CA48AD667C4DE2B18B4` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll` | 286,720 | `D46BD31D61B45950AFB8F9717CC4444C0C0C4CF6D1E12FB3E20AF99BCBE9FCBD` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb` | 53,096 | `4DCD674C11CF0BBA593C5EC13B826C58219387FB766EBA4CA88E8484C5719D50` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll` | 303,104 | `4379BE35700337F797BB17F25D5BAC2A8014FAA9332D9878E587A12E5758A9C4` | **UNMODIFIED** |
| `scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.pdb` | 72,628 | `2309CEC04514B58E23FC1885DDED87FAAF30F1BDEECA4CA48AD667C4DE2B18B4` | **UNMODIFIED** |

---

## 9. Conclusion & Recommendations

The preparation phase for milestone M04 is complete. The exact architectural requirements, defect locations, proposed code modifications, frontend execution prerequisites, and prospective normal test oracle have been fully documented without modifying any production code or candidate binaries.

Master is advised to:
1. Review and approve the implementation contract specified in [IMPLEMENTATION_CONTRACT.md](file:///c:/Users/user/Desktop/RimMulti/scratch/EngineGate05R24RoleLaunchPreparation/IMPLEMENTATION_CONTRACT.md).
2. Authorize the subsequent work package for implementation and pure unit test execution of Spans A, B, and C.
3. Maintain the Foundation HOLD invariant until full multi-process validator execution is independently verified by Sol QA.
