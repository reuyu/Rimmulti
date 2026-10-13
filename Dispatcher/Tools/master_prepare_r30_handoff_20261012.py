from pathlib import Path
import json,sys,copy,tomllib,hashlib
sys.stdout.reconfigure(encoding='utf-8')
import master_r29_s1_stop_prepare_s2_20261012 as m
def main():
 cs=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');board=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');old=board['tasks'][-1]
 assert cs['active_operation'] is None and old['wp_revision']=='GATE05-R29-STARTUP-PAIR' and old['independent_qa_review']
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf-8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
 review=m.H/'MASTER_REVIEW_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S3_20261012.md';m.check(old['independent_qa_review'])
 dispatch='WE-A-ENGINE-GATE05-R30-HANDOFF-20261012-DIRECT-16ce928f';T=m.R/'Dispatcher/A_TASKS'/dispatch
 if T.exists():assert T.is_dir() and not list(T.iterdir()),'Only own empty preflight directory may be reused'
 else:T.mkdir()
 wp=m.H/'WP_ENGINE_GATE05_R30_HANDOFF.md';release=m.H/'RELEASE_ENGINE_GATE05_R30_HANDOFF_20261012.md';scope=T/'MASTER_R30_AUTHORIZED_SOURCE_SCOPE.json';base=m.C/'MASTER_R30_HANDOFF_PROTECTED_BASELINE_20261012.json';ip=T/'INSTRUCTIONS.md'
 src=m.R/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';data=src.read_bytes();assert hashlib.sha256(data).hexdigest().upper()=='55441CE93DF32F5E5940D99A4A9CA8449B3F7839840CA3A3832C9DB31396FBDE'
 anchors=[('BOOTSTRAP_HANDOFF_AFTER_PURE_ADMISSION',b'                    // Install parent receipt into component',b'                // Legacy self7 fallback mode'),('PRIVATE_OWNER_HANDOFF_STATE',b'        private OperatorStartupPairSnapshot? _privatePairProfile;',b'        private TcpListener? listener;'),('AWAKE_EARLY_PAIR_GATE',b'                if (TryAcquirePendingStartupHandoff',b'                // Explicitly disable fastEcology'),('PAIR_MODE_LAUNCH_HOLD',b'            {                if (_privatePairProfile != null)',b'                if (currentValidatorTask == null)\n                {\n                    RevokeReadiness("No active ValidatorTask outstanding to launch validator for.");'),('OWNER_SCOPED_DESTROY',b'        {            _privatePairProfile = null;',b'            isRunning = false;\n            try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }')]
 spans=[]
 for name,a,z in anchors:
  assert data.count(a)==data.count(z)==1,name
  start=data.index(a);end=data.index(z);assert start<end
  spans.append(dict(id=name,start=start,end=end,before_sha256=hashlib.sha256(data[start:end]).hexdigest().upper(),context_before_sha256=hashlib.sha256(data[max(0,start-128):start]).hexdigest().upper(),context_after_sha256=hashlib.sha256(data[end:end+128]).hexdigest().upper()))
 spans.sort(key=lambda v:v['start']);assert all(a['end']<=b['start'] for a,b in zip(spans,spans[1:]))
 prod=[m.row(Path(v['path'])) for v in old['all9_before']];assert len(prod)==9
 mutable=list(old['allowed_mutable_paths']);assert len(mutable)==7 and str(src) in mutable
 fixed=[v for v in prod if v['path'] not in mutable];publisher=m.R/'scratch/OperatorStartupPairR29/publish_operator_pair.py';fixed.append(m.row(publisher))
 assert len(fixed)==3
 baseline=m.read(m.C/'MASTER_R29_S3_PAIR_QA_PROTECTED_BASELINE_20261012.json');paths={v['path'].lower():v for v in baseline['files'] if v['path'] not in mutable}
 pres=m.read(m.C/'MASTER_R29_S3_COMPLETED_TERMINAL_PRESERVATION_20261012.json')
 for v in pres['files']+fixed+[m.row(review)]:paths[v['path'].lower()]=v
 for v in paths.values():m.check(v)
 m.create(base,dict(at=m.now(),files=list(paths.values()),protected_unique_paths=len(paths),excluded_exact_current_mutable7=mutable,old_R29_source_and_frozen132_immutable=True,Sol_S3_terminal_and_all_old_stops_immutable=True,publisher_Census_csproj_fixed=True))
 contract=m.H/'MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md';defect=m.C/'MASTER_DEFECT_ENGINE_G05_R29_HANDOFF_20261012.json'
 m.create(scope,dict(at=m.now(),all9_before=prod,Worker_original=m.row(src),allowed_mutable_paths=mutable,allowed_new_source_paths=[],fixed_current_files=fixed,allowed_byte_spans=spans,outside_spans_entire_bytes_fixed=True,protected_baseline=m.row(base),controlling_review=m.row(review),contract=m.row(contract),defect=m.row(defect),TryInstallOperatorStartupConfig_and_legacy_parent_seal_byte_fixed=True,PURE_Pair_Capture_factories_API_codec_currenttask_Census_publisher_byte_fixed=True))
 wp.write_text(f'''# A R30 — owner-bound startup handoff 修正

{dispatch}; WP_ENGINE_GATE05_R30_HANDOFF / GATE05-R30-HANDOFF / envelope33. Master가 승인한 좁은 후속 구현이다. 먼저 {review}, {defect}, {contract}, {scope} 전체를 읽는다. R29 새 후보 정상 PURE Pair6/Capture4 독립 QA는 각438PASS로 채택됐지만 handoff/carrier/publisher High3과 native E2는 OPEN이다. R29 candidate/QA raw/과거 실패를 수정하지 않는다. Root는 {m.R}; 실제 SRS {m.R/'docs/요구사항_명세서.md'} 및 accepted Master/C corrections를 유지한다. gitroot 없음; init/reset/clean 금지.

## 이번 수정의 정확한 목표

ENGINE-G05-R29-HANDOFF-20261012-01만 수정한다. Carrier 입력/검증 전 IO, publisher, UTF8/parser, task/receiver/native/launcher 허용 범위 확장은 후속 작업이다. current WorkerBridge.cs의 지정5 spans와 existing6 build outputs만 변경할 수 있다. Publisher/Census/csproj, 기존 PURE Pair/Capture/factory 및 TryInstallOperatorStartupConfig/legacy parent seal 본문과 기타 전체 bytes는 고정한다. 새로운 파일/source/package/reference 추가를 허용하지 않는다. Source baseline/eachspan/context SHA는 {scope}; 밖의 전체 byte segments를 이전 R29 frozen source와 직접 비교한다.

1. 실제 `_activeAdmissionReceipt`와 pending parent receipt 및 pair.ParentReceipt를 같은 receipt object reference로 결속한다. receipt↔snapshot ReferenceEquals를 제거하고 snapshot 관계는 해당 receipt.Snapshot과 정확히 검사한다. 문자열 ID/SHA 값만 같다고 같은 owner receipt로 대체하지 않는다. 공개 child/global registry/receipt replacement/reset API를 만들지 않는다.
2. Pair-required mode와 정확한 freshly created owner/cohort를 AddComponent 이전에 설정한다. Pending set은 installed receipt/parent/pair/owner가 같은 cohort임을 검사하고, 기존 live pending을 덮어쓰지 않으며 bool/explicit failure를 bootstrap이 확인한다. Acquisition은 정확한 this.gameObject owner에 한 번만 성공한다. 소비 후 다른 instance나 stale owner가 재사용할 수 없도록 mode/ownership bookkeeping을 설계한다. static child profile을 지속 보관하지 않고 성공하면 private instance profile로 옮긴다.
3. Awake에서 pair-required acquisition 실패는 fastEcology 변경, log callback 구독, package policy 설정, listener/thread 생성보다 먼저 명시적으로 종료한다. Pair-required는 profile != null 여부로 추론하지 않는다. 필요한 mode 상태는 pending 소비 뒤에도 failclosed/launch HOLD를 유지한다. Legacy mode는 새 keys가 모두 없는 기존 경로에서만 그대로 유지하며 새 pair 실패를 legacy 성공으로 낮추지 않는다. 이미 known carrier parser 결함을 고쳤다고 주장하지 않는다.
4. M05 HOLD는 pair-required mode/owner 상태로 판단한다. profile acquisition 실패/cleanup 후 profile null이 되어도 old launch body로 들어가지 않는다. return ERROR M05_NOT_ADMITTED를 유지하고 currentValidatorTask/isConsumed/RevokeReadiness/Process/receiver 본문은 그대로 둔다. 실제 child launch 권한은 이번 WP에서 주지 않는다.
5. 성공한 acquire의 pending 소비와 failure/destroy cleanup은 owner/cohort 범위로만 수행한다. 무관 instance의 OnDestroy가 다른 pending을 지우거나 required mode를 해제하지 않는다. Bootstrap set/AddComponent exception 정리도 소유한 pending에만 적용하며 Unity Awake가 즉시 호출된다는 가정으로 성공 직후 pending을 지우지 않는다. owner custody/native timing source 설계만으로 실제 runtime proof/High closure를 선언하지 않는다.

실제 Unity 객체 equality 특성과 alive/destroyed state는 ReferenceEquals custody와 구분한다. null/operator equality 의미를 원문 source/reference와 검토하고 제한을 보고한다. 새 schema/issuer/nonce/auth/CLI task fields를 만들지 않는다. 모호한 구조가 있으면 구체적 source evidence와 proposed minimal span diff를 보고하되 이미 승인된 범위의 정상 구현은 자율 수행한다. 다른 span 수정이 필요하면 진행 전 BLOCKED로 명시하며 scope를 임의로 넓히지 않는다.

## 실제 증거와 실행 범위

Source 전후 control-flow table을 작성한다: bootstrap pair-required mark→owner-bound set→AddComponent→Awake exact receipt/owner/one-use acquire→required failure return 또는 private instance success→M05 HOLD→owner cleanup. 각 invariant와 실제 source line/byte span을 결속한다. Wrong owner/second consume/overwrite/missing pair/profile-null/destroyed owner는 이번 WP SOURCE_ONLY table로 분석한다; adversarial/native lifecycle 실행이 아니다. 단순 문자열 grep만으로 native proof나 closure를 선언하지 않는다.

Production Debug/Release build와 A-owned 새 PURE regression runner만 허용한다. Development compiler 최대3 attempt/full raw 기록; 최종 final source/all references/toolchain/expected literal inputs/callplan pin을 final build와 각 실행 전에 작성한다. R29 정상 PURE Pair6/Capture4 regression을 새 candidate에서 two fresh en-US/de-DE 프로세스로 수행한다. 기존 Sol inputs/oracle는 TEXT-only reference이고 old QA helper/runner를 import/실행하지 않는다. 독립 parent14/child14/original7/pairId/copy expected full graph 및 raw를 실행 전에 선언하고 output으로 기대값을 만들지 않는다. 기존 source APIs의 receipt/getter/data-only calls만 사용한다. Production bootstrap/global install/set/acquire/Awake/private reflection/GameObject/Unity/native/currenttask/cache/provider/Process/publisher/rejection/adverse 실행0. Handoff runtime regression은 이후 별도 native admission을 요구한다. Pure regression PASS를 handoff runtime PASS로 부르지 않는다.

각 build/run 실제 argv/cwd/culture/ownedPID/numeric exit/full stdout-stderr/CLR+loadedmanagedpathSHA-MVID/recursive outputs/pre-post를 남긴다. 최종 Debug/Release actual MVID/CodeView/PDB/source4/4, 선택 candidate DLL SHA, compile references/compiler SHA를 따로 측정한다. 복사 검증은 실제 편집한 data 범위만 쓰고 holder replacement를 in-place test로 과장하지 않는다. 실패/identity gap은 raw 보존 후 BLOCKED; production/adverse retry 금지. Passive read path/encoding 오류는 실제 고정 inventory/unique frozen source 경로로만 고쳐 새 raw capture를 남길 수 있으며 oracle/source/schema/hash/test mismatch는 숨기지 않는다.

## 산출물과 보호

Task root {T}. ACK.json은 exact dispatch/WP/revision/envelope33/읽은 contract·scope·baseline hash/IN_PROGRESS를 work 전에 쓴다. IMPLEMENTATION_REPORT.md, SOURCE_SCOPE_DIFF.json(5spans+밖의 전체 bytes), HANDOFF_CONTROL_FLOW_AND_CUSTODY.json, CANDIDATE_IDENTITY.json, RELEASE_MANIFEST.json, FINAL_PRE_RUN_MANIFEST.json, E1_NORMAL_RESULTS.json, FULL_TYPED_RAW_COPY_BINDING.json, BEFORE_AFTER_PRESERVATION.json, own fresh harness/raw/tool proofs/RESULT_INDEX.json을 작성한다. Root report {m.H/'A_ENGINE_GATE05_R30_HANDOFF_REPORT_20261012.md'}. COMPLETION.json은 마지막 atomic write, 고유 result WE-A-ENGINE-GATE05-R30-HANDOFF-RESULT-01, schema1/status COMPLETED 또는 BLOCKED/e1_verdict/limitations list/report·manifest·모든 artifacts actual SHA/bytes와 정확 identity를 결속한다. 표준 필수 필드와 실제 table 의미를 구분한다.

Protected baseline {base}/SHA{m.row(base)['sha256']}/{len(paths)}. Original Pipeline/Engine archives/frozen candidates/all QA raw, R29 frozen132, publisher/Census/csproj, installed incident baseline을 보존한다. Master governance/state/WP/AGENTS/SRS 변경, 설치/deployment/Steam/assets copy 금지. Known installed mismatch OPEN/actor UNKNOWN을 복원·정규화하지 않는다. Sole production writer A; Master의 freeze/fresh Sol targeted QA 이후에만 좁은 source fix 채택, whole native E2/High closure/release는 별도 Master 판정이다. Engine002006/Pipeline007/current schema/G-Q1 OPEN/Foundation HOLD.
''',encoding='utf-8')
 release.write_text(f'# R30 narrow source repair admission\n{dispatch}/envelope33. Five Worker spans +six current build outputs only. Handoff High1 source repair/PURE regression permitted. Carrier/publisher/currenttask/native/launch and fullGate E2 not admitted. {wp}; {scope}; {base}. Exact new freeze/fresh independent QA required; Foundation HOLD.\n',encoding='utf-8')
 ip.write_text(f'# Master 승인 A R30\n전체 읽기: {review}\n{defect}\n{contract}\n{wp}\n{release}\n{scope}\n보호 baseline: {base}\nR29 정상 unit PASS를 보존하고 handoff High1만 지정5spans로 수정. Publisher/carrier/currenttask/native 미허용. 실제 installed receipt identity/owner-one-use/required-mode early failure/M05 hold/owner cleanup. Exact ACK33 before work; COMPLETION last.\n',encoding='utf-8')
 message=f'Master 승인 R30입니다. {ip} 전체와 연결된 WP·scope를 읽고 수행하세요. Sol의 R29 정상 데이터 QA는 통과로 채택했습니다. 이번에는 handoff High1만 지정5구간에서 수정합니다: 실제 installed receipt identity, owner 일회 전달, pair-required 실패의 조기 종료, M05 HOLD, owner cleanup. Carrier·publisher·native 실행은 다음 범위로 남깁니다. Exact ACK33와 새 후보·원문 증거·COMPLETION을 남기세요.'
 msg=T/'UI_MESSAGE.txt';msg.write_text(message,encoding='utf-8')
 policy=copy.deepcopy(old['preservation_policy']);policy.update(fixed_current_files=fixed,fixed_current_prefixes=[],current_task_allowed_changed_engine_paths=mutable,r30_permission='FIVE_EXACT_HANDOFF_SOURCE_SPANS_PLUS_SIX_CURRENT_BUILD_OUTPUTS',historical_allowlist_does_not_expand_r30=True)
 policy['additional_preserved_candidate_manifests'].append(dict(path=old['frozen_manifest'],sha256=old['frozen_manifest_sha256'],lineage='R29_FROZEN132_SCOPED_NORMAL_PASS_STATIC_HIGH3_OPEN'))
 task=dict(dispatch_id=dispatch,recipient='A',approved=True,wp_id='WP_ENGINE_GATE05_R30_HANDOFF',wp_revision='GATE05-R30-HANDOFF',delivery_envelope_revision=33,created_at=m.now(),approved_at=m.now(),approval_source='User autonomous necessary technical continuation + Master independent R29 disposition',status='PREPARED_NOT_SENT',delivery_status='NOT_SENT',route='MASTER_DIRECT_COMPUTER_USE_ANTIGRAVITY',delivery_owner='Master',instruction_path=str(ip),instruction_sha256=m.row(ip)['sha256'],work_package_path=str(wp),work_package_sha256=m.row(wp)['sha256'],release_path=str(release),release_sha256=m.row(release)['sha256'],scope_baseline_path=str(scope),scope_baseline_sha256=m.row(scope)['sha256'],allowed_mutable_paths=mutable,allowed_new_source_paths=[],production_fixed_files=fixed,all9_before=prod,ack_path=str(T/'ACK.json'),completion_path=str(T/'COMPLETION.json'),exact_message_path=str(msg),exact_message=message,exact_message_sha256=m.row(msg)['sha256'],reference_paths=[str(review),str(defect),str(contract),str(base)],runtime_verdict='HANDOFF_SOURCE_REPAIR_AND_PURE_REGRESSION_ONLY_NATIVE_NOT_ADMITTED',preservation_policy=policy,prerequisites=['Fresh actual A idle/conversation/draft/one Submit','Live renewed byte0 guard/exact baseline','Actual SENT before hourly resume'],submission_attempts=0,unknown_delivery=False,follows_dispatch_id=old['dispatch_id'])
 sys.path.insert(0,str(m.R/'Dispatcher'));import master_check_a_result as ck
 preservation=ck.inspect_preservation(task);assert len(preservation['preservation_errors'])==1 and 'Steam' in preservation['preservation_errors'][0]
 m.create(T/'MASTER_PREDISPATCH_PRESERVATION.json',preservation)
 board['tasks'].append(task);board['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',board)
 cs.update(a_status='R30_HANDOFF_PREPARED_NOT_SENT',a_current_wp=task['wp_id'],a_prepared_dispatch_id=dispatch,a_pending_dispatch_id=dispatch,updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',cs)
 m.event(dict(at=m.now(),event='R30_HANDOFF_APPROVED_PREPARED_NOT_SENT',dispatch_id=dispatch,wp=m.row(wp),scope=m.row(scope),baseline=m.row(base),protected_unique_paths=len(paths),known_installed_incident_open=True))
 m.append_delta('LOCAL-A-R30-HANDOFF-PREPARED-NOT-SENT',dispatch+'/WP_ENGINE_GATE05_R30_HANDOFF/GATE05-R30-HANDOFF/envelope33 approvedNOTSENT. R29 originalSol terminal accepted scoped438PASS each;High3stillOPEN. Next soleA handoffHigh1 narrow5spans+6buildoutputs,receiptowner/requiredmodeearlyreturn/oneuse/M05hold/ownercleanup;currentPUREPair-Capture-currenttask-Census-csproj-publisher fixed. Protected'+str(len(paths))+' oldR29frozen132+QAterminal937+historicalraw;knowninstalledincident unchangedOPEN. Production/native/global/operator/adverse calls not admitted;normalunitnewcandidate required. FreshCUidle+actualSubmit beforeSENT and samehourlyACTIVE;Sol idle no duplicate/newWP. No native E2/Highclosure/Foundationrelease. WP '+str(wp)+'; scope '+str(scope))
 print(json.dumps(dict(status='R30_APPROVED_NOT_SENT',dispatch_id=dispatch,wp=m.row(wp),instruction=m.row(ip),protected_unique_paths=len(paths),source_spans=5),ensure_ascii=False))
if __name__=='__main__':main()
