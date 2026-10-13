"""Read-only independent evidence verification; no candidate/runner execution or build."""
from pathlib import Path
import json, hashlib, datetime, struct, subprocess, re
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def verify(x,workspace=True):
 p=Path(x['path']);assert p.is_file()
 if workspace:assert p.resolve().is_relative_to(R)
 assert sha(p)==x['sha256'] and p.stat().st_size==x.get('bytes',x.get('size',p.stat().st_size)),p
def typed_equal(e,a):
 if isinstance(e,dict):return isinstance(a,dict) and set(e)==set(a) and all(typed_equal(e[k],a[k]) for k in e)
 if isinstance(e,list):return isinstance(a,list) and len(e)==len(a) and all(typed_equal(x,y) for x,y in zip(e,a))
 if type(e)==float:return type(a) in [float,int] and struct.pack('<f',e)==struct.pack('<f',a)
 return type(e)==type(a) and e==a
def check_rows(d):
 if isinstance(d,dict):
  if all(k in d for k in ['expected','actual','kind','matched']):yield d
  for v in d.values():yield from check_rows(v)
 elif isinstance(d,list):
  for v in d:yield from check_rows(v)
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
assert c['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009-c0cfd1b859084a538e9866c78fde8635'
assert c['wp_id']=='WP_QA_ENGINE_GATE05_R10_PACKAGE_POLICY_INDEPENDENT' and c['delivery_id']=='SOL-GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009-01' and c['wp_revision']=='S1' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='AE86F2CB5478E9ED73762E34717B660DBA5A10EC77A86B4A8ED3F73F9A7D61C8'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(c[k])
assert len(m['files'])==c['artifact_count']==397
for x in m['files']:verify(x)
before={x['path']:x for x in read(Q/'PRESERVATION_BEFORE.json')['files']};after={x['path']:x for x in read(Q/'PRESERVATION_AFTER.json')['files']}
assert before==after and len(after)==3644
for x in after.values():verify(x)
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');pin=read(Q/'ORACLE_BEFORE_BUILD.json')
assert sha(Path(pin['oracle']['path']))==pin['oracle']['sha256'] and not oracle['expected_policies_derived_from_actual']
assert len(oracle['cases'])==12 and len(oracle['package_policy_cases'])==6 and len(oracle['target_version_oracle'])==6
thread=read(H/'coordination/MASTER_R10_QA_ACTUAL_THREAD_READ_20261009.json')
commands=[x for x in thread['turns'][0]['items'] if x.get('type')=='commandExecution'];runs=[]
for n in [1,2]:
 pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(Q/f'POST_RUN{n}_IDENTITY.json');tool=read(Q/f'RUN{n}_TOOL_PROOF.json')
 assert pre['files']==post['files'] and len(pre['files'])==116
 for x in pre['files']:verify(x,False)
 assert pre['run_id']==post['run_id'] and pre['culture']==['en-US','de-DE'][n-1]
 assert tool['exit_code']==post['actual_tool_exit_code']==0 and sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
 command=next(x for x in commands if pre['run_id'] in x.get('command','') and f'RUN{n}_RAW.txt' in x['command'])
 assert command['exitCode']==0 and '$LASTEXITCODE' in command['command'] and 'exit' in command['command'] and '*>' in command['command']
 assert command['cwd']==tool['cwd']==pre['cwd'] and command['output']['text']==tool['output']
 raw=(Q/f'RUN{n}_RAW.txt').read_text(encoding='utf-8-sig');tail=int(re.search(r'-Tail (\d+)',tool['cmd'])[1])
 assert raw.splitlines()[-tail:]==tool['output'].splitlines()
 assert sum(l.startswith('PASS ') for l in raw.splitlines())==135 and not any(l.startswith('FAIL ') for l in raw.splitlines())
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 loaded=read(Q/f'RUN{n}_ACTUAL_LOADED_PREPIN_BINDING.json');mapping={x['path'].lower():x for x in pre['files']}
 assert loaded['all_loaded_pre_pin_matched'] and loaded['run_id']==pre['run_id'] and len(loaded['files'])==12
 for x in loaded['files']:assert x['pre_pin_matched'] and mapping[x['path'].lower()]['sha256']==x['sha256']==sha(Path(x['path']))
 runs.append({'run_id':pre['run_id'],'culture':pre['culture'],'prepost_files':116,'tool_exit':0,'assertions_pass':135,'assertions_fail':0,'loaded_managed':12,'runner_sha256':pre['runner']['exe_sha256'],'runner_mvid':pre['runner']['exe_mvid']})
normal=read(Q/'NORMAL_RESULTS.json');assert len(normal['results'])==135 and all(x['status']=='PASS' for x in normal['results']) and normal['normal_case_count']==12
assert c['selected_sha256']==normal['selected_sha256']=='1772DFBD1674B7CF8450CAF42FDE7AC6F92FD3A22183B7DDE5AA705CCEC24721' and c['selected_mvid']=='7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb'
assert c['qa_runner_builds']==1 and c['candidate_runner_processes']==2 and all(c[k]==0 for k in ['production_modify_builds','configuration_cache_provider_game_native_operator_runs','old_runner_negative_rejection_tied_ambiguity_adverse_runs'])
count=0
for root in [Q,Q/'RUN1_ARCHIVE']:
 for p in root.glob('*.json'):
  if any(s in p.name for s in ['checks','semantic_checks','version_checks','policy_check']):
   for row in check_rows(read(p)):assert row['matched'] and same(row),(p,row);count+=1
packages=[]
for name,o in oracle['package_policy_cases'].items():
 p=o['expected_policy'];preimage=(p['policyId']+'|'+p['revision']+'|'+','.join(x.lower() for x in p['admittedPackageIds'])).encode('utf-8')
 assert preimage==bytes.fromhex(o['preimage_utf8_hex'])==Path(o['preimage_utf8_path']).read_bytes()
 digest=hashlib.sha256(preimage).hexdigest().upper();assert digest==o['expected_digest']==p['policyDigest']
 for root in [Q,Q/'RUN1_ARCHIVE']:
  check=read(root/(name+'.policy_check.json'));assert check['success'] and check['reason']=='' and typed_equal(o['expected_check_result'],check['actual'])
  decoded=read(root/(name+'.policy_admitted.decoded.json'));assert typed_equal(o['expected_admitted_manifest'],decoded)
  assert (root/(name+'.policy_admitted.canonical.json')).read_bytes()==(Q/(name+'.policy_admitted.canonical.json')).read_bytes()
 packages.append({'case':name,'digest':digest,'semantic_leaves':len(read(Q/(name+'.policy_admitted.checks.json'))),'independent_typed_policy_full_result':'MATCHED','cross_process_bytes_match':True})
digests={x['case']:x['digest'] for x in packages};assert digests['EQ_A']==digests['EQ_A_SEPARATE'] and all(digests['EQ_A']!=digests[k] for k in ['ID_ONLY','REV_ONLY','ORDER_ONLY'])
targets=read(Q/'TARGETED_VERSION_RESULTS.json');assert len(targets)==6
for t in targets:assert t['status']=='PASS' and t['views_compared']==5 and t['expected']==t['actual']==oracle['target_version_oracle'][t['case_id']] and not t['positive_required_helper_invoked']
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');assert len(summary['pairs'])==32
for pair in summary['pairs']:
 verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
assert read(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
build=next(x for x in commands if 'csc.dll' in x.get('command','') and 'BUILD_RAW.txt' in x['command']);assert build['exitCode']==0
runner=summary['runner'];meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),runner['exe_path'],runner['pdb_path']],check=True,capture_output=True,text=True).stdout)
assert meta['mvid']==runner['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
scope=read(Q/'FIXED_SOURCE_SCOPE.json');assert scope['prefix_match'] and scope['prefix_bytes']==72547
for row in scope['files']:verify(row['current']);verify(row['prior']);assert row['matched'] and row['current']['sha256']==row['prior']['sha256']
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['result_id']==c['result_id'] and sha(Path(transport['exact_tool_return_file']))==transport['exact_tool_return_sha256']
snap=H/'coordination/MASTER_SOL_R10_PACKAGE_POLICY_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261009.json';poll=json.loads(next(x['text'] for x in read(snap)['content'] if x['type']=='text'))['polls'][0]
assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11d47-78b5-7030-ad19-5d70087bff02'
comm=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
proof={'at':at,'guard_run':'MASTER-SOL-R10-INDEPENDENT-COMPLETE-20261009-01','guard_session':58878,'result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report']['path'],'report_sha256':c['report']['sha256'],'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':397,'protected_unique_paths_master_rehashed':3644,'runs':runs,'package_cases':packages,'typed_check_rows_verified':count,'target_version_cases':targets,'canonical_crossprocess_pairs':32,'runner_metadata_master':meta,'source_scope':scope,'actual_thread':poll,'actual_execution_thread_read':str(H/'coordination/MASTER_R10_QA_ACTUAL_THREAD_READ_20261009.json'),'direct_transport_verified':True,'master_execution_builds':0,'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
p=H/'coordination/MASTER_SOL_R10_PACKAGE_POLICY_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261009.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verified':True,'evidence':397,'protected':3644,'runs':runs,'package_cases':6,'typed_rows':count,'canonical_pairs':32,'disposition':'PENDING_MASTER'}))
