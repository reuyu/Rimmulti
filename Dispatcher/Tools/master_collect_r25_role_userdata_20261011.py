from pathlib import Path
import json,datetime,hashlib,sys,shutil,subprocess,difflib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['completion_path']).parent;ac=read(Path(t['completion_path']))
assert c['active_operation'] is None and t['dispatch_id'].endswith('dd341868') and all(t[k]==ac[k] for k in ['dispatch_id','wp_id','wp_revision']) and ac['producer']=='A' and ac['report_kind']=='E1'
assert not any(x.get('result_id')==ac['result_id'] for x in read(R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
checks=[]
for f in ac['artifacts']:
 p=Path(f['path']);assert p.resolve().is_relative_to(R) and sha(p)==f['sha256'] and p.stat().st_size==f['size'],str(p);checks.append(dict(f,matched=True))
print('artifacts matched '+str(len(checks)),flush=True)
ack=read(Path(t['ack_path']));assert all(ack[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and ack['envelope']==28
pp=T/'MASTER_R25_TERMINAL_PRESERVATION_20261011.json'
pres=read(pp) if pp.exists() else ck.inspect_preservation(t)
assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0],str(pres['preservation_errors'])
if not pp.exists():write(pp,pres)
base=read(Path(t['scope_baseline_path']));protected=read(Path(base['protected_baseline']['path']));protected_checks=0
assert sha(Path(base['protected_baseline']['path']))==base['protected_baseline']['sha256']
for f in protected['files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p);protected_checks+=1
source=R/'scratch/WorkerBridgeMod/Source';s=R/'scratch/EngineGate05R25RoleUserData'
oldmap={f['original_path'].lower():f for f in read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files']}
old=Path(oldmap[str(source/'WorkerBridge.cs').lower()]['frozen_path']).read_bytes();new=(source/'WorkerBridge.cs').read_bytes()
assert hashlib.sha256(old).hexdigest().upper()==base['source_before']['sha256']
fixedchecks=[];cursor=0;newmutable=[];prev=0
for i,f in enumerate(base['fixed_segments']):
 p=Path(f['path']);raw=p.read_bytes();assert sha(p)==f['sha256'] and len(raw)==f['bytes'] and old[f['old_start']:f['old_end']]==raw
 pos=new.find(raw,cursor);assert pos>=0 and new.find(raw,pos+1)<0 and (i!=0 or pos==0)
 if i:newmutable.append(new[prev:pos].decode('utf8'))
 fixedchecks.append(dict(f,new_start=pos,new_end=pos+len(raw),matched=True));cursor=prev=pos+len(raw)
assert cursor==len(new) and len(newmutable)==3
assert '_activeStartupConfig != null' in newmutable[0] and 'OperatorRolePathSelector.SelectUserData(_activeStartupConfig)' in newmutable[0]
assert 'DeclaredRoleUserData' in newmutable[1] and 'OperatorRolePathSelector.SelectUserData(_activeAdmissionReceipt.Snapshot)' in newmutable[1]
assert 'public static class OperatorRolePathSelector' in newmutable[2]
diff=T/'MASTER_R25_WORKER_SOURCE_DIFF.txt';diff.write_text(''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True),new.decode('utf-8-sig').splitlines(True),fromfile='FrozenR23Worker',tofile='R25Worker')),encoding='utf8')
for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:assert sha(source/n)==oldmap[str(source/n).lower()]['sha256']
beforeafter=[]
for phase in ['BEFORE','AFTER']:
 freeze=read(T/f'ENGINE_FREEZE_{phase}.json')
 for f in freeze if isinstance(freeze,list) else freeze['files']:
  original=Path(f['path']);q=Path(oldmap[str(original).lower()]['frozen_path']) if phase=='BEFORE' else original
  assert sha(q)==f['sha256'] and q.stat().st_size==f['size'];beforeafter.append(dict(phase=phase,path=str(original),sha256=f['sha256'],size=f['size'],matched=True))
assert len(beforeafter)==18
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb')
 m=json.loads(subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True,timeout=30).stdout)
 assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents'])
 m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
rel=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R25_ROLE_USERDATA.json')
for m,key in zip(lineage,['selected_candidate','alternate_candidate']):
 assert m['mvid']==rel[key]['mvid'] and m['dll_sha256']==rel[key]['dll_sha256'] and m['pdb_sha256']==rel[key]['pdb_sha256']
host=read(s/'HOST_TELEMETRY.json');assert host['pinned_runner']['sha256']==sha(Path(host['pinned_runner']['path']))
processes=[]
for n in ['run_en_us','run_de_de']:
 root=s/n;res=read(root/'E1_EXECUTION_REPORT.json');inv=read(root/'OUTPUT_INVENTORY.json');hr=next(x for x in host['runs'] if Path(x['run_dir']).name==n)
 assert res['culture']==hr['culture'] and hr['exit_code']==0 and res['total_cases']==4 and res['to_snapshot_calls']==4 and res['select_userdata_calls']==8 and all(x['status']=='PASS' for x in res['cases'])
 rows=[]
 for f in inv:
  q=root/f['relative_path'];assert sha(q)==f['sha256'] and q.stat().st_size==f['size_bytes'];rows.append(dict(f,matched=True))
 actualset={q.relative_to(root).as_posix() for q in root.rglob('*') if q.is_file() and q.name!='OUTPUT_INVENTORY.json'}
 assert actualset=={f['relative_path'] for f in inv}
 processes.append({'directory':str(root),'actual_culture':res['culture'],'host_child_pid':hr['child_pid'],'host_recorded_numeric_exit':hr['exit_code'],'results':res,'inventory_rows':len(inv),'actual_nonself_files':len(actualset),'inventory_exact_path_set':True,'inventory_checks':rows,'actual_loaded_candidate_identity':'NOT_RECORDED_BY_PRODUCER'})
files=set()
for basepath in [source,s,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in basepath.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for f in ac['artifacts']:files.add(Path(f['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.md','.json','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R25-dd341868';mp=T/'MASTER_GATE05_R25_ROLE_USERDATA_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','files':rows,'runtime_e2_released':False})
vp=C/'MASTER_GATE05_R25_ROLE_USERDATA_E1_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'run_id':'MASTER-R25-HEARTBEAT-20261011T132716Z-01','guard_session':72947,'guard_pid':26592,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':ac['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'artifact_aliases_require_reconciliation':True,'before_after_checks':beforeafter,'fixed_segment_checks':fixedchecks,'new_mutable_source_spans':newmutable,'protected_paths_checked':protected_checks,'source_diff':str(diff),'source_sha256':sha(source/'WorkerBridge.cs'),'preservation_path':str(pp),'preservation_sha256':sha(pp),'lineage':lineage,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'selected_sha256':lineage[0]['dll_sha256'],'selected_mvid':lineage[0]['mvid'],'selected_pdb_sha256':lineage[0]['pdb_sha256'],'processes':processes,'ACK_valid':True,'producer_host_telemetry':host,'native_execution':'UNTESTED','master_build_execute':0,'runtime_e2_released':False,'trigger_received_at':'2026-10-11T13:27:16.095Z','closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_DISPOSITION'}
write(vp,proof);print(json.dumps({'artifacts':len(checks),'protected_paths':protected_checks,'fixed_segments':len(fixedchecks),'freeze':len(rows),'freezeSHA':sha(mp),'selected':proof['selected_sha256'],'MVID':proof['selected_mvid'],'inventory_counts':[(p['inventory_rows'],p['actual_nonself_files']) for p in processes],'status':'PENDING_MASTER_DISPOSITION'}))
