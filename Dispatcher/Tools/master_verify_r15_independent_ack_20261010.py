from pathlib import Path
import json,datetime,hashlib,tomllib,sys
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);ack=read(Q/'ACK_INITIAL.json');assert c['active_operation'] is None and ack['wp_id']==c['sol_current_wp'] and ack['delivery_id']==c['sol_current_attempt_id'] and ack['producer']=='Sol' and ack['wp_revision']=='S1'
assert ack['result_id']=='SOL-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010-7843e15c956b49ab83fd2c11f205f8b4'
snap=json.loads(read(C/'MASTER_SOL_R15_PUBLIC_MANIFEST_BOUNDARY_INDEPENDENT_ACK_SNAPSHOT_20261010.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='active' and snap['latestTurn']['status']=='inProgress' and snap['latestTurn']['id']=='01a121a2-fc67-73b2-8d9a-64ab6a15e2ca'
base=Path(c['sol_current_delivery']['baseline_path']);b=read(base);assert len(b['files'])==7994
for f in b['files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
qa=read(Q/'R15_LINEAGE.json');master=read(C/'MASTER_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_E1_VERIFICATION_20261010.json')['lineage'];assert len(qa['candidates'])==2
for actual,expected in zip(qa['candidates'],master):
 assert actual['mvid']==expected['mvid'] and actual['dll_sha256']==expected['dll_sha256'] and actual['pdb_sha256']==expected['pdb_sha256'] and actual['guid']==actual['codeview_guid']==expected['codeviewGuid'];assert len(actual['documents'])==4
 for a,e in zip(actual['documents'],expected['documents']):assert a['pdb_hash']==e['expected']==sha(Path(a['frozen_source_path'])) and a['matched']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
proof={'at':at,'result_id':ack['result_id'],'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'ack_path':str(Q/'ACK_INITIAL.json'),'ack_sha256':sha(Q/'ACK_INITIAL.json'),'actual_snapshot':snap,'protected_paths_master_rehashed':7994,'baseline_sha256':sha(base),'qa_lineage_path':str(Q/'R15_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R15_LINEAGE.json'),'qa_pdb_sources_against_master_own_metadata':'Debug4/4,Release4/4','selected_sha256':master[0]['dll_sha256'],'selected_mvid':master[0]['mvid'],'verdict':'ACK_VERIFIED_INDEPENDENT_NORMAL_QA_IN_PROGRESS_EXECUTION_PENDING','guard_run':'MASTER-SOL-R15-INDEPENDENT-ACK-20261010-01','guard_session':13508,'guard_pid':30484,'automation':'ACTUAL_PAUSED60MIN','master_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp=C/'MASTER_SOL_R15_PUBLIC_MANIFEST_BOUNDARY_INDEPENDENT_ACK_VERIFICATION_20261010.json';assert not vp.exists();write(vp,proof)
c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,last_sol_cursor=snap['cursor'],updated_at=at);c['sol_last_ack']=proof;c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':13508,'guard_pid':30484,'at':at,'status':'R15_INDEPENDENT_ACK_VERIFIED_NO_DUPLICATE_NO_SCHEDULE_CHANGE','release_in_finally_follows':True};write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(current_result_id=ack['result_id'],ack_verified=True,explicit_ack_pending=False,execution_phase='IN_PROGRESS',last_runtime_observation_cursor=snap['cursor']);s['updated_at']=at
for d in s['deliveries']:
 if d.get('delivery_id')==ack['delivery_id']:d.update(status=proof['verdict'],ack_verified=True)
write(sp,s)
event=dict(proof,event_id=ack['delivery_id']+'-ACK_VERIFIED',type='SOL_R15_INDEPENDENT_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);assert not any(x.get('event_id')==event['event_id'] for x in r['processed_dispatch_events']);r['processed_dispatch_events'].append(event);r['updated_at']=at;write(rp,r)
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(event)+'\n')
para=f'\n\n## LOCAL-SOL-R15-INDEPENDENT-S1-ACK — {at}\nOriginalSol {ack["delivery_id"]}/{ack["result_id"]} immutableACK_INITIAL matches sameactualactive turn{snap["latestTurn"]["id"]}/cursor{snap["revision"]}.7994protected paths Masterrehashed/QA DebugReleaseMVID-PDBsource4/4 comparedtoownMastermetadata/exactDebug835E...MVID4fb1a25f.../93freezeSHA951F31... . ACKreportsprospectiveoracle/newQA runnerbuild-calls notyetperformed atACKtime;currentexecutionverdictPENDING,not assertedcurrentallcalls0. BothnormalCURRENTmatchingpublicationoverloads/outcarrier/fulltypedownership/purecodec/emptyglobal lifecycle only. NewR15header/+1/APIoracle beforefinalbuildcalls required;publicprivatecollector/sharedcompute-success routes staticallycredited andreviewed source-only. Production/globalactualCompute/GetActual/privatecollector/globalpublish/seed/errorinjection/stale/mismatch/rejection/race/adverse/native/game/operator/producerTC16 replay notadmitted. InitialACKpendingterminalhash retained;no newWP/duplicate/schedulerchange/fullGateE2/closure. SameactualhourlyPAUSED/directterminalpushauthorized,FoundationHOLD/openEngine002006/Pipeline007/currentschema/G-Q1. Proof{vp}\n'
for p in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'ack':'VERIFIED','protected':7994,'metadata_sources':'4/4 each','execution':'PENDING','duplicate':False,'schedule_change':False}))
