from pathlib import Path
import json,hashlib,datetime,tomllib,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R26-R27-RECOVERY-20261012-01';PID=20116;SESSION=83680;P='MASTER_SOL_R27_CHILD_CAPTURE_PREPARATION_'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def data(p):return json.loads(read(p)['content'][0]['text'])
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);stage=sys.argv[1];t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1]
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
assert t['dispatch_id'].endswith('cdc223f3') and t['delivery_status']=='SENT' and not t['unknown_delivery']
lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert lock['status']=='LOCKED' and lock['run_id']==RUN and lock['pid']==PID
if stage=='sending':
 assert c['active_operation'] is None;op=c['sol_next_prepared_delivery'];assert op['delivery_status']=='PREPARED_NOT_SENT'
 pre=data(C/(P+'PREDISPATCH_20261011.json'))['polls'][0];assert pre['thread']['id']==c['sol_thread_id'] and pre['thread']['status']['type']=='idle' and pre['latestTurn']['status']=='completed'
 for k in ['wp','baseline']:assert sha(Path(op[k+'_path']))==op[k+'_sha256']
 for f in t['production_fixed_files']:
  p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
 op.update(type='SOL_R27_CAPTURE_PREPARATION',delivery_status='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL',unknown_delivery=True,actual_predispatch=pre,attempt_started_at=at,guard_run=RUN,guard_pid=PID,guard_session=SESSION);c['active_operation']=op;write(cp,c);event({'at':at,'event_id':op['delivery_id']+'-ATTEMPT','type':'SOL_R27_DIRECT_ATTEMPT','unknown_delivery':True});print('ONE_SOL_DELIVERY_PENDING')
elif stage=='sent':
 op=c['active_operation'];assert op['unknown_delivery']
 paths={k:C/(P+n+'_20261011.json') for k,n in [('pre','PREDISPATCH'),('tool','SEND_TOOL'),('post','POSTSEND')]}
 pre=data(paths['pre'])['polls'][0];post=data(paths['post'])['polls'][0]
 assert not read(paths['tool']).get('isError') and post['thread']['id']==c['sol_thread_id'] and post['latestTurn']['id']!=pre['latestTurn']['id'] and post['thread']['status']['type']=='active' and post['latestTurn']['status']=='inProgress'
 proof=dict(op,at=at,delivery_status='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN',unknown_delivery=False,status='SENT_IN_PROGRESS_ACK_PENDING',actual_snapshot=post,scope='INDEPENDENT_READONLY_PREP_FROZEN_R25_FOR_FUTURE_R27_CAPTURE',production_modify_build=0,qa_build_execute=0,native_e2_released=False,foundation='HOLD',monitor='ACTUAL_ACTIVE60MIN')
 for k,p in paths.items():proof[k+'_path']=str(p);proof[k+'_sha256']=sha(p)
 vp=C/(P+'DELIVERY_VERIFICATION_20261011.json');assert not vp.exists();write(vp,proof)
 c.update(active_operation=None,sol_current_attempt_id=op['delivery_id'],sol_current_wp=op['wp_id'],sol_current_revision='S1',sol_current_result_id=None,sol_status='R27_CAPTURE_INDEPENDENT_READONLY_PREPARATION_SENT_ACK_PENDING',sol_current_ack=None,sol_current_delivery=proof,sol_latest_delivery=proof,last_sol_cursor=post['cursor'],sol_next_wp_prepared=None,sol_next_prepared_delivery=None,sol_next_action='COLLECT_R27_QA_PREPARATION_AND_A_E1_THEN_NEW_EXACT_FREEZE_FRESH_SOL_EXECUTION_QA',updated_at=at);c['last_monitor_run'].update(status='R26_DISPOSED_R27_A_IMPLEMENTATION_AND_SOL_PREP_ACTUAL_SENT');write(cp,c)
 sp=H/'DISPATCHER_STATE.json';st=read(sp);st['endpoints']['sol'].update(current_wp=op['wp_id'],current_wp_revision='S1',current_delivery_id=op['delivery_id'],current_result_id=None,current_turn_id=post['latestTurn']['id'],actual_turn_id=post['latestTurn']['id'],execution_phase='IN_PROGRESS',ack_verified=False,explicit_ack_pending=True,current_runtime_idle_verified=False,last_runtime_observation_cursor=post['cursor']);st['master_monitor_automation']=c['master_monitor_automation'];st['deliveries'].append({'delivery_id':op['delivery_id'],'recipient':'Sol','wp_id':op['wp_id'],'wp_revision':'S1','delivery_status':'SENT','status':'ACTIVE_ACK_PENDING','proof':str(vp),'runtime_e2_released':False});st['updated_at']=at;write(sp,st)
 e={'at':at,'event_id':op['delivery_id']+'-ACTUAL_SENT','type':'SOL_R27_INDEPENDENT_CAPTURE_READONLY_PREPARATION_SENT','delivery_id':op['delivery_id'],'proof':str(vp),'proof_sha256':sha(vp),'turn_id':post['latestTurn']['id'],'cursor':post['cursor'],'protected':op['protected_unique_paths'],'no_duplicate_wp':True}
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr);event(e)
 para=f'\n\n## LOCAL-R27-A-IMPLEMENTATION-SOL-INDEPENDENT-QA-PREP-SENT — {at}\nOriginalSol {op["delivery_id"]}/{op["wp_id"]}/S1 actual direct SENT/new active turn {post["latestTurn"]["id"]}/cursor{post["revision"]}/ACKpending. Scope independent READ_ONLY frozen R25/R26 plus Master R27 contract15getters, prospectively owned4normalpairs/fulltyped-UTF8/copy27-private7/provenance only; QA build-execution0, mutableR27 read0. Protected{op["protected_unique_paths"]}; A solewriter R27PURECapture oneinsertion/6outputs SENT; no registration-launcher-native/adverse. SameactualhourlyACTIVE60min173charcorrecttarget; futureR27run UNOBSERVED. R26 preparationaccepted notPASS/R25S2scopedPASS andoldS1FAILpreserved/fullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof {vp}\n'
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
 nx=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';nx.write_text(para+'\n'+nx.read_text(encoding='utf-8-sig'),encoding='utf8');print(json.dumps(e))
else:raise ValueError(stage)
