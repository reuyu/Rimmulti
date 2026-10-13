"""Read-only independent evidence verification; no candidate/runner execution or build."""
from pathlib import Path
import json, hashlib, datetime, struct, subprocess, re
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009'
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
assert c['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009-60adcacee14e45a4b4a199a2ab928bfe'
assert c['wp_id']=='WP_QA_ENGINE_GATE05_R12_PACKAGE_ORDER_INDEPENDENT' and c['delivery_id']=='SOL-GATE05-R12-PACKAGE-ORDER-INDEPENDENT-S1-20261009-01' and c['wp_revision']=='S1' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='3F4CE10B7C92AEC967C09EC9DBEB0F75A2DFCC77E46D75168D80FDE553439428'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(c[k])
assert len(m['files'])==c['artifact_count']==814
for x in m['files']:verify(x)
before={x['path']:x for x in read(Q/'PRESERVATION_BEFORE.json')['files']};after={x['path']:x for x in read(Q/'PRESERVATION_AFTER.json')['files']}
assert before==after and len(after)==5078
for x in after.values():verify(x)
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');pin=read(Q/'ORACLE_BEFORE_BUILD.json')
assert sha(Path(pin['oracle']['path']))==pin['oracle']['sha256'] and not oracle['expected_policies_derived_from_actual']
assert len(oracle['cases'])==12 and len(oracle['policy_cases'])==14 and len(oracle['target_version_oracle'])==6
threadraw=read(H/'coordination/MASTER_R12_QA_ACTUAL_THREAD_READ_20261009.json');thread=json.loads(next(x['text'] for x in threadraw['content'] if x['type']=='text'))
commands=[x for x in thread['turns'][0]['items'] if x.get('type')=='commandExecution'];runs=[]
for n in [1,2]:
 pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(Q/f'POST_RUN{n}_IDENTITY.json');tool=read(Q/f'RUN{n}_TOOL_PROOF.json')
 assert pre['files']==post['files'] and len(pre['files'])==129
 for x in pre['files']:verify(x,False)
 assert pre['run_id']==post['run_id'] and pre['culture']==['en-US','de-DE'][n-1]
 assert tool['exit_code']==post['actual_tool_exit_code']==0 and sha(Path(post['tool_proof_path']))==post['tool_proof_sha256']
 command=next(x for x in commands if pre['run_id'] in x.get('command','') and f'RUN{n}_RAW.txt' in x['command'])
 assert command['exitCode']==0 and '$LASTEXITCODE' in command['command'] and 'exit' in command['command'] and '*>' in command['command']
 assert command['cwd']==tool['cwd']==pre['cwd']
 # read_thread renders the exec command with an outer PowerShell shell/quoting wrapper. Match execution-defining tokens, not raw request-string equality.
 for token in [pre['run_id'],pre['culture'],'QaCodecRunner.exe',f'RUN{n}_RAW.txt','$LASTEXITCODE','exit','*>']:assert token in command['command'] and token in tool['cmd']
 assert command['output']['text']==tool['output'] or (command['output'].get('truncated') and tool['output'].startswith(command['output']['text']))
 raw=(Q/f'RUN{n}_RAW.txt').read_text(encoding='utf-8-sig');tail=int(re.search(r'-Tail (\d+)',tool['cmd'])[1])
 assert raw.splitlines()[-tail:]==tool['output'].splitlines()
 assert sum(l.startswith('PASS ') for l in raw.splitlines())==265 and not any(l.startswith('FAIL ') for l in raw.splitlines())
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 loaded=read(Q/f'RUN{n}_ACTUAL_LOADED_PREPIN_BINDING.json');mapping={x['path'].lower():x for x in pre['files']}
 assert loaded['all_loaded_pre_pin_matched'] and loaded['run_id']==pre['run_id'] and len(loaded['files'])==12
 for x in loaded['files']:assert x['pre_pin_matched'] and mapping[x['path'].lower()]['sha256']==x['sha256']==sha(Path(x['path']))
 runs.append({'run_id':pre['run_id'],'culture':pre['culture'],'prepost_files':129,'tool_exit':0,'assertions_pass':265,'assertions_fail':0,'loaded_managed':12,'runner_sha256':pre['runner']['exe_sha256'],'runner_mvid':pre['runner']['exe_mvid']})
normal=read(Q/'NORMAL_RESULTS.json');assert len(normal['results'])==265 and all(x['status']=='PASS' for x in normal['results']) and normal['normal_case_count']==12
assert c['selected_sha256']==normal['selected_sha256']=='3035A0D0FDD799D42AC83B7D776998AFF07A8BDD3246959E685AA0F8D7ACF94E' and c['selected_mvid']=='ad4caf3c-88bc-4971-9c2a-ab78eae395e5'
assert c['qa_runner_builds']==1 and c['candidate_runner_processes']==2 and all(c[k]==0 for k in ['production_modify_builds','configuration_cache_provider_game_native_operator_old_negative_rejection_tied_gapped_unknownschema_ambiguity_adverse'])
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');count=0
for item in summary['typed_files']:
 verify(item['file']);checks=list(check_rows(read(Path(item['file']['path']))));assert len(checks)==item['typed_checks'] and item['all_matched']
 for row in checks:assert row['matched'] and same(row)
 count+=len(checks)
assert count==67458
packages=[]
for name,o in oracle['policy_cases'].items():
 expected=o['expected_canonical_declaration'];independent=json.dumps(expected,ensure_ascii=False,separators=(',',':')).encode('utf8');digest=hashlib.sha256(independent).hexdigest().upper();assert independent==Path(o['reference']['path']).read_bytes()==o['expected_json'].encode('utf8') and digest==o['expected_digest']
 raw=o['independent_observed_manifest']['activeMods'];ordered=o['independent_expected_execution_records'];assert ordered==sorted(raw,key=lambda x:x['loadOrder']) and sorted(x['loadOrder'] for x in raw)==list(range(len(raw))) and [x['packageId'].lower() for x in ordered]==expected['admittedPackageIds']
 for root in [Q,Q/'RUN1_ARCHIVE']:
  assert (root/(name+'.policy.canonical.json')).read_bytes()==independent
  check=read(root/(name+'.order.check_results.json'));assert typed_equal(o['expected_check_result'],check['recordResult']) and typed_equal(o['expected_check_result'],check['declResult']) and check['callerBefore']==check['callerAfter']
  for overload in [0,1]:assert typed_equal(o['expected_admitted_manifest'],read(root/(name+f'.policy{overload}.canonical.json')))
  for view in ['fresh','explicit','reconstructed']:assert typed_equal(o['expected_admitted_manifest'],read(root/(name+f'.bound.{view}.canonical.json')))
  assert typed_equal(o['expected_bound_transport_manifest'],read(root/(name+'.bound.raw.json')))
 packages.append({'case':name,'digest':digest,'full_check9fields_and_caller':'MATCHED','fresh_original_before_normalize_full_binding':'MATCHED','whole_admitted_record_association':'MATCHED'})
for relation in oracle['relations']:
 l=oracle['policy_cases'][relation['left']];r=oracle['policy_cases'][relation['right']];assert (l['expected_digest']==r['expected_digest'])==relation['reference_policy_digest_equal'] and typed_equal(l['expected_admitted_manifest'],r['expected_admitted_manifest'])==relation['reference_full_content_semantics_equal']

targets=read(Q/'TARGETED_VERSION_RESULTS.json');assert len(targets)==6
for t in targets:assert t['status']=='PASS' and t['views_compared']==5 and t['expected']==t['actual']==oracle['target_version_oracle'][t['case_id']] and not t['positive_required_helper_invoked']
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');assert len(summary['pairs'])==110 and len(summary['reference_pairs'])==66
for pair in summary['pairs']:
 verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
for pair in summary['reference_pairs']:
 verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
assert len(summary['independent_reference_bindings'])==268
for row in summary['independent_reference_bindings']:
 verify(row['actual']);verify(row['reference']);assert row['matched'] and Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
process=read(Q/'FRESH_PROCESS_PROOF.json');assert process['run1_context_basis']=='DERIVED_FROM_RETAINED_RAW_AND_TOOL_NOT_RESTORED_SIDECAR' and len(process['archive_limitations'])==1
for row in process['rows']:
 verify(row['raw']);verify(row['tool']);raw=Path(row['raw']['path']).read_text(encoding='utf-8-sig');assert row['run_id'] in raw and f"Culture={row['culture']} Runtime={row['runtime']} ProcessId={row['process_id']}" in raw and raw.startswith('Independent reference byte stage complete before candidate calls: 66') and row['numeric_exit']==0
assert process['rows'][0]['process_id']!=process['rows'][1]['process_id']
for name in ['ACTUAL_PROCESS_CONTEXT.json','REFERENCE_BYTE_STAGE.json','ORDER_POLICY_RESULTS.json']:assert not (Q/'RUN1_ARCHIVE'/name).exists()
verify(process['run2_runner_context']);assert read(Path(process['run2_runner_context']['path']))['run_id']==runs[1]['run_id']
assert read(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
build=next(x for x in commands if 'csc.dll' in x.get('command','') and 'BUILD_RAW.txt' in x['command']);assert build['exitCode']==0
runner=summary['runner'];meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),runner['exe_path'],runner['pdb_path']],check=True,capture_output=True,text=True).stdout)
assert meta['mvid']==runner['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
scope=read(Q/'FIXED_SOURCE_SCOPE.json');assert scope['prefix_match'] and scope['prefix_bytes']==72547
for row in scope['files']:verify(row['current']);verify(row['prior']);assert row['matched'] and row['current']['sha256']==row['prior']['sha256']
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='DIRECT_MASTER_TERMINAL_SENT' and transport['actual_terminal_sends']==1 and transport['result_id']==c['result_id'] and sha(Path(transport['return_tool_path']))==transport['return_tool_sha256']
assert not read(Path(transport['return_tool_path']))['isError']
snap=H/'coordination/MASTER_SOL_R12_PACKAGE_ORDER_INDEPENDENT_S1_COMPLETION_SNAPSHOT_20261009.json';poll=json.loads(next(x['text'] for x in read(snap)['content'] if x['type']=='text'))['polls'][0]
assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11f91-bdee-7ae0-93a4-991c80034899'
comm=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
proof={'at':at,'guard_run':'MASTER-SOL-R12-INDEPENDENT-COMPLETE-20261009-01','guard_session':85079,'result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':c['report']['path'],'report_sha256':c['report']['sha256'],'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':814,'protected_unique_paths_master_rehashed':5078,'runs':runs,'package_cases':packages,'typed_check_rows_verified':count,'policy_bearing_fresh_original_before_normalize':'INDEPENDENT_VALID_CURRENT_V1_BINDING_14_CASES_FULL_TYPED_BYTES_MATCHED','QA_archive_limitations':process['archive_limitations'],'shared_vendor_reference_limit':summary['byte_oracle_library_limit'],'target_version_cases':targets,'canonical_crossprocess_pairs':110,'reference_crossprocess_pairs':66,'runner_metadata_master':meta,'source_scope':scope,'general_schema':'CURRENT_V1_ONLY_STATIC_OPEN_NOT_GENERAL_VERSION_PROOF','actual_thread':poll,'actual_execution_thread_read':str(H/'coordination/MASTER_R12_QA_ACTUAL_THREAD_READ_20261009.json'),'direct_transport_verified':True,'master_execution_builds':0,'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
p=H/'coordination/MASTER_SOL_R12_PACKAGE_ORDER_INDEPENDENT_S1_COMPLETION_VERIFICATION_20261009.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verified':True,'evidence':814,'protected':5078,'runs':runs,'policy_cases':14,'typed_rows':count,'canonical_pairs':110,'disposition':'PENDING_MASTER'}))
