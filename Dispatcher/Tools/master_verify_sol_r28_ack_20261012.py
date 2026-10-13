from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';RUN='MASTER-R28-SOL-ACK-20261012-01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);d=c['sol_current_delivery'];Q=Path(d['qa_root']);mode=sys.argv[1]
if mode=='verify':
 lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert lock['status']=='LOCKED' and lock['run_id']==RUN and lock['pid']==31636
 assert c['active_operation'] is None and d['wp_revision']=='S1' and d['delivery_id']=='SOL-GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012-01'
 ack=read(Q/'ACK_INITIAL.json');assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='AD2F58855FB9D4FC49C7068389F217BE498DD63093D0FA460CBA6025CB15A52B'
 assert all(ack[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and ack['result_id']=='SOL-GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012-99b7c410f7ee452a91169778881914dc'
 for k in ['wp','baseline','frozen_manifest','selected','pdb']:check(ack[k])
 assert ack['wp']['path']==d['wp_path'] and ack['wp']['sha256']==d['wp_sha256'] and ack['baseline']['path']==d['baseline_path'] and ack['baseline']['sha256']==d['baseline_sha256']
 sn=json.loads(read(C/'MASTER_SOL_R28_FRONTEND_ROUTE_ACK_SNAPSHOT_20261012.json')['content'][0]['text'])['polls'][0];assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
 base=read(Path(d['baseline_path']));before=read(Q/'PRESERVATION_BEFORE.json');assert len(base['files'])==14045
 for f in base['files']:check(f)
 assert {f['path']:(f['sha256'],f['bytes']) for f in base['files']}=={f['path']:(f['sha256'],f['bytes']) for f in before['protected_files']}
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173
 b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];assert t['dispatch_id'].endswith('7c324c51') and t['status']=='IN_PROGRESS' and t['ack_verified'] and not Path(t['completion_path']).exists()
 proof={'at':at,'guard_run':RUN,'guard_session':34847,'guard_pid':31636,'delivery_id':d['delivery_id'],'wp_id':d['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'initial_ACK':row(Q/'ACK_INITIAL.json'),'actual_snapshot':sn,'protected_unique_paths':14045,'frozen_candidate':ack['selected'],'matching_PDB':ack['pdb'],'selected_mvid':ack['selected_mvid_master_admitted'],'current9_before_exact':True,'QA_before_inventory_matched':True,'status':'ACK_VERIFIED_ORIGINAL_SOL_INDEPENDENT_FRONTEND_ROUTE_STATIC_IN_PROGRESS','ACK_counters_are_initial_not_current_or_terminal':True,'A_current_result_completion_observed':False,'A_busy_no_duplicate':True,'no_new_WP_or_message':True,'native_e2_released':False,'closure_changed':False,'foundation':'HOLD','scheduler_actual':cfg}
 p=C/'MASTER_SOL_R28_FRONTEND_ROUTE_ACK_VERIFICATION_20261012.json';assert not p.exists();write(p,proof);c.update(sol_current_ack=proof,sol_current_result_id=ack['result_id'],sol_status=proof['status'],last_sol_cursor=sn['cursor'],updated_at=at);c['last_monitor_run']={'run_id':RUN,'guard_pid':31636,'guard_session':34847,'at':at,'status':'R28_SOL_ACK_VERIFIED_A_BUSY_NO_NEW_WP_MONITOR_UNCHANGED','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(execution_phase='IN_PROGRESS_ACK_VERIFIED',ack_verified=True,last_result_id=ack['result_id'],last_runtime_observation_cursor=sn['cursor']);write(sp,s)
 event={'at':at,'event_id':d['delivery_id']+'-ACK-VERIFIED','type':'SOL_R28_INDEPENDENT_STATIC_ACK_ACTUAL_SAME_ACTIVE_TURN','proof':row(p)}
 para=f'\n\n## LOCAL-SOL-R28-FRONTEND-ROUTE-ACK — {at}\nOriginalSol{d["delivery_id"]}/{ack["result_id"]}/S1 immutableACKSHA{sha(Q/"ACK_INITIAL.json")}/actualsameactiveinProgress/cursor174;Master rehashed14045/current9/frozen83/managed4/before inventory matched. ExactR27 read-only frontendIL/bootstraporder-route audit/noAnewproposalread/initialcounters0areACKnotterminal-currentclaim. A R28actualSENT/ACKinProgress/completionabsent/no duplicate/newWP;currenthourlyACTIVE unchanged/futureR28runUNOBSERVED. Findingspending/notnormalruntime-or-nativePASS/EnginePipelineGQ1OPEN/FoundationHOLD. Proof{p}\n'
 for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with q.open('a',encoding='utf8') as f:f.write(para)
elif mode=='released':
 p=C/'MASTER_R28_SOL_ACK_GUARD_FINALLY_RELEASE_20261012.json';tool=read(p)['actual_release_tool'];lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert tool['exit_code']==0 and lock['status']=='RELEASED' and lock['run_id']==RUN
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',release_proof=str(p),released_at=lock['released_at']);write(cp,c);event={'at':at,'event_id':RUN+'-RELEASE','type':'ACTUAL_GUARD_FINALLY_RELEASE','proof':str(p)}
else:raise ValueError(mode)
for q in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with q.open('a',encoding='utf8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(mode+'_RECORDED')
