from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R7-8524bf02';MAN=TASK/'MASTER_GATE05_R7_CONTENT_ADMISSION_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R7_QA_PROTECTED_BASELINE_20261008.json';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def preservation():
    assert sha(BASELINE)=='5B68231D84C68F6A6FBFFF6EB38A45A68A77DFD7848FF5CE85BAA27F3B5848F0'
    d=load(BASELINE);rows=[];seen=set()
    for x in d['files']:
        p=Path(x['path']);assert p.resolve().is_relative_to(ROOT.resolve()),'Original/external path not authorized'
        assert str(p).lower() not in seen;seen.add(str(p).lower());assert sha(p)==x['sha256'] and p.stat().st_size==x['size'],str(p)
        rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    assert len(rows)==d['protected_unique_paths']
    assert sha(MAN)=='DE49655C30976C254F59B022C7DD768806B90EB6F566055936B05EAFFE3F13CF' and sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    for x in load(MAN)['files']:
        p=Path(x['frozen_path']);assert sha(p)==x['sha256'] and p.stat().st_size==x['size'],str(p)
    return dict(at=now(),baseline_path=str(BASELINE),baseline_sha256=sha(BASELINE),protected_unique_paths=len(rows),files=rows,original_steam_userdata_mutable_candidate_read=False)
def identity():
    source=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R7_LINEAGE.json')
    defs=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_metadata_only','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='223B4055C0AFAA6F30488C9787AE6F68D65D62F395CFCA722EDA83674975CD2A' and r[0]['mvid']=='bdf94567-be4d-4270-9a70-dbf2df9b5b4a'
    assert r[1]['mvid']=='db8d92c1-a284-4e67-8bcc-708e279944c1';return r
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not (ROOT/'docs/QA_EngineHost_Gate05_R7_Content_Admission_Independent_S1_20261008.md').exists()
    wp=PKG/'WP_QA_ENGINE_GATE05_R7_CONTENT_ADMISSION_INDEPENDENT_S1.md';assert sha(wp)=='F447D47696E2196C96EA256D88F7079B639AC0500A179678BB1C1C5A67C24921'
    d=preservation();write(Q/'PRESERVATION_BEFORE.json',d);r=identity()
    a=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R7_CONTENT_ADMISSION_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008-01',result_id='SOL-GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Fresh R7 frozen defensive static and positive pure codec/ValidateContract/TryAdmitManifest helpers',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R7_Content_Admission_Independent_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Initial terminal hashes pending','No prior candidate PASS inheritance','No production change/build/provider/cache/game/native/operator/old runner/rejection/adverse execution'])
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a);print(json.dumps(dict(result_id=a['result_id'],protected_unique_paths=len(d['files']),selected_sha256=r[0]['dll_sha256'],pdb_documents=[len(x['documents']) for x in r]),indent=2))
