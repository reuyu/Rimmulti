from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R15-03649052';MAN=TASK/'MASTER_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R16_QA_PREPARATION_PROTECTED_BASELINE_20261010.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R16_Operator_Native_Preparation_S1_20261010.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_E1_VERIFICATION_20261010.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='4B567A39019F6033F81F8A97E91FD583674F8E799F2804A25E02405448444AE3'
    assert sha(MAN)=='951F31D922BA7639A86C1BF1D88A03375432080FB56CD2EEA9D4EC0A3419E1D9'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION_S1.md')=='7EF30FCFB9638FFA92282350D9DB40C5D4EB4551D108BFAC2222689361E7C74E'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==8932
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R16_FROZEN_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='835E81216B850B571577677AB724FAC9A515465F79888A5CACC13C51FF832877' and r[0]['mvid']=='4fb1a25f-72c8-426d-b93f-d6cba4f9af72'
    assert r[1]['mvid']=='58766cdc-afee-4682-858a-dab68c96e36e';return r

if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010-01',result_id='SOL-GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Independent read-only operator16dimension/source RuntimeCopy7 readiness andfuture normalnative QAcriteria only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Exact R15 source/PE-PDB metadata only;candidate orQA runnerbuildloadexecute0','RuntimeCopy7 existingfiles metadata only;no assets copy/install/native/operator/game/adverse0','A in-progress R16outputs notread','Preparation notnativePASS/E2/closure/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=8932,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
