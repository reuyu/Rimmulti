"""Master read-only evidence and PE/PDB verification;no candidate or QA execution/build."""
from pathlib import Path
import json,datetime,hashlib,struct,subprocess,sys,ast,uuid,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R21-RECEIPT-UTC-INDEPENDENT-S1-20261011'
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
rid='SOL-GATE05-R21-RECEIPT-UTC-INDEPENDENT-S1-20261011-af67dd4d2d454bba926c4f3c8cf14d6f'
assert comp['result_id']==manifest['result_id']==idx['result_id']==rid and comp['status']=='COMPLETED' and comp['wp_revision']=='S1'
assert sha(Q/'COMPLETION.json')=='FF1606D2B56604AE1395146D64D8D8127745FEFCC54444FBD85166719517B016'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(manifest['files'])==579
for f in manifest['files']:verify(f)
print('579 evidence SHA-size matched',flush=True)
before=read(Q/'PRESERVATION_BEFORE.json')['files'];after=read(Q/'PRESERVATION_AFTER.json')['files'];assert before==after and len(after)==10939
for f in after:verify(f)
print('10939 protected SHA-size matched',flush=True)
ackproof=read(C/'MASTER_SOL_R21_RECEIPT_UTC_INDEPENDENT_ACK_VERIFICATION_20261011.json')
assert sha(Q/'ACK_INITIAL.json')==ackproof['ack_sha256'] and read(Q/'ACK_INITIAL.json')['result_id']==rid
master=read(C/'MASTER_GATE05_R21_RECEIPT_UTC_E1_VERIFICATION_20261011.json')['lineage']
for q in read(Q/'R21_FROZEN_LINEAGE.json')['candidates']:
 mm=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==mm['dll_sha256'] and q['pdb_sha256']==mm['pdb_sha256'] and q['guid']==q['codeview_guid']==mm['pdbGuid']==mm['codeviewGuid']
 for d in q['documents']:
  md=next(x for x in mm['documents'] if x['path']==d['path']);assert d['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(Path(d['frozen_source_path']))
thread=json.loads(read(C/'MASTER_SOL_R21_INDEPENDENT_TERMINAL_READ_20261011.json')['content'][0]['text'])
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
 assert pre['files']==post['files'] and len(pre['files'])==206 and pre['run_id']==post['run_id']==row['run_id']==context['run_id']==host['run_id']
 for f in pre['files']:verify(f)
 assert row['culture']==pre['culture']==context['culture']==host['requested_culture']==host['observed_culture']==['en-US','de-DE'][n-1]
 assert row['actual_numeric_exit']==post['actual_numeric_exit']==host['numeric_exit']==tool['exit_code']==0
 assert row['owned_host_pid']==post['host_pid']==host['owned_child_pid']>0 and context['argv']==host['argv']==pre['argv'] and context['cwd']==host['cwd']==pre['cwd']
 assert Path(host['cwd']).is_absolute()
 actual=json.loads(tool['output'].splitlines()[0]);assert actual['owned_child_pid']==host['owned_child_pid'] and actual['numeric_exit']==0 and actual['observed_culture']==context['culture']
 normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==245 and normal['failed_assertions']==0
 assert all(x['status']=='PASS' for x in normal['results'])
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==245 and not any(x.startswith('FAIL ') for x in raw.splitlines())
 assert normal['selected_sha256']==comp['selected_sha256'] and normal['selected_mvid']==comp['selected_mvid']
 loaded=read(root/'ACTUAL_LOADED_PREPIN_BINDING.json');assert loaded['all_loaded_prepin_matched'] and len(loaded['files'])==10
 mapping={x['path'].lower():x for x in pre['files']}
 for f in loaded['files']:
  assert f['pre_pin_matched'] and mapping[f['path'].lower()]['sha256']==f['sha256']==sha(Path(f['path'])) and mvid(Path(f['path']))==f['mvid']
 inv=read(Path(row['inventory']['path']));assert inv['file_count']==len(inv['files'])==249 and inv['every_generated_output_recursive'] and inv['excluded_self_only']
 actualset={str(p.resolve()).lower() for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 assert actualset=={str(Path(f['path']).resolve()).lower() for f in inv['files']}
 for f in inv['files']:verify(f)
 ledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json')
 assert len(ledger)==586 and sum(x['scope']=='direct_pure' for x in ledger)==378 and sum(x['scope']=='grouped_snapshot_read' for x in ledger)==176 and sum(x['scope']=='grouped_receipt_read' for x in ledger)==32
 assert not any(re.search(r'ProcessIdentity|Process\.|GetCurrentProcess|MainModule|WorkerBridgeComponent|Awake|Bootstrapper|ComputeActual|GetActual|Invalidate|Cache|stale|reject|mismatch',x['api'],re.I) for x in ledger)
 assert datetime.datetime.fromisoformat(admit['at'])<datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at'])<datetime.datetime.fromisoformat(host['completed_at'])<datetime.datetime.fromisoformat(post['at'])
 print('run '+str(n)+' identity, raw, outputs, ledger matched; metadata inspect',flush=True)
 meta=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),pre['runner']['exe_path'],pre['runner']['pdb_path']],check=True,capture_output=True,text=True,timeout=20).stdout)
 assert meta['mvid']==pre['runner']['exe_mvid'] and meta['codeviewMatched'] and all(x['matched'] for x in meta['documents'])
 runs.append({'run_id':row['run_id'],'pid':row['owned_host_pid'],'culture':row['culture'],'exit':0,'pass':245,'fail':0,'prepost':206,'loaded':10,'output_files':249,'direct_calls':378,'grouped_reads':208})
