#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_final_completion_and_index.py
Builds OWNED_OUTPUT_MANIFEST.json, RESULT_INDEX.json, and COMPLETION.json for R38.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e")
OWNED_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R38PublisherBoundaries-10b9846e")
DOCS_DIR = os.path.join(WORKSPACE_ROOT, r"docs")
HANDOFF_DIR = os.path.join(DOCS_DIR, r"WarEconomy_Master_Handoff_20261006")
PUBLISHER_PATH = os.path.join(WORKSPACE_ROOT, r"scratch\OperatorStartupPairR29\publish_operator_pair.py")

def get_file_info(p):
    with open(p, "rb") as f:
        data = f.read()
    return {
        "path": os.path.abspath(p),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper()
    }

# 1. Update OWNED_OUTPUT_MANIFEST.json first (excluding itself)
files_manifest = []
for root, dirs, files in os.walk(OWNED_ROOT):
    for f in sorted(files):
        if f == "OWNED_OUTPUT_MANIFEST.json":
            continue
        p = os.path.join(root, f)
        info = get_file_info(p)
        rel_path = os.path.relpath(p, OWNED_ROOT)
        files_manifest.append({
            "relative_path": rel_path,
            "absolute_path": info["path"],
            "bytes": info["size"],
            "sha256": info["sha256"]
        })

owned_manifest_data = {
    "owned_root": os.path.abspath(OWNED_ROOT),
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "file_count": len(files_manifest),
    "files": files_manifest
}

owned_manifest_path = os.path.join(OWNED_ROOT, "OWNED_OUTPUT_MANIFEST.json")
with open(owned_manifest_path, "w", encoding="utf-8") as f:
    json.dump(owned_manifest_data, f, indent=2)

print(f"Updated OWNED_OUTPUT_MANIFEST.json with {len(files_manifest)} files.")

# List of all key artifacts
artifacts_to_index = [
    ("korean_report", os.path.join(HANDOFF_DIR, "A_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES_REPORT_20261014.md")),
    ("implementation_report", os.path.join(TASK_DIR, "IMPLEMENTATION_REPORT.md")),
    ("release_manifest_docs", os.path.join(DOCS_DIR, "RELEASE_MANIFEST_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES_20261014.md")),
    ("release_manifest_task", os.path.join(TASK_DIR, "RELEASE_MANIFEST.json")),
    ("publisher_identity", os.path.join(TASK_DIR, "PUBLISHER_IDENTITY.json")),
    ("source_scope_diff", os.path.join(TASK_DIR, "SOURCE_SCOPE_DIFF.json")),
    ("requirement8_source_witness", os.path.join(TASK_DIR, "REQUIREMENT8_SOURCE_WITNESS.json")),
    ("supported_domain_config_path_contract", os.path.join(TASK_DIR, "SUPPORTED_DOMAIN_CONFIG_PATH_CONTRACT.json")),
    ("exclusive_publication_flow", os.path.join(TASK_DIR, "EXCLUSIVE_PUBLICATION_FLOW.json")),
    ("rejection_source_matrix", os.path.join(TASK_DIR, "REJECTION_SOURCE_MATRIX.json")),
    ("original_six_literal_compatibility_source_review", os.path.join(TASK_DIR, "ORIGINAL_SIX_LITERAL_COMPATIBILITY_SOURCE_REVIEW.md")),
    ("before_after_preservation", os.path.join(TASK_DIR, "BEFORE_AFTER_PRESERVATION.json")),
    ("preservation_before", os.path.join(TASK_DIR, "PRESERVATION_BEFORE.json")),
    ("ack_initial", os.path.join(TASK_DIR, "ACK_INITIAL.json")),
    ("ack", os.path.join(TASK_DIR, "ACK.json")),
    ("ast_input_manifest", os.path.join(OWNED_ROOT, "AST_INPUT_MANIFEST.json")),
    ("ast_host_tool_proof", os.path.join(OWNED_ROOT, "AST_HOST_TOOL_PROOF.json")),
    ("ast_stdout_raw", os.path.join(OWNED_ROOT, "ast_stdout.raw.bin")),
    ("ast_stderr_raw", os.path.join(OWNED_ROOT, "ast_stderr.raw.bin")),
    ("owned_output_manifest", owned_manifest_path),
    ("modified_publisher_source", PUBLISHER_PATH)
]

artifact_entries = []
for role, p in artifacts_to_index:
    info = get_file_info(p)
    artifact_entries.append({
        "role": role,
        "path": info["path"],
        "sha256": info["sha256"],
        "size": info["size"],
        "mvid": ""
    })

# 2. RESULT_INDEX.json
result_index = {
    "dispatch_id": "WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e",
    "wp_id": "WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES",
    "wp_revision": "GATE05-R38-PUBLISHER-BOUNDARIES",
    "envelope": 41,
    "result_id": "WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-RESULT-01",
    "indexed_at_utc": datetime.now(timezone.utc).isoformat(),
    "artifacts_count": len(artifact_entries),
    "artifacts": artifact_entries
}

result_index_path = os.path.join(TASK_DIR, "RESULT_INDEX.json")
with open(result_index_path, "w", encoding="utf-8") as f:
    json.dump(result_index, f, indent=2)

print(f"Created RESULT_INDEX.json at {result_index_path}")

# Add RESULT_INDEX to artifact_entries for COMPLETION.json
result_index_info = get_file_info(result_index_path)
artifact_entries.append({
    "role": "result_index",
    "path": result_index_info["path"],
    "sha256": result_index_info["sha256"],
    "size": result_index_info["size"],
    "mvid": ""
})

