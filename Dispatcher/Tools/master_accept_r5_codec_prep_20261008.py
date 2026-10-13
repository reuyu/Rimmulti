from pathlib import Path
import json,datetime,sys,hashlib,tomllib
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as checker
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return checker.digest(p)
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def payload(d):return json.loads(next(x['text'] for x in d['content'] if x['type']=='text' and x['text'].startswith('{')))
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(Q/'COMPLETION.json');i=read(Q/'RESULT_INDEX.json');m=read(Q/'EVIDENCE_MANIFEST.json')
assert c['delivery_id']=='SOL-GATE05-R5-CODEC-PREP-S1-20261008-01' and c['wp_id']=='WP_QA_ENGINE_GATE05_R5_CODEC_PREPARATION' and c['wp_revision']=='S1'
assert c['result_id']==i['result_id']==m['result_id'] and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='6E003D32DA3A5B09C7321F4FCFB7FB946A314DAD4D8C4FF747FF6170AD72CE17'
assert sha(Q/'RESULT_INDEX.json')==c['result_index_sha256'] and sha(Q/'EVIDENCE_MANIFEST.json')==c['evidence_manifest_sha256'] and sha(Path(c['report_path']))==c['report_sha256']
checks=[]
for row in m['files']:
 p=Path(row['path']);assert p.resolve().is_relative_to(R);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];checks.append({'path':str(p),'matched':True,'size_matched':True})
assert len(checks)==19
def rows(d):
 if isinstance(d,dict):
  if 'path' in d and 'sha256' in d and Path(d['path']).is_absolute():yield d
  if 'manifest' in d and 'manifest_sha256' in d:yield {'path':d['manifest'],'sha256':d['manifest_sha256']}
  for v in d.values():yield from rows(v)
 elif isinstance(d,list):
  for v in d:yield from rows(v)
before={x['path']:x for x in rows(read(Q/'PRESERVATION_BEFORE.json'))};after={x['path']:x for x in rows(read(Q/'PRESERVATION_AFTER.json'))}
assert set(before)==set(after) and len(after)==2089
for k,row in after.items():
 p=Path(k);assert p.resolve().is_relative_to(R);assert sha(p)==row['sha256']==before[k]['sha256'];assert p.stat().st_size==row.get('bytes',row.get('size',p.stat().st_size))
