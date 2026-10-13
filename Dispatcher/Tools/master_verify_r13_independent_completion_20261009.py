"""Evidence and PE metadata only; candidate/runner build or execution zero."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,re,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-INDEPENDENT-S1-20261009'
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
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();comp=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json');rid='SOL-GATE05-R13-POLICY-CACHE-LIFECYCLE-INDEPENDENT-S1-20261009-a59c76c5155a49a094a044837a5e6099'
assert comp['result_id']==m['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1';assert sha(Q/'COMPLETION.json')=='9CC5B6B2B73C5C2F8CB9272B5F72C160274153670124ADF113A30E4784F0C36F'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(m['files'])==902
for f in m['files']:verify(f)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==6021
for f in after:verify(f)
oracle=read(Q/'INPUT_EXPECTED_SEMANTICS.json');pin=read(Q/'ORACLE_BEFORE_BUILD.json');verify(pin['oracle']);assert not oracle['expected_policies_derived_from_actual'] and len(oracle['policy_cases'])==14 and len(oracle['cache_policies'])==2
thread=json.loads(read(C/'MASTER_R13_QA_ACTUAL_THREAD_READ_20261009.json')['content'][0]['text']);commands=[x for x in thread['turns'][0]['items'] if x.get('type')=='commandExecution'];summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');process=read(Q/'FRESH_PROCESS_PROOF.json');runs=[]
assert len(process['rows'])==2
for n,row in enumerate(process['rows'],1):
 for k in ['context','raw','tool','all_generated_output_inventory']:verify(row[k])
 root=Path(row['context']['path']).parent;pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');tool=read(Path(row['tool']['path']));raw=Path(row['raw']['path']).read_text(encoding='utf-8-sig');context=read(Path(row['context']['path']))
 assert pre['files']==post['files'] and len(pre['files'])==150 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==['en-US','de-DE'][n-1] and row['actual_numeric_exit']==tool['exit_code']==post['actual_tool_exit_code']==0
 command=next(x for x in commands if row['run_id'] in x.get('command','') and 'QaCodecRunner.exe' in x.get('command','') and 'RAW_CONSOLE' in x.get('command',''))
 assert command['exitCode']==0 and command['cwd']==tool['cwd']==row['cwd'] and '$LASTEXITCODE' in command['command']
 assert command['output']['text']==tool['output'] or (command['output'].get('truncated') and tool['output'].startswith(command['output']['text']))
 tail=int(re.search(r'-Tail (\d+)',tool['cmd'])[1]);assert raw.splitlines()[-tail:]==tool['output'].splitlines();assert sum(x.startswith('PASS ') for x in raw.splitlines())==339 and not any(x.startswith('FAIL ') for x in raw.splitlines())
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==339 and all(x['status']=='PASS' for x in normal['results'])
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_pre_pin_matched'] and len(loaded['files'])==12;mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path']))
 inventory=read(Path(row['all_generated_output_inventory']['path']));assert inventory['file_count']==len(inventory['files'])==411 and inventory['recursive_every_generatedfile']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'};assert actualset=={str(Path(f['path']).resolve()).lower() for f in inventory['files']}
 for f in inventory['files']:verify(f)
 ledger=read(root/'ACTUAL_CACHE_LIFECYCLE_CALL_LEDGER.json');assert len(ledger)==72 and sum(x['api']=='TryPublishComputedEntry_CURRENT_MATCHING_ONLY' for x in ledger)==5 and sum(x['api']=='ContentProfileCacheCore.constructor' for x in ledger)==2
 assert row['run_id'] in raw and str(row['pid']) in raw and raw.startswith('Independent reference byte stage complete before candidate calls: 68')
 assert datetime.datetime.fromisoformat(oracle['created_at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(post['at'])
 runs.append({'run_id':row['run_id'],'pid':row['pid'],'culture':row['culture'],'exit':0,'pass':339,'fail':0,'prepost':150,'loaded':12,'output_files':411,'stage_ledger':72,'root':str(root)})
 assert 'cache calls0' in raw or 'cache calls 0' in raw
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
assert comp['production_modify_builds']==0 and comp['actual_getactual_compute_globalpublication_seed_reflectionwrite_collection_game_native_operator_old_stale_mismatch_rejection_race_adverse']==0
scope=read(Q/'ACTUAL_EXECUTION_SCOPE_AND_RAW_SUMMARY_CORRECTION.json');assert scope['raw_source_unchanged'] and len(scope['rows'])==2
delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='DIRECT_MASTER_TERMINAL_SENT' and delivery['actual_terminal_sends']==1 and sha(Path(delivery['return_tool_path']))==delivery['return_tool_sha256']
snap=json.loads(read(C/'MASTER_SOL_R13_POLICY_CACHE_LIFECYCLE_INDEPENDENT_COMPLETION_SNAPSHOT_20261009.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['latestTurn']['id']=='01a1206c-833a-7530-97ab-66ebd84e494e'
vp=C/'MASTER_SOL_R13_POLICY_CACHE_LIFECYCLE_INDEPENDENT_COMPLETION_VERIFICATION_20261009.json';assert not vp.exists();proof={'at':at,'guard_run':'MASTER-SOL-R13-INDEPENDENT-COMPLETE-20261009-01','guard_session':77102,'guard_pid':25976,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':902,'protected_paths_rehashed':6021,'runs':runs,'typed_rows':count,'canonical_pairs':115,'reference_pairs':68,'reference_bindings':278,'runner_metadata_master':meta,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_R13_QA_ACTUAL_THREAD_READ_20261009.json'),'scope_correction':scope,'selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'};vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'verified':True,'evidence':902,'protected':6021,'runs':runs,'typed_rows':count,'status':'PENDING_DISPOSITION'}))
