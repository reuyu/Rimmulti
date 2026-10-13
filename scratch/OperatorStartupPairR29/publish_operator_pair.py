#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
publish_operator_pair.py

Standalone, plan-only operator startup pair publisher for Gate05 R29 / R35 / R36 / R37 / R38 / R39.
Contracts:
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R35_PLAN_ONLY_PUBLISHER_SAFETY_CONTRACT_20261013.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R37_PUBLISHER_FINAL_IMPLEMENTATION_CONTRACT_20261014.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R38_PUBLISHER_BOUNDARIES_IMPLEMENTATION_CONTRACT_20261014.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R39_PUBLISHER_GENERAL_IMPLEMENTATION_CONTRACT_20261014.md
- C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R39_ISSUER_WHITESPACE_SUPPORTED_DOMAIN_20261014.md

Supported Domain & Safety Contracts:
- Standalone stdlib Python script (no external dependencies, no subprocess spawning).
- Strict --spec mode with exact arity (sys.argv == 3) and closed required keys.
- Non-overwrite exclusive owned root: output root must not preexist, created via os.mkdir.
- Direct nofollow lstat ancestry guard: inspects root and every actual component directly,
  rejecting inspection errors, reparse points (symlinks/junctions), traversal, ADS, and reserved DOS names.
  Requires usable Windows st_file_attributes integer (bool excluded) on existing components;
  missing, None, or non-integer st_file_attributes is unsupported and fails closed.
  Catches ONLY FileNotFoundError for the exact new output leaf.
- Observation witness model: prior lstat and handle fstat capture observations under the assumption
  of a protected local owner without hostile concurrent writers; does NOT claim nofollow-open or
  universal race-condition / TOCTOU immunity.
- Common readonce helper: captures raw bytes, SHA-256, prior lstat, and handle fstat observation
  for spec and config files; passes captured inputs directly into provenance manifest.
- Fixed one basename 'operator_startup_pair.json'; custom or traversing filenames prohibited.
- Never os.remove/unlink/rmtree/replace/rename; partial outputs on error are preserved as forensic evidence.
- Exclusive file creation ('xb' / O_EXCL) for staging bundle, sha256 file, and provenance manifest.
- Directory entry creation via os.link from staging file into final bundle on NTFS is atomic for entry creation only;
  hardlink file data is shared and mutable between directory entries. Publication across multiple files (bundle,
  sidecar sha, provenance manifest) does NOT provide multi-file transactional atomicity or crash durability
  on ANY volume regardless of volume journaling.
- Staging file retained alongside final bundle; contents are shared and mutable through either directory entry.
- Independently supplied parent and child declarations (7 fields each) and raw config bytes.
- Reads actual raw config files ONCE; strict UTF-8 without BOM; no duplicate JSON properties.
- Exact bootstrap schema: schemaVersion == "WE-OPERATOR-BOOTSTRAP-V1".
- Exact raw role: parent is "SIMULATION", child is "READ_ONLY" (exact ordinal match, no normalization).
- ConfigId binding: raw configId equals original untrimmed expectedConfigId, and snapshot-supported
  trimmed configId equals the SAME untrimmed expectedConfigId.
- CapabilityBoundary binding: raw config capabilityBoundary matches factory-cloned/trimmed descriptor
  expectedCapabilityBoundary case-insensitively BEFORE snapshot; raw capabilityBoundary is never stripped.
- Capability NONBLANK check: descriptor expectedCapabilityBoundary stripped result must be explicitly non-empty;
  empty capability boundary rejected fail-closed BEFORE binding/outputs.
