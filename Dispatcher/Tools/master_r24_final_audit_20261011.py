from pathlib import Path
import json,hashlib,datetime,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];r=read(R/'Dispatcher/MASTER_RECEIPTS.json');v=read(C/'MASTER_SOL_R23_IDENTIFIER_MAPPING_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json')
assert c['active_operation'] is None and v['verification_status']=='MASTER_DISPOSED'
assert sum(x.get('result_id')==v['result_id'] for x in r['processed_results'])==1
assert sum(x.get('event_id')==t['dispatch_id']+'-SENT-HOURLY-ACTIVE' for x in r['processed_dispatch_events'])==1
assert sum(x.get('event_id')==c['sol_current_attempt_id']+'-ACTUAL_SENT' for x in r['processed_dispatch_events'])==1
assert t['delivery_status']=='SENT' and not t['unknown_delivery'] and t['submission_attempts']==1 and t['ack_verified']
for key in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[key+'_path']))==t[key+'_sha256']
for key in ['wp','baseline']:assert sha(Path(c['sol_current_delivery'][key+'_path']))==c['sol_current_delivery'][key+'_sha256']
protected=read(Path(c['sol_current_delivery']['baseline_path']))['files'];assert len(protected)==13002
for f in protected+t['production_fixed_files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size')),str(p)
ack=read(Path(t['ack_path']));assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack['envelope']==27 and ack['task_state']=='IN_PROGRESS' and sha(Path(t['ack_path']))==t['ack_sha256']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
snpath=C/'MASTER_R24_DUAL_CURRENT_SOL_SNAPSHOT_20261011.json';sn=json.loads(read(snpath)['content'][0]['text'])['polls'][0];assert sn['latestTurn']['id']==c['sol_current_delivery']['actual_snapshot']['latestTurn']['id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress'
dp=C/'MASTER_DEFECT_ENGINE_G05_DECLARATION_TRIM_R22_20261011.json';d=read(dp);assert d['status']=='CLOSED_SCOPED_SOURCE_AND_NORMAL_FACTORY_REGRESSION' and not d['full_gate_e2_released']
vp=C/'MASTER_R23_COMPLETE_R24_DUAL_SENT_FINAL_AUDIT_20261011.json';assert not vp.exists();write(vp,{'at':at,'guard_run':'MASTER-SOL-R23-COMPLETE-20261011-01','guard_pid':34628,'guard_session':34592,'R23_result_dedupe_count':1,'R24_A_delivery_dedupe_count':1,'R24_Sol_delivery_dedupe_count':1,'A_actual_sent_and_ack':True,'A_ack_hash':sha(Path(t['ack_path'])),'A_ack_declared_timestamp':ack['acknowledged_at'],'timestamp_qualification':'Producer supplied time is not Master observed delivery or execution time','Sol_actual':sn,'protected_unique_paths_master_rehashed':13002,'current_all9_engine_unchanged':True,'monitor_actual_config':cfg,'future_R24_scheduled_run_observed':False,'R23_closure':'CLOSED_SCOPED_SOURCE_AND_NORMAL_FACTORY_REGRESSION_ONLY','runtime_e2_released':False,'next_action':'Collect exact independent A/Sol M04 contracts,Master reconcile,approve bounded connected implementation automatically;no duplicated dispatch','foundation':'HOLD','known_installed_incident':'OPEN_ACTOR_CAUSE_UNKNOWN_NO_RESTORE','guard_finally_release':'PENDING'})
c.update(last_sol_cursor=sn['cursor'],sol_last_observation={'at':at,'path':str(snpath),'actual_snapshot':sn},updated_at=at);c['last_monitor_run'].update(status='R23_DISPOSED_SCOPED_CLOSED_R24_A_AND_SOL_SENT_HOURLY_ACTIVE_FINAL_AUDIT_MATCHED');write(cp,c)
pointer=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';pointer.write_text(f'Current{at}: R23 freshindependent297PASS0FAIL each/646evidence12350protected/12456typed92bindings accepted;declarationTrim defect CLOSED_SCOPED_SOURCE_NORMAL_FACTORY exactR23ONLY/nativeCLI-operatorOPEN. A{t["dispatch_id"]} actualSENT/ACKverified READ_ONLY M04 roleuserdata/frontend/launchcontract,ALL9fixed. OriginalSol{c["sol_current_attempt_id"]} actualdirectSENT/newactive{sn["latestTurn"]["id"]}/cursor{sn["revision"]}/independentREAD_ONLY/13002protected. SamehourlyactualACTIVE60min173charcorrecttarget. Collect bothoriginalreports/proposals/prerequisites→Master currentfacts reconciliation→exactboundedimplementation next automatically;no routinehumancontinue/duplicate. FullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Audit{vp}\n\n'+pointer.read_text(encoding='utf-8-sig'),encoding='utf8')
e={'at':at,'event_id':t['dispatch_id']+'-FINAL-DUAL-AUDIT','type':'R23_SCOPED_CLOSED_R24_DUAL_READONLY_SENT_HOURLY_ACTIVE','proof':str(vp),'proof_sha256':sha(vp)}
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
print(json.dumps({'protected':13002,'ALL9':'MATCHED','A':'SENT_ACK_VERIFIED','Sol':'ACTUAL_ACTIVE','monitor':'ACTIVE_HOURLY','closure':'R23_SOURCE_NORMAL_FACTORY_SCOPED_ONLY','native':'UNTESTED'},ensure_ascii=True))
