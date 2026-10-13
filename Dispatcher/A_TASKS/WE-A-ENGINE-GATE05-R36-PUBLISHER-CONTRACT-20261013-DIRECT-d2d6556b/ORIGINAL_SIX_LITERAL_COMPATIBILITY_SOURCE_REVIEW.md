# Original Six Normal Raw Literal Compatibility Source Review

**Work Package**: `WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT` / `GATE05-R36-PUBLISHER-CONTRACT` (Envelope 39)  
**Target File**: [`scratch/OperatorStartupPairR29/publish_operator_pair.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/OperatorStartupPairR29/publish_operator_pair.py)  
**Authority**: [`docs/WarEconomy_Master_Handoff_20261006/MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md`](file:///C:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md)  
**Evaluation**: Source Inspection & AST Syntax Verification (Zero Runtime Execution)

---

## 1. Executive Summary

This review conducts an in-depth source-level compatibility evaluation of the updated standalone publisher script ([`publish_operator_pair.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/OperatorStartupPairR29/publish_operator_pair.py)) against the six original normal raw literal test cases established in Gate05 R29 through R35. 

Under the Master approved R36 contract, publisher runtime executions, fixture generation, Engine builds, and native execution are strictly prohibited. The verification of compatibility is achieved through rigorous static source analysis and stdlib AST parsing (`ast.parse`), demonstrating that all six normal literal structures remain 100% representable, admitted, and preserved without modification or loss.

---

## 2. Case-by-Case Literal Compatibility Analysis

### Case 1: Standard Baseline Pair (Raw14 Simulation + Read-Only)
- **Source Characteristics**:
  - Parent role: `"SIMULATION"`
  - Child role: `"READ_ONLY"`
  - Config schema: `"WE-OPERATOR-BOOTSTRAP-V1"`
  - All 14 required properties present in exact canonical order without unknown properties.
- **R36 Source Admission**:
  - `publish_operator_pair.py` implements explicit checks:
    ```python
    if parent_cfg.get("role") != "SIMULATION":
        raise ValueError("Parent config role must be SIMULATION")
    if child_cfg.get("role") != "READ_ONLY":
        raise ValueError("Child config role must be READ_ONLY")
    if cfg.get("schemaVersion") != "WE-OPERATOR-BOOTSTRAP-V1":
        raise ValueError("schemaVersion must strictly equal WE-OPERATOR-BOOTSTRAP-V1")
    ```
  - Exact literal strings match without requiring case-insensitive folding or strip mutation.
- **Status**: **100% COMPATIBLE (Source Admitted)**.

---

### Case 2: ConfigId Ordinal Representation and Capability Boundary Matching
- **Source Characteristics**:
  - `configId` strings representing ordinals (e.g., `"config-001"`, `"CFG-SIM-1"`).
  - Corresponding descriptor `expectedConfigId`.
  - Descriptor whitespace padding in legacy fixtures (e.g., `"  CFG-SIM-1  "`).
- **R36 Source Admission**:
  - The implementation enforces:
    1. `configId` must be non-blank.
    2. Exact raw ordinal comparison: `cfg_id == expected_id`.
    3. Snapshot-trimmed ordinal fallback: `cfg_id.strip() == expected_id.strip()`.
  - Neither the config nor the descriptor is mutated on disk; matching succeeds without altering source literals.
- **Status**: **100% COMPATIBLE (Source Admitted)**.

---

### Case 3: Opaque Pair ID Preservation and Compact UTF-8 Ordering
- **Source Characteristics**:
  - `operatorPairId` contains arbitrary opaque string identifiers (e.g., `"WE-PAIR-20261013-001"`, `"Ω-PAIR-AUTH"`).
  - Compact UTF-8 serialization without trailing newline (`
`) or Byte Order Mark (`BOM`).
- **R36 Source Admission**:
  - The publisher treats `operatorPairId` as an opaque, non-empty string without performing stripping, truncation, or normalization:
    ```python
    if not isinstance(operator_pair_id, str) or not operator_pair_id:
        raise ValueError("operator_pair_id must be a non-empty string")
    ```
  - Serialization uses `json.dumps(bundle, separators=(',', ':'), ensure_ascii=False).encode('utf-8')` guaranteeing compact byte representation without BOM or extraneous whitespace.
- **Status**: **100% COMPATIBLE (Source Admitted)**.

---