fields=read(Q/'SUPPORTED_FIELD_MATRIX.json');matrix=read(Q/'ACCEPTANCE_MATRIX_INDEX.json');assert len(fields['rows'])==fields['leaf_field_rows']==65 and len({x['family'] for x in fields['rows']})==8
src=Path(fields['source']['path']);assert sha(src)==fields['source']['sha256'];lines=src.read_text(encoding='utf-8-sig').splitlines()
assert all(1<=x['source_line']<=len(lines) and x['source_sha256']==fields['source']['sha256'] for x in fields['rows'])
assert matrix['normal_control_ids']==[f'C{n:02}' for n in range(1,19)] and matrix['provenance_ids']==[f'P{n:02}' for n in range(1,13)] and matrix['status']=='PLANNED_NOT_EXECUTED'
assert all(c[k]==0 for k in ['mutable_r5_reads','candidate_executions','runner_executions','game_executions','native_executions','builds','production_changes','adverse_reproductions','codec_controls_executed']) and not c['r5_candidate_reviewed']
snapshot=H/'coordination/MASTER_SOL_R5_CODEC_PREP_S1_COMPLETION_SNAPSHOT_20261008.json';poll=payload(read(snapshot))['polls'][0];assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11aab-9a96-70e2-b4f4-bb738ac4cfaf'
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and sha(Path(transport['proof_path']))==transport['proof_sha256']
proof={'at':at,'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'wp_revision':'S1','result_id':c['result_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_sha256':c['evidence_manifest_sha256'],'result_index_sha256':c['result_index_sha256'],'evidence_files':len(checks),'artifact_checks':checks,'protected_unique_paths_master_rehashed':len(after),'independent_verdict':c['independent_verdict'],'master_verdict':'ACCEPTED_QA_PREPARATION_NO_R5_CANDIDATE_VERDICT','actual_thread':poll,'direct_report_received':True,'transport_proof_verified':True,'supported_families':8,'historical_leaf_rows':65,'normal_plan_rows':18,'provenance_plan_rows':12,'controls_executed':0,'upstream_clr_width_enum_metadata':'PENDING_ADMITTED_DEPENDENCY_VERIFICATION','r5_candidate_reviewed':False,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','candidate_executions_by_master':0}
review=H/'MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_QA_PREPARATION_S1_20261008.md'
review.write_text('''# R5 codec QA preparation Master disposition

**ACCEPTED_QA_PREPARATION_NO_R5_CANDIDATE_VERDICT**. Original Sol direct report and published terminal match actual completed/idle turn/cursor33. Report/manifest/index/completion graph and19 evidence SHA/size,2089 protected unique paths independently rehashed. Mutable R5 source/bin/obj was outside QA scope; reported QA executions/build/production/adverse reproduction0. Master candidate execution/build0.

Historical frozen R4 ContentProfileProvider source SHA09D57... is the baseline. Eight Def families and65 leaf rows have source/function/line/SHA/type/requiredness/material/null/collection/order anchors. These65 rows describe the historical supported projection, not full RimWorld content or final adopted R5/global schema. Exact numeric CLR widths/enums still require admitted dependency metadata. Normal optional parent absence is not automatically an error; missing/unavailable/unknown must remain distinct from legitimate null/empty. Stable keys/order/multiplicity follow declared semantic meaning; no all-Def/all-sort prohibition or ownership freeze is adopted.

18 positive normal controls and12 provenance acceptance rows are accepted as an independent review checklist. Every row remains PLANNED_NOT_EXECUTED. Actual production codec linkage/semantic values/canonical bytes/digest are distinct from actual loaded profile/cache/Worker-validator/native issuer/whole gate. Independent expected values must not be copied from actual outputs. A future normal codec QA WP must release an exact frozen R5 candidate, permitted controls and execution boundary; this preparation is no such release. Normal Unicode/punctuation/null/precision input coverage is data-format verification, not security reproduction.

Provenance criteria retain final last-build→pre-run→normal-run→post-run identity/source/PDB/generated/dependency/tooling/content/config/run_id/Debug-vs-Release/raw/report checks. Historical pre-run5 identity and before7 size discrepancies remain; post-completion freeze does not become pre-execution proof. Existing accepted authority/context/MD129/native corrections remain outside R5 codec-only work.

A same R5 task remains IN_PROGRESS with identity-matched ACK; no unique terminal completion observed during this collection. No duplicate A/QA WP is issued. Existing hourly monitor remains ACTIVE until actual A terminal collection/disposition. Newly accepted QA evidence19 is additively protected in the Master-owned current A policy; initial dispatch baseline remains unchanged. Independent matrix is available for Master final candidate review, with no retroactive alteration to the sent A WP or instructions.

Sol waits for exact candidate/independent review WP. Runtime E2 NOT_RELEASED,Engine002006/Pipeline007/current schema7/G-Q1 OPEN,Foundation HOLD. Installed identity incident OPEN/actor UNKNOWN; no external restore/normalization. Review proof: coordination/MASTER_SOL_R5_CODEC_PREP_S1_COMPLETION_VERIFICATION_20261008.json.
''',encoding='utf-8')
proof.update(master_review_path=str(review),master_review_sha256=sha(review));vp=H/'coordination/MASTER_SOL_R5_CODEC_PREP_S1_COMPLETION_VERIFICATION_20261008.json';write(vp,proof)
rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp);assert not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results']);receipt=dict(proof,type='SOL_R5_CODEC_QA_PREPARATION_S1',verification_path=str(vp),verification_sha256=sha(vp));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(rp,receipts)
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'];comm.update(sol_status='R5_CODEC_PREPARATION_COMPLETED_MASTER_ACCEPTED_IDLE',sol_latest_result=receipt,last_sol_cursor=poll['cursor'],updated_at=at);write(cp,comm)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',last_result_id=c['result_id'],latest_review=str(review),current_runtime_idle_verified=True);state['updated_at']=at
for d in state['deliveries']:
 if d.get('delivery_id')==c['delivery_id']:d.update(status='COMPLETED_PREPARATION_MASTER_REVIEWED',result_id=c['result_id'],master_disposition=str(review))
