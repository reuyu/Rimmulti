import os
import hashlib
import json
from datetime import datetime, timezone

def file_info(p):
    with open(p, "rb") as f:
        d = f.read()
    return {
        "path": p.replace("\\", "/"),
        "sha256": hashlib.sha256(d).hexdigest().upper(),
        "bytes": len(d)
    }

manifest = {
    "manifest_version": "1.0",
    "work_package": "WP_ENGINE_GATE05_R5_CODEC",
    "candidate_lineage": "GATE05-R5-CODEC",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "agent_role": "Antigravity A",
    "dispatch_id": "WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046",
    "selected_candidate": {
        "configuration": "Debug",
        "target_framework": "net472",
        "dll_path": "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll",
        "dll_sha256": file_info("scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll")["sha256"],
        "dll_bytes": file_info("scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll")["bytes"],
        "pdb_path": "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb",
        "pdb_sha256": file_info("scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb")["sha256"],
        "pdb_bytes": file_info("scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb")["bytes"],
        "mvid": "0e6b7cca-e02c-4af5-97da-5de31ec7aec3"
    },
    "alternate_candidate": {
        "configuration": "Release",
        "target_framework": "net472",
        "dll_path": "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll",
        "dll_sha256": file_info("scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll")["sha256"],
        "dll_bytes": file_info("scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll")["bytes"],
        "pdb_path": "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb",
        "pdb_sha256": file_info("scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb")["sha256"],
        "pdb_bytes": file_info("scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb")["bytes"],
        "mvid": "0e6b7cca-e02c-4af5-97da-5de31ec7aec3"
    },
    "source_files": [
        file_info("scratch/WorkerBridgeMod/Source/WorkerBridge.cs"),
        {
            **file_info("scratch/WorkerBridgeMod/Source/EngineHostCensus.cs"),
            "prefix_marker": "    public static class ContentProfileProvider",
            "prefix_length": 72547,
            "prefix_sha256": "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
        },
        file_info("scratch/WorkerBridgeMod/Source/WorkerBridge.csproj")
    ],
    "verification_evidence": {
        "runner_project": file_info("scratch/EngineGate05R5Codec/Harness/Gate05R5CodecRunner.csproj"),
        "runner_source": file_info("scratch/EngineGate05R5Codec/Harness/Program.cs"),
        "results_json": file_info("scratch/EngineGate05R5Codec/results.json"),
        "raw_console_log": file_info("scratch/EngineGate05R5Codec/raw_console.txt"),
        "pre_run_manifest": file_info("scratch/EngineGate05R5Codec/CANDIDATE_PRE_RUN_MANIFEST.json"),
        "engine_freeze_before": file_info("scratch/EngineGate05R5Codec/ENGINE_FREEZE_BEFORE.json"),
        "engine_freeze_after": file_info("scratch/EngineGate05R5Codec/ENGINE_FREEZE_AFTER.json"),
        "report_markdown": file_info("docs/POC_EngineHost_Content_Codec_Gate05_R5.md")
    },
    "summary": {
        "total_tests": 12,
        "pass": 12,
        "fail": 0,
        "e1_verdict": "IMPLEMENTATION_PARTIAL",
        "codec_status": "NORMAL_CODEC_VERIFIED",
        "native_observation_status": "NATIVE_UNTESTED (Prohibited under WP_ENGINE_GATE05_R5_CODEC)",
        "installed_incident_status": "UNKNOWN OPEN INCIDENT",
        "disposition_note": "Gate05-R5 successfully implements supported loaded-content manifest as typed versioned canonical records under ADR-006B-v5, eliminating legacy delimiter and sentinel combinations. Defects remain OPEN pending Master disposition and Sol QA independent verification."
    }
}

target = "docs/RELEASE_MANIFEST_ENGINE_GATE05_R5_CODEC.json"
with open(target, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("Wrote", target)
print(json.dumps(manifest, indent=2))
