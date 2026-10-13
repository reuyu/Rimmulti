from pathlib import Path
import json,hashlib,datetime,tomllib,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R27-S2-QA-ACK-20261012-01';PID=28408;SESSION=45341
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
if len(sys.argv)>1 and sys.argv[1]=='released':
 p=C/'MASTER_R27_S2_ACK_GUARD_FINALLY_RELEASE_20261012.json';raw=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert raw['exit_code']==0 and info['status']=='RELEASED' and info['run_id']==RUN and info['pid']==PID
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':RUN+'-RELEASE','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','proof':str(p)});print('ACTUAL_GUARD_RELEASE_RECORDED');sys.exit(0)
d=c['sol_current_delivery'];Q=Path(d['qa_root']);ap=Q/'ACK_INITIAL.json';a=read(ap)
assert all(a[k]==d[k] for k in ['delivery_id','wp_id','wp_revision','selected_sha256','selected_mvid']) and a['status']=='ACKNOWLEDGED_IN_PROGRESS'
assert a['result_id']=='SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012-bff0acad007f4167b974eb7496240425' and sha(ap)=='302FF07EB60199FD7CF80EA20CB2342B64E0D1BD4157EBF9FFAC8B7BB035C3FF' and sha(Q/'ACK.json')==sha(ap)
sf=C/'MASTER_SOL_R27_CHILD_CAPTURE_INDEPENDENT_S2_ACK_SNAPSHOT_20261012.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
for k in ['wp','baseline']:assert sha(Path(d[k+'_path']))==d[k+'_sha256']
assert sha(Path(d['frozen_manifest']))==d['frozen_manifest_sha256']
cor=d['supplemental_report_identity_correction'];assert sha(Path(cor['path']))==cor['sha256'] and a['report_path']==d['new_report_path']
loader=read(Path(d['loader_admission']['path']))['admitted_frozen_loader_reference'];assert sha(Path(loader['path']))==loader['sha256']=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D' and Path(loader['path']).stat().st_size==711952 and loader['mvid']=='dd21e087-47d9-4bce-bed8-b56112226337'

files=read(Path(d['baseline_path']))['files'];assert len(files)==13674
for f in files:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==13674 and {f['path']:(f['sha256'],f['bytes']) for f in before['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
v=read(C/'MASTER_GATE05_R27_CHILD_CAPTURE_E1_VERIFICATION_20261012.json');assert a['selected_mvid']==v['selected_mvid'] and all(pe['codeviewMatched'] and all(z['matched'] for z in pe['documents']) for pe in v['Debug_Release_PE_PDB'])
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];assert t['status']=='COMPLETED_REVIEWED_SOURCE_CAPTURE_CREDITED_SCOPED_QA_PENDING'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
pp=C/'MASTER_R27_S2_ACK_CURRENT_PRESERVATION_20261012.json';assert not pp.exists();write(pp,pres)
vp=C/'MASTER_SOL_R27_CHILD_CAPTURE_INDEPENDENT_S2_ACK_VERIFICATION_20261012.json';assert not vp.exists()
proof={'at':at,'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION,'delivery_id':a['delivery_id'],'wp_id':a['wp_id'],'wp_revision':'S2','result_id':a['result_id'],'initial_ACK':row(ap),'actual_snapshot':sn,'snapshot':row(sf),'WP':row(Path(d['wp_path'])),'baseline':row(Path(d['baseline_path'])),'protected_paths_Master_rehashed':13674,'frozen_files':83,'currentProduction9_matched':True,'selected_sha256':a['selected_sha256'],'selected_mvid':a['selected_mvid'],'matching_pdb_sha256':v['selected_pdb_sha256'],'Master_prior_independent_PE_CodeView_PDB_source4of4_bound_by_current_SHA':True,'ACK_initial_execution0':'Historical ACK moment only; current execution verdict PENDING','verdict':'ACK_VERIFIED_R27_FRESH_EXACT_NORMAL_PURE_CAPTURE_QA_IN_PROGRESS','admitted_QA_owned_final_builds':1,'admitted_normal_culture_runs':2,'normal_primary_direct_calls_per_run':'factory8 IsValid8 Capture4; full15getters/alltypedrawownership','new_WP':False,'production_candidate_modify_rebuild':0,'full_native_e2_released':False,'closure_changed':False,'scheduler_actual':cfg,'foundation':'HOLD'}
proof.update(corrected_loader_admission=d['loader_admission'],new_S2_report=d['new_report_path'],supplemental_output_identity_correction=cor,S1_stop_raw_preserved=True);write(vp,proof);c.update(sol_status=proof['verdict'],sol_current_result_id=a['result_id'],sol_current_ack=proof,sol_last_ack=proof,last_sol_cursor=sn['cursor'],updated_at=at);c['last_monitor_run']={'run_id':RUN,'guard_pid':PID,'guard_session':SESSION,'at':at,'status':'R27_FRESH_SOL_ACK_SAME_ACTIVE_TURN_IDENTITY_PROTECTED_MATCHED','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
sp=H/'DISPATCHER_STATE.json';st=read(sp);st['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=a['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=sn['cursor']);st['updated_at']=at;write(sp,st)
e=dict(proof,event_id=a['delivery_id']+'-ACK-VERIFIED',type='SOL_R27_FRESH_EXACT_NORMAL_QA_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr);event(e)
para=f'\n\n## LOCAL-SOL-R27-S2-CORRECTED-LOADER-EXACT-CAPTURE-QA-ACK — {at}\nOriginalSol{a["delivery_id"]}/{a["result_id"]}/immutableinitialACK matchedactualsameactive turn{sn["latestTurn"]["id"]}/cursor{sn["revision"]}. Master13674protected/newfrozen83/currentproduction9SHA-size matched/selected68BFE510...MVID44ba753c-6570-49d8-8068-4edf87a4e5d0/PDBF0BC.../MasterownbothmodePE-CodeView-PDBsource4of4bound. NewQAfinalbuild1/twofreshnormalruns/factory8IsValid8Capture4/full15typedraw-allownership admitted; executionverdictPENDING/no inheritedproducerPASS/oldpreparationnotPASS. Productionmodifyrebuild/global-native-Process-registration-readonlymutation-exception-adverse0;no newWP/duplicate/closure/schedulerchange. SameactualhourlyPAUSED60min173charcorrecttarget/directSolcompletionpush;Aterminalreviewed/nextA noneNOT_SENTpendingQA/fullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'verdict':proof['verdict'],'protected':13674,'cursor':sn['revision'],'newWP':False,'scheduler':'PAUSED60MIN'}))
