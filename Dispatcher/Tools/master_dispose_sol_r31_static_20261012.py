from pathlib import Path
import json,hashlib,struct
import master_r29_s1_stop_prepare_s2_20261012 as m
def il_at(data,rva):
 pe=struct.unpack_from('<I',data,0x3c)[0];n=struct.unpack_from('<H',data,pe+6)[0];opt=struct.unpack_from('<H',data,pe+20)[0];sec=pe+24+opt
 for i in range(n):
  a=sec+i*40;vs,va,rs,rp=struct.unpack_from('<IIII',data,a+8)
  if va<=rva<va+max(vs,rs):
   off=rp+rva-va;b=data[off]
   if b&3==2:return data[off+1:off+1+(b>>2)]
   flags=struct.unpack_from('<H',data,off)[0];head=((flags>>12)&15)*4;size=struct.unpack_from('<I',data,off+4)[0];return data[off+head:off+head+size]
 raise AssertionError(rva)
def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];Q=Path(d['qa_root']);comp=m.read(Q/'COMPLETION.json');rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')
 assert c['active_operation'] is None and all(comp[k]==d[k] for k in ['delivery_id','wp_id','wp_revision','result_id']);assert not any(v.get('result_id')==comp['result_id'] for v in rec['processed_results'])
 assert m.row(Q/'COMPLETION.json')['sha256']=='B24B1349332FA59828BA1A86FBBBC42EA202A85068ACE7657783BC51B294D102'
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==59
 for v in em['files']:m.check(v)
 for key in ['report','evidence_manifest','initial_ACK','result_index','ACK_completion_binding','preservation']:m.check(comp[key])
 base=m.read(Path(d['baseline_path']));assert len(base['files'])==15854
 for v in base['files']:m.check(v)
 for name in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
  p=m.read(Q/name);assert p['all_matched'] and p['protected_files']==base['files'] and p['protected_unique_paths']==15854 and p['frozen_count']==131
 freeze=m.read(Path(d['frozen_manifest']))
 for v in freeze['files']:
  a=m.row(Path(v['frozen_path']));assert a['sha256']==v['sha256'] and a['bytes']==v['bytes']
 preservation=m.read(Q/'PRESERVATION_BEFORE_AFTER.json')
 for v in preservation['old_frozen128']:m.check(v)
 for v in preservation['additive_original_reference_observations']:
  m.check(v['before']);m.check(v['after']);assert v['before']==v['after'] and v['initial_baseline_coverage'] is False and v['prospective_compile_reference_proof'] is False
 tools={}
 for p in Q.glob('*TOOL.json'):
  tool=m.read(p);assert tool['exit_code']==(1 if p.name=='review_provenance.TOOL.json' else 0)
  for key in ['script','stdout','stderr']:m.check(tool[key])
  assert tool.get('first_streams_complete',True);tools[p.name]=dict(exit_code=tool['exit_code'],tool=m.row(p))
 allowed={Path(v['path']).resolve() for v in em['files'] if Path(v['path']).resolve().is_relative_to(Q.resolve())}
 excluded=set(comp['cycle_logger_exclusions']);actual={p.resolve() for p in Q.rglob('*') if p.is_file() and p.name not in excluded};assert actual==allowed
 u=m.read(Q/'UNITY_REFERENCE_CUSTODY_IL.json');m.check(u['input']);m.check(u['dependency_manifest']);data=Path(u['input']['path']).read_bytes();methods=[]
 for v in u['methods']:
  if v['rva']:
   assert il_at(data,v['rva']).hex().lower()==v['IL_hex'].lower();methods.append(v['name'])
 prov=m.read(Q/'PROVENANCE_REVIEW.json');assert prov['dependency_mismatch_count']==5 and prov['stdout_mismatch_count']==2
 for v in prov['stdout_bindings']:
  m.check(v['actual_raw']);data=Path(v['actual_raw']['path']).read_bytes();assert data.count(b'\r\r\n')==20
  sha=hashlib.sha256(data.replace(b'\r\r\n',b'\r\n')).hexdigest().upper();assert sha==v['read_only_CRCRLF_to_CRLF_sha'] and sha!=v['declared_sha'] and not v['supplement_matches_declared']
 src=m.read(Q/'SOURCE_BRANCH_LIFECYCLE_REVIEW.json');claims=m.read(Q/'CLAIM_EVIDENCE_MATRIX.json');assert src['case_count']==20 and claims['count']==20 and comp['candidate_compiler_runner_global_native_adverse_executions']==0
 snap=json.loads(m.read(m.C/'MASTER_SOL_R31_STATIC_COMPLETED_IDLE_20261012.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['latestTurn']['id']==d['actual_new_turn_id']
 terminal=[m.row(p) for p in sorted(Q.rglob('*')) if p.is_file()]+[m.check(comp['report'])]
 tp=m.C/'MASTER_R31_STATIC_QA_TERMINAL_PRESERVATION_20261012.json';m.create(tp,dict(at=m.now(),files=terminal,failed_first_tool_raw_preserved=True,post_seal_logger_direct_return_included=True))
 verdict='ACCEPTED_INDEPENDENT_R31_STATIC_GAINS_MANAGED_CUSTODY_RESOURCE_EVIDENCE_REVISION_REQUIRED_NATIVE_UNTESTED'
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R31_INDEPENDENT_STATIC_S1_20261012.md';review.write_text(f'''# R31 independent STATIC S1 — Master disposition

{verdict}. Original completedidle15/result4daa915.../COMPLETIONB24B.../report6564.../EM67CD...59 artifacts verified;protected15854/newfrozen131/oldfrozen128 and additive Newtonsoft original reference observation matched. Actual core first numeric exits0 and provenance firstexit1/fullstderr900/correctedpassive locator stages retained; originalfailedhelper/raw not overwritten. QA sealed pathset/cycle exclusions/postseal logger/direct return verified. Terminal{len(terminal)} files protected by {tp}. Master/QA candidate/build/compiler/native/adverse0;20source cases/20claims NOT tests. Independent PE/PDB/source4of4 retained from own ACK verification, referenceIL six actual method bodies rechecked against pinned bytes without CLR/Unity execution.

Adopt R31 SOURCE gains: selected durable pairmode before attach, lifetime spent registration, payload-only transfer, Update and M05 HOLD, retainedowner OnDestroy+independent own resource cleanup. Entireoutside8/260917 and PURE/currenttask/carrier/publisher/Census/csproj unchanged. Actual7maps/producer7wrongnewranges+hashes independently corroborated. High1 not closed: managed custody still gated by overloaded Unity null, catch isRunning=true and cleanup unprotected. Native liveness/event order unobserved.

Controlling precision: getter-before-mode does NOT establish Update/M05 legacy execution bypass because catch globalabort alreadyholds them; retain this as owner-retention/ordering failure-context gap only. No claimed native exploit. CRCRLF host text-write is a hypothesis, NOT reconciliation: both transformations independently still differ from declared stdout hashes. Actual20CRCRLF each, all5dependency SHA ANDsizes wrong; current/frozen Newtonsoft samebytes not original beforebuild reference coverage. No raw normalization or evidence reconstruction. Historical R29 literal fixtures may be read as inputs; copied publisher/time/path labels do not prove new publication. Full prospective compiler/reference/oracle/load/typed/order/raw/copy graph absent. OriginalMaster raw supplement false comparison fields remain preserved; this correction controls any looser 'translation explains hash' reading.

Additional source countermodel accepted: unrelated instance can set globalabort while legitimate payload remains; legitimate acquire/Awake lacks prior-abort resource gate and can initialize listener/thread though Update/M05 remainheld. Master chooses same already selected failclosed abort scope: once pair startup aborted, no further pair resource initialization, clear only safely matched own pending payload, no reset/ignoreabort or new isolation/availability policy. R32 narrows4existing source spans to managed ReferenceEquals custody, mode-before-owner-getter, prior-abort before pair payload transfer/resource setup, isRunning=false/independent safe failure cleanup and robust OnDestroy finalization. Successful legacy body fixed; legacy invalid-parent earlyreturn outside spans remains separately unverified, no wholelegacy rollback claims. Registration-spent/consumed/closed histories documented, no canonical state/schema expansion.

R32 technical division: A source correction+truthful prospective compile/source/refs/tool/full firstbinarylog/actual PE-PDB evidence only, zero normal unit runner/test execution. Production compile is developer E1 build evidence, not semanticPASS. After new Master freeze/admission, original Sol can receive a separate fresh static+normal PURE regression WP with complete independent typed/raw/copy evidence. This avoids treating A shallow labels or rebuiltold evidence as proof while maintaining required independent regression/native obligations. No new A/Sol WP SENT yet; actualCUidle/oneSubmit needed. CarrierHigh2/publisherHigh3/E1lineageHigh4 stayOPEN. Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplitOPEN/FoundationHOLD/fullnativeE2NOTRELEASED. SamehourlyPAUSED until nextactualA delivery.
''',encoding='utf-8')
 p=m.C/'MASTER_SOL_R31_STATIC_COMPLETION_VERIFICATION_20261012.json';v=dict(at=m.now(),delivery_id=d['delivery_id'],result_id=comp['result_id'],completion=m.row(Q/'COMPLETION.json'),report=m.check(comp['report']),evidence_count=59,protected_paths=15854,frozen_files=131,terminal_preservation=m.row(tp),tools=tools,actual_snapshot=snap,Master_rechecked_reference_IL_methods=methods,source_cases=20,static_claims=20,not_executed_tests=True,source_highs='OPEN',master_verdict=verdict,review=m.row(review),next_A='R32_CUSTODY_RESOURCE_AND_BUILD_ONLY_APPROVED_DIRECTION_NOT_SENT',monitor='PAUSED_HOURLY',Foundation='HOLD',native_E2='NOT_RELEASED',guard_session=75967,guard_run='MASTER-R31-SOL-STATIC-COMPLETE-20261012-01');m.create(p,v)
 d.update(status='COMPLETED_MASTER_ACCEPTED_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED',completion_sha256=v['completion']['sha256'],master_disposition=verdict,master_review=str(review));c.update(sol_current_delivery=d,sol_latest_completion=dict(v,proof=m.row(p)),sol_status=d['status'],last_sol_cursor=snap['cursor'],sol_next_action='WAIT_NEW_EXACT_R32_CANDIDATE_NO_NEW_QA_WP_SENT',updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 rec['processed_results'].append(dict(at=m.now(),recipient='Sol',result_id=comp['result_id'],completion_sha256=v['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(p)));m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');b['tasks'][-1].update(status='COMPLETED_REVIEWED_INDEPENDENT_STATIC_REVISION_REQUIRED',independent_static_master_review=str(review));b['tasks'][-1]['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(tp),sha256=m.row(tp)['sha256']));b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['sol'].update(current_status=d['status'],current_runtime_status='ACTUAL_COMPLETED_IDLE',current_runtime_idle_verified=True,last_cursor=snap['cursor'],latest_review=str(review),latest_progress_proof=str(p));ds['endpoints']['a']['current_status']=b['tasks'][-1]['status'];m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(v,event='SOL_R31_STATIC_TERMINAL_MASTER_DISPOSED_R32_DIRECTION_APPROVED',proof=m.row(p)))
 m.append_delta('LOCAL-SOL-R31-INDEPENDENT-STATIC-COMPLETE',verdict+'. Actualidle15/59evidence/protected15854/newfrozen131/old128/terminal'+str(len(terminal))+' matched/IL6bytechecked. Durablemode-spent-Update-M05-OnDestroy source gains credited;managednullcustody/ownisRunningfailurecleanup/priorabortresourcegapOPEN. Getterfailure doesNOTproveUpdateM05bypass/globalabortHOLD;CRCRLF transform matchesNEITHERdeclaredSHA,5depsSHAandsizeswrong/no rawrepair. New R32 fourspans source+prospectivebuild ONLY directionapprovedNOTSENT,normalexecution separatefutureoriginalSol freshQA;no lowerednative/closure standard. AllHighsOPEN/FoundationHOLD/nativeE2NOTRELEASED/hourlyPAUSEDuntilactualA delivery. Review '+str(review)+'; proof '+str(p))
 print(json.dumps(dict(status='R31_STATIC_ACCEPTED_REVISION_REQUIRED_R32_DIRECTION_NOT_SENT',terminal_files=len(terminal),proof=m.row(p)),ensure_ascii=False))
if __name__=='__main__':main()
