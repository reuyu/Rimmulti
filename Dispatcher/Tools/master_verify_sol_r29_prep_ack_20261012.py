from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';RUN='MASTER-R29-SOL-PREP-ACK-20261012-01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);d=c['sol_current_delivery'];Q=Path(d['qa_root']);mode=sys.argv[1]
if mode=='verify':
 lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert lock['status']=='LOCKED' and lock['run_id']==RUN and lock['pid']==21856 and c['active_operation'] is None
 ack=read(Q/'ACK_INITIAL.json');assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='8B801439D5857404F93E99C343328F1881980E751112705F940B5322AD3FF97A' and all(ack[k]==d[k] for k in ['delivery_id','wp_id','wp_revision'])
 assert ack['result_id']=='SOL-GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012-2b883a31352547c6bda6f398d204600f'
 for k in ['wp','contract','master_review','baseline','frozen_manifest']:check(ack[k])
 assert ack['wp']['path']==d['wp_path'] and ack['wp']['sha256']==d['wp_sha256'] and ack['baseline']['sha256']==d['baseline_sha256']
 sn=json.loads(read(C/'MASTER_SOL_R29_STARTUP_PAIR_PREP_ACK_SNAPSHOT_20261012.json')['content'][0]['text'])['polls'][0];assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
 base=read(Path(d['baseline_path']));before=read(Q/'PRESERVATION_BEFORE.json');assert len(base['files'])==14105
 for f in base['files']:check(f)
 assert {f['path']:(f['sha256'],f['bytes']) for f in base['files']}=={f['path']:(f['sha256'],f['bytes']) for f in before['protected_files']}
 b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];assert t['dispatch_id'].endswith('46f60e2a') and t['status']=='IN_PROGRESS' and t['ack_verified'] and not Path(t['completion_path']).exists()
 for f in t['production_fixed_files']:check(f)
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173
 proof={'at':at,'guard_run':RUN,'guard_session':49220,'guard_pid':21856,'delivery_id':d['delivery_id'],'wp_id':d['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'initial_ACK':row(Q/'ACK_INITIAL.json'),'actual_snapshot':sn,'protected_unique_paths':14105,'frozen83_currentfixed2_matched':True,'exactcurrentmutable7_excluded_unread':True,'status':'ACK_VERIFIED_R29_INDEPENDENT_FROZEN_R27_AUXILIARY_CONTRACT_NORMAL_ORACLE_PREPARATION_IN_PROGRESS','R29_candidate_verdict':'NOT_REVIEWED','ACK_counters_initial_not_current_terminal':True,'preparation_reported_approach':'Original declaration7 versus existing factory UsedClone/Trim/nested snapshot GetFullPath separated; future ownQA configlocator rebind explicit sidecar, historicalraw14/7 preserved; final oracle notyetverified','A_completion_observed':False,'no_new_WP_or_duplicate':True,'native_e2_released':False,'closure_changed':False,'foundation':'HOLD','scheduler_actual':cfg}
 p=C/'MASTER_SOL_R29_STARTUP_PAIR_PREP_ACK_VERIFICATION_20261012.json';assert not p.exists();write(p,proof);c.update(sol_current_ack=proof,sol_current_result_id=ack['result_id'],sol_status=proof['status'],last_sol_cursor=sn['cursor'],updated_at=at);c['last_monitor_run']={'run_id':RUN,'guard_pid':21856,'guard_session':49220,'at':at,'status':'R29_SOL_PREP_ACK_VERIFIED_A_BUSY_NO_DUPLICATE_MONITOR_UNCHANGED','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(execution_phase='PREPARATION_IN_PROGRESS_ACK_VERIFIED',ack_verified=True,last_result_id=ack['result_id'],last_runtime_observation_cursor=sn['cursor']);write(sp,s)
 event={'at':at,'event_id':d['delivery_id']+'-ACK-VERIFIED','type':'SOL_R29_PREPARATION_ACK_ACTUAL_SAME_ACTIVE_TURN','proof':row(p)}
 para=f'\n\n## LOCAL-SOL-R29-STARTUP-PAIR-PREP-S1-ACK — {at}\nOriginalSol{d["delivery_id"]}/{ack["result_id"]}/S1 immutableACKSHA{sha(Q/"ACK_INITIAL.json")}/actualsameactiveinProgress/cursor177. Master rehashed14105/frozen83/currentfixedCensuscsproj2/beforeinventory matched; exactmutable7unread/newR29sourcepublisherbinobjunread. Contract-only prospective6normal fulltyped/raw/copy oracle preparation, initialcounters0notcurrentterminalclaim/R29NOTREVIEWED/no executionPASS. Originaldecl7 separatedfromlegacy factoryUsedClone/Trim/nestedGetFullPath; plannedownQA configlocator rebind only+oldraw14/7sidecar unchanged approach, finaloraclepending. AactualR29SENT/ACKinProgress/completionabsent/no duplicate/newWP; samehourlyACTIVE60minunchanged/directSolpush. EnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{p}\n'
 for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with q.open('a',encoding='utf8') as f:f.write(para)
elif mode=='released':
 p=C/'MASTER_R29_SOL_PREP_ACK_GUARD_FINALLY_RELEASE_20261012.json';tool=read(p)['actual_release_tool'];lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert tool['exit_code']==0 and lock['status']=='RELEASED' and lock['run_id']==RUN
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=lock['released_at'],release_proof=str(p));write(cp,c);event={'at':at,'event_id':RUN+'-RELEASE','type':'ACTUAL_GUARD_FINALLY_RELEASE','proof':str(p)}
else:raise ValueError(mode)
for q in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with q.open('a',encoding='utf8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(mode+'_RECORDED')
