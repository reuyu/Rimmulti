# Implementation Contract: OperatorChildLaunchInputs Pure Immutable Data Capture

- **Task Dispatch ID**: `WE-A-ENGINE-GATE05-R27-CHILD-CAPTURE-20261011-DIRECT-cdc223f3`
- **Work Package**: `WP_ENGINE_GATE05_R27_CHILD_CAPTURE` (Envelope 30)
- **Status**: `IMPLEMENTED_CHILD_CAPTURE_PASS_NATIVE_UNTESTED`
- **Class Implemented**: `public sealed class OperatorChildLaunchInputs` in `WorkerBridge.cs`
- **Target Insertion Point**: Byte 166910 (zero-width insertion between `OperatorRolePathSelector` and `#region Gate05-R18`)
- **Scope Boundary**: One new PURE immutable capture class and 6 project DLL/PDB outputs ONLY. Zero registration, launcher, CLI flag, or native engine modifications.

---

## 1. Architectural Scope & Purpose

The R27 work package implements the single, pure, immutable data capture container `OperatorChildLaunchInputs` defined in Master review `MASTER_REVIEW_ENGINE_GATE05_R26_DUAL_CHILD_REG_PREPARATION_20261011.md` and controlling instructions `INSTRUCTIONS.md` (with API name corrections `MASTER_R27_CAPTURE_API_NAME_CORRECTION_20261012.md`).

Following the reconciliation of R26 preparations, all static global registration slots, issuer authentication claims, and CLI launcher mutations were deferred. This milestone strictly captures the immutable data contract required to bundle a parent `SIMULATION` admission receipt, a separate child `READ_ONLY` admission receipt, and a simulator-owned 27-field `ValidatorTask` into a tamper-proof container.

### Core Non-Functional Constraints Enforced:
1. **Single Zero-Width Insertion**: Spliced strictly at byte offset 166910 in `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`.
   - Prefix segment (0..166910, 166,910 bytes): SHA-256 `CC93D88C3EDEFF0574F3C5030F5B06346A0F69B956D1F71E85443F249A3F8099` (100% bit-exact).
   - Suffix segment (178847..239574, 60,727 bytes): SHA-256 `7DBD3BFD89EA8B93E951B8F2FD01743E4B85DFFC55079D8ED0F0A7CF55733F47` (100% bit-exact).
2. **Fixed Source Dependencies**: `EngineHostCensus.cs` (170,135 B, SHA `391F9645...`) and `WorkerBridge.csproj` (1,774 B, SHA `571A58F5...`) remain byte-identical.
3. **Pure Execution**: Zero `Process.Start`, zero filesystem lookups, zero reflection, zero global state modification.
4. **Scope Marker**: Hard-coded constant `DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED`.

---

## 2. API Contract & 15 Public Getters

The class exposes exactly fifteen (15) public getters in strict observation order:

| Index | Getter Name | Return Type | Source & Derivation Contract |
| :---: | :--- | :--- | :--- |
| **1** | `ParentReceipt` | `OperatorStartupAdmissionReceipt` | Validated immutable parent admission receipt (`Snapshot.Role == "SIMULATION"`). |
| **2** | `ChildReceipt` | `OperatorStartupAdmissionReceipt` | Validated immutable child admission receipt (`Snapshot.Role == "READ_ONLY"`). |
| **3** | `ApprovedChildDeclaration` | `OperatorLaunchDescriptor` | **Detached fresh copy** constructed on every getter call using child receipt's internal `Approved*` fields (`originId`, `expectedConfigId`, `expectedRole`, `expectedCapabilityBoundary`, `launchPlanId`, `expectedConfigPath`, `expectedConfigSha256`). |
| **4** | `Task` | `ValidatorTask` | **Detached fresh copy** constructed on every getter call with all 27 scalar fields copied from private immutable snapshot. |
| **5** | `TaskFilePath` | `string` | Verbatim `taskFilePath` passed to `Capture`. |
| **6** | `ExecutablePath` | `string` | `parentReceipt.Snapshot.AdmittedValidatorExecutablePath`. |
| **7** | `ExecutableExpectedSha256` | `string` | `parentReceipt.Snapshot.AdmittedValidatorExecutableSha256`. |
| **8** | `WorkingDirectory` | `string` | `childReceipt.Snapshot.ValidatorCwd`. |
| **9** | `SelectedUserDataDirectory` | `string` | Evaluated via `OperatorRolePathSelector.SelectUserData(childReceipt.Snapshot)` (`ValidatorUserDataDirectory`). |
| **10** | `OperatorOptionValues` | `IReadOnlyList<string>` | Read-only collection of the 7 approved options in exact order: `[ApprovedExpectedConfigPath, ApprovedExpectedConfigSha256, ApprovedOriginId, ApprovedLaunchPlanId, ApprovedExpectedConfigId, ApprovedExpectedRole, ApprovedExpectedCapabilityBoundary]`. |
| **11** | `TaskInvocationValues` | `IReadOnlyList<string>` | Read-only collection in exact order: `[taskFilePath, task.capabilityNonce]`. |
| **12** | `ResultChannelPath` | `string` | Copied from `task.resultChannelPath`. |
| **13** | `StagedFilePath` | `string` | Copied from `task.stagedFilePath`. |
| **14** | `StagedSha` | `string` | Copied from `task.stagedSha`. |
| **15** | `Scope` | `string` | Literal `"DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED"`. |

