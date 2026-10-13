from pathlib import Path
import json,hashlib,datetime,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent
assert c['active_operation'] is None and t['dispatch_id'].endswith('49256586') and t['delivery_status']=='SENT' and t['submission_attempts']==1 and not t['unknown_delivery']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json');v=read(C/'MASTER_SOL_R20_TRUSTED_STARTUP_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json')
assert v['verification_status']=='MASTER_DISPOSED' and sum(x.get('result_id')==v['result_id'] for x in receipts['processed_results'])==1
assert read(C/'MASTER_DEFECT_ENGINE_G05_OPAQUE_R18_20261010.json')['status']=='CLOSED'
assert read(C/'MASTER_DEFECT_ENGINE_G05_RECEIPT_UTC_R20_20261011.json')['status']=='OPEN'
assert not read(C/'MASTER_R20_DISPOSITION_NOTICE_SOL_SEND_TOOL_20261011.json').get('isError')
sn=json.loads(read(C/'MASTER_R20_DISPOSITION_NOTICE_SOL_FINAL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
notice={'at':at,'type':'SOL_R20_MASTER_DISPOSITION_RECEIPT_NOTICE','new_QA_WP':False,'exact_message':'Master R20 판정을 수신해 주세요. MASTER_R20_SOL_DISPOSITION_NOTICE_20261011.md 수신만 기록;기존candidate/raw불변,새QA 아님','instruction_path':str(C/'MASTER_R20_SOL_DISPOSITION_NOTICE_20261011.md'),'instruction_sha256':sha(C/'MASTER_R20_SOL_DISPOSITION_NOTICE_20261011.md'),'actual_predispatch':str(C/'MASTER_R20_DISPOSITION_NOTICE_SOL_PREDISPATCH_20261011.json'),'actual_send_tool':str(C/'MASTER_R20_DISPOSITION_NOTICE_SOL_SEND_TOOL_20261011.json'),'actual_send_tool_sha256':sha(C/'MASTER_R20_DISPOSITION_NOTICE_SOL_SEND_TOOL_20261011.json'),'actual_latest_snapshot':sn,'delivery_status':'SENT_TOOL_ACCEPTED_ACTUAL_NEW_TURN','unknown_delivery':False,'duplicate_terminal_request':False}
notice['exact_user_message']=json.loads(read(C/'MASTER_R20_DISPOSITION_NOTICE_SOL_SEND_TOOL_20261011.json')['content'][0]['text'])
baseline=read(Path(t['scope_baseline_path']));worker=Path(t['allowed_mutable_paths'][0]);raw=worker.read_bytes();prefix=Path(baseline['fixed_prefix']['path']).read_bytes();suffix=Path(baseline['fixed_suffix']['path']).read_bytes()
assert raw.startswith(prefix) and raw.endswith(suffix)
current_worker_changed=sha(worker)!=baseline['worker_before_sha256']
ack=None;ackerr=None
if Path(t['ack_path']).exists():
 try:
  ack=read(Path(t['ack_path']));assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==24
 except (json.JSONDecodeError,AssertionError) as ex:ackerr=str(ex) or 'Identity mismatch';ack=None
if ack:
 t.update(ack_verified=True,ack_sha256=sha(Path(t['ack_path'])),status='IN_PROGRESS',updated_at=at);b['updated_at']=at;write(bp,b);c['a_status']='R21_IN_PROGRESS_ACK_VERIFIED'
 c['a_latest_delivery'].update(status='SENT_ACK_VERIFIED_IN_PROGRESS',ack=ack,ack_sha256=t['ack_sha256'])
proof={'at':at,'R20_dedupe_count':1,'R20_master_verdict':v['master_verdict'],'A_R21_actual_sent':True,'A_one_submission':True,'A_ACK':'VERIFIED' if ack else ('UNVERIFIED_ERROR' if ackerr else 'PENDING'),'A_ACK_error':ackerr,'A_completion_exists':Path(t['completion_path']).exists(),'R21_fixed_source_prefix_suffix_match':True,'R21_current_worker_changed':current_worker_changed,'Sol_notice':notice,'new_QA_WP':False,'scheduler_actual':cfg,'full_native_E2_released':False,'historical_scoped_opaque_defect':'CLOSED_R19_ONLY','new_receipt_UTC_lexical_defect':'OPEN','foundation':'HOLD','guard_actual_release':'PENDING_FINALLY','Master_production_execution_builds':0,'metadata_preparation_failures':'InitialLFvsCRLFdelimiter then undefined final-print verdict;disposition/preparation persisted at respective stop points;reconciled same unique task/no duplicate/no candidate or QA mutation/execution'}
vp=C/'MASTER_R20_COMPLETE_R21_FINAL_COORDINATION_AUDIT_20261011.json';assert not vp.exists();write(vp,proof)
c.update(sol_latest_receipt_notice=notice,last_sol_cursor=sn['cursor'],sol_status='R20_DISPOSED_RECEIPT_NOTICE_ONLY_'+sn['thread']['status']['type'].upper(),updated_at=at);write(cp,c)
s=read(H/'DISPATCHER_STATE.json');s['endpoints']['sol'].update(execution_phase=c['sol_status'],current_runtime_idle_verified=sn['thread']['status']['type']=='idle',last_runtime_observation_cursor=sn['cursor']);s['endpoints']['a']['ack_verified']=bool(ack);s['updated_at']=at;write(H/'DISPATCHER_STATE.json',s)
event(dict(notice,event_id='MASTER-SOL-R20-DISPOSITION-NOTICE-20261011-01',proof_path=str(vp),proof_sha256=sha(vp)))
event({'at':at,'event_id':'MASTER-R20-R21-FINAL-AUDIT-20261011-01','type':'MASTER_COORDINATION_FINAL_AUDIT','proof_path':str(vp),'proof_sha256':sha(vp),'ACK':proof['A_ACK'],'scheduler':'ACTIVE60MIN','Foundation':'HOLD'})
print(json.dumps({k:proof[k] for k in ['R20_dedupe_count','A_R21_actual_sent','A_ACK','A_completion_exists','R21_fixed_source_prefix_suffix_match','R21_current_worker_changed','foundation']}))
