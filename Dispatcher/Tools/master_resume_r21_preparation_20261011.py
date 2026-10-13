from pathlib import Path
import json,datetime,hashlib,copy,uuid,sys,tomllib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
Q=R/'QA-Tactical-Engine/GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
vp=C/'MASTER_SOL_R20_TRUSTED_STARTUP_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json';v=read(vp)
assert v['verification_status']=='MASTER_DISPOSED'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);old=b['tasks'][-1]
assert c['active_operation'] is None and old['dispatch_id'].endswith('e35ff656')
review=Path(v['review_path']);assert sha(review)==v['review_sha256']
event({'at':at,'event_id':'MASTER-R21-PREPARATION-LF-RECOVERY-20261011-01','type':'MASTER_METADATA_PREPARATION_RECONCILIATION','detail':'First metadata-only preparation expected CRLF delimiter but actual Worker LF; R20 disposition completed before failure. Resume unregistered same unique R21 directory after correcting read-only byte delimiter. No production/QA source,runner,oracle,evidence modified/executed; no delivery attempted.'})
source=(R/'Dispatcher/Tools/master_dispose_r20_prepare_r21_20261011.py').read_text(encoding='utf8')
tail=source[source.index("dispatch='WE-A-ENGINE-GATE05-R21-"):]
first=tail.splitlines()[0]
tail=tail.replace(first,"dispatch='WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586';T=R/'Dispatcher/A_TASKS'/dispatch;assert T.exists() and not list(T.iterdir())",1)
exec(compile(tail,str(R/'Dispatcher/Tools/master_dispose_r20_prepare_r21_20261011.py')+'-resume','exec'))
