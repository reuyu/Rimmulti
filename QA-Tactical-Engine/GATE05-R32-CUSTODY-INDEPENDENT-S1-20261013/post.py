from common import *
from collections import Counter
from pe_pdb_reader import metadata_streams,table_header,guid,u16,u32
import ast,struct,re
# New definition-only extraction from this QA's already pinned execution source; no top-level execution.
source=Q/'execution.py';tree=ast.parse(source.read_bytes().decode('utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mvid')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(source)+'#mvid-file-bytes-only','exec'),globals())
def exact(e,a,name):
    assert type(e) is type(a),name
    if isinstance(e,dict):
        assert list(e)==list(a),name
        for k in e:exact(e[k],a[k],name+'.'+k)
    elif isinstance(e,list):
        assert len(e)==len(a),name
        for i,(x,y) in enumerate(zip(e,a)):exact(x,y,name+f'[{i}]')
    else:assert e==a,name
def inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');rows=[dict(**row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json'];assert rows==d['files'];return rows
oracle=load(Q/'NORMAL_EXPECTED_ORACLE.json');raw={};graphs={};pairs={};captures={};phases=['BEFORE','AFTER_CALLER','AFTER_RETURNED']
for c in oracle['pair_cases']:
    cid='PAIR_'+c['case_id'];p=c['independently_supplied_parent14_7'];ch=c['independently_supplied_child14_7'];pairs[cid]=c
    names={'pair.envelope':c['expected_full_graph_compact_UTF8'],'pair.parent.original7':p['original_declaration7_compact_utf8'],'pair.child.original7':ch['original_declaration7_compact_utf8'],'pair.parent.receipt11':p['receipt_compact_utf8'],'pair.child.receipt11':ch['receipt_compact_utf8'],'pair.parent.snapshot15':p['snapshot_compact_utf8'],'pair.child.snapshot15':ch['snapshot_compact_utf8'],'pair.parent.receipt.pretty':p['receipt_redacted_pretty_windows_utf8'],'pair.child.receipt.pretty':ch['receipt_redacted_pretty_windows_utf8'],'pair.parent.snapshot.pretty':p['snapshot_redacted_pretty_windows_utf8'],'pair.child.snapshot.pretty':ch['snapshot_redacted_pretty_windows_utf8'],'pair.bundleProjection':c['expected_bundle_compact_UTF8_noLF']}
    for phase in phases:
        for n,e in names.items():raw[f'{cid}.{phase}.{n}.utf8']=e['utf8_text'].encode('utf-8')
        graphs[f'{cid}.{phase}.pair.graph.json']=c['expected_full_observation_graph']
for c in oracle['normal_pairs']:
    cid=c['case_id'];captures[cid]=c;names={'capture':c['expected_Capture15_compact_utf8'],'envelope':c['expected_full_envelope_compact_utf8'],'approved7':c['expected_approved7_compact_utf8'],'task27':c['expected_task27_compact_utf8'],'options7':c['expected_option7_compact_utf8'],'invocation2':c['expected_invocation2_compact_utf8'],'receiptParent':c['expected_receipt_pretty_utf8']['parent'],'receiptChild':c['expected_receipt_pretty_utf8']['child'],'snapshotParent':c['expected_snapshot_pretty_utf8']['parent'],'snapshotChild':c['expected_snapshot_pretty_utf8']['child']}
    for phase in phases:
        for n,e in names.items():raw[f'{cid}.{phase}.{n}.utf8']=e['utf8_text'].encode('utf-8')
        graphs[f'{cid}.{phase}.graph.json']=c['expected_observation_envelope']
