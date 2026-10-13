from pathlib import Path
import json,hashlib,datetime,sys,struct
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008'
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
def verify(row,workspace=True):
 p=Path(row['path']);assert p.exists(),p
 if workspace:assert p.resolve().is_relative_to(R),p
 assert sha(p)==row['sha256'],p
 assert p.stat().st_size==row.get('bytes',row.get('size',p.stat().st_size)),p
c=read(Q/'COMPLETION.json');i=read(Q/'RESULT_INDEX.json');m=read(Q/'EVIDENCE_MANIFEST.json');at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert c['delivery_id']=='SOL-GATE05-R5-CODEC-INDEPENDENT-S1-20261008-01' and c['wp_id']=='WP_QA_ENGINE_GATE05_R5_CODEC_INDEPENDENT' and c['wp_revision']=='S1'
assert c['result_id']==m['result_id']==i['result_id'] and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='724CBD6E216AE9B2CBFC39536A5437871147D18FD699E972CC19684DE52C8DFC'
for p,v in [(Q/'EVIDENCE_MANIFEST.json',c['evidence_manifest_sha256']),(Q/'RESULT_INDEX.json',c['result_index_sha256']),(Path(c['report_path']),c['report_sha256']),(Path(c['ack_completion_binding_path']),c['ack_completion_binding_sha256'])]:assert sha(p)==v
assert len(m['files'])==101
for row in m['files']:verify(row)
before={x['path']:x for x in rows(read(Q/'PRESERVATION_BEFORE.json'))};after={x['path']:x for x in rows(read(Q/'PRESERVATION_AFTER.json'))}
assert set(before)==set(after) and len(after)==2233
for k,v in after.items():
 verify(v);assert v['sha256']==before[k]['sha256']
 if 'bytes' in v and 'bytes' in before[k]:assert v['bytes']==before[k]['bytes']
pre=read(Q/'PRE_RUN2_MANIFEST.json');post=read(Q/'POST_RUN2_IDENTITY.json');tool=read(Q/'RUN2_TOOL_PROOF.json');normal=read(Q/'NORMAL_RESULTS.json');oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json')
assert len(pre['files'])==len(post['files'])==140 and pre['files']==post['files']
for row in pre['files']:verify(row,False)
assert pre['run_id']==post['run_id']==normal['run_id']==c['final_run_id']
assert tool['exit_code']==post['actual_tool_exit_code']==c['actual_final_tool_exit_code']==0
assert sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
assert (Q/'RUN2_RAW.txt').read_text(encoding='utf-8-sig').splitlines()==tool['output'].splitlines()
assert normal['normal_case_count']==6 and normal['historical_leaf_count']==65 and len(normal['results'])==17 and all(x['status']=='PASS' for x in normal['results'])
assert normal['selected_sha256']==c['selected_sha256']=='930B69D012F34BFD3BB50F97B86629BAEA082D201A3A81696549DF1450075AE8'
assert normal['selected_mvid']==c['selected_mvid']=='0e6b7cca-e02c-4af5-97da-5de31ec7aec3'
assert c['qa_runner_builds']==1 and c['managed_codec_runs']==2
assert all(c[k]==0 for k in ['production_builds','production_modifications','provider_cache_game_native_operator_calls','original_a_runner_or_tc11_runs','adverse_reproductions'])
assert not c['runtime_e2_released'] and not c['closure_changed']
assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(normal['at'])<datetime.datetime.fromisoformat(post['at'])
canonical=[]
for name in oracle['cases']:
 p=Q/(name+'.canonical.json');arch=Q/'RUN1_ARCHIVE'/(name+'.canonical.json')
 assert p.read_bytes()==arch.read_bytes(),name
 assert sha(p)==(Q/(name+'.sha256.txt')).read_text().strip()
 checks=read(Q/(name+'.semantic_checks.json'));assert checks and all(x['matched'] for x in checks)
 for row in checks:
  e=json.loads(row['expected']);a=json.loads(row['actual'])
  if row['kind']=='float32 exact bits':assert struct.pack('<f',float(e))==struct.pack('<f',float(a))
  else:assert e==a
 canonical.append({'case':name,'sha256':sha(p),'semantic_leaves':len(checks),'across_process_bytes_matched':True})
