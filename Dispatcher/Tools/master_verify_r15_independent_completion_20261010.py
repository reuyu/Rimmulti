"""Evidence and PE metadata only; candidate/runner build or execution zero."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,re,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def verify(f):
 p=Path(f['path']);assert p.is_file() and sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size',p.stat().st_size)),str(p)
def checks(d):
 if isinstance(d,dict):
  if all(k in d for k in ['expected','actual','kind','matched']):yield d
  for v in d.values():yield from checks(v)
 elif isinstance(d,list):
  for v in d:yield from checks(v)
def equal(row):
 e=json.loads(row['expected']);a=json.loads(row['actual']);k=row['kind']
 if k=='float32 exact bits':return struct.pack('<f',float(e))==struct.pack('<f',float(a))
 if k=='bool':return type(e)==type(a)==bool and e==a
 if k=='integer exact Int64':return type(e)==type(a)==int and e==a
 if k=='string/codepoint':return type(e)==type(a)==str and e==a
 if k=='null':return e is None and a is None
 raise AssertionError(k)
def typed_equal(e,a):
 if isinstance(e,dict):return isinstance(a,dict) and set(e)==set(a) and all(typed_equal(e[k],a[k]) for k in e)
 if isinstance(e,list):return isinstance(a,list) and len(e)==len(a) and all(typed_equal(x,y) for x,y in zip(e,a))
 if type(e)==float:return type(a) in [float,int] and struct.pack('<f',e)==struct.pack('<f',a)
 return type(e)==type(a) and e==a
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();comp=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json');rid='SOL-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010-7843e15c956b49ab83fd2c11f205f8b4'
assert comp['result_id']==m['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1';assert sha(Q/'COMPLETION.json')=='EBC2F890A782313FB044AC530050C8705D4A2B505ACF23DCBD055178BA15758A'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(m['files'])==925
for f in m['files']:verify(f)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==7994
for f in after:verify(f)
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');pin=read(Q/'ORACLE_BEFORE_BUILD.json');verify(pin['oracle']);assert not oracle['expected_policies_derived_from_actual'] and len(oracle['policy_cases'])==14 and len(oracle['cache_policies'])==2
thread=json.loads(read(C/'MASTER_R15_QA_ACTUAL_THREAD_READ_20261010.json')['content'][0]['text']);commands=[x for x in thread['turns'][0]['items'] if x.get('type')=='commandExecution'];summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');process=read(Q/'FRESH_PROCESS_PROOF.json');runs=[]
assert len(process['rows'])==2
for n,row in enumerate(process['rows'],1):
 for k in ['context','raw','tool','all_generated_output_inventory']:verify(row[k])
 root=Path(row['context']['path']).parent;pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');tool=read(Path(row['tool']['path']));raw=Path(row['raw']['path']).read_text(encoding='utf-8-sig');context=read(Path(row['context']['path']))
 assert pre['files']==post['files'] and len(pre['files'])==174 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==['en-US','de-DE'][n-1] and row['actual_numeric_exit']==tool['exit_code']==post['actual_tool_exit_code']==0
 command=next(x for x in commands if row['run_id'] in x.get('command','') and 'QaCodecRunner.exe' in x.get('command','') and 'RAW_CONSOLE' in x.get('command',''))
 assert command['exitCode']==0 and command['cwd']==tool['cwd']==row['cwd'] and '$LASTEXITCODE' in command['command']
 assert command['output']['text']==tool['output'] or (command['output'].get('truncated') and tool['output'].startswith(command['output']['text']))
 tail=int(re.search(r'-Tail (\d+)',tool['cmd'])[1]);assert raw.splitlines()[-tail:]==tool['output'].splitlines();assert sum(x.startswith('PASS ') for x in raw.splitlines())==360 and not any(x.startswith('FAIL ') for x in raw.splitlines())
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==360 and all(x['status']=='PASS' for x in normal['results'])
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_pre_pin_matched'] and len(loaded['files'])==12;mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path']))
 inventory=read(Path(row['all_generated_output_inventory']['path']));assert inventory['file_count']==len(inventory['files'])==423 and inventory['recursive_every_generatedfile']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'};assert actualset=={str(Path(f['path']).resolve()).lower() for f in inventory['files']}
 for f in inventory['files']:verify(f)
 cacheledger=read(root/'ACTUAL_CACHE_LIFECYCLE_CALL_LEDGER.json');ledger=[x for x in cacheledger if x['scope']!='direct_pure_provider'];assert len(cacheledger)==855 and len(ledger)==87 and sum(x['api']=='TryPublishComputedEntry_LEGACY_CURRENT_MATCHING' for x in ledger)==5 and sum(x['api']=='TryPublishComputedEntry_OUTENTRY_CURRENT_MATCHING' for x in ledger)==5 and sum(x['api']=='ContentProfileCacheCore.constructor' for x in ledger)==2
 assert row['run_id'] in raw and str(row['pid']) in raw and raw.startswith('Independent reference byte stage complete before candidate calls: 68')
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 runs.append({'run_id':row['run_id'],'pid':row['pid'],'culture':row['culture'],'exit':0,'pass':360,'fail':0,'prepost':174,'loaded':12,'output_files':423,'stage_ledger':87,'root':str(root)})
 assert 'cache calls0' not in raw and 'cache calls 0' not in raw
 allledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json');assert allledger==cacheledger and len(allledger)==855 and sum(x['scope']=='direct_pure_provider' for x in allledger)==768;assert [x for x in allledger if x['scope']!='direct_pure_provider']==ledger
assert runs[0]['pid']!=runs[1]['pid'];assert read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_first_outputs_unchanged'] and read(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['all_generated_output_inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=0
for entry in summary['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['typed_checks'] and entry['all_matched']
 for x in rows:assert x['matched'] and equal(x)
 count+=len(rows)
assert count==84252
for key,num in [('pairs',125),('reference_pairs',68)]:
 assert len(summary[key])==num
 for pair in summary[key]:verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
assert len(summary['independent_candidate_reference_bindings'])==298
for row in summary['independent_candidate_reference_bindings']:verify(row['actual']);verify(row['reference']);assert row['matched'] and Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
for name,o in oracle['policy_cases'].items():
 independent=json.dumps(o['expected_canonical_declaration'],ensure_ascii=False,separators=(',',':')).encode('utf8');assert hashlib.sha256(independent).hexdigest().upper()==o['expected_digest']
 for run in runs:
  root=Path(run['root']);check=read(root/(name+'.order.check_results.json'));assert typed_equal(o['expected_check_result'],check['recordResult']) and typed_equal(o['expected_check_result'],check['declResult']) and check['callerBefore']==check['callerAfter']
  for v in ['fresh','explicit','reconstructed']:assert typed_equal(o['expected_admitted_manifest'],read(root/(name+f'.bound.{v}.canonical.json')))
  for overload in [0,1]:assert typed_equal(o['expected_admitted_manifest'],read(root/(name+f'.policy{overload}.canonical.json')))
build=read(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0;bc=next(x for x in commands if 'csc.dll' in x.get('command','') and 'BUILD_RAW' in x.get('command',''));assert bc['exitCode']==0
runner=summary['runner'];meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),runner['exe_path'],runner['pdb_path']],check=True,capture_output=True,text=True).stdout);assert meta['mvid']==runner['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
assert comp['production_modify_builds']==0 and comp['actual_compute_getactual_privatecollector_globalpublication_seed_errorhelper_native_game_operator_old_stale_mismatch_rejection_race_adverse']==0
scope=read(Q/'ACTUAL_EXECUTION_SCOPE.json');assert scope['raw_source_unchanged'] and len(scope['rows'])==2
for row in scope['rows']:
 verify(row['actual_runtime_ledger']);assert row['actual_logged_stages']==855 and row['direct_provider_API_calls']==768 and row['core_or_global_grouped_stages']==87
api=read(Q/'API_AND_GENERATION_RECONCILIATION.json');assert api['actual_rule']['invalidate_increment']==1 and api['actual_rule']['expected_main_sequence']==[0,1,2,3,4,5] and datetime.datetime.fromisoformat(api['at'])<datetime.datetime.fromisoformat(pin['at'])
producer=read(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json');assert producer['TC16_stale_error_actual_calls_three']==3 and len(producer['before9_rows'])==len(producer['after9_rows'])==9 and not producer['all_25_label_scope_PASS_admitted'] and producer['producer_replays']==0
assert len(producer['three_processes'])==3
for row in producer['three_processes']:
 for obj in row.values():
  if isinstance(obj,dict) and all(k in obj for k in ['path','sha256']):verify(obj)
 actual=read(Path(row['result']['path']));account=actual['cache_accounting'];assert sum(v for k,v in account.items() if k.startswith('normal_') and k!='normal_core_instance_creations')==account['total_normal_cache_calls']==55
 ledger=read(Path(row['stage_ledger']['path']));assert len(ledger)==44 and sum(x['method_name']=='SetComputationError(staleGen,err)' for x in ledger)==1
for row in producer['before9_rows']+producer['after9_rows']:
 verify(row['resolved_frozen']);assert row['recorded']['sha256']==row['resolved_frozen']['sha256'] and row['recorded']['size']==row['resolved_frozen']['bytes'] and row['matched']
count_reconciliation=read(Q/'ANALYSIS_METADATA_COUNT_RECONCILIATION.json');assert count_reconciliation['actual_metadata_before_count']==count_reconciliation['actual_metadata_after_count']==9 and count_reconciliation['original_graph_outputs_unchanged'] and count_reconciliation['candidate_reruns']==0 and count_reconciliation['QA_rebuilds']==0
integration=read(Q/'SOURCE_REUSE_AND_INTEGRATION_AUDIT.json');assert integration['final_wrapper_reinserted_and_oracle_source_pin_corrected_before_onlybuild_andcalls'] and integration['final_program_unchanged_afterbuild'] and integration['no_oracle_runner_input_candidate_output_changes_or_reruns_aftercalls']
for key in ['final_program','final_oracle']:verify(integration[key])
setup={'analysis_count_reconciliation':count_reconciliation,'source_before_build_integration':integration,'toolchain_timestamp':'Compiler date only;at-second chronology unobserved;actual buildtool andidentity retained'}

delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='AUTHORIZED_TERMINAL_SEND_TOOL_SUCCEEDED' and delivery['attempts']==1 and delivery['destination']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174/local'
return_wrapper=read(Path(delivery['tool_proof']));return_tool=return_wrapper['actual_tool_result'];assert return_wrapper['terminal_delivery_attempt']==1 and return_wrapper['result_id']==rid and not return_tool.get('isError') and json.loads(return_tool['content'][0]['text'])['threadId']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
actual_sends=[x for x in thread['turns'][0]['items'] if x.get('type')=='mcpToolCall' and x.get('tool')=='send_message_to_thread' and x.get('arguments',{}).get('prompt','')==return_wrapper['prompt']];assert len(actual_sends)==1 and actual_sends[0]['status']=='completed' and actual_sends[0]['arguments']['threadId']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
snap=json.loads(read(C/'MASTER_SOL_R15_PUBLIC_MANIFEST_BOUNDARY_INDEPENDENT_COMPLETION_SNAPSHOT_20261010.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['latestTurn']['id']=='01a121a2-fc67-73b2-8d9a-64ab6a15e2ca'
vp=C/'MASTER_SOL_R15_PUBLIC_MANIFEST_BOUNDARY_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json';assert not vp.exists();proof={'at':at,'guard_run':'MASTER-SOL-R15-COMPLETE-CONTINUE-20261010-01','guard_session':58943,'guard_pid':16944,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':925,'protected_paths_rehashed':7994,'runs':runs,'typed_rows':count,'canonical_pairs':125,'reference_pairs':68,'reference_bindings':298,'runner_metadata_master':meta,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_R15_QA_ACTUAL_THREAD_READ_20261010.json'),'scope_correction':scope,'producer_reconciliation':producer,'pre_execution_setup_qualification':setup,'selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'};vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'verified':True,'evidence':925,'protected':7994,'runs':runs,'typed_rows':count,'status':'PENDING_DISPOSITION'}))
