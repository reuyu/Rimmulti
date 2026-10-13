#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_final_completion_and_index.py
Builds RESULT_INDEX.json, COMPLETION.json, and refreshes OWNED_OUTPUT_MANIFEST.json.
"""
import hashlib
import json
import os
from datetime import datetime, timezone

task_dir = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e"
owned_root = r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R35Publisher-16a25a7e"
docs_dir = r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006"

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
for root, dirs, files in os.walk(owned_root):
    for f in sorted(files):
        if f == "OWNED_OUTPUT_MANIFEST.json":
            continue
        p = os.path.join(root, f)
        info = get_file_info(p)
        rel_path = os.path.relpath(p, owned_root)
        files_manifest.append({
            "relative_path": rel_path,
            "absolute_path": info["path"],
            "bytes": info["size"],
            "sha256": info["sha256"]
        })

owned_manifest_data = {
    "owned_root": os.path.abspath(owned_root),
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "file_count": len(files_manifest),
    "files": files_manifest
}

owned_manifest_path = os.path.join(owned_root, "OWNED_OUTPUT_MANIFEST.json")
with open(owned_manifest_path, "w", encoding="utf-8") as f:
    json.dump(owned_manifest_data, f, indent=2)

print(f"Updated OWNED_OUTPUT_MANIFEST.json with {len(files_manifest)} files.")

# List of all key artifacts
artifacts_to_index = [
    ("korean_report", os.path.join(docs_dir, "A_ENGINE_GATE05_R35_PUBLISHER_REPORT_20261013.md")),
    ("implementation_report", os.path.join(task_dir, "IMPLEMENTATION_REPORT.md")),
    ("release_manifest_docs", r"C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R35_PUBLISHER.json"),
    ("release_manifest_task", os.path.join(task_dir, "RELEASE_MANIFEST.json")),
    ("publisher_identity", os.path.join(task_dir, "PUBLISHER_IDENTITY.json")),
    ("source_scope_diff", os.path.join(task_dir, "SOURCE_SCOPE_DIFF.json")),
    ("config_path_binding_contract", os.path.join(task_dir, "CONFIG_PATH_BINDING_CONTRACT.json")),
    ("exclusive_publication_flow", os.path.join(task_dir, "EXCLUSIVE_PUBLICATION_FLOW.json")),
    ("rejection_source_matrix", os.path.join(task_dir, "REJECTION_SOURCE_MATRIX.json")),
    ("before_after_preservation", os.path.join(task_dir, "BEFORE_AFTER_PRESERVATION.json")),
    ("preservation_before", os.path.join(task_dir, "PRESERVATION_BEFORE.json")),
    ("ack_initial", os.path.join(task_dir, "ACK_INITIAL.json")),
    ("ack", os.path.join(task_dir, "ACK.json")),
    ("ast_input_manifest", os.path.join(owned_root, "AST_INPUT_MANIFEST.json")),
    ("ast_host_tool_proof", os.path.join(owned_root, "AST_HOST_TOOL_PROOF.json")),
    ("ast_stdout_raw", os.path.join(owned_root, "ast_stdout.raw.bin")),
    ("ast_stderr_raw", os.path.join(owned_root, "ast_stderr.raw.bin")),
    ("owned_output_manifest", owned_manifest_path),
    ("modified_publisher_source", r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py")
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
    "dispatch_id": "WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e",
    "wp_id": "WP_ENGINE_GATE05_R35_PUBLISHER",
    "wp_revision": "GATE05-R35-PUBLISHER",
    "envelope": 38,
    "result_id": "WE-A-ENGINE-GATE05-R35-PUBLISHER-RESULT-01",
    "indexed_at_utc": datetime.now(timezone.utc).isoformat(),
    "artifacts_count": len(artifact_entries),
    "artifacts": artifact_entries
}

result_index_path = os.path.join(task_dir, "RESULT_INDEX.json")
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
completion_data = {
    "schema_version": 1,
    "producer": "A",
    "report_kind": "E1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e",
    "wp_id": "WP_ENGINE_GATE05_R35_PUBLISHER",
    "wp_revision": "GATE05-R35-PUBLISHER",
    "envelope": 38,
    "result_id": "WE-A-ENGINE-GATE05-R35-PUBLISHER-RESULT-01",
    "status": "COMPLETED",
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "summary": "WP_ENGINE_GATE05_R35_PUBLISHER / GATE05-R35-PUBLISHER (Envelope 38) plan-only publisher safety hardening and AST syntax verification completed. Single authorized Python publisher (scratch/OperatorStartupPairR29/publish_operator_pair.py) updated to enforce strict R35 safety contracts: (1) Non-overwrite exclusive owned root: output root must not preexist (os.path.lexists check), created via os.mkdir, rejecting relative paths, traversal ('..'), and unsafe reparse points/junctions; (2) Fixed one basename: 'operator_startup_pair.json' only, rejecting custom/traversing filenames; (3) Non-destructive failure policy: zero occurrences of os.remove, os.unlink, rmtree, os.replace, or os.rename; partial outputs on error remain raw forensic evidence without deletion or retry; (4) Exclusive creation & atomic publication: staging bundle, sha sidecar, and provenance manifest written exclusively with mode 'xb'; published atomically into final bundle via os.link on Windows NTFS, retaining staging bundle as immutable audit evidence; (5) Strict config14 and decl7 binding: reads config files ONCE and validates raw SHA-256 against descriptor expectedConfigSha256; enforces declared Windows path equality without mutating opaque declaration fields; enforces strict UTF-8 without BOM and duplicate property rejection; enforces exact 14 properties of OperatorStartupConfig; enforces that validatorArguments is strictly blank in paired mode (fail-closed); enforces role binding (parent SIMULATION, child READ_ONLY). Maintained all 9 Engine baseline files (WorkerBridge.cs, EngineHostCensus.cs, WorkerBridge.csproj, Debug/Release assemblies, and 1.6/Assemblies) 100% bit-exact against baseline. Standalone AST syntax verification executed via ast_checker.py (PID 11312, exit code 0, raw stdout 750 B, raw stderr 0 B, 24 AST body nodes, 10 functions). Zero publisher executions, zero Engine builds, and zero unit/native tests conducted per work package boundaries. Dedicated Server remains final Domain Authority; Foundation HOLD.",
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
        "ZERO_PUBLISHER_EXECUTIONS: publish_operator_pair.py was not imported, executed, or invoked with test arguments per R35 work package boundaries; independent normal publication testing is reserved for Sol.",
        "ZERO_ENGINE_BUILDS: All 9 Engine baseline files remain bit-exact and immutable; no compile or C# project modification was performed.",
        "ZERO_NATIVE_EXECUTION: In-engine, game runtime, native execution, Awake event loops, and operator promotion were strictly prohibited and not executed.",
        "DEDICATED_SERVER_AUTHORITY: Dedicated Server remains final Domain Authority; Engine/Client produces bounded simulation proposals.",
        "STEAM_INSTALLED_INCIDENT_OPEN: Steam installed DLL discrepancy against archive baseline remains an UNKNOWN OPEN INCIDENT, preserved unmodified.",
        "FOUNDATION_HOLD: Foundation remains HOLD pending Pipeline independent E2 PASS."
    ],
    "artifacts": artifact_entries
}

completion_path = os.path.join(task_dir, "COMPLETION.json")
with open(completion_path, "w", encoding="utf-8") as f:
    json.dump(completion_data, f, indent=2)

print(f"Created COMPLETION.json at {completion_path}")
