#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_final_completion_and_index.py
Emits OWNED_OUTPUT_MANIFEST.json, RESULT_INDEX.json, and COMPLETION.json for Gate05 R39.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-20261014-DIRECT-42e1f0cc")
OWNED_E1_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R39PublisherGeneral-42e1f0cc")

DISPATCH_ID = "WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-20261014-DIRECT-42e1f0cc"
RESULT_ID = "WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-RESULT-01"
WP_ID = "WP_ENGINE_GATE05_R39_PUBLISHER_GENERAL"
WP_REVISION = "GATE05-R39-PUBLISHER-GENERAL"
ENVELOPE = 42

def compute_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_stats(path):
    return {
        "path": os.path.abspath(path),
        "bytes": os.path.getsize(path),
        "sha256": compute_sha256(path)
    }

def main():
    print("=== EMITTING OWNED OUTPUT MANIFEST, RESULT INDEX, AND COMPLETION ===")
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Enumerate owned E1 root files
    owned_files = []
    for root, dirs, files in os.walk(OWNED_E1_ROOT):
        for f in sorted(files):
            if f == "OWNED_OUTPUT_MANIFEST.json":
                continue
            fp = os.path.join(root, f)
            st = get_file_stats(fp)
            owned_files.append(st)
            print(f"[OWNED] {os.path.basename(fp)}: {st['bytes']} B, SHA {st['sha256'][:16]}...")
            
    owned_manifest = {
        "schema_version": 1,
        "dispatch_id": DISPATCH_ID,
        "wp_id": WP_ID,
        "envelope": ENVELOPE,
        "captured_at_utc": now_iso,
        "owned_root": os.path.abspath(OWNED_E1_ROOT),
        "total_files_count": len(owned_files),
        "files": owned_files,
        "exclusions": ["OWNED_OUTPUT_MANIFEST.json (self-reference exclusion)"]
    }
    
    owned_manifest_path = os.path.join(OWNED_E1_ROOT, "OWNED_OUTPUT_MANIFEST.json")
    with open(owned_manifest_path, "w", encoding="utf-8") as f:
        json.dump(owned_manifest, f, indent=2)
    print(f"[EMITTED] OWNED_OUTPUT_MANIFEST.json: {owned_manifest_path}")
    
    # 2. Enumerate task directory files for RESULT_INDEX.json
    task_files = []
    for root, dirs, files in os.walk(TASK_DIR):
        for f in sorted(files):
            if f in ("RESULT_INDEX.json", "COMPLETION.json"):
                continue
            fp = os.path.join(root, f)
            st = get_file_stats(fp)
            task_files.append(st)
            print(f"[TASK ARTIFACT] {os.path.basename(fp)}: {st['bytes']} B, SHA {st['sha256'][:16]}...")
            
    result_index = {
        "schema_version": 1,
        "dispatch_id": DISPATCH_ID,
        "result_id": RESULT_ID,
        "wp_id": WP_ID,
        "envelope": ENVELOPE,
        "captured_at_utc": now_iso,
        "task_directory": os.path.abspath(TASK_DIR),
        "total_artifacts_count": len(task_files),
        "artifacts": task_files,
        "exclusions": ["RESULT_INDEX.json", "COMPLETION.json"]
    }
    
    result_index_path = os.path.join(TASK_DIR, "RESULT_INDEX.json")
    with open(result_index_path, "w", encoding="utf-8") as f:
        json.dump(result_index, f, indent=2)
    print(f"[EMITTED] RESULT_INDEX.json: {result_index_path}")
    
    # Also get result_index stats
    res_index_stats = get_file_stats(result_index_path)
    
    # 3. Emit COMPLETION.json
    all_final_artifacts = task_files + [res_index_stats]
    
    completion_data = {
        "schema_version": 1,
        "dispatch_id": DISPATCH_ID,
        "result_id": RESULT_ID,
        "wp_id": WP_ID,
        "wp_revision": WP_REVISION,
        "delivery_envelope_revision": ENVELOPE,
        "recipient": "A",
        "status": "COMPLETED",
        "completed_at_utc": now_iso,
        "e1_verdict": "SOURCE_SYNTAX_ONLY_PUBLICATION_NOT_EXECUTED",
        "runtime_verdict": "NOT_EXECUTED_NOT_RELEASED",
        "single_mutable_source": {
            "path": r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py",
            "bytes": 46246,
            "sha256": "242FB7399C118A1BD3DE588BA99671616ED41E614369142F006E93B889C64242",
            "lines": 955,
            "mvid": "N/A"
        },
        "engine9_builds": 0,
        "all_Engine9_bit_exact": True,
        "publisher_runtime_executions": 0,
        "native_engine_executions": 0,
        "ast_tool_proof": {
            "proof_file": os.path.join(OWNED_E1_ROOT, "AST_HOST_TOOL_PROOF.json"),
            "sha256": compute_sha256(os.path.join(OWNED_E1_ROOT, "AST_HOST_TOOL_PROOF.json")),
            "verdict": "AST_PARSED_SUCCESS",
            "ast_node_count": 4872,
            "function_count": 19,
            "class_count": 0,
            "raw_stderr_bytes": 0
        },
        "artifacts_count": len(all_final_artifacts),
        "artifacts": all_final_artifacts,
        "commitments": {
            "authority": "Dedicated Server remains final Domain Authority; Foundation HOLD.",
            "historical_pass": "Prior R38 normal6 QA PASS is recognized as historical and NOT inherited to this new candidate.",
            "narrow_repair": "Strictly limited to single mutable publisher source and owned E1 metadata; zero Engine builds or candidate runs."
        }
    }
    
    completion_path = os.path.join(TASK_DIR, "COMPLETION.json")
    with open(completion_path, "w", encoding="utf-8") as f:
        json.dump(completion_data, f, indent=2)
    print(f"[EMITTED] COMPLETION.json: {completion_path}")
    print("=== FINAL COMPLETION EMITTED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
