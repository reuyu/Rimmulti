# Implementation Contract: Operator-Owned READ_ONLY Child Declaration & Private Registration Carrier

- **Task Dispatch ID**: `WE-A-ENGINE-GATE05-R26-CHILD-REG-PREP-20261011-DIRECT-4d660e9b`
- **Revision**: `GATE05-R26-CHILD-REG-PREP` (Envelope 29)
- **Status**: `READ_ONLY_PREPARATION_NO_EXECUTION`
- **Execution / Build**: Zero (0) candidate builds, zero (0) test runner executions, zero (0) native process starts, zero (0) assets copied/installed.
- **Production Code Status**: ALL nine (9) Engine candidate files remain 100% frozen and byte-identical to `MASTER_R26_READ_ONLY_SCOPE.json`.

---

## 1. Architectural Scope & Problem Statement

### 1.1 Context & Current Baseline
In the current Engine baseline (`scratch\WorkerBridgeMod\Source\WorkerBridge.cs`):
- A simulation worker process admits and seals its own operator startup configuration via `TryInstallOperatorStartupConfig(receipt)` (lines 422–436).
- This installation sets `_activeAdmissionReceipt` and `_activeStartupConfig`, with `_operatorConfigSealed = true`. In a simulation host, `receipt.Snapshot.Role == "SIMULATION"`.
- When `HandleLaunchOperatorValidator` executes (lines 2230–2295), it derives executable path, SHA-256, arguments, and working directory directly from `_activeStartupConfig` (the parent `SIMULATION` worker config).
- It only passes legacy task parameters: `childArgs = $"--task-file \"{currentValidatorTaskPath}\" --nonce \"{currentValidatorTask.capabilityNonce}\"";` (lines 2264–2268).

### 1.2 The Missing Carrier Gap
1. **No Child Configuration Slot**: There is currently no slot in `WorkerBridge` to store or register a separate `READ_ONLY` operator configuration issued for the child validator process.
2. **Forbidden Shortcuts**:
   - Mutating the parent's `_activeStartupConfig.Role` to `"READ_ONLY"` is strictly prohibited: `OperatorStartupConfigSnapshot` is deeply immutable, and mutating it would invalidate the raw config byte SHA-256 binding (`BoundConfigSha256`).
   - Inventing child IDs (`originId`, `launchPlanId`, `configId`) or minting capability nonces in the Engine host or public requester is prohibited: only the Operator is the authoritative issuer (MD125..132, SRS).
   - Global receipt replacement (`TryInstallOperatorStartupConfig`) is rejected once sealed (`_operatorConfigSealed == true`), preventing a single process from swapping its own identity.
3. **The Architectural Requirement**:
   The parent process requires a **private, operator-owned registration carrier** for a separate, independently admitted `READ_ONLY` child configuration receipt (`OperatorStartupAdmissionReceipt`), from which a closed, data-only launch plan can be projected.

---

## 2. End-to-End Lifecycle: Creation -> Validation -> Private Capture -> Selection -> Launch Consumer

```
[Operator Authority]
      |
      | 1. Issues separate child config JSON (role="READ_ONLY") & launch descriptor
      v
[OperatorStartupConfigAdmissionFactory]
      |
      | 2. Validates raw byte SHA-256, schema 14, descriptor 7, creates immutable Receipt (schema 11)
      v
[WorkerBridge Private Child Carrier]
      |
      | 3. TryRegisterChildValidatorReceipt(childReceipt)
      |    - Verifies childReceipt.Snapshot.Role == "READ_ONLY"
      |    - Verifies executable path & SHA-256 match parent SIMULATION config
      |    - Verifies content profile fingerprint & policy record match parent
      |    - Stores in private static field _activeChildValidatorReceipt under lock
      v
[ChildValidatorLaunchPlanBuilder]
      |
      | 4. Combines:
      |    - Parent admitted SIMULATION receipt
      |    - Registered child READ_ONLY receipt
      |    - Currently owned, sealed validator task (27 fields)
      |    Produces immutable ChildValidatorLaunchPlan DTO
      v
[HandleLaunchOperatorValidator]
      |
      | 5. Consumes ChildValidatorLaunchPlan:
      |    - Emits exact 7 mandatory startup keys:
      |      -operatorconfig, -operatorconfigsha, -operatororigin,
      |      -operatorlaunchplan, -operatorconfigid, -operatorrole="READ_ONLY",
      |      -operatorcapability
      |    - Emits reference-only:
      |      -savedatafolder="<childReceipt.Snapshot.ValidatorUserDataDirectory>"
      |    - Emits task parameters:
      |      --task-file="<currentValidatorTaskPath>" --nonce="<task.capabilityNonce>"
      v
[Process.Start(psi)]
      |
      | 6. Single-use consumption or explicit RevokeChildValidatorReceipt()
```