assert len(read(Q/'HISTORICAL65_FIELD_RESULTS.json'))==65
boundary=read(Q/'BOUNDARY_OBSERVATIONS.json');assert boundary['set_input_order_bytes_equal'] is False
snap=H/'coordination/MASTER_SOL_R5_CODEC_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261008.json';s=read(snap);p=json.loads(next(x['text'] for x in s['content'] if x['type']=='text'))['polls'][0]
assert p['latestTurn']['id']=='01a11ae8-7f1c-7953-9081-2bd07fb7602b' and p['latestTurn']['status']=='completed' and p['thread']['status']['type']=='idle'
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and sha(Path(transport['proof_path']))==transport['proof_sha256']
comm=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id']
receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
review=H/'MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_INDEPENDENT_S1_20261008.md'
review.write_text('''# R5 codec independent QA Master review

**ACCEPTED_SCOPED_NORMAL_CODEC_UNIT_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED**. Original Sol completion matches actual completed/idle turn and cursor38. Master independently checked101 evidence SHA/size,2233 protected unique paths,140 final-run pre/post files (including actual tooling/CLR dependencies), tool exit0/raw linkage, six cross-process canonical byte pairs and semantic row values. Master production/runner execution/build0; QA-owned runner build1 and pure normal managed codec runs2.

Selected frozen Debug SHA930B69D012F34BFD3BB50F97B86629BAEA082D201A3A81696549DF1450075AE8 / MVID0e6b7cca-e02c-4af5-97da-5de31ec7aec3. Six normal SYNTHETIC_CODEC_INPUT cases,17 assertions/run,65 historical leaf semantics and BASE102 observed leaves pass. Production Serialize/Deserialize typed DTO transport preserves observed values/float32 bits/Int64 above binary64 exact range/Unicode/null versus empty and supplied ordered sequences. This is independent codec unit evidence for this exact candidate. No loaded-content profile, provider/cache, native/game/operator/promotion or complete authority proof is released. Changed candidates require fresh independent QA.

Static R5-M02/03/04/05/06/07 remain revision required. Missing fields can become constructor defaults; null inventory/child/class fallbacks and patch/settings count-only coverage do not establish supported required material observation. Valid optional null/empty or justified semantic normalization remains permitted. The serializer preserves input order; two legitimate Biome Def set orders produce different bytes. Adopt explicit canonical sorted-input validation or normalization for declared sets, while preserving material order/multiplicity for active mods/verbs/Hediff stages/comps until independence is proved. This observation is not automatically a whole-gate runtime failure or a ban on every sort.

QA upstream metadata corrects the preparation matrix provisional JobDef.checkOverrideOnDamage boolean to Verse.CheckJobOverrideOnDamageMode enum. FoodPreferability enum is also observed. Both R5 DTO members carry string representations. Old preparation/report bytes remain preserved; this review and the independent report control their interpretation. Other unobserved upstream types/widths remain unobserved.

Producer TC11 catch-all predicate and environmental ECall failure cannot certify intended admission failure. QA did not execute that producer runner or adverse fixtures. Producer12 labels do not extend actual assertions; normal QA fills only its own supported codec scope. First QA run had unpinned resolved CLR dependencies/numeric exit missing; same built runner/input fresh run2 pre-pins those dependencies and records actual exit0/post identities. This repairs QA unit provenance prospectively, not producer evidence retroactively. Release actual MVID7552980a-c4e1-4126-9451-e2114be623ae controls; wrong producer Debug copy is preserved as evidence.

Next approved technical direction is narrow R6 supported codec contract/disposition/collector mapping/canonical boundary and honest final packaging. WorkerBridge/csproj/Census prefix remain fixed; operator/native/control-plane follow separately. No copied or inherited runtime PASS. Original Sol waits for a new exact frozen candidate, with no redundant preparation WP.

Engine002006/Pipeline007/current schema7/G-Q1 remain OPEN,Foundation HOLD. Pipeline REV6-R1 observed controls pass/full gate inconclusive. Installed identity incident remains OPEN/actor unknown, no restore or normalization. No defect closure or product release.
''',encoding='utf-8')
proof={'at':at,'type':'SOL_R5_CODEC_INDEPENDENT_MASTER_REVIEW','result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'wp_revision':'S1','completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':101,'protected_unique_paths_master_rehashed':2233,'final_pre_post_files':140,'actual_exit_code':0,'normal_cases':canonical,'historical_leaf_semantics':65,'assertions_per_run':17,'qa_runner_builds':1,'qa_codec_runs':2,'master_candidate_and_runner_execution_builds':0,'actual_thread':p,'direct_report_transport_verified':True,'master_review_path':str(review),'master_review_sha256':sha(review),'master_verdict':'ACCEPTED_SCOPED_NORMAL_CODEC_UNIT_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','upstream_correction':'JobDef.checkOverrideOnDamage=Verse.CheckJobOverrideOnDamageMode enum;provisional prep boolean superseded without original modification'}
vp=H/'coordination/MASTER_SOL_R5_CODEC_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261008.json';write(vp,proof);receipt=dict(proof,verification_path=str(vp),verification_sha256=sha(vp))
receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(R/'Dispatcher/MASTER_RECEIPTS.json',receipts)
comm.update(sol_status='R5_CODEC_INDEPENDENT_COMPLETED_MASTER_ACCEPTED_IDLE',sol_latest_result=receipt,last_sol_cursor=p['cursor'],updated_at=at);comm['sol_current_delivery'].update(status='COMPLETED_MASTER_REVIEWED',result_id=c['result_id']);write(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',comm)
state=read(H/'DISPATCHER_STATE.json');state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',last_result_id=c['result_id'],latest_review=str(review),current_runtime_idle_verified=True);state['updated_at']=at
for d in state['deliveries']:
 if d.get('delivery_id')==c['delivery_id']:d.update(status='COMPLETED_SCOPED_CODEC_QA_MASTER_REVIEWED',result_id=c['result_id'],master_disposition=str(review))
write(H/'DISPATCHER_STATE.json',state)
paragraph=f'\n\n## LOCAL-SOL-R5-CODEC-INDEPENDENT-S1-COMPLETE — {at}\nOriginal Sol {c["result_id"]}/{c["delivery_id"]} actual completed/idle/cursor38. Master {proof["master_verdict"]};101 evidence/2233 protected unique paths/140 final pre-post identities/tool exit0/six cross-process canonical pairs checked. QA runner build1,pure codec runs2,17 assertions/run,historical65leaf/BASE102 observed;production/provider/cache/game/native/operator/adverse0. Provisional prep JobDef boolean corrected to actual enum without old-byte changes. New A R6 technical direction codec contract/disposition/canonical boundary/packaging approved to prepare,NOT SENT until fresh CU proof. Same hourly monitor PAUSED until actual A delivery;Sol idle waits new frozen candidate. No closure;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {vp}\n'
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'AGENTS.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(receipt,event_id='SOL-R5-CODEC-INDEPENDENT-COMPLETE-MASTER-20261008-01'),ensure_ascii=False)+'\n')
print(json.dumps({'verdict':proof['master_verdict'],'files':101,'protected':2233,'prepost':140,'canonical':canonical,'review':str(review)},ensure_ascii=False))
