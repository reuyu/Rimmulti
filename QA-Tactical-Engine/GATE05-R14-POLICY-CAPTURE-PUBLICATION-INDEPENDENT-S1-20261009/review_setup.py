from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R14-ff285a3b';MAN=TASK/'MASTER_GATE05_R14_POLICY_CAPTURE_PUBLICATION_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R14_QA_INDEPENDENT_PROTECTED_BASELINE_20261009.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R14_Policy_Capture_Publication_Independent_S1_20261009.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R14_POLICY_CAPTURE_PUBLICATION_E1_VERIFICATION_20261009.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='00978F869BF9483253A2AF0DA39564C006AB17D574934A21A4369FCA6A54E1F9'
    assert sha(MAN)=='163626FB64A0BFED749483ED755EC8B19C1951BB838A8A239FBC7174F20D2823'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_S1.md')=='007F861D641FDB63A1F4D6DD94738E5C4F096E50EA5BF091F580FF3EDAD8306A'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==7003
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R14_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='1A19B47232F86C3BA3A8238783EA66ED71AE61E2DB16CF3B3C5162B0F7A6FC5F' and r[0]['mvid']=='acab0270-bc98-4d17-b920-9941950ff024'
    assert r[1]['mvid']=='874a8ce6-014a-4506-aba5-4648e50abd83';return r
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009-01',result_id='SOL-GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Exact frozen R14 positive valid lifecycle/standalone matching core/pure codec and defensive static review',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Current-v1 normal data only;no unknownschema/rejection/adverse','Valid config/Clear/Invalidate/emptydiagnostics andstandalone normalmatching core only;no actualCompute/GetActual/provider/globalpublish/game/native/operator/old/adverse','Own QA graph cannot repair producer chronology;fullGate E2 not released'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=7003,selected_sha256=meta[0]['dll_sha256'],pdb_documents=[len(r['documents']) for r in meta]),indent=2))
