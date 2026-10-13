from pathlib import Path
import json,hashlib,sys,datetime,tomllib
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';Q=R/'QA-Tactical-Engine/GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(d):
 if isinstance(d,dict):
  if 'path' in d and 'sha256' in d and Path(d['path']).is_absolute():yield d
  if 'manifest' in d and 'manifest_sha256' in d:yield {'path':d['manifest'],'sha256':d['manifest_sha256']}
  for v in d.values():yield from rows(v)
 elif isinstance(d,list):
  for v in d:yield from rows(v)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);ack=read(Q/'ACK.json');assert comm['active_operation'] is None and ack['delivery_id']==comm['sol_current_attempt_id']=='SOL-GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008-01' and ack['wp_id']==comm['sol_current_wp']=='WP_QA_ENGINE_GATE05_R7_CONTENT_ADMISSION_INDEPENDENT' and ack['wp_revision']=='S1' and ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp'];assert ack['result_id']=='SOL-GATE05-R7-CONTENT-ADMISSION-INDEPENDENT-S1-20261008-a860491cbc81403eb91650ce707f26cc'
snap=H/'coordination/MASTER_SOL_R7_CONTENT_ADMISSION_INDEPENDENT_S1_ACK_SNAPSHOT_20261008.json';d=read(snap);poll=json.loads(next(x['text'] for x in d['content'] if x['type']=='text'))['polls'][0];assert poll['latestTurn']['status']=='inProgress' and poll['latestTurn']['id']=='01a11bda-0e86-7330-ad00-d21baf5fd5b0' and poll['thread']['status']['type']=='active'
inventory={row['path']:row for row in rows(read(Q/'PRESERVATION_BEFORE.json'))};assert len(inventory)==2701,len(inventory)
for p,row in inventory.items():
 path=Path(p);assert path.resolve().is_relative_to(R) and sha(path)==row['sha256'];assert path.stat().st_size==row.get('bytes',row.get('size',path.stat().st_size))
lineage=read(Q/'R7_LINEAGE.json');assert not lineage['candidate_executed'] and len(lineage['candidates'])==2
oldproof=read(H/'coordination/MASTER_GATE05_R7_CONTENT_ADMISSION_E1_VERIFICATION_20261008.json')
for i,x in enumerate(lineage['candidates']):
 assert x['mvid']==oldproof['lineage'][i]['mvid'] and x['dll_sha256']==oldproof['lineage'][i]['dll_sha256'] and x['pdb_sha256']==oldproof['lineage'][i]['pdb_sha256'];assert sha(Path(x['dll']))==x['dll_sha256']
 assert len(x['documents'])==4 and all(row['matched'] for row in x['documents'])
 for row in x['documents']:assert sha(Path(row['frozen_source_path']))==row['pdb_hash']==row['actual_sha256']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf-8-sig'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
proof={'at':at,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'status':'ACK_VERIFIED_INDEPENDENT_R7_STATIC_AND_POSITIVE_PURE_CODEC_QA_IN_PROGRESS','ack_path':str(Q/'ACK.json'),'ack_sha256':sha(Q/'ACK.json'),'actual_snapshot':str(snap),'actual_snapshot_sha256':sha(snap),'actual_turn_id':poll['latestTurn']['id'],'actual_cursor':poll['cursor'],'protected_unique_paths_master_rehashed':2701,'qa_lineage_path':str(Q/'R7_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R7_LINEAGE.json'),'debug_release_metadata_pdb_sources':'MATCHED4/4','execution_verdict':'PENDING_FRESH_QA','scope':'Selected frozen Debug pure positive Serialize/Deserialize/CanonicalNormalize/normal ValidateContract and positive TryAdmitManifest helpers;QA-owned runner only;no production rebuild/provider/cache/game/native/operator/adverse/rejection','runtime_e2_released':False,'closure_changed':False,'scheduler_changed':False,'direct_report_received':True,'master_execution_builds':0,'foundation':'HOLD'}
vp=H/'coordination/MASTER_SOL_R7_CONTENT_ADMISSION_INDEPENDENT_S1_ACK_VERIFICATION_20261008.json';write(vp,proof);comm.update(sol_status=proof['status'],sol_current_ack=proof,last_sol_cursor=poll['cursor'],updated_at=at);comm['sol_current_delivery'].update(status=proof['status'],result_id=ack['result_id']);write(cp,comm)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='IN_PROGRESS',ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],current_turn_id=poll['latestTurn']['id']);state['updated_at']=at
for row in state['deliveries']:
 if row.get('delivery_id')==ack['delivery_id']:row.update(status=proof['status'],result_id=ack['result_id'],ack_proof=str(vp))
write(sp,state)
event=dict(proof,event_id='SOL-R7-CONTENT-ADMISSION-INDEPENDENT-S1-ACK-MASTER-20261008-01',proof=str(vp),proof_sha256=sha(vp))
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
paragraph=f'\n\n## LOCAL-SOL-R7-CONTENT-ADMISSION-INDEPENDENT-S1-ACK — {at}\nOriginal Sol {ack["delivery_id"]}/{ack["wp_id"]}/S1/result {ack["result_id"]} identity-matched ACK and same actual active/inProgress turn/cursor46. Master independently rehashed2701 unique protected paths and frozen PDB source4/4 against own R7 PE/MVID/CodeView verification. ACK_VERIFIED_INDEPENDENT_R7_STATIC_AND_POSITIVE_PURE_CODEC_QA_IN_PROGRESS;fresh execution verdict pending,no inherited R6 PASS/new WP/duplicate/closure/scheduler change. Selected frozen223B... pure normal codec/ValidateContract/positive TryAdmit only;QA-owned fresh runner build permitted,production modify/rebuild/provider/cache/getter/game/native/operator/oldrunner/rejection/adverse not released. Same hourly monitor PAUSED,Foundation HOLD/open gates unchanged. Proof {vp}\n'

for p in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md',R/'AGENTS.md']:
 with p.open('a',encoding='utf-8') as f:f.write(paragraph)
rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp);assert not any(x.get('event_id')==event['event_id'] for x in receipts['processed_dispatch_events']);receipts['processed_dispatch_events'].append(dict(event,type='SOL_R7_INDEPENDENT_ACK_COLLECTED'));receipts['updated_at']=at;write(rp,receipts)
print(json.dumps({'status':proof['status'],'protected_paths':2701,'execution':'PENDING','scheduler':'PAUSED','new_wp':False},ensure_ascii=False))
