from pathlib import Path
import json
import master_r29_s1_stop_prepare_s2_20261012 as m

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];Q=Path(d['qa_root']);co=m.read(Q/'COMPLETION.json');rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')
 assert c['active_operation'] is None and co['status']=='COMPLETED' and co['delivery_id']==d['delivery_id'] and not any(v.get('result_id')==co['result_id'] for v in rec['processed_results'])
 raw=m.read(m.C/'MASTER_SOL_R33_PREP_COMPLETION_SNAPSHOT_20261013.json');s=json.loads(raw['content'][0]['text'])['polls'][0]
 assert s['thread']['status']['type']=='idle' and s['latestTurn']['status']=='completed' and s['latestTurn']['id']==d['resume_turn_id']
 assert co['all_candidate_compiler_runner_global_Unity_native_operator_Process_adverse_executions']==0 and co['mutable_R33_reads_hashes']==0 and not co['old_PASS_inherited']
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==co['artifact_count']==44
 for v in em['files']:m.check(v)
 for k in ['report','evidence_manifest','preservation','initial_ACK','resume_ACK','result_index','ACK_binding','selected_frozen_R32']:m.check(co[k])
 for n in ['RESULT_INDEX.json','ACK_COMPLETION_BINDING_R1.json']:
  x=m.read(Q/n);assert x['delivery_id']==co['delivery_id'] and x['result_id']==co['result_id'] and x['resume_id']==co['resume_id']
 p=m.read(Q/'PRESERVATION_BEFORE_AFTER_R1.json')
 for k in ['original_before','resume_before','after','partial_manifest']:m.check(p[k])
 before=m.read(Path(p['original_before']['path']));resume=m.read(Path(p['resume_before']['path']));after=m.read(Path(p['after']['path']))
 baseline=m.read(Path(d['baseline_path']));frozen=m.read(Path(d['frozen_manifest']));partial=m.read(Path(p['partial_manifest']['path']))
 def ident(rows):return {v['path'].lower():(v['sha256'],v['bytes']) for v in rows}
 assert ident(after['protected_files'])==ident(before['protected_files'])==ident(resume['protected_files'])==ident(baseline['files'])
 for key in ['additional_helper_files','frozen_files']:assert ident(before[key])==ident(resume[key])==ident(after[key])
 assert ident(resume['partial_files'])==ident(after['partial_files'])==ident(partial['files'])
 assert len(after['protected_files'])==16929 and len(after['partial_files'])==26
 for key in ['additional_helper_files','frozen_files','partial_files']:
  for v in after[key]:m.check(v)
 returnproof=m.read(Q/'RETURN_TOOL_PROOF_R1.json');assert not returnproof.get('isError');assert '01a1156b-97ec-7ce0-9e4a-dfc4a3acb174' in returnproof['content'][0]['text']
 # This invocation already independently hashed the full original baseline. Compare
 # every final inventory row to that baseline; do not assert another full rehash.
 fullproof=m.C/'MASTER_SOL_R33_PREP_ACK_AND_USAGE_RECONCILIATION_20261013.json';assert fullproof.exists()
 terminal=m.C/'MASTER_R33_NATIVE_PREP_TERMINAL_PRESERVATION_20261013.json';files=[m.row(v) for v in sorted(Q.rglob('*')) if v.is_file()]+[m.row(Path(co['report']['path']))]
 m.create(terminal,dict(at=m.now(),files=files,original_plans_ACK_partial26_failed_usage_raw_and_new_R1_terminal_immutable=True))
 verdict='ACCEPTED_PREPARATION_NATIVE_NOT_READY_NO_R33_CANDIDATE_VERDICT'
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R33_NATIVE_PREPARATION_S1_20261013.md';assert not review.exists()
 review.write_text(f'''# R33 native/resource 준비 S1 — Master 판정

{verdict}.

원래 Sol 대화의 동일 WP/S1·고유 result·metadata-only resume R1과 실제 completed/idle cursor24를 확인했다. Manifest44, report, 초기/재개 ACK, index/terminal binding, preservation 및 실제 Master 보고 tool 성공을 SHA/bytes로 대조했다. 초기 usage-limit 실패를 완료로 승계하지 않고, 같은 승인 범위의 새 metadata finalizer가 완료한 증거를 채택한다. 기존 부분26 및 실패 원문은 수정하지 않았다. 과거 요약의 부분31개 표현은 실제26개 manifest가 controlling correction이다.

이 준비는 frozen R32 Debug0B23C358…/MVID7d436c98…에 한정한다. Source 의무9·정상 관측8phase·소유권8row·readiness blocker7·후속 admission3track은 계획 개수다. Candidate/compiler/runner/global/Unity/native/operator/Process/adverse 실행0, mutable R33 읽기/해시0. R33 후보 검토나 runtime PASS로 승격하지 않는다.

원본16929 protected rows와 original/resume/final 전체 identity graph가 같고, 추가 R32helper5/frozen64/partial26은 실제 다시 검사했다. 전체16929의 Master 실제 해시는 같은 invocation의 {fullproof}에 이미 기록돼 있다. 이 문서는 final inventory 전체 행 대조를 기록하며 또 한 번 전체1.93GB 해시를 실행했다고 주장하지 않는다. Terminal 원문과 postseal actual exit/return 기록 {len(files)}개를 별도 불변 manifest로 보존한다.

준비 계획은 prospective exact candidate/source/PDB/content/authority/context와 literal operator/custody/carrier/publisher/isolated runtime 결속, Worker-origin PID/start/MainModule/loaded identity, normal resource commit·정상 종료의 실제 관측, launch→exit sealed evidence 순서를 요구한다. 독립 safe observer/현재 custody/loaded content/full runtime이 미충족이면 UNOBSERVED/STOP이다. Private observer·새 callback/native 실행은 승인하지 않는다. Historical7file pack의 부족은 과거 정보이며 현재 실패 원인으로 단정하지 않는다. 정상 shutdown만으로 unknown owner·동시 abort·Thread.Abort/native teardown 성공을 증명할 수 없다. 스키마/authority를 약화하거나 game profile을 가정하지 않는다.

다음은 새 frozen R33 71개·DebugEC01A3B3…/MVIDadb6cbc8…에 대한 별도 독립 STATIC + fresh positive Pair6/Capture4 QA다. 준비 PASS를 승계하지 않는다. 기존 승인 WP를 덮어쓰지 않고 이 판정/terminal 보존을 별도 release supplement로 추가한다. Master R33 E1의 lock 내부 Stop/Abort/과도한 수학적 deadlock 주장 제한도 독립 리뷰 대상이다. Production 재빌드·수정0/수정된 lifecycle·native 실행 미승인. 새 A 수정 WP는 독립 findings 후 결정한다.

High4 및 Engine002006/Pipeline007/current schema/G-Q1/exact PlayerGlobal/physical split OPEN, installed incident OPEN actor UNKNOWN, Foundation HOLD, full/native E2 NOT_RELEASED. 동일 hourly scheduler PAUSED; Sol 직접 통신은 계속한다.
''',encoding='utf-8')
 proof=m.C/'MASTER_SOL_R33_PREPARATION_COMPLETION_VERIFICATION_20261013.json'
 summary=dict(at=m.now(),delivery_id=co['delivery_id'],result_id=co['result_id'],resume_id=co['resume_id'],completion=m.row(Q/'COMPLETION.json'),actual_snapshot=s,evidence_files=44,protected_inventory_rows_compared=16929,same_invocation_full_rehash_proof=m.row(fullproof),additional_actual_rehash=dict(helper5=5,frozen64=64,partial26=26),review=m.row(review),terminal_preservation=m.row(terminal),terminal_files=len(files),master_verdict=verdict,all_candidate_executions=0,R33_candidate_verdict='NOT_REVIEWED_BY_PREPARATION',nativeE2='NOT_RELEASED',Foundation='HOLD',guard_run='MASTER-R33-CONTINUE-20261013-02',guard_session=91758)
 m.create(proof,summary)
 supplement=m.C/'MASTER_R33_INDEPENDENT_QA_RELEASE_SUPPLEMENT_20261013.json'
 m.create(supplement,dict(at=m.now(),delivery_id=c['sol_prepared_delivery']['delivery_id'],approved=True,scope='EXISTING_APPROVED_WP_UNCHANGED_ADDITIVE_PREP_TERMINAL_PRESERVATION',preparation_review=m.row(review),preparation_proof=m.row(proof),additional_protected_manifest=m.row(terminal),existing_wp=m.row(Path(c['sol_prepared_delivery']['wp_path'])),existing_baseline=m.row(Path(c['sol_prepared_delivery']['baseline_path'])),all_preparation_terminal_paths_immutable=True,Foundation='HOLD',nativeE2='NOT_RELEASED'))
 d.update(status='COMPLETED_MASTER_ACCEPTED_PREPARATION_NATIVE_NOT_READY',master_disposition=verdict,completion_sha256=summary['completion']['sha256'],master_review=str(review));c.update(sol_current_delivery=d,sol_latest_completion=dict(summary,proof=m.row(proof)),sol_status=d['status'],last_sol_cursor=s['cursor'],sol_snapshot_cursor=s['cursor'],updated_at=m.now())
 c['sol_prepared_delivery'].update(delivery_status='APPROVED_NOT_SENT_READY_FRESH_IDLE_CHECK',release_supplement=str(supplement),release_supplement_sha256=m.row(supplement)['sha256']);m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 rec['processed_results'].append(dict(at=m.now(),recipient='Sol',result_id=co['result_id'],completion_sha256=summary['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(proof)));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');b['tasks'][-1]['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(terminal),sha256=m.row(terminal)['sha256']));b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['sol'].update(current_status=d['status'],current_runtime_idle_verified=True,current_runtime_status='ACTUAL_COMPLETED_IDLE',last_cursor=s['cursor'],last_result_id=co['result_id'],latest_review=str(review));m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(summary,event='SOL_R33_PREPARATION_TERMINAL_MASTER_DISPOSED_FRESH_CANDIDATE_QA_RELEASE_READY',proof=m.row(proof)))
 m.append_delta('LOCAL-SOL-R33-NATIVE-PREPARATION-S1-COMPLETE',verdict+'. Original resumedturn actualcompletedidle24/evidence44/terminal'+str(len(files))+' preserved. Whole16929 original-resume-final rows matched; sameinvocation Master fullrehash reused transparently, actualadditional5+64+26 rehashed. Allcandidate/compiler/native0/R33notreviewed. Plan9obligations8phases8ownership7blockers3tracks notexecutions. FrozenR33 DebugEC01A3B3/MVIDadb6 newindependentSTATIC+freshpositivePair6Capture4 WP unchanged/additiveterminal release supplement approvedNOTSENTuntilfreshidle. SamehourlyPAUSED/High4OPEN/FoundationHOLD/nativeE2NOTRELEASED. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status='PREPARATION_DISPOSED_FRESH_R33_QA_READY',terminal_files=len(files),proof=m.row(proof),supplement=m.row(supplement))))

if __name__=='__main__':main()
