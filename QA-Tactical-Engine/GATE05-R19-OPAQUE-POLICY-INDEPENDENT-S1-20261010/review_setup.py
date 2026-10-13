from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R19-OPAQUE-POLICY-20261010-DIRECT-5415a675';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R19-5415a675';MAN=TASK/'MASTER_GATE05_R19_OPAQUE_POLICY_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R19_QA_INDEPENDENT_PROTECTED_BASELINE_20261010.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R19_Opaque_Policy_Independent_S1_20261010.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R19_OPAQUE_POLICY_E1_VERIFICATION_20261010.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='9F1B154C47D6434EF751FA8ED32915D472B4FB8FAB8DE50918C02379753A2D75'
    assert sha(MAN)=='746D9B76B8F338291D9B5F5602D3BF571C5BEFFBBB963F8C82E903177C179310'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R19_OPAQUE_POLICY_INDEPENDENT_S1.md')=='D290ABF01C304CE56871F463C5E14AD273AFA3C6AF1E6DEFBCF020EF955C8C08'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==9841
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R19_FROZEN_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='FB69CB8385CF665AEBAFA1913A8A02CC7887F48F8BBA6FCDEE85CF67C8CB646D' and r[0]['mvid']=='4969ba0f-2bdf-4a27-b4f8-d7fa217f0b70'
    assert r[1]['mvid']=='4804693e-29fc-4acd-b51d-1c74046b417f';return r



if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R19_OPAQUE_POLICY_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010-01',result_id='SOL-GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='ExactfrozenR19 STATIC+normalPUREParseStrict/configbytefileSHA/descriptor/detachedsnapshot fulltypedopaqueidentityownership only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Opaque policyId/revision whitespaceUnicode unchanged independentoracle;normalFAILreportedwithoutcorrection/rerun','Process/globalWorkerinstaller/bootstrap/native/adverse0','NewQArunner notyetbuilt','FullGateE2NOTRELEASED/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=9841,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
