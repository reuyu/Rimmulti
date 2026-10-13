from pathlib import Path
import json,hashlib,datetime
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent
PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R31-LIFECYCLE-20261012-DIRECT-b8d47a10'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R31-b8d47a10'
FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R31-LIFECYCLE-20261012-DIRECT-b8d47a10'
MAN=TASK/'MASTER_GATE05_R31_LIFECYCLE_REVIEW_FREEZE_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R31_STATIC_QA_PROTECTED_BASELINE_20261012.json'
WP=PKG/'WP_QA_ENGINE_GATE05_R31_LIFECYCLE_INDEPENDENT_STATIC_S1.md'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DELIVERY='SOL-GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012-01'
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
        p=Path(r[path_key]);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p);result.append(v)
    return result
def preservation():
    assert sha(BASELINE)=='6BB19CD4A32ADE5F013A317C2741B712102C800BF5C5CD1212D1E8D3F96DA425'
    assert sha(MAN)=='F8770090C7CB2D03077A9A7336D13F7F9F61E9F0D2DABB442BA62669B24EA3E4'
    protected=verify(load(BASELINE)['files']);frozen=verify(load(MAN)['files'],'frozen_path')
    assert len(protected)==15854 and len(frozen)==131
    return dict(at=now(),protected_files=protected,frozen_files=frozen,protected_unique_paths=15854,frozen_count=131,all_matched=True,candidate_compiler_runner_native_calls=0)
