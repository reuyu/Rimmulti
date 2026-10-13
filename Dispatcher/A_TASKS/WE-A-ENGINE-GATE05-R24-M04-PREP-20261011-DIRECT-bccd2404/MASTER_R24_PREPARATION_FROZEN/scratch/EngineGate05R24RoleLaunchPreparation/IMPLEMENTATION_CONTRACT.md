# M04 Role-Aware UserData & Validator Launch Implementation Contract

- **Document Type**: Technical Implementation Contract & Patch Specification
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R24-M04-PREP-20261011-DIRECT-bccd2404`
- **Work Package**: `WP_ENGINE_GATE05_R24_ROLE_LAUNCH_CONTRACT_PREPARATION`
- **Status**: Pure Read-Only Specification (Zero Code Edits, Zero Builds, Zero Execution)
- **Target File**: `scratch/WorkerBridgeMod/Source/WorkerBridge.cs` (227,009 B, SHA `2076E3A8...`)

---

## 1. Problem Statement & Defect Localization

Under current R23 code in [WorkerBridge.cs](file:///C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs):
1. **Unconditional WorkerUserData Selection**:
   In `SafeSaveDataFolderPath` (lines 438-460):
   ```csharp
   if (_activeStartupConfig != null && !string.IsNullOrEmpty(_activeStartupConfig.WorkerUserDataDirectory))
   {
       return _activeStartupConfig.WorkerUserDataDirectory;
   }
   ```
   When the process runs in `READ_ONLY` role (a standalone validator worker), all save, task, and staging directory references still resolve to `WorkerUserDataDirectory` instead of `ValidatorUserDataDirectory`.
2. **Awake Log Blindness**:
   In `Awake` (line 580):
   ```csharp
   Log.Message($"[WorkerBridge] Operator startup config applied in Awake: ConfigId='{_activeAdmissionReceipt.Snapshot.ConfigId}', Role='{_activeAdmissionReceipt.Snapshot.Role}', UserData='{_activeAdmissionReceipt.Snapshot.WorkerUserDataDirectory}'");
   ```
   The startup log always prints `WorkerUserDataDirectory`, failing to indicate which isolated sandbox is active for the current role.
3. **Validator Launch Argument Incompleteness**:
   In `HandleLaunchOperatorValidator` (lines 2264-2281):
   `childArgs` only passes `baseArgs` plus `--task-file` and `--nonce`. For a native RimWorld child process, native UserData isolation requires `-savedatafolder="<ValidatorUserDataDirectory>"` to prevent collisions with the primary worker's `%LOCALAPPDATA%\RimWorld` or worker folder.

---

## 2. Minimal Proposed Patch Specification

### 2.1 Patch Region A: `SafeSaveDataFolderPath` (lines 443-446)
**Current Content**:
```csharp
                // Gate05-R17: If operator startup config is active, route saves/tasks to worker isolated userdata directory
                if (_activeStartupConfig != null && !string.IsNullOrEmpty(_activeStartupConfig.WorkerUserDataDirectory))
                {
                    return _activeStartupConfig.WorkerUserDataDirectory;
                }
```
**Proposed Replacement**:
```csharp
                // Gate05-R24/M04: Role-aware UserData directory routing (Worker vs Validator)
                if (_activeStartupConfig != null)
                {
                    bool isReadOnly = string.Equals(_activeStartupConfig.Role, "READ_ONLY", StringComparison.OrdinalIgnoreCase);
                    string targetDataDir = isReadOnly
                        ? _activeStartupConfig.ValidatorUserDataDirectory
                        : _activeStartupConfig.WorkerUserDataDirectory;
                    if (!string.IsNullOrEmpty(targetDataDir))
                    {
                        return targetDataDir;
                    }
                }
