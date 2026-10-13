from pathlib import Path
import json,hashlib,datetime,sys,shutil
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size')),str(p)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];T=Path(t['instruction_path']).parent;x=read(T/'COMPLETION.json');scope=read(Path(t['scope_baseline_path']));lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert lock['status']=='LOCKED' and lock['run_id']=='MASTER-R29-SOL-PREP-COMPLETE-20261012-01' and c['active_operation'] is None
assert all(x[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and x['envelope']==32 and x['status']=='COMPLETED'
for f in x['artifacts']:check(f)
for f in t['production_fixed_files']:check(f)
base=read(Path(c['sol_current_delivery']['baseline_path']));assert len(base['files'])==14105
for f in base['files']:check(f)
add=read(Path(t['r29_additional_completed_QA_preservation']['terminal_additive_manifest']['path']))
for f in add['files']:check(f)
orig=R/'Dispatcher/CANDIDATES/G05R27-cdc223f3/scratch/WorkerBridgeMod/Source/WorkerBridge.cs';cur=R/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';oldbytes=orig.read_bytes();newbytes=cur.read_bytes();assert sha(orig)==scope['Worker_original']['sha256'];diff=read(T/'SOURCE_SCOPE_DIFF.json');permissions={p['id']:(p['start'],p['end']) for p in scope['allowed_byte_spans']};assert len(diff['authorized_spans'])==6
oi=ni=0;outside=[]
for z in sorted(diff['authorized_spans'],key=lambda v:v['orig_range'][0]):
 os,oe=z['orig_range'];ns,ne=z['new_range'];assert permissions[z['span_id']]==(os,oe);assert oldbytes[oi:os]==newbytes[ni:ns];outside.append({'old':[oi,os],'new':[ni,ns],'bytes':os-oi,'sha256':hashlib.sha256(oldbytes[oi:os]).hexdigest().upper()});assert hashlib.sha256(newbytes[ns:ne]).hexdigest().upper()==z['new_sha256'];oi,ni=oe,ne
assert oldbytes[oi:]==newbytes[ni:];outside.append({'old':[oi,len(oldbytes)],'new':[ni,len(newbytes)],'bytes':len(oldbytes)-oi,'sha256':hashlib.sha256(oldbytes[oi:]).hexdigest().upper()});assert sum(z['bytes'] for z in outside)==234431
identity=read(T/'CANDIDATE_IDENTITY.json');pe={}
for mode in ['Debug','Release']:
 r=read(C/('MASTER_R29_'+mode.upper()+'_PE_PDB_TOOL_20261012.json'));assert r['exit_code']==0;p=json.loads(r['output']);assert p['codeviewMatched'] and len(p['documents'])==4 and all(z['matched'] for z in p['documents']);k=identity[mode.lower()+'_candidate'];assert p['mvid']==k['mvid'] and p['codeviewGuid']==k['codeview_guid'];assert sha(Path(k['assembly_path']))==k['sha256'] and sha(Path(k['pdb_path']))==k['pdb_sha256'];pe[mode]=p
E=R/'scratch/EngineGate05R29StartupPair';host=read(E/'HOST_TELEMETRY.json');assert len(host['runs'])==2
for run in host['runs']:
 assert run['exit_code']==0 and run['culture'] in ['en-US','de-DE'] and run['pid']>0;assert Path(run['stdout_path']).stat().st_size==1959 and Path(run['stderr_path']).stat().st_size==0
pre=read(T/'FINAL_PRE_RUN_MANIFEST.json');pub=read(T/'PRODUCER_PUBLICATION_EVIDENCE.json');res=read(T/'E1_NORMAL_RESULTS.json');assert len(pub['cases'])==6 and res['overall_status']=='PASS'
source=cur.read_text(encoding='utf8');publisher=Path(t['allowed_new_source_paths'][0]);ps=publisher.read_text(encoding='utf8');assert 'object.ReferenceEquals(_pendingParentReceipt, _activeStartupConfig)' in source and '_pendingParentReceipt = parentReceipt' in source and '_activeStartupConfig = receipt.Snapshot' in source
assert 'os.remove(out_bundle_path)' in ps and 'with open(tmp_bundle_path, "wb")' in ps and 'with open(out_sha_path, "w"' in ps
paths={}
for f in x['artifacts']:
 p=Path(f['path']);paths[str(p.resolve()).lower()]=p
for root in [T,E,R/'scratch/WorkerBridgeMod/Source/obj',R/'scratch/WorkerBridgeMod/Source/bin']:
 for p in root.rglob('*'):
  if p.is_file():paths[str(p.resolve()).lower()]=p
for p in [R/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',R/'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj',publisher,T/'COMPLETION.json']:paths[str(p.resolve()).lower()]=p
F=R/'Dispatcher/CANDIDATES/G05R29-46f60e2a';assert not F.exists();F.mkdir();files=[]
for p in paths.values():
 q=F/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);assert sha(q)==sha(p);files.append(dict(row(p),original_path=str(p),frozen_path=str(q)))
fm=T/'MASTER_GATE05_R29_STARTUP_PAIR_REVIEW_FREEZE_MANIFEST.json';write(fm,{'at':at,'files':files,'scope':'R29_EXACT_POST_COMPLETION_SOURCE_BIN_PDB_PUBLISHER_AND_E1_EVIDENCE_FREEZE_NOT_RUNTIME_ADMISSION'})
nj=[f for f in files if f['original_path']==str(E/'Harness/bin/Debug/net472/Newtonsoft.Json.dll')];assert len(nj)==1 and nj[0]['sha256']=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D'
proof={'at':at,'guard_run':lock['run_id'],'guard_session':7127,'guard_pid':27876,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':x['result_id'],'completion':row(T/'COMPLETION.json'),'artifact_count':len(x['artifacts']),'protected':14105,'additional_QA_terminal_preserved':len(add['files']),'six_spans_outside7_entirebytes_matched':outside,'outside_bytes_total':234431,'candidate_identity':identity,'Master_PE_PDB_Source4of4':pe,'host_runs':host['runs'],'reported_normal6_case_PASS_no_Master_rerun':True,'producer_full_typed_raw_and_normal_capture_coverage':'SHALLOW_SELECTED_FIELDS_NOT_FULL_SNAPSHOT_OR_AFTERGRAPH_TYPED_BINDING','producer_pre_manifest_at':pre['generated_at'],'host_telemetry_at':host['recorded_at'],'publisher_evidence_at':pub['generated_at'],'prospective_final_compiler_allrefs_inputs_pin':'NOT_PROVED; manifest generated after publisher and normal runs','critical_source_finding':'ReferenceEquals receipt versus snapshot alwaysfalse, Awake fails togate pairmode; launchHold bypass possible','publisher_static_findings':'DELETE/TRUNCATE_EXISTING_OUTPUT_CAPABLE; nonexclusive temporary; configurable filename may escape root; declaredpath equality/config14 role/schema checks missing','carrier_static_findings':'anyPair usesnonempty corelookup; blank/malformed/duplicate rawsignals not closed beforelegacy','frozen_manifest':row(fm),'frozen_files':len(files),'selected_frozen_dll':str(F/Path(identity['debug_candidate']['relative_path'])),'selected_sha256':identity['debug_candidate']['sha256'],'selected_mvid':identity['debug_candidate']['mvid'],'matching_pdb_sha256':identity['debug_candidate']['pdb_sha256'],'publisher_frozen_path':str(F/publisher.relative_to(R)),'frozen_loader_library':nj[0],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','Master_candidate_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp=C/'MASTER_GATE05_R29_STARTUP_PAIR_E1_VERIFICATION_20261012.json';write(vp,proof);print(json.dumps({'status':proof['verification_status'],'artifacts':len(x['artifacts']),'frozen':len(files),'manifestSHA':sha(fm),'selectedSHA':proof['selected_sha256'],'outsidefixed':234431,'Highsource':'RECEIPT_VS_SNAPSHOT_ALWAYSFALSE'},ensure_ascii=False))
