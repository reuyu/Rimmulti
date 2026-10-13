from common import *
from normal_tools import inventory,verify_inventory,mvid
from collections import Counter
import re
def exact(e,a,p):
    assert type(e) is type(a),p
    if isinstance(e,dict):
        assert list(e)==list(a),p
        for k in e:exact(e[k],a[k],p+'.'+k)
    elif isinstance(e,list):
        assert len(e)==len(a),p
        for i,(x,y) in enumerate(zip(e,a)):exact(x,y,p+f'[{i}]')
    else:assert e==a,p
assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')=='89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D'
oracle=load(Q/'NORMAL_EXPECTED_ORACLE.json');phases=['BEFORE','AFTER_CALLER','AFTER_RETURNED'];raw={};graphs={};pair_cases={};cap_cases={}
for c in oracle['pair_cases']:
    cid='PAIR_'+c['case_id'];pair_cases[cid]=c;p=c['independently_supplied_parent14_7'];ch=c['independently_supplied_child14_7']
    components={'pair.envelope':c['expected_full_graph_compact_UTF8'],'pair.parent.original7':p['original_declaration7_compact_utf8'],'pair.child.original7':ch['original_declaration7_compact_utf8'],'pair.parent.receipt11':p['receipt_compact_utf8'],'pair.child.receipt11':ch['receipt_compact_utf8'],'pair.parent.snapshot15':p['snapshot_compact_utf8'],'pair.child.snapshot15':ch['snapshot_compact_utf8'],'pair.parent.receipt.pretty':p['receipt_redacted_pretty_windows_utf8'],'pair.child.receipt.pretty':ch['receipt_redacted_pretty_windows_utf8'],'pair.parent.snapshot.pretty':p['snapshot_redacted_pretty_windows_utf8'],'pair.child.snapshot.pretty':ch['snapshot_redacted_pretty_windows_utf8'],'pair.bundleProjection':c['expected_bundle_compact_UTF8_noLF']}
    for phase in phases:
        for k,v in components.items():raw[f'{cid}.{phase}.{k}.utf8']=v['utf8_text'].encode('utf-8')
        graphs[f'{cid}.{phase}.pair.graph.json']=c['expected_full_observation_graph']
for c in oracle['normal_pairs']:
    cid=c['case_id'];cap_cases[cid]=c
    components={'capture':c['expected_Capture15_compact_utf8'],'envelope':c['expected_full_envelope_compact_utf8'],'approved7':c['expected_approved7_compact_utf8'],'task27':c['expected_task27_compact_utf8'],'options7':c['expected_option7_compact_utf8'],'invocation2':c['expected_invocation2_compact_utf8'],'receiptParent':c['expected_receipt_pretty_utf8']['parent'],'receiptChild':c['expected_receipt_pretty_utf8']['child'],'snapshotParent':c['expected_snapshot_pretty_utf8']['parent'],'snapshotChild':c['expected_snapshot_pretty_utf8']['child']}
    for phase in phases:
        for k,v in components.items():raw[f'{cid}.{phase}.{k}.utf8']=v['utf8_text'].encode('utf-8')
        graphs[f'{cid}.{phase}.graph.json']=c['expected_observation_envelope']
