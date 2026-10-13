import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

WORKSPACE = r"C:\Users\user\Desktop\RimMulti"

def hash_file(rel):
    full = os.path.join(WORKSPACE, rel.replace("/", "\\"))
    data = open(full, "rb").read()
    return hashlib.sha256(data).hexdigest().upper(), len(data)

def get_mvid(full_path):
    cmd = [
        "powershell", "-NoProfile", "-Command",
        f"[System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes('{full_path}')).ManifestModule.ModuleVersionId.ToString()"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

debug_dll_rel = r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
debug_pdb_rel = r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
debug_dll_sha, debug_dll_sz = hash_file(debug_dll_rel)
debug_pdb_sha, debug_pdb_sz = hash_file(debug_pdb_rel)
debug_mvid = get_mvid(os.path.join(WORKSPACE, debug_dll_rel))

release_dll_rel = r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
release_pdb_rel = r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
release_dll_sha, release_dll_sz = hash_file(release_dll_rel)
release_pdb_sha, release_pdb_sz = hash_file(release_pdb_rel)
release_mvid = get_mvid(os.path.join(WORKSPACE, release_dll_rel))

deployed_dll_rel = r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"
deployed_pdb_rel = r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
dep_dll_sha, dep_dll_sz = hash_file(deployed_dll_rel)
dep_pdb_sha, dep_pdb_sz = hash_file(deployed_pdb_rel)

wb_cs_sha, wb_cs_sz = hash_file(r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs")
census_cs_sha, census_cs_sz = hash_file(r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs")
csproj_sha, csproj_sz = hash_file(r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj")

census_data = open(os.path.join(WORKSPACE, r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"), "rb").read()
prefix = census_data[:72547]
prefix_sha = hashlib.sha256(prefix).hexdigest().upper()

sdk_ver = subprocess.run(["dotnet", "--version"], capture_output=True, text=True).stdout.strip()

pre_run_manifest = {
    "schema_version": 1,
    "run_id": "RUN_GATE05_R7_CONTENT_ADMISSION_20261008_01",
    "dispatch_id": "WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02",
    "wp_id": "WP_ENGINE_GATE05_R7_CONTENT_ADMISSION",
    "wp_revision": "GATE05-R7-CONTENT-ADMISSION",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "selected_candidate": {
        "role": "candidate_binary",
        "path": os.path.join(WORKSPACE, debug_dll_rel),
        "sha256": debug_dll_sha,
        "size": debug_dll_sz,
        "mvid": debug_mvid,
        "matching_pdb": {
            "path": os.path.join(WORKSPACE, debug_pdb_rel),
            "sha256": debug_pdb_sha,
            "size": debug_pdb_sz
        }
    },
    "alternate_release_candidate": {
        "role": "alternate_binary",
        "path": os.path.join(WORKSPACE, release_dll_rel),
        "sha256": release_dll_sha,
        "size": release_dll_sz,
        "mvid": release_mvid,
        "matching_pdb": {
            "path": os.path.join(WORKSPACE, release_pdb_rel),
            "sha256": release_pdb_sha,
            "size": release_pdb_sz
        }
    },
    "deployed_mod_assemblies": {
        "dll_path": os.path.join(WORKSPACE, deployed_dll_rel),
        "dll_sha256": dep_dll_sha,
        "dll_size": dep_dll_sz,
        "pdb_path": os.path.join(WORKSPACE, deployed_pdb_rel),
        "pdb_sha256": dep_pdb_sha,
        "pdb_size": dep_pdb_sz
    },
    "sources": [
        {
            "path": os.path.join(WORKSPACE, r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
            "sha256": wb_cs_sha,
            "size": wb_cs_sz
        },
        {
            "path": os.path.join(WORKSPACE, r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
            "sha256": census_cs_sha,
            "size": census_cs_sz,
            "prefix_marker": "    public static class ContentProfileProvider",
            "prefix_length": 72547,
            "prefix_sha256": prefix_sha
        },
        {
            "path": os.path.join(WORKSPACE, r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
            "sha256": csproj_sha,
            "size": csproj_sz
        }
    ],
    "content_schema_profile": {
        "manifest_schema_version": "ADR-006B-v5",
        "content_contract_version": "ADR-006B-v5-R7",
        "supported_coverage_profile": "POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5",
        "mod_patch_support_status": "COUNT_ONLY_EXPLICIT_EXCLUSION_RAW_PATCHES_SETTINGS",
        "capability_flags": [
            "TACTICAL_PROBE_V4",
            "READ_ONLY",
            "SIMULATION",
            "GATE05_R7_CONTENT_ADMISSION",
            "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
        ]
    },
    "runtime_candidate_proof": "NOT_OBSERVED (Positive pure normal DTO/helper controls executed under Developer E1; game/native execution prohibited per WP_ENGINE_GATE05_R7_CONTENT_ADMISSION)",
    "tooling_environment": {
        "dotnet_sdk": sdk_ver,
        "target_framework": "net472",
        "build_command_debug": "dotnet build scratch\\WorkerBridgeMod\\Source\\WorkerBridge.csproj -c Debug",
        "build_command_release": "dotnet build scratch\\WorkerBridgeMod\\Source\\WorkerBridge.csproj -c Release"
    }
}

target = os.path.join(WORKSPACE, r"scratch\EngineGate05R7ContentAdmission\CANDIDATE_PRE_RUN_MANIFEST.json")
with open(target, "w", encoding="utf-8") as f:
    json.dump(pre_run_manifest, f, indent=2)

print(f"Wrote {target}")
