from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R9-fbe8a43b';MAN=TASK/'MASTER_GATE05_R9_VERSION_MEANING_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R9_QA_PROTECTED_BASELINE_20261009.json';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R8-SUPPORTED-DISPOSITION-INDEPENDENT-S1-20261009'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def preservation():
    assert sha(BASELINE)=='AC36866CFAE90EF23FD753C5DED0B8154BDF8448C1095C61DB51120A3A5DE103'
    d=load(BASELINE);rows=[];seen=set()
    for x in d['files']:
        p=Path(x['path']);assert p.resolve().is_relative_to(ROOT.resolve()),'Original/external path not authorized'
        assert str(p).lower() not in seen;seen.add(str(p).lower());assert sha(p)==x['sha256'] and p.stat().st_size==x['size'],str(p)
        rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    assert len(rows)==d['protected_unique_paths']
    assert sha(MAN)=='F3130B707E0B99690E6E724654EE794C61BBADFD34F8F9C07297C4AB481BD193' and sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    for x in load(MAN)['files']:
        p=Path(x['frozen_path']);assert sha(p)==x['sha256'] and p.stat().st_size==x['size'],str(p)
    return dict(at=now(),baseline_path=str(BASELINE),baseline_sha256=sha(BASELINE),protected_unique_paths=len(rows),files=rows,original_steam_userdata_mutable_candidate_read=False)
def identity():
    source=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R9_LINEAGE.json')
    defs=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_metadata_only','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='02815FF8A20CB971AD716BBA75417E5FFAD9FADEB358078A785253124FEF4BF5' and r[0]['mvid']=='12aa23c7-3ec0-4b6a-bbb1-4a036127c5da'
    assert r[1]['mvid']=='9d4837eb-4ad1-4e50-9c29-52e3d9466061';return r
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not (ROOT/'docs/QA_EngineHost_Gate05_R9_Version_Meaning_Independent_S1_20261009.md').exists()
    wp=PKG/'WP_QA_ENGINE_GATE05_R9_VERSION_MEANING_INDEPENDENT_S1.md';assert sha(wp)=='EF7D0C153DD964C7B2765011FBBC05CC4AB25CC1178FE65190CFA31A00F6CD9D'
    d=preservation();write(Q/'PRESERVATION_BEFORE.json',d);r=identity()
    a=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R9_VERSION_MEANING_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009-01',result_id='SOL-GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Fresh R9 frozen defensive static and positive pure codec/ValidateContract/TryAdmitManifest helpers',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R9_Version_Meaning_Independent_S1_20261009.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Initial terminal hashes pending','No prior candidate PASS inheritance','No production change/build/provider/cache/game/native/operator/old runner/rejection/adverse execution'])
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a);print(json.dumps(dict(result_id=a['result_id'],protected_unique_paths=len(d['files']),selected_sha256=r[0]['dll_sha256'],pdb_documents=[len(x['documents']) for x in r]),indent=2))
