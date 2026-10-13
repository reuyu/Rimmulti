#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_owned_manifest.py
Recursively inventories all files in owned root and computes SHA-256 and byte sizes.
"""
import hashlib
import json
import os
from datetime import datetime, timezone

owned_root = r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R35Publisher-16a25a7e"

files_manifest = []

for root, dirs, files in os.walk(owned_root):
    for f in sorted(files):
        if f == "OWNED_OUTPUT_MANIFEST.json":
            continue
        p = os.path.join(root, f)
        with open(p, "rb") as fp:
            data = fp.read()
        rel_path = os.path.relpath(p, owned_root)
        files_manifest.append({
            "relative_path": rel_path,
            "absolute_path": os.path.abspath(p),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest().upper()
        })

output_manifest = {
    "owned_root": os.path.abspath(owned_root),
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "file_count": len(files_manifest),
    "files": files_manifest
}

out_path = os.path.join(owned_root, "OWNED_OUTPUT_MANIFEST.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output_manifest, f, indent=2)

print(f"Generated OWNED_OUTPUT_MANIFEST.json with {len(files_manifest)} files.")
