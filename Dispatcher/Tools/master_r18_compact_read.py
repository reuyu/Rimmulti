from pathlib import Path
import json
R=Path.cwd();H=R/'docs/WarEconomy_Master_Handoff_20261006';p=json.loads((H/'coordination/MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_E1_VERIFICATION_20261010.json').read_text(encoding='utf-8-sig'))
print(json.dumps({k:v for k,v in p.items() if not isinstance(v,(dict,list))},indent=2))
fm=json.loads(Path(p['frozen_manifest']).read_text(encoding='utf-8-sig'))
print(json.dumps(fm['files'][:4],indent=2))
c=json.loads((R/'Dispatcher/MASTER_COMMUNICATION_STATE.json').read_text(encoding='utf-8-sig'))
print(json.dumps({k:v for k,v in c.items() if k in ['active_operation','a_status','sol_status','last_sol_cursor','sol_current_wp','sol_current_attempt_id','master_monitor_automation']},indent=2))

