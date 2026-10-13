from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
OLD=ROOT/'QA-Tactical-Engine/GATE05-R33-RESOURCE-COMMIT-INDEPENDENT-S1-20261013'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R34-a4d6866c';FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c'
MAN=TASK/'MASTER_GATE05_R34_ROLLBACK_REVIEW_FREEZE_MANIFEST.json';BASELINE=PKG/'coordination/MASTER_R34_INDEPENDENT_QA_PROTECTED_BASELINE_20261013.json'
WP=PKG/'WP_QA_ENGINE_GATE05_R34_ROLLBACK_INDEPENDENT_S1.md';BINDING=PKG/'coordination/MASTER_R34_FRESH_QA_ORACLE_TEMPLATE_BINDING_20261013.json'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
NJ=ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/EngineGate05R29StartupPair/Harness/bin/Debug/net472/Newtonsoft.Json.dll'
DELIVERY='SOL-GATE05-R34-ROLLBACK-INDEPENDENT-S1-20261013-01';MVID='7b08d3f4-27de-4685-b61b-8a312708a496';SELECTED_SHA='8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029'
VERDICT='SCOPED_R34_NORMAL_PURE_PAIR_CAPTURE_FULL_TYPED_RAW_COPY_PASS_STATIC_ROLLBACK_SOURCE_GAINS_UNIVERSAL_CLAIMS_UNSUPPORTED_NATIVE_UNTESTED'
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
def check(rows,key='path',sizekey='bytes'):
    actual=[]
    for r in rows:
        v=row(Path(r[key]));assert v['sha256']==r['sha256'] and v['bytes']==r[sizekey],r[key];actual.append(v)
    return actual
def preservation():
    assert sha(WP)=='F3183ED4415082BC4185A8FEF02985A3A7C441BD86BD96C4BE54C095534D23B3'
    assert sha(BASELINE)=='30F78C41BFBD7ED8B4C816DCD5B266F44754FC5DA53915962E7FAAE9A0697ED8'
    assert sha(MAN)=='1CD74A89DAC67524631FA7D0A163CC50626AB386CBA191220A159F9365A87F47'
    p=check(load(BASELINE)['files']);f=check(load(MAN)['files'],'frozen_path');assert len(p)==18163 and len(f)==75
    return dict(at=now(),protected_files=p,frozen_files=f,protected_count=len(p),frozen_count=len(f),all_matched=True)
