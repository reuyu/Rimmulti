# -*- coding: utf-8 -*-
"""
Helper script to generate R36 task manifests and handoff reports.
Located in owned root: scratch/EngineGate05R36PublisherContract-d2d6556b/generate_manifests.py
"""
import os
import sys
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b")
OWNED_DIR = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R36PublisherContract-d2d6556b")
DOCS_DIR = os.path.join(WORKSPACE_ROOT, r"docs")
HANDOFF_DIR = os.path.join(DOCS_DIR, r"WarEconomy_Master_Handoff_20261006")

def compute_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_stats(path):
    size = os.path.getsize(path)
    sha = compute_sha256(path)
    return size, sha

print("Generator script template ready.")
