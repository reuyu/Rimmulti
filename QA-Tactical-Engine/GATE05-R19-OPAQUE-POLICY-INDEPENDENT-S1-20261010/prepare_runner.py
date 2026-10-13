from review_setup import *
import copy,re

if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    old=ROOT/'QA-Tactical-Engine/GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010'
    prior=load(old/'INPUT_EXPECTED_SEMANTICS.json')
    census=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
    assert sha(census)==sha(ROOT/'Dispatcher/CANDIDATES/G05R15-03649052/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs')
    fixtures=Q/'fixtures';fixtures.mkdir();filecases={}
    for n,b in [('NORMAL_UTF8','R19 normal owned file\n한글 Ω café\n007\n'.encode()),('NORMAL_BINARY',bytes(range(256))+b'normal\x00')]:
        p=fixtures/(n+'.bin');p.write_bytes(b);filecases[n]=dict(file=row(p),expected_sha256=sha(p))
    paths=Q/'normal_paths'
    for n in ['worker-data','validator-data','worker-cwd','validator-cwd']:(paths/n).mkdir(parents=True)
    profilefile=fixtures/'NORMAL_PROFILE.json';write(profilefile,dict(schemaVersion='QA-OWNED-NORMAL-PROFILE-FIXTURE-V1',normalFixture=True,nativeLoadedContentProof=False,policyContract='WE-PACKAGE-POLICY-V1'))
    profileSHA=sha(profilefile)
    configs={};cfgroot=Q/'normal_configs';cfgroot.mkdir()
    runtime=ROOT/'scratch/EngineGate05R4/RuntimeCopy/RimWorldWin64.exe'
    mapping={'schemaVersion':'SchemaVersion','configId':'ConfigId','admittedValidatorExecutablePath':'AdmittedValidatorExecutablePath','admittedValidatorExecutableSha256':'AdmittedValidatorExecutableSha256','validatorArguments':'ValidatorArguments','workerUserDataDirectory':'WorkerUserDataDirectory','validatorUserDataDirectory':'ValidatorUserDataDirectory','workerCwd':'WorkerCwd','validatorCwd':'ValidatorCwd','expectedPackagePolicyDeclaration':'ExpectedPackagePolicyDeclaration','expectedContentProfileFingerprint':'ExpectedContentProfileFingerprint','role':'Role','capabilityBoundary':'CapabilityBoundary','issuedAtUtc':'IssuedAtUtc'}
    for role in ['SIMULATION','READ_ONLY']:
        for kind in ['PLAIN','OPAQUE']:
            name=role+'_'+kind
            policy=dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId='qa.R19.policy' if kind=='PLAIN' else '  qa.R18 정책 Ω  ',revision='007' if kind=='PLAIN' else '  007 café Ω  ',admittedPackageIds=['ludeon.rimworld','example.qa.normal'])
            canonical=json.dumps(policy,ensure_ascii=False,separators=(',',':'))
            record={k:copy.deepcopy(policy[k]) for k in ['policyId','revision','admittedPackageIds']};record['policyDigest']=hashlib.sha256(canonical.encode()).hexdigest().upper()
            config=dict(schemaVersion='WE-OPERATOR-BOOTSTRAP-V1',configId='qa.R19.'+name,admittedValidatorExecutablePath=str(runtime),admittedValidatorExecutableSha256=sha(runtime).lower(),validatorArguments='--normal-owned-option "Ω 007"',workerUserDataDirectory=str(paths/'worker-data'),validatorUserDataDirectory=str(paths/'validator-data'),workerCwd=str(paths/'worker-cwd'),validatorCwd=str(paths/'validator-cwd'),expectedPackagePolicyDeclaration=copy.deepcopy(policy),expectedContentProfileFingerprint=profileSHA,role=role,capabilityBoundary='LOCAL_SANDBOXED',issuedAtUtc='2026-10-10T00:00:00.0000000Z')
            assert len(config)==14 and len(policy)==4 and isinstance(policy['revision'],str)
            p=cfgroot/(name+'.json');write(p,config)
            expected={mapping[k]:copy.deepcopy(v) for k,v in config.items()};expected['AdmittedValidatorExecutableSha256']=sha(runtime);expected['PolicyAdmittedPackageIds']=copy.deepcopy(policy['admittedPackageIds'])
            redacted={k:copy.deepcopy(v) for k,v in config.items() if k!='validatorArguments'};redacted['admittedValidatorExecutableSha256']=sha(runtime);redacted={'schemaVersion':redacted['schemaVersion'],'configId':redacted['configId'],'role':redacted['role'],**{k:v for k,v in redacted.items() if k not in ['schemaVersion','configId','role']}}
            descriptor=dict(originId='QA_LOCAL_OPERATOR_PLAN_R19',expectedConfigId=config['configId'],expectedRole=role,expectedCapabilityBoundary=config['capabilityBoundary'],launchPlanId='QA.R19.EXPLICIT.PLAN.'+name)
            configs[name]=dict(input=config,file=row(p),expected_config_sha256=sha(p),descriptor=descriptor,expected_snapshot=expected,expected_declaration=policy,expected_record=record,expected_policy_json=canonical,expected_redacted=redacted,routes=['CONSTRUCTOR','TO_SNAPSHOT','ADMIT_BYTES','ADMIT_FILE'],opaque_original_strings_never_trim_or_derived_from_outputs=True)
    vals=copy.deepcopy(prior['validator_results'])
    for n,c in vals.items():
        for d in [c['input'],c['expected_redacted']]:
            d['validatorTaskId']=d['validatorTaskId'].replace('R17','R19');d['actualContentProfileFingerprint']=profileSHA
    oracle=dict(at=now(),config_cases=configs,file_cases=filecases,validator_results=vals,codec_cases=copy.deepcopy(prior['codec_cases']),policy_cases=copy.deepcopy(prior['policy_cases']),lifecycle_policy_declaration=copy.deepcopy(prior['lifecycle_policy_declaration']),lifecycle_policy_record=copy.deepcopy(prior['lifecycle_policy_record']),runtime_exe_metadata_reference=row(runtime),normal_only=True,output_derived_oracle=False,shared_standard_JsonNET_primitive_limit=True)
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    schema=load(old/'REFERENCE_DTO_SCHEMA.json');schema['at']=now();schema['source']=row(census);write(Q/'REFERENCE_DTO_SCHEMA.json',schema)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
    newton=FROZEN/'scratch/EngineGate05R19OpaquePolicy/Harness/bin/Debug/net472/Newtonsoft.Json.dll'
    allowed=[candidate,newton]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(at=now(),selected=row(candidate),selected_mvid='4969ba0f-2bdf-4a27-b4f8-d7fa217f0b70',allowed_managed=[row(p) for p in allowed],CSharp_Process_globalWorker_native_adverse_calls=0,host_own_new_QA_child_only_inline_WP=True))
    template=(old/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig').replace('R17','R19').replace('freshR17','freshR19')
    a=template.index('  static JObject SnapshotView(');b=template.index('  static void RunFileHelpers(',a)
    template=template[:a]+(Q/'SnapshotControls.cs.txt').read_text(encoding='utf-8')+'\n'+template[b:]
    template=template.replace('typeof(OperatorStartupConfigSnapshot),','typeof(OperatorStartupConfigSnapshot),typeof(OperatorLaunchDescriptor),')
    priorTemplate=(ROOT/'QA-Tactical-Engine/GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010/RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig')
    ref=priorTemplate[priorTemplate.index('  static JToken ReferenceValue('):priorTemplate.index('  [MethodImpl(MethodImplOptions.NoInlining)] static void PrepareReferenceBytes')]
    comp=priorTemplate[priorTemplate.index('  static int Bits('):priorTemplate.index('  [MethodImpl(MethodImplOptions.NoInlining)] static int Run(',priorTemplate.index('  static int Bits('))]
    template=template.replace('%%REFERENCE_FUNCTIONS%%',ref).replace('%%COMPARE_FUNCTIONS%%',comp)
    names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony']
    resolver=['{'+json.dumps(n)+',@"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    program=template.replace('%%ROOT%%',str(Q)).replace('%%RESOLVER%%',',\n'.join(resolver))
    assert not re.search(r'\bProcess\s*\.|VerifyProcessIdentity\s*\(|GetCurrentProcess\s*\(|MainModule|DllImport|WorkerBridgeComponent\s*\.|WorkerBridgeBootstrapper\s*\.|ComputeActualContentProfile\w*\s*\(|GetActualContentProfile\w*\s*\(|InvalidateCache\s*\(|SetComputationError\s*\(|BindingFlags.NonPublic',program)
    (Q/'RunnerTemplate.cs.txt').write_text(template,encoding='utf-8');(Q/'Program.cs').write_text(program,encoding='utf-8');(Q/'runner').mkdir()
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(Q/'runner/QaPureRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaPureRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [fw/'mscorlib.dll',fw/'System.dll',fw/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"']
    (Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    allocations=[]
    for stage,culture in [(1,'en-US'),(2,'de-DE')]:
        runid='R19-'+uuid.uuid4().hex[:16];out=Q/'runs'/runid;assert not out.exists();out.mkdir(parents=True);assert len(str(out/'input_snapshot/INPUT_EXPECTED_SEMANTICS.json'))<250;allocations.append(dict(stage=stage,culture=culture,run_id=runid,output_root=str(out)))
    write(Q/'RUN_ALLOCATION_PLAN.json',dict(at=now(),allocations=allocations,candidate_calls=0,runner_builds=0))
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),source=row(Q/'Program.cs'),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),allocations=row(Q/'RUN_ALLOCATION_PLAN.json'),fixture_files=[r['file'] for r in filecases.values()],config_files=[r['file'] for r in configs.values()],snapshot_public_properties=15,snapshot_redacted_properties=13,validator_result_fields=25,original_opaque_ID_revision_preserved=True,full_operator_descriptor_fields=5,normal_only=True,output_derived_oracle=False,source_policy_record_digest_independent_before_calls=True,candidate_calls=0))
    print(json.dumps(dict(config_cases=4,snapshot_routes_per_case=4,snapshot_properties=15,resultfields=25,builds=0,candidate_calls=0)))
