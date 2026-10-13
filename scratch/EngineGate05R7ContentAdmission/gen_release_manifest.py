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

# Candidates
debug_dll_path = "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll"
debug_pdb_path = "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb"
release_dll_path = "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll"
release_pdb_path = "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb"

debug_dll_sha, debug_dll_bytes = hash_file(debug_dll_path)
debug_pdb_sha, debug_pdb_bytes = hash_file(debug_pdb_path)
debug_mvid = get_mvid(os.path.join(WORKSPACE, debug_dll_path.replace("/", "\\")))

release_dll_sha, release_dll_bytes = hash_file(release_dll_path)
release_pdb_sha, release_pdb_bytes = hash_file(release_pdb_path)
release_mvid = get_mvid(os.path.join(WORKSPACE, release_dll_path.replace("/", "\\")))

# Sources
wb_cs_sha, wb_cs_bytes = hash_file("scratch/WorkerBridgeMod/Source/WorkerBridge.cs")
census_cs_sha, census_cs_bytes = hash_file("scratch/WorkerBridgeMod/Source/EngineHostCensus.cs")
csproj_sha, csproj_bytes = hash_file("scratch/WorkerBridgeMod/Source/WorkerBridge.csproj")

# Evidence
runner_proj_sha, runner_proj_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/Harness/Gate05R7ContentRunner.csproj")
runner_src_sha, runner_src_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/Harness/Program.cs")
results_sha, results_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/results.json")
raw_console_sha, raw_console_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/raw_console.txt")
pre_run_sha, pre_run_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/CANDIDATE_PRE_RUN_MANIFEST.json")
freeze_before_sha, freeze_before_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/ENGINE_FREEZE_BEFORE.json")
freeze_after_sha, freeze_after_bytes = hash_file("scratch/EngineGate05R7ContentAdmission/ENGINE_FREEZE_AFTER.json")
report_sha, report_bytes = hash_file("docs/POC_EngineHost_Content_Codec_Gate05_R7.md")

release_manifest = {
    "manifest_version": "1.0",
    "work_package": "WP_ENGINE_GATE05_R7_CONTENT_ADMISSION",
    "candidate_lineage": "GATE05-R7-CONTENT-ADMISSION",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "agent_role": "Antigravity A",
    "dispatch_id": "WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02",
    "selected_candidate": {
        "configuration": "Debug",
        "target_framework": "net472",
        "dll_path": debug_dll_path,
        "dll_sha256": debug_dll_sha,
        "dll_bytes": debug_dll_bytes,
        "pdb_path": debug_pdb_path,
        "pdb_sha256": debug_pdb_sha,
        "pdb_bytes": debug_pdb_bytes,
        "mvid": debug_mvid
    },
    "alternate_candidate": {
        "configuration": "Release",
        "target_framework": "net472",
        "dll_path": release_dll_path,
        "dll_sha256": release_dll_sha,
        "dll_bytes": release_dll_bytes,
        "pdb_path": release_pdb_path,
        "pdb_sha256": release_pdb_sha,
        "pdb_bytes": release_pdb_bytes,
        "mvid": release_mvid
    },
    "source_files": [
        {
            "path": "scratch/WorkerBridgeMod/Source/WorkerBridge.cs",
            "sha256": wb_cs_sha,
            "bytes": wb_cs_bytes
        },
        {
            "path": "scratch/WorkerBridgeMod/Source/EngineHostCensus.cs",
            "sha256": census_cs_sha,
            "bytes": census_cs_bytes,
            "prefix_marker": "    public static class ContentProfileProvider",
            "prefix_length": 72547,
            "prefix_sha256": "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
        },
        {
            "path": "scratch/WorkerBridgeMod/Source/WorkerBridge.csproj",
            "sha256": csproj_sha,
            "bytes": csproj_bytes
        }
    ],
    "verification_evidence": {
        "runner_project": {
            "path": "scratch/EngineGate05R7ContentAdmission/Harness/Gate05R7ContentRunner.csproj",
            "sha256": runner_proj_sha,
            "bytes": runner_proj_bytes
        },
        "runner_source": {
            "path": "scratch/EngineGate05R7ContentAdmission/Harness/Program.cs",
            "sha256": runner_src_sha,
            "bytes": runner_src_bytes
        },
        "results_json": {
            "path": "scratch/EngineGate05R7ContentAdmission/results.json",
            "sha256": results_sha,
            "bytes": results_bytes
        },
        "raw_console_log": {
            "path": "scratch/EngineGate05R7ContentAdmission/raw_console.txt",
            "sha256": raw_console_sha,
            "bytes": raw_console_bytes
        },
        "pre_run_manifest": {
            "path": "scratch/EngineGate05R7ContentAdmission/CANDIDATE_PRE_RUN_MANIFEST.json",
            "sha256": pre_run_sha,
            "bytes": pre_run_bytes
        },
        "engine_freeze_before": {
            "path": "scratch/EngineGate05R7ContentAdmission/ENGINE_FREEZE_BEFORE.json",
            "sha256": freeze_before_sha,
            "bytes": freeze_before_bytes
        },
        "engine_freeze_after": {
            "path": "scratch/EngineGate05R7ContentAdmission/ENGINE_FREEZE_AFTER.json",
            "sha256": freeze_after_sha,
            "bytes": freeze_after_bytes
        },
        "report_markdown": {
            "path": "docs/POC_EngineHost_Content_Codec_Gate05_R7.md",
            "sha256": report_sha,
            "bytes": report_bytes
        }
    },
    "summary": {
        "total_tests": 14,
        "pass": 14,
        "fail": 0,
        "e1_verdict": "IMPLEMENTATION_PARTIAL",
        "codec_status": "POSITIVE_NORMAL_DTO_AND_ADMISSION_VERIFIED",
        "native_observation_status": "NATIVE_UNTESTED (Prohibited under WP_ENGINE_GATE05_R7_CONTENT_ADMISSION)",
        "installed_incident_status": "UNKNOWN OPEN INCIDENT",
        "disposition_note": "Gate05-R7 successfully wires actual content admission validation to ComputeActualContentProfileManifest and ComputeActualContentProfileFingerprint, enforces explicit supported content contract (MD-130), establishes executable patch/settings boundary status, and binds independent PE MVIDs for Debug and Release candidates. Full Gate05 and Foundation remain HOLD pending independent QA and Master governance disposition."
    }
}

target_file = os.path.join(WORKSPACE, r"docs\RELEASE_MANIFEST_ENGINE_GATE05_R7_CONTENT_ADMISSION.json")
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(release_manifest, f, indent=2)

print(f"Wrote {target_file}")
