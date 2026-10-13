from pathlib import Path
import json,datetime,sys,shutil,subprocess,hashlib,difflib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=ck.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];assert t['dispatch_id'].endswith('ff285a3b');T=Path(t['completion_path']).parent;c=read(Path(t['completion_path']));assert c['dispatch_id']==t['dispatch_id'] and c['wp_revision']==t['wp_revision'] and c['wp_id']==t['wp_id'] and c['producer']=='A' and c['report_kind']=='E1';checks=[]
for f in c['artifacts']:
 p=Path(f['path']);assert p.resolve().is_relative_to(R) and sha(p)==f['sha256'] and p.stat().st_size==f['size'];checks.append(dict(f,matched=True))
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];assert [len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']]==[19,1395,206,5186]
installed=Path('C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll');assert sha(installed)=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61';pres['known_installed_incident']={'sha256':sha(installed),'status':'UNCHANGED_OPEN','actor':'UNKNOWN'};write(T/'MASTER_R14_TERMINAL_PRESERVATION.json',pres)
source=R/'scratch/WorkerBridgeMod/Source';s=R/'scratch/EngineGate05R14PolicyCapturePublication';old=read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files'];oldmap={f['original_path'].lower():f for f in old};oldc=Path(oldmap[str(source/'EngineHostCensus.cs').lower()]['frozen_path']);newc=source/'EngineHostCensus.cs';assert oldc.read_bytes()[:72547]==newc.read_bytes()[:72547]
for n in ['WorkerBridge.cs','WorkerBridge.csproj']:assert sha(source/n)==oldmap[str(source/n).lower()]['sha256']
(T/'MASTER_R14_SOURCE_DIFF.txt').write_text(''.join(difflib.unified_diff(oldc.read_text(encoding='utf-8-sig').splitlines(True),newc.read_text(encoding='utf-8-sig').splitlines(True),fromfile='FrozenR13',tofile='R14')),encoding='utf8')
files=set()
for base in [source,s,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for f in c['artifacts']:files.add(Path(f['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.md','.json','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R14-ff285a3b';mp=T/'MASTER_GATE05_R14_POLICY_CAPTURE_PUBLICATION_REVIEW_FREEZE_MANIFEST.json';assert not mp.exists();rows=[]
for p in sorted(files):
 assert p.is_relative_to(R);dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);h=sha(p);n=p.stat().st_size
 if dest.exists():assert sha(dest)==h and dest.stat().st_size==n
 else:shutil.copy2(p,dest)
 assert sha(p)==sha(dest)==h;rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':h,'size':n})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_CHRONOLOGY','files':rows,'runtime_e2_released':False})
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');out=subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True);m=json.loads(out.stdout);assert m['codeviewMatched'] and len(m['documents'])==4 and all(x['matched'] for x in m['documents']);m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
freezechecks=[]
for phase in ['BEFORE','AFTER']:
 for f in read(s/f'ENGINE_FREEZE_{phase}.json')['files']:
  original=(R/f['path']).resolve();p=Path(oldmap[str(original).lower()]['frozen_path']) if phase=='BEFORE' else original;assert sha(p)==f['sha256'] and p.stat().st_size==f['size'];freezechecks.append(dict(phase=phase,path=str(original),matched=True))
release=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION.json');assert [m['mvid'] for m in lineage]==[release['selected_candidate']['mvid'],release['alternate_candidate']['mvid']]
raw=(s/'raw_console.txt').read_text(encoding='utf-8-sig');result=read(s/'results.json');assert sum(l.startswith('[PASS]') for l in raw.splitlines())==22 and len(result['test_cases'])==22
proof={'at':at,'run_id':'MASTER-R14-HEARTBEAT-20261009T130103Z-01','guard_session':29525,'guard_pid':20716,'trigger_received_at':'2026-10-09T13:01:03.514Z','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':c['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'artifact_checks':checks,'preservation':pres,'lineage':lineage,'before_after_checks':freezechecks,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'selected_sha256':lineage[0]['dll_sha256'],'selected_mvid':lineage[0]['mvid'],'selected_pdb_sha256':lineage[0]['pdb_sha256'],'retained_results':result,'raw_pass_labels':22,'raw_culture':'ko-KR','native_execution':'UNTESTED','master_build_execute':0,'static_credit':['Fingerprint usescapturedpolicythroughcollector then guardedpublish refusal throws','ExplicitInvalidate advancesgeneration+1 and clearsentry/error underlock'],'static_remaining':['Public parameterless actualmanifest returns collector result without final currentstamp check','New public actualmanifest(caller-suppliedpolicy) overload lacks provider-origin/currentstamp binding;must not be adopted as actualprofile admission authority','Separate manifest/JSON/fingerprint coreinputs and error writes still qualified'], 'packaging_qualifications':['No immutable perprocess roots/full output inventories retained','Only root raw/results ko-KR retained;runnerbin results separate identity not fullculturegraph','Actual compiler/inputexpected/loadedhash/MVID/PID/argv-cwd/numericbuildrunexit/fullprepost chronology graph incomplete','Raw CacheAccounting total46/configure11/invalidate2/publish6/query10 arithmetic and reportqueries27 disagree;declaration not fully instrumented invocation proof'], 'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_DISPOSITION'}
vp=H/'coordination/MASTER_GATE05_R14_POLICY_CAPTURE_PUBLICATION_E1_VERIFICATION_20261009.json';assert not vp.exists();write(vp,proof);print(json.dumps({'freeze':len(rows),'freeze_sha':sha(mp),'artifacts':len(checks),'beforeafter':len(freezechecks),'selected':lineage[0]['dll_sha256'],'mvid':lineage[0]['mvid']}))
