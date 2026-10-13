from pathlib import Path
import json,hashlib,datetime,sys,ast,struct,uuid,tomllib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R27-QA-DEPENDENCY-REPAIR-20261012-01';PID=26572;SESSION=44434
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
def refs(x):
 if isinstance(x,dict):
  if all(k in x for k in ['path','sha256','bytes']):check(x)
  for y in x.values():refs(y)
 elif isinstance(x,list):
  for y in x:refs(y)
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);d=c['sol_current_delivery'];Q=Path(d['qa_root']);x=read(Q/'COMPLETION.json');rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp)
assert c['active_operation'] is None and all(x[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and x['result_id']==c['sol_current_result_id'] and x['status']=='BLOCKED_REPORT_COMPLETE'
assert sha(Q/'COMPLETION.json')=='207B2E6AB263E87F812B62072AFCE7A7922704CB5D90B9CEA44273D303C9AE02' and not any(z.get('result_id')==x['result_id'] for z in rr['processed_results'])
assert all(x[k]==0 for k in ['QA_compiler_builds','QA_child_runs','candidate_factory_IsValid_Capture_getter_load_calls','normal_cases_executed','native_game_Process_adverse','production_modify_rebuild'])
em=read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==15
for f in em['files']:check(f)
refs(x);refs(read(Q/'RESULT_INDEX.json'));refs(read(Q/'ACK_COMPLETION_BINDING.json'))
assert sha(Q/'ACK_INITIAL.json')==c['sol_current_ack']['initial_ACK']['sha256']==sha(Q/'ACK.json')
sf=C/'MASTER_SOL_R27_CHILD_CAPTURE_S1_STOP_COMPLETION_SNAPSHOT_20261012.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
base=read(Path(d['baseline_path']));assert len(base['files'])==13652
for f in base['files']:check(f)
for name in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 p=read(Q/name);assert p['protected_unique_paths']==13652 and {f['path']:(f['sha256'],f['bytes']) for f in p['files']}=={f['path']:(f['sha256'],f['bytes']) for f in base['files']}
block=read(Q/'BLOCKER_DEPENDENCY_LOCATION.json');refs(block);missing=Path(block['required_path']);assert not missing.exists() and not (Q/'Harness/Program.cs').exists() and not (Q/'QA_RUNNER_CONFIG.json').exists() and not list(Q.rglob('*.exe'))
fm=Path(d['frozen_manifest']);assert sha(fm)==d['frozen_manifest_sha256'];fr=read(fm);assert len(fr['files'])==83
njrows=[f for f in fr['files'] if Path(f['frozen_path']).name=='Newtonsoft.Json.dll'];assert len(njrows)==1
njrow=njrows[0];nj=Path(njrow['frozen_path']);assert str(nj)==block['manifest_newtonsoft_metadata']['path'] and sha(nj)==njrow['sha256']=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D' and nj.stat().st_size==711952
parse=H/'bootstrap/verify_local_identity.py';node=next(n for n in ast.parse(parse.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid');ns={'struct':struct,'uuid':uuid};exec(compile(ast.Module(body=[node],type_ignores=[]),str(parse),'exec'),ns)
njMvid=ns['mvid'](nj);assert njMvid=='dd21e087-47d9-4bce-bed8-b56112226337'
bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];assert t['status']=='COMPLETED_REVIEWED_SOURCE_CAPTURE_CREDITED_SCOPED_QA_PENDING'
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
pp=C/'MASTER_R27_QA_DEPENDENCY_STOP_PRESERVATION_20261012.json';assert not pp.exists();write(pp,pres)
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
verdict='ACCEPTED_QA_S1_STOP_BEFORE_BUILD_MASTER_DEPENDENCY_POINTER_ERROR_NORMAL_NOT_EXECUTED_S2_CORRECTION_ADMITTED'
review=H/'MASTER_REVIEW_ENGINE_GATE05_R27_QA_S1_DEPENDENCY_STOP_20261012.md';assert not review.exists()
review.write_text(f'''# R27 QA S1 중단 — Master 정정

{at};{x['result_id']}. **{verdict}**.

OriginalSol 실제completed/idle169/S1result-COMPLETION hash와 원문 보고·manifest15/index/binding/immutableACK를 대조했다. Baseline13652/currentproduction9/frozen83 before-after가 actualSHA-size 일치한다. Own metadata prepare_runner exit1은 지정 Newtonsoft 파일 SHA조회 단계 FileNotFoundError이며 원문 보존됐다. GeneratedProgram/config/toolchainpin/compiler/build/QAOSchild/candidateDLLload/factory/IsValid/Capture/getters 모두0. 이 중단은 candidate FAIL도 PASS도 아니며 독립 정상 실행 목표는 달성하지 않았다.

Master S1 WP에서 selectedDLL.parent/Newtonsoft.Json.dll을 실제 manifest에 확인하지 않고 지정한 것이 원인이다. 해당 경로는 없다. 실제 manifest83에는 오직 아래 frozen path가 있고, 정상 SHA-size 및 ECMA335 Module MVID를 Master가 metadata-only로 독립 확인했다:
{nj}
SHA{sha(nj)}, bytes711952, MVID{njMvid}.

이 DLL만 별도 loader/reference support로 admission한다. A executable/runner 실행 승인은 아니며 candidate수정·재빌드·dependency이동/원본Steam/새DLL다운로드가 아니다. 실제 manifest row, original hash, existingselected68BFE510.../MVID44ba753c.../matchingPDBF0BC.../sourceB292... 및 old/raw QA 증거는 변경하지 않는다. DLL path 이름이 Harness 아래여도 이 frozen library reference와 producer runner 실행을 구분한다.

Sol이 ownjudgment로 경로를 바꾸거나 재실행하지 않고 중단한 절차를 채택한다. Master가 같은 승인 범위에서 기술적으로 pointer를 정정하고 **새 S2 delivery/revision/newQAroot**에서 실행을 다시 승인한다. Candidate와 정상4 fixtures/independent oracle40raw/full15 typed graph/task27+approved7/copy통제와 전체compiler/load/prospective/recursive proof 요구는 동일하다. S1의 existing failed prepare_runner/review_setup은 TEXT-only 복사하여 S2소유로 새 경로/root/identity만 명시 정정할 수 있지만 S1 top-level script import/execute 및 파일 수정은 금지한다. 입력원문·기대값은 byte동일하게 보존한다. S1 Program/config/build없음을 새S2계속실행 근거로 기록하며 finalbuild1/twofreshnormalruns를 승인한다.

QA-G05-R27-DEPENDENCY-PATH-20261012-01 OPEN_CORRECTION_ADOPTED_FRESH_EXECUTION_PENDING. 기술 path정정/metadataadmission은 실제 새 build/load/provenance 및 정상regression proof를 대체하지 않는다. 정상런칭·typed/rawPASS 뒤 Master가 이 QA defect의 좁은 closure를 판단한다. Engine002006/Pipeline007/schema/GQ1/PlayerGlobalphysicalsplitOPEN/FoundationHOLD/fullnativeE2NOTRELEASED/closure0. Source/privatebacking staticcredit retained, no runtimeownershipPASS. SameactualhourlyPAUSED60min/173charcorrecttarget/directSolreporting 유지/nextA없음.
''',encoding='utf8')
pointer=H/'MASTER_R27_FROZEN_NEWTONSOFT_POINTER_CORRECTION_20261012.json';assert not pointer.exists()
write(pointer,{'at':at,'Master_controlling_correction':row(review),'original_S1_WP':row(Path(d['wp_path'])),'manifest':row(fm),'missing_pointer':str(missing),'missing_not_admitted':True,'actual_manifest_row':njrow,'admitted_frozen_loader_reference':dict(row(nj),mvid=njMvid),'admission_scope':'DLL_METADATA_COMPILER_REFERENCE_AND_MANAGED_LOADER_SUPPORT_ONLY_NOT_A_RUNNER_OR_NATIVE','candidate_unchanged':True,'no_copy_move_download_or_rebuild':True,'S1_error_raw':row(Q/'PREPARE_RUNNER_FAILURE_RAW.txt')})
vp=C/'MASTER_SOL_R27_S1_DEPENDENCY_STOP_COMPLETION_VERIFICATION_20261012.json';assert not vp.exists()
proof={'at':at,'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION,'delivery_id':x['delivery_id'],'wp_id':x['wp_id'],'wp_revision':'S1','result_id':x['result_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'actual_snapshot':sn,'evidence_count':15,'protected':13652,'candidate_modify_rebuild':0,'candidate_QA_build_execute':0,'execution_verdict':'NOT_EXECUTED_NOT_CANDIDATE_FAIL_OR_PASS','master_verdict':verdict,'master_review_path':str(review),'master_review_sha256':sha(review),'pointer_correction':row(pointer),'native_e2_released':False,'closure_changed':False,'foundation':'HOLD','scheduler_actual':cfg}
write(vp,proof);rec=dict(proof,proof_path=str(vp),proof_sha256=sha(vp));rr['processed_results'].append(rec);rr['updated_at']=at;write(rp,rr)
stp=H/'DISPATCHER_STATE.json';st=read(stp);st['endpoints']['sol'].update(execution_phase='TERMINAL_S1_STOP_MASTER_ACCEPTED',current_runtime_idle_verified=True,last_result_id=x['result_id'],last_runtime_observation_cursor=sn['cursor'],latest_review=str(review))
for z in st['deliveries']:
 if z.get('delivery_id')==x['delivery_id']:z.update(status='COMPLETED_BLOCKER_REPORT_MASTER_REVIEWED_NOT_EXECUTED',master_review=str(review))
write(stp,st);event(dict(rec,event_id=x['delivery_id']+'-MASTER-COMPLETE',type='SOL_R27_S1_BLOCKER_MASTER_DEPENDENCY_POINTER_CORRECTED'))
paths={str(Path(f['path']).resolve()).lower():f for f in base['files']}
for p in Q.rglob('*'):
 if p.is_file():paths[str(p.resolve()).lower()]=row(p)
report=Path(x['report']['path']);paths[str(report.resolve()).lower()]=row(report)
base2=C/'MASTER_R27_S2_CORRECTED_LOADER_PROTECTED_BASELINE_20261012.json';assert not base2.exists();write(base2,{'at':at,'files':list(paths.values()),'protected_unique_paths':len(paths),'S1_original_failure_raw_source_oracle_and_terminal_graph_preserved':True,'currentproduction9_frozen83_unchanged':True})
t['preservation_policy']['qa_preserved_manifests'].append({'path':str(Q/'EVIDENCE_MANIFEST.json'),'sha256':sha(Q/'EVIDENCE_MANIFEST.json')});t['r27_S1_stop_additional_preservation']=row(base2);write(bp,b)
Q2=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012';Q2.mkdir()
wp2=H/'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2.md';assert not wp2.exists();oldWP=Path(d['wp_path']).read_text(encoding='utf8')
newWP=oldWP.replace('SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S1-20261012-01','SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012-01').replace('INDEPENDENT / S1','INDEPENDENT / S2').replace(str(Q),str(Q2)).replace(str(missing),str(nj)).replace(str(Path(d['baseline_path'])),str(base2)).replace(d['baseline_sha256'],sha(base2)).replace('13652경로',str(len(paths))+'경로')
assert str(missing) not in newWP and str(nj) in newWP
wp2.write_text(f'''# S2 controlling dependency pointer correction

{at}; new delivery SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012-01/revisionS2. Read {review} SHA{sha(review)} and {pointer} SHA{sha(pointer)} first. Preserve original S1 raw stop/metadata script/expected/oracle/terminalgraph byteexact. S1 had noProgram/config/QAcompile/candidatecall/run; this new S2 is explicitly approved continuation on SAME frozen83/selectedcandidate and SAME normal4/fulltyped-raw-copy/prospective provenance contract. The sole technical change is correct frozen Newtonsoft loader path {nj} SHA{sha(nj)}/MVID{njMvid}/711952bytes. New QA baseline{len(paths)} includes all S1 artifacts. No candidate/dependency copying/moving/download/productionrebuild and no A executable/runner invocation. To prepare own newS2 source, TEXT-only clone S1 own unexecuted prepare_runner/review_setup generator into S2 if useful and change ONLY root/delivery/revision/WP pointers and this exact loader pointer; keep intended normal testlogic/inputs/expectations. Do not import/execute or edit S1 files. Pin own new source+allrefs+inputs+unchanged oracle before finalbuild/calls. Future normalFAIL/proofgap stops/rawpreserves/Masterreports; no unapproved retry. New immutableACK_INITIAL+resultID+newreport and terminal independentS2, never overwrite S1.

## Full S2 approved contract

{newWP}
''',encoding='utf8')
delivery='SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012-01'
c.update(sol_status='R27_S1_DEPENDENCY_STOP_ACCEPTED_S2_CORRECTION_PREPARED_NOT_SENT',sol_latest_completion=rec,last_sol_cursor=sn['cursor'],sol_next_wp_prepared=str(wp2),sol_next_prepared_delivery={'delivery_id':delivery,'wp_id':'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT','wp_revision':'S2','wp_path':str(wp2),'wp_sha256':sha(wp2),'baseline_path':str(base2),'baseline_sha256':sha(base2),'protected_unique_paths':len(paths),'qa_root':str(Q2),'delivery_status':'PREPARED_NOT_SENT','unknown_delivery':False,'frozen_manifest':str(fm),'frozen_manifest_sha256':sha(fm),'selected_sha256':d['selected_sha256'],'selected_mvid':d['selected_mvid'],'loader_admission':row(pointer)},sol_next_action='FRESH_IDLE_ORIGINALSOL_DELIVER_CORRECTED_LOADER_S2_SAME_EXACT_CANDIDATE_AND_NORMAL_TESTCONTRACT',updated_at=at)
c['last_monitor_run']={'run_id':RUN,'guard_pid':PID,'guard_session':SESSION,'at':at,'status':'R27_S1_DEPENDENCY_STOP_DISPOSED_S2_CORRECTED_POINTER_APPROVED_NOT_SENT','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
defect=C/'MASTER_DEFECT_QA_G05_R27_DEPENDENCY_PATH_20261012.json';assert not defect.exists();write(defect,{'at':at,'id':'QA-G05-R27-DEPENDENCY-PATH-20261012-01','owner':'Master QA WP pointer','status':'OPEN_CORRECTION_ADOPTED_FRESH_EXECUTION_PENDING','initial_failure':row(Q/'PREPARE_RUNNER_FAILURE_RAW.txt'),'Master_pointer_correction':row(pointer),'newS2_WP':row(wp2),'actual_candidate_FAIL':False,'fullnativeE2_released':False})
event({'at':at,'event_id':delivery+'-PREPARED','type':'S1_STOP_PRESERVED_NEW_S2_CORRECTED_LOADER_APPROVED_NOT_SENT','wp':row(wp2),'protected':len(paths),'newcandidate':False})
para=f'\n\n## LOCAL-R27-QA-S1-DEPENDENCY-STOP-S2-APPROVED — {at}\n{verdict}. OriginalSolidle169/15evidence13652protected/current9/frozen83matched/ownprepareexit1 FileNotFoundError BEFOREgeneratedProgram-config-build-load-candidatecalls0;notcandidateFAIL/notPASS/goalunachieved. Master erroneous selectedDLLparent/Newtonsoft path absent; actual immutable manifest DLL{nj}/SHA{sha(nj)}/MVID{njMvid}/711952bytes independentlymetadataadmittedONLYreference-loader. Candidate/source/manifest unchanged/no copy-move-download-rebuild/S1raw evidence preserved. NewS2 {delivery} SAMEselected68BFE510...MVID44ba753c.../normal4/full15typedraw-ownership/newfinalbuild1-twofresh/prospectiveproof requirements;protected{len(paths)} includesALLS1stop/oracle/source/terminalgraph. APPROVED_NOT_SENT untilfreshidle/directtool; no AnewWP/schedulerchange/closure. SameactualhourlyPAUSED60min/directSolpush/FoundationHOLD/fullEnginePipelineGQ1OPEN/nativeE2NOTRELEASED. QAdependencydefectOPEN_CORRECTION_ADOPTED_FRESH_EXECUTION_PENDING. Review{review};proof{vp};S2WP{wp2}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'status':'S1_STOP_DISPOSED_NEW_S2_CORRECTED_POINTER_APPROVED_NOT_SENT','protected':len(paths),'S2WP':str(wp2),'loader_SHA':sha(nj),'loader_MVID':njMvid}))
