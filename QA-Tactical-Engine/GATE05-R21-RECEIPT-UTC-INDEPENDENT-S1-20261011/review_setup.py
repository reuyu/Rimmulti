from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R21-49256586';MAN=TASK/'MASTER_GATE05_R21_RECEIPT_UTC_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R21_QA_INDEPENDENT_PROTECTED_BASELINE_20261011.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R21_Receipt_Utc_Independent_S1_20261011.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R21_RECEIPT_UTC_E1_VERIFICATION_20261011.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='B3A4F1CC59D73E9774580216A03647336687A43637AA30F3FC6FBECED1421B6F'
    assert sha(MAN)=='D2E2FEF82674B9C2C8F4C90045D9F75AE8C3463C82BC4AB1A9CB2502008623DB'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R21_RECEIPT_UTC_INDEPENDENT_S1.md')=='1D70407D24EC6DC3195DEDBF31CC10A746F72C5CE8825577763E2EA7F1C15F4F'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==10939
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R21_FROZEN_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='31D7A2508ACFADE1B9430F43E6F3D2ACF3E9822C787D00DAF55C9E44CF8E5AC4' and r[0]['mvid']=='7a8b444a-3a07-4dee-9d37-4fa7ed3c461c'
    assert r[1]['mvid']=='28abd2eb-3220-4e97-aa99-c4ff1edb5900';return r



if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R21_RECEIPT_UTC_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R21-RECEIPT-UTC-INDEPENDENT-S1-20261011-01',result_id='SOL-GATE05-R21-RECEIPT-UTC-INDEPENDENT-S1-20261011-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='ExactfrozenR21 STATIC+normalPUREParseStrict/configbytefileSHA/descriptor/detachedsnapshot fulltypedopaqueidentityownership only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Opaque policyId/revision whitespaceUnicode unchanged independentoracle;normalFAILreportedwithoutcorrection/rerun','Process/globalWorkerinstaller/bootstrap/native/adverse0','NewQArunner notyetbuilt','FullGateE2NOTRELEASED/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=10939,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
