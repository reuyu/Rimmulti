from pathlib import Path
import json,datetime,sys,shutil,subprocess,difflib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['completion_path']).parent;ac=read(Path(t['completion_path']));assert c['active_operation'] is None and t['dispatch_id'].endswith('57163c71')
assert all(t[k]==ac[k] for k in ['dispatch_id','wp_id','wp_revision']) and ac['producer']=='A' and ac['report_kind']=='E1';checks=[]
for f in ac['artifacts']:
 p=Path(f['path']);assert p.resolve().is_relative_to(R) and sha(p)==f['sha256'] and p.stat().st_size==f['size'];checks.append(dict(f,matched=True))
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];assert [len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']]==[19,1572,206,7043]
installed=Path('C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll');assert sha(installed)=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61';pres['known_installed_incident']={'status':'UNCHANGED_OPEN','sha256':sha(installed),'actor':'UNKNOWN'};write(T/'MASTER_R17_TERMINAL_PRESERVATION.json',pres)
source=R/'scratch/WorkerBridgeMod/Source';s=R/'scratch/EngineGate05R17OwnedBootstrap';oldmanifest=next(x['path'] for x in t['preservation_policy']['additional_preserved_candidate_manifests'] if x.get('lineage')=='R15_REVIEW93');oldmap={f['original_path'].lower():f for f in read(Path(oldmanifest))['files']}
for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:assert sha(source/n)==oldmap[str(source/n).lower()]['sha256']
oldw=Path(oldmap[str(source/'WorkerBridge.cs').lower()]['frozen_path']);(T/'MASTER_R17_WORKER_SOURCE_DIFF.txt').write_text(''.join(difflib.unified_diff(oldw.read_text(encoding='utf-8-sig').splitlines(True),(source/'WorkerBridge.cs').read_text(encoding='utf-8-sig').splitlines(True),fromfile='FrozenR15Worker',tofile='R17Worker')),encoding='utf8')
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
F=R/'Dispatcher/CANDIDATES/G05R17-57163c71';mp=T/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','files':rows,'runtime_e2_released':False})
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');o=subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True);m=json.loads(o.stdout);assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents']);m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
rel=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R17_OWNED_BOOTSTRAP.json');assert [m['mvid'] for m in lineage]==[rel['selected_candidate']['mvid'],rel['alternate_candidate']['mvid']]
processes=[]
for name in ['run_default','run_en_us','run_de_de']:
 root=s/name;res=read(root/'RESULTS.json');ledger=read(root/'API_LEDGER.json');inv=read(root/'OUTPUT_INVENTORY.json');raw=(root/'stdout.txt').read_text(encoding='utf-8-sig')
 assert res['PassedTests']==res['TotalTests']==5 and res['FailedTests']==0 and res['LoadedCandidateSha256']==lineage[0]['dll_sha256'] and res['LoadedCandidateMvid']==lineage[0]['mvid']
 assert res['ApiLedger']==ledger and ledger['VerifyProcessIdentityCalls']==1
 assert inv['file_count']==len(inv['files'])==4 and {f['relative_path'] for f in inv['files']}=={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 for f in inv['files']:p=root/f['relative_path'];assert sha(p)==f['sha256'] and p.stat().st_size==f['size']
 assert 'Self-validation prohibited' in res['Tests'][2]['Artifacts']['RejectionReason']
 processes.append({'directory':str(root),'culture':res['Culture'],'recorded_pid':res['ProcessId'],'recorded_run_id':res['RunId'],'runner_reported_numeric_exit':res['NumericExitCode'],'retained_actual_os_exit_tool_proof':False,'tests_labels':5,'ledger':ledger,'direct_manual_ledger_sum':sum(ledger.values()),'out_of_scope_self_pid_rejection':True,'inventory_files':4,'inventory_captured_at':inv['captured_at_utc'],'runtime_timestamp':res['TimestampUtc'],'loaded_candidate_self_report':res['LoadedCandidateSha256'],'source_liveprocess_query':'Process.GetCurrentProcess/MainModule andVerifyProcessIdentity self-rejection called,notnormaladmittedhelper'})
proof={'at':at,'run_id':'MASTER-HEARTBEAT-R17-20261009T191508Z-01','guard_session':31503,'guard_pid':30996,'trigger_received_at':'2026-10-09T19:15:08.977Z','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':ac['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'before_after_checks':beforeafter,'preservation':pres,'lineage':lineage,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'selected_sha256':lineage[0]['dll_sha256'],'selected_mvid':lineage[0]['mvid'],'selected_pdb_sha256':lineage[0]['pdb_sha256'],'processes':processes,'static_credit':['Executable file SHA used inlaunchpreflight/MainModule hash helper present','Child callerpath/rawargs nomination restricted,currenttask argsderived','Startup config parse+Awake policy initialization sourcewire added','PublicValidatorResult two secrets redacted/protectedchannel raw retained','Census/csproj fixed'], 'static_remaining':['PublicConfigure/Reset/ActiveStartup plusmutable nestedpolicy andpubliclegacysetter fallback compromise ownedimmutableconfig','ConfigfileSHA/origin notpinned;missingconfig/parsefails logthencontinue;trustedreadyconfig gate absent','Path.GetFullPath beforeIsPathRooted normalizesrelative;SHA onlylengthnothex;emptycwd/profile/defaultrole+capability allowed','READ_ONLYuserdata alwaysusesWorkerUserData;childargs omitvalidatordata/READ_ONLYbootstrap/CLIhandler-taskdispatch integration','Expectedroleunused/expectedPidproc.Id/startnull are observation notindependentadmittedtuple','ExpectedContentProfileFingerprint declared/getter-redactedonly not actualauthorityprofilebind','Core existing target/currentcontext/revocation/error/content/patchsettings unresolved'], 'producer_scope_deviation':'TEST03 invokesactualProcess.GetCurrentProcess/MainModule andVerifyProcessIdentity self-rejection onceeach3process contrarypositivepureonly;do notreplay orall5scopePASS','packaging_qualifications':['Three4outputinventories present+currentSHA-size match;createdafterallthree runs notfirstbeforenext','execute_runs Culture valuesneverapplied;actualRESULTSCulturecontrols names','Runnerreportedexit0 isnotretainedactualOSexitororiginaltooltranscript','No originalbuildnumerictool/resolvedcompiler/prepin/independenttypedexpected/fullactualmanagedloaded/postpin graph','TC01 snapshotimmutabilitylabel lacksnestedownershipmutation/fulltypedassertion'], 'native_execution':'UNTESTED','master_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_DISPOSITION'}
vp=C/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_E1_VERIFICATION_20261010.json';assert not vp.exists();write(vp,proof);print(json.dumps({'artifacts':len(checks),'freeze':len(rows),'freezeSHA':sha(mp),'selected':lineage[0]['dll_sha256'],'MVID':lineage[0]['mvid'],'actualcultures':[p['culture'] for p in processes],'self_pid_scope_deviation':True},ensure_ascii=True))
