from pathlib import Path
import json,datetime,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(Q/'COMPLETION.json');i=read(Q/'RESULT_INDEX.json');m=read(Q/'EVIDENCE_MANIFEST.json')
assert c['delivery_id']=='SOL-GATE05-R4-INDEPENDENT-REVIEW-S1-20261008-01' and c['result_id']==i['result_id']==m['result_id']
assert sha(Q/'COMPLETION.json')=='E357E2D5C488E74496715324389A4DF0A7E79BBD4B86581EF82C4818789A3F51'
assert sha(Q/'RESULT_INDEX.json')==c['result_index_sha256'] and sha(Q/'EVIDENCE_MANIFEST.json')==c['evidence_manifest_sha256'] and sha(Path(c['report_path']))==c['report_sha256']
checks=[]
for row in m['files']:
 p=Path(row['path']);assert p.resolve().is_relative_to(R);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];checks.append({'path':str(p),'matched':True,'size_matched':True})
def rows(d):
 if isinstance(d,dict):
  if 'path' in d and 'sha256' in d and Path(d['path']).is_absolute():yield d
  if 'manifest' in d and 'manifest_sha256' in d:yield {'path':d['manifest'],'sha256':d['manifest_sha256']}
  for v in d.values():yield from rows(v)
 elif isinstance(d,list):
  for v in d:yield from rows(v)
before={x['path']:x for x in rows(read(Q/'PRESERVATION_BEFORE.json'))};after={x['path']:x for x in rows(read(Q/'PRESERVATION_AFTER.json'))}
assert set(before)==set(after) and len(after)==2066
for key,row in after.items():
 p=Path(key);assert p.resolve().is_relative_to(R);assert sha(p)==row['sha256']==before[key]['sha256'];assert p.stat().st_size==row.get('bytes',row.get('size',p.stat().st_size))
