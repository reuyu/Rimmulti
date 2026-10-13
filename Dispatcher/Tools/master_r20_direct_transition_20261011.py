from pathlib import Path
import json,hashlib,datetime,sys,tomllib,re
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';c=read(cp);b=read(bp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent
assert t['dispatch_id'].endswith('e35ff656');stage=sys.argv[1]
if stage=='presubmit':
 assert t['delivery_status']=='NOT_SENT' and not c['active_operation']['unknown_delivery']
 draft=read(T/'MASTER_UI_DRAFT.json')['accessibility']['tree'];idle=read(C/'MASTER_R20_CU_IDLE_BEFORE_INPUT_20261011.json')['accessibility']['tree']
 assert 'WarEconomy 컨텍스트 복구 및 수행' in draft and 'Message input Value: '+t['exact_message'] in draft and '단추 Send message' in draft
 assert 'Message input Value:' not in idle and not any(x in idle for x in ['Working','Cancel'])
 for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
 for f in read(Path(t['scope_baseline_path']))['allowed_mutable_paths']:
  q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['size']
 t.update(status='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',submission_attempts=1,submit_attempted_at=at,unknown_delivery=True);b['updated_at']=at;write(bp,b)
 c['active_operation'].update(stage='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',unknown_delivery=True,attempt_started_at=at);c['updated_at']=at;write(cp,c)
 event({'at':at,'event_id':t['dispatch_id']+'-SUBMIT-ATTEMPT','type':'A_R20_ONE_CU_SUBMIT_ATTEMPT','unknown_delivery':True,'dispatch_id':t['dispatch_id'],'exact_draft_proof':str(T/'MASTER_UI_DRAFT.json')});print('ONE_SUBMIT_PENDING_UNKNOWN')
elif stage=='sent':
 assert c['active_operation']['unknown_delivery'] and t['submission_attempts']==1
 q=T/'MASTER_UI_SUBMITTED.json';post=read(q)['accessibility']['tree']
 assert ' 텍스트 '+t['exact_message'] in post
 assert 'Message input Value:' not in post and 'Working' in post and 'Cancel' in post
 pp=T/'MASTER_UI_SUBMISSION_PROOF.json';assert not pp.exists()
 write(pp,{'at':at,'dispatch_id':t['dispatch_id'],'exact_message':t['exact_message'],'one_actual_submit':True,'new_exact_message':True,'composer_empty':True,'working_cancel':True,'post_path':str(q),'post_sha256':sha(q),'send_tool':str(T/'MASTER_UI_SEND_TOOL.json'),'send_tool_sha256':sha(T/'MASTER_UI_SEND_TOOL.json'),'draft':str(T/'MASTER_UI_DRAFT.json'),'idle':str(C/'MASTER_R20_CU_IDLE_BEFORE_INPUT_20261011.json'),'focus_qualification':'UIA RootWebArea but observed screenshot caret in empty composer followed by exact Message input value; first geometry error reobserved before retry, no submission repeated'})
 t.update(delivery_status='SENT',status='SENT_IN_PROGRESS_ACK_PENDING',sent_at=at,unknown_delivery=False,submission_proof=str(pp),submission_proof_sha256=sha(pp));write(bp,b)
 c['active_operation'].update(stage='SENT_MONITOR_RESUME_PENDING',unknown_delivery=False);c.update(a_status=t['status'],a_result_completion_path=t['completion_path'],updated_at=at);write(cp,c)
 event({'at':at,'event_id':t['dispatch_id']+'-ACTUAL-SENT','type':'A_R20_DIRECT_CU_SENT','proof':str(pp),'one_submit':True});print('ACTUAL_SENT_MONITOR_RESUME_PENDING')