- Preserves original descriptor role and capability boundary padding/lowercase verbatim in output bundle.
- Original descriptor expectedConfigSha256: exactly 64 ASCII hex characters without padding or trimming.
- Executable SHA (admittedValidatorExecutableSha256): 64 ASCII hex characters after trim.
- Bounded whitespace support profile: explicit documented issuer whitespace set W = {U+0009..000D, U+0020,
  U+0085, U+00A0, U+1680, U+2000..200A, U+2028, U+2029, U+202F, U+205F, U+3000}. Opaque NONBLANK rejects
  empty/all-W strings; version-sensitive blank-only strings involving U+180E are explicitly unsupported;
  interior Unicode and boundary Omega preserved verbatim. Identity boundary trim inspects leading/trailing
  whitespace regions using W and U+180E, rejects non-ASCII boundary whitespace fail-closed, and trims supported
  ASCII whitespace only. Python isspace() is removed from semantic blank and trimming decisions.
- Required paths: admittedValidatorExecutablePath, workerUserDataDirectory, validatorUserDataDirectory,
  workerCwd, validatorCwd are non-blank and valid local DOS paths (lexical check; existence not required).
- UserData isolation: normalized workerUserDataDirectory and validatorUserDataDirectory must be distinct.
- expectedContentProfileFingerprint: opaque non-blank string (not constrained to 64 hex).
- validatorArguments: strictly blank in paired mode (fail-closed).
- expectedPackagePolicyDeclaration: exact 4 keys (schemaVersion, policyId, revision, admittedPackageIds).
  schemaVersion and policyId are opaque non-blank strings; revision is string or integer (explicitly bool-excluded);
  admittedPackageIds is array of strings (order preserved; no package uniqueness or non-empty requirement).
- issuedAtUtc: valid Gregorian UTC ISO 8601 timestamp YYYY-MM-DDTHH:mm:ss[.1..7digits]Z validated with
  full consumption regex matching (ASCII digits [0-9], calendar/leap/time validity, year 1..9999).
  Preserves original raw fractional digits verbatim without rounding (Parent .1234567Z, Child .0000000Z).
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

# Supported issuer whitespace code points (set W) per MASTER_R39_ISSUER_WHITESPACE_SUPPORTED_DOMAIN_20261014.md
SUPPORTED_WHITESPACE_CHARS = {
    '\u0009', '\u000a', '\u000b', '\u000c', '\u000d',  # U+0009..000D (tab, lf, vt, ff, cr)
    '\u0020',                                            # U+0020 (space)
    '\u0085',                                            # U+0085 (next line, NEL)
    '\u00a0',                                            # U+00A0 (no-break space, NBSP)
    '\u1680',                                            # U+1680 (ogham space mark)
    '\u2000', '\u2001', '\u2002', '\u2003', '\u2004',  # U+2000..200A (quad/space variants)
    '\u2005', '\u2006', '\u2007', '\u2008', '\u2009', '\u200a',
    '\u2028',                                            # U+2028 (line separator)
    '\u2029',                                            # U+2029 (paragraph separator)
    '\u202f',                                            # U+202F (narrow no-break space)
    '\u205f',                                            # U+205F (medium mathematical space)
    '\u3000',                                            # U+3000 (ideographic space)
}

ASCII_WHITESPACE_CHARS = {'\u0009', '\u000a', '\u000b', '\u000c', '\u000d', '\u0020'}
LEGACY_VERSION_SENSITIVE_WS = {'\u180e'}  # U+180E (mongolian vowel separator)

# Strict ISO 8601 UTC regex matching ASCII digits [0-9] and ending in 'Z'
_ISO_UTC_REGEX = re.compile(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]{1,7}))?Z$')

# DOS reserved device names
_RESERVED_DOS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}


