# Work Log: WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586`
- **Work Package**: `WP_ENGINE_GATE05_R21_RECEIPT_UTC_LITERAL`
- **Revision**: `GATE05-R21-RECEIPT-UTC` (Envelope 24)
- **Role**: Producer Agent A (sole authorized code writer)
- **Date**: 2026-10-11T06:17:00+09:00

---

## 1. Scope & Recovery
- Received Master approved R21 instruction (`WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586`, Envelope 24).
- Acknowledged task via [ACK.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586/ACK.json) (size 1,344 bytes, SHA-256 `3BF465C9016A62F5BECF88CEF994EDB874346B9486E5CFCBDF975CD7D26C7A02`).
- Emitted [A_RECOVERY_ACK.md](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586/A_RECOVERY_ACK.md) and [ENGINE_FREEZE_BEFORE.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586/ENGINE_FREEZE_BEFORE.json) recording all 9 pre-edit Engine files.
- Scope boundary strictly enforced: ONLY `OperatorStartupAdmissionReceipt.ToRedactedJson` in `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` is modified.
- `WORKER_FIXED_PREFIX.bin` (size 179,745 bytes, SHA-256 `D8502FC0A667DC819F62898885A6AA15618B17D3DD09D2F7DCDD237C7C7CE9F4`) and `WORKER_FIXED_SUFFIX.bin` (size 33,242 bytes, SHA-256 `1F4D372F0366DA5F44A3EA34A094BC997812C511D64A3F9E7BEFC37914BBCAA8`): 100% byte-for-byte immutable.
- `EngineHostCensus.cs` (size 170,135 bytes, SHA `391F9645...`) and `WorkerBridge.csproj` (size 1,774 bytes, SHA `571A58F5...`): 100% byte-for-byte immutable.

---

## 2. Source Modifications in `WorkerBridge.cs`
- **Defect Addressed**: In R20, `OperatorStartupAdmissionReceipt.ToRedactedJson` used `JObject.Parse(Snapshot.ToRedactedJson())`, which defaulted to `DateParseHandling.DateTime`, parsing ISO-8601 strings into Date tokens and modifying the lexical formatting/precision of nested `snapshot.issuedAtUtc` (e.g. dropping trailing `.0000000Z`).
- **Correction**: Inside ONLY `OperatorStartupAdmissionReceipt.ToRedactedJson`:
  - Reads `Snapshot.ToRedactedJson()` using an explicit `Newtonsoft.Json.JsonTextReader` over `System.IO.StringReader`.
  - Configures `jsonReader.DateParseHandling = Newtonsoft.Json.DateParseHandling.None`.
  - Loads using `Newtonsoft.Json.Linq.JObject.Load(jsonReader)`.
  - Properly disposes readers via `using` blocks.
  - Leaves the string literal token intact as `JTokenType.String`, preserving the original UTC representation (including `.0000000Z`) verbatim.
- **Prefix/Suffix Exact Verification**:
  - `WorkerBridge.cs` before size: 213,803 bytes.
  - `WorkerBridge.cs` after size: 214,277 bytes, SHA-256 `CD3FBAB2F3BEA22A2E81B8687352451CC695D477069FE1A788291A78A6F85E5D`.
  - Prefix byte match: `WorkerBridge.cs[0:179745] == WORKER_FIXED_PREFIX.bin` (100% match).
  - Suffix byte match: `WorkerBridge.cs[-33242:] == WORKER_FIXED_SUFFIX.bin` (100% match).

---

## 3. Candidate Build & PE Metadata
- `dotnet build "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" -c Release`:
  - Exit 0, 0 warnings, 0 errors.
  - Release DLL: size 279,552 bytes, SHA256 `A2C4C5AD66E082C5F7BEC25A91FA8E7B237121398B94A59E5D60E3B401D0F840`.
  - Release MVID: `28abd2eb-3220-4e97-aa99-c4ff1edb5900`.
  - Release CodeView: GUID `1123d112-6825-4f2d-9f34-54aaf6c32f03`, Age 1, PDB `scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`.
  - Release PDB: size 52,172 bytes, SHA256 `41330A059B468E9011C284068AAF0DA100EA7C5CBC1DCDCB56802E797E0E3A1E`.
