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
    "run_id": "RUN_GATE05_R6_CODEC_CONTRACT_20261008_01",
    "dispatch_id": "WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe",
    "wp_id": "WP_ENGINE_GATE05_R6_CODEC_CONTRACT",
    "wp_revision": "GATE05-R6-CODEC-CONTRACT",
    "created_at": "2026-10-08T19:30:00+09:00",
    "selected_candidate": {
        "role": "candidate_binary",
        "path": os.path.abspath(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
        "sha256": file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")["sha256"],
        "size": file_info(r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll")["size"],
        "mvid": "b3481641-2711-4b0e-96dd-db0983c2b689",
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
        "mvid": "354737fd-10a8-4160-8307-3e186c2118e6",
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
        "content_contract_version": "ADR-006B-v5-R6",
        "capability_flags": [
            "TACTICAL_PROBE_V4",
            "READ_ONLY",
            "SIMULATION",
            "GATE05_R6_CODEC_CONTRACT",
            "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
        ]
    },
    "runtime_candidate_proof": "NOT_OBSERVED (Normal pure DTO codec controls executed under Developer E1; game/native execution prohibited per WP_ENGINE_GATE05_R6_CODEC_CONTRACT)",
    "tooling_environment": {
        "dotnet_sdk": "8.0+",
        "target_framework": "net472",
        "build_command_debug": "dotnet build scratch\\WorkerBridgeMod\\Source\\WorkerBridge.csproj -c Debug",
        "build_command_release": "dotnet build scratch\\WorkerBridgeMod\\Source\\WorkerBridge.csproj -c Release"
    }
}

target = r"scratch\EngineGate05R6CodecContract\CANDIDATE_PRE_RUN_MANIFEST.json"
with open(target, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("Wrote", target)
