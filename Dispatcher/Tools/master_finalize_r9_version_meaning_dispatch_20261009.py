from pathlib import Path
import json, hashlib, datetime, tomllib

R=Path(__file__).resolve().parents[2]
H=R/'docs/WarEconomy_Master_Handoff_20261006'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
bp=R/'Dispatcher/MASTER_A_TASKS.json'; b=read(bp); t=b['tasks'][-1]
assert t['dispatch_id']=='WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b' and t['delivery_status']=='SENT'
root=Path(t['instruction_path']).parent; ui=read(root/'MASTER_UI_SUBMISSION_CONFIRMED.json')
assert ui['exact_message']==t['exact_message'] and ui['composer_cleared'] and ui['send_clicks']==1 and ui['active_cancel_observed']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf-8-sig'))
assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json'; c=read(cp); op=c['active_operation']; assert op['dispatch_id']==t['dispatch_id']
pres=read(root/'MASTER_FRESH_PREDISPATCH_PRESERVATION.json')
assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
for key,n in [('engine_archive_checks',19),('prior_candidate_checks',1029),('pipeline_preservation_checks',206),('qa_preservation_checks',1834)]: assert len(pres[key])==n and all(x['matched'] for x in pres[key])
installed=Path('C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll')
assert sha(installed)==op['known_installed_actual_sha256_verified']=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61'
ack_path=Path(t['ack_path']); ack=read(ack_path) if ack_path.exists() else None
if ack:
 assert ack['dispatch_id']==t['dispatch_id'] and ack['wp_id']==t['wp_id'] and ack['wp_revision']==t['wp_revision'] and ack['envelope']==12
 assert ack['status'] in ['ACKNOWLEDGED','IN_PROGRESS']
