# Work Log: WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656`
- **Work Package**: `WP_ENGINE_GATE05_R20_TRUSTED_STARTUP_ORIGIN`
- **Revision**: `GATE05-R20-TRUSTED-STARTUP` (Envelope 23)
- **Role**: Producer Agent A (sole authorized code writer)
- **Date**: 2026-10-11T04:47:50+09:00

---

## 1. Scope & Recovery
- Received Master approved R20 instruction.
- Acknowledged task via [ACK.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656/ACK.json).
- Emitted [ENGINE_FREEZE_BEFORE.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656/ENGINE_FREEZE_BEFORE.json) recording all 9 pre-edit Engine files.
- Confirmed R19 opaque defect is independently CLOSED; preserved all bytes outside the 6 enumerated M01/M03 regions.
- Preserved `EngineHostCensus.cs` (`391F9645...`, 170,135 bytes) and `WorkerBridge.csproj` (`571A58F5...`, 1,774 bytes) 100% byte-for-byte immutable.

---

## 2. Source Modifications in `WorkerBridge.cs`
Modified exclusively within the 6 baseline-enumerated M01/M03 regions:

1. **Region 1 (`WorkerBridgeBootstrapper`)**:
   - Explicit CLI parameter checks for `-operatorconfig` and `-operatorconfigsha`.
   - If missing or invalid, returns immediately before attaching `GameObject` or bridge component.
   - Parses local launch declaration arguments (`-operatorlaunchorigin`, `-operatorlaunchplan`, `-operatorlaunchrole`, `-operatorlaunchconfigid`, `-operatorlaunchboundary`).
   - Calls `OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configPath, expectedSha, launchDesc)`.
   - If receipt issuance fails, logs error and returns before attaching `GameObject`.
   - Invokes `TryInstallOperatorStartupConfig(receipt)`. Only attaches `GameObject` on success.

2. **Region 2 (`WorkerBridgeComponent` state & installer)**:
   - Added private field `_activeAdmissionReceipt` and internal property `ActiveAdmissionReceipt`.
   - Added `TryInstallOperatorStartupConfig(OperatorStartupAdmissionReceipt receipt)`: sole entry point for startup configuration, strictly requiring factory-issued admission receipt. Seals and stores receipt and snapshot.

3. **Region 3 (`Awake`)**:
   - Defense-in-depth gate: checks `_activeAdmissionReceipt != null && _activeAdmissionReceipt.IsValid()`.
   - If not satisfied, immediately invokes `RevokeReadiness`, logs critical error, and returns before policy setup, listener creation/start, or thread start.

4. **Region 4 (`HandleValidateInput`)**:
   - Verifies `_activeAdmissionReceipt != null && _activeAdmissionReceipt.IsValid()`.
   - If missing or invalid, revokes readiness and returns immediate failure, preventing `trustedSimulationReady = true`.

5. **Region 5 (`OperatorLaunchDescriptor` & `OperatorStartupAdmissionReceipt`)**:
   - `OperatorLaunchDescriptor`: Preserved 5 fields (`originId`, `expectedConfigId`, `expectedRole`, `expectedCapabilityBoundary`, `launchPlanId`) + added `expectedConfigPath`, `expectedConfigSha256`, and `Clone()`.
   - `OperatorStartupAdmissionReceipt`: Immutable sealed class with `internal` constructor, containing `ReceiptSchemaVersion`, `Snapshot`, `BoundConfigPath`, `BoundConfigSha256`, `BoundOriginId`, `BoundLaunchPlanId`, `BoundConfigId`, `BoundRole`, `BoundCapabilityBoundary`, `AdmittedAtUtc`, `IsTrusted`, `IsValid()`, and `ToRedactedJson()`.

