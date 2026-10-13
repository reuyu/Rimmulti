from pathlib import Path
import json,hashlib,datetime,tomllib,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
if len(sys.argv)>1 and sys.argv[1]=='released':
 p=C/'MASTER_R24_ACK_GUARD_FINALLY_RELEASE_20261011.json';rr=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert rr['exit_code']==0 and info['status']=='RELEASED' and info['run_id']=='MASTER-SOL-R24-ACK-20261011-01' and info['pid']==13224
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],release_proof_path=str(p),all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':'MASTER-R24-ACK-GUARD-RELEASE-20261011-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':info['run_id'],'pid':13224,'proof':str(p)});print('ACTUAL_ACK_GUARD_RELEASE_RECORDED');sys.exit(0)
d=c['sol_current_delivery'];Q=Path(d['qa_root']);ack=read(Q/'ACK_INITIAL.json');assert ack['delivery_id']==c['sol_current_attempt_id']==d['delivery_id']=='SOL-GATE05-R24-M04-PREPARATION-S1-20261011-01'
assert ack['result_id']=='SOL-GATE05-R24-M04-PREPARATION-S1-20261011-eb71f49825a7400699a8b23188e5db28' and ack['wp_id']==c['sol_current_wp']==d['wp_id'] and ack['wp_revision']=='S1' and ack['producer']=='Sol' and ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp']
assert ack['report_sha256'] is None and ack['evidence_manifest_sha256'] is None and sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')
assert sha(Path(d['wp_path']))==d['wp_sha256'];base=Path(d['baseline_path']);assert sha(base)==d['baseline_sha256']=='F02B2EA7360767393EBE679638FFDC548E43BC500B4B2EA0702E91BD50C88050'
files=read(base)['files'];assert len(files)==13002
for f in files:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==13002 and before['baseline']['sha256']==sha(base) and before['files']==files
sf=C/'MASTER_SOL_R24_M04_PREPARATION_ACK_SNAPSHOT_20261011.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0];assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];assert t['wp_id']=='WP_ENGINE_GATE05_R24_ROLE_LAUNCH_CONTRACT_PREPARATION' and t['delivery_status']=='SENT' and not t['unknown_delivery'] and t['submission_attempts']==1
for f in t['production_fixed_files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
assert not Path(t['completion_path']).exists(),'NEW_A_TERMINAL_REQUIRES_COLLECTION_BEFORE_ROUTINE_ACK_CLOSE'
proof={'at':at,'guard_run':'MASTER-SOL-R24-ACK-20261011-01','guard_session':55488,'guard_pid':13224,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'result_id':ack['result_id'],'ack_path':str(Q/'ACK_INITIAL.json'),'ack_sha256':sha(Q/'ACK_INITIAL.json'),'actual_snapshot':sn,'snapshot_path':str(sf),'snapshot_sha256':sha(sf),'protected_paths_master_rehashed':13002,'baseline_sha256':sha(base),'current_all9fixed':True,'A_current_same_readonly_wp_in_progress_no_completion':True,'knowninstalled':'UNCHANGED_OPEN_ACTOR_CAUSE_UNKNOWN','verdict':'ACK_VERIFIED_R24_INDEPENDENT_READ_ONLY_M04_PREPARATION_IN_PROGRESS','production_candidate_and_QA_runner_build_load_execute_permission':0,'new_wp':False,'monitor':'ACTUAL_ACTIVE_HOURLY173CHAR_SAME_TARGET','R23_targeted_closure':'RETAINED_SOURCE_NORMAL_FACTORY_SCOPED_ONLY','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp=C/'MASTER_SOL_R24_M04_PREPARATION_ACK_VERIFICATION_20261011.json';assert not vp.exists();write(vp,proof)
c.update(sol_current_ack=proof,sol_last_ack=proof,sol_current_result_id=ack['result_id'],sol_status=proof['verdict'],last_sol_cursor=sn['cursor'],updated_at=at);c['last_monitor_run']={'run_id':proof['guard_run'],'guard_pid':13224,'guard_session':55488,'at':at,'status':'R24_READ_ONLY_ACK_ACTIVE_TURN_BASELINE_ALL9_VERIFIED_NO_DUPLICATE','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=sn['cursor']);write(sp,s)
rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);e=dict(proof,event_id=ack['delivery_id']+'-ACK-VERIFIED',type='SOL_R24_READ_ONLY_M04_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));assert not any(x.get('event_id')==e['event_id'] for x in r['processed_dispatch_events']);r['processed_dispatch_events'].append(e);write(rp,r);event(e)
para=f'\n\n## LOCAL-SOL-R24-M04-PREPARATION-ACK — {at}\nOriginalSol{ack["delivery_id"]}/{ack["result_id"]} immutableinitialACK matchesactualactive{sn["latestTurn"]["id"]}/cursor{sn["revision"]}. Master rehashed13002baseline+all9currentEngine fixed;A sameR24READ_ONLYactualSENT/ACK/currentnoCOMPLETION/no duplicate. IndependentM04source-roleuserdata/frontend-ownedlaunchcontract preparation only/QAproductionbuild-load-execute-native-game-Process-assetscopy-adverse0. ExistinghourlyactualACTIVE60min173charcorrecttarget unchanged. R23 declaredtrim source/normalfactory scopedCLOSED retained/nativeCLI-M04..07-wholeEnginePipelineGQ1OPEN/FoundationHOLD/runtimeE2NOTRELEASED/no newclosure. Proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print('R24_ACK_13002PROTECTED_ALL9_MATCHED_SAME_ACTIVE_TURN_NO_DUPLICATE')