def is_leap_year(y: int) -> bool:
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def validate_iso_utc_date(val: str, field_name: str) -> None:
    if not isinstance(val, str):
        raise ValueError(f"{field_name} must be a String token (observed {type(val).__name__}).")
    m = _ISO_UTC_REGEX.fullmatch(val)
    if not m:
        raise ValueError(
            f"{field_name} must be a valid Gregorian UTC ISO 8601 string (e.g. YYYY-MM-DDTHH:mm:ss[.1..7digits]Z) using ASCII digits [0-9], observed '{val}'."
        )
    year = int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3))
    hour = int(m.group(4))
    minute = int(m.group(5))
    second = int(m.group(6))
    
    if year < 1 or year > 9999:
        raise ValueError(f"{field_name} year out of valid Gregorian range 1..9999: {year}.")
    if month < 1 or month > 12:
        raise ValueError(f"{field_name} month out of range 1..12: {month}.")
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        max_days = 29
    else:
        max_days = days_in_month[month]
    if day < 1 or day > max_days:
        raise ValueError(f"{field_name} day out of valid range 1..{max_days} for month {month}, year {year}: {day}.")
    if hour < 0 or hour > 23:
        raise ValueError(f"{field_name} hour out of range 0..23: {hour}.")
    if minute < 0 or minute > 59:
        raise ValueError(f"{field_name} minute out of range 0..59: {minute}.")
    if second < 0 or second > 59:
        raise ValueError(f"{field_name} second out of range 0..59: {second}.")


def compute_sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def compute_sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()


def check_no_duplicate_keys(pairs):
    seen = set()
    d = OrderedDict()
    for k, v in pairs:
        if k in seen:
            raise ValueError(f"Duplicate JSON property: '{k}'.")
        seen.add(k)
        d[k] = v
    return d


def check_opaque_non_blank(val: str, field_name: str) -> str:
    """
    Validates opaque string tokens under the bounded issuer whitespace support profile:
    - Must be a string.
    - Reject empty strings.
    - Reject strings composed entirely of supported whitespace characters (set W).
    - Version-sensitive blank-only strings involving U+180E are explicitly UNSUPPORTED.
    - Preserves all supplied Unicode content verbatim (including interior/boundary Unicode whitespace,
      original padding, quotes, backslashes, '=', and symbols like 'Ω').
    - Python isspace() is NOT used for semantic blank decisions.
    """
    if not isinstance(val, str):
        raise ValueError(f"{field_name} must be a String token (observed {type(val).__name__}).")
    if len(val) == 0:
        raise ValueError(f"{field_name} cannot be null or empty.")
    if all(c in SUPPORTED_WHITESPACE_CHARS for c in val):
        raise ValueError(f"{field_name} cannot be whitespace-only (observed all supported whitespace code points).")
    if all(c in (SUPPORTED_WHITESPACE_CHARS | LEGACY_VERSION_SENSITIVE_WS) for c in val):
        raise ValueError(f"{field_name} blank-only string involving version-sensitive U+180E is explicitly unsupported.")
    return val


def identity_boundary_trim(s: str) -> str:
    """
    Trims boundary ASCII whitespace without restricting interior content.
    First examines the leading and trailing whitespace regions using the explicit support profile
    (set W and version-sensitive U+180E):
    - Non-ASCII whitespace (or U+180E) in the boundary region is UNSUPPORTED and fails closed.
    - Leading ASCII spaces followed by non-ASCII whitespace before first content are detected and rejected.
    - Preserves non-ASCII interior content and ordinary boundary non-ASCII characters like 'Ω'.
    - Trims only supported ASCII boundary whitespace (space, tab, cr, lf, vt, ff).
    - Used for identity fields that pass through .NET String.Trim().
    """
    all_ws = SUPPORTED_WHITESPACE_CHARS | LEGACY_VERSION_SENSITIVE_WS
    
    # 1. Find leading whitespace boundary
    i = 0
    while i < len(s) and s[i] in all_ws:
        if s[i] not in ASCII_WHITESPACE_CHARS:
            raise ValueError(
                f"Unsupported non-ASCII boundary whitespace code point {repr(s[i])} (U+{ord(s[i]):04X}) in identity field '{s}'."
            )
        i += 1
        
    # If the string was entirely whitespace
    if i == len(s):
        return ""
        
    # 2. Find trailing whitespace boundary
    j = len(s) - 1
    while j >= i and s[j] in all_ws:
        if s[j] not in ASCII_WHITESPACE_CHARS:
            raise ValueError(
                f"Unsupported non-ASCII boundary whitespace code point {repr(s[j])} (U+{ord(s[j]):04X}) in identity field '{s}'."
            )
        j -= 1
        
    return s[i:j+1]


