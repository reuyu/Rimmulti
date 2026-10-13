"""Independent Master evidence collection;no production/QA-runner execution/build."""
from pathlib import Path
import json,hashlib,datetime,sys,struct,subprocess
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def verify(x,workspace=True):
 p=Path(x['path']);assert p.is_file()
 if workspace:assert p.resolve().is_relative_to(R)
 assert sha(p)==x['sha256'] and p.stat().st_size==x.get('bytes',x.get('size',p.stat().st_size)),p
def same(x):
 e=json.loads(x['expected']);a=json.loads(x['actual'])
 if x['kind']=='float32 exact bits':return struct.pack('<f',float(e))==struct.pack('<f',float(a))
 if x['kind']=='bool':return type(e)==type(a)==bool and e==a
 if x['kind']=='integer exact Int64':return type(e)==type(a)==int and e==a
 if x['kind']=='string/codepoint':return type(e)==type(a)==str and e==a
 if x['kind']=='null':return e is None and a is None
 raise AssertionError(x['kind'])
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json')
assert c['result_id']==idx['result_id']==m['result_id']=='SOL-GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009-e519e8e7421c46e5b4e2808e7137be84'
assert c['wp_id']=='WP_QA_ENGINE_GATE05_R9_VERSION_MEANING_INDEPENDENT' and c['delivery_id']=='SOL-GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009-01' and c['wp_revision']=='S1' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='AF00A8872AD37828376B8DC5B2EFA3EEC5ED73FA14BDE49679031235E1DAC1D5'
for p,s in [(Q/'EVIDENCE_MANIFEST.json',c['evidence_manifest_sha256']),(Q/'RESULT_INDEX.json',c['result_index_sha256']),(Path(c['report_path']),c['report_sha256']),(Path(c['ack_completion_binding_path']),c['ack_completion_binding_sha256'])]:assert sha(p)==s
assert len(m['files'])==326
for x in m['files']:verify(x)
before={x['path']:x for x in read(Q/'PRESERVATION_BEFORE.json')['files']};after={x['path']:x for x in read(Q/'PRESERVATION_AFTER.json')['files']};assert before==after and len(after)==3206
for x in after.values():verify(x)
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');runs=[]
assert len(oracle['cases'])==12 and len(oracle['target_version_oracle'])==6
for n in [1,2]:
 pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(Q/f'POST_RUN{n}_IDENTITY.json');tool=read(Q/f'RUN{n}_TOOL_PROOF.json');assert pre['files']==post['files'] and len(pre['files'])==103
 for x in pre['files']:verify(x,False)
 assert pre['run_id']==post['run_id']==c['run_ids'][n-1] and pre['culture']==c['cultures'][n-1]
 assert tool['exit_code']==post['actual_tool_exit_code']==0 and sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
 raw=(Q/f'RUN{n}_RAW.txt').read_text(encoding='utf-8-sig')
 # R9 saves complete process stdout to a file;tool output records exit and its last12 lines.
 commands=read(H/'coordination/MASTER_R9_QA_ACTUAL_RUN_COMMANDS_20261009.json');command=commands[n-1]
 assert command['exitCode']==0 and pre['run_id'] in command['command'] and f'RUN{n}_RAW.txt' in command['command'] and '$LASTEXITCODE' in command['command'] and 'Set-Content' in command['command']
 assert tool['output'].splitlines()[0]==f'QA_RUN_EXIT=0; culture {pre["culture"]}; full raw in RUN{n}_RAW.txt'
 assert raw.splitlines()[-12:]==tool['output'].splitlines()[1:]
 assert sum(l.startswith('PASS ') for l in raw.splitlines())==88 and not any(l.startswith('FAIL ') for l in raw.splitlines())
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 runs.append({'run_id':pre['run_id'],'culture':pre['culture'],'prepost_files':103,'tool_exit':0,'assertions_pass':88,'assertions_fail':0,'runner_sha256':pre['runner']['exe_sha256'],'runner_mvid':pre['runner']['exe_mvid']})
normal=read(Q/'NORMAL_RESULTS.json');assert len(normal['results'])==88 and all(x['status']=='PASS' for x in normal['results']) and normal['normal_case_count']==12
assert c['selected_sha256']==normal['selected_sha256']=='02815FF8A20CB971AD716BBA75417E5FFAD9FADEB358078A785253124FEF4BF5' and c['selected_mvid']=='12aa23c7-3ec0-4b6a-bbb1-4a036127c5da'
assert c['qa_runner_builds']==1 and c['managed_codec_runs']==2 and all(c[k]==0 for k in ['production_builds','production_modifications','provider_cache_game_native_operator_calls','old_a_or_qa_runner_runs','invalid_rejection_tied_adverse_tests'])
cases=[]
for name in oracle['cases']:
 canonical=Q/(name+'.canonical.json');fresh=Q/(name+'.fresh_original.canonical.json')
 assert canonical.read_bytes()==(Q/'RUN1_ARCHIVE'/canonical.name).read_bytes()==fresh.read_bytes()==(Q/'RUN1_ARCHIVE'/fresh.name).read_bytes()
 assert sha(canonical)==(Q/(name+'.sha256.txt')).read_text().strip()
 checks_count=0
 for suffix in ['semantic_checks','normalize_checks','transport_checks','fresh_original_checks']:
  checks=read(Q/(name+'.'+suffix+'.json'));assert checks
  for x in checks:assert x['matched'] and same(x)
  checks_count+=len(checks)
 cases.append({'case':name,'canonical_sha256':sha(canonical),'fresh_original_sha256':sha(fresh),'cross_process_bytes_match':True,'semantic_checks_master_verified':checks_count,'semantics':'PASS'})