```
**Rationale**:
- Checks `_activeStartupConfig.Role` with `OrdinalIgnoreCase` to preserve canonical case contract.
- Routes `READ_ONLY` instances strictly to `ValidatorUserDataDirectory`.
- Routes `SIMULATION` instances strictly to `WorkerUserDataDirectory`.
- Preserves downstream fallback to `CustomSaveDataPathOverride`, `GenFilePaths.SaveDataFolderPath`, and `%LOCALAPPDATA%\RimWorld`.

### 2.2 Patch Region B: `Awake` Diagnostic Logging (line 580)
**Current Content**:
```csharp
                Log.Message($"[WorkerBridge] Operator startup config applied in Awake: ConfigId='{_activeAdmissionReceipt.Snapshot.ConfigId}', Role='{_activeAdmissionReceipt.Snapshot.Role}', UserData='{_activeAdmissionReceipt.Snapshot.WorkerUserDataDirectory}'");
```
**Proposed Replacement**:
```csharp
                bool isReadOnlyRole = string.Equals(_activeAdmissionReceipt.Snapshot.Role, "READ_ONLY", StringComparison.OrdinalIgnoreCase);
                string activeUserDataDir = isReadOnlyRole
                    ? _activeAdmissionReceipt.Snapshot.ValidatorUserDataDirectory
                    : _activeAdmissionReceipt.Snapshot.WorkerUserDataDirectory;
                Log.Message($"[WorkerBridge] Operator startup config applied in Awake: ConfigId='{_activeAdmissionReceipt.Snapshot.ConfigId}', Role='{_activeAdmissionReceipt.Snapshot.Role}', UserData='{activeUserDataDir}'");
```
**Rationale**:
- Accurately reports the active UserData directory reflecting the admitted role.

### 2.3 Patch Region C: `HandleLaunchOperatorValidator` Argument Construction (lines 2264-2270)
**Current Content**:
```csharp
                // Child arguments are strictly bound to current task and private config
                string childArgs = $"--task-file \"{currentValidatorTaskPath}\" --nonce \"{currentValidatorTask.capabilityNonce}\"";
                if (!string.IsNullOrWhiteSpace(baseArgs))
                {
                    childArgs = $"{baseArgs} {childArgs}";
                }
```
**Proposed Addition/Replacement**:
```csharp
                // Child arguments are strictly bound to current task and private config
                string childArgs = $"--task-file \"{currentValidatorTaskPath}\" --nonce \"{currentValidatorTask.capabilityNonce}\"";
                if (!string.IsNullOrWhiteSpace(baseArgs))
                {
                    childArgs = $"{baseArgs} {childArgs}";
                }
                // Gate05-R24/M04: Enforce native UserData isolation for child validator
                if (!string.IsNullOrWhiteSpace(_activeStartupConfig.ValidatorUserDataDirectory))
                {
                    childArgs = $"-savedatafolder=\"{_activeStartupConfig.ValidatorUserDataDirectory}\" {childArgs}";
                }
```
**Rationale**:
- Provides native RimWorld engine isolation for child processes that consume `-savedatafolder`.
- Avoids collision with simulator worker data.

---

## 3. Schema & Binary Compatibility Guarantees

1. **Zero Schema Modifications Required**:
   - `OperatorStartupConfig`: Already declares `workerUserDataDirectory` (field 8) and `validatorUserDataDirectory` (field 9) in schema `WE-OPERATOR-BOOTSTRAP-V1`.
   - `OperatorStartupConfigAdmissionSnapshot`: Already exposes `WorkerUserDataDirectory` and `ValidatorUserDataDirectory` properties.
   - `OperatorStartupAdmissionReceipt`: 11 public get-only properties remain 100% fixed.
2. **Fixed Segments Integrity**:
   - The proposed changes affect ONLY lines 442-446, line 580, and lines 2264-2270.
   - All other regions (R21 UTC serialization, 11-field receipt schema, ParseStrict, Census package policies, opaque policy digests) remain 100% frozen.
3. **Subsequent Milestones Boundary**:
   - M05 (task tuple generation/binding): Kept separate.
   - M06 (content-context validation): Kept separate.
   - M07 (control-plane authority & promotion): Kept separate.
