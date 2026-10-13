import hashlib
import os
import subprocess

ws = r"C:\Users\user\Desktop\RimMulti"

def hash_file(rel):
    full = os.path.join(ws, rel)
    data = open(full, "rb").read()
    return hashlib.sha256(data).hexdigest().upper(), len(data)

def get_mvid(rel):
    full = os.path.join(ws, rel)
    cmd = ["powershell", "-NoProfile", "-Command", f"[System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes('{full}')).ManifestModule.ModuleVersionId.ToString()"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

debug_dll_sha, debug_dll_sz = hash_file(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")
debug_pdb_sha, debug_pdb_sz = hash_file(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb")
debug_mvid = get_mvid(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")

release_dll_sha, release_dll_sz = hash_file(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll")
release_pdb_sha, release_pdb_sz = hash_file(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb")
release_mvid = get_mvid(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll")

print("=== DEBUG CANDIDATE ===")
print(f"DLL: size={debug_dll_sz}, SHA={debug_dll_sha}, MVID={debug_mvid}")
print(f"PDB: size={debug_pdb_sz}, SHA={debug_pdb_sha}")

print("=== RELEASE CANDIDATE ===")
print(f"DLL: size={release_dll_sz}, SHA={release_dll_sha}, MVID={release_mvid}")
print(f"PDB: size={release_pdb_sz}, SHA={release_pdb_sha}")
