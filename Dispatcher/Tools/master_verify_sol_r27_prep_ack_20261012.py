from pathlib import Path
import json,hashlib,datetime,tomllib,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R27-QA-ACK-20261012-01';PID=22116;SESSION=11510
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
if len(sys.argv)>1 and sys.argv[1]=='released':
 p=C/'MASTER_R27_ACK_GUARD_FINALLY_RELEASE_20261012.json';raw=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert raw['exit_code']==0 and info['status']=='RELEASED' and info['run_id']==RUN and info['pid']==PID
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':RUN+'-RELEASE','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':RUN,'pid':PID,'proof':str(p)});print('ACK_GUARD_RELEASE_RECORDED');sys.exit(0)
d=c['sol_current_delivery'];Q=Path(d['qa_root']);ap=Q/'ACK_INITIAL.json';ack=read(ap);assert all(ack[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and ack['status']=='ACKNOWLEDGED_INDEPENDENT_READ_ONLY_PREPARATION' and ack['result_id']=='SOL-GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011-bc67d273756f4bda89475a4fcf4d6da9'
assert sha(ap)=='0541BCCE562AE35FD3E9F57A0094967B42CCBFF064DC77522D13B2E27785A09B' and sha(Q/'ACK.json')==sha(ap) and ack['protected_paths']==13458
sf=C/'MASTER_SOL_R27_CHILD_CAPTURE_PREPARATION_ACK_SNAPSHOT_20261012.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0];assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
for k in ['wp','api_correction']:
 f=ack[k];p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
assert sha(Path(d['wp_path']))==d['wp_sha256']==ack['wp']['sha256'];base=Path(d['baseline_path']);assert sha(base)==d['baseline_sha256'];files=read(base)['files'];assert len(files)==13458
for f in files:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==13458 and {f['path']:(f['sha256'],f['bytes']) for f in before['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];assert t['dispatch_id'].endswith('cdc223f3') and t['delivery_status']=='SENT' and not t['unknown_delivery'];assert len(t['production_fixed_files'])==2
excluded={str(Path(p).resolve()).lower() for p in t['allowed_mutable_paths']};assert len(excluded)==7 and not any(str(Path(f['path']).resolve()).lower() in excluded for f in files)
for f in t['production_fixed_files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
prespath=C/'MASTER_R27_ACK_A_CURRENT_PRESERVATION_20261012.json';assert not prespath.exists();write(prespath,pres)
write(C/'MASTER_R27_ACK_METADATA_SCHEMA_RECONCILIATION_20261012.json',{'at':at,'Master_collector_original_error':'KeyError protected_files copied from R26 schema; R27 actual PRESERVATION_BEFORE uses files','correction':'Read actual files schema; original QA evidence unchanged; new verifier only','candidate_QA_reexecution':0,'baseline_actual_rehashed':13458,'preservation':row(prespath)})
vp=C/'MASTER_SOL_R27_CHILD_CAPTURE_PREPARATION_ACK_VERIFICATION_20261012.json';assert not vp.exists()
proof={'at':at,'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'initial_ACK':row(ap),'actual_snapshot':sn,'snapshot':row(sf),'WP':row(Path(d['wp_path'])),'api_correction':ack['api_correction'],'baseline':row(base),'protected_paths_master_rehashed':13458,'current_fixed_Census_csproj_matched':True,'current_mutable7_not_read_and_excluded':True,'historical_R25_lineage':'Frozen99 hash bound; Master prior verified PE/MVID/PDB source4of4, Sol fresh metadata assertion is QA evidence not new R27 identity','A_actualSent_ack_verified':t.get('ack_verified',False),'A_completion_exists_now':Path(t['completion_path']).exists(),'scope':'FROZEN_READONLY_PREPARATION_FUTURE_CAPTURE15_NORMAL4_NO_EXECUTION','verdict':'ACK_VERIFIED_R27_INDEPENDENT_READONLY_CAPTURE_PREPARATION_IN_PROGRESS','execution_verdict':'NOT_APPLICABLE_READONLY_PREPARATION_RESULT_PENDING','production_candidate_and_QA_build_execute':0,'no_mutable_read_statement':'QA_DECLARED_SCOPE_NOT_OS_ACCESS_TRACE','new_WP':False,'scheduler_actual':cfg,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'};write(vp,proof)
c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,sol_last_ack=proof,last_sol_cursor=sn['cursor'],updated_at=at);c['last_monitor_run']={'run_id':RUN,'guard_pid':PID,'guard_session':SESSION,'at':at,'status':'R27_ORIGINALSOL_ACK_SAME_ACTIVE_TURN_IDENTITY_PROTECTED_MATCHED','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R27_ACK_GUARD_FINALLY_RELEASE_20261012.json')};write(cp,c)
sp=H/'DISPATCHER_STATE.json';st=read(sp);st['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=sn['cursor']);st['updated_at']=at;write(sp,st)
e=dict(proof,event_id=ack['delivery_id']+'-ACK-VERIFIED',type='SOL_R27_PREPARATION_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr);event(e)
para=f'\n\n## LOCAL-SOL-R27-CAPTURE-PREPARATION-ACK — {at}\nOriginalSol {ack["delivery_id"]}/{ack["result_id"]}/immutable initial ACK matches actual same active turn {sn["latestTurn"]["id"]}/cursor{sn["revision"]}; Master13458protected/current fixed Census+csproj matched/exactmutable7 excluded-unread. R27independent READ_ONLY frozenR25/R26 + Master15getter/sourceactual lowercase descriptor7 order vs option-values/task27/copy/prospective4normalpair/provenance only; resultPENDING/execution0/notPASS. A same R27PURECapture singlewriter SENT/ACKverified; no duplicate WP/schedulerchange. SameactualhourlyACTIVE60min173charcorrecttarget/directSolpush; oldR25S2scopedPASS andS1rawFAILpreserved/fullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'verdict':proof['verdict'],'protected':13458,'cursor':sn['revision'],'new_wp':False,'A_completion':proof['A_completion_exists_now']}))