targets=read(Q/'TARGETED_VERSION_RESULTS.json');assert len(targets)==6
for target in targets:
 name=target['case_id'];assert target['views_compared']==5 and target['status']=='PASS' and target['expected']==target['actual']==oracle['target_version_oracle'][name] and not target['positive_required_helper_invoked']
 checks=read(Q/(name+'.version_checks.json'));assert len(checks)==len(target['expected'])*4*5
 assert all(x['matched'] and same(x) for x in checks)
unknown=next(x for x in targets if x['case_id']=='OPTIONAL_UNKNOWN_VERSION');assert unknown['actual'][0]['modVersion'] is None and unknown['actual'][0]['compatibilityVersionRange']=='1.6'
reverse=next(x for x in targets if x['case_id']=='REVERSE_NO_INFERENCE_VERSION');assert reverse['actual'][0]['compatibilityVersionRange']=='' and reverse['actual'][0]['modVersion']=='2.1.0'
empty=next(x for x in targets if x['case_id']=='OPTIONAL_EMPTY_VERSION');assert empty['actual'][0]['modVersion']==''
assert len(read(Q/'HISTORICAL65_FIELD_RESULTS.json'))==65
admitted=[]
for name in ['BASE','NORMAL_REVISION_B']:
 p=Q/(name+'.admitted.canonical.json');assert p.read_bytes()==(Q/'RUN1_ARCHIVE'/p.name).read_bytes()==(Q/(name+'.canonical.json')).read_bytes()
 obs=read(Q/(name+'.admission_observation.json'));assert obs['success'] and obs['reason']=='' and obs['canonical_sha256']==sha(p) and obs['canonical_utf8_bytes']==len(p.read_bytes())
 assert all(x['matched'] and same(x) for x in read(Q/(name+'.admission_checks.json')))
 admitted.append({'case':name,'sha256':sha(p),'positive_helper_semantics':'PASS','cross_process_bytes_match':True})
loaded=read(Q/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_managed_hashes_match_prerun']
for row in loaded['rows']:
 mapping={x['path'].lower():x for x in read(Q/f'PRE_RUN{row["stage"]}_MANIFEST.json')['files']};assert row['pre_pinned'] and mapping[row['path'].lower()]['sha256']==row['sha256']==sha(Path(row['path']))
assert read(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),c['runner']['exe_path'],c['runner']['pdb_path']],check=True,capture_output=True,text=True).stdout)
assert meta['mvid']==c['runner']['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
scope=read(Q/'FIXED_SOURCE_SCOPE.json');assert scope['full_normalized_text_matches_only_declared_changes'] and scope['prefix_match'] and scope['other_child_key_order_patch_settings_behavior_unchanged']
for x in scope['files']:verify(x);assert x['matched'] and sha(Path(x['prior_frozen_path']))==x['sha256']
for name in ['old_source','new_source','diff']:verify(scope[name])
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and transport['completion_sha256']==sha(Q/'COMPLETION.json') and sha(Path(transport['tool_proof_path']))==transport['tool_proof_sha256']
snap=H/'coordination/MASTER_SOL_R9_VERSION_MEANING_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261009.json';poll=json.loads(next(x['text'] for x in read(snap)['content'] if x['type']=='text'))['polls'][0];assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11ca3-5c18-7bd0-abab-77e17e3b6463'
comm=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
proof={'at':at,'guard_run':'MASTER-SOL-R9-COMPLETE-20261009-01','guard_session':15606,'result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report_path'],'report_sha256':c['report_sha256'],'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':326,'protected_unique_paths_master_rehashed':3206,'runs':runs,'cases':cases,'target_cases':targets,'admitted_cases':admitted,'historical_leaf_semantics':65,'all_actual_loaded_pre_pins_verified':True,'runner_metadata_master':meta,'source_scope':scope,'actual_thread':poll,'direct_transport_verified':True,'master_execution_builds':0,'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
p=H/'coordination/MASTER_SOL_R9_VERSION_MEANING_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261009.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verified':True,'evidence':326,'protected':3206,'runs':runs,'target_cases':6,'codec_pairs':12,'fresh_original_pairs':12,'admitted_pairs':2,'closure':'PENDING_MASTER_DISPOSITION'}))
