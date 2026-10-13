# R28 독립 frontend·bootstrap 경로 정적 QA

판정은 **READ_ONLY_STATIC_AUDIT_COMPLETE / CONNECTED_OPERATOR_ROUTE_REQUIRED / NATIVE_UNTESTED**다. 실제 동결 명령행 소비와 초기화 순서를 확인했으며, R27 PURE Capture가 실제 operator provisioning·private owner·child 수신으로 연결되었다고 판단할 증거는 없다. 빌드·후보 호출·게임·Unity lifecycle·Process·normal/adverse/rejection 실행은 모두 0이다. 새 flag·carrier·schema를 채택하지 않았다.

- WP: WP_QA_ENGINE_GATE05_R28_FRONTEND_ROUTE_INDEPENDENT / S1
- delivery: SOL-GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012-01
- result: SOL-GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012-99b7c410f7ee452a91169778881914dc
- QA root: C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012

## 자료와 분석 방법

R27 동결83 manifest SHA 1FD4B9EFB368EE03F327241418C5CC0ACC08F9210E6E1BD271AECC373D219EE3, selected Debug SHA 68BFE5105FA0471AAAF7943009703BB2599B39C5B572833507D6733BCE63CF64, MVID 44ba753c-6570-49d8-8068-4edf87a4e5d0, PDB SHA F0BC1B7D92F67593EA967F56A90EE302C76B920A46B98EF77219F7B884C47814, Worker source SHA B292AB846F78568F74333F58C5967ED38CAAA2F59B07393FC846F4329583E388를 사용했다. Debug/Release 모두 CodeView–portable PDB GUID와 frozen source document 4/4가 일치한다. Release는 metadata만 읽었다.

R5 frozen managed4 manifest SHA 7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481의 frozen_path만 읽었다. 설치 게임·Workshop 원본이나 UserData·save는 읽거나 복사하지 않았다.

| Module | SHA256 | MVID |
|---|---|---|
| Assembly-CSharp.dll | 5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A | 61e41735-6189-4da4-9d21-0260257b5097 |
| UnityEngine.CoreModule.dll | C5C58EA254834291780A1D6C388C241443D07167B4A4B890A23C9494F626DDBA | e422ced3-d0f6-4bb2-9423-e8338d57bc04 |
| UnityEngine.dll | 0422FF282130458380D2FB4B63A718465D3BD2D5738F1532F60798B0D35DFF0D | 6818d81b-8068-4c2b-9985-ad10378e10a4 |
| 0Harmony.dll | 353DAAFEC180BB8E7BBE4DA78F2A7CDC78067392E3A4E79DC8E7AF295F2371E6 | e5339928-9d9b-419d-83f9-f5b02c5cf609 |

새 QA Python byte reader로 PE/ECMA335 table·method token·RVA·file offset·raw IL·code SHA를 추출했다. Assembly-CSharp 90,840 MethodDef 전부의 직접 IL 참조 스캔에서 decode error 0, 관련 참조 18개다. selected Worker 532 MethodDef도 직접 참조를 확인했다. 88개 추출 managed body의 branch target을 검증했고 5 module MVID가 별도 AST-only byte reader와 일치한다. 원래 QA/helper module top-level은 실행하지 않았다. TypeSpec/generic signature는 raw hex를 보존하며 완전한 decompiler/type verifier라고 주장하지 않는다.

이것은 동결 원래 IL과 직접 참조의 증거다. 실제 loaded assembly, Harmony/다른 모드 patch, reflection/native 경로나 운영 프로세스 상태는 검증하지 않았다. A의 새 R28 제안은 읽지 않았다.

## 실제 명령행 소비

Verse.GenCommandLine.TryGetCommandLineArg: token 0x060054D8, RVA 0x001B4E90, code offset 1781916, 96 bytes, code SHA 74F28CE61BEC0CCE4C527B713B4FDB796D51731292A64A647B6996151D9B524A.

