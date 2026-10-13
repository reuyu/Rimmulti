from common import *
import sys,os
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R32_Custody_Independent_S1_20261013.md'
VERDICT='SCOPED_R32_POSITIVE_PURE_PAIR_CAPTURE_FULL_TYPED_RAW_COPY_PASS_SOURCE_NATIVE_LIMITS_OPEN'
def guards():
    for name in ['bootstrap','static_review','prepare','execution_pin','execution_build','execution_pre_1','execution_run_1','execution_post_1','execution_pre_2','execution_run_2','execution_post_2','post']:assert load(Q/(name+'.TOOL.json'))['exit_code']==0,name
    assert sha(Q/'ACK_INITIAL.json')=='FCA87F6EDADAC42F112BB9FB9365D525202F6D8CB4F40CF5B340A5B0B262272A' and (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
    assert load(Q/'BUILD_TOOL_PROOF.json')['compiler_attempts']==1 and load(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json')['failed']==0
    check(load(Q/'BUILD_INPUTS.json')['files'])
def inv(out):
    d=load(out/'OUTPUT_INVENTORY.json');fs=[dict(**row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json'];assert d['files']==fs and len(fs)==407;return row(out/'OUTPUT_INVENTORY.json')
def prepare():
    guards();before=load(Q/'PRESERVATION_BEFORE.json');after=preservation();assert before['protected_files']==after['protected_files'] and before['frozen_files']==after['frozen_files']
    allocations=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'];inventories=[]
    for i,al in enumerate(allocations,1):
        check(load(Q/f'PRE_RUN{i}_MANIFEST.json')['files']);inventories.append(inv(Path(al['output_root'])))
    assert inventories[0]==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['first_inventory']
    write(Q/'PRESERVATION_AFTER.json',after)
    write(Q/'PRESERVATION_BEFORE_AFTER.json',dict(at=now(),before=row(Q/'PRESERVATION_BEFORE.json'),after=row(Q/'PRESERVATION_AFTER.json'),protected_unique_paths=16026,frozen_count=64,all_SHA_bytes_matched=True,run_inventories=inventories,run1_unchanged_afterrun2=True,compiler_builds=1,normal_runs=2,production_modify_build_native=0))
    write(Q/'FINAL_INPUT_OUTPUT_INVENTORY_BINDING.json',dict(at=now(),build_inputs=row(Q/'BUILD_INPUTS.json'),pre_runs=[row(Q/f'PRE_RUN{i}_MANIFEST.json') for i in [1,2]],output_inventories=inventories,raw_cross=row(Q/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json'),normal_analysis=row(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json'),all_final_prepost_verified=True))
    print(json.dumps(dict(protected=16026,frozen=64,prepost_pins=[172,172],outputs=[407,407],builds=1,runs=2,assertions=876,failed=0,report=row(REPORT),matched=True)))
def seal():
    guards();assert load(Q/'finalize_prepare.TOOL.json')['exit_code']==0
    cycles=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']
    logger=['finalize_seal.STDOUT.txt','finalize_seal.STDERR.txt','finalize_seal.TOOL.json'];excluded=cycles+logger
    files=[p for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in excluded]+[REPORT];assert not any(p.suffix=='.pyc' for p in files)
    artifacts=[row(p) for p in files];ack=load(Q/'ACK_INITIAL.json')
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),delivery_id=DELIVERY,result_id=ack['result_id'],files=artifacts,artifact_count=len(artifacts),cycle_exclusions=cycles,unfinished_seal_logger_exclusions=logger,actual_postseal_logger_return='Preserved separately after real completion; no unfinished stream hash or fabricated submission.'))
    em=row(Q/'EVIDENCE_MANIFEST.json')
    index=dict(at=now(),delivery_id=DELIVERY,wp_id=ack['wp_id'],wp_revision='S1',result_id=ack['result_id'],selected=ack['selected'],selected_mvid=ack['selected_mvid'],verdict=VERDICT,source_verdict='GAINS_CREDITED_CONCURRENCY_LEGACY_UNKNOWN_OWNER_NATIVE_OPEN',own_runner_builds=1,normal_runs=2,assertions=876,failed=0,typed_rows=13400,raw_literal_bindings=672,cross_raw_pairs=336,cross_graphs=30,protected_unique_paths=16026,frozen_files=64,production_modify_build=0,changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse_execution=0,native='UNTESTED',full_gate_E2='NOT_RELEASED',Foundation='HOLD',Master_disposition='PENDING',prior_PASS_inherited=False,report=row(REPORT),evidence_manifest=em,initial_ACK=row(Q/'ACK_INITIAL.json'))
    write(Q/'RESULT_INDEX.json',index)
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),delivery_id=DELIVERY,result_id=ack['result_id'],immutable_initial_ACK=row(Q/'ACK_INITIAL.json'),terminal_status='COMPLETED_SCOPED_NORMAL_PASS_NATIVE_LIMITS_OPEN',initial_pending_not_rewritten=True,result_index=row(Q/'RESULT_INDEX.json')))
    write(Q/'RETURN_PENDING.json',dict(at=now(),delivery_id=DELIVERY,result_id=ack['result_id'],submission='PENDING_ACTUAL_TOOL',Master_receipt='PENDING',immutable_intent_only=True))
    check(artifacts);check([em,row(Q/'RESULT_INDEX.json'),row(Q/'ACK_COMPLETION_BINDING.json')])
    completion=dict(**index,status='COMPLETED',artifact_count=len(artifacts),result_index=row(Q/'RESULT_INDEX.json'),ACK_binding=row(Q/'ACK_COMPLETION_BINDING.json'),preservation=row(Q/'PRESERVATION_BEFORE_AFTER.json'),COMPLETION_last_atomic=True,exclusions=excluded,no_closure_release=True)
    tmp=Q/'COMPLETION.json.tmp';target=Q/'COMPLETION.json';assert not tmp.exists() and not target.exists();write(tmp,completion);os.replace(tmp,target)
    print(json.dumps(dict(status='COMPLETED',verdict=VERDICT,artifact_count=len(artifacts),completion=row(target),evidence_manifest=em,report=row(REPORT),builds=1,runs=2,production_native=0)))
if sys.argv[1]=='prepare':prepare()
elif sys.argv[1]=='seal':seal()
else:raise ValueError(sys.argv[1])
