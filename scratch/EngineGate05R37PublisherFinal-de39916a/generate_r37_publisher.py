# -*- coding: utf-8 -*-
"""
generate_r37_publisher.py
Generates the updated publish_operator_pair.py implementing all 8 R37 contract requirements.
"""
import os

target_path = r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py"

code = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
publish_operator_pair.py

Standalone, plan-only operator startup pair publisher for Gate05 R29 / R35 / R36 / R37.
Contracts:
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R35_PLAN_ONLY_PUBLISHER_SAFETY_CONTRACT_20261013.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R37_PUBLISHER_FINAL_IMPLEMENTATION_CONTRACT_20261014.md

Supported Domain & Safety Contracts:
- Standalone stdlib Python script (no external dependencies, no subprocess spawning).
- Strict --spec mode with exact arity (sys.argv == 3) and closed required keys.
- Non-overwrite exclusive owned root: output root must not preexist, created via os.mkdir.
- Direct nofollow lstat ancestry guard: inspects root and every actual component directly,
  rejecting inspection errors, reparse points (symlinks/junctions), traversal, ADS, and reserved DOS names.
  Does NOT guard mandatory lstat with lexists/isdir/isfile that convert inspection errors to False.
  Catches ONLY FileNotFoundError for the exact new output leaf.
- Common readonce helper: captures raw bytes, SHA-256, prior lstat, and handle fstat observation
  for spec and config files; passes captured inputs directly into provenance manifest.
- Fixed one basename 'operator_startup_pair.json'; custom or traversing filenames prohibited.
- Never os.remove/unlink/rmtree/replace/rename; partial outputs on error are preserved as forensic evidence.
- Exclusive file creation ('xb' / O_EXCL) for staging bundle, sha256 file, and provenance manifest.
- Atomic directory entry creation via os.link from staging file into final bundle on NTFS.
  (Note: hard link file data is shared with staging file and mutable if modified; does not provide
   multi-file cross-volume transactional atomicity without volume journaling.)
- Staging file retained as immutable audit evidence alongside final bundle.
- Independently supplied parent and child declarations (7 fields each) and raw config bytes.
- Reads actual raw config files ONCE; strict UTF-8 without BOM; no duplicate JSON properties.
- Exact bootstrap schema: schemaVersion == "WE-OPERATOR-BOOTSTRAP-V1".
- Exact raw role: parent is "SIMULATION", child is "READ_ONLY" (exact ordinal match, no normalization).
- ConfigId binding: raw configId equals original untrimmed expectedConfigId, and snapshot-supported
  trimmed configId equals the SAME untrimmed expectedConfigId.
- CapabilityBoundary binding: raw config capabilityBoundary matches factory-cloned/trimmed descriptor
  expectedCapabilityBoundary case-insensitively BEFORE snapshot; raw capabilityBoundary is never stripped.
- Preserves original descriptor role and capability boundary padding/lowercase verbatim in output bundle.
- Original descriptor expectedConfigSha256: exactly 64 ASCII hex characters without padding or trimming.
- Executable SHA (admittedValidatorExecutableSha256): 64 ASCII hex characters after trim.
- Required paths: admittedValidatorExecutablePath, workerUserDataDirectory, validatorUserDataDirectory,
  workerCwd, validatorCwd are non-blank and valid local DOS paths (lexical check; existence not required).
- UserData isolation: normalized workerUserDataDirectory and validatorUserDataDirectory must be distinct.
- expectedContentProfileFingerprint: non-blank string (not constrained to 64 hex).
- validatorArguments: strictly blank in paired mode (fail-closed).
- expectedPackagePolicyDeclaration: exact 4 keys (schemaVersion, policyId, revision, admittedPackageIds).
  schemaVersion and policyId are non-blank strings; revision is string or integer (explicitly bool-excluded);
  admittedPackageIds is array of strings (order preserved; no package uniqueness or non-empty requirement).
- issuedAtUtc: valid Gregorian UTC ISO 8601 timestamp YYYY-MM-DDTHH:mm:ss[.1..7digits]Z (calendar/time validity,
  ASCII digits [0-9], full consumption, preserves original fractional digits without rounding to 6 digits).
- Exact top 4 JSON fields in writer order:
    1. "schemaVersion" = "we-operator-startup-pair/v1"
    2. "operatorPairId" (opaque, non-empty, original preserved, noTrim/normalize)
    3. "parentDeclaration" (descriptor7 object)
    4. "childDeclaration" (descriptor7 object)
- Descriptor field order:
    1. "originId"
    2. "expectedConfigId"
    3. "expectedRole"
    4. "expectedCapabilityBoundary"
    5. "launchPlanId"
    6. "expectedConfigPath"
    7. "expectedConfigSha256"
