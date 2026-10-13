from pathlib import Path
import json,datetime,hashlib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cpath=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bpath=R/'Dispatcher/MASTER_A_TASKS.json';c=read(cpath);b=read(bpath);t=b['tasks'][-1];T=Path(t['instruction_path']).parent
assert t['dispatch_id'].endswith('befc4fba') and t['status']=='PREPARED_NOT_SENT' and c['active_operation']['dispatch_id']==t['dispatch_id']
d=json.loads(read(T/'MASTER_UI_PREDRAFT_TOOL.json')['content'][0]['text']);assert d['exact_message']==t['exact_message'] and d['exact_message'] in d['draft']['tree'] and 'WarEconomy 컨텍스트 복구 및 수행' in d['pre']['tree'] and 'Working' not in d['pre']['tree'] and 'Cancel' not in d['pre']['tree']
assert '단추 (disabled) Send message' in d['pre']['tree'] and '단추 Send message' in d['draft']['tree']
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c['active_operation'].update(status='SUBMIT_ATTEMPT_DELIVERY_UNCERTAIN',unknown_delivery=True,attempt_started_at=at,predraft_proof=str(T/'MASTER_UI_PREDRAFT_TOOL.json'))
t.update(status='DELIVERY_UNCERTAIN_SUBMIT_ATTEMPT',delivery_status='UNKNOWN_PENDING_ACTUAL_OBSERVATION',submission_attempts=1,submission_attempt_at=at)
write(cpath,c);write(bpath,b)
e={'at':at,'event_id':t['dispatch_id']+'-ONE-SUBMIT-ATTEMPT','dispatch_id':t['dispatch_id'],'type':'R18_UI_SUBMIT_ATTEMPT_UNKNOWN_UNTIL_OBSERVED','one_send_planned':True,'no_retry_without_observation':True}
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e)+'\n')
print('R18_SUBMIT_ATTEMPT_RECORDED;NO_SENT_CLAIM')
