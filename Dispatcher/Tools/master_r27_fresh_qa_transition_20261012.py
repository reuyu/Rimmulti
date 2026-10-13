from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R27-SOL-PREP-COMPLETE-20261012-01';PID=11168;SESSION=8532;P='MASTER_SOL_R27_CHILD_CAPTURE_INDEPENDENT_'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def data(p):return json.loads(read(p)['content'][0]['text'])
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];stage=sys.argv[1]
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
assert t['dispatch_id'].endswith('cdc223f3') and t['status']=='COMPLETED_REVIEWED_SOURCE_CAPTURE_CREDITED_SCOPED_QA_PENDING'
if stage=='prepare':
 assert c['active_operation'] is None
 v=read(C/'MASTER_GATE05_R27_CHILD_CAPTURE_E1_VERIFICATION_20261012.json');assert v['verification_status']=='MASTER_DISPOSED'
 fm=Path(v['frozen_manifest']);assert sha(fm)==v['frozen_manifest_sha256'];freeze=read(fm);assert len(freeze['files'])==83
 paths={str(Path(f['path']).resolve()).lower():f for f in read(Path(c['sol_current_delivery']['baseline_path']))['files']}
 for f in freeze['files']:
  for k in ['original_path','frozen_path']:
   p=Path(f[k]);assert sha(p)==f['sha256'] and p.stat().st_size==f['size'];paths[str(p.resolve()).lower()]=row(p)
 previous=Path(c['sol_current_delivery']['qa_root'])
 for p in previous.rglob('*'):
  if p.is_file():paths[str(p.resolve()).lower()]=row(p)
 for f in read(Path(t['additional_completed_QA_preservation']['path']))['additional_QA_original_files']:paths[str(Path(f['path']).resolve()).lower()]=f
 base=C/'MASTER_R27_FRESH_CAPTURE_QA_PROTECTED_BASELINE_20261012.json';assert not base.exists();write(base,{'at':at,'files':list(paths.values()),'protected_unique_paths':len(paths),'all_current_production9_and_frozen83_fixed':True,'all_old_QA_raw_FAIL_and_preparation_preserved':True})
 Q=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S1-20261012';Q.mkdir()
 wp=H/'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S1.md';assert not wp.exists()
 F=Path(v['frozen_root']);dll=F/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb')
 managed=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
 assert sha(managed)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
 delivery='SOL-GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S1-20261012-01'
 wp.write_text(f'''# WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT / S1

Master 승인 {at}. Delivery {delivery}. OriginalSol local01a11583-ff90-73e0-8916-d021e2bb038d. APPROVED new exact frozen candidate normal PURE unit QA, NOT_SENT until fresh idle/direct proof. FullnativeE2 NOT_RELEASED.

Master review {v['master_review_path']} SHA{v['master_review_sha256']}와 independent prep review {H/'MASTER_REVIEW_ENGINE_GATE05_R27_CHILD_CAPTURE_QA_PREPARATION_S1_20261012.md'}, source implementation WP {H/'WP_ENGINE_GATE05_R27_CHILD_CAPTURE.md'} 및 controlling actual API correction {H/'MASTER_R27_CAPTURE_API_NAME_CORRECTION_20261012.md'}를 읽는다. A E1 partial fourPASS/exit0를 fresh QA PASS로 재사용하지 않는다. Producer report readonly-exception claim은 actual runner에서 관측되지 않았고 재현하지 않는다.

정확 새 frozen83 manifest {fm} SHA{sha(fm)}. 선택 DebugDLL {dll} SHA{v['selected_sha256']}/MVID{v['selected_mvid']}/308224bytes,matchingPDB {pdb} SHA{v['selected_pdb_sha256']}/73776bytes. 새 source WorkerB292AB846F78568F74333F58C5967ED38CAAA2F59B07393FC846F4329583E388/239574bytes,Census391F9645.../csproj571A58...; bothmodesCodeView/sourcePDB4of4 Master verified. {F} 내 matching PDB documents로만 source결속; 생산 current source를 new frozen snapshot처럼 취급하지 않는다. Normal PURE candidate 실행은 이 selectedDLL만 가능; Release metadata-only/no Release execution. Public Capture/source4/metadata/getters형과 task27 CLRstring22/long3/int1/bool1을 staticPE/source로 확인한다.

보존 baseline {base} SHA{sha(base)} {len(paths)}경로. 모든 currentproduction9 및 newfrozen83,originalSolR27preparation23+primarygraph/R25S2PASS/S1rawFAIL/olderQA/archive/Pipeline을 before-after 실제SHA-size로 검사. Production source/DLL/PDB/candidate rebuild/modification0. Unknown mismatch는 raw 보존·Master보고/자체baseline 정상화 금지. Metadata dependencycopy4 {managed} SHA{sha(managed)} frozen_path4만 loader support로 사용하며 원본Steam/Workshop은 읽거나복사하지 않는다. Frozen selected candidate Newtonsoft.Json은 {dll.parent/'Newtonsoft.Json.dll'}를 hash/MVID로 결속한다. Nativecontentprofile/gameexecute권한이 아니다.

실행 허용 정상 scope: 독립 rawbytes parentSIMULATION/childREAD_ONLY **IssueAdmissionReceiptFromBytes**, normal receipt IsValid, **OperatorChildLaunchInputs.Capture**, 15typedgetters/관련 snapshot-policyrecord/receipt and snapshot ToRedactedJson PURE helper 관측. Constructor/private fields reflection이나global ActiveReceipt/IsTrusted 변경 금지. Provider/cache getter/Compute/InvalidateCache/game/Awake/Process/File admission/native/operator/CLI/registration/lifecycle/channel/currenttaskauthority/rejection/default/null/adverse/oldA runner/old whole battery 실행은0. Normal runner에서 ownQA output을 쓰는 File IO만 허용. 기존 IsValid nested Path.GetFullPath 비교는 승인 helper의 source fact이며 새Capture directnew normalization과 구분. Task scalar ??empty SOURCE_ONLY/nullableinput실행0; 완전히 명시한 normalnonnull literal27만 사용.

Independent 기존 preparation oracle {previous/'PROSPECTIVE_CAPTURE_ORACLE.json'} SHA{sha(previous/'PROSPECTIVE_CAPTURE_ORACLE.json')}, callplan {previous/'PROSPECTIVE_CALLPLAN.json'} SHA{sha(previous/'PROSPECTIVE_CALLPLAN.json')}, COPY_OWNERSHIP_MATRIX/CONSTRUCTION_COPY_RISKS/FUTURE_EXECUTION_PROVENANCE_CHECKLIST를 요구사항으로 사용. 이것들은 실행PASS가 아니다. 네 독립 pairPLAIN_PLAIN/OPAQUE_OPAQUE/PLAIN_OPAQUE_PADDED/OPAQUE_PLAIN_PADDED raw parent14+child14 각기 원문유지; parent.role바꿔 child파생금지. Original lowercamel descriptor7 declaration순서와 option7 values순서를 구분, raw expected SHA/opaquepolicy ID-revision/case/공백/Ω/UTC/path/packageorder 원문보존. Validated immutable existing receipt refs보관은 허용; source backing/Array.AsReadOnly private arrays 비노출은 static audit, runtime는 detached copy 정상 controls만.

Primary direct one-run calls factory8/normalIsValid8/Capture4와 fifteen getters4×3phase=180, nestedreceipt validations/selector/parser/digest/redaction helpers 별도 구분. Every phase15getter 보관값으로 fullCapture+bothreceipt11/snapshot15/policyrecord4/redaction13/nestedredaction11/approved7/task27/list7+2와 codepoints/order/type/rawUTF8 전부 검증. 단계 BEFORE→callerTask27+actualsubmittedparentchilddescriptor7 전필드 mutation→returnedTask27/approved7/policydecl-record4/detachedlists mutation 후 original전체 재관측. 원본rawfixture/files는 pin뒤재작성금지. Edited task/descriptor를 factory/Capture에 재적용하지 않는다. Null/invalid/default/adverse 입력을 사용하지 않는다. IReadOnlyList cast-write/NotSupportedException probe금지; detached materialized copies만변경하고 hidden backing은 source static 판정과구분. Normal graph40raw expectation은 preparation의 독립ordereddata; actual result에서 expected 생성/normalization/날짜coercion/whitespace 무시/필드생략 금지.

새 QA-owned runner source는 {Q/'Harness'}에서 작성. Production candidateimmutable. Finalcompiler/build source/프로젝트/입력/독립 fulltyped+raworacle/primaryandgroupedhelpercallplan/runner+allmanagedrefsha/actualtoolchain경로SHA-size/complete invocation을 **finalbuild와 anycandidatecall 전에** prospectivelyseal. 필요metadatahelpers만새QA소유로작성하거나olddefinition AST-only선별읽기; oldtop-level script import/execute금지. QA final build1(실패 시 raw보존보고/자체재빌드로PASS만들지않음), twofresh en-US/de-DE runs ONLY. Duplicate runner/preflight candidate call금지. Complete compiler stdoutstderr/exitcode/fullOSstdoutstderr/PID/culture/executableSHA/argv/cwd/elapsed and eachactual loadedmanaged SHA+independentlyreadMVID/CLR provenance/pre-post allcandidate-runtime-input-oracle-callplan/fullrecursive output pathsSHA-size. 첫run을두번째전에seal하고 bothafterall재검증. FrozenPDBsource/Compilerallrefs/compiledQAexe-PDB/loadeddllidentity를별개결속. Native-authorityproof와혼동금지.

정상unexpectedFAIL/exit≠0/proofgap이면 원문을 보존하고 **중단·Master보고**. 테스트기대값변경/후행normalization/추가실행/compiledcandidate修正/대체model/QAauto-repair는 승인하지 않는다. 필요routine보완은 Master가 동일권한내 direct지시한다.

산출 {Q}: immutable ACK_INITIAL+ACK/resultID/allbeforeafter inventories/newrunner/compiler raw/prospectivepins/oracles/typedcomparison/rawgraphs/crossculturefourpairs/rawOSstreams/loadedSHA-MVID/recursive seals/finalFreeze/report/manifest/index/ACK_COMPLETION_BINDING/COMPLETIONlast. Report {R/'docs/QA_EngineHost_Gate05_R27_Child_Capture_Independent_S1_20261012.md'}. Actualcontrols/count/coverage/UNOBSERVED/SOURCE_ONLY/FAIL를구분. InitialACK 및완료를Master01a1156b-97ec-7ce0-9e4a-dfc4a3acb174/local에 userauthorizeddirectthreadtools로보고; returntransportproof는 primaryimmutable PENDING과구분/unknown delivery재시도전확인. Governance/WP/schema/closure/scheduler 수정금지.

Scope DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED; publicsuccess/IsValid/IsTrusted/equality는issuer/pairing/currenttaskauth/nativeauthority가 아니다. Master 최종closure/release; actualproducer/private registry/M04native/frontend/cwd-genroot/M05equality/M06content/M07revoke/fullEnginePipelineGQ1/exactPlayerGlobal/physicalsplitOPEN/FoundationHOLD/nativeE2NOTRELEASED. 새QA 결과는이exactcandidate와이정상PURE범위만이다.
''',encoding='utf8')
 c.update(sol_next_wp_prepared=str(wp),sol_next_prepared_delivery={'delivery_id':delivery,'wp_id':'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT','wp_revision':'S1','wp_path':str(wp),'wp_sha256':sha(wp),'baseline_path':str(base),'baseline_sha256':sha(base),'protected_unique_paths':len(paths),'qa_root':str(Q),'delivery_status':'PREPARED_NOT_SENT','unknown_delivery':False,'frozen_manifest':str(fm),'frozen_manifest_sha256':sha(fm),'selected_sha256':v['selected_sha256'],'selected_mvid':v['selected_mvid']},sol_next_action='ORIGINALSOL_IDLE_FRESH_R27_EXACT_NORMAL_PURE_QA_APPROVED_NOT_SENT',updated_at=at)
 c['master_monitor_automation'].update(status='PAUSED',desired_status='PAUSED',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,pause_reason='R27 A terminal reviewed; fresh original Sol normal PURE QA')
 write(cp,c);stp=H/'DISPATCHER_STATE.json';st=read(stp);st['master_monitor_automation']=c['master_monitor_automation'];write(stp,st)
 write(C/'MASTER_R27_TERMINAL_PAUSED_FRESH_QA_APPROVED_20261012.json',{'at':at,'actual_scheduler':cfg,'newQA':c['sol_next_prepared_delivery'],'next_A':'NONE_NOT_SENT','runtime_e2_released':False,'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION})
 event({'at':at,'event_id':delivery+'-PREPARED','type':'NEW_EXACT_R27_NORMAL_PURE_QA_APPROVED_NOT_SENT','wp':row(wp),'protected':len(paths)})
 print(json.dumps({'status':'FRESH_QA_PREPARED_NOT_SENT','protected':len(paths),'WP':str(wp),'selected':v['selected_sha256']}))
elif stage=='sending':
 assert c['active_operation'] is None;op=c['sol_next_prepared_delivery'];assert op['delivery_status']=='PREPARED_NOT_SENT'
 pre=data(C/(P+'PREDISPATCH_20261012.json'))['polls'][0];assert pre['thread']['id']==c['sol_thread_id'] and pre['thread']['status']['type']=='idle' and pre['latestTurn']['status']=='completed'
 for k in ['wp','baseline','frozen_manifest']:assert sha(Path(op[k+'_path'] if k!='frozen_manifest' else op[k]))==op[k+'_sha256']
 op.update(type='SOL_R27_FRESH_EXACT_NORMAL_QA',delivery_status='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL',unknown_delivery=True,actual_predispatch=pre,attempt_started_at=at,guard_run=RUN,guard_pid=PID,guard_session=SESSION);c['active_operation']=op;write(cp,c);event({'at':at,'event_id':op['delivery_id']+'-ATTEMPT','type':'SOL_R27_FRESH_NORMAL_QA_DIRECT_ATTEMPT','unknown_delivery':True});print('ONE_DIRECT_DELIVERY_PENDING')
elif stage=='sent':
 op=c['active_operation'];assert op['unknown_delivery'];paths={k:C/(P+n+'_20261012.json') for k,n in [('pre','PREDISPATCH'),('tool','SEND_TOOL'),('post','POSTSEND')]}
 pre=data(paths['pre'])['polls'][0];post=data(paths['post'])['polls'][0];assert not read(paths['tool']).get('isError') and post['thread']['id']==c['sol_thread_id'] and post['latestTurn']['id']!=pre['latestTurn']['id'] and post['thread']['status']['type']=='active' and post['latestTurn']['status']=='inProgress'
 proof=dict(op,at=at,delivery_status='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN',unknown_delivery=False,status='SENT_IN_PROGRESS_ACK_PENDING',actual_snapshot=post,scope='NEW_SELECTED_FROZEN_R27_DEFENSIVE_STATIC_AND_NORMAL_PURE_CAPTURE_UNIT_QA',production_modify_rebuild=0,qa_owned_final_runner_build_admitted=1,normal_culture_runs_admitted=2,native_e2_released=False,foundation='HOLD',monitor='ACTUAL_PAUSED60MIN')
 for k,p in paths.items():proof[k+'_path']=str(p);proof[k+'_sha256']=sha(p)
 vp=C/(P+'DELIVERY_VERIFICATION_20261012.json');assert not vp.exists();write(vp,proof)
 c.update(active_operation=None,sol_current_attempt_id=op['delivery_id'],sol_current_wp=op['wp_id'],sol_current_revision='S1',sol_current_result_id=None,sol_status='R27_FRESH_NORMAL_PURE_CAPTURE_QA_SENT_ACK_PENDING',sol_current_ack=None,sol_current_delivery=proof,sol_latest_delivery=proof,last_sol_cursor=post['cursor'],sol_next_wp_prepared=None,sol_next_prepared_delivery=None,sol_next_action='COLLECT_FRESH_R27_QA_RESULT_THEN_MASTER_SCOPED_DISPOSITION_AND_NEXT_BOUNDED_TECHNICAL_WORK_AUTOMATIC',updated_at=at);c['last_monitor_run'].update(status='R27_A_TERMINAL_DISPOSED_SCHEDULER_PAUSED_FRESH_SOL_NORMAL_QA_ACTUAL_SENT',release_status='PENDING_ACTUAL_FINALLY');write(cp,c)
 sp=H/'DISPATCHER_STATE.json';st=read(sp);st['endpoints']['sol'].update(current_wp=op['wp_id'],current_wp_revision='S1',current_delivery_id=op['delivery_id'],current_result_id=None,current_turn_id=post['latestTurn']['id'],actual_turn_id=post['latestTurn']['id'],execution_phase='IN_PROGRESS',ack_verified=False,explicit_ack_pending=True,current_runtime_idle_verified=False,last_runtime_observation_cursor=post['cursor']);st['master_monitor_automation']=c['master_monitor_automation'];st['deliveries'].append({'delivery_id':op['delivery_id'],'recipient':'Sol','wp_id':op['wp_id'],'wp_revision':'S1','delivery_status':'SENT','status':'ACTIVE_ACK_PENDING','proof':str(vp),'runtime_e2_released':False});write(sp,st)
 e={'at':at,'event_id':op['delivery_id']+'-ACTUAL_SENT','type':'SOL_R27_FRESH_FROZEN_NORMAL_PURE_QA_ACTUAL_SENT','delivery_id':op['delivery_id'],'proof':str(vp),'proof_sha256':sha(vp),'turn_id':post['latestTurn']['id'],'cursor':post['cursor'],'protected':op['protected_unique_paths'],'selected_sha256':op['selected_sha256'],'selected_mvid':op['selected_mvid'],'no_duplicate_wp':True}
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr);event(e)
 para=f'\n\n## LOCAL-R27-TERMINAL-PAUSED-FRESH-SOL-CAPTURE-QA-SENT — {at}\nSamewareconomy-master actualPAUSED60min173charcorrecttarget. OriginalSol {op["delivery_id"]}/{op["wp_id"]}/S1 actualdirectSENT/newactive turn{post["latestTurn"]["id"]}/cursor{post["revision"]}/ACKpending/no duplicate-substitute. Exactfrozen83SHA{op["frozen_manifest_sha256"]}/Debug{op["selected_sha256"]}/MVID{op["selected_mvid"]} admittedONLYdefensive static+fullyspecified normalfactory8IsValid8Capture4/full15getters/fulltypedraw-copyownership4pair-newQAfinalbuild1-twofreshcultures-prospectiveallcompilerrefsloadedrecursive proof. Protected{op["protected_unique_paths"]}includingcurrent9/newfrozen83/oldQArawFAIL+prep23. Productioncandidate modify-rebuild0/native-global-registration-launcher-adverse0/fullGateE2NOTRELEASED/FoundationHOLD/closure0. Aterminalsourcefixcredited/E1partial notinheritedPASS;nextA noneNOT_SENT pendingQA. Proof{vp}\n'
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
 nx=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';nx.write_text(para+'\n'+nx.read_text(encoding='utf-8-sig'),encoding='utf8');print(json.dumps(e))
else:raise ValueError(stage)
