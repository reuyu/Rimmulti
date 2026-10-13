from pathlib import Path
import json,datetime,hashlib,tomllib,sys
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);ack=read(Q/'ACK.json');assert c['active_operation'] is None and ack['wp_id']==c['sol_current_wp'] and ack['delivery_id']==c['sol_current_attempt_id'] and ack['producer']=='Sol' and ack['wp_revision']=='S1'
assert ack['result_id']=='SOL-GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009-39d2285260ab486b85ea99cd8db0bffa'
snap=json.loads(read(C/'MASTER_SOL_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_ACK_SNAPSHOT_20261009.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='active' and snap['latestTurn']['status']=='inProgress' and snap['latestTurn']['id']=='01a120cd-940b-7561-8c58-454439174272'
base=Path(c['sol_current_delivery']['baseline_path']);b=read(base);assert len(b['files'])==7003
for f in b['files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
qa=read(Q/'R14_LINEAGE.json');master=read(C/'MASTER_GATE05_R14_POLICY_CAPTURE_PUBLICATION_E1_VERIFICATION_20261009.json')['lineage'];assert len(qa['candidates'])==2
for actual,expected in zip(qa['candidates'],master):
 assert actual['mvid']==expected['mvid'] and actual['dll_sha256']==expected['dll_sha256'] and actual['pdb_sha256']==expected['pdb_sha256'] and actual['guid']==actual['codeview_guid']==expected['codeviewGuid'];assert len(actual['documents'])==4
 for a,e in zip(actual['documents'],expected['documents']):assert a['pdb_hash']==e['expected']==sha(Path(a['frozen_source_path'])) and a['matched']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
proof={'at':at,'result_id':ack['result_id'],'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'ack_path':str(Q/'ACK.json'),'ack_sha256':sha(Q/'ACK.json'),'actual_snapshot':snap,'protected_paths_master_rehashed':7003,'baseline_sha256':sha(base),'qa_lineage_path':str(Q/'R14_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R14_LINEAGE.json'),'qa_pdb_sources_against_master_own_metadata':'Debug4/4,Release4/4','selected_sha256':master[0]['dll_sha256'],'selected_mvid':master[0]['mvid'],'verdict':'ACK_VERIFIED_INDEPENDENT_NORMAL_QA_IN_PROGRESS_EXECUTION_PENDING','guard_run':'MASTER-SOL-R14-INDEPENDENT-ACK-20261009-01','guard_session':99072,'guard_pid':23048,'automation':'ACTUAL_PAUSED60MIN','master_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
vp=C/'MASTER_SOL_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_ACK_VERIFICATION_20261009.json';assert not vp.exists();write(vp,proof)
c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,last_sol_cursor=snap['cursor'],updated_at=at);c['sol_last_ack']=proof;c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':99072,'guard_pid':23048,'at':at,'status':'R14_INDEPENDENT_ACK_VERIFIED_NO_DUPLICATE_NO_SCHEDULE_CHANGE','release_in_finally_follows':True};write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(current_result_id=ack['result_id'],ack_verified=True,explicit_ack_pending=False,execution_phase='IN_PROGRESS',last_runtime_observation_cursor=snap['cursor']);s['updated_at']=at
for d in s['deliveries']:
 if d.get('delivery_id')==ack['delivery_id']:d.update(status=proof['verdict'],ack_verified=True)
write(sp,s)
event=dict(proof,event_id=ack['delivery_id']+'-ACK_VERIFIED',type='SOL_R14_INDEPENDENT_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);assert not any(x.get('event_id')==event['event_id'] for x in r['processed_dispatch_events']);r['processed_dispatch_events'].append(event);r['updated_at']=at;write(rp,r)
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(event)+'\n')
para=f'\n\n## LOCAL-SOL-R14-INDEPENDENT-S1-ACK — {at}\nOriginalSol {ack["delivery_id"]}/{ack["result_id"]} identityACK matches actualactive01a120cd-940b-7561-8c58-454439174272/cursor{snap["revision"]}. Master7003protectedSHA-size rehashed,QA DebugReleasePDB/source4/4 each matched against ownMasterPE metadata/selected1A19...MVIDacab0270... . Normalexecutionverdict pending,no newWP/duplicate/schedulerchange/closure/fullGateE2. Valid lifecycle/standalone currentmatchingcore/purecodec only,newQAownrunnerbuild allowed;actualGetActualCompute/globalpublication/native/game/operator/old/stale/mismatch/rejection/race/adverse prohibited. Fingerprint pass-through/refusedpublish throw and Invalidate+1 statically credited;public parameterless manifest finalstamp/newpublic callerpolicy origin boundaries remainHighOPEN/staticonly. R14 oracle+1 must precede finalbuild/calls,oldPASS/rawzero-cachefooter notinherited. ActualCompute/GetActual/publiccallercollector/native/globalpublish prohibited;prospectiveoracle/build/normalexecution result still pending. SameactualhourlyPAUSED,directterminal reporting authorized,FoundationHOLD/openEngine002006/Pipeline007/currentschema/G-Q1. Proof {vp}\n'
for p in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'ack':'VERIFIED','protected':7003,'metadata_sources':'4/4 each','execution':'PENDING','duplicate':False,'schedule_change':False}))
