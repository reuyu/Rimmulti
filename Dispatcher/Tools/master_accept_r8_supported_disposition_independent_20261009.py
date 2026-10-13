"""Collect independent R8 normal semantic FAIL evidence;no candidate/runner execution."""
from pathlib import Path
import json,hashlib,datetime,sys,struct,subprocess
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R8-SUPPORTED-DISPOSITION-INDEPENDENT-S1-20261009'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify(x,workspace=True):
 p=Path(x['path']);assert p.exists()
 if workspace:assert p.resolve().is_relative_to(R)
 assert sha(p)==x['sha256'] and p.stat().st_size==x.get('bytes',x.get('size',p.stat().st_size)),p
def equal(x):
 e=json.loads(x['expected']);a=json.loads(x['actual'])
 if x['kind']=='float32 exact bits':return struct.pack('<f',float(e))==struct.pack('<f',float(a))
 if x['kind']=='bool':return isinstance(a,bool) and e==a
 return e==a
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json')
assert c['delivery_id']=='SOL-GATE05-R8-SUPPORTED-DISPOSITION-INDEPENDENT-S1-20261009-01' and c['wp_id']=='WP_QA_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION_INDEPENDENT' and c['wp_revision']=='S1'
assert c['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R8-SUPPORTED-DISPOSITION-INDEPENDENT-S1-20261009-95208a162c494ac5a7bfc6e84a72f911' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='B3456CEE1BC80854BE32AC5393B1E7B6619C45A84E445EB93F7D1AE728D88AC9'
for path,expected in [(Q/'EVIDENCE_MANIFEST.json',c['evidence_manifest_sha256']),(Q/'RESULT_INDEX.json',c['result_index_sha256']),(Path(c['report_path']),c['report_sha256']),(Path(c['ack_completion_binding_path']),c['ack_completion_binding_sha256'])]:assert sha(path)==expected
assert len(m['files'])==182
for x in m['files']:verify(x)
before={x['path']:x for x in read(Q/'PRESERVATION_BEFORE.json')['files']};after={x['path']:x for x in read(Q/'PRESERVATION_AFTER.json')['files']};assert set(before)==set(after) and len(after)==2944
for k,x in after.items():verify(x);assert x['sha256']==before[k]['sha256'] and x.get('size',x.get('bytes'))==before[k].get('size',before[k].get('bytes'))
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');reg=read(Q/'NORMAL_SEMANTIC_REGRESSION.json');failed_ids={x['id'] for x in reg['failed_predicates']};assert len(failed_ids)==4 and reg['root_cause_dimensions']==1 and reg['expected'] is None and reg['actual']=='1.6'
runs=[]
for n in [1,2]:
 pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(Q/f'POST_RUN{n}_IDENTITY.json');tool=read(Q/f'RUN{n}_TOOL_PROOF.json');assert pre['files']==post['files'] and len(pre['files'])==106
 for x in pre['files']:verify(x,False)
 assert pre['run_id']==post['run_id']==c['run_ids'][n-1] and pre['culture']==c['cultures'][n-1]
 assert tool['exit_code']==post['actual_tool_exit_code']==1 and sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
 raw=(Q/f'RUN{n}_RAW.txt').read_text(encoding='utf-8-sig');assert raw.splitlines()==tool['output'].splitlines()
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==41 and sum(x.startswith('FAIL ') for x in raw.splitlines())==4
 assert {x.split(' ',2)[1] for x in raw.splitlines() if x.startswith('FAIL ')}==failed_ids
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 runs.append({'run_id':pre['run_id'],'culture':pre['culture'],'prepost_files':106,'tool_exit':1,'pass_assertions':41,'fail_assertions':4,'runner_sha256':pre['runner']['exe_sha256'],'runner_mvid':pre['runner']['exe_mvid']})
normal=read(Q/'NORMAL_RESULTS.json');assert len(normal['results'])==45 and sum(x['status']=='PASS' for x in normal['results'])==41 and {x['id'] for x in normal['results'] if x['status']=='FAIL'}==failed_ids
assert c['selected_sha256']==normal['selected_sha256']=='F82F3B08FF8D7D129F520DE054E7BAB666728B9909D9C9C2E955E5E583EBE9D5' and c['selected_mvid']=='348b49f3-74f8-4643-9a2f-4a1dc5fb9a41'
assert c['qa_runner_builds']==1 and c['managed_codec_runs']==2 and all(c[k]==0 for k in ['production_builds','production_modifications','provider_cache_game_native_operator_calls','old_a_or_qa_runner_runs','invalid_or_rejection_tests','tied_or_adverse_reproductions'])
cases=[]
for name in oracle['cases']:
 p=Q/(name+'.canonical.json');arch=Q/'RUN1_ARCHIVE'/(name+'.canonical.json');assert p.read_bytes()==arch.read_bytes() and sha(p)==(Q/(name+'.sha256.txt')).read_text().strip()
 mismatches=[]
 for suffix in ['semantic_checks','normalize_checks','transport_checks']:
  checks=read(Q/(name+'.'+suffix+'.json'));assert checks
  for x in checks:
   actual_equal=equal(x);assert x['matched']==actual_equal
   if not actual_equal:
    assert name=='OPTIONAL_UNKNOWN_VERSION' and suffix!='transport_checks' and x['path']=='activeMods[0].modVersion' and json.loads(x['expected']) is None and json.loads(x['actual'])=='1.6'
    mismatches.append({'stage':suffix,'field':x['path'],'expected':None,'actual':'1.6'})
 cases.append({'case':name,'sha256':sha(p),'cross_process_bytes_match':True,'semantic_verdict':'FAIL' if mismatches else 'PASS','mismatch_rows':mismatches})
assert len(cases)==7 and sum(x['semantic_verdict']=='FAIL' for x in cases)==1 and len(read(Q/'HISTORICAL65_FIELD_RESULTS.json'))==65
admitted=[]
for name in ['BASE','NORMAL_REVISION_B']:
 p=Q/(name+'.admitted.canonical.json');assert p.read_bytes()==(Q/'RUN1_ARCHIVE'/(name+'.admitted.canonical.json')).read_bytes()==(Q/(name+'.canonical.json')).read_bytes()
 obs=read(Q/(name+'.admission_observation.json'));assert obs['success'] and obs['reason']=='' and obs['canonical_sha256']==sha(p) and obs['canonical_utf8_bytes']==len(p.read_bytes())
 assert all(x['matched'] and equal(x) for x in read(Q/(name+'.admission_checks.json')))
 admitted.append({'case':name,'sha256':sha(p),'semantic_verdict':'PASS','cross_process_bytes_match':True})
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and transport['completion_sha256']==sha(Q/'COMPLETION.json') and sha(Path(transport['tool_proof_path']))==transport['tool_proof_sha256']
loaded=read(Q/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_managed_hashes_match_prerun']
for row in loaded['rows']:
 mapping={x['path'].lower():x for x in read(Q/f'PRE_RUN{row["stage"]}_MANIFEST.json')['files']};assert row['pre_pinned'] and mapping[row['path'].lower()]['sha256']==row['sha256']==sha(Path(row['path']))
assert read(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),c['runner']['exe_path'],c['runner']['pdb_path']],check=True,capture_output=True,text=True).stdout);assert meta['mvid']==c['runner']['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
snap=C/'MASTER_SOL_R8_SUPPORTED_DISPOSITION_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261009.json';poll=json.loads(next(x['text'] for x in read(snap)['content'] if x['type']=='text'))['polls'][0];assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11c2f-b048-73b0-a61d-a1eccf88b883'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp);assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
review=H/'MASTER_REVIEW_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION_INDEPENDENT_S1_20261009.md';assert review.exists()
proof={'at':at,'type':'SOL_R8_NORMAL_CODEC_SEMANTIC_FAIL_MASTER_REVIEW','result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'wp_revision':'S1','completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':182,'protected_unique_paths_master_rehashed':2944,'runs':runs,'cases':cases,'admitted_cases':admitted,'positive_validate_cases_per_run':2,'positive_try_admit_cases_per_run':2,'all_actual_loaded_pre_pins_verified':True,'runner_metadata_master':meta,'actual_thread':poll,'regression_path':str(Q/'NORMAL_SEMANTIC_REGRESSION.json'),'regression_sha256':sha(Q/'NORMAL_SEMANTIC_REGRESSION.json'),'normal_semantic_root_causes':1,'defect_id':'ENGINE-CONTENT-VERSION-SEMANTIC-20261009-01','defect_severity':'High','master_execution_builds':0,'master_review_path':str(review),'master_review_sha256':sha(review),'master_verdict':'ACCEPTED_R8_NORMAL_CODEC_SEMANTIC_FAIL_HELPERS_SCOPED_PASS_REVISION_REQUIRED_NATIVE_UNTESTED','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp=C/'MASTER_SOL_R8_SUPPORTED_DISPOSITION_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261009.json';write(vp,proof);receipt=dict(proof,verification_path=str(vp),verification_sha256=sha(vp));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(rp,receipts)
comm.update(sol_status='R8_SUPPORTED_DISPOSITION_INDEPENDENT_COMPLETED_MASTER_ACCEPTED_FAIL_IDLE',sol_latest_result=receipt,last_sol_cursor=poll['cursor'],updated_at=at);comm['sol_current_delivery'].update(status='COMPLETED_MASTER_REVIEWED_NORMAL_SEMANTIC_FAIL',result_id=c['result_id']);write(cp,comm)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',last_result_id=c['result_id'],latest_review=str(review),current_runtime_idle_verified=True);state['updated_at']=at
for d in state['deliveries']:
 if d.get('delivery_id')==c['delivery_id']:d.update(status='COMPLETED_R8_NORMAL_SEMANTIC_FAIL_MASTER_REVIEWED',result_id=c['result_id'],master_disposition=str(review))
write(sp,state)
paragraph=f'\n\n## LOCAL-SOL-R8-SUPPORTED-DISPOSITION-INDEPENDENT-S1-COMPLETE — {at}\nOriginal Sol {c["result_id"]}/{c["delivery_id"]} matches actual completed/idle/cursor52. Master {proof["master_verdict"]};182 evidence/2944 protected unique paths/both106 pre-post identities/exit1 and41PASS+4FAIL each checked;7codec+2admitted byte pairs,one normal semantic root FAIL. Optional unknown modVersion=null becomes compatibility1.6 in canonical output;false transport preservesnull. High {proof["defect_id"]} OPEN,targeted repair+fresh independent QA required. Fullydeclared positive Validate2/TryAdmit2 PASS alone not whole codec/native PASS. QA build1,process2;production/provider/cache/game/native/operator/rejection/tied/adverse0,Master execution/build0. Child observation/key improvements credited;actual supported boundary/default/observation/producer graph gaps remain. Narrow R9 VERSION_MEANING corrective direction approved to prepare NOT SENT until fresh A idle/CU proof;other content-disposition/native gates separate. Same hourly PAUSED until actual A delivery,Sol waits new candidate;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {vp}\n'
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'AGENTS.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(receipt,event_id='SOL-R8-INDEPENDENT-COMPLETE-MASTER-20261009-01'),ensure_ascii=False)+'\n')
print(json.dumps({'verdict':proof['master_verdict'],'evidence':182,'protected':2944,'runs':runs,'defect':proof['defect_id'],'next_A':'R9_NOT_SENT'},ensure_ascii=False))