1. 매 호출 Environment.GetCommandLineArgs()를 받아 index 0부터 선형 탐색한다. dictionary/token cache는 없다.
2. 항목에 =가 있으면 Split('=', options0)한다. 결과가 정확히 2개일 때만 검사한다.
3. 첫 부분은 key 또는 -key와 String.Compare(string,string,bool true)로 비교한다. ignore-case overload이며 Ordinal 비교를 지정하지 않았다. 실제 문화권별 비교를 실행하지 않았다.
4. 첫 일치 항목의 두 번째 부분을 그대로 반환한다. 중복 검출이나 last-wins가 없다. 빈 값도 true로 반환하며 실패하면 out은 null이다.
5. 파서 자체에는 trim·quote 제거·backslash/percent/base64 decoding이 없다.

이미 한 argv인 -operatorconfig=C:\space root\a.json은 해당 문자열을 전달하지만 -operatororigin=a=b는 3부분이어서 건너뛴다. -key value와 조회명이 key일 때의 --key=value는 이 consumer 형식이 아니다. 추가 =는 OS 인용으로 감춰지지 않는다. 공백·Ω·opaque ID를 한 argv로 만드는 Windows 인용/역슬래시 변환은 이 IL 밖이며 실제 OS 증거가 필요하다. 이 조건들은 실행 결과가 아닌 IL에서 도출했다.

현재 Bootstrap은 operatorconfig/operatorconfigsha/operatororigin/operatorlaunchplan/operatorconfigid/operatorrole/operatorcapability 7개를 소비한다. origin/plan/configId 원문은 유지하고 role/capability/path/SHA는 기존 명시 trim을 거친다. Awake에는 bridgeport consumer가 있다. CommandLineArgPassed는 값 없는 key/-key를 비교하는 별도 함수다.

## 실제 savedatafolder와 초기화 시점

GenFilePaths.SaveDataFolderPath: token 0x06005522, RVA 0x001B7384, offset 1791376, 266 bytes, code SHA AFF5BD726B688E874B45B12135B8952EF0E1588111D2917BB65FC6A76830DBD9. 실제 savedatafolder를 조회하며 지원 argv는 -savedatafolder=<value> 또는 savedatafolder=<value>다. 이는 동결 게임 managed consumer 관측이며 임의 Unity native flag의 지원 주장이 아니다.

saveDataPath는 .cctor에서 null로 시작한다. 첫 getter가 override/default를 저장하고 이후 non-null 캐시를 바로 반환한다. override 분기의 TrimEnd('\\','/') 결과는 pop되므로 원문 trailing separator를 제거하지 않는다. 빈 override는 DirectorySeparatorChar 문자열로 바뀐다. 이 분기는 absolute/approved/equal-root를 검사하지 않고 DirectoryInfo Exists/Create를 사용한다. relative path의 실제 해석은 child cwd에 달려 있다. override가 없으면 UnityData/editor/platform 또는 외부 Application persistentDataPath 경로가 남는다.

Root.CheckGlobalInit token 0x060015F4의 IL0058은 UnityData copy, IL0067은 Prefs.Init, 이후 IL008A/009B는 static constructors CallAll delegate queue다. Prefs.Init 첫 call은 PrefsFilePath→ConfigFolderPath→FolderUnderSaveData→SaveDataFolderPath다. 따라서 정상 초기화의 이 경로에서는 Worker startup constructor보다 먼저 config/prefs root가 선택되고 디렉터리 접근도 발생할 수 있다. 다른 모드/earlier 접근이 전혀 없다는 전역 보장은 하지 않는다.

Worker SafeSaveDataFolderPath는 admitted role snapshot의 선언 root를 반환한다. core saveDataPath를 설정하지 않는다. READ_ONLY ValidatorUserDataDirectory 선언이나 Awake DeclaredRoleUserData 로그는 core/native effective root 증거가 아니다. operator가 argv와 cwd를 새 child 시작 전에 확정해야 하며 Bootstrap/Awake에서 뒤늦게 root를 바꾸어 early config/prefs 접근을 해소했다고 해서는 안 된다.

