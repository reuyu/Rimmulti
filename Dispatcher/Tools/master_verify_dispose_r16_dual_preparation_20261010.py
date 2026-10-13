from pathlib import Path
import json,datetime,hashlib,shutil,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def pin(f):
 p=Path(f['path']);assert p.is_file() and sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size')),str(p)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None;bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);a=b['tasks'][-1];T=Path(a['completion_path']).parent;ac=read(Path(a['completion_path']));assert a['dispatch_id'].endswith('7972af00')
assert all(ac[k]==a[k] for k in ['dispatch_id','wp_id','wp_revision']) and ac['envelope']==19 and ac['producer']=='A' and ac['e1_verdict']=='PREPARATION_COMPLETE_NATIVE_UNTESTED' and len(ac['artifacts'])==10
for f in ac['artifacts']:pin(f)
baseline=read(Path(a['scope_baseline_path']));assert len(baseline['fixed_current_engine_paths'])==9
for f in baseline['fixed_current_engine_paths']:pin(f)
for f in ac['fixed_current_engine_paths_verification']:p=Path(f['path']);assert f['baseline_sha256']==f['current_sha256']==sha(p) and p.stat().st_size==f['size']
pres=read(C/'MASTER_R16_A_PRESERVATION_AT_SOL_COMPLETION_20261010.json');assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
assert [len(pres[k]) for k in ['engine_archive_checks','prior_candidate_checks','pipeline_preservation_checks','qa_preservation_checks']]==[19,1561,206,7002]
ai=read(T/'RUNTIME_READINESS_INVENTORY.json');assert len(ai['files'])==7
for f in ai['files']:pin({'path':f['absolute_path'],'sha256':f['sha256'],'bytes':f['size_bytes']})
assert sum(f['size_bytes'] for f in ai['files'])==33030151
Q=R/'QA-Tactical-Engine/GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010';qc=read(Q/'COMPLETION.json');rid=qc['result_id'];assert rid==c['sol_current_result_id'] and qc['delivery_id']==c['sol_current_attempt_id'] and qc['verdict']=='PREPARATION_COMPLETE_NATIVE_UNTESTED'
assert sha(Q/'COMPLETION.json')=='439064FB7BCE1A3C10227DE30181B97EDFD6B01BE0047529E6E89AF46AA05167' and sha(Path(qc['report']['path']))=='0D9070F22812830548D69512FBE47F0A86D62E30BFCCB6E989DCD19972164433'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:pin(qc[k])
manifest=read(Q/'EVIDENCE_MANIFEST.json');assert len(manifest['files'])==41
for f in manifest['files']:pin(f)
binding=read(Q/'ACK_COMPLETION_BINDING.json');assert binding['result_id']==rid and binding['initial_ack_bytes_preserved']
for k in ['ack_initial','ack','report','evidence_manifest','result_index']:pin(binding[k])
base=Path(c['sol_current_delivery']['baseline_path']);assert sha(base)==c['sol_current_delivery']['baseline_sha256'];files=read(base)['files'];assert len(files)==8932
expected={f['path']:(f['sha256'],f['bytes']) for f in files}
for f in files:pin(f)
for n in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 x=read(Q/n);assert x['protected_unique_paths']==8932 and {f['path']:(f['sha256'],f['bytes']) for f in x['files']}==expected
line=read(Q/'R16_FROZEN_LINEAGE.json');master=read(C/'MASTER_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_E1_VERIFICATION_20261010.json')['lineage']
for q in line['candidates']:
 m=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==m['dll_sha256'] and q['pdb_sha256']==m['pdb_sha256'] and q['guid']==q['codeview_guid']==m['pdbGuid']==m['codeviewGuid'] and len(q['documents'])==4
 for d in q['documents']:
  md=next(x for x in m['documents'] if x['path']==d['path']);assert d['matched'] and d['pdb_hash']==d['actual_sha256']==md['actual']==md['expected']==sha(Path(d['frozen_source_path']))
anchors=read(Q/'SOURCE_ANCHOR_INDEX.json')['rows'];assert len(anchors)==17
for r in anchors:
 anchor=r['anchor'];pin(anchor['source']);pin(r['verbatim_numbered_extract']);src=Path(anchor['source']['path']).read_text(encoding='utf-8-sig').splitlines();actual=Path(r['verbatim_numbered_extract']['path']).read_text(encoding='utf-8-sig').splitlines();assert actual==[f'{i}: {src[i-1]}' for i in range(anchor['first_line'],anchor['last_line']+1)],r['name']
