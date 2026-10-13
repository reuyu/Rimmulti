"""Evidence and PE metadata only; candidate/runner build or execution zero."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,re,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
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
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();comp=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json');rid='SOL-GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009-39d2285260ab486b85ea99cd8db0bffa'
assert comp['result_id']==m['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1';assert sha(Q/'COMPLETION.json')=='1D367B49FADC197CF22F596F6E4E0A51F0AD7564FC9D1C512BA537BF8A573D0C'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(m['files'])==891
for f in m['files']:verify(f)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==7003
for f in after:verify(f)
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');pin=read(Q/'ORACLE_BEFORE_BUILD.json');verify(pin['oracle']);assert not oracle['expected_policies_derived_from_actual'] and len(oracle['policy_cases'])==14 and len(oracle['cache_policies'])==2
thread=json.loads(read(C/'MASTER_R14_QA_ACTUAL_THREAD_READ_20261009.json')['content'][0]['text']);commands=[x for x in thread['turns'][0]['items'] if x.get('type')=='commandExecution'];summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');process=read(Q/'FRESH_PROCESS_PROOF.json');runs=[]
assert len(process['rows'])==2
for n,row in enumerate(process['rows'],1):
 for k in ['context','raw','tool','all_generated_output_inventory']:verify(row[k])
 root=Path(row['context']['path']).parent;pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');tool=read(Path(row['tool']['path']));raw=Path(row['raw']['path']).read_text(encoding='utf-8-sig');context=read(Path(row['context']['path']))
 assert pre['files']==post['files'] and len(pre['files'])==153 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==['en-US','de-DE'][n-1] and row['actual_numeric_exit']==tool['exit_code']==post['actual_tool_exit_code']==0
 command=next(x for x in commands if row['run_id'] in x.get('command','') and 'QaCodecRunner.exe' in x.get('command','') and 'RAW_CONSOLE' in x.get('command',''))
 assert command['exitCode']==0 and command['cwd']==tool['cwd']==row['cwd'] and '$LASTEXITCODE' in command['command']
 assert command['output']['text']==tool['output'] or (command['output'].get('truncated') and tool['output'].startswith(command['output']['text']))
 tail=int(re.search(r'-Tail (\d+)',tool['cmd'])[1]);assert raw.splitlines()[-tail:]==tool['output'].splitlines();assert sum(x.startswith('PASS ') for x in raw.splitlines())==339 and not any(x.startswith('FAIL ') for x in raw.splitlines())
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==339 and all(x['status']=='PASS' for x in normal['results'])
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_pre_pin_matched'] and len(loaded['files'])==12;mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path']))
 inventory=read(Path(row['all_generated_output_inventory']['path']));assert inventory['file_count']==len(inventory['files'])==412 and inventory['recursive_every_generatedfile']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'};assert actualset=={str(Path(f['path']).resolve()).lower() for f in inventory['files']}
 for f in inventory['files']:verify(f)
 cacheledger=read(root/'ACTUAL_CACHE_LIFECYCLE_CALL_LEDGER.json');ledger=[x for x in cacheledger if x['scope']!='direct_pure_provider'];assert len(cacheledger)==835 and len(ledger)==72 and sum(x['api']=='TryPublishComputedEntry_CURRENT_MATCHING_ONLY' for x in ledger)==5 and sum(x['api']=='ContentProfileCacheCore.constructor' for x in ledger)==2
 assert row['run_id'] in raw and str(row['pid']) in raw and raw.startswith('Independent reference byte stage complete before candidate calls: 68')
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 runs.append({'run_id':row['run_id'],'pid':row['pid'],'culture':row['culture'],'exit':0,'pass':339,'fail':0,'prepost':153,'loaded':12,'output_files':412,'stage_ledger':72,'root':str(root)})
 assert 'cache calls0' not in raw and 'cache calls 0' not in raw
 allledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json');assert allledger==cacheledger and len(allledger)==835 and sum(x['scope']=='direct_pure_provider' for x in allledger)==763;assert [x for x in allledger if x['scope']!='direct_pure_provider']==ledger
assert runs[0]['pid']!=runs[1]['pid'];assert read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_first_outputs_unchanged'] and read(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['all_generated_output_inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=0
for entry in summary['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['typed_checks'] and entry['all_matched']
 for x in rows:assert x['matched'] and equal(x)
 count+=len(rows)
assert count==78682
for key,num in [('pairs',115),('reference_pairs',68)]:
 assert len(summary[key])==num
 for pair in summary[key]:verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
assert len(summary['independent_candidate_reference_bindings'])==278
for row in summary['independent_candidate_reference_bindings']:verify(row['actual']);verify(row['reference']);assert row['matched'] and Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
for name,o in oracle['policy_cases'].items():
 independent=json.dumps(o['expected_canonical_declaration'],ensure_ascii=False,separators=(',',':')).encode('utf8');assert hashlib.sha256(independent).hexdigest().upper()==o['expected_digest']
 for run in runs:
  root=Path(run['root']);check=read(root/(name+'.order.check_results.json'));assert typed_equal(o['expected_check_result'],check['recordResult']) and typed_equal(o['expected_check_result'],check['declResult']) and check['callerBefore']==check['callerAfter']
  for v in ['fresh','explicit','reconstructed']:assert typed_equal(o['expected_admitted_manifest'],read(root/(name+f'.bound.{v}.canonical.json')))
  for overload in [0,1]:assert typed_equal(o['expected_admitted_manifest'],read(root/(name+f'.policy{overload}.canonical.json')))
build=read(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0;bc=next(x for x in commands if 'csc.dll' in x.get('command','') and 'BUILD_RAW' in x.get('command',''));assert bc['exitCode']==0
runner=summary['runner'];meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),runner['exe_path'],runner['pdb_path']],check=True,capture_output=True,text=True).stdout);assert meta['mvid']==runner['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
assert comp['production_modify_builds']==0 and comp['actual_compute_getactual_publicpolicycollector_globalpublication_seed_privatewrites_native_game_operator_old_stale_mismatch_rejection_race_adverse']==0
scope=read(Q/'ACTUAL_EXECUTION_SCOPE.json');assert scope['raw_source_unchanged'] and len(scope['rows'])==2
for row in scope['rows']:
 verify(row['actual_runtime_ledger']);assert row['actual_logged_stages']==835 and row['direct_provider_API_calls']==763 and row['core_or_global_grouped_stages']==72
api=read(Q/'API_AND_GENERATION_RECONCILIATION.json');assert api['actual_rule']['invalidate_increment']==1 and api['actual_rule']['expected_main_sequence']==[0,1,2,3,4,5] and datetime.datetime.fromisoformat(api['at'])<datetime.datetime.fromisoformat(pin['at'])
producer=read(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json');accounting=read(Path(producer['root_results']['path']))['cache_accounting'];assert accounting==producer['accounting']
keys=['normal_provider_configure_calls','normal_provider_clear_calls','normal_provider_invalidate_calls','normal_provider_diagnostics_calls','normal_core_configure_calls','normal_core_publish_calls','normal_core_query_calls','normal_core_invalidate_calls'];assert sum(accounting[k] for k in keys)==accounting['total_normal_cache_calls']==46
verify(producer['additional_frozen_runnerbin_results']);assert read(Path(producer['additional_frozen_runnerbin_results']['path']))['culture']=='de-DE'
setup=read(Q/'PRE_EXECUTION_METADATA_SETUP_FAILURE.json');assert setup['candidate_calls']==0 and not setup['candidate_runner_started'] and setup['runner_builds']==1

delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='DIRECT_MASTER_TERMINAL_SENT' and delivery['actual_terminal_sends']==1 and sha(Path(delivery['return_tool_path']))==delivery['return_tool_sha256']
snap=json.loads(read(C/'MASTER_SOL_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_COMPLETION_SNAPSHOT_20261009.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['latestTurn']['id']=='01a120cd-940b-7561-8c58-454439174272'
vp=C/'MASTER_SOL_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_COMPLETION_VERIFICATION_20261009.json';assert not vp.exists();proof={'at':at,'guard_run':'MASTER-SOL-R14-COMPLETE-CONTINUE-20261009-01','guard_session':38756,'guard_pid':32404,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':891,'protected_paths_rehashed':7003,'runs':runs,'typed_rows':count,'canonical_pairs':115,'reference_pairs':68,'reference_bindings':278,'runner_metadata_master':meta,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_R14_QA_ACTUAL_THREAD_READ_20261009.json'),'scope_correction':scope,'producer_reconciliation':producer,'pre_execution_setup_qualification':setup,'selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'};vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'verified':True,'evidence':891,'protected':7003,'runs':runs,'typed_rows':count,'status':'PENDING_DISPOSITION'}))
