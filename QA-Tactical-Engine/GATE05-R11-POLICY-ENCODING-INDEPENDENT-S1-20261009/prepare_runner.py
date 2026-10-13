from review_setup import *
import copy,re

def expected_normal(snapshot):
    x=copy.deepcopy(snapshot)
    for m in x['activeMods']:
        if 'modVersion' not in m:m['modVersion']=None
    x['dlcExpansions'].sort(key=lambda r:r['defName']);x['activeMods'].sort(key=lambda r:(r['loadOrder'],r['packageId']));x['loadedAssemblies'].sort(key=lambda r:(r['packageId'],r['assemblyName'],r['mvid'],r['sha256']))
    for rows in x['defFamilies'].values():rows.sort(key=lambda r:r['defName'])
    for t in x['defFamilies']['thingDefs']:
        t.get('stats',[]).sort(key=lambda r:(r['statDef'],r['value']));t.get('costList',[]).sort(key=lambda r:(r['thingDef'],r['count']));t.get('stuffCategories',[]).sort()
    return x

if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    selection=load(SELECTION);assert selection['reference_variant']=='LITERAL_UNICODE_MINIMAL' and selection['candidate_calls_before_selection']==0
    prepared=load(PREP/'NORMAL_REFERENCE_ORACLE.json');assert sha(PREP/'NORMAL_REFERENCE_ORACLE.json')==selection['policy_reference_oracle_sha256']
    oracle=copy.deepcopy(load(PREVQ/'INPUT_EXPECTED_SEMANTICS.json'));oracle.pop('package_policy_cases');oracle.pop('policy_framing_limit',None)
    oracle.update(created_at=now(),scope='Fresh exact R11 current-version positive declaration/codec helpers only;no old PASS',master_prospective_selection=row(SELECTION),selection_precedes_candidate_calls=True)
    for x in oracle['cases'].values():
        x['contentContractVersion']='ADR-006B-v5-R11';x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R11_POLICY_ENCODING','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5']
    oracle['expected_canonical_cases']={n:expected_normal(x) for n,x in oracle['cases'].items()}
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r11_json_path']=r['r5_json_path']
    policy_inputs=copy.deepcopy(prepared['cases'])
    alternate_raw=dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId='qa.policy.secondary',revision='3',admittedPackageIds=['Example.Core','example.other'])
    alternate_decl=dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId='qa.policy.secondary',revision='3',admittedPackageIds=['example.core','example.other'])
    alternate_bytes=json.dumps(alternate_decl,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    policy_inputs['ALTERNATE_UNIQUE_LIST']=dict(expected_input=alternate_raw,expected_canonical_declaration=alternate_decl,separate_observed_inventory_literal=[dict(loadOrder=0,packageId='EXAMPLE.CORE'),dict(loadOrder=1,packageId='example.other')],references={'LITERAL_UNICODE_MINIMAL':dict(expected_sha256=hashlib.sha256(alternate_bytes).hexdigest().upper())})
    base_mods=sorted(oracle['cases']['BASE']['activeMods'],key=lambda m:m['loadOrder']);policy_cases={};refs=Q/'policy_references';refs.mkdir()
    for name,c in policy_inputs.items():
        raw=c['expected_input'];decl=c['expected_canonical_declaration'];blob=json.dumps(decl,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8');digest=hashlib.sha256(blob).hexdigest().upper()
        assert digest==c['references']['LITERAL_UNICODE_MINIMAL']['expected_sha256'];reference=refs/(name+'.canonical.utf8.json');reference.write_bytes(blob)
        actual=copy.deepcopy(oracle['cases']['BASE']);actual['activeMods']=[]
        for ordinal,observed in enumerate(c['separate_observed_inventory_literal']):
            assert observed['loadOrder']==ordinal;m=copy.deepcopy(base_mods[ordinal]);m.update(observed);actual['activeMods'].append(m)
        admitted=expected_normal(actual);admitted['packagePolicyDisposition']=dict(policyId=raw['policyId'],revision=raw['revision'],policyDigest=digest,status='ADMITTED');admitted['patchSettingsDisposition']['supportedModBoundary']='CHECKED_POLICY:'+raw['policyId']+':'+raw['revision']
        record=dict(policyId=raw['policyId'],revision=raw['revision'],admittedPackageIds=raw['admittedPackageIds'],policyDigest=digest)
        check=dict(isAdmitted=True,policyId=raw['policyId'],revision=raw['revision'],policyDigest=digest,status='ADMITTED',failureReason='',expectedPackages=raw['admittedPackageIds'],observedPackages=[m['packageId'].lower() for m in c['separate_observed_inventory_literal']])
        policy_cases[name]=dict(input_declaration=raw,expected_canonical_declaration=decl,expected_policy_record=record,independent_observed_manifest=actual,expected_check_result=check,expected_admitted_manifest=admitted,expected_json=blob.decode('utf-8'),expected_digest=digest,reference=row(reference),expected_escaped_policyId=json.dumps(raw['policyId'],ensure_ascii=False)[1:-1],expected_escaped_revision=json.dumps(raw['revision'],ensure_ascii=False)[1:-1],expected_boundary=admitted['patchSettingsDisposition']['supportedModBoundary'],schema_scope='CURRENT_WE-PACKAGE-POLICY-V1_ONLY',raw_expected_package_spelling='Preserved in Check result;canonical declaration and record.ToDeclaration normalize lowercase',manifest_package_spelling='Observed literal spelling preserved in content codec')
    oracle['policy_cases']=policy_cases;oracle['expected_policies_derived_from_actual']=False;oracle['actual_schema_carrier_map']=dict(declaration='schemaVersion string',record='No schemaVersion,ToDeclaration restores constant',check='No schema field,ID/revision/digest/raw expected-list/lower observed-list',disposition='No schema field,current-version digest and exactID/revision/status',general_schema_handling='STATIC_OPEN_NOT_EXECUTED')
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R11PolicyEncoding/Harness/bin/Debug/net472/Newtonsoft.Json.dll';assert newton.exists();allowed=[candidate,newton]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='e6c6f6fd-2915-4493-8ef9-dc5d87de1c6b',allowed_managed=[row(p) for p in allowed],master_selected_variant='LITERAL_UNICODE_MINIMAL',supported_policy_schema='WE-PACKAGE-POLICY-V1',allowed_production_calls=['DTO fields/constructors','policy Serialize/Deserialize/EscapeJsonString','digest declaration/record/scalar overloads','ToRecord/ToDeclaration current schema','matching CheckPackagePolicy allfour overloads','matching TryAdmitWithPackagePolicy record/declaration','positive codec/Normalize/Validate/structuralTryAdmit'],forbidden_calls=['Configure/Clear/properties/provider/cache/game/native/operator','oldrunner/unknownschema/rejection/tied/ambiguity/adverse'],oracle_before_build=True))
    prior_template=ROOT/'QA-Tactical-Engine/GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009/RunnerTemplate.cs.txt'
    s=prior_template.read_text(encoding='utf-8-sig').replace('R9','R11').replace('version-meaning','policy-encoding')
    s=s.replace('static bool Compared(', (Q/'PolicyChecks.cs.txt').read_text(encoding='utf-8-sig')+'\n  static bool Compared(')
    s=s.replace('var leafRows=new List<object>();int leafCount=0;','RunPolicyDeclarations(input);\n    var leafRows=new List<object>();int leafCount=0;bool allHistorical=true;')
    s=s.replace('Compare(ev,av,path,checks);leafRows.Add','Compare(ev,av,path,checks);allHistorical=allHistorical&&Compared(checks);leafRows.Add').replace('leafCount==65,"65 historical','leafCount==65&&allHistorical,"65 historical')
    s=s.replace('Save("BOUNDARY_OBSERVATIONS.json",','Check("NORMAL_SET_PERMUTATION",outputs["BASE"]==outputs["NORMAL_SET_ORDER"],"Normal distinct-set permutation bytes;ordered material sequence compared in full semantic checks");\n    Save("BOUNDARY_OBSERVATIONS.json",')
    s=s.replace('string[] types={','string[] types={"ExpectedPackagePolicyDeclaration","ExpectedPackagePolicyRecord","PackagePolicyDispositionRecord","PackagePolicyCheckResult",')
    (Q/'RunnerTemplate.cs.txt').write_text(s,encoding='utf-8');names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    program=s.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(resolver));assert not any(n in program for n in ['ConfigureExpectedPackagePolicy','ClearConfiguredExpectedPackagePolicy','GetActualContent','ComputeActualContent','InvalidateCache'])
    (Q/'Program.cs').write_text(program,encoding='utf-8');out=Q/'runner';out.mkdir();framework=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(out/'QaCodecRunner.exe')+'"','-pdb:"'+str(out/'QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [framework/'mscorlib.dll',framework/'System.dll',framework/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),reference_files=[row(p) for p in sorted(refs.iterdir())],generic_cases=12,policy_cases=15,selected_variant='LITERAL_UNICODE_MINIMAL',selection=row(SELECTION),schema_carrier_mapping=oracle['actual_schema_carrier_map'],independent_input_before_final_build=True,candidate_calls_before_reference=0,prior_PASS_inherited=False))
    print(json.dumps(dict(generic_cases=12,policy_cases=15,prebuilt_reference_files=15,selected_variant='LITERAL_UNICODE_MINIMAL',oracle_before_build=True)))
