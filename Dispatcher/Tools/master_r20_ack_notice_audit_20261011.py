from pathlib import Path
import json,datetime,hashlib,sys,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def journal(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
cpath=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cpath);bpath=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bpath);t=b['tasks'][-1];T=Path(t['instruction_path']).parent
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
if sys.argv[1]=='attempt':
 assert c['active_operation'] is None and t['delivery_status']=='SENT'
 d=read(T/'MASTER_ACK_NOTICE_DRAFT.json');assert 'Message input Value: '+d['message'] in d['accessibility']['tree']
 c['active_operation']={'type':'SAME_R20_ACK_JSON_NOTICE','dispatch_id':t['dispatch_id'],'message':d['message'],'unknown_delivery':True,'attempt_started_at':at,'new_wp':False};c['updated_at']=at;write(cpath,c)
 journal({'at':at,'event_id':t['dispatch_id']+'-ACK-NOTICE-ATTEMPT','type':'SAME_WP_METADATA_CLARIFICATION_ATTEMPT','unknown_delivery':True,'new_wp':False})
 print('ACK_NOTICE_ONE_SUBMIT_PENDING')
elif sys.argv[1]=='delivered':
 op=c['active_operation'];assert op['type']=='SAME_R20_ACK_JSON_NOTICE' and op['unknown_delivery']
 p=T/'MASTER_ACK_NOTICE_SUBMITTED.json';d=read(p);tree=d['accessibility']['tree']
 assert ' 텍스트 '+op['message'] in tree and 'Message input Value:' not in tree
 proof=dict(op,at=at,unknown_delivery=False,status='SAME_WP_NOTICE_ACTUAL_SENT_NO_NEW_WP',post_path=str(p),post_sha256=sha(p),actual_send_tool=str(T/'MASTER_ACK_NOTICE_SEND_TOOL.json'),one_notice_submit=True,producer_bad_ACK_preserved=str(T/'MASTER_ACK_MALFORMED_ORIGINAL_20261011.json.txt'))
 vp=T/'MASTER_ACK_NOTICE_DELIVERY_PROOF.json';assert not vp.exists();write(vp,proof)
 c.update(active_operation=None,a_same_wp_metadata_notice=proof,updated_at=at);write(cpath,c)
 t['same_wp_metadata_notice']=str(vp);b['updated_at']=at;write(bpath,b)
 journal({'at':at,'event_id':t['dispatch_id']+'-ACK-NOTICE-SENT','type':'SAME_WP_ACK_JSON_CLARIFICATION_ACTUAL_SENT','proof':str(vp),'new_wp':False})
 print('SAME_WP_ACK_NOTICE_ACTUAL_SENT')
elif sys.argv[1]=='audit':
 assert c['active_operation'] is None and t['delivery_status']=='SENT' and t['submission_attempts']==1
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
 assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173
 assert read(C/'MASTER_DEFECT_ENGINE_G05_OPAQUE_R18_20261010.json')['status']=='CLOSED'
 r=read(R/'Dispatcher/MASTER_RECEIPTS.json')
 rid='SOL-GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010-2c4a145f15334594bba451900223477a'
 assert sum(x.get('result_id')==rid for x in r['processed_results'])==1
 s=json.loads(read(C/'MASTER_R19_DISPOSITION_NOTICE_SOL_FINAL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
 assert s['thread']['status']['type']=='idle' and s['latestTurn']['status']=='completed'
 proof={'at':at,'R19_result_dedupe':1,'R19_scope_closed':'OPAQUE_NORMAL_ONLY','A_R20_actual_sent':True,'one_WP_submit':True,'one_same_WP_metadata_notice':True,'ACK_current':'UNVERIFIED_MALFORMED_ORIGINAL_PENDING_PRODUCER_CORRECTION','Sol_receipt_notice':s,'new_QA':False,'scheduler_actual':cfg,'all_Master_child_commands_completed':True,'historic_mutex_gaps_not_retroclaimed':True,'full_native_E2_not_released':True,'foundation':'HOLD','actual_guard_release':'PENDING'}
 write(C/'MASTER_R19_COMPLETE_R20_FINAL_COORDINATION_AUDIT_20261011.json',proof)
 with (R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md').open('a',encoding='utf8') as f:f.write(f'\n\n## R20 ACK metadata qualification — {at}\nActual A R20 {t["dispatch_id"]} SENT oneWPsubmit;ACK file malformed JSON escape so ACK UNVERIFIED,not code/delivery failure. Raw original preserved in task, same-WP notice actual oneSent (no newWP),A must preserve malformed history and serialize corrected artifact with truthfulidentity/timestamp. Do not silently fix producer ACK in Master. SameactualhourlyACTIVE;Sol R19 artifactaccepted/opaque scopedCLOSED,failedhistoricalturn separate;new receipt notice actualcompletedidle124/no newQA. Master v2 read-only verification390/9841 completed;first latency-interrupted Masterchecker no candidate/QAexecute. Task notice proof {T/"MASTER_ACK_NOTICE_DELIVERY_PROOF.json"}.\n')
 print('FINAL_COORDINATION_AUDIT_MATCHED')
else:raise ValueError(sys.argv[1])
