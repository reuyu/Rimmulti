from pathlib import Path
import json,datetime,hashlib,sys,tomllib,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ui(p):return json.loads(read(p)['content'][0]['text'])
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';c=read(cp);b=read(bp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent;stage=sys.argv[1]
assert t['dispatch_id'].endswith('5415a675')
if stage=='presubmit':
 assert c['active_operation']['status']=='PREPARED_NOT_SENT' and not c['active_operation']['unknown_delivery'] and t['delivery_status']=='NOT_SENT'
 draft=ui(T/'MASTER_UI_DRAFT_VERIFIED_TOOL.json');idle=ui(T/'MASTER_UI_IDLE_CONTROLS_TOOL.json')
 assert any('WarEconomy 컨텍스트 복구 및 수행' in x for x in draft['controls'])
 assert any('Message input Value: '+t['exact_message'] in x for x in draft['controls']) and any(' 단추 Send message' in x for x in draft['controls'])
 assert not any('Master 승인 R19' in x or 'Working' in x or 'Cancel' in x for x in idle['controls'])
 for k in ['instruction','work_package','release','scope_baseline','exact_message']:
  assert sha(Path(t[k+'_path']))==t[k+'_sha256']
 baseline=read(Path(t['scope_baseline_path']))
 for f in baseline['allowed_mutable_paths']:
  q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['size']
 t.update(status='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',submission_attempts=1,submit_attempted_at=at,unknown_delivery=True);b['updated_at']=at;write(bp,b)
 c['active_operation'].update(status='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',unknown_delivery=True,attempt_started_at=at);c['updated_at']=at;write(cp,c)
 event({'at':at,'event_id':t['dispatch_id']+'-SUBMIT-ATTEMPT','type':'A_R19_CU_EXACT_DRAFT_ONE_SUBMISSION_ATTEMPT','dispatch_id':t['dispatch_id'],'unknown_delivery':True,'WP_SHA':t['work_package_sha256']})
 print('EXACT_DRAFT_VERIFIED;ONE_SUBMIT_PENDING_ACTUAL_UI;UNKNOWN_UNTIL_OBSERVED')
elif stage=='sent':
 assert t['submission_attempts']==1 and c['active_operation']['unknown_delivery']
 post=ui(T/'MASTER_UI_SUBMITTED_VERIFIED_TOOL.json')
 assert any(' 텍스트 '+t['exact_message'] in x for x in post['controls'])
 assert any('Message input' in x and 'Value: Master 승인 R19' not in x for x in post['controls'])
 assert any('Cancel' in x for x in post['controls']) and any('Working' in x for x in post['controls'])
 proof={'observed_at':at,'dispatch_id':t['dispatch_id'],'message':t['exact_message'],'actual_new_message_matches':True,'composer_cleared':True,'one_send_action':True,'working_cancel_observed':True,'actual_submission_tool':str(T/'MASTER_UI_SEND_TOOL.json'),'actual_submission_tool_sha256':sha(T/'MASTER_UI_SEND_TOOL.json'),'postsubmit_observation':str(T/'MASTER_UI_SUBMITTED_VERIFIED_TOOL.json'),'postsubmit_sha256':sha(T/'MASTER_UI_SUBMITTED_VERIFIED_TOOL.json'),'predraft_actualidle':str(T/'MASTER_UI_IDLE_CONTROLS_TOOL.json'),'draft_actualexact':str(T/'MASTER_UI_DRAFT_VERIFIED_TOOL.json'),'focus_qualification':'UIA reportedRootWebArea;visualeditablecaret thenexactMessageInputValue verified beforeoneSend;no separate focus claim','geometry_recovery':'Initialclickwithout screenshotgeometry failed;freshscreenshot/click thenexactdraft,neversecondSend'}
 pp=T/'MASTER_UI_SUBMISSION_PROOF.json';assert not pp.exists();write(pp,proof)
 t.update(status='SENT_IN_PROGRESS_ACK_PENDING',delivery_status='SENT',sent_at=at,unknown_delivery=False,submission_proof=str(pp),submission_proof_sha256=sha(pp))
 c['active_operation'].update(status='ACTUAL_SENT_MONITOR_RESUME_PENDING',unknown_delivery=False);c.update(a_current_attempt_id=t['dispatch_id'],a_status='R19_ACTUAL_SENT_IN_PROGRESS_ACK_PENDING',a_result_completion_path=t['completion_path'],updated_at=at);write(cp,c);write(bp,b)
 event({'at':at,'event_id':t['dispatch_id']+'-ACTUAL-SENT','type':'A_R19_ACTUAL_DIRECT_CU_SENT_WORKING','dispatch_id':t['dispatch_id'],'proof':str(pp),'one_submit':True,'ack_pending':True,'monitor_resume_pending':True});print('R19_ACTUAL_SENT_ONE_SUBMIT_MONITOR_RESUME_PENDING')
