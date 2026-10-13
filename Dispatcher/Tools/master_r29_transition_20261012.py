from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';RUN='MASTER-R28-DUAL-COMPLETE-20261012-01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(x):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(x,ensure_ascii=False)+'\n')
def append(para):
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';sp=H/'DISPATCHER_STATE.json';c=read(cp);b=read(bp);s=read(sp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent;mode=sys.argv[1]
assert t['dispatch_id'].endswith('46f60e2a')
if mode!='released':
 lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert lock['status']=='LOCKED' and lock['run_id']==RUN and lock['pid']==33196
if mode=='a_drafting':
 assert c['active_operation'] is None and t['delivery_status']=='NOT_SENT'
 tree=read(T/'MASTER_UI_IDLE.json')['accessibility']['tree'];assert 'WarEconomy 컨텍스트 복구 및 수행' in tree and 'Message input Value:' not in tree and '텍스트 Working\n' not in tree and '단추 Cancel' not in tree
 for f in t['all9_before']:assert sha(Path(f['path']))==f['sha256']
 for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
 c['active_operation']={'recipient':'A','dispatch_id':t['dispatch_id'],'stage':'DRAFTING_NO_SUBMISSION','unknown_delivery':False,'at':at};write(cp,c);event({'at':at,'event_id':t['dispatch_id']+'-DRAFTING','type':'A_R29_FRESH_IDLE_DRAFT_PREPARATION'})
elif mode=='a_presubmit':
 assert c['active_operation']['stage']=='DRAFTING_NO_SUBMISSION' and t['submission_attempts']==0
 tree=read(T/'MASTER_UI_DRAFT.json')['accessibility']['tree'];assert 'Message input Value: '+t['exact_message'] in tree and '단추 Send message' in tree
 t.update(status='SUBMIT_ATTEMPT_PENDING_ACTUAL_UI',submission_attempts=1,unknown_delivery=True,submit_attempted_at=at);write(bp,b);c['active_operation'].update(stage=t['status'],unknown_delivery=True);write(cp,c);event({'at':at,'event_id':t['dispatch_id']+'-ONE-SUBMIT-ATTEMPT','type':'A_R29_CU_SUBMIT_UNKNOWN_PENDING_ACTUAL_PROOF'})
elif mode=='a_sent':
 assert c['active_operation']['unknown_delivery'] and t['submission_attempts']==1
 p=T/'MASTER_UI_SUBMITTED.json';tree=read(p)['accessibility']['tree'];assert ' 텍스트 '+t['exact_message'] in tree and 'Message input Value:' not in tree and '텍스트 Working' in tree and '단추 Cancel' in tree
 pp=T/'MASTER_UI_SUBMISSION_PROOF.json';assert not pp.exists();write(pp,{'at':at,'dispatch_id':t['dispatch_id'],'fresh_idle_exact_draft_one_actual_submission':True,'newexactmessage_composerempty_WorkingCancel':True,'post_path':str(p),'post_sha256':sha(p),'draft_path':str(T/'MASTER_UI_DRAFT.json'),'idle_path':str(T/'MASTER_UI_IDLE.json'),'guard_run':RUN,'guard_pid':33196,'guard_session':99760})
 t.update(delivery_status='SENT',status='SENT_IN_PROGRESS_ACK_PENDING',unknown_delivery=False,sent_at=at,submission_proof=str(pp),submission_proof_sha256=sha(pp));write(bp,b);c['active_operation'].update(stage='SENT_MONITOR_RESUME_PENDING',unknown_delivery=False);write(cp,c);event({'at':at,'event_id':t['dispatch_id']+'-SENT','type':'A_R29_DIRECT_CU_ACTUAL_SENT','proof':str(pp)})
