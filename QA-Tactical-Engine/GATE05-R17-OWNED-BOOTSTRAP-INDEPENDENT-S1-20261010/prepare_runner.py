from review_setup import *
import copy,re
if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    previous=ROOT/'QA-Tactical-Engine/GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010';prior=load(previous/'INPUT_EXPECTED_SEMANTICS.json')
    assert sha(FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs')==sha(ROOT/'Dispatcher/CANDIDATES/G05R15-03649052/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs')
    ownfixtures=Q/'fixtures';ownfixtures.mkdir();filecases={}
    for name,data in [('NORMAL_UTF8','R17 normal file\n한글 Ω café\r\n007\tvalid\n'.encode('utf-8')),('NORMAL_BINARY',bytes(range(256))+b'normal valid bytes\x00\n')]:
        p=ownfixtures/(name+'.bin');p.write_bytes(data);filecases[name]=dict(file=row(p),expected_sha256=sha(p),normal_file_only_not_executable_bootstrap_proof=True)
    paths=Q/'normal_paths'
    for n in ['worker-data','validator-data','worker-cwd','validator-cwd']: (paths/n).mkdir(parents=True)
    runtimeexe=ROOT/'scratch/EngineGate05R4/RuntimeCopy/RimWorldWin64.exe';runtime_exe=row(runtimeexe)
    declaration=copy.deepcopy(prior['cache_policies']['A']['input_declaration']);configs={}
    for role in ['SIMULATION','READ_ONLY']:
        for route in ['CONSTRUCTOR','TO_SNAPSHOT']:
            name=role+'_'+route;config=dict(schemaVersion='WE-OPERATOR-BOOTSTRAP-V1',configId='qa.R17 '+role+' Ω007',admittedValidatorExecutablePath=str(runtimeexe),admittedValidatorExecutableSha256=sha(runtimeexe).lower(),validatorArguments='--normal-owned-option "Ω 007"',workerUserDataDirectory=str(paths/'worker-data'),validatorUserDataDirectory=str(paths/'validator-data'),workerCwd=str(paths/'worker-cwd'),validatorCwd=str(paths/'validator-cwd'),expectedPackagePolicyDeclaration=copy.deepcopy(declaration),expectedContentProfileFingerprint='12AB'*16,role=role,capabilityBoundary='LOCAL_SANDBOXED',issuedAtUtc='2026-10-10T00:00:00.0000000Z')
            mapping={'schemaVersion':'SchemaVersion','configId':'ConfigId','admittedValidatorExecutablePath':'AdmittedValidatorExecutablePath','admittedValidatorExecutableSha256':'AdmittedValidatorExecutableSha256','validatorArguments':'ValidatorArguments','workerUserDataDirectory':'WorkerUserDataDirectory','validatorUserDataDirectory':'ValidatorUserDataDirectory','workerCwd':'WorkerCwd','validatorCwd':'ValidatorCwd','expectedPackagePolicyDeclaration':'ExpectedPackagePolicyDeclaration','expectedContentProfileFingerprint':'ExpectedContentProfileFingerprint','role':'Role','capabilityBoundary':'CapabilityBoundary','issuedAtUtc':'IssuedAtUtc'}
            expected={mapping[k]:copy.deepcopy(v) for k,v in config.items()};expected['AdmittedValidatorExecutableSha256']=sha(runtimeexe)
            redacted={k:copy.deepcopy(v) for k,v in config.items() if k!='validatorArguments'};redacted['admittedValidatorExecutableSha256']=sha(runtimeexe);redacted={'schemaVersion':redacted['schemaVersion'],'configId':redacted['configId'],'role':redacted['role'],**{k:v for k,v in redacted.items() if k not in ['schemaVersion','configId','role']}}
            configs[name]=dict(input=config,route=route,expected_snapshot=expected,expected_redacted=redacted,normal_paths_owned_QA_unapplied=True,initial_caller_edits_after_snapshot_only_not_reapplied=True)
    vals={}
    for n in ['NORMAL_A','NORMAL_B']:
        v=dict(validatorTaskId='VT.QA.R17.'+n,capabilityNonce='qa-owned-synthetic-capability-'+n,channelSecretToken='qa-owned-synthetic-secret-'+n,validatorProcessId='4242' if n=='NORMAL_A' else '4250',validatorProcessStartTimeUtc='2026-10-10T00:00:00.0000000Z',validatorExecutable=str(runtimeexe),authorityId='AUTH.QA.Ω.'+n,storeIncarnation='STORE.QA.001',baseLineage='LINEAGE.QA.001',grantId='GRANT.'+n,workerGeneration=2147483649,scopeId='QA.TARGET.'+n,targetMapIndex=0,allowedMode='READ_ONLY',manifestVersion='4.0',sealedResultId='SEAL.'+n,resultEpoch=4294967301,sealedManifestHash='2B'*32,sourceArtifactHash='3C'*32,validatorResult='PASS',actualContentProfileFingerprint='12AB'*16,actualManifestHash='2B'*32,stagedSha='4D'*32,stagedFilePath=str(ownfixtures/(n+'.staged.literal.rws')),validatedAtUtc='2026-10-10T00:00:01.0000000Z')
        expected=copy.deepcopy(v);expected['capabilityNonce']='[REDACTED_PROTECTED_OPERATOR_CAPABILITY]';expected['channelSecretToken']='[REDACTED_PROTECTED_CHANNEL_SECRET]';vals[n]=dict(input=v,expected_redacted=expected,synthetic_owned_DTO_no_real_PID_or_channel_claim=True)
    codec={n:dict(input=prior['cases'][n],expected_transport=prior['expected_transport_cases'][n],expected_canonical=prior['expected_canonical_cases'][n]) for n in ['BASE','NORMAL_REVISION_B']}
    policy={n:copy.deepcopy(prior['policy_cases'][n]) for n in ['ALIGNED','UNICODE_REV']}
    # No candidate output or constructor is used to create these expected carriers.
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',dict(at=now(),config_cases=configs,file_cases=filecases,validator_results=vals,codec_cases=codec,policy_cases=policy,lifecycle_policy_declaration=declaration,lifecycle_policy_record=prior['cache_policies']['A']['expected_policy_record'],runtime_exe_metadata_reference=runtime_exe,current_fulltyped_literal_oracles_before_build_calls=True,shared_standard_JsonNET_primitive_limit=True,normal_only=True,priorR15_PASS_notinherited=True))
    schema=load(previous/'REFERENCE_DTO_SCHEMA.json');schema['at']=now();schema['source']=row(FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs');write(Q/'REFERENCE_DTO_SCHEMA.json',schema)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R17OwnedBootstrap/Harness/bin/Debug/net472/Newtonsoft.Json.dll';allowed=[candidate,newton]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(at=now(),selected=row(candidate),selected_mvid='d5a25e43-567c-414f-b7bd-4d4aa0b47050',allowed_managed=[row(p) for p in allowed],CSharp_Process_and_VerifyProcessIdentity_calls=0,host_own_QA_child_telemetry_requires_Master_clarification=True,Workerglobal_Awake_bootstrap_native_adverse_allowed=False))
    template=(Q/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig');old=(previous/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig')
    ref=old[old.index('  static JToken ReferenceValue('):old.index('  [MethodImpl(MethodImplOptions.NoInlining)] static void PrepareReferenceBytes')]
    comp=old[old.index('  static int Bits('):old.index('  [MethodImpl(MethodImplOptions.NoInlining)] static int Run(',old.index('  static int Bits('))]
    # Retain only independent comparison functions, not old Run or wrappers/Process calls.
    template=template.replace('%%REFERENCE_FUNCTIONS%%',ref).replace('%%COMPARE_FUNCTIONS%%',comp)
    names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+',@"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    program=template.replace('%%ROOT%%',str(Q)).replace('%%RESOLVER%%',',\n'.join(resolver))
    assert not re.search(r'\bProcess\s*\.|VerifyProcessIdentity\s*\(|GetCurrentProcess\s*\(|MainModule|DllImport|WorkerBridgeComponent\s*\.|WorkerBridgeBootstrapper\s*\.|ComputeActualContentProfile\w*\s*\(|GetActualContentProfile\w*\s*\(|InvalidateCache\s*\(|SetComputationError\s*\(|BindingFlags.NonPublic',program)
    (Q/'Program.cs').write_text(program,encoding='utf-8');(Q/'runner').mkdir()
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(Q/'runner/QaPureRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaPureRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [fw/'mscorlib.dll',fw/'System.dll',fw/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    allocations=[]
    for stage,culture in [(1,'en-US'),(2,'de-DE')]:
        runid='R17-'+uuid.uuid4().hex[:16];out=Q/'runs'/runid;assert not out.exists();out.mkdir(parents=True);assert len(str(out/'input_snapshot/INPUT_EXPECTED_SEMANTICS.json'))<250;allocations.append(dict(stage=stage,culture=culture,run_id=runid,output_root=str(out),allocated_validated_before_final_build_calls=True))
    write(Q/'RUN_ALLOCATION_PLAN.json',dict(at=now(),allocations=allocations,candidate_calls=0,runner_builds=0))
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),source=row(Q/'Program.cs'),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),allocations=row(Q/'RUN_ALLOCATION_PLAN.json'),fixture_files=[r['file'] for r in filecases.values()],snapshot_fields_all14=True,validator_result_fields_full26=True,independent_current_census_schema_bytes_unchanged=True,candidate_process_queries_global_worker_native_adverse_calls=0,output_derived_oracle=False))
    print(json.dumps(dict(config_cases=4,filecases=2,validatorDTOs=2,codec_cases=2,policy_cases=2,newsource=str(Q/'Program.cs'),candidate_calls=0,builds=0)))
