# R30 Handoff 독립 정적 QA — S1

판정은 `REVISION_REQUIRED_REQUIRED_MODE_LIFETIME_CUSTODY_AND_EVIDENCE_NATIVE_UNTESTED`다. Receipt/cohort 비교, bool set 확인, matched-owner 실패의 Awake early gate, 살아 있는 matching-owner cleanup은 소스 개선으로 인정한다. Required-mode 부재·wrong-owner·소비 후 새 instance 분기는 failclosed되지 않으며, one-use는 현재 등록 slot의 소비에 한정된다. 실제 native lifecycle 및 runtime E2는 검증하지 않았다. Source High1, carrier/publisher, E1 lineage 문제는 OPEN, Foundation HOLD다. QA가 closure/release를 설정하지 않는다.

Delivery `SOL-GATE05-R30-HANDOFF-INDEPENDENT-STATIC-S1-20261012-01`; WP `WP_QA_ENGINE_GATE05_R30_HANDOFF_INDEPENDENT_STATIC / S1`; result `SOL-GATE05-R30-HANDOFF-INDEPENDENT-STATIC-S1-20261012-7705b91d0779465387a937a18e35405b`. Original Sol/local에서 수행했다. 후보·production·compiler·runner·global·Unity·game·native·operator·Process·provider/cache·currenttask·rejection/adverse 실행은 모두 0이다. SOURCE-only branch review 16개와 주장 검토 17개는 실행한 테스트 수가 아니다. R29의 정상 PURE PASS를 R30에 상속하지 않았다.

## 정확한 후보와 보호

Frozen128 manifest SHA `D5948C6EAFE071AC723FF814708CE2D6DD62E55FFB1039D8946099E0992B7B2C`. Debug DLL SHA `9142C63AF18E2AE028D9E44AC36277F2FEBFFBB7AE8B6AF2437D12CED288C706`, MVID `71b83cb9-f67f-4520-b611-6b8d0d4d2860`, PDB SHA `4BCF43B7E9FBF84D11FF677708C050415E68032CF1A0BACADA3CF46E13B8E28A`. Source SHA `B1F8C00D1DF6E8E797EAC8E5A7F7FB462679BA06E79096D5C558C687BD413311`, 268,703바이트다. Release는 별도 MVID `7ffbba39-9a18-434b-ac07-93886e829c9f`이며 실행하지 않았다.

새 own PE/PDB file-byte reader로 두 mode의 actual MVID/CodeView GUID/PDB GUID와 각 4개 source 문서 SHA를 독립 확인했다. PDB의 original mutable 문서명을 freeze manifest의 실제 frozen_source로 매핑했고, original source fallback 또는 CLR/Assembly.Load를 사용하지 않았다. 따라서 Source/bin/Release·배포 PDB나 과거 후보로 lineage를 대체하지 않는다. Matching source/PDB는 빌드 정체성 근거이며 issuer/native authority가 아니다.

Baseline SHA `29AD8B2493A67F9A98A39671851CF7945D903C9CBBC813790273741FE3D8DD92`의 보호15549 경로와 frozen128을 초기·최종 SHA/bytes/path로 확인한다. Old R29 frozen132도 독립 재해시했다. Source/Census/csproj/publisher/Pipeline/current9/old QA와 기존 실패 원문을 수정·재빌드·복원하지 않는다. Installed incident는 OPEN/actor UNKNOWN이며 이번 QA에서 설치 파일·game UserData/save를 확인·복사하지 않았다.

## Source byte map과 개선의 범위

Old frozen R29 source 265,416바이트와 비교한 전체 outside6 구간 261,380바이트가 exact equal이다. Actual SOURCE_SCOPE_DIFF의 각 old/new range·size·SHA와 승인된 5구간을 직접 결속했다. Pair/Capture/factory/currenttask/receiver 등 고정 본문은 이 전체 byte 비교 범위에 포함된다. 소스가 같다는 사실은 새로운 DLL의 runtime PASS가 아니다.

| 변경 구간 | old byte range | actual R30 byte range |
|---|---|---|
| Bootstrap handoff | 7573..9072 | 7573..9856 |
| Private owner state | 26233..28118 | 27017..31076 |
| Awake early gate | 32923..33287 | 35881..36536 |
| M05 HOLD | 111224..111419 | 114473..114691 |
| Owner destroy | 178190..178283 | 181462..181570 |

