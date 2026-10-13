from pathlib import Path
import json,hashlib,datetime,tomllib,sys
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent
assert c['active_operation'] is None and t['dispatch_id'].endswith('cdc223f3') and t['delivery_status']=='SENT' and t['submission_attempts']==1 and not t['unknown_delivery']
sol=c['sol_current_delivery'];assert sol['wp_id']=='WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_PREPARATION' and sol['delivery_status']=='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN' and not sol['unknown_delivery']
for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
for k in ['wp','baseline','pre','tool','post']:assert sha(Path(sol[k+'_path']))==sol[k+'_sha256']
for f in t['production_fixed_files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
rr=read(R/'Dispatcher/MASTER_RECEIPTS.json');v=read(C/'MASTER_R26_DUAL_CHILD_REG_PREPARATION_COMPLETION_VERIFICATION_20261011.json')
assert v['verification_status']=='MASTER_DISPOSED'
for k in ['A_result_id','Sol_result_id']:assert sum(x.get('result_id')==v[k] for x in rr['processed_results'])==1
for k in [t['dispatch_id']+'-SENT-HOURLY-ACTIVE',sol['delivery_id']+'-ACTUAL_SENT']:assert sum(x.get('event_id')==k for x in rr['processed_dispatch_events'])==1
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
ack=None
if Path(t['ack_path']).exists():
 ack=read(Path(t['ack_path']))
 assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack.get('wp_revision',ack.get('task_revision'))==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==30
 t.update(ack_verified=True,ack_sha256=sha(Path(t['ack_path'])),status='IN_PROGRESS',ack_observed_at=at);write(bp,b)
c.update(a_status='R27_CHILD_CAPTURE_IMPLEMENTATION_IN_PROGRESS_ACK_VERIFIED' if ack else 'R27_CHILD_CAPTURE_IMPLEMENTATION_SENT_ACK_PENDING',updated_at=at)
c['last_monitor_run'].update(status='R26_DUAL_DISPOSED_R27_A_PURE_CAPTURE_AND_SOL_READONLY_PREPARATION_ACTUAL_SENT',release_status='PENDING_ACTUAL_FINALLY')
write(cp,c)
p=C/'MASTER_R26_R27_RECOVERY_FINAL_COORDINATION_AUDIT_20261012.json';assert not p.exists()
proof={'at':at,'run_id':'MASTER-R26-R27-RECOVERY-20261012-01','guard_pid':20116,'guard_session':83680,'R26_result_receipts_each':1,'A_R27_actual_submission':row(Path(t['submission_proof'])),'A_exact_scope':row(Path(t['scope_baseline_path'])),'A_ACK':'VERIFIED' if ack else 'PENDING','Sol_R27_delivery':sol['delivery_id'],'Sol_actual':sol['actual_snapshot'],'Sol_ACK':'PENDING','Sol_exact_message':row(C/'MASTER_SOL_R27_CHILD_CAPTURE_PREPARATION_EXACT_MESSAGE_20261012.json'),'api_name_correction':row(H/'MASTER_R27_CAPTURE_API_NAME_CORRECTION_20261012.md'),'protected':sol['protected_unique_paths'],'single_writer':'A exact current7 only; Sol frozen-R25 source/read-only-preparation only','current_obj_in_protected_baseline':0,'contender_actual':'MASTER-R27-CONTENDER-20261012-01 LOCK_BUSY/exit1','actual_scheduler':cfg,'future_R27_scheduled_run_observed':False,'old_invocation_full_lock_coverage':'UNVERIFIED_TTL_EXPIRED_NOT_RETROCLAIMED','reconciliation':row(C/'MASTER_R26_R27_INTERRUPTED_PREPARATION_RECONCILIATION_20261012.json'),'A_completion_exists_now':Path(t['completion_path']).exists(),'production_native_execution_by_Master':0,'full_native_e2_released':False,'closure_changed':False,'foundation':'HOLD','release_status':'PENDING_ACTUAL_FINALLY'}
write(p,proof)
for j in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with j.open('a',encoding='utf8') as f:f.write(json.dumps({'at':at,'event_id':t['dispatch_id']+'-FINAL-AUDIT','type':'R26_DISPOSED_R27_A_AND_SOL_ACTUAL_SENT_FINAL_AUDIT','proof':str(p),'proof_sha256':sha(p)},ensure_ascii=False)+'\n')
print(json.dumps({'status':'FINAL_AUDIT_MATCHED','A_ACK':proof['A_ACK'],'Sol_ACK':proof['Sol_ACK'],'scheduler':'ACTIVE60MIN','A_completion':proof['A_completion_exists_now']}))
