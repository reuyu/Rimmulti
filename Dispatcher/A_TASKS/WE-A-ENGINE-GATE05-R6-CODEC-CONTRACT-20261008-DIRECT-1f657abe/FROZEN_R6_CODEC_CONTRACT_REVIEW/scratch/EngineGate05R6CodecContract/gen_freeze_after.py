import hashlib
import json
import os
import subprocess

WORKSPACE = r"C:\Users\user\Desktop\RimMulti"

paths_to_hash = [
    r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj",
    r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
    r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb",
]

def hash_file(rel):
    full = os.path.join(WORKSPACE, rel)
    if not os.path.exists(full):
        return None, 0
    with open(full, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest().upper(), len(data)

def get_mvid(full_path):
    cmd = [
        "powershell", "-NoProfile", "-Command",
        f"[System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes('{full_path}')).ManifestModule.ModuleVersionId.ToString()"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

items = {}
for p in paths_to_hash:
    sha, size = hash_file(p)
    entry = {"sha256": sha, "size": size}
    if p.endswith(".dll") and sha:
        entry["mvid"] = get_mvid(os.path.join(WORKSPACE, p))
    items[p] = entry

out_doc = {
    "schema_version": 1,
    "freeze_time": "2026-10-08T19:36:00+09:00",
    "dispatch_id": "WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe",
    "phase": "POST_RUN_FREEZE_AFTER",
    "files": items
}

out_path = os.path.join(WORKSPACE, r"scratch\EngineGate05R6CodecContract\ENGINE_FREEZE_AFTER.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out_doc, f, indent=2)

print(f"Wrote {out_path}")
