# POC_EngineHost_Semantic_Authority_Gate_05_R25.md
**Work Package**: `WP_ENGINE_GATE05_R25_ROLE_USERDATA_SELECTION`  
**Revision**: `GATE05-R25-ROLE-USERDATA`  
**Envelope**: `envelope28`  
**Dispatch ID**: `WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868`  
**Role**: Antigravity A (Primary Engine Host Development Agent)  
**Authority & Disposition**: Master (`01a1156b-97ec-7ce0-9e4a-dfc4a3acb174`)  
**Independent Verifier Reference**: Sol QA (`01a11583-ff90-73e0-8916-d021e2bb038d`)  
**Status**: COMPLETED  
**Final Technical Verdict**: `E1 PASS (PURE DATA-ONLY OPERATOR ROLE USERDATA SELECTOR & ACTIVE SAFE GETTER CONNECTED, NATIVE UNTESTED)`  
**Execution Timestamp**: 2026-10-11 21:41:00 UTC+9  

---

## 1. Executive Summary

Under Master instructions for **Work Package WP_ENGINE_GATE05_R25_ROLE_USERDATA_SELECTION** (Envelope 28), this deliverable establishes the technical implementation, candidate compilation, and pure developer E1 verification of the bounded milestone **M04: Role-Aware UserData Directory Selection and Safe Getter Connection**.

### 1.1 Master R24 Corrections Acknowledged & Adopted
Per Master controlling review (`MASTER_REVIEW_ENGINE_GATE05_R24_DUAL_M04_PREPARATION_20261011.md`, SHA `BE20FB28...`), all non-adopted R24 proposals were strictly rejected and excluded:
1. **Zero Invented CLI Flags**: The mandatory 7 bootstrap CLI flags (`operatorconfig`, `operatorconfigsha`, `operatororigin`, `operatorlaunchplan`, `operatorconfigid`, `operatorrole`, `operatorcapability`) are strictly preserved. A's draft proposals (`operatortaskid`, `operatorclaimnonce`, `operatorworkeruserdata`, `operatorvalidatoruserdata`) were not added.
2. **Zero Cryptographic Capability Signature Inventions**: Maintained ADR-006B / MD126 unguessable nonce model without adding unadmitted cryptographic signatures.
3. **No Unobserved Cross-Contamination Overclaims**: Distinguished source selection defect from native `GenFilePaths` root.
4. **Span C Launcher Modifications Rejected**: `HandleLaunchOperatorValidator`, launch plans, working directories, ProcessStartInfo, and child process registration remain 100% **BYTE FIXED**.
5. **No Null / Fallback / Adverse Oracles**: Null config / missing directory fallback tests were zeroed; verification is strictly positive pure normal.
6. **Canonical Config Uppercase Only**: Config role canonical comparison is uppercase ordinal (`"SIMULATION"` vs `"READ_ONLY"`).

### 1.2 Implementation Summary (3 Spans, 4 Fixed Segments)
1. **P1 (Pure Helper Insertion - Span 3, byte 166282)**:
   - Inserted `public static class OperatorRolePathSelector` immediately before `#region Gate05-R18`.
   - Single public pure method `SelectUserData(OperatorStartupConfigSnapshot snapshot)`:
     - `snapshot.Role == "SIMULATION"` -> returns `snapshot.WorkerUserDataDirectory`.
     - `snapshot.Role == "READ_ONLY"` -> returns `snapshot.ValidatorUserDataDirectory`.
     - Canonical ordinal string comparisons (`StringComparison.Ordinal`).
     - Null snapshot / unknown role fail-closed with explicit exceptions (never default to Worker or Gen root).
     - Zero fields, state, IO, `Directory.Create`, `Path.GetFullPath`, `Verse`, `Process`, or caller DTO mutations.
