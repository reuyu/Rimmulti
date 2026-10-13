from review_setup import *
import copy,re
def expected_normal(snapshot):
    x=copy.deepcopy(snapshot)
    # Explicit constructor policy for an absent OPTIONAL actual version,never infer a version.
    for m in x['activeMods']:
        if 'modVersion' not in m:m['modVersion']=None
    x['dlcExpansions'].sort(key=lambda r:r['defName']);x['activeMods'].sort(key=lambda r:(r['loadOrder'],r['packageId']));x['loadedAssemblies'].sort(key=lambda r:(r['packageId'],r['assemblyName'],r['mvid'],r['sha256']))
    for rows in x['defFamilies'].values():rows.sort(key=lambda r:r['defName'])
    for t in x['defFamilies']['thingDefs']:
        t.get('stats',[]).sort(key=lambda r:(r['statDef'],r['value']));t.get('costList',[]).sort(key=lambda r:(r['thingDef'],r['count']));t.get('stuffCategories',[]).sort()
    return x
def core(x):return next(m for m in x['activeMods'] if m['loadOrder']==0)
if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    prior=PREVQ/'INPUT_EXPECTED_SEMANTICS.json';oracle=copy.deepcopy(load(prior));oracle.update(created_at=now(),scope='Fresh R9 normal targeted version meaning +compact supported controls;prior R8 oracle is rationale,not executed old evidence',original_r8_oracle_path=str(prior),original_r8_oracle_sha256=sha(prior))
    for x in oracle['cases'].values():
        x['contentContractVersion']='ADR-006B-v5-R9';x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R9_VERSION_MEANING','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5']
    for name,compat,actual in [('KNOWN_DISTINCT_VERSION','1.5;1.6','2.1.0'),('REVERSE_NO_INFERENCE_VERSION','','2.1.0'),('OPTIONAL_EMPTY_VERSION','1.6',''),('GENERIC_VERSION_TEXT','1.6; α \t\n','内容:2.1.0 / (null) \t\n')]:
        x=copy.deepcopy(oracle['cases']['BASE']);core(x).update(compatibilityVersionRange=compat,modVersion=actual);oracle['cases'][name]=x
    missing=copy.deepcopy(oracle['cases']['OPTIONAL_UNKNOWN_VERSION']);del core(missing)['modVersion'];oracle['cases']['OPTIONAL_MISSING_VERSION']=missing
    oracle['expected_canonical_cases']={name:expected_normal(x) for name,x in oracle['cases'].items()}
    targets=['OPTIONAL_UNKNOWN_VERSION','KNOWN_DISTINCT_VERSION','REVERSE_NO_INFERENCE_VERSION','OPTIONAL_EMPTY_VERSION','GENERIC_VERSION_TEXT','OPTIONAL_MISSING_VERSION']
    oracle['target_version_oracle']={name:[dict(loadOrder=m['loadOrder'],packageId=m['packageId'],compatibilityVersionRange=m['compatibilityVersionRange'],modVersion=m['modVersion']) for m in oracle['expected_canonical_cases'][name]['activeMods']] for name in targets}
    oracle.pop('r8_fresh_expected_policy',None);oracle['r9_fresh_expected_policy']='Unknown optional actual content version stays null,empty remains empty,known content and compatibility strings remain distinct;reverse inference prohibited;optional missing constructor default is null;normal canonical ordering only. Expectations fixed before final build,not derived from production outputs.'
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r9_json_path']=r['r5_json_path'];r['historical_path_label']='Stable historical DTO mapping;fresh R9 candidate observation only'
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R9VersionMeaning/Harness/bin/Debug/net472/Newtonsoft.Json.dll';allowed=[candidate,newton]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    cfg=dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='12aa23c7-3ec0-4b6a-bbb1-4a036127c5da',allowed_managed=[dict(path=str(p),sha256=sha(p)) for p in allowed],allowed_production_calls=['DTO constructors/fields','SerializeCanonicalJson(manifest,bool)','DeserializeCanonicalJson','CanonicalNormalize','positive ValidateContract','positive TryAdmitManifest'],forbidden_calls=['GetActual*/ComputeActual*','cache/InvalidateCache/game/native/operator','old A/QA runner','missing-required/rejection/tied/adverse'],case_scope='12normalcases/6targetedversioncases;positivehelperBASE/revisiononly;fresh original Serialize(true) checked separately')
    write(Q/'QA_RUNNER_CONFIG.json',cfg)
    s=(PREVQ/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig').replace('R8','R9').replace('supported-disposition','version-meaning')
    s=s.replace('static bool Compared(','''static readonly List<object> TargetResults=new List<object>();
  static JArray VersionView(JToken d){return new JArray(((JArray)d["activeMods"]).OrderBy(m=>m["loadOrder"].Value<int>()).Select(m=>new JObject{["loadOrder"]=m["loadOrder"],["packageId"]=m["packageId"],["compatibilityVersionRange"]=m["compatibilityVersionRange"],["modVersion"]=m["modVersion"]}));}
  static bool Compared(''')
    marker='ContentProfileProvider.CanonicalNormalize(dto);'
    fresh='''var freshOriginalDto=ContentProfileProvider.DeserializeCanonicalJson(before);string freshOriginalTrue=ContentProfileProvider.SerializeCanonicalJson(freshOriginalDto,true);
      var freshOriginalDecoded=ContentProfileProvider.DeserializeCanonicalJson(freshOriginalTrue);var freshOriginalChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(freshOriginalDecoded),"",freshOriginalChecks);
      Check("FRESH_ORIGINAL_TRUE_"+p.Name,Compared(freshOriginalChecks),"Serialize(true) independently checked from a fresh original input before any explicit Normalize on this instance");
      Save(p.Name+".fresh_original.canonical.json",freshOriginalTrue);Save(p.Name+".fresh_original_checks.json",JsonConvert.SerializeObject(freshOriginalChecks,Formatting.Indented));
      '''
    assert s.count(marker)==1;s=s.replace(marker,fresh+marker)
    marker='outputs[p.Name]=bytes;decoded[p.Name]=semantics;'
    targeted='''
      var targetOracle=input["target_version_oracle"] as JObject;
      if(targetOracle[p.Name]!=null){var versionChecks=new List<object>();
        foreach(var view in new[]{VersionView(JToken.FromObject(transportDecoded)),VersionView(JToken.FromObject(dto)),VersionView(JToken.FromObject(freshOriginalDecoded)),VersionView(semantics),VersionView(JToken.FromObject(ContentProfileProvider.DeserializeCanonicalJson(repeat)))})Compare(targetOracle[p.Name],view,"versions",versionChecks);
        bool targetOk=Compared(versionChecks);Check("TARGET_VERSION_"+p.Name,targetOk,"Independent unknown/null/empty/known/reverse/generic version meaning across false,Normalize,fresh true,decoded reconstruction");
        TargetResults.Add(new{case_id=p.Name,status=targetOk?"PASS":"FAIL",expected=targetOracle[p.Name],actual=VersionView(semantics),views_compared=5,positive_required_helper_invoked=false});Save(p.Name+".version_checks.json",JsonConvert.SerializeObject(versionChecks,Formatting.Indented));
      }
      '''
    assert s.count(marker)==1;s=s.replace(marker,marker+targeted)
    s=s.replace('var typeRows=new List<object>();','Save("TARGETED_VERSION_RESULTS.json",JsonConvert.SerializeObject(TargetResults,Formatting.Indented));\n    var typeRows=new List<object>();')
    (Q/'RunnerTemplate.cs.txt').write_text(s,encoding='utf-8');names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    (Q/'Program.cs').write_text(s.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(resolver)),encoding='utf-8')
    out=Q/'runner';out.mkdir(exist_ok=True);refs=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(out/'QaCodecRunner.exe')+'"','-pdb:"'+str(out/'QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [refs/'mscorlib.dll',refs/'System.dll',refs/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    print(json.dumps(dict(normalcases=len(oracle['cases']),targetcases=len(targets),historical65=65,oracle_before_build=True,no_cross_inference_expected=True,fresh_original_true_separate=True)))
