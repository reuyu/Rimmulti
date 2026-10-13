from review_setup import *
import copy,re
SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
def headers(x):
    x=copy.deepcopy(x);x['contentContractVersion']='ADR-006B-v5-R14';x['capabilityFlags']=['TACTICAL_PROBE_V4','READ_ONLY','SIMULATION','GATE05_R14_POLICY_CAPTURE_PUBLICATION','ADR006B_LOSSLESS_CANONICAL_CONTENT_V5'];return x
if __name__=='__main__':
    assert not (Q/'Program.cs').exists()
    helper=(ROOT/'QA-Tactical-Engine/GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009/prepare_runner.py').read_text(encoding='utf-8-sig').replace('ADR-006B-v5-R12','ADR-006B-v5-R14');nodes=[n for n in ast.parse(helper).body if isinstance(n,ast.FunctionDef) and n.name in {'normal','schema','fill'}];ns=dict(globals());exec(compile(ast.Module(body=nodes,type_ignores=[]),'audited_frozen_reference_functions_text_only','exec'),ns);types=ns['schema']();normal=ns['normal'];fill=ns['fill']
    write(Q/'REFERENCE_DTO_SCHEMA.json',dict(at=now(),source=row(SOURCE),types=types,reference_spec='Prospective orderedfields/defaults/types independentliterals;own standardJsonNET primitiveformatter only;candidatecodec/constructor/reflection/output notoracle',shared_primitive_jsonnet_limit=True))
    oracle=copy.deepcopy(load(PREVQ/'INPUT_EXPECTED_SEMANTICS.json'));oracle.update(created_at=now(),scope='R14 positive lifecycle/Invalidate+1/currentmatchingstandalonecore/globalempty/purecodecorderpolicyversion',prior_PASS_inherited=False,reference_dto_schema=row(Q/'REFERENCE_DTO_SCHEMA.json'))
    oracle['cases']={n:headers(x) for n,x in oracle['cases'].items()};oracle['expected_canonical_cases']={n:fill(normal(x),'ContentProfileManifest',types) for n,x in oracle['cases'].items()};oracle['expected_transport_cases']={n:fill(x,'ContentProfileManifest',types) for n,x in oracle['cases'].items()}
    for r in oracle['historical65_leaf_oracle']:
        value=oracle['expected_canonical_cases']['BASE']
        for part in re.findall(r'[^.\[\]]+',r['r5_json_path']):value=value[int(part)] if part.isdigit() else value[part]
        r['expected_value']=value;r['r14_json_path']=r['r5_json_path']
    refs=Q/'policy_references';refs.mkdir()
    for n,c in oracle['policy_cases'].items():
        for k in ['independent_observed_manifest','independent_bound_fresh_manifest','expected_bound_transport_manifest','expected_admitted_manifest']:c[k]=fill(headers(c[k]),'ContentProfileManifest',types)
        p=refs/(n+'.canonical.utf8.json');p.write_bytes(c['expected_json'].encode());assert sha(p)==c['expected_digest'];c['reference']=row(p)
    for c in oracle['cache_policies'].values():c['expected_full_manifest']=fill(headers(c['expected_full_manifest']),'ContentProfileManifest',types);c['expected_contract']='ADR-006B-v5-R14'
    oracle['lifecycle_rule']=dict(configuration_generation_clr='System.Int64',initial=0,configure_record_increment=1,configure_declaration_increment=1,same_policy_configure_increment=1,clear_increment=1,invalidate_increment=1,expected_main_sequence=[0,1,2,3,4,5],expected_secondary_sequence=[0,1],cached_at='ObservedUTCdiagnosticonlynotworldordering',operational_stamp_not_canonical_revision=True,source_anchors=[3259,3267],r13_pluszero_not_adopted=True);write(Q/'INPUT_EXPECTED_SEMANTICS.json',oracle)
    write(Q/'API_AND_GENERATION_RECONCILIATION.json',dict(at=now(),source=row(SOURCE),actual_rule=oracle['lifecycle_rule'],source_anchors=dict(header=1536,public_parameterless_manifest=[2468,2475],public_caller_policy_manifest=[2478,2484],fingerprint_capture_guard=[3011,3045],invalidate_plusone=[3259,3267]),actual_normal_APIs='SamepublicnormalCore/entry/currentstamp/property/carrier signatures as frozenR13 confirmedsource;R14headers andInvalidate+1 newlyadoptedbeforebuildcalls',public_actualmanifest_overloads='STATIC_ONLY_UNINVOKED_PROVIDER_ORIGIN_FINALSTAMP_REQUIRED_REVIEW',newbyteheaders_adopted_beforecalls=True,original_R13_evidence_oracle_immutable=True))
    cache=(PREVQ/'CacheChecks.cs.txt').read_text(encoding='utf-8-sig')
    replacements={
      'EmptyCore("CACHE_INVALIDATE_B",core,2,':'EmptyCore("CACHE_INVALIDATE_B",core,3,',
      'PublishMatching("CACHE_B_AFTER_INVALIDATE_G2",core,2,':'PublishMatching("CACHE_B_AFTER_INVALIDATE_G3",core,3,',
      'EmptyCore("CACHE_SAME_POLICY_B",core,3,':'EmptyCore("CACHE_SAME_POLICY_B",core,4,',
      'PublishMatching("CACHE_B_G3",core,3,':'PublishMatching("CACHE_B_G4",core,4,',
      'EmptyCore("CACHE_CLEAR",core,4,':'EmptyCore("CACHE_CLEAR",core,5,',
      'EmptyCore("CACHE_MAIN_UNAFFECTED",core,4,':'EmptyCore("CACHE_MAIN_UNAFFECTED",core,5,',
      'GlobalEmpty("GLOBAL_INVALIDATE",2,':'GlobalEmpty("GLOBAL_INVALIDATE",3,',
      'GlobalEmpty("GLOBAL_SAME_B",3,':'GlobalEmpty("GLOBAL_SAME_B",4,',
      'GlobalEmpty("GLOBAL_CLEAR",4,':'GlobalEmpty("GLOBAL_CLEAR",5,'}
    for a,b in replacements.items():assert a in cache,a;cache=cache.replace(a,b)
    (Q/'CacheChecks.cs.txt').write_text(cache,encoding='utf-8')
    template=(PREVQ/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig');first=template.index('  static readonly List<object> CacheCalls=');last=template.index('  static bool Compared(',first);template=template[:first]+cache+'\n'+template[last:]
    template=template.replace('R13','R14').replace('policy-cache-lifecycle','policy-capture-publication')
    template=template.replace('ContentProfileProvider.','ObservedProvider.')
    template=template.replace('  static bool Compared(', (Q/'ObservedProvider.cs.txt').read_text(encoding='utf-8-sig')+'\n  static bool Compared(')
    template=template.replace('forbidden_provider_cache_game_native_operator_calls=0','actual_admitted_call_ledger_file="ACTUAL_ADMITTED_CALL_LEDGER.json",actual_direct_or_grouped_stage_records=CacheCalls.Count')
    template=template.replace('Save("NORMAL_RESULTS.json",', 'Save("ACTUAL_ADMITTED_CALL_LEDGER.json",JsonConvert.SerializeObject(CacheCalls,Formatting.Indented));\n    Save("NORMAL_RESULTS.json",')
    template=template.replace('Actual provider/game/native/operator/cache calls0.', 'Actual admitted direct or grouped stages are retained in ACTUAL_ADMITTED_CALL_LEDGER.json.')
    (Q/'RunnerTemplate.cs.txt').write_text(template,encoding='utf-8')
    candidate=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';newton=FROZEN/'scratch/EngineGate05R14PolicyCapturePublication/Harness/bin/Debug/net472/Newtonsoft.Json.dll';allowed=[candidate,newton]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(root=str(Q),selected=str(candidate),selected_sha256=sha(candidate),selected_mvid='acab0270-bc98-4d17-b920-9941950ff024',allowed_managed=[row(p) for p in allowed],execution_scope='Explicitdirectpurecodec API wrappers;normalcorecurrentmatching+validglobalempty lifecycle only',globalactual_collector_native_publication_adverse_allowed=False))
    names=['WarEconomy.WorkerBridge.PoC','Newtonsoft.Json','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine','0Harmony'];resolver=['{'+json.dumps(n)+', @"'+str(p).replace('"','""')+'"}' for n,p in zip(names,allowed)]
    program=template.replace('%%ROOT%%',str(Q).replace('"','""')).replace('%%RESOLVER%%',',\n'.join(resolver));assert not any(s in program for s in ['ComputeActualContentProfile','GetActualContentProfile','SetComputationError','ClearComputationError','BindingFlags.NonPublic','_globalCache','cache calls0']);(Q/'Program.cs').write_text(program,encoding='utf-8')
    (Q/'runner').mkdir();fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(Q/'runner/QaCodecRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaCodecRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [fw/'mscorlib.dll',fw/'System.dll',fw/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    allocations=[]
    for stage,culture in [(1,'en-US'),(2,'de-DE')]:
        runid='R14-'+uuid.uuid4().hex[:16];out=Q/'runs'/runid;assert not out.exists();out.mkdir(parents=True);assert out.resolve().is_relative_to(Q.resolve())
        longest=max(len(str(out/'input_snapshot/policy_references'/p.name)) for p in refs.iterdir());assert longest<250,longest;allocations.append(dict(stage=stage,culture=culture,run_id=runid,output_root=str(out),prospective_longest_inputcopy_path_characters=longest,allocated_validated_before_final_build_calls=True))
    write(Q/'RUN_ALLOCATION_PLAN.json',dict(at=now(),allocations=allocations,short_unique_ids=True,candidate_calls=0,runner_builds_so_far=0))
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),API_rules=row(Q/'API_AND_GENERATION_RECONCILIATION.json'),cache_controls=row(Q/'CacheChecks.cs.txt'),explicit_codec_invocation_wrappers=row(Q/'ObservedProvider.cs.txt'),final_runner_source=row(Q/'Program.cs'),short_process_allocation=row(Q/'RUN_ALLOCATION_PLAN.json'),generic_cases=12,order_cases=14,cache_policies=2,reference_manifests_before_candidate_calls=68,oldzerofooter_removed_beforebuild=True,nooutputderivedoracle=True,prospective_candidate_calls=0))
    write(Q/'PROSPECTIVE_SOURCE_EXECUTION_SCOPE.json',dict(at=now(),source=row(Q/'Program.cs'),direct_allowed_actual_provider_names=sorted(set(re.findall(r'ContentProfileProvider\.(\w+)\s*\(',program))),actual_global_publication_collector_privatewrites_adverse_source_sites=0,standalone_publication='Freshcapture/currentgeneration/matchingpolicy/fullindependentmanifest referenceJSONSHA only',actual_invocation_ledger='DirectownProviderAPI calls throughObservedProvider wrappers plus explicitcorestages/groupedgetter markers;not profiling nestedinternalproduction calls',metadata_public_readonly=True,old_R13_raw_zerofooter_not_inherited=True))
    print(json.dumps(dict(generic_cases=12,order_cases=14,cache_policies=2,reference_manifests=68,invalidate_increment=1,main_generation_sequence=oracle['lifecycle_rule']['expected_main_sequence'],allocated_short_run_ids=[r['run_id'] for r in allocations],candidate_calls=0)))
