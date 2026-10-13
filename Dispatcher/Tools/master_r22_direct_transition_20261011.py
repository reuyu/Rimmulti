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
assert t['dispatch_id'].endswith('9be1579a');stage=sys.argv[1]
if stage=='presubmit':
 assert t['delivery_status']=='NOT_SENT' and not c['active_operation']['unknown_delivery']
 draft=read(T/'MASTER_UI_DRAFT.json')['accessibility']['tree'];idle=read(C/'MASTER_R22_CU_IDLE_BEFORE_INPUT_20261011.json')['accessibility']['tree']
 assert 'WarEconomy 컨텍스트 복구 및 수행' in draft and 'Message input Value: '+t['exact_message'] in draft and '단추 Send message' in draft
 assert 'Message input Value:' not in idle and not any(x in idle for x in ['Working','Cancel'])
 for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
 for f in read(Path(t['scope_baseline_path']))['allowed_mutable_paths']:
  q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['size']
 t.update(status='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',submission_attempts=1,submit_attempted_at=at,unknown_delivery=True);b['updated_at']=at;write(bp,b)
 c['active_operation'].update(stage='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',unknown_delivery=True,attempt_started_at=at);c['updated_at']=at;write(cp,c)
 event({'at':at,'event_id':t['dispatch_id']+'-SUBMIT-ATTEMPT','type':'A_R22_ONE_CU_SUBMIT_ATTEMPT','unknown_delivery':True,'dispatch_id':t['dispatch_id'],'exact_draft_proof':str(T/'MASTER_UI_DRAFT.json'),'metadata_preparation_qualification':'R21 freshQA disposition and narrow closure succeeded;R22 prepared new uniqueID/exactfourregions;one initial JS patch parse error wrote0/input0, corrected before actualpreparation/no productionchange'});print('ONE_SUBMIT_PENDING_UNKNOWN')
elif stage=='sent':
 assert c['active_operation']['unknown_delivery'] and t['submission_attempts']==1
 q=T/'MASTER_UI_SUBMITTED.json';post=read(q)['accessibility']['tree']
 assert ' 텍스트 '+t['exact_message'] in post and 'Message input Value:' not in post and 'Working' in post and 'Cancel' in post
 pp=T/'MASTER_UI_SUBMISSION_PROOF.json';assert not pp.exists()
 write(pp,{'at':at,'dispatch_id':t['dispatch_id'],'exact_message':t['exact_message'],'one_actual_submit':True,'new_exact_message':True,'composer_empty':True,'working_cancel':True,'post_path':str(q),'post_sha256':sha(q),'send_tool':str(T/'MASTER_UI_SEND_TOOL.json'),'send_tool_sha256':sha(T/'MASTER_UI_SEND_TOOL.json'),'draft':str(T/'MASTER_UI_DRAFT.json'),'idle':str(C/'MASTER_R22_CU_IDLE_BEFORE_INPUT_20261011.json'),'focus_qualification':'RootWebArea UIA; observed screenshot caret in composer, then exact inputValue. Immediate typing accessibility stale,reobserved no duplicate type/submit.'})
 t.update(delivery_status='SENT',status='SENT_IN_PROGRESS_ACK_PENDING',sent_at=at,unknown_delivery=False,submission_proof=str(pp),submission_proof_sha256=sha(pp));write(bp,b)
 c['active_operation'].update(stage='SENT_MONITOR_RESUME_PENDING',unknown_delivery=False);c.update(a_status=t['status'],a_result_completion_path=t['completion_path'],updated_at=at);write(cp,c)
 event({'at':at,'event_id':t['dispatch_id']+'-ACTUAL-SENT','type':'A_R22_DIRECT_CU_SENT','proof':str(pp),'one_submit':True});print('ACTUAL_SENT_MONITOR_RESUME_PENDING')
