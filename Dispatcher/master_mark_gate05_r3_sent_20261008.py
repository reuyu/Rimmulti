"""Reconcile actual UI submission; never treat a prepared file as delivery."""
from pathlib import Path
import datetime,json,hashlib
ROOT=Path(__file__).resolve().parent.parent;D=ROOT/'Dispatcher';H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
board=read(D/'MASTER_A_TASKS.json');t=next(t for t in board['tasks']if t['dispatch_id']=='WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa')
assert t['status']=='PREPARED_NOT_SENT'
folder=Path(t['instruction_path']).parent;obs=read(folder/'MASTER_UI_SUBMISSION_OBSERVATION.json')
assert any(t['exact_message']in line for line in obs['relevant_accessibility'])
assert any('Working'in line for line in obs['relevant_accessibility']) and any('Cancel'in line for line in obs['relevant_accessibility'])
composer=next(line for line in obs['relevant_accessibility']if 'Message input'in line)
assert 'Value:' not in composer
assert obs['window']['id']==4458672
proof=folder/'MASTER_UI_SUBMISSION_CONFIRMED.json'
record={'at':now,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','actor':'Master','route':'computer-use/Antigravity','window':obs['window'],'conversation':obs['conversation'],'observation_path':str(folder/'MASTER_UI_SUBMISSION_OBSERVATION.json'),'observation_sha256':sha(folder/'MASTER_UI_SUBMISSION_OBSERVATION.json'),'exact_message_sha256':t['exact_message_sha256'],'new_user_message_visible':True,'composer_empty':True,'working_cancel_observed':True,'actual_submission_time_exact':None,'submission_observed_at':obs['observed_at_utc'],'candidate_runtime_verdict':None,'no_resend':True}
write(proof,record)
t.update(status='IN_PROGRESS',delivery_status='SENT',sent_observed_at=now,submission_actor='Master',submission_proof=str(proof),submission_proof_sha256=sha(proof),execution_observation='NEW_USER_MESSAGE_AND_WORKING_UI_OBSERVED',ack_verified=False,updated_at=now)
if Path(t['ack_path']).is_file():
 ack=read(Path(t['ack_path']))
 assert all(ack.get(k)==t[k]for k in ['dispatch_id','wp_id','wp_revision','recipient'])
 t.update(ack_verified=True,ack_sha256=sha(Path(t['ack_path'])),acknowledged_at=ack.get('acknowledged_at'),ack_observed_at=now)
board['updated_at']=now;write(D/'MASTER_A_TASKS.json',board)
state=read(D/'MASTER_COMMUNICATION_STATE.json')
state.update(a_current_attempt_id=t['dispatch_id'],a_pending_dispatch_id=None,a_status='R3_SENT_IN_PROGRESS_ACK_VERIFIED'if t['ack_verified']else'R3_SENT_IN_PROGRESS_ACK_PENDING',a_result_completion_path=t['completion_path'],updated_at=now)
state['active_operation'].update(phase='ACTUAL_SUBMISSION_CONFIRMED_MONITOR_RESUME_PENDING',submission_proof=str(proof))
state['a_last_delivery']={'dispatch_id':t['dispatch_id'],'delivery_status':'SENT','status':'SENT','actor':'Master','observed_at':now,'proof':str(proof),'ack_verified':t['ack_verified'],'resend_allowed':False}
state['a_endpoint_context_status']='CURRENT_CONVERSATION_WARECONOMY_RECOVERY_AND_EXECUTION_VERIFIED'
state['master_monitor_automation']['desired_status']='ACTIVE'
write(D/'MASTER_COMMUNICATION_STATE.json',state)
dispatch=read(H/'DISPATCHER_STATE.json')
dispatch['endpoints']['a'].update(current_wp=t['wp_id'],current_attempt_id=t['dispatch_id'],runtime_delivery_verified=True,current_conversation_status='ACTUAL_R3_NEW_USER_MESSAGE_AND_WORKING',conversation_title=obs['conversation'],execution_phase='IN_PROGRESS',ack_verified=t['ack_verified'],current_runtime_idle_verified=False,latest_delivery_proof=str(proof),last_verified_at=now)
dispatch['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','work_package':t['wp_id'],'revision':t['wp_revision'],'status':'IN_PROGRESS','delivery_status':'SENT','actor':'Master','at':now,'proof':str(proof)})
dispatch['updated_at']=now;write(H/'DISPATCHER_STATE.json',dispatch)
event={'event_id':t['dispatch_id']+'-SENT','at':now,'type':'MASTER_DIRECT_A_R3_SENT','dispatch_id':t['dispatch_id'],'proof':str(proof),'proof_sha256':sha(proof),'status':'SENT_IN_PROGRESS','ack_verified':t['ack_verified'],'scheduler':'RESUME_PENDING','closure_changed':False}
for p in [D/'MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8')as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
delta=f'''\n\n## LOCAL-A-ENGINE-GATE05-R3-SENT — {now}\nActual Master Computer Use submission of {t['dispatch_id']}/WP_ENGINE_GATE05_R3/GATE05-R3 envelope6 confirmed in current WarEconomy 컨텍스트 복구 및 수행. Exact new user message visible,composer cleared,Working/Cancel observed: SENT/IN_PROGRESS,ACK verified={t['ack_verified']}. No duplicate WP/no resend. Candidate runtime verdict remains unobserved;prior R2 rejection and archive/R1/R2/Pipeline/QA protection remain. User-authorized same existing hourly monitor activation pending actual tool/config proof;no new scheduler/QA WP/closure. Proof: {proof}\n'''
for name in ['MASTER_AGENT_DISPATCH_BOARD.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md']:
 with(H/name).open('a',encoding='utf-8')as f:f.write(delta)
with(ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md').open('a',encoding='utf-8')as f:f.write(delta)
print(json.dumps({'status':'SENT_IN_PROGRESS','ack_verified':t['ack_verified'],'proof':str(proof)},ensure_ascii=False))
