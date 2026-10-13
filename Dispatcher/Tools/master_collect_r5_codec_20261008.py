"""Read-only metadata/hash collection and post-completion copy; no candidate execution."""
from pathlib import Path
import json,sys,datetime,subprocess,shutil
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as checker
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=checker.digest;at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];T=Path(t['completion_path']).parent;c=read(Path(t['completion_path']));assert c['dispatch_id']==t['dispatch_id'] and c['wp_revision']==t['wp_revision']
checks=[]
for x in c['artifacts']:
 p=Path(x['path']);assert p.resolve().is_relative_to(R);actual=sha(p);assert actual==x['sha256'] and p.stat().st_size==x['size'];checks.append(dict(x,actual_sha256=actual,actual_size=p.stat().st_size,matched=True))
pres=checker.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];write(T/'MASTER_R5_TERMINAL_PRESERVATION.json',pres)
files=set();source=R/'scratch/WorkerBridgeMod/Source'
for base in [source,R/'scratch/EngineGate05R5Codec',R/'scratch/WorkerBridgeMod/1.6/Assemblies']:
 for p in base.rglob('*'):
  if p.is_file() and not p.is_symlink():files.add(p.resolve())
for x in c['artifacts']:files.add(Path(x['path']).resolve())
for p in T.iterdir():
 if p.is_file() and not p.name.startswith('MASTER_') and p.suffix in ['.json','.md','.txt']:files.add(p.resolve())
F=T/'FROZEN_R5_CODEC_REVIEW';mp=T/'MASTER_GATE05_R5_CODEC_REVIEW_FREEZE_MANIFEST.json';assert not F.exists() and not mp.exists()
rows=[]
for p in sorted(files):
 assert p.is_relative_to(R);dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);before=sha(p);size=p.stat().st_size;shutil.copy2(p,dest);assert sha(dest)==before==sha(p) and size==dest.stat().st_size
 rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':before,'size':size})
write(mp,{'at':at,'dispatch_id':t['dispatch_id'],'kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','runtime_e2_released':False,'files':rows})
lineage=[]
for conf in ['Debug','Release']:
 dll=source/'bin'/conf/'net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');out=subprocess.run(['dotnet',str(R/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True);m=json.loads(out.stdout);assert m['codeviewMatched'] and all(x['matched'] for x in m['documents']);m.update(configuration=conf,dll_sha256=sha(dll),pdb_sha256=sha(pdb));lineage.append(m)
raw=(R/'scratch/EngineGate05R5Codec/raw_console.txt').read_text(encoding='utf-8-sig');results=read(R/'scratch/EngineGate05R5Codec/results.json')
proof={'at':at,'run_id':'MASTER-HEARTBEAT-20261008-1837-01','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'result_id':c['result_id'],'completion_sha256':sha(Path(t['completion_path'])),'reported_e1_verdict':c['e1_verdict'],'standard_schema_accepted':True,'artifact_checks':checks,'preservation':pres,'lineage':lineage,'frozen_manifest':str(mp),'frozen_manifest_sha256':sha(mp),'frozen_files':len(rows),'freeze_kind':'POST_COMPLETION_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','results_declared':results,'raw_pass_rows':sum(l.startswith('[PASS]') for l in raw.splitlines()),'candidate_execution_by_master':0,'candidate_rebuild_by_master':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','scheduled_r5_run_observed_at':'2026-10-08T09:37:09.643Z','master_review_status':'PENDING_DISPOSITION'}
vp=H/'coordination/MASTER_GATE05_R5_CODEC_E1_VERIFICATION_20261008.json';write(vp,proof)
print(json.dumps({'frozen_files':len(rows),'freeze_sha256':sha(mp),'artifacts':len(checks),'lineage':[{k:m[k] for k in ['configuration','mvid','codeviewMatched','dll_sha256','pdb_sha256']} for m in lineage],'results_keys':list(results),'raw_pass_rows':proof['raw_pass_rows']},ensure_ascii=False))
