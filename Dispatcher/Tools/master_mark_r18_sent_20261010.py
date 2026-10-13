from pathlib import Path
import json,datetime,hashlib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';c=read(cp);b=read(bp);t=b['tasks'][-1];T=Path(t['instruction_path']).parent;p=T/'MASTER_UI_SUBMISSION_PROOF.json';proof=read(p)
assert t['dispatch_id'].endswith('befc4fba') and t['submission_attempts']==1 and proof['message']==t['exact_message'] and all(proof[k] for k in ['actual_new_message_matches','composer_cleared','one_send_action','working_cancel_observed'])
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();t.update(status='SENT_IN_PROGRESS_ACK_PENDING',delivery_status='SENT',sent_at=at,submission_proof=str(p),submission_proof_sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper())
c['active_operation'].update(status='ACTUAL_SENT_MONITOR_RESUME_PENDING',unknown_delivery=False);c.update(a_current_attempt_id=t['dispatch_id'],a_status='R18_ACTUAL_SENT_IN_PROGRESS_ACK_PENDING',a_result_completion_path=t['completion_path'],updated_at=at);write(cp,c);write(bp,b)
e={'at':at,'event_id':t['dispatch_id']+'-ACTUAL-SENT','type':'A_R18_ACTUAL_DIRECT_CU_SENT_WORKING','dispatch_id':t['dispatch_id'],'proof':str(p),'one_submit':True,'ack_pending':True,'monitor_resume_pending':True}
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e)+'\n')
print('R18_ACTUAL_SENT;ONE_SUBMIT;MONITOR_RESUME_PENDING')
