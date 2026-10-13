from qa_common import *
import sys
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R30_Handoff_Independent_Static_S1_20261012.md'
VERDICT='REVISION_REQUIRED_REQUIRED_MODE_LIFETIME_CUSTODY_AND_EVIDENCE_NATIVE_UNTESTED'
def guard():
    for name in ['bootstrap.TOOL.json','METADATA_SCHEMA_R1_PREPARE_TOOL.json','review_static_r1_references.TOOL.json','review_static_r1_source.TOOL.json','EVIDENCE_REVIEW_branches_TOOL.json','EVIDENCE_REVIEW_provenance_TOOL.json','CLAIMS_REVIEW_TOOL.json']:
        assert load(Q/name)['exit_code']==0,name
    assert load(Q/'review_static_references.TOOL.json')['exit_code']==1
    verify(load(MAN)['files'],'frozen_path')
    assert load(Q/'ACK_INITIAL.json')==load(Q/'ACK.json') and load(Q/'ACK_INITIAL.json')['delivery_id']==DELIVERY
if __name__=='__main__':
    mode=sys.argv[1];guard()
    if mode=='prepare':
        after=preservation();before=load(Q/'PRESERVATION_BEFORE.json')
        assert after['protected_files']==before['protected_files'] and after['frozen_files']==before['frozen_files']
        write(Q/'PRESERVATION_AFTER.json',after)
        prov=load(Q/'PROVENANCE_AND_ORIGINAL_DRIFT_REVIEW.json');assert prov['independent_drift_count']==12 and prov['master_drift_pathset_match']
        verify(prov['old_frozen132_verified'])
        for v in prov['original_E1_scope_current_changed']:
            verify([v['old_frozen_reference'],v['current_original']])
        cases=load(Q/'SOURCE_BRANCH_CUSTODY_REVIEW.json')['source_only_cases'];claims=load(Q/'CLAIM_EVIDENCE_MATRIX.json')['claims']
        assert len(cases)==16 and len(claims)==17 and REPORT.is_file()
        write(Q/'FINAL_REVIEW_VALIDATION.json',dict(at=now(),report=row(REPORT),protected_before=row(Q/'PRESERVATION_BEFORE.json'),protected_after=row(Q/'PRESERVATION_AFTER.json'),protected15549_unchanged=True,frozen128_unchanged=True,old_frozen132_unchanged=True,old_original_drift12_current_snapshot_unchanged=True,static_source_cases=16,claim_reviews=17,metadata_locator_original_failure_preserved=True,verdict=VERDICT,candidate_compiler_runner_native_global_game_Process_adverse_calls=0,sourceHighclosure=0,Foundation='HOLD',native_E2='NOT_RELEASED'))
        print(json.dumps(dict(protected=15549,frozen=128,old_frozen=132,drift12_snapshot_preserved=True,cases=16,claims=17,report=row(REPORT),verdict=VERDICT,candidate_calls=0)))
    elif mode=='seal':
        assert load(Q/'finalize_prepare.TOOL.json')['exit_code']==0
        verify([load(Q/'FINAL_REVIEW_VALIDATION.json')['report']])
        initial=load(Q/'ACK_INITIAL.json');assert not (Q/'COMPLETION.json').exists()
        cycles={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
        unfinished={'finalize_seal.STDOUT.txt','finalize_seal.STDERR.txt','finalize_seal.TOOL.json'}
        paths=[p for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in cycles|unfinished and '__pycache__' not in p.parts]
        rows=[row(p) for p in paths]+[row(REPORT)];verify(rows)
        write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),delivery_id=DELIVERY,result_id=initial['result_id'],file_count=len(rows),files=rows,excluded_cycles=sorted(cycles),actual_unfinished_seal_logger_excluded=sorted(unfinished),exclusion_reason='Actual outer seal logger first streams and postreturn tool preserved separately; no unfinished hash claimed',recursive_own_set=True,report=row(REPORT)))
        artifacts={k:row(p) for k,p in [('report',REPORT),('manifest',Q/'EVIDENCE_MANIFEST.json'),('source_branch_custody',Q/'SOURCE_BRANCH_CUSTODY_REVIEW.json'),('claim_matrix',Q/'CLAIM_EVIDENCE_MATRIX.json'),('provenance_drift',Q/'PROVENANCE_AND_ORIGINAL_DRIFT_REVIEW.json'),('source_byte_map',Q/'SOURCE_BYTE_MAP_AND_FULL_CHANGED_SPANS.json'),('PE_PDB_identity',Q/'INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json'),('Unity_reference_IL',Q/'UNITY_REFERENCE_NULL_AND_ADDCOMPONENT_IL.json'),('next_repair',Q/'NEXT_MINIMAL_REPAIR.md'),('path_coverage',Q/'PRESERVATION_POLICY_PATH_COVERAGE_REVIEW.json'),('preservation_before',Q/'PRESERVATION_BEFORE.json'),('preservation_after',Q/'PRESERVATION_AFTER.json'),('final_validation',Q/'FINAL_REVIEW_VALIDATION.json'),('initial_ACK',Q/'ACK_INITIAL.json')]}
        limits=['No candidate/production/compiler/runner/Unity/global/game/native/Process/adverse execution. Static16 cases/17 claims are not executed tests.','R29 normal PASS remains historical; no R30 normal/nativeE2 verdict inherited.','Unity frozen reference managed IL supports conditional null/custody interpretation; actual loaded/installed/native lifetime/Awake timing UNOBSERVED.','Producer original drift12 and stale built prepin7/7 are preserved discrepancies, not fixed expected values.','Matched-owner and per-slot improvements are source credit; durable required-mode/lifetime one-use/whole lifecycle stop remain not established.','Original own metadata schema KeyError retained exit1; separately corrected size locator under WP authorization, no semantic/type/hash change.','Master final adoption/closure/release pending; SourceHigh1/carrier/publisher/evidence integrity and engine/pipeline/schema/GQ1 OPEN/Foundation HOLD.']
        counts=dict(candidate_build_or_execution=0,QA_compiler=0,QA_runner=0,production_modifications=0,global_Awake_Unity_game_native_operator_Process_provider_cache_currenttask_rejection_adverse=0,source_only_cases=16,claim_reviews=17,closure=0)
        write(Q/'RESULT_INDEX.json',dict(at=now(),wp_id=initial['wp_id'],wp_revision='S1',delivery_id=DELIVERY,result_id=initial['result_id'],status='COMPLETED_INDEPENDENT_STATIC_REVISION_REQUIRED',verdict=VERDICT,normal_runtime='UNTESTED',native_E2='NOT_RELEASED',Foundation='HOLD',Master_adoption='PENDING',report_delivery='PENDING',artifacts=artifacts,counts=counts,limitations=limits))
        write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),delivery_id=DELIVERY,result_id=initial['result_id'],ACK_INITIAL=row(Q/'ACK_INITIAL.json'),ACK_mirror=row(Q/'ACK.json'),RESULT_INDEX=row(Q/'RESULT_INDEX.json'),initial_pending_immutable=True,verdict=VERDICT,Master_adoption='PENDING'))
        write(Q/'RETURN_PENDING.json',dict(at=now(),target='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174',host='local',result_id=initial['result_id'],delivery='PENDING',no_unknown_delivery_retry=True))
        artifacts.update(result_index=row(Q/'RESULT_INDEX.json'),ACK_binding=row(Q/'ACK_COMPLETION_BINDING.json'),return_pending=row(Q/'RETURN_PENDING.json'))
        verify(rows);verify(artifacts.values());verify(load(Q/'PRESERVATION_AFTER.json')['protected_files']);verify(load(Q/'PRESERVATION_AFTER.json')['frozen_files'])
        assert {str(p) for p in paths}=={str(p) for p in Q.rglob('*') if p.is_file() and p.name not in cycles|unfinished and '__pycache__' not in p.parts}
        completion=dict(schema_version=1,at=now(),wp_id=initial['wp_id'],wp_revision='S1',delivery_id=DELIVERY,result_id=initial['result_id'],status='COMPLETED',report_kind='INDEPENDENT_STATIC',verdict=VERDICT,static_verdict='REVISION_REQUIRED',runtime='UNTESTED',native_E2='NOT_RELEASED',Foundation='HOLD',Master_adoption='PENDING',report_delivery='PENDING',artifacts=artifacts,counts=counts,limitations=limits,evidence_file_count=len(rows),completion_last_atomic=True)
        tmp=Q/'COMPLETION.json.tmp';assert not tmp.exists();tmp.write_bytes((json.dumps(completion,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));tmp.rename(Q/'COMPLETION.json')
        print(json.dumps(dict(COMPLETION=row(Q/'COMPLETION.json'),manifest=row(Q/'EVIDENCE_MANIFEST.json'),report=row(REPORT),evidence_count=len(rows),status='COMPLETED_STATIC_ONLY_REVISION_REQUIRED')))
    else:raise ValueError(mode)
