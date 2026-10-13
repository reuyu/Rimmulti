from pathlib import Path
import json,hashlib,datetime,sys
Q=Path(__file__).resolve().parent;ROOT=Q.parent.parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006';F=ROOT/'Dispatcher/CANDIDATES/G05R38-10b9846e'
T=F/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e';O=F/'scratch/EngineGate05R38PublisherBoundaries-10b9846e';S=F/'scratch/OperatorStartupPairR29/publish_operator_pair.py'
WP=PKG/'WP_QA_ENGINE_GATE05_R38_PUBLISHER_INDEPENDENT_STATIC_S1.md';BASE=PKG/'coordination/MASTER_R38_INDEPENDENT_STATIC_PROTECTED_BASELINE_20261014.json';MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e/MASTER_GATE05_R38_PUBLISHER_BOUNDARIES_REVIEW_FREEZE_MANIFEST.json'
OLDQ=ROOT/'QA-Tactical-Engine/GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014';ORACLE=ROOT/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013/NORMAL_PUBLISHER_EXPECTATION_ORACLE.json'
CORR=PKG/'MASTER_R37_ORIGINAL_LITERAL_TIMESTAMP_CORRECTION_20261014.md';RAWWIT=PKG/'coordination/MASTER_R37_ORIGINAL_LITERAL_TIMESTAMP_RAW_WITNESS_20261014.json'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R38_Publisher_Independent_Static_S1_20261014.md';DELIVERY='SOL-GATE05-R38-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-01'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(Path(p).read_bytes().decode('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def row(p):p=Path(p).resolve();return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,d):
    p=Path(p);assert p.parent==Q or p==REPORT;assert not p.exists(),str(p);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows):
    out=[]
    for r in rows:
        rr=row(r.get('path',r.get('frozen_path')));assert rr['sha256']==r['sha256'].upper() and rr['bytes']==r['bytes'],rr['path'];out.append(rr)
    return out
def preservation():
    controls=[(WP,'587D050A6F1C19322388D556ACEB0E967F0F793588C5811D41CB719AC3E4F14E'),(BASE,'17DE6797EECAE6CFFEEACB068660354294AE37F6D6804C9CCFA378F87C485682'),(MAN,'85F08534BD3BD47258A8AC3A247438702FB318EA7F298C952B452C2464AF99DD'),(S,'940CF77220C272D117CDBC278B64858EFB3077267141CC548A0105B47D6E1306')]
    for p,h in controls:assert sha(p)==h,str(p)
    a=check(load(BASE)['files']);b=check(load(MAN)['files']);assert len(a)==19676 and len(b)==42
    return dict(at=now(),protected_files=a,frozen_files=b,controls=[row(p) for p,h in controls],all_match=True)