assert len(raw)==336 and len(graphs)==30
allocs=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'];runs=[];dirs=[]
for i,al in enumerate(allocs,1):
    assert load(Q/f'execution_post_{i}.TOOL.json')['exit_code']==0
    out=Path(al['output_root']);files=inventory(out);dirs.append(out);known={r['relative_path'] for r in files};assert {n for n in known if n.endswith('.utf8')}==set(raw)
    rawbindings=[]
    for n,e in raw.items():
        assert (out/n).read_bytes()==e and not e.startswith(b'\xef\xbb\xbf'),n
        rawbindings.append(dict(file=row(out/n),expected_sha256=hashlib.sha256(e).hexdigest().upper(),expected_bytes=len(e),literal_before_build_matched=True))
    for n,e in graphs.items():exact(e,load(out/n),n)
    typed=load(out/'TYPED_CHECKS.json');res=load(out/'NORMAL_RESULTS.json');ledger=load(out/'ACTUAL_ADMITTED_CALL_LEDGER.json');assert res['failed_assertions']==0 and len(res['results'])==438 and all(r['status']=='PASS' for r in res['results'])
    assert len({r['id'] for r in res['results']})==438 and len(typed)==6700 and len({r['path'] for r in typed})==6700
    for r in typed:assert r['matched'] and r['expected_type']==r['actual_type'];exact(r['expected'],r['actual'],r['path'])
    counts=Counter(r['scope'] for r in ledger);assert counts==Counter(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18)
    primary=Counter(r['api'] for r in ledger if r['scope']=='primary_direct');assert primary==Counter({'OperatorStartupPairAdmission.AdmitPairBytes':6,'IssueAdmissionReceiptFromBytes.parent':4,'IssueAdmissionReceiptFromBytes.child':4,'receipt.IsValid.parent':10,'receipt.IsValid.child':10,'OperatorChildLaunchInputs.Capture':4})
    assert sum(r['path'].startswith('PAIR_') for r in typed)==3708
    for cid,c in pairs.items():
        m=load(out/(cid+'.caller_array_mutation.json'));assert m['arrays_edited_after_success_only'] and not m['readmitted']
        for field,e in [('bundle_sha_after',c['expected_bundle_compact_UTF8_noLF']),('parent_sha_after',c['independently_supplied_parent14_7']['raw_config']),('child_sha_after',c['independently_supplied_child14_7']['raw_config'])]:assert m[field]!=e['sha256']
        m=load(out/(cid+'.returned_owned_mutations.json'));expected=c['planned_copy_controls']
        for actual,k in [('ParentDeclaration7','returnedParentDeclaration7'),('ChildDeclaration7','returnedChildDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4')]:exact(expected[k],m[actual],cid+'.'+actual)
        for role in ['Parent','Child']:assert m[role+'IdsDetachedInplace'] and all(v==f'edited.{role.lower()}.ids.{k}' for k,v in enumerate(m[role+'IdsDetachedInplace']))
    for cid,c in captures.items():
        expected=c['mutations_after_successful_capture_only'];caller=load(out/(cid+'.caller_owned_mutations.json'));returned=load(out/(cid+'.returned_owned_mutations.json'))
        for field,k in [('Task','callerTask27'),('ParentDescriptor','submittedParentDescriptor7'),('ChildDescriptor','submittedChildDescriptor7')]:exact(expected[k],caller[field],cid+'.caller.'+field)
        for field,k in [('Task','returnedTask27'),('ApprovedChildDeclaration','returnedApprovedDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4'),('OptionCopy','detachedOperatorOptionCopy7'),('InvocationCopy','detachedTaskInvocationCopy2'),('ParentIdsCopy','detachedParentReadOnlyPolicyIdCopy'),('ChildIdsCopy','detachedChildReadOnlyPolicyIdCopy')]:exact(expected[k],returned[field],cid+'.returned.'+field)
    pre=load(Q/f'PRE_RUN{i}_MANIFEST.json');post=load(out/'POST_RUN_IDENTITY.json');assert pre['files']==post['files'] and post['prepost_all_matched'];check(pre['files'])
    pinmap={r['path'].lower():r for r in pre['files']};loaded_checks=[]
    for boundary,filename in [('BEFORE','ACTUAL_LOADED_MANAGED_BEFORE.json'),('AFTER_CALLS','ACTUAL_LOADED_MANAGED_AFTER.json'),('FINAL_SERIALIZATION','ACTUAL_LOADED_MANAGED.json')]:
        loaded=load(out/filename)
        for r in loaded:
            assert r['path'].lower() in pinmap and r['sha256']==pinmap[r['path'].lower()]['sha256'];assert mvid(Path(r['path']))==r['mvid']
        loaded_checks.append(dict(boundary=boundary,file=row(out/filename),count=len(loaded),all_prospective_hash_MVID_matched=True))
    host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json');assert ctx['run_id']==host['run_id']==al['run_id'] and ctx['culture']==al['culture'] and host['numeric_exit']==0
    runs.append(dict(run_id=al['run_id'],culture=al['culture'],PID=host['owned_child_PID'],numeric_exit=0,assertions=438,failed=0,typed_hierarchical=6700,Pair_typed=3708,Capture_typed=2992,raw_files=336,full_graphs=30,raw_bindings=rawbindings,ledger_categories=dict(counts),primary_calls=dict(primary),loaded_boundaries=loaded_checks,prepost_pins=len(pre['files']),output_count=len(files),output_inventory=row(out/'OUTPUT_INVENTORY.json'),CLR_EnvironmentVersion=ctx['EnvironmentVersion']))
