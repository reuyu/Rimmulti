from pathlib import Path
import json,datetime,hashlib,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None;Q=R/'QA-Tactical-Engine/GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010';ap=Q/'ACK_INITIAL.json';ack=read(ap);delivery=c['sol_current_delivery']
assert ack['delivery_id']==c['sol_current_attempt_id']==delivery['delivery_id'] and ack['wp_id']==c['sol_current_wp'] and ack['wp_revision']=='S1' and ack['producer']=='Sol' and ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp']
assert ack['result_id']=='SOL-GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010-d7c1c37a89a14eadb400986441ce198d'
sf=C/'MASTER_SOL_R16_OPERATOR_NATIVE_PREPARATION_ACK_SNAPSHOT_20261010.json';snap=json.loads(read(sf)['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='active' and snap['latestTurn']['id']==delivery['actual_snapshot']['latestTurn']['id'] and snap['latestTurn']['status']=='inProgress'
base=Path(delivery['baseline_path']);assert sha(base)==delivery['baseline_sha256'];files=read(base)['files'];assert len(files)==8932
for f in files:p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==8932 and before['baseline']['sha256']==sha(base)
assert {f['path']:(f['sha256'],f['bytes']) for f in before['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
line=read(Q/'R16_FROZEN_LINEAGE.json');master=read(C/'MASTER_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_E1_VERIFICATION_20261010.json')['lineage'];assert len(line['candidates'])==2 and not line['candidate_executed'] and not line['original_helper_top_level_executed']
for q in line['candidates']:
 m=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==m['dll_sha256'] and q['pdb_sha256']==m['pdb_sha256'] and q['guid']==q['codeview_guid']==m['pdbGuid']==m['codeviewGuid']
 assert len(q['documents'])==4
 for d in q['documents']:
  md=next(x for x in m['documents'] if x['path']==d['path']);p=Path(d['frozen_source_path']);assert d['matched'] and md['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(p)
vp=C/'MASTER_SOL_R16_OPERATOR_NATIVE_PREPARATION_ACK_VERIFICATION_20261010.json';assert not vp.exists();proof={'at':at,'guard_run':'MASTER-SOL-R16-PREP-ACK-20261010-01','guard_session':48395,'guard_pid':17140,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'ack_path':str(ap),'ack_sha256':sha(ap),'actual_snapshot':snap,'protected_paths_master_rehashed':8932,'qa_lineage_path':str(Q/'R16_FROZEN_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R16_FROZEN_LINEAGE.json'),'master_metadata_comparison':'DebugReleaseSHA-MVID-CodeView-PDB-source4/4 matched','verdict':'ACK_VERIFIED_INDEPENDENT_READ_ONLY_R16_PREPARATION_IN_PROGRESS_NO_NATIVE_VERDICT','production_runner_build_load_execute_permissions':0,'runtime_e2_released':False,'closure_changed':False,'monitor':'SAME_HOURLY_ACTIVE_A_SEPARATE_READ_ONLY_PREPARATION','foundation':'HOLD'};write(vp,proof)
c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,last_sol_cursor=snap['cursor'],updated_at=at);c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':48395,'guard_pid':17140,'at':at,'status':'R16_PREPARATION_ACK_IDENTITY_AND_SCOPE_VERIFIED_NO_NEW_WP','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R16_ACK_GUARD_FINALLY_RELEASE_20261010.json')};write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=snap['cursor']);s['updated_at']=at;write(sp,s)
e=dict(proof,event_id=ack['delivery_id']+'-ACK-VERIFIED',type='SOL_R16_PREPARATION_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr)
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e)+'\n')
para=f'\n\n## LOCAL-SOL-R16-PREPARATION-ACK — {at}\nOriginalSol {ack["delivery_id"]}/{ack["result_id"]} initialACK matches actualsameactive turn{snap["latestTurn"]["id"]}/cursor{snap["revision"]}.8932 protectedSHA-size Masterrehashed;QA DebugRelease frozenSHA-MVID-CodeView/PDBsource4/4 comparedtoMasterownR15metadata matched. ACK_VERIFIED independentread-only operator/context/native readiness QApreparation inprogress;no newnative executionverdict/newWP/duplicate/closure/schedulerchange. A R16separate readonlySENT/ACKverified,all9Enginefixed. SamehourlyACTIVE,Engine002006/Pipeline007/current schema/G-Q1OPEN/FoundationHOLD. Proof {vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'verdict':proof['verdict'],'protected':8932,'cursor':snap['revision'],'result_id':ack['result_id'],'new_wp':False},ensure_ascii=True))
