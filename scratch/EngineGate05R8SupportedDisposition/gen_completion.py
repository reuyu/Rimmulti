import os, hashlib, json, datetime

task_dir = r'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692'
out_path = os.path.join(task_dir, 'COMPLETION.json')

def get_file_info(p, role, extra=None):
    abs_p = os.path.abspath(p)
    size = os.path.getsize(abs_p)
    with open(abs_p, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()
    entry = {
        'role': role,
        'path': abs_p,
        'sha256': sha,
        'size': size
    }
    if extra:
        entry.update(extra)
    return entry

now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

debug_dll = r'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
debug_pdb = r'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
release_dll = r'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll'
release_pdb = r'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb'
deployed_dll = r'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
deployed_pdb = r'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb'

artifacts = [
    get_file_info(r'docs\POC_EngineHost_Content_Codec_Gate05_R8.md', 'implementation_report'),
    get_file_info(r'docs\RELEASE_MANIFEST_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION.json', 'release_manifest'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\Harness\Program.cs', 'harness'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\Harness\Gate05R8SupportedRunner.csproj', 'harness_project'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\results.json', 'results'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\raw_console.txt', 'raw_evidence'),
    get_file_info(debug_dll, 'candidate_binary', {'mvid': '348b49f3-74f8-4643-9a2f-4a1dc5fb9a41'}),
    get_file_info(debug_pdb, 'pdb'),
    get_file_info(release_dll, 'alternate_binary', {'mvid': 'f3ab51a3-2c77-423c-adde-806782360d8f'}),
    get_file_info(release_pdb, 'alternate_pdb'),
    get_file_info(deployed_dll, 'deployed_assembly', {'mvid': '348b49f3-74f8-4643-9a2f-4a1dc5fb9a41'}),
    get_file_info(deployed_pdb, 'deployed_pdb'),
    get_file_info(r'scratch\WorkerBridgeMod\Source\WorkerBridge.cs', 'source'),
    get_file_info(r'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs', 'source_census'),
    get_file_info(r'scratch\WorkerBridgeMod\Source\WorkerBridge.csproj', 'source_csproj'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\CANDIDATE_PRE_RUN_MANIFEST.json', 'pre_run_manifest'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\ENGINE_FREEZE_BEFORE.json', 'engine_freeze_before'),
    get_file_info(r'scratch\EngineGate05R8SupportedDisposition\ENGINE_FREEZE_AFTER.json', 'engine_freeze_after'),
    get_file_info(os.path.join(task_dir, 'A_WORK_LOG.md'), 'work_log'),
    get_file_info(os.path.join(task_dir, 'A_RECOVERY_ACK.md'), 'recovery_ack'),
    get_file_info(os.path.join(task_dir, 'ACK.json'), 'ack_json')
]

completion = {
    'schema_version': 1,
    'producer': 'A',
    'report_kind': 'E1',
    'dispatch_id': 'WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692',
    'wp_id': 'WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION',
    'wp_revision': 'GATE05-R8-SUPPORTED-DISPOSITION',
    'result_id': 'WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-RESULT-01',
    'status': 'COMPLETED',
    'completed_at': now_utc,
    'summary': 'WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION / GATE05-R8-SUPPORTED-DISPOSITION narrow technical correction completed and developer E1 verification recorded. Successfully replaced label-only patch/settings support with actual typed disposition (ModPatchSettingsDispositionRecord, mod-level patchDisposition, settingsDisposition, totalObservedPatches). Enforced fail-closed child element observation before projection, eliminating silent filter omission and distinctly preserving legitimate optional absence. Disentangled compatibility version range (SupportedVersionsReadOnly) from mod version. Established composite key uniqueness and deterministic multi-key tie-breaking for loaded assemblies and active mods. Preserved immutable source baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72547 bytes SHA F3C4F865...). Executed positive pure normal DTO/helper unit harness (16/16 PASS) with Master-approved frozen managed dependencies without cache calls, adverse execution, or runtime initialization anomalies. Bound actual PE MVIDs for Debug (348b49f3-...) and Release (f3ab51a3-...) candidates. All historical lineages and installed incident preserved as OPEN.',
    'e1_verdict': 'IMPLEMENTATION_PARTIAL',
    'limitations': [
        'NATIVE_UNTESTED: In-engine and game runtime execution was strictly prohibited under WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION. Verification was conducted via isolated positive pure normal DTO and helper unit harness (16/16 PASS).',
        'INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.',
        'NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Gate05 defects, Engine002/006, Pipeline007, and Foundation HOLD remain OPEN pending Master disposition and independent Sol QA review.'
    ],
    'artifacts': artifacts
}

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(completion, f, indent=2)

print(f'Wrote {out_path}')
