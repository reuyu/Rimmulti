"""Master read-only R2 evidence review, identity verification, immutable snapshot."""
from pathlib import Path
import collections, datetime, hashlib, json, re, shutil, subprocess, sys, tomllib
import master_check_a_result as checker
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'Dispatcher'; H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
board=read(D/'MASTER_A_TASKS.json')
t=next(t for t in board['tasks'] if t['dispatch_id']=='WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708')
folder=Path(t['completion_path']).parent
completion=read(Path(t['completion_path']))
assert completion['task_id']==t['dispatch_id'] and completion['work_package_id']==t['wp_id'] and completion['revision']==t['wp_revision']
config_path=Path(r'C:\Users\user\.codex\automations\wareconomy-master\automation.toml')
config=tomllib.loads(config_path.read_text(encoding='utf-8'))
assert config['status']=='PAUSED' and config['rrule'].removeprefix('RRULE:')=='FREQ=HOURLY;INTERVAL=1'
assert config['target_thread_id']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
assert config['prompt']==(D/'MASTER_MONITOR_TRIGGER.txt').read_text(encoding='utf-8-sig').strip()
pauseproof=H/'coordination/MASTER_MONITOR_PAUSED_R2_REVIEW_20261008.json'
write(pauseproof,{'checked_at':now,'user_instruction':'A completed; verify; pause scheduled task','automation_tool_result':{'automationId':'wareconomy-master','mode':'update','status':'PAUSED'},'actual_config':config,'config_sha256':sha(config_path),'interval_minutes':60,'target_and_short_prompt_matched':True})
checks=[]
for entry in completion['deliverables']:
 p=Path(entry['path']);assert p.is_absolute() and p.resolve().is_relative_to(ROOT)
 checks.append({'logical_name':entry['logical_name'],'path':str(p),'sha256':sha(p),'matched':sha(p)==entry['sha256'],'size_matched':p.stat().st_size==entry['bytes']})
for group in ['selected_candidate','alternate_candidate']:
 entry=completion[group]
 for ext in ['dll','pdb']:
  p=Path(entry[ext+'_path'])
  checks.append({'logical_name':group+'_'+ext,'path':str(p),'sha256':sha(p),'matched':sha(p)==entry[ext+'_sha256'],'size_matched':p.stat().st_size==entry[ext+'_bytes']})
assert all(c['matched'] and c['size_matched'] for c in checks)
lineages={}
for group in ['selected_candidate','alternate_candidate']:
 entry=completion[group]
 lineages[group]=json.loads(subprocess.check_output(['dotnet',str(D/'Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),entry['dll_path'],entry['pdb_path']],text=True))
 assert lineages[group]['codeviewMatched'] and all(x['matched'] for x in lineages[group]['documents'])
assert lineages['selected_candidate']['mvid']==completion['selected_candidate']['mvid']
results=read(ROOT/'scratch/EngineGate05R2/results.json')
counts=dict(collections.Counter(r['status'] for r in results['checkpoints']))
raw=(ROOT/'scratch/EngineGate05R2/raw_console.txt').read_text(encoding='utf-8-sig')
rawcounts=dict(collections.Counter(re.findall(r'^\[(PASS|FAIL|BLOCKED|UNTESTED)\] ',raw,re.M)))
assert counts==rawcounts and counts=={'PASS':23,'BLOCKED':1}
assert len(results['checkpoints'])==24
preservation=checker.inspect_preservation(t)
checker_result=checker.inspect()
write(folder/'MASTER_R2_COMPLETION_SCHEMA_CHECK.json',checker_result)
installed=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll')
installed_sha=sha(installed)
priorincident=read(H/'coordination/MASTER_R2_RECOVERY_ACK_REVIEW_20261008.json')
assert installed_sha==priorincident['installed_identity_incident']['actual_sha256']
paths={Path(c['path']) for c in checks}
paths.add(Path(t['completion_path']))
paths.update((ROOT/'scratch/EngineGate05R2').rglob('*'))
paths.update((ROOT/'scratch/WorkerBridgeMod/Source').rglob('*'))
paths.update((ROOT/'scratch/WorkerBridgeMod/1.6/Assemblies').rglob('*'))
paths={p for p in paths if p.is_file()}
freeze=folder/'FROZEN_GATE05_R2_REJECTED'
assert not freeze.exists(), 'Do not overwrite earlier R2 snapshot'
rows=[]
for p in sorted(paths,key=lambda p:str(p)):
 rel=p.relative_to(ROOT); dest=freeze/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 expected=sha(p);shutil.copy2(p,dest)
 assert sha(dest)==expected and sha(p)==expected
 rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':expected,'size':p.stat().st_size})
freeze_manifest=folder/'MASTER_GATE05_R2_REJECTED_FREEZE_MANIFEST.json'
write(freeze_manifest,{'schema_version':1,'created_at':now,'dispatch_id':t['dispatch_id'],'master_disposition':'REVISION_REQUIRED_E2_NOT_RELEASED','kind':'POST_REVIEW_IMMUTABLE_OBSERVATION_NOT_PRE_EXECUTION_PROOF','files':rows})
proof=H/'coordination/MASTER_GATE05_R2_E1_VERIFICATION_20261008.json'
record={'schema_version':1,'event_id':'MASTER-GATE05-R2-E1-REVIEW-20261008-01','at':now,'exclusive_lock_session':73015,'exclusive_lock_run':'MASTER-A-R2-RESULT-REVIEW-20261008-01','dispatch_id':t['dispatch_id'],'original_completion_sha256':sha(Path(t['completion_path'])),'producer_result_id_missing':True,'master_collection_key':'MASTER-OBSERVED-R2-'+sha(Path(t['completion_path'])),'completion_alias_identity_reconciled':True,'standard_completion_schema_valid':False,'artifact_checks':checks,'lineages':lineages,'checkpoint_counts':counts,'raw_counts':rawcounts,'producer_verdict':completion['e1_verification_summary']['verdict'],'master_verdict':'REVISION_REQUIRED_E2_NOT_RELEASED','preservation':preservation,'installed_sha256':installed_sha,'installed_incident_unchanged':True,'native_actual_launch_proof':False,'native_blocker_reason_proven':False,'runner_execution_not_repeated_by_master':True,'freeze_manifest':str(freeze_manifest),'freeze_manifest_sha256':sha(freeze_manifest),'frozen_file_count':len(rows),'pause_proof':str(pauseproof),'sol_snapshot':{'cursor':'2745552a-f142-41a1-8eaf-3fe7b2d500ca:19','status':'notLoaded','last_turn':'completed','new_final':False},'closure_changed':False,'new_qa_release':False,'new_a_dispatch':False}
write(proof,record)
print(json.dumps({'artifact_checks':len(checks),'hash_matches':all(c['matched'] for c in checks),'source_pdb':{k:len(v['documents']) for k,v in lineages.items()},'checkpoints':counts,'frozen_count':len(rows),'schema_errors':checker_result['evidence_errors'],'proof':str(proof),'pause':'PAUSED60MIN'},ensure_ascii=False))