## Bootstrap·AddComponent·Awake 경계

selected Bootstrap .cctor token 0x060000ED는 다음 순서다.

| IL offset | 실제 동작 |
|---|---|
| IL01E0 | IssueAdmissionReceipt |
| IL022C | TryInstallOperatorStartupConfig |
| IL02BC | new GameObject |
| IL02C5 | DontDestroyOnLoad |
| IL02CD | AddComponent WorkerBridgeComponent |

TryInstall token 0x06000107은 IsValid·lock·기존 seal 검사를 거쳐 process-global receipt/snapshot/sealed를 설치한다. 현재 per-owner current-task child registry는 아니다. 실제 StaticConstructorOnStartup attribute와 core CallAll→RunClassConstructor를 확인했지만 모든 타입의 전체 runtime 실행 순서를 보장하지 않는다.

Unity generic AddComponent token 0x060018E5 IL000C→Type overload 0x060018E4 IL0003→Internal_AddComponentWithType token 0x060018E3으로 간다. 마지막 method는 RVA0/internal-call이고 managed body가 없다. immediate/deferred Awake 호출 시점과 activation·native 등록 순서는 UNVERIFIED다.

현재 Awake token 0x0600010D는 fastEcology 변경과 log callback 구독 후 receipt guard를 검사한다. guard는 policy/listener/thread보다 앞서지만 private child pairing/task context acquisition은 없다. 최소 안전 제약은 AddComponent 전에 immutable startup context를 완성하고 Awake가 그 호출 중 실행될 수 있다고 가정하는 것이다. Awake 초입에서 instance child context를 확보·검증한 후 policy/listener/task 부작용을 시작해야 한다. AddComponent 반환 뒤 property를 넣거나 inactive GameObject 관행에 의존하는 ordering은 이 metadata로 입증하지 못한다.

## 연결의 실제 frontier와 결손

StageSave는 현재 sealed result에서 task27·random capabilityNonce·channel secret·절대 task/result/stage 경로를 만든다. 이는 MD126이 인정한 simulator/operator 소유 producer다. Engine 전체에 nonce mint 금지를 새로 만들지 않는다.

현재 런처는 private current task의 nonce를 검사하고 parent config에서 executable/SHA/freeform ValidatorArguments/ValidatorCwd를 가져온다. --task-file "<path>" --nonce "<nonce>"를 이어 붙이고 cwd는 Directory.Exists일 때만 지정한다. 별도 operator-approved READ_ONLY receipt의 조합, private current-task registration, closed child plan은 없다. selected Worker 전체에서 PURE OperatorChildLaunchInputs.Capture 직접 호출은 0이다.

child Bootstrap은 task-file/nonce를 읽지 않는다. core 전체 직접 IL 스캔에서도 TryGetCommandLineArg caller는 savedatafolder getter 하나다. 이것은 감사한 DLL의 직접 참조 결론이며 미감사 별도 executable의 모든 경로를 부정하는 것은 아니다.

HandleExecuteValidatorTask는 별도 TCP command이며 문자열을 공백으로 나눠 task path/nonce를 읽고 task file·profile·stage/load/result 작업으로 간다. CLI 수신과 연결된 경로가 아니다. task file nonce와 제공 nonce의 일치만으로 operator issuer/pair approval/current owner 인증이 성립하지 않는다. File SHA/config/receipt 일치는 유지해야 할 consistency 검증이며 실제 issuer 증명을 대체하지 않는다. IsTrusted·private constructor·internal visibility도 같은 한계를 가진다.

Root.CheckGlobalInit IL0008/001E/0023/002D는 argv0을 제외한 **전체 argv를 Log.Message에 전달**한다. 현재 launch string의 nonce를 실제 child에 전달하면 이 logging 경로에 포함될 수 있다. child를 실행하거나 유출 로그를 관측한 것은 아니다. 새 보호 channel 설계에서 CLI capability를 보호된 비밀로 간주해서는 안 되며 operator-owned local pipe/동등한 보호 carrier 또는 별도 승인된 early log redaction 증거가 필요하다. public non-secret locator와 capability를 구분해야 한다.

