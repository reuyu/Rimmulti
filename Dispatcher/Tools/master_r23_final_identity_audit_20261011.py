from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['completion_path']).parent;v=read(C/'MASTER_GATE05_R23_IDENTIFIER_MAPPING_E1_VERIFICATION_20261011.json')
assert c['active_operation'] is None and c['sol_current_wp']=='WP_QA_ENGINE_GATE05_R23_IDENTIFIER_MAPPING_INDEPENDENT'
fm=Path(v['frozen_manifest']);assert sha(fm)==v['frozen_manifest_sha256'];manifest=read(fm)
for f in manifest['files']:
 p=Path(f['frozen_path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['size']
runnerbase=R/'Dispatcher/CANDIDATES/G05R23-31bd3af2/scratch/EngineGate05R23IdentifierMapping/Harness/bin/Debug/net472'
assert sha(runnerbase/'WarEconomy.WorkerBridge.PoC.dll')==v['selected_sha256'] and sha(runnerbase/'WarEconomy.WorkerBridge.PoC.pdb')==v['selected_pdb_sha256']
after=read(T/'ENGINE_FREEZE_AFTER.json')
for f in after if isinstance(after,list) else after['files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['size']
msg=C/'MASTER_SOL_R23_IDENTIFIER_MAPPING_INDEPENDENT_EXACT_MESSAGE_20261011.txt';snapshot=read(C/'MASTER_R23_QA_CURRENT_PROGRESS_SNAPSHOT_20261011.json');sn=json.loads(snapshot['content'][0]['text'])['polls'][0]
assert sn['thread']['status']['type']=='active' and sn['latestTurn']['id']==c['sol_current_delivery']['actual_snapshot']['latestTurn']['id']
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();dest=C/'MASTER_R23_FINAL_IDENTITY_COORDINATION_AUDIT_20261011.json';assert not dest.exists()
proof={'at':at,'run_id':'MASTER-HEARTBEAT-R23-20261011T085442Z-01','guard_session':49350,'guard_pid':19228,'frozen_files_rehashed':len(manifest['files']),'current_after_paths_rehashed':9,'producer_runner_actual_DLL_PDB_matched_selected':True,'actual_loaded_candidate_MVID_identity_basis':'Master independent PE metadata for identical selected DLL bytes;producer loaded module observation separately reported','Sol_actual':sn,'Sol_ACK':'FORMAL_IDENTITY_ACK_PENDING;actual_commentary_started','exact_message_path':str(msg),'exact_message_file_sha256':sha(msg),'exact_sent_text_convention':'file final LF excluded;remaining text equals actual submitted prompt','exact_submitted_text_sha256':hashlib.sha256(msg.read_text(encoding='utf8').removesuffix('\n').encode('utf8')).hexdigest().upper(),'scheduler_actual_status':'PAUSED60MIN','next_A':'NOT_SENT_PENDING_QA','master_candidate_build_execute':0,'full_runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','preparation_qualification':'Initialgenerator substring failure wrote0;initialunsentbaseline retainedR21insteadR22 detectedbeforeanydelivery;initialWP-baselinepreserved/newadditive12350baseline+correctedunsentWPactualdelivered/protectedQAoriginalsuntouched','guard_finally_release':'PENDING_ACTUAL'}
write(dest,proof);c['sol_last_observation'].update(final_identity_audit=str(dest),actual_started_commentary_verified=True);c['updated_at']=at;write(cp,c)
e={'at':at,'event_id':'MASTER-R23-FINAL-IDENTITY-20261011-01','type':'R23_EXACT_IDENTITY_SOL_ACTUAL_STARTED_AUDIT','proof':str(dest),'proof_sha256':sha(dest),'exact_message_path':str(msg),'exact_message_sha256':sha(msg)}
for q in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with q.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
print(json.dumps({'freeze':len(manifest['files']),'current_after':9,'runner_candidate_copy':'MATCHED','Sol':'ACTIVE_ORIGINAL_NEW_TURN145','formal_ACK':'PENDING','native':'UNTESTED'}))
