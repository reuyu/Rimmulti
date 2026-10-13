from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R11-bec3d350';MAN=TASK/'MASTER_GATE05_R11_POLICY_ENCODING_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R11_QA_PROTECTED_BASELINE_20261009.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R11-POLICY-ENCODING-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R11_Policy_Encoding_Independent_S1_20261009.md';SELECTION=PKG/'coordination/MASTER_R11_POLICY_ESCAPE_CONVENTION_SELECTION_20261009.json';ADMISSION=TASK/'MASTER_R11_ADMITTED_CODEC_CANDIDATE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='9B9A2E1113E16976729A5805019A45DACF8E51FDA7150E13AC0ACC109E5470A6'
    assert sha(MAN)=='79151763B710FE37E59148E272C1C7BC6C3D606D275B5215AF4174187C209DB1' and sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(ADMISSION)=='19A7A624349327D545DBF50FD00185739EBBD97FC333A2C91016345CBB80EDB0'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==4189
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R11_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='133348C3FBC20215B9C4E0E9CA25D731781FCE9AD8CBE91F5A145BDB3620F98D' and r[0]['mvid']=='e6c6f6fd-2915-4493-8ef9-dc5d87de1c6b'
    assert r[1]['mvid']=='35dfe68f-6a6f-44cc-a648-7c8153f6a2ad';return r
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R11_POLICY_ENCODING_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R11-POLICY-ENCODING-INDEPENDENT-S1-20261009-01',result_id='SOL-GATE05-R11-POLICY-ENCODING-INDEPENDENT-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Exact frozen R11 positive current policy declaration/codec helpers and defensive static review',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Selected current WE-PACKAGE-POLICY-V1 normal data only;no unknownschema/rejection/adverse','No production rebuild/provider/config/cache/native/game/operator/oldrunner execution','Invalid producer release manifest preserved;new graph not producer chronology'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=4189,selected_sha256=meta[0]['dll_sha256'],pdb_documents=[len(r['documents']) for r in meta]),indent=2))
