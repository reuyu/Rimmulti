#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_all_artifacts.py
Verifies all R38 task artifacts, owned files, and Engine baseline files.
"""

import os
import sys
import json
import hashlib

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e")
OWNED_DIR = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R38PublisherBoundaries-10b9846e")
DOCS_DIR = os.path.join(WORKSPACE_ROOT, r"docs")
HANDOFF_DIR = os.path.join(DOCS_DIR, r"WarEconomy_Master_Handoff_20261006")
PUBLISHER_PATH = os.path.join(WORKSPACE_ROOT, r"scratch\OperatorStartupPairR29\publish_operator_pair.py")

ENGINE_9 = [
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
    print("=== VERIFYING ALL ARTIFACTS AND BASELINE FILES ===")
    
    # 1. Engine 9
    engine_ok = True
    for rel, exp_sz, exp_sha in ENGINE_9:
        full = os.path.join(WORKSPACE_ROOT, rel)
        sz = os.path.getsize(full)
        sha = compute_sha256(full)
        if sz == exp_sz and sha == exp_sha:
            print(f"[ENGINE MATCH] {rel}")
        else:
            print(f"[ENGINE FAIL] {rel}: sz={sz} (exp {exp_sz}), sha={sha} (exp {exp_sha})")
            engine_ok = False
            
    # 2. Publisher
    pub_sz = os.path.getsize(PUBLISHER_PATH)
    pub_sha = compute_sha256(PUBLISHER_PATH)
    print(f"[PUBLISHER] sz={pub_sz}, sha={pub_sha}")
    
    # 3. Task directory files
    task_files = os.listdir(TASK_DIR)
    print(f"[TASK DIR] {len(task_files)} files in {TASK_DIR}")
    for tf in sorted(task_files):
        p = os.path.join(TASK_DIR, tf)
        print(f"  - {tf} ({os.path.getsize(p)} B, {compute_sha256(p)[:16]}...)")
        
    # 4. Owned directory files
    owned_files = os.listdir(OWNED_DIR)
    print(f"[OWNED DIR] {len(owned_files)} files in {OWNED_DIR}")
    for of in sorted(owned_files):
        p = os.path.join(OWNED_DIR, of)
        print(f"  - {of} ({os.path.getsize(p)} B, {compute_sha256(p)[:16]}...)")
        
    if engine_ok:
        print("=== VERIFICATION COMPLETED: ALL ENGINE 9 MATCH 100% ===")
    else:
        print("=== VERIFICATION FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
