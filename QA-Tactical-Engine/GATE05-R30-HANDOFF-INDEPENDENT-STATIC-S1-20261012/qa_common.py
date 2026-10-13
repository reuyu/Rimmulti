from pathlib import Path
import json,hashlib,datetime
ROOT=Path(r'C:\Users\user\Desktop\RimMulti')
Q=Path(__file__).resolve().parent
PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R30-HANDOFF-20261012-DIRECT-16ce928f'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R30-16ce928f'
MAN=TASK/'MASTER_GATE05_R30_HANDOFF_REVIEW_FREEZE_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R30_STATIC_QA_PROTECTED_BASELINE_20261012.json'
WP=PKG/'WP_QA_ENGINE_GATE05_R30_HANDOFF_INDEPENDENT_STATIC_S1.md'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
DELIVERY='SOL-GATE05-R30-HANDOFF-INDEPENDENT-STATIC-S1-20261012-01'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def verify(rows,path_key='path'):
    result=[]
    for r in rows:
        p=Path(r[path_key]);v=row(p)
        assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p)
        result.append(v)
    return result
def preservation():
    assert sha(BASELINE)=='29AD8B2493A67F9A98A39671851CF7945D903C9CBBC813790273741FE3D8DD92'
    assert sha(MAN)=='D5948C6EAFE071AC723FF814708CE2D6DD62E55FFB1039D8946099E0992B7B2C'
    protected=verify(load(BASELINE)['files']);frozen=verify(load(MAN)['files'],'frozen_path')
    assert len(protected)==15549 and len(frozen)==128
    return dict(at=now(),protected_files=protected,frozen_files=frozen,protected_unique_paths=15549,frozen_count=128,all_matched=True,candidate_execution_build=0)
