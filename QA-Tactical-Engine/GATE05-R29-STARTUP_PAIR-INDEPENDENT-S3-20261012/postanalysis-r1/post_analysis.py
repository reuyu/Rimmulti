from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
"""Independent review of sealed normal outputs; no candidate execution."""
from review_setup import *
from collections import Counter
A=Path(__file__).resolve().parent
def exact_graph(expected, actual, name):
    assert type(expected) is type(actual), name
    if isinstance(expected, dict):
        assert list(expected)==list(actual), name
        for k in expected: exact_graph(expected[k],actual[k],name+'.'+k)
    elif isinstance(expected, list):
        assert len(expected)==len(actual),name
        for i,(e,a) in enumerate(zip(expected,actual)):exact_graph(e,a,name+f'[{i}]')
    else:assert expected==actual,name
def hierarchy(x):
    return 1+sum(hierarchy(v) for v in x.values()) if isinstance(x,dict) else 1+sum(hierarchy(v) for v in x) if isinstance(x,list) else 1
def check_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');known={r['relative_path']:r for r in d['files']}
    current={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
    assert current==set(known) and d['file_count']==len(known)
    for n,r in known.items():
        p=out/n;assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],n
    return known
if __name__=='__main__':
    oracle=load(Q/'NORMAL_EXPECTED_ORACLE.json');raw={};graphs={};mutations={}; phases=['BEFORE','AFTER_CALLER','AFTER_RETURNED']
    for c in oracle['pair_cases']:
        cid='PAIR_'+c['case_id'];p=c['independently_supplied_parent14_7'];ch=c['independently_supplied_child14_7']
        names={'pair.envelope':c['expected_full_graph_compact_UTF8'],'pair.parent.original7':p['original_declaration7_compact_utf8'],'pair.child.original7':ch['original_declaration7_compact_utf8'],'pair.parent.receipt11':p['receipt_compact_utf8'],'pair.child.receipt11':ch['receipt_compact_utf8'],'pair.parent.snapshot15':p['snapshot_compact_utf8'],'pair.child.snapshot15':ch['snapshot_compact_utf8'],'pair.parent.receipt.pretty':p['receipt_redacted_pretty_windows_utf8'],'pair.child.receipt.pretty':ch['receipt_redacted_pretty_windows_utf8'],'pair.parent.snapshot.pretty':p['snapshot_redacted_pretty_windows_utf8'],'pair.child.snapshot.pretty':ch['snapshot_redacted_pretty_windows_utf8'],'pair.bundleProjection':c['expected_bundle_compact_UTF8_noLF']}
        for phase in phases:
            for n,e in names.items():raw[f'{cid}.{phase}.{n}.utf8']=e['utf8_text'].encode('utf-8')
            graphs[f'{cid}.{phase}.pair.graph.json']=c['expected_full_observation_graph']
        mutations[cid]=c
    for c in oracle['normal_pairs']:
        cid=c['case_id'];names={'capture':c['expected_Capture15_compact_utf8'],'envelope':c['expected_full_envelope_compact_utf8'],'approved7':c['expected_approved7_compact_utf8'],'task27':c['expected_task27_compact_utf8'],'options7':c['expected_option7_compact_utf8'],'invocation2':c['expected_invocation2_compact_utf8'],'receiptParent':c['expected_receipt_pretty_utf8']['parent'],'receiptChild':c['expected_receipt_pretty_utf8']['child'],'snapshotParent':c['expected_snapshot_pretty_utf8']['parent'],'snapshotChild':c['expected_snapshot_pretty_utf8']['child']}
        for phase in phases:
            for n,e in names.items():raw[f'{cid}.{phase}.{n}.utf8']=e['utf8_text'].encode('utf-8')
            graphs[f'{cid}.{phase}.graph.json']=c['expected_observation_envelope']
    assert len(raw)==336 and len(graphs)==30
    allocations=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'];runs=[];outdirs=[];cross=[]
    for i,al in enumerate(allocations,1):
        out=Path(al['output_root']);known=check_inventory(out);outdirs.append(out)
        def read(n):
            assert n in known,n
            return load(out/n)
        assert {n for n in known if n.endswith('.utf8')}==set(raw)
        rawbindings=[]
        for n,e in raw.items():
            assert (out/n).read_bytes()==e,n
            rawbindings.append(dict(file=row(out/n),expected_sha256=hashlib.sha256(e).hexdigest().upper(),expected_bytes=len(e),independent_prebuild_oracle_match=True))
        for n,e in graphs.items():exact_graph(e,read(n),n)
        typed=read('TYPED_CHECKS.json');results=read('NORMAL_RESULTS.json');ledger=read('ACTUAL_ADMITTED_CALL_LEDGER.json')
        assert results['failed_assertions']==0 and len(results['results'])==438 and all(r['status']=='PASS' for r in results['results'])
        assert len({r['id'] for r in results['results']})==438
        assert len(typed)==6700 and len({r['path'] for r in typed})==6700
        for r in typed:
            assert r['matched'] and r['expected_type']==r['actual_type'],r['path']
            exact_graph(r['expected'],r['actual'],r['path'])
        counts=Counter(r['scope'] for r in ledger);assert counts==Counter(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18)
        primary=Counter(r['api'] for r in ledger if r['scope']=='primary_direct')
        assert primary==Counter({'OperatorStartupPairAdmission.AdmitPairBytes':6,'IssueAdmissionReceiptFromBytes.parent':4,'IssueAdmissionReceiptFromBytes.child':4,'receipt.IsValid.parent':10,'receipt.IsValid.child':10,'OperatorChildLaunchInputs.Capture':4})
        pair_typed=sum(r['path'].startswith('PAIR_') for r in typed)
        assert pair_typed==3708 and len(typed)-pair_typed==2992
        for cid,c in mutations.items():
            m=read(cid+'.caller_array_mutation.json');assert m['arrays_edited_after_success_only'] and not m['readmitted']
            for field,original in [('bundle_sha_after',c['expected_bundle_compact_UTF8_noLF']),('parent_sha_after',c['independently_supplied_parent14_7']['raw_config']),('child_sha_after',c['independently_supplied_child14_7']['raw_config'])]:assert m[field]!=original['sha256']
            m=read(cid+'.returned_owned_mutations.json');expected=c['planned_copy_controls']
            for actual,k in [('ParentDeclaration7','returnedParentDeclaration7'),('ChildDeclaration7','returnedChildDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4')]:exact_graph(expected[k],m[actual],cid+'.'+actual)
            for role in ['Parent','Child']:
                ids=m[role+'IdsDetachedInplace'];assert ids and all(v==f'edited.{role.lower()}.ids.{k}' for k,v in enumerate(ids))
        host=read('HOST_RUN_PROCESS_OBSERVATION.json');ctx=read('ACTUAL_PROCESS_CONTEXT.json');pre=load(Q/f'PRE_RUN{i}_MANIFEST.json');post=read('POST_RUN_IDENTITY.json')
        assert load(Q/f'execution_tools_post_{i}.TOOL.json')['exit_code']==load(Q/f'execution_tools_run_{i}.TOOL.json')['exit_code']==host['numeric_exit']==0
        assert ctx['run_id']==host['run_id']==al['run_id'] and ctx['culture']==host['culture']==al['culture']
        assert pre['files']==post['files'] and post['all_prepost_matched']
        binding=read('ACTUAL_LOADED_PREPIN_BINDING.json');assert binding['all_matched'] and len(binding['files'])==10
        for r in pre['files']:
            p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(p)
        runs.append(dict(run_id=al['run_id'],culture=ctx['culture'],EnvironmentVersion=ctx['EnvironmentVersion'],PID=host['owned_child_pid'],numeric_exit=0,assertions=438,failed_assertions=0,typed_hierarchical_comparisons=6700,pair_typed=pair_typed,Capture_typed_including_descriptor_purity=2992,raw_byte_bindings=rawbindings,raw_files=336,full_graphs=30,primary_direct_calls=dict(primary),ledger_category_counts=dict(counts),prepost_pins=len(pre['files']),loaded_managed=10,output_files_excluding_inventory=len(known),output_inventory=row(out/'OUTPUT_INVENTORY.json')))
    assert runs[0]['PID']!=runs[1]['PID'] and runs[0]['run_id']!=runs[1]['run_id']
    for n in raw:
        assert (outdirs[0]/n).read_bytes()==(outdirs[1]/n).read_bytes()
        cross.append(dict(relative_name=n,en_US=row(outdirs[0]/n),de_DE=row(outdirs[1]/n),exact_bytes_equal=True))
    for n in graphs:exact_graph(load(outdirs[0]/n),load(outdirs[1]/n),n)
    for out in outdirs:check_inventory(out)
    write(A/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json',dict(at=now(),prebuild_oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),raw_pairs=cross,pair_raw216_and_Capture_raw120_per_run=True,QA_bundleProjection_not_actual_publisher=True,full_graph_pairs=len(graphs),all_matched=True))
    write(A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json',dict(at=now(),verdict='SCOPED_R29_POSITIVE_PURE_PAIR_AND_CAPTURE_DATA_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED',runs=runs,distinct_fresh_processes=True,total_assertions=876,total_failed=0,total_typed_comparisons=13400,total_raw_expected_bindings=672,cross_culture_raw_pairs=336,typed_count_note='Hierarchical JSON rows include containers and repeated phase observations; not independent leaf requirements. CLR widths compiled from declared public fields, Integer JSON tag alone does not prove width.',copy_control_note='Pair detached ID arrays edited in place; Capture ID holders replaced only. No readonly-cast exception or rejection reproduction.',source_High3='OPEN',runtimeE2='NOT_RELEASED',Foundation='HOLD',production_build_modify=0,provider_cache_global_Awake_publisher_game_native_Process_adverse=0))
    print(json.dumps(dict(runs=2,assertions=876,failed=0,typed_rows=13400,raw_expected_bindings=672,cross_culture_raw_pairs=336,source_High3_OPEN=True,native_UNTESTED=True)))
