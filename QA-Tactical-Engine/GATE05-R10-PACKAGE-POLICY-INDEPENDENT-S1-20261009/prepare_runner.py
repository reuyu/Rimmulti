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
    prior=ROOT/'QA-Tactical-Engine/GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009'
    oracle=copy.deepcopy(load(prior/'INPUT_EXPECTED_SEMANTICS.json'))
    oracle.update(created_at=now(),scope='Fresh exact R10 independent positive codec and matching separate-policy helpers; no previous PASS inherited',prior_oracle_reference=dict(path=str(prior/'INPUT_EXPECTED_SEMANTICS.json'),sha256=sha(prior/'INPUT_EXPECTED_SEMANTICS.json')))
    for x in oracle['cases'].values():
        x['contentContractVersion']='ADR-006B-v5-R10';x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R10_PACKAGE_POLICY','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5']
        x['patchSettingsDisposition']['supportedModBoundary']='UNCONFIGURED';x['packagePolicyDisposition']=None
    oracle['expected_canonical_cases']={n:expected_normal(x) for n,x in oracle['cases'].items()}
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r10_json_path']=r['r5_json_path']
    # Expected declarations and actual IDs below are distinct handwritten literals.
    declarations=[('EQ_A','qa.policy.primary','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),('EQ_A_SEPARATE','qa.policy.primary','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),('ID_ONLY','qa.policy.alternate','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),('REV_ONLY','qa.policy.primary','8',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),('ORDER_ONLY','qa.policy.primary','7',['example.material','Example.Core'],['EXAMPLE.MATERIAL','example.core']),('LIST_ALTERNATE','qa.policy.secondary','3',['example.core','example.other'],['EXAMPLE.CORE','example.other'])]
    policies={}
    source_mods=sorted(oracle['cases']['BASE']['activeMods'],key=lambda m:m['loadOrder'])
    for name,pid,rev,expected_ids,observed_ids in declarations:
        preimage=(pid+'|'+rev+'|'+','.join(p.lower() for p in expected_ids)).encode('utf-8');digest=hashlib.sha256(preimage).hexdigest().upper()
        expected_policy=dict(policyId=pid,revision=rev,admittedPackageIds=expected_ids,policyDigest=digest)
        actual=copy.deepcopy(oracle['cases']['BASE']);actual['activeMods']=[]
        for ordinal,pkg in enumerate(observed_ids):
            m=copy.deepcopy(source_mods[ordinal]);m.update(loadOrder=ordinal,packageId=pkg);actual['activeMods'].append(m)
        admitted=expected_normal(actual);admitted['packagePolicyDisposition']=dict(policyId=pid,revision=rev,policyDigest=digest,status='ADMITTED');admitted['patchSettingsDisposition']['supportedModBoundary']='CHECKED_POLICY:'+pid+':'+rev
        check=dict(isAdmitted=True,policyId=pid,revision=rev,policyDigest=digest,status='ADMITTED',failureReason='',expectedPackages=expected_ids,observedPackages=[p.lower() for p in observed_ids])
        (Q/(name+'.policy.preimage.utf8')).write_bytes(preimage)
        policies[name]=dict(expected_policy=expected_policy,independent_observed_manifest=actual,expected_check_result=check,expected_admitted_manifest=admitted,preimage_utf8_path=str(Q/(name+'.policy.preimage.utf8')),preimage_utf8_hex=preimage.hex(),expected_digest=digest,expected_boundary='CHECKED_POLICY:'+pid+':'+rev,normal_scope='Nonempty unpadded normal identifiers, dot package IDs, unique physical list aligned to sequential loadOrder; no rejection/ambiguity')
    oracle['package_policy_cases']=policies;oracle['policy_framing_limit']='Observed normal pId|revision|lowercase comma list reference only; no typed/injective/escaped/general policy schema claim';oracle['expected_policies_derived_from_actual']=False
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R10PackagePolicy/Harness/bin/Debug/net472/Newtonsoft.Json.dll'
    assert newton.exists()
    allowed=[candidate,newton]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb',allowed_managed=[dict(path=str(p),sha256=sha(p)) for p in allowed],allowed_production_calls=['DTO fields/constructors','SerializeCanonicalJson','DeserializeCanonicalJson','CanonicalNormalize','positive ValidateContract/structuralTryAdmitManifest','ComputePackagePolicyDigest record and string overload','matching CheckPackagePolicy both overloads','fullydeclaredmatching TryAdmitWithPackagePolicy'],forbidden_calls=['Configure/Clear/Configured/HasConfigured','provider/cache/native/operator/game','oldrunner/rejection/tied/ambiguity/adverse'],oracle_fixed_before_finalbuild=True))
    s=(prior/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig').replace('R9','R10').replace('version-meaning','package-policy')
    s=s.replace('static bool Compared(', (Q/'PackageChecks.cs.txt').read_text(encoding='utf-8-sig')+'\n  static bool Compared(')
    s=s.replace('var leafRows=new List<object>();','RunPackagePolicies(input);\n    var leafRows=new List<object>();')
    s=s.replace('string[] types={','string[] types={"ExpectedPackagePolicyRecord","PackagePolicyDispositionRecord","PackagePolicyCheckResult",')
    (Q/'RunnerTemplate.cs.txt').write_text(s,encoding='utf-8')
    names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    program=s.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(resolver))
    assert not any(n in program for n in ['ConfigureExpectedPackagePolicy','ClearConfiguredExpectedPackagePolicy','GetActualContent','ComputeActualContent','InvalidateCache'])
    (Q/'Program.cs').write_text(program,encoding='utf-8')
    out=Q/'runner';out.mkdir();refs=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(out/'QaCodecRunner.exe')+'"','-pdb:"'+str(out/'QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [refs/'mscorlib.dll',refs/'System.dll',refs/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"']
    (Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),oracle=dict(path=str(Q/'INPUT_EXPECTED_SEMANTICS.json'),sha256=sha(Q/'INPUT_EXPECTED_SEMANTICS.json')),generic_cases=len(oracle['cases']),package_cases=len(policies),historical_leaf_oracle=65,independent_preimage_sha_expected_before_candidate_execution=True,concrete_types='ExpectedPackagePolicyRecord.policyId/revision/digest strings,list<string> IDs',policy_case_relation=dict(equal=['EQ_A','EQ_A_SEPARATE'],id_only=['EQ_A','ID_ONLY'],revision_only=['EQ_A','REV_ONLY'],order_only_same_id_revision=['EQ_A','ORDER_ONLY']),stronger_general_framing='STATIC_REVISION_REQUIRED',controls_executed=0))
    print(json.dumps(dict(generic_cases=len(oracle['cases']),package_cases=len(policies),oracle_before_build=True)))
