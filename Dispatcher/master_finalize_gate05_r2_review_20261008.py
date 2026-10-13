"""Durable Master disposition after the read-only R2 review."""
from pathlib import Path
import datetime, json, hashlib
ROOT=Path(__file__).resolve().parent.parent;D=ROOT/'Dispatcher';H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
proof=H/'coordination/MASTER_GATE05_R2_E1_VERIFICATION_20261008.json';verified=read(proof)
receipts=read(D/'MASTER_RECEIPTS.json')
qa=[]
for e in receipts['processed_results']:
 if e.get('type')=='INDEPENDENT_GATE05_E2_SCOPED_RESULT':
  old=read(H/'coordination/MASTER_GATE05_E2_EVIDENCE_VERIFICATION_20261007.json')
  idx=read(Path(old['index_path']));p=Path(idx['evidence_manifest']['path'])
  expected=e['evidence_manifest_sha256']
 elif e.get('type','').startswith('SOL_PIPELINE_REV6_R1'):
  idx=read(Path(e['result_index_path']));p=Path(e.get('evidence_manifest_path') or idx['evidence_manifest_path'])
  expected=e['evidence_manifest_sha256']
 else:continue
 manifest=read(p);files=manifest['files']
 rows=[{'path':name,**item} for name,item in files.items()] if isinstance(files,dict) else files
 errors=[]
 for f in rows:
  q=Path(f['path'])
  if not q.is_file() or sha(q)!=f['sha256']:errors.append(str(q))
 assert sha(p)==expected and not errors
 qa.append({'manifest':str(p),'manifest_sha256':sha(p),'file_count':len(rows),'file_errors':errors})
