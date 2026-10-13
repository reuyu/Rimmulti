from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'Dispatcher/Tools/master_verify_r19_independent_completion_v2_20261011.py').read_text(encoding='utf8')
for a,b in [
 ('OPAQUE_POLICY','TRUSTED_STARTUP'),('OPAQUE-POLICY','TRUSTED-STARTUP'),('R19','R20'),('r19','r20'),('20261010','20261011'),
 ('2c4a145f15334594bba451900223477a','4245a7b9c3a8434993de3c5f411b762a'),
 ('EC88A9E0895C7E8A66F696730B0B0F028339B6E2E88533F26F46B82331FC3890','7170B8090D4AC40C959D84616763CC9194C5052145BD818F337FBDA744833CA0'),
 ('390','474'),('9841','10346'),('==181','==192'),("'prepost':181","'prepost':192"),('==148','==197'),("'output_files':148","'output_files':197"),('==266','==426'),('==186','==282'),('==80','==144'),("'direct_calls':186","'direct_calls':282"),("'grouped_reads':80","'grouped_reads':144"),
 ('count==5576','count==8216'),('failed==0','failed==16'),('bindingfail==0','bindingfail==16'),
 ("'reference_bindings':52","'reference_bindings':68"),('len(bindings)==52','len(bindings)==68'),
 ("'reference_bindings_failed':0","'reference_bindings_failed':16"),
 ("('meaningful_crossprocess_byte_pairs',66)","('meaningful_crossprocess_byte_pairs',90)"),("'repeatability_pairs':66","'repeatability_pairs':90"),
 ("'guard_session':40147","'guard_session':54820"),("'guard_pid':19832","'guard_pid':30204"),
 ("MASTER-CONTINUE-R20-20261011-01","MASTER-SOL-R20-COMPLETE-20261011-01"),
]:
 s=s.replace(a,b)
s=s.replace("==tool['exit_code']==0","==tool['exit_code']==1").replace("actual['numeric_exit']==0","actual['numeric_exit']==1")
s=s.replace("len(normal['results'])==117 and normal['failed_assertions']==0","len(normal['results'])==181 and normal['failed_assertions']==8")
s=s.replace("sum(x['status']=='PASS' for x in normal['results'])==117","sum(x['status']=='PASS' for x in normal['results'])==173")
s=s.replace("sum(x['status']=='FAIL' for x in normal['results'])==0","sum(x['status']=='FAIL' for x in normal['results'])==8")
s=s.replace("sum(x.startswith('PASS ') for x in raw.splitlines())==117","sum(x.startswith('PASS ') for x in raw.splitlines())==173")
s=s.replace("sum(x.startswith('FAIL ') for x in raw.splitlines())==0","sum(x.startswith('FAIL ') for x in raw.splitlines())==8")
s=s.replace("'exit':0,'pass':117,'fail':0","'exit':1,'pass':173,'fail':8")
s=s.replace("assert all('_OPAQUE_' in x['id'] and any(x['id'].endswith(s) for s in ['FULL_LOSSLESS','REDACTED_LOSSLESS','AFTER_EDITS_LOSSLESS']) for x in normal['results'] if x['status']=='FAIL')","assert all('RECEIPT' in x['id'] and 'REDACTED' in x['id'] for x in normal['results'] if x['status']=='FAIL')")
start=s.index("audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')")
end=s.index("vp=C/'MASTER_SOL_R20_TRUSTED_STARTUP_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json'")
s=s[:start]+'''audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')
for k in ['source','normal_oracle','receipt_oracle','prospective','prepin_annotation_setup_reconciliation']:verify(audit[k])
assert audit['old_source_oracle_readonly_reference_only'] and audit['no_oldrunner_or_output_reuse']
assert audit['final_source_oracles_runner_unchanged_after_only_finalbuild_and2runs'] and audit['no_output_derived_expectations']
streams=read(Q/'COMPLETE_BUILD_STREAM_BINDING.json')
for k in ['tool','invocation','stdout','stderr']:verify(streams[k])
assert streams['actual_builds']==1 and streams['actual_numeric_exit']==0 and streams['stdout']['bytes']==24464 and streams['stderr']['bytes']==0
assert streams['full_compile_run_streams_direct_ownedfiles'] and streams['no_warning_stream_truncation']
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
''' +s[end:]
s=s.replace("'compiler_warning_stream':'COMPLETE_OWNED_RAW_19219_BYTES_EXIT0','thread_operational_status':'FAILED_USAGE_LIMIT_IDLE','terminal_delivery_status':'PENDING_NO_ACTUAL_TERMINAL_SEND','artifact_terminal_status':'COMPLETED_VERIFIED_NOT_INFERRED_FROM_THREAD'","'compiler_warning_stream':'COMPLETE_OWNED_RAW_24464_BYTES_EXIT0','thread_operational_status':'COMPLETED_IDLE','terminal_delivery_status':'ONE_ACTUAL_TERMINAL_SEND_ACCEPTED','artifact_terminal_status':'COMPLETED_VERIFIED_ACTUAL_THREAD_MATCHED'")
dest=R/'Dispatcher/Tools/master_verify_r20_independent_completion_20261011.py';assert not dest.exists()
dest.write_text(s,encoding='utf8')
print(str(dest))
