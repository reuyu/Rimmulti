from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
WP=PKG/'WP_QA_ENGINE_GATE05_R33_RESOURCE_NATIVE_PREPARATION_S1.md'
BASELINE=PKG/'coordination/MASTER_R33_RESOURCE_COMMIT_PROTECTED_BASELINE_20261013.json'
EXTRA=PKG/'coordination/MASTER_R32_OUTSIDE_OWNED_HELPER_DISCOVERY_20261013.json'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5'
SCOPE=TASK/'MASTER_R33_AUTHORIZED_SOURCE_SCOPE.json'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R32-64ad38e2'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R32-CUSTODY-20261012-DIRECT-64ad38e2/MASTER_GATE05_R32_CUSTODY_REVIEW_FREEZE_MANIFEST.json'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DELIVERY='SOL-GATE05-R33-RESOURCE-NATIVE-PREP-S1-20261013-01'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_bytes().decode('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert not p.exists(),str(p);p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows,key='path'):
    out=[]
    for r in rows:
        p=Path(r[key]);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p);out.append(v)
    return out
def preservation():
    assert sha(BASELINE)=='DAE9DE6DE5AA170BF62476412EE5C0F4078357DE074164BEDC66F9894DBC4D1E'
    assert sha(EXTRA)=='74C4785667B26AFEC041298DFC5E21178AF645C495B6A343E4CC6E56FAF6EF2F'
    assert sha(MAN)=='F5EDD5DCBC021407B3598DEBCF80276F39C158EC38FABD37D10AD15E6098E6BF'
    scope=load(SCOPE);denied={p.lower() for p in scope['allowed_mutable_paths']+scope['allowed_generated_intermediate_paths']};assert len(denied)==22
    rows=load(BASELINE)['files'];assert len(rows)==16929 and not any(r['path'].lower() in denied for r in rows)
    extras=load(EXTRA)['files'];assert len(extras)==5 and not any(r['path'].lower() in denied for r in extras)
    frozen=load(MAN)['files'];assert len(frozen)==64
    return dict(at=now(),protected_files=check(rows),additional_helper_files=check(extras),frozen_files=check(frozen,'frozen_path'),protected_count=16929,additional_count=5,frozen_count=64,mutable22_not_read_hashed=True,all_matched=True)