### Case 4: Unicode Characters in Path Segments and Opaque Identifiers
- **Source Characteristics**:
  - Path components and metadata fields containing valid Unicode characters, such as Greek capital letter Omega (`Ω`), quotes, backslashes, or hyphens (e.g., `C:\RimMulti\test_Ω_dir\config.json`).
- **R36 Source Admission**:
  - The path lexical validator (`validate_dos_path`) explicitly allows non-ASCII characters in path components while strictly filtering forbidden Windows filesystem characters:
    ```python
    INVALID_PATH_CHARS = set('<>"|?*') | {chr(c) for c in range(32)}
    ```
  - Unicode characters such as `Ω` do not intersect with `INVALID_PATH_CHARS` or the ADS colon (`:`) check, preserving full directory segment fidelity.
  - The whole-ancestry guard utilizes `os.lstat`, which natively supports Unicode path strings on Windows NTFS without transcoding errors.
- **Status**: **100% COMPATIBLE (Source Admitted)**.

---

### Case 5: 7-Digit Sub-Microsecond Fractional UTC Timestamps
- **Source Characteristics**:
  - High-precision ISO 8601 UTC timestamps with up to 7 fractional second digits (e.g., `"2026-10-13T10:00:00.1234567Z"`).
  - Strict `'Z'` suffix representing zero UTC offset.
- **R36 Source Admission**:
  - The implementation validates ISO 8601 structure, Gregorian calendar validity, and 24-hour time ranges using regular expressions and standard datetime parsing:
    ```python
    ISO_REGEX = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,7}))?Z$'
    ```
  - Crucially, the raw fractional string is **never rounded, truncated to 6 digits, or re-serialized**, completely eliminating DateTime roundtrip truncation defects identified in R35.
- **Status**: **100% COMPATIBLE (Source Admitted)**.

---

### Case 6: Integer and String Policy Revisions with Boolean Exclusion
- **Source Characteristics**:
  - `expectedPackagePolicyDeclaration.policyRevision` represented as either an integer literal (e.g., `1`, `42`) or string literal (e.g., `"1"`, `"v1.0"`).
  - Explicit exclusion of Python/JSON boolean values (`true`, `false`), which in Python inherit from `int`.
- **R36 Source Admission**:
  - The implementation applies strict type filtering:
    ```python
    if isinstance(rev, bool) or not (isinstance(rev, (int, str))):
        raise ValueError("policyRevision must be an integer or string, and cannot be a boolean")
    ```
  - Both integer and string literals pass cleanly, while booleans fail closed immediately.
  - List of package IDs (`admittedPackageIds`) retains original declaration order without requiring uniqueness or specific hardcoded policy schema constants.
- **Status**: **100% COMPATIBLE (Source Admitted)**.

---

## 3. Structural Comparison Matrix

| Property / Scenario | R35 Implementation | R36 Contract Implementation | Compatibility Impact |
| :--- | :--- | :--- | :--- |
| **schemaVersion** | Prefix match allowed | Strict exact match `"WE-OPERATOR-BOOTSTRAP-V1"` | Fixes loose admission defect |
| **Role Matching** | Case-insensitive `.upper()` | Exact raw match (`"SIMULATION"` / `"READ_ONLY"`) | Eliminates unintended drift |
| **Descriptor SHA** | Stripped before check | Strictly 64 ASCII hex without padding | Fixes whitespace bypass defect |
| **UserData Paths** | Not checked for collision | Enforces distinct worker vs validator directories | Prevents runtime data contamination |
| **Fingerprint** | Mandated 64 hex characters | Any non-blank string allowed | Admits arbitrary opaque fingerprints |
| **Policy Revision** | Primitive check | Integer or string with explicit `bool` rejection | Rejects invalid boolean types |
| **Timestamp (ISO)** | Parsed via `datetime.fromisoformat` | Regex calendar check preserving raw 1..7 digits | Eliminates sub-microsecond roundoff |
| **Path Ancestry** | Checked leaf only | Recursively checks all existing ancestors via `os.lstat` | Closes junction / symlink bypass |
| **CLI Mode** | Allowed inline flags | Strict `--spec <path>` only (exact argc 3) | Prevents argument ambiguity |

---

## 4. Conclusion

All six normal raw literal test cases are 100% representable and source-admitted by the R36 publisher. The contract hardening strictly closes safety loopholes (symlinks, whitespace padding, boolean revisions, sub-microsecond truncation) while preserving full compatibility with valid canonical operator startup configurations.
