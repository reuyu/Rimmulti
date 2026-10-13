from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R17-OWNED-BOOTSTRAP-20261010-DIRECT-57163c71';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R17-57163c71';MAN=TASK/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R17_QA_INDEPENDENT_PROTECTED_BASELINE_20261010.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R17_Owned_Bootstrap_Independent_S1_20261010.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R17_OWNED_BOOTSTRAP_E1_VERIFICATION_20261010.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='40E6FF1D398663C9D85CB1947B6BAF2A4F0525D54D69602A425FF97E7F3E18AD'
    assert sha(MAN)=='6D17F1A90702249EA1B0F1BA36A06F4C870DEC6E8E88D722ABF7FE34B74CE7DA'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT_S1.md')=='01890B40A98F199DF9F8BA9FE20A2402200A365DAC2CD52D6E1C39E421676580'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==9082
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R17_FROZEN_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='F7946FED1F4FB896DD8F46B7C253C4DB24E6CF2AA6D9C0528CD5B59CD05DBAA3' and r[0]['mvid']=='d5a25e43-567c-414f-b7bd-4d4aa0b47050'
    assert r[1]['mvid']=='ab67e9ac-0c30-4718-98a3-cbfe9af31c87';return r


if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010-01',result_id='SOL-GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='ExactfrozenR17 defensivestatic+positivePUREisolatedconfigsnapshot/fileSHA/redaction/limitedvalidcodec only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','No VerifyProcessIdentity/Process queries/Worker globalConfigureReset/getfallback/Awake/bootstrap/native/game/operator/negative/adverse','Ownnormalhelperrunnerbuild permitted butnotyetbuilt','Native E2notreleased/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=9082,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