def structural_ascii_strip(s: str) -> str:
    """
    Strips boundary ASCII whitespace from structural tokens.
    Rejects prohibited non-ASCII characters if present in structural tokens.
    """
    res = []
    for c in s:
        if ord(c) >= 128:
            raise ValueError(f"Prohibited non-ASCII character in structural token: {repr(c)}.")
        res.append(c)
    return "".join(res).strip(" \t\r\n\v\f")


def structural_ascii_upper(s: str) -> str:
    """
    Converts ASCII lowercase to uppercase for structural token case comparison.
    Rejects non-ASCII characters in structural tokens that require ASCII case mapping.
    """
    res = []
    for c in s:
        if 'a' <= c <= 'z':
            res.append(c.upper())
        elif ord(c) < 128:
            res.append(c)
        else:
            raise ValueError(f"Prohibited non-ASCII character in structural token: {repr(c)}.")
    return "".join(res)


def check_supported_local_dos_path(p: str, field_name: str = "Path") -> str:
    if not isinstance(p, str) or len(p) == 0:
        raise ValueError(f"{field_name} must be a non-empty string.")
    if all(c in (SUPPORTED_WHITESPACE_CHARS | LEGACY_VERSION_SENSITIVE_WS) for c in p):
        raise ValueError(f"{field_name} cannot be whitespace-only: '{p}'.")
        
    # Check ASCII control characters (< 32)
    for ch in p:
        if ord(ch) < 32:
            raise ValueError(f"{field_name} contains prohibited control character (ord {ord(ch)}): '{p}'.")
            
    # Prohibit repeated separators or ambiguous slash combinations
    if '//' in p or '\\\\' in p or '\\/' in p or '/\\' in p:
        raise ValueError(f"{field_name} contains prohibited repeated separators or ambiguous alias: '{p}'.")

    # Reject UNC (\\), device (\\.\, \\?\), or relative paths
    if p.startswith('\\\\') or p.startswith('//'):
        raise ValueError(f"{field_name} must not be a UNC or NT device path: '{p}'.")
    if not (len(p) >= 3 and p[0].isalpha() and p[1] == ':' and p[2] in ('\\', '/')):
        raise ValueError(f"{field_name} must be a fully-qualified local DOS path starting with '<Drive>:\\': '{p}'.")

    drive_prefix = p[:3]
    body = p[3:]
    
    # Check trailing separators in non-root path
    if body and (body.endswith('\\') or body.endswith('/')):
        raise ValueError(f"{field_name} contains prohibited trailing separator or ambiguous alias: '{p}'.")
    
    segments = [seg for seg in re.split(r'[\\/]', body) if seg != ""]
    
    # Reject empty interior segments (e.g. from consecutive slashes in body)
    raw_segments = re.split(r'[\\/]', body) if body else []
    if any(s == "" for s in raw_segments):
        raise ValueError(f"{field_name} contains prohibited empty interior segment or repeated separator: '{p}'.")

    for seg in segments:
        if seg == "." or seg == "..":
            raise ValueError(f"{field_name} contains prohibited traversal segment '{seg}' in '{p}'.")
        if ":" in seg:
            raise ValueError(f"{field_name} contains prohibited Alternate Data Stream (ADS) colon in segment '{seg}'.")
        if seg.endswith(" ") or seg.endswith("."):
            raise ValueError(f"{field_name} contains prohibited trailing dot/space in segment '{seg}'.")
        base_name = seg.split('.')[0].upper()
        if base_name in _RESERVED_DOS_NAMES:
            raise ValueError(f"{field_name} contains prohibited reserved DOS device name '{base_name}' in '{p}'.")
            
    return p


