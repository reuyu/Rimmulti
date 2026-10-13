"""Master read-only evidence and PE/PDB verification;no candidate or QA execution/build."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,sys,ast,uuid,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011'
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
 return type(e)==type(a) and e==a
# Only the existing pure PE-byte reader definition,not its old inventory top-level.
defs=[n for n in ast.parse((H/'bootstrap/verify_local_identity.py').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid']
exec(compile(ast.Module(body=defs,type_ignores=[]),'master_readonly_PE_module_MVID','exec'),globals())
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();comp=read(Q/'COMPLETION.json');manifest=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json')
rid='SOL-GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011-4245a7b9c3a8434993de3c5f411b762a'
assert comp['result_id']==manifest['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1'
assert sha(Q/'COMPLETION.json')=='7170B8090D4AC40C959D84616763CC9194C5052145BD818F337FBDA744833CA0'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(manifest['files'])==474
for f in manifest['files']:verify(f)
print('474 evidence SHA-size matched',flush=True)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==10346
for f in after:verify(f)
print('10346 protected SHA-size matched',flush=True)
ackproof=read(C/'MASTER_SOL_R20_TRUSTED_STARTUP_INDEPENDENT_ACK_VERIFICATION_20261011.json')
assert sha(Q/'ACK_INITIAL.json')==ackproof['ack_sha256'] and read(Q/'ACK_INITIAL.json')['result_id']==rid
master=read(C/'MASTER_GATE05_R20_TRUSTED_STARTUP_E1_VERIFICATION_20261011.json')['lineage']
for q in read(Q/'R20_FROZEN_LINEAGE.json')['candidates']:
 mm=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==mm['dll_sha256'] and q['pdb_sha256']==mm['pdb_sha256'] and q['guid']==q['codeview_guid']==mm['pdbGuid']==mm['codeviewGuid']
 for d in q['documents']:
  md=next(x for x in mm['documents'] if x['path']==d['path']);assert d['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(Path(d['frozen_source_path']))
thread=json.loads(read(C/'MASTER_SOL_R20_INDEPENDENT_TERMINAL_READ_20261011.json')['content'][0]['text'])
build=read(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0
assert read(Q/'BUILD_INVOCATION_TOOL_PROOF.json')['exit_code']==0
print('lineage and actual build metadata matched',flush=True)
pin=read(Q/'ORACLE_BEFORE_BUILD.json');admit=read(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')
for k in ['source','oracle','schema','allocations']:verify(pin[k])
for k in ['WP','source','oracle']:verify(admit[k])
for k in ['fixture_files','config_files']:
 for f in pin[k]:verify(f)
for f in admit['pins']:verify(f)
assert not pin['output_derived_oracle'] and not admit['output_derived_oracle'] and admit['prebuild_candidate_calls']==0
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');process=read(Q/'FRESH_PROCESS_PROOF.json');schema=read(Q/'FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json');runs=[]
assert len(process['rows'])==2
print('prospective pins matched; verifying runs',flush=True)
for n,row in enumerate(process['rows'],1):
 for k in ['context','host','tool','stdout','stderr','inventory']:verify(row[k])
 root=Path(row['context']['path']).parent;pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');host=read(Path(row['host']['path']));context=read(Path(row['context']['path']));tool=read(Path(row['tool']['path']));raw=Path(row['stdout']['path']).read_text(encoding='utf-8-sig')
 assert pre['files']==post['files'] and len(pre['files'])==192 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']==host['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==context['culture']==host['requested_culture']==host['observed_culture']==['en-US','de-DE'][n-1]
 assert row['actual_numeric_exit']==post['actual_numeric_exit']==host['numeric_exit']==tool['exit_code']==1
 assert row['owned_host_pid']==post['host_pid']==host['owned_child_pid']>0 and context['argv']==host['argv']==pre['argv'] and context['cwd']==host['cwd']==pre['cwd']
 assert Path(host['cwd']).is_absolute()
 actual=json.loads(tool['output'].splitlines()[0]);assert actual['owned_child_pid']==host['owned_child_pid'] and actual['numeric_exit']==1 and actual['observed_culture']==context['culture']
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==181 and normal['failed_assertions']==8
 assert sum(x['status']=='PASS' for x in normal['results'])==173 and sum(x['status']=='FAIL' for x in normal['results'])==8
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==173 and sum(x.startswith('FAIL ') for x in raw.splitlines())==8
 assert all(x['id'].startswith('RECEIPT_') and x['id'].endswith('_FULL_REDACTION') for x in normal['results'] if x['status']=='FAIL')
 assert normal['selected_sha256']==comp['selected_sha256'] and normal['selected_mvid']==comp['selected_mvid']
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_prepin_matched'] and len(loaded['files'])==10
 mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:
  assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path'])) and mvid(Path(f['path']))==f['mvid']
 inv=read(Path(row['inventory']['path']));assert inv['file_count']==len(inv['files'])==197 and inv['every_generated_output_recursive'] and inv['excluded_self_only']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 assert actualset=={str(Path(f['path']).resolve()).lower() for f in inv['files']}
 for f in inv['files']:verify(f)
 ledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json')
 assert len(ledger)==426 and sum(x['scope']=='direct_pure' for x in ledger)==282 and sum(x['scope']=='grouped_snapshot_read' for x in ledger)==128 and sum(x['scope']=='grouped_receipt_read' for x in ledger)==16
 assert not any(re.search(r'ProcessIdentity|Process\.|GetCurrentProcess|MainModule|WorkerBridgeComponent|Awake|Bootstrapper|ComputeActual|GetActual|Invalidate|Cache|stale|reject|mismatch',x['api'],re.I) for x in ledger)
 assert datetime.datetime.fromisoformat(admit['at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at'])<datetime.datetime.fromisoformat(host['completed_at'])<datetime.datetime.fromisoformat(post['at'])
 print('run '+str(n)+' identity, raw, outputs, ledger matched; metadata inspect',flush=True)
 meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),pre['runner']['exe_path'],pre['runner']['pdb_path']],check=True,capture_output=True,text=True,timeout=20).stdout)
 assert meta['mvid']==pre['runner']['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
 runs.append({'run_id':row['run_id'],'pid':row['owned_host_pid'],'culture':row['culture'],'exit':1,'pass':173,'fail':8,'prepost':192,'loaded':10,'output_files':197,'direct_calls':282,'grouped_reads':144})
assert runs[0]['pid']!=runs[1]['pid'] and read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_firstoutputs_unchanged']
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=failed=0
for entry in schema['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['compared_rows']
 errors=0
 for row in rows:
  match=equal(row);assert row['matched']==match;errors+=not match
 assert errors==entry['failed_rows'] and entry['all_matched']==(errors==0);count+=len(rows);failed+=errors
assert count==8216 and failed==16
assert len(summary['all_byte_pairs'])==90 and summary['reference_pair_count']==4
for pair in summary['all_byte_pairs']:
 verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
bindings=schema['candidate_reference_bindings'];assert len(bindings)==52;bindingfail=0
for row in bindings:
 verify(row['actual'])
 if 'reference' in row:
  verify(row['reference']);match=Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
 else:
  verify(row['oracle']);oracle=read(Path(row['oracle']['path']))['policy_cases'][Path(row['actual']['path']).name.split('.policy.json')[0]]
  expected=oracle['expected_json'].encode('utf8');assert hashlib.sha256(expected).hexdigest().upper()==oracle['expected_digest']==row['expected_digest'];match=expected==Path(row['actual']['path']).read_bytes()
 assert row['matched']==match;bindingfail+=not match
assert bindingfail==0
receipt_bindings=[r for r in summary['bindings'] if 'redacted_actual' in r]
assert len(receipt_bindings)==16
for row in receipt_bindings:
 for key in ['graph','oracle','redacted_actual','redacted_reference']:verify(row[key])
 assert row['all11_receipt_properties_and15_nested_andpolicyrecord_matched']
 assert not row['matched'] and row['changed_leaf']=='snapshot.issuedAtUtc'
 expected=read(Path(row['redacted_reference']['path']));actual=read(Path(row['redacted_actual']['path']))
 assert expected['snapshot']['issuedAtUtc']==row['expected']=='2026-10-10T00:00:00.0000000Z'
 assert actual['snapshot']['issuedAtUtc']==row['actual']=='2026-10-10T00:00:00Z'
 assert datetime.datetime.fromisoformat(row['expected'])==datetime.datetime.fromisoformat(row['actual'])
 expected['snapshot']['issuedAtUtc']=actual['snapshot']['issuedAtUtc'];assert expected==actual
 bindingfail+=1
assert bindingfail==16
source=(Q/'Program.cs').read_text(encoding='utf-8-sig');assert not any(x in source for x in ['System.Diagnostics.Process','GetCurrentProcess','VerifyProcessIdentity(','TryInstallOperatorStartupConfig','WorkerBridgeComponent.ActiveStartupConfig'])
audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')
for k in ['source','normal_oracle','receipt_oracle','prospective','prepin_annotation_setup_reconciliation']:verify(audit[k])
assert audit['old_source_oracle_readonly_reference_only'] and audit['no_oldrunner_or_output_reuse']
assert audit['final_source_oracles_runner_unchanged_after_only_finalbuild_and2runs'] and audit['no_output_derived_expectations']
streams=read(Q/'COMPLETE_BUILD_STREAM_BINDING.json')
for k in ['tool','wrapper','stdout','stderr']:verify(streams[k])
assert streams['actual_final_builds']==1 and streams['compiler_numeric_exit']==0 and streams['stdout']['bytes']==24464 and streams['stderr']['bytes']==0
assert streams['full_streams_directfiles'] and streams['prepin_setup_failures_compiler_calls0_preserved']
reconcile=read(Q/'METADATA_SCOPE_RECONCILIATION.json')
assert reconcile['controlling_producer_inventory_count']['actual_frozen_declared_unique_rows_each']==15
assert not reconcile['oracle_values_source_runner_runoutputs_modified_after_candidate_calls']
for name in ['run_en_us','run_de_de']:
 root=R/'Dispatcher/CANDIDATES/G05R20-e35ff656/scratch/EngineGate05R20TrustedStartup'/name
 inv=read(root/'OUTPUT_INVENTORY.json');assert len(inv)==15
 actualnames={str(q.relative_to(root)) for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'}
 assert actualnames=={f['relative_path'] for f in inv}
 for f in inv:
  q=root/f['relative_path'];assert sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes']
 ledger=read(root/'API_LEDGER.json');assert sum(ledger.values())==83
 res=read(root/'RESULTS.json');pathcase=next(x for x in res['Tests'] if x['TestName']=='TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_HELPER')
 assert pathcase['NonFullChecksPassed']==pathcase['TotalNonFullChecks']==7
delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='ONE_ACTUAL_TERMINAL_SEND_TOOL_ACCEPTED' and delivery['actual_send_count']==1 and not delivery['unknown_delivery']
ret=read(Q/'RETURN_TOOL_PROOF.json');assert ret['result_id']==rid and not ret['actual_tool_result'].get('isError')
assert json.loads(ret['actual_tool_result']['content'][0]['text'])['threadId']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
snap=json.loads(read(C/'MASTER_SOL_R20_INDEPENDENT_TERMINAL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
vp=C/'MASTER_SOL_R20_TRUSTED_STARTUP_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-SOL-R20-COMPLETE-20261011-01','guard_session':54820,'guard_pid':30204,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':474,'protected_paths_rehashed':10346,'runs':runs,'typed_rows':count,'typed_mismatch_rows':failed,'repeatability_pairs':90,'reference_pairs':4,'reference_bindings':68,'reference_bindings_failed':16,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_SOL_R20_INDEPENDENT_TERMINAL_READ_20261011.json'),'scope_metadata_reconciliation':reconcile,'compiler_warning_stream':'COMPLETE_OWNED_RAW_24464_BYTES_EXIT0','thread_operational_status':'COMPLETED_IDLE','terminal_delivery_status':'ONE_ACTUAL_TERMINAL_SEND_ACCEPTED','artifact_terminal_status':'COMPLETED_VERIFIED_ACTUAL_THREAD_MATCHED','selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'verified':True,'evidence':474,'protected':10346,'runs':runs,'typed_rows':count,'typed_failed':failed,'status':'PENDING_DISPOSITION'},ensure_ascii=True))

