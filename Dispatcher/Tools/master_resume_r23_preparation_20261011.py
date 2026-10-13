from pathlib import Path
R=Path(__file__).resolve().parents[2];s=(R/'Dispatcher/Tools/master_dispose_r22_prepare_r23_20261011.py').read_text(encoding='utf8')
head=s[:s.index('at=datetime.datetime.now')]
resume='''at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();vp=C/'MASTER_SOL_R22_DECLARATION_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json';v=read(vp)
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);old=b['tasks'][-1];rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp)
assert v['verification_status']=='MASTER_DISPOSED' and c['active_operation'] is None and old['dispatch_id'].endswith('9be1579a')
assert sum(x.get('result_id')==v['result_id'] for x in receipts['processed_results'])==1
review=Path(v['master_review_path']);verdict=v['master_verdict'];assert sha(review)==v['master_review_sha256']
dispatch='WE-A-ENGINE-GATE05-R23-IDENTIFIER-MAPPING-20261011-DIRECT-31bd3af2';T=R/'Dispatcher/A_TASKS'/dispatch;assert T.exists() and not list(T.iterdir())
qualification=C/'MASTER_R23_PREPARATION_RESUMED_AFTER_POLICY_SCHEMA_ERROR_20261011.json'
write(qualification,{'at':at,'same_unique_dispatch_id':dispatch,'R22_disposition_already_committed':True,'R22_result_dedupe':1,'initial_preparation_failure':'Missing additional_preserved_paths key;actual policy uses qa_preserved_manifests and fixed_current_files','before_failure_new_WP_release_baseline_taskboard_UI_input':0,'empty_task_directory_reused':True,'no_production_or_QA_original_change':True})
'''
tail=s[s.index('policy=copy.deepcopy(old') :]
start=tail.index("for f in read(Q/'EVIDENCE_MANIFEST.json')");end=tail.index("source=R/'scratch/WorkerBridgeMod/Source'",start)
tail=tail[:start]+'''qm=Q/'EVIDENCE_MANIFEST.json';policy['qa_preserved_manifests'].append({'path':str(qm),'sha256':sha(qm)})
for n in ['EVIDENCE_MANIFEST.json','COMPLETION.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
 q=Q/n;policy['fixed_current_files'].append({'path':str(q),'sha256':sha(q),'size':q.stat().st_size})
''' +tail[end:]
out=R/'Dispatcher/Tools/master_r23_prepare_continuation_20261011.py';assert not out.exists();out.write_text(head+resume+tail,encoding='utf8');print('RESUME_SAME_R23_PREPARATION_ONLY_NO_REDISPOSITION')
