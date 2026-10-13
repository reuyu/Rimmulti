from pathlib import Path
import json,hashlib,datetime,sys,struct
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(d):
 if isinstance(d,dict):
  if 'path' in d and 'sha256' in d and Path(d['path']).is_absolute():yield d
  if 'manifest' in d and 'manifest_sha256' in d:yield {'path':d['manifest'],'sha256':d['manifest_sha256']}
  for v in d.values():yield from rows(v)
 elif isinstance(d,list):
  for v in d:yield from rows(v)
def verify(x,workspace=True):
 p=Path(x['path']);assert p.exists()
 if workspace:assert p.resolve().is_relative_to(R)
 assert sha(p)==x['sha256'] and p.stat().st_size==x.get('bytes',x.get('size',p.stat().st_size)),p
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json')
assert c['delivery_id']=='SOL-GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008-01' and c['wp_id']=='WP_QA_ENGINE_GATE05_R6_CODEC_CONTRACT_INDEPENDENT' and c['wp_revision']=='S1'
assert c['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008-562ad497021b4c36bd59c08df730b7ed' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='95A205969E9BA30588DECFA1BF46E8E3FD32A4EEB79855C70811D19C0F5BAC19'
for path,expected in [(Q/'EVIDENCE_MANIFEST.json',c['evidence_manifest_sha256']),(Q/'RESULT_INDEX.json',c['result_index_sha256']),(Path(c['report_path']),c['report_sha256']),(Path(c['ack_completion_binding_path']),c['ack_completion_binding_sha256'])]:assert sha(path)==expected
assert len(m['files'])==147
for x in m['files']:verify(x)
before={x['path']:x for x in rows(read(Q/'PRESERVATION_BEFORE.json'))};after={x['path']:x for x in rows(read(Q/'PRESERVATION_AFTER.json'))};assert set(before)==set(after) and len(after)==2453
for k,x in after.items():verify(x);assert x['sha256']==before[k]['sha256'] and x.get('bytes')==before[k].get('bytes')
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');run_records=[]
for n in [1,2]:
 pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(Q/f'POST_RUN{n}_IDENTITY.json');tool=read(Q/f'RUN{n}_TOOL_PROOF.json');assert pre['files']==post['files'] and len(pre['files'])==141
 for x in pre['files']:verify(x,False)
 assert pre['run_id']==post['run_id']==c['run_ids'][n-1] and pre['culture']==c['cultures'][n-1]
 assert tool['exit_code']==post['actual_tool_exit_code']==0 and sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
 raw=(Q/f'RUN{n}_RAW.txt').read_text(encoding='utf-8-sig');assert raw.splitlines()==tool['output'].splitlines() and sum(x.startswith('PASS ') for x in raw.splitlines())==25
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 run_records.append({'run_id':pre['run_id'],'culture':pre['culture'],'prepost_files':141,'tool_exit':0,'assertions':25,'runner_sha256':pre['runner']['exe_sha256'],'runner_mvid':pre['runner']['exe_mvid']})
normal=read(Q/'NORMAL_RESULTS.json');assert len(normal['results'])==25 and all(x['status']=='PASS' for x in normal['results']) and normal['normal_case_count']==6 and normal['historical_leaf_count']==65
assert c['selected_sha256']==normal['selected_sha256']=='721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B' and c['selected_mvid']=='b3481641-2711-4b0e-96dd-db0983c2b689'
assert c['qa_runner_builds']==1 and c['managed_codec_runs']==2 and all(c[k]==0 for k in ['production_builds','production_modifications','provider_cache_game_native_operator_calls','old_a_or_qa_runner_or_tc11_tc13_runs','invalid_or_rejection_tests','adverse_reproductions'])
cases=[]
for name in oracle['cases']:
 p=Q/(name+'.canonical.json');arch=Q/'RUN1_ARCHIVE'/(name+'.canonical.json');assert p.read_bytes()==arch.read_bytes() and sha(p)==(Q/(name+'.sha256.txt')).read_text().strip()
 for suffix in ['semantic_checks','normalize_checks','transport_checks']:
  checks=read(Q/(name+'.'+suffix+'.json'));assert checks and all(x['matched'] for x in checks)
  for x in checks:
   e=json.loads(x['expected']);a=json.loads(x['actual'])
   if x['kind']=='float32 exact bits':assert struct.pack('<f',float(e))==struct.pack('<f',float(a))
   else:assert e==a
 cases.append({'case':name,'canonical_sha256':sha(p),'semantic_leaves':len(read(Q/(name+'.semantic_checks.json'))),'cross_process_bytes_match':True})
assert len(read(Q/'HISTORICAL65_FIELD_RESULTS.json'))==65 and read(Q/'BOUNDARY_OBSERVATIONS.json')['set_input_order_bytes_equal'] is True
snap=H/'coordination/MASTER_SOL_R6_CODEC_CONTRACT_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261008.json';d=read(snap);poll=json.loads(next(x['text'] for x in d['content'] if x['type']=='text'))['polls'][0];assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11b78-ed00-7da3-a6f4-3a4e17abbe05'
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and sha(Path(transport['tool_proof_path']))==transport['tool_proof_sha256']
comm=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
review=H/'MASTER_REVIEW_ENGINE_GATE05_R6_CODEC_CONTRACT_INDEPENDENT_S1_20261008.md'
review.write_text('''# R6 independent codec/helper QA Master disposition

**ACCEPTED_SCOPED_R6_POSITIVE_CODEC_HELPER_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED**. Original Sol report/terminal matches completed/idle actual turn/cursor42. Master independently checked147 evidence SHA/size,2453 protected unique paths,both141 pre/post identity rows,actual numeric exit0/0 and25 raw PASS rows/process,6 cross-process canonical byte pairs and semantic/normalization/transport check values. QA owned build1/positive managed processes2,en-US/de-DE. Master production/runner execution/build0.

Exact selected Debug721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B/MVIDb3481641-2711-4b0e-96dd-db0983c2b689. Historical65 leaf semantics,BASE149 observed leaves and fully declared positive helper2cases/run pass. Distinct-key set normalization now maps normal permutations to equal bytes,transport false preserves supplied order,ordered verbs/stages/comps/multiplicity remain preserved,and default normalization mutates the input DTO as observed. Same built runner in fresh en-US/de-DE processes yielded equal normal bytes. This closes no Engine defect and does not certify actual loaded content/authority/native/material noninterference.

Independent R6-M01~08 static qualifications are adopted. ValidateContract is definition-only/unwired and lacks complete declared required material coverage. Collector child skip/class/metadata/inventory/default/count fallbacks remain. Report-only patch/settings exclusion is not enforced in profile construction. Content contract version/coverage must be bound to the actual profile admission boundary. Key uniqueness/tie policy and in-place caller semantics remain explicit contract work. Valid optional absence/justified normalization is permitted;no universal all-Def/all-null/all-sort failure or exact global schema is imposed.

Producer21 artifacts/18 before-after rows/correct Debug and Release MVID/PDB are credited. TC13 cache calls are outside WP;TC11 format rejection is distinct from prior R5 ECall/catch and was not rerun. Producer labels do not establish complete semantic oracle/lifecycle/authority. Hardcoded pre-time/SDK8.0+/tooling-dependency/config/generated/raw graph gaps remain;fresh independent QA proof does not retroactively certify A chronology. Long-path partial stays unadmitted;valid shorter112 freeze governs.

Next narrow A R7 direction: wire actual content admission validation;make declared required/optional/disposition and unsupported patch/settings coverage executable;bind contract/coverage and canonical key/caller policy;positive normal semantic/provenance evidence only. Retain WorkerBridge/csproj/Census prefix fixed and operator/native as separate future work. Generic DTO codec transport can remain distinct from admitted loaded-profile construction. Neither a success flag nor simply disabling all profiles qualifies as demonstrated supported admission. Unobserved actual profile/runtime remains untested. No new runtime release is given.

New R7 WP still NOT SENT pending fresh A idle/CU proof. Existing hourly monitor PAUSED until actual new A delivery;original Sol waits fresh candidate. Engine002006/Pipeline007/current schema7/G-Q1 OPEN,Foundation HOLD;installed incident OPEN/actor unknown,no restore. No closure/release.
''',encoding='utf-8')
proof={'at':at,'type':'SOL_R6_CODEC_CONTRACT_INDEPENDENT_MASTER_REVIEW','result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'wp_revision':'S1','completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':147,'protected_unique_paths_master_rehashed':2453,'runs':run_records,'cases':cases,'historical_leaf_semantics':65,'positive_helper_cases_per_run':2,'actual_thread':poll,'direct_transport_verified':True,'master_execution_builds':0,'master_review_path':str(review),'master_review_sha256':sha(review),'master_verdict':'ACCEPTED_SCOPED_R6_POSITIVE_CODEC_HELPER_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'};vp=H/'coordination/MASTER_SOL_R6_CODEC_CONTRACT_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261008.json';write(vp,proof);receipt=dict(proof,verification_path=str(vp),verification_sha256=sha(vp));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(R/'Dispatcher/MASTER_RECEIPTS.json',receipts)
comm.update(sol_status='R6_CODEC_CONTRACT_INDEPENDENT_COMPLETED_MASTER_ACCEPTED_IDLE',sol_latest_result=receipt,last_sol_cursor=poll['cursor'],updated_at=at);comm['sol_current_delivery'].update(status='COMPLETED_MASTER_REVIEWED',result_id=c['result_id']);write(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',comm)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',last_result_id=c['result_id'],latest_review=str(review),current_runtime_idle_verified=True);state['updated_at']=at
for d in state['deliveries']:
 if d.get('delivery_id')==c['delivery_id']:d.update(status='COMPLETED_SCOPED_R6_CODEC_QA_MASTER_REVIEWED',result_id=c['result_id'],master_disposition=str(review))
write(sp,state)
paragraph=f'\n\n## LOCAL-SOL-R6-CODEC-CONTRACT-INDEPENDENT-S1-COMPLETE — {at}\nOriginal Sol {c["result_id"]}/{c["delivery_id"]} matches actual completed/idle/cursor42. Master {proof["master_verdict"]};147 evidence/2453 protected unique paths/both141 pre-post identities/exit0 and6 canonical cross-process pairs checked. QA runner build1,en-US/de-DE2positive runs,25assertions/run,historical65leaf/BASE149,positive helper2cases/run;production/provider/cache/game/native/operator/rejection/adverse0,Master execution/build0. Canonical/ordered comps/actual MVID improvements credited;unwired helper/required child disposition/document-only patch-settings exclusion/contract coverage binding/key and mutation/provenance gaps remain. R7 narrow admission/disposition follow-up approved to prepare NOT SENT until fresh A idle/CU proof;same hourly PAUSED until actual A delivery,Sol waits new candidate. No runtime E2/closure;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {vp}\n'
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'AGENTS.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(receipt,event_id='SOL-R6-CODEC-CONTRACT-INDEPENDENT-COMPLETE-MASTER-20261008-01'),ensure_ascii=False)+'\n')
print(json.dumps({'verdict':proof['master_verdict'],'evidence':147,'protected':2453,'runs':run_records,'review':str(review)},ensure_ascii=False))