fm=read(Path(verified['freeze_manifest']))
assert all(sha(Path(f['frozen_path']))==f['sha256'] for f in fm['files'])
runner_dep=ROOT/'scratch/EngineGate05R2/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
runner_dep_check={'path':str(runner_dep),'sha256':sha(runner_dep),'matches_selected_current':sha(runner_dep)==verified['artifact_checks'][12]['sha256'],'interpretation':'Present post-execution dependency matches candidate; not proof of actual loaded runtime profile or pre-execution snapshot'}
review=H/'MASTER_REVIEW_ENGINE_GATE05_R2_E1_20261008.md';scope=H/'ENGINE_GATE05_R3_CORRECTIVE_SCOPE_20261008.md'
body=review.read_text(encoding='utf-8').replace('CodeView GUID一致','CodeView GUID 일치').replace('明示 산출물','명시 산출물')
review.write_text(body,encoding='utf-8')
verified.update(finalized_at=now,qa_preservation=qa,runner_dependency=runner_dep_check,review_path=str(review),review_sha256=sha(review),followup_scope_path=str(scope),followup_scope_sha256=sha(scope),followup_status='PREPARED_NOT_DISPATCHED',producer_terminal_collected=True,producer_full_remediation_claim_adopted=False)
write(proof,verified)
board=read(D/'MASTER_A_TASKS.json');t=next(t for t in board['tasks'] if t['dispatch_id']==verified['dispatch_id'])
t.update(status='COMPLETED_REVIEWED_REVISION_REQUIRED',completed_at='2026-10-08T01:26:30Z',completion_sha256=verified['original_completion_sha256'],producer_result_id=None,master_collection_key=verified['master_collection_key'],producer_completion_schema='NONCONFORMANT_ALIAS_IDENTITY_RECONCILED',master_disposition='REVISION_REQUIRED_E2_NOT_RELEASED',master_review_path=str(review),master_review_sha256=sha(review),candidate_freeze_manifest=verified['freeze_manifest'],candidate_freeze_manifest_sha256=verified['freeze_manifest_sha256'],collected_at=now,updated_at=now,preservation_notice_delivery_status='CANCELLED_UNSENT_SUPERSEDED_BY_TERMINAL_REVIEW',preservation_incident_status='OPEN',followup_scope_path=str(scope),followup_dispatch_status='NOT_SENT')
board['updated_at']=now;write(D/'MASTER_A_TASKS.json',board)
state=read(D/'MASTER_COMMUNICATION_STATE.json')
state.update(a_status='TERMINAL_COLLECTED_REVISION_REQUIRED_E2_NOT_RELEASED',a_current_attempt_id=None,updated_at=now,sol_status='AWAIT_FRESH_ENGINE_ADMISSION_NO_NEW_WP')
state['master_monitor_automation'].update(status='PAUSED',desired_status='PAUSED',interval_minutes=60,configuration_verified=True,configuration_proof=str(H/'coordination/MASTER_MONITOR_PAUSED_R2_REVIEW_20261008.json'),configuration_checked_at=now,pause_reason='User instruction and R2 terminal reviewed',no_resume_in_this_review=True)
state['a_latest_result']={'master_collection_key':verified['master_collection_key'],'producer_result_id':None,'dispatch_id':verified['dispatch_id'],'completion_sha256':verified['original_completion_sha256'],'status':'COMPLETED_REVIEWED_REVISION_REQUIRED','master_verdict':'REVISION_REQUIRED_E2_NOT_RELEASED','review':str(review),'proof':str(proof)}
state['a_last_delivery'].update(ack_verified=True,ack_sha256=t['ack_sha256'],ack_proof_scope='Actual identity-matched ACK; no native PASS inferred')
state['a_preservation_attention'].update(status='OPEN',last_checked_at=now,notice_delivery_status='CANCELLED_UNSENT_SUPERSEDED_BY_TERMINAL_REVIEW',current_review=str(review))
state['sol_runtime_observation'].update(status='notLoaded',latest_turn_status='completed',at=now,new_final=False,recheck_before_fresh_delivery=True)
write(D/'MASTER_COMMUNICATION_STATE.json',state)
key=verified['master_collection_key']
assert not any(e.get('master_collection_key')==key for e in receipts['processed_results']), 'Result already collected; do not duplicate'
receipts['processed_results'].append({'type':'A_ENGINE_GATE05_R2_E1','master_collection_key':key,'producer_result_id':None,'dispatch_id':verified['dispatch_id'],'processed_at':now,'completion_sha256':verified['original_completion_sha256'],'producer_verdict':verified['producer_verdict'],'master_verdict':verified['master_verdict'],'completion_schema_valid':False,'alias_identity_matched':True,'report_path':str(ROOT/'docs/POC_EngineHost_Semantic_Authority_Gate_05_R2.md'),'review_path':str(review),'review_sha256':sha(review),'verification_path':str(proof),'verification_sha256':sha(proof),'freeze_manifest':verified['freeze_manifest'],'freeze_manifest_sha256':verified['freeze_manifest_sha256'],'frozen_files':107,'artifact_hash_matches':16,'source_pdb_documents_debug':4,'source_pdb_documents_release':4,'e1_checkpoint_counts':verified['checkpoint_counts'],'native_unexecuted':True,'installed_incident_open':True,'qa_preserved_counts':[x['file_count'] for x in qa],'new_qa_release':False,'closure_changed':False})
receipts['updated_at']=now;write(D/'MASTER_RECEIPTS.json',receipts)
dispatch=read(H/'DISPATCHER_STATE.json')
dispatch['endpoints']['a'].update(current_wp=None,ack_verified=True,execution_phase='TERMINAL_REVIEWED',recovery_progress_status='SUPERSEDED_BY_TERMINAL_RESULT',last_result_id=None,last_master_collection_key=key,last_result_verdict='REVISION_REQUIRED_E2_NOT_RELEASED',latest_review=str(review),current_runtime_idle_verified=False)
dispatch['latest_master_review']={'at':now,'review':str(review),'proof':str(proof),'status':'REVISION_REQUIRED_E2_NOT_RELEASED','scheduler':'PAUSED60MIN','new_dispatch':False}
dispatch['automation_enabled']=False
dispatch['updated_at']=now;write(H/'DISPATCHER_STATE.json',dispatch)
event={'event_id':verified['event_id'],'at':now,'type':'A_R2_TERMINAL_REVIEW_REVISION_REQUIRED','dispatch_id':verified['dispatch_id'],'master_collection_key':key,'original_completion_sha256':verified['original_completion_sha256'],'proof':str(proof),'proof_sha256':sha(proof),'review':str(review),'review_sha256':sha(review),'scheduler':'PAUSED60MIN','new_dispatch':False,'closure_changed':False,'previous_notice':'CANCELLED_UNSENT_SUPERSEDED_BY_TERMINAL_REVIEW'}
for p in [D/'MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
delta=f'''\n\n## LOCAL-ENGINE-GATE05-R2-E1-MASTER — {now}\nA terminal R2 collected after human completion notice. Original completion nonconformant schema (aliases/task identity reconciled; producer result_id absent);16 artifact SHA/size checks and Debug/Release CodeView/source4/4 matched. Raw/results counts24/23PASS/1BLOCKED agree but fixture/stub/source checks do not prove native authority. Master REVISION_REQUIRED/E2_NOT_RELEASED: requester/operator boundary, complete MD128 result context, channel/process lifetime, typed lossless MD130 coverage remain; no actual native attempt/DRM failure proof. Old installed SHA BB3B... differs from immutable old2D64...;actor/cause UNKNOWN/incident OPEN, archive19/Pipeline206/R1frozen147 and QA inventories {[x['file_count'] for x in qa]} matched. R2 post-review107 freeze preserved;no candidate build/execution by Master/no old E2 reuse. Previous unsent R2 notice explicitly CANCELLED_UNSENT_SUPERSEDED_BY_TERMINAL_REVIEW. Concrete R3 corrective scope PREPARED_NOT_DISPATCHED, no new A/QA WP. User-requested existing wareconomy-master actual PAUSED/60min/short prompt/correct target confirmed;no resume/new scheduler. Sol notLoaded/same completed cursor19, no new result. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD/narrow historical closures retained. Review: {review};proof: {proof}\n'''
for name in ['MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md']:
 with (H/name).open('a',encoding='utf-8') as f:f.write(delta)
with (ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md').open('a',encoding='utf-8') as f:f.write(delta)
print(json.dumps({'master_verdict':verified['master_verdict'],'qa_counts':[x['file_count']for x in qa],'freeze_files':len(fm['files']),'runner_dependency_sha':runner_dep_check['sha256'],'new_dispatch':False,'scheduler':'PAUSED60MIN','review':str(review)},ensure_ascii=False))
