"""Master-only reconciliation for the user-requested reference source review."""
from pathlib import Path
import datetime, json, hashlib, shutil
import master_check_a_result as checker

ROOT = Path(__file__).resolve().parent.parent
H = ROOT / 'docs/WarEconomy_Master_Handoff_20261006'
D = ROOT / 'Dispatcher'
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
board = read(D/'MASTER_A_TASKS.json')
t = next(t for t in board['tasks'] if t['dispatch_id']=='WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708')
folder = Path(t['ack_path']).parent
ack = read(Path(t['ack_path']))
assert all(ack.get(k)==t[k] for k in ['dispatch_id','wp_id','wp_revision','recipient'])
assert ack['status']=='IN_PROGRESS'
preservation = checker.inspect_preservation(t)
installed = Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll')
incident_dir = H/'coordination/ENGINE_INSTALLED_IDENTITY_INCIDENT_20261008'
incident_dir.mkdir(exist_ok=True)
snapshot = incident_dir/'OBSERVED_INSTALLED_WorkerBridge.dll'
if not snapshot.exists(): shutil.copy2(installed, snapshot)
stat = installed.stat()
identity = {'path':str(installed),'expected_sha256':'2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C', 'actual_sha256':sha(installed), 'size':stat.st_size, 'last_write_utc':datetime.datetime.fromtimestamp(stat.st_mtime,datetime.timezone.utc).isoformat(), 'snapshot_path':str(snapshot),'snapshot_sha256':sha(snapshot),'actor':'UNKNOWN','cause':'UNKNOWN','external_original_modified_by_master':False}
proof = H/'coordination/MASTER_R2_RECOVERY_ACK_REVIEW_20261008.json'
record={'schema_version':1,'event_id':'MASTER-R2-RECOVERY-ACK-AND-PRESERVATION-20261008-01','checked_at':now,'exclusive_lock_run':'MASTER-REFERENCE-ACK-INCIDENT-20261008-02','exclusive_lock_session':80768,'dispatch_id':t['dispatch_id'],'user_reset_again_confirmed':True,'ack':ack,'ack_sha256':sha(Path(t['ack_path'])),'recovery_report_path':str(folder/'A_RECOVERY_ACK.md'),'recovery_report_sha256':sha(folder/'A_RECOVERY_ACK.md'),'work_log_sha256':sha(folder/'A_WORK_LOG.md'),'completion_present':Path(t['completion_path']).exists(),'preservation':preservation,'installed_identity_incident':identity,'master_corrections':['No .git means Git clean/HEAD status unavailable, not clean checkout.','Manifest SHA match is not file inventory preservation proof.','Only exact nine allowed Engine paths govern; broad bin directory authorization is not adopted.','Implementation plans/ACK do not prove native execution or E1/E2.','Sol notLoaded last completed snapshot needs fresh check before delivery.'],'new_wp_or_resend':False,'gate_or_closure_change':False}
write(proof,record)
t.update(ack_verified=True,ack_sha256=record['ack_sha256'],acknowledged_at=ack['acknowledged_at'],ack_observed_at=now,a_context_status='RECOVERY_ACK_OBSERVED_IMPLEMENTATION_IN_PROGRESS',recovery_delivery_state='IDENTITY_MATCHED_ACK_OBSERVED',execution_observation='A_REPORTED_IN_PROGRESS_NO_NATIVE_EXECUTION_PROOF',recovery_progress_status='ACK_RECEIVED_AFTER_USER_RESET',preservation_status='INCIDENT_OPEN_INSTALLED_DLL_CHANGED',preservation_incident_proof=str(proof),updated_at=now)
board['updated_at']=now
write(D/'MASTER_A_TASKS.json',board)
state=read(D/'MASTER_COMMUNICATION_STATE.json')
state.update(a_status='ACK_VERIFIED_IN_PROGRESS_PRESERVATION_INCIDENT_OPEN',updated_at=now)
state['a_progress_attention'].update(status='SUPERSEDED_BY_USER_RESET_AND_NEW_ACK',resolved_at=now,resolution_proof=str(proof))
state['a_preservation_attention']={'attention_id':'ENGINE-INSTALLED-IDENTITY-20261008-01','status':'OPEN','proof':str(proof),'notify_unchanged_again':False,'external_restore_authorized':False}
state['a_latest_runtime_observation']={'at':now,'dispatch_id':t['dispatch_id'],'ack_verified':True,'completion_present':record['completion_present'],'proof':str(proof),'native_execution_verified':False}
write(D/'MASTER_COMMUNICATION_STATE.json',state)
event={'event_id':record['event_id'],'at':now,'type':'A_RESET_ACK_VERIFIED_PRESERVATION_INCIDENT_OPEN','dispatch_id':t['dispatch_id'],'proof':str(proof),'proof_sha256':sha(proof),'new_dispatch':False,'closure_changed':False}
for p in [D/'MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(event,ensure_ascii=False)+'\n')
delta=f'''\n\n## LOCAL-A-R2-RESET-ACK-PRESERVATION-INCIDENT — {now}\nLatest user reports another A reset and resumed processing. Same R2 ACK identity/revision/recipient verified IN_PROGRESS; A_RECOVERY_ACK/work log collected, prior possible-stall attention superseded. No duplicate WP, terminal/native/E1/E2 proof or closure inferred. No Git repo means unavailable Git clean state; manifest hashes alone do not prove preserved files. Master actual archive19/Pipeline206/R1frozen147 checks retained. Existing Steam installed WorkerBridge DLL differs: expected {identity['expected_sha256']}, actual {identity['actual_sha256']}, last-write metadata {identity['last_write_utc']}; actor/cause UNKNOWN. Immutable installed path is outside allowed Engine repair paths. Observed bytes copied to project incident folder; external original not changed/restored, baseline hashes not normalized. Incident ENGINE-INSTALLED-IDENTITY-20261008-01 OPEN; no new Engine E2 release until provenance/isolated runtime identity resolved. Same R2 technical preservation notice prepared; delivery requires actual proof. Existing hourly monitor ACTIVE unchanged; reference-mod analysis read-only, no integration/build. Engine002006/Pipeline007/current schema/G-Q1 OPEN, Foundation HOLD. Proof: {proof}\n'''
for name in ['MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md']:
    with (H/name).open('a',encoding='utf-8') as f:f.write(delta)
with (ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md').open('a',encoding='utf-8') as f:f.write(delta)
notice=folder/'MASTER_SAME_WP_PRESERVATION_NOTICE_20261008.md'
notice.write_text(f'''# 동일 R2 WP 보존 확인 — 새 WP 아님\n\n작성 {now}; dispatch {t['dispatch_id']} / WP_ENGINE_GATE05_R2 / GATE05-R2. 현재 구현 범위/번호는 유지하고 중복 작업을 시작하지 않는다.\n\nMaster는 새 ACK와 복구 보고서를 읽었다. 아래 실제 보존 불일치를 현재 작업의 A_WORK_LOG.md에 기록하고 원인·변경 작업·배포 경로·실제 로딩 identity를 근거로 설명한다.\n\n- 기존 Steam 설치 DLL: {installed}\n- 기대 SHA256: {identity['expected_sha256']}\n- 실제 SHA256: {identity['actual_sha256']}\n- last-write metadata UTC: {identity['last_write_utc']} (변경 주체/시각의 확정 증거 아님)\n- archive19/Pipeline206/R1 frozen147은 Master 전체 파일 검사에서 보존됨.\n\n이 기존 설치 경로는 승인 변경 목록에 없다. 추가 Steam 설치/core/ProbeMod 쓰기를 중단하고 자동 복구/덮어쓰기도 하지 않는다. 기존 증거/기대 해시는 수정하지 않는다. R2 native 작업은 승인된 프로젝트 내부 별도 licensed runtime copy에서 수행한다. 변경된 설치 DLL을 old Gate05 identity로 취급하거나 old E2를 재사용하지 않는다. 테스트 중이라면 먼저 읽기 전용으로 실제 candidate SHA/MVID/source/PDB/loaded profile을 기록한다. 알 수 없는 부분은 UNKNOWN으로 남긴다. 이 notice 때문에 새 구현 WP/재빌드/게임 종료를 임의로 만들지 않는다.\n\n복구 보고서 정정: .git 부재는 Git clean 상태를 증명하지 않는다. 허용 경로는 task preservation_policy의 정확한 9개 파일이다. manifest SHA 일치와 manifest 내부 전체 파일 일치는 다르다. ACK/계획은 실행/PASS/closure 증거가 아니다.\n\n완료 전 이 incident에 대한 답을 A_WORK_LOG.md 및 최종 report limitation에 넣는다. 보존 제약으로 진행 불가능하면 이유를 BLOCKED로 정직하게 보고한다. Master의 fresh candidate review/freeze 이후 독립 Sol E2는 별도다.\n''',encoding='utf-8')
print(json.dumps({'proof':str(proof),'ack_verified':True,'preservation_errors':preservation['preservation_errors'],'installed_identity':identity,'notice':str(notice)},ensure_ascii=False))
