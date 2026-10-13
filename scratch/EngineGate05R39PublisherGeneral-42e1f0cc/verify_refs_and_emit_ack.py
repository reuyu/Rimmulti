#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_refs_and_emit_ack.py
Validates task references and emits ACK_INITIAL.json, ACK.json, and PRESERVATION_BEFORE.json
for Gate05 R39 before any source modifications.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-20261014-DIRECT-42e1f0cc")
OWNED_E1_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R39PublisherGeneral-42e1f0cc")
PUBLISHER_PATH = os.path.join(WORKSPACE_ROOT, r"scratch\OperatorStartupPairR29\publish_operator_pair.py")

DISPATCH_ID = "WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-20261014-DIRECT-42e1f0cc"
WP_ID = "WP_ENGINE_GATE05_R39_PUBLISHER_GENERAL"
WP_REVISION = "GATE05-R39-PUBLISHER-GENERAL"
ENVELOPE = 42

ENGINE_9_FILES = [
    (r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs", 276685, "544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD"),
    (r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs", 170135, "391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1"),
    (r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", 1774, "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052"),
    (r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll", 326144, "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029"),
    (r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb", 79220, "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE"),
    (r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll", 308224, "9CBA7E69210DE90B069F269744F3140C4ADD802FD868AB0E0C71FB0E5F69D106"),
    (r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb", 57776, "F05FE976EB522B6A5FC78338B0C35A8CC5341322BACB4CA6310F6AF3682933F5"),
    (r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll", 326144, "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029"),
    (r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb", 79220, "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE")
]

def compute_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_stats(path):
    sz = os.path.getsize(path)
    sh = compute_sha256(path)
    return sz, sh

def main():
    print("=== STARTING R39 VERIFICATION AND INITIAL ACK EMISSION ===")
    
    # 1. Verify Engine 9 baseline files
    engine_results = []
    all_engine_ok = True
    for rel_path, exp_bytes, exp_sha in ENGINE_9_FILES:
        full_path = os.path.join(WORKSPACE_ROOT, rel_path)
        if not os.path.isfile(full_path):
            print(f"[ERROR] Engine file missing: {full_path}")
            all_engine_ok = False
            continue
        act_bytes, act_sha = get_file_stats(full_path)
        match = (act_bytes == exp_bytes) and (act_sha == exp_sha)
        if not match:
            print(f"[FAIL] Engine mismatch: {rel_path} (bytes {act_bytes} vs {exp_bytes}, sha {act_sha} vs {exp_sha})")
            all_engine_ok = False
        else:
            print(f"[PASS] Engine bit-exact: {rel_path}")
        engine_results.append({
            "path": full_path,
            "expected_sha256": exp_sha,
            "expected_bytes": exp_bytes,
            "actual_sha256": act_sha,
            "actual_bytes": act_bytes,
            "bit_exact": match
        })
        
    if not all_engine_ok:
        print("[CRITICAL] Engine baseline mismatch! Aborting.")
        sys.exit(1)
        
    # 2. Verify Publisher before state
    if not os.path.isfile(PUBLISHER_PATH):
        print(f"[ERROR] Publisher source missing: {PUBLISHER_PATH}")
        sys.exit(1)
    pub_bytes, pub_sha = get_file_stats(PUBLISHER_PATH)
    print(f"[PUBLISHER BEFORE] {PUBLISHER_PATH}: {pub_bytes} B, SHA: {pub_sha}")
    
    # Expected before state from R38
    exp_pub_sha = "940CF77220C272D117CDBC278B64858EFB3077267141CC548A0105B47D6E1306"
    exp_pub_bytes = 43666
    if pub_bytes != exp_pub_bytes or pub_sha != exp_pub_sha:
        print(f"[WARN] Publisher before state differs: exp ({exp_pub_bytes}, {exp_pub_sha}) vs act ({pub_bytes}, {pub_sha})")
    else:
        print("[PASS] Publisher matches R38 before baseline.")
        
    # 3. Read reference files and compute exact hashes dynamically
    task_json_path = os.path.join(TASK_DIR, "TASK.json")
    with open(task_json_path, "r", encoding="utf-8") as f:
        task_data = json.load(f)
        
    refs = task_data.get("reference_paths", [])
    ref_witnesses = []
    for r in refs:
        rpath = r["path"]
        if os.path.isfile(rpath):
            sz, sh = get_file_stats(rpath)
            ref_witnesses.append({
                "path": rpath,
                "bytes": sz,
                "sha256": sh,
                "expected_sha256": r.get("sha256")
            })
            print(f"[REF] {os.path.basename(rpath)}: {sz} B, SHA: {sh[:16]}...")
        else:
            print(f"[WARN] Reference missing: {rpath}")
            
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 4. Emit PRESERVATION_BEFORE.json
    preservation_before = {
        "dispatch_id": DISPATCH_ID,
        "wp_id": WP_ID,
        "wp_revision": WP_REVISION,
        "envelope": ENVELOPE,
        "captured_at_utc": now_iso,
        "publisher_before": {
            "path": PUBLISHER_PATH,
            "bytes": pub_bytes,
            "sha256": pub_sha
        },
        "all_Engine9_files": engine_results,
        "all_Engine9_bit_exact": all_engine_ok
    }
    pres_path = os.path.join(TASK_DIR, "PRESERVATION_BEFORE.json")
    with open(pres_path, "w", encoding="utf-8") as f:
        json.dump(preservation_before, f, indent=2)
    print(f"[PRESERVED] Emitted PRESERVATION_BEFORE.json: {pres_path}")
    
    # 5. Emit ACK_INITIAL.json and ACK.json
    ack_data = {
        "schema_version": 1,
        "dispatch_id": DISPATCH_ID,
        "wp_id": WP_ID,
        "wp_revision": WP_REVISION,
        "delivery_envelope_revision": ENVELOPE,
        "recipient": "A",
        "status": "ACKNOWLEDGED",
        "acknowledged_at": now_iso,
        "working_state": "IN_PROGRESS",
        "target_file": PUBLISHER_PATH,
        "publisher_before": {
            "path": PUBLISHER_PATH,
            "bytes": pub_bytes,
            "sha256": pub_sha
        },
        "engine9_verified_bit_exact": all_engine_ok,
        "engine9_builds": 0,
        "publisher_runtime_executions": 0,
        "references_verified_count": len(ref_witnesses),
        "commitments": [
            "Single mutable source: scratch/OperatorStartupPairR29/publish_operator_pair.py only.",
            "All 9 Engine baseline files 100% bit-exact (0 builds).",
            "Zero publisher runtime executions, zero native/unit tests, zero 1.7 migrations.",
            "Isolated child AST syntax verification only.",
            "Prior R38 QA PASS will NOT be inherited to new candidate; fresh candidate requires fresh review.",
            "Dedicated Server remains final Domain Authority; Foundation HOLD."
        ]
    }
    
    ack_initial_path = os.path.join(TASK_DIR, "ACK_INITIAL.json")
    with open(ack_initial_path, "w", encoding="utf-8") as f:
        json.dump(ack_data, f, indent=2)
    print(f"[ACK] Emitted ACK_INITIAL.json: {ack_initial_path}")
    
    ack_path = os.path.join(TASK_DIR, "ACK.json")
    with open(ack_path, "w", encoding="utf-8") as f:
        json.dump(ack_data, f, indent=2)
    print(f"[ACK] Emitted ACK.json: {ack_path}")
    
    print("=== R39 INITIAL ACK COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
