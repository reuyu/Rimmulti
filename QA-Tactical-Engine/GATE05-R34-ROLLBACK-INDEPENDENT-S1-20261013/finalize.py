from common import *
from normal_tools import verify_inventory
import sys
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R34_Rollback_Independent_S1_20261013.md'
RESULT=load(Q/'ACK_INITIAL.json')['result_id']
def guards():
    for n in ['bootstrap','static_r1','prepare','plumbing','host_pin','host_build','host_pre_1','host_run_1','host_post_1','host_pre_2','host_run_2','host_post_2','post','PATCH_LOCATOR']:
        d=load(Q/(n+'.TOOL.json'));assert d['exit_code']==0,n;check([d['stdout'],d['stderr']])
    assert load(Q/'static.TOOL.json')['exit_code']==1
    assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='4C08BBF001058E596DDA362AB8433884A6C06DA319FDF89A61E849310BA37FEB'
    a=load(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json')
    assert a['verdict']==VERDICT and a['total_assertions']==876 and a['failed']==0 and a['builds']==1 and a['fresh_processes']==2
    assert a['typed_rows']==13400 and a['raw_literal_bindings']==672 and a['cross_raw_pairs']==336 and a['cross_ordered_graphs']==30
    assert a['production_modify_build']==a['changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse']==0
    return a
mode=sys.argv[1];a=guards()
if mode=='prepare':
    before=load(Q/'PRESERVATION_BEFORE.json');after=preservation()
    for k in ['protected_files','frozen_files']:assert before[k]==after[k],k
    check(load(Q/'BUILD_INPUTS.json')['files']);assert load(Q/'BUILD_INPUTS.json')['input_count']==188
    runs=[]
    for i,al in enumerate(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'],1):
        out=Path(al['output_root']);pre=load(Q/f'PRE_RUN{i}_MANIFEST.json');post=load(out/'POST_RUN_IDENTITY.json');assert pre['files']==post['files'] and post['actual_exit']==0 and len(pre['files'])==201;check(pre['files']);inv=verify_inventory(out);assert load(out/'OUTPUT_INVENTORY.json')['file_count']==407
        runs.append(dict(pre=row(Q/f'PRE_RUN{i}_MANIFEST.json'),post=row(out/'POST_RUN_IDENTITY.json'),pins=201,inventory=inv,outputs=407))
    assert runs[0]['inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['first_inventory']
    write(Q/'PRESERVATION_AFTER.json',after)
    write(Q/'PRESERVATION_BEFORE_AFTER.json',dict(at=now(),before=row(Q/'PRESERVATION_BEFORE.json'),after=row(Q/'PRESERVATION_AFTER.json'),protected_count=18163,frozen_count=75,all_full_lists_equal=True,all_SHA_bytes_match=True))
    write(Q/'FINAL_INPUT_OUTPUT_BINDING.json',dict(at=now(),build_input_count=188,build_inputs=row(Q/'BUILD_INPUTS.json'),runs=runs,report=row(REPORT),production_changes=0))
    print(json.dumps(dict(all_preserved=True,protected=18163,frozen=75,build_pins=188,run_pins=[201,201],outputs=[407,407],report=row(REPORT))))
elif mode=='seal':
    d=load(Q/'finalize_prepare.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']]);check([load(Q/'FINAL_INPUT_OUTPUT_BINDING.json')['report']])
    excluded=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json','finalize_seal.STDOUT.txt','finalize_seal.STDERR.txt','finalize_seal.TOOL.json']
    fs=[row(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.relative_to(Q).as_posix() not in excluded]+[row(REPORT)];check(fs)
    ctx=dict(delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R34_ROLLBACK_INDEPENDENT',stage='S1',result_id=RESULT,verdict=VERDICT,Master_disposition='PENDING',Foundation='HOLD',native='UNTESTED',full_native_E2='NOT_RELEASED')
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),**ctx,files=fs,file_count=len(fs),cycle_and_postseal_exclusions=excluded,postseal_proof_policy='Actual numeric seal exit/full first streams and structured direct return captured separately; no initial ACK or sealed evidence rewrite'))
    stats={k:a[k] for k in ['builds','fresh_processes','total_assertions','failed','typed_rows','raw_literal_bindings','cross_raw_pairs','cross_ordered_graphs','production_modify_build','changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse','old_PASS_inherited']}
    write(Q/'RESULT_INDEX.json',dict(at=now(),**ctx,statistics=stats,static_verdict='R34_NARROW_ROLLBACK_SOURCE_GAINS_SUPPORTED_NATIVE_CLAIMS_UNSUPPORTED_NATIVE_UNTESTED',source_assessments=13,source_failure_paths=9,source_labels_not_tests=True,prose_only_rebuild_required=False,protected=18163,frozen=75,report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ACK=row(Q/'ACK_INITIAL.json'),preservation=row(Q/'PRESERVATION_BEFORE_AFTER.json'),own_passive_locator_exit1_preserved=True,no_compiler_runner_failure=True))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),**ctx,initial_ACK=row(Q/'ACK_INITIAL.json'),initial_ACK_mirror=row(Q/'ACK.json'),report=row(REPORT),index=row(Q/'RESULT_INDEX.json'),manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ACK_unchanged=True))
    write(Q/'RETURN_PENDING.json',dict(at=now(),**ctx,intent='Direct terminal report once after successful actual seal; return captured separately',status='PENDING_TOOL_SUBMISSION'))
    arts=[row(Q/n) for n in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_PENDING.json','PRESERVATION_BEFORE_AFTER.json']]+[row(REPORT)];check(load(Q/'EVIDENCE_MANIFEST.json')['files']);check(arts)
    comp=dict(at=now(),**ctx,status='COMPLETED',artifacts=arts,evidence_file_count=len(fs),statistics=stats,production_candidate_modified_rebuilt_installed=0,modified_lifecycle_native_operator_adverse_executions=0,source_gains=True,universal_claims_unsupported=True,closure=False,atomic_completion_last=True,postseal_exclusions=excluded)
    write(Q/'COMPLETION.json.tmp',comp);assert not (Q/'COMPLETION.json').exists();(Q/'COMPLETION.json.tmp').rename(Q/'COMPLETION.json')
    print(json.dumps(dict(report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json'),evidence_file_count=len(fs),verdict=VERDICT)))
else:raise ValueError(mode)
