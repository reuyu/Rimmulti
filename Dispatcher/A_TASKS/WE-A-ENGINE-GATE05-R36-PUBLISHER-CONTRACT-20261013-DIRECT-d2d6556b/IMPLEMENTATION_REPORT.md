# Implementation Report: Gate05 R36 Publisher Contract Hardening

**Dispatch ID**: `WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b`  
**Work Package**: `WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT` / `GATE05-R36-PUBLISHER-CONTRACT` (Envelope 39)  
**Evaluated At**: `2026-10-13T14:40:23.550380+00:00`  
**Producer**: A (Antigravity)  
**Report Kind**: E1  
**Target File**: [`scratch/OperatorStartupPairR29/publish_operator_pair.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/OperatorStartupPairR29/publish_operator_pair.py)

---

## 1. Executive Summary

In accordance with Master instructions and the controlling contract [`MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md`](file:///C:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md), Agent A has completed the safety contract hardening of the standalone publisher script [`publish_operator_pair.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/OperatorStartupPairR29/publish_operator_pair.py).

All work strictly adhered to the authorized scope boundaries:
1. **Single Mutable Source**: Only `scratch/OperatorStartupPairR29/publish_operator_pair.py` was modified (size changed from 22,371 bytes to 31689 bytes, SHA-256: `F60CBC184C6627F0FE15A5A904D0C45A026E20C5138973066BB8174DD8FBFD3F`).
2. **Engine Baseline Immutability**: All 9 Engine baseline files (`WorkerBridge.cs`, `EngineHostCensus.cs`, `WorkerBridge.csproj`, Debug/Release assemblies, and 1.6 assemblies) were verified 100% bit-exact against baseline. Zero Engine builds were executed.
3. **Execution Boundaries**: Zero publisher runtime executions, zero fixture writing, zero unit/native test executions, and zero 1.7 migrations were performed.
4. **AST Syntax Verification**: Standalone Python stdlib AST verification (`ast.parse`) was executed via an isolated helper (`ast_checker.py`), producing a verified `SYNTAX_PASS` verdict (PID 19052, exit code 0).

---

## 2. Technical Modifications in publish_operator_pair.py

The publisher implementation was updated to address the 8 minimal corrective requirements and full supported domain contracts:

1. **Exact Schema Version Requirement**:
   - Strictly enforces `schemaVersion == "WE-OPERATOR-BOOTSTRAP-V1"`.
2. **Raw Role Exact Matching**:
   - Parent role must strictly equal `"SIMULATION"` and child role must strictly equal `"READ_ONLY"` without case-conversion or strip normalization.
3. **ConfigId Validation**:
   - Enforces non-blank string, raw ordinal match, and snapshot-trimmed ordinal match against descriptor `expectedConfigId`.
4. **Descriptor SHA-256 Formatting**:
   - Descriptor `expectedConfigSha256` must be strictly 64 ASCII hex characters without padding or whitespace.
   - Executable SHA-256 trimmed and validated as 64 ASCII hex characters.
