from pathlib import Path
import json,datetime,hashlib,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');r=read(R/'Dispatcher/MASTER_RECEIPTS.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1]
p=read(C/'MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_E1_VERIFICATION_20261010.json');d=read(C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_DELIVERY_VERIFICATION_20261010.json')
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
assert c['active_operation'] is None and cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
assert p['verification_status']=='MASTER_DISPOSED' and t['dispatch_id']==p['dispatch_id'] and t['result_id']==p['result_id'] and t['monitor_status']=='PAUSED60MIN_VERIFIED'
assert sum(x.get('result_id')==p['result_id'] for x in r['processed_results'])==1
assert sum(x.get('event_id')==d['delivery_id']+'-ACTUAL_SENT' for x in r['processed_dispatch_events'])==1
assert c['sol_current_attempt_id']==d['delivery_id'] and c['last_sol_cursor']==d['actual_snapshot']['cursor'] and not d['unknown_delivery']
checks=[]
for key in ['wp','baseline']:
 q=Path(d[key+'_path']);assert sha(q)==d[key+'_sha256'];checks.append({'path':str(q),'sha256':sha(q),'matched':True})
for q,h in [(Path(p['frozen_manifest']),p['frozen_manifest_sha256']),(Path(p['master_review_path']),p['master_review_sha256'])]:
 assert sha(q)==h;checks.append({'path':str(q),'sha256':h,'matched':True})
proof={'at':at,'run_id':p['run_id'],'guard_session':41964,'guard_pid':11096,'status':'R18_TERMINAL_DISPOSED_FRESH_ORIGINAL_SOL_QA_SENT_HOURLY_PAUSED_VERIFIED','identity_checks':checks,'result_dedupe_count':1,'dispatch_dedupe_count':1,'a_status':t['status'],'sol_delivery_id':d['delivery_id'],'actual_sol_turn':d['actual_snapshot']['latestTurn']['id'],'actual_sol_cursor':c['last_sol_cursor'],'sol_ACK':'PENDING_SEPARATE_IDENTITY_PROOF','automation_actual':cfg,'active_operation':None,'immutable_protected_count':9374,'new_A_corrective_WP':'NOT_SENT_PENDING_INDEPENDENT_FINDINGS','production_modify_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','actual_guard_finally_release':'PENDING'}
dest=C/'MASTER_R18_TERMINAL_QA_SENT_COORDINATION_AUDIT_20261010.json';assert not dest.exists();dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:proof[k] for k in ['status','result_dedupe_count','dispatch_dedupe_count','actual_sol_turn','actual_sol_cursor','immutable_protected_count','sol_ACK','new_A_corrective_WP']},ensure_ascii=True))

