"""Master read/copy-only R4 collection. Does not build or run candidate/harness/game."""
from pathlib import Path
import sys, json, hashlib, shutil, datetime, subprocess
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Dispatcher'))
import master_check_a_result as checker
H = ROOT/'docs/WarEconomy_Master_Handoff_20261006'
board = json.loads((ROOT/'Dispatcher/MASTER_A_TASKS.json').read_text(encoding='utf-8-sig'))
task = next(t for t in board['tasks'] if t['dispatch_id']=='WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1')
T = Path(task['completion_path']).parent
def sha(p): return checker.digest(p)
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
completion = read(T/'COMPLETION.json')
assert completion['dispatch_id']==task['dispatch_id'] and completion['wp_revision']==task['wp_revision']
artifact_checks=[]
for a in completion['artifacts']:
    p=Path(a['path']); assert p.is_absolute() and p.resolve().is_relative_to(ROOT)
    artifact_checks.append(dict(a,actual_sha256=sha(p),actual_size=p.stat().st_size,matched=sha(p)==a['sha256'].upper(),size_matched=p.stat().st_size==a['size']))
assert all(a['matched'] and a['size_matched'] for a in artifact_checks)
preservation=checker.inspect_preservation(task)
write(T/'MASTER_R4_PRESERVATION_AT_COLLECTION.json',preservation)
files=set()
source=ROOT/'scratch/WorkerBridgeMod/Source'
for p in source.rglob('*'):
    if p.is_file() and not p.is_symlink(): files.add(p.resolve())
for p in (ROOT/'scratch/EngineGate05R4').rglob('*'):
    if p.is_file() and not p.is_symlink(): files.add(p.resolve())
for p in (ROOT/'scratch/WorkerBridgeMod/1.6/Assemblies').glob('*'):
    if p.is_file(): files.add(p.resolve())
for a in completion['artifacts']: files.add(Path(a['path']).resolve())
for p in T.iterdir():
    if p.is_file() and not p.name.startswith('MASTER_'): files.add(p.resolve())
freeze=T/'FROZEN_R4_REVIEW'
manifest_path=T/'MASTER_GATE05_R4_REVIEW_FREEZE_MANIFEST.json'
assert not freeze.exists() and not manifest_path.exists(), 'Do not overwrite freeze'
rows=[]
for p in sorted(files):
    assert p.is_relative_to(ROOT)
    dest=freeze/p.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True)
    before=sha(p); size=p.stat().st_size; shutil.copy2(p,dest)
    assert sha(dest)==before and sha(p)==before and dest.stat().st_size==size, str(p)
    rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':before,'size':size})
write(manifest_path,{'at':now,'dispatch_id':task['dispatch_id'],'kind':'POST_COMPLETION_READ_ONLY_REVIEW_SNAPSHOT_NOT_PRE_EXECUTION_PROOF','candidate_admitted_for_runtime_e2':False,'files':rows})
metadata=[]
for configuration in ['Debug','Release']:
    dll=source/'bin'/configuration/'net472/WarEconomy.WorkerBridge.PoC.dll'
    pdb=dll.with_suffix('.pdb')
    result=subprocess.run(['dotnet',str(ROOT/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True)
    d=json.loads(result.stdout); d['configuration']=configuration
    d['dll_sha256']=sha(dll);d['pdb_sha256']=sha(pdb)
    assert d['codeviewMatched'] and all(x['matched'] for x in d['documents'])
    metadata.append(d)
results=read(ROOT/'scratch/EngineGate05R4/results.json')
runtime=ROOT/'scratch/EngineGate05R4/RuntimeCopy'
runtime_rows=[{'path':str(p),'sha256':sha(p),'size':p.stat().st_size} for p in runtime.rglob('*') if p.is_file()]
proof={'at':now,'run_id':'MASTER-HEARTBEAT-20261008-1707-01','dispatch_id':task['dispatch_id'],'wp_id':task['wp_id'],'wp_revision':task['wp_revision'],'result_id':completion['result_id'],'completion_sha256':sha(T/'COMPLETION.json'),'reported_e1_verdict':completion['e1_verdict'],'limitations':completion['limitations'],'standard_schema_accepted':False,'schema_issue':'limitations object is meaningful but checker contract accepts string/list; e1_verdict present','artifact_checks':artifact_checks,'preservation_proof':str(T/'MASTER_R4_PRESERVATION_AT_COLLECTION.json'),'preservation':preservation,'lineage':metadata,'frozen_manifest':str(manifest_path),'frozen_manifest_sha256':sha(manifest_path),'frozen_files':len(rows),'freeze_kind':'POST_COMPLETION_READ_ONLY_REVIEW_SNAPSHOT','runtime_copy_inventory':runtime_rows,'reported_tests':{'declared':results['total_tests'],'rows':len(results['results']),'pass_rows':sum(x['status']=='PASS' for x in results['results']),'ids':[x['id'] for x in results['results']]},'master_verdict':'REVISION_REQUIRED_E2_RUNTIME_NOT_RELEASED','candidate_execution_by_master':0,'candidate_rebuild_by_master':0,'closure_changed':False,'foundation':'HOLD','next_action':'Independent Sol static review on exact frozen R4; no runtime execution release'}
write(H/'coordination/MASTER_GATE05_R4_E1_VERIFICATION_20261008.json',proof)
print(json.dumps({'at':now,'freeze_count':len(rows),'freeze_sha256':sha(manifest_path),'artifact_count':len(artifact_checks),'lineage':[{k:d[k] for k in ['configuration','mvid','codeviewMatched']} for d in metadata],'preservation_keys':list(preservation),'runtime_files':len(runtime_rows),'reported_tests':proof['reported_tests']},ensure_ascii=False))