Revoke/reset/load/grant/tick의 기존 task clearing과 OnDestroy의 listener/log/thread 종료는 source fact다. 새 child registration의 stale invalidation·same-current lookup·consume/revoke/dispose는 아직 존재하지 않는다. 기존 CompleteStageValidation의 현재 task 검증을 일괄 삭제하거나 전체 FAIL로 재판정하지 않는다.

## 제안하는 한 경로와 최초 구현 검증

제안은 PROPOSED다. Master가 실제 operator producer/endpoint와 보호 carrier, 허용 source spans를 지정한 뒤 다음 한 경로를 연결하는 것이 우선이다.

**operator 승인 producer → 별도 READ_ONLY config14/원본 approved7 → parent 현재 StageSave task → instance private registration/closed plan → child 초기 savedatafolder/cwd → 보호된 typed task receiver → AddComponent 전 startup payload → Awake instance binding → typed task execution → 등록된 result channel → 현재 task consume/revoke.**

기존 simulator stage nonce와 config14/descriptor7/task27은 유지한다. local pipe/동등한 operator channel은 MD126 범위이며 새 PKI를 요구하지 않는다. carrier/locator 이름·payload는 아직 채택되지 않았다. 실제 operator provider 없이 fixture receipt나 public JSON 입력만 넣은 경로를 operator integration이라고 해서는 안 된다.

최초 구현 리뷰는 StageSave·launcher·Bootstrap·Awake·typed Execute·lifetime callsite의 실제 연결, 원문 field/copy 보존, pre-attach order, closed argv/no duplicates, capability logging 배제, same-current registration을 한 diff에서 추적해야 한다. fresh frozen candidate 뒤 정상 managed QA는 네 기존 parent/child 조합의 전체 typed/raw/copy oracle와 producer→registration→plan→receiver round-trip, 공백 path typed 전달, pre-attach 준비 기록을 새 runner로 검증할 수 있다. mock transport/callback은 해당 seam 증거로만 표시한다.

후속 native E2는 별도 Master WP가 필요하다. 실제 operator source/channel, child PID/start/executable SHA/role/task binding, early core config/prefs root와 cwd, actual AddComponent/Awake order, capability 비노출, 실제 stage semantic load/result/consume/cleanup을 관측해야 한다. 이번에는 실행하지 않았다. 7개 IR과 단계별 계획은 IMPLEMENTATION_REVIEW_REQUIREMENTS.json에 있다.

## 보존과 제한

Master R27 S2 정상 Capture15 scoped PASS와 QA dependency pointer defect CLOSED_SCOPED만 이전 판정으로 수용한다. S1 FileNotFoundError와 old raw FAIL은 보존하며 실행 PASS로 바꾸지 않는다. R26 F09의 reference-only savedatafolder 사실을 exact IL consumer 증거로 좁게 보강했을 뿐 native root PASS를 추가하지 않았다.

Protected 14,045 paths, frozen83, managed4의 before/after SHA·size를 검증한다. 초기 recovery의 ADR 파일명 추정 실패는 실제 ADR-006B_Configuration_Content_Manifest_v2.md와 Master acceptance map으로 additive 정정했고 원문 audit은 보존한다. 완료 manifest/index/COMPLETION이 artifact identity와 최종 보존 결과를 결속한다.

Production/candidate 수정·재빌드, QA compiler/runner, assembly load/reflection/invocation, game/native/Unity lifecycle/Process, adverse/rejection 실행은 모두 0이다. Engine002006/Pipeline007/current schema/G-Q1/PlayerGlobal·physicalsplit은 OPEN, Foundation HOLD, full/nativeGate E2 NOT_RELEASED다. Closure·release·새 구현 WP 채택은 Master 판단이다.

