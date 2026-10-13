from pathlib import Path
import json,sys,datetime,re
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c=read(cp)
if sys.argv[1]=='progress':
 tool=C/'MASTER_R18_QA_CURRENT_PROGRESS_SNAPSHOT_20261010.json';s=json.loads(read(tool)['content'][0]['text'])['polls'][0]
 assert s['thread']['status']['type']=='active' and s['latestTurn']['status']=='inProgress' and s['latestTurn']['id']==c['sol_current_delivery']['actual_snapshot']['latestTurn']['id']
 c.update(last_sol_cursor=s['cursor'],sol_last_observation={'at':at,'path':str(tool),'thread_status':'ACTIVE_IN_PROGRESS','turn_id':s['latestTurn']['id'],'cursor':s['cursor'],'explicit_ACK':'PENDING_SEPARATE_IDENTITY_PROOF'},updated_at=at);write(cp,c)
 stp=H/'DISPATCHER_STATE.json';st=read(stp);st['endpoints']['sol']['last_runtime_observation_cursor']=s['cursor'];st['updated_at']=at;write(stp,st)
 print('CURRENT_SOL_ACTIVE_CURSOR114_ACK_PENDING')
elif sys.argv[1]=='released':
 q=C/'MASTER_R18_HEARTBEAT_GUARD_FINALLY_RELEASE_20261010.json';r=read(q)
 # Preserve raw PTY proof. VT line-wrap control codes can split/duplicate characters;
 # extract only unbroken terminal values, never rewrite the original transcript.
 raw=r['actual_release_tool']['output']
 assert '"status": "RELEASED"' in raw and '"run_id": "MASTER-HEARTBEAT-R18-20261010T063748Z-01"' in raw
 assert re.search(r'id"\s*:\s*11096\b',raw)
 release_time=re.search(r'"released_at"\s*:\s*"([^"]+)"',raw).group(1)
 actual={'status':'RELEASED','run_id':'MASTER-HEARTBEAT-R18-20261010T063748Z-01','pid':11096,'released_at':release_time}
 assert actual['run_id']=='MASTER-HEARTBEAT-R18-20261010T063748Z-01' and actual['pid']==11096 and r['actual_release_tool'].get('exit_code')==0
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',release_proof_path=str(q),released_at=actual.get('released_at'),all_child_commands_completed_before_release=True);c['updated_at']=at;write(cp,c)
 dest=C/'MASTER_R18_TERMINAL_QA_SENT_COORDINATION_AUDIT_20261010.json';audit=read(dest);audit.update(actual_guard_finally_release='RELEASED_HELPER_EXIT0',release_proof=str(q),last_progress_cursor=c['last_sol_cursor']);write(dest,audit)
 event={'at':at,'event_id':'MASTER-R18-HEARTBEAT-GUARD-RELEASE-20261010-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':actual['run_id'],'pid':11096,'proof':str(q),'all_child_commands_completed_before_release':True}
 for f in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with f.open('a',encoding='utf8') as out:out.write(json.dumps(event)+'\n')
 print('ACTUAL_GUARD_RELEASE_PROOF_RECORDED_EXIT0')
else:raise ValueError(sys.argv[1])

