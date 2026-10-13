from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R12-e9dcd1e6';MAN=TASK/'MASTER_GATE05_R12_PACKAGE_ORDER_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R12_QA_PROTECTED_BASELINE_20261009.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R12-PACKAGE-ORDER-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R11-POLICY-ENCODING-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R12_Package_Order_Independent_S1_20261009.md';ADMISSION=TASK/'MASTER_R12_ADMITTED_CODEC_CANDIDATE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='D500246BF05FBE17A8BC05D9DD88EE91390928C1BD8E37B5BF0CE521582EB09C'
    assert sha(MAN)=='824747638CC2B71EB42CB778CBA90F8EA4DB3A9C388306AA6D3BC48D868F2A18'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(ADMISSION)=='CE2E6DB04DF19DFDABC214A27E678DFD71AA56D8B0EDA73A329A52F38D2AE618'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==5078
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R12_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='3035A0D0FDD799D42AC83B7D776998AFF07A8BDD3246959E685AA0F8D7ACF94E' and r[0]['mvid']=='ad4caf3c-88bc-4971-9c2a-ab78eae395e5'
    assert r[1]['mvid']=='7b97e307-b06f-40fc-ad6f-5530d180ebe0';return r
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R12_PACKAGE_ORDER_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009-01',result_id='SOL-GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Exact frozen R12 positive package-order codec/helpers and defensive static review',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Current-v1 normal data only;no unknownschema/rejection/adverse','No production rebuild/provider/config/cache/native/game/operator/oldrunner execution','Own QA graph cannot repair producer chronology;fullGate E2 not released'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=5078,selected_sha256=meta[0]['dll_sha256'],pdb_documents=[len(r['documents']) for r in meta]),indent=2))
