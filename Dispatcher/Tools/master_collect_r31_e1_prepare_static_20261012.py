from pathlib import Path
import json,hashlib,shutil,sys
import master_r29_s1_stop_prepare_s2_20261012 as m
sys.stdout.reconfigure(encoding='utf-8')
def ck(v,key='path'):
 a=m.row(Path(v[key]));assert a['sha256']==v['sha256'] and a['bytes']==v.get('bytes',v.get('size')),v[key];return a
def main():
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=b['tasks'][-1];T=Path(t['instruction_path']).parent;E=Path(t['new_owned_E1_root'])
 assert c['active_operation'] is None and t['wp_revision']=='GATE05-R31-LIFECYCLE'
 comp=m.read(T/'COMPLETION.json');assert all(comp[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and comp['envelope']==34
 rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(v.get('result_id')==comp['result_id'] for v in rec['processed_results'])
 verified=[ck(v) for v in comp['artifacts']]
 for v in t['production_fixed_files']:m.check(v)
 scope=m.read(Path(t['scope_baseline_path']));assert m.row(Path(t['scope_baseline_path']))['sha256']==t['scope_baseline_sha256']
 baseline=Path(scope['protected_baseline']['path']);ck(scope['protected_baseline']);bj=m.read(baseline)
 for v in bj['files']:m.check(v)
 assert len(bj['files'])==15598
 oldfm=Path(b['tasks'][-2]['frozen_manifest']);old=m.read(oldfm)
 for v in old['files']:ck(v,'frozen_path')
 ob=next(Path(v['frozen_path']).read_bytes() for v in old['files'] if v['original_path']==scope['Worker_original']['path'])
 assert hashlib.sha256(ob).hexdigest().upper()==scope['Worker_original']['sha256']
 src=Path(scope['Worker_original']['path']);nb=src.read_bytes();spans=sorted(scope['allowed_byte_spans'],key=lambda v:v['start'])
 pos=spans[0]['start'];assert ob[:pos]==nb[:pos];outside=[dict(old_range=[0,pos],new_range=[0,pos],bytes=pos)];actual=[]
 for i,s in enumerate(spans):
  end=spans[i+1]['start'] if i+1<len(spans) else len(ob);fixed=ob[s['end']:end];assert fixed
  npos=nb.find(fixed,pos);assert npos>=pos and nb.find(fixed,npos+1)==-1, s['id']
  actual.append(dict(span_id=s['id'],orig_range=[s['start'],s['end']],new_range=[pos,npos],new_bytes=npos-pos,new_sha256=hashlib.sha256(nb[pos:npos]).hexdigest().upper()))
  outside.append(dict(old_range=[s['end'],end],new_range=[npos,npos+len(fixed)],bytes=len(fixed),sha256=hashlib.sha256(fixed).hexdigest().upper()));pos=npos+len(fixed)
 assert pos==len(nb) and len(outside)==8 and sum(v['bytes'] for v in outside)==260917
 declared=m.read(T/'SOURCE_SCOPE_DIFF.json');diffbad=[]
 for a in actual:
  d=next(v for v in declared['authorized_spans'] if v['span_id']==a['span_id'])
  if any(a[k]!=d[k] for k in ['orig_range','new_range','new_bytes','new_sha256']):diffbad.append(dict(actual=a,declared=d))
 deps=m.read(T/'BUILD_INPUT_MANIFEST.json')['compiler_dependencies'];depbad=[]
 for v in deps:
  a=m.row(Path(v['path']))
  if a['sha256']!=v['sha256'] or a['bytes']!=v['bytes']:depbad.append(dict(declared=v,actual=a))
 pe={};ident=m.read(T/'CANDIDATE_IDENTITY.json')
 for mode in ['Debug','Release']:
  tool=m.read(m.C/f'MASTER_R31_{mode.upper()}_PE_PDB_TOOL_20261012.json');assert tool['exit_code']==0;v=json.loads(tool['output']);k=ident[mode.lower()+'_candidate']
  assert v['codeviewMatched'] and len(v['documents'])==4 and all(d['matched'] for d in v['documents']) and v['mvid']==k['mvid'] and v['codeviewGuid']==k['codeview_guid'];pe[mode]=v
 rawruns=m.read(E/'HOST_TELEMETRY.json')['runs'];rawbad=[]
 for r in rawruns:
  assert r['exit_code']==0 and r['pid']>0 and r['report_summary']['dispatch_id']==t['dispatch_id'] and r['report_summary']['envelope']==34
  for k in ['stdout','stderr','execution_report']:
   a=m.row(Path(r[k+'_path']))
   if a['sha256']!=r[k+'_sha256']:rawbad.append(dict(culture=r['culture'],key=k,declared_sha256=r[k+'_sha256'],actual=a))
 text=(E/'Harness/Program.cs').read_text(encoding='utf-8');source=src.read_text(encoding='utf-8')
 audit=m.C/'MASTER_R31_SOURCE_AND_EVIDENCE_AUDIT_20261012.json'
 m.create(audit,dict(at=m.now(),actual_source_spans=actual,outside_segments=outside,outside_bytes=260917,producer_scope_rows_wrong=diffbad,build_input_dependency_rows_wrong=depbad,raw_runs=[dict(culture=r['culture'],pid=r['pid'],exit_code=r['exit_code'],runtime_dispatch=r['report_summary']['dispatch_id'],runtime_timestamp=r['report_summary']['timestamp_utc']) for r in rawruns],manifest_declared_generated_at=m.read(T/'BUILD_INPUT_MANIFEST.json')['generated_at'],actual_loaded_SHA_MVID_CLR_before_after_in_raw=False,complete_typed_raw_copy_oracle_output_graph=False,normal_unchanged_PURE_API_only=True,new_owned_E1_root_used=True,old_E1_current_drift_files_preserved=True,source_custody_uses_Unity_null_shortcircuit='if (owner == null)' in source,Awake_owner_getter_before_durable_mode=True,Awake_catch_isRunning_not_stopped=True,Master_candidate_execution_build=0,read_only_locator_failure='Own initial text locator assumed nonnullable field; actual rg found nullable declaration; no candidate execution or mutation',old_guard_session27640_expired_on_user_interruption=True,no_mutation_before_new_guard=True,prior_outside_guard_thread_snapshot_not_claimed_locked=True))
 paths={v['path']:Path(v['path']) for v in verified}
 for root in [T,E,m.R/'scratch/WorkerBridgeMod/Source/bin',m.R/'scratch/WorkerBridgeMod/Source/obj']:
  for p in root.rglob('*'):
   if p.is_file():paths[str(p)]=p
 for v in t['all9_before']+t['production_fixed_files']:paths[v['path']]=Path(v['path'])
 F=m.R/'Dispatcher/CANDIDATES/G05R31-b8d47a10';assert not F.exists();F.mkdir();frozen=[]
 for p in paths.values():
  target=F/p.relative_to(m.R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);a=m.row(p);assert m.row(target)['sha256']==a['sha256'];frozen.append(dict(a,original_path=str(p),frozen_path=str(target)))
 fm=T/'MASTER_GATE05_R31_LIFECYCLE_REVIEW_FREEZE_MANIFEST.json';m.create(fm,dict(at=m.now(),files=frozen,scope='R31_POST_COMPLETION_EXACT_SOURCE_BINARY_PDB_PRODUCER_RAW_STATIC_ONLY_ADMISSION',no_old_E2_or_PASS_inheritance=True))
 verdict='DURABLE_MODE_UPDATE_GAINS_CREDITED_MANAGED_CUSTODY_AND_PROVENANCE_REVISION_REQUIRED_NATIVE_NOT_RELEASED'
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R31_LIFECYCLE_E1_20261012.md'
 review.write_text(f'''# R31 E1 Master review

{verdict}. Actual {comp['result_id']}/envelope34 collected. {len(verified)} artifact SHA/bytes, protected15598 and R30frozen128 matched. New exact freeze{len(frozen)} SHA{m.row(fm)['sha256']}. Debug F6C06D6B1392C5CF90483D047150D53A80193DED655850BF1A06FE65A72A52CE/MVIDf8c7c77e-e2c5-4d3e-9371-a4e349d433c9/PDBFDCE1F...; Release2B8220B6.../MVID130c2741-3e20-4275-9891-d4aea8adffd3/PDB69E60B...; both actual CodeView/PDB/source4of4 verified by trusted file-byte metadata reader. Master candidate/build0. Independent full outside8/260917bytes unchanged across actual7spans; producer {len(diffbad)} declared new span maps/hashes differ from actual. {audit} controls; no correction of producer originals.

Credit SOURCE-only durable process pair-required marker established against installed parent receipt before GameObject/AddComponent; registration-spent flag retained after payload transfer/cleanup; mode before acquire under normal getter success; Update initialization/profile+aborted entry guard; retained owner used in OnDestroy and separated resource cleanup; M05 staticmode/aborted hold. Old PURE/Capture/currenttask/receiver/Census/csproj/publisher outside bytes unchanged. Source gains are not native lifecycle or High closure.

Remaining custody: CleanupOwnerPendingHandoff and CleanupEscapingAddComponentFailure still return on overloaded Unity owner==null and use registeredowner!=null before ReferenceEquals. This can skip managed-reference custody when native liveness differs; exact frozen reference IL/conditional interpretation only, no destroyed-object probe executed. TryAcquire also gates managed identity on overloaded-null. Awake evaluates this.gameObject BEFORE marking instance required mode; real getter failure/timing is unobserved, catch marks global abort but own cleanup depends on owner/native checks. Awake catch stops callbacks/listener/thread but leaves isRunning=true and calls cleanup outside try. Do not call all partial-resource failures robust rollback. Review whether global abort handling by an unrelated instance should retain current source failclosed policy; no new policy/schema authority inferred. Whole task/currenttask/native remains unreleased.

New owned E1 root and correct runtime R31/envelope34 credited; old R29 E1 originals/current drift preserved. Two host PID18656/9624 exits0, labels6Pair+4Capture observed. Runner remains selected field/sentinel comparisons, no entire typed/order/value/raw BEFORE/AFTER_CALLER/AFTER_RETURNED graph or independently declared full oracle, no actual loaded selected SHA/MVID/corelib/CLR/prepost runtime witness, no recursive sealed output inventory. A FULL_TYPED_RAW_COPY_BINDING lists fixtures/API metadata, not complete executed graph. Copied fixture descriptors/provenance retain historical R29 path/timestamp/publisher identity; bytes may serve historical literal normal fixture but not new publication proof. No publisher executed/adopted.

BUILD_INPUT_MANIFEST dependency rows mismatch actual {len(depbad)}/{len(deps)}; toolchain labels lack executable/compiler hashes/complete source/reference/callplan/oracle pins and compiler PID/argv/fullraw. Declared20:55 generation follows raw20:48:31 normal report timestamps; internal declaration chronology is not independently observed time or world-order proof. PRE_RUN manifests have selected/runner declarations matching current bytes but omit dependency/CLR/oracle/fullpin graph and actual runtime verification; prospective before-run existence is not proven. Actual hash errors in declaration are not a permission to mutate dependency/candidate. Old originals/QA remain immutable. E1 PASS cannot be adopted as fresh full normal or native E2. HandoffHigh1/E1lineageHigh4 remainOPEN; carrierHigh2/publisherHigh3 separatelyOPEN.

Next original Sol: exact fresh frozen R31 independent defensive STATIC source/coverage/custody/provenance/nextminimal repair only, zero candidate load/build/run/compiler/global/bootstrap/Set/Acquire/Awake/Update/OnDestroy/private-reflection/Process/provider/cache/publisher/native/rejection/adverse. Challenge Master findings against actual source and evidence, no inherited R29/R30 PASS. Fresh normal unit execution later requires separate explicit admitted WP. No new A WP until independent static findings. Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplitOPEN/FoundationHOLD/nativeE2NOTRELEASED. Same existing hourly monitor pause via actual tool after terminal disposition; direct Sol push proceeds.
''',encoding='utf-8')
 proof=m.C/'MASTER_GATE05_R31_LIFECYCLE_E1_VERIFICATION_20261012.json'
 summary=dict(at=m.now(),dispatch_id=t['dispatch_id'],result_id=comp['result_id'],completion=m.row(T/'COMPLETION.json'),artifact_count=len(verified),protected_paths=15598,old_frozen_files=len(old['files']),frozen_manifest=m.row(fm),frozen_files=len(frozen),source_audit=m.row(audit),candidate_identity=ident,PE_PDB_Source=pe,Master_candidate_build_execution=0,master_verdict=verdict,review=m.row(review),guard_run='MASTER-R31-E1-COLLECT-20261012-01',guard_session=29837,monitor='PAUSE_PENDING_TOOL',Foundation='HOLD',native_E2='NOT_RELEASED')
 m.create(proof,summary)
 t.update(status='COMPLETED_REVIEWED_STATIC_REVISION_REQUIRED',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_disposition=verdict,master_review_path=str(review),frozen_manifest=str(fm),frozen_manifest_sha256=m.row(fm)['sha256'],qa_runtime_status='INDEPENDENT_STATIC_PREPARING_NOT_SENT');b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 c.update(a_status=t['status'],a_latest_completion=dict(summary,proof=m.row(proof)),updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 rec['processed_results'].append(dict(at=m.now(),recipient='A',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(proof)));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['a'].update(current_status=t['status'],last_result_id=comp['result_id'],latest_review=str(review),current_runtime_idle_verified=False,current_runtime_status='R31_TERMINAL_FILE_REVIEWED_UI_UNVERIFIED');m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(summary,event='R31_E1_EXACT_FREEZE_STATIC_ONLY_DISPOSED',proof=m.row(proof)))
 m.append_delta('LOCAL-R31-LIFECYCLE-E1-MASTER-STATIC-ADMISSION',verdict+'. Artifacts'+str(len(verified))+'/protected15598/oldfrozen128 matched/newfreeze'+str(len(frozen))+'/DebugF6C06D...MVIDf8c7.../Release2B8220...MVID130c...PDBsource4of4;actual7spans/outside260917bytes exact,producer'+str(len(diffbad))+'map rows and'+str(len(depbad))+' dependency hashes wrong. Durablemode/spent/Updateguard source credited,Unitynull custody/getter-before-mode/partial resource gaps remain. NewE1root/runtimeR31 identity credited,fulltyped/raw/load/prospective/compiler proof incomplete/no native. All HighsOPEN/FoundationHOLD;nextoriginalSol fresh frozen static only preparingNOTSENT,nextA NOTSENTpendingQA/samehourlypause pending actualtool. Historical TTL expired on interruption not claimed coverage,new actual guard acquired before mutations. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status='R31_E1_DISPOSED_STATIC_ONLY',artifact_count=len(verified),frozen_files=len(frozen),wrong_scope_rows=len(diffbad),wrong_dependencies=len(depbad),proof=m.row(proof)),ensure_ascii=False))
if __name__=='__main__':main()
