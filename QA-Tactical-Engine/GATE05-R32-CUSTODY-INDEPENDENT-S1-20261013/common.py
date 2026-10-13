from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent
PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R32-CUSTODY-20261012-DIRECT-64ad38e2'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R32-64ad38e2'
MAN=TASK/'MASTER_GATE05_R32_CUSTODY_REVIEW_FREEZE_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R32_STATIC_POSITIVE_QA_PROTECTED_BASELINE_20261013.json'
WP=PKG/'WP_QA_ENGINE_GATE05_R32_CUSTODY_INDEPENDENT_S1.md'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
NJ=ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/EngineGate05R29StartupPair/Harness/bin/Debug/net472/Newtonsoft.Json.dll'
BINDING=PKG/'coordination/MASTER_R32_FRESH_QA_ORACLE_TEMPLATE_BINDING_20261013.json'
DELIVERY='SOL-GATE05-R32-CUSTODY-INDEPENDENT-S1-20261013-01'
OLD=ROOT/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_bytes().decode('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows,pathkey='path',sizekey='bytes'):
    result=[]
    for r in rows:
        p=Path(r[pathkey]);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r[sizekey],str(p);result.append(v)
    return result
def preservation():
    assert sha(BASELINE)=='9A1297820ADCD3E7D52B253E73DF8C25A237642F379F63175C8CBF0DD462ABA5'
    assert sha(MAN)=='F5EDD5DCBC021407B3598DEBCF80276F39C158EC38FABD37D10AD15E6098E6BF'
    a=check(load(BASELINE)['files']);b=check(load(MAN)['files'],'frozen_path');assert len(a)==16026 and len(b)==64
    return dict(at=now(),protected_files=a,frozen_files=b,protected_count=16026,frozen_count=64,all_matched=True)
