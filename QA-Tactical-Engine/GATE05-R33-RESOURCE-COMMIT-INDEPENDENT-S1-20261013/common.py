from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R33-d19c64a5';FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5'
MAN=TASK/'MASTER_GATE05_R33_RESOURCE_COMMIT_REVIEW_FREEZE_MANIFEST.json'
WP=PKG/'WP_QA_ENGINE_GATE05_R33_RESOURCE_COMMIT_INDEPENDENT_S1.md';BASELINE=PKG/'coordination/MASTER_R33_INDEPENDENT_QA_PROTECTED_BASELINE_20261013.json'
SUP=PKG/'coordination/MASTER_R33_INDEPENDENT_QA_RELEASE_SUPPLEMENT_20261013.json'
BINDING=PKG/'coordination/MASTER_R33_FRESH_QA_ORACLE_TEMPLATE_BINDING_20261013.json'
HELPERS=PKG/'coordination/MASTER_R33_OUTSIDE_OWNED_HELPER_DISCOVERY_20261013.json'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
NJ=ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/EngineGate05R29StartupPair/Harness/bin/Debug/net472/Newtonsoft.Json.dll'
OLD=ROOT/'QA-Tactical-Engine/GATE05-R32-CUSTODY-INDEPENDENT-S1-20261013'
DELIVERY='SOL-GATE05-R33-RESOURCE-COMMIT-INDEPENDENT-S1-20261013-01'
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
    out=[]
    for r in rows:
        p=Path(r[key]);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r[sizekey],str(p);out.append(v)
    return out
def preservation():
    assert sha(WP)=='93510A55A610FC62B7B74FB8F5A06B3A0D7E8BF9ED222BED71D2A18B1FA7801C'
    assert sha(BASELINE)=='23202D7DECB3C5E3D0D03286580158D5A4FFBF727125A63C056C6FA777DBFE50'
    assert sha(SUP)=='D144768BE14438AC8EDFB4EDC92F574503A78D1289D46A8392954F9649B40A67'
    assert sha(MAN)=='176AC1C3EF7F700BD105699B7A69147977F15ECD51FD9979DF0CF35A0391FC29'
    s=load(SUP);check([s[k] for k in ['preparation_review','preparation_proof','additional_protected_manifest','existing_wp','existing_baseline']])
    a=check(load(BASELINE)['files']);f=check(load(MAN)['files'],'frozen_path');terminal=check(load(Path(s['additional_protected_manifest']['path']))['files']);helpers=check(load(HELPERS)['files'])
    assert len(a)==17099 and len(f)==71 and len(terminal)==54 and len(helpers)==6
    return dict(at=now(),protected_files=a,frozen_files=f,prep_terminal_files=terminal,outside_helper_files=helpers,protected_count=17099,frozen_count=71,terminal_count=54,helpers_count=6,all_matched=True)