elif mode=='a_finalize':
 assert c['active_operation']['stage']=='SENT_MONITOR_RESUME_PENDING' and t['delivery_status']=='SENT'
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
 sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
 pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];write(T/'MASTER_POSTSENT_PRESERVATION.json',pres)
 ack=None
 if Path(t['ack_path']).exists():
  ack=read(Path(t['ack_path']));assert all(ack[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and ack.get('envelope',ack.get('delivery_envelope_revision'))==32
 proof={'at':at,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'envelope':32,'actual_submission_proof':t['submission_proof'],'ack':ack,'ack_sha256':sha(Path(t['ack_path'])) if ack else None,'status':'SENT_ACK_VERIFIED_IN_PROGRESS' if ack else 'SENT_IN_PROGRESS_ACK_PENDING','monitor_actual_config':cfg,'scope':'EXACT_SIX_STARTUP_SOURCE_SPANS_PLUS_NEW_PLAN_ONLY_PAIR_PUBLISHER_PURE_NORMAL_E1_NO_NATIVE','native_e2_released':False,'foundation':'HOLD','future_R29_scheduled_run_observed':False,'guard_run':RUN,'guard_pid':33196,'guard_session':99760}
 p=C/'MASTER_GATE05_R29_STARTUP_PAIR_DISPATCH_MONITOR_ACTIVE_20261012.json';assert not p.exists();write(p,proof)
 t.update(status='IN_PROGRESS' if ack else proof['status'],ack_verified=bool(ack),ack_sha256=proof['ack_sha256'],monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(p));write(bp,b)
 c.update(active_operation=None,a_status='R29_ROUTE_IN_PROGRESS_ACK_VERIFIED' if ack else proof['status'],a_latest_delivery=proof,a_prepared_dispatch_id=None,a_pending_dispatch_id=None,a_result_completion_path=t['completion_path'],updated_at=at);c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(p),future_run_after_r29_resume_observed=False,pause_reason=None);write(cp,c)
 s['endpoints']['a'].update(current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],execution_phase='IN_PROGRESS',current_runtime_idle_verified=False,ack_verified=bool(ack),last_ui_proof=t['submission_proof']);s['master_monitor_automation']=c['master_monitor_automation'];s['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','proof':str(p)});write(sp,s)
 event(dict(proof,event_id=t['dispatch_id']+'-SENT-ACTIVE',type='A_R29_ACTUAL_SENT_EXISTING_HOURLY_ACTIVE',proof_path=str(p)))
 append(f'\n\n## LOCAL-A-R29-CONNECTED-ROUTE-SENT-HOURLY-ACTIVE — {at}\n{t["dispatch_id"]}/R29/envelope32 actualfreshidle-exactdraft-oneSend-newmessage-emptycomposer-WorkingCancel/SENT;ACK separately tracked/no resend. Actual startup-provisioning implementation six explicit source spans/currentmutable7+newpublisher/Censuscsprojfixed; new PUREnormal E1 permitted/no native-globalentry-Process-adverse. Sameactualwareconomy-masterACTIVE60min173charcorrectMastertarget/futureR29runUNOBSERVED. R27S2normal168PASS/run scopedaccepted/QAdependencydefectscopedCLOSED/S1rawstopretained. OriginalSol newR29 independent normaloracle preparation pending actualnewturn proof after historical usage failure. FullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{p}\n')
elif mode=='sol_sending':
 assert c['active_operation'] is None;d=c['sol_next_prepared_delivery'];assert d['delivery_status']=='PREPARED_NOT_SENT' and sha(Path(d['wp_path']))==d['wp_sha256']
 snap=read(C/'MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_PREDISPATCH_20261012.json');a=json.loads(snap['content'][0]['text'])['polls'][0];assert a['thread']['status']['type'] in ['idle','notLoaded','systemError'] and a['latestTurn']['status'] in ['completed','failed']
 c['active_operation']={'recipient':'Sol','delivery_id':d['delivery_id'],'stage':'DIRECT_SEND_ATTEMPT_PENDING_PROOF','unknown_delivery':True,'at':at};write(cp,c);event({'at':at,'event_id':d['delivery_id']+'-SEND-ATTEMPT','type':'SOL_R29_DIRECT_SEND_PENDING_PROOF'})
