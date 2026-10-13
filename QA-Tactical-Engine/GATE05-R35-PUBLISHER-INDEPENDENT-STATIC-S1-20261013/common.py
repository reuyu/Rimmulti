from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
PREP=ROOT/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013'
WP=PKG/'WP_QA_ENGINE_GATE05_R35_PUBLISHER_INDEPENDENT_STATIC_S1.md';BASE=PKG/'coordination/MASTER_R35_PUBLISHER_INDEPENDENT_STATIC_PROTECTED_BASELINE_20261013.json'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e/MASTER_GATE05_R35_PUBLISHER_REVIEW_FREEZE_MANIFEST.json';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R35-16a25a7e';TASKREL='Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e';FT=FROZEN/TASKREL;FO=FROZEN/'scratch/EngineGate05R35Publisher-16a25a7e'
PUBLISHER=FROZEN/'scratch/OperatorStartupPairR29/publish_operator_pair.py';SOURCE=ROOT/'Dispatcher/CANDIDATES/G05R34-a4d6866c/scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DELIVERY='SOL-GATE05-R35-PUBLISHER-INDEPENDENT-STATIC-S1-20261013-01';VERDICT='INDEPENDENT_R35_NONOVERWRITE_SOURCE_GAINS_CONFIG_PATH_CLI_REVISION_REQUIRED_PUBLICATION_NATIVE_NOT_ADMITTED'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_bytes().decode('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert p.is_relative_to(Q) and not p.exists(),str(p);p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows,key='path',sizekey='bytes'):
    out=[]
    for r in rows:
        v=row(Path(r[key]));assert v['sha256']==r['sha256'] and v['bytes']==r[sizekey],r[key];out.append(v)
    return out
def preservation():
    assert sha(WP)=='165023C11FC92E920384B439F250762048C9121E2923EAC5955168251878C738'
    assert sha(BASE)=='0955BDCC8A4AD053A017EE9E214B91E0C70AD22B2D52124BA3EFBE0729734C63'
    assert sha(MAN)=='2E24EB1828DC892B8554D69F1D7A85DDEE57A8FF717533C620A258BF76D6393A'
    a=check(load(BASE)['files']);f=check(load(MAN)['files'],'frozen_path');assert len(a)==19229 and len(f)==34
    return dict(at=now(),protected_files=a,frozen_files=f,protected_count=19229,frozen_count=34,all_matched=True,historical_live_publisher_pointers_not_invoked=True)
