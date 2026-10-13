from pathlib import Path
import json, hashlib, datetime, tomllib

R=Path(__file__).resolve().parents[2]
H=R/'docs/WarEconomy_Master_Handoff_20261006'
Q=R/'QA-Tactical-Engine/GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(d):
 if isinstance(d,dict):
  if 'path' in d and 'sha256' in d and Path(d['path']).is_absolute(): yield d
  if 'manifest' in d and 'manifest_sha256' in d: yield {'path':d['manifest'],'sha256':d['manifest_sha256']}
  for v in d.values(): yield from rows(v)
 elif isinstance(d,list):
  for v in d: yield from rows(v)

at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);ack=read(Q/'ACK.json')
delivery='SOL-GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009-01'
wp='WP_QA_ENGINE_GATE05_R10_PACKAGE_POLICY_INDEPENDENT'
event_id=delivery+'-ACK-MASTER-01'
rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp)
assert not any(x.get('event_id')==event_id for x in receipts['processed_dispatch_events']), 'already collected'
assert comm['active_operation'] is None
assert ack['delivery_id']==comm['sol_current_attempt_id']==delivery
assert ack['wp_id']==comm['sol_current_wp']==wp and ack['wp_revision']=='S1'
assert ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp']
assert ack['result_id']=='SOL-GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009-c0cfd1b859084a538e9866c78fde8635'
sp=H/'coordination/MASTER_SOL_R10_PACKAGE_POLICY_INDEPENDENT_S1_ACK_SNAPSHOT_20261009.json'
poll=read(sp)['polls'][0]
assert poll['thread']['id']=='01a11583-ff90-73e0-8916-d021e2bb038d' and poll['thread']['status']['type']=='active'
assert poll['latestTurn']['id']=='01a11d47-78b5-7030-ad19-5d70087bff02' and poll['latestTurn']['status']=='inProgress' and poll['latestTurn']['error'] is None
inventory={x['path']:x for x in rows(read(Q/'PRESERVATION_BEFORE.json'))}
assert len(inventory)==3644
for p,row in inventory.items():
 path=Path(p);assert path.resolve().is_relative_to(R) and sha(path)==row['sha256']
 assert path.stat().st_size==row.get('bytes',row.get('size',path.stat().st_size))
lineage=read(Q/'R10_LINEAGE.json');master=read(H/'coordination/MASTER_GATE05_R10_PACKAGE_POLICY_E1_VERIFICATION_20261009.json')
assert not lineage['candidate_executed'] and len(lineage['candidates'])==2
for i,x in enumerate(lineage['candidates']):
 m=master['lineage'][i]
 assert x['mvid']==m['mvid'] and x['dll_sha256']==m['dll_sha256'] and x['pdb_sha256']==m['pdb_sha256']
 assert sha(Path(x['dll']))==x['dll_sha256'] and sha(Path(x['dll']).with_suffix('.pdb'))==x['pdb_sha256']
 assert x['codeview_guid']==m['codeviewGuid']==m['pdbGuid'] and m['codeviewMatched']
 assert len(x['documents'])==4 and all(d['matched'] for d in x['documents'])
 for d in x['documents']: assert sha(Path(d['frozen_source_path']))==d['pdb_hash']==d['actual_sha256']
correction=read(Q/'SETUP_CORRECTION_NOTE.json')
assert correction['actual_delivery']==delivery and correction['draft_original_bytes_preserved'] and correction['candidate_execution']==0 and correction['production_change']==0
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf-8-sig'))
assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and cfg['target_thread_id']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
proof={'at':at,'delivery_id':delivery,'wp_id':wp,'wp_revision':'S1','result_id':ack['result_id'],'status':'ACK_VERIFIED_INDEPENDENT_R10_STATIC_AND_POSITIVE_PURE_CODEC_POLICY_QA_IN_PROGRESS','ack_path':str(Q/'ACK.json'),'ack_sha256':sha(Q/'ACK.json'),'actual_snapshot':str(sp),'actual_snapshot_sha256':sha(sp),'actual_turn_id':poll['latestTurn']['id'],'actual_cursor':poll['cursor'],'protected_unique_paths_master_rehashed':len(inventory),'qa_lineage_path':str(Q/'R10_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R10_LINEAGE.json'),'debug_release_metadata_pdb_sources':'MATCHED4/4','setup_correction_path':str(Q/'SETUP_CORRECTION_NOTE.json'),'setup_correction_sha256':sha(Q/'SETUP_CORRECTION_NOTE.json'),'setup_correction_claim':'QA_DECLARED_NO_EXECUTION_BEFORE_DRAFT_CORRECTION','execution_verdict':'PENDING_FRESH_QA','scope':'Exact frozen Debug positive pure codec/digest/matching policy Check/TryAdmitWithPackagePolicy helpers,QA-owned fresh normal runner only;configuration/cache/provider/native/operator/old/negative/adverse not admitted','master_execution_builds':0,'runtime_e2_released':False,'closure_changed':False,'scheduler_changed':False,'new_wp_sent':False,'foundation':'HOLD'}
vp=H/'coordination/MASTER_SOL_R10_PACKAGE_POLICY_INDEPENDENT_S1_ACK_VERIFICATION_20261009.json';write(vp,proof)
comm.update(sol_status=proof['status'],sol_current_ack=proof,last_sol_cursor=poll['cursor'],updated_at=at)
comm['sol_current_delivery'].update(status=proof['status'],result_id=ack['result_id']);write(cp,comm)
dp=H/'DISPATCHER_STATE.json';state=read(dp)
state['endpoints']['sol'].update(execution_phase='IN_PROGRESS',ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],current_turn_id=poll['latestTurn']['id'])
state['updated_at']=at
for d in state['deliveries']:
 if d.get('delivery_id')==delivery:d.update(status=proof['status'],result_id=ack['result_id'],ack_proof=str(vp))
write(dp,state)
event=dict(proof,event_id=event_id,proof=str(vp),proof_sha256=sha(vp),type='SOL_R10_INDEPENDENT_ACK_COLLECTED')
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
paragraph=f'\n\n## LOCAL-SOL-R10-PACKAGE-POLICY-INDEPENDENT-S1-ACK — {at}\nOriginal Sol {delivery}/{wp}/S1/result {ack["result_id"]} identity-matched ACK/same actual active inProgress turn/cursor{poll["revision"]}. Master rehashed3644 protected unique paths and Debug/Release frozen DLL/PDB/source4/4 metadata against prior independent Master PE/MVID proof. {proof["status"]};fresh execution verdict pending. QA setup draft correction preserved,declared before execution;not a candidate alteration. Distinct expected/actual positive normal policy helpers only,policy ID/revision/order isolated normal cases and R9 version regression independent expectations;general policy encoding/injectivity/operator/native not certified. Configure/Clear/properties/cache/provider/game/native/operator/old/negative/adverse not admitted. Same hourlyPAUSED,no duplicate/newWP/closure/scheduler change. R9 narrow historical version CLOSED not inherited R10PASS;Engine002006/Pipeline007/current schema/G-Q1 OPEN,FoundationHOLD. Proof {vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf-8') as f:f.write(paragraph)
receipts['processed_dispatch_events'].append(event);receipts['updated_at']=at;write(rp,receipts)
print(json.dumps({'status':proof['status'],'protected_paths':len(inventory),'execution_verdict':'PENDING','monitor':'PAUSED60MIN','new_wp':False},ensure_ascii=False))
