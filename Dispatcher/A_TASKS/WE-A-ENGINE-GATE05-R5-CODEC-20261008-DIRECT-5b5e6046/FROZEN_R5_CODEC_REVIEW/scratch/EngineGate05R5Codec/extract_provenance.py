import os
import hashlib
import subprocess
import json

def get_file_info(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    return {
        "path": os.path.abspath(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper()
    }

ps_script = """
$dbg = [System.Reflection.Assembly]::LoadFrom((Resolve-Path "scratch\\WorkerBridgeMod\\Source\\bin\\Debug\\net472\\WarEconomy.WorkerBridge.PoC.dll").Path)
$rel = [System.Reflection.Assembly]::LoadFrom((Resolve-Path "scratch\\WorkerBridgeMod\\Source\\bin\\Release\\net472\\WarEconomy.WorkerBridge.PoC.dll").Path)
[PSCustomObject]@{
    DebugMvid = $dbg.ManifestModule.ModuleVersionId.ToString()
    ReleaseMvid = $rel.ManifestModule.ModuleVersionId.ToString()
} | ConvertTo-Json
"""

with open("scratch/EngineGate05R5Codec/get_mvid.ps1", "w", encoding="utf-8") as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/EngineGate05R5Codec/get_mvid.ps1"], capture_output=True, text=True)
print("PowerShell output:", res.stdout)
if res.stderr:
    print("PowerShell error:", res.stderr)

mvids = json.loads(res.stdout) if res.stdout.strip() else {}

info = {
    "selected_debug_candidate": {
        "dll": get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
        "pdb": get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
        "assemblies_dll": get_file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
        "assemblies_pdb": get_file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
        "mvid": mvids.get("DebugMvid", "")
    },
    "alternate_release_candidate": {
        "dll": get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"),
        "pdb": get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
        "mvid": mvids.get("ReleaseMvid", "")
    }
}

print(json.dumps(info, indent=2))
with open(r"scratch\EngineGate05R5Codec\candidate_provenance.json", "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2)
