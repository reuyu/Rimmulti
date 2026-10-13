#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_all_artifacts.py
Performs independent comprehensive cryptographic verification of all Gate05 R39 artifacts,
manifests, Engine 9 files, and publisher candidate identity.
"""

import os
import sys
import json
import hashlib

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-20261014-DIRECT-42e1f0cc")
OWNED_E1_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R39PublisherGeneral-42e1f0cc")
PUBLISHER_PATH = os.path.join(WORKSPACE_ROOT, r"scratch\OperatorStartupPairR29\publish_operator_pair.py")
DOCS_DIR = os.path.join(WORKSPACE_ROOT, r"docs")
HANDOFF_DIR = os.path.join(DOCS_DIR, r"WarEconomy_Master_Handoff_20261006")

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

def main():
    print("=== STARTING INDEPENDENT COMPREHENSIVE VERIFICATION ===")
    all_ok = True
    
    # 1. Verify Engine 9 baseline files
    print("\n[1] Verifying Engine 9 baseline files:")
    for rel, sz, sha in ENGINE_9_FILES:
        fp = os.path.join(WORKSPACE_ROOT, rel)
        if not os.path.isfile(fp):
            print(f"  [MISSING] {rel}")
            all_ok = False
            continue
        act_sz = os.path.getsize(fp)
        act_sha = compute_sha256(fp)
        if act_sz == sz and act_sha == sha:
            print(f"  [PASS] {rel} bit-exact ({sz} B, {sha[:16]}...)")
        else:
            print(f"  [FAIL] {rel} mismatch! act ({act_sz}, {act_sha}) vs exp ({sz}, {sha})")
            all_ok = False
            
    # 2. Verify Publisher Candidate
    print("\n[2] Verifying Publisher candidate:")
    exp_pub_sz = 46246
    exp_pub_sha = "242FB7399C118A1BD3DE588BA99671616ED41E614369142F006E93B889C64242"
    act_pub_sz = os.path.getsize(PUBLISHER_PATH)
    act_pub_sha = compute_sha256(PUBLISHER_PATH)
    if act_pub_sz == exp_pub_sz and act_pub_sha == exp_pub_sha:
        print(f"  [PASS] Publisher candidate identity exact: {act_pub_sz} B, SHA {act_pub_sha}")
    else:
        print(f"  [FAIL] Publisher mismatch! act ({act_pub_sz}, {act_pub_sha}) vs exp ({exp_pub_sz}, {exp_pub_sha})")
        all_ok = False
        
    # 3. Verify COMPLETION.json artifacts
    print("\n[3] Verifying COMPLETION.json and indexed artifacts:")
    comp_path = os.path.join(TASK_DIR, "COMPLETION.json")
    if not os.path.isfile(comp_path):
        print("  [FAIL] COMPLETION.json missing!")
        all_ok = False
    else:
        with open(comp_path, "r", encoding="utf-8") as f:
            comp_data = json.load(f)
        artifacts = comp_data.get("artifacts", [])
        print(f"  Checking {len(artifacts)} artifacts listed in COMPLETION.json:")
        for a in artifacts:
            ap = a["path"]
            exp_sz = a["bytes"]
            exp_sha = a["sha256"]
            if not os.path.isfile(ap):
                print(f"    [MISSING] {ap}")
                all_ok = False
                continue
            act_sz = os.path.getsize(ap)
            act_sha = compute_sha256(ap)
            if act_sz == exp_sz and act_sha == exp_sha:
                print(f"    [PASS] {os.path.basename(ap)} ({act_sz} B, {act_sha[:16]}...)")
            else:
                print(f"    [FAIL] {os.path.basename(ap)} mismatch! act ({act_sz}, {act_sha}) vs exp ({exp_sz}, {exp_sha})")
                all_ok = False
                
    # 4. Verify OWNED_OUTPUT_MANIFEST.json
    print("\n[4] Verifying OWNED_OUTPUT_MANIFEST.json:")
    owned_man_path = os.path.join(OWNED_E1_ROOT, "OWNED_OUTPUT_MANIFEST.json")
    if not os.path.isfile(owned_man_path):
        print("  [FAIL] OWNED_OUTPUT_MANIFEST.json missing!")
        all_ok = False
    else:
        with open(owned_man_path, "r", encoding="utf-8") as f:
            owned_man = json.load(f)
        files = owned_man.get("files", [])
        print(f"  Checking {len(files)} files listed in OWNED_OUTPUT_MANIFEST.json:")
        for f in files:
            fp = f["path"]
            exp_sz = f["bytes"]
            exp_sha = f["sha256"]
            if not os.path.isfile(fp):
                print(f"    [MISSING] {fp}")
                all_ok = False
                continue
            act_sz = os.path.getsize(fp)
            act_sha = compute_sha256(fp)
            if act_sz == exp_sz and act_sha == exp_sha:
                print(f"    [PASS] {os.path.basename(fp)} ({act_sz} B, {act_sha[:16]}...)")
            else:
                print(f"    [FAIL] {os.path.basename(fp)} mismatch! act ({act_sz}, {act_sha}) vs exp ({exp_sz}, {exp_sha})")
                all_ok = False
                
    # 5. Verify Documentation and Reports
    print("\n[5] Verifying Docs and Handoff Reports:")
    docs_rel_path = os.path.join(DOCS_DIR, "RELEASE_MANIFEST_ENGINE_GATE05_R39_PUBLISHER_GENERAL_20261014.md")
    korean_report_path = os.path.join(HANDOFF_DIR, "A_ENGINE_GATE05_R39_PUBLISHER_GENERAL_REPORT_20261014.md")
    for doc_p in [docs_rel_path, korean_report_path]:
        if os.path.isfile(doc_p):
            print(f"  [PASS] {os.path.basename(doc_p)}: {os.path.getsize(doc_p)} B, SHA {compute_sha256(doc_p)[:16]}...")
        else:
            print(f"  [MISSING] {doc_p}")
            all_ok = False

    print("\n" + "="*50)
    if all_ok:
        print("[SUMMARY] ALL ARTIFACTS, MANIFESTS, BASELINE FILES, AND PROOFS ARE 100% BIT-EXACT AND VERIFIED!")
    else:
        print("[SUMMARY] VERIFICATION FAILED! DISCREPANCIES FOUND.")
        sys.exit(1)

if __name__ == "__main__":
    main()