Producer custody table의 7개 `span_range`가 실제 map과 모두 다르다. `SOURCE_SCOPE_DIFF`의 verified byte map은 인정하되 잘못된 prose range를 증거 anchor로 사용하지 않는다.

Set은 installed `_activeAdmissionReceipt`, `pair.ParentReceipt`, `parentReceipt.Snapshot`↔`_activeStartupConfig`를 올바른 object cohort로 비교한다. 기존 pending triple이 하나라도 남으면 overwrite를 거부하고 bootstrap이 bool 실패를 확인한 뒤 AddComponent 없이 Destroy/return한다. Pending owner/receipt/pair는 AddComponent 이전에 실제로 저장된다. 따라서 **pre-attachment pair context가 전혀 없다**는 광범위한 표현은 부정확하다. 문제는 slot이 없거나 소비·cleanup된 뒤에도 확인할 **독립적이고 지속적인 required-mode/owner/cohort 상태가 없다**는 것이다.

## 모든 handoff 분기의 판정

[Frozen WorkerBridge.cs](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R30-16ce928f/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:654)의 `_isPairRequiredMode=false`는 [acquire](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R30-16ce928f/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:722)의 live pending owner match 내부에서만 true로 바뀐다.

| SOURCE-only 분기 | 실제 소스 결과 | 범위 판정 |
|---|---|---|
| matched owner + valid cohort | mode=true, pair transfer, pending triple lock 내 clear | 현재 등록의 소비 인정 |
| matched owner + cohort 실패 | mode=true/null profile, slot clear, Awake early return | 이름 붙은 Awake sideeffects 전 failclosed 인정 |
| fresh instance + absent/cleaned pending | mode=false/null profile; required gate false | 유효한 global pair parent receipt가 있으면 policy/listener 본문까지 source fallthrough 가능 |
| other owner | 정당한 owner pending은 그대로, 다른 instance mode=false | 무관 instance의 legacy-style setup 차단이 없음 |
| consume 후 fresh component | pending 없음, 새 instance mode=false | 지속 owner/required-mode bookkeeping 없음 |
| consume 후 같은 instance | 이전 mode/profile 유지, acquire false/null | 단일 등록의 재조회는 막음; 새 payload 성공을 주장하지 않음 |
| same owner/cohort repeat internal Set | 빈 slot과 동일 receipt 관계가 다시 통과 | 생애 전체 one-use 미입증; 현재 bootstrap Set callsite는 하나, 실제 반복/native exploit 관측 없음 |
| true mode 뒤 profile clear | M05 OR guard가 계속 true | 이 instance의 HOLD 인정 |
| alive matching-owner cleanup | exact managed reference만 slot clear | 무관 살아 있는 owner의 clear 방지 인정 |
| Unity-null, managed-non-null owner | overloaded null guard가 ReferenceEquals 이전 cleanup을 생략할 수 있음 | conditional lifetime/custody 공백; actual destruction timing 미관측 |

[Awake](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R30-16ce928f/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:856)는 matched-owner cohort 실패에서 fastEcology 변경·Unity callback 구독·package policy·listener/thread 전에 return한다. 반면 mode=false 분기는 이 gate를 선택하지 않는다. Parent receipt gate도 callback 구독 이후에 있으므로 이를 required-pair gate의 대체로 보지 않는다. 유효하지 않은 parent receipt라면 이후 policy/listener는 차단되지만 이미 앞의 두 작업을 지나며, 이 사실을 실제 native 실행으로 주장하지 않는다.

[M05](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R30-16ce928f/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:2502)는 true mode 또는 non-null profile에 한해서 HOLD다. Fresh mode=false/null profile에서 이 OR guard가 선택되지 않는다는 것이 결론이다. 기존 task/readiness 검사도 그대로 남아 있으므로 실제 Process.Start나 child launch를 관측·증명했다고 주장하지 않는다.

[OnDestroy](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R30-16ce928f/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:3759)는 profile을 지우고 owner cleanup을 호출하며 mode는 해제하지 않는다. 다만 `owner == null`의 Unity semantics와 exact managed identity는 다르다. 초기 `this.gameObject` 평가/cleanup이 종료·unsubscribe/listener stop 블록보다 앞에 있고 전체 catch가 없다는 소스 제한도 남긴다. Actual getter/OnDestroy timing과 예외는 실행하지 않았다.

