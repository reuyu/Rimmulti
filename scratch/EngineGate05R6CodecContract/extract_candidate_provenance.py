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

ps_script_dbg = """
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path "scratch\\WorkerBridgeMod\\Source\\bin\\Debug\\net472\\WarEconomy.WorkerBridge.PoC.dll").Path)
$asm = [System.Reflection.Assembly]::Load($bytes)
Write-Output $asm.ManifestModule.ModuleVersionId.ToString()
"""

ps_script_rel = """
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path "scratch\\WorkerBridgeMod\\Source\\bin\\Release\\net472\\WarEconomy.WorkerBridge.PoC.dll").Path)
$asm = [System.Reflection.Assembly]::Load($bytes)
Write-Output $asm.ManifestModule.ModuleVersionId.ToString()
"""

with open("scratch/EngineGate05R6CodecContract/get_dbg_mvid.ps1", "w", encoding="utf-8") as f:
    f.write(ps_script_dbg)
with open("scratch/EngineGate05R6CodecContract/get_rel_mvid.ps1", "w", encoding="utf-8") as f:
    f.write(ps_script_rel)

res_dbg = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/EngineGate05R6CodecContract/get_dbg_mvid.ps1"], capture_output=True, text=True)
dbg_mvid = res_dbg.stdout.strip()

res_rel = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/EngineGate05R6CodecContract/get_rel_mvid.ps1"], capture_output=True, text=True)
rel_mvid = res_rel.stdout.strip()

print("Debug MVID:  ", dbg_mvid)
print("Release MVID:", rel_mvid)

dbg_dll = get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")
dbg_pdb = get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb")
rel_dll = get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll")
rel_pdb = get_file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb")
dep_dll = get_file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll")
dep_pdb = get_file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb")

prov = {
    "selected_candidate_debug": {
        "dll": dbg_dll,
        "pdb": dbg_pdb,
        "mvid": dbg_mvid
    },
    "alternate_candidate_release": {
        "dll": rel_dll,
        "pdb": rel_pdb,
        "mvid": rel_mvid
    },
    "deployed_assembly": {
        "dll": dep_dll,
        "pdb": dep_pdb
    }
}

print(json.dumps(prov, indent=2))
with open(r"scratch\EngineGate05R6CodecContract\candidate_provenance.json", "w", encoding="utf-8") as f:
    json.dump(prov, f, indent=2)
