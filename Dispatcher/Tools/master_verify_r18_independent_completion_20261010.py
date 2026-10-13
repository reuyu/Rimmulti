"""Master read-only evidence and PE/PDB verification;no candidate or QA execution/build."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,sys,ast,uuid,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010'
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
rid='SOL-GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010-be5a988c6f01410f88b5769c0c555322'
assert comp['result_id']==manifest['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1'
assert sha(Q/'COMPLETION.json')=='71BE5152112A6AA8F57D295C9EBE5CEEA998DCBBFEEF4C5027D70C9619149012'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(manifest['files'])==362
for f in manifest['files']:verify(f)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==9374
for f in after:verify(f)
ackproof=read(C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_ACK_VERIFICATION_20261010.json')
assert sha(Q/'ACK_INITIAL.json')==ackproof['ack_sha256'] and read(Q/'ACK_INITIAL.json')['result_id']==rid
master=read(C/'MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_E1_VERIFICATION_20261010.json')['lineage']
for q in read(Q/'R18_FROZEN_LINEAGE.json')['candidates']:
 mm=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==mm['dll_sha256'] and q['pdb_sha256']==mm['pdb_sha256'] and q['guid']==q['codeview_guid']==mm['pdbGuid']==mm['codeviewGuid']
 for d in q['documents']:
  md=next(x for x in mm['documents'] if x['path']==d['path']);assert d['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(Path(d['frozen_source_path']))
thread=json.loads(read(C/'MASTER_SOL_R18_INDEPENDENT_TERMINAL_READ_20261010.json')['content'][0]['text'])
commands=[x for t in thread['turns'] for x in t.get('items',[]) if x.get('type')=='commandExecution']
build=read(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0
bc=next(x for x in commands if 'csc.dll' in x.get('command','') and 'build.rsp' in x.get('command',''));assert bc['exitCode']==0
pin=read(Q/'ORACLE_BEFORE_BUILD.json');admit=read(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')
for k in ['source','oracle','schema','allocations']:verify(pin[k])
for k in ['WP','source','oracle']:verify(admit[k])
for k in ['fixture_files','config_files']:
 for f in pin[k]:verify(f)
for f in admit['pins']:verify(f)
assert not pin['output_derived_oracle'] and not admit['output_derived_oracle'] and admit['prebuild_candidate_calls']==0
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');process=read(Q/'FRESH_PROCESS_PROOF.json');schema=read(Q/'FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json');runs=[]
assert len(process['rows'])==2
for n,row in enumerate(process['rows'],1):
 for k in ['context','host','tool','stdout','stderr','inventory']:verify(row[k])
 root=Path(row['context']['path']).parent;pre=read(Q/f'PRE_RUN{n}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');host=read(Path(row['host']['path']));context=read(Path(row['context']['path']));tool=read(Path(row['tool']['path']));raw=Path(row['stdout']['path']).read_text(encoding='utf-8-sig')
 assert pre['files']==post['files'] and len(pre['files'])==167 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']==host['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==context['culture']==host['requested_culture']==host['observed_culture']==['en-US','de-DE'][n-1]
 assert row['actual_numeric_exit']==post['actual_numeric_exit']==host['numeric_exit']==tool['exit_code']==1
 assert row['owned_host_pid']==post['host_pid']==host['owned_child_pid']>0 and context['argv']==host['argv']==pre['argv'] and context['cwd']==host['cwd']==pre['cwd']
 cmd=next(x for x in commands if f'host_launch.py {n}' in x.get('command',''));assert cmd['exitCode']==1 and Path(cmd['cwd']).resolve()==R.resolve()
 actual=json.loads(tool['output'].splitlines()[0]);assert actual['owned_child_pid']==host['owned_child_pid'] and actual['numeric_exit']==1 and actual['observed_culture']==context['culture']
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==125 and normal['failed_assertions']==24
 assert sum(x['status']=='PASS' for x in normal['results'])==101 and sum(x['status']=='FAIL' for x in normal['results'])==24
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==101 and sum(x.startswith('FAIL ') for x in raw.splitlines())==24
 assert all('_OPAQUE_' in x['id'] and any(x['id'].endswith(s) for s in ['FULL_LOSSLESS','REDACTED_LOSSLESS','AFTER_EDITS_LOSSLESS']) for x in normal['results'] if x['status']=='FAIL')
 assert normal['selected_sha256']==comp['selected_sha256'] and normal['selected_mvid']==comp['selected_mvid']
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_prepin_matched'] and len(loaded['files'])==10
 mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:
  assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path'])) and mvid(Path(f['path']))==f['mvid']
 inv=read(Path(row['inventory']['path']));assert inv['file_count']==len(inv['files'])==147 and inv['every_generated_output_recursive'] and inv['excluded_self_only']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 assert actualset=={str(Path(f['path']).resolve()).lower() for f in inv['files']}
 for f in inv['files']:verify(f)
 ledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json')
 assert len(ledger)==298 and sum(x['scope']=='direct_pure' for x in ledger)==202 and sum(x['scope']=='grouped_snapshot_read' for x in ledger)==96
 assert not any(re.search(r'ProcessIdentity|Process\.|GetCurrentProcess|MainModule|WorkerBridgeComponent|Awake|Bootstrapper|ComputeActual|GetActual|Invalidate|Cache|stale|reject|mismatch',x['api'],re.I) for x in ledger)
 assert datetime.datetime.fromisoformat(admit['at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at'])<datetime.datetime.fromisoformat(host['completed_at'])<datetime.datetime.fromisoformat(post['at'])
 meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),pre['runner']['exe_path'],pre['runner']['pdb_path']],check=True,capture_output=True,text=True).stdout)
 assert meta['mvid']==pre['runner']['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
 runs.append({'run_id':row['run_id'],'pid':row['owned_host_pid'],'culture':row['culture'],'exit':1,'pass':101,'fail':24,'prepost':167,'loaded':10,'output_files':147,'direct_calls':202,'grouped_reads':96})
assert runs[0]['pid']!=runs[1]['pid'] and read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_firstoutputs_unchanged']
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=failed=0
for entry in schema['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['compared_rows']
 errors=0
 for row in rows:
  match=equal(row);assert row['matched']==match;errors+=not match
 assert errors==entry['failed_rows'] and entry['all_matched']==(errors==0);count+=len(rows);failed+=errors
assert count==5576 and failed==256
for key,num in [('meaningful_crossprocess_byte_pairs',66),('independent_reference_pairs',4)]:
 assert len(summary[key])==num
 for pair in summary[key]:verify(pair['run1']);verify(pair['run2']);assert Path(pair['run1']['path']).read_bytes()==Path(pair['run2']['path']).read_bytes()
bindings=schema['candidate_reference_bindings'];assert len(bindings)==52;bindingfail=0
for row in bindings:
 verify(row['actual'])
 if 'reference' in row:
  verify(row['reference']);match=Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
 else:
  verify(row['oracle']);oracle=read(Path(row['oracle']['path']))['policy_cases'][Path(row['actual']['path']).name.split('.policy.json')[0]]
  expected=oracle['expected_json'].encode('utf8');assert hashlib.sha256(expected).hexdigest().upper()==oracle['expected_digest']==row['expected_digest'];match=expected==Path(row['actual']['path']).read_bytes()
 assert row['matched']==match;bindingfail+=not match
assert bindingfail==16
source=(Q/'Program.cs').read_text(encoding='utf-8-sig');assert not any(x in source for x in ['System.Diagnostics.Process','GetCurrentProcess','VerifyProcessIdentity(','TryInstallOperatorStartupConfig','WorkerBridgeComponent.ActiveStartupConfig'])
audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')
for k in ['source','prospective_row','scope_metadata_reconciliation','build_warning_capture_limit']:verify(audit[k])
assert audit['source_oracle_values_equal_prospective'] and audit['independentpolicyJSON_digest_hostprepared_beforebuild'] and audit['finalsource_oracle_runner_unchanged_afteronlybuild_andruns']
reconcile=read(Q/'METADATA_REVIEW_RECONCILIATION.json')
assert reconcile['producer_manual_counter']['actual_frozen_API_LEDGER_sum_both_runs']==16
assert reconcile['ownership_control_scope']['connected_source_config_edits_constructor_ToSnapshot']==8 and reconcile['ownership_control_scope']['detached_returned_policy_edits_connected_all_routes']==16
for name in ['run_en_us','run_de_de']:
 ledger=read(R/'Dispatcher/CANDIDATES/G05R18-befc4fba/scratch/EngineGate05R18ConfigAdmissionSeal'/name/'API_LEDGER.json');assert sum(ledger.values())==16
assert read(Q/'BUILD_CAPTURE_LIMITATIONS.json')['full_compile_warning_stream_unavailable']
delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='ONE_ACTUAL_TERMINAL_SEND_TOOL_ACCEPTED' and delivery['actual_send_count']==1 and not delivery['unknown_delivery']
ret=read(Q/'RETURN_TOOL_PROOF.json');assert ret['result_id']==rid and not ret['actual_tool_result'].get('isError') and json.loads(ret['actual_tool_result']['content'][0]['text'])['threadId']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
snap=json.loads(read(C/'MASTER_SOL_R18_INDEPENDENT_TERMINAL_SNAPSHOT_20261010.json')['content'][0]['text'])['polls'][0]
assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
vp=C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-SOL-R18-COMPLETE-20261010-01','guard_session':36347,'guard_pid':34784,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':362,'protected_paths_rehashed':9374,'runs':runs,'typed_rows':count,'typed_mismatch_rows':failed,'repeatability_pairs':66,'reference_pairs':4,'reference_bindings':52,'reference_bindings_failed':16,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_SOL_R18_INDEPENDENT_TERMINAL_READ_20261010.json'),'scope_metadata_reconciliation':reconcile,'compiler_warning_stream':'TRUNCATED_LIMITATION_RETAINED_NO_REBUILD','selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'verified':True,'evidence':362,'protected':9374,'runs':runs,'typed_rows':count,'typed_failed':failed,'status':'PENDING_DISPOSITION'},ensure_ascii=True))

