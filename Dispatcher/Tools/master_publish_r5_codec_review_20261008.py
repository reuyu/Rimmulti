from pathlib import Path
import json,datetime,hashlib,shutil,sys
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();vp=H/'coordination/MASTER_GATE05_R5_CODEC_E1_VERIFICATION_20261008.json';p=read(vp);bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];T=Path(t['completion_path']).parent
# Verify before/after rows against the correct exact historical/final lineage.
oldmap={x['original_path'].lower():x for x in read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']))['files']}
checks=[]
for label in ['BEFORE','AFTER']:
 d=read(R/f'scratch/EngineGate05R5Codec/ENGINE_FREEZE_{label}.json')
 for x in d['entries']:
  original=(R/x['path']).resolve();actual=Path(oldmap[str(original).lower()]['frozen_path']) if label=='BEFORE' else original
  checks.append({'kind':label,'path':str(original),'actual_path':str(actual),'matched':sha(actual)==x['sha256'],'size_matched':actual.stat().st_size==x['size_bytes']})
assert all(x['matched'] and x['size_matched'] for x in checks)
review=H/'MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_E1_20261008.md';p.update(master_review_path=str(review),master_review_sha256=sha(review),master_review_status='DISPOSED',master_verdict='CODEC_IMPROVEMENTS_CREDITED_REVISION_REQUIRED_FULL_GATE_E2_NOT_RELEASED',scoped_admission='EXACT_SELECTED_DEBUG_DEFENSIVE_STATIC_AND_PURE_CODEC_UNIT_QA_ONLY',actual_release_mvid='7552980a-c4e1-4126-9451-e2114be623ae',declared_release_mvid='0e6b7cca-e02c-4af5-97da-5de31ec7aec3',before_after_checks=checks,monitor_pause='PENDING_TOOL');write(vp,p)
# Read/copy known managed dependency files only, no external mutation or execution.
deps=T/'FROZEN_MANAGED_QA_DEPENDENCIES';assert not deps.exists();deps.mkdir()
game=Path('C:/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed')
paths=[game/'Assembly-CSharp.dll',game/'UnityEngine.CoreModule.dll',game/'UnityEngine.dll',Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/294100/2009463077/Current/Assemblies/0Harmony.dll')]
dep_rows=[]
for original in paths:
 assert original.is_file();dest=deps/original.name;before=sha(original);shutil.copy2(original,dest);assert before==sha(original)==sha(dest);dep_rows.append({'original_path':str(original),'frozen_path':str(dest),'sha256':before,'size':dest.stat().st_size,'mvid':'NOT_YET_PARSED;QA metadata check permitted'})
dm=T/'MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json';write(dm,{'at':at,'scope':'Managed DTO/Serialize/Deserialize dependency metadata and loader support only;no native/game/profile execute admission','read_only_original_copy':True,'runtime_content_profile_admitted':False,'files':dep_rows})
receipt={k:p[k] for k in ['dispatch_id','wp_id','wp_revision','result_id','completion_sha256','master_verdict','frozen_manifest','frozen_manifest_sha256','frozen_files','master_review_path','master_review_sha256','scoped_admission']};receipt.update(at=at,type='A_R5_CODEC_E1_MASTER_REVIEW',verification_path=str(vp),verification_sha256=sha(vp),runtime_e2_released=False,closure_changed=False,foundation='HOLD',managed_dependency_manifest=str(dm),managed_dependency_manifest_sha256=sha(dm))
rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);assert not any(x.get('result_id')==receipt['result_id'] for x in r['processed_results']);r['processed_results'].append(receipt);r['updated_at']=at;write(rp,r)
t.update(status='COMPLETED_REVIEWED_REVISION_REQUIRED_SCOPED_CODEC_QA_ADMITTED',result_id=receipt['result_id'],completion_sha256=receipt['completion_sha256'],master_disposition=str(review),master_disposition_sha256=sha(review),runtime_verdict='FULL_GATE_E2_NOT_RELEASED',frozen_manifest=p['frozen_manifest'],frozen_manifest_sha256=p['frozen_manifest_sha256'],monitor_status='PAUSE_PENDING_TOOL',updated_at=at);b['updated_at']=at;write(bp,b)
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None;c.update(a_status='R5_TERMINAL_REVIEWED_REVISION_REQUIRED_SCOPED_CODEC_QA_ADMITTED',a_latest_result=receipt,last_sol_cursor='2745552a-f142-41a1-8eaf-3fe7b2d500ca:34',sol_status='R5_PREPARATION_ACCEPTED_IDLE_DISPOSITION_ACK_OBSERVED',updated_at=at);c['master_monitor_automation'].update(desired_status='PAUSED',future_run_after_engine_r5_resume_observed=True,first_run_after_engine_r5_resume_observed_at='2026-10-08T09:37:09.643Z');write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s.update(latest_master_review=receipt,updated_at=at,master_monitor_automation=c['master_monitor_automation']);s['endpoints']['a'].update(execution_phase='TERMINAL_REVIEWED',last_result_id=receipt['result_id'],last_result_verdict=receipt['master_verdict'],latest_review=str(review),current_runtime_idle_verified=False);write(sp,s)
paragraph=f'''\n\n## LOCAL-R5-CODEC-E1-MASTER — {at}\nActual {receipt['result_id']}/{receipt['dispatch_id']} terminal collected,21 artifact SHA/size/18 before-after rows matched,Debug/Release CodeView/PDB source4/4. Typed DTO+production Serialize/Deserialize credited;remaining supported disposition/content/order/evidence gaps,Release actual MVID7552980a-c4e1-4126-9451-e2114be623ae differs from producer Debug-MVID copy.113 post-completion frozen manifest SHA{p['frozen_manifest_sha256']}. Master CODEC_IMPROVEMENTS_CREDITED_REVISION_REQUIRED_FULL_GATE_E2_NOT_RELEASED;selected930B... only admitted for independent defensive static+pure normal codec unit QA. Actual loaded-content/game/native/operator/promotion E2 NOT_RELEASED;Master execution/build0. Archive19/prior619/Pipeline206/QA1241+fixed source matched,known installed incident unchanged OPEN. Same R5 hourly scheduled run actually observed09:37:09.643Z;existing monitor pause pending tool,Sol same original endpoint idle/completed/cursor34 (receipt notice,not new WP). New A corrective WP NOT SENT pending QA. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review};proof {vp};managed dependency metadata-only copy {dm}\n'''
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md',R/'AGENTS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
event=dict(receipt,event_id='MASTER-R5-CODEC-TERMINAL-REVIEW-20261008-01',event_type='A_TERMINAL_REVIEW',scheduler='PAUSE_PENDING',new_a_wp='NOT_SENT',new_sol_wp='PREPARING_BOUNDED_CODEC_ONLY')
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps({'review_at':at,'master_verdict':receipt['master_verdict'],'dependency_manifest':str(dm),'dependency_manifest_sha256':sha(dm),'before_after_rows':len(checks),'managed_dependency_files':len(dep_rows)},ensure_ascii=False))
