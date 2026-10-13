from pathlib import Path
import json,hashlib,datetime,sys,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R25-S2-COMPLETE-NEXT-20261011-01';PID=24636;SESSION=35120
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';c=read(cp);b=read(bp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent;stage=sys.argv[1];assert t['dispatch_id'].endswith('4d660e9b')
if stage=='presubmit':
 assert t['delivery_status']=='NOT_SENT' and t['submission_attempts']==0 and not c['active_operation']['unknown_delivery']
 draft=read(T/'MASTER_UI_DRAFT.json')['accessibility']['tree'];idle=read(T/'MASTER_UI_IDLE.json')['accessibility']['tree']
 assert 'WarEconomy 컨텍스트 복구 및 수행' in idle and not any(x in idle for x in ['Message input Value:','Working','Cancel'])
 assert 'Message input Value: '+t['exact_message'] in draft and '단추 Send message' in draft
 for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
 for f in read(Path(t['scope_baseline_path']))['production_fixed_files']:
  p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
 t.update(status='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',submission_attempts=1,unknown_delivery=True,submit_attempted_at=at);write(bp,b);c['active_operation'].update(stage='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',unknown_delivery=True);write(cp,c);event({'at':at,'event_id':t['dispatch_id']+'-SUBMIT-ATTEMPT','type':'A_R26_ONE_CU_SUBMIT_ATTEMPT','unknown_delivery':True});print('ONE_SUBMIT_PENDING_UNKNOWN')
