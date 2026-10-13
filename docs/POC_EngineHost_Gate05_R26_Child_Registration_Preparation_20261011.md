# PoC EngineHost Gate05 R26: Child Registration & Launch Plan Preparation Report

- **Date / Time**: `2026-10-11T23:52:00+09:00`
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R26-CHILD-REG-PREP-20261011-DIRECT-4d660e9b`
- **Work Package Revision**: `GATE05-R26-CHILD-REG-PREP` (Envelope 29)
- **Task Verdict**: `READ_ONLY_PREPARATION_NO_EXECUTION`
- **Execution & Mutation Count**: Zero (0) candidate builds, zero (0) test runner executions, zero (0) native process starts, zero (0) assets copied/installed.
- **Production Code Status**: ALL nine (9) Engine candidate files remain 100% frozen and byte-identical to `MASTER_R26_READ_ONLY_SCOPE.json`.

---

## 1. Executive Summary & Purpose

The R26 work package represents a strictly bounded, read-only architectural preparation addressing the missing link between parent simulation workers and child validator processes within Gate05 (M04).

Following the successful acceptance of R25's pure role-based UserData selector (`OperatorRolePathSelector.SelectUserData`) and the scoped closure of the QA prospective newline defect, the next critical architectural prerequisite is establishing a **private, operator-owned registration carrier** for a separate `READ_ONLY` child configuration receipt, enabling the construction of a closed, data-only launch plan.

### Core Deliverables Provided:
1. `IMPLEMENTATION_CONTRACT.md`: Comprehensive lifecycle contract covering Creation, Validation, Private Capture, Selection, and Launch Consumer phases.
2. `CURRENT_FACT_PROPOSAL_MATRIX.json`: Rigorous separation of current source facts, proposed typed mechanisms, and unresolved native prerequisites.
3. `PROPOSED_MINIMUM_PATCH_SPANS.json`: Exact byte offsets, line numbers, context SHA-256 hashes, and minimal code spans in `WorkerBridge.cs`.
4. `PROSPECTIVE_NORMAL_ORACLE.json`: Seven (7) pure unit test specifications with concrete fixtures and expected token vectors.
5. `FRONTEND_PREREQUISITES.json`: Inventory of six (6) blocking external and native prerequisites before physical execution can occur.
6. `ENGINE_FREEZE_BEFORE.json` & `ENGINE_FREEZE_AFTER.json`: Verified cryptographic hashes proving zero mutations across all 9 production files.

---

## 2. Problem Statement: The Child Configuration Carrier Gap

### 2.1 Current Source Architecture
In `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`:
- A single static slot exists for operator startup configuration:
  - `_activeAdmissionReceipt` (line 414)
  - `_activeStartupConfig` (line 415)
  - `_operatorConfigSealed` (line 416)
- Once `TryInstallOperatorStartupConfig(receipt)` executes (lines 422–436), `_operatorConfigSealed` becomes `true`. Subsequent calls return `false`.
- In a simulation host process, `receipt.Snapshot.Role == "SIMULATION"`.
- When `HandleLaunchOperatorValidator` executes (lines 2237–2281), it derives its executable path, arguments, and working directory directly from `_activeStartupConfig`.
- It currently formats launch arguments as:
  ```csharp
  string childArgs = $"--task-file \"{currentValidatorTaskPath}\" --nonce \"{currentValidatorTask.capabilityNonce}\"";
  if (!string.IsNullOrWhiteSpace(baseArgs))
  {
      childArgs = $"{baseArgs} {childArgs}";
  }
  ```

### 2.2 Defects of the Current Launch Seam
1. **Missing Child Identity & Configuration**: The child process is not provided with an operator startup config JSON, its own `configId`, or its `READ_ONLY` role.
2. **Missing UserData Isolation**: The child process is not launched with `-savedatafolder` pointing to `ValidatorUserDataDirectory`.
3. **Missing Operator Startup Keys**: None of the 7 mandatory operator startup tokens (`-operatorconfig`, `-operatorconfigsha`, `-operatororigin`, `-operatorlaunchplan`, `-operatorconfigid`, `-operatorrole`, `-operatorcapability`) are passed to the child process.

### 2.3 Strict Rejection of Prohibited Shortcuts
Per Master instructions, the following anti-patterns are strictly rejected:
- **No Mutation of Parent Snapshot**: Do not derive a child by mutating `_activeStartupConfig.Role` to `"READ_ONLY"`. The snapshot is immutable, and mutating it would break the raw config byte SHA-256 binding (`BoundConfigSha256`).
- **No Arbitrary ID Generation**: Do not fabricate `originId`, `launchPlanId`, or `configId`, and do not mint capability nonces in the Engine host or from public requester DTOs. Only the Operator is the authoritative issuer (MD125..132, SRS).
- **No Global Receipt Swap**: Do not reuse `TryInstallOperatorStartupConfig` to swap the process's own identity. A process has exactly one active identity.

---

## 3. Fact vs. Proposal vs. Prerequisites Matrix

| Category | Item ID | Location / Source Anchor | Description & Technical Significance |
| :--- | :--- | :--- | :--- |
| **FACT** | `FACT-01` | `WorkerBridge.cs:413-436`<br>(Bytes 14401–15598) | Single static slot `_activeAdmissionReceipt` sealed via `_operatorConfigSealed`. No slot exists for child receipts. |
| **FACT** | `FACT-02` | `WorkerBridge.cs:2237-2281`<br>(Bytes 101495–103837) | `HandleLaunchOperatorValidator` derives launch info directly from parent `SIMULATION` config and passes only `--task-file`/`--nonce`. |
| **FACT** | `FACT-03` | `WorkerBridge.cs:3454-3475` | `OperatorRolePathSelector.SelectUserData` strictly isolates `SIMULATION` (`WorkerUserDataDirectory`) vs `READ_ONLY` (`ValidatorUserDataDirectory`). |
| **FACT** | `FACT-04` | `WorkerBridge.cs:3738-4360` | Existing admission factory enforces raw byte SHA-256 preflight checks and creates immutable receipts. |
| **FACT** | `FACT-05` | `HostUtil.cs:218-226`<br>(Bytes 8746–9279) | Checked-in Multiplayer code shows reference usage of `-savedatafolder`. It is reference usage only, not proof of base-game runtime support. |
| **PROPOSAL**| `PROP-01` | Proposed Span 1 (`WorkerBridge.cs`) | Private slot `_activeChildValidatorReceipt` with `TryRegisterChildValidatorReceipt` and `RevokeChildValidatorReceipt`. |
| **PROPOSAL**| `PROP-02` | Proposed Span 3 (`WorkerBridge.cs`) | Pure DTO `ChildValidatorLaunchPlan` and static pure builder `ChildValidatorLaunchPlanBuilder.BuildLaunchPlan`. |
| **PROPOSAL**| `PROP-03` | Parameter Vector Contract | Formatting child arguments with 7 mandatory operator keys + `-savedatafolder` + task parameters. |
| **PROPOSAL**| `PROP-04` | Single-Use Lifetime | Consumption upon `Process.Start` and explicit revocation upon task termination. |
| **PREREQ** | `PREREQ-01`| Operator Authority | External operator orchestration service must issue a separate `READ_ONLY` config JSON and descriptor. |
| **PREREQ** | `PREREQ-02`| Native Bootstrap | Empirical proof that RimWorld executable (Verse/Unity) accepts `-savedatafolder` without regression. |
| **PREREQ** | `PREREQ-03`| Filesystem Isolation | Physical provisioning of distinct `ValidatorUserDataDirectory` and `ValidatorCwd`. |
| **PREREQ** | `PREREQ-04`| Data Access | Safe read-only access to parent staged save game artifact without file locking conflicts. |
| **PREREQ** | `PREREQ-05`| Network (M05) | Allocation of independent loopback TCP port and mutual nonce authentication. |
| **PREREQ** | `PREREQ-06`| Game Environment | Full RimWorld game assemblies and content assets installed in runtime environment. |

---

## 4. Minimum Source Patch Spans (Detailed)

Three precise spans have been identified in `WorkerBridge.cs`:

### Span 1: Private Child Storage & Registration API
- **File**: `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`
- **Lines**: 413–436 (Byte range: 14401 to 15598, Length: 1197 bytes)
- **Context SHA-256**: `B153800FB5FFADE8C8A95D1B8F263EB970FC97BB94BFA2ADDA14151F68F5C473`
- **Action**: Add `private static OperatorStartupAdmissionReceipt? _activeChildValidatorReceipt = null;`, `TryRegisterChildValidatorReceipt(...)`, and `RevokeChildValidatorReceipt()`.
- **Invariants Enforced**:
  - `childReceipt.Snapshot.Role == "READ_ONLY"` (Ordinal comparison).
  - Executable path and SHA-256 match `_activeStartupConfig`.
  - Content profile fingerprint matches `_activeStartupConfig`.
  - Rejects overwrite if a child receipt is already active.

### Span 2: Launch Consumer Integration
- **File**: `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`
- **Lines**: 2237–2281 (Byte range: 101495 to 103837, Length: 2342 bytes)
- **Context SHA-256**: `1EF1BAC86DBC663557B882E41419CDA150754D00F44C9C3B26A377120216DD54`
- **Action**: In `HandleLaunchOperatorValidator`, replace direct parent config derivation with:
  - Fail-closed check for `_activeChildValidatorReceipt`.
  - Call to `ChildValidatorLaunchPlanBuilder.BuildLaunchPlan(...)`.
  - Argument construction from `plan.FormattedArgumentTokens`.
  - Working directory bound to `plan.WorkingDirectory`.

### Span 3: Pure Launch Plan Builder DTO & Class
- **File**: `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`
- **Lines**: 3474–3477 (Byte range: 166893 to 166988, Length: 95 bytes)
- **Context SHA-256**: `58987D3D2EC5940247F84F6E74C553CE91654089B53CDA54C1E04A50ADEC0384`
- **Action**: Add `ChildValidatorLaunchPlan` and `ChildValidatorLaunchPlanBuilder` definitions adjacent to `OperatorRolePathSelector`.

---

## 5. Prospective Normal Unit Oracle Specification

Seven (7) pure unit tests are defined in `PROSPECTIVE_NORMAL_ORACLE.json`:
1. `TC01_REGISTER_VALID_READ_ONLY_CHILD_SUCCESS`: Successfully registers an admitted `READ_ONLY` child receipt matching parent executable and profile.
2. `TC02_REJECT_SIMULATION_ROLE_AS_CHILD`: Strictly rejects registration of a receipt with `Role == "SIMULATION"`.
3. `TC03_REJECT_EXECUTABLE_SHA_MISMATCH`: Rejects child receipt if executable SHA-256 differs from parent worker config.
4. `TC04_REJECT_CONTENT_PROFILE_MISMATCH`: Rejects child receipt if content profile fingerprint differs from parent worker config.
5. `TC05_REJECT_OVERWRITE_WHILE_ACTIVE`: Rejects second child registration while first is active (enforces single-active).
6. `TC06_REVOKE_CLEARS_ACTIVE_CHILD`: Verifies `RevokeChildValidatorReceipt()` clears the active slot to null, allowing re-registration.
7. `TC07_LAUNCH_PLAN_BUILDER_TOKEN_VECTOR`: Verifies builder produces exact token vector containing the 7 mandatory startup keys, reference `-savedatafolder`, and task parameters.

---

## 6. Freeze Manifest & Baseline Integrity

All nine (9) production Engine candidate files were verified before and after preparation. Zero bytes were modified:

| Production File | Size (Bytes) | SHA-256 Digest | Status |
| :--- | :--- | :--- | :--- |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` | 227,637 | `AB5AD60F16A62FC4473712ABF03AF10A3BB22A66DD8E283F0EC241857BD25BD2` | FROZEN |
| `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` | 170,135 | `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` | FROZEN |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` | 1,774 | `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` | FROZEN |
| `scratch\...\bin\Debug\...\WarEconomy.WorkerBridge.PoC.dll` | 303,616 | `A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7` | FROZEN |
| `scratch\...\bin\Debug\...\WarEconomy.WorkerBridge.PoC.pdb` | 72,740 | `1B13F39A917F7C96EE736C1470B6F385B0534CFABF2174E4B86191950DB2458D` | FROZEN |
| `scratch\...\bin\Release\...\WarEconomy.WorkerBridge.PoC.dll`| 287,232 | `10C01657CF148AD0BE8B6B70A5466F4739D64397922BD78088B1431983BBBC72` | FROZEN |
| `scratch\...\bin\Release\...\WarEconomy.WorkerBridge.PoC.pdb`| 53,152 | `57E80AB13FA1819564F2DAAA2CEF86054CCDFADE354C50FE0AB69B2F0E06159C` | FROZEN |
| `scratch\...\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` | 303,616 | `A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7` | FROZEN |
| `scratch\...\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb` | 72,740 | `1B13F39A917F7C96EE736C1470B6F385B0534CFABF2174E4B86191950DB2458D` | FROZEN |

---

## 7. Governance & Next Steps

1. **Gate Status**:
   - Engine002006 / Pipeline007 / current schema / G-Q1 remain **OPEN**.
   - Foundation **HOLD** remains in effect until independent Pipeline E2 PASS.
   - Native runtime execution remains **NOT RELEASED**.
2. **Next Milestone Action**:
   - Master reconciles independent proposals from A and Sol.
   - Upon Master approval, subsequent bounded work package will implement Span 1, Span 2, Span 3 and execute pure normal unit test suite (TC01..TC07) under independent QA.
