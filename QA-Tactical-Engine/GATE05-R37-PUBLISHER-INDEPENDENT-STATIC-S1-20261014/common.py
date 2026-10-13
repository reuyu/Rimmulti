from pathlib import Path
import json,hashlib,datetime,sys
Q=Path(__file__).resolve().parent;ROOT=Q.parent.parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006';F=ROOT/'Dispatcher/CANDIDATES/G05R37-de39916a'
T=F/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a';O=F/'scratch/EngineGate05R37PublisherFinal-de39916a';S=F/'scratch/OperatorStartupPairR29/publish_operator_pair.py'
WP=PKG/'WP_QA_ENGINE_GATE05_R37_PUBLISHER_INDEPENDENT_STATIC_S1.md';BASE=PKG/'coordination/MASTER_R37_INDEPENDENT_STATIC_PROTECTED_BASELINE_20261014.json';MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a/MASTER_GATE05_R37_PUBLISHER_FINAL_REVIEW_FREEZE_MANIFEST.json'
OLDQ=ROOT/'QA-Tactical-Engine/GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014';ORACLE=ROOT/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013/NORMAL_PUBLISHER_EXPECTATION_ORACLE.json'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R37_Publisher_Independent_Static_S1_20261014.md';DELIVERY='SOL-GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-01'
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
    controls=[(WP,'A755C63AB5AFF3C7ED6690A8BF5C73B42171765D03D7A06490ACDE1DB4F00A26'),(BASE,'79A53CB58F6CDE28E688705B6642DCC923C62FB498BEB6A50E4D04505B357618'),(MAN,'1916E40664113EDD90A1679336E37A6C6101C0184326C47ECF0B6734DA5119FC'),(S,'8F31D69A26A364BF727ABD029E096C0416B3C7B6BA54AC29A6A6E246FF537FD9')]
    for p,h in controls:assert sha(p)==h,str(p)
    a=check(load(BASE)['files']);b=check(load(MAN)['files']);assert len(a)==19530 and len(b)==42
    return dict(at=now(),protected_files=a,frozen_files=b,controls=[row(p) for p,h in controls],all_match=True)
