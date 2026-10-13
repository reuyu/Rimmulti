import json
import hashlib
import os

def file_info(p):
    with open(p, "rb") as f:
        d = f.read()
    return {
        "path": os.path.abspath(p),
        "sha256": hashlib.sha256(d).hexdigest().upper(),
        "size": len(d)
    }

manifest = {
    "schema_version": 1,
    "run_id": "RUN_GATE05_R5_CODEC_20261008_01",
    "dispatch_id": "WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046",
    "wp_id": "WP_ENGINE_GATE05_R5_CODEC",
    "wp_revision": "GATE05-R5-CODEC",
    "created_at": "2026-10-08T17:55:00+09:00",
    "selected_candidate": {
        "role": "candidate_binary",
        "path": os.path.abspath(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
        "sha256": file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")["sha256"],
        "size": file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")["size"],
        "mvid": "0e6b7cca-e02c-4af5-97da-5de31ec7aec3",
        "matching_pdb": {
            "path": os.path.abspath(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
            "sha256": file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb")["sha256"],
            "size": file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb")["size"]
        }
    },
    "alternate_release_candidate": {
        "role": "alternate_binary",
        "path": os.path.abspath(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"),
        "sha256": file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll")["sha256"],
        "size": file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll")["size"],
        "mvid": "0e6b7cca-e02c-4af5-97da-5de31ec7aec3",
        "matching_pdb": {
            "path": os.path.abspath(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
            "sha256": file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb")["sha256"],
            "size": file_info(r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb")["size"]
        }
    },
    "deployed_mod_assemblies": {
        "dll_path": os.path.abspath(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
        "dll_sha256": file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll")["sha256"],
        "dll_size": file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll")["size"],
        "pdb_path": os.path.abspath(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
        "pdb_sha256": file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb")["sha256"],
        "pdb_size": file_info(r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb")["size"]
    },
    "sources": [
        file_info(r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
        {
            **file_info(r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
            "prefix_marker": "    public static class ContentProfileProvider",
            "prefix_length": 72547,
            "prefix_sha256": "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
        },
        file_info(r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj")
    ],
    "content_schema_profile": {
        "manifest_schema_version": "ADR-006B-v5",
        "capability_flags": [
            "TACTICAL_PROBE_V5",
            "READ_ONLY",
            "SIMULATION",
            "GATE05_R5_TYPED_CANONICAL_CODEC",
            "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
        ]
    },
    "runtime_candidate_proof": "NOT_OBSERVED (Normal codec unit controls executed under Developer E1; game/native execution prohibited per WP_ENGINE_GATE05_R5_CODEC)",
    "tooling_environment": {
        "dotnet_sdk": "8.0+",
        "target_framework": "net472",
        "build_command_debug": "dotnet build scratch\\WorkerBridgeMod\\Source\\WorkerBridge.csproj -c Debug",
        "build_command_release": "dotnet build scratch\\WorkerBridgeMod\\Source\\WorkerBridge.csproj -c Release"
    }
}

target = r"scratch\EngineGate05R5Codec\CANDIDATE_PRE_RUN_MANIFEST.json"
with open(target, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("Wrote", target)
print(json.dumps(manifest, indent=2))
