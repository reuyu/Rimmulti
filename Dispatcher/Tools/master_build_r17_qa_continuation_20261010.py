from pathlib import Path
src=Path('Dispatcher/Tools/master_publish_r17_e1_prepare_qa_20261010.py').read_text(encoding='utf8')
tail=src[src.index('# New independent scope baseline'):]
prefix=src[:src.index('at=datetime.datetime')]
prefix+='''at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
vp=C/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_E1_VERIFICATION_20261010.json';p=read(vp);assert p['verification_status']=='MASTER_DISPOSED'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1]
review=H/'MASTER_REVIEW_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_E1_20261010.md';verdict=p['master_verdict']
'''
needle="for f in paths.values():q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['bytes']"
replacement='''excluded=[]
for key in list(paths):
 if Path(key).resolve()==(R/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs').resolve():
  excluded.append(dict(paths.pop(key),reason='Historical fixed Worker in priorQA baseline;R17explicitlyauthorized sourceedit;oldbytes preservedfrozenR15 andpriorbaseline NOTnormalized'))
assert len(excluded)==1
write(C/'MASTER_R17_QA_BASELINE_AUTHORIZED_SOURCE_RECONCILIATION_20261010.json',{'at':at,'historical_baseline':str(oldbase),'historical_baseline_sha256':sha(oldbase),'excluded_current_paths':excluded,'old_QA_evidence_unchanged':True,'current_source_admitted_ONLY_frozenR17':True,'guard_session':31503})
'''+needle
assert needle in tail
tail=tail.replace(needle,replacement)
Path('Dispatcher/Tools/master_continue_r17_qa_after_authorized_source_reconciliation_20261010.py').write_text(prefix+tail,encoding='utf8')
