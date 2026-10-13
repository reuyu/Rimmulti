from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
BASELINE=PKG/'coordination/MASTER_R9_QA_PROTECTED_BASELINE_20261009.json';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R9-fbe8a43b';MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b/MASTER_GATE05_R9_VERSION_MEANING_REVIEW_FREEZE_MANIFEST.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='AC36866CFAE90EF23FD753C5DED0B8154BDF8448C1095C61DB51120A3A5DE103';assert sha(MAN)=='F3130B707E0B99690E6E724654EE794C61BBADFD34F8F9C07297C4AB481BD193'
    rows={}
    def check(p,h,n):
        assert p.resolve().is_relative_to(ROOT.resolve()),'Unapproved original/external path';assert sha(p)==h and p.stat().st_size==n,str(p);r=row(p);key=str(p).lower();assert key not in rows or rows[key]==r;rows[key]=r
    for r in load(BASELINE)['files']:check(Path(r['path']),r['sha256'],r['size'])
    base_count=len(rows);assert base_count==load(BASELINE)['protected_unique_paths']
    manifest=PREVQ/'EVIDENCE_MANIFEST.json';assert sha(manifest)=='13D7C33FB46B96A3409E42FEDB44311300FFEE008CAD5955233952FD70792B14';old=load(manifest);assert len(old['files'])==326
    for r in old['files']:check(Path(r['path']),r['sha256'],r['bytes'])
    terminal_names=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']
    for p in [BASELINE]+[PREVQ/n for n in terminal_names]:r=row(p);check(p,r['sha256'],r['bytes'])
    assert sha(PREVQ/'COMPLETION.json')=='AF00A8872AD37828376B8DC5B2EFA3EEC5ED73FA14BDE49679031235E1DAC1D5'
    return dict(at=now(),master_baseline=row(BASELINE),master_baseline_paths=base_count,added_r9_qa_evidence=len(old['files']),r9_qa_manifest=row(manifest),additional_terminal_and_baseline_refs=[row(p) for p in [BASELINE]+[PREVQ/n for n in terminal_names]],protected_unique_paths=len(rows),files=sorted(rows.values(),key=lambda r:r['path'].lower()),mutable_r10_or_original_steam_userdata_read=False)
if __name__=='__main__':
    assert not (Q/'ACK.json').exists() and not (ROOT/'docs/QA_EngineHost_Gate05_R10_Package_Policy_Preparation_S1_20261009.md').exists();wp=PKG/'WP_QA_ENGINE_GATE05_R10_PACKAGE_POLICY_PREPARATION_S1.md';assert sha(wp)=='637DC053B0672128E2C95C88E9C4734CAF22F6B7CB2B15476CD38FBC8941CEE6'
    d=preservation();write(Q/'PRESERVATION_BEFORE.json',d);a=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R10_PACKAGE_POLICY_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R10-PACKAGE-POLICY-PREP-S1-20261009-01',result_id='SOL-GATE05-R10-PACKAGE-POLICY-PREP-S1-20261009-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Read-only frozenR9/static+independent normal acceptance preparation;mutableR10 not reviewed',r10_candidate_verdict='NOT_REVIEWED',controls_executed=0,qa_runner_builds=0,candidate_runner_processes=0,production_modifications_builds=0,report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R10_Package_Policy_Preparation_S1_20261009.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Preparation only;R10 candidate unseen','No mutableR10/source/bin/obj/native/game/provider/cache/oldrunner/rejection/adverse access or execution','No global supported catalogue/patch-settings exclusion/operatororigin policy choice','Terminal hashes pending creation'])
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a);print(json.dumps(dict(result_id=a['result_id'],protected_unique_paths=d['protected_unique_paths'],master_baseline=d['master_baseline_paths'],added_r9_qa_evidence=d['added_r9_qa_evidence'],execution=0),indent=2))
