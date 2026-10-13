"""Master post-completion hashes/copies/PE metadata only; candidate execute/build0."""
from pathlib import Path
import json,sys,datetime,subprocess,shutil
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as checker
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=checker.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1]
assert t['dispatch_id']=='WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692'
assert read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json')['active_operation'] is None
T=Path(t['completion_path']).parent;c=read(Path(t['completion_path']))
assert c['dispatch_id']==t['dispatch_id'] and c['wp_revision']==t['wp_revision']
assert c['result_id']=='WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-RESULT-01'
assert sha(Path(t['completion_path']))=='3EEA7DE17F4F0E8486A4D1FA3E5EFD250AD7F4D4CEDBB5935CE85BD8FA55791A'
checks=[]
for x in c['artifacts']:
 p=Path(x['path']);assert p.resolve().is_relative_to(R)
 assert sha(p)==x['sha256'] and p.stat().st_size==x['size']
 checks.append(dict(x,actual_sha256=sha(p),actual_size=p.stat().st_size,matched=True))
pres=checker.inspect_preservation(t)
assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
installed=Path('C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll')
installed_sha=sha(installed)
assert installed_sha=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61'
pres['known_installed_incident']={'path':str(installed),'actual_sha256':installed_sha,'actual_size':installed.stat().st_size,'unchanged_from_observed_incident':True,'status':'OPEN','actor':'UNKNOWN','restored':False}
write(T/'MASTER_R8_TERMINAL_PRESERVATION.json',pres)
files=set();source=R/'scratch/WorkerBridgeMod/Source';scratch=R/'scratch/EngineGate05R8SupportedDisposition'
for base in [source,scratch,R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for x in c['artifacts']:files.add(Path(x['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.json','.md','.txt']:files.add(p.resolve())
F=R/'Dispatcher/CANDIDATES/G05R8-41abc692';mp=T/'MASTER_GATE05_R8_SUPPORTED_DISPOSITION_REVIEW_FREEZE_MANIFEST.json'
assert not mp.exists();rows=[]
for p in sorted(files):
 assert p.is_relative_to(R);dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);before=sha(p);size=p.stat().st_size
 if dest.exists():assert sha(dest)==before and dest.stat().st_size==size
 else:shutil.copy2(p,dest)
 assert sha(dest)==before==sha(p) and size==dest.stat().st_size
 rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':before,'size':size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','runtime_e2_released':False,'files':rows})
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb')
 out=subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True)
 m=json.loads(out.stdout);assert m['codeviewMatched'] and all(x['matched'] for x in m['documents'])
 m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
oldmap={x['original_path'].lower():x for x in read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files']}
freeze_checks=[]
for phase in ['BEFORE','AFTER']:
 for rel,x in read(scratch/f'ENGINE_FREEZE_{phase}.json')['files'].items():
  original=(R/rel).resolve();p=Path(oldmap[str(original).lower()]['frozen_path']) if phase=='BEFORE' else original
  assert sha(p)==x['sha256'] and p.stat().st_size==x['size']
  freeze_checks.append({'kind':phase,'path':str(original),'matched':True,'size_matched':True})
raw=(scratch/'raw_console.txt').read_text(encoding='utf-8-sig');results=read(scratch/'results.json');release=read(R/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION.json')
assert [x['mvid'] for x in lineage]==[release['selected_candidate']['mvid'],release['alternate_candidate']['mvid']]
assert sum(l.startswith('[PASS]') for l in raw.splitlines())==16==len(results['results'])
ids=[l.split(':',1)[0].removeprefix('[PASS] ') for l in raw.splitlines() if l.startswith('[PASS]')]
assert ids==[x['test_id'] for x in results['results']]
proof={'at':at,'run_id':'MASTER-HOURLY-R8-20261009-003544-01','guard_session':83368,'guard_renewed_before_mutation':True,'dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':c['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'reported_e1_verdict':c['e1_verdict'],'artifact_checks':checks,'preservation':pres,'lineage':lineage,'before_after_checks':freeze_checks,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'freeze_kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','results_declared':results,'raw_pass_rows':16,'candidate_execution_by_master':0,'candidate_rebuild_by_master':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','scheduled_r8_run_observed_at':'2026-10-08T15:35:44.760Z','master_review_status':'PENDING_DISPOSITION'}
write(H/'coordination/MASTER_GATE05_R8_SUPPORTED_DISPOSITION_E1_VERIFICATION_20261009.json',proof)
print(json.dumps({'frozen_files':len(rows),'freeze_sha256':sha(mp),'artifacts':len(checks),'lineage':[{k:m[k] for k in ['configuration','mvid','codeviewMatched','dll_sha256','pdb_sha256']} for m in lineage],'before_after':len(freeze_checks),'raw_pass_rows':16,'installed_unchanged':True},ensure_ascii=False))
