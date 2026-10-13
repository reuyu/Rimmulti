from review_setup import *
import copy,re
def normal_expected(snapshot):
    x=copy.deepcopy(snapshot)
    x['dlcExpansions'].sort(key=lambda r:r['defName']);x['activeMods'].sort(key=lambda r:(r['loadOrder'],r['packageId']));x['loadedAssemblies'].sort(key=lambda r:(r['packageId'],r['assemblyName'],r['mvid']))
    for records in x['defFamilies'].values():records.sort(key=lambda r:r['defName'])
    for t in x['defFamilies']['thingDefs']:
        t.get('stats',[]).sort(key=lambda r:(r['statDef'],r['value']));t.get('costList',[]).sort(key=lambda r:(r['thingDef'],r['count']));t.get('stuffCategories',[]).sort()
    return x
if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    oracle=copy.deepcopy(load(PREVQ/'INPUT_EXPECTED_SEMANTICS.json'));oracle['created_at']=now();oracle['scope']='Fresh R7 SYNTHETIC_CODEC_INPUT / CODEC_UNIT_ONLY;prior layouts are design references,not inherited evidence'
    for name,x in oracle['cases'].items():
        x.update(contentContractVersion='ADR-006B-v5-R7',supportedCoverageProfile='POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5',modPatchSupportStatus='COUNT_ONLY_EXPLICIT_EXCLUSION_RAW_PATCHES_SETTINGS')
        x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R7_CONTENT_ADMISSION','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5']
        # Ordinary distinct composite assembly keys: same package, different names.
        extra=copy.deepcopy(x['loadedAssemblies'][0]);extra.update(packageId='example.z',assemblyName='Example.Auxiliary',mvid='33333333-4444-5555-6666-777777777777',sizeBytes=4096);x['loadedAssemblies'].insert(0,extra)
    perm=copy.deepcopy(oracle['cases']['BASE']);perm['activeMods'].reverse();perm['dlcExpansions'].reverse();perm['loadedAssemblies'].reverse()
    for rows in perm['defFamilies'].values():rows.reverse()
    for t in perm['defFamilies']['thingDefs']:t['stats'].reverse();t['costList'].reverse();t['stuffCategories'].reverse()
    oracle['cases']['NORMAL_SET_ORDER']=perm
    oracle['expected_canonical_cases']={name:normal_expected(x) for name,x in oracle['cases'].items()}
    oracle.pop('r6_fresh_expected_policy',None);oracle['r7_fresh_expected_policy']='Ordinal DLC/Def names;distinct mod(loadOrder,packageId),assembly(packageId,name,MVID),stat(name,value),cost(name,count) keys;ordered verbs/stages/comps and multiplicity unchanged. Generic false transport retains input order. No tied/unsupported/rejection fixtures.'
    oracle['positive_contract_cases']=['BASE','NORMAL_REVISION_B'];oracle['positive_try_admit_cases']=['BASE','NORMAL_REVISION_B']
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r7_json_path']=r['r5_json_path'];r['historical_path_label']='Stable historical DTO mapping;no prior candidate result reuse'
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R7ContentAdmission/Harness/bin/Debug/net472/Newtonsoft.Json.dll';allowed=[candidate,newton]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    config=dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='bdf94567-be4d-4270-9a70-dbf2df9b5b4a',allowed_managed=[dict(path=str(p),sha256=sha(p)) for p in allowed],allowed_production_calls=['DTO constructors/fields','SerializeCanonicalJson(manifest,bool)','DeserializeCanonicalJson','CanonicalNormalize','positive ValidateContract','positive TryAdmitManifest'],framework='net472/Windows CLR;no game initialization',forbidden_calls=['GetActual*/ComputeActual*','InvalidateCache/cache getters','game/native/operator/task/channel/STEP/SEAL/STAGE/PROMOTE','old A/QA runner','invalid/missing-required/rejection/adverse'],case_scope='R7 fresh normal oracle,positive helper2cases only;optional transport not admission proof')
    write(Q/'QA_RUNNER_CONFIG.json',config)
    template=(PREVQ/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig').replace('R6','R7').replace('codec-contract','content-admission')
    marker='Check("POSITIVE_CONTRACT_"+p.Name,valid&&reason=="","Fully declared normal manifest positive helper return;not admission proof");'
    assert template.count(marker)==1
    addition='''
        var admittedDto=ContentProfileProvider.DeserializeCanonicalJson(before);string admitBefore=ContentProfileProvider.SerializeCanonicalJson(admittedDto,false);string admittedJson,admitReason;
        bool admitted=ContentProfileProvider.TryAdmitManifest(admittedDto,out admittedJson,out admitReason);
        var admitChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(ContentProfileProvider.DeserializeCanonicalJson(admittedJson)),"",admitChecks);
        string admitAfter=ContentProfileProvider.SerializeCanonicalJson(admittedDto,false);
        Check("POSITIVE_TRY_ADMIT_"+p.Name,admitted&&admitReason==""&&admittedJson==bytes&&admitAfter==bytes,"Positive pure helper output independently matches expected normalized semantics and codec bytes;caller mutation recorded,not loaded-profile authority");
        Save(p.Name+".admitted.canonical.json",admittedJson);Save(p.Name+".admission_checks.json",JsonConvert.SerializeObject(admitChecks,Formatting.Indented));
        Save(p.Name+".admission_observation.json",JsonConvert.SerializeObject(new{success=admitted,reason=admitReason,before_transport_sha256=Hash(Utf8.GetBytes(admitBefore)),after_transport_sha256=Hash(Utf8.GetBytes(admitAfter)),canonical_utf8_bytes=Utf8.GetByteCount(admittedJson),canonical_sha256=Hash(Utf8.GetBytes(admittedJson)),in_place_bytes_changed=admitBefore!=admitAfter,scope="POSITIVE_PURE_HELPER_ONLY"},Formatting.Indented));
    '''
    template=template.replace(marker,marker+addition)
    (Q/'RunnerTemplate.cs.txt').write_text(template,encoding='utf-8')
    names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];lines=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    (Q/'Program.cs').write_text(template.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(lines)),encoding='utf-8')
    out=Q/'runner';out.mkdir(exist_ok=True);refs=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(out/'QaCodecRunner.exe')+'"','-pdb:"'+str(out/'QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [refs/'mscorlib.dll',refs/'System.dll',refs/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    print(json.dumps(dict(normal_cases=len(oracle['cases']),historical_leaves=len(oracle['historical65_leaf_oracle']),positive_validate_cases=2,positive_try_admit_cases=2,expected_oracle_before_build=True,selected_sha256=sha(candidate)),indent=2))
