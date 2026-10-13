# R35 Plan-Only Publisher Safety Implementation Report

**Dispatch ID**: `WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e`  
**Envelope**: 38  
**Work Package**: `WP_ENGINE_GATE05_R35_PUBLISHER`  
**Revision**: `GATE05-R35-PUBLISHER`  
**Date**: 2026-10-13  
**Producer**: Antigravity Development Agent A  
**Verdict**: `SOURCE_SYNTAX_ONLY_PUBLICATION_NOT_EXECUTED`

---

## 1. Executive Summary

This report documents the implementation of the Master-approved R35 Plan-Only Publisher Safety work package.
The objective of R35 is a targeted, safe modification of the single standalone publisher file:
`scratch\OperatorStartupPairR29\publish_operator_pair.py`.

All 9 Engine baseline binaries and source files (`WorkerBridge.cs`, `EngineHostCensus.cs`, `WorkerBridge.csproj`, Debug/Release assemblies, and `1.6\Assemblies`) remain **100% bit-exact and immutable**. No Engine build was performed (Engine build executions: 0).
In strict compliance with the work package contract, Agent A performed source modifications and AST syntax verification ONLY; no publisher executions and no native runtime executions were conducted (Publisher executions: 0, Unit native executions: 0).

---

## 2. Key Safety Contracts Implemented

### 2.1 Non-Overwrite Exclusive Owned Root
- `output_dir` must be a fully-qualified Windows path without `..` traversal segments.
- Prior existence check: `if os.path.lexists(output_dir): raise FileExistsError(...)`. Any preexisting directory or file causes immediate fail-closed termination.
- Parent directory check: resolved parent must exist and must not be a reparse point / junction.
- Exclusive creation: directory is created via `os.mkdir(output_dir)` in a single operation.

### 2.2 Rejection of Unsafe Paths, Traversal, and Reparse Points
- Path checks enforce DOS drive root (`C:\...`) or UNC path (`\\server\share\...`) format.
- Prohibits relative paths, path traversal segments (`..`), and invalid Windows path characters.
- Reparse point guard: `is_reparse_point` checks `st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT` (0x0400) and `os.path.islink`. Reparse points in config paths, output paths, or parent paths are rejected.

### 2.3 Fixed Basename Bundle
- Fixed one basename: `operator_startup_pair.json`.
- Configurable or traversing filenames are strictly prohibited (fail-closed `ValueError`).

### 2.4 Non-Destructive Failure Policy
- The modified script contains **zero** calls to `os.remove`, `os.unlink`, `shutil.rmtree`, `os.replace`, or `os.rename`.
- If an error occurs during publication, partial outputs remain in place as raw forensic evidence without deletion or automatic retry.

### 2.5 Exclusive Creation & Atomic Publication
- All output files are opened exclusively using mode `'xb'` (`O_CREAT | O_EXCL`):
  1. Staging bundle: `operator_startup_pair.staging.json` (`'xb'`)
  2. SHA file: `operator_startup_pair.sha256.txt` (`'xb'`)
  3. Provenance manifest: `PROVENANCE_MANIFEST.json` (`'xb'`)
- Atomic final publication: `os.link(staging_bundle_path, out_bundle_path)`.
  - On Windows NTFS, `os.link` creates a directory entry atomically without overwrite capability.
  - If the target final bundle already exists, `os.link` raises `FileExistsError` without touching existing content.
  - Staging bundle is preserved as immutable audit evidence alongside the final bundle.

### 2.6 Strict Config14 and Decl7 Binding
- Config files are read **ONCE** and rehashed.
- Strict UTF-8 decoding without BOM (BOM raises `ValueError`).
- Duplicate property detection: `check_no_duplicate_keys` hook rejects duplicate JSON properties.
- Exact 14 properties validated per C# `OperatorStartupConfig`:
  - `schemaVersion`, `configId`, `role`, `admittedValidatorExecutablePath`, `admittedValidatorExecutableSha256`, `validatorArguments`, `workerUserDataDirectory`, `validatorUserDataDirectory`, `workerCwd`, `validatorCwd`, `capabilityBoundary`, `issuedAtUtc`, `expectedContentProfileFingerprint`, `expectedPackagePolicyDeclaration`.
