#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_r35_artifacts.py
Validates that every single artifact listed in COMPLETION.json exists on disk,
re-computes SHA-256 and byte sizes, and confirms 100% bit-exact consistency.
"""
import hashlib
import json
import os
import sys

completion_path = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e\COMPLETION.json"

with open(completion_path, "r", encoding="utf-8") as f:
    completion = json.load(f)

errors = []
verified_count = 0

print(f"Verifying {len(completion['artifacts'])} artifacts from COMPLETION.json...")

for item in completion["artifacts"]:
    role = item["role"]
    path = item["path"]
    expected_sha = item["sha256"]
    expected_size = item["size"]

    if not os.path.isfile(path):
        errors.append(f"MISSING FILE: [{role}] {path}")
        continue

    with open(path, "rb") as f:
        data = f.read()

    actual_sha = hashlib.sha256(data).hexdigest().upper()
    actual_size = len(data)

    if actual_sha != expected_sha:
        errors.append(f"SHA MISMATCH: [{role}] {path}: expected {expected_sha}, got {actual_sha}")
    elif actual_size != expected_size:
        errors.append(f"SIZE MISMATCH: [{role}] {path}: expected {expected_size}, got {actual_size}")
    else:
        verified_count += 1
        print(f"  OK: [{role}] {os.path.basename(path)} ({actual_size} B, SHA {actual_sha[:16]}...)")

if errors:
    print(f"\nFAILED with {len(errors)} errors:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print(f"\nALL {verified_count} ARTIFACTS VERIFIED SUCCESSFULLY WITH ZERO ERRORS!")
    sys.exit(0)
