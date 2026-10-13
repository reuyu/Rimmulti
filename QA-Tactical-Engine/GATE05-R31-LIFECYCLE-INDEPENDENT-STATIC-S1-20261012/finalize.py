from qa_common import *
import sys,os
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R31_Lifecycle_Independent_Static_S1_20261012.md'
VERDICT='MANAGED_CUSTODY_RESOURCE_AND_EVIDENCE_REVISION_REQUIRED_NATIVE_UNTESTED'
def guards():
    for name in ['bootstrap.TOOL.json','review_metadata_source.TOOL.json','LOCATOR_R1_PREPARE_TOOL.json','review_r1_provenance.TOOL.json','LIFECYCLE_ANALYSIS_TOOL.json','RECOVERY_CAPTURED_TOOL.json']:
        assert load(Q/name)['exit_code']==0,name
    assert load(Q/'review_provenance.TOOL.json')['exit_code']==1
    assert sha(Q/'ACK_INITIAL.json')=='F587A9EE427F338A6116329580AF6306C4EA69AC58A50F79162F21FE739FE7DA'
    assert (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
    assert load(Q/'SOURCE_BRANCH_LIFECYCLE_REVIEW.json')['case_count']==20
    assert len(load(Q/'CLAIM_EVIDENCE_MATRIX.json')['claims'])==20
    assert REPORT.exists()
def prepare():
    guards();before=load(Q/'PRESERVATION_BEFORE.json');after=preservation()
    assert before['protected_files']==after['protected_files'] and before['frozen_files']==after['frozen_files']
    oldman=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R30-HANDOFF-20261012-DIRECT-16ce928f/MASTER_GATE05_R30_HANDOFF_REVIEW_FREEZE_MANIFEST.json'
    old=verify(load(oldman)['files'],'frozen_path');assert len(old)==128
    prov=load(Q/'PROVENANCE_REVIEW.json');observations=[]
    for dep in prov['dependencies']:
        previous=dep['current_unprotected_declared_path_observation']
        if previous:
            observed=verify([previous])[0];observations.append(dict(before=previous,after=observed,initial_baseline_coverage=False,prospective_compile_reference_proof=False))
    assert len(observations)==1
    write(Q/'PRESERVATION_AFTER.json',after)
    write(Q/'PRESERVATION_BEFORE_AFTER.json',dict(at=now(),before=row(Q/'PRESERVATION_BEFORE.json'),after=row(Q/'PRESERVATION_AFTER.json'),protected_unique_paths=15854,frozen_files=131,all_SHA_bytes_matched=True,old_frozen128=old,additive_original_reference_observations=observations,baseline_not_modified=True,candidate_calls=0))
    print(json.dumps(dict(protected=15854,frozen=131,old_frozen=128,additive_observations=len(observations),matched=True,report=row(REPORT),candidate_calls=0)))
def seal():
    guards();assert load(Q/'finalize_prepare.TOOL.json')['exit_code']==0
    cycles=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']
    pendinglogger=['finalize_seal.STDOUT.txt','finalize_seal.STDERR.txt','finalize_seal.TOOL.json']
    excluded=cycles+pendinglogger
    files=[p for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in excluded]+[REPORT]
    assert not any(p.suffix=='.pyc' for p in files)
    artifacts=[row(p) for p in files]
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),delivery_id=DELIVERY,result_id=load(Q/'ACK_INITIAL.json')['result_id'],files=artifacts,artifact_count=len(artifacts),explicit_cycle_exclusions=cycles,in_progress_logger_exclusions=pendinglogger,excluded_logger_and_direct_tool_return='Preserved separately after actual exit/submission; not represented as already hashed/observed.',candidate_calls=0))
    em=row(Q/'EVIDENCE_MANIFEST.json');ack=load(Q/'ACK_INITIAL.json')
    result=dict(at=now(),delivery_id=DELIVERY,wp_id=ack['wp_id'],wp_revision='S1',result_id=ack['result_id'],static_verdict=VERDICT,native='UNTESTED',full_gate_E2='NOT_RELEASED',Foundation='HOLD',source_cases=20,claim_assessments=20,candidate_compiler_runner_global_native_adverse_executions=0,prior_PASS_inherited=False,protected_unique_paths=15854,frozen_files=131,evidence_manifest=em,report=row(REPORT),initial_ACK=row(Q/'ACK_INITIAL.json'),Master_disposition='PENDING')
    write(Q/'RESULT_INDEX.json',result)
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),delivery_id=DELIVERY,result_id=ack['result_id'],immutable_initial_ACK=row(Q/'ACK_INITIAL.json'),terminal_status='COMPLETED_INDEPENDENT_STATIC_REVISION_REQUIRED',initial_static_PENDING_not_rewritten=True,result_index=row(Q/'RESULT_INDEX.json')))
    write(Q/'RETURN_PENDING.json',dict(at=now(),delivery_id=DELIVERY,result_id=ack['result_id'],submission='PENDING_ACTUAL_DIRECT_TOOL',Master_receipt='PENDING',immutable_intent_only=True))
    verify(artifacts);verify([em,row(Q/'RESULT_INDEX.json'),row(Q/'ACK_COMPLETION_BINDING.json')])
    completion=dict(**result,status='COMPLETED',result_index=row(Q/'RESULT_INDEX.json'),ACK_completion_binding=row(Q/'ACK_COMPLETION_BINDING.json'),preservation=row(Q/'PRESERVATION_BEFORE_AFTER.json'),artifact_count=len(artifacts),COMPLETION_last_atomic=True,no_closure_release=True,cycle_logger_exclusions=excluded)
    tmp=Q/'COMPLETION.json.tmp';target=Q/'COMPLETION.json';assert not target.exists() and not tmp.exists()
    write(tmp,completion);os.replace(tmp,target)
    print(json.dumps(dict(status='COMPLETED',static_verdict=VERDICT,artifact_count=len(artifacts),completion=row(target),evidence_manifest=em,report=row(REPORT),candidate_calls=0)))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='seal':seal()
    else:raise ValueError(sys.argv[1])