write(sp,state)
bp=R/'Dispatcher/MASTER_A_TASKS.json';board=read(bp);t=board['tasks'][-1];assert t['dispatch_id']=='WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046'
assert not any(x['path']==str(Q/'EVIDENCE_MANIFEST.json') for x in t['preservation_policy']['qa_preserved_manifests'])
original_policy_sha=hashlib.sha256(json.dumps(t['preservation_policy'],sort_keys=True).encode()).hexdigest().upper()
t['preservation_policy']['qa_preserved_manifests'].append({'path':str(Q/'EVIDENCE_MANIFEST.json'),'sha256':sha(Q/'EVIDENCE_MANIFEST.json')})
t['additional_qa_protection_after_dispatch']={'at':at,'manifest':str(Q/'EVIDENCE_MANIFEST.json'),'sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'previous_qa_files':1222,'current_qa_files':1241,'initial_scope_baseline_and_sent_wp_unchanged':True};board['updated_at']=at;write(bp,board)
pres=checker.inspect_preservation(t);pp=H/'coordination/MASTER_R5_PRESERVATION_AFTER_QA_PREP_20261008.json';write(pp,pres)
extra_errors=[x for x in pres['preservation_errors'] if 'Steam' not in x];assert len(pres['qa_preservation_checks'])==1241
delta={'at':at,'event_id':'SOL-R5-CODEC-PREP-COMPLETE-MASTER-20261008-01','type':'QA_PREPARATION_MASTER_ACCEPTED','result_id':c['result_id'],'proof':str(vp),'proof_sha256':sha(vp),'master_verdict':proof['master_verdict'],'a_dispatch_id':t['dispatch_id'],'a_completion_exists':Path(t['completion_path']).exists(),'a_extra_preservation_errors':extra_errors,'preservation_proof':str(pp),'policy_addition':t['additional_qa_protection_after_dispatch'],'previous_policy_json_sha256':original_policy_sha,'new_a_wp':False,'new_qa_wp':False,'scheduler_changed':False,'closure_changed':False}
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(delta,ensure_ascii=False)+'\n')
paragraph=f'''\n\n## LOCAL-SOL-R5-CODEC-PREP-S1-COMPLETE — {at}\nOriginal Sol {c['result_id']}/{c['delivery_id']} matches actual completed/idle/cursor33. Master ACCEPTED_QA_PREPARATION_NO_R5_CANDIDATE_VERDICT;19 evidence +2089 protected unique path SHA/size matched. Historical8family65leaf matrix/18 normal-control/12 provenance criteria adopted as preparation only,upstream CLR width/enum metadata pending;controls executed0,R5 NOT_REVIEWED/runtime E2 NOT_RELEASED. Same A R5 IN_PROGRESS/ACK verified,completion observed={delta['a_completion_exists']};no duplicate/new WP/scheduler change. New preparation19 additively protected current QA1241 without changing initial baseline/sent WP;archive19/prior619/Pipeline206 checked,current fixed source additional errors={len(extra_errors)},known installed incident unchanged OPEN. Same hourly ACTIVE lifecycle remains. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {vp};preservation {pp}\n'''
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md',R/'AGENTS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
print(json.dumps({'at':at,'master_verdict':proof['master_verdict'],'artifact_count':len(checks),'protected_paths':len(after),'a_terminal_exists':delta['a_completion_exists'],'a_extra_preservation_errors':extra_errors,'qa_protected_files_now':1241,'next_action':'same A WP;Sol awaits frozen candidate;no new dispatch'},ensure_ascii=False))
