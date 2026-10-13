# A Engine Gate05 R35 Publisher Safety Report — 2026-10-13

**Work Package**: `WP_ENGINE_GATE05_R35_PUBLISHER`  
**Revision**: `GATE05-R35-PUBLISHER`  
**Envelope**: 38  
**Dispatch ID**: `WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e`  
**Producer**: Antigravity Development Agent A  
**E1 Verdict**: `SOURCE_SYNTAX_ONLY_PUBLICATION_NOT_EXECUTED`

---

## 1. Scope & Execution Boundary

Pursuant to Master instructions and the R35 Plan-Only Publisher Safety Contract (`MASTER_R35_PLAN_ONLY_PUBLISHER_SAFETY_CONTRACT_20261013.md`), Agent A performed targeted safety hardening on the single plan-only publisher source:
- `scratch\OperatorStartupPairR29\publish_operator_pair.py`

### Absolute Invariants Maintained:
- **Zero Engine Modifications**: All 9 Engine baseline files (`WorkerBridge.cs`, `EngineHostCensus.cs`, `WorkerBridge.csproj`, candidate Debug DLL/PDB, Release DLL/PDB, and `1.6\Assemblies` DLL/PDB) remain 100% bit-exact against baseline (`MASTER_R35_AUTHORIZED_SOURCE_SCOPE.json`). Engine build executions: 0.
- **Zero Publisher Executions**: The publisher script was NOT imported and NOT executed. No processes spawned. Publisher executions: 0.
- **Zero Unit / Native Executions**: No runner or game runtime executions. Unit/native executions: 0.
- **AST Syntax Verification ONLY**: Standalone stdlib `ast.parse` via `ast_checker.py` verified the syntax of `publish_operator_pair.py` with exit code 0.

---

## 2. Hardened Safety Features

1. **Non-Overwrite Exclusive Root**:
   - Rejects existing output directories via `os.path.lexists`.
   - Exclusively reserves output directory using `os.mkdir`.
   - Rejects non-absolute paths, path traversal (`..`), and unsafe parent reparse points / junctions.

2. **Fixed Bundle Basename**:
   - Fixed to `operator_startup_pair.json`. Custom or traversing filenames are rejected fail-closed.

3. **Non-Destructive Failure Guarantees**:
   - Zero occurrences of `os.remove`, `os.unlink`, `shutil.rmtree`, `os.replace`, or `os.rename`.
   - Partial outputs on error remain in place as raw forensic evidence without deletion or retry.

4. **Exclusive Creation & Atomic Hardlink Publication**:
   - Staging bundle, SHA sidecar, and provenance manifest written exclusively with mode `'xb'`.
   - Atomic publication into final bundle via `os.link` on Windows NTFS.
   - Retains staging bundle as immutable audit evidence alongside final bundle.

5. **Strict Config14 and Decl7 Binding**:
   - Reads config files ONCE and validates raw SHA-256 against descriptor `expectedConfigSha256`.
   - Enforces declared Windows path equality between supplied config path and descriptor `expectedConfigPath`.
   - Enforces strict UTF-8 without BOM and duplicate property rejection.
   - Enforces exact 14 properties of `OperatorStartupConfig`.
   - Enforces that `validatorArguments` is strictly blank in paired mode.
   - Enforces role binding: parent `SIMULATION`, child `READ_ONLY`.

---

## 3. Tool & AST Telemetry

- **AST Checker**: `scratch\EngineGate05R35Publisher-16a25a7e\ast_checker.py`
- **Command**: `[python.exe, -B, ast_checker.py, publish_operator_pair.py]`
- **Process ID**: 11312
- **Duration**: 0.0689s
- **Exit Code**: 0 (`SYNTAX_PASS`)
- **Raw Stdout**: 750 bytes (`ast_stdout.raw.bin`, SHA `6D33EB8394CF10CDA62AC27F9043F3A0E14F594E47307646F2862A7C336EA3B5`)
- **Raw Stderr**: 0 bytes (`ast_stderr.raw.bin`)
- **AST Nodes**: 24 top-level body nodes, 10 functions, 0 classes, stdlib imports only.

---

## 4. Source & Baseline Identity

- **Publisher Before**: 10,442 bytes, SHA-256 `0204609D1D9D8A697B1A0B88537419D78B9E506558C771CA3EDD4C50FD49D470`
- **Publisher After**: 22,371 bytes, SHA-256 `9CAEA2DF0B8F3517DFCBEF080F7D26EC4343CDF4D2FD761453EFA2E4F3B86B4A`
- **Engine Baseline (9 files)**: 100% BIT-EXACT MATCH.
- **Dedicated Server Authority**: Unaltered; Foundation HOLD.
