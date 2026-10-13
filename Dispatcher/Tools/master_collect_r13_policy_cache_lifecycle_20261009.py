"""Read/hash/copy and PE metadata only. No production build or execution."""
from pathlib import Path
import json,sys,datetime,subprocess,shutil,difflib,hashlib
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];assert t['dispatch_id'].endswith('2661a749');T=Path(t['completion_path']).parent;c=read(Path(t['completion_path']))
assert c['dispatch_id']==t['dispatch_id'] and c['wp_id']==t['wp_id'] and c['wp_revision']==t['wp_revision'] and c['producer']=='A' and c['report_kind']=='E1' and c['schema_version']==1
checks=[]
for x in c['artifacts']:
 p=Path(x['path']);assert p.resolve().is_relative_to(R) and sha(p)==x['sha256'] and p.stat().st_size==x['size'];checks.append(dict(x,matched=True))
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
installed=Path('C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll');assert sha(installed)=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61'
pres['known_installed_incident']={'actual_sha256':sha(installed),'size':installed.stat().st_size,'status':'UNCHANGED_OPEN','actor':'UNKNOWN','restored':False};write(T/'MASTER_R13_TERMINAL_PRESERVATION.json',pres)
source=R/'scratch/WorkerBridgeMod/Source';scratch=R/'scratch/EngineGate05R13PolicyCacheLifecycle';oldrows=read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files'];oldmap={x['original_path'].lower():x for x in oldrows};oldc=Path(oldmap[str(source/'EngineHostCensus.cs').lower()]['frozen_path']);newc=source/'EngineHostCensus.cs'
assert newc.read_bytes()[:72547]==oldc.read_bytes()[:72547]
for name in ['WorkerBridge.cs','WorkerBridge.csproj']:assert sha(source/name)==oldmap[str(source/name).lower()]['sha256']
(T/'MASTER_R13_SOURCE_SCOPE_DIFF.txt').write_text(''.join(difflib.unified_diff(oldc.read_text(encoding='utf-8-sig').splitlines(True),newc.read_text(encoding='utf-8-sig').splitlines(True),fromfile='Frozen R12',tofile='R13')),encoding='utf-8')
files=set()
for base in [source,scratch,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for x in c['artifacts']:files.add(Path(x['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.json','.md','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R13-2661a749';mp=T/'MASTER_GATE05_R13_POLICY_CACHE_LIFECYCLE_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 assert p.is_relative_to(R);dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);h=sha(p);n=p.stat().st_size
 if dest.exists():assert sha(dest)==h and dest.stat().st_size==n
 else:shutil.copy2(p,dest)
 assert sha(p)==sha(dest)==h and dest.stat().st_size==n;rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':h,'size':n})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','files':rows,'runtime_e2_released':False})
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');cmd=['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)];out=subprocess.run(cmd,capture_output=True,text=True,check=True);m=json.loads(out.stdout);assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents']);m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb),metadata_tool_argv=cmd,metadata_tool_exit=out.returncode);lineage.append(m)
fc=[]
for phase in ['BEFORE','AFTER']:
 for x in read(scratch/f'ENGINE_FREEZE_{phase}.json')['files']:
  p=(R/x['path']).resolve();compare=Path(oldmap[str(p).lower()]['frozen_path']) if phase=='BEFORE' else p;assert sha(compare)==x['sha256'] and compare.stat().st_size==x['size'];fc.append({'phase':phase,'path':str(p),'matched':True})
release=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE.json');assert [m['mvid'] for m in lineage]==[release['selected_candidate']['mvid'],release['alternate_candidate']['mvid']]
results=read(scratch/'results.json');raw=(scratch/'raw_console.txt').read_text(encoding='utf-8-sig');assert results['culture']=='ko-KR' and len(results['test_cases'])==24 and sum(x.startswith('[PASS]') for x in raw.splitlines())==24
proof={'at':at,'run_id':'MASTER-R13-HEARTBEAT-20261009T110931Z-01','guard_session':32118,'guard_pid':864,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':c['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'preservation':pres,'lineage':lineage,'before_after_checks':fc,'fixed_prefix_sha256':hashlib.sha256(newc.read_bytes()[:72547]).hexdigest().upper(),'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'results_declared':results,'raw_pass_labels':24,'retained_culture':'ko-KR','other_cultures_report_only':True,'producer_scope_conflicts':['TC13 stale generation rejection actually called','TC19 cross-policy mismatch rejection actually called','report says negative/rejection/mismatch executions0 contrary source/raw'], 'packaging_limitations':['No immutable per-process output directories/full output inventories retained','Only root results/raw ko-KR retained;en-US/de-DE narrative only','Actual compiler SDK/framework resolved graph,input oracle,loaded identity/PID,argv/cwd/numeric build-run exit graph incomplete'],'source_findings':['Configure/Clear increment generation and clear entry atomically;defensive policy clones and serialized manifest copies credited','InvalidateCache clears entry without advancing stamp;in-flight captured generation can still publish afterward STATIC_OPEN','ComputeActual captures state but ComputeActualManifest reacquires policy later;TryPublish rejection only logs warning then returns fingerprint STATIC_REVISION_REQUIRED','TryPublish stores separately supplied JSON/fingerprint/manifest without internal coherent identity derivation;matching normal core inputs only admitted','Native/global actual collection or full profile gate remains UNTESTED'],'candidate_execute_by_master':0,'candidate_rebuild_by_master':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','master_review_status':'PENDING_DISPOSITION'}
vp=H/'coordination/MASTER_GATE05_R13_POLICY_CACHE_LIFECYCLE_E1_VERIFICATION_20261009.json';assert not vp.exists();write(vp,proof);print(json.dumps({'files':len(rows),'freeze_sha256':sha(mp),'artifacts':len(checks),'before_after':len(fc),'lineage':[{'configuration':m['configuration'],'mvid':m['mvid'],'pdb_source':len(m['documents'])} for m in lineage],'proof':str(vp)}))
