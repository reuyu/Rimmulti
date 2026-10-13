from pathlib import Path
import json,datetime,hashlib,tomllib,sys,re
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp)
if len(sys.argv)>1 and sys.argv[1]=='released':
 rp=C/'MASTER_R18_COMPLETE_R19_DISPATCH_GUARD_FINALLY_RELEASE_20261010.json';r=read(rp)['actual_release_tool'];raw=r['output']
 # Raw PTY may wrap at column80 and repeat a prefix before a VT cursor move.
 # Keep raw bytes intact;accept only the observed expected PID in that exact form.
 pid_match=re.search(r'id"\s*:\s*34784\b',raw) or re.search(r'"pid":\s*[0-9]+\r?\n\x1b\[[0-9;]+H34784\b',raw)
 assert r['exit_code']==0 and '"status": "RELEASED"' in raw and '"run_id": "MASTER-SOL-R18-COMPLETE-20261010-01"' in raw and pid_match
 released_at=re.search(r'"released_at"\s*:\s*"([^"]+)"',raw).group(1)
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=released_at,release_proof_path=str(rp),all_child_commands_completed_before_release=True);c['updated_at']=at;write(cp,c)
 audit=C/'MASTER_R18_COMPLETE_R19_FINAL_COORDINATION_AUDIT_20261010.json';d=read(audit);d.update(actual_guard_finally_release='RELEASED_HELPER_EXIT0',release_proof=str(rp));write(audit,d)
 event({'at':at,'event_id':'MASTER-R18-COMPLETE-R19-DISPATCH-GUARD-RELEASE-20261010-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':c['last_monitor_run']['run_id'],'pid':34784,'proof':str(rp),'all_child_commands_completed_before_release':True});print('ACTUAL_R18_COMPLETE_R19_DISPATCH_GUARD_RELEASE_RECORDED_EXIT0');sys.exit(0)
