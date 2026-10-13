from pathlib import Path
import json,sys,hashlib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert c['active_operation'] is None and c['a_current_attempt_id']==t['dispatch_id']
p=Path(t['completion_path']);exists=p.exists()
print(json.dumps({'A_dispatch':t['dispatch_id'],'A_status':t['status'],'A_COMPLETION_exists':exists,'active_operation':c['active_operation'],'sol_status':c['sol_status'],'last_cursor':c['last_sol_cursor'],'monitor_status':c['master_monitor_automation']['status']},ensure_ascii=True))
if exists:
 d=read(p);print(json.dumps(d,ensure_ascii=False,indent=2))
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t)
out=Path(t['instruction_path']).parent/'MASTER_R19_HEARTBEAT_PRESERVATION_20261010T082750Z.json';assert not out.exists();out.write_text(json.dumps(pres,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'preservation_errors':pres['preservation_errors'],'counts':{k:len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']},'proof':str(out)},ensure_ascii=True))