- Strict validation that `validatorArguments` is **blank** in paired mode (`config['validatorArguments'].strip() == ''`). Non-blank values trigger immediate fail-closed rejection.
- Declared Windows path equality binding:
  - `os.path.normcase(os.path.abspath(supplied_path)) == os.path.normcase(os.path.abspath(decl['expectedConfigPath']))`
  - Opaque declaration fields are preserved as-is without mutation.
- Raw SHA-256 binding: `compute_sha256_bytes(raw_bytes) == decl['expectedConfigSha256'].strip().upper()`.
- Semantic binding:
  - `config['configId'] == decl['expectedConfigId']`
  - `config['role']` matches `decl['expectedRole']` (parent `SIMULATION`, child `READ_ONLY`)
  - `config['capabilityBoundary']` matches `decl['expectedCapabilityBoundary']`.

---

## 3. AST Syntax Verification Evidence

- Tool: `ast_checker.py` (stdlib `ast.parse` only; does NOT import or execute `publish_operator_pair.py`).
- Pinned Inputs: `AST_INPUT_MANIFEST.json` pinned prior to execution.
- Execution Telemetry:
  - Process ID: 11312
  - Exit Code: 0
  - Duration: 0.0689s
  - Standard Output: 750 bytes (`ast_stdout.raw.bin`, SHA-256 `6D33EB8394CF10CDA62AC27F9043F3A0E14F594E47307646F2862A7C336EA3B5`)
  - Standard Error: 0 bytes (`ast_stderr.raw.bin`, clean)
  - AST Node Count: 24 top-level body nodes, 10 functions, 0 classes.
  - AST Verdict: `SYNTAX_PASS`.

---

## 4. Immutability & Preservation Summary

| File | Role | Expected SHA-256 | Actual SHA-256 | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `WorkerBridge.cs` | Engine Source | `544B2217...` | `544B2217...` | BIT-EXACT MATCH |
| `EngineHostCensus.cs` | Engine Source | `391F9645...` | `391F9645...` | BIT-EXACT MATCH |
| `WorkerBridge.csproj` | Project | `571A58F5...` | `571A58F5...` | BIT-EXACT MATCH |
| `bin\Debug\...\WorkerBridge.PoC.dll` | Candidate DLL | `8091F441...` | `8091F441...` | BIT-EXACT MATCH |
| `bin\Debug\...\WorkerBridge.PoC.pdb` | Candidate PDB | `FE75B3D1...` | `FE75B3D1...` | BIT-EXACT MATCH |
| `bin\Release\...\WorkerBridge.PoC.dll` | Release DLL | `9CBA7E69...` | `9CBA7E69...` | BIT-EXACT MATCH |
| `bin\Release\...\WorkerBridge.PoC.pdb` | Release PDB | `F05FE976...` | `F05FE976...` | BIT-EXACT MATCH |
| `1.6\Assemblies\WorkerBridge.PoC.dll` | Game Deploy DLL | `8091F441...` | `8091F441...` | BIT-EXACT MATCH |
| `1.6\Assemblies\WorkerBridge.PoC.pdb` | Game Deploy PDB | `FE75B3D1...` | `FE75B3D1...` | BIT-EXACT MATCH |
| `publish_operator_pair.py` | Modified Publisher | `9CAEA2DF...` (new) | `9CAEA2DF...` | AUTHORIZED MUTATION |

---

## 5. Execution Boundaries

- **Publisher Executions**: 0 (not imported, not executed).
- **Engine Rebuilds**: 0 (no compile, no project modifications).
- **Native / Runner Executions**: 0.
- **Dedicated Server Authority**: Maintained as final Domain Authority; Foundation HOLD.
