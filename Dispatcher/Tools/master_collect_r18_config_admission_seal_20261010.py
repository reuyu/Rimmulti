from pathlib import Path
import json,datetime,hashlib,sys,shutil,subprocess,difflib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['completion_path']).parent;ac=read(Path(t['completion_path']))
assert c['active_operation'] is None and t['dispatch_id'].endswith('befc4fba') and all(t[k]==ac[k] for k in ['dispatch_id','wp_id','wp_revision']) and ac['producer']=='A' and ac['report_kind']=='E1';checks=[]
for f in ac['artifacts']:
 p=Path(f['path']);assert p.resolve().is_relative_to(R) and sha(p)==f['sha256'] and p.stat().st_size==f['size'];checks.append(dict(f,matched=True))
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];assert [len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']]==[19,1663,206,7236]
write(T/'MASTER_R18_TERMINAL_PRESERVATION.json',pres)
source=R/'scratch/WorkerBridgeMod/Source';s=R/'scratch/EngineGate05R18ConfigAdmissionSeal';oldmap={f['original_path'].lower():f for f in read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files']}
for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:assert sha(source/n)==oldmap[str(source/n).lower()]['sha256']
oldw=Path(oldmap[str(source/'WorkerBridge.cs').lower()]['frozen_path']);(T/'MASTER_R18_WORKER_SOURCE_DIFF.txt').write_text(''.join(difflib.unified_diff(oldw.read_text(encoding='utf-8-sig').splitlines(True),(source/'WorkerBridge.cs').read_text(encoding='utf-8-sig').splitlines(True),fromfile='FrozenR17Worker',tofile='R18Worker')),encoding='utf8')
beforeafter=[]
for phase in ['BEFORE','AFTER']:
 for f in read(T/f'ENGINE_FREEZE_{phase}.json')['files']:
  original=Path(f['path']);selected=Path(oldmap[str(original).lower()]['frozen_path']) if phase=='BEFORE' else original
  assert sha(selected)==f['sha256'] and selected.stat().st_size==f['size'];beforeafter.append(dict(phase=phase,path=str(original),sha256=f['sha256'],size=f['size'],matched=True))
assert len(beforeafter)==18
files=set()
for base in [source,s,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for f in ac['artifacts']:files.add(Path(f['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.md','.json','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R18-befc4fba';mp=T/'MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','files':rows,'runtime_e2_released':False})
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');o=subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True);m=json.loads(o.stdout)
 assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents']);m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
rel=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R18_CONFIG_ADMISSION_SEAL.json');assert [m['mvid'] for m in lineage]==[rel['selected_candidate']['mvid'],rel['alternate_candidate']['mvid']]
host=read(s/'HOST_TELEMETRY.json');assert host['pinned_runner']['sha256']==sha(Path(host['pinned_runner']['path'])) and len(host['runs'])==2
processes=[]
for n in ['run_en_us','run_de_de']:
 root=s/n;res=read(root/'RESULTS.json');ledger=read(root/'API_LEDGER.json');inv=read(root/'OUTPUT_INVENTORY.json');raw=(root/'stdout.txt').read_text(encoding='utf-8-sig');hr=next(x for x in host['runs'] if x['run_name']==n)
 assert res['PassedTests']==res['TotalTests']==9 and res['FailedTests']==0 and res['LoadedCandidateSha256']==lineage[0]['dll_sha256'] and res['LoadedCandidateMvid']==lineage[0]['mvid'] and res['Culture']==hr['culture']
 assert res['ApiLedger']==ledger and ledger['ProcessApiCalls']==ledger['VerifyProcessIdentityCalls']==ledger['WorkerBridgeGlobalConfigureResetCalls']==0
 inventorychecks=[]
 for name,f in inv.items():
  p=Path(f['path']);inventorychecks.append({'relative_path':name,'recorded_sha256':f['sha256'],'actual_sha256':sha(p),'recorded_size':f['size'],'actual_size':p.stat().st_size,'matched':sha(p)==f['sha256'] and p.stat().st_size==f['size'],'self_row':p.name=='OUTPUT_INVENTORY.json'})
 actualset={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'};recordset=set(inv)-{'OUTPUT_INVENTORY.json'}
 assert actualset==recordset and all(x['matched'] for x in inventorychecks if not x['self_row'])
 processes.append({'directory':str(root),'actual_culture':res['Culture'],'runner_pid_literal':res['ProcessId'],'host_child_pid':hr['child_pid'],'host_reported_numeric_exit':hr['exit_code'],'original_numeric_tool_transcript_retained':False,'labels':9,'manual_ledger':ledger,'ledger_sum':sum(ledger.values()),'unique_process_runid':res['RunId'],'inventory_rows':len(inv),'actual_nonself_files':len(actualset),'inventory_checks':inventorychecks,'stdout_sha256':sha(root/'stdout.txt'),'loaded_candidate_self_report':res['LoadedCandidateSha256']})
vp=C/'MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_E1_VERIFICATION_20261010.json';assert not vp.exists()
proof={'at':at,'run_id':'MASTER-HEARTBEAT-R18-20261010T063748Z-01','guard_session':41964,'guard_pid':11096,'trigger_received_at':'2026-10-10T06:37:48.784Z','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':ac['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'before_after_checks':beforeafter,'preservation':pres,'lineage':lineage,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'selected_sha256':lineage[0]['dll_sha256'],'selected_mvid':lineage[0]['mvid'],'selected_pdb_sha256':lineage[0]['pdb_sha256'],'processes':processes,'producer_host_telemetry':host,'static_credit':['PublicConfigureReset removed;internalone-time installer','Privatecopiedarray/detachedpolicygetters','Config byteSHA verified beforeparse;duplicate/unknown/missing structuralguards','RawrootednessbeforeFullPath/SHAASCIIhex/nonemptyfields','Awakeandlaunchbind missing-config Revoke added'],'static_remaining':['MissingCLIconfig stillattaches;Awake revokes thenlistens;ValidateInput canregrant withoutconfig check','Operatordescriptor originId/launchPlanId andAdmitBytes configPath notbound;nullable/defaultdescriptor/configIDskip','Internalinstaller acceptsanydetachedsnapshot,notadmissionprovenance;localtrustedstartup assumptionnot actualoriginproof','Path.IsPathRooted permitsdrive-relative/rootrelative;UTC TryParse not UTC-enforced;profile onlynonempty','Policy schema onlynonempty;policyId/revision Trim andintrevisioncoercion weakenopaque fixedCensus contract','Roleuserdata/cwd/frontend/currenttask/options/origin processidentity andactualcontent/context remainOPEN'],'producer_scope':'PureCSharpProcess0/globalWorkerConfigureReset0 credited;no observed negative probe in9validcalls;invalidguardassertion claim onlystatic','packaging_qualifications':['en-US/de-DE actualrecordedcultures +hostPID/exit0 rows credited;runnerPID0 isnotactualPID','Firstinventoryself stale-row mismatch andcount8versus7;namedreuseddirs +runner-onlyprepin,originaltools/fullinputs-resolved-loadedpostgraph partial','Manual17 directcalls notnestedprofiler;partialtyped assertions/not full14-or17snapshot/full25result oracle','TEST01 report saysmissing/unknown/duplicate rejection verified butonlyvalidParseStrict called','Hostfirstbeforelater source andisolationboolean present;no separatelysealedrun1-before/after graph originalproof'],'native_execution':'UNTESTED','master_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_DISPOSITION'}
write(vp,proof);print(json.dumps({'artifacts':len(checks),'freeze':len(rows),'freezeSHA':sha(mp),'selected':lineage[0]['dll_sha256'],'MVID':lineage[0]['mvid'],'actualcultures':[p['actual_culture'] for p in processes],'inventorySelfMismatch':any(not f['matched'] for p in processes for f in p['inventory_checks']),'status':'PENDING_MASTER_DISPOSITION'},ensure_ascii=True))
