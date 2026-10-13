from pathlib import Path
import ast,json,hashlib,datetime,sys,tomllib,copy
sys.stdout.reconfigure(encoding='utf8')
src=Path(__file__).with_name('master_dispose_r26_prepare_r27_20261011.py')
tree=ast.parse(src.read_text(encoding='utf8'))
# Only imports/constants/helper definitions; never re-run disposition or existing WP writes.
for n in tree.body:
 if n.lineno<17:exec(compile(ast.Module(body=[n],type_ignores=[]),str(src),'exec'))
RUN='MASTER-R26-R27-RECOVERY-20261012-01';PID=20116;SESSION=83680
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';rp=R/'Dispatcher/MASTER_RECEIPTS.json'
c=read(cp);b=read(bp);rr=read(rp);old=b['tasks'][-1]
assert old['dispatch_id'].endswith('4d660e9b') and c['active_operation'] is None
info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert info['status']=='LOCKED' and info['run_id']==RUN and info['pid']==PID
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
vp=C/'MASTER_R26_DUAL_CHILD_REG_PREPARATION_COMPLETION_VERIFICATION_20261011.json';v=read(vp);assert v['verification_status']=='MASTER_DISPOSED'
review=H/'MASTER_REVIEW_ENGINE_GATE05_R26_DUAL_CHILD_REG_PREPARATION_20261011.md';verdict=v['master_verdict'];assert sha(review)==v['master_review']['sha256']
assert all(sum(x.get('result_id')==v[k] for x in rr['processed_results'])==1 for k in ['A_result_id','Sol_result_id'])
old.update(status='COMPLETED_REVIEWED_READ_ONLY_PREPARATION_CORRECTED',result_id=v['A_result_id'],completion_sha256=v['A_completion_sha256'],master_disposition=verdict,master_review_path=str(review))
c.update(sol_status='R26_PREPARATION_COMPLETE_MASTER_ACCEPTED_NO_EXECUTION',sol_latest_completion=rr['processed_results'][-1],last_sol_cursor=v['Sol_actual']['cursor'],updated_at=at)
c['master_monitor_automation'].update(status='PAUSED',desired_status='PAUSED',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,pause_reason='R26 terminal reviewed; resume after actual next A delivery')
T=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R27-CHILD-CAPTURE-20261011-DIRECT-cdc223f3';dispatch=T.name
wp=H/'WP_ENGINE_GATE05_R27_CHILD_CAPTURE.md';release=H/'RELEASE_ENGINE_GATE05_R27_CHILD_CAPTURE_20261011.md';ip=T/'INSTRUCTIONS.md';scope=T/'MASTER_R27_AUTHORIZED_INSERTION_SCOPE.json'
s=read(scope);prod=s['all9_before'];fixed=s['fixed_current_files'];mutable=s['allowed_mutable_paths']
base=C/'MASTER_R27_CHILD_CAPTURE_PROTECTED_BASELINE_20261011.json';basejson=read(base);paths={f['path']:f for f in basejson['files']}
for f in prod+list(paths.values()):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size')),str(p)
policy=copy.deepcopy(old['preservation_policy'])
# Baseline inspector compares original Gate05, so historical Engine9 allowlist must remain.
# Current task's actual permissions are ONLY7, fixed current Census/csproj still independently pinned.
historical=policy['allowed_changed_engine_paths']
policy.update(fixed_current_files=fixed,r27_permission='ONE_NEW_PURE_IMMUTABLE_CAPTURE_CLASS_AND_EXACT6_OUTPUTS_ONLY',current_task_allowed_changed_engine_paths=mutable,historical_allowlist_does_not_expand_r27=True,prior_candidate_lineage='R25_FROZEN99_NOT_CURRENT_MUTABLE')
assert len(historical)==9 and len(mutable)==7
policy['additional_preserved_candidate_manifests'].append({'path':v['A_preparation_freeze']['path'],'sha256':v['A_preparation_freeze']['sha256'],'lineage':'R26_PREPARATION_DOCS11'})
policy['qa_preserved_manifests'].append({'path':str(Q/'EVIDENCE_MANIFEST.json'),'sha256':sha(Q/'EVIDENCE_MANIFEST.json')})
message=(T/'UI_MESSAGE.txt').read_text(encoding='utf8')
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='task' for x in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),str(src),'exec'))
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(task);write(T/'MASTER_R27_RECOVERED_PREDISPATCH_PRESERVATION.json',pres)
assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0],pres['preservation_errors']
write(T/'MASTER_R27_PRESERVATION_PREDISPATCH.json',pres)
audit={'at':at,'old_guard_run':'MASTER-R26-SOL-COMPLETE-20261011-01','old_pid':20528,'old_guard_actual':'TTL_EXPIRED_2026-10-12T00:34:56.623734+09','full_invocation_lock_coverage':'UNVERIFIED_NOT_RETROCLAIMED','recovered_run':RUN,'pid':PID,'session':SESSION,'failed_step':'Old-Gate05 preservation inspector historical9 allowlist narrowed to7 caused existing fixed Census/csproj old-baseline deltas; no new production change','correction':'Retain original historical9 comparison allowance; exact currenttask mutable7 and current fixed Census/csproj+Worker insertion fixed bytes independently enforce scope','A_actual_UI_input':'NONE_R27_NOT_SENT','R26_result_receipts_deduped':2,'review_and_WP_original_bytes_preserved':True,'known_installed_error':'UNCHANGED_OPEN','current_production9_match':True,'protected_paths_match':len(paths)}
write(C/'MASTER_R26_R27_INTERRUPTED_PREPARATION_RECONCILIATION_20261012.json',audit)
event(dict(audit,event_id=RUN+'-RECOVERY',type='INTERRUPTED_PREPARATION_NO_UI_DELIVERY_RECONCILED'))
# Continue only after the failed check. Generated WP bytes remain exact; no rerun old writes.
for n in tree.body:
 if n.lineno>=135:exec(compile(ast.Module(body=[n],type_ignores=[]),str(src),'exec'))
