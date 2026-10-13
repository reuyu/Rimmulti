from pathlib import Path
import json,hashlib,datetime,sys,os,stat
Q=Path(__file__).absolute().parent;ROOT=Q.parent.parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006';CO=PKG/'coordination'
WP=PKG/'WP_QA_ENGINE_GATE05_R38_PUBLISHER_NORMAL6_S1.md';ADMIT=CO/'MASTER_R38_NORMAL6_EXACT_CANDIDATE_ADMISSION_20261014.json';EXPECTED=CO/'MASTER_R38_NORMAL6_PREFROZEN_EXPECTED_ORACLE_20261014.json';BASE=CO/'MASTER_R38_NORMAL6_PROTECTED_BASELINE_20261014.json'
S=ROOT/'Dispatcher/CANDIDATES/G05R38-10b9846e/scratch/OperatorStartupPairR29/publish_operator_pair.py';MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e/MASTER_GATE05_R38_PUBLISHER_BOUNDARIES_REVIEW_FREEZE_MANIFEST.json'
OLDQ=ROOT/'QA-Tactical-Engine/GATE05-R38-PUBLISHER-INDEPENDENT-STATIC-S1-20261014';ORIGINAL=ROOT/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013/NORMAL_PUBLISHER_EXPECTATION_ORACLE.json'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R38_Publisher_Normal6_S1_20261014.md';DELIVERY='SOL-GATE05-R38-PUBLISHER-NORMAL6-S1-20261014-01';EXE=Path('C:/Users/user/anaconda3/python.exe')
PINS=[(WP,'F7A36F6F091CC6AC0A45F456F97C2F72415DE4D89BEC652F6A553243AF9E400A'),(ADMIT,'2044BAFFAB9BC46521E3F9855724276BB40CA0739006084ADF59F813047177AE'),(EXPECTED,'C2D667CC372D605FDEC680B5663A62636DEF81DFCD6133689055C2FB86D343CB'),(BASE,'7DC67B8B9AAC482C30ECCD78999B8E2A6F65DBF12F58AE44BC17D62380F2A90E'),(S,'940CF77220C272D117CDBC278B64858EFB3077267141CC548A0105B47D6E1306'),(MAN,'85F08534BD3BD47258A8AC3A247438702FB318EA7F298C952B452C2464AF99DD'),(EXE,'388FE2CFFDA8A134E7D7DC4E978F7C478857ECE6B69694DAECBED25E51EC633A')]
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(Path(p).read_bytes().decode('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def row(p):p=Path(p).absolute();return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,d):
    p=Path(p).absolute();assert p.is_relative_to(Q) or p==REPORT
    with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows):
    actual=[]
    for r in rows:
        a=row(r.get('path',r.get('frozen_path')));assert a['sha256']==r['sha256'].upper() and a['bytes']==r['bytes'],a['path'];actual.append(a)
    return actual
def controls():
    for p,h in PINS:assert sha(p)==h,str(p)
    assert EXE.stat().st_size==104264 and S.stat().st_size==43666
def statrow(p):
    s=os.lstat(p);a=getattr(s,'st_file_attributes',None);assert isinstance(a,int) and not isinstance(a,bool) and not a&1024 and not stat.S_ISLNK(s.st_mode),str(p)
    return dict(path=str(p),dev=s.st_dev,ino=s.st_ino,mode=s.st_mode,size=s.st_size,mtime_ns=s.st_mtime_ns,attributes=a,nlink=s.st_nlink)
def ancestry(p,new_leaf=False,leaf_dir=False):
    p=Path(p);assert p.is_absolute() and p.drive.upper()=='C:' and '..' not in p.parts
    parts=[Path(p.anchor)];cur=parts[0]
    for part in p.parts[1:]:cur=cur/part;parts.append(cur)
    rr=[]
    for i,path in enumerate(parts):
        if new_leaf and i==len(parts)-1:
            try:os.lstat(path)
            except FileNotFoundError:rr.append(dict(path=str(path),status='EXACT_NEW_LEAF_ABSENT'));continue
            raise AssertionError('Expected absent leaf: '+str(path))
        r=statrow(path);assert stat.S_ISDIR(r['mode']) if i<len(parts)-1 or leaf_dir else stat.S_ISREG(r['mode']);rr.append(r)
    return rr
def preservation():
    controls();a=check(load(BASE)['files']);b=check(load(MAN)['files']);assert len(a)==19785 and len(b)==42
    return dict(at=now(),protected_files=a,frozen_files=b,controls=[row(p) for p,h in PINS],all_match=True)
def literal(r):
    b=r['utf8_text'].encode('utf-8');assert b.hex().upper()==r['hex'] and hashlib.sha256(b).hexdigest().upper()==r['sha256'] and len(b)==r['bytes'];return b
