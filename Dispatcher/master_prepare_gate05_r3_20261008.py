"""Approve a unique R3 envelope under the user's direct dispatch/resume request."""
from pathlib import Path
import copy, datetime, hashlib, json, uuid
import master_check_a_result as checker
ROOT=Path(__file__).resolve().parent.parent;D=ROOT/'Dispatcher';H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
board=read(D/'MASTER_A_TASKS.json')
assert not any(t['status'] in ['SENT','ACKNOWLEDGED','IN_PROGRESS','DELIVERY_UNCERTAIN']for t in board['tasks'])
old=next(t for t in board['tasks']if t['wp_id']=='WP_ENGINE_GATE05_R2')
assert old['master_disposition']=='REVISION_REQUIRED_E2_NOT_RELEASED'
dispatch_id='WE-A-ENGINE-GATE05-R3-20261008-DIRECT-'+uuid.uuid4().hex[:8]
folder=D/'A_TASKS'/dispatch_id;folder.mkdir()
wp=H/'WP_ENGINE_GATE05_R3.md';release=Path(old['master_review_path'])
policy=copy.deepcopy(old['preservation_policy'])
policy['additional_preserved_candidate_manifests']=[{'path':policy['prior_candidate_freeze_manifest'],'sha256':policy['prior_candidate_freeze_manifest_sha256'],'lineage':'R1_REJECTED147'}]
policy['prior_candidate_freeze_manifest']=old['candidate_freeze_manifest']
policy['prior_candidate_freeze_manifest_sha256']=old['candidate_freeze_manifest_sha256']
policy['prior_candidate_lineage']='R2_REJECTED107'
policy['known_installed_incident']={'id':'ENGINE-INSTALLED-IDENTITY-20261008-01','status':'OPEN','expected_old_sha256':'2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C','observed_sha256_at_dispatch':'BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61','not_new_approval_to_modify_or_restore':True}
installed=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll')
assert sha(installed)==policy['known_installed_incident']['observed_sha256_at_dispatch']
task={'dispatch_id':dispatch_id,'recipient':'A','approved':True,'wp_id':'WP_ENGINE_GATE05_R3','wp_revision':'GATE05-R3','delivery_envelope_revision':6,'created_at':now,'approved_at':now,'approval_source':'Latest explicit user: automatically send A follow-up and activate existing schedule','status':'PREPARED_NOT_SENT','delivery_status':'NOT_SENT','route':'computer-use/Antigravity','delivery_owner':'Master','instruction_path':str(folder/'INSTRUCTIONS.md'),'work_package_path':str(wp),'work_package_sha256':sha(wp),'release_path':str(release),'release_sha256':sha(release),'follows_dispatch_id':old['dispatch_id'],'preservation_policy':policy,'ack_path':str(folder/'ACK.json'),'completion_path':str(folder/'COMPLETION.json'),'ack_existed_before_delivery':False,'completion_existed_before_delivery':False,'runtime_verdict':None,'reference_paths':[str(H/'REFERENCE_MOD_REUSE_ANALYSIS_20261008.md'),str(H/'C_REVIEW_CORRECTIONS_CONSOLIDATED.md'),str(H/'history/MASTER_DECISION_LOG_MDR-067.md'),str(H/'coordination/MASTER_GATE05_R2_E1_VERIFICATION_20261008.json'),policy['engine_archive_manifest'],policy['pipeline_manifest'],policy['prior_candidate_freeze_manifest'],policy['additional_preserved_candidate_manifests'][0]['path']],'prerequisites':['actual Master exclusive byte0 lock','A exact current conversation idle and R2 terminal confirmed','no active/unknown duplicate delivery','Engine archive19/Pipeline206/R1 frozen147/R2 frozen107 and QA archives preserved','installed known incident unchanged; no restore/modification authorization','actual UI submission proof before monitor activation']}
preservation=checker.inspect_preservation(task)
assert len(preservation['preservation_errors'])==1 and str(installed) in preservation['preservation_errors'][0]
assert len(preservation['engine_archive_checks'])==19 and len(preservation['pipeline_preservation_checks'])==206 and len(preservation['prior_candidate_checks'])==254
prior_proof=read(H/'coordination/MASTER_GATE05_R2_E1_VERIFICATION_20261008.json')
qa=[]
for m in prior_proof['qa_preservation']:
 p=Path(m['manifest']);assert sha(p)==m['manifest_sha256'];data=read(p);entries=data['files']
 rows=[{'path':name,**e}for name,e in entries.items()]if isinstance(entries,dict)else entries
 assert all(Path(e['path']).is_file() and sha(Path(e['path']))==e['sha256']for e in rows)
 qa.append({'manifest':str(p),'sha256':sha(p),'checked_files':len(rows),'errors':[]})