Awake의 early return만으로 component가 disable/destroy되거나 고정 Update 본문이 차단되는 것은 아니다. `isRunning=true` initializer와 Update suppression/readiness 코드가 남아 있다. Actual 이후 callback은 관측하지 않았다. 이 추가 범위가 필요하다면 현재 5구간을 임의로 넘어 고치지 말고 Master가 별도로 범위를 결정해야 한다.

## Unity reference와 catch 주장

검토한 frozen Unity CoreModule SHA `C5C58EA254834291780A1D6C388C241443D07167B4A4B890A23C9494F626DDBA`, 1,386,688바이트, MVID `e422ced3-d0f6-4bb2-9423-e8338d57bc04`는 admitted R5 dependency manifest의 파일이다. 실제 설치 또는 실행 중인 Unity/native module을 관측한 것은 아니다.

Own byte-only TypeDef/MethodDef/IL reader에서 `op_Equality`/`op_Inequality`는 CompareBaseObjects를 호출한다. 이 exact reference의 managed-null 판정은 `ceq`, 한쪽 null 분기는 IsNativeObjectAlive→GetCachedPtr→IntPtr inequality를 사용하고, 두 wrapper가 non-null인 마지막 분기는 `ceq`다. 따라서 일반적인 Unity 문서나 기억의 instance-ID 비교로 이 파일의 원문을 대체하지 않는다. Pointer-zero 상태에서 Unity-null과 managed ReferenceEquals가 달라질 수 있다는 conditional 해석만 사용한다.

GameObject AddComponent wrapper는 RVA0/InternalCall 메서드로 넘긴다. Managed IL은 Awake의 동기 호출을 보증하지 않으므로 producer의 synchronous Awake 주장은 UNOBSERVED/미채택이다. Awake는 자신의 try/catch에서 예외를 log하고 rethrow하지 않는다. 따라서 **모든 Awake 예외가 bootstrap AddComponent catch에 전파된다**는 일반 보증은 소스로 반박된다. Actual AddComponent에서 탈출한 exception을 bootstrap이 cleanup/Destroy/return으로 처리한다는 좁은 소스 개선은 인정한다.

## E1 원문·timing·lineage

Old original `scratch/EngineGate05R29StartupPair` 아래 12개 파일의 현재 SHA/bytes가 R29 frozen reference와 달라졌고, 경로 집합은 Master drift 원문과 정확히 일치한다. Bin runner/PDB·local candidate/PDB 4개, HOST_TELEMETRY 1개, 두 run의 report/stdout 4개, obj의 AssemblyReference cache·runner·PDB 3개다. Old frozen132와 old independent QA는 보존됐다. Original을 복원·정규화하거나 old PASS를 fresh candidate로 옮기지 않는다.

Initial A 보호 baseline15296에는 이 원본 12개가 0개 포함돼 있었다. 따라서 해당 보호 rows의 hash PASS와 old frozen PASS가 original E1 경로 보존까지 의미하지 않는다. 이는 WP의 original raw 보존 요구를 없애지 않는다. Current QA baseline15549는 현재 drift 상태를 pin하므로 이후 추가 변경도 허용하지 않는다.

추가 결속 문제는 `FINAL_PRE_RUN_MANIFEST` built-candidate 선언 **7/7이 old R29 SHA/size**라는 점이다. 실제 R30 frozen Debug/Release/동반 PDB·배포물·recompiled runner와 맞지 않는다. Source 항목이 새 R30 source를 담았다는 사실로 이 stale binary graph를 정정·완화하지 않는다. Producer pre-run 선언은 18:13:20, 두 runtime report의 UTC는 각각 18:09:51 환산이며 선언상 약 208.8초 뒤다. 이는 producer metadata의 내부 chronology 충돌이지 독립 file-creation timing 또는 UTC world ordering proof가 아니다.

Producer host는 두 PID/exit0, stdout/stderr/report SHA를 기록했고 그 원문 hash 연결은 frozen files에서 확인됐다. 실제 raw reports는 여전히 **R29 WP/dispatch/envelope32**, 새 summary는 R30/envelope33이다. Program은 old frozen R29 source와 byte-identical이며 old harness/output root를 재사용·재빌드했다. ACK의 scope SHA `8CC855...`도 실제 scope hash와 다르고 원래 ACK가 reconciliation되지 않았다.

