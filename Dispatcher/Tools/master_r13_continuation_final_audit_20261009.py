from pathlib import Path
import json,datetime,hashlib,tomllib
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];r=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert c['active_operation'] is None and c['sol_current_wp']=='WP_QA_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_INDEPENDENT' and t['status'].startswith('COMPLETED_REVIEWED')
base=Path(c['sol_current_delivery']['baseline_path']);d=read(base);assert len(d['files'])==6021
for f in d['files']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173
snap=json.loads(read(C/'MASTER_R13_CONTINUATION_FINAL_SNAPSHOT_20261009.json')['content'][0]['text'])['polls'][0];assert snap['latestTurn']['id']=='01a1206c-833a-7530-97ab-66ebd84e494e' and snap['latestTurn']['status']=='inProgress'
ids=['WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-RESULT-01','SOL-GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009-061977ed92374bc1a534ee3d99098e01'];counts={rid:sum(x.get('result_id')==rid for x in r['processed_results']) for rid in ids};assert all(n==1 for n in counts.values())
q=R/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-INDEPENDENT-S1-20261009';ack=q/'ACK.json';a=read(ack) if ack.exists() else None
if a:assert a['delivery_id']==c['sol_current_attempt_id'] and a['wp_id']==c['sol_current_wp'] and a['wp_revision']=='S1' and a['producer']=='Sol'
proof={'at':at,'run_id':'MASTER-R13-HEARTBEAT-20261009T110931Z-01','guard_session':32118,'guard_pid':864,'old_lease_expired_no_retroactive_coverage':True,'current_live_renewal_and_contender_LOCK_BUSY_observed':True,'no_pending_child_command_sessions':True,'a_r13_terminal_verdict':c['a_latest_result']['master_verdict'],'a_candidate_frozen':72,'result_dedupe_counts':counts,'original_sol_independent_delivery':'ACTUAL_SENT_NEW_ACTIVE_TURN','actual_sol_snapshot':snap,'ack':a,'ack_sha256':sha(ack) if a else None,'protected_unique_rehashed':6021,'baseline_sha256':sha(base),'automation_actual':cfg,'next_a':'NOT_SENT_PENDING_INDEPENDENT_QA_FINDINGS','full_runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','float_reference_verifier_repair':'Initial assertion used Python double decimal equality;corrected to declared Float32 exact bits,all other typed leaves exact;no producer/QA/oracle edits or invalid acceptance writes','release_protocol':'RELEASE same valid helper session in finally immediately after audit;actual helper release tool evidence follows'};vp=C/'MASTER_R13_CONTINUATION_FINAL_AUDIT_20261009.json';assert not vp.exists();write(vp,proof)
c['last_sol_cursor']=snap['cursor'];c['last_monitor_run'].update(at=at,status='FINISHED_A_R13_DISPOSED_SOL_R13_INDEPENDENT_ACTIVE',final_audit=str(vp),release_requested_after_final_audit=True);c['updated_at']=at
if a:c.update(sol_status='R13_INDEPENDENT_NORMAL_QA_ACK_IDENTITY_VERIFIED_ACTIVE',sol_current_result_id=a['result_id'],sol_current_ack={'path':str(ack),'sha256':sha(ack),'actual_snapshot':snap,'proof':str(vp)})
write(cp,c)
with (R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps({'at':at,'type':'R13_CONTINUATION_FINAL_AUDIT','proof':str(vp),'proof_sha256':sha(vp),'A':'TERMINAL_REVIEWED','Sol':'INDEPENDENT_ACTIVE','monitor':'PAUSED60MIN','protected':6021,'guard_release_follows':True})+'\n')
print(json.dumps({'A':'R13_TERMINAL_REVIEWED_STATIC_REVISION_REQUIRED','Sol':'R13_INDEPENDENT_ACTIVE_ACK_VERIFIED' if a else 'R13_INDEPENDENT_ACTIVE_ACK_PENDING','monitor':'PAUSED60MIN','protected':6021,'dedupe':counts}))
