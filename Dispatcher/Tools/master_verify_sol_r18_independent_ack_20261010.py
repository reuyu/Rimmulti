from pathlib import Path
import json,datetime,hashlib,tomllib,sys,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def append(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
if len(sys.argv)>1 and sys.argv[1]=='released':
 rp=C/'MASTER_R18_ACK_GUARD_FINALLY_RELEASE_20261010.json';raw=read(rp)['actual_release_tool']
 assert raw['exit_code']==0 and '"status": "RELEASED"' in raw['output'] and '"run_id": "MASTER-SOL-R18-ACK-20261010-01"' in raw['output'] and re.search(r'id"\s*:\s*23172\b',raw['output'])
 released_at=re.search(r'"released_at"\s*:\s*"([^"]+)"',raw['output']).group(1)
 assert c['last_monitor_run']['run_id']=='MASTER-SOL-R18-ACK-20261010-01'
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=released_at,release_proof_path=str(rp),all_child_commands_completed_before_release=True);c['updated_at']=at;write(cp,c)
 append({'at':at,'event_id':'MASTER-SOL-R18-ACK-GUARD-RELEASE-20261010-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':c['last_monitor_run']['run_id'],'pid':23172,'proof':str(rp),'all_child_commands_completed_before_release':True})
 print('ACTUAL_ACK_GUARD_RELEASE_RECORDED_EXIT0');sys.exit(0)