- `dotnet build "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" -c Debug`:
  - Exit 0, 0 warnings, 0 errors.
  - Debug DLL: size 295,424 bytes, SHA256 `31D7A2508ACFADE1B9430F43E6F3D2ACF3E9822C787D00DAF55C9E44CF8E5AC4`.
  - Debug MVID: `7a8b444a-3a07-4dee-9d37-4fa7ed3c461c`.
  - Debug CodeView: GUID `8d435f4d-06a1-4b6a-a50a-b2fa31d92bbb`, Age 1, PDB `scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`.
  - Debug PDB: size 71,192 bytes, SHA256 `84C1F2D2BC339DFD00A9BBA29AEA655E92CBD6F77C64A27D0D54A4433370CDD8`.
- Synchronized `scratch\WorkerBridgeMod\1.6\Assemblies\` with Debug candidate DLL and PDB.

---

## 4. Test Execution & Evidence (7/7 PASS)
- Created detached runner `scratch\EngineGate05R21ReceiptUtc\Harness\Gate05R21ReceiptUtcRunner.csproj` and `Program.cs`. Built with 0 warnings, 0 errors.
- Created Python host battery `scratch\EngineGate05R21ReceiptUtc\run_battery.py`.
- Subprocess execution results:
  - Run 1 (`en-US`): Child PID 15684, Exit Code 0, Duration 0.276s.
  - Run 2 (`de-DE`): Child PID 32936, Exit Code 0, Duration 0.165s.
- Test Battery Results (100% PASS across 7 suites):
  - `TEST_01_OPAQUE_POLICY_LOSSLESS_PRESERVATION`: PASS (16/16 routes verified, exact lossless digest `8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`).
  - `TEST_02_ADMISSION_RECEIPT_ISSUANCE_AND_BOUND_PROVENANCE`: PASS (8/8 routes verified, factory-issued immutable receipt bound provenance across SIMULATION/READ_ONLY, PLAIN/OPAQUE, file/bytes).
  - `TEST_03_RECEIPT_REDACTED_JSON_EXACT_LITERAL_UTC_PRESERVATION`: PASS (3/3 UTC variants verified, preserving literal strings including `.0000000Z`, fractional UTC, and whole seconds without Date token coercion).
  - `TEST_04_DECLARATION_AND_RECEIPT_DEFENSIVE_IMMUTABILITY`: PASS (zero mutation leakage to receipt or snapshot).
  - `TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_POSITIVE_HELPER`: PASS (positive DOS drive roots and UNC roots admitted; zero invalid/rejection probes executed).
  - `TEST_06_VALIDATOR_RESULT_REDACTION_REGRESSION`: PASS (capabilityNonce and channelSecretToken masked).
  - `TEST_07_CENSUS_PACKAGE_POLICY_REGRESSION`: PASS (Census package policy roundtrip verified).
- Stream & Inventory Closure:
  - `stdout.txt` and `stderr.txt` explicitly flushed and closed before computing `OUTPUT_INVENTORY.json` (17 items, 100% accounted).
  - Process isolation verified: 100% of Run 1 files identical after Run 2 execution (`isolation_verified: true`).
- Operational Invariants:
  - Zero C# `Process` APIs called (`ProcessApiCalls`: 0).
  - Zero live `VerifyProcessIdentity` called (`VerifyProcessIdentityCalls`: 0).
  - Zero global `WorkerBridge` configure/reset calls (`WorkerBridgeGlobalConfigureResetCalls`: 0).
  - Zero `Awake` calls (`AwakeCalls`: 0).
  - Zero `Harmony` calls (`HarmonyCalls`: 0).
  - Zero invalid/rejection probes executed.
