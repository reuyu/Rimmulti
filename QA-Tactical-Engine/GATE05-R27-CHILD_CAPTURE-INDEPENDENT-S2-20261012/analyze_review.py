from review_setup import *
from collections import Counter
def eq(e,a,path='$'):
    rows=[dict(path=path,expected_type=type(e).__name__,actual_type=type(a).__name__,matched=type(e)==type(a) and e==a)]
    if isinstance(e,dict):
        rows[0]['matched']=rows[0]['matched'] and isinstance(a,dict) and list(e)==list(a)
        for k,v in e.items():rows+=eq(v,a[k],path+'.'+k)
    elif isinstance(e,list):
        for i,v in enumerate(e):rows+=eq(v,a[i],path+'['+str(i)+']')
    return rows
if __name__=='__main__':
    oracle=load(Q/'NORMAL_EXPECTED_ORACLE.json');alloc=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'];cases=oracle['normal_pairs'];summ=[];allrows=[];raw=[];mutation=[]
    phase=['BEFORE','AFTER_CALLER','AFTER_RETURNED']
    for r in alloc:
        out=Path(r['output_root']);res=load(out/'NORMAL_RESULTS.json');host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');typed=load(out/'TYPED_CHECKS.json');ledger=load(out/'ACTUAL_ADMITTED_CALL_LEDGER.json');pre=load(Q/f"PRE_RUN{r['stage']}_MANIFEST.json");loaded=load(out/'ACTUAL_LOADED_PREPIN_BINDING.json')['files'];inventory=load(out/'OUTPUT_INVENTORY.json')
        assert host['numeric_exit']==0 and res['failed_assertions']==0 and len(res['results'])==168 and all(v['status']=='PASS' for v in res['results'])
        assert len(typed)==2992 and all(v['matched'] for v in typed)
        groups=Counter(v['scope'] for v in ledger);primary=Counter(v['api'].split('.')[0] if v['api'].startswith('IssueAdmissionReceiptFromBytes') else 'IsValid' if v['api'].startswith('receipt.IsValid') else 'Capture' for v in ledger if v['scope']=='primary_direct')
        assert primary==dict(IssueAdmissionReceiptFromBytes=8,IsValid=8,Capture=4) and groups['ordered_getter']==180 and groups['observational_helper']==72 and groups['grouped_helper']==24
        assert len(loaded)==10 and len(pre['files'])==150 and inventory['file_count']==157
        for c in cases:
            cid=c['case_id'];m=c['mutations_after_successful_capture_only'];actual_caller=load(out/(cid+'.caller_owned_mutations.json'));actual_returned=load(out/(cid+'.returned_owned_mutations.json'))
            assert actual_caller['Task']==m['callerTask27'] and list(actual_caller['Task'])==list(m['callerTask27'])
            assert actual_caller['ParentDescriptor']==m['submittedParentDescriptor7'] and actual_caller['ChildDescriptor']==m['submittedChildDescriptor7']
            assert actual_returned['Task']==m['returnedTask27'] and actual_returned['ApprovedChildDeclaration']==m['returnedApprovedDeclaration7']
            for actual,key in [('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4'),('OptionCopy','detachedOperatorOptionCopy7'),('InvocationCopy','detachedTaskInvocationCopy2'),('ParentIdsCopy','detachedParentReadOnlyPolicyIdCopy'),('ChildIdsCopy','detachedChildReadOnlyPolicyIdCopy')]:assert actual_returned[actual]==m[key]
            mutation.append(dict(run_id=r['run_id'],case_id=cid,caller_task27_exact_edits=True,returned_task27_exact_edits=True,approved7_edits=True,submitted_descriptor7_each_edits=True,policy_declaration_record_actual_field_list_edits=True,operator_option_copy7_and_invocation_copy2_inplace_edits=True,readonly_policy_ids_control='Own holder reference replaced by new detached array; not in-place mutation of original materialized ID array; no readonly backing mutation/exception',caller=row(out/(cid+'.caller_owned_mutations.json')),returned=row(out/(cid+'.returned_owned_mutations.json'))))
            values={'capture':c['expected_Capture15_compact_utf8'],'envelope':c['expected_full_envelope_compact_utf8'],'approved7':c['expected_approved7_compact_utf8'],'task27':c['expected_task27_compact_utf8'],'options7':c['expected_option7_compact_utf8'],'invocation2':c['expected_invocation2_compact_utf8'],'receiptParent':c['expected_receipt_pretty_utf8']['parent'],'receiptChild':c['expected_receipt_pretty_utf8']['child'],'snapshotParent':c['expected_snapshot_pretty_utf8']['parent'],'snapshotChild':c['expected_snapshot_pretty_utf8']['child']}
            for p in phase:
                gp=out/(cid+'.'+p+'.graph.json');g=load(gp);rows=eq(c['expected_observation_envelope'],g,r['run_id']+'.'+cid+'.'+p);assert all(v['matched'] for v in rows);allrows+=rows
                for k,e in values.items():
                    file=out/(cid+'.'+p+'.'+k+'.utf8');actual=file.read_bytes();expected=e['utf8_text'].encode();assert actual==expected and len(actual)==e['bytes'] and sha(file)==e['sha256'];raw.append(dict(run_id=r['run_id'],case_id=cid,phase=p,value=k,file=row(file),expected_sha256=e['sha256'],expected_bytes=e['bytes'],exact=True,actual_normalized=False))
        summ.append(dict(run_id=r['run_id'],culture=r['culture'],owned_PID=host['owned_child_pid'],actual_OS_exit=host['numeric_exit'],assertions=168,failed=0,runtime_typed_rows=2992,primary_direct_calls=dict(primary),ordered_getter_reads=180,observational_helper_marks=72,grouped_snapshot_reads=24,total_ledger_marks=len(ledger),all_prepost_pins=150,loaded_managed=10,recursive_outputs=157,stdout=host['stdout'],stderr=host['stderr'],runner=pre['runner']))
    assert len(allrows)==5856 and len(raw)==240
    pairs=[];a=Path(alloc[0]['output_root']);b=Path(alloc[1]['output_root'])
    for c in cases:
        entries=[]
        for p in phase:
            fa=a/(c['case_id']+'.'+p+'.graph.json');fb=b/(c['case_id']+'.'+p+'.graph.json');assert fa.read_bytes()==fb.read_bytes();entries.append(dict(phase=p,enUS=row(fa),deDE=row(fb),bytes_identical=True))
            for k in ['capture','envelope','approved7','task27','options7','invocation2','receiptParent','receiptChild','snapshotParent','snapshotChild']:
                assert (a/(c['case_id']+'.'+p+'.'+k+'.utf8')).read_bytes()==(b/(c['case_id']+'.'+p+'.'+k+'.utf8')).read_bytes()
        pairs.append(dict(case_id=c['case_id'],complete_three_phase_graph_pair=entries,all30_raw_value_pairs_identical=True,repeatability_not_independent_oracle_correctness=True))
    write(Q/'FULL_TYPED_AND_RAW_BINDING.json',dict(at=now(),independent_full_envelope_rows=allrows,independent_row_count=5856,failed=0,runtime_typed_rows_per_run=2992,total_runtime_typed_rows=5984,raw_bindings=raw,raw_count=240,actual_output_normalization=False,expectation_files_changed=False))
    write(Q/'COPY_OWNERSHIP_OBSERVED.json',dict(at=now(),cases=mutation,scope='Normal connected caller and detached returned Task27/approved7/policy/list controls; static readonly backing proof separate',readonly_backing_mutation_exception_probes=0,policy_readonly_ID_copy_replacement_limitation_explicit=True))
    write(Q/'CROSS_CULTURE_NORMAL_PAIRS.json',dict(at=now(),pairs=pairs,complete_case_pairs=4,individual_phase_graph_file_pairs=12,individual_raw_value_file_pairs=120))
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',dict(at=now(),verdict='SCOPED_FRESH_NORMAL_CAPTURE15_FULL_TYPED_RAW_AND_COPY_OWNERSHIP_PASS_NATIVE_UNTESTED',runs=summ,final_QA_builds=1,compiler=load(Q/'BUILD_TOOL_PROOF.json'),controls=4,two_actual_OS_exits=[0,0],passed_per_run=[168,168],failed_per_run=[0,0],raw_byte_bindings=240,independent_envelope_rows=5856,runtime_rows_with_input_descriptor_purity=5984,complete_crossculture_pairs=4,production_candidate_modify_build=0,provider_actual_compute_cache_global_game_native_Process_registration_adverse=0,ReadonlyPolicyID_detachedcopy_control='Holder replaced by newly allocated detached array; declaration/record lists and option/invocation materialized arrays actually edited; no readonly backing mutation claim',normal_failure_reruns=0,framework_CLR_provenance='Actual loaded mscorlib path/SHA/MVID independently PE checked; target/runtime metadata v4 via CLR assembly provenance; Environment.Version string not separately recorded',native_fullgate_E2=False,closure_changed=False,foundation='HOLD'))
    print(json.dumps(dict(runs=[dict(culture=r['culture'],PID=r['owned_PID'],PASS=r['assertions'],FAIL=r['failed'],exit=r['actual_OS_exit'],typed=r['runtime_typed_rows'],ledger=r['total_ledger_marks']) for r in summ],independent_rows=5856,total_runtime_rows=5984,exact_raw_bindings=240,complete_culture_pairs=4),indent=2))
