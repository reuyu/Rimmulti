from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R13-2661a749';MAN=TASK/'MASTER_GATE05_R13_POLICY_CACHE_LIFECYCLE_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R13_QA_INDEPENDENT_PROTECTED_BASELINE_20261009.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R13_Policy_Cache_Lifecycle_Independent_S1_20261009.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R13_POLICY_CACHE_LIFECYCLE_E1_VERIFICATION_20261009.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='D90EA84C24A979DDAE347AB3CD132329694BDDA884E5BF869ED1F0637B035A5E'
    assert sha(MAN)=='3F831ED136C1A499943DE5F167620D6CF3032ECEA2FF294C7B1E279307D3B098'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_INDEPENDENT_S1.md')=='2D096CF2AF8775815994AD9D3DFFAB7DCB06A7CA3A600FA137C09BA1C3BF8A26'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==6021
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R13_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='EC04C539E4B6F057238F2D1A454B517333C3C11C4307C3CB73DD623A65FE044D' and r[0]['mvid']=='48adef37-dea2-41e0-aee6-b293e329a2b5'
    assert r[1]['mvid']=='94055e10-b349-4c49-a37c-cb1338d83425';return r
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R13-POLICY-CACHE-LIFECYCLE-INDEPENDENT-S1-20261009-01',result_id='SOL-GATE05-R13-POLICY-CACHE-LIFECYCLE-INDEPENDENT-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Exact frozen R13 positive valid lifecycle/standalone matching core/pure codec and defensive static review',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Current-v1 normal data only;no unknownschema/rejection/adverse','Valid config/Clear/Invalidate/emptydiagnostics andstandalone normalmatching core only;no actualCompute/GetActual/provider/globalpublish/game/native/operator/old/adverse','Own QA graph cannot repair producer chronology;fullGate E2 not released'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=6021,selected_sha256=meta[0]['dll_sha256'],pdb_documents=[len(r['documents']) for r in meta]),indent=2))
