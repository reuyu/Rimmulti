"""Read evidence and PE/PDB metadata only. No production or QA runner execution/build."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010'
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
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();comp=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json');rid='SOL-GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010-4cc8216bb6e144339a4dce4bc543d344'
assert comp['result_id']==m['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1'
assert sha(Q/'COMPLETION.json')=='C2316E4DE43CD8DF6740DA53622D524111C7006A9524931D07B2EC89EC83732C'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(m['files'])==193
for f in m['files']:verify(f)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==9082
for f in after:verify(f)
ack=read(Q/'ACK_INITIAL.json');ackproof=read(C/'MASTER_SOL_R17_OWNED_BOOTSTRAP_INDEPENDENT_ACK_SCOPE_VERIFICATION_20261010.json');assert sha(Q/'ACK_INITIAL.json')==ackproof['ack_sha256'] and ack['result_id']==rid
line=read(Q/'R17_FROZEN_LINEAGE.json');master=read(C/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_E1_VERIFICATION_20261010.json')['lineage']
for q in line['candidates']:
 mm=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==mm['dll_sha256'] and q['pdb_sha256']==mm['pdb_sha256'] and q['guid']==q['codeview_guid']==mm['pdbGuid']==mm['codeviewGuid']
 for d in q['documents']:
  md=next(x for x in mm['documents'] if x['path']==d['path']);assert d['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(Path(d['frozen_source_path']))
thread=json.loads(read(C/'MASTER_R17_QA_ACTUAL_THREAD_READ_VALID_20261010.json')['content'][0]['text']);items=[x for t in thread['turns'] for x in t.get('items',[])];commands=[x for x in items if x.get('type')=='commandExecution']
build=read(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0 and build['actual_QA_runner_build_count']==1
bc=next(x for x in commands if 'csc.dll' in x.get('command','') and 'BUILD_RAW' in x.get('command',''));assert bc['exitCode']==0
pin=read(Q/'ORACLE_BEFORE_BUILD.json');admit=read(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')
for k in ['source','oracle','schema','allocations','host_scope_clarification','execution_admission']:verify(pin[k])
for k in ['WP','host_telemetry_clarification','source','oracle']:verify(admit[k])
assert pin['host_scope_clarification']['sha256']==admit['host_telemetry_clarification']['sha256']=='B35BF9836E70B162571730D301CF2452F7E01F080568F80C69D0FD47414BAB59'
assert not pin['output_derived_oracle'] and admit['prebuild_candidate_calls']==0 and admit['host_game_Worker_validator_native_producer_oldrunner_launches']==0
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');process=read(Q/'FRESH_PROCESS_PROOF.json');runs=[];assert len(process['rows'])==2
for n,row in enumerate(process['rows'],1):
 for k in ['context','host','tool','stdout','stderr','inventory']:verify(row[k])
 root=Path(row['context']['path']).parent;pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');host=read(Path(row['host']['path']));context=read(Path(row['context']['path']));tool=read(Path(row['tool']['path']));raw=Path(row['stdout']['path']).read_text(encoding='utf-8-sig')
 assert pre['files']==post['files'] and len(pre['files'])==158 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']==host['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==context['culture']==host['requested_culture']==host['observed_culture']==['en-US','de-DE'][n-1]
 assert row['actual_numeric_exit']==post['actual_numeric_exit']==host['numeric_exit']==tool['exit_code']==0
 assert row['owned_host_pid']==post['host_pid']==host['owned_child_pid']>0 and context['argv']==host['argv']==pre['argv'] and context['cwd']==host['cwd']==pre['cwd']
 cmd=next(x for x in commands if f'host_launch.py {n}' in x.get('command',''));assert cmd['exitCode']==0 and cmd['cwd']==tool['cwd'] and 'numeric_exit' in cmd['output']['text']
 actual=json.loads(tool['output'].splitlines()[0]);assert actual['owned_child_pid']==host['owned_child_pid'] and actual['numeric_exit']==0 and actual['observed_culture']==context['culture']
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==29 and all(x['status']=='PASS' for x in normal['results']) and normal['failed_assertions']==0
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==29 and not any(x.startswith('FAIL ') for x in raw.splitlines())
 assert normal['selected_sha256']==comp['selected_sha256'] and normal['selected_mvid']==comp['selected_mvid']
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_prepin_matched'] and len(loaded['files'])==10;mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path']))
 inventory=read(Path(row['inventory']['path']));assert inventory['file_count']==len(inventory['files'])==71 and inventory['every_generated_output_recursive'] and inventory['excluded_self_only']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'};assert actualset=={str(Path(f['path']).resolve()).lower() for f in inventory['files']}
 for f in inventory['files']:verify(f)
 ledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json');assert len(ledger)==54 and sum(x['scope']=='direct_pure' for x in ledger)==38 and sum(x['scope']=='grouped_snapshot_read' for x in ledger)==16
 assert all('VerifyProcessIdentity' not in x['api'] and 'ConfigureOperatorStartup' not in x['api'] and 'ResetOperatorStartup' not in x['api'] for x in ledger)
 assert datetime.datetime.fromisoformat(admit['at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at'])<datetime.datetime.fromisoformat(host['completed_at'])<datetime.datetime.fromisoformat(post['at'])
 runs.append({'run_id':row['run_id'],'pid':row['owned_host_pid'],'culture':row['culture'],'exit':0,'pass':29,'fail':0,'prepost':158,'loaded':10,'output_files':71,'direct_calls':38,'grouped_reads':16})
assert runs[0]['pid']!=runs[1]['pid'];assert read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_firstoutputs_unchanged']
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=0
for entry in summary['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['fulltyped_compared_rows'] and entry['all_matched']
 for x in rows:assert x['matched'] and equal(x),str(x)
 count+=len(rows)
assert count==2864
for key,num in [('pairs',18),('reference_pairs',4)]:
 assert len(summary[key])==num
 for pair in summary[key]:verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
assert len(summary['bindings'])==28
for row in summary['bindings']:
 verify(row['actual']);assert row['matched']
 if 'reference' in row:
  verify(row['reference']);assert Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
 else:
  verify(row['oracle']);assert row['expected_digest']==row['actual']['sha256']
  policy=read(Path(row['oracle']['path']))['policy_cases'][Path(row['actual']['path']).name.split('.policy.json')[0]]
  expected=policy['expected_json'].encode('utf8');assert hashlib.sha256(expected).hexdigest().upper()==policy['expected_digest']==row['expected_digest'] and expected==Path(row['actual']['path']).read_bytes()
runner=summary['runner'];meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),runner['exe_path'],runner['pdb_path']],check=True,capture_output=True,text=True).stdout);assert meta['mvid']==runner['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
source=(Q/'Program.cs').read_text(encoding='utf-8-sig');assert 'System.Diagnostics.Process' not in source and 'GetCurrentProcess' not in source and 'VerifyProcessIdentity(' not in source
audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json');verify(audit['source']);verify(audit['prospective_row']);assert audit['source_equals_prospective'] and audit['oracle_casevalues_notmodified_byoutputs'] and audit['finalsource_oracle_runner_unchanged_afteronlybuild_andruns']
producer=read(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json');assert producer['TEST03_scope_deviation_calls']==3 and producer['actualrecorded_cultures']==['ko-KR']*3 and producer['global_state_isolation_qualification_requires_Master'] and producer['producerreplays']==0 and producer['noall5labelscopePASS']
verify(producer['source']);verify(producer['original_A_scope']);verify(producer['execute_runs_source'])
psource=Path(producer['source']['path']).read_text(encoding='utf-8-sig');assert 'ConfigureOperatorStartup' in psource and 'ResetOperatorStartupConfig' in psource
for row in producer['rows']:
 for k in ['result','manual_ledger','posthoc4inventory']:verify(row[k])
 ledger=read(Path(row['manual_ledger']['path']));assert ledger['ConfigureOperatorStartupCalls']==ledger['ResetOperatorStartupConfigCalls']==ledger['VerifyProcessIdentityCalls']==1
scope=read(Q/'ACTUAL_EXECUTION_SCOPE.json');assert scope['source_no_process_queries'] and not scope['actual_native_issuer_authority_proof']
delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='AUTHORIZED_TERMINAL_SEND_TOOL_SUCCEEDED' and delivery['attempts']==1
ret=read(Path(delivery['tool_proof']));assert ret['result_id']==rid and not ret['actual_tool_result'].get('isError') and json.loads(ret['actual_tool_result']['content'][0]['text'])['threadId']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
snap=json.loads(read(C/'MASTER_SOL_R17_INDEPENDENT_COMPLETION_SNAPSHOT_20261010.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
vp=C/'MASTER_SOL_R17_OWNED_BOOTSTRAP_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json'
if vp.exists():assert read(vp)['verification_status']=='VERIFIED_PENDING_MASTER_DISPOSITION' and read(vp)['completion_sha256']==sha(Q/'COMPLETION.json')
proof={'at':at,'guard_run':'MASTER-SOL-R17-COMPLETE-20261010-01','guard_session':11454,'guard_pid':5480,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':193,'protected_paths_rehashed':9082,'runs':runs,'typed_rows':count,'canonical_pairs':18,'reference_pairs':4,'reference_bindings':28,'runner_metadata_master':meta,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_R17_QA_ACTUAL_THREAD_READ_20261010.json'),'scope_correction':scope,'producer_reconciliation':producer,'selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'verified':True,'evidence':193,'protected':9082,'runs':runs,'typed_rows':count,'status':'PENDING_DISPOSITION'}))
