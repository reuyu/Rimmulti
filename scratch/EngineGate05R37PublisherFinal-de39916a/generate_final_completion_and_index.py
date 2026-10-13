#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_final_completion_and_index.py
Builds OWNED_OUTPUT_MANIFEST.json, RESULT_INDEX.json, and COMPLETION.json for R37.
"""
import hashlib
import json
import os
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a")
OWNED_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R37PublisherFinal-de39916a")
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
    ("korean_report", os.path.join(HANDOFF_DIR, "A_ENGINE_GATE05_R37_PUBLISHER_FINAL_REPORT_20261014.md")),
    ("implementation_report", os.path.join(TASK_DIR, "IMPLEMENTATION_REPORT.md")),
    ("release_manifest_docs", os.path.join(DOCS_DIR, "RELEASE_MANIFEST_ENGINE_GATE05_R37_PUBLISHER_FINAL.json")),
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
    "dispatch_id": "WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a",
    "wp_id": "WP_ENGINE_GATE05_R37_PUBLISHER_FINAL",
    "wp_revision": "GATE05-R37-PUBLISHER-FINAL",
    "envelope": 40,
    "result_id": "WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-RESULT-01",
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
    "WP_ENGINE_GATE05_R37_PUBLISHER_FINAL / GATE05-R37-PUBLISHER-FINAL (Envelope 40) "
    "publisher final bounded repair and AST syntax verification completed. Single authorized Python publisher "
    "(scratch/OperatorStartupPairR29/publish_operator_pair.py) updated to enforce all 8 R37 contract requirements: "
    "(1) ConfigId and Capability Boundary binding: rawConfigId matches untrimmed expectedConfigId and trimmed configId "
    "matches SAME untrimmed expectedConfigId; raw capabilityBoundary matches cloned-trimmed descriptor case-insensitively "
    "before snapshot (raw cap is never stripped); bounded structural ASCII strip/upper helpers reject non-ASCII whitespace; "
    "original descriptor role and capability boundary padding and lowercase preserved verbatim in output bundle; "
    "(2) Timestamp ASCII fidelity: ISO 8601 UTC timestamp regex strictly using ASCII digits [0-9] with full consumption; "
    "calendar and time validity enforced for years 1..9999, months 1..12, days 1..max_days with leap years, hours/mins/secs 0..59; "
    "exact raw fractional digits preserved without rounding to 6 digits or inventing .0000000Z; "
    "(3) Real filesystem ancestry guard: direct nofollow lstat on drive root (C:\\) and every actual component without "
    "lexists/isdir/isfile error-masking; fails closed on inspection errors; reparse points (0x400) and symlinks rejected; "
    "new output leaf catches ONLY FileNotFoundError; post-mkdir and pre-link rechecks enforced; "
    "(4) Common readonce helper: read_once_file_and_stat captures prior lstat, handle fstat, raw bytes, and SHA-256 for spec "
    "and configs, linked directly into PROVENANCE_MANIFEST.json; protected owner assumptions, non-hostile concurrent writer "
    "assumptions, hardlink mutability, and TOCTOU limits explicitly documented; "
    "(5) Strict CLI and non-destructive failure policy: strict --spec <spec_path> CLI mode with exact argc 3 and closed 6 required keys; "
    "exclusive creation via os.mkdir and mode 'xb'; atomic directory entry creation via os.link; zero destructive cleanups "
    "(os.remove, unlink, rmtree, replace, rename, 'wb' all 0); partial outputs preserved for forensic analysis; "
    "(6) Original six normal literal compatibility: hash-linked to all 6 case IDs in ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json "
    "and NORMAL_PUBLISHER_EXPECTATION_ORACLE.json; raw UTC timestamps, opaque strings, and padded declarations preserved; "
    "(7) Packaging prospective and AST telemetry: pre-pinned AST_INPUT_MANIFEST.json, isolated ast_checker.py child execution "
    "(PID 15208, exit code 0, raw stdout 3022 B, raw stderr 0 B, verdict SYNTAX_PASS, 36 body nodes, 16 functions); "
    "(8) Submission scope and immutability: all 9 Engine baseline files independently verified 100% bit-exact (0 builds); "
    "zero publisher runtime executions, zero native/unit test executions, zero 1.7 migrations. Dedicated Server remains final "
    "Domain Authority; Foundation HOLD."
)

completion_data = {
    "schema_version": 1,
    "producer": "A",
    "report_kind": "E1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a",
    "wp_id": "WP_ENGINE_GATE05_R37_PUBLISHER_FINAL",
    "wp_revision": "GATE05-R37-PUBLISHER-FINAL",
    "envelope": 40,
    "result_id": "WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-RESULT-01",
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
        "ZERO_PUBLISHER_EXECUTIONS: publish_operator_pair.py was not imported, executed, or invoked with test arguments per R37 work package boundaries; independent normal publication testing is reserved for Sol.",
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
