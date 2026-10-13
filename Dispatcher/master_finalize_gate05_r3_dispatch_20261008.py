"""Verify persisted hourly activation and record actual R3 ACK/dispatch."""
from pathlib import Path
import datetime,json,hashlib,tomllib
import master_check_a_result as checker
ROOT=Path(__file__).resolve().parent.parent;D=ROOT/'Dispatcher';H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
config_path=Path(r'C:\Users\user\.codex\automations\wareconomy-master\automation.toml')
config=tomllib.loads(config_path.read_text(encoding='utf-8'))
assert config['status']=='ACTIVE'and config['rrule'].removeprefix('RRULE:')=='FREQ=HOURLY;INTERVAL=1'
assert config['target_thread_id']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
assert config['prompt']==(D/'MASTER_MONITOR_TRIGGER.txt').read_text(encoding='utf-8-sig').strip() and len(config['prompt'])==173
board=read(D/'MASTER_A_TASKS.json');active=[t for t in board['tasks']if t['status']in['SENT','ACKNOWLEDGED','IN_PROGRESS','DELIVERY_UNCERTAIN']]
assert len(active)==1;t=active[0];assert t['dispatch_id']=='WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa'and t['delivery_status']=='SENT'
folder=Path(t['ack_path']).parent;ack=read(Path(t['ack_path']))
assert all(ack.get(k)==t[k]for k in['dispatch_id','wp_id','wp_revision','recipient']) and ack['status']in['ACKNOWLEDGED','IN_PROGRESS']
preservation=checker.inspect_preservation(t)
assert len(preservation['preservation_errors'])==1 and 'unapproved Engine baseline change:'in preservation['preservation_errors'][0]
proof=H/'coordination/MASTER_GATE05_R3_DISPATCH_MONITOR_ACTIVE_20261008.json'
record={'schema_version':1,'event_id':'MASTER-GATE05-R3-ACK-MONITOR-ACTIVE-20261008-01','at':now,'exclusive_lock_run':'MASTER-A-R3-DIRECT-DISPATCH-20261008-01','exclusive_lock_session':30539,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'delivery_status':'SENT','submission_proof':t['submission_proof'],'submission_proof_sha256':sha(Path(t['submission_proof'])),'ack':ack,'ack_sha256':sha(Path(t['ack_path'])),'ack_identity_matched':True,'actual_configuration':config,'configuration_sha256':sha(config_path),'automation_tool_result':{'automationId':'wareconomy-master','mode':'update','status':'ACTIVE'},'interval_minutes':60,'short_prompt_chars':173,'preservation':preservation,'known_installed_incident':'OPEN_NO_NORMALIZATION','candidate_runtime_verdict':None,'future_run_after_r3_resume_observed':False,'new_qa_wp':False,'closure_changed':False}
write(proof,record)
t.update(ack_verified=True,ack_sha256=record['ack_sha256'],acknowledged_at=ack['acknowledged_at'],ack_observed_at=now,status='IN_PROGRESS',monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(proof),updated_at=now)
board['updated_at']=now;write(D/'MASTER_A_TASKS.json',board)
state=read(D/'MASTER_COMMUNICATION_STATE.json')
state.update(a_status='R3_ACK_VERIFIED_IN_PROGRESS',active_operation=None,updated_at=now)
state['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=now,configuration_proof=str(proof),no_resume_in_this_review=False,pause_reason=None,resumed_by='Master after latest explicit user authorization and actual R3 submission',future_run_after_r3_resume_observed=False)
state['a_last_delivery'].update(ack_verified=True,ack_sha256=record['ack_sha256'],ack_observed_at=now)
state['a_latest_runtime_observation']={'at':now,'dispatch_id':t['dispatch_id'],'ack_verified':True,'completion_present':Path(t['completion_path']).exists(),'proof':str(proof),'native_execution_verified':False}
write(D/'MASTER_COMMUNICATION_STATE.json',state)
dispatch=read(H/'DISPATCHER_STATE.json')
dispatch['automation_enabled']=True;dispatch['updated_at']=now
dispatch['endpoints']['a'].update(ack_verified=True,execution_phase='IN_PROGRESS',latest_ack_proof=str(proof),last_verified_at=now)
dispatch['latest_master_dispatch']={'at':now,'dispatch_id':t['dispatch_id'],'status':'SENT_IN_PROGRESS_ACK_VERIFIED','scheduler':'ACTIVE60MIN','proof':str(proof),'future_run_observed':False}
write(H/'DISPATCHER_STATE.json',dispatch)
event={'event_id':record['event_id'],'at':now,'type':'MASTER_R3_ACK_EXISTING_HOURLY_MONITOR_ACTIVE','dispatch_id':t['dispatch_id'],'proof':str(proof),'proof_sha256':sha(proof),'scheduler':'ACTIVE60MIN','future_run_observed':False,'closure_changed':False}
for p in[D/'MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8')as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
delta=f'''\n\n## LOCAL-A-ENGINE-GATE05-R3-ACK-MONITOR-ACTIVE — {now}\nLatest explicit user requests automatic A delivery and monitor activation. Actual {t['dispatch_id']}/WP_ENGINE_GATE05_R3/GATE05-R3 envelope6 submitted via Master Computer Use to verified idle current WarEconomy 컨텍스트 복구 및 수행,exact new message/cleared composer/Working observed,identity-matched ACK IN_PROGRESS collected: SENT/IN_PROGRESS/no resend. Existing wareconomy-master tool-updated ACTIVE;persisted config ACTIVE/hourly60min/173char trigger/correct Master target/name verified,no new scheduler. Future R3 scheduled run not yet observed. Archive19/Pipeline206/R2frozen107+R1frozen147=254 and initial QA324297312238 preserved;known old installed incident OPEN/no restore or hash normalization. Exact task policy and source allowed paths control new repair. No new QA WP/no closure/no E1→E2;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Proof: {proof}\n'''
for name in['MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','MASTER_AGENT_DISPATCH_BOARD.md']:
 with(H/name).open('a',encoding='utf-8')as f:f.write(delta)
with(ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md').open('a',encoding='utf-8')as f:f.write(delta)
monitor_delta=f'''\n\n## Latest user automatic R3 dispatch/resume — {now}\nUser explicitly authorizes automatic A follow-up delivery and existing monitor activation; this supersedes review-only pause after R2. Current exact WP_ENGINE_GATE05_R3/GATE05-R3 envelope6 {t['dispatch_id']} actual Master Computer Use SENT/identity-matched ACK IN_PROGRESS. Same wareconomy-master ACTIVE/hourly60min/173char trigger/current Master target actual tool+config verified;future run pending observation. Current task/prior_candidate_freeze_manifest=R2 frozen107 and additional_preserved_candidate_manifests=R1 frozen147;master_check_a_result.py now checks both immutable lineages (254) plus archive19/Pipeline206. Old R2 COMPLETION/rejected runtime verdict/unsent cancelled notice must not be treated as R3 result/delivery. Known installed DLL incident remains OPEN;check preservation even before terminal and dedupe unchanged attention. Master admits any fresh candidate only after review,then separately releases original Sol E2. Monitor auto-pauses after actual R3 terminal collection/disposition;next actual A delivery uses same latest hourly lifecycle. Proof {proof}.\n'''
with(D/'MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md').open('a',encoding='utf-8')as f:f.write(monitor_delta)
with(ROOT/'AGENTS.md').open('a',encoding='utf-8')as f:f.write(f'''\n\n## Latest user R3 automatic dispatch/resume — 2026-10-08\nLatest user explicitly requests Master automatically send A corrective work and activate the existing schedule. WP_ENGINE_GATE05_R3/GATE05-R3 envelope6 {t['dispatch_id']} actual Computer Use SENT/ACK IN_PROGRESS verified in current WarEconomy 컨텍스트 복구 및 수행. Same wareconomy-master ACTIVE60min/short prompt/correct target verified;prior R2 review pause is historical. R2 rejected107 + R1 rejected147 + old archive19 + Pipeline206 + QA protected. Master task prior/additional preservation manifests control;mutable Engine source/build allowed exact9 files are never old candidate identity. Known Steam installed SHA mismatch incident OPEN,do not restore/normalize baseline. Current task/monitor/latest delta govern,new E2/closure still requires Master candidate admission and independent Sol.\n''')
print(json.dumps({'dispatch_id':t['dispatch_id'],'delivery':'SENT','ack':ack['status'],'scheduler':'ACTIVE','interval_minutes':60,'short_prompt_chars':173,'proof':str(proof),'protected_candidates':len(preservation['prior_candidate_checks'])},ensure_ascii=False))
