import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

WORKSPACE = r"C:\Users\user\Desktop\RimMulti"

def hash_file(full_path):
    if not os.path.exists(full_path):
        raise FileNotFoundError(full_path)
    with open(full_path, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest().upper(), len(data)

def get_mvid(full_path):
    cmd = [
        "powershell", "-NoProfile", "-Command",
        f"[System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes('{full_path}')).ManifestModule.ModuleVersionId.ToString()"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

artifacts_defs = [
    ("implementation_report", r"docs\POC_EngineHost_Content_Codec_Gate05_R6.md"),
    ("release_manifest", r"docs\RELEASE_MANIFEST_ENGINE_GATE05_R6_CODEC_CONTRACT.json"),
    ("harness", r"scratch\EngineGate05R6CodecContract\Harness\Program.cs"),
    ("harness_project", r"scratch\EngineGate05R6CodecContract\Harness\Gate05R6CodecRunner.csproj"),
    ("results", r"scratch\EngineGate05R6CodecContract\results.json"),
    ("raw_evidence", r"scratch\EngineGate05R6CodecContract\raw_console.txt"),
    ("candidate_binary", r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
    ("pdb", r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    ("alternate_binary", r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"),
    ("alternate_pdb", r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    ("deployed_assembly", r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
    ("deployed_pdb", r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
    ("source", r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
    ("source_census", r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
    ("source_csproj", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
    ("pre_run_manifest", r"scratch\EngineGate05R6CodecContract\CANDIDATE_PRE_RUN_MANIFEST.json"),
    ("engine_freeze_before", r"scratch\EngineGate05R6CodecContract\ENGINE_FREEZE_BEFORE.json"),
    ("engine_freeze_after", r"scratch\EngineGate05R6CodecContract\ENGINE_FREEZE_AFTER.json"),
    ("work_log", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe\A_WORK_LOG.md"),
    ("recovery_ack", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe\A_RECOVERY_ACK.md"),
    ("ack_json", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe\ACK.json")
]

artifact_entries = []
for role, rel in artifacts_defs:
    full = os.path.join(WORKSPACE, rel)
    sha, size = hash_file(full)
    entry = {
        "role": role,
        "path": full,
        "sha256": sha,
        "size": size
    }
    if role in ("candidate_binary", "alternate_binary", "deployed_assembly"):
        entry["mvid"] = get_mvid(full)
    artifact_entries.append(entry)

completion_doc = {
    "schema_version": 1,
    "producer": "A",
    "report_kind": "E1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe",
    "wp_id": "WP_ENGINE_GATE05_R6_CODEC_CONTRACT",
    "wp_revision": "GATE05-R6-CODEC-CONTRACT",
    "result_id": "WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-RESULT-01",
    "status": "COMPLETED",
    "completed_at": "2026-10-08T19:40:00+09:00",
    "summary": "WP_ENGINE_GATE05_R6_CODEC_CONTRACT / GATE05-R6-CODEC-CONTRACT narrow technical repair completed and developer E1 verification recorded. Successfully implemented MD-130 explicit supported content contract and disposition specification for all 8 Def families and metadata, established canonical sorting boundary with strict preservation of material sequence (activeMods loadOrder, verbs, stages, comps) and multiplicity, implemented fail-closed collector mapping for unobserved required materials with explicit out-of-scope disclosure for mod patch/setting raw identity, extracted and bound independent PE MVIDs for Debug (b3481641-...) and Release (354737fd-...) candidates, preserved immutable source baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72547 bytes SHA F3C4F865...), and executed pure normal DTO codec and contract unit harness (14/14 PASS) without runtime initialization anomalies. All historical lineages and installed incident preserved as OPEN.",
    "e1_verdict": "IMPLEMENTATION_PARTIAL",
    "limitations": [
        "NATIVE_UNTESTED: In-engine and game runtime execution was strictly prohibited under WP_ENGINE_GATE05_R6_CODEC_CONTRACT. Verification was conducted via isolated normal production codec and contract unit harness (14/14 PASS).",
        "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
        "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Gate05 defects, Engine002/006, Pipeline007, and Foundation HOLD remain OPEN pending Master disposition and independent Sol QA review."
    ],
    "artifacts": artifact_entries
}

out_target = os.path.join(WORKSPACE, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe\COMPLETION.json")
with open(out_target, "w", encoding="utf-8") as f:
    json.dump(completion_doc, f, indent=2)

print(f"Wrote {out_target}")
