from review_setup import *
import copy,re
SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
def headers(x):
    x=copy.deepcopy(x);x['contentContractVersion']='ADR-006B-v5-R12';x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R12_PACKAGE_ORDER','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5'];return x
def normal(x):
    x=copy.deepcopy(x)
    for m in x['activeMods']:m.setdefault('modVersion',None)
    x['dlcExpansions'].sort(key=lambda r:r['defName']);x['activeMods'].sort(key=lambda r:r['loadOrder']);x['loadedAssemblies'].sort(key=lambda r:(r['packageId'],r['assemblyName'],r['mvid'],r['sha256']))
    for rows in x['defFamilies'].values():rows.sort(key=lambda r:r['defName'])
    for t in x['defFamilies']['thingDefs']:
        t.get('stats',[]).sort(key=lambda r:(r['statDef'],r['value']));t.get('costList',[]).sort(key=lambda r:(r['thingDef'],r['count']));t.get('stuffCategories',[]).sort()
    x['patchSettingsDisposition']['totalObservedPatches']=sum(m['patchCount'] for m in x['activeMods'] if m['patchCount']>0)
    return x
def schema():
    text=SOURCE.read_text(encoding='utf-8-sig');classes=list(re.finditer(r'^    public class (\w+)\s*$',text,re.M));result={}
    constants={'ContentProfileProvider.MANIFEST_SCHEMA_VERSION':'ADR-006B-v5','ContentProfileProvider.CONTENT_CONTRACT_VERSION':'ADR-006B-v5-R12','ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE':'POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5','ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS':'TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1','POLICY_SCHEMA_VERSION':'WE-PACKAGE-POLICY-V1'}
    for i,c in enumerate(classes):
        body=text[c.end():classes[i+1].start() if i+1<len(classes) else len(text)];fields=[]
        for f in re.finditer(r'^        public ([\w?<>]+) (\w+) = ([^;]+);\s*$',body,re.M):
            ty,name,expr=f.groups()
            if expr in constants:default=constants[expr]
            elif expr=='null':default=None
            elif expr in ['true','false']:default=expr=='true'
            elif expr.startswith('"'):default=json.loads(expr)
            elif expr.startswith('new List<'):default=[]
            elif expr.startswith('new '):default={}
            elif ty in ['int','long']:default=int(expr)
            elif ty=='float':default=float(expr.rstrip('f'))
            else:raise ValueError((ty,name,expr))
            fields.append(dict(name=name,type=ty,default=default,line=text[:c.end()+f.start()].count('\n')+1))
        result[c.group(1)]=fields
    assert len(result['ContentProfileManifest'])==14 and len(result['PackagePolicyCheckResult'])==9
    return result
def fill(value,ty,s):
    if value is None:return None
    if ty.startswith('List<'):return [fill(v,ty[5:-1],s) for v in value]
    ty=ty.rstrip('?')
    if ty not in s:return copy.deepcopy(value)
    assert not set(value)-{f['name'] for f in s[ty]},(ty,set(value))
    return {f['name']:fill(value.get(f['name'],copy.deepcopy(f['default'])),f['type'],s) for f in s[ty]}