Producer records는 run마다 Pair6 + Capture4의 selected-field/sentinel 정상 관측이다. Capture는 15 getter를 호출하지만 일부는 non-null 또는 array count만 검사한다. Pair returned declaration은 일부 필드 편집 후 origin sentinel만 확인하고, caller arrays 편집 후 PairId/Role 등을 다시 확인한다. Full snapshot15/receipt11/task27/options7/invocation2의 전체 shape/type/value/order/raw/copy 단계 증거는 아니다. Producer total_cases6과 6/6 label은 4 Capture 회귀를 별도 기록한다. 독립 fresh R30 normal/handoff runtime PASS로 승격하지 않는다.

Actual loadedmanaged path/SHA/MVID/corelib/CLR, full prospective compiler command/body/reference/oracle/callplan, 양쪽 recursive pre/post outputs와 모든 typed/raw/copy expectations의 proof graph는 충분하지 않다. Host의 file hash·OS exit0·10 case labels는 그 공백을 채우지 못한다. Actual 후보 PE/PDB/source4/4 결속과 SOURCE boundary 보존은 별도로 유효하다.

## 다음 최소 수정과 독립성

우선 같은 5구간 안에서 exact pre-attach owner/cohort의 지속 required-mode와 consumed 상태를 payload slot과 분리해 설정한다. Missing/wrong/postconsume instance를 legacy로 낮추지 않고, per-registration lock+clear를 lifetime one-use로 확대하지 않는다. Overloaded-null liveness와 ReferenceEquals custody를 분리해 owner cleanup의 조건을 명시한다. 성공 모드가 profile clear 뒤에도 M05 HOLD를 유지하는 개선은 보존한다. 새 global child registry/currenttask replacement/schema/keys/issuer/nonce/cryptography나 native 실행을 제안하지 않는다.

Evidence는 새 task-owned harness/run root와 정확한 새 identity, actual before-build/before-run pins, full independent literal expected/raw/type/copy와 loaded provenance가 필요하다. 현재 snapshot·old original drift·frozen copies·failed raw를 보호하고 old outputs를 다시 쓰지 않는다. Update 등 outside 구간 변경이나 native regression이 필요하면 Master의 별도 scope/admission을 요구한다. Carrier/parser-beforeIO/publisher, Engine002006/Pipeline007/current schema/G-Q1/PlayerGlobal/physical split은 계속 OPEN이며 Dedicated Server가 final Domain Authority다.

Master review는 답안이 아니라 검토 입력으로 다뤘다. Core required-mode/drift 결론은 독립 근거가 지지한다. Pre-attach pending context는 실제로 존재하고 one-use는 per-slot이라는 제한을 명시했으며, 7 stale binary declarations와 0/12 original-path 보호 coverage, exact reference IL의 lifetime 조건을 추가했다. Full `CLAIM_EVIDENCE_MATRIX.json`은 지지·조건부·반박·미관측을 구분한다.

자체 선택적 metadata 조회의 `bytes`/`size` KeyError는 원래 helper/exit1/완전 stderr를 보존했다. 실제 sealed R5 manifest의 `size`와 현재 보호 inventory의 `bytes`가 같은 값·SHA임을 확인하고, WP가 허용한 schema locator만 새 helper에 정정했다. Source/hash/type/expected/runtime 결과는 바꾸지 않았고 이 오류를 PASS라고 하지 않는다. 이후 references/source/branches/provenance/claims의 성공은 별도 full first-stream proof로 남긴다. Optional InspectLineage는 원래 mutable 문서 경로를 읽는 동작이 있어 실행하지 않았다.

주요 산출물은 새 QA root의 `INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json`, `SOURCE_BYTE_MAP_AND_FULL_CHANGED_SPANS.json`, `SOURCE_BRANCH_CUSTODY_REVIEW.json`, `UNITY_REFERENCE_NULL_AND_ADDCOMPONENT_IL.json`, `CLAIM_EVIDENCE_MATRIX.json`, `PROVENANCE_AND_ORIGINAL_DRIFT_REVIEW.json`, `PRESERVATION_POLICY_PATH_COVERAGE_REVIEW.json`, `NEXT_MINIMAL_REPAIR.md`, before/after inventory다. EM/index/ACK binding/COMPLETION은 동일 unique result의 actual SHA/bytes로 결속하며 COMPLETION은 마지막 atomic write로 봉인한다. Master adoption·closure·release는 별도 PENDING이다.
