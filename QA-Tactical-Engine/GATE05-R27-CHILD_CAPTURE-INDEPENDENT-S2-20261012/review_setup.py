from pathlib import Path
import json,hashlib,datetime,uuid,ast,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=ROOT/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012';PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R27-CHILD-CAPTURE-20261011-DIRECT-cdc223f3';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R27-cdc223f3';MAN=TASK/'MASTER_GATE05_R27_CHILD_CAPTURE_REVIEW_FREEZE_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R27_S2_CORRECTED_LOADER_PROTECTED_BASELINE_20261012.json';DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json';WP=PKG/'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2.md';PREP=ROOT/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011'
ADMISSION=PKG/'coordination/MASTER_GATE05_R27_CHILD_CAPTURE_E1_VERIFICATION_20261012.json';REPORT=ROOT/'docs/QA_EngineHost_Gate05_R27_Child_Capture_Independent_S2_20261012.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists(),str(p)
    p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def preservation():
    for p,h in [(BASELINE,'F73B73C42CB05C558A6487370D7F10F159E09B49AC0E4FDD41AEAD23C3C30FB0'),(MAN,'1FD4B9EFB368EE03F327241418C5CC0ACC08F9210E6E1BD271AECC373D219EE3'),(DEP,'7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'),(WP,'098602B4E0CEB179FDEF5C9D89A6B12BE673D88202C5407F95119D68159C5D7F')]:assert sha(p)==h,str(p)
    rows=[];seen=set()
    for d in load(BASELINE)['files']:
        p=Path(d['path']);assert p.resolve().is_relative_to(ROOT.resolve()) and str(p).lower() not in seen;seen.add(str(p).lower());r=row(p);assert r['sha256']==d['sha256'] and r['bytes']==d['bytes'],str(p);rows.append(r)
    frozen=[]
    for d in load(MAN)['files']:
        p=Path(d['frozen_path']);r=row(p);assert r['sha256']==d['sha256'] and r['bytes']==d['size'];frozen.append(r)
    assert len(rows)==13674 and len(frozen)==83
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=13674,files=rows,frozen83=frozen,all_matched=True,production_build_modify=0)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R27_FROZEN_LINEAGE.json');defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'AST_METADATA_ONLY_OLD_NAMED_DEFINITIONS','exec'),ns);v=ns['identity']()
    assert v[0]['dll_sha256']=='68BFE5105FA0471AAAF7943009703BB2599B39C5B572833507D6733BCE63CF64' and v[0]['mvid']=='44ba753c-6570-49d8-8068-4edf87a4e5d0';assert v[0]['pdb_sha256']=='F0BC1B7D92F67593EA967F56A90EE302C76B920A46B98EF77219F7B884C47814';assert all(len(r['documents'])==4 and all(d['matched'] for d in r['documents']) for r in v);return v
if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists();write(Q/'PRESERVATION_BEFORE.json',preservation());v=identity()
    rid='SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012-'+uuid.uuid4().hex
    a=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT',wp_revision='S2',delivery_id='SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012-01',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',report_path=str(REPORT),report_sha256='PENDING',manifest_sha256='PENDING',completion_sha256='PENDING',protected_paths=13674,frozen83=True,selected_sha256=v[0]['dll_sha256'],selected_mvid=v[0]['mvid'],PDBsources=[4,4],qa_builds_calls_yet=0,scope='Exact selected R27 defensive static+fullyspecified fournormalpair bytesfactory8 IsValid8 Capture4 and full15getter/raw/ownership only; newQA finalbuild1-twofreshcultures',limitations=['No normal execution verdict yet','Productioncandidate modify-rebuild/global/native/Process/registration/adverse0','UnexpectedFAIL/proofgap stop preserve/report; no selfrepair-rerun'],closure_changed=False,runtime_e2_released=False,foundation='HOLD')
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a)
    print(json.dumps(dict(result_id=rid,ack_sha256=sha(Q/'ACK_INITIAL.json'),protected=13674,frozen=83,sourcePDB=[4,4],candidate_calls=0),indent=2))
