from review_setup import *
import copy,re
def normal_expected(snapshot):
    x=copy.deepcopy(snapshot)
    x['dlcExpansions'].sort(key=lambda r:r['defName']);x['activeMods'].sort(key=lambda r:r['loadOrder']);x['loadedAssemblies'].sort(key=lambda r:(r['packageId'],r['assemblyName']))
    for records in x['defFamilies'].values():records.sort(key=lambda r:r['defName'])
    for t in x['defFamilies']['thingDefs']:
        t.get('stats',[]).sort(key=lambda r:r['statDef']);t.get('costList',[]).sort(key=lambda r:r['thingDef']);t.get('stuffCategories',[]).sort()
    return x
def main():
    # Historical input design only; no prior runner/binary/PASS is executed or inherited.
    old=(PREVQ/'prepare_runner.py').read_text(encoding='utf-8-sig').replace('scratch/EngineGate05R5Codec/Harness/bin/Debug/net472/Newtonsoft.Json.dll','scratch/EngineGate05R6CodecContract/Harness/bin/Debug/net472/Newtonsoft.Json.dll').replace('0e6b7cca-e02c-4af5-97da-5de31ec7aec3','b3481641-2711-4b0e-96dd-db0983c2b689')
    ns=dict(globals(),PREP=ROOT/'QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008');defs=[n for n in ast.parse(old).body if isinstance(n,ast.FunctionDef) and n.name=='main'];exec(compile(ast.Module(body=defs,type_ignores=[]),'historical_input_layout_only','exec'),ns);ns['main']()
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json');base=oracle['cases']['BASE'];base['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R6_CODEC_CONTRACT','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5']
    base['activeMods'].reverse();base['dlcExpansions']=[dict(defName='ExampleDlcB',status='Inactive',linkedMod=None,statusDescription='정상 부재'),dict(defName='ExampleDlcA',status='Active',linkedMod='example.core',statusDescription='정상 활성')]
    second=copy.deepcopy(base['loadedAssemblies'][0]);second.update(packageId='example.z',assemblyName='Example.Second',sizeBytes=2048);base['loadedAssemblies'].insert(0,second)
    t=base['defFamilies']['thingDefs'][0];t['stats'].insert(0,dict(statDef='Weight',value=2.345678));t['costList'].insert(0,dict(thingDef='Zinc',count=4));t['comps']=['Example.CompZ','Example.CompA','Example.CompZ']
    second=copy.deepcopy(t);second.update(defName='ZExampleThing',label='다른 정상 항목');base['defFamilies']['thingDefs'].insert(0,second)
    for name in ['OPTIONAL_NULL','OPTIONAL_EMPTY','OPTIONAL_MISSING']:
        x=oracle['cases'][name];x['capabilityFlags']=base['capabilityFlags'];x['activeMods']=copy.deepcopy(base['activeMods']);x['dlcExpansions']=copy.deepcopy(base['dlcExpansions']);x['loadedAssemblies']=copy.deepcopy(base['loadedAssemblies'])
    revision=copy.deepcopy(base);revision['activeMods'][0]['modVersion']='1.2';revision['defFamilies']['thingDefs'][1]['costStuffCount']=11;revision['defFamilies']['weatherDefs'][0]['rainRate']=0.5;oracle['cases']['NORMAL_REVISION_B']=revision
    perm=copy.deepcopy(base);perm['activeMods'].reverse();perm['dlcExpansions'].reverse();perm['loadedAssemblies'].reverse()
    for records in perm['defFamilies'].values():records.reverse()
    for thing in perm['defFamilies']['thingDefs']:thing['stats'].reverse();thing['costList'].reverse();thing['stuffCategories'].reverse()
    oracle['cases']['NORMAL_SET_ORDER']=perm
    oracle['expected_canonical_cases']={name:normal_expected(x) for name,x in oracle['cases'].items()};oracle['created_at']=now();oracle['r6_fresh_expected_policy']='Declared distinct normal set keys and loadOrder normalize;ordered verbs/stages/comps/multiplicity unchanged;transport false retains source order. Expected semantics independently specified before build/run.';oracle['positive_contract_cases']=['BASE','NORMAL_REVISION_B']
    for row in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',row['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        row['expected_value']=value;row['r6_json_path']=row['r5_json_path'];row['historical_path_label']='r5_json_path is stable historical DTO mapping name,not R5 candidate evidence'
    write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    cfg=load(Q/'QA_RUNNER_CONFIG.json');cfg['allowed_production_calls']=['SerializeCanonicalJson(manifest,bool)','DeserializeCanonicalJson','CanonicalNormalize','ValidateContract(fully declared positive manifest,out reason)'];cfg['forbidden_calls']+=['cache properties','R6 TC11','R6 TC13','old QA runner','invalid/missing-required rejection'];cfg['case_scope']='Fresh R6 normal contract inputs;historical R5 design referenced only';write(Q/'QA_RUNNER_CONFIG.json',cfg)
    print(json.dumps(dict(r6_expected_normal_cases=6,historical_leaf65=65,positive_helper_cases=2,selected_sha=cfg['selected_sha256'],oracle_before_build=True),indent=2))
if __name__=='__main__':main()