6. **Region 6 (`OperatorStartupConfigAdmissionFactory`)**:
   - Added `IsFullyQualifiedWindowsPath(string? path)`: enforces DOS drive roots (`C:\` / `C:/`) or UNC roots (`\\server\share\`), rejecting relative, root-relative, or drive-relative paths.
   - Added `ValidateAdmissionReceipt(OperatorStartupAdmissionReceipt? receipt)`.
   - Added `IssueAdmissionReceipt(...)` and `IssueAdmissionReceiptFromBytes(...)`: issues verified, immutable admission receipts.
   - Updated `AdmitConfigFile` and `AdmitConfigBytes` to require fully-qualified Windows path and validate against descriptor path/SHA if specified.

---

## 3. Build & Candidate PE Metadata
- `dotnet build "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" -c Release`:
  - Exit 0, 0 warnings, 0 errors.
  - Release DLL: size 279,552 bytes, SHA256 `90FDAF96404913D917CEE3EFCDC81A94C05B348DBF1BFE3F44852096A32B2C4C`.
  - Release MVID: `96ac6c7c-420a-4c16-a26e-7c0a18d4c360`.
  - Release CodeView: GUID `727f832b-dcb4-4ccd-aed3-4f15239091a1`, Age 1, PDB `scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`.
  - Release PDB: size 52,036 bytes, SHA256 `749A540D23FF0A77CD0A7E0D53E5927B303B40615A7DEDF11A0E4C8D91B4C051`.
- `dotnet build "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" -c Debug`:
  - Exit 0, 0 warnings, 0 errors.
  - Debug DLL: size 295,424 bytes, SHA256 `482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0`.
  - Debug MVID: `9e516c44-35c8-49b8-b3ec-f73ec58ba12f`.
  - Debug CodeView: GUID `b89d72d6-b70a-4e6e-afec-d6654fcfeff7`, Age 1, PDB `scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`.
  - Debug PDB: size 71,020 bytes, SHA256 `EC05783A49CA30FECD9E615020A71206F2AE388D8053D750B3EECEDF9B97455F`.
- Synchronized `scratch\WorkerBridgeMod\1.6\Assemblies\` with Debug candidate.

---

## 4. Test Execution & Evidence
- Authored detached runner `scratch\EngineGate05R20TrustedStartup\Harness\Gate05R20TrustedStartupRunner.csproj` and `Program.cs`. Built with 0 warnings, 0 errors.
- Authored Python host battery `scratch\EngineGate05R20TrustedStartup\run_battery.py`.
- Executed isolated child processes:
  - Run 1 (`en-US`): Child PID 32552, Exit Code 0, Duration 0.310s.
  - Run 2 (`de-DE`): Child PID 8020, Exit Code 0, Duration 0.173s.
- Test Battery Results (100% PASS across 7 suites):
  - `TEST_01_OPAQUE_POLICY_LOSSLESS_PRESERVATION`: PASS (16/16 routes verified, exact lossless digest `8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`).
  - `TEST_02_ADMISSION_RECEIPT_ISSUANCE_AND_BOUND_PROVENANCE`: PASS (8/8 routes verified, factory-issued immutable receipt bound provenance).
  - `TEST_03_DECLARATION_AND_RECEIPT_DEFENSIVE_IMMUTABILITY`: PASS (zero mutation leakage to receipt or snapshot).
  - `TEST_04_RECEIPT_REDACTED_JSON_REPRESENTATION`: PASS (11 public properties, redaction verified).
  - `TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_HELPER`: PASS (DOS drive roots, UNC roots admitted; relative rejected).
  - `TEST_06_VALIDATOR_RESULT_REDACTION_REGRESSION`: PASS (capabilityNonce and channelSecretToken masked).
  - `TEST_07_CENSUS_PACKAGE_POLICY_REGRESSION`: PASS (Census package policy roundtrip verified).
- Stream & Inventory Closure:
  - `stdout.txt` and `stderr.txt` written and closed before computing `OUTPUT_INVENTORY.json`. Both files included and hashed in inventory.
  - Process isolation verified: 100% of Run 1 files identical after Run 2 execution.
- Operational Invariants:
  - Zero C# `Process` APIs called (`ProcessApiCalls`: 0).
  - Zero live `VerifyProcessIdentity` called (`VerifyProcessIdentityCalls`: 0).
  - Zero global `WorkerBridge` configure/reset calls (`WorkerBridgeGlobalConfigureResetCalls`: 0).
  - Zero `Awake` calls (`AwakeCalls`: 0).
  - Zero `Harmony` calls (`HarmonyCalls`: 0).
  - Negative/adverse probes unexecuted (reviewed via static code inspection only).

---

## 5. Same-WP ACK Metadata Correction (MASTER_SAME_WP_ACK_JSON_NOTICE.md)
- Per `MASTER_SAME_WP_ACK_JSON_NOTICE.md`, corrected an invalid JSON escape sequence in `ACK.json` where `wp_file` contained an unescaped single backslash before `WP_ENGINE...`.
- Preserved the original raw malformed ACK bytes as [ACK_ORIGINAL_MALFORMED.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656/ACK_ORIGINAL_MALFORMED.json) (size 1,350 bytes, SHA-256 `81B3FFC323605244B131CBD4C795F564449617BEF6405022AA8330AACF16E4E1`).
- Re-serialized [ACK.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656/ACK.json) using standard Python `json.dump`, and re-read/parsed with `json.load` to guarantee strict JSON validity across all absolute paths and dispatch identities.
- New corrected `ACK.json`: size 1,373 bytes, SHA-256 `F4D7619B0B890E68D5357C5D7C084244DB10F518C0D377923B7485AF6D019547`.
- Bound updated ACK and malformed history identities into [COMPLETION.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656/COMPLETION.json).
- No code scope changes, candidate rebuild, or test rerun occurred; all implementation and E1 results remain identical.