def verify_path_ancestry(p: str, is_new_leaf: bool = False, require_dir: bool = False, field_name: str = "Path") -> str:
    r"""
    Direct nofollow lstat ancestry guard:
    Inspects drive root (e.g. C:\) and every actual component directly via os.lstat.
    Requires usable Windows st_file_attributes integer (bool excluded) on existing components;
    missing, None, or non-integer st_file_attributes is unsupported and fails closed.
    Rejects reparse points (symlinks/junctions, 0x400) and directory symlinks.
    If is_new_leaf is True:
      - All ancestors must exist and be safe real directories.
      - The leaf must NOT exist (os.lstat raises FileNotFoundError).
    If is_new_leaf is False:
      - All ancestors and leaf must exist and be safe real files/directories.
    """
    check_supported_local_dos_path(p, field_name)
    clean_p = os.path.normpath(p)
    
    drive, tail = os.path.splitdrive(clean_p)
    drive_root = drive + "\\"
    
    reparse_flag = 0x00000400  # FILE_ATTRIBUTE_REPARSE_POINT

    def check_stat(st, comp_path, should_be_dir):
        attrs = getattr(st, 'st_file_attributes', None)
        if isinstance(attrs, bool) or not isinstance(attrs, int):
            raise ValueError(
                f"Unsupported environment: missing or non-integer st_file_attributes ({attrs}) on '{comp_path}'."
            )
        if (attrs & reparse_flag) or stat.S_ISLNK(st.st_mode):
            raise ValueError(f"Unsafe reparse point / junction / symlink detected at '{comp_path}'.")
        if should_be_dir:
            if not stat.S_ISDIR(st.st_mode):
                raise ValueError(f"Expected directory at '{comp_path}', but found file or non-directory.")
        else:
            if stat.S_ISDIR(st.st_mode):
                raise ValueError(f"Expected regular file at '{comp_path}', but found directory.")

    # 1. Inspect drive root
    try:
        st_root = os.lstat(drive_root)
    except FileNotFoundError:
        raise FileNotFoundError(f"Drive root does not exist: '{drive_root}'.")
    except OSError as ex:
        raise OSError(f"Inspection error on drive root '{drive_root}': {ex}") from ex
    check_stat(st_root, drive_root, should_be_dir=True)

    # 2. Inspect components
    parts = [seg for seg in tail.split(os.sep) if seg]
    curr = drive_root
    
    for idx, part in enumerate(parts):
        curr = os.path.join(curr, part)
        is_leaf = (idx == len(parts) - 1)
        
        if is_leaf and is_new_leaf:
            try:
                st_leaf = os.lstat(curr)
                raise FileExistsError(f"Preexisting output root prohibited: destination leaf already exists at '{curr}'.")
            except FileNotFoundError:
                # Exactly what is required: leaf must not exist
                pass
            except OSError as ex:
                if not isinstance(ex, FileNotFoundError):
                    raise OSError(f"Inspection error on leaf '{curr}': {ex}") from ex
        else:
            try:
                st_comp = os.lstat(curr)
            except FileNotFoundError:
                raise FileNotFoundError(f"Path component does not exist: '{curr}'.")
            except OSError as ex:
                raise OSError(f"Inspection error on component '{curr}': {ex}") from ex
                
            expected_dir = (not is_leaf) or require_dir
            check_stat(st_comp, curr, should_be_dir=expected_dir)

    return clean_p