assert c['active_operation'] is None
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];assert t['dispatch_id'].endswith('5415a675') and t['delivery_status']=='SENT' and t['ack_verified'] and t['submission_attempts']==1
ack=read(Path(t['ack_path']));assert sha(Path(t['ack_path']))==t['ack_sha256'] and ack['task_state']=='IN_PROGRESS' and ack['envelope']==22
for k in ['instruction','work_package','release','scope_baseline','exact_message']:assert sha(Path(t[k+'_path']))==t[k+'_sha256']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
v=read(C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json');assert v['verification_status']=='MASTER_DISPOSED'
receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert sum(x.get('result_id')==v['result_id'] for x in receipts['processed_results'])==1
assert sum(x.get('event_id')==t['dispatch_id']+'-SENT-HOURLY-ACTIVE' for x in receipts['processed_dispatch_events'])==1
snapfile=C/'MASTER_R18_DISPOSITION_NOTICE_SOL_FINAL_SNAPSHOT_20261010.json';s=json.loads(read(snapfile)['content'][0]['text'])['polls'][0]
assert s['thread']['id']==c['sol_thread_id'] and s['latestTurn']['id']=='01a124b2-aec6-7993-9d5d-fd1a586e9ffa'
c.update(last_sol_cursor=s['cursor'],sol_last_receipt_notice={'path':str(snapfile),'sha256':sha(snapfile),'actual_snapshot':s,'not_a_QA_WP':True},updated_at=at);write(cp,c)
sp=H/'DISPATCHER_STATE.json';d=read(sp);d['endpoints']['sol'].update(last_runtime_observation_cursor=s['cursor'],current_runtime_idle_verified=s['thread']['status']['type']=='idle',execution_phase='R18_TERMINAL_RECEIPT_NOTICE_ONLY_NO_ACTIVE_QA_WP');d['updated_at']=at;write(sp,d)
defect=C/'MASTER_DEFECT_ENGINE_G05_OPAQUE_R18_20261010.json';assert not defect.exists()
write(defect,{'defect_id':'ENGINE-G05-OPAQUE-R18-20261010-01','at':at,'status':'OPEN','severity':'HIGH','scope':'Normal opaque policyId/revision losslessstring invariant across4snapshotroutes/bothroles;separatefromwholeEngine002006','candidate_sha256':v['selected_sha256'],'candidate_mvid':v['selected_mvid'],'independent_result_id':v['result_id'],'actual_runs':v['runs'],'cause':'WorkerSnapshot3612..3613 Trim removes normalleading/trailingspaces,changescanonicalpolicy digest','Master_verification':str(C/'MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json'),'report':v['report_path'],'corrective_dispatch_id':t['dispatch_id'],'corrective_scope':'TWO_ASSIGNMENTS_ONLY;otherWorkerbytesfixed','closure_requires':['Exactnewcandidatehash-MVID-source-PDB+manifest','Independentnewnormalfulltypedoriginalopaque policygraph/digest regression','Scope/preservation matched','Masterdisposition;no inference fromE1'],'broader_gate_closure':False,'foundation':'HOLD'})
ledger=H/'QA_DEFECT_LEDGER.md'
with ledger.open('a',encoding='utf8') as f:f.write(f'\n\n## ENGINE-G05-OPAQUE-R18-20261010-01 — OPEN / HIGH — {at}\nNormal opaque policy ID/revision spaces lost by snapshotTrim;bothroles/4routes/actual101PASS24FAIL each. Independent result{v["result_id"]};exactcandidate{v["selected_sha256"]}. NewR19{t["dispatch_id"]} actualSENT/ACKIN_PROGRESS;twoassignments only/expectedWorkerSHA{t["allowed_worker_source_after_sha256"]}. Closure needsnewexactcandidate+freshindependentnormaloriginalgraph-digestQA+Masterdisposition. This scopeddefect doesnotcloseEngine002006/fullGate. Proof{defect}\n')
# Durable acceptance criterion,not a producer repair oroldmanifest normalization.
instructions=R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md'
with instructions.open('a',encoding='utf8') as f:f.write(f'\n\n## R19 exact source admission check — {at}\nCurrent{t["dispatch_id"]}: terminal review MUST compare actualnewWorkerSHA to task.allowed_worker_source_after_sha256={t["allowed_worker_source_after_sha256"]};baseline onlytwoTrimassignments permitted,ALLother sourcebytes fixed. Generic allowedmutable7 preservation alone is insufficient. Ifhashdiffers,record scopeviolation/integritydelta anddo notadmitfreshQAuntilMasterreconciliation;do notnormalizebaseline/frozenpriorbytes. OriginalR18normalFAIL andproducer manualactual16 correction retained. RoutineAterminal→Masterreviewfreeze→SolidlefreshWP/directQA→Masterdisposition remainsautomatic;no native/bootstrap/adversepermission inferred.\n')
proof={'at':at,'run_id':'MASTER-SOL-R18-COMPLETE-20261010-01','guard_session':36347,'guard_pid':34784,'status':'R18_NORMAL_LOSSLESS_FAIL_ACCEPTED_R19_MINIMALFIX_ACTUAL_SENT_ACK_VERIFIED_HOURLY_ACTIVE','R18_result_id':v['result_id'],'R18_result_dedupe_count':1,'R19_dispatch_id':t['dispatch_id'],'R19_ACK_sha256':t['ack_sha256'],'R19_status':t['status'],'one_actual_submit':True,'R19_expected_sourceSHA':t['allowed_worker_source_after_sha256'],'Sol_notice_actual':s,'new_QA_WP':False,'scheduler_actual':cfg,'futureR19heartbeat_observed':False,'defect_id':'ENGINE-G05-OPAQUE-R18-20261010-01','defect_status':'OPEN_HIGH_PENDING_FRESH_QA','actual_guard_finally_release':'PENDING','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
dest=C/'MASTER_R18_COMPLETE_R19_FINAL_COORDINATION_AUDIT_20261010.json';assert not dest.exists();write(dest,proof)
event(dict(proof,event_id=t['dispatch_id']+'-FINAL-COORDINATION-AUDIT',type='R18_FAIL_DISPOSED_R19_ACTUAL_SENT_ACK_ACTIVE_MONITOR_SOL_TERMINAL_NOTICE',proof_path=str(dest),proof_sha256=sha(dest)))
print(json.dumps({'A':t['status'],'ACK':'VERIFIED_IN_PROGRESS','Sol_actual':s['thread']['status']['type'],'Sol_cursor':s['revision'],'scheduler':'ACTIVE60MIN','one_submit':True,'new_QA_WP':False,'defect':'OPEN_HIGH','foundation':'HOLD'},ensure_ascii=True))

