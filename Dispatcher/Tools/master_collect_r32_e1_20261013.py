from pathlib import Path
import json,hashlib,shutil,re,sys
import master_r29_s1_stop_prepare_s2_20261012 as m
sys.stdout.reconfigure(encoding='utf-8')
def ck(v,key='path'):
 a=m.row(Path(v[key]));assert a['sha256']==v['sha256'] and a['bytes']==v.get('bytes',v.get('size')),v[key];return a
def main():
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=b['tasks'][-1];T=Path(t['instruction_path']).parent;E=Path(t['new_owned_E1_root'])
 assert c['active_operation'] is None and t['wp_revision']=='GATE05-R32-CUSTODY' and t['status']=='IN_PROGRESS'
 comp=m.read(T/'COMPLETION.json');assert all(comp[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and comp['envelope']==35 and comp['status']=='COMPLETED'
 rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(v.get('result_id')==comp['result_id'] for v in rec['processed_results'])
 verified=[ck(v) for v in comp['artifacts']];assert len(verified)==23
 for v in t['production_fixed_files']:m.check(v)
 scope=m.read(Path(t['scope_baseline_path']));assert m.row(Path(t['scope_baseline_path']))['sha256']==t['scope_baseline_sha256'];ck(scope['protected_baseline'])
 bj=m.read(Path(scope['protected_baseline']['path']))
 for v in bj['files']:m.check(v)
 assert len(bj['files'])==15903
 oldfm=Path(b['tasks'][-2]['frozen_manifest']);old=m.read(oldfm)
 for v in old['files']:ck(v,'frozen_path')
 assert len(old['files'])==131
 ob=next(Path(v['frozen_path']).read_bytes() for v in old['files'] if v['original_path']==scope['Worker_original']['path'])
 assert hashlib.sha256(ob).hexdigest().upper()==scope['Worker_original']['sha256']
 src=Path(scope['Worker_original']['path']);nb=src.read_bytes();spans=sorted(scope['allowed_byte_spans'],key=lambda v:v['start']);pos=spans[0]['start'];assert ob[:pos]==nb[:pos]
 outside=[dict(old_range=[0,pos],new_range=[0,pos],bytes=pos)];actual=[]
 for i,s in enumerate(spans):
  end=spans[i+1]['start'] if i+1<len(spans) else len(ob);fixed=ob[s['end']:end];assert fixed
  npos=nb.find(fixed,pos);assert npos>=pos and nb.find(fixed,npos+1)==-1,s['id']
  actual.append(dict(span_id=s['id'],orig_range=[s['start'],s['end']],new_range=[pos,npos],new_bytes=npos-pos,new_sha256=hashlib.sha256(nb[pos:npos]).hexdigest().upper()))
  outside.append(dict(old_range=[s['end'],end],new_range=[npos,npos+len(fixed)],bytes=len(fixed),sha256=hashlib.sha256(fixed).hexdigest().upper()));pos=npos+len(fixed)
 assert pos==len(nb) and len(outside)==5 and sum(v['bytes'] for v in outside)==263961
 declared=m.read(T/'SOURCE_SCOPE_DIFF.json')
 for a in actual:
  d=next(v for v in declared['authorized_spans'] if v['span_id']==a['span_id']);assert all(a[k]==d[k] for k in ['orig_range','new_range','new_bytes','new_sha256'])
 bi=m.read(T/'BUILD_INPUT_MANIFEST.json');inputs=[]
 for k in ['input_source_files','generated_cs_documents','actual_resolved_compile_references','toolchain_executables_and_compiler_dlls']:
  inputs.extend([ck(v) for v in bi[k]])
 assert len(inputs)==19
 for v in m.read(T/'BUILD_OUTPUT_MANIFEST.json')['outputs']:ck(v)
 pe={};ident=m.read(T/'CANDIDATE_IDENTITY.json')
 for mode in ['Debug','Release']:
  tool=m.read(m.C/f'MASTER_R32_{mode.upper()}_PE_PDB_TOOL_20261013.json');assert tool['exit_code']==0;v=json.loads(tool['output']);k=ident[mode.lower()+'_candidate']
  assert v['codeviewMatched'] and len(v['documents'])==4 and all(d['matched'] for d in v['documents']) and v['mvid']==k['mvid'] and v['codeviewGuid']==k['codeview_guid'];pe[mode]=v
 runs=m.read(T/'BUILD_HOST_TOOL_TELEMETRY.json')['build_runs'];raw=[];refpaths=set()
 for run in runs:
  assert run['exit_code']==0 and run['pid']>0
  streams={}
  for k in ['stdout','stderr']:
   v=m.row(Path(run[k+'_path']));assert v['sha256']==run[k+'_sha256'] and v['bytes']==run[k+'_bytes'];streams[k]=v
  text=Path(run['stdout_path']).read_text(encoding='utf-8-sig',errors='replace');lines=[line for line in text.splitlines() if '/noconfig' in line and ('csc.exe' in line or 'csc.dll' in line)];assert len(lines)==1
  refs=re.findall(r'/reference:(?:"([^"]+)"|([^\s]+))',lines[0]);mode_refs=[]
  for quoted,unquoted in refs:
   p=Path(quoted or unquoted);assert p.exists(),str(p);refpaths.add(str(p));mode_refs.append(m.row(p))
  raw.append(dict(configuration=run['configuration'],producer_host_pid=run['pid'],exit_code=run['exit_code'],argv=run['argv'],cwd=run['cwd'],duration=run['duration_seconds'],streams=streams,actual_csc_command=lines[0],actual_csc_command_sha256=hashlib.sha256(lines[0].encode('utf-8')).hexdigest().upper(),compiler_references_observed_now=mode_refs,compiler_server_lines=[line.strip() for line in text.splitlines() if 'CompilerServer:' in line]))
 installed=m.read(m.C/'MASTER_R32_POSTDISPATCH_PRESERVATION_VERIFICATION_20261012.json')['installed_known_unchanged_OPEN_actorUNKNOWN'];ck(installed)
 audit=m.C/'MASTER_R32_SOURCE_BUILD_EVIDENCE_AUDIT_20261013.json'
 m.create(audit,dict(at=m.now(),actual_source_spans=actual,outside_segments=outside,outside_bytes=263961,producer_maps_matched=True,producer_build_inputs_matched=inputs,actual_build_raw=raw,compiler_reference_unique_paths=len(refpaths),framework_references_prospective_in_producer_input=False,compiler_server_PID_start_end_unobserved=True,producer_pin_chronology_internally_consistent=True,Master_observed_before_compile=False,build_metadata_csc_version_not_independently_claimed=True,all_unit_native_execution=0,known_installed=installed,Master_candidate_build_run=0,guard_run='MASTER-R32-HOURLY-20261013-0022-01',guard_session=86751))
 paths={v['path']:Path(v['path']) for v in verified}
 for root in [T,E,m.R/'scratch/WorkerBridgeMod/Source/bin',m.R/'scratch/WorkerBridgeMod/Source/obj']:
  for p in root.rglob('*'):
   if p.is_file():paths[str(p)]=p
 for v in t['all9_before']+t['production_fixed_files']:paths[v['path']]=Path(v['path'])
 F=m.R/'Dispatcher/CANDIDATES/G05R32-64ad38e2';assert not F.exists();F.mkdir();frozen=[]
 for p in paths.values():
  target=F/p.relative_to(m.R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);a=m.row(p);assert m.row(target)['sha256']==a['sha256'];frozen.append(dict(a,original_path=str(p),frozen_path=str(target)))
 fm=T/'MASTER_GATE05_R32_CUSTODY_REVIEW_FREEZE_MANIFEST.json';m.create(fm,dict(at=m.now(),files=frozen,scope='R32_POST_COMPLETION_EXACT_SOURCE_BINARY_PDB_BUILD_RAW_STATIC_AND_FRESH_POSITIVE_PURE_QA_ADMISSION',no_old_E2_or_PASS_inheritance=True))
 verdict='MANAGED_CUSTODY_RESOURCE_SOURCE_AND_BUILD_GAINS_CREDITED_FRESH_INDEPENDENT_REGRESSION_PENDING_NATIVE_NOT_RELEASED'
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R32_CUSTODY_E1_20261013.md'
 review.write_text(f'''# R32 E1 Master 판정

{verdict}.

실제 {comp['result_id']}/envelope35의 원문과 23 artifact SHA/size, protected15903, oldR31frozen131, fixedCensus/csproj/publisher3를 대조했다. 새 frozen{len(frozen)} manifest {fm} / SHA{m.row(fm)['sha256']}. Debug DLL0B23C358E8C8FC16FCD02DDE654AD8AE763EA177460BB15F5F1E1B1F0CB67E26/325632/MVID7d436c98-659a-4df1-a085-06fe9e55a0bc/PDB226DF5428AB94D48E0B08DC237AF3FC2E9F193315FE4D2F6EE2A8654B512E90D/79124. Release19F2CA8D466B10E99B86C8F5DD380102CCA14555B1FC7052AAB2B5DCFA98806F/MVIDcee8068e-e814-4203-8135-8c0fd5107005/PDBA0F37D44... 별도 identity. 두 actual CodeView/PDB/source4of4가 trusted file-byte PE reader와 일치한다. Worker source214F1F95.../275573. Master candidate 실행·빌드0.

지정4구간의 실제 새 byte map/hash는 이번 producer declaration과 일치하며, 밖5구간263961bytes는 R31 frozen 원문과 동일하다. 관리된 null/owner ReferenceEquals를 acquisition/cleanup에 적용했고, mode를 gameObject getter 전에 표시하며, 이미 aborted인 process의 payload transfer/resource setup을 source에서 차단했다. Awake catch는 isRunning=false와 incomplete/stickyabort 이후 로그·callback·listener·thread·matching-owner cleanup을 독립적으로 시도한다. OnDestroy finally는 own resources 정리 시도를 유지한다. 안전하게 획득하지 못한 owner를 다른 instance의 registeredowner로 대체하지 않았다. SOURCE 개선을 credit한다. Native-null wrapper/event timing/Thread.Abort 성공/실제 callback rollback을 실행 검증한 것은 아니다. Unchanged legacy invalid-parent return, concurrent acquire-to-resource interval, unknown retainedowner 조건은 독립 static QA에서 평가하고 실제 native 시험 전에는 닫지 않는다.

빌드 input19(source3/generated4/resolved HintPath6/tool6)와 output7 및 raw Debug/Release stdout·stderr SHA/bytes가 실제 일치한다. Host PID34256/12188·exit0·argv/cwd, diagnostic compiler command와 references를 읽었다. Pin 선언23:29:22→빌드 record23:29:26→후보/완료 chronology는 내부 일관성이 있지만 Master가 compile 전에 존재를 관측했다고 소급 주장하지 않는다. CompilerServer server processed compilation 원문이 있으므로 build PID를 fresh csc/server PID로 해석하지 않는다. Framework references 전체의 prospective hashes, compiler-server 별도 PID/start/end, recursive producer helper/output graph은 불완전하다. 해당 gap은 원문 보존해 별도 표시한다. 일부 compiler version prose도 독립 확인 값이 아니다. 새 QA는 자체 최종 compiler/run/loaded graph를 실제로 prospectively pin해야 한다. A BUILT_SOURCE_CORRECTION_RUNTIME_NOT_EXECUTED/단위·native0를 그대로 채택하며 E1을 E2 PASS로 승격하지 않는다.

새 정확한 Debug 후보만 original Sol의 defensive static + 정상 PURE Pair6/Capture4 fresh QA에 admission한다. QA 자체 새 runner build1 및 en-US/de-DE 정상 process2, 전체 independent typed/value/order/raw/copy oracle와 pre/post selected-load identity 증거가 필요하다. 기존 R29 정상 PASS나 R31 source labels를 새 후보 PASS로 승계하지 않는다. 수정된 global/Set/acquire/Awake/Update/OnDestroy/Unity/native/operator/Process/provider/cache/rejection/adverse는 실행 admission 밖이다. Production 수정·재빌드 금지. Sol 독립 결과 뒤 Master가 다음 bounded 수정/남은 native plan을 판정한다. Source High4 모두 OPEN; full Gate05 E2 NOT_RELEASED, Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplit OPEN, Foundation HOLD. Installed knownBB3B52... unchanged OPEN/actorUNKNOWN, 복원·정상화0.

근거 {audit}. 기존 hourly 같은 예약은 terminal review 후 실제 도구로 PAUSED, direct QA 완료 push는 계속한다. 다음 A는 독립 검토 뒤 실제 필요 범위를 새 WP로 승인·전달한다.
''',encoding='utf-8')
 proof=m.C/'MASTER_GATE05_R32_CUSTODY_E1_VERIFICATION_20261013.json'
 summary=dict(at=m.now(),dispatch_id=t['dispatch_id'],result_id=comp['result_id'],completion=m.row(T/'COMPLETION.json'),artifact_count=len(verified),protected_paths=15903,old_frozen_files=131,frozen_manifest=m.row(fm),frozen_files=len(frozen),source_audit=m.row(audit),candidate_identity=ident,PE_PDB_Source=pe,Master_candidate_build_execution=0,master_verdict=verdict,review=m.row(review),guard_run='MASTER-R32-HOURLY-20261013-0022-01',guard_session=86751,monitor='PAUSE_PENDING_TOOL',R32_hourly_run_observed_UTC='2026-10-12T15:22:54.212Z',Foundation='HOLD',native_E2='NOT_RELEASED')
 m.create(proof,summary)
 t.update(status='COMPLETED_REVIEWED_FRESH_INDEPENDENT_QA_PENDING',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_disposition=verdict,master_review_path=str(review),frozen_manifest=str(fm),frozen_manifest_sha256=m.row(fm)['sha256'],qa_runtime_status='INDEPENDENT_STATIC_POSITIVE_PURE_PREPARING_NOT_SENT');b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 c.update(a_status=t['status'],a_latest_completion=dict(summary,proof=m.row(proof)),updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 rec['processed_results'].append(dict(at=m.now(),recipient='A',result_id=comp['result_id'],completion_sha256=summary['completion']['sha256'],master_verdict=verdict,review=m.row(review),proof=m.row(proof)));rec['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['a'].update(current_status=t['status'],last_result_id=comp['result_id'],latest_review=str(review),current_runtime_idle_verified=False,current_runtime_status='R32_TERMINAL_FILE_REVIEWED_UI_UNVERIFIED');m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(summary,event='R32_E1_EXACT_FREEZE_FRESH_STATIC_POSITIVE_QA_ADMISSION',proof=m.row(proof)))
 m.append_delta('LOCAL-R32-CUSTODY-E1-MASTER-FRESH-QA-ADMISSION',verdict+'. Actual23artifacts/protected15903/old131/fixed3 matched/newfreeze'+str(len(frozen))+'/Debug0B23...MVID7d436c98.../Release19F2...MVIDcee8068e.../PDBsource4of4;actual4spans/outside263961bytes/producer maps correct/input19/rawbuild2exit0 matched. Managednull/modebeforegetter/stickyabort/resourcecleanup SOURCE gains credited; A unitnative0/no newPASS. Compiler-server/fullprospectiveframework graph limits explicit; freshSol static+positivePair6Capture4 preparingNOTSENT,noHighclosure/nativeE2/Foundationrelease. R32hourly15:22:54.212Z observed/samehourlypausependingtool. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status='R32_E1_REVIEWED_FRESH_QA_ADMISSION',frozen_files=len(frozen),artifact_count=23,protected=15903,compiler_refs=len(refpaths),proof=m.row(proof))))
if __name__=='__main__':main()