elif stage=='finalize':
 assert c['active_operation']['status']=='ACTUAL_SENT_MONITOR_RESUME_PENDING' and not c['active_operation']['unknown_delivery']
 sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
 pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
 counts={k:len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']};assert list(counts.values())==[19,1755,206,7598]
 pp=T/'MASTER_POSTSENT_PRESERVATION.json';write(pp,pres)
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
 assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id'] and cfg['name']=='WarEconomy Master 통합 작업 확인'
 tool=C/'MASTER_R19_MONITOR_RESUME_TOOL_20261010.json';assert not read(tool).get('isError')
 ack=read(Path(t['ack_path'])) if Path(t['ack_path']).exists() else None
 if ack:assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==22
 status='SENT_ACK_VERIFIED_IN_PROGRESS' if ack else 'SENT_IN_PROGRESS_ACK_PENDING'
 notice=json.loads(read(C/'MASTER_R18_DISPOSITION_NOTICE_SOL_SNAPSHOT_20261010.json')['content'][0]['text'])['polls'][0]
 proof={'at':at,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'envelope':22,'status':status,'ui_submission':t['submission_proof'],'ui_submission_sha256':sha(Path(t['submission_proof'])),'ack':ack,'ack_sha256':sha(Path(t['ack_path'])) if ack else None,'postsent_preservation':str(pp),'postsent_preservation_sha256':sha(pp),'counts':counts,'source_scope':'ONLYTWO_WORKER_ASSIGNMENTS_REMOVE_OPAQUE_TRIM_AND6_NEW_DLLPDB','allowed_worker_source_after_sha256':t['allowed_worker_source_after_sha256'],'normal_execution_scope':'NEW_DETACHED_POSITIVE_PURE_OPAQUE_POLICY_HELPERS_NO_GLOBAL_PROCESS_NATIVE','automation_actual_config':cfg,'automation_tool_path':str(tool),'automation_tool_sha256':sha(tool),'future_r19_scheduled_run_observed':False,'original_sol_notice_snapshot':notice,'original_sol':'R18_QA_COMPLETED_ACCEPTED_NORMAL_OPAQUE_FAIL;RECEIPT_NOTICE_SEPARATE_NOT_QA_WP;NO_NEW_QA','guard_run':'MASTER-SOL-R18-COMPLETE-20261010-01','guard_session':36347,'guard_pid':34784,'actual_renewal_before_inputs_observed':True,'historic_mutex_gaps_not_retroclaimed':True,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
 vp=C/'MASTER_GATE05_R19_OPAQUE_POLICY_DISPATCH_MONITOR_ACTIVE_20261010.json';assert not vp.exists();write(vp,proof)
 write(C/'MASTER_R19_MONITOR_ACTUAL_CONFIG_VERIFICATION_20261010.json',{'at':at,'config':cfg,'tool':str(tool),'matched':True})
 t.update(status='IN_PROGRESS' if ack else status,ack_verified=bool(ack),ack_sha256=proof['ack_sha256'],monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(vp),updated_at=at);b['updated_at']=at;write(bp,b)
 c.update(active_operation=None,a_pending_dispatch_id=None,a_current_attempt_id=t['dispatch_id'],a_result_completion_path=t['completion_path'],a_current_ack=proof if ack else None,a_status='R19_OPAQUE_POLICY_IN_PROGRESS_ACK_VERIFIED' if ack else 'R19_OPAQUE_POLICY_ACTUAL_SENT_ACK_PENDING',a_latest_delivery=proof,a_latest_runtime_observation=proof,last_sol_cursor=notice['cursor'],sol_next_action='R18_TERMINAL_NEW_QA_NONE;WAIT_R19_TERMINAL_MASTER_FREEZE_ADMISSION_THEN_FRESH_ORIGINAL_SOL_QA',updated_at=at)
 c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(vp),future_run_after_engine_r19_resume_observed=False,pause_reason=None,resumed_by='Master after actualR19 oneCU SENT')
 c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':36347,'guard_pid':34784,'at':at,'status':'R18_QA_NORMAL_LOSSLESS_FAIL_DISPOSED_R19_MINIMALFIX_ACTUAL_SENT_HOURLY_ACTIVE','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R18_COMPLETE_R19_DISPATCH_GUARD_FINALLY_RELEASE_20261010.json')};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['a'].update(current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],execution_phase='IN_PROGRESS',current_conversation_status='ACTUAL_R19_SUBMITTED_EMPTY_COMPOSER_WORKING_CANCEL',ack_verified=bool(ack),last_ui_proof=t['submission_proof'],current_runtime_idle_verified=False)
 s['endpoints']['sol'].update(execution_phase='R18_QA_COMPLETED_SEPARATE_RECEIPT_NOTICE_NO_QA_WP',current_runtime_idle_verified=notice['thread']['status']['type']=='idle',last_runtime_observation_cursor=notice['cursor'],latest_notice_turn_id=notice['latestTurn']['id'])
 s['master_monitor_automation']=c['master_monitor_automation'];s['updated_at']=at;s['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','status':status,'proof':str(vp),'runtime_e2_released':False});write(sp,s)
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);eid=t['dispatch_id']+'-SENT-HOURLY-ACTIVE';assert not any(x.get('event_id')==eid for x in r['processed_dispatch_events'])
 e=dict(proof,event_id=eid,type='A_R19_OPAQUE_POLICY_ACTUAL_SENT_HOURLY_ACTIVE',proof_path=str(vp),proof_sha256=sha(vp));r['processed_dispatch_events'].append(e);r['updated_at']=at;write(rp,r);event(e)
 para=f'\n\n## LOCAL-A-R19-OPAQUE-POLICY-SENT-HOURLY-ACTIVE — {at}\n{t["dispatch_id"]}/{t["wp_id"]}/{t["wp_revision"]}/envelope22 actualfreshconversationidle/exactdraft/oneSend/newmessage/emptycomposer/WorkingCancel verified;{status},no resend. Source ONLYtwoopaqueID/revisionTrimassignments removed/expectedWorkerSHA{t["allowed_worker_source_after_sha256"]}/ALLotherbytesfixed+Census-csproj-runtime7 fixed;newnormalPUREbothroles4routes/prospectivefulltypedoriginalgraph-digest packaging. Master R18normal101PASS24FAIL each/362evidence9374protected/167pins10PEloads147outputs5576typed256mismatches52bindings16FAIL acceptedFAIL,ownership-SHA-redaction-limitedcodec credited;actualproducer16 correctshistorical17/no oldbytechange. Origin-trustedmissinggate/schema-role-userdata-context-native OPEN laterboundedwork,notR19. Archive19/prior1755/Pipeline206/QA7598/managed4/runtime7 matched,knownSteamBBOPENactorUNKNOWN. Sameactualwareconomy-master ACTIVE60min/173char/correctname-target/futureR19runUNOBSERVED. OriginalSol R18terminalaccepted/separatereceiptnotice,no newQA;newexactcandidateQA afterMasterfreeze. Liveguard36347/pid34784 renewals/inputcoverageobserved,historicgapsnotretroclaimed. Engine002006/Pipeline007/schema/G-Q1OPEN/FoundationHOLD/fullGateE2NOTRELEASED/no closure. Proof {vp}\n'
 for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with q.open('a',encoding='utf8') as f:f.write(para)
 pointer=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';pointer.write_text(f'Current{at}: R18independentnormalOPAQUEFAIL accepted(twoactual101PASS24FAIL/exit1);ownership-SHA-redaction-limitedcodec scopedPASS. A R19{t["dispatch_id"]} actualSENT/{status}/ONLY2Workerassignments removeTrim/expectedfinalSHA{t["allowed_worker_source_after_sha256"]}/othersfixed/newnormalPURE. SameactualhourlyACTIVE60min. OriginalSol R18terminalaccepted/receipt notice/newQA none;awaitR19terminal→Masterfreeze-admission→freshQA→boundedtrustedstartup/originfollowup automatically. FoundationHOLD/Engine002006/Pipeline007/schema/G-Q1OPEN/no fullGateE2/closure.\n\n'+pointer.read_text(encoding='utf-8-sig'),encoding='utf8')
 print(json.dumps({'A':status,'dispatch':t['dispatch_id'],'monitor':'ACTIVE60MIN','Sol':'R18_TERMINAL_NO_NEW_QA','native_permissions':0},ensure_ascii=True))
else:raise ValueError(stage)

