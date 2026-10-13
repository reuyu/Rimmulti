from pathlib import Path
import json,hashlib,datetime,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for q in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with q.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1]
assert c['active_operation'] is None and t['delivery_status']=='SENT' and t['submission_attempts']==1 and not t['unknown_delivery'] and t['dispatch_id'].endswith('9be1579a')
for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
v=read(C/'MASTER_SOL_R21_RECEIPT_UTC_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json');r=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert v['verification_status']=='MASTER_DISPOSED' and sum(x.get('result_id')==v['result_id'] for x in r['processed_results'])==1
defect=read(C/'MASTER_DEFECT_ENGINE_G05_RECEIPT_UTC_R20_20261011.json');assert defect['status']=='CLOSED' and defect['independent_closure_result_id']==v['result_id'] and not defect['broader_gate_closure'];assert read(C/'MASTER_DEFECT_ENGINE_G05_OPAQUE_R18_20261010.json')['status']=='CLOSED'
ack=read(Path(t['ack_path']));assert all(ack[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and ack['envelope']==25 and ack['status']=='ACKNOWLEDGED' and ack['task_state']=='IN_PROGRESS'
sn=json.loads(read(C/'MASTER_R21_DISPOSITION_NOTICE_SOL_FINAL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0];send=C/'MASTER_R21_DISPOSITION_NOTICE_SOL_SEND_TOOL_20261011.json';assert not read(send).get('isError')
msg=C/'MASTER_R21_SOL_DISPOSITION_EXACT_MESSAGE_20261011.txt';notice={'at':at,'type':'SOL_R21_DISPOSITION_RECEIPT_ONLY','new_QA_WP':False,'actual_tool':str(send),'tool_sha256':sha(send),'exact_message_path':str(msg),'exact_message_sha256':sha(msg),'actual_snapshot':sn,'delivery_status':'TOOL_ACCEPTED_NEW_RECEIPT_TURN','unknown_delivery':False,'no_terminal_resend_requested':True}
proof={'at':at,'R21_result_dedupe':1,'R21_UTC_defect':'CLOSED_NORMAL_16_RECEIPT_ORIGINAL_STRING_TOKEN_WHOLE_GRAPH_BYTES_ONLY','new_A_dispatch_id':t['dispatch_id'],'A_delivery_status':'SENT_ACK_VERIFIED_IN_PROGRESS','one_actual_A_submit':True,'ACK':ack,'ACK_sha256':sha(Path(t['ack_path'])),'ACK_observed_at':at,'ACK_timestamp_qualification':'Producer selfreported time; actual UI SENT and Master observed ACK time control. Not independent runtime clock proof.','completion_observed':Path(t['completion_path']).exists(),'scheduler_actual':cfg,'Sol_notice':notice,'new_QA_WP':False,'full_native_E2_released':False,'Foundation':'HOLD','scope':'R22M01explicit7/privatecapture fourregions,R21UTC11schemafixed','actual_guard_release':'PENDING_FINALLY'}
vp=C/'MASTER_R21_COMPLETE_R22_FINAL_COORDINATION_AUDIT_20261011.json';assert not vp.exists();write(vp,proof)
t.update(status='IN_PROGRESS',ack_verified=True,ack_sha256=proof['ACK_sha256'],ack_observed_at=at,updated_at=at);b['updated_at']=at;write(bp,b)
c.update(a_status='R22_EXPLICIT_DECLARATION_IN_PROGRESS_ACK_VERIFIED',sol_latest_receipt_notice=notice,last_sol_cursor=sn['cursor'],sol_status='R21_DISPOSED_RECEIPT_ONLY_'+sn['thread']['status']['type'].upper(),latest_coordination_audit=str(vp),updated_at=at);c['a_latest_delivery'].update(status='SENT_ACK_VERIFIED_IN_PROGRESS',ack=ack,ack_sha256=proof['ACK_sha256'],ack_observed_at=at);write(cp,c)
s=read(H/'DISPATCHER_STATE.json');s['endpoints']['a'].update(ack_verified=True,execution_phase='IN_PROGRESS');s['endpoints']['sol'].update(execution_phase=c['sol_status'],current_runtime_idle_verified=sn['thread']['status']['type']=='idle',last_runtime_observation_cursor=sn['cursor']);s['updated_at']=at;write(H/'DISPATCHER_STATE.json',s)
event(dict(proof,event_id=t['dispatch_id']+'-ACK-FINAL-AUDIT',type='R22_IDENTITY_MATCHED_ACK_AND_COORDINATION_AUDIT',proof_path=str(vp),proof_sha256=sha(vp)))
event(dict(notice,event_id='MASTER-SOL-R21-DISPOSITION-NOTICE-20261011-01',proof_path=str(vp),proof_sha256=sha(vp)))
para=f'\n\n## LOCAL-R22-ACK-VERIFIED-CURRENT — {at}\nA{t["dispatch_id"]}/WP_ENGINE_GATE05_R22_EXPLICIT_DECLARATION/envelope25 identitymatchedACK ACKNOWLEDGED/taskIN_PROGRESS;actual prioroneCU SENT unchanged/no resend. ACK timestamp producer selfreport,Masterobservedtime/UI proof controls. SameactualhourlyACTIVE60min173charcorrecttarget;R21UTCscopedCLOSED/fresh245PASS0FAIL each,fullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. OriginalSol R21dispositionreceipt-only actual{sn["thread"]["status"]["type"]}/cursor{sn["revision"]},newQA none,awaitnextfrozenR22candidate. Proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'A':'SENT_ACK_VERIFIED_IN_PROGRESS','Sol_receipt':sn['thread']['status']['type'],'UTC_defect':'CLOSED_NARROW','monitor':'ACTIVE60MIN','new_QA':False,'Foundation':'HOLD'}))
