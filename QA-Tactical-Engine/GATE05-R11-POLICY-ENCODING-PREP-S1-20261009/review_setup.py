from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
BASELINE=PKG/'coordination/MASTER_R11_QA_PREP_PROTECTED_BASELINE_20261009.json'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb/MASTER_GATE05_R10_PACKAGE_POLICY_REVIEW_FREEZE_MANIFEST.json'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R10-81a28ecb'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R11_Policy_Encoding_Preparation_S1_20261009.md'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='6BB4CE6FA59094BD325C2EAFD8009F3E0281B1A69112E8B84EC5CAD07186F24F'
    assert sha(MAN)=='5BBDD6AA47C415783CDD0FCB256A87B852D227720FBD0B6E62B9F061680E8578'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        expected_size=r['bytes'] if 'bytes' in r else r['size']
        if 'bytes' in r and 'size' in r:assert r['bytes']==r['size']
        assert sha(p)==r['sha256'] and p.stat().st_size==expected_size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==4047
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,mutable_r11_source_bin_obj_runner_completion_read=False,original_steam_userdata_save_read_restore=False)
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not REPORT.exists()
    d=preservation();write(Q/'PRESERVATION_BEFORE.json',d)
    a=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R11_POLICY_ENCODING_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R11-POLICY-ENCODING-PREP-S1-20261009-01',result_id='SOL-GATE05-R11-POLICY-ENCODING-PREP-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Read-only frozen R10/reference canonical policy preparation only',r11_candidate_verdict='NOT_REVIEWED',controls_executed=0,qa_runner_builds=0,candidate_runner_processes=0,production_modifications_builds=0,report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Future R11 API/escape convention unobserved;no candidate assertions or inherited PASS','Normal reference JSON/hash preparation allowed,not candidate execution','General order/cache/patch-settings/native/operator remain separate OPEN','Initial terminal hashes pending'])
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a);print(json.dumps(dict(result_id=a['result_id'],protected_unique_paths=4047,controls_executed=0),indent=2))
