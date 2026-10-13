from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];PKG=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
state=json.loads((PKG/'DISPATCHER_STATE.json').read_text(encoding='utf-8'))
journal=[json.loads(x) for x in (PKG/'DISPATCH_JOURNAL.jsonl').read_text(encoding='utf-8').splitlines()]
baseline=json.loads((OUT/'local_identity_verification.json').read_text(encoding='utf-8'))
pipeline_changed=[r['path'] for r in baseline['pipeline'] if sha(Path(r['path']))!=r['sha256']]
production_changed=[r['path'] for r in baseline['prior_production_freeze'] if not Path(r['path']).exists() or sha(Path(r['path']))!=r['sha256']]
freeze=json.loads((OUT/'GATE05_LOCAL_FREEZE_MANIFEST.json').read_text(encoding='utf-8'))
engine_changed=[p for p,v in freeze['files'].items() if not Path(p).exists() or sha(Path(p))!=v['sha256']]
manifest=json.loads((PKG/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
wp_expected={x['path']:x['sha256'].upper() for x in manifest['files'] if x['path'].startswith('WP_')}
wp_unchanged={n:sha(PKG/n)==s for n,s in wp_expected.items()}
back=OUT/'premerge/ROOT_AGENTS.md';agents_preserved=(ROOT/'AGENTS.md').read_bytes().startswith(back.read_bytes())
sol=next(x for x in state['queued_work'] if x['recipient']=='sol');a=next(x for x in state['queued_work'] if x['recipient']=='a')
checks={'migration_bootstrap_verified':state['migration_bootstrap_verified'],
 'bootstrap_report_current_sha_match':sha(PKG/'IDE_BOOTSTRAP_VERIFICATION.md')==state['bootstrap_verification_sha256'],
 'original_bootstrap_report_sha_match':sha(Path(state['bootstrap_checkpoint_report']))==state['bootstrap_checkpoint_report_sha256'],
 'journal_unique_event_ids':len({x['event_id'] for x in journal})==len(journal),
 'sol_single_delivery_record':len(state['deliveries'])==1 and state['deliveries'][0]['recipient']=='sol',
 'sol_in_progress':sol['status']=='IN_PROGRESS' and sol['delivery_status']=='SENT',
 'a_not_sent':a['status']=='NOT_SENT','automation_disabled':not state['automation_enabled'],
 'manual_submission_active_run_cleared':state['active_run'] is None,'original_wp_unchanged':all(wp_unchanged.values()),
 'agents_original_prefix_preserved':agents_preserved,'pipeline_identities_unchanged':not pipeline_changed,
 'prior_353_production_files_unchanged':not production_changed,'engine_local_freeze_unchanged':not engine_changed}
result={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
        'checks':checks,'wp_checks':wp_unchanged,'pipeline_changed':pipeline_changed,'production_changed':production_changed,'engine_changed':engine_changed,
        'scope':'local recovery records/frozen artifacts; no runtime E1/E2 rerun or new closure',
        'current_governance_hashes':{n:sha(PKG/n) for n in ['IDE_BOOTSTRAP_VERIFICATION.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md','DISPATCHER_STATE.json','DISPATCH_JOURNAL.jsonl']}}
(OUT/'final-record-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));assert all(checks.values())