ws=(R/'Dispatcher/CANDIDATES/G05R15-03649052/scratch/WorkerBridgeMod/Source/WorkerBridge.cs').read_text(encoding='utf-8-sig');assert ws.count('AdmittedOperatorValidatorSha')==1 and ws.count('ConfigureExpectedPackagePolicy')==0
assert len(read(Q/'INDEPENDENT_OPERATOR_AUTHORITY_MATRIX.json')['rows'])==16 and len(read(Q/'PROSPECTIVE_ADMISSION_CRITERIA.json')['rows'])==12
rg=read(Q/'RUNTIME_GAP_REVIEW.json');assert len(rg['files'])==7 and len(rg['missing_or_unadmitted_assets'])==11 and rg['historical_failure_cause']=='UNKNOWN'
for f in rg['files']:pin(f)
for f in rg['missing_or_unadmitted_assets']:assert not f['exists'] and not Path(f['path']).exists()
scope=read(Q/'ACTUAL_PREPARATION_SCOPE.json');assert all(scope[k]==0 for k in ['production_changes_builds','candidate_build_load_execute','QA_runner_build_load_execute','provider_cache_calls','runtime_game_native_operator_calls','old_runner_negative_stale_mismatch_rejection_race_adverse_calls','assets_copy_install_restore','A_inprogress_R16_output_reads_or_changes'])
snap=json.loads(read(C/'MASTER_SOL_R16_COMPLETION_SNAPSHOT_20261010.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['revision']==105
thread=json.loads(read(C/'MASTER_SOL_R16_ACTUAL_THREAD_READ_20261010.json')['content'][0]['text']);rt=read(Q/'RETURN_TOOL_PROOF.json');ds=read(Q/'DELIVERY_STATUS.json');assert ds['attempts']==rt['terminal_delivery_attempt']==1 and not rt['actual_tool_result'].get('isError') and json.loads(rt['actual_tool_result']['content'][0]['text'])['threadId']==c['master_thread_id']
sends=[x for x in thread['turns'][0]['items'] if x.get('type')=='mcpToolCall' and x.get('tool')=='send_message_to_thread' and x.get('arguments',{}).get('prompt')==rt['prompt']];assert len(sends)==1 and sends[0]['status']=='completed'
F=R/'Dispatcher/CANDIDATES/G05R16PREP-7972af00';assert not F.exists();F.mkdir();frozen=[]
for src in [Path(f['path']) for f in ac['artifacts']]+[Path(a['completion_path'])]:
 dst=F/src.name;shutil.copy2(src,dst);assert sha(dst)==sha(src);frozen.append({'original_path':str(src),'frozen_path':str(dst),'sha256':sha(dst),'size':dst.stat().st_size})
fm=T/'MASTER_R16_PREPARATION_REVIEW_FREEZE_MANIFEST.json';write(fm,{'at':at,'dispatch_id':a['dispatch_id'],'kind':'POSTCOMPLETION_PREPARATION_ARTIFACTS_NO_NEW_PRODUCTION_CANDIDATE','files':frozen,'runtime_e2_released':False})
review=H/'MASTER_REVIEW_ENGINE_GATE05_R16_DUAL_OPERATOR_NATIVE_PREPARATION_20261010.md';verdict='ACCEPTED_INDEPENDENT_READINESS_PREPARATION_A_CAUSAL_AND_AUTHORITY_OVERCLAIMS_CORRECTED_NATIVE_UNTESTED'
review.write_text(f'''# R16 dual readiness Master disposition
At {at}. {verdict}. A {ac['result_id']} terminal/Sol{rid} actualcompletedidle105. No R16 productioncandidate/nativeE2/Highclosure;Engine002006/Pipeline007/schema/G-Q1OPEN/FoundationHOLD.

Verified A10artifacts/current9engine/runtime7SHA-size33030151bytes/archive19/prior1561/Pipeline206/QA7002;11postcompletion producer docs frozen {fm} SHA{sha(fm)}. Sol41evidence/8932protected beforeafter/17verbatimsource extracts/16logicaldimensions/12futuremilestones/11assetabsence/DebugReleasePE-PDBsource4/4/report-index-ACKbinding-COMPLETION-actualdirectsend matched. Exact production candidate remains frozenR15 selected835E...MVID4fb1a25f...,no new runtime PASS. Installedmismatch unchangedOPEN/actorUNKNOWN.

Controlling corrections to A (originals preserved):
1. Missingassets observed now are readiness gaps;historical5secondkillcause UNKNOWN. Reject completelydiagnosed/reproducible/notpermissions-antivirus-DRM claims without actualhistoricalevidence;no new run.
2. Admittedpath enforcement is conditionalnonemptyconfig;AdmittedOperatorValidatorSha declaration1/use0. Bind providedpath/PID/start is not actualMainModule-SHA/operator-ownedconfig/launch proof.
3. Sixteen carried/equalityfields not16nativePASS;Complete explicitcurrentGeneration/currentmode,stablemapidentity/listindex/clamp/fallback andpromotionmode consumption remain qualified.
4. Awake bridgeport/declareduserdataoverride is not ownedpolicy/profile/isolateduserdata bootstrap. AuditedWorker ConfigureExpectedPackagePolicy calls0;R15unitPASS doesn't initialize native.
5. MD129 role-awarecontrolplane earlyreturns require disposition;generic failclosed label not comprehensive revokeproof. Queryerrors remainseparate,no negative execution.
6. Hardcoded settings/patchAST exclusion is not accepted blanket materialnoninterference. Requiredcontent/guardparity/patchsettings stays OPEN;no automatic newADR forroutinefix.
7. Wait30lines+XMLguard15lines not sufficient minimalsole repair;ownedbootstrap/admittedruntime mandatoryactualexeSHA-path-options/policyuserdata first. Blocking Unitymainthread wait not adopted;native lifetime later.
8. CLI/libraryfolders/DLC/ModsConfig values and exactloaderlayout are prospective assumptions until verified;versiontextdeclaredonly. No license/loader genericstatement establishes actual provenance.
9. Privateprotectedrawtask/result versusredactedpublic evidence;nonce/PID/UTC diagnostic alone notissuer/worldorder. Filetransport allowed,no cryptographynewrequirement.

Adopt Sol minimal normalbootstrap/admitted-launch configuration +strict failclosed path/SHA/options andvalidpolicy/isolateduserdata initialization as R17 narrow implementation direction. Native/game/operatorProcess.Start/oldrunner/adverse/promotion/assetscopy not released. Preserve R15Census/codec;A soleproductionwriter. Freshcandidatefreeze+source/PDB andindependenttargetednormalQA required beforelatercompleteisolatedruntime+onepositiveSTEP1-SEAL-STAGE→freshREAD_ONLYvalidator→internalreceipt,STOPbeforepromotion. Currentcontext/target/revocation gaps must be resolved before laternative admission.

Adopt NATIVE_PHASE_OUTPUT_PROTOCOL: Worker lives throughchild andinternalreceipt;freezeimmutableprelaunchsealed/task/stage/context phase,validator EVERYfinaloutput afterexit,Worker EVERYfinaloutput afterreceipt+exit,allfirstexperimentfinal inventories beforeanylaterexperiment. RejectfictionalWorker wholefinal inventory beforechild.

Next R17 preparing NOT_SENT until concreteapprovedWP/freshCUidle. Samehourly pausependingtool afterAterminal;originalSolidle/no duplicateQA. No routinehumancontinue needed.
''',encoding='utf8')
vp=C/'MASTER_R16_DUAL_PREPARATION_COMPLETION_VERIFICATION_20261010.json';assert not vp.exists();proof={'at':at,'guard_run':'MASTER-SOL-R16-PREP-COMPLETE-20261010-01','guard_session':25888,'guard_pid':21488,'verification_status':'MASTER_DISPOSED','master_verdict':verdict,'master_review':str(review),'master_review_sha256':sha(review),'A_result_id':ac['result_id'],'A_completion_sha256':sha(Path(a['completion_path'])),'A_artifacts':10,'A_frozen_files':11,'A_frozen_manifest':str(fm),'A_frozen_manifest_sha256':sha(fm),'Sol_result_id':rid,'Sol_delivery_id':qc['delivery_id'],'Sol_completion_sha256':sha(Q/'COMPLETION.json'),'Sol_report_path':qc['report']['path'],'Sol_report_sha256':sha(Path(qc['report']['path'])),'Sol_manifest_path':str(Q/'EVIDENCE_MANIFEST.json'),'Sol_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'Sol_evidence_files':41,'protected_paths_master_rehashed':8932,'source_extracts_master_compared':17,'normal_milestones':12,'context_dimensions':16,'actual_sol_snapshot':snap,'runtime7_matched':True,'historical_native_cause':'UNKNOWN','runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','next_direction':'R17_OWNED_BOOTSTRAP_ADMITTED_LAUNCH_IMPLEMENTATION_PREPARE_NOT_SENT','monitor_pause':'PENDING_TOOL'};write(vp,proof)
rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp)
for who,result,completion in [('A',ac['result_id'],proof['A_completion_sha256']),('Sol',rid,proof['Sol_completion_sha256'])]:
 assert not any(x.get('result_id')==result for x in rr['processed_results']);rr['processed_results'].append(dict(proof,result_id=result,completion_sha256=completion,recipient=who,proof_path=str(vp),proof_sha256=sha(vp)))
rr['updated_at']=at;write(rp,rr)
a.update(status='COMPLETED_PREPARATION_REVIEWED_A_OVERCLAIMS_CORRECTED_NATIVE_UNTESTED',result_id=ac['result_id'],completion_sha256=proof['A_completion_sha256'],master_disposition=str(review),frozen_manifest=str(fm),frozen_manifest_sha256=sha(fm),independent_qa_result_id=rid,runtime_verdict='NO_R16_PRODUCTION_CANDIDATE_NATIVE_UNTESTED_FULL_GATE_NOT_RELEASED',monitor_status='PAUSE_PENDING_TOOL',updated_at=at);b['updated_at']=at;write(bp,b)
c.update(a_status='R16_PREPARATION_TERMINAL_REVIEWED_CORRECTIONS_ADOPTED',a_latest_result=proof,sol_status='R16_INDEPENDENT_PREPARATION_COMPLETE_ACCEPTED_NATIVE_UNTESTED_IDLE',sol_latest_result=proof,last_sol_cursor=snap['cursor'],sol_next_action='NO_DUPLICATE_QA_AWAIT_NEW_R17_CANDIDATE_OR_NECESSARY_DISJOINT_PREPARATION',updated_at=at);c['sol_current_delivery'].update(status='COMPLETED_PREPARATION_ACCEPTED_NATIVE_UNTESTED',result_id=rid);c['master_monitor_automation']['desired_status']='PAUSED';write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',current_runtime_idle_verified=True,last_result_id=rid,last_runtime_observation_cursor=snap['cursor'],latest_review=str(review));s['endpoints']['a'].update(execution_phase='TERMINAL_R16_REVIEWED_NO_ACTIVE_WP',current_runtime_idle_verified=False,last_result_id=ac['result_id'],latest_review=str(review));s['latest_master_review']=proof;s['updated_at']=at;write(sp,s)
para=f'\n\n## LOCAL-R16-DUAL-PREPARATION-MASTER-DISPOSITION — {at}\nA {ac["result_id"]} terminal10artifacts/current9/runtime7SHA-size matched,11docs frozen(no newcandidate);originalSol {rid} completedidle105/41evidence/8932protected/17sourceextracts/16dimensions/12futuremilestones/11assetabsence/PDBsource4/4 matched. {verdict}. Ninecontrollingcorrections in {review};originalsunchanged/historicalkillcauseUNKNOWN/installedactorUNKNOWNOPEN. Adopt normalbootstrap/admittedruntime mandatoryactualexeSHA-path-options+validpolicy/isolateduserdata and nestedprocessphase protocol. NextR17implementation preparingNOT_SENT/native-game-ProcessStart-adverse-promotion-assetscopy NOTreleased. Samehourly pausePENDINGtool,originalSolidle/no duplicateQA. Engine002006/Pipeline007/schema/G-Q1OPEN/FoundationHOLD. Proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
e=dict(proof,event_id='MASTER-R16-DUAL-PREPARATION-DISPOSITION-20261010-01',type='A_AND_INDEPENDENT_QA_READINESS_MASTER_DISPOSITION')
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e)+'\n')
print(json.dumps({'verdict':verdict,'A_artifacts':10,'A_frozen_docs':11,'QA':41,'protected':8932,'next':'R17_PREPARE_NOT_SENT','monitor':'PAUSE_PENDING_TOOL'},ensure_ascii=True))