---

## 3. Factory Method & Fail-Closed Preflight Guards

`OperatorChildLaunchInputs` provides a private constructor and a single public entry point:
```csharp
public static OperatorChildLaunchInputs Capture(
    OperatorStartupAdmissionReceipt parentReceipt,
    OperatorStartupAdmissionReceipt childReceipt,
    ValidatorTask task,
    string taskFilePath)
```

### Preflight Invariants (Fail-Closed, SOURCE-ONLY):
1. **Parent Admission Receipt**:
   - `parentReceipt != null` (throws `ArgumentNullException`)
   - `parentReceipt.IsValid()` (throws `ArgumentException`)
   - `parentReceipt.Snapshot != null` (throws `ArgumentException`)
   - `string.Equals(parentReceipt.Snapshot.Role, "SIMULATION", StringComparison.Ordinal)` (throws `InvalidOperationException`)
2. **Child Admission Receipt**:
   - `childReceipt != null` (throws `ArgumentNullException`)
   - `childReceipt.IsValid()` (throws `ArgumentException`)
   - `childReceipt.Snapshot != null` (throws `ArgumentException`)
   - `string.Equals(childReceipt.Snapshot.Role, "READ_ONLY", StringComparison.Ordinal)` (throws `InvalidOperationException`)
3. **Validator Task**:
   - `task != null` (throws `ArgumentNullException`)
4. **Task File Path**:
   - `!string.IsNullOrWhiteSpace(taskFilePath)` (throws `ArgumentException`)
   - `OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath(taskFilePath)` (throws `ArgumentException`)
   - *Note*: Evaluated strictly via pure string predicate without touching the filesystem.

---

## 4. Defensive Copy & Immutability Verification

To prevent race conditions, memory corruption, and unauthorized mutation:
1. **Caller Task Isolation**:
   - All 27 fields of the caller's `ValidatorTask` are captured into private scalar fields.
   - Any subsequent mutation of the caller's `task` instance (modifying IDs, nonces, paths, or flags) has zero effect on the captured instance.
2. **Detached Getter Isolation**:
   - Every invocation of `.Task` or `.ApprovedChildDeclaration` instantiates and returns a brand-new object.
   - Mutating properties of the returned object does not alter subsequent getter invocations.
3. **Read-Only Collections**:
   - `OperatorOptionValues` and `TaskInvocationValues` are backed by `Array.AsReadOnly(...)`.

---

## 5. Status & Deferred Milestones

- **M04 (Current Scope)**: Pure data capture complete and verified.
- **M05 (Deferred)**: Task tuple authority, process identity binding, loopback bridge port allocation, and channel mutual authentication remain **OPEN**.
- **M06 (Deferred)**: Native XML def content census and live context semantics remain **OPEN**.
- **M07 (Deferred)**: Control plane promotion and revocation remain **OPEN**.
- **Foundation Status**: **HOLD** remains strictly in effect.
