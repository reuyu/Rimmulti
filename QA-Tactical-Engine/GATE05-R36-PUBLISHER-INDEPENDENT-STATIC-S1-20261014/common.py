from pathlib import Path
import json,hashlib,datetime,sys
Q=Path(__file__).resolve().parent;ROOT=Q.parent.parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
F=ROOT/'Dispatcher/CANDIDATES/G05R36-d2d6556b';T=F/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b';O=F/'scratch/EngineGate05R36PublisherContract-d2d6556b';S=F/'scratch/OperatorStartupPairR29/publish_operator_pair.py'
WP=PKG/'WP_QA_ENGINE_GATE05_R36_PUBLISHER_INDEPENDENT_STATIC_S1.md';BASE=PKG/'coordination/MASTER_R36_INDEPENDENT_STATIC_PROTECTED_BASELINE_20261014.json';MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b/MASTER_GATE05_R36_PUBLISHER_CONTRACT_REVIEW_FREEZE_MANIFEST.json'
PREP=ROOT/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013';ORACLE=PREP/'NORMAL_PUBLISHER_EXPECTATION_ORACLE.json'
DELIVERY='SOL-GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-01';VERDICT='INDEPENDENT_R36_CONFIG_CLI_SOURCE_GAINS_RECEIPT_ANCESTRY_TIME_ORACLE_PROVENANCE_REVISION_REQUIRED_PUBLICATION_NATIVE_NOT_ADMITTED'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R36_Publisher_Independent_Static_S1_20261014.md'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def row(p):p=Path(p).resolve();return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def load(p):return json.loads(Path(p).read_bytes().decode('utf-8-sig'))
def write(p,d):
    p=Path(p);assert p.parent==Q or p==REPORT;assert not p.exists(),str(p)
    p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows):
    out=[]
    for r in rows:
        rr=row(r.get('path',r.get('frozen_path')));assert rr['sha256']==r['sha256'].upper() and rr['bytes']==r['bytes'],rr['path'];out.append(rr)
    return out
def preserve():
    expected=[(WP,'A0BBF3587CFD0050F6B9FE030410C789AEB5036EAF2D78C1FEAF624582E0AF00'),(BASE,'4BD2C7789721BBA4DBB61A8F57B289837B9496CB104FA83CB5BFA70CA967554E'),(MAN,'3F60458A4303F0B9CB8F1C0003D3E0E39E37F80E002B5FA06CACA4A3D197D130'),(S,'F60CBC184C6627F0FE15A5A904D0C45A026E20C5138973066BB8174DD8FBFD3F')]
    for p,h in expected:assert sha(p)==h,str(p)
    protected=check(load(BASE)['files']);frozen=check(load(MAN)['files']);assert len(protected)==19380 and len(frozen)==43
    return dict(at=now(),protected_files=protected,frozen_files=frozen,controls=[row(p) for p,h in expected],all_match=True)
