from common import *
from normal_tools import verify_inventory
import sys
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R33_Resource_Commit_Independent_S1_20261013.md'
RESULT=load(Q/'ACK_INITIAL.json')['result_id']
VERDICT='SCOPED_R33_NORMAL_PURE_PAIR_CAPTURE_FULL_TYPED_RAW_COPY_PASS_STATIC_LOCK_ROLLBACK_REVISION_REQUIRED_NATIVE_UNTESTED'
stages=['bootstrap','static_r1','prepare','host_pin','host_build','host_pre_1','host_run_1','host_post_1','host_pre_2','host_run_2','host_post_2','post','RECOVERY_FINALIZE']
def guards():
    for n in stages:
        d=load(Q/(n+'.TOOL.json'));assert d['exit_code']==0,n;check([d['stdout'],d['stderr']])
    p=load(Q/'PATCH_R1_TOOL.json');assert p['exit_code']==0;check([p['stdout'],p['stderr']])
    assert load(Q/'static.TOOL.json')['exit_code']==1
    assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='A50AE909E62719528753EFA2C7485A83D77EB473239CA86BB22641DB487FA4EE'
    a=load(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json')
    assert a['verdict']==VERDICT and a['total_assertions']==876 and a['failed']==0 and a['builds']==1 and a['fresh_processes']==2
    assert a['typed_rows']==13400 and a['raw_literal_bindings']==672 and a['cross_raw_pairs']==336 and a['cross_ordered_graphs']==30
    assert a['production_modify_build']==a['changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse']==0
    assert REPORT.is_file()
    return a
mode=sys.argv[1];a=guards()
if mode=='prepare':
    before=load(Q/'PRESERVATION_BEFORE.json');after=preservation()
    for k in ['protected_files','frozen_files','prep_terminal_files','outside_helper_files']:assert before[k]==after[k],k
    build=check(load(Q/'BUILD_INPUTS.json')['files']);assert len(build)==236
    runs=[]
    for i,alloc in enumerate(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'],1):
        out=Path(alloc['output_root']);pre=load(Q/f'PRE_RUN{i}_MANIFEST.json');post=load(out/'POST_RUN_IDENTITY.json')
        assert pre['files']==post['files'] and post['actual_exit']==0 and len(pre['files'])==249
        check(pre['files']);inv=verify_inventory(out);assert load(out/'OUTPUT_INVENTORY.json')['file_count']==407
        runs.append(dict(pre=row(Q/f'PRE_RUN{i}_MANIFEST.json'),post=row(out/'POST_RUN_IDENTITY.json'),pins=249,inventory=inv,outputs=407))
    assert runs[0]['inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['first_inventory']
    write(Q/'PRESERVATION_AFTER.json',after)
    write(Q/'PRESERVATION_BEFORE_AFTER.json',dict(at=now(),before=row(Q/'PRESERVATION_BEFORE.json'),after=row(Q/'PRESERVATION_AFTER.json'),protected_count=17099,frozen_count=71,prep_terminal_count=54,outside_helper_count=6,all_full_lists_equal=True,all_SHA_bytes_match=True))
    write(Q/'FINAL_INPUT_OUTPUT_BINDING.json',dict(at=now(),build_input_count=len(build),build_inputs=row(Q/'BUILD_INPUTS.json'),runs=runs,run1_unchanged=True,report=row(REPORT),production_changes=0))
    print(json.dumps(dict(all_preserved=True,protected=17099,frozen=71,terminal=54,helpers=6,build_pins=236,run_pins=[249,249],outputs=[407,407],report=row(REPORT))))
elif mode=='seal':
    d=load(Q/'finalize_prepare.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']])
    check([load(Q/'FINAL_INPUT_OUTPUT_BINDING.json')['report']]);assert load(Q/'PRESERVATION_BEFORE_AFTER.json')['all_full_lists_equal']
    excluded=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json','finalize_seal.STDOUT.txt','finalize_seal.STDERR.txt','finalize_seal.TOOL.json']
    fs=[row(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.relative_to(Q).as_posix() not in excluded]+[row(REPORT)]
    check(fs)
    context=dict(delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R33_RESOURCE_COMMIT_INDEPENDENT',stage='S1',result_id=RESULT,verdict=VERDICT,Master_disposition='PENDING',Foundation='HOLD',native='UNTESTED',full_native_E2='NOT_RELEASED')
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),**context,files=fs,file_count=len(fs),cycle_and_postseal_exclusions=excluded,postseal_proof_policy='Actual numeric seal exit/full first streams and structured direct return captured separately; no initial ACK or sealed evidence rewrites'))
    stats={k:a[k] for k in ['builds','fresh_processes','total_assertions','failed','typed_rows','raw_literal_bindings','cross_raw_pairs','cross_ordered_graphs','production_modify_build','changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse','old_PASS_inherited']}
    write(Q/'RESULT_INDEX.json',dict(at=now(),**context,statistics=stats,static_verdict='RESOURCE_PARENT_ORDER_GAINS_LOCK_HELD_ROLLBACK_CLAIM_REVISION_REQUIRED_NATIVE_UNTESTED',static_assessments=12,protected=17099,frozen=71,prep_terminal=54,outside_helpers=6,report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ACK=row(Q/'ACK_INITIAL.json'),preservation=row(Q/'PRESERVATION_BEFORE_AFTER.json'),owned_passive_locator_exit1_preserved=True,no_compiler_or_runner_failure=True))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),**context,initial_ACK=row(Q/'ACK_INITIAL.json'),initial_ACK_mirror=row(Q/'ACK.json'),report=row(REPORT),index=row(Q/'RESULT_INDEX.json'),manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ACK_unchanged=True))
    write(Q/'RETURN_PENDING.json',dict(at=now(),**context,intent='Direct terminal report once to Master after successful actual seal; return captured separately',status='PENDING_TOOL_SUBMISSION'))
    artifacts=[row(Q/n) for n in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_PENDING.json','PRESERVATION_BEFORE_AFTER.json']]+[row(REPORT)]
    check(load(Q/'EVIDENCE_MANIFEST.json')['files']);check(artifacts)
    completion=dict(at=now(),**context,status='COMPLETED',artifacts=artifacts,evidence_file_count=len(fs),statistics=stats,production_candidate_modified_rebuilt_installed=0,modified_lifecycle_native_operator_adverse_executions=0,source_revision_required=True,closure=False,atomic_completion_last=True,postseal_exclusions=excluded)
    write(Q/'COMPLETION.json.tmp',completion);assert not (Q/'COMPLETION.json').exists();(Q/'COMPLETION.json.tmp').rename(Q/'COMPLETION.json')
    print(json.dumps(dict(report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json'),evidence_file_count=len(fs),verdict=VERDICT)))
else:raise ValueError(mode)