### 2.1 Creation Phase (Operator Authority)
- The Operator prepares a separate `OperatorStartupConfig` JSON file specifically for the child validator.
- Key properties:
  - `role`: Must be `"READ_ONLY"` (strict uppercase canonical).
  - `configId`: Unique operator-generated identifier for the child configuration.
  - `admittedValidatorExecutablePath`: Must match the parent's admitted executable.
  - `admittedValidatorExecutableSha256`: Must match the parent's admitted executable SHA-256.
  - `validatorUserDataDirectory`: Distinct isolated directory for validator data.
  - `validatorCwd`: Distinct isolated working directory for validator.
  - `expectedContentProfileFingerprint`: Matching the simulation worker's profile.
  - `expectedPackagePolicyDeclaration`: Matching the simulation worker's policy declaration.
  - `issuedAtUtc`: Canonical ISO 8601 UTC timestamp.

### 2.2 Validation & Admission Phase
- The child configuration is admitted via the existing, audited `OperatorStartupConfigAdmissionFactory.IssueAdmissionReceiptFromBytes` or `IssueAdmissionReceipt`.
- Produces a valid, trusted `OperatorStartupAdmissionReceipt`:
  - `ReceiptSchemaVersion`: `"WE-OPERATOR-RECEIPT-V1"`
  - `IsTrusted`: `true`
  - `BoundRole`: `"READ_ONLY"`
  - `BoundConfigSha256`: 64-character hex digest of the raw child configuration bytes.

### 2.3 Private Capture Phase (`TryRegisterChildValidatorReceipt`)
- A minimal, private/internal registration API on `WorkerBridge`:
  ```csharp
  internal static bool TryRegisterChildValidatorReceipt(OperatorStartupAdmissionReceipt childReceipt)
  ```
- **Registration Rules**:
  1. **Non-Null & Valid**: `childReceipt != null && childReceipt.IsValid()`.
  2. **Role Invariant**: `string.Equals(childReceipt.Snapshot.Role, "READ_ONLY", StringComparison.Ordinal)`.
     - Reject if `childReceipt.Snapshot.Role == "SIMULATION"`.
     - Reject if `childReceipt.Snapshot.Role` is null, empty, or unknown.
  3. **Parent Context Invariant**: Parent worker config (`_activeStartupConfig`) must be active and sealed.
  4. **Executable Consistency**:
     - `string.Equals(childReceipt.Snapshot.AdmittedValidatorExecutablePath, _activeStartupConfig.AdmittedValidatorExecutablePath, StringComparison.OrdinalIgnoreCase)`
     - `string.Equals(childReceipt.Snapshot.AdmittedValidatorExecutableSha256, _activeStartupConfig.AdmittedValidatorExecutableSha256, StringComparison.OrdinalIgnoreCase)`
  5. **Policy & Content Profile Consistency**:
     - `string.Equals(childReceipt.Snapshot.ExpectedContentProfileFingerprint, _activeStartupConfig.ExpectedContentProfileFingerprint, StringComparison.Ordinal)`
     - Package policy digest/revision must match parent.
  6. **Storage**: Stored in `private static OperatorStartupAdmissionReceipt? _activeChildValidatorReceipt` under `_configLock`.
  7. **Concurrency & Overwrite**: Single-active registration. If a child receipt is already registered and not consumed/revoked, subsequent registration attempts return `false` unless explicitly revoked.

### 2.4 Selection & Closed Launch Plan Construction
- An immutable DTO represents the closed launch plan:
  ```csharp
  public sealed class ChildValidatorLaunchPlan
  {
      public string ExecutablePath { get; }
      public string ExecutableExpectedSha256 { get; }
      public string WorkingDirectory { get; }
      public string SelectedUserDataDirectory { get; }
      public string BoundConfigPath { get; }
      public string BoundConfigSha256 { get; }
      public string BoundOriginId { get; }
      public string BoundLaunchPlanId { get; }
      public string BoundConfigId { get; }
      public string BoundRole { get; } // Always "READ_ONLY"
      public string BoundCapabilityBoundary { get; }
      public string TaskFilePath { get; }
      public string TaskCapabilityNonce { get; }
      public IReadOnlyList<string> FormattedArgumentTokens { get; }
  }
  ```
- A pure builder projects the plan without mutating any static state or executing processes:
  ```csharp
  public static class ChildValidatorLaunchPlanBuilder
  {
      public static (bool isValid, string error, ChildValidatorLaunchPlan? plan) BuildLaunchPlan(
          OperatorStartupAdmissionReceipt parentReceipt,
          OperatorStartupAdmissionReceipt childReceipt,
          ValidatorTask currentTask,
          string taskFilePath)
  }
  ```

