# -*- coding: utf-8 -*-
import json
import hashlib
import os

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b")
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

if all_ok:
    print("\nALL ARTIFACTS VERIFIED 100% MATCHING!")
else:
    print("\nFAILURES DETECTED!")