def read_once_file_and_stat(path: str) -> dict:
    """
    Common read-once helper for spec and config files:
    - Captures prior lstat observation.
    - Opens handle and captures fstat observation.
    - Reads raw bytes once and computes SHA-256.
    - Verifies raw bytes length matches handle stat st_size.
    - Returns witness dictionary.
    """
    clean_path = verify_path_ancestry(path, is_new_leaf=False, require_dir=False, field_name=f"File '{path}'")
    
    prior_st = os.lstat(clean_path)
    prior_attrs = getattr(prior_st, 'st_file_attributes', None)
    
    with open(clean_path, "rb") as f:
        handle_st = os.fstat(f.fileno())
        raw_bytes = f.read()
        
    handle_attrs = getattr(handle_st, 'st_file_attributes', None)
    raw_sha = compute_sha256_bytes(raw_bytes)
    
    if len(raw_bytes) != handle_st.st_size:
        raise ValueError(
            f"Read length mismatch on '{clean_path}': read {len(raw_bytes)} bytes but handle size was {handle_st.st_size} bytes."
        )
        
    return {
        "clean_path": clean_path,
        "raw_bytes": raw_bytes,
        "bytes_len": len(raw_bytes),
        "sha256": raw_sha,
        "prior_stat": {
            "size": prior_st.st_size,
            "mtime": prior_st.st_mtime,
            "st_file_attributes": prior_attrs
        },
        "handle_stat": {
            "size": handle_st.st_size,
            "mtime": handle_st.st_mtime,
            "st_file_attributes": handle_attrs
        }
    }


def is_exact_64_ascii_hex_no_trim(val: str) -> bool:
    if not isinstance(val, str) or len(val) != 64:
        return False
    return bool(re.fullmatch(r'[0-9a-fA-F]{64}', val))