if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    s=schema();write(Q/'REFERENCE_DTO_SCHEMA.json',dict(at=now(),source=row(SOURCE),types=s,reference_spec='Frozen-source ordered field names/defaults/types;own JObject writer,no candidate DTO/codec/normalizer calls for reference;finite float32 Single R-format via standard Json.NET,Int32/Int64 exact,Unicode literal minimal,UTF8noBOM,compact fixed field order',scope='Prospectively specified before final build and every candidate call',library_independence_limit='Shares pinned standard Json.NET primitive formatting dependency;does not share candidate codec/DTO constructors/reflection/output'))
    oracle=copy.deepcopy(load(PREVQ/'INPUT_EXPECTED_SEMANTICS.json'));oracle.pop('policy_cases');oracle.pop('master_prospective_selection',None)
    oracle.update(created_at=now(),scope='R12 normal package-order and positive pure codec only',prior_PASS_inherited=False,reference_dto_schema=row(Q/'REFERENCE_DTO_SCHEMA.json'))
    oracle['cases']={n:headers(x) for n,x in oracle['cases'].items()};oracle['expected_canonical_cases']={n:fill(normal(x),'ContentProfileManifest',s) for n,x in oracle['cases'].items()}
    oracle['expected_transport_cases']={n:fill(x,'ContentProfileManifest',s) for n,x in oracle['cases'].items()}
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r12_json_path']=r['r5_json_path']
    prep=load(PREP/'NORMAL_ORDER_REFERENCE_ORACLE.json');policy_cases={};refs=Q/'policy_references';refs.mkdir()
    for name,c in prep['cases'].items():
        raw=copy.deepcopy(c['expected_input_policy']);blob=json.dumps(c['expected_policy_canonical'],ensure_ascii=False,separators=(',',':')).encode();digest=hashlib.sha256(blob).hexdigest().upper();assert digest==c['expected_digest']==sha(Path(c['policy_reference']['path']))
        p=refs/(name+'.canonical.utf8.json');p.write_bytes(blob)
        unbound=fill(headers(c['independent_unbound_input_manifest_template']),'ContentProfileManifest',s)
        bound=fill(headers(c['independent_policy_bearing_freshoriginal_input_template']),'ContentProfileManifest',s)
        admitted=fill(headers(c['expected_admitted_content_and_caller_after']),'ContentProfileManifest',s)
        assert bound['packagePolicyDisposition']['policyDigest']==digest and admitted==fill(normal(bound),'ContentProfileManifest',s)
        check=copy.deepcopy(c['expected_full_check_current_carrier_plan']);check['rawPhysicalPackages']=[m['packageId'].lower() for m in c['independent_raw_inventory_literal']]
        policy_cases[name]=dict(input_declaration=raw,expected_canonical_declaration=c['expected_policy_canonical'],expected_policy_record=dict(policyId=raw['policyId'],revision=raw['revision'],admittedPackageIds=raw['admittedPackageIds'],policyDigest=digest),independent_observed_manifest=unbound,independent_bound_fresh_manifest=bound,expected_bound_transport_manifest=bound,expected_admitted_manifest=admitted,expected_check_result=check,expected_digest=digest,expected_json=blob.decode(),expected_escaped_policyId=json.dumps(raw['policyId'],ensure_ascii=False)[1:-1],expected_escaped_revision=json.dumps(raw['revision'],ensure_ascii=False)[1:-1],reference=row(p),independent_expected_execution_records=c['independent_expected_execution_records'])
    oracle['policy_cases']=policy_cases;oracle['relations']=prep['relations'];oracle['expected_policies_derived_from_actual']=False;write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R12PackageOrder/Harness/bin/Debug/net472/Newtonsoft.Json.dll';allowed=[candidate,newton]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='ad4caf3c-88bc-4971-9c2a-ab78eae395e5',allowed_managed=[row(p) for p in allowed],allowed_production_calls=['normal DTO/codec/Normalize','current policy Serialize/Deserialize/Escape/digest/conversion','four fully matching Check/two admission overloads','positive structural controls'],forbidden_calls=['configuration/provider/cache/properties/game/native/operator/oldrunner/negative/adverse'],oracle_before_build=True))
    prior=(PREVQ/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig');start=prior.index('    static void RunPolicyDeclarations(');end=prior.index('  static bool Compared(',start)
    template=prior[:start]+(Q/'ReferenceCodec.cs.txt').read_text(encoding='utf-8-sig')+'\n'+(Q/'OrderChecks.cs.txt').read_text(encoding='utf-8-sig')+'\n'+prior[end:]
    template=template.replace('R11','R12').replace('policy-encoding','package-order')
    template=template.replace('System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);return Run(args[1]);','System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);PrepareReferenceBytes();return Run(args[1]);')
    template=template.replace('Compare(p.Value,JToken.FromObject(transportDecoded)','Compare(input["expected_transport_cases"][p.Name],JToken.FromObject(transportDecoded)')
    template=template.replace('Check("FRESH_ORIGINAL_TRUE_"+p.Name,Compared(freshOriginalChecks)', 'Check("FRESH_ORIGINAL_TRUE_"+p.Name,Compared(freshOriginalChecks)&&freshOriginalTrue==References["generic."+p.Name]')
    template=template.replace('Check("NORMAL_"+p.Name+"_SEMANTICS",Compared(checks)', 'Check("NORMAL_"+p.Name+"_SEMANTICS",Compared(checks)&&bytes==References["generic."+p.Name]')
    template=template.replace('Check("TRANSPORT_"+p.Name+"_SEMANTICS",Compared(transportChecks)','Check("TRANSPORT_"+p.Name+"_SEMANTICS",Compared(transportChecks)&&transport==References["transport."+p.Name]')
    template=template.replace('var ao=actual as JObject;if(ao==null)throw new Exception("Object mismatch "+path);','var ao=actual as JObject;if(ao==null)throw new Exception("Object mismatch "+path);if(eo.Count!=ao.Count)throw new Exception("Full object shape mismatch "+path);')
    template=template.replace('var cfg=JObject.Parse(', 'Save("ACTUAL_PROCESS_CONTEXT.json",JsonConvert.SerializeObject(new{run_id=runId,argv=Environment.GetCommandLineArgs(),cwd=Environment.CurrentDirectory,pid=System.Diagnostics.Process.GetCurrentProcess().Id,culture=System.Threading.Thread.CurrentThread.CurrentCulture.Name,runtime=Environment.Version.ToString(),at=DateTimeOffset.Now.ToString("o"),reference_bytes_materialized_before_candidate_calls=true},Formatting.Indented));\n    var cfg=JObject.Parse(')
    (Q/'RunnerTemplate.cs.txt').write_text(template,encoding='utf-8');names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    program=template.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(resolver));assert not any(n in program for n in ['ConfigureExpectedPackagePolicy','ClearConfiguredExpectedPackagePolicy','GetActualContent','ComputeActualContent','InvalidateCache']);(Q/'Program.cs').write_text(program,encoding='utf-8')
    out=Q/'runner';out.mkdir();fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(out/'QaCodecRunner.exe')+'"','-pdb:"'+str(out/'QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [fw/'mscorlib.dll',fw/'System.dll',fw/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),reference_formatter_source=row(Q/'ReferenceCodec.cs.txt'),order_controls_source=row(Q/'OrderChecks.cs.txt'),policy_references=[row(p) for p in sorted(refs.iterdir())],generic_cases=12,order_cases=14,prospective_semantic_and_byte_spec_before_build=True,reference_materialization='At Main before NoInlining candidate Run;uses own schema/literal inputs and pinned primitive Json.NET only,no candidatecalls/output/reflection',candidate_calls_so_far=0,full_gate_e2=False))
    print(json.dumps(dict(generic_cases=12,order_cases=14,schema_types=len(s),root_fields=len(s['ContentProfileManifest']),policy_references=14,candidate_calls=0)))
