"""Master read-only evidence and PE/PDB verification;no candidate or QA execution/build."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,sys,ast,uuid,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010'
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
rid='SOL-GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010-2c4a145f15334594bba451900223477a'
assert comp['result_id']==manifest['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1'
assert sha(Q/'COMPLETION.json')=='EC88A9E0895C7E8A66F696730B0B0F028339B6E2E88533F26F46B82331FC3890'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(manifest['files'])==390
for f in manifest['files']:verify(f)
print('390 evidence SHA-size matched',flush=True)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==9841
for f in after:verify(f)
print('9841 protected SHA-size matched',flush=True)
ackproof=read(C/'MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_ACK_VERIFICATION_20261010.json')
assert sha(Q/'ACK_INITIAL.json')==ackproof['ack_sha256'] and read(Q/'ACK_INITIAL.json')['result_id']==rid
master=read(C/'MASTER_GATE05_R19_OPAQUE_POLICY_E1_VERIFICATION_20261010.json')['lineage']
for q in read(Q/'R19_FROZEN_LINEAGE.json')['candidates']:
 mm=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==mm['dll_sha256'] and q['pdb_sha256']==mm['pdb_sha256'] and q['guid']==q['codeview_guid']==mm['pdbGuid']==mm['codeviewGuid']
 for d in q['documents']:
  md=next(x for x in mm['documents'] if x['path']==d['path']);assert d['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(Path(d['frozen_source_path']))
thread=json.loads(read(C/'MASTER_SOL_R19_INDEPENDENT_TERMINAL_READ_20261011.json')['content'][0]['text'])
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
 assert pre['files']==post['files'] and len(pre['files'])==181 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']==host['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==context['culture']==host['requested_culture']==host['observed_culture']==['en-US','de-DE'][n-1]
 assert row['actual_numeric_exit']==post['actual_numeric_exit']==host['numeric_exit']==tool['exit_code']==0
 assert row['owned_host_pid']==post['host_pid']==host['owned_child_pid']>0 and context['argv']==host['argv']==pre['argv'] and context['cwd']==host['cwd']==pre['cwd']
 assert Path(host['cwd']).is_absolute()
 actual=json.loads(tool['output'].splitlines()[0]);assert actual['owned_child_pid']==host['owned_child_pid'] and actual['numeric_exit']==0 and actual['observed_culture']==context['culture']
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==117 and normal['failed_assertions']==0
 assert sum(x['status']=='PASS' for x in normal['results'])==117 and sum(x['status']=='FAIL' for x in normal['results'])==0
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==117 and sum(x.startswith('FAIL ') for x in raw.splitlines())==0
 assert all('_OPAQUE_' in x['id'] and any(x['id'].endswith(s) for s in ['FULL_LOSSLESS','REDACTED_LOSSLESS','AFTER_EDITS_LOSSLESS']) for x in normal['results'] if x['status']=='FAIL')
 assert normal['selected_sha256']==comp['selected_sha256'] and normal['selected_mvid']==comp['selected_mvid']
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_prepin_matched'] and len(loaded['files'])==10
 mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:
  assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path'])) and mvid(Path(f['path']))==f['mvid']
 inv=read(Path(row['inventory']['path']));assert inv['file_count']==len(inv['files'])==148 and inv['every_generated_output_recursive'] and inv['excluded_self_only']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 assert actualset=={str(Path(f['path']).resolve()).lower() for f in inv['files']}
 for f in inv['files']:verify(f)
 ledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json')
 assert len(ledger)==266 and sum(x['scope']=='direct_pure' for x in ledger)==186 and sum(x['scope']=='grouped_snapshot_read' for x in ledger)==80
 assert not any(re.search(r'ProcessIdentity|Process\.|GetCurrentProcess|MainModule|WorkerBridgeComponent|Awake|Bootstrapper|ComputeActual|GetActual|Invalidate|Cache|stale|reject|mismatch',x['api'],re.I) for x in ledger)
 assert datetime.datetime.fromisoformat(admit['at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at'])<datetime.datetime.fromisoformat(host['completed_at'])<datetime.datetime.fromisoformat(post['at'])
 print('run '+str(n)+' identity, raw, outputs, ledger matched; metadata inspect',flush=True)
 meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),pre['runner']['exe_path'],pre['runner']['pdb_path']],check=True,capture_output=True,text=True,timeout=20).stdout)
 assert meta['mvid']==pre['runner']['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
 runs.append({'run_id':row['run_id'],'pid':row['owned_host_pid'],'culture':row['culture'],'exit':0,'pass':117,'fail':0,'prepost':181,'loaded':10,'output_files':148,'direct_calls':186,'grouped_reads':80})
assert runs[0]['pid']!=runs[1]['pid'] and read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_firstoutputs_unchanged']
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=failed=0
for entry in schema['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['compared_rows']
 errors=0
 for row in rows:
  match=equal(row);assert row['matched']==match;errors+=not match
 assert errors==entry['failed_rows'] and entry['all_matched']==(errors==0);count+=len(rows);failed+=errors
assert count==5576 and failed==0
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
assert bindingfail==0
source=(Q/'Program.cs').read_text(encoding='utf-8-sig');assert not any(x in source for x in ['System.Diagnostics.Process','GetCurrentProcess','VerifyProcessIdentity(','TryInstallOperatorStartupConfig','WorkerBridgeComponent.ActiveStartupConfig'])
audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')
for k in ['source','oracle','prospective','only_metadata_analysis_repaired']:verify(audit[k])
assert audit['old_source_oracle_readonly_references_only'] and audit['no_old_runner_binary_execution_or_outputs_reuse']
assert audit['source_oracle_runner_values_unchanged_afteronly_finalbuild_and2processes'] and not audit['output_derived_oracle']
streams=read(Q/'COMPLETE_BUILD_STREAM_BINDING.json')
for k in ['tool','invocation','stdout','stderr']:verify(streams[k])
assert streams['actual_builds']==1 and streams['actual_numeric_exit']==0 and streams['stdout']['bytes']==19219 and streams['stderr']['bytes']==0
assert streams['full_compile_run_streams_direct_ownedfiles'] and streams['no_warning_stream_truncation']
reconcile=read(Q/'PRODUCER_INVENTORY_METADATA_RECONCILIATION.json')
assert [(r['declared'],r['actual_nonself']) for r in reconcile['rows']]==[(10,10),(8,10)]
assert reconcile['rows'][1]['unlisted']==['stderr.txt','stdout.txt'] and reconcile['builds_runs_reruns_during_metadata_repair']==0
for row in reconcile['rows']:
 verify(row['inventory'])
 inventory=read(Path(row['inventory']['path']))
 assert len(inventory)==row['declared']
 root=Path(row['inventory']['path']).parent
 actualnames={p.name for p in root.iterdir() if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 assert len(actualnames)==row['actual_nonself']
 names={r['relative_path'] for r in inventory}
 assert sorted(actualnames-names)==row['unlisted']
 errors=[]
 for r in inventory:
  q=root/r['relative_path']
  if sha(q)!=r['sha256'] or q.stat().st_size!=r['size_bytes']:errors.append(r['relative_path'])
 assert sorted(errors)==(['stderr.txt','stdout.txt'] if row['run']=='run_en_us' else [])
pending=read(Q/'RETURN_PENDING.json')
assert pending['result_id']==rid and pending['status']=='PENDING_ONE_AUTHORIZED_TERMINAL_SEND'
for key in ['report','manifest','index','completion']:verify(pending[key])
assert not (Q/'RETURN_TOOL_PROOF.json').exists()
snap=json.loads(read(C/'MASTER_SOL_R19_CONTINUE_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='failed'
assert 'usage limit' in snap['latestTurn']['error']['message']
assert snap['latestTurn']['id']==read(C/'MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_ACK_VERIFICATION_20261010.json')['actual_snapshot']['latestTurn']['id']
vp=C/'MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-CONTINUE-R19-20261011-01','guard_session':40147,'guard_pid':19832,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':390,'protected_paths_rehashed':9841,'runs':runs,'typed_rows':count,'typed_mismatch_rows':failed,'repeatability_pairs':66,'reference_pairs':4,'reference_bindings':52,'reference_bindings_failed':0,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_SOL_R19_INDEPENDENT_TERMINAL_READ_20261011.json'),'scope_metadata_reconciliation':reconcile,'compiler_warning_stream':'COMPLETE_OWNED_RAW_19219_BYTES_EXIT0','thread_operational_status':'FAILED_USAGE_LIMIT_IDLE','terminal_delivery_status':'PENDING_NO_ACTUAL_TERMINAL_SEND','artifact_terminal_status':'COMPLETED_VERIFIED_NOT_INFERRED_FROM_THREAD','selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'verified':True,'evidence':390,'protected':9841,'runs':runs,'typed_rows':count,'typed_failed':failed,'status':'PENDING_DISPOSITION'},ensure_ascii=True))

