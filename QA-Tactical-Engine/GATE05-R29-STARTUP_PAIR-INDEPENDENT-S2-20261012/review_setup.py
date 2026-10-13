from pathlib import Path
import json,hashlib,datetime,uuid,ast,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R29-STARTUP-PAIR-20261012-DIRECT-46f60e2a'
MAN=TASK/'MASTER_GATE05_R29_STARTUP_PAIR_REVIEW_FREEZE_MANIFEST.json'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a'
BASELINE=PKG/'coordination/MASTER_R29_S2_PAIR_QA_PROTECTED_BASELINE_20261012.json'
WP=PKG/'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S2.md'
ADMISSION=PKG/'MASTER_REVIEW_ENGINE_GATE05_R29_STARTUP_PAIR_E1_20261012.md'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
PREP=ROOT/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-PREPARATION-S2-20261012'
CAP=ROOT/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011'
SELECTED=FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
NJ=FROZEN/'scratch/EngineGate05R29StartupPair/Harness/bin/Debug/net472/Newtonsoft.Json.dll'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def preservation():
    for p,e in [(BASELINE,'31AF29450CF7CFB47F0178C2E7182B38BC93118AA1C97CDE2CA20828CF8B3176'),(MAN,'006DE41FCB6EC9C9E183C877BD6E3D5C3FB48047454F4AF3902673C0B08D447E'),(ADMISSION,'935D7C10676E965A8C370F63E3ADF357E9CB63D05D9D8DD381E4EACEEFDDE4FA'),(PREP/'PRE_RUN_EXPECTED_ORACLE.json','7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02')]:assert sha(p)==e,str(p)
    out=[]
    for r in load(BASELINE)['files']:
        p=Path(r['path']);assert p.is_relative_to(ROOT);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p);out.append(v)
    fs=[]
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'];fs.append(v)
    assert len(out)==14348 and len(fs)==132
    assert sha(SELECTED)=='084C58CCD770AF90D2F2AE162FF5456C8CD2F0DB3167AE13394635BF8E567E7A'
    assert sha(SELECTED.with_suffix('.pdb'))=='7E76C8CEE38F98FB5B33639AAFB1AA9B4321D563DD483C35A1469A32229C1F3F'
    assert sha(NJ)=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D'
    return dict(at=now(),protected_unique_paths=14348,protected_files=out,frozen_files=fs,all_matched=True,current_production_rebuild_modify=0,publisher_execution=0,game_native=0)
def identity():
    old=ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py'
    fn=next(n for n in ast.parse(old.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='identity')
    ns=dict(Path=Path,ROOT=ROOT,PKG=PKG,Q=Q,MAN=MAN,FROZEN=FROZEN,ast=ast,struct=struct,uuid=uuid,hashlib=hashlib,sha=sha,load=load,write=write,now=now)
    exec(compile(ast.unparse(fn).replace('R3_LINEAGE.json','R29_FROZEN_LINEAGE.json'),str(old)+'#identity-AST-only','exec'),ns)
    return ns['identity']()
if __name__=='__main__':
    Q.mkdir(parents=True,exist_ok=True)
    write(Q/'PRESERVATION_BEFORE.json',preservation());ids=identity()
    assert ids[0]['mvid']=='5c410658-e435-4ae4-8aa3-d074fbcf4f5d'
    a=dict(schema_version=1,at=now(),wp_id='WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT',wp_revision='S2',delivery_id='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S2-20261012-01',result_id='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S2-20261012-'+uuid.uuid4().hex,status='ACKNOWLEDGED_SCOPED_STATIC_AND_NORMAL_PURE_QA',wp=row(WP),master_admission=row(ADMISSION),baseline=row(BASELINE),frozen_manifest=row(MAN),selected=row(SELECTED),selected_mvid=ids[0]['mvid'],matching_PDB=row(SELECTED.with_suffix('.pdb')),exact_newtonsoft=row(NJ),protected_paths=14348,frozen_files=132,source_PDB_docs_both_modes='4/4',initial_QA_builds_candidate_calls=0,publisher_bootstrap_Awake_native_Process_adverse_calls=0,normal_verdict='PENDING',report_hash='PENDING',manifest_hash='PENDING',completion_hash='PENDING',Foundation='HOLD',native_E2='NOT_RELEASED')
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a)
    print(json.dumps(dict(result_id=a['result_id'],ack=row(Q/'ACK_INITIAL.json'),protected=14348,frozen=132,mvid=ids[0]['mvid'],PDB_documents=[len(i['documents']) for i in ids])))
