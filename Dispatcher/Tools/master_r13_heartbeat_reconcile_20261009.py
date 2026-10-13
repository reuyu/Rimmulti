from pathlib import Path
import json,sys,datetime
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=H/'coordination'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1]
assert t['dispatch_id'].endswith('2661a749')
baseline=Path(c['active_operation']['baseline_path']);d=read(baseline);errors=[]
for f in d['files']:
 p=Path(f['path'])
 if not p.exists() or ck.digest(p)!=f['sha256'] or p.stat().st_size!=f.get('bytes',f.get('size')):errors.append(f['path'])
assert not errors,errors
assert len(d['files'])==5901
a=ck.inspect();pres=ck.inspect_preservation(t)
proof={'at':at,'run_id':'MASTER-R13-HEARTBEAT-20261009T110931Z-01','guard_session':32118,'guard_pid':864,'old_guard':{'run_id':'MASTER-SOL-R12-INDEPENDENT-COMPLETE-20261009-01','session':85079,'pid':1956,'release_reason':'TTL_EXPIRED','released_at':'2026-10-09T17:36:40.395400+09:00','full_interruption_coverage_verified':False},'heartbeat_messages_received':['2026-10-09T09:07:30.216Z','2026-10-09T10:06:00.952Z','2026-10-09T11:09:31.918Z'],'earlier_separate_guarded_handlers_verified':False,'actual_guarded_handler_at':at,'baseline_path':str(baseline),'baseline_sha256':ck.digest(baseline),'protected_unique_paths':5901,'protected_errors':errors,'a_result_check':a,'preservation':pres,'a_r13_no_resend':True,'sol_r13_still_prepared_not_sent':True}
out=Q/'MASTER_R13_HEARTBEAT_RECONCILIATION_20261009.json';assert not out.exists();write(out,proof)
c['active_operation'].update(guard_run=proof['run_id'],guard_session=32118,guard_pid=864,reconciliation_proof=str(out));c.update(a_current_attempt_id=t['dispatch_id'],a_result_completion_path=t['completion_path'],a_status='R13_TERMINAL_OBSERVED_REVIEW_PENDING',updated_at=at)
c['master_monitor_automation'].update(future_run_after_engine_r13_resume_observed=True,first_run_after_engine_r13_resume_observed_at='2026-10-09T09:07:30.216Z',latest_r13_trigger_received_at='2026-10-09T11:09:31.918Z',actual_r13_guarded_handler_at=at,earlier_r13_handler_execution_unverified=True)
c['last_monitor_run']={'run_id':proof['run_id'],'guard_session':32118,'guard_pid':864,'at':at,'status':'R13_TERMINAL_REVIEW_PENDING_SOL_PREP_DISPATCH_PENDING','release_pending':True};write(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
with (R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':at,'type':'R13_HEARTBEAT_RECONCILIATION','proof':str(out),'proof_sha256':ck.digest(out),'old_lease_expired':True,'a_r13_terminal_observed':True,'sol_prep_delivery':'NOT_SENT','protected':5901})+'\n')
print(json.dumps({'baseline':5901,'baseline_sha':ck.digest(baseline),'a_status':a.get('status'),'a_errors':a.get('errors'),'preservation_counts':{k:v for k,v in pres.items() if k.endswith('count')},'preservation_errors':pres.get('preservation_errors'),'proof':str(out)}))
