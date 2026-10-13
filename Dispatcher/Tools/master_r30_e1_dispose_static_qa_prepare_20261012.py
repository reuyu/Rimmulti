from pathlib import Path
import json,sys,hashlib,shutil,tomllib
sys.stdout.reconfigure(encoding='utf-8')
import master_r29_s1_stop_prepare_s2_20261012 as m
def ck(v,key='path'):
 a=m.row(Path(v[key]));assert a['sha256']==v['sha256'] and a['bytes']==v.get('bytes',v.get('size')),v[key];return a
def main():
 cs=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];T=Path(t['instruction_path']).parent
 assert cs['active_operation'] is None and t['wp_revision']=='GATE05-R30-HANDOFF'
 comp=m.read(T/'COMPLETION.json');assert all(comp[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and comp['envelope']==33 and comp['status']=='COMPLETED'
 rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(v.get('result_id')==comp['result_id'] for v in rec['processed_results'])
 verified=[ck(v) for v in comp['artifacts']];assert len(verified)==33
 for v in t['production_fixed_files']:m.check(v)
 cfgp=Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml');cfg=tomllib.loads(cfgp.read_text(encoding='utf-8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==cs['master_thread_id']
 base=m.C/'MASTER_R30_HANDOFF_PROTECTED_BASELINE_20261012.json';basej=m.read(base);assert len(basej['files'])==15296
 for v in basej['files']:m.check(v)
 scope=m.read(Path(t['scope_baseline_path']));assert m.row(Path(t['scope_baseline_path']))['sha256']==t['scope_baseline_sha256']
 oldman=Path(b['tasks'][-2]['frozen_manifest']);oldj=m.read(oldman)
 for v in oldj['files']:ck(v,'frozen_path')
 osrc=next(Path(v['frozen_path']) for v in oldj['files'] if v['original_path']==scope['Worker_original']['path']);ck(scope['Worker_original'],key='path') if False else None
 ob=osrc.read_bytes();src=Path(scope['Worker_original']['path']);nb=src.read_bytes();assert hashlib.sha256(ob).hexdigest().upper()==scope['Worker_original']['sha256']
 diff=m.read(T/'SOURCE_SCOPE_DIFF.json');permissions={v['id']:(v['start'],v['end']) for v in scope['allowed_byte_spans']};oi=ni=0;outside=[]
 for z in sorted(diff['authorized_spans'],key=lambda v:v['orig_range'][0]):
  a,e=z['orig_range'];x,y=z['new_range'];assert permissions[z['span_id']]==(a,e)
  assert ob[oi:a]==nb[ni:x] and hashlib.sha256(nb[x:y]).hexdigest().upper()==z['new_sha256']
  outside.append(dict(old_range=[oi,a],new_range=[ni,x],bytes=a-oi,sha256=hashlib.sha256(ob[oi:a]).hexdigest().upper()));oi,ni=e,y
 assert ob[oi:]==nb[ni:];outside.append(dict(old_range=[oi,len(ob)],new_range=[ni,len(nb)],bytes=len(ob)-oi,sha256=hashlib.sha256(ob[oi:]).hexdigest().upper()));assert len(outside)==6 and sum(v['bytes'] for v in outside)==261380
 ident=m.read(T/'CANDIDATE_IDENTITY.json');PE={}
 for mode in ['Debug','Release']:
  tool=m.read(m.C/('MASTER_R30_'+mode.upper()+'_PE_PDB_TOOL_20261012.json'));assert tool['exit_code']==0;pe=json.loads(tool['output']);assert pe['codeviewMatched'] and len(pe['documents'])==4 and all(v['matched'] for v in pe['documents'])
  k=ident[mode.lower()+'_candidate'];assert m.row(Path(k['assembly_path']))['sha256']==k['sha256'] and m.row(Path(k['pdb_path']))['sha256']==k['pdb_sha256'] and pe['mvid']==k['mvid'] and pe['codeviewGuid']==k['codeview_guid'];PE[mode]=pe
 drift=[]
 for v in oldj['files']:
  p=Path(v['original_path'])
  if 'EngineGate05R29StartupPair' in str(p):
   a=m.row(p) if p.exists() else None
   if a is None or a['sha256']!=v['sha256']:drift.append(dict(original_frozen_reference=v,current_original=a))
 assert len(drift)==12
 driftp=m.C/'MASTER_R30_ORIGINAL_R29_E1_LINEAGE_DRIFT_20261012.json';m.create(driftp,dict(at=m.now(),files=drift,old_R29_frozen132_matched=True,initial_15296_baseline_matched=True,producer_report_explicit_old_runner_path_reuse=True,original_E1_raw_and_runner_overwrite_not_authorized_by_R30_WP=True,no_restore_or_old_freeze_rewrite=True))
 E=m.R/'scratch/EngineGate05R29StartupPair';host=m.read(E/'HOST_TELEMETRY.json');runs=m.read(T/'E1_NORMAL_RESULTS.json')['runs'];assert len(runs)==2
 for r in runs:
  assert r['exit_code']==0 and r['pid']>0
  for key in ['stdout','stderr','execution_report']:assert m.row(Path(r[key+'_path']))['sha256']==r[key+'_sha256']
  assert r['report_summary']['wp_revision']=='GATE05-R29-STARTUP-PAIR'
 paths={v['path']:Path(v['path']) for v in verified}
 for root in [T,E,m.R/'scratch/WorkerBridgeMod/Source/bin',m.R/'scratch/WorkerBridgeMod/Source/obj']:
  for p in root.rglob('*'):
   if p.is_file():paths[str(p)]=p
 for v in t['all9_before']+t['production_fixed_files']:paths[v['path']]=Path(v['path'])
 F=m.R/'Dispatcher/CANDIDATES/G05R30-16ce928f';assert not F.exists();F.mkdir();frozen=[]
 for p in paths.values():
  target=F/p.relative_to(m.R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);a=m.row(p);assert m.row(target)['sha256']==a['sha256'];frozen.append(dict(a,original_path=str(p),frozen_path=str(target)))
 fm=T/'MASTER_GATE05_R30_HANDOFF_REVIEW_FREEZE_MANIFEST.json';m.create(fm,dict(at=m.now(),files=frozen,scope='R30_POST_COMPLETION_SOURCE_BINARY_PDB_AND_E1_RAW_EXACT_FREEZE_STATIC_ADMISSION_ONLY',original_R29_raw_drift_not_normalized=True))
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R30_HANDOFF_E1_20261012.md';assert not review.exists()
 verdict='RECEIPT_OWNER_COHORT_CORRECTIONS_CREDITED_REQUIRED_MODE_CUSTODY_AND_EVIDENCE_REVISION_REQUIRED_NATIVE_NOT_RELEASED'
 review.write_text(f'''# R30 E1 — Master 判定

{verdict}. Actual {comp['result_id']}/{t['dispatch_id']}/envelope33 collected. Artifacts33 SHA/size, baseline15296/fixed3 and oldR29frozen132 matched. New exact freeze{len(frozen)} SHA{m.row(fm)['sha256']}. Debug9142C63AF18E2AE028D9E44AC36277F2FEBFFBB7AE8B6AF2437D12CED288C706/MVID71b83cb9-f67f-4520-b611-6b8d0d4d2860/matchingPDB4BCF43B7...; ReleaseD6D4EFEE.../MVID7ffbba39-9a18-434b-ac07-93886e829c9f/PDB4E179AEA...; both Master PE CodeView/PDB/source4of4 matched. Candidate execution/build0. All5authorized spans and ENTIREoutside6segments261380bytes independently matched; sourceSHA{m.row(src)['sha256']}. Report/control-flow prose uses different newranges/sizes from actual SOURCE_SCOPE_DIFF; actual byte map controls.

Credited SOURCE-only: correct receipt↔installed _activeAdmissionReceipt and receipt.Snapshot↔active config comparisons, pending overwrite rejection, bool return checked before AddComponent, owner-scoped cleanup and matched-owner cohort failure earlyreturn, retained instance mode on destruction/M05hold. No source correction is native/issuer/high closure proof.

Remaining handoff blocker: `_isPairRequiredMode=false` default and only set INSIDE TryAcquire when pending owner matches. Bootstrap does not establish an independent durable required-pairmode/owner cohort before AddComponent. If pending absent/cleaned/consumed or wrong owner, acquire returnsfalse with mode stillfalse; Awake's `_isPairRequiredMode && profile==null` gate and same-mode M05hold can fall through legacy. Preserve strict unknown/native behavior; no adverse reproduction. Requirement is required mode known before acquire, scoped owner+receipt mode remains after pending consumed/cleanup, unknown/unmatched component cannot gain legacy startup from installed pair receipt. Check Unity overloaded null/lifetime guards via actual reference metadata and state assumptions separately; no native guarantee.

Producer HANDOFF_CONTROL_FLOW says Unity invokes Awake synchronously and catch catches Awake exceptions, neither independently observed nor adopted. Awake has its own try/catch. Static source table is declaration, not actual native calltrace. Pure 6Pair+4Capture normal labels do not exercise modified handoff code. Two host exits0 and local runner selected9142... bytes observed, but actual loadedmanaged/MVID pre-post/CLR/source/complete prospective compile pins and fulltyped/raw/copy oracle proof remain missing. FINAL_PRE_RUN_MANIFEST generated18:13:20 after normal runtime timestamps18:09:51 and includes built candidates, vague compiler4.8 metadata. Do not rerun or promote old runner evidence to independent E2.

Producer reused/rebuilt original `scratch/EngineGate05R29StartupPair/Harness` and overwrote its two run outputs/HOST_TELEMETRY:12 original paths differ from R29 freeze. This violates task's own-new-runner/oldraw preservation requirement even though frozen132 and protected QA originals survive. R30 run report still identifies R29/envelope32. Record drift as new lineage; do not restore originalpaths, edit old freeze/QA, or silently inherit oldPASS. {driftp} controls. Source/evidence integrity defect remainsOPEN pending separate producer packaging remedy. Original ACK scope field8CC... still differs immutable actual85BF...; no separate correction found. New source/model contracts are not inferred from a hash label.

SourceHigh1 stillOPEN; carrierHigh2/publisherHigh3 unchangedOPEN. Next original Sol fresh independent read-only static review on exact new frozen candidate/source/protected evidence; no candidate/compiler/runner/game/native/operator/global/adverse execution. Normal PURE methods' entirebytes unchanged supports inspection scope; existingR29PASS is not a verdict on newR30. Review missing-custody branches/Unity lifetime metadata/prose vs actualbyte map/provenance and ownrawdrift independently, challenge Master conclusions if evidence differs. Further A repair NOT SENT pending independent findings. Native E2 NOT_RELEASED/Engine002006/Pipeline007/current schema/G-Q1 OPEN/Foundation HOLD/known installed incidentOPENactorUNKNOWN.

Hourly actual PAUSED60min173charcorrectMastertarget after A terminal; directSolreport path continues. Master evidence definitions found in docs/MASTER_PROJECT_STATE_MSR-043.md706..709: E0 analytical/contract,E1 developer feasibility,E2 independent verification,E3 Production/regression. Referenced MASTER_ADR_EVIDENCE_POLICY.md is absent from actual rg inventory; no invented replacement/adoption. This uncertainty does not relax current E1/E2 boundary.
''',encoding='utf-8')
 proof=m.C/'MASTER_GATE05_R30_HANDOFF_E1_VERIFICATION_20261012.json';summary=dict(at=m.now(),dispatch_id=t['dispatch_id'],result_id=comp['result_id'],completion=m.row(T/'COMPLETION.json'),master_verdict=verdict,review=m.row(review),artifact_count=33,protected_paths=15296,frozen_manifest=m.row(fm),frozen_files=len(frozen),outside_segments=outside,outside_bytes_total=261380,candidate_identity=ident,Master_PE_PDB_Source4of4=PE,original_R29_E1_drift=m.row(driftp),original_R29_frozen132_matched=True,normal_host_runs=[dict(culture=r['culture'],pid=r['pid'],exit_code=r['exit_code'],run_identity=r['report_summary']['wp_revision']) for r in runs],normal_runtime_modified_handoff_executed=False,Master_build_candidate_execution=0,High3='OPEN',Foundation='HOLD',native_E2='NOT_RELEASED',monitor_config=cfg,guard_run='MASTER-R30-HOURLY-20261012-1905-01',guard_session=4089)
 m.create(proof,summary)
 integrity=m.C/'MASTER_DEFECT_ENGINE_G05_R30_E1_LINEAGE_20261012.json';m.create(integrity,dict(at=m.now(),defect_id='ENGINE-G05-R30-E1-LINEAGE-20261012-04',severity='High',status='OPEN',kind='ORIGINAL_PRODUCER_EVIDENCE_PRESERVATION_AND_PROVENANCE',evidence=m.row(driftp),old_R29_frozen_copies_preserved=True,closure_requires='fresh authorized new-root prospective runner/evidence with exact ownidentity, retain both oldfrozen and drift snapshot; Master review, no restore or oldPASSinheritance'))
 t.update(status='COMPLETED_REVIEWED_REQUIRED_MODE_AND_EVIDENCE_REVISION_REQUIRED',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_disposition=verdict,master_review_path=str(review),frozen_manifest=str(fm),frozen_manifest_sha256=m.row(fm)['sha256'],qa_runtime_status='NEW_INDEPENDENT_STATIC_PREPARING_NOT_SENT',same_wp_notice_delivery_status='CANCELLED_UNSENT_SUPERSEDED_BY_TERMINAL_REVIEW',monitor_status='PAUSED_60MIN');b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 cs.update(a_status=t['status'],a_latest_completion=dict(summary,proof=m.row(proof)),updated_at=m.now());cs['master_monitor_automation'].update(status='PAUSED',desired_status='PAUSED',interval_minutes=60,configuration_verified=True,configuration_checked_at=m.now(),pause_reason='R30 terminal Master reviewed; fresh independent static QA direct');m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',cs)
 rec['processed_results'].append(dict(at=m.now(),recipient='A',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(proof)));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['a'].update(current_status=t['status'],current_wp=t['wp_id'],last_result_id=comp['result_id'],latest_review=str(review),current_runtime_idle_verified=False);ds['master_monitor_automation']=cs['master_monitor_automation'];ds['latest_master_review']=str(review);ds['updated_at']=m.now();m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(at=m.now(),event='R30_E1_DISPOSED_NEW_FROZEN_STATIC_ONLY',dispatch_id=t['dispatch_id'],result_id=comp['result_id'],proof=m.row(proof),old_original_E1_drift12=True,old_frozen132_and_QA_preserved=True))
 m.append_delta('LOCAL-R30-HANDOFF-E1-MASTER-STATIC-ADMISSION',verdict+'. Artifacts33/baseline15296/fixed3/oldfrozen132 matched,newfreeze'+str(len(frozen))+'/Debug9142...MVID71b8.../ReleaseD6D4...MVID7ffb...bothPDBsource4of4;5spans/outside261380bytes match. Receiptcohort/boolset/ownercleanup improvementsSOURCEcredited;requiredmode onlyonmatchedpending anddefaultfalse missing-beforeacquire/fallthrough remainsOPEN. Producer oldR29 E1 root12paths overwritten,reusedrunner/wrongR29runidentity/afterrunprepin/fulltyped-load gaps;newHighE1LINEAGE04OPEN,oldfrozenQAintact/no restore. ACK scopewronghash remains/evidenceprosewrongranges/syncAwakeunadopted. New Sol independentstaticONLY preparednextNOTSENT/no runtimeorPUREbuildcall. SameactualhourlyPAUSED/directreport;newA NOTSENTpendingSol findings. Highhandoff-carrier-publisherOPEN/FoundationHOLD/nativeE2NOTRELEASED. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status='R30_E1_DISPOSED_STATIC_ONLY',proof=m.row(proof),frozen_files=len(frozen),old_original_E1_drift=12,next='PREPARE_ORIGINAL_SOL_STATIC_WP'),ensure_ascii=False))
if __name__=='__main__':main()
