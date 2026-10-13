from pathlib import Path
import json,datetime,hashlib,sys,shutil,subprocess,difflib,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['completion_path']).parent;ac=read(Path(t['completion_path']))
assert c['active_operation'] is None and t['dispatch_id'].endswith('49256586') and all(t[k]==ac[k] for k in ['dispatch_id','wp_id','wp_revision']) and ac['producer']=='A' and ac['report_kind']=='E1'
assert not any(x.get('result_id')==ac['result_id'] for x in read(R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
checks=[]
for f in ac['artifacts']:
 p=Path(f['path']);assert p.resolve().is_relative_to(R) and sha(p)==f['sha256'] and p.stat().st_size==f['size'];checks.append(dict(f,matched=True))
print('artifacts matched '+str(len(checks)),flush=True)
ack=read(Path(t['ack_path']));assert all(ack[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and ack['envelope']==24
assert ack['envelope']==24
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
pp=T/'MASTER_R21_HEARTBEAT_PRESERVATION_20261011T070932.json';assert not pp.exists();write(pp,pres)
source=R/'scratch/WorkerBridgeMod/Source';s=R/'scratch/EngineGate05R21ReceiptUtc'
oldmap={f['original_path'].lower():f for f in read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files']}
oldw=Path(oldmap[str(source/'WorkerBridge.cs').lower()]['frozen_path']);old=oldw.read_bytes();new=(source/'WorkerBridge.cs').read_bytes()
base=read(Path(t['scope_baseline_path']))
prefix=Path(base['fixed_prefix']['path']).read_bytes();suffix=Path(base['fixed_suffix']['path']).read_bytes()
assert sha(Path(base['fixed_prefix']['path']))==base['fixed_prefix']['sha256'] and sha(Path(base['fixed_suffix']['path']))==base['fixed_suffix']['sha256']
scope_match=new.startswith(prefix) and new.endswith(suffix);assert scope_match
assert old.startswith(prefix) and old.endswith(suffix)
diff=T/'MASTER_R21_WORKER_SOURCE_DIFF.txt';diff.write_text(''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True),new.decode('utf-8-sig').splitlines(True),fromfile='FrozenR20Worker',tofile='R21Worker')),encoding='utf8')
for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:assert sha(source/n)==oldmap[str(source/n).lower()]['sha256']
beforeafter=[]
for phase in ['BEFORE','AFTER']:
 for f in read(T/f'ENGINE_FREEZE_{phase}.json')['files']:
  original=Path(f['path']);q=Path(oldmap[str(original).lower()]['frozen_path']) if phase=='BEFORE' else original
  assert sha(q)==f['sha256'] and q.stat().st_size==f['size'];beforeafter.append(dict(phase=phase,path=str(original),sha256=f['sha256'],size=f['size'],matched=True))
assert len(beforeafter)==18
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb')
 m=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True,timeout=30).stdout)
 assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents'])
 m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
rel=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R21_RECEIPT_UTC.json');assert [m['mvid'] for m in lineage]==[rel['selected_candidate']['mvid'],rel['alternate_candidate']['mvid']]
host=read(s/'HOST_TELEMETRY.json');assert host['pinned_runner']['sha256']==sha(Path(host['pinned_runner']['path']))
processes=[]
for n in ['run_en_us','run_de_de']:
 root=s/n;res=read(root/'RESULTS.json');ledger=read(root/'API_LEDGER.json');inv=read(root/'OUTPUT_INVENTORY.json');hr=next(x for x in host['runs'] if x['run_name']==n)
 assert res['PassedTests']==res['TotalTests']==7 and res['FailedTests']==0 and res['LoadedCandidateSha256']==lineage[0]['dll_sha256'] and res['LoadedCandidateMvid']==lineage[0]['mvid'] and res['Culture']==hr['culture']
 assert res['ApiLedger']==ledger
 rows=[]
 for f in inv:
  q=root/f['relative_path'];rows.append(dict(relative_path=f['relative_path'],recorded_sha256=f['sha256'],actual_sha256=sha(q),recorded_size=f['size_bytes'],actual_size=q.stat().st_size,matched=sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes']))
 actualset={str(q.relative_to(root)) for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'}
 processes.append({'directory':str(root),'actual_culture':res['Culture'],'host_child_pid':hr['child_pid'],'host_recorded_numeric_exit':hr['exit_code'],'labels':7,'manual_ledger':ledger,'ledger_sum':sum(ledger.values()),'tests':res['Tests'],'inventory_rows':len(inv),'actual_nonself_files':len(actualset),'inventory_exact_path_set':actualset=={f['relative_path'] for f in inv},'inventory_checks':rows})
# immutable post-completion snapshot, not prospective execution proof
files=set()
for base in [source,s,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for f in ac['artifacts']:files.add(Path(f['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.md','.json','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R21-49256586';mp=T/'MASTER_GATE05_R21_RECEIPT_UTC_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','files':rows,'runtime_e2_released':False})
vp=C/'MASTER_GATE05_R21_RECEIPT_UTC_E1_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'run_id':'MASTER-HEARTBEAT-R21-20261010T220932Z-01','guard_session':90005,'guard_pid':28816,'trigger_received_at':'2026-10-10T22:09:32.637Z','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':ac['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'before_after_checks':beforeafter,'outside_authorized_regions_byte_match':scope_match,'source_diff':str(diff),'source_sha256':sha(source/'WorkerBridge.cs'),'preservation_path':str(pp),'preservation_sha256':sha(pp),'lineage':lineage,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'selected_sha256':lineage[0]['dll_sha256'],'selected_mvid':lineage[0]['mvid'],'selected_pdb_sha256':lineage[0]['pdb_sha256'],'processes':processes,'ACK_valid':True,'ACK_sha256':sha(Path(t['ack_path'])),'producer_host_telemetry':host,'native_execution':'UNTESTED','master_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_DISPOSITION'}
write(vp,proof)
print(json.dumps({'artifacts':len(checks),'outside_scope_bytes_matched':scope_match,'freeze':len(rows),'freezeSHA':sha(mp),'selected':proof['selected_sha256'],'MVID':proof['selected_mvid'],'inventory_mismatches':[sum(not f['matched'] for f in p['inventory_checks']) for p in processes],'ledger_sum':[p['ledger_sum'] for p in processes],'status':'PENDING_MASTER_DISPOSITION'}))