delivery=c['sol_current_delivery'];Q=Path(delivery['qa_root']);ap=Q/'ACK_INITIAL.json';ack=read(ap)
assert ack['delivery_id']==c['sol_current_attempt_id']==delivery['delivery_id']
assert ack['wp_id']==c['sol_current_wp'] and ack['wp_revision']=='S1' and ack['producer']=='Sol' and ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp']
assert ack['result_id']=='SOL-GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010-be5a988c6f01410f88b5769c0c555322' and sha(ap)==sha(Q/'ACK.json')
assert ack['report_sha256'] is None and ack['evidence_manifest_sha256'] is None
sf=C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_ACK_SNAPSHOT_20261010.json';snap=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert snap['thread']['id']==c['sol_thread_id']=='01a11583-ff90-73e0-8916-d021e2bb038d' and snap['thread']['status']['type']=='active' and snap['latestTurn']['id']==delivery['actual_snapshot']['latestTurn']['id'] and snap['latestTurn']['status']=='inProgress'
assert sha(Path(delivery['wp_path']))==delivery['wp_sha256']=='3E86C2FB5C7D7AA4D20ECF0EA0937E9BA560D3A671C3AD3EF4C51D25ACF23B02'
base=Path(delivery['baseline_path']);assert sha(base)==delivery['baseline_sha256']=='2C84708033FC11481B6C1444DC1CF0341C1CE6CCDE390CD597E96A87FF545BAC';files=read(base)['files'];assert len(files)==9374
for f in files:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==9374 and before['baseline']['sha256']==sha(base)
assert {f['path']:(f['sha256'],f['bytes']) for f in before['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
masterproof=read(C/'MASTER_GATE05_R18_CONFIG_ADMISSION_SEAL_E1_VERIFICATION_20261010.json');master=masterproof['lineage'];line=read(Q/'R18_FROZEN_LINEAGE.json')
assert len(line['candidates'])==2 and not line['candidate_executed'] and not line['original_helper_top_level_executed']
for q in line['candidates']:
 m=next(x for x in master if x['mvid']==q['mvid'])
 assert q['dll_sha256']==m['dll_sha256'] and q['pdb_sha256']==m['pdb_sha256'] and q['guid']==q['codeview_guid']==m['pdbGuid']==m['codeviewGuid']
 assert len(q['documents'])==4
 for d in q['documents']:
  md=next(x for x in m['documents'] if x['path']==d['path']);p=Path(d['frozen_source_path']);assert d['matched'] and md['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(p)
fm=Path(masterproof['frozen_manifest']);assert sha(fm)==masterproof['frozen_manifest_sha256'] and len(read(fm)['files'])==92
# Reconcile already disposed A result and current production package without rerunning collector.
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert t['result_id']==masterproof['result_id'] and sha(Path(t['completion_path']))==masterproof['completion_sha256']
assert sum(x.get('result_id')==masterproof['result_id'] for x in receipts['processed_results'])==1
production_roles={'candidate_binary','pdb','alternate_binary','alternate_pdb','deployed_binary','deployed_pdb','source_worker','source_census','project'}
current=[]
for x in masterproof['artifact_checks']:
 if x['role'] in production_roles:
  q=Path(x['path']);assert sha(q)==x['sha256'] and q.stat().st_size==x['size'];current.append(x['role'])
assert len(current)==9
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
vp=C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_ACK_VERIFICATION_20261010.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-SOL-R18-ACK-20261010-01','guard_session':49585,'guard_pid':23172,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'ack_path':str(ap),'ack_sha256':sha(ap),'actual_snapshot':snap,'snapshot_path':str(sf),'snapshot_sha256':sha(sf),'protected_paths_master_rehashed':9374,'baseline_sha256':sha(base),'qa_lineage_path':str(Q/'R18_FROZEN_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R18_FROZEN_LINEAGE.json'),'master_metadata_comparison':'DebugReleaseSHA-MVID-CodeView-PDB-source4/4 matched','A_terminal_completion_deduped_unchanged':True,'current_production_package_identity_checked':9,'verdict':'ACK_VERIFIED_INDEPENDENT_R18_STATIC_POSITIVE_PURE_CONFIG_ADMISSION_QA_IN_PROGRESS','initial_ACK_execution_count_statement':'Historical initial ACK runner notbuilt;current QA execution verdict PENDING','qa_owned_runner_build_allowed':True,'master_candidate_build_execute':0,'new_wp':False,'runtime_e2_released':False,'closure_changed':False,'monitor_actual_status':'PAUSED60MIN173CHAR_SAME_TARGET','foundation':'HOLD'}
write(vp,proof)
c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,sol_last_ack=proof,last_sol_cursor=snap['cursor'],updated_at=at)
c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':49585,'guard_pid':23172,'at':at,'status':'R18_ACK_IDENTITY_SAME_ACTIVE_TURN_SCOPE_AND_PRESERVATION_VERIFIED_NO_NEW_WP','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R18_ACK_GUARD_FINALLY_RELEASE_20261010.json')};write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=snap['cursor']);s['updated_at']=at;write(sp,s)
e=dict(proof,event_id=ack['delivery_id']+'-ACK-VERIFIED',type='SOL_R18_INDEPENDENT_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp))
assert not any(x.get('event_id')==e['event_id'] for x in receipts['processed_dispatch_events'])
receipts['processed_dispatch_events'].append(e);receipts['updated_at']=at;write(R/'Dispatcher/MASTER_RECEIPTS.json',receipts);append(e)
para=f'\n\n## LOCAL-SOL-R18-INDEPENDENT-ACK — {at}\nOriginalSol {ack["delivery_id"]}/{ack["result_id"]} immutableinitialACK matchesactual sameactive turn{snap["latestTurn"]["id"]}/cursor{snap["revision"]}. Master rehashed9374 protectedpaths/frozen92/currentproduction9/Aterminalcompletiondedupe unchanged;QA DebugRelease SHA-MVID-CodeView/PDBsource4/4 comparedto independentMastermetadata matched. ACK_VERIFIED static+positivePUREconfigbyte-fileSHA/explicitdescriptor/detachedsnapshotfulltypedopaque stringownership QAinprogress;actualexecutionverdictPENDING(initialnotbuilt is historical),no inheritedE1PASS/newWP/duplicate/closure/schedulerchange. ALLC#Process/globalWorkerbootstrap-installer-ActiveStartup/native/game/adverse/productionmodifybuild0;externalhost onlynewQA-ownedpuremanagedrunnertelemetry allowed. SamehourlyPAUSED60min/directcompletionpush continues,automaticMasterdisposition afteractualterminal. Engine002006/Pipeline007/current schema/G-Q1OPEN/FoundationHOLD/fullGateE2NOTRELEASED. Proof {vp}\n'
for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with q.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'verdict':proof['verdict'],'protected':9374,'cursor':snap['revision'],'result_id':ack['result_id'],'new_wp':False},ensure_ascii=True))

