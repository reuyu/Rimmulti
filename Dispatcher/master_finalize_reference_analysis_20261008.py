"""Finalize Master analysis/disposition under the live exclusive run lock."""
from pathlib import Path
import datetime, hashlib, json, subprocess
import master_check_a_result as checker
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'Dispatcher'
H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=H/'coordination/REFERENCE_MOD_SOURCE_INVENTORY_20261008.json'
data=read(inventory)
errors=[]
for source in data['sources'].values():
 for f in source['files']:
  if sha(Path(f['path']))!=f['sha256']:errors.append(f['path'])
assert not data['missing'] and not errors
report=H/'REFERENCE_MOD_REUSE_ANALYSIS_20261008.md'
text=report.read_text(encoding='utf-8')
assert text.count('|')>100
board=read(D/'MASTER_A_TASKS.json')
t=next(x for x in board['tasks'] if x['dispatch_id']=='WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708')
folder=Path(t['ack_path']).parent
notice=folder/'MASTER_SAME_WP_PRESERVATION_NOTICE_20261008.md'
noticeproof=folder/'MASTER_PRESERVATION_NOTICE_DELIVERY_20261008.json'
np={'event_id':'MASTER-SAME-R2-PRESERVATION-NOTICE-20261008-01','observed_at':now,'message_path':str(notice),'message_sha256':sha(notice),'delivery_status':'NOT_SENT','reason':'Fresh returned Antigravity window4458672/current conversation WarEconomy 컨텍스트 복구 및 수행 shows exact user R2 recovery and Working. Composer focus remains root document after observed clicks; no text/submission/cancel. No duplicate WP. Retry requires fresh observation and proven composer focus.','window_id':4458672,'actual_text_input':False,'submission':False,'new_wp':False}
write(noticeproof,np)
# Remove only the final null line this Master invocation accidentally appended after
# a PowerShell boolean typo; preserve all valid prior journal entries.
journal=D/'MASTER_MONITOR_JOURNAL.jsonl'
lines=journal.read_text(encoding='utf-8-sig').splitlines()
if lines and lines[-1]=='null':journal.write_text('\n'.join(lines[:-1])+'\n',encoding='utf-8')
with journal.open('a',encoding='utf-8') as f:f.write(json.dumps(np,ensure_ascii=False)+'\n')
t['preservation_notice_delivery_status']='NOT_SENT'
t['preservation_notice_path']=str(notice)
t['preservation_notice_delivery_proof']=str(noticeproof)
t['updated_at']=now
board['updated_at']=now
write(D/'MASTER_A_TASKS.json',board)
incident=H/'coordination/ENGINE_INSTALLED_IDENTITY_INCIDENT_20261008'
snapshot=incident/'OBSERVED_INSTALLED_WorkerBridge.dll'
pdb=ROOT/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb'
lineage=json.loads(subprocess.check_output(['dotnet',str(D/'Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(snapshot),str(pdb)],text=True))
lineage.update(observed_at=now,assembly_sha256=sha(snapshot),pdb_sha256=sha(pdb),master_interpretation='PE MVID/CodeView observed read-only. Current mutable Debug PDB does NOT match this installed snapshot; its source checksums cannot establish the installed binary source lineage. No candidate execution.')
write(incident/'READONLY_PE_CURRENT_PDB_COMPARISON.json',lineage)
result=checker.inspect()
preservation=checker.inspect_preservation(t)
proof=H/'coordination/REFERENCE_MOD_REUSE_MASTER_DISPOSITION_20261008.json'
record={'schema_version':1,'event_id':'MASTER-REFERENCE-MOD-ANALYSIS-20261008-01','at':now,'exclusive_lock_run':'MASTER-REFERENCE-FINALIZE-20261008-03','exclusive_lock_session':1486,'user_request':'Analyze local working mods for implementation/PoC reuse; another A reset/resumed processing reported','report_path':str(report),'report_sha256':sha(report),'inventory_path':str(inventory),'inventory_sha256':sha(inventory),'inventory_checked_files':sum(len(v['files']) for v in data['sources'].values()),'inventory_changes':errors,'reference_build_or_runtime_tests':False,'production_candidate_modified_by_this_analysis':False,'disposition':'CONCRETE_REUSE_ANALYSIS_ADOPTED_NO_IMPLEMENTATION_RELEASE','priorities':['Gate05 fresh native process adapter reference','G-Q1 bounded map time/RNG/context probe','target map materialization/cross-reference controls','Tactical transport/replay/UI after gates'],'license_mp':'MIT notice/provenance/dependency checks required','license_rt':'CC BY-NC-ND4 adaptation public-sharing not granted; conceptual reference pending separate permissions/source','new_wp_sent':False,'a_same_task_status':t['status'],'a_latest_check':result,'preservation':preservation,'notice_delivery_status':'NOT_SENT','installed_incident':'OPEN_ACTOR_CAUSE_UNKNOWN','installed_snapshot_mvid':lineage['mvid'],'snapshot_current_debug_pdb_matched':lineage['codeviewMatched'],'closure_changed':False,'foundation':'HOLD','gq1':'OPEN','monitor_interval_minutes':60,'monitor_changed':False}
write(proof,record)
event={k:record[k] for k in ['event_id','at','disposition','closure_changed']}
event.update(proof=str(proof),proof_sha256=sha(proof),report=str(report),new_wp_sent=False)
for p in [journal,H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
delta=f'''\n\n## LOCAL-REFERENCE-MOD-REUSE-ANALYSIS — {now}\nUser requests actual local Together/Multiplayer analysis for implementation and PoC reuse. Master adopted concrete source-based reuse backlog in REFERENCE_MOD_REUSE_ANALYSIS_20261008.md;58 selected files SHA verified unchanged; no reference build/runtime PASS or Production integration. MP MIT context/launcher/materializer/trace/test patterns are adapter candidates; RT CC BY-NC-ND4/DLL-only client/shared/network scope constrains adapted public reuse. MP streaming is hard-disabled (CanUseStandaloneMapStreaming=>false); Def count/name hash and Arbiter lockstep peer do not satisfy MD130/126~129. Current A R2 ACK IN_PROGRESS retained, no new WP. Existing installed DLL incident remains OPEN; snapshot MVID {lineage['mvid']}, current mutable Debug PDB CodeView mismatch. Same-WP notice prepared NOT SENT (active A, composer focus unproven; no text/cancel/submission). No old hash normalization/external restore. Current gates/closure and hourly monitor unchanged: Engine002006/Pipeline007/current schema/G-Q1 OPEN;Foundation HOLD. Proof: {proof}\n'''
for name in ['MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','MASTER_AGENT_DISPATCH_BOARD.md']:
 with (H/name).open('a',encoding='utf-8') as f:f.write(delta)
with (ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md').open('a',encoding='utf-8') as f:f.write(delta)
state=read(D/'MASTER_COMMUNICATION_STATE.json')
state['reference_analysis']={'status':'COMPLETED_ANALYSIS_ONLY','report':str(report),'proof':str(proof),'new_wp_sent':False}
state['a_preservation_attention']['notice_delivery_status']='NOT_SENT'
state['updated_at']=now
write(D/'MASTER_COMMUNICATION_STATE.json',state)
print(json.dumps({'report':str(report),'verified_reference_files':record['inventory_checked_files'],'a_status':result['status'],'notice_status':'NOT_SENT','incident_mvid':lineage['mvid'],'installed_snapshot_pdb_match':lineage['codeviewMatched'],'proof':str(proof)},ensure_ascii=False))