elif stage=='finalize':
 assert c['active_operation']['stage']=='SENT_MONITOR_RESUME_PENDING' and not c['active_operation']['unknown_delivery']
 sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
 pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
 pp=T/'MASTER_POSTSENT_PRESERVATION.json';write(pp,pres)
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
 assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
 tool=C/'MASTER_R20_MONITOR_RESUME_TOOL_20261011.json';assert not read(tool).get('isError')
 ack=None;ack_error=None
 if Path(t['ack_path']).exists():
  try:ack=read(Path(t['ack_path']))
  except json.JSONDecodeError as ex:
   ack_error=str(ex)
   rawcopy=T/'MASTER_ACK_MALFORMED_ORIGINAL_20261011.json.txt'
   if not rawcopy.exists():rawcopy.write_bytes(Path(t['ack_path']).read_bytes())
 if ack:assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==23
 sol=json.loads(read(C/'MASTER_R19_DISPOSITION_NOTICE_SOL_FINAL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
 proof={'at':at,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'envelope':23,'status':'SENT_ACK_VERIFIED_IN_PROGRESS' if ack else 'SENT_IN_PROGRESS_ACK_PENDING','one_submit':True,'ui_submission_proof':t['submission_proof'],'ack':ack,'ack_sha256':sha(Path(t['ack_path'])) if ack else None,'automation_actual_config':cfg,'automation_tool':str(tool),'postsent_preservation':str(pp),'counts':{k:len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']},'known_installed_incident':'UNCHANGED_OPEN_ACTOR_UNKNOWN','original_Sol_receipt_notice_actual':sol,'new_QA_WP':False,'future_R20_scheduled_run_observed':False,'guard_run':'MASTER-CONTINUE-R19-20261011-01','guard_session':40147,'guard_pid':19832,'native_permissions':0,'full_runtime_e2_released':False,'scoped_R19_defect':'CLOSED_NORMAL_OPAQUE_ONLY','broader_gate_closure':False,'foundation':'HOLD','verification_attempt_limitation':'First Master read-only verifier was interrupted by Master after metadata latency without disposition; v2 read-only verification completed with all checks. No candidate/QA runner rebuild or rerun.'}
 proof.update(ack_parse_error=ack_error,ack_raw_sha256=sha(Path(t['ack_path'])) if Path(t['ack_path']).exists() else None,ack_status='MALFORMED_PRODUCER_JSON_UNVERIFIED' if ack_error else ('VERIFIED' if ack else 'PENDING'))
 vp=C/'MASTER_GATE05_R20_TRUSTED_STARTUP_DISPATCH_MONITOR_ACTIVE_20261011.json';assert not vp.exists();write(vp,proof)
 t.update(status='IN_PROGRESS' if ack else proof['status'],ack_verified=bool(ack),ack_sha256=proof['ack_sha256'],monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(vp),updated_at=at);b['updated_at']=at;write(bp,b)
 c.update(active_operation=None,a_status='R20_TRUSTED_STARTUP_IN_PROGRESS_ACK_VERIFIED' if ack else 'R20_ACTUAL_SENT_ACK_PENDING',a_latest_delivery=proof,a_latest_runtime_observation=proof,a_pending_dispatch_id=None,a_prepared_dispatch_id=None,last_sol_cursor=sol['cursor'],sol_latest_receipt_notice=proof,sol_next_action='R19_ARTIFACT_ACCEPTED_NO_ACTIVE_QA;AWAIT_NEW_R20_EXACT_FREEZE_ADMISSION_FRESH_ORIGINAL_SOL_QA',updated_at=at)
 c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(vp),future_run_after_engine_r20_resume_observed=False,pause_reason=None,resumed_by='Master after actual R20 one CU submission')
 c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':40147,'guard_pid':19832,'at':at,'status':'R19_INDEPENDENT_SCOPED_PASS_CLOSED_R20_SENT_HOURLY_ACTIVE','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R19_COMPLETE_R20_GUARD_FINALLY_RELEASE_20261011.json')};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['a'].update(current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],execution_phase='IN_PROGRESS',current_runtime_idle_verified=False,ack_verified=bool(ack),last_ui_proof=t['submission_proof'])
 s['endpoints']['sol'].update(execution_phase='R19_ARTIFACT_DISPOSED_RECEIPT_NOTICE_ONLY_NO_QA',current_runtime_idle_verified=sol['thread']['status']['type']=='idle',last_runtime_observation_cursor=sol['cursor'],latest_notice_turn_id=sol['latestTurn']['id'])
 s['master_monitor_automation']=c['master_monitor_automation'];s['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','status':proof['status'],'proof':str(vp),'runtime_e2_released':False});s['updated_at']=at;write(sp,s)
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);eid=t['dispatch_id']+'-SENT-HOURLY-ACTIVE';assert not any(x.get('event_id')==eid for x in r['processed_dispatch_events'])
 e=dict(proof,event_id=eid,type='A_R20_ACTUAL_SENT_HOURLY_ACTIVE',proof_path=str(vp),proof_sha256=sha(vp));r['processed_dispatch_events'].append(e);r['updated_at']=at;write(rp,r);event(e)
 para=f'\n\n## LOCAL-R19-SCOPED-CLOSED-A-R20-SENT-HOURLY-ACTIVE — {at}\nR19 fresh independent390 evidence/9841 protected/both117PASS0FAIL/5576typed0mismatch accepted; ENGINE-G05-OPAQUE-R18-20261010-01 CLOSED normal opaque strings/graph/digest only. Original Sol artifact terminal before usage failure, separately observed failed idle122; receipt notice actual direct tool/new turn recorded, no new QA/rebuild/rerun or substitute. Master producer deDE correction8listed8match+2unlisted logs controls historical10 annotation, original bytes unchanged. A {t["dispatch_id"]}/{t["wp_id"]}/{t["wp_revision"]}/envelope23 actual fresh idle/exactdraft/oneSend/newmessage/emptycomposer/WorkingCancel observed; {proof["status"]}, no resend. Scope bounded Worker M01/M03 explicit local declaration→immutable factory receipt→sealed installer→missing attach/listener/trusted readiness guard; normalPURE E1 only. R19 Snapshot/codec,Census/csproj/runtime7/priorQA fixed; known installedBB incident OPEN actorUNKNOWN. Same actual wareconomy-master ACTIVE60min/173char/correctMastertarget; futureR20run UNOBSERVED. Aterminal→Masterfreeze/admission/pause→originalSolidlefreshQA→necessarytechnicalfollowup automatic. WholeEngine002006/Pipeline007/schema/G-Q1 OPEN/Foundation HOLD/fullnativeGateE2 NOT RELEASED. Proof {vp}\n'
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
 pointer=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';pointer.write_text(f'Current {at}: R19 scoped opaque defect CLOSED on fresh117PASS0FAIL each;A R20 {t["dispatch_id"]} actualSENT/{proof["status"]}/bounded M01M03 trusted local admission and missingready gate/newnormalPURE. Same actualhourlyACTIVE60min. Sol R19 artifactaccepted/threadusagefailure recorded;receipt-only newturn, no activeQA. Next exact R20 candidate afterterminalreview/freeze→freshoriginalSolQA automatically. WholeEngine/Pipeline/schema/GQ1 OPEN/FoundationHOLD/nativeE2NOTRELEASED.\n\n'+pointer.read_text(encoding='utf-8-sig'),encoding='utf8')
 print(json.dumps({'A':proof['status'],'monitor':'ACTIVE60MIN','Sol_notice':sol['thread']['status']['type'],'newQA':False,'scoped_defect':'CLOSED','foundation':'HOLD'}))
elif stage=='released':
 q=C/'MASTER_R19_COMPLETE_R20_GUARD_FINALLY_RELEASE_20261011.json';raw=read(q)['actual_release_tool']
 assert raw['exit_code']==0 and '"status": "RELEASED"' in raw['output'] and '"run_id": "MASTER-CONTINUE-R19-20261011-01"' in raw['output'] and re.search(r'id"\s*:\s*19832\b',raw['output'])
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=re.search(r'"released_at"\s*:\s*"([^"]+)"',raw['output']).group(1),all_child_commands_completed_before_release=True);c['updated_at']=at;write(cp,c)
 event({'at':at,'event_id':'MASTER-R19-R20-GUARD-RELEASE-20261011-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':'MASTER-CONTINUE-R19-20261011-01','pid':19832,'proof':str(q)});print('ACTUAL_GUARD_RELEASE_RECORDED')
else:raise ValueError(stage)
