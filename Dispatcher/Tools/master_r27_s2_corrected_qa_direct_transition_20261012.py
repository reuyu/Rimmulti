from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R27-QA-DEPENDENCY-REPAIR-20261012-01';PID=26572;SESSION=44434;P='MASTER_SOL_R27_CHILD_CAPTURE_INDEPENDENT_S2_'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def data(p):return json.loads(read(p)['content'][0]['text'])
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];stage=sys.argv[1]
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
assert t['dispatch_id'].endswith('cdc223f3') and t['status']=='COMPLETED_REVIEWED_SOURCE_CAPTURE_CREDITED_SCOPED_QA_PENDING'
if stage=='sending':
 assert c['active_operation'] is None;op=c['sol_next_prepared_delivery'];assert op['delivery_status']=='PREPARED_NOT_SENT'
 pre=data(C/(P+'PREDISPATCH_20261012.json'))['polls'][0];assert pre['thread']['id']==c['sol_thread_id'] and pre['thread']['status']['type']=='idle' and pre['latestTurn']['status']=='completed'
 for k in ['wp','baseline','frozen_manifest']:assert sha(Path(op[k+'_path'] if k!='frozen_manifest' else op[k]))==op[k+'_sha256']
 op.update(type='SOL_R27_FRESH_EXACT_NORMAL_QA',delivery_status='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL',unknown_delivery=True,actual_predispatch=pre,attempt_started_at=at,guard_run=RUN,guard_pid=PID,guard_session=SESSION);c['active_operation']=op;write(cp,c);event({'at':at,'event_id':op['delivery_id']+'-ATTEMPT','type':'SOL_R27_FRESH_NORMAL_QA_DIRECT_ATTEMPT','unknown_delivery':True});print('ONE_DIRECT_DELIVERY_PENDING')
elif stage=='sent':
 op=c['active_operation'];assert op['unknown_delivery'];paths={k:C/(P+n+'_20261012.json') for k,n in [('pre','PREDISPATCH'),('tool','SEND_TOOL'),('post','POSTSEND')]}
 pre=data(paths['pre'])['polls'][0];post=data(paths['post'])['polls'][0];assert not read(paths['tool']).get('isError') and post['thread']['id']==c['sol_thread_id'] and post['latestTurn']['id']!=pre['latestTurn']['id'] and post['thread']['status']['type']=='active' and post['latestTurn']['status']=='inProgress'
 proof=dict(op,at=at,delivery_status='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN',unknown_delivery=False,status='SENT_IN_PROGRESS_ACK_PENDING',actual_snapshot=post,scope='NEW_SELECTED_FROZEN_R27_DEFENSIVE_STATIC_AND_NORMAL_PURE_CAPTURE_UNIT_QA',production_modify_rebuild=0,qa_owned_final_runner_build_admitted=1,normal_culture_runs_admitted=2,native_e2_released=False,foundation='HOLD',monitor='ACTUAL_PAUSED60MIN')
 for k,p in paths.items():proof[k+'_path']=str(p);proof[k+'_sha256']=sha(p)
 vp=C/(P+'DELIVERY_VERIFICATION_20261012.json');assert not vp.exists();write(vp,proof)
 c.update(active_operation=None,sol_current_attempt_id=op['delivery_id'],sol_current_wp=op['wp_id'],sol_current_revision='S2',sol_current_result_id=None,sol_status='R27_FRESH_NORMAL_PURE_CAPTURE_QA_SENT_ACK_PENDING',sol_current_ack=None,sol_current_delivery=proof,sol_latest_delivery=proof,last_sol_cursor=post['cursor'],sol_next_wp_prepared=None,sol_next_prepared_delivery=None,sol_next_action='COLLECT_FRESH_R27_QA_RESULT_THEN_MASTER_SCOPED_DISPOSITION_AND_NEXT_BOUNDED_TECHNICAL_WORK_AUTOMATIC',updated_at=at);c['last_monitor_run'].update(status='R27_A_TERMINAL_DISPOSED_SCHEDULER_PAUSED_FRESH_SOL_NORMAL_QA_ACTUAL_SENT',release_status='PENDING_ACTUAL_FINALLY');write(cp,c)
 sp=H/'DISPATCHER_STATE.json';st=read(sp);st['endpoints']['sol'].update(current_wp=op['wp_id'],current_wp_revision='S2',current_delivery_id=op['delivery_id'],current_result_id=None,current_turn_id=post['latestTurn']['id'],actual_turn_id=post['latestTurn']['id'],execution_phase='IN_PROGRESS',ack_verified=False,explicit_ack_pending=True,current_runtime_idle_verified=False,last_runtime_observation_cursor=post['cursor']);st['master_monitor_automation']=c['master_monitor_automation'];st['deliveries'].append({'delivery_id':op['delivery_id'],'recipient':'Sol','wp_id':op['wp_id'],'wp_revision':'S2','delivery_status':'SENT','status':'ACTIVE_ACK_PENDING','proof':str(vp),'runtime_e2_released':False});write(sp,st)
 e={'at':at,'event_id':op['delivery_id']+'-ACTUAL_SENT','type':'SOL_R27_FRESH_FROZEN_NORMAL_PURE_QA_ACTUAL_SENT','delivery_id':op['delivery_id'],'proof':str(vp),'proof_sha256':sha(vp),'turn_id':post['latestTurn']['id'],'cursor':post['cursor'],'protected':op['protected_unique_paths'],'selected_sha256':op['selected_sha256'],'selected_mvid':op['selected_mvid'],'no_duplicate_wp':True}
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr);event(e)
 para=f'\n\n## LOCAL-R27-TERMINAL-PAUSED-FRESH-SOL-CAPTURE-QA-SENT — {at}\nSamewareconomy-master actualPAUSED60min173charcorrecttarget. OriginalSol {op["delivery_id"]}/{op["wp_id"]}/S2 actualdirectSENT/newactive turn{post["latestTurn"]["id"]}/cursor{post["revision"]}/ACKpending/no duplicate-substitute. Exactfrozen83SHA{op["frozen_manifest_sha256"]}/Debug{op["selected_sha256"]}/MVID{op["selected_mvid"]} admittedONLYdefensive static+fullyspecified normalfactory8IsValid8Capture4/full15getters/fulltypedraw-copyownership4pair-newQAfinalbuild1-twofreshcultures-prospectiveallcompilerrefsloadedrecursive proof. Protected{op["protected_unique_paths"]}includingcurrent9/newfrozen83/oldQArawFAIL+prep23. Productioncandidate modify-rebuild0/native-global-registration-launcher-adverse0/fullGateE2NOTRELEASED/FoundationHOLD/closure0. Aterminalsourcefixcredited/E1partial notinheritedPASS;nextA noneNOT_SENT pendingQA. Proof{vp}\n'
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
 nx=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';nx.write_text(para+'\n'+nx.read_text(encoding='utf-8-sig'),encoding='utf8');print(json.dumps(e))
else:raise ValueError(stage)
