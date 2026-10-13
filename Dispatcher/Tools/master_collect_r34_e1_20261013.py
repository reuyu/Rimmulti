from pathlib import Path
import json,hashlib,shutil,re
import master_r29_s1_stop_prepare_s2_20261012 as m
from master_collect_r32_e1_20261013 import ck

def main():
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=b['tasks'][-1];T=Path(t['instruction_path']).parent;E=Path(t['new_owned_E1_root']);assert c['active_operation'] is None and t['wp_revision']=='GATE05-R34-ROLLBACK' and t['status']=='IN_PROGRESS'
 co=m.read(T/'COMPLETION.json');assert all(co[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and co['envelope']==37 and co['status']=='COMPLETED';rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(v.get('result_id')==co['result_id'] for v in rec['processed_results']);art=[ck(v) for v in co['artifacts']];assert len(art)==25
 scope=m.read(Path(t['scope_baseline_path']));ck(scope['protected_baseline']);base=m.read(Path(scope['protected_baseline']['path']));assert len(base['files'])==18019
 for v in base['files']:m.check(v)
 for v in t['production_fixed_files']:m.check(v)
 old=m.read(Path(b['tasks'][-2]['frozen_manifest']));assert len(old['files'])==71
 for v in old['files']:ck(v,'frozen_path')
 ob=next(Path(v['frozen_path']).read_bytes() for v in old['files'] if v['original_path']==scope['Worker_original']['path']);assert hashlib.sha256(ob).hexdigest().upper()==scope['Worker_original']['sha256'];nb=Path(scope['Worker_original']['path']).read_bytes();sp=scope['allowed_byte_spans'][0];start=sp['start'];tail=ob[sp['end']:];end=nb.find(tail,start);assert ob[:start]==nb[:start] and end>=start and nb.find(tail,end+1)==-1 and end+len(tail)==len(nb);assert start+len(tail)==269893
 actual=dict(span_id=sp['id'],orig_range=[start,sp['end']],new_range=[start,end],new_bytes=end-start,new_sha256=hashlib.sha256(nb[start:end]).hexdigest().upper());decl=m.read(T/'SOURCE_SCOPE_DIFF.json')['authorized_spans'][0];assert all(actual[k]==decl[k] for k in actual)
 inputs=m.read(T/'BUILD_INPUT_MANIFEST.json');pins=[]
 for k in ['input_source_files','generated_cs_documents','actual_resolved_compile_references','toolchain_executables_and_compiler_dlls']:pins.extend(ck(v) for v in inputs[k])
 assert len(pins)==133 and len(inputs['actual_resolved_compile_references'])==120
 for v in m.read(T/'BUILD_OUTPUT_MANIFEST.json')['outputs']:ck(v)
 ident=m.read(T/'CANDIDATE_IDENTITY.json');pe={}
 for mode in ['Debug','Release']:
  tool=m.read(m.C/f'MASTER_R34_{mode.upper()}_PE_PDB_TOOL_20261013.json');assert tool['exit_code']==0;x=json.loads(tool['output']);expected=ident[mode.lower()+'_candidate'];assert x['mvid']==expected['mvid'] and x['codeviewGuid']==expected['codeview_guid'] and x['codeviewMatched'] and len(x['documents'])==4 and all(v['matched'] for v in x['documents']);pe[mode]=x
 raw=[]
 for run in m.read(T/'BUILD_HOST_TOOL_TELEMETRY.json')['build_runs']:
  assert run['exit_code']==0 and run['pid']>0;streams={}
  for k in ['stdout','stderr']:
   v=m.row(Path(run[k+'_path']));assert v['sha256']==run[k+'_sha256'] and v['bytes']==run[k+'_bytes'];streams[k]=v
  txt=Path(run['stdout_path']).read_text(encoding='utf-8-sig',errors='replace');lines=[v for v in txt.splitlines() if '/noconfig' in v and ('csc.exe' in v or 'csc.dll' in v)];assert len(lines)==1;refs=re.findall(r'/reference:(?:"([^"]+)"|([^\s]+))',lines[0]);rr=[m.row(Path(a or z)) for a,z in refs];assert len(rr)==120 and {v['path'].lower():(v['sha256'],v['bytes']) for v in rr}=={v['path'].lower():(v['sha256'],v['bytes']) for v in inputs['actual_resolved_compile_references']};raw.append(dict(configuration=run['configuration'],pid=run['pid'],exit_code=0,argv=run['argv'],cwd=run['cwd'],streams=streams,actual_csc_command=lines[0],reference_count=120,compiler_server_lines=[v.strip() for v in txt.splitlines() if 'CompilerServer:' in v]))
 installed=m.read(m.C/'MASTER_R34_POSTDISPATCH_PRESERVATION_VERIFICATION_20261013.json')['installed_known_unchanged_OPEN_actorUNKNOWN'];ck(installed)
 text=nb[start:end].decode('utf-8');assert text.index('if (_activeAdmissionReceipt == null')<text.index('Application.logMessageReceived +=');inner=text[text.index('// Synchronized resource admission commit'):text.index('catch (Exception ex)',text.index('// Synchronized resource admission commit'))];assert 'listener?.Stop' not in inner and 'listenerThread?.Abort' not in inner and 'isRunning = false;' in inner and '_staticStartupAborted = true;' in inner;assert text.count('listener?.Stop')==1 and text.count('listenerThread?.Abort')==1
 outer=text[text.index('catch (Exception ex)',text.index('// Synchronized resource admission commit')):];assert outer.index('_staticStartupAborted = true;')<outer.index('Log.Error')<outer.index('listener?.Stop')
 audit=m.C/'MASTER_R34_SOURCE_BUILD_EVIDENCE_AUDIT_20261013.json';m.create(audit,dict(at=m.now(),actual_source_span=actual,outside_bytes=269893,input_files=133,actual_builds=raw,PE=pe,protected_paths=18019,old_frozen_files=71,source_gains=['failure flags published under existing lock before inner rethrow','inner Stop/Abort removed; guarded separate outer cleanup','parent/start/owner gates preserved outside fixed bytes'],remaining=['start calls still execute under lock with unmodeled BCL/native synchronization','postcommitabort/unknownowner/native teardown success unobserved','universal deadlock100 claim rejected','producer internal chronology/compiler-server identity/fullrecursive helper graph limited'],installed=installed,CRCRLF_in_allowed_span=True,outside_original_newline_bytes_unchanged=True,Master_candidate_build_run=0,guard_session=97639))
 paths={v['path']:Path(v['path']) for v in art}
 for root in [T,E,m.R/'scratch/WorkerBridgeMod/Source/bin',m.R/'scratch/WorkerBridgeMod/Source/obj']:
  for p in root.rglob('*'):
   if p.is_file():paths[str(p)]=p
 for v in t['all9_before']+t['production_fixed_files']:paths[v['path']]=Path(v['path'])
 F=m.R/'Dispatcher/CANDIDATES/G05R34-a4d6866c';assert not F.exists();F.mkdir();fr=[]
 for p in paths.values():
  target=F/p.relative_to(m.R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);x=m.row(p);assert m.row(target)['sha256']==x['sha256'];fr.append(dict(x,original_path=str(p),frozen_path=str(target)))
 fm=T/'MASTER_GATE05_R34_ROLLBACK_REVIEW_FREEZE_MANIFEST.json';m.create(fm,dict(at=m.now(),files=fr,scope='R34_SOURCE_BUILD_POSTCOMPLETION_NEW_INDEPENDENT_STATIC_AND_POSITIVE_PURE_ONLY',oldPASSnotinherited=True))
 verdict='FAILURE_PUBLICATION_OUTSIDE_LOCK_CLEANUP_SOURCE_GAINS_CREDITED_CLAIMS_CORRECTED_FRESH_QA_REQUIRED_NATIVE_NOT_RELEASED';review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R34_ROLLBACK_E1_20261013.md';assert not review.exists()
 review.write_text(f'''# R34 E1 Master 판정

{verdict}.

Actual {co['result_id']}/envelope37/E1/COMPLETED를 수집했다. Artifact25/protected18019/priorfrozen71 실제SHA/bytes 일치. OriginalAwake39056..45687→new39056..{end}, outside269893 bytes 고정/producer map 일치. New frozen{len(fr)} {fm} SHA{m.row(fm)['sha256']}. Debug8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029/MVID7b08d3f4-27de-4685-b61b-8a312708a496/PDBFE75B3D1…79220/CVb1f9cfe5-6eac-4783-8ec6-3f755d7e58d2, Release9CBA7E69…/MVID93bc479a-cd1d-4d11-8d86-3364fc5e4180 distinct metadata only. ActualPE/PDB/source4of4 matched. Source544B2217…276685. Master 후보빌드/실행0.

Source gains: resource-start innercatch가 incomplete/isRunningfalse/stickyabort를 기존lock 아래 먼저 기록하고 rethrow한다. InnerStop/Abort는 없어졌고, lockunwind후 outercatch의 guardedlogging/callbackunsubscribe/listenerStop/threadAbort/knownownerclear 각 독립시도가 한 번씩 있다. Outercatch도 먼저 failureflag/stickyabort 기록. Parentbeforecallback/abort-to-startcommit/modebeforegetter/managedowner/cohort/selectedspent/no borrowedowner gates와 모든 fixedmethod/PURE/Capture/Census/csproj/publisher 밖bytes 유지. Allowed span 내 CRCRLF가 생겼지만 실제 compile/PDBsource가 맞으며 원문을 정규화하지 않는다. 이것만으로 의미적회귀FAIL을 주장하지 않는다.

Controlling correction: CALLBACK_LOCK_ORDER_REVIEW.md의 'Blocking in lock completely eliminated', 'Deadlock freedom100percent structurally guaranteed across all thread interleavings'를 채택하지 않는다. Listener.Start/Thread.Start는 여전히 sharedlock 내부이며 BCL/native/internal synchronization은 한mutex source로 모델링되지 않는다. CleanupOwnerPendingHandoff 자체는 lock을 취하므로 'cleanupoutsidealllocks'는 caller의 lockrelease와 구분해야 한다. 독립 cleanup 시도는 성공/완전 teardown proof가 아니다. No 실제deadlock/누출/bypass 관측, nativepostcommitabort/unknownowner/normalshutdown untested. 과도한 prose가 재발했지만 소스 개선과 분리해 판단하고, 이를 고치려고 불필요한 production 재빌드를 요구하지 않는다.

Producer source3/generated4/fullrefs120/tool6=133pins, actualbuild2 PID12300/3172 exits0/firststdoutstderr4 and compilercommandrefs120/config match. Outputmanifest는 여전히7finaloutputs이며 ownedroothelper/raw가 있어도 전체prospective recursive graph가 완성된 것은 아니다. Pin timestamps는 내부chronology, compiler-server independentPID/startend는 미관측. BuildPASS는 unit/nativeE2 PASS가 아니다. Ownedroot newhelpers 배치는 개선됐으며 옛loosehelpers/failures immutable. Actual unit/native0/기존installedBB3B incident unchangedOPENactorUNKNOWN/no restore.

Exact selectedDebug는 원래idleSol의 새独立STATIC/resource/claim/provenance +freshpositivePair6/Capture4 only admitted. New QA-owned finalcompiler1/twofreshnormalcultures 허용, production/candidate rebuild/modifiedAwake/global/Unity/native/operator/publisher/Process/provider/cache/rejection/adverse 미승인. OldR33 scopedPASS notinherited. 실제독립 결과 없이는 sourceHigh/native release/closure 아니다. Fresh native feasibility/readiness는 별도 admission이 필요하다. High4/Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplit OPEN/FoundationHOLD/fullnativeE2NOTRELEASED.

R34hourly actual trigger09:53:40.622Z 관측; 검토 후 동일hourlyPAUSE 예정/directSolpush. NextA 없음pendingindependentQA. Audit {audit}.
''',encoding='utf-8')
 proof=m.C/'MASTER_GATE05_R34_ROLLBACK_E1_VERIFICATION_20261013.json';v=dict(at=m.now(),dispatch_id=t['dispatch_id'],result_id=co['result_id'],completion=m.row(T/'COMPLETION.json'),artifacts=25,protected_paths=18019,frozen_files=len(fr),frozen_manifest=m.row(fm),audit=m.row(audit),review=m.row(review),candidate_identity=ident,master_verdict=verdict,Master_candidate_execution_build=0,guard_session=97639,monitor='PAUSE_PENDING_TOOL',Sol='ORIGINAL_IDLE27',Foundation='HOLD',native_E2='NOT_RELEASED');m.create(proof,v)
 t.update(status='COMPLETED_REVIEWED_SOURCE_GAINS_FRESH_QA_REQUIRED',result_id=co['result_id'],completion_sha256=v['completion']['sha256'],master_disposition=verdict,master_review_path=str(review),frozen_manifest=str(fm),frozen_manifest_sha256=m.row(fm)['sha256'],qa_runtime_status='R34_NEW_EXACT_FROZEN_STATIC_POSITIVE_QA_ADMITTED_NOT_SENT');b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b);c.update(a_status=t['status'],a_latest_completion=dict(v,proof=m.row(proof)),updated_at=m.now());c['master_monitor_automation']['future_R34_scheduled_run_observed']=True;c['master_monitor_automation']['first_R34_trigger_observed_utc']='2026-10-13T09:53:40.622Z';m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c);rec['processed_results'].append(dict(at=m.now(),recipient='A',result_id=co['result_id'],completion_sha256=v['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(proof)));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['a'].update(current_status=t['status'],last_result_id=co['result_id'],latest_review=str(review),current_runtime_idle_verified=False,current_runtime_status='TERMINAL_FILE_REVIEWED_NO_NEW_UI_IDLE_CLAIM');m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(v,event='R34_E1_COLLECTED_EXACT_FREEZE_SOURCE_GAINS_OVERCLAIMS_CORRECTED',proof=m.row(proof)))
 m.append_delta('LOCAL-R34-ROLLBACK-E1-MASTER',verdict+'. Artifact25/protected18019/priorfrozen71/sourceoutside269893/maps/133pins/120actualrefs/rawbuild2exit0/PEPDBsource4of4 matched. Newfreeze'+str(len(fr))+'/Debug8091F441-MVID7b08/Release9CBA7E69-MVID93bc distinct; source544B2217. Failureflags-beforecleanup/innerStopAbortremoved/outerguards credited; A renewed universaldeadlock100%/blockingeliminated claims rejected; native/cleanupsuccess unobserved. ExactnewSolSTATIC+freshpositivePURE admittedNOTSENTuntilfreshidle. Currenthourlytriggerobserved09:53:40.622Z/PAUSEpendingtool. High4OPEN/FoundationHOLD/fullnativeE2NOTRELEASED. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status='R34_E1_REVIEWED_FROZEN',files=len(fr),proof=m.row(proof))))

if __name__=='__main__':main()