assert len(raw)==336 and len(graphs)==30
runs=[];dirs=[]
for i,alloc in enumerate(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'],1):
    assert load(Q/f'host_post_{i}.TOOL.json')['exit_code']==0
    out=Path(alloc['output_root']);dirs.append(out);inv=verify_inventory(out);files=inventory(out)
    assert {r['relative_path'] for r in files if r['relative_path'].endswith('.utf8')}==set(raw)
    bindings=[]
    for name,expected in raw.items():
        assert (out/name).read_bytes()==expected and not expected.startswith(b'\xef\xbb\xbf'),name
        bindings.append(dict(file=row(out/name),expected_sha256=hashlib.sha256(expected).hexdigest().upper(),expected_bytes=len(expected),literal_before_build_matched=True))
    for name,expected in graphs.items():exact(expected,load(out/name),name)
    results=load(out/'NORMAL_RESULTS.json');typed=load(out/'TYPED_CHECKS.json');ledger=load(out/'ACTUAL_ADMITTED_CALL_LEDGER.json')
    assert len(results['results'])==438 and results['failed_assertions']==0 and all(r['status']=='PASS' for r in results['results']) and len({r['id'] for r in results['results']})==438
    assert len(typed)==6700 and len({r['path'] for r in typed})==6700
    for r in typed:assert r['matched'] and r['expected_type']==r['actual_type'];exact(r['expected'],r['actual'],r['path'])
    categories=Counter(r['scope'] for r in ledger);assert categories==Counter(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18)
    primary=Counter(r['api'] for r in ledger if r['scope']=='primary_direct');assert primary==Counter({'OperatorStartupPairAdmission.AdmitPairBytes':6,'IssueAdmissionReceiptFromBytes.parent':4,'IssueAdmissionReceiptFromBytes.child':4,'receipt.IsValid.parent':10,'receipt.IsValid.child':10,'OperatorChildLaunchInputs.Capture':4})
    assert sum(r['path'].startswith('PAIR_') for r in typed)==3708
    for cid,c in pair_cases.items():
        mut=load(out/(cid+'.caller_array_mutation.json'));assert mut['arrays_edited_after_success_only'] and not mut['readmitted']
        for field,expected in [('bundle_sha_after',c['expected_bundle_compact_UTF8_noLF']),('parent_sha_after',c['independently_supplied_parent14_7']['raw_config']),('child_sha_after',c['independently_supplied_child14_7']['raw_config'])]:assert mut[field]!=expected['sha256']
        mut=load(out/(cid+'.returned_owned_mutations.json'));e=c['planned_copy_controls']
        for field,key in [('ParentDeclaration7','returnedParentDeclaration7'),('ChildDeclaration7','returnedChildDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4')]:exact(e[key],mut[field],cid+'.'+field)
        for role in ['Parent','Child']:assert mut[role+'IdsDetachedInplace'] and all(v==f'edited.{role.lower()}.ids.{k}' for k,v in enumerate(mut[role+'IdsDetachedInplace']))
    for cid,c in cap_cases.items():
        e=c['mutations_after_successful_capture_only'];mut=load(out/(cid+'.caller_owned_mutations.json'))
        for field,key in [('Task','callerTask27'),('ParentDescriptor','submittedParentDescriptor7'),('ChildDescriptor','submittedChildDescriptor7')]:exact(e[key],mut[field],cid+'.caller.'+field)
        mut=load(out/(cid+'.returned_owned_mutations.json'))
        for field,key in [('Task','returnedTask27'),('ApprovedChildDeclaration','returnedApprovedDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4'),('OptionCopy','detachedOperatorOptionCopy7'),('InvocationCopy','detachedTaskInvocationCopy2'),('ParentIdsCopy','detachedParentReadOnlyPolicyIdCopy'),('ChildIdsCopy','detachedChildReadOnlyPolicyIdCopy')]:exact(e[key],mut[field],cid+'.returned.'+field)
    pre=load(Q/f'PRE_RUN{i}_MANIFEST.json');post=load(out/'POST_RUN_IDENTITY.json');assert pre['files']==post['files'] and post['prepost_all_matched'];check(pre['files']);pins={r['path'].lower():r for r in pre['files']};loaded_counts=[]
    for name in ['ACTUAL_LOADED_MANAGED_BEFORE.json','ACTUAL_LOADED_MANAGED_AFTER.json','ACTUAL_LOADED_MANAGED.json']:
        rows=load(out/name)
        for r in rows:assert r['path'].lower() in pins and r['sha256']==pins[r['path'].lower()]['sha256'] and mvid(Path(r['path']))==r['mvid']
        loaded_counts.append(len(rows))
    host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json');assert ctx['run_id']==host['run_id']==alloc['run_id'] and ctx['culture']==alloc['culture'] and host['numeric_exit']==0
    runs.append(dict(run_id=alloc['run_id'],culture=alloc['culture'],PID=host['owned_child_PID'],numeric_exit=0,assertions=438,failed=0,typed_hierarchical=6700,Pair_typed=3708,Capture_typed=2992,raw_files=336,full_graphs=30,raw_bindings=bindings,ledger_categories=dict(categories),primary_calls=dict(primary),loaded_boundary_counts=loaded_counts,prepost_pins=len(pre['files']),output_count=len(files),output_inventory=inv,CLR_EnvironmentVersion=ctx['EnvironmentVersion']))
assert runs[0]['PID']!=runs[1]['PID'] and runs[0]['run_id']!=runs[1]['run_id'];cross=[]
for name in raw:
    assert (dirs[0]/name).read_bytes()==(dirs[1]/name).read_bytes();cross.append(dict(relative_name=name,en_US=row(dirs[0]/name),de_DE=row(dirs[1]/name),exact_bytes_equal=True))
for name in graphs:exact(load(dirs[0]/name),load(dirs[1]/name),name)
for out in dirs:verify_inventory(out)
write(Q/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json',dict(at=now(),oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),raw_pairs=cross,raw_pairs_count=336,full_ordered_graph_pairs=30,all_matched=True,QA_projection_not_publisher=True))
census=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';s=census.read_bytes().decode('utf-8');lo=s.index('public class ValidatorTask');hi=s.index('\n    public ',lo+20);snippet=s[lo:hi];widths={}
for kind,name in [('long','simulatorGeneration'),('long','workerGeneration'),('long','resultEpoch'),('int','targetMapIndex'),('bool','isConsumed')]:assert re.search(r'public\s+'+kind+r'\s+'+name+r'\s*=',snippet);widths[name]=kind
write(Q/'CLR_SOURCE_WIDTH_WITNESS.json',dict(at=now(),exact_source=row(census),raw_utf8=snippet,widths=widths,runner_source=row(Q/'Harness/Program.cs'),JSON_Integer_not_CLR_width_proof=True))
write(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json',dict(at=now(),verdict=VERDICT,runs=runs,builds=1,fresh_processes=2,total_assertions=876,failed=0,typed_rows=13400,raw_literal_bindings=672,cross_raw_pairs=336,cross_ordered_graphs=30,hierarchy_counts_not_independent_requirements=True,production_modify_build=0,changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse=0,old_PASS_inherited=False,nativeE2='NOT_RELEASED',Foundation='HOLD'))
print(json.dumps(dict(runs=2,assertions=876,failed=0,typed=13400,raw_literal=672,cross_raw=336,cross_graphs=30,loaded_counts=[r['loaded_boundary_counts'] for r in runs],outputs=[r['output_count'] for r in runs],prepost_pins=[r['prepost_pins'] for r in runs],modified_lifecycle_native=0)))