notice=H/'coordination/MASTER_SOL_R8_VERSION_MEANING_DISPOSITION_NOTICE_TOOL_20261009.json'
assert not read(notice).get('isError',False)
snap=read(H/'coordination/MASTER_SOL_R8_VERSION_MEANING_DISPOSITION_NOTICE_POSTSEND_20261009.json')
poll=json.loads(next(x['text'] for x in snap['content'] if x['type']=='text'))['polls'][0]
contender=read(H/'coordination/MASTER_R9_CONTENDER_LOCK_PROOF_20261009.json'); assert 'LOCK_BUSY' in contender['output'] and not contender.get('session_id')
status='SENT_ACK_VERIFIED_IN_PROGRESS' if ack else 'SENT_ACK_PENDING'
vp=H/'coordination/MASTER_GATE05_R9_VERSION_MEANING_DISPATCH_MONITOR_ACTIVE_20261009.json'
proof={'at':at,'type':'A_R9_VERSION_MEANING_SENT_HOURLY_ACTIVE','dispatch_id':t['dispatch_id'],'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'envelope':12,'status':status,'actual_ui_proof':str(root/'MASTER_UI_SUBMISSION_CONFIRMED.json'),'actual_ui_sha256':sha(root/'MASTER_UI_SUBMISSION_CONFIRMED.json'),'trees':[{'path':str(root/n),'sha256':sha(root/n)} for n in ['MASTER_UI_PREDISPATCH_TREE.txt','MASTER_UI_EXACT_DRAFT_TREE.txt','MASTER_UI_SUBMITTED_TREE.txt']],'ack_verified':bool(ack),'ack_path':str(ack_path),'ack_sha256':sha(ack_path) if ack else None,'ack_status':ack.get('status') if ack else None,'preservation_before':str(root/'MASTER_FRESH_PREDISPATCH_PRESERVATION.json'),'preservation_before_sha256':sha(root/'MASTER_FRESH_PREDISPATCH_PRESERVATION.json'),'counts':{'archive':19,'prior':1029,'pipeline':206,'qa':1834},'installed_actual_sha256':sha(installed),'installed_incident':'UNCHANGED_OPEN_ACTOR_UNKNOWN_NO_RESTORE','automation_actual_config':cfg,'future_r9_scheduled_run_observed':False,'guard_run':op['guard_run'],'guard_session':op['guard_session'],'previous_expired_guard_not_reused':True,'contender_lock_busy_verified':True,'historical_r4_lease_gap_unverified':True,'sol_notice_proof':str(notice),'sol_notice_sha256':sha(notice),'sol_post_notice':poll,'sol_new_qa_wp':False,'defect':'ENGINE-CONTENT-VERSION-SEMANTIC-20261009-01 OPEN','scope':'ONE version inference/projection meaning repair;other supported boundary/native gates separate','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
write(vp,proof)
t.update(status='IN_PROGRESS' if ack else 'SENT_ACK_PENDING',ack_verified=bool(ack),ack_sha256=proof['ack_sha256'],monitor_status='ACTIVE60MIN_VERIFIED',monitor_configuration_proof=str(vp),updated_at=at)
b['updated_at']=at; write(bp,b)
c.update(a_status='R9_VERSION_MEANING_IN_PROGRESS_ACK_VERIFIED' if ack else 'R9_VERSION_MEANING_SENT_ACK_PENDING',a_pending_dispatch_id=None,a_latest_delivery=proof,a_latest_runtime_observation=proof,active_operation=None,last_sol_cursor=poll['cursor'],sol_status='R8_INDEPENDENT_FAIL_ACCEPTED_DISPOSITION_NOTICE_NO_NEW_QA_WP',updated_at=at,last_monitor_run={'run_id':op['guard_run'],'at':at,'result':status})
c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(vp),future_run_after_engine_r9_resume_observed=False,pause_reason=None,resumed_by='Master after actual R9 Computer Use SENT',no_resume_in_this_review=False)
c['sol_preparation_disposition_notice']={'at':at,'status':'SENT_TOOL_RETURNED','proof':str(notice),'new_wp':False,'actual_snapshot':poll}; write(cp,c)
sp=H/'DISPATCHER_STATE.json'; s=read(sp)
s['endpoints']['a'].update(route='Master Computer Use',current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],current_conversation_status='ACTUAL_R9_SUBMITTED_COMPOSER_CLEARED_ACTIVE_CANCEL',execution_phase='IN_PROGRESS',ack_verified=bool(ack),last_ui_proof=proof['actual_ui_proof'],last_ui_observation_at=ui['observed_at'])
s['endpoints']['sol'].update(execution_phase='R8_QA_COMPLETE_NOTICE_ONLY_NO_NEW_WP',last_runtime_observation_cursor=poll['cursor'],current_runtime_idle_verified=poll['thread']['status']['type']=='idle')
s['master_monitor_automation']=c['master_monitor_automation']; s.update(updated_at=at,latest_master_dispatch=str(vp)); s['deliveries'].append({'delivery_id':t['dispatch_id'],'recipient':'A','status':status,'wp_id':t['wp_id'],'wp_revision':t['wp_revision'],'proof':str(vp),'proof_sha256':sha(vp),'runtime_e2_released':False});write(sp,s)
rp=R/'Dispatcher/MASTER_RECEIPTS.json'; receipts=read(rp); eid=t['dispatch_id']+'-SENT-HOURLY-ACTIVE';assert not any(x.get('event_id')==eid for x in receipts['processed_dispatch_events'])
receipts['processed_dispatch_events'].append({'event_id':eid,'at':at,'dispatch_id':t['dispatch_id'],'proof':str(vp),'proof_sha256':sha(vp)});receipts['updated_at']=at;write(rp,receipts)
event={'at':at,'event_id':eid,'type':proof['type'],'dispatch_id':t['dispatch_id'],'status':status,'proof':str(vp),'proof_sha256':sha(vp),'closure_changed':False}
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
paragraph=f'\n\n## LOCAL-A-R9-VERSION-MEANING-SENT-HOURLY-ACTIVE — {at}\n{t["dispatch_id"]}/{t["wp_id"]}/{t["wp_revision"]}/envelope12 actual Computer Use SENT: fresh exact A conversation/idle/focused composer/exact draft/one submit/new user message/cleared composer/active Cancel observed. {status};no resend. Narrow version meaning repair only;unknown modVersion cannot be manufactured from compatibility;other content support/native gates separate. Prior R8 independent normal FAIL retained,High ENGINE-CONTENT-VERSION-SEMANTIC-20261009-01 OPEN until fresh candidate/targeted independent QA/Master disposition. Pre-input archive19/prior1029/Pipeline206/QA1834 and fixed paths matched;known installed BB3B unchanged OPEN/actorUNKNOWN/no restore. New live renewed guard25013/run MASTER-R9-CONTINUE-20261009-01 and contender LOCK_BUSY;previous expired guard not used for input. Historical R4 gap remains unverified. Same actual wareconomy-master ACTIVE60min/173char/correct Master target;future R9 run unobserved. Original Sol R8 FAIL accepted,disposition notice sent,no new QA WP;await fresh frozen R9. Production writer A only;Master execute/build0. No full runtime E2/closure;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Proof {vp}\n'
for dest in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
print(json.dumps({'status':status,'monitor':cfg['status'],'interval':60,'proof':str(vp),'closure':False}))
