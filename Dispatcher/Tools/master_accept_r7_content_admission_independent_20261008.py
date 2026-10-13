from pathlib import Path
import json,hashlib,datetime,sys,struct
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008'
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
assert c['delivery_id']=='SOL-GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008-01' and c['wp_id']=='WP_QA_ENGINE_GATE05_R7_CONTENT_ADMISSION_INDEPENDENT' and c['wp_revision']=='S1'
assert c['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008-a860491cbc81403eb91650ce707f26cc' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='20F6CFFAFCF14D3C46EF2F8D425D5C456493D9BD0538A6252D2A836C56CF4955'
for path,expected in [(Q/'EVIDENCE_MANIFEST.json',c['evidence_manifest_sha256']),(Q/'RESULT_INDEX.json',c['result_index_sha256']),(Path(c['report_path']),c['report_sha256']),(Path(c['ack_completion_binding_path']),c['ack_completion_binding_sha256'])]:assert sha(path)==expected
assert len(m['files'])==163
for x in m['files']:verify(x)
before={x['path']:x for x in rows(read(Q/'PRESERVATION_BEFORE.json'))};after={x['path']:x for x in rows(read(Q/'PRESERVATION_AFTER.json'))};assert set(before)==set(after) and len(after)==2701
for k,x in after.items():verify(x);assert x['sha256']==before[k]['sha256'] and x.get('bytes')==before[k].get('bytes')
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');run_records=[]
for n in [1,2]:
 pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(Q/f'POST_RUN{n}_IDENTITY.json');tool=read(Q/f'RUN{n}_TOOL_PROOF.json');assert pre['files']==post['files'] and len(pre['files'])==141
 for x in pre['files']:verify(x,False)
 assert pre['run_id']==post['run_id']==c['run_ids'][n-1] and pre['culture']==c['cultures'][n-1]
 assert tool['exit_code']==post['actual_tool_exit_code']==0 and sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
 raw=(Q/f'RUN{n}_RAW.txt').read_text(encoding='utf-8-sig');assert raw.splitlines()==tool['output'].splitlines() and sum(x.startswith('PASS ') for x in raw.splitlines())==27
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 run_records.append({'run_id':pre['run_id'],'culture':pre['culture'],'prepost_files':141,'tool_exit':0,'assertions':27,'runner_sha256':pre['runner']['exe_sha256'],'runner_mvid':pre['runner']['exe_mvid']})
normal=read(Q/'NORMAL_RESULTS.json');assert len(normal['results'])==27 and all(x['status']=='PASS' for x in normal['results']) and normal['normal_case_count']==6 and normal['historical_leaf_count']==65
assert c['selected_sha256']==normal['selected_sha256']=='223B4055C0AFAA6F30488C9787AE6F68D65D62F395CFCA722EDA83674975CD2A' and c['selected_mvid']=='bdf94567-be4d-4270-9a70-dbf2df9b5b4a'
assert c['qa_runner_builds']==1 and c['managed_codec_runs']==2 and all(c[k]==0 for k in ['production_builds','production_modifications','provider_cache_game_native_operator_calls','old_a_or_qa_runner_runs','invalid_or_rejection_tests','adverse_reproductions'])
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
snap=H/'coordination/MASTER_SOL_R7_CONTENT_ADMISSION_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261008.json';d=read(snap);poll=json.loads(next(x['text'] for x in d['content'] if x['type']=='text'))['polls'][0];assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11bda-0e86-7330-ad00-d21baf5fd5b0'
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and sha(Path(transport['tool_proof_path']))==transport['tool_proof_sha256']
comm=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
review=H/'MASTER_REVIEW_ENGINE_GATE05_R7_CONTENT_ADMISSION_INDEPENDENT_S1_20261008.md'
assert review.exists()
loaded=read(Q/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_managed_hashes_match_prerun']
for row in loaded['rows']:
 pre=read(Q/f'PRE_RUN{row["stage"]}_MANIFEST.json');mapping={x['path'].lower():x for x in pre['files']};assert row['pre_pinned'] and row['path'].lower() in mapping and mapping[row['path'].lower()]['sha256']==row['sha256'];assert sha(Path(row['path']))==row['sha256']
assert read(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
admitted=[]
for name in ['BASE','NORMAL_REVISION_B']:
 canonical=Q/(name+'.admitted.canonical.json');arch=Q/'RUN1_ARCHIVE'/(name+'.admitted.canonical.json');assert canonical.read_bytes()==arch.read_bytes()==(Q/(name+'.canonical.json')).read_bytes()
 observation=read(Q/(name+'.admission_observation.json'));assert observation['success'] and observation['reason']=='' and observation['canonical_sha256']==sha(canonical) and observation['canonical_utf8_bytes']==len(canonical.read_bytes())
 for x in read(Q/(name+'.admission_checks.json')):
  assert x['matched'];e=json.loads(x['expected']);a=json.loads(x['actual'])
  if x['kind']=='float32 exact bits':assert struct.pack('<f',float(e))==struct.pack('<f',float(a))
  else:assert e==a
 admitted.append({'case':name,'sha256':sha(canonical),'cross_process_bytes_match':True,'expected_semantics_match':True,'actual_utf8_bytes':len(canonical.read_bytes())})
import subprocess
runner_meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),c['runner']['exe_path'],c['runner']['pdb_path']],check=True,capture_output=True,text=True).stdout)
assert runner_meta['mvid']==c['runner']['exe_mvid'] and runner_meta['codeviewMatched'] and all(x['matched'] for x in runner_meta['documents'])
proof={'at':at,'type':'SOL_R7_CONTENT_ADMISSION_INDEPENDENT_MASTER_REVIEW','result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'wp_revision':'S1','completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':163,'protected_unique_paths_master_rehashed':2701,'runs':run_records,'cases':cases,'historical_leaf_semantics':65,'positive_helper_cases_per_run':2,'positive_try_admit_cases_per_run':2,'admitted_cases':admitted,'all_actual_loaded_pre_pins_verified':True,'runner_pe_metadata_master':runner_meta,'actual_thread':poll,'direct_transport_verified':True,'master_execution_builds':0,'master_review_path':str(review),'master_review_sha256':sha(review),'master_verdict':'ACCEPTED_SCOPED_R7_POSITIVE_CODEC_ADMISSION_HELPER_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'};vp=H/'coordination/MASTER_SOL_R7_CONTENT_ADMISSION_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261008.json';write(vp,proof);receipt=dict(proof,verification_path=str(vp),verification_sha256=sha(vp));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(R/'Dispatcher/MASTER_RECEIPTS.json',receipts)
comm.update(sol_status='R7_CONTENT_ADMISSION_INDEPENDENT_COMPLETED_MASTER_ACCEPTED_IDLE',sol_latest_result=receipt,last_sol_cursor=poll['cursor'],updated_at=at);comm['sol_current_delivery'].update(status='COMPLETED_MASTER_REVIEWED',result_id=c['result_id']);write(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',comm)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',last_result_id=c['result_id'],latest_review=str(review),current_runtime_idle_verified=True);state['updated_at']=at
for d in state['deliveries']:
 if d.get('delivery_id')==c['delivery_id']:d.update(status='COMPLETED_SCOPED_R7_CODEC_QA_MASTER_REVIEWED',result_id=c['result_id'],master_disposition=str(review))
write(sp,state)
paragraph=f'\n\n## LOCAL-SOL-R7-CONTENT-ADMISSION-INDEPENDENT-S1-COMPLETE — {at}\nOriginal Sol {c["result_id"]}/{c["delivery_id"]} matches actual completed/idle/cursor47. Master {proof["master_verdict"]};163 evidence/2701 protected unique paths/both141 pre-post identities/exit0 and6codec+2admitted cross-process canonical pairs checked;actual loaded managed pre-pins and runner PE/PDB verified. QA build1,en-US/de-DE positive processes2,27assertions/run,historical65leaf/BASE157,Validate2+TryAdmit2cases/run;production/provider/cache/game/native/operator/rejection/adverse0,Master candidate/build0. Actual computed content validation linkage/three contract fields credited;patch-settings label-only/child filtering/observed-empty/type/version/key policy/producer provenance gaps remain. R8 supported-disposition narrow corrective direction approved to prepare NOT SENT until fresh A idle/CU proof;same hourly PAUSED until actual A delivery,original Sol waits new admitted candidate. No runtime E2/closure;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {vp}\n'

for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'AGENTS.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(receipt,event_id='SOL-R7-CONTENT-ADMISSION-INDEPENDENT-COMPLETE-MASTER-20261008-01'),ensure_ascii=False)+'\n')
print(json.dumps({'verdict':proof['master_verdict'],'evidence':163,'protected':2701,'runs':run_records,'review':str(review)},ensure_ascii=False))