assert all(c[k]==0 for k in ['candidate_executions','runner_executions','game_executions','native_executions','builds','production_changes','adverse_reproductions'])
proof={'at':at,'result_id':c['result_id'],'delivery_id':c['delivery_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_sha256':c['evidence_manifest_sha256'],'result_index_sha256':c['result_index_sha256'],'evidence_files':len(checks),'artifact_checks':checks,'protected_unique_paths_master_rehashed':len(after),'independent_verdict':c['independent_verdict'],'master_verdict':'ACCEPTED_INDEPENDENT_STATIC_REVISION_REQUIRED_RUNTIME_UNTESTED','actual_thread_status':'idle','actual_turn_status':'completed','actual_turn_id':'01a11a99-5277-7622-8417-ea46d137131b','cursor':'2745552a-f142-41a1-8eaf-3fe7b2d500ca:30','direct_report_received':True,'candidate_executions_by_master':0,'closure_changed':False,'foundation':'HOLD','runtime_e2_released':False,'monitor':'PAUSED60MIN','next_a_scope':'R5 codec/content-only first; operator/native repair separate sequential WP not released'}
p=H/'coordination/MASTER_SOL_R4_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261008.json';write(p,proof)
review=H/'MASTER_REVIEW_ENGINE_GATE05_R4_INDEPENDENT_QA_S1_20261008.md'
review.write_text('''# R4 independent QA Master disposition

**ACCEPTED_INDEPENDENT_STATIC_REVISION_REQUIRED_RUNTIME_UNTESTED**. Original Sol terminal/direct report matches actual completed/idle turn and cursor30. Evidence17 SHA/size, report/manifest/index/completion graph and2066 protected unique paths independently rehashed. No candidate/runner/game/native execution, rebuild or production modification by Master.

Sol R4-M01~10 qualifications are adopted within accepted MD125~132/ADR006B; no gate weakening or new all-fields requirement. Complete explicitly requires current Authority/Grant existence+SIMULATION and task/result READ_ONLY: do not characterize nullable comparisons as null-current acceptance. Direct R3 mode regression is corrected statically. Existing census/Promote/cache/core dependencies and R4 DLC inventory exist. Receipt proposal-mode recheck/admitted workload/config/origin/stable target/role-aware MD129/typed content and native proof remain insufficient. No observed exploitation is claimed.

43 raw/JSON PASS counts/IDs/order agree. Independent coverage:metadata4,mock/reflection handler IO35,OS child1,reflection API1,schema constant1,cache helper1,native semantic normal0. GEN03 actual result writer is runner; GEN07 census/hash/Game mocked. SEC06 does not execute OS getter failure; CLAMP03 error-text absence is not successful validator evidence. Completion18 and report9 rows match; meaningful limitations object fails checker type only. Pre-run5 identity rows differ, before7 sizes differ. Post-completion frozen232 is not pre-run proof.

Runtime7 contains incomplete assets, but no single failure cause is established. CLI/PID/copy identity do not prove loaded candidate/content/UserData isolation or numeric exit/semantic result. Native UNTESTED/CAUSE_UNKNOWN; installed incident OPEN/actor UNKNOWN, no restore/normalization.

Master approves sequential narrower development: R5 codec/content-only first, then independent verification, then separately scoped operator/native repair. There is one A source writer; Sol remains independent. R5 must retain R4 role/control code, explicitly declare supported typed field/null/order/content scope, use actual codec normal evidence and final pre-run identity. R5 alone does not repair/release whole Gate05. No parallel Engine source edits or broad full-gate repeat. New A R5 is NOT SENT until fresh UI idle/submission proof; same hourly monitor resumes only after actual submission. Sol may independently prepare admitted-content coverage without modifying production.

Engine002006/Pipeline007/current schema7/G-Q1 OPEN,Foundation HOLD; narrow historical CLOSED scope unchanged. Runtime E2 NOT_RELEASED,closure/release none. Verification: coordination/MASTER_SOL_R4_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261008.json. Original report: C:/Users/user/Desktop/RimMulti/docs/QA_EngineHost_Gate05_R4_Independent_Review_S1_20261008.md.
''',encoding='utf-8')
proof.update(master_review_path=str(review),master_review_sha256=sha(review));write(p,proof)
rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp);assert not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results']);receipt=dict(proof,type='SOL_R4_INDEPENDENT_STATIC_S1',verification_path=str(p),verification_sha256=sha(p));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(rp,receipts)
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';state=read(cp);assert state['active_operation'] is None;state.update(sol_status='R4_STATIC_QA_COMPLETED_MASTER_REVIEWED_IDLE',sol_latest_result=receipt,last_sol_cursor=proof['cursor'],updated_at=at);write(cp,state)
sp=H/'DISPATCHER_STATE.json';d=read(sp);d['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',last_result_id=c['result_id'],latest_review=str(review),current_runtime_idle_verified=True);d['updated_at']=at
for row in d['deliveries']:
 if row.get('delivery_id')==c['delivery_id']:row.update(status='COMPLETED_STATIC_MASTER_REVIEWED',result_id=c['result_id'],master_disposition=str(review))
write(sp,d)
paragraph=f'''\n\n## LOCAL-SOL-R4-INDEPENDENT-S1-COMPLETE — {at}\nOriginal Sol {c['result_id']}/{c['delivery_id']} direct terminal matches actual completed/idle/cursor30. Master ACCEPTED_INDEPENDENT_STATIC_REVISION_REQUIRED_RUNTIME_UNTESTED;17 evidence and2066 protected unique paths SHA/size matched. R3 direct mode correction/Complete current authority existence/R4 DLC inventory credited;remaining supported context/operator/typed content/native/provenance gaps.43 labels metadata4+fixture35+OSchild1+API1+schema1+cache1,native0;pre-run5 identity/before7 size gaps. Master adopts narrow sequential R5 codec/content-first,operator/native separate later;new A task NOT SENT pending fresh idle/CU proof,no whole-gate release. Same hourly scheduler PAUSED until actual A delivery;Sol idle/direct reporting ready. No closure;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {p}\n'''
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md',R/'AGENTS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(receipt,event_id='SOL-R4-STATIC-COMPLETE-MASTER-20261008-01'),ensure_ascii=False)+'\n')
print(json.dumps({k:proof[k] for k in ['at','master_verdict','evidence_files','protected_unique_paths_master_rehashed','master_review_path']},ensure_ascii=False))