2. **P2 Safe Getter Connection (Span 1, bytes 15691..16046)**:
   - Replaced active admitted config branch in [SafeSaveDataFolderPath](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs#L438-L460) with:
     ```csharp
     if (_activeStartupConfig != null)
     {
         return OperatorRolePathSelector.SelectUserData(_activeStartupConfig);
     }
     ```
   - Inactive `CustomSaveDataPathOverride` and `GenFilePaths` fallback outside span remain 100% byte-fixed.
3. **P2 Awake Diagnostic Logging (Span 2, bytes 22390..22654)**:
   - Updated config-applied log line in `Awake` to display `DeclaredRoleUserData`:
     ```csharp
     Log.Message($"[WorkerBridge] Operator startup config applied in Awake: ConfigId='{_activeAdmissionReceipt.Snapshot.ConfigId}', Role='{_activeAdmissionReceipt.Snapshot.Role}', DeclaredRoleUserData='{OperatorRolePathSelector.SelectUserData(_activeAdmissionReceipt.Snapshot)}'");
     ```
4. **4 Fixed Binary Segments Fidelity**:
   - Spliced across the 3 authorized spans; all 4 fixed segments (`WORKER_FIXED_SEGMENT_0..3.bin`) verified to match Master baseline SHA-256 digests byte-for-byte.
   - [EngineHostCensus.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs) (170,135 B, SHA `391F9645...`) and [WorkerBridge.csproj](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.csproj) (1,774 B, SHA `571A58F5...`) remain 100% immutable.

---

## 2. Cryptographic Provenance & Lineage Baseline

All deliverable artifacts are strictly bound by cryptographic SHA-256 digests and PE metadata:

| Artifact Category | File Path | Size (Bytes) | SHA-256 Checksum | Metadata / Lineage Identity |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate DLL (Debug)** | `scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll` | 303,616 | `A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7` | Target: net472, Config: Debug, MVID: `5553a632-0557-433f-8840-bb12875cf577`, CodeView GUID: `fc75dba4-e23e-4d20-99be-1a5add6d36c4` |
| **Candidate PDB (Debug)** | `scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb` | 72,740 | `1B13F39A917F7C96EE736C1470B6F385B0534CFABF2174E4B86191950DB2458D` | Matching Debug Lineage PDB |
| **Release DLL** | `scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll` | 287,232 | `10C01657CF148AD0BE8B6B70A5466F4739D64397922BD78088B1431983BBBC72` | Target: net472, Config: Release, MVID: `da8efff8-3b44-48c1-a3bb-fd61f5d18795`, CodeView GUID: `75219ae2-fe8b-41fb-8a95-19f3abd568dd` |
| **Release PDB** | `scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb` | 53,152 | `57E80AB13FA1819564F2DAAA2CEF86054CCDFADE354C50FE0AB69B2F0E06159C` | Matching Release Lineage PDB |
| **Assemblies DLL** | `scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll` | 303,616 | `A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7` | Synchronized Debug Distribution DLL |
| **Assemblies PDB** | `scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.pdb` | 72,740 | `1B13F39A917F7C96EE736C1470B6F385B0534CFABF2174E4B86191950DB2458D` | Synchronized Debug Distribution PDB |
| **WorkerBridge Source** | `scratch/WorkerBridgeMod/Source/WorkerBridge.cs` | 227,637 | `AB5AD60F16A62FC4473712ABF03AF10A3BB22A66DD8E283F0EC241857BD25BD2` | R25 Bounded Spliced Implementation |
| **Census Source** | `scratch/WorkerBridgeMod/Source/EngineHostCensus.cs` | 170,135 | `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` | Fixed ADR-006B-v5 Deep Census Engine |
| **Project File** | `scratch/WorkerBridgeMod/Source/WorkerBridge.csproj` | 1,774 | `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` | Fixed MSBuild Project Specification |

---

## 3. Developer E1 Verification & Test Battery Results

### 3.1 Normal 4-Case Specification
The E1 test suite (`Gate05R25RoleUserDataRunner`) executes exactly 4 fully specified cases:
1. **Case 1 (`CFG-SIMULATION-PLAIN`)**: `Role="SIMULATION"`, `Policy="PLAIN"`. Expected selected root: `WorkerUserDataDirectory` (`C:\WarEconomy\Data R25\작업자 01\UserData`).
2. **Case 2 (`CFG-SIMULATION-OPAQUE`)**: `Role="SIMULATION"`, `Policy="OPAQUE"`. Expected selected root: `WorkerUserDataDirectory` (`C:\WarEconomy\Data R25\작업자 02 Ω\UserData`). Verified opaque policy digest matches `8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`.
3. **Case 3 (`CFG-READ_ONLY-PLAIN`)**: `Role="READ_ONLY"`, `Policy="PLAIN"`. Expected selected root: `ValidatorUserDataDirectory` (`C:\WarEconomy\Data R25\검증자 03\UserData`).
4. **Case 4 (`CFG-READ_ONLY-OPAQUE`)**: `Role="READ_ONLY"`, `Policy="OPAQUE"`. Expected selected root: `ValidatorUserDataDirectory` (`C:\WarEconomy\Data R25\검증자 04 Ω\UserData`). Verified opaque policy digest matches `8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`.

### 3.2 Immutability & Caller Mutation Invariants
In each case:
- `OperatorStartupConfigSnapshot` constructed via `config.ToSnapshot()` (`s_toSnapshotCalls++`, total 4).
- `OperatorRolePathSelector.SelectUserData(snapshot)` called BEFORE caller edit (`s_selectUserDataCalls++`).
- Caller `config` fields deliberately mutated (`role`, `workerUserDataDirectory`, `validatorUserDataDirectory`, `workerCwd`, `validatorCwd`, `configId`, `expectedPackagePolicyDeclaration`).
- `OperatorRolePathSelector.SelectUserData(snapshot)` called AFTER caller edit (`s_selectUserDataCalls++`).
- Verified returned string identical before and after caller edit, matching independent pinned literal root.
- Verified all 15 public snapshot properties and 13 redacted properties remain completely unmutated.

### 3.3 Host Subprocess Telemetry
- **Run 1 (`en-US`)**: Child PID `10408`, Exit Code `0`, Duration `0.154s`, 11 artifacts generated and sealed.
- **Run 2 (`de-DE`)**: Child PID `34440`, Exit Code `0`, Duration `0.072s`, 11 artifacts generated and sealed.
- **Cross-Run Isolation**: Run 1 artifacts verified 100% byte-identical post-Run 2. Runner binary verified 100% immutable.

---

## 4. Bounded Scope & Governance Invariants

- **PROHIBITED CALLS ZEROED**:
  - `s_toSnapshotCalls = 4` (expected 4).
  - `s_selectUserDataCalls = 8` (expected 8).
  - C# `Process`, `GetCurrentProcess`, `VerifyProcessIdentity` execution: `0`.
  - Global `WorkerBridgeComponent` constructor, `ActiveStartupConfig` global set, `SafeSaveDataFolderPath` global get, `Awake`, `Bootstrapper`, `Harmony`, listener: `0`.
  - Negative/rejection/fallback probes: `0`.
- **FUTURE MILESTONES STRICTLY DEFERRED**:
  - M05 (task tuple / channel protocol binding), M06 (live content context XML census), and M07 (control plane stale capability revocation) remain strictly unaddressed.
- **FINAL DOMAIN AUTHORITY**: Dedicated Server remains final Domain Authority.
- **FOUNDATION STATUS**: Foundation remains **HOLD** pending Pipeline independent E2 PASS.
