# -*- coding: utf-8 -*-
"""
verify_all_artifacts.py
Verifies all 22 artifacts listed in COMPLETION.json on disk:
- Checks file existence
- Checks exact byte size match
- Checks exact SHA-256 match
Also checks the 9 Engine baseline files for bit-exactness.
"""
import json
import hashlib
import os

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a")
completion_path = os.path.join(TASK_DIR, "COMPLETION.json")

with open(completion_path, "r", encoding="utf-8") as f:
    completion = json.load(f)

print(f"Verifying {len(completion['artifacts'])} artifacts in COMPLETION.json...")

all_ok = True
for a in completion["artifacts"]:
    p = a["path"]
    expected_sz = a["size"]
    expected_sha = a["sha256"]
    if not os.path.isfile(p):
        print(f"FAIL: File not found: {p}")
        all_ok = False
        continue
    actual_sz = os.path.getsize(p)
    with open(p, "rb") as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest().upper()
    if actual_sz != expected_sz:
        print(f"FAIL: Size mismatch for {p}: expected {expected_sz}, got {actual_sz}")
        all_ok = False
    elif actual_sha != expected_sha:
        print(f"FAIL: SHA mismatch for {p}: expected {expected_sha}, got {actual_sha}")
        all_ok = False
    else:
        print(f"OK: {a['role']} -> {actual_sz} bytes, {actual_sha[:16]}...")

print("\nVerifying 9 Engine baseline files...")
engine_9 = [
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs", 276685, "544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs", 170135, "391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", 1774, "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll", 326144, "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb", 79220, "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll", 308224, "9CBA7E69210DE90B069F269744F3140C4ADD802FD868AB0E0C71FB0E5F69D106"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb", 57776, "F05FE976EB522B6A5FC78338B0C35A8CC5341322BACB4CA6310F6AF3682933F5"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll", 326144, "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb", 79220, "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE")
]

for p, exp_sz, exp_sha in engine_9:
    sz = os.path.getsize(p)
    with open(p, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()
    if sz != exp_sz or sha != exp_sha:
        print(f"FAIL: Engine file mismatch: {p}")
        all_ok = False
    else:
        print(f"OK: Engine file {os.path.basename(p)} -> bit-exact")

if all_ok:
    print("\nALL ARTIFACTS AND ENGINE BASELINE VERIFIED 100% MATCHING!")
else:
    print("\nFAILURES DETECTED!")