def is_64_ascii_hex_trimmed(val: str) -> bool:
    if not isinstance(val, str):
        return False
    s = identity_boundary_trim(val)
    if len(s) != 64:
        return False
    return bool(re.fullmatch(r'[0-9a-fA-F]{64}', s))


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
            
    # Validate each field according to its structural vs opaque nature
    # Preserves original strings verbatim in output ordered_desc!
    ordered_desc = OrderedDict()
    for k in DESCRIPTOR_KEYS:
        val = desc[k]
        if not isinstance(val, str):
            raise ValueError(f"{decl_name} field '{k}' must be a string, observed {type(val).__name__}.")
        ordered_desc[k] = val
        
    # Opaque fields: originId, launchPlanId
    check_opaque_non_blank(ordered_desc["originId"], f"{decl_name} originId")
    check_opaque_non_blank(ordered_desc["launchPlanId"], f"{decl_name} launchPlanId")
    
    # Structural identity field: expectedConfigId
    check_opaque_non_blank(ordered_desc["expectedConfigId"], f"{decl_name} expectedConfigId")
    
    # Structural role: trim structural ASCII whitespace and compare case
    role_trimmed = structural_ascii_upper(structural_ascii_strip(ordered_desc["expectedRole"]))
    if role_trimmed != structural_ascii_upper(expected_role):
        raise ValueError(f"{decl_name} expectedRole must be '{expected_role}', observed '{ordered_desc['expectedRole']}'.")
        
    # Structural capability boundary: non-blank, valid structural ASCII
    # Item 1: save structural_ascii_strip result and reject empty explicitly BEFORE binding/outputs
    stripped_cap = structural_ascii_strip(ordered_desc["expectedCapabilityBoundary"])
    if len(stripped_cap) == 0:
        raise ValueError(f"{decl_name} expectedCapabilityBoundary cannot be blank or empty after strip.")
    
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
        
    # 3. ConfigId binding:
    # rawConfigId equals original UNTRIMMED expectedConfigId (Ordinal),
    # and snapshot-supported trimmed configId equals the SAME UNTRIMMED original desc expectedConfigId.
    # NOT trim both!
    cfg_id = config_dict["configId"]
    expected_id = desc["expectedConfigId"]
    check_opaque_non_blank(cfg_id, f"{config_label} configId")
    if cfg_id != expected_id:
        raise ValueError(
            f"{config_label} raw configId mismatch: declared '{expected_id}' vs config '{cfg_id}'."
        )
    if identity_boundary_trim(cfg_id) != expected_id:
        raise ValueError(
            f"{config_label} snapshot-trimmed configId mismatch: declared untrimmed '{expected_id}' vs trimmed config '{identity_boundary_trim(cfg_id)}'."
        )
        
    # 4. CapabilityBoundary:
    # raw config capabilityBoundary must match factory-cloned/trimmed
    # descriptor expectedCapabilityBoundary case-insensitively BEFORE snapshot.
    # Raw config capabilityBoundary is NEVER stripped for binding.
    cloned_trimmed_desc_cap = structural_ascii_upper(structural_ascii_strip(desc["expectedCapabilityBoundary"]))
    raw_cfg_cap = structural_ascii_upper(config_dict["capabilityBoundary"])
    if raw_cfg_cap != cloned_trimmed_desc_cap:
        raise ValueError(
            f"{config_label} capabilityBoundary mismatch: declared cloned-trimmed '{cloned_trimmed_desc_cap}' vs raw config '{raw_cfg_cap}'."
        )
        
    # 5. Required executable and working directory paths (lexical checks)
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
    if identity_boundary_trim(val_args) != "":
        raise ValueError(f"{config_label} validatorArguments must be blank in paired mode (observed '{val_args}').")
        
    # 9. issuedAtUtc valid Gregorian UTC ISO 8601 string (preserves original raw text without rounding)
    validate_iso_utc_date(config_dict["issuedAtUtc"], f"{config_label} issuedAtUtc")
    
    # 10. expectedContentProfileFingerprint non-blank string (opaque Unicode non-blank string, not 64 hex)
    check_opaque_non_blank(config_dict["expectedContentProfileFingerprint"], f"{config_label} expectedContentProfileFingerprint")
        
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
            
    check_opaque_non_blank(policy_obj["schemaVersion"], f"{config_label} policy schemaVersion")
    check_opaque_non_blank(policy_obj["policyId"], f"{config_label} policy policyId")
        
    # revision must be string or integer, explicitly bool-excluded
    rev_val = policy_obj["revision"]
    if isinstance(rev_val, bool) or not (isinstance(rev_val, str) or isinstance(rev_val, int)):
        raise ValueError(f"{config_label} policy 'revision' must be a String or Integer token (bool excluded).")
    if isinstance(rev_val, str):
        check_opaque_non_blank(rev_val, f"{config_label} policy revision")
        
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
    Validates, rehashes, and writes the operator startup pair bundle and manifest.
    Guarantees non-overwrite exclusive publication under a freshly created owned root.
    Note: Directory entry creation is atomic via os.link on NTFS, but hardlink contents are shared/mutable
    between staging and final bundle entries. Publication of multiple files (bundle, sha, manifest) does NOT
    provide multi-file transactional atomicity or crash durability on any volume regardless of journaling.
    Observation witnesses assume a protected local owner without hostile concurrent writers.
    Returns publication metadata summary.
    """
    if not isinstance(operator_pair_id, str) or len(operator_pair_id) == 0:
        raise ValueError("operator_pair_id must be an opaque, non-empty string.")
    check_opaque_non_blank(operator_pair_id, "operator_pair_id")
        
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
    
    # Path equality with descriptor declared paths under normalized DOS paths
    norm_decl_parent = os.path.normcase(os.path.abspath(ordered_parent_decl["expectedConfigPath"])).rstrip("\\/")
    norm_clean_parent = os.path.normcase(os.path.abspath(clean_parent_cfg_path)).rstrip("\\/")
    if norm_decl_parent != norm_clean_parent:
        raise ValueError(
            f"Parent config path does not match descriptor expectedConfigPath: declared '{norm_decl_parent}' vs supplied '{norm_clean_parent}'."
        )
        
    norm_decl_child = os.path.normcase(os.path.abspath(ordered_child_decl["expectedConfigPath"])).rstrip("\\/")
    norm_clean_child = os.path.normcase(os.path.abspath(clean_child_cfg_path)).rstrip("\\/")
    if norm_decl_child != norm_clean_child:
        raise ValueError(
            f"Child config path does not match descriptor expectedConfigPath: declared '{norm_decl_child}' vs supplied '{norm_clean_child}'."
        )
        
    # Read parent and child configs ONCE with handle stat observation
    parent_witness = read_once_file_and_stat(clean_parent_cfg_path)
    child_witness = read_once_file_and_stat(clean_child_cfg_path)
    
    parent_raw_bytes = parent_witness["raw_bytes"]
    parent_raw_sha = parent_witness["sha256"]
    
    child_raw_bytes = child_witness["raw_bytes"]
    child_raw_sha = child_witness["sha256"]
    
    # SHA-256 binding check against descriptor declarations
    if parent_raw_sha != ordered_parent_decl["expectedConfigSha256"]:
        raise ValueError(
            f"Parent config SHA mismatch: declared '{ordered_parent_decl['expectedConfigSha256']}' vs actual '{parent_raw_sha}'."
        )
    if child_raw_sha != ordered_child_decl["expectedConfigSha256"]:
        raise ValueError(
            f"Child config SHA mismatch: declared '{ordered_child_decl['expectedConfigSha256']}' vs actual '{child_raw_sha}'."
        )
        
    # Validate config JSON content against schema and descriptor
    parent_config = validate_config(parent_witness, ordered_parent_decl, "SIMULATION", "parentConfig")
    child_config = validate_config(child_witness, ordered_child_decl, "READ_ONLY", "childConfig")
    
    # Verify and create exclusive output directory
    output_dir_clean = verify_path_ancestry(
        output_dir, is_new_leaf=True, require_dir=True, field_name="output_dir"
    )
    os.mkdir(output_dir_clean)
    
    # Re-verify post-creation
    verify_path_ancestry(output_dir_clean, is_new_leaf=False, require_dir=True, field_name="output_dir")
    
    # Assemble final startup pair bundle (exact top 4 fields in writer order)
    bundle = OrderedDict()
    bundle["schemaVersion"] = SCHEMA_VERSION
    bundle["operatorPairId"] = operator_pair_id
    bundle["parentDeclaration"] = ordered_parent_decl
    bundle["childDeclaration"] = ordered_child_decl
    
    # Serialize bundle: UTF-8 without BOM, compact separators, ensure_ascii=False, no trailing newline
    bundle_bytes = json.dumps(bundle, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    bundle_sha256 = compute_sha256_bytes(bundle_bytes)
    
    staging_bundle_path = os.path.join(output_dir_clean, "operator_startup_pair.staging.json")
    out_bundle_path = os.path.join(output_dir_clean, bundle_filename)
    out_sha_path = os.path.join(output_dir_clean, "operator_startup_pair.sha256.txt")
    out_manifest_path = os.path.join(output_dir_clean, "PROVENANCE_MANIFEST.json")
    
    # 1. Exclusively write staging bundle
    with open(staging_bundle_path, "xb") as f:
        f.write(bundle_bytes)
        
    # 2. Exclusively write sha256 sidecar file (exact 64 uppercase hex chars, no newline)
    with open(out_sha_path, "xb") as f:
        f.write(bundle_sha256.encode('ascii'))
        
    # 3. Exclusively write PROVENANCE_MANIFEST.json linking all witnesses
    manifest = {
        "schemaVersion": "we-operator-startup-pair-provenance/v1",
        "publishedAtUtc": datetime.now(timezone.utc).isoformat(),
        "bundle": {
            "path": os.path.abspath(out_bundle_path),
            "stagingPath": os.path.abspath(staging_bundle_path),
            "sha256": bundle_sha256,
            "bytes": len(bundle_bytes)
        },
        "inputs": {
            "operatorPairId": operator_pair_id,
            "specFile": {
                "path": os.path.abspath(spec_witness["clean_path"]) if spec_witness else "N/A",
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
            "multi_file_transactional_atomicity_unsupported": True,
            "crash_durability_unproven": True,
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
        check_opaque_non_blank(spec["operatorPairId"], "spec 'operatorPairId'")
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
