from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R18-CONFIG-ADMISSION-SEAL-20261010-DIRECT-befc4fba';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R18-befc4fba';MAN=TASK/'MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R18_QA_INDEPENDENT_PROTECTED_BASELINE_20261010.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R18_Config_Admission_Seal_Independent_S1_20261010.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_E1_VERIFICATION_20261010.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='2C84708033FC11481B6C1444DC1CF0341C1CE6CCDE390CD597E96A87FF545BAC'
    assert sha(MAN)=='C558CC579658D04CCC4396AFAAEB8792455663BE377A6F36E3835BBE5F99C908'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_S1.md')=='3E86C2FB5C7D7AA4D20ECF0EA0937E9BA560D3A671C3AD3EF4C51D25ACF23B02'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==9374
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R18_FROZEN_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='AE7B2FB6FF3BDFD449D43CB055B85768557E872D4985017E71E2E5655F8F6073' and r[0]['mvid']=='9e8501fc-d16e-413b-8682-17ba8550d9bf'
    assert r[1]['mvid']=='3e31c359-ffda-491b-a7b7-fcfb04ff5d3b';return r



if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010-01',result_id='SOL-GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='ExactfrozenR18 STATIC+normalPUREParseStrict/configbytefileSHA/descriptor/detachedsnapshot fulltypedopaqueidentityownership only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Opaque policyId/revision whitespaceUnicode unchanged independentoracle;normalFAILreportedwithoutcorrection/rerun','Process/globalWorkerinstaller/bootstrap/native/adverse0','NewQArunner notyetbuilt','FullGateE2NOTRELEASED/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=9374,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