elif stage=='sent':
 assert c['active_operation']['unknown_delivery'] and t['submission_attempts']==1
 p=T/'MASTER_UI_SUBMITTED.json';tree=read(p)['accessibility']['tree'];assert ' 텍스트 '+t['exact_message'] in tree and 'Message input Value:' not in tree and 'Working' in tree and 'Cancel' in tree
 pp=T/'MASTER_UI_SUBMISSION_PROOF.json';assert not pp.exists();write(pp,{'at':at,'dispatch_id':t['dispatch_id'],'one_actual_submit':True,'new_exact_message':True,'composer_empty':True,'WorkingCancel':True,'post_path':str(p),'post_sha256':sha(p),'draft_path':str(T/'MASTER_UI_DRAFT.json'),'idle_path':str(T/'MASTER_UI_IDLE.json'),'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION})
 t.update(delivery_status='SENT',status='SENT_IN_PROGRESS_ACK_PENDING',unknown_delivery=False,sent_at=at,submission_proof=str(pp),submission_proof_sha256=sha(pp));write(bp,b);c['active_operation'].update(stage='SENT_MONITOR_RESUME_PENDING',unknown_delivery=False);c.update(a_status=t['status'],a_result_completion_path=t['completion_path']);write(cp,c);event({'at':at,'event_id':t['dispatch_id']+'-ACTUAL-SENT','type':'A_R26_DIRECT_CU_SENT','proof':str(pp)});print('ACTUAL_SENT_MONITOR_RESUME_PENDING')
elif stage=='finalize':
 assert c['active_operation']['stage']=='SENT_MONITOR_RESUME_PENDING' and not c['active_operation']['unknown_delivery']
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
 assert not read(C/'MASTER_R26_MONITOR_RESUME_TOOL_20261011.json').get('isError')
 sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
 pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];write(T/'MASTER_POSTSENT_PRESERVATION.json',pres)
 ack=None
 if Path(t['ack_path']).exists():
  ack=read(Path(t['ack_path']));assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==29
 proof={'at':at,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'envelope':29,'actual_submission_proof':t['submission_proof'],'ack':ack,'ack_sha256':sha(Path(t['ack_path'])) if ack else None,'status':'SENT_ACK_VERIFIED_IN_PROGRESS' if ack else 'SENT_IN_PROGRESS_ACK_PENDING','monitor_actual_config':cfg,'scope':'M04_READ_ONLY_CHILD_SEPARATE_DECLARATION_PRIVATE_REGISTRATION_CONTRACT_ALL9_FIXED','native_e2_released':False,'foundation':'HOLD','future_R26_scheduled_run_observed':False,'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION,'knowninstalled':'UNCHANGED_OPEN_ACTOR_CAUSE_UNKNOWN','Sol':'R25S2_DISPOSED_IDLE_R26_INDEPENDENT_READONLY_PREPARED_NOT_SENT'}
 p=C/'MASTER_GATE05_R26_CHILD_REG_PREP_DISPATCH_MONITOR_ACTIVE_20261011.json';assert not p.exists();write(p,proof);t.update(status='IN_PROGRESS' if ack else proof['status'],ack_verified=bool(ack),ack_sha256=proof['ack_sha256'],monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(p),updated_at=at);write(bp,b)
 c.update(active_operation=None,a_status='R26_CHILD_REG_PREPARATION_IN_PROGRESS_ACK_VERIFIED' if ack else 'R26_CHILD_REG_PREPARATION_ACTUAL_SENT_ACK_PENDING',a_latest_delivery=proof,a_prepared_dispatch_id=None,a_pending_dispatch_id=None,updated_at=at);c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(p),future_run_after_r24_resume_observed=True,r24_heartbeat_received_utc=['2026-10-11T10:18:43.371Z','2026-10-11T11:23:44.299Z','2026-10-11T12:19:45.138Z'],future_run_after_r26_resume_observed=False,pause_reason=None,resumed_by='Master after actual R26 direct CU delivery');c['last_monitor_run']={'run_id':RUN,'guard_session':SESSION,'guard_pid':PID,'at':at,'status':'R25_S2_DISPOSED_R26_SENT_HOURLY_ACTIVE','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['a'].update(current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],execution_phase='IN_PROGRESS',current_runtime_idle_verified=False,ack_verified=bool(ack),last_ui_proof=t['submission_proof']);s['master_monitor_automation']=c['master_monitor_automation'];s['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','proof':str(p)});write(sp,s)
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);e=dict(proof,event_id=t['dispatch_id']+'-SENT-HOURLY-ACTIVE',type='A_R26_ACTUAL_SENT_HOURLY_ACTIVE',proof_path=str(p),proof_sha256=sha(p));assert not any(x.get('event_id')==e['event_id'] for x in r['processed_dispatch_events']);r['processed_dispatch_events'].append(e);write(rp,r);event(e)
 para=f'\n\n## LOCAL-R25-S2-DISPOSED-A-R26-CHILD-REG-PREP-SENT — {at}\nA{t["dispatch_id"]}/{t["wp_id"]}/envelope29 actualfreshidle/exactdraft/oneSend/newmessage/emptycomposer/WorkingCancel/SENT/ACKpending-or-separatelybound/no resend. R25S2freshnormal36PASS0FAILeach/1824typed24rawbytebounds/QAnewline scopedCLOSED only/S1raw8FAILpreserved/nativeOPEN. R26READ_ONLY separateoperator-ownedREAD_ONLYconfig-original7declaration-receipt privatechild-registration contract/minimumspans/prospectiveoracle ONLY/ALLproduction9fixed/build-execution-assetscopy0. Protected13419/R25frozen99/priorQA preserved;actualsamewareconomy-masterACTIVE60min173charcorrecttarget/futureR26runUNOBSERVED. OriginalSolR25S2completedidle/R26independentprepapprovedNOT_SENTuntildirecttoolproof. FullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{p}\n'
 for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with q.open('a',encoding='utf8') as f:f.write(para)
 print(proof['status'])
elif stage=='released':
 p=C/'MASTER_R25_S2_COMPLETE_R26_GUARD_FINALLY_RELEASE_20261011.json';rr=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert rr['exit_code']==0 and info['status']=='RELEASED' and info['run_id']==RUN and info['pid']==PID
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],release_proof_path=str(p),all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':RUN+'-RELEASE','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':RUN,'pid':PID,'proof':str(p)});print('ACTUAL_GUARD_RELEASE_RECORDED')
else:raise ValueError(stage)
