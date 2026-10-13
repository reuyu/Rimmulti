from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
OLD=ROOT/'QA-Tactical-Engine/GATE05-R34-ROLLBACK-INDEPENDENT-S1-20261013';NATIVE_PREP=ROOT/'QA-Tactical-Engine/GATE05-R33-RESOURCE-NATIVE-PREPARATION-S1-20261013'
WP=PKG/'WP_QA_ENGINE_GATE05_R35_PUBLISHER_PREPARATION_S1.md';BASE=PKG/'coordination/MASTER_R35_PUBLISHER_PROTECTED_BASELINE_20261013.json';EXTRA=PKG/'coordination/MASTER_R34_LATE_OUTSIDE_HELPER_DISCOVERY_20261013.json'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c/MASTER_GATE05_R34_ROLLBACK_REVIEW_FREEZE_MANIFEST.json';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R34-a4d6866c'
PUBLISHER=FROZEN/'scratch/OperatorStartupPairR29/publish_operator_pair.py';SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
SCOPE=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e/MASTER_R35_AUTHORIZED_SOURCE_SCOPE.json'
PAIR=ROOT/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012/PRE_RUN_EXPECTED_ORACLE.json';COMBINED=ROOT/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012/NORMAL_EXPECTED_ORACLE.json'
DELIVERY='SOL-GATE05-R35-PUBLISHER-PREP-S1-20261013-01';VERDICT='QA_PREPARATION_ONLY_R35_NOT_READ_NOT_REVIEWED_PUBLICATION_NATIVE_NOT_ADMITTED'
MUTABLE=ROOT/'scratch/OperatorStartupPairR29/publish_operator_pair.py';ACTIVE=ROOT/'scratch/EngineGate05R35Publisher-16a25a7e'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def permitted(p):
    s=str(p.absolute()).replace('/','\\').lower();assert s!=str(MUTABLE).lower() and not s.startswith(str(ACTIVE).lower()+'\\'),str(p)
    task=str(SCOPE.parent).lower()+'\\';assert not s.startswith(task) or s==str(SCOPE).lower(),str(p)
    return p
def load(p):return json.loads(permitted(p).read_bytes().decode('utf-8-sig'))
def sha(p):
    permitted(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert p.is_relative_to(Q) and not p.exists(),str(p);p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows,key='path'):
    out=[]
    for r in rows:
        p=permitted(Path(r[key]));v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p);out.append(v)
    return out
def preservation():
    assert sha(WP)=='67CE8201AEB86329654371A16E68EF3F1884090CB999475F70FE62272A230DDB'
    assert sha(BASE)=='E5BA3D340EEED15DE64C5C77F7E6258D23F9CF06D482712657780FA794D75735';assert sha(EXTRA)=='76E1BE93E16E5FE5E5F4E90217D4050D1D8A3E787626F5316D194660893DFA97';assert sha(MAN)=='1CD74A89DAC67524631FA7D0A163CC50626AB386CBA191220A159F9365A87F47'
    rows=load(BASE)['files'];[permitted(Path(r['path'])) for r in rows]
    p=check(rows);e=check(load(EXTRA)['files']);f=check(load(MAN)['files'],'frozen_path');assert len(p)==19103 and len(e)==1 and len(f)==75
    return dict(at=now(),protected_files=p,additive_late_helper=e,frozen_files=f,protected_count=19103,extra_count=1,frozen_count=75,all_matched=True,mutable_R35_read_hash=False)