assert runs[0]['pid']!=runs[1]['pid'] and read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['all_firstoutputs_unchanged']
assert datetime.datetime.fromisoformat(read(Path(process['rows'][0]['inventory']['path']))['at'])<datetime.datetime.fromisoformat(read(Q/'PRE_RUN2_MANIFEST.json')['at'])
count=failed=0
for entry in schema['typed_files']:
 verify(entry['file']);rows=list(checks(read(Path(entry['file']['path']))));assert len(rows)==entry['compared_rows']
 errors=0
 for row in rows:
  match=equal(row);assert row['matched']==match;errors+=not match
 assert errors==entry['failed_rows'] and entry['all_matched']==(errors==0);count+=len(rows);failed+=errors
assert count==10856 and failed==0
assert len(summary['all_byte_pairs'])==114 and summary['reference_pair_count']==4
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
receipt_bindings=[row for row in summary['bindings'] if 'redacted_actual' in row];assert len(receipt_bindings)==32
for row in receipt_bindings:
 for k in ['graph','oracle','redacted_actual','redacted_reference']:verify(row[k])
 assert row['all11_receipt15_nested_policyrecord_matched'] and row['matched'] and row['strict_original_values_matched']
 expected=Path(row['redacted_reference']['path']).read_bytes();actual=Path(row['redacted_actual']['path']).read_bytes();assert expected==actual
 obj=read(Path(row['redacted_actual']['path']));assert type(obj['snapshot']['issuedAtUtc'])==str and obj['snapshot']['issuedAtUtc']==obj['admittedAtUtc']==row['literal']
 assert row['literal'] in ['2026-10-10T00:00:00.0000000Z','2026-10-10T00:00:00.1234567Z','2026-10-10T00:00:00Z']
utc=read(Q/'UTC_LITERAL_TYPE_AND_WHOLE_BYTES_BINDING.json');assert len(utc['rows'])==32 and utc['expectedstrings_neverdatetime_canonicalized']
for row in utc['rows']:
 verify(row['actual']);verify(row['reference']);assert Path(row['actual']['path']).read_bytes()==Path(row['reference']['path']).read_bytes()
 assert row['actual_nested']==row['actual_admitted']==row['literal'] and row['actual_token']=='String' and row['all_stringtypes_matched'] and row['entire11receipt_redaction_bytes_matched'] and row['not_DateTime_parsed_or_canonicalized']
