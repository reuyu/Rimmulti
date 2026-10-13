from pathlib import Path
R=Path(__file__).resolve().parents[2];s=(R/'Dispatcher/Tools/master_verify_r21_independent_completion_20261011.py').read_text(encoding='utf8')
for a,b in [('R21','R22'),('RECEIPT-UTC','DECLARATION'),('RECEIPT_UTC','DECLARATION'),('49256586','9be1579a'),('af67dd4d2d454bba926c4f3c8cf14d6f','f555312829e4454ea4d3e254fcfc054d'),('FF1606D2B56604AE1395146D64D8D8127745FEFCC54444FBD85166719517B016','823D25293FF027F9E6FF962C5C775F214B2789E71AE782ACA860D01C173FDB19'),('579','578'),('10939','11639'),('206','208'),('245','261'),('586','618'),('378','410'),('10856','11080'),('24048','24321'),('26221','97421'),('27436','19552')]:s=s.replace(a,b)
start=s.index("scope=read(Q/'METHOD_SCOPE");end=s.index("source=(Q/'Program.cs')",start)
s=s[:start]+'''scope=read(Q/'FOUR_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json');verify(scope['source']);verify(scope['previous_frozen_source']);verify(scope['scope_baseline'])
for f in scope['fixed']:verify(f)
new=Path(scope['source']['path']).read_bytes();old=Path(scope['previous_frozen_source']['path']).read_bytes()
base=read(Path(scope['scope_baseline']['path']));assert len(scope['five_fixed_ordered_segments'])==len(base['fixed_segments'])==5
for row in scope['five_fixed_ordered_segments']:
 f=row['original_fixed_file'];verify(f);fixed=Path(f['path']).read_bytes();assert row['bytes_exact'] and new[row['new_start']:row['new_end']]==fixed
 assert sha(Path(f['path']))==base['fixed_segments'][row['index']]['sha256']
assert scope['all_other_bytes_exact'] and scope['source_R21_UTC_public11_Snapshot_ParseStrict_AdmitBytesFile_globalguards_fixed']
''' +s[end:]
start=s.index("reconcile={'QA_suffix_bytes'");end=s.index("delivery=read(Q/'DELIVERY_STATUS.json')",start)
s=s[:start]+'''reconcile={'four_mutable_spans_five_fixed_segments':True,'producer18_nonself_each_all_SHA_size_match':True,'producer_normal16_snapshot_direct_calls':0,'original_reports_unmodified':True,'M01_CLI_original_identifier_Trim':'REVISION_REQUIRED_SOURCEONLY','role_capability_normalization':'OPEN_SOURCEONLY_CANONICAL_INPUTS_PASS'}
for name in ['run_en_us','run_de_de']:
 root=R/'Dispatcher/CANDIDATES/G05R22-9be1579a/scratch/EngineGate05R22Declaration'/name;inv=read(root/'OUTPUT_INVENTORY.json');assert len(inv)==18
 actualnames={str(q.relative_to(root)) for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'};assert actualnames=={f['relative_path'] for f in inv}
 for f in inv:
  q=root/f['relative_path'];assert sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes']
 result=read(root/'E1_EXECUTION_REPORT.json');assert sum(result['call_counts'].values())==54 and result['call_counts']['ToSnapshot']==0
 assert len(result['tests'])==7 and all(x['status']=='PASS' for x in result['tests'])
''' +s[end:]
s=s.replace("MASTER_SOL_R22_INDEPENDENT_TERMINAL_SNAPSHOT_20261011.json","MASTER_SOL_R22_DECLARATION_INDEPENDENT_COMPLETION_SNAPSHOT_20261011.json")
s=s.replace("'targeted_UTC_regression':'PASS_PENDING_MASTER_CLOSURE'","'fresh_R22_receipt_declaration_UTC_regression':'PASS_PENDING_MASTER_DISPOSITION;M01_CLI_TRIM_REVISION_REQUIRED'")
out=R/'Dispatcher/Tools/master_verify_r22_independent_completion_20261011.py';assert not out.exists();out.write_text(s,encoding='utf8');print('R22_COMPLETION_VERIFIER_PREPARED')
