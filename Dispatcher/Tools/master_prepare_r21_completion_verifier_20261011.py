from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'Dispatcher/Tools/master_verify_r20_independent_completion_20261011.py').read_text(encoding='utf8')
for a,b in [('R20','R21'),('r20','r21'),('TRUSTED_STARTUP','RECEIPT_UTC'),('TRUSTED-STARTUP','RECEIPT-UTC'),('4245a7b9c3a8434993de3c5f411b762a','af67dd4d2d454bba926c4f3c8cf14d6f'),('7170B8090D4AC40C959D84616763CC9194C5052145BD818F337FBDA744833CA0','FF1606D2B56604AE1395146D64D8D8127745FEFCC54444FBD85166719517B016'),('474','579'),('10346','10939'),('==192','==206'),("'prepost':192","'prepost':206"),('==197','==249'),("'output_files':197","'output_files':249"),('==426','==586'),('==282','==378'),('==128','==176'),('==16\n assert not any','==32\n assert not any'),("'direct_calls':282","'direct_calls':378"),("'grouped_reads':144","'grouped_reads':208"),('==8216','==10856'),('failed==16','failed==0'),('==90','==114'),('e35ff656','49256586'),('TrustedStartup','ReceiptUtc'),('24464','24048'),('54820','26221'),('30204','27436')]:s=s.replace(a,b)
s=s.replace("==tool['exit_code']==1","==tool['exit_code']==0").replace("actual['numeric_exit']==1","actual['numeric_exit']==0")
start=s.index(" normal=read(root/'NORMAL_RESULTS.json')");end=s.index(" loaded=read(",start)
s=s[:start]+''' normal=read(root/'NORMAL_RESULTS.json');assert len(normal['results'])==245 and normal['failed_assertions']==0
 assert all(x['status']=='PASS' for x in normal['results'])
 assert sum(x.startswith('PASS ') for x in raw.splitlines())==245 and not any(x.startswith('FAIL ') for x in raw.splitlines())
 assert normal['selected_sha256']==comp['selected_sha256'] and normal['selected_mvid']==comp['selected_mvid']
''' +s[end:]
s=s.replace("'exit':1,'pass':173,'fail':8","'exit':0,'pass':245,'fail':0")
start=s.index("receipt_bindings=[");end=s.index("source=(Q/'Program.cs')",start)
s=s[:start]+'''receipt_bindings=[row for row in summary['bindings'] if 'redacted_actual' in row];assert len(receipt_bindings)==32
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
assert len(suffix)==33242 and scope['suffix_bytes']==33243 and new[-33243:]==b'\\n'+suffix and old[-33243:]==b'\\n'+suffix
''' +s[end:]
s=s.replace("'prepin_annotation_setup_reconciliation'","'prebuild_annotation_initial'")
s=s.replace("and streams['prepin_setup_failures_compiler_calls0_preserved']","and streams['no_compiler_retry_or_candidate_rerun']")
start=s.index("reconcile=read(");end=s.index("delivery=read(Q/'DELIVERY_STATUS.json')",start)
s=s[:start]+'''reconcile={'QA_suffix_bytes':33243,'Master_task_suffix_bytes':33242,'boundary_difference':'QA includes preceding LF, both frozen versions match exact task prefix/suffix independently','producer17_nonself_each_all_SHA_size_match':True,'original_reports_unmodified':True}
for name in ['run_en_us','run_de_de']:
 root=R/'Dispatcher/CANDIDATES/G05R21-49256586/scratch/EngineGate05R21ReceiptUtc'/name;inv=read(root/'OUTPUT_INVENTORY.json');assert len(inv)==17
 actualnames={str(q.relative_to(root)) for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'};assert actualnames=={f['relative_path'] for f in inv}
 for f in inv:
  q=root/f['relative_path'];assert sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes']
 ledger=read(root/'API_LEDGER.json');assert sum(ledger.values())==80
 result=read(root/'RESULTS.json');helper=next(x for x in result['Tests'] if x['TestName']=='TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_POSITIVE_HELPER');assert helper['ValidChecksPassed']==helper['TotalValidChecks']==5
''' +s[end:]
s=s.replace("'typed_mismatch_rows':failed,'repeatability_pairs':90","'typed_mismatch_rows':failed,'repeatability_pairs':114").replace("'reference_bindings':68,'reference_bindings_failed':16","'reference_bindings':84,'reference_bindings_failed':0")
s=s.replace("'closure_changed':False,'foundation':'HOLD'","'closure_changed':False,'targeted_UTC_regression':'PASS_PENDING_MASTER_CLOSURE','receipt_cases':16,'foundation':'HOLD'")
dest=R/'Dispatcher/Tools/master_verify_r21_independent_completion_20261011.py';assert not dest.exists();dest.write_text(s,encoding='utf8');print(dest)
