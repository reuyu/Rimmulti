#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_final_completion_and_index.py
Builds OWNED_OUTPUT_MANIFEST.json, RESULT_INDEX.json, and COMPLETION.json for R36.
"""
import hashlib
import json
import os
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b")
OWNED_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R36PublisherContract-d2d6556b")
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
    ("korean_report", os.path.join(HANDOFF_DIR, "A_ENGINE_GATE05_R36_PUBLISHER_CONTRACT_REPORT_20261013.md")),
    ("implementation_report", os.path.join(TASK_DIR, "IMPLEMENTATION_REPORT.md")),
    ("release_manifest_docs", os.path.join(DOCS_DIR, "RELEASE_MANIFEST_ENGINE_GATE05_R36_PUBLISHER_CONTRACT.json")),
    ("release_manifest_task", os.path.join(TASK_DIR, "RELEASE_MANIFEST.json")),
    ("publisher_identity", os.path.join(TASK_DIR, "PUBLISHER_IDENTITY.json")),
    ("source_scope_diff", os.path.join(TASK_DIR, "SOURCE_SCOPE_DIFF.json")),
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
    "dispatch_id": "WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b",
    "wp_id": "WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT",
    "wp_revision": "GATE05-R36-PUBLISHER-CONTRACT",
    "envelope": 39,
    "result_id": "WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-RESULT-01",
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
    "WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT / GATE05-R36-PUBLISHER-CONTRACT (Envelope 39) "
    "publisher safety contract hardening and AST syntax verification completed. Single authorized Python publisher "
    "(scratch/OperatorStartupPairR29/publish_operator_pair.py) updated to enforce strict R36 contract requirements: "
    "(1) Strict schemaVersion == 'WE-OPERATOR-BOOTSTRAP-V1' requirement; "
    "(2) Exact raw role matching ('SIMULATION' parent, 'READ_ONLY' child) without strip or case normalization; "
    "(3) ConfigId non-blank requirement, raw ordinal match, and snapshot-trimmed ordinal match with descriptor; "
    "(4) Descriptor expectedConfigSha256 strictly 64 ASCII hex characters without padding or whitespace; "
    "(5) Fully-qualified local DOS path lexical validations, rejecting UNC/device/network paths, traversal ('..'), ADS colons, "
    "control characters, and reserved DOS device names; enforcing that worker and validator UserData directories normalize to distinct directories; "
    "(6) expectedContentProfileFingerprint non-blank string requirement (not restricted to 64 hex characters); "
    "(7) expectedPackagePolicyDeclaration validation admitting string or integer revisions with explicit boolean exclusion (not isinstance(val, bool)), "
    "and preserving package ID ordering without mandating constant schema or package uniqueness; "
    "(8) issuedAtUtc valid Gregorian UTC ISO 8601 validation preserving exact raw 1..7 fractional second digits without rounding or truncation to 6 digits; "
    "(9) Reusable whole-ancestry guard (verify_path_ancestry) verifying all existing ancestor directories via os.lstat without following symlinks/junctions, "
    "rejecting reparse points (0x400) and failing closed on inspection errors; "
    "(10) Strict CLI invocation restricted to '--spec <spec_path>' with exact argc 3 and closed 6 required keys + optional bundleFilename fixed to 'operator_startup_pair.json'. "
    "Maintained all 9 Engine baseline files (WorkerBridge.cs, EngineHostCensus.cs, WorkerBridge.csproj, Debug/Release assemblies, and 1.6/Assemblies) "
    "100% bit-exact against baseline (0 builds). Standalone AST syntax verification executed via ast_checker.py (PID 19052, exit code 0, raw stdout 861 B, "
    "raw stderr 0 B, 25 AST body statements, 13 functions). Zero publisher runtime executions, zero Engine builds, zero unit/native tests conducted, "
    "and zero 1.7 migrations per work package boundaries. Dedicated Server remains final Domain Authority; Foundation HOLD."
)

completion_data = {
    "schema_version": 1,
    "producer": "A",
    "report_kind": "E1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b",
    "wp_id": "WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT",
    "wp_revision": "GATE05-R36-PUBLISHER-CONTRACT",
    "envelope": 39,
    "result_id": "WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-RESULT-01",
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
        "ZERO_PUBLISHER_EXECUTIONS: publish_operator_pair.py was not imported, executed, or invoked with test arguments per R36 work package boundaries; independent normal publication testing is reserved for Sol.",
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