elif mode=='sol_sent':
 assert c['active_operation']['recipient']=='Sol' and c['active_operation']['unknown_delivery'];d=c['sol_next_prepared_delivery']
 a=json.loads(read(C/'MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_POSTSEND_20261012.json')['content'][0]['text'])['polls'][0];tr=read(C/'MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_SEND_TOOL_20261012.json');assert not tr.get('isError') and a['thread']['status']['type']=='active' and a['latestTurn']['status']=='inProgress' and a['latestTurn']['id']!=c['sol_latest_completion']['actual_snapshot']['latestTurn']['id']
 d.update(delivery_status='SENT',unknown_delivery=False,sent_at=at,actual_snapshot=a);c.update(active_operation=None,sol_current_delivery=d,sol_current_delivery_id=d['delivery_id'],sol_current_wp=d['wp_id'],sol_current_revision='S1',sol_current_result_id=None,sol_current_ack=None,sol_status='R29_STARTUP_PAIR_PREPARATION_IN_PROGRESS_ACK_PENDING',last_sol_cursor=a['cursor'],sol_next_prepared_delivery=None,sol_next_wp_prepared=None,updated_at=at);write(cp,c)
 proof=dict(d,at=at,tool_path=str(C/'MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_SEND_TOOL_20261012.json'),tool_sha256=sha(C/'MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_SEND_TOOL_20261012.json'),guard_run=RUN,guard_pid=33196,guard_session=99760,no_substitute_agent=True,scope='FROZEN_R27_NEW_AUXILIARY_CONTRACT_NORMAL_ORACLE_PREPARATION_NO_MUTABLE_R29_READ_OR_BUILD_CALLS_NATIVE')
 p=C/'MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_DELIVERY_VERIFICATION_20261012.json';assert not p.exists();write(p,proof);s['endpoints']['sol'].update(current_wp=d['wp_id'],current_delivery_id=d['delivery_id'],execution_phase='IN_PROGRESS_ACK_PENDING',current_runtime_idle_verified=False,last_runtime_observation_cursor=a['cursor']);s['deliveries'].append({'delivery_id':d['delivery_id'],'recipient':'Sol','wp_id':d['wp_id'],'wp_revision':'S1','delivery_status':'SENT','proof':str(p)});write(sp,s);event(dict(proof,event_id=d['delivery_id']+'-SENT',type='SOL_R29_ORIGINAL_DIRECT_ACTUAL_NEW_ACTIVE_TURN'))
 append(f'\n\n## LOCAL-SOL-R29-STARTUP-PAIR-PREPARATION-SENT — {at}\nOriginalSol{d["delivery_id"]}/WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_PREPARATION/S1 actualdirecttoolSENT/newactiveturn{a["latestTurn"]["id"]}/cursor{a["cursor"]};ACKpending/no duplicate. Independent frozenR27+Masterclosedauxpaircontract prospective fulltyped/raw/copy/provenance6normalfixture preparation; no mutableR29read/compiler/candidate/game/native calls. baseline14105 exactcurrentmutable7excluded/oldfrozen preserved/R27S2scopedPASS/S1stop intact. A R29pairedstartup source implementation inprogress/samehourlyACTIVE60min/directSolcompletionpush. AfterAterminal Masterfreeze and freshindependentcandidateQA;fullGateE2NOTRELEASED/EnginePipelineGQ1OPEN/FoundationHOLD. Proof{p}\n')
elif mode=='released':
 p=C/'MASTER_R28_DUAL_COMPLETE_R29_GUARD_FINALLY_RELEASE_20261012.json';rr=read(p)['actual_release_tool'];lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert rr['exit_code']==0 and lock['status']=='RELEASED' and lock['run_id']==RUN
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=lock['released_at'],release_proof_path=str(p),all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':RUN+'-RELEASE','type':'GUARD_ACTUAL_FINALLY_RELEASE','proof':str(p)})
else:raise ValueError(mode)
print(mode+'_RECORDED')
