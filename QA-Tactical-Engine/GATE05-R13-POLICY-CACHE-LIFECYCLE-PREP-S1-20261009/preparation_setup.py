from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
WP=PKG/'WP_QA_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_PREPARATION_S1.md';BASELINE=PKG/'coordination/MASTER_R13_QA_PREP_PROTECTED_BASELINE_20261009.json'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R12-e9dcd1e6';SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6/MASTER_GATE05_R12_PACKAGE_ORDER_REVIEW_FREEZE_MANIFEST.json'
PRIOR=ROOT/'QA-Tactical-Engine/GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009';REPORT=ROOT/'docs/QA_EngineHost_Gate05_R13_Policy_Cache_Lifecycle_Preparation_S1_20261009.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(WP)=='3DDA11D7B4B7D9117947BB8ADC8A5C861CC51522E842158F1D96D2993EE74989'
    assert sha(BASELINE)=='873F3E2F715A0A52B58E80198A5A7DDD07672498B944DF7A667319C04196ECD7'
    assert sha(MAN)=='824747638CC2B71EB42CB778CBA90F8EA4DB3A9C388306AA6D3BC48D868F2A18'
    assert sha(SOURCE)=='5E9A4DE9A6280A887E3659CE2D80A8029C2BEF41DC615BB3F6F1BB859B1F020E'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        assert '2661a749' not in key and not ('r13' in key and any(s in key for s in ['scratch','ack','completion']))
        assert sha(p)==r['sha256'] and p.stat().st_size==r.get('bytes',r.get('size')),str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==5901
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=5901,files=files,mutable_r13_original_steam_userdata_save_read=False)
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists();write(Q/'PRESERVATION_BEFORE.json',preservation())
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009-01',result_id='SOL-GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_PREPARATION_IN_PROGRESS',scope='Frozen R12 only;prospective policy/cache lifecycle and immutable perprocess output preparation',other_active_wp=False,report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,qa_runner_builds=0,assembly_loads=0,candidate_runner_processes=0,controls_executed=0,r13_candidate_verdict='NOT_REVIEWED',limitations=['Future R13 API/types/generation/header/formatter unobserved','Read-only preparation is not execution/E2/closure','R12 archive/sharedprimitiveJsonNET qualifications preserved'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=5901,frozen_reference=row(SOURCE)),indent=2))
