import os
import hashlib
import json

def get_artifact(role, path, extra=None):
    abs_path = os.path.abspath(path)
    with open(abs_path, "rb") as f:
        data = f.read()
    item = {
        "role": role,
        "path": abs_path,
        "sha256": hashlib.sha256(data).hexdigest().upper(),
        "size": len(data)
    }
    if extra:
        item.update(extra)
    return item

completion = {
    "schema_version": 1,
    "producer": "A",
    "report_kind": "E1",
    "dispatch_id": "WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046",
    "wp_id": "WP_ENGINE_GATE05_R5_CODEC",
    "wp_revision": "GATE05-R5-CODEC",
    "result_id": "WE-A-ENGINE-GATE05-R5-CODEC-RESULT-01",
    "status": "COMPLETED",
    "completed_at": "2026-10-08T18:02:00+09:00",
    "summary": "WP_ENGINE_GATE05_R5_CODEC / GATE05-R5-CODEC narrow codec implementation and developer E1 verification completed. Replaced legacy delimiter/sentinel string combinations with typed versioned canonical records under ADR-006B-v5 for all 8 Def families (ThingDef, HediffDef, JobDef, SkillDef, FactionDef, BiomeDef, WeatherDef, ResearchProjectDef), DLC expansions, active mods, and loaded assemblies. Maintained exact immutability of WorkerBridge.cs (SHA BA28C2...), WorkerBridge.csproj (SHA 571A58...), and EngineHostCensus.cs prefix (Length 72547, SHA F3C4F865...). Validated normal production codec controls 12/12 PASS in isolated unit harness without adverse/security or game execution. Deployed candidate packaging with matching Debug/Release binaries, PDBs, MVID, and pre-run/post-run freeze manifests. Preserved all historical lineages and installed incident as OPEN.",
    "e1_verdict": "IMPLEMENTATION_PARTIAL",
    "limitations": [
        "NATIVE_UNTESTED: In-engine and game runtime execution was strictly prohibited under WP_ENGINE_GATE05_R5_CODEC. Verification was conducted via isolated normal production codec unit harness (12/12 PASS).",
        "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
        "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Gate05 defects, Engine002/006, Pipeline007, and Foundation HOLD remain OPEN pending Master disposition and independent Sol QA review."
    ],
    "artifacts": [
        get_artifact("implementation_report", r"docs\POC_EngineHost_Content_Codec_Gate05_R5.md"),
        get_artifact("release_manifest", r"docs\RELEASE_MANIFEST_ENGINE_GATE05_R5_CODEC.json"),
        get_artifact("harness", r"scratch\EngineGate05R5Codec\Harness\Program.cs"),
        get_artifact("harness_project", r"scratch\EngineGate05R5Codec\Harness\Gate05R5CodecRunner.csproj"),
        get_artifact("results", r"scratch\EngineGate05R5Codec\results.json"),
        get_artifact("raw_evidence", r"scratch\EngineGate05R5Codec\raw_console.txt"),
        get_artifact("candidate_binary", r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll", {"mvid": "0e6b7cca-e02c-4af5-97da-5de31ec7aec3"}),
        get_artifact("pdb", r"scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
        get_artifact("alternate_binary", r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll", {"mvid": "0e6b7cca-e02c-4af5-97da-5de31ec7aec3"}),
        get_artifact("alternate_pdb", r"scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
        get_artifact("deployed_assembly", r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
        get_artifact("deployed_pdb", r"scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
        get_artifact("source", r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
        get_artifact("source_census", r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
        get_artifact("source_csproj", r"scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
        get_artifact("pre_run_manifest", r"scratch\EngineGate05R5Codec\CANDIDATE_PRE_RUN_MANIFEST.json"),
        get_artifact("engine_freeze_before", r"scratch\EngineGate05R5Codec\ENGINE_FREEZE_BEFORE.json"),
        get_artifact("engine_freeze_after", r"scratch\EngineGate05R5Codec\ENGINE_FREEZE_AFTER.json"),
        get_artifact("work_log", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\A_WORK_LOG.md"),
        get_artifact("recovery_ack", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\A_RECOVERY_ACK.md"),
        get_artifact("ack_json", r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\ACK.json")
    ]
}

target = r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046\COMPLETION.json"
with open(target, "w", encoding="utf-8") as f:
    json.dump(completion, f, indent=2)

print("Generated COMPLETION.json successfully:")
print(json.dumps(completion, indent=2))