assert len({row['case_id'] for row in utc['rows']})==16
assert all(sum(row['utc_kind']==kind for row in utc['rows'])==num for kind,num in [('ZERO_FRACTION7_MAIN',16),('FRACTION7',8),('WHOLE_SECONDS',8)])
scope=read(Q/'METHOD_SCOPE_ADMISSION_BEFORE_CALLS.json');verify(scope['source']);verify(scope['previous_frozen_source'])
for f in scope['fixed']:verify(f)
new=Path(scope['source']['path']).read_bytes();old=Path(scope['previous_frozen_source']['path']).read_bytes()
assert new[:scope['prefix_bytes']]==old[:scope['prefix_bytes']] and new[-scope['suffix_bytes']:]==old[-scope['suffix_bytes']:] and scope['explicitDateParseNone_before_JObjectLoad'] and scope['local_reader_disposal_source'] and not scope['global_json_settings_changed']
base=read(R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586/MASTER_R21_SCOPE_BASELINE.json')
prefix=Path(base['fixed_prefix']['path']).read_bytes();suffix=Path(base['fixed_suffix']['path']).read_bytes()
assert new.startswith(prefix) and new.endswith(suffix) and old.startswith(prefix) and old.endswith(suffix)
assert len(suffix)==33242 and scope['suffix_bytes']==33243 and new[-33243:]==b'\n'+suffix and old[-33243:]==b'\n'+suffix
source=(Q/'Program.cs').read_text(encoding='utf-8-sig');assert not any(x in source for x in ['System.Diagnostics.Process','GetCurrentProcess','VerifyProcessIdentity(','TryInstallOperatorStartupConfig','WorkerBridgeComponent.ActiveStartupConfig'])
audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')
for k in ['source','normal_oracle','receipt_oracle','prospective','prebuild_annotation_initial']:verify(audit[k])
assert audit['old_source_oracle_readonly_reference_only'] and audit['no_oldrunner_or_output_reuse']
assert audit['final_source_oracles_runner_unchanged_after_only_finalbuild_and2runs'] and audit['no_output_derived_expectations']
streams=read(Q/'COMPLETE_BUILD_STREAM_BINDING.json')
for k in ['tool','wrapper','stdout','stderr']:verify(streams[k])
assert streams['actual_final_builds']==1 and streams['compiler_numeric_exit']==0 and streams['stdout']['bytes']==24048 and streams['stderr']['bytes']==0
assert streams['full_streams_directfiles'] and streams['no_compiler_retry_or_candidate_rerun']
reconcile={'QA_suffix_bytes':33243,'Master_task_suffix_bytes':33242,'boundary_difference':'QA includes preceding LF, both frozen versions match exact task prefix/suffix independently','producer17_nonself_each_all_SHA_size_match':True,'original_reports_unmodified':True}
for name in ['run_en_us','run_de_de']:
 root=R/'Dispatcher/CANDIDATES/G05R21-49256586/scratch/EngineGate05R21ReceiptUtc'/name;inv=read(root/'OUTPUT_INVENTORY.json');assert len(inv)==17
 actualnames={str(q.relative_to(root)) for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'};assert actualnames=={f['relative_path'] for f in inv}
 for f in inv:
  q=root/f['relative_path'];assert sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes']
 ledger=read(root/'API_LEDGER.json');assert sum(ledger.values())==80
 result=read(root/'RESULTS.json');helper=next(x for x in result['Tests'] if x['TestName']=='TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_POSITIVE_HELPER');assert helper['ValidChecksPassed']==helper['TotalValidChecks']==5
delivery=read(Q/'DELIVERY_STATUS.json');assert delivery['status']=='ONE_ACTUAL_TERMINAL_SEND_TOOL_ACCEPTED' and delivery['actual_send_count']==1 and not delivery['unknown_delivery']
ret=read(Q/'RETURN_TOOL_PROOF.json');assert ret['result_id']==rid and not ret['actual_tool_result'].get('isError')
assert json.loads(ret['actual_tool_result']['content'][0]['text'])['threadId']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
snap=json.loads(read(C/'MASTER_SOL_R21_INDEPENDENT_TERMINAL_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
vp=C/'MASTER_SOL_R21_RECEIPT_UTC_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-SOL-R21-COMPLETE-20261011-01','guard_session':26221,'guard_pid':27436,'result_id':rid,'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'result_index_sha256':sha(Q/'RESULT_INDEX.json'),'evidence_files':579,'protected_paths_rehashed':10939,'runs':runs,'typed_rows':count,'typed_mismatch_rows':failed,'repeatability_pairs':114,'reference_pairs':4,'reference_bindings':84,'reference_bindings_failed':0,'actual_snapshot':snap,'actual_thread_read':str(C/'MASTER_SOL_R21_INDEPENDENT_TERMINAL_READ_20261011.json'),'scope_metadata_reconciliation':reconcile,'compiler_warning_stream':'COMPLETE_OWNED_RAW_24048_BYTES_EXIT0','thread_operational_status':'COMPLETED_IDLE','terminal_delivery_status':'ONE_ACTUAL_TERMINAL_SEND_ACCEPTED','artifact_terminal_status':'COMPLETED_VERIFIED_ACTUAL_THREAD_MATCHED','selected_sha256':comp['selected_sha256'],'selected_mvid':comp['selected_mvid'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_execute_builds':0,'runtime_e2_released':False,'closure_changed':False,'targeted_UTC_regression':'PASS_PENDING_MASTER_CLOSURE','receipt_cases':16,'foundation':'HOLD'}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'verified':True,'evidence':579,'protected':10939,'runs':runs,'typed_rows':count,'typed_failed':failed,'status':'PENDING_DISPOSITION'},ensure_ascii=True))