assert runs[0]['PID']!=runs[1]['PID'] and runs[0]['run_id']!=runs[1]['run_id']
cross=[]
for n in raw:assert (dirs[0]/n).read_bytes()==(dirs[1]/n).read_bytes();cross.append(dict(relative_name=n,en_US=row(dirs[0]/n),de_DE=row(dirs[1]/n),exact_bytes_equal=True))
for n in graphs:exact(load(dirs[0]/n),load(dirs[1]/n),n)
for out in dirs:inventory(out)
write(Q/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json',dict(at=now(),oracle_beforebuild=row(Q/'NORMAL_EXPECTED_ORACLE.json'),raw_pairs=cross,raw_pairs_count=336,full_ordered_graph_pairs=30,all_matched=True,QA_bundleProjection_not_publisher=True))
census=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';text=census.read_bytes().decode('utf-8');start=text.index('public class ValidatorTask');end=text.index('\n    public ',start+20);snippet=text[start:end];widths={}
for kind,name in [('long','simulatorGeneration'),('long','workerGeneration'),('long','resultEpoch'),('int','targetMapIndex'),('bool','isConsumed')]:assert re.search(r'public\s+'+kind+r'\s+'+name+r'\s*=',snippet);widths[name]=kind
write(Q/'CLR_SOURCE_WIDTH_WITNESS.json',dict(at=now(),exact_file=row(census),raw_utf8=snippet,source_widths=widths,runner_long3_int1_bool1_casts=row(Q/'Harness/Program.cs'),Integer_JSON_tag_not_CLR_width_proof=True,original_locator_observation=row(Q/'WIDTH_SEARCH_LOCATOR_OBSERVATION.json')))
write(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json',dict(at=now(),verdict='SCOPED_R32_POSITIVE_PURE_PAIR_CAPTURE_FULL_TYPED_RAW_COPY_PASS_SOURCE_NATIVE_LIMITS_OPEN',runs=runs,builds=1,fresh_processes=2,total_assertions=876,failed=0,typed_rows=13400,raw_literal_bindings=672,cross_raw_pairs=336,cross_ordered_graphs=30,typed_counts='Hierarchical repeated type/key/order/container/value rows, not independent requirements',copy_controls='Pair detached IDs edited in place; Capture ID holder replaced only; caller arrays edited AFTER success, no re-admission',production_modify_build=0,changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse=0,old_PASS_inherited=False,nativeE2='NOT_RELEASED',Foundation='HOLD'))
print(json.dumps(dict(runs=2,assertions=876,failed=0,typed=13400,raw_expected=672,cross_raw=336,cross_graphs=30,outputs=[r['output_count'] for r in runs],loaded_boundaries=[[x['count'] for x in r['loaded_boundaries']] for r in runs],source_widths_file='EngineHostCensus.cs',native_execution=0)))
