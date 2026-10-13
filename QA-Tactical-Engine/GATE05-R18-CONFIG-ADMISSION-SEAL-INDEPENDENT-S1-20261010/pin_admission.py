from review_setup import *
import re,sys
if __name__=='__main__':
    assert not (Q/'runner/QaPureRunner.exe').exists() and not (Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json').exists()
    program=(Q/'Program.cs').read_text(encoding='utf-8-sig')
    assert not re.search(r'\bProcess\s*\.|GetCurrentProcess\s*\(|MainModule|VerifyProcessIdentity\s*\(|DllImport|WorkerBridgeComponent\s*\.|WorkerBridgeBootstrapper\s*\.|BindingFlags.NonPublic|TryInstallOperatorStartupConfig|ActiveStartupConfig',program)
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json')
    assert all(len(c['input'])==14 and len(c['descriptor'])==5 and len(c['expected_snapshot'])==15 and len(c['expected_redacted'])==13 and len(c['expected_declaration'])==4 for c in oracle['config_cases'].values())
    assert all(len(c['expected_redacted'])==25 for c in oracle['validator_results'].values())
    for n,c in oracle['config_cases'].items():
        assert row(Path(c['file']['path']))==c['file'] and c['expected_config_sha256']==c['file']['sha256'] and load(Path(c['file']['path']))==c['input']
        if n.endswith('OPAQUE'):
            assert c['expected_declaration']['policyId']!=c['expected_declaration']['policyId'].strip() and c['expected_declaration']['revision']!=c['expected_declaration']['revision'].strip()
        assert c['expected_declaration']==c['input']['expectedPackagePolicyDeclaration']==c['expected_snapshot']['ExpectedPackagePolicyDeclaration']==c['expected_redacted']['expectedPackagePolicyDeclaration']
    paths=[Q/n for n in ['bootstrap.py','review_setup.py','prepare_runner.py','prepare_evidence_tools.py','SnapshotControls.cs.txt','RunnerTemplate.cs.txt','Program.cs','pin_admission.py','run_identity.py','host_launch.py','build.rsp','ORACLE_BEFORE_BUILD.json','INPUT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','QA_RUNNER_CONFIG.json','RUN_ALLOCATION_PLAN.json','TOOLCHAIN_OBSERVED.json','R18_FROZEN_LINEAGE.json']]
    paths += [Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]+list((Q/'fixtures').glob('*'))+list((Q/'normal_configs').glob('*'))
    paths += [MAN,DEP,BASELINE,ADMISSION,PKG/'WP_QA_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_S1.md',Path(sys.executable),Path(r'C:\Program Files\dotnet\dotnet.exe')]
    paths += list(Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore').glob('*.dll'))
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    paths += [fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll']]
    unique={str(p).lower():p for p in paths}
    write(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json',dict(at=now(),WP=row(PKG/'WP_QA_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_S1.md'),host_telemetry_inline_WP=True,source=row(Q/'Program.cs'),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),pins=[row(p) for p in sorted(unique.values())],allowed='ONLYnewownedPUREnormalrunner onebuild/en-US,de-DE explicitdescriptor/opaqueORIGINALlosslessexpectations;hostonlynewQAchildPIDexit',snapshot_full15_result25=True,normal_source_and_detachedcopies_edits_only=True,all_Process_globalWorker_native_adverse_production_calls=0,prebuild_candidate_calls=0,output_derived_oracle=False))
    print('Full R18 normal original-string oracle/source/tools/input/DLL-PDB bindings pinned before only final build')
