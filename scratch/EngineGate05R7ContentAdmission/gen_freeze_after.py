import os
import hashlib
import json
import subprocess
from datetime import datetime, timezone

ws = r"C:\Users\user\Desktop\RimMulti"
out_dir = os.path.join(ws, r"scratch\EngineGate05R7ContentAdmission")

paths = [
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

def get_mvid(p):
    cmd = ["powershell", "-NoProfile", "-Command", f"[System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes('{p}')).ManifestModule.ModuleVersionId.ToString()"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

items = {}
for rel in paths:
    full = os.path.join(ws, rel)
    data = open(full, "rb").read()
    sha = hashlib.sha256(data).hexdigest().upper()
    entry = {"sha256": sha, "size": len(data)}
    if rel.endswith(".dll"):
        entry["mvid"] = get_mvid(full)
    items[rel] = entry

doc = {
    "schema_version": 1,
    "freeze_time": datetime.now(timezone.utc).isoformat(),
    "dispatch_id": "WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02",
    "phase": "POST_RUN_FREEZE_AFTER",
    "files": items
}

out_file = os.path.join(out_dir, "ENGINE_FREEZE_AFTER.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2)

print(f"Wrote {out_file}")