- UTF-8 without BOM, compact separators (',', ':'), ensure_ascii=False, NO trailing newline.
"""

import os
import re
import sys
import json
import stat
import hashlib
from datetime import datetime, timezone
from collections import OrderedDict

SCHEMA_VERSION = "we-operator-startup-pair/v1"
CONFIG_BOOTSTRAP_SCHEMA = "WE-OPERATOR-BOOTSTRAP-V1"
FIXED_BUNDLE_BASENAME = "operator_startup_pair.json"

DESCRIPTOR_KEYS = [
    "originId",
    "expectedConfigId",
    "expectedRole",
    "expectedCapabilityBoundary",
    "launchPlanId",
    "expectedConfigPath",
    "expectedConfigSha256"
]

CONFIG_ROOT_KEYS = [
    "schemaVersion",
    "configId",
    "role",
    "admittedValidatorExecutablePath",
    "admittedValidatorExecutableSha256",
    "validatorArguments",
    "workerUserDataDirectory",
    "validatorUserDataDirectory",
    "workerCwd",
    "validatorCwd",
    "capabilityBoundary",
    "issuedAtUtc",
    "expectedContentProfileFingerprint",
    "expectedPackagePolicyDeclaration"
]

POLICY_DECLARATION_KEYS = [
    "schemaVersion",
    "policyId",
    "revision",
    "admittedPackageIds"
]

SPEC_REQUIRED_KEYS = [
    "operatorPairId",
    "parentDeclaration",
    "childDeclaration",
    "parentConfigPath",
    "childConfigPath",
    "outputDir"
]

RESERVED_DOS_DEVICE_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

_ISO_UTC_REGEX = re.compile(
    r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]{1,7}))?Z$"
)

_DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def validate_iso_utc_date(val: str, field_name: str) -> None:
    if not isinstance(val, str):
        raise ValueError(f"{field_name} must be a String token, observed {type(val).__name__}.")
    m = _ISO_UTC_REGEX.match(val)
    if not m:
        raise ValueError(
            f"{field_name} must be a valid Gregorian UTC ISO 8601 string 'YYYY-MM-DDTHH:mm:ss[.1..7digits]Z' with ASCII digits [0-9], observed '{val}'."
        )
    year = int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3))
    hour = int(m.group(4))
    minute = int(m.group(5))
    second = int(m.group(6))
    
    if year < 1 or year > 9999:
        raise ValueError(f"{field_name} invalid year {year} (must be 1..9999) in '{val}'.")
    if month < 1 or month > 12:
        raise ValueError(f"{field_name} invalid month {month} in '{val}'.")
    max_days = _DAYS_IN_MONTH[month]
    if month == 2 and is_leap_year(year):
        max_days = 29
    if day < 1 or day > max_days:
        raise ValueError(f"{field_name} invalid day {day} for month {month} in '{val}'.")
    if hour < 0 or hour > 23:
        raise ValueError(f"{field_name} invalid hour {hour} in '{val}'.")
    if minute < 0 or minute > 59:
        raise ValueError(f"{field_name} invalid minute {minute} in '{val}'.")
    if second < 0 or second > 59:
        raise ValueError(f"{field_name} invalid second {second} in '{val}'.")


def compute_sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def compute_sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return compute_sha256_bytes(f.read())


def check_no_duplicate_keys(pairs):
    seen = set()
    d = OrderedDict()
    for k, v in pairs:
        if k in seen:
            raise ValueError(f"Duplicate JSON property: '{k}'.")
        seen.add(k)
        d[k] = v
    return d


def ascii_strip(s: str) -> str:
    """
    Strips only ASCII whitespace (space, tab, cr, lf, vt, ff).
    Rejects prohibited non-ASCII whitespace characters in structural tokens.
    """
    for ch in s:
        if ch > '\x7f' and ch.isspace():
            raise ValueError(f"Prohibited non-ASCII whitespace character in structural token: {repr(ch)}.")
    return s.strip(" \t\r\n\v\f")


def ascii_upper(s: str) -> str:
    """Converts ASCII lowercase to uppercase without unbounded Unicode case-mapping."""
    return "".join(c.upper() if 'a' <= c <= 'z' else c for c in s)


def check_supported_local_dos_path(p: str, field_name: str = "Path") -> str:
    if not isinstance(p, str) or len(p) == 0 or p.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string.")
        
    # Check ASCII control characters (< 32)
    for ch in p:
        if ord(ch) < 32:
            raise ValueError(f"{field_name} contains prohibited control character (ord {ord(ch)}): '{p}'.")
            
    # Prohibit UNC and network paths
    if p.startswith(r"\\") or p.startswith("//"):
        raise ValueError(f"{field_name} cannot be a UNC or network path: '{p}'.")
        
    # Drive letter: [A-Za-z]:[\\/]
    if len(p) < 3 or not (('A' <= p[0] <= 'Z' or 'a' <= p[0] <= 'z') and p[1] == ':' and p[2] in ('\\', '/')):
        raise ValueError(
            f"{field_name} must be a fully-qualified local DOS path starting with drive letter (e.g. 'C:\\'): '{p}'."
        )
        
    # Check Alternate Data Streams (ADS): colon only allowed at index 1 for drive letter
    if ':' in p[2:]:
        raise ValueError(f"{field_name} contains prohibited Alternate Data Stream (ADS) colon: '{p}'.")
        
    # Check standard invalid characters (<>"|?*)
    for ch in '<>"|?*':
        if ch in p:
            raise ValueError(f"{field_name} contains prohibited character '{ch}': '{p}'.")
            
    # Normalize separator to backslash without resolving aliases before inspection
    drive = p[:2]
    rest = p[2:].replace('/', '\\')
    segments = [seg for seg in rest.split('\\') if seg != ""]
    
    for seg in segments:
        if seg == "." or seg == "..":
            raise ValueError(f"{field_name} contains prohibited traversal segment '{seg}': '{p}'.")
        if seg.endswith(".") or seg.endswith(" "):
            raise ValueError(f"{field_name} contains prohibited trailing dot or space in segment '{seg}': '{p}'.")
        base_seg = seg.split('.')[0].upper()
        if base_seg in RESERVED_DOS_DEVICE_NAMES or seg.upper() in RESERVED_DOS_DEVICE_NAMES:
            raise ValueError(f"{field_name} contains prohibited reserved DOS device name '{seg}': '{p}'.")
            
    return drive + "\\" + "\\".join(segments)


def verify_path_ancestry(
    p: str,
    is_new_leaf: bool = False,
    require_dir: bool = False,
    field_name: str = "Path"
) -> str:
    """
    Direct nofollow lstat ancestry guard:
    - Inspects drive root and every actual component directly with os.lstat.
    - Does NOT guard mandatory lstat with lexists/isdir/isfile that convert inspection errors to False.
    - Rejects reparse points (0x0400), junctions, symlinks, and inspection errors fail-closed.
    - For new output leaf (is_new_leaf=True): catches ONLY FileNotFoundError; any other result stops.
    - For existing components: requires parent directories to be directories and input leaves regular files.
    """
    clean_path = check_supported_local_dos_path(p, field_name)
    drive = clean_path[:2]
    rest = clean_path[2:].strip('\\')
    segments = [seg for seg in rest.split('\\') if seg != ""]
    
    # Construct component paths from root down
    root_path = drive + '\\'
    components = [root_path]
    current = root_path
    for seg in segments:
        current = os.path.join(current, seg)
        components.append(current)
        
    # Ancestor directories: all components except leaf (if leaf is new)
    if is_new_leaf:
        ancestors_to_check = components[:-1]
        leaf_to_check = components[-1]
    else:
        ancestors_to_check = components[:-1]
        leaf_to_check = components[-1]
        
    # 1. Direct lstat on root and every required ancestor directory
    for comp in ancestors_to_check:
        try:
            st = os.lstat(comp)
        except FileNotFoundError as ex:
            raise FileNotFoundError(f"Required ancestor directory not found for '{clean_path}': '{comp}'.") from ex
        except OSError as ex:
            raise ValueError(f"Cannot inspect ancestor directory '{comp}' for '{clean_path}': {ex}.") from ex
            
        attrs = getattr(st, 'st_file_attributes', None)
        reparse_flag = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x0400)
        if (attrs is not None and (attrs & reparse_flag)) or stat.S_ISLNK(st.st_mode):
            raise ValueError(f"Unsafe reparse point / junction / symlink in ancestor '{comp}'.")
            
        if not stat.S_ISDIR(st.st_mode):
            raise ValueError(f"Ancestor component is not a directory for '{clean_path}': '{comp}'.")
            
    # 2. Inspect leaf component
    if is_new_leaf:
        # Leaf must NOT exist. Direct lstat: FileNotFoundError is the ONLY permitted exception!
        try:
            st = os.lstat(leaf_to_check)
            # If lstat succeeded, leaf already exists!
            raise FileExistsError(f"Preexisting output root prohibited: '{leaf_to_check}'.")
        except FileNotFoundError:
            # Expected and required: output leaf does not exist
            pass
        except OSError as ex:
            raise ValueError(f"Inspection error on output root leaf '{leaf_to_check}': {ex}.") from ex
    else:
        try:
            st = os.lstat(leaf_to_check)
        except FileNotFoundError as ex:
            raise FileNotFoundError(f"{field_name} not found: '{leaf_to_check}'.") from ex
        except OSError as ex:
            raise ValueError(f"Cannot inspect {field_name} '{leaf_to_check}': {ex}.") from ex
            
        attrs = getattr(st, 'st_file_attributes', None)
        reparse_flag = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x0400)
        if (attrs is not None and (attrs & reparse_flag)) or stat.S_ISLNK(st.st_mode):
            raise ValueError(f"Unsafe reparse point / junction / symlink on leaf '{leaf_to_check}'.")
            
        if require_dir:
            if not stat.S_ISDIR(st.st_mode):
                raise ValueError(f"{field_name} is not a directory: '{leaf_to_check}'.")
        else:
            if not stat.S_ISREG(st.st_mode):
                raise ValueError(f"{field_name} is not a regular file: '{leaf_to_check}'.")
                
    return clean_path


def read_once_file_and_stat(clean_path: str) -> dict:
    """
    Common readonce helper:
    Captures prior nofollow lstat witness, opens handle, observes fstat, reads bytes once,
    computes SHA-256, and verifies handle size matches bytes read.
    """
    prior_st = os.lstat(clean_path)
    prior_stat_dict = {
        "dev": getattr(prior_st, "st_dev", "N/A"),
        "ino": getattr(prior_st, "st_ino", "N/A"),
        "mode": getattr(prior_st, "st_mode", "N/A"),
        "size": getattr(prior_st, "st_size", "N/A"),
        "mtime_ns": getattr(prior_st, "st_mtime_ns", "N/A"),
        "attributes": getattr(prior_st, "st_file_attributes", "N/A")
    }
    
    with open(clean_path, "rb") as f:
        handle_st = os.fstat(f.fileno())
        handle_stat_dict = {
            "dev": getattr(handle_st, "st_dev", "N/A"),
            "ino": getattr(handle_st, "st_ino", "N/A"),
            "mode": getattr(handle_st, "st_mode", "N/A"),
            "size": getattr(handle_st, "st_size", "N/A"),
            "mtime_ns": getattr(handle_st, "st_mtime_ns", "N/A"),
            "attributes": getattr(handle_st, "st_file_attributes", "N/A")
        }
        raw_bytes = f.read()
        
    if handle_st.st_size != len(raw_bytes):
        raise ValueError(
            f"Handle fstat size {handle_st.st_size} differs from {len(raw_bytes)} bytes read for '{clean_path}'."
        )
        
    raw_sha = compute_sha256_bytes(raw_bytes)
    
    return {
        "path": clean_path,
        "raw_bytes": raw_bytes,
        "sha256": raw_sha,
        "bytes_len": len(raw_bytes),
        "prior_stat": prior_stat_dict,
        "handle_stat": handle_stat_dict
    }


def is_exact_64_ascii_hex_no_trim(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64:
        return False
    return all(c in '0123456789abcdefABCDEF' for c in s)


def is_64_ascii_hex_trimmed(s: str) -> bool:
    if not isinstance(s, str):
        return False
    trimmed = ascii_strip(s)
    if len(trimmed) != 64:
        return False
    return all(c in '0123456789abcdefABCDEF' for c in trimmed)


def validate_declaration(desc: dict, expected_role: str, decl_name: str) -> OrderedDict:
    if not isinstance(desc, dict):
        raise ValueError(f"{decl_name} must be a dictionary/object.")
    
    # Check exact 7 keys
    keys = list(desc.keys())
    for k in DESCRIPTOR_KEYS:
        if k not in desc:
            raise ValueError(f"{decl_name} missing required key '{k}'.")
    for k in keys:
        if k not in DESCRIPTOR_KEYS:
            raise ValueError(f"{decl_name} contains unknown key '{k}'.")
            
    # Value types and non-empty checks; preserve original strings verbatim
    ordered_desc = OrderedDict()
    for k in DESCRIPTOR_KEYS:
        val = desc[k]
        if not isinstance(val, str):
            raise ValueError(f"{decl_name} field '{k}' must be a string, observed {type(val).__name__}.")
        if ascii_strip(val) == "":
            raise ValueError(f"{decl_name} field '{k}' cannot be null, empty, or whitespace.")
        ordered_desc[k] = val
        
    # Role check: case-insensitive match against expected role after structural ASCII strip
    role_trimmed = ascii_upper(ascii_strip(ordered_desc["expectedRole"]))
    if role_trimmed != ascii_upper(expected_role):
        raise ValueError(f"{decl_name} expectedRole must be '{expected_role}', observed '{ordered_desc['expectedRole']}'.")
        
    # Path check: must be a supported local DOS path
    check_supported_local_dos_path(ordered_desc["expectedConfigPath"], f"{decl_name} expectedConfigPath")
        
    # SHA check: must be EXACTLY 64 ASCII hex characters without padding or trimming
    if not is_exact_64_ascii_hex_no_trim(ordered_desc["expectedConfigSha256"]):
        raise ValueError(
            f"{decl_name} expectedConfigSha256 '{ordered_desc['expectedConfigSha256']}' must be exactly 64 ASCII hex characters without padding or whitespace."
        )
        
    return ordered_desc


def validate_config(config_witness: dict, desc: OrderedDict, expected_role: str, config_label: str) -> OrderedDict:
    raw_bytes = config_witness["raw_bytes"]
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        raise ValueError(f"{config_label} contains prohibited UTF-8 Byte Order Mark (BOM).")
        
    try:
        text = raw_bytes.decode('utf-8')
    except UnicodeDecodeError as ex:
        raise ValueError(f"{config_label} UTF-8 decode error: {ex}") from ex
        
    try:
        config_dict = json.loads(text, object_pairs_hook=check_no_duplicate_keys)
    except Exception as ex:
        raise ValueError(f"{config_label} JSON syntactic/duplicate property error: {ex}") from ex
        
    if not isinstance(config_dict, dict):
        raise ValueError(f"{config_label} must be a JSON object.")
        
    # Check exact 14 properties
    for k in CONFIG_ROOT_KEYS:
        if k not in config_dict:
            raise ValueError(f"{config_label} missing required property '{k}'.")
    for k in config_dict.keys():
        if k not in CONFIG_ROOT_KEYS:
            raise ValueError(f"{config_label} contains unknown root property '{k}'.")
            
    # Validate scalar string properties (the first 13)
    for k in CONFIG_ROOT_KEYS:
        if k == "expectedPackagePolicyDeclaration":
            continue
        val = config_dict[k]
        if not isinstance(val, str):
            raise ValueError(f"{config_label} property '{k}' must be a String token (observed {type(val).__name__}).")
            
    # 1. Exact bootstrap schema
    if config_dict["schemaVersion"] != CONFIG_BOOTSTRAP_SCHEMA:
        raise ValueError(
            f"{config_label} schemaVersion must be '{CONFIG_BOOTSTRAP_SCHEMA}', observed '{config_dict['schemaVersion']}'."
        )
        
    # 2. Exact raw role (exact string match without case conversion or trimming)
    if config_dict["role"] != expected_role:
        raise ValueError(
            f"{config_label} role must be exact '{expected_role}', observed '{config_dict['role']}'."
        )
        
    # 3. ConfigId: rawConfigId equals original UNTRIMMED expectedConfigId (Ordinal),
    # and snapshot-supported trim(configId) equals the SAME UNTRIMMED original desc expectedConfigId.
    cfg_id = config_dict["configId"]
    expected_id = desc["expectedConfigId"]
    if ascii_strip(cfg_id) == "":
        raise ValueError(f"{config_label} configId cannot be null, empty, or whitespace.")
    if cfg_id != expected_id:
        raise ValueError(
            f"{config_label} raw configId mismatch: declared '{expected_id}' vs config '{cfg_id}'."
        )
    if ascii_strip(cfg_id) != expected_id:
        raise ValueError(
            f"{config_label} snapshot-trimmed configId mismatch: declared untrimmed '{expected_id}' vs trimmed config '{ascii_strip(cfg_id)}'."
        )
        
    # 4. CapabilityBoundary: raw config capabilityBoundary must match factory-cloned/trimmed
    # descriptor expectedCapabilityBoundary case-insensitively BEFORE snapshot.
    # Raw config capabilityBoundary is NEVER stripped for binding.
    cloned_trimmed_desc_cap = ascii_upper(ascii_strip(desc["expectedCapabilityBoundary"]))
    raw_cfg_cap = ascii_upper(config_dict["capabilityBoundary"])
    if raw_cfg_cap != cloned_trimmed_desc_cap:
        raise ValueError(
            f"{config_label} capabilityBoundary mismatch: declared cloned-trimmed '{cloned_trimmed_desc_cap}' vs raw config '{raw_cfg_cap}'."
        )
        
    # 5. Required executable and working directory paths
    check_supported_local_dos_path(config_dict["admittedValidatorExecutablePath"], f"{config_label} admittedValidatorExecutablePath")
    check_supported_local_dos_path(config_dict["workerUserDataDirectory"], f"{config_label} workerUserDataDirectory")
    check_supported_local_dos_path(config_dict["validatorUserDataDirectory"], f"{config_label} validatorUserDataDirectory")
    check_supported_local_dos_path(config_dict["workerCwd"], f"{config_label} workerCwd")
    check_supported_local_dos_path(config_dict["validatorCwd"], f"{config_label} validatorCwd")
    
    # 6. UserData directory separation
    norm_worker_ud = os.path.normcase(os.path.abspath(config_dict["workerUserDataDirectory"])).rstrip("\\/")
    norm_val_ud = os.path.normcase(os.path.abspath(config_dict["validatorUserDataDirectory"])).rstrip("\\/")
    if norm_worker_ud == norm_val_ud:
        raise ValueError(
            f"{config_label} workerUserDataDirectory and validatorUserDataDirectory must be distinct (both resolve to '{norm_worker_ud}')."
        )
        
    # 7. Executable SHA: trimmed 64 ASCII hex characters
    if not is_64_ascii_hex_trimmed(config_dict["admittedValidatorExecutableSha256"]):
        raise ValueError(
            f"{config_label} admittedValidatorExecutableSha256 '{config_dict['admittedValidatorExecutableSha256']}' must be a valid 64-character hex string."
        )
        
    # 8. validatorArguments strictly blank
    val_args = config_dict["validatorArguments"]
    if ascii_strip(val_args) != "":
        raise ValueError(f"{config_label} validatorArguments must be blank in paired mode (observed '{val_args}').")
        
    # 9. issuedAtUtc valid Gregorian UTC ISO 8601 string (preserves original raw text without rounding)
    validate_iso_utc_date(config_dict["issuedAtUtc"], f"{config_label} issuedAtUtc")
    
    # 10. expectedContentProfileFingerprint non-blank string
    if ascii_strip(config_dict["expectedContentProfileFingerprint"]) == "":
        raise ValueError(f"{config_label} expectedContentProfileFingerprint cannot be null, empty, or whitespace.")
        
    # 11. expectedPackagePolicyDeclaration validation
    policy_obj = config_dict["expectedPackagePolicyDeclaration"]
    if not isinstance(policy_obj, dict):
        raise ValueError(
            f"{config_label} property 'expectedPackagePolicyDeclaration' must be an Object token (observed {type(policy_obj).__name__})."
        )
        
    for k in POLICY_DECLARATION_KEYS:
        if k not in policy_obj:
            raise ValueError(f"{config_label} missing required property '{k}' in expectedPackagePolicyDeclaration.")
    for k in policy_obj.keys():
        if k not in POLICY_DECLARATION_KEYS:
            raise ValueError(f"{config_label} contains unknown property '{k}' in expectedPackagePolicyDeclaration.")
            
    if not isinstance(policy_obj["schemaVersion"], str) or ascii_strip(policy_obj["schemaVersion"]) == "":
        raise ValueError(f"{config_label} policy 'schemaVersion' must be a non-blank String token.")
    if not isinstance(policy_obj["policyId"], str) or ascii_strip(policy_obj["policyId"]) == "":
        raise ValueError(f"{config_label} policy 'policyId' must be a non-blank String token.")
        
    # revision must be string or integer, explicitly bool-excluded
    rev_val = policy_obj["revision"]
    if isinstance(rev_val, bool) or not (isinstance(rev_val, str) or isinstance(rev_val, int)):
        raise ValueError(f"{config_label} policy 'revision' must be a String or Integer token (bool excluded).")
    if isinstance(rev_val, str) and ascii_strip(rev_val) == "":
        raise ValueError(f"{config_label} policy 'revision' cannot be blank string.")
        
    if not isinstance(policy_obj["admittedPackageIds"], list):
        raise ValueError(f"{config_label} policy 'admittedPackageIds' must be an Array token.")
    for idx, pkg_id in enumerate(policy_obj["admittedPackageIds"]):
        if not isinstance(pkg_id, str):
            raise ValueError(f"{config_label} element {idx} in 'admittedPackageIds' must be a String token.")
            
    return config_dict


def publish_pair(
    operator_pair_id: str,
    parent_decl: dict,
    child_decl: dict,
    parent_config_path: str,
    child_config_path: str,
    output_dir: str,
    bundle_filename: str = FIXED_BUNDLE_BASENAME,
    spec_witness: dict = None
) -> dict:
    """
    Validates, rehashes, and atomically writes the operator startup pair bundle and manifest.
    Guarantees non-overwrite exclusive publication under a freshly created owned root.
    Returns publication metadata summary.
    """
    if not isinstance(operator_pair_id, str) or len(operator_pair_id) == 0:
        raise ValueError("operator_pair_id must be an opaque, non-empty string.")
        
    # Validate fixed bundle filename
    if bundle_filename != FIXED_BUNDLE_BASENAME or "/" in bundle_filename or "\\" in bundle_filename:
        raise ValueError(
            f"Only fixed basename '{FIXED_BUNDLE_BASENAME}' is supported; custom or traversing filename '{bundle_filename}' prohibited."
        )
        
    # Validate declarations independently without mutation (preserves original padding and case)
    ordered_parent_decl = validate_declaration(parent_decl, "SIMULATION", "parentDeclaration")
    ordered_child_decl = validate_declaration(child_decl, "READ_ONLY", "childDeclaration")
    
    # Validate parent and child config paths with direct nofollow ancestry guard
    clean_parent_cfg_path = verify_path_ancestry(
        parent_config_path, is_new_leaf=False, require_dir=False, field_name="parent_config_path"
    )
    clean_child_cfg_path = verify_path_ancestry(
        child_config_path, is_new_leaf=False, require_dir=False, field_name="child_config_path"
    )
    
    # Windows path equality check between supplied path and descriptor expectedConfigPath
    norm_supplied_parent = os.path.normcase(os.path.abspath(clean_parent_cfg_path)).rstrip("\\/")
    norm_decl_parent = os.path.normcase(os.path.abspath(ordered_parent_decl["expectedConfigPath"])).rstrip("\\/")
    if norm_supplied_parent != norm_decl_parent:
        raise ValueError(
            f"Parent config path '{clean_parent_cfg_path}' does not match descriptor expectedConfigPath '{ordered_parent_decl['expectedConfigPath']}'."
        )
        
    norm_supplied_child = os.path.normcase(os.path.abspath(clean_child_cfg_path)).rstrip("\\/")
    norm_decl_child = os.path.normcase(os.path.abspath(ordered_child_decl["expectedConfigPath"])).rstrip("\\/")
    if norm_supplied_child != norm_decl_child:
        raise ValueError(
            f"Child config path '{clean_child_cfg_path}' does not match descriptor expectedConfigPath '{ordered_child_decl['expectedConfigPath']}'."
        )
        
    # Read actual files ONCE into byte buffers with handle stat observation
    parent_witness = read_once_file_and_stat(clean_parent_cfg_path)
    child_witness = read_once_file_and_stat(clean_child_cfg_path)
    
    parent_raw_bytes = parent_witness["raw_bytes"]
    child_raw_bytes = child_witness["raw_bytes"]
    parent_raw_sha = parent_witness["sha256"]
    child_raw_sha = child_witness["sha256"]
    
    # Verify raw bytes SHA matches descriptor expectedConfigSha256
    expected_parent_sha = ordered_parent_decl["expectedConfigSha256"].upper()
    expected_child_sha = ordered_child_decl["expectedConfigSha256"].upper()
    
    if parent_raw_sha != expected_parent_sha:
        raise ValueError(
            f"Parent config SHA mismatch: declared '{expected_parent_sha}' vs actual '{parent_raw_sha}'."
        )
    if child_raw_sha != expected_child_sha:
        raise ValueError(
            f"Child config SHA mismatch: declared '{expected_child_sha}' vs actual '{child_raw_sha}'."
        )
        
    # Validate config14 contents and strict binding against descriptor
    parent_config = validate_config(parent_witness, ordered_parent_decl, "SIMULATION", "parentConfig")
    child_config = validate_config(child_witness, ordered_child_decl, "READ_ONLY", "childConfig")
    
    # Validate output directory: must be non-existing leaf with whole valid ancestor directories
    clean_out_dir = verify_path_ancestry(
        output_dir, is_new_leaf=True, require_dir=False, field_name="output_dir"
    )
    output_dir_clean = os.path.abspath(clean_out_dir)
    
    # Create output root exclusively
    os.mkdir(output_dir_clean)
    
    # Re-verify output root ancestry after creation (now leaf exists and must be directory)
    verify_path_ancestry(output_dir_clean, is_new_leaf=False, require_dir=True, field_name="output_dir")
    
    # Construct exact top-4 ordered dictionary
    bundle_data = OrderedDict()
    bundle_data["schemaVersion"] = SCHEMA_VERSION
    bundle_data["operatorPairId"] = operator_pair_id
    bundle_data["parentDeclaration"] = ordered_parent_decl
    bundle_data["childDeclaration"] = ordered_child_decl
    
    # Serialize to compact JSON without BOM, ensure_ascii=False, no trailing newline
    bundle_json_str = json.dumps(bundle_data, ensure_ascii=False, separators=(',', ':'))
    bundle_bytes = bundle_json_str.encode('utf-8')
    bundle_sha256 = compute_sha256_bytes(bundle_bytes)
    
    out_bundle_path = os.path.join(output_dir_clean, FIXED_BUNDLE_BASENAME)
    staging_bundle_path = os.path.join(output_dir_clean, "operator_startup_pair.staging.json")
    out_sha_path = os.path.join(output_dir_clean, "operator_startup_pair.sha256.txt")
    out_manifest_path = os.path.join(output_dir_clean, "PROVENANCE_MANIFEST.json")
    
    # 1. Write staging bundle exclusively (xb)
    with open(staging_bundle_path, "xb") as f:
        f.write(bundle_bytes)
        
    # 2. Write SHA file exclusively (xb)
    with open(out_sha_path, "xb") as f:
        f.write(bundle_sha256.encode('utf-8'))
        
    # 3. Build and write provenance manifest exclusively (xb)
    manifest = {
        "schemaVersion": "we-operator-pair-provenance/v1",
        "publishedAtUtc": datetime.now(timezone.utc).isoformat(),
        "operatorPairId": operator_pair_id,
        "bundleFile": {
            "path": os.path.abspath(out_bundle_path),
            "sha256": bundle_sha256,
            "bytes": len(bundle_bytes)
        },
        "stagingFile": {
            "path": os.path.abspath(staging_bundle_path),
            "sha256": bundle_sha256,
            "bytes": len(bundle_bytes)
        },
        "inputs": {
            "specFile": {
                "path": os.path.abspath(spec_witness["path"]) if spec_witness else "N/A",
                "sha256": spec_witness["sha256"] if spec_witness else "N/A",
                "bytes": spec_witness["bytes_len"] if spec_witness else "N/A",
                "prior_stat": spec_witness.get("prior_stat") if spec_witness else "N/A",
                "handle_stat": spec_witness.get("handle_stat") if spec_witness else "N/A"
            },
            "parentConfig": {
                "path": os.path.abspath(clean_parent_cfg_path),
                "sha256": parent_raw_sha,
                "bytes": len(parent_raw_bytes),
                "configId": parent_config["configId"],
                "role": parent_config["role"],
                "prior_stat": parent_witness["prior_stat"],
                "handle_stat": parent_witness["handle_stat"]
            },
            "childConfig": {
                "path": os.path.abspath(clean_child_cfg_path),
                "sha256": child_raw_sha,
                "bytes": len(child_raw_bytes),
                "configId": child_config["configId"],
                "role": child_config["role"],
                "prior_stat": child_witness["prior_stat"],
                "handle_stat": child_witness["handle_stat"]
            },
            "parentDeclaration": dict(ordered_parent_decl),
            "childDeclaration": dict(ordered_child_decl)
        },
        "publisher": {
            "scriptPath": os.path.abspath(__file__),
            "scriptSha256": compute_sha256_file(__file__),
            "pythonVersion": sys.version
        },
        "guarantees_and_limits": {
            "protected_owner_assumed": True,
            "no_hostile_concurrent_writers_assumed": True,
            "hardlink_entry_creation_atomic": True,
            "hardlink_contents_shared_mutable": True,
            "multi_file_cross_volume_atomicity_untested": True,
            "native_engine_run_untested": True
        }
    }
    
    manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode('utf-8')
    with open(out_manifest_path, "xb") as f:
        f.write(manifest_bytes)
        
    # Re-verify output root ancestry before final link
    verify_path_ancestry(output_dir_clean, is_new_leaf=False, require_dir=True, field_name="output_dir")
    
    # 4. Atomic publication: link staging into final bundle without overwrite
    # Note: On Windows NTFS, os.link atomically creates the directory entry.
    # The file contents are shared with the staging file. Zero destructive deletions or replacements.
    os.link(staging_bundle_path, out_bundle_path)
    
    return {
        "status": "PUBLISHED",
        "operatorPairId": operator_pair_id,
        "bundlePath": os.path.abspath(out_bundle_path),
        "bundleSha256": bundle_sha256,
        "bundleBytes": len(bundle_bytes),
        "stagingPath": os.path.abspath(staging_bundle_path),
        "manifestPath": os.path.abspath(out_manifest_path),
        "parentConfigSha256": parent_raw_sha,
        "childConfigSha256": child_raw_sha
    }


def main():
    # Strict CLI arity: exactly 2 arguments (sys.argv has length 3: [script, "--spec", spec_path])
    if len(sys.argv) == 3 and sys.argv[1] == "--spec":
        spec_path = sys.argv[2]
        clean_spec_path = verify_path_ancestry(
            spec_path, is_new_leaf=False, require_dir=False, field_name="spec_path"
        )
        
        # Read spec file ONCE with handle stat observation
        spec_witness = read_once_file_and_stat(clean_spec_path)
        spec_bytes = spec_witness["raw_bytes"]
        
        if spec_bytes.startswith(b'\xef\xbb\xbf'):
            raise ValueError("spec file contains prohibited UTF-8 Byte Order Mark (BOM).")
        spec_text = spec_bytes.decode('utf-8')
        spec = json.loads(spec_text, object_pairs_hook=check_no_duplicate_keys)
        
        if not isinstance(spec, dict):
            raise ValueError("spec file must contain a JSON object.")
            
        # Closed required keys check
        for k in SPEC_REQUIRED_KEYS:
            if k not in spec:
                raise ValueError(f"spec file missing required key '{k}'.")
        allowed_keys = set(SPEC_REQUIRED_KEYS) | {"bundleFilename"}
        for k in spec.keys():
            if k not in allowed_keys:
                raise ValueError(f"spec file contains unknown key '{k}'.")
                
        # Value types check
        if not isinstance(spec["operatorPairId"], str) or spec["operatorPairId"] == "":
            raise ValueError("spec 'operatorPairId' must be a non-empty string.")
        if not isinstance(spec["parentDeclaration"], dict):
            raise ValueError("spec 'parentDeclaration' must be an object.")
        if not isinstance(spec["childDeclaration"], dict):
            raise ValueError("spec 'childDeclaration' must be an object.")
        if not isinstance(spec["parentConfigPath"], str):
            raise ValueError("spec 'parentConfigPath' must be a string.")
        if not isinstance(spec["childConfigPath"], str):
            raise ValueError("spec 'childConfigPath' must be a string.")
        if not isinstance(spec["outputDir"], str):
            raise ValueError("spec 'outputDir' must be a string.")
        if "bundleFilename" in spec:
            bname = spec["bundleFilename"]
            if not isinstance(bname, str) or bname != FIXED_BUNDLE_BASENAME:
                raise ValueError(
                    f"spec 'bundleFilename' must be fixed '{FIXED_BUNDLE_BASENAME}', observed '{bname}'."
                )
                
        result = publish_pair(
            operator_pair_id=spec["operatorPairId"],
            parent_decl=spec["parentDeclaration"],
            child_decl=spec["childDeclaration"],
            parent_config_path=spec["parentConfigPath"],
            child_config_path=spec["childConfigPath"],
            output_dir=spec["outputDir"],
            bundle_filename=spec.get("bundleFilename", FIXED_BUNDLE_BASENAME),
            spec_witness=spec_witness
        )
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        print(
            "Error: Unsupported CLI invocation. Strict usage: publish_operator_pair.py --spec <absoluteSpecPath> (exact 2 arguments required). Inline CLI flag mode is deprecated and unsupported.",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

with open(target_path, "w", encoding="utf-8") as f:
    f.write(code)

print(f"Generated R37 publisher at {target_path}")
