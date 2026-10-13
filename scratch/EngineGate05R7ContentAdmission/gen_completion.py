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
    ("implementation_report", r"docs\POC_EngineHost_Content_Codec_Gate05_R7.md"),
    ("release_manifest", r"docs\RELEASE_MANIFEST_ENGINE_GATE05_R7_CONTENT_ADMISSION.json"),
    ("harness", r"scratch\EngineGate05R7ContentAdmission\Harness\Program.cs"),
    ("harness_project", r"scratch\EngineGate05R7ContentAdmission\Harness\Gate05R7ContentRunner.csproj"),
    ("results", r"scratch\EngineGate05R7ContentAdmission\results.json"),
    ("raw_evidence", r"scratch\EngineGate05R7ContentAdmission\raw_console.txt"),
    ("candidate_binary", r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
    ("pdb", r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    ("alternate_binary", r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"),
    ("alternate_pdb", r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    ("deployed_assembly", r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
    ("deployed_pdb", r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
    ("source", r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
    ("source_census", r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
    ("source_csproj", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
    ("pre_run_manifest", r"scratch\EngineGate05R7ContentAdmission\CANDIDATE_PRE_RUN_MANIFEST.json"),
    ("engine_freeze_before", r"scratch\EngineGate05R7ContentAdmission\ENGINE_FREEZE_BEFORE.json"),
    ("engine_freeze_after", r"scratch\EngineGate05R7ContentAdmission\ENGINE_FREEZE_AFTER.json"),
    ("work_log", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02\A_WORK_LOG.md"),
    ("recovery_ack", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02\A_RECOVERY_ACK.md"),
    ("ack_json", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02\ACK.json")
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
    "dispatch_id": "WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02",
    "wp_id": "WP_ENGINE_GATE05_R7_CONTENT_ADMISSION",
    "wp_revision": "GATE05-R7-CONTENT-ADMISSION",
    "result_id": "WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-RESULT-01",
    "status": "COMPLETED",
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "summary": "WP_ENGINE_GATE05_R7_CONTENT_ADMISSION / GATE05-R7-CONTENT-ADMISSION narrow technical correction completed and developer E1 verification recorded. Successfully wired ValidateContract into ComputeActualContentProfileManifest and ComputeActualContentProfileFingerprint to enforce explicit supported content contract before admission and fingerprint generation. Implemented TryAdmitManifest for external callers. Enforced executable coverage and disposition policies for all 8 Def families, DLCs, active mods, and loaded assemblies without silent child omission or sentinel abbreviation. Bound executable patch/settings exclusion status (contentContractVersion ADR-006B-v5-R7, supportedCoverageProfile, modPatchSupportStatus) into manifest and contract validation. Implemented deterministic multi-key tie-breaking (loadedAssemblies, stats, costList) and formalized in-place mutation contract for CanonicalNormalize. Preserved immutable source baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72547 bytes SHA F3C4F865...). Executed positive pure normal DTO/helper unit harness (14/14 PASS) without cache calls, adverse execution, or runtime initialization anomalies. Bound actual PE MVIDs for Debug (bdf94567-...) and Release (db8d92c1-...) candidates. All historical lineages and installed incident preserved as OPEN.",
    "e1_verdict": "IMPLEMENTATION_PARTIAL",
    "limitations": [
        "NATIVE_UNTESTED: In-engine and game runtime execution was strictly prohibited under WP_ENGINE_GATE05_R7_CONTENT_ADMISSION. Verification was conducted via isolated positive pure normal DTO and helper unit harness (14/14 PASS).",
        "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
        "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Gate05 defects, Engine002/006, Pipeline007, and Foundation HOLD remain OPEN pending Master disposition and independent Sol QA review."
    ],
    "artifacts": artifact_entries
}

out_target = os.path.join(WORKSPACE, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02\COMPLETION.json")
with open(out_target, "w", encoding="utf-8") as f:
    json.dump(completion_doc, f, indent=2)

print(f"Wrote {out_target}")
