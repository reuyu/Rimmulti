from pathlib import Path
import json,sys,hashlib,struct,tomllib
sys.stdout.reconfigure(encoding='utf-8')
import master_r29_s1_stop_prepare_s2_20261012 as m
Q=m.R/'QA-Tactical-Engine/GATE05-R30-HANDOFF-INDEPENDENT-STATIC-S1-20261012'
def il_at(b,rva):
 pe=struct.unpack_from('<I',b,0x3c)[0];count=struct.unpack_from('<H',b,pe+6)[0];opt=struct.unpack_from('<H',b,pe+20)[0]
 off=None
 for i in range(count):
  h=pe+24+opt+i*40;vs,va,rs,rp=struct.unpack_from('<IIII',b,h+8)
  if va<=rva<va+max(vs,rs):off=rp+rva-va;break
 assert off is not None
 if b[off]&3==2:start=off+1;n=b[off]>>2
 else:assert b[off]&3==3;start=off+(struct.unpack_from('<H',b,off)[0]>>12)*4;n=struct.unpack_from('<I',b,off+4)[0]
 return b[start:start+n].hex()
def main():
 cs=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=cs['sol_current_delivery'];assert cs['active_operation'] is None
 comp=m.read(Q/'COMPLETION.json');assert comp['status']=='COMPLETED' and all(comp[k]==d[k] for k in ['delivery_id','wp_id','wp_revision','result_id'])
 rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(v.get('result_id')==comp['result_id'] for v in rec['processed_results'])
 assert m.row(Q/'COMPLETION.json')['sha256']=='E1602AD6B429C6E0D370AA0B060DCEAAA1E51DF4730350E01C226C9104420FA1'
 for v in comp['artifacts'].values():m.check(v)
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==em['file_count']==59
 for v in em['files']:m.check(v)
 actual={str(p) for p in Q.rglob('*') if p.is_file()};included={v['path'] for v in em['files'] if str(Q) in v['path']};excluded={str(Q/n) for n in em['excluded_cycles']+em['actual_unfinished_seal_logger_excluded']};assert actual-included==excluded
 index=m.read(Q/'RESULT_INDEX.json');ackbind=m.read(Q/'ACK_COMPLETION_BINDING.json');assert index['result_id']==ackbind['result_id']==comp['result_id']
 for v in index['artifacts'].values():m.check(v)
 for k in ['ACK_INITIAL','ACK_mirror','RESULT_INDEX']:m.check(ackbind[k])
 assert m.row(Q/'ACK_INITIAL.json')['sha256']=='841A3138544C824775152EEB48F5F21218700393ECB141560E1647B353F2F472'
 seal=m.read(Q/'finalize_seal.TOOL.json');assert seal['exit_code']==0 and seal['first_streams_complete'] and seal['candidate_compiler_runner_native_calls']==0
 for k in ['script','stdout','stderr']:m.check(seal[k])
 before=m.read(Q/'PRESERVATION_BEFORE.json');after=m.read(Q/'PRESERVATION_AFTER.json');base=m.read(Path(d['baseline_path']))
 assert len(base['files'])==len(before['protected_files'])==len(after['protected_files'])==15549
 shape=lambda rows:{v['path']:(v['sha256'],v['bytes']) for v in rows}
 assert shape(base['files'])==shape(before['protected_files'])==shape(after['protected_files'])
 for v in base['files']:m.check(v)
 assert shape(before['frozen_files'])==shape(after['frozen_files']) and len(after['frozen_files'])==128
 for v in after['frozen_files']:m.check(v)
 rawsnap=m.read(m.C/'MASTER_SOL_R30_STATIC_COMPLETED_IDLE_20261012.json');snap=json.loads(rawsnap['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['latestTurn']['id']==d['actual_new_turn_id']
 branch=m.read(Q/'SOURCE_BRANCH_CUSTODY_REVIEW.json');assert branch['case_count']==16 and branch['abstract_branch_review_not_executed_tests']
 provenance=m.read(Q/'PROVENANCE_AND_ORIGINAL_DRIFT_REVIEW.json');assert provenance['independent_drift_count']==12 and provenance['master_drift_pathset_match'] and provenance['old_frozen132_verified']
 stale=provenance['declared_built_candidates_vs_actual_frozen'];assert len(stale)==provenance['stale_declared_built_count']==7
 for v in stale:
  m.check(v['actual_R30_frozen']);assert v['original_declared']['sha256']!=v['actual_R30_frozen']['sha256'] and not v['sha_matches']
 coverage=m.read(Q/'PRESERVATION_POLICY_PATH_COVERAGE_REVIEW.json');assert coverage['initial_original_path_covered_count']==0
 u=m.read(Q/'UNITY_REFERENCE_NULL_AND_ADDCOMPONENT_IL.json');m.check(u['input']);m.check(u['dependency_manifest']);ub=Path(u['input']['path']).read_bytes()
 checked_IL=[]
 for method in u['methods']:
  if method['rva']:
   assert il_at(ub,method['rva']).lower()==method['IL_hex'].lower(),method['name'];checked_IL.append(method['name'])
 assert 'CompareBaseObjects' in checked_IL and 'op_Equality' in checked_IL and 'op_Inequality' in checked_IL
 correction=m.read(Q/'METADATA_SCHEMA_R1_CORRECTION.json')
 for k in ['original_helper','corrected_helper','diff','original_failure_tool','original_stderr']:m.check(correction[k])
 old=Path(correction['original_helper']['path']).read_bytes();new=Path(correction['corrected_helper']['path']).read_bytes();needle=b"['bytes']";positions=[i for i in range(len(old)) if old.startswith(needle,i) and old[:i]+b"['size']"+old[i+len(needle):]==new];assert len(positions)==1
 assert m.read(Path(correction['original_failure_tool']['path']))['exit_code']==1 and correction['original_stderr']['bytes']==825
 report=Path(comp['artifacts']['report']['path']);review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R30_HANDOFF_INDEPENDENT_STATIC_S1_20261012.md';proof=m.C/'MASTER_SOL_R30_STATIC_COMPLETION_VERIFICATION_20261012.json';pres=m.C/'MASTER_R30_STATIC_COMPLETED_QA_TERMINAL_PRESERVATION_20261012.json'
 owned=[m.row(p) for p in sorted(Q.rglob('*')) if p.is_file()]+[m.row(report)];m.create(pres,dict(at=m.now(),files=owned,protected_unique_paths=len(owned),result_id=comp['result_id'],initial_ACK_and_failed_raw_terminal_postseal_RETURN_all_preserved=True))
 verdict='ACCEPTED_INDEPENDENT_R30_STATIC_RECEIPT_COHORT_GAINS_REQUIRED_MODE_LIFETIME_EVIDENCE_REVISION_REQUIRED_NATIVE_UNTESTED'
 review.write_text(f'''# R30 independent STATIC S1 — Master

{verdict}. Original Sol actualcompletedidle12/result7705b91.../COMPLETION E1602... immutable initial841A.../report776E.../EMD7F5...59entries verified. Full artifact/index/ACKbinding graph and actualsealexit0/fullstreams with10cycle exclusions/postsealactualreturn checked. Baseline15549 and both pre/post128freeze matched; candidate/build/native/QAcompiler/runner/adverse0. SOURCE16 branch cases/17claims are static analyses, not tests/PASS/runtime E2. Full Masterreview read original report and actual completed thread; no substitute. All terminal{len(owned)}files+report protected.

Adopt precision corrections: pendingowner/receipt/pair context DOES exist beforeAddComponent. Defect is absent independent durable requiredmode/owner/cohort/consumed record after absence/cleanup/consume, not absence of allprecontext. Lock+clear is one retrieval per CURRENTregistration; lifetime re-registration ofsameowner/cohort is not barred. Bootstrap has one current callsite; no repeat/native exploit was executed or claimed. Correct activeReceipt/snapshot cohort/boolset/matchedowner gate/aliveowner cleanup gains independently credited. High1 remainsOPEN for missing/wrong/postconsume modefalse fallthrough, durable consumption/lifetime/no-native proof. High2carrier/High3publisher andE1lineage04 OPEN.

Exact frozen Unity reference C5C58EA2.../MVIDe422... IL was independently file-byte checked at methodRVAs by Master, without Unityexecution. Equality/inequality dispatch toCompareBaseObjects and cachedptr conditionalnull interpretation apply only to this reference. Do not substitute generic instance-ID memory. actualdestroyed-pointer/nativeAwake/getter/Disable/Update timings remainUNOBSERVED. Cleanup needs managedidentity custody independent of overloaded-null liveness. Actual Awake catch logs/no rethrow, so blanket allAwakeexception→bootstrapcatch guarantee rejected; actualescapingAddComponent exceptions sourcecaught only. Earlyreturn does not disable or prevent Update; outside5 update/failure completion guards require a NEW explicit Master scope.

Source5spans/outside6 all261380bytes retained. Custody prose7wrongranges rejected; actual byte map controls. OriginalR29E1drift12 currentpathset/frozen132 confirmed. A initialbaseline15296 covered0/12 originals; preservationchecker PASS did not implyalloriginalrawpreserved. R30pre-run builtcandidate declarations7/7 staleoldR29 hashes, verified independently against actual frozen bytes; declaredafterrun~208.8s is internal producer chronology, not clock/order proof. OldrunnerProgram identity/rebuiltoldroot/wrongR29envelope32/rawlabels/insufficient fulltyped/raw/loaded/compiler/oracle proof notfreshR30normalorhandoffverification. ACKscopehashwrong remains. Source/PDB4of4 identity is valid and notoperatorauthentication.

Ownmetadata bytes→size locator error original helper/exit1/fullstderr825 preserved; exactsinglelookup correction and successful stages within approved passive scope accepted, no candidate or expected mutation. Neither failedattempt nor finalstatic finding is runtimePASS/closure. Do not repair originals/oldfreeze/oldQA or usepriorPASS onnewcandidate.

Next A R31: durable bounded pair-required cohort/owner/consumed record separate frompayload slot, modeknownbeforeacquire and retained; one lifetime registration forsealedstartup; managedownercleanup withoutunsafegetter dependency; failclosed Awakecatch and Updateentry guard. New7explicit source spans extends prior5 by Awake failure/success tail and Updateentry only; existingPAIR/Capture/currenttask/receiver/Census/csproj/publisher/outsidebytes fixed. No newpublicchild/globalregistry/issuer/schema/taskauthority/native execution. Fresh task-owned harness/raw/prospectivepins and actualbinary/runner identity; allhistorical originalE1includingcurrentdrift paths explicitly protected. NewexactWP/readablecontract/preservation+freshCUidle/oneSubmit needed beforeSENT. R31currentlyNOTSENT untilprepared/actualdelivery; no newSolWP whileidle awaitingnewcandidate. SamehourlyPAUSEDuntilactualA delivery,thenresumeexisting60min173char/correcttarget.

FoundationHOLD/nativeE2NOTRELEASED/Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplitOPEN. Mastercandidate execution/build0/Highclosure0/release0. Source '''+str(comp['artifacts']['report']['path'])+'; exactverification '+str(proof)+'.\n',encoding='utf-8')
 summary=dict(at=m.now(),delivery_id=comp['delivery_id'],result_id=comp['result_id'],wp_id=comp['wp_id'],wp_revision='S1',completion=m.row(Q/'COMPLETION.json'),master_verdict=verdict,review=m.row(review),report=m.row(report),evidence_count=59,protected_paths=15549,frozen_files=128,terminal_preservation=m.row(pres),actual_snapshot=snap,static_source_branches=16,static_claims=17,not_executed_tests=True,Unity_reference_IL_methods_byte_checked=checked_IL,stale_pre_manifest_binaries=7,original_drift_initial_baseline_coverage=0,original_drift_current_matched=12,QA_execution_compile_candidate_native_adverse=0,Master_candidate_build_execute=0,source_high1_carrier_publisher_and_E1lineage='OPEN',native_E2='NOT_RELEASED',Foundation='HOLD',next_A='R31_DURABLE_MODE_FAILURE_UPDATE_AND_NEW_EVIDENCE_APPROVED_DIRECTION_NOT_SENT',monitor='PAUSED_HOURLY',guard_run='MASTER-R30-SOL-STATIC-COMPLETE-20261012-01',guard_session=2627)
 m.create(proof,summary);cs['sol_latest_completion']=dict(summary,proof=m.row(proof));cs['sol_current_delivery'].update(status='COMPLETED_MASTER_ACCEPTED_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED',completion_sha256=summary['completion']['sha256'],master_disposition=verdict,master_review=str(review));cs.update(sol_status='R30_STATIC_COMPLETED_MASTER_ACCEPTED_ACTUAL_IDLE',last_sol_cursor=snap['cursor'],sol_next_action='WAIT_NEW_EXACT_R31_CANDIDATE_NO_NEW_WP_SENT',updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',cs)
 rec['processed_results'].append(dict(at=m.now(),recipient='Sol',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(proof)));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 board=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');t=board['tasks'][-1];t['qa_runtime_status']=verdict;t['independent_qa_review']=m.row(review);t['status']='COMPLETED_REVIEWED_INDEPENDENT_STATIC_REVISION_REQUIRED';t['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(pres),sha256=m.row(pres)['sha256']));board['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',board)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['sol'].update(current_status=cs['sol_status'],current_runtime_status='ACTUAL_COMPLETED_IDLE',current_runtime_idle_verified=True,last_result_id=comp['result_id'],last_verdict=verdict,last_cursor=snap['cursor'],last_runtime_observation_cursor=snap['cursor'],latest_review=str(review),latest_progress_proof=str(proof));ds['latest_master_review']=str(review);ds['updated_at']=m.now();m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(summary,event='SOL_R30_STATIC_COMPLETED_MASTER_ACCEPTED_R31_DIRECTION',proof=m.row(proof)))
 m.append_delta('LOCAL-SOL-R30-INDEPENDENT-STATIC-COMPLETE',verdict+'. Originalactualidle12/COMPLETIONE1602.../report776E...59evidence/15549protected/128frozen matched;16SOURCEbranches17claims are NOTtests/allcandidatecompileexecutionnative0. Pre-attach pendingcontext exists,missingdurable independentmode/cohort/consumed remains;oneuseperregistration notlifetime,currentonecallsite/noreplaynativeproof. ExactUnityreferenceIL Masterbytechecked/nullconditional notactualdestroy/lifecycleproof;Awakeowncatchno-rethrow/allpropagationreject,Updateunblocked earlyreturnneedsnewscope. Custody7proserangeswrong/staleprebin7/0of12originalbaselinecoverage/drift12frozen132preserved;allHighsOPEN/no oldPASSinherit. Adopt narrowR31new7spans inclAwake failure/success tail+Updateentry/durablemode/owner/lifetime+newownedprospectiveevidence;directionapprovedNOTSENTuntilWP/freshCUproof. No newSolWP;hourlyPAUSEDuntilactualA delivery,FoundationHOLD/nativeE2NOTRELEASED. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status=verdict,proof=m.row(proof),terminal_files=len(owned),next_A='R31_DIRECTION_NOT_SENT'),ensure_ascii=False))
if __name__=='__main__':main()