# 3. COMPLETION.json
summary_text = (
    "WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES / GATE05-R38-PUBLISHER-BOUNDARIES (Envelope 41) "
    "publisher boundaries repair and AST syntax verification completed. Single authorized Python publisher "
    "(scratch/OperatorStartupPairR29/publish_operator_pair.py) updated to enforce all 8 R38 contract requirements: "
    "(1) DATE: full consumption regex _ISO_UTC_REGEX.fullmatch(val), ASCII digits [0-9], year 1..9999, calendar/leap/time "
    "validity, raw fractional digits preserved verbatim, Child .0000000Z original preserved across all 6 cases; "
    "(2) REQUIRED ATTRIBUTES: direct nofollow lstat on existing root, ancestor, input, output directory, and leaf components "
    "requires usable Windows st_file_attributes integer (bool excluded), failing closed on missing/None/non-integer; "
    "reparse points (0x400) and symlinks rejected; ONLY exact new output leaf FileNotFoundError permits creation; "
    "(3) STRUCTURAL vs OPAQUE: structural ASCII strip/upper for role/cap tokens rejecting non-ASCII characters; raw config "
    "capabilityBoundary is never trimmed before comparison to cloned-trimmed descriptor; configId raw and snapshot-trimmed "
    "ordinal matching against untrimmed descriptor; opaque NONBLANK strings (originId, launchPlanId, operatorPairId, "
    "fingerprint, policy) retain supplied Unicode content verbatim; original descriptor role/capability padding and lowercase "
    "preserved verbatim in output bundle; "
    "(4) PATH NORMAL FORM: fully-qualified local DOS drive paths only; explicit slash handling rejecting repeated separators "
    "(//, \\\\, \\/, /\\), empty interior segments, and ambiguous aliases; valid drive-root (C:\\) and normal segments (spaces, Omega) "
    "preserved; UNC, device, ADS, traversal, control characters, and reserved DOS device names rejected; "
    "(5) CLAIMS & READ-ONCE: accurate observation witness model under protected local owner assumption; removal of all claims of "
    "immutable staging, atomic sidecars, or crash durability; shared/mutable hardlink contents acknowledged; "
    "(6) ORIGINALS & LINE WITNESS: exact 6 case IDs bound to NORMAL_PUBLISHER_EXPECTATION_ORACLE.json; canonical original Case 5/6 "
    "PairIDs with quotes, Omega, backslash, and padding preserved; Child .0000000Z original preserved; line witness status "
    "SOURCE_IMPLEMENTED_UNVERIFIED with limitations; "
    "(7) ONE OWN AST E1 GRAPH: pre-pinned AST_INPUT_MANIFEST.json, isolated ast_checker.py child execution "
    "(PID 9668, exit code 0, raw stdout 2699 B, raw stderr 0 B, verdict AST_PARSED_SUCCESS, 18 functions, 0 classes); "
    "(8) COMPLETE OWNED INVENTORY: all new helpers in scratch/EngineGate05R38PublisherBoundaries-10b9846e; all 9 Engine baseline files "
    "independently verified 100% bit-exact (0 builds); zero publisher runtime executions, zero native/unit test executions, "
    "zero 1.7 migrations. Dedicated Server remains final Domain Authority; Foundation HOLD."
)

completion_data = {
    "schema_version": 1,
    "producer": "A",
    "report_kind": "E1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e",
    "wp_id": "WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES",
    "wp_revision": "GATE05-R38-PUBLISHER-BOUNDARIES",
    "envelope": 41,
    "result_id": "WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-RESULT-01",
    "status": "COMPLETED",
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "summary": summary_text,
    "e1_verdict": "SOURCE_SYNTAX_ONLY_PUBLICATION_NOT_EXECUTED",
    "test_counts": {
        "total_cases": 0,
        "passed_cases": 0,
        "failed_cases": 0,
        "runtime_publish_executions": 0,
        "engine_build_executions": 0,
        "unit_native_executions": 0
    },
    "limitations": [
        "SOURCE_AND_AST_SYNTAX_ONLY: Verification conducted strictly via source inspection and stdlib ast.parse AST syntax validation (exit code 0). The publisher script was NOT executed.",
        "ZERO_PUBLISHER_EXECUTIONS: publish_operator_pair.py was not imported, executed, or invoked with test arguments per R38 work package boundaries; independent normal publication testing is reserved for Sol.",
        "ZERO_ENGINE_BUILDS: All 9 Engine baseline files remain bit-exact and immutable; no compile or C# project modification was performed.",
        "ZERO_NATIVE_EXECUTION: In-engine, game runtime, native execution, Awake event loops, and operator promotion were strictly prohibited and not executed.",
        "DEDICATED_SERVER_AUTHORITY: Dedicated Server remains final Domain Authority; Engine/Client produces bounded simulation proposals.",
        "STEAM_INSTALLED_INCIDENT_OPEN: Steam installed DLL discrepancy against archive baseline remains an UNKNOWN OPEN INCIDENT, preserved unmodified.",
        "FOUNDATION_HOLD: Foundation remains HOLD pending Pipeline independent E2 PASS."
    ],
    "artifacts": artifact_entries
}

completion_path = os.path.join(TASK_DIR, "COMPLETION.json")
with open(completion_path, "w", encoding="utf-8") as f:
    json.dump(completion_data, f, indent=2)

print(f"Created COMPLETION.json at {completion_path}")
