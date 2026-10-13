from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
BASELINE=PKG/'coordination/MASTER_R12_QA_PREP_PROTECTED_BASELINE_20261009.json'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350/MASTER_GATE05_R11_POLICY_ENCODING_REVIEW_FREEZE_MANIFEST.json'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R11-bec3d350';PRIOR=ROOT/'QA-Tactical-Engine/GATE05-R11-POLICY-ENCODING-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R12_Package_Order_Preparation_S1_20261009.md'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='150B60EFB482E95370444096F9658A49A1A47AD4FC8962F29BB7F3FADD70CC03'
    assert sha(MAN)=='79151763B710FE37E59148E272C1C7BC6C3D606D275B5215AF4174187C209DB1'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==4901
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,mutable_r12_source_bin_obj_runner_ack_completion_read=False,original_steam_userdata_save_read_restore=False)
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists()
    d=preservation();write(Q/'PRESERVATION_BEFORE.json',d)
    a=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R12_PACKAGE_ORDER_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R12-PACKAGE-ORDER-PREP-S1-20261009-01',result_id='SOL-GATE05-R12-PACKAGE-ORDER-PREP-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Read-only frozen R11/normal reference package ordinal and transport preparation only',r12_candidate_verdict='NOT_REVIEWED',controls_executed=0,qa_runner_builds=0,candidate_runner_processes=0,production_modify_builds=0,report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Future R12 API/headers/field carrier unseen;no candidate assertions/inherited PASS','Normal standard JSON/hash reference preparation only','General schema/cache/patch-settings/native/operator remain separate OPEN','Terminal hashes pending'])
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a);print(json.dumps(dict(result_id=a['result_id'],protected_unique_paths=4901,controls_build_run=0),indent=2))