### 2.5 Launch Consumer Phase (`HandleLaunchOperatorValidator`)
- In `HandleLaunchOperatorValidator`:
  1. Retrieve `_activeChildValidatorReceipt`. If null, fail-closed (`RevokeReadiness("No admitted child validator startup configuration registered.")`).
  2. Build `ChildValidatorLaunchPlan` from parent `_activeAdmissionReceipt`, `_activeChildValidatorReceipt`, `currentValidatorTask`, and `currentValidatorTaskPath`.
  3. Preflight check executable using `ExecutableAdmissionHelper.VerifyAdmittedExecutable(plan.ExecutablePath, plan.ExecutableExpectedSha256)`.
  4. Construct `ProcessStartInfo` with:
     - `FileName = plan.ExecutablePath`
     - `Arguments = string.Join(" ", plan.FormattedArgumentTokens)`
     - `WorkingDirectory = plan.WorkingDirectory`
  5. Execute `Process.Start(psi)`.
  6. On successful start, consume/revoke the registration (`_activeChildValidatorReceipt = null`) to enforce single-use lifetime.

---

## 3. Mandatory 7 Startup Keys & Parameter Token Contract

The child validator process must be invoked with the exact 7 mandatory startup keys recognized by the bootstrap system:

| Startup Argument Token | Source Property | Value Type / Invariant |
| :--- | :--- | :--- |
| `-operatorconfig="<path>"` | `childReceipt.BoundConfigPath` | Fully-qualified Windows path to child config JSON |
| `-operatorconfigsha="<sha>"` | `childReceipt.BoundConfigSha256` | 64-character uppercase hex digest |
| `-operatororigin="<id>"` | `childReceipt.BoundOriginId` | Operator-issued origin identifier |
| `-operatorlaunchplan="<id>"` | `childReceipt.BoundLaunchPlanId` | Operator-issued launch plan identifier |
| `-operatorconfigid="<id>"` | `childReceipt.BoundConfigId` | Operator-issued child config identifier |
| `-operatorrole="READ_ONLY"` | `childReceipt.BoundRole` | Canonical uppercase literal `"READ_ONLY"` |
| `-operatorcapability="<boundary>"` | `childReceipt.BoundCapabilityBoundary` | Operator-issued capability boundary |
| `-savedatafolder="<path>"` | `childReceipt.Snapshot.ValidatorUserDataDirectory` | Reference-only isolated userdata path |
| `--task-file="<path>"` | `taskFilePath` | Protected absolute path to sealed task JSON |
| `--nonce="<nonce>"` | `currentTask.capabilityNonce` | Operator-issued capability nonce |

### Strict Formatting Rules:
- **No Free Concat**: `baseArgs` from `childReceipt.Snapshot.ValidatorArguments` may only be included if explicitly permitted and must not override or shadow any of the 7 mandatory operator keys.
- **No Ad-Hoc Splitting**: Arguments must not be constructed via naive whitespace splitting of untrusted strings.
- **Path Quoting**: All path arguments must be strictly enclosed in double quotes (`"`).

---

## 4. M04 Pass-Through vs. M05 Authoritative Equality

To ensure clear milestone governance:
- **M04 (Current Scope: Preparation & Future Implementation)**:
  - Focuses on **data-only projection, registration carrier, and argument formatting**.
  - Pass-through copy of admitted receipt fields into child argument tokens.
  - Unit tests verify PURE builder outputs, argument strings, and registration rejection guards without executing processes.
- **M05 (Future Scope: Authority & Channel Binding)**:
  - Focuses on **authoritative runtime binding and process identity verification**.
  - Verifies child process PID, process start time UTC, and mutual authentication.
  - Binds the loopback bridge port and establishes nonce-authenticated stream channels.
  - Ensures the child process cannot impersonate the simulator or read arbitrary files.

---

## 5. Security & Isolation Boundaries

1. **Role Immutability**:
   - `SIMULATION` workers cannot switch to `READ_ONLY`.
   - `READ_ONLY` child processes cannot switch to `SIMULATION`.
   - The child registration slot strictly rejects any receipt where `Role != "READ_ONLY"`.
2. **Channel Separation**:
   - The protected task channel (`Tasks\`) and result channel (`Tasks\...result.json`) remain at their absolute, operator-configured paths.
   - Child UserData directory (`ValidatorUserDataDirectory`) is completely isolated from the parent UserData directory (`WorkerUserDataDirectory`).
3. **No Untrusted DTO Promotion**:
   - Child receipts cannot be registered from raw public HTTP/Bridge requests.
   - Only receipts admitted through `OperatorStartupConfigAdmissionFactory` with valid raw byte SHA-256 matching the operator descriptor may be registered.
4. **Local Nonce Protection**:
   - Per MD125..132 and SRS, communication channels are protected by local unguessable nonces, not heavy asymmetric PKI/certificates.