before=folder/'MASTER_PRESERVATION_BEFORE_DISPATCH.json'
write(before,{'at':now,'dispatch_id':dispatch_id,'preservation':preservation,'qa_preservation':qa,'installed_incident_known_open':True,'checker_additional_manifest_support':True,'no_candidate_rebuild':True})
instructions=f'''# Master 승인 전달 — WP_ENGINE_GATE05_R3 / GATE05-R3\n\nDispatch ID: {dispatch_id}\nEnvelope6 / Recipient A. 사용자가 Master 자동 직접 전달 및 기존 예약 활성화를 명시 승인했다.\n\n1. 정확한 새 WP `{wp}`를 전체 읽고 수행한다. Controlling R2 review `{release}`를 반드시 읽는다. R2는 수집/거절/107파일 보존됐고 새 corrective WP다. 이전 prepared scope의 NOT DISPATCHED는 역사 준비 상태이며 이 새 승인 envelope가 실제 작업을 지정한다.\n2. Root AGENTS/실제 SRS/C corrections/accepted MD125~132·새 WP의 exact preservation policy를 확인한다. 새 task folder는 `{folder}`이다.\n3. 새로운 작업 시작 전 ACK.json에 schema_version1,dispatch_id `{dispatch_id}`,wp_id WP_ENGINE_GATE05_R3,wp_revision GATE05-R3,recipient A,status ACKNOWLEDGED|IN_PROGRESS|BLOCKED,acknowledged_at timezone,note를 기록한다. 다른 WP 처리 중이면 중복 시작하지 말고 그 상태를 알린다.\n4. 정확한 9 allowed Engine paths와 새 root scratch/EngineGate05R3/report/manifest/task만 변경한다. 기존 R2 원문/107 frozen,R1 frozen147,Engine archive19,Pipeline206,QA324297312238를 보존한다. 실제 사전 검사 `{before}`에서 known installed incident 하나가 남는다. 기존 Steam DLL 실제 BB3B...와 expected2D64... 차이를 정상화하지 말고 원인/경로/loaded identity를 설명한다. 원본 설치/core/ProbeMod/실제 사용자 save/예약·Master governance를 변경하지 않는다.\n5. 권한 우회/위조·exploit reproduction은 수행하지 않는다. defensive source review와 genuine normal operator→fresh native validation flow만 수행한다. Mock/stub/source checks를 native/full gate PASS로 포장하지 않는다. 설치 보호 우회 없이 새 project licensed runtime copy를 실제 확인하거나 미실행/관측 제약을 정확히 보고한다.\n6. 새 COMPLETION은 envelope/WP에 명시된 표준 schema/unique result_id/실제 hash/roles/limits/freeze before-after를 계산한 뒤 마지막에 발행한다. task_id/work_package_id aliases만으로 대체하지 않는다. `COMPLETED`는 E2/closure가 아니다. BLOCKED/FAILED는 reason과 partial artifacts를 포함한다. 한국어로 A_WORK_LOG.md와 report를 작성한다.\n\n필수 references: \n'''+''.join('- '+p+'\n'for p in task['reference_paths'])
(folder/'INSTRUCTIONS.md').write_text(instructions,encoding='utf-8')
message=f'Master 승인 새 작업: {folder / "INSTRUCTIONS.md"} 를 전체 읽고 WP_ENGINE_GATE05_R3/GATE05-R3를 수행하세요. R2는 리뷰·보존 완료입니다. 먼저 새 task에 ACK.json, 완료 후 표준 COMPLETION.json을 작성하세요. 다른 WP 처리 중이면 중복 시작하지 말고 알려주세요.'
(folder/'UI_MESSAGE.txt').write_text(message,encoding='utf-8')
task.update(instruction_sha256=sha(folder/'INSTRUCTIONS.md'),exact_message_path=str(folder/'UI_MESSAGE.txt'),exact_message=message,exact_message_sha256=sha(folder/'UI_MESSAGE.txt'),preservation_before_path=str(before),preservation_before_sha256=sha(before))
write(folder/'MASTER_DELIVERY_PREPARED.json',{'at':now,'task':task,'exclusive_lock_session':30539,'actual_delivery':False,'monitor_status':'PAUSED_UNTIL_ACTUAL_SUBMISSION'})
board['tasks'].append(task);board['updated_at']=now;write(D/'MASTER_A_TASKS.json',board)
state=read(D/'MASTER_COMMUNICATION_STATE.json')
state.update(a_pending_dispatch_id=dispatch_id,a_status='R3_APPROVED_NOT_SENT',active_operation={'run_id':'MASTER-A-R3-DIRECT-DISPATCH-20261008-01','dispatch_id':dispatch_id,'phase':'PREPARED_AWAIT_ACTUAL_UI_SUBMISSION','started_at':now},updated_at=now)
write(D/'MASTER_COMMUNICATION_STATE.json',state)
event={'event_id':dispatch_id+'-PREPARED','at':now,'type':'MASTER_R3_APPROVED_PREPARED_NOT_SENT','dispatch_id':dispatch_id,'wp':'WP_ENGINE_GATE05_R3','revision':'GATE05-R3','approved':True,'instruction_path':task['instruction_path'],'instruction_sha256':task['instruction_sha256'],'actual_delivery':False,'scheduler':'PAUSED_UNTIL_SUBMISSION','closure_changed':False}
for p in [D/'MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8')as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
delta=f'''\n\n## LOCAL-A-ENGINE-GATE05-R3-APPROVED — {now}\nLatest user explicitly directs automatic A delivery and existing monitor activation, superseding prior review-only pause at actual new submission. WP_ENGINE_GATE05_R3/GATE05-R3 envelope6 approved/new unique {dispatch_id} PREPARED_NOT_SENT. Exact instruction/WP/release/reference paths+hashes and standard completion schema recorded. R2/R1 rejected107/147,Engine archive19,Pipeline206,QA324297312238 matched; installed BB3B... known pre-existing incident OPEN, not normalized/restored. Current exact A recovery conversation/R2 final and empty Send/no Working observed;actual input/submission pending. One existing hourly scheduler remains PAUSED until confirmed submission;no duplicate scheduler/QA WP/closure. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Instruction: {task['instruction_path']}\n'''
for name in ['MASTER_AGENT_DISPATCH_BOARD.md','MASTER_DECISION_LOG.md','MASTER_PROJECT_STATE.md']:
 with (H/name).open('a',encoding='utf-8')as f:f.write(delta)
with (ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md').open('a',encoding='utf-8')as f:f.write(delta)
print(json.dumps({'dispatch_id':dispatch_id,'instruction_path':task['instruction_path'],'message':message,'checks':{'archive':19,'pipeline':206,'R1_R2_frozen':254,'qa':[r['checked_files']for r in qa]},'status':'PREPARED_NOT_SENT'},ensure_ascii=False))
