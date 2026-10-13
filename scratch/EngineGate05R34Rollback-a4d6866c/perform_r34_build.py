#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perform_r34_build.py

Pins pre-build input manifest, executes prospective Debug and Release builds
with full subprocess telemetry and raw byte capture, synchronizes 1.6 Assemblies,
extracts PE MVID and CodeView metadata, and emits build outputs.
"""

import os
import sys
import json
import time
import struct
import hashlib
import subprocess
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, "Dispatcher", "A_TASKS", "WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c")
R34_ROOT = os.path.join(WORKSPACE_ROOT, "scratch", "EngineGate05R34Rollback-a4d6866c")
os.makedirs(R34_ROOT, exist_ok=True)

def hash_file(p):
    with open(p, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest().upper(), len(data)

def get_codeview_info(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    idx = data.find(b'RSDS')
    if idx == -1: return None, 0, ""
    guid_bytes = data[idx+4:idx+20]
    d1, d2, d3 = struct.unpack_from('<IHH', guid_bytes)
    d4 = guid_bytes[8:16]
    guid = f'{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}'
    age = struct.unpack_from('<I', data, idx+20)[0]
    pdb_path = data[idx+24:data.find(b'\x00', idx+24)].decode('utf-8', errors='replace')
    return guid, age, pdb_path

def get_mvid_powershell(file_path):
    ps_cmd = f"( [System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes('{file_path}')).ManifestModule.ModuleVersionId ).ToString()"
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
    return res.stdout.strip()

# =========================================================================
# Step 1: Pre-build Input Manifest
# =========================================================================
print("[BUILD] Pinning pre-build input manifest...")

source_files = [
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "WorkerBridge.cs"),
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "EngineHostCensus.cs"),
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "WorkerBridge.csproj")
]

generated_cs_files = [
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "obj", "Debug", "net472", "WorkerBridge.AssemblyInfo.cs"),
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "obj", "Debug", "net472", ".NETFramework,Version=v4.7.2.AssemblyAttributes.cs"),
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "obj", "Release", "net472", "WorkerBridge.AssemblyInfo.cs"),
    os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "obj", "Release", "net472", ".NETFramework,Version=v4.7.2.AssemblyAttributes.cs")
]

# Read actual compile reference observation from R33 task
ref_obs_path = os.path.join(WORKSPACE_ROOT, "Dispatcher", "A_TASKS", "WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5", "MASTER_EXISTING_FULL_COMPILER_REFERENCE_OBSERVATION.json")
with open(ref_obs_path, "r", encoding="utf-8") as f:
    ref_obs = json.load(f)

toolchain_files = [
    r"C:\Program Files\dotnet\dotnet.exe",
    r"C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.exe",
    r"C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll",
    r"C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\VBCSCompiler.exe",
    r"C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\VBCSCompiler.dll",
    r"C:\Program Files\dotnet\sdk\10.0.201\MSBuild.dll"
]

build_input_manifest = {
    "manifest_version": "we-r34-build-input-manifest/v1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c",
    "wp_id": "WP_ENGINE_GATE05_R34_ROLLBACK",
    "envelope": 37,
    "pinned_at": datetime.now(timezone.utc).isoformat(),
    "new_candidates_exist_before_build": False,
    "input_source_files": [
        {"path": p, "bytes": hash_file(p)[1], "sha256": hash_file(p)[0]} for p in source_files
    ],
    "generated_cs_documents": [
        {"path": p, "bytes": hash_file(p)[1], "sha256": hash_file(p)[0]} for p in generated_cs_files if os.path.isfile(p)
    ],
    "actual_resolved_compile_references": ref_obs["files"],
    "toolchain_executables_and_compiler_dlls": [
        {"path": p, "bytes": hash_file(p)[1], "sha256": hash_file(p)[0]} for p in toolchain_files if os.path.isfile(p)
    ],
    "build_commands": [
        {"configuration": "Debug", "command": ["dotnet", "build", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", "-c", "Debug", "--no-restore", "-v:diag"], "cwd": WORKSPACE_ROOT},
        {"configuration": "Release", "command": ["dotnet", "build", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", "-c", "Release", "--no-restore", "-v:diag"], "cwd": WORKSPACE_ROOT}
    ]
}

# Write BUILD_INPUT_MANIFEST.json in task dir and new root
input_manifest_task = os.path.join(TASK_DIR, "BUILD_INPUT_MANIFEST.json")
input_manifest_r34 = os.path.join(R34_ROOT, "BUILD_INPUT_MANIFEST.json")
with open(input_manifest_task, "w", encoding="utf-8") as f:
    json.dump(build_input_manifest, f, indent=2, ensure_ascii=False)
with open(input_manifest_r34, "w", encoding="utf-8") as f:
    json.dump(build_input_manifest, f, indent=2, ensure_ascii=False)
print(f"[BUILD] Saved BUILD_INPUT_MANIFEST.json to {input_manifest_task}")

# =========================================================================
# Step 2: Execute Debug Build
# =========================================================================
print("\n[BUILD] Launching Debug build...")
cmd_debug = ["dotnet", "build", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", "-c", "Debug", "--no-restore", "-v:diag"]
t0_dbg = time.perf_counter()
proc_dbg = subprocess.Popen(cmd_debug, cwd=WORKSPACE_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pid_dbg = proc_dbg.pid
out_dbg_raw, err_dbg_raw = proc_dbg.communicate()
t1_dbg = time.perf_counter()
duration_dbg = t1_dbg - t0_dbg
exit_dbg = proc_dbg.returncode

dbg_out_file = os.path.join(R34_ROOT, "build_debug_stdout.raw.txt")
dbg_err_file = os.path.join(R34_ROOT, "build_debug_stderr.raw.txt")
with open(dbg_out_file, "wb") as f:
    f.write(out_dbg_raw)
with open(dbg_err_file, "wb") as f:
    f.write(err_dbg_raw)

dbg_out_sha, dbg_out_len = hash_file(dbg_out_file)
dbg_err_sha, dbg_err_len = hash_file(dbg_err_file)
print(f"[BUILD] Debug exit code: {exit_dbg}, PID: {pid_dbg}, Duration: {duration_dbg:.4f}s, Out: {dbg_out_len} B, Err: {dbg_err_len} B")
if exit_dbg != 0:
    raise RuntimeError(f"Debug build failed with code {exit_dbg}!\nStderr: {err_dbg_raw.decode('utf-8', errors='replace')}")

# =========================================================================
# Step 3: Execute Release Build
# =========================================================================
print("\n[BUILD] Launching Release build...")
cmd_rel = ["dotnet", "build", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", "-c", "Release", "--no-restore", "-v:diag"]
t0_rel = time.perf_counter()
proc_rel = subprocess.Popen(cmd_rel, cwd=WORKSPACE_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pid_rel = proc_rel.pid
out_rel_raw, err_rel_raw = proc_rel.communicate()
t1_rel = time.perf_counter()
duration_rel = t1_rel - t0_rel
exit_rel = proc_rel.returncode

rel_out_file = os.path.join(R34_ROOT, "build_release_stdout.raw.txt")
rel_err_file = os.path.join(R34_ROOT, "build_release_stderr.raw.txt")
with open(rel_out_file, "wb") as f:
    f.write(out_rel_raw)
with open(rel_err_file, "wb") as f:
    f.write(err_rel_raw)

rel_out_sha, rel_out_len = hash_file(rel_out_file)
rel_err_sha, rel_err_len = hash_file(rel_err_file)
print(f"[BUILD] Release exit code: {exit_rel}, PID: {pid_rel}, Duration: {duration_rel:.4f}s, Out: {rel_out_len} B, Err: {rel_err_len} B")
if exit_rel != 0:
    raise RuntimeError(f"Release build failed with code {exit_rel}!\nStderr: {err_rel_raw.decode('utf-8', errors='replace')}")

# =========================================================================
# Step 4: Synchronize 1.6 Assemblies with Debug
# =========================================================================
debug_dll = os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "bin", "Debug", "net472", "WarEconomy.WorkerBridge.PoC.dll")
debug_pdb = os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "bin", "Debug", "net472", "WarEconomy.WorkerBridge.PoC.pdb")
mod_1_6_dll = os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "1.6", "Assemblies", "WarEconomy.WorkerBridge.PoC.dll")
mod_1_6_pdb = os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "1.6", "Assemblies", "WarEconomy.WorkerBridge.PoC.pdb")

with open(debug_dll, "rb") as f_in, open(mod_1_6_dll, "wb") as f_out:
    f_out.write(f_in.read())
with open(debug_pdb, "rb") as f_in, open(mod_1_6_pdb, "wb") as f_out:
    f_out.write(f_in.read())
print("\n[BUILD] Synchronized 1.6 Assemblies with Debug candidate.")

# Metadata extraction
release_dll = os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "bin", "Release", "net472", "WarEconomy.WorkerBridge.PoC.dll")
release_pdb = os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "bin", "Release", "net472", "WarEconomy.WorkerBridge.PoC.pdb")

dbg_dll_sha, dbg_dll_len = hash_file(debug_dll)
dbg_pdb_sha, dbg_pdb_len = hash_file(debug_pdb)
rel_dll_sha, rel_dll_len = hash_file(release_dll)
rel_pdb_sha, rel_pdb_len = hash_file(release_pdb)
mod_1_6_dll_sha, mod_1_6_dll_len = hash_file(mod_1_6_dll)
mod_1_6_pdb_sha, mod_1_6_pdb_len = hash_file(mod_1_6_pdb)

dbg_mvid = get_mvid_powershell(debug_dll)
rel_mvid = get_mvid_powershell(release_dll)
dbg_cv_guid, dbg_cv_age, dbg_cv_path = get_codeview_info(debug_dll)
rel_cv_guid, rel_cv_age, rel_cv_path = get_codeview_info(release_dll)

print(f"[METADATA] Debug DLL: {dbg_dll_len} B, SHA: {dbg_dll_sha}, MVID: {dbg_mvid}, CV GUID: {dbg_cv_guid}")
print(f"[METADATA] Debug PDB: {dbg_pdb_len} B, SHA: {dbg_pdb_sha}")
print(f"[METADATA] Release DLL: {rel_dll_len} B, SHA: {rel_dll_sha}, MVID: {rel_mvid}, CV GUID: {rel_cv_guid}")
print(f"[METADATA] Release PDB: {rel_pdb_len} B, SHA: {rel_pdb_sha}")

# =========================================================================
# Step 5: Write BUILD_HOST_TOOL_TELEMETRY.json
# =========================================================================
tool_telemetry = {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "dispatch_id": "WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c",
    "wp_id": "WP_ENGINE_GATE05_R34_ROLLBACK",
    "envelope": 37,
    "build_runs": [
        {
            "configuration": "Debug",
            "pid": pid_dbg,
            "exit_code": exit_dbg,
            "duration_seconds": round(duration_dbg, 6),
            "argv": cmd_debug,
            "cwd": WORKSPACE_ROOT,
            "stdout_path": dbg_out_file,
            "stdout_bytes": dbg_out_len,
            "stdout_sha256": dbg_out_sha,
            "stderr_path": dbg_err_file,
            "stderr_bytes": dbg_err_len,
            "stderr_sha256": dbg_err_sha
        },
        {
            "configuration": "Release",
            "pid": pid_rel,
            "exit_code": exit_rel,
            "duration_seconds": round(duration_rel, 6),
            "argv": cmd_rel,
            "cwd": WORKSPACE_ROOT,
            "stdout_path": rel_out_file,
            "stdout_bytes": rel_out_len,
            "stdout_sha256": rel_out_sha,
            "stderr_path": rel_err_file,
            "stderr_bytes": rel_err_len,
            "stderr_sha256": rel_err_sha
        }
    ]
}

with open(os.path.join(R34_ROOT, "BUILD_HOST_TOOL_TELEMETRY.json"), "w", encoding="utf-8") as f:
    json.dump(tool_telemetry, f, indent=2, ensure_ascii=False)
with open(os.path.join(TASK_DIR, "BUILD_HOST_TOOL_TELEMETRY.json"), "w", encoding="utf-8") as f:
    json.dump(tool_telemetry, f, indent=2, ensure_ascii=False)

# =========================================================================
# Step 6: Write ACTUAL_REFERENCE_BINDING.json
# =========================================================================
actual_ref_binding = {
    "manifest_version": "we-r34-actual-reference-binding/v1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c",
    "wp_id": "WP_ENGINE_GATE05_R34_ROLLBACK",
    "envelope": 37,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "project": {
        "path": os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "WorkerBridge.csproj"),
        "sha256": hash_file(os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "WorkerBridge.csproj"))[0],
        "bytes": hash_file(os.path.join(WORKSPACE_ROOT, "scratch", "WorkerBridgeMod", "Source", "WorkerBridge.csproj"))[1]
    },
    "bound_compile_references": ref_obs["files"]
}

with open(os.path.join(TASK_DIR, "ACTUAL_REFERENCE_BINDING.json"), "w", encoding="utf-8") as f:
    json.dump(actual_ref_binding, f, indent=2, ensure_ascii=False)
with open(os.path.join(R34_ROOT, "ACTUAL_REFERENCE_BINDING.json"), "w", encoding="utf-8") as f:
    json.dump(actual_ref_binding, f, indent=2, ensure_ascii=False)

print("\n[BUILD] Pre-build manifest, build execution, telemetry, and reference bindings complete.")
