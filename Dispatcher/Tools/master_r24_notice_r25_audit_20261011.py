from pathlib import Path
import json,datetime,hashlib,sys,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);stage=sys.argv[1];pre=C/'MASTER_R24_DISPOSITION_NOTICE_PREDISPATCH_20261011.json'
if stage=='sending':
 assert c['active_operation'] is None
 sn=json.loads(read(pre)['content'][0]['text'])['polls'][0];assert sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['revision']==151
 c['active_operation']={'type':'SOL_R24_DISPOSITION_RECEIPT_NOTICE_ONLY','stage':'DELIVERY_ATTEMPT_PENDING_TOOL','delivery_id':'MASTER-R24-DISPOSITION-NOTICE-20261011-01','unknown_delivery':True,'new_QA_WP':False,'at':at};write(cp,c);print('SOL_RECEIPT_ONLY_NOTICE_ONE_ATTEMPT_PENDING')
elif stage=='sent_audit':
 assert c['active_operation']['type']=='SOL_R24_DISPOSITION_RECEIPT_NOTICE_ONLY' and c['active_operation']['unknown_delivery']
 tool=C/'MASTER_R24_DISPOSITION_NOTICE_SEND_TOOL_20261011.json';assert not read(tool).get('isError');postp=C/'MASTER_R24_DISPOSITION_NOTICE_POSTSEND_20261011.json';post=json.loads(read(postp)['content'][0]['text'])['polls'][0];assert post['latestTurn']['id']!=json.loads(read(pre)['content'][0]['text'])['polls'][0]['latestTurn']['id']
 notice={'at':at,'delivery_id':c['active_operation']['delivery_id'],'status':'SENT_ACTUAL_TOOL_NEW_NOTICE_TURN','unknown_delivery':False,'actual_snapshot':post,'tool_path':str(tool),'tool_sha256':sha(tool),'new_QA_WP':False}
 b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];assert t['dispatch_id'].endswith('dd341868') and t['delivery_status']=='SENT' and not t['unknown_delivery'] and t['submission_attempts']==1
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
 r=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert sum(x.get('result_id')=='WE-A-ENGINE-GATE05-R24-M04-PREP-RESULT-01' for x in r['processed_results'])==1 and sum(x.get('result_id')=='SOL-GATE05-R24-M04-PREPARATION-S1-20261011-eb71f49825a7400699a8b23188e5db28' for x in r['processed_results'])==1
 assert sum(x.get('event_id')==t['dispatch_id']+'-SENT-HOURLY-ACTIVE' for x in r['processed_dispatch_events'])==1
 ack=None
 if Path(t['ack_path']).exists():
  ack=read(Path(t['ack_path']));assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack.get('envelope',ack.get('delivery_envelope_revision'))==28
  t.update(status='IN_PROGRESS',ack_verified=True,ack_sha256=sha(Path(t['ack_path'])),ack_observed_at=at);write(R/'Dispatcher/MASTER_A_TASKS.json',b)
 c.update(active_operation=None,last_sol_cursor=post['cursor'],sol_latest_receipt_notice=notice,sol_status='R24_DISPOSED_RECEIPT_NOTICE_ONLY_NO_ACTIVE_QA',a_status='R25_ROLE_USERDATA_IN_PROGRESS_ACK_VERIFIED' if ack else c['a_status'],updated_at=at);write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(execution_phase='R24_DISPOSED_RECEIPT_NOTICE_ONLY_NO_NEW_QA',current_runtime_idle_verified=post['thread']['status']['type']=='idle',last_runtime_observation_cursor=post['cursor'],latest_notice_turn_id=post['latestTurn']['id']);s['endpoints']['a'].update(ack_verified=bool(ack));write(sp,s)
 p=C/'MASTER_R24_DUAL_COMPLETE_R25_FINAL_COORDINATION_AUDIT_20261011.json';assert not p.exists();write(p,{'at':at,'guard_run':'MASTER-R24-RESUME-20261011T121945Z-01','guard_pid':11696,'guard_session':37601,'R24_A_result_dedupe':1,'R24_Sol_result_dedupe':1,'R25_delivery_dedupe':1,'R25_actual_sent':True,'R25_ack':ack,'R25_ack_sha256':sha(Path(t['ack_path'])) if ack else None,'actual_scheduler':cfg,'Sol_receipt_only_notice':notice,'no_new_QA_WP':True,'next_QA':'ONLY_AFTER_NEW_R25_TERMINAL_MASTER_FREEZE_ADMISSION_AND_ORIGINAL_SOL_IDLE','R25_scope':'PURE_ROLE_SELECTOR_ACTIVE_SAFE_BRANCH_DECLARED_LOG_3SPANS4FIXED6OUTPUTS','protected_baseline_paths':13055,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','original_old_guard_status':'TTL_EXPIRED_NO_MUTATIONS_AFTER_INTERRUPTION_NO_RETROLOCKCLAIM','metadata_errors':'Initial JS patch parse failed before calls/writes;node kernel sky missing then initialized;console cp949 mojibake only,UTF8 files preserved'})
 e={'at':at,'event_id':notice['delivery_id']+'-ACTUAL_SENT','type':'SOL_R24_MASTER_DISPOSITION_RECEIPT_ONLY_NOTICE_SENT','proof':str(p),'proof_sha256':sha(p)}
 r['processed_dispatch_events'].append(e);write(R/'Dispatcher/MASTER_RECEIPTS.json',r)
 for q in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with q.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 print(json.dumps({'R24A':'DISPOSED','R24Sol':'DISPOSED','R25A':'SENT_ACK_VERIFIED' if ack else 'SENT_ACK_PENDING','Sol':'RECEIPT_ONLY_NOTICE_NEW_TURN_NO_QA','monitor':'ACTIVE_HOURLY','foundation':'HOLD'},ensure_ascii=True))
else:raise ValueError(stage)
