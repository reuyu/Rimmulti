from review_setup import *
import copy,re
def expected_normal(snapshot):
    x=copy.deepcopy(snapshot)
    # Canonical order only. Compatibility range and actual content version never alias.
    x['dlcExpansions'].sort(key=lambda r:r['defName']);x['activeMods'].sort(key=lambda r:(r['loadOrder'],r['packageId']));x['loadedAssemblies'].sort(key=lambda r:(r['packageId'],r['assemblyName'],r['mvid'],r['sha256']))
    for rows in x['defFamilies'].values():rows.sort(key=lambda r:r['defName'])
    for t in x['defFamilies']['thingDefs']:
        t.get('stats',[]).sort(key=lambda r:(r['statDef'],r['value']));t.get('costList',[]).sort(key=lambda r:(r['thingDef'],r['count']));t.get('stuffCategories',[]).sort()
    return x
if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    oracle=copy.deepcopy(load(PREVQ/'INPUT_EXPECTED_SEMANTICS.json'));oracle.update(created_at=now(),scope='Fresh R8 normal synthetic codec inputs;previous layouts design only;semantic failures retained')
    for x in oracle['cases'].values():
        x['contentContractVersion']='ADR-006B-v5-R8';x['modPatchSupportStatus']='TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1';x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R8_SUPPORTED_DISPOSITION','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5']
        for m in x['activeMods']:m.update(compatibilityVersionRange='1.6',patchDisposition='COUNT_OBSERVED_RAW_AST_EXCLUDED',settingsDisposition='USER_MOD_SETTINGS_EXCLUDED')
        x['patchSettingsDisposition']=dict(patchPolicy='COUNT_OBSERVED_RAW_AST_EXCLUDED',settingsPolicy='USER_MOD_SETTINGS_EXCLUDED',supportedModBoundary='POC_DECLARED_PACKAGES_ONLY',totalObservedPatches=sum(m['patchCount'] for m in x['activeMods']))
    unknown=copy.deepcopy(oracle['cases']['BASE']);unknown['activeMods'][1]['modVersion']=None
    oracle['cases']['OPTIONAL_UNKNOWN_VERSION']=unknown
    oracle['expected_canonical_cases']={name:expected_normal(x) for name,x in oracle['cases'].items()}
    oracle.pop('r7_fresh_expected_policy',None);oracle['r8_fresh_expected_policy']='Canonical ordering preserves material values and legitimate optional unknown actual modVersion. compatibilityVersionRange=1.6 is a separate compatibility declaration,not observed mod content version. Explicit policies/count are fixture data,not trusted source observation. No producer TC16 cross-fill in expected values.'
    oracle['positive_contract_cases']=['BASE','NORMAL_REVISION_B'];oracle['positive_try_admit_cases']=['BASE','NORMAL_REVISION_B'];oracle['optional_unknown_version_case']='Generic transport/canonical only;no rejection/requiredness/helper call'
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r8_json_path']=r['r5_json_path'];r['historical_path_label']='Stable historical DTO mapping;no previous candidate PASS'
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R8SupportedDisposition/Harness/bin/Debug/net472/Newtonsoft.Json.dll';allowed=[candidate,newton]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    cfg=dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='348b49f3-74f8-4643-9a2f-4a1dc5fb9a41',allowed_managed=[dict(path=str(p),sha256=sha(p)) for p in allowed],allowed_production_calls=['DTO constructors/fields','SerializeCanonicalJson(manifest,bool)','DeserializeCanonicalJson','CanonicalNormalize','positive ValidateContract','positive TryAdmitManifest'],forbidden_calls=['GetActual*/ComputeActual*','cache/InvalidateCache/game/native/operator','old A/QA runner','missing-required/rejection/tied/adverse'],case_scope='Normal7cases;positive BASE/revision fully declared;optional unknown version generic only;honest semantic FAILs retained')
    write(Q/'QA_RUNNER_CONFIG.json',cfg)
    s=(PREVQ/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig').replace('R7','R8').replace('content-admission','supported-disposition')
    s=s.replace('static readonly List<object> Results=new List<object>();','static readonly List<object> Results=new List<object>();static int Failures=0;\n  static bool Compared(List<object> rows){return rows.All(r=>(bool)r.GetType().GetProperty("matched").GetValue(r));}')
    s=s.replace('if(!ok)throw new InvalidOperationException(id+": "+detail);','if(!ok)Failures++;')
    s=s.replace('if(!ok)throw new Exception("Semantic mismatch "+path);','if(!ok)Console.WriteLine("SEMANTIC_FAIL "+path+" expected="+expected.ToString(Formatting.None)+" actual="+actual.ToString(Formatting.None));')
    s=s.replace('string bytes=ContentProfileProvider.SerializeCanonicalJson(dto,true);','Check("TRANSPORT_"+p.Name+"_SEMANTICS",Compared(transportChecks),"False transport preserves original normal input values/order");\n      Check("NORMALIZE_"+p.Name+"_SEMANTICS",Compared(normalizeChecks),"Canonical order must preserve separately declared normal material meaning and optional unknown content version");\n      string bytes=ContentProfileProvider.SerializeCanonicalJson(dto,true);')
    s=s.replace('Check("NORMAL_"+p.Name+"_SEMANTICS",true,','Check("NORMAL_"+p.Name+"_SEMANTICS",Compared(checks),')
    s=s.replace('freshCanonical==bytes&&freshAfter==bytes,','freshCanonical==bytes&&freshAfter==bytes&&Compared(normalizeChecks),')
    s=s.replace('admitted&&admitReason==""&&admittedJson==bytes&&admitAfter==bytes,','admitted&&admitReason==""&&admittedJson==bytes&&admitAfter==bytes&&Compared(admitChecks),')
    s=s.replace('string[] types={"DlcExpansionRecord"','string[] types={"ModPatchSettingsDispositionRecord","DlcExpansionRecord"')
    marker='var typeRows=new List<object>();'
    version='''var unknownMod=decoded["OPTIONAL_UNKNOWN_VERSION"].SelectToken("activeMods[0]");
    Check("C_VERSION_OPTIONAL_UNKNOWN",unknownMod["modVersion"].Type==JTokenType.Null&&unknownMod["compatibilityVersionRange"].Value<string>()=="1.6","Legitimate optional unknown actual modVersion must stay null;compatibility range remains separately declared");
    Save("VERSION_MEANING_OBSERVATIONS.json",JsonConvert.SerializeObject(new{case_id="OPTIONAL_UNKNOWN_VERSION",expected_actual_mod_version=(string)null,expected_compatibility_range="1.6",actual_mod=unknownMod,input_scope="NORMAL_GENERIC_DTO_TRANSPORT_ONLY",positive_helper_invoked_for_unknown_case=false},Formatting.Indented));
    '''
    assert s.count(marker)==1;s=s.replace(marker,version+marker)
    s=s.replace('results=Results,forbidden_provider','results=Results,failed_assertions=Failures,forbidden_provider')
    s=s.replace('cache calls0.");return 0;','cache calls0. FAIL assertions="+Failures);return Failures==0?0:1;')
    assert 'if(!ok)throw' not in s and 'return Failures==0?0:1;' in s
    (Q/'RunnerTemplate.cs.txt').write_text(s,encoding='utf-8');names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    (Q/'Program.cs').write_text(s.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(resolver)),encoding='utf-8')
    out=Q/'runner';out.mkdir(exist_ok=True);refs=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(out/'QaCodecRunner.exe')+'"','-pdb:"'+str(out/'QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [refs/'mscorlib.dll',refs/'System.dll',refs/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    print(json.dumps(dict(cases=len(oracle['cases']),historical_leaves=65,positive_helper_cases=2,unknown_version_preserved_in_expected=True,oracle_before_build=True)))
