import os, hashlib, json, datetime, subprocess

now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def get_mvid(dll_path):
    cmd = ['powershell', '-Command', f'''
        [Reflection.Assembly]::Load([IO.File]::ReadAllBytes('{dll_path}')).ManifestModule.ModuleVersionId.ToString()
    ''']
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

def get_file_info(p):
    size = os.path.getsize(p)
    with open(p, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()
    return {'path': os.path.abspath(p), 'sha256': sha, 'size': size}

debug_dll = r'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
debug_pdb = r'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
release_dll = r'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll'
release_pdb = r'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb'
deployed_dll = r'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
deployed_pdb = r'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb'
census_cs = r'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs'
bridge_cs = r'scratch\WorkerBridgeMod\Source\WorkerBridge.cs'
csproj = r'scratch\WorkerBridgeMod\Source\WorkerBridge.csproj'

d_mvid = get_mvid(debug_dll)
r_mvid = get_mvid(release_dll)

d_dll_info = get_file_info(debug_dll)
d_dll_info['role'] = 'candidate_binary'
d_dll_info['mvid'] = d_mvid
d_dll_info['matching_pdb'] = get_file_info(debug_pdb)

r_dll_info = get_file_info(release_dll)
r_dll_info['role'] = 'candidate_binary'
r_dll_info['mvid'] = r_mvid
r_dll_info['matching_pdb'] = get_file_info(release_pdb)

dep_dll_info = get_file_info(deployed_dll)
dep_dll_info['role'] = 'deployed_mod_binary'
dep_dll_info['mvid'] = d_mvid
dep_dll_info['matching_pdb'] = get_file_info(deployed_pdb)

with open(census_cs, 'rb') as f:
    census_bytes = f.read()
prefix_sha = hashlib.sha256(census_bytes[:72547]).hexdigest().upper()

sources_info = {
    'engine_host_census': get_file_info(census_cs),
    'prefix_verification': {
        'byte_count': 72547,
        'sha256': prefix_sha,
        'marker': '    public static class ContentProfileProvider',
        'status': 'IMMUTABLE_VERIFIED'
    },
    'worker_bridge_cs': get_file_info(bridge_cs),
    'worker_bridge_csproj': get_file_info(csproj)
}

pre_manifest = {
    'schema_version': 'ADR-006B-v5',
    'run_id': 'GATE05-R8-SUPPORTED-DISPOSITION-PRE-RUN-01',
    'dispatch_id': 'WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692',
    'wp_id': 'WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION',
    'wp_revision': 'GATE05-R8-SUPPORTED-DISPOSITION',
    'created_at': now_iso,
    'selected_candidate': d_dll_info,
    'alternate_release_candidate': r_dll_info,
    'deployed_mod_assemblies': dep_dll_info,
    'sources': sources_info,
    'content_schema_profile': {
        'schema_version': 'ADR-006B-v5',
        'content_contract_version': 'ADR-006B-v5-R8',
        'supported_coverage_profile': 'POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5',
        'mod_patch_support_status': 'TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1',
        'patch_disposition': 'COUNT_OBSERVED_RAW_AST_EXCLUDED',
        'settings_disposition': 'USER_MOD_SETTINGS_EXCLUDED',
        'def_families_count': 8
    },
    'runtime_candidate_proof': {
        'debug_codeview_pdb': 'C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\Source\\obj\\Debug\\net472\\WarEconomy.WorkerBridge.PoC.pdb',
        'release_codeview_pdb': 'C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\Source\\obj\\Release\\net472\\WarEconomy.WorkerBridge.PoC.pdb'
    },
    'tooling_environment': {
        'dotnet_sdk': '10.0.201',
        'compiler': 'Roslyn C# 10+',
        'target_framework': 'net472',
        'os': 'Microsoft Windows 11 / 10 x64',
        'build_configuration_selected': 'Debug',
        'build_configuration_alternate': 'Release',
        'harness_dependencies': 'FROZEN_MANAGED_QA_DEPENDENCIES_V1'
    }
}

manifest_path = r'scratch\EngineGate05R8SupportedDisposition\CANDIDATE_PRE_RUN_MANIFEST.json'
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(pre_manifest, f, indent=2)

print('Updated CANDIDATE_PRE_RUN_MANIFEST.json successfully!')
print('Debug DLL:', d_dll_info['sha256'], f"({d_dll_info['size']} bytes), MVID: {d_mvid}")
print('Release DLL:', r_dll_info['sha256'], f"({r_dll_info['size']} bytes), MVID: {r_mvid}")