5. **Path Lexical Validation & UserData Isolation**:
   - `validate_dos_path` enforces fully-qualified local DOS paths (`^[A-Za-z]:[\\/].*`), rejecting UNC, network paths, traversal (`..`), control characters, ADS colons (`:`), and reserved DOS device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`).
   - Normalizes and verifies that `workerUserDataDirectory` and `validatorUserDataDirectory` are distinct directories.
6. **Content Profile Fingerprint**:
   - `expectedContentProfileFingerprint` enforced as a non-blank string (not restricted to 64 hex characters).
7. **Package Policy Revision Boolean Exclusion**:
   - `policyRevision` admits string or integer, with explicit boolean exclusion (`not isinstance(val, bool)`).
   - Order of `admittedPackageIds` is strictly preserved.
8. **ISO 8601 Timestamp Fidelity**:
   - `issuedAtUtc` validated as valid Gregorian UTC ISO 8601 (`YYYY-MM-DDTHH:mm:ss[.1..7digits]Z`).
   - Raw fractional digits (1 to 7 digits) preserved verbatim without roundoff or truncation to 6 digits.
9. **Reusable Whole-Ancestry Guard**:
   - `verify_path_ancestry` recursively checks all existing ancestor directories using `os.lstat` without following symlinks or junctions.
   - Rejects reparse points (`FILE_ATTRIBUTE_REPARSE_POINT` / 0x400), invalid path characters, and trailing dots/spaces.
   - Fails closed on any inspection error.
10. **Strict CLI Ingestion**:
    - CLI mode restricted strictly to `--spec <absoluteSpecPath>` with exact argc 3. Inline flag mode fails closed.

---

## 3. Standalone AST Verification Evidence

- **Verification Tool**: [`scratch/EngineGate05R36PublisherContract-d2d6556b/ast_checker.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/EngineGate05R36PublisherContract-d2d6556b/ast_checker.py)
- **Target File**: [`scratch/OperatorStartupPairR29/publish_operator_pair.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/OperatorStartupPairR29/publish_operator_pair.py)
- **Interpreter**: `C:\Users\user\anaconda3\python.exe` (104,264 bytes, SHA-256: `388FE2CFFDA8A1341FF9BEB6BCE41B532C2268393F2B6ED6C910B8D99DF14DC6`)
- **Execution PID**: `19052`
- **Exit Code**: `0`
- **Verdict**: `SYNTAX_PASS`
- **AST Nodes**: 25 body statements, 13 top-level functions (`validate_dos_path`, `verify_path_ancestry`, `is_reparse_point`, `read_file_once_and_hash`, `validate_gregorian_utc_iso`, `validate_package_policy`, `validate_config_14`, `validate_declaration_7`, `validate_spec_file`, `parse_args`, `publish_operator_startup_pair`, `main`).
- **Raw Outputs**:
  - stdout: 861 bytes ([`ast_stdout.raw.bin`](file:///C:/Users/user/Desktop/RimMulti/scratch/EngineGate05R36PublisherContract-d2d6556b/ast_stdout.raw.bin))
  - stderr: 0 bytes ([`ast_stderr.raw.bin`](file:///C:/Users/user/Desktop/RimMulti/scratch/EngineGate05R36PublisherContract-d2d6556b/ast_stderr.raw.bin))

---

## 4. Preservation & Baseline Immutability

All 9 Engine baseline files were verified 100% bit-exact against baseline:
1. `WorkerBridge.cs`: 276,685 bytes, SHA `544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD` (MATCH)
2. `EngineHostCensus.cs`: 170,135 bytes, SHA `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` (MATCH)
3. `WorkerBridge.csproj`: 1,774 bytes, SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` (MATCH)
4. `Debug/.../WorkerBridge.PoC.dll`: 326,144 bytes, SHA `8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029` (MATCH)
5. `Debug/.../WorkerBridge.PoC.pdb`: 79,220 bytes, SHA `FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE` (MATCH)
6. `Release/.../WorkerBridge.PoC.dll`: 308,224 bytes, SHA `9CBA7E69210DE90B069F269744F3140C4ADD802FD868AB0E0C71FB0E5F69D106` (MATCH)
7. `Release/.../WorkerBridge.PoC.pdb`: 57,776 bytes, SHA `F05FE976EB522B6A5FC78338B0C35A8CC5341322BACB4CA6310F6AF3682933F5` (MATCH)
8. `1.6/Assemblies/WorkerBridge.PoC.dll`: 326,144 bytes, SHA `8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029` (MATCH)
9. `1.6/Assemblies/WorkerBridge.PoC.pdb`: 79,220 bytes, SHA `FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE` (MATCH)

---

## 5. Governance & Authority Statements

- **Dedicated Server Authority**: Dedicated Server remains final Domain Authority; Engine/Client produces bounded simulation proposals.
- **Foundation HOLD**: Foundation remains HOLD pending Pipeline independent E2 PASS.
- **Steam Installed Incident**: Steam installed DLL discrepancy against archive baseline remains an UNKNOWN OPEN INCIDENT, preserved unmodified.
- **Next Steps**: A awaits Master review and freeze manifest creation, followed by Sol independent static/QA verification under a fresh explicit work package.