elif stage=='finalize':
 assert c['active_operation']['stage']=='SENT_MONITOR_RESUME_PENDING' and not c['active_operation']['unknown_delivery']
 sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
 pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
 pp=T/'MASTER_POSTSENT_PRESERVATION.json';write(pp,pres)
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
 assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
 tool=C/'MASTER_R22_MONITOR_RESUME_TOOL_20261011.json';assert not read(tool).get('isError')
 ack=None;ackerr=None
 if Path(t['ack_path']).exists():
  try:ack=read(Path(t['ack_path']))
  except json.JSONDecodeError as ex:ackerr=str(ex)
 if ack:assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==25
 sol=json.loads(read(C/'MASTER_R21_DISPOSITION_NOTICE_SOL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
 proof={'at':at,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'envelope':25,'status':'SENT_ACK_VERIFIED_IN_PROGRESS' if ack else 'SENT_IN_PROGRESS_ACK_PENDING','one_submit':True,'ui_submission_proof':t['submission_proof'],'ack':ack,'ack_sha256':sha(Path(t['ack_path'])) if ack else None,'ack_parse_error':ackerr,'automation_actual_config':cfg,'automation_tool':str(tool),'postsent_preservation':str(pp),'counts':{k:len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']},'known_installed_incident':'UNCHANGED_OPEN_ACTOR_UNKNOWN','original_Sol_receipt_notice_actual':sol,'new_QA_WP':False,'future_R22_scheduled_run_observed':False,'guard_run':'MASTER-SOL-R21-COMPLETE-20261011-01','guard_session':26221,'guard_pid':27436,'native_permissions':0,'full_runtime_e2_released':False,'R21_disposition':'SCOPED_UTC_LITERAL_FULL_GRAPH_BYTES_PASS_CLOSED','broader_gate_closure':False,'foundation':'HOLD','R22_source_scope':'M01_EXPLICIT7_PRIVATE_CAPTURE_FOUR_REGIONS_FIXED_SEGMENTS'}
 vp=C/'MASTER_GATE05_R22_DECLARATION_DISPATCH_MONITOR_ACTIVE_20261011.json';assert not vp.exists();write(vp,proof)
 t.update(status='IN_PROGRESS' if ack else proof['status'],ack_verified=bool(ack),ack_sha256=proof['ack_sha256'],monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(vp),updated_at=at);b['updated_at']=at;write(bp,b)
 c.update(active_operation=None,a_status='R22_DECLARATION_IN_PROGRESS_ACK_VERIFIED' if ack else 'R22_ACTUAL_SENT_ACK_PENDING',a_latest_delivery=proof,a_latest_runtime_observation=proof,a_pending_dispatch_id=None,a_prepared_dispatch_id=None,last_sol_cursor=sol['cursor'],sol_latest_receipt_notice=proof,sol_next_action='R21_DISPOSED_NO_ACTIVE_QA;AWAIT_NEW_R22_EXACT_FREEZE_ADMISSION_FRESH_ORIGINAL_SOL_QA',updated_at=at)
 c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(vp),future_run_after_engine_r22_resume_observed=False,pause_reason=None,resumed_by='Master after actual R22 one CU submission')
 c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':26221,'guard_pid':27436,'at':at,'status':'R21_INDEPENDENT_DISPOSED_R22_SENT_HOURLY_ACTIVE','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R21_COMPLETE_R22_GUARD_FINALLY_RELEASE_20261011.json')};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['a'].update(current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],execution_phase='IN_PROGRESS',current_runtime_idle_verified=False,ack_verified=bool(ack),last_ui_proof=t['submission_proof'])
 s['endpoints']['sol'].update(execution_phase='R21_DISPOSED_RECEIPT_NOTICE_ONLY_NO_QA',current_runtime_idle_verified=sol['thread']['status']['type']=='idle',last_runtime_observation_cursor=sol['cursor'],latest_notice_turn_id=sol['latestTurn']['id']);s['master_monitor_automation']=c['master_monitor_automation'];s['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','status':proof['status'],'proof':str(vp),'runtime_e2_released':False});s['updated_at']=at;write(sp,s)
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);eid=t['dispatch_id']+'-SENT-HOURLY-ACTIVE';assert not any(x.get('event_id')==eid for x in r['processed_dispatch_events']);e=dict(proof,event_id=eid,type='A_R22_ACTUAL_SENT_HOURLY_ACTIVE',proof_path=str(vp),proof_sha256=sha(vp));r['processed_dispatch_events'].append(e);r['updated_at']=at;write(rp,r);event(e)
 para=f'\n\n## LOCAL-R21-UTC-SCOPED-CLOSED-A-R22-SENT-HOURLY-ACTIVE — {at}\nR21 originalSol actualcompletedidle135/directterminalaccepted/579evidence10939protected/both245PASS0FAIL actualexit0/0/10856typed0mismatch84bindings0FAIL accepted;UTCdefectCLOSED ONLY16normalreceiptoriginalStringtoken-wholegraphUTF8bytes/new31D7...MVID7a8b444a.../oldR20FAILpreserved/no broadclocknativeclosure. A {t["dispatch_id"]}/{t["wp_id"]}/{t["wp_revision"]}/envelope25 actualfreshidle/exactdraft/oneSend/newmessage/emptycomposer/WorkingCancelverified;{proof["status"]},no resend. M01 explicitrequired7fielddeclaration/defaultremoval/privateapprovedcapture ONLYfourregions/sixDLLPDB;R21UTCmethod/public11schema/otherorderedfixedsegments/Census-csproj-runtime7fixed. NewpositivePURE/newexactcandidatefreeze-freshoriginalSolQArequired;M04..07/native laterOPEN. Sameactualwareconomy-master ACTIVE60min173char/correcttarget/futureR22runUNOBSERVED. SolR21dispositionreceipt-only directtool/newQAnone. KnowninstalledBBOPENactorUNKNOWN unchanged/no restore. R19opaqueCLOSEDhistorical/fullEngine002006-Pipeline007-schema-GQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED/no broaderclosure. Proof {vp}\n'
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
 pointer=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';pointer.write_text(f'Current{at}: R21 fresh245PASS0FAIL each/UTCscopedCLOSED;A R22{t["dispatch_id"]}actualSENT/{proof["status"]}/explicit7decl-defaultsremoval-privatecaptureM01onlyfourregions/positivePURE. SameactualhourlyACTIVE60min. OriginalSolreceipt-only/newQAnone;nextexactR22terminalfreeze→freshQAautomatic. FullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED.\n\n'+pointer.read_text(encoding='utf-8-sig'),encoding='utf8');print(json.dumps({'A':proof['status'],'monitor':'ACTIVE60MIN','Sol_notice':sol['thread']['status']['type'],'newQA':False,'foundation':'HOLD'}))

elif stage=='released':
 q=C/'MASTER_R21_COMPLETE_R22_GUARD_FINALLY_RELEASE_20261011.json';raw=read(q)['actual_release_tool'];lockinfo=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json')
 assert raw['exit_code']==0 and '"status": "RELEASED"' in raw['output'] and '"run_id": "MASTER-SOL-R21-COMPLETE-20261011-01"' in raw['output'] and '27436' in raw['output']
 assert lockinfo['status']=='RELEASED' and lockinfo['run_id']=='MASTER-SOL-R21-COMPLETE-20261011-01' and lockinfo['pid']==27436
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=re.search(r'"released_at"\s*:\s*"([^"]+)"',raw['output']).group(1),all_child_commands_completed_before_release=True);c['updated_at']=at;write(cp,c);event({'at':at,'event_id':'MASTER-R21-R22-GUARD-RELEASE-20261011-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':'MASTER-SOL-R21-COMPLETE-20261011-01','pid':27436,'proof':str(q)});print('ACTUAL_GUARD_RELEASE_RECORDED')
else:raise ValueError(stage)
