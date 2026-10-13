# QA Tactical Worker Hardening Independent Review

```yaml
Work Package: WP-QA-TAC-BOUNDARY-02
Reviewer: Independent QA / Architecture Reviewer
Date: 2026-10-02 Asia/Seoul
Target: frozen exact WP-TAC-WORKER-HARDEN-01 scratch implementation
Work Package Verdict: FAIL
Architecture Gate Recommendation: BLOCKED BY ARCHITECTURE 유지
ADR-002 Recommendation: PROVISIONAL 유지
Status Change Authority: Master
Production Code Modified: false
Candidate Code Modified: false
Computer Use: not used
```

## 1. Master에게 제출하는 결론

동결된 source/DLL/fixture/script를 독립 실행했다. 정상 fixture의 실제 엔진 로드, cooperative STEP, pre-load 자동 틱 차단, START 이전 시간 부채 제거는 개선이 확인됐다. 그러나 **의미 손실을 READY/SAVED로 허용하는 로드 경로, 미분류 GameComponent의 상태 변경, 불완전한 최종 oracle**가 남아 있다. 이 후보로 Worker 전체 gate를 통과시키거나 ADR-002를 ACCEPTED로 승격하도록 권고하지 않는다.

| Defect | 독립 QA 권고 — 각 항목 하나의 판정 | 판정의 핵심 경계 |
|---|---|---|
| QA-ENGINE-002 | **STILL FAILING** | RecipeDef 누락으로 bill 소실, 잘못된 typed Def로 battery 소실, 잘못된 body-part 참조로 Hediff 소실 후 READY/SAVED |
| QA-ENGINE-003 | **PARTIAL** | 정상 RUN 격리·실제 STEP cap·취소·queue expiry 확인. 연결 종료 후 미실행 요청이 뒤늦게 실행되는 경계와 공개 diagnostic bypass는 남음 |
| QA-ENGINE-004 | **STILL FAILING** | OPEN 유지. foreign chronological getter가 G를 따라 증가하며 typed temporal materialization/B2 publication 구현 증거 없음 |
| QA-ENGINE-005 | **STILL FAILING** | world/history/tales 차단과 fastEcology 방어는 확인. GameComponent 전체 dispatch와 native Anomaly timer 변경은 계속됨 |
| QA-ENGINE-006 | **STILL FAILING** | fixture는 개선됐으나 11개 negative oracle 중 9개가 훼손을 검출하지 못함. inventory 삭제도 PASS |
| QA-ENGINE-007 | **CONFIRMED RESOLVED** | 이 동결본·환경에서 pre-load부터 READY까지 autonomous ticking을 막는 기계적 fence 확인. 전체 temporal/semantic READY 승인 의미는 아님 |
| QA-ENGINE-008 | **CONFIRMED RESOLVED** | LOAD/EXPORT/idle/pause/cancel 이전 elapsed가 START 예산에 들어가는 결함은 독립 측정에서 재현되지 않음 |

위 표는 **결함 판정 및 상태 변경 권고**다. 기존 ledger, ADR 또는 Master 상태 문서를 수정하지 않았다. QA-ENGINE-007/008의 해결 판정으로 QA-ENGINE-002/004/005를 닫지 않는다. QA-001~QA-014의 기존 OPEN 상태도 변경하지 않는다.

## 2. 요구 및 ADR 기준

Canonical requirement 원문은 [요구사항_명세서.md](C:/Users/user/Desktop/RimMulti/요구사항_명세서.md) 하나다. 이 문서의 SRS 접두 표기는 해당 최상위 번호를 뜻한다.

| Canonical requirement | 이번 검증과의 관계 | 이 작업에서의 판단 |
|---|---|---|
| SRS-FR-001/002/003 | Server W, independent Settlement L, offline ordinary freeze | Worker G를 W로 취급할 수 없음. foreign chronology/fence는 §7/9/10 참조. Server W 전체 구현 통과를 주장하지 않음 |
| SRS-FR-098 | 생성된 기존 Settlement Map 사용 | 정상 native save load는 확인. semantic failure admission은 FAIL |
| SRS-FR-153/154/155, SRS-CON-010 | offline 공격, defender AI, 실제 상태 영구 반영 | 로드 손실·time/write boundary 문제 때문에 end-to-end 충족을 승인할 수 없음. 실제 전투 AI 전체 검증은 이번 범위 밖 |
| SRS-FR-166, SRS-NFR-002/005 | Pawn/Animal/Building/Item scope 및 원자성 | full export 보존은 canonical transaction 원자성의 증거가 아님. inventory oracle 누락 확인 |
| SRS-NFR-004/006/007 | 상태 일관성, 내구성, 중앙 최종 권한 | false-success admission 및 미구현 B2/temporal/revision publication 경계가 blocker |
| SRS-NFR-008/011 | client fault 격리, tactical 반응성 | 실제 concurrent control 측정은 있음. fleet/client crash 및 최종 remote latency SLO 통과는 아님 |
| SRS-CON-003 | RimWorld 1.6 | 실제 1.6.4871 엔진으로 검증 |

Master 지정 baseline은 ADR-001 **ACCEPTED**, ADR-002 **PROVISIONALLY ACCEPTED**, ADR-006A **ACCEPTED**다. [ADR-006A accepted 원문](C:/Users/user/Desktop/RimMulti/ADR-006A_Temporal_Authority_ACCEPTED.md)의 W/L/G/M 구분, one-clock execution island, typed temporal schema, pre-load/READY boundary, B2 target-scoped publication을 적용했다. 별도 proposal 파일의 PROPOSED 표기는 현행 Master 결정의 대체 근거가 아니다.

Full Worker save는 private checkpoint/extraction input으로만 판단했다. **SAVED 문자열이 서버의 canonical commit을 의미한다고 해석하지 않는다.** 아래 false-success는 Worker admission/export gate 자체의 실패이며, 실제 운영 DB에 잘못된 full save가 commit됐다는 주장이 아니다. ADR-003 inventory canonicalization 및 ADR-004 durable multi-state commit/repair의 상세 구현도 이 후보에 있다고 가정하지 않는다.

## 3. 동결 대상 식별과 증거 관리

Candidate scratch root:

`C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch`

| 대상 | SHA-256 | bytes |
|---|---|---:|
| WorkerBridgeMod/Source/WorkerBridge.cs | `18DC9B8481FC21AF510430362AFECF7720D2AC01ED771F3AF3AFCE4115C807CF` | 63616 |
| 1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll | `B1CBE74E539B5964DE5DB0A961AAF064813145F9FC1BC0DDE58DF476FC12B39D` | 57344 |
| Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll | `B1CBE74E539B5964DE5DB0A961AAF064813145F9FC1BC0DDE58DF476FC12B39D` | 57344 |
| Harden_Manifest/Saves/EngineComplexFixture.rws | `ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED` | 25868299 |
| run_hardening_regressions.py | `DDD7F395CE60E9CFEE3149C0C0A81FF0F901FCA13F36E00E392094DB3EF81232` | 23336 |
| hardening-test-results.json — A 결과 | `95797D912C97FC280FEF22A03A2C31F29820B7224198570A90E3707177B726B8` | 5606 |
| Tactical_Worker_Hardening_Evidence_01.md — A 보고서 | `56CED62188AE3222B0ED25ABCECB60D48934E16B4F43343138850BAC7F2D04E0` | 26016 |

독립 observation process가 실제 로드한 candidate DLL MVID는 `babab41b-fa03-45b3-8b05-911ce720a688`, SHA는 위 DLL과 같다. [실제 module identity](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/observer-module-identity.xml)에 엔진의 loaded assembly 경로까지 기록했다.

실제 환경은 RimWorld **1.6.4871 rev591**, Unity **2022.3.35f1**, WindowsPlayer다. Assembly-CSharp.dll SHA는 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`다. 활성 구성은 Core/Harmony/WarEconomy/WorkerBridge, Royalty/Ideology/Biotech/Anomaly/Odyssey, 기존 QA Engine02 Probe다. instrumented profile에는 별도 QA Boundary02 Observer가 추가됐다. Royalty mismatch case는 의도적으로 Royalty를 뺀 격리 profile이다. [실제 환경 응답](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/environment.json)과 profile별 Config/ModsConfig.xml, Prefs.xml을 보존했다.

Freeze manifest 7개 항목을 시작 전, 실행 중 명령/로드 경계, 종료 후 대조했다. **종료 시 7/7 일치**다. 별도 보호 목록 81개 파일(Production source/project/deployment files, candidate source 및 산출물, 기존 probe, SRS/선행 ADR/엔진 등)도 **81/81 전후 해시 일치**다. 전체 디스크에 대한 감사라는 뜻은 아니며, 보호 대상 목록은 증거 파일에 명시했다.

Evidence root:

`C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\BOUNDARY02-20261002`

- [freeze 시작 검사](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/freeze-verification-before.json), [freeze 종료 검사](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/freeze-verification-after.json)
- [보호 파일 시작 목록](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/protected-inputs-before.json), [보호 파일 종료 대조](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/protected-inputs-after.json)
- [동결 source 검토용 사본](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs), [동결 A regression 검토용 사본](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/run_hardening_regressions.py)

## 4. 독립 방법 및 한계

터미널에서 실제 RimWorld native executable을 hidden batch process로 실행했다. 게임 화면을 조작하지 않았다. Candidate를 재빌드/수정하지 않고 frozen DLL을 기존 Mods junction으로 읽었다. QA-owned savedatafolder마다 save/config/log/ports를 격리했다. Production 서버 7777, 사용자 save/profile에는 접속하거나 쓰지 않았다.

총 9개 자체 process profile을 사용했다. primary 증거는 ExactBaseline, DependencyDirectLoad, DLCMismatch, ConcurrentControls, ValidatedBoundary, ValidatedFreshReload, FreshSemanticNegatives다. 초기에 만든 ObservedBoundary/ObservedFreshReload는 **QA observer의 overloaded LoadGame Harmony target ambiguity**가 발견된 탐색 실행이다. 해당 로그를 보존했지만 최종 fence/global/fixture 판정의 primary 근거로 사용하지 않았다. observer만 수정해 clean ValidatedBoundary/ValidatedFreshReload로 재실행했다. Candidate는 그대로다.

별도 QA observer는 loader/FinalizeInit/DoSingleTick의 시점·실제 호출 수·frame별 호출 수와 live state를 읽는다. 관측 prefix/postfix는 candidate 함수의 반환값이나 인자를 바꾸지 않는다. Game/World/Map probe, native caravan 생성, main-thread BLOCK, queue inspection, QA ThreadPool 설정은 **명시적 관측·failure injection**이다. target MapProbe의 global/foreign read는 causal dependency 검증을 위한 QA-only 결과 필드이며 특정 vanilla 전투 결과가 변했다는 증거로 확대하지 않는다.

Controls에는 observer V2 DLL을 사용했다. 해당 source/DLL은 ObserverVersions/ControlObserverV2.*로 보존했으며 DLL SHA는 `D01180DC61A8B14CDBB20E4A2063AC81CED59F6757DEF279A40D17320C515EC0`다. Validated/targeted에는 V3를 사용했고 loaded observer MVID는 `27eaf451-19a0-410f-be93-e7c602ea657f`다. 모든 QA script 및 각 observer DLL은 최종 artifact manifest에 hash로 묶는다.

Gemini B의 미완성 작업, root의 B 검증 script/results/report는 **증거로 채택하지 않았다**. A의 PASS는 검증 대상 claim이며 독립 결과의 대체 근거가 아니다. Native engine IL inspection은 metadata-only로 시행했고 실행 증거와 분리했다. 전체 solution 빌드는 이 작업의 gate가 아니며 수행하지 않았다. QA observer만 QA 폴더에서 빌드했다.

## 5. QA-ENGINE-002 — dependency / semantic load gate

**CLAIM:** 직접 LOAD_SAVE도 사전 scanner 및 post-load error gate를 통과해야 하며 의미 손실이 있으면 READY/export success를 거부한다.

**SETUP:** frozen fixture의 QA 복사본에 한 가지 결함씩 주입했다. 모든 case는 **VALIDATE_MANIFEST를 사전에 호출하지 않고 LOAD_SAVE**했다. 정상 원본도 처음/negative 후에 다시 로드했다. MissingRecipe는 fresh native process의 첫 load로도 재현했다.

**ORACLE:** dependency/typed reference/body-part 손실 가능 case는 LOAD_FAILED 또는 LOAD_REJECTED이며 READY=false, EXPORT 차단이어야 한다. 정상 원본은 READY 및 private export 허용이어야 한다. native bill/battery/Hediff identity를 입력과 실제 live/export에서 대조한다.

**OBSERVED:**

| Case | LOAD → terminal | READY | EXPORT | 의미 상태 |
|---|---|---:|---|---|
| 정상 frozen fixture | QUEUED → READY | true | SAVED | 정상 내용 로드 |
| 누락 mod를 meta/modIds에 추가 | LOAD_REJECTED → LOAD_FAILED | false | 거부 / 파일 없음 | 방어 확인 |
| missing ThingDef | LOAD_REJECTED → LOAD_FAILED | false | 거부 / 파일 없음 | 방어 확인 |
| missing HediffDef | LOAD_REJECTED → LOAD_FAILED | false | 거부 / 파일 없음 | 방어 확인 |
| missing RecipeDef — bill의 recipe 참조 | QUEUED → READY | true | SAVED | TableSculpting bill **1 → 0** |
| ThingDef 위치 Battery를 HediffDef 이름 Stab으로 변경 | QUEUED → READY | true | SAVED | Battery **2 → 1**, 대상 Battery509102 소실 |
| BionicEye part/index 16 → 99999 | QUEUED → READY | true | SAVED | 입력 BionicEye가 export에서 소실 |
| meta gameVersion 1.5 | LOAD_REJECTED → LOAD_FAILED | false | 거부 / 파일 없음 | 방어 확인 |
| fixture 요구 Royalty / active config에서 Royalty 제거 | LOAD_REJECTED → LOAD_FAILED | false | 거부 | DLC configuration mismatch 방어 확인 |
| negative 이후 정상 fixture 재로드 | QUEUED → READY | true | 허용 가능 | scanner false reject 미재현 |

Fresh missing Recipe의 첫 load는 `Gen=1`, `LastFailure=''`, **loadErrorCount=0**인데 bill을 잃었다. private MissingRecipeExport.rws SHA는 `382BBFDBDD860D254C9DC8E40627AF5BCD33649582FC98CEBD336268F5F46D92`다. InvalidPartExport.rws SHA는 `332438E2315D9D4FD0C58233C4BD24B9FBBE3B7C6846391E807D90D70252C0E0`다. 이 case들은 이전 정상 Game의 재사용으로만 설명할 수 없다.

CrossRegistryThing 로그에는 `Could not load reference to Verse.ThingDef named Stab` 및 관련 load/registration/cross-reference 오류가 있는데 READY/SAVED가 반환됐다. 어떤 Unity log callback 전달 분기가 모든 오류를 놓쳤는지까지 확정하지 않는다. 독립 증거는 **현재 gate가 실제 native semantic failure를 차단하지 못한다**는 것이다.

**EVIDENCE:** [dependency 결과](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/dependency-results.json), [fresh semantic/timeout 결과](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/targeted-boundary-results.json), [fresh live 상태](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/FreshSemanticNegatives/missing-recipe-live.json), [실제 fresh load log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/FreshSemanticNegatives/player.log), [cross-registry load log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/DependencyDirectLoad/player.log). 입력·출력 rws는 해당 profile의 Saves에 보존했다.

**SCOPE:** missing dependencies와 실제 graph loss의 admission/export boundary. 최초 InvalidBodyPart mutator는 잘못된 schema 경로 때문에 setup failure였고 판정에서 제외했다. FreshSemanticNegatives에서 실제 `<part><body>/<index>` schema로 재시험한 결과만 위 표에 채택했다.

**DOES NOT PROVE:** 모든 mod/DLC schema를 검증했다거나 corrupt export가 canonical DB에 commit됐다는 뜻은 아니다. 정상 파일 한 종류의 승인으로 scanner의 전체 false-reject 부재를 보장하지 않는다.

**Severity / location / required fix:** 기존 QA-ENGINE-002 **Critical**, SRS-FR-098/155, SRS-NFR-004/006/007. [WorkerBridge.cs:435](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:435), [851](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:851), [858](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:858), [1471](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:1471). 현재 scanner는 literal `def`와 any-registry name existence를 혼용하고 recipe/typed body-part graph를 검증하지 않는다. Unity Error/Exception counter만으로 semantic integrity를 보장할 수 없다. typed dependency/reference 검증과 loaded graph의 identity/count/relationship loss 검증을 READY 이전에 수행해야 한다. unknown critical state는 fail-closed/quarantine해야 한다.

부수 관찰: successful reload 후 이전 실패의 LastFailure 문자열이 STATUS에 남는 case가 있다. 실패 원인과 현재 generation 성공 상태를 분리해야 한다. 이는 위 Critical loss의 대체 원인이 아니다.

## 6. QA-ENGINE-003 — cooperative execution / queued request boundary

**CLAIM:** 정상 RUN은 격리되고 STEP이 제한된 slice로 실행되어 별도 control connection을 굶기지 않으며 cancellation/expiry/overflow/timeout 방어가 있다.

**SETUP:** 정상 RUN_TICKS 50000, STEP_TICKS 50000 999999, 별도 TCP connection의 STATUS, CANCEL, observer main-thread BLOCK과 queue inspection을 사용했다. STATUS latency는 RemainingStep>0인 실제 실행 중에만 측정했다. 180 connection flood에는 QA ThreadPool min=256을 명시적으로 적용했다. timeout 단일 case는 별도 fresh process에서 queued command/시점을 확인했다.

**ORACLE:** quarantine의 실제 tick effect=0; STEP native DoSingleTick/frame ≤20; CANCEL 후 remaining=0/안정; expired request effect=0; overflow는 명시적 거부; expired/invalidated execution lease의 요청은 나중에 실행되면 안 된다. numeric latency는 A의 self-test claim과 비교하며 SRS-NFR-011의 미확정 최종 SLO로 만들지 않는다.

**OBSERVED:**

| 시험 | 독립 측정 |
|---|---|
| normal RUN_TICKS 50000 | quarantine error, **ΔG=0 / ΔL-equivalent=0** |
| oversized STEP | response SliceSize=20 / HardCap=20, **실제 최대 native ticks/frame=20** |
| concurrent STATUS | 별도 connection, **45/45 samples가 active workload**, 평균 **13.204 ms**, p95 **29.645 ms**, 최대 **138.244 ms** |
| CANCEL | L-equivalent=1268에서 remaining=0, 후속 관측에서 tick count 안정 |
| 12초 queue expiry — STEP77 | worker queue timeout, **ΔG=0 / ΔL=0** |
| 180 connection flood / main-thread BLOCK33초 | 관측 peak queue=100, capacity rejection=1, server wait timeout=57, worker expiry=45, OK STEP=23, network error=54 |
| flood 해제 후 | ΔG/ΔL=38, 후속 상태 안정. 각 요청 enqueue 시점이 달라 이 38틱을 timeout 요청의 실행으로 귀속하지 않음 |
| controlled server30초 timeout — queued STEP777 | **30001.38 ms**에 server timeout. unblock 및 후속 상태 모두 **ΔG/ΔL=0** |
| controlled client5초 timeout/disconnect — queued STEP79, BLOCK8초 | **5002.266 ms**에 client timeout/소켓 종료. unblock 후 remaining79 → 늦은 실행16 → **최종79틱 완료** |

30초 server wait timeout 뒤의 단일 expired request가 실행되지 않은 점은 인정한다. 반면 **client timeout/disconnect는 queue 내 request를 invalidate하지 않는다.** 두 상황을 혼동하지 않는다. 현재 10초 TTL 안에서 detached STEP이 실행되는 것을 확인했다. 연결 종료 뒤 accepted operation을 계속하도록 설계할 수는 있지만 그 경우 operation/lease/epoch/result 조회 계약이 필요하다. 현재 후보는 그런 계약 없이 caller가 사라진 pre-execution 요청을 실행한다. ADR-001 fencing을 만족한다고 볼 수 없다.

A self-test의 `max <50ms` oracle는 이 concurrent 측정에서 통과하지 않았다. 다만 138ms 단일 최대치로 최종 제품 NFR-011 FAIL 임계값을 새로 정하지 않는다. slice가 한 native tick의 실행 시간을 선점할 수 없으므로 10ms budget도 엄격한 frame deadline은 아니다.

**EVIDENCE:** [controls / 전체 sample 및 flood 응답](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/control-results.json), [controlled timeout 결과](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/targeted-boundary-results.json), [controls 실행 script](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/controls.py), [timeout injection script](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/targeted_boundaries.py). 각 profile에는 frame/queue sample과 raw command 응답이 있다.

**SCOPE:** cooperative tick 및 control/request liveness. flood에서 queue>100 race는 **재현하지 않았다**. Count check와 Enqueue가 원자적 admission이 아닌 문제는 static concern으로 남긴다. flood 성공23건이 모두 7틱씩 commit됐다는 보존 보장은 없다. STEP command는 남은 tick budget을 설정하는 제어 명령이므로 이 시험을 operation queue의 FIFO transaction 보존 시험으로 해석하지 않는다.

**DOES NOT PROVE:** 공개 diagnostic loop를 50000틱으로 이번에 재실행하지 않았다. production remote command latency, multi-worker fairness, 강제 client crash 또는 모든 request/epoch fencing을 검증한 것은 아니다. mixed flood 결과만으로 timeout 후 effect가 모두 0이라고 결론내리지 않는다.

**Severity / location / required fix:** 기존 QA-ENGINE-003 **High**, SRS-NFR-008/011 및 ADR-001/002. [WorkerBridge.cs:486](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:486), [609](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:609), [620](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:620). Execution generation/lease와 request deadline·cancellation의 원자적 admission 모델이 필요하다. runtime expiry는 DateTime.UtcNow 대신 monotonic M 계약에 맞춰야 한다. 안전한 bounded admission도 필요하다.

추가 static 경로: [686](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:686), [1033](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:1033)의 `QA_DIAGNOSTIC_RUN_TICKS`는 같은 TCP command dispatch에서 monolithic DoSingleTick loop로 들어가며 cap/budget·별도 authorization/enable switch가 없다. 이름만 diagnostic으로 바꾼 것으로 endpoint 안전성까지 입증할 수 없다. 지원된 프로토콜에서 배제하거나 명시적 isolated diagnostic mode로 봉쇄해야 한다.

## 7. QA-ENGINE-005 — global dispatch / causal isolation

**CLAIM:** retained global helper는 passive/read-only 또는 minimal coherence이며 target 이외 domain progression을 만들지 않는다. fastEcology escape가 차단된다.

**SETUP:** clean ValidatedBoundary에서 READY 전/후와 authorized 2000 target ticks를 비교했다. native fields/collections, WorldComponents/GameComponents, factions/history/tales/off-map Pawn을 읽었다. 실제 native Caravan을 생성하고 StartPath로 이동 가능 경로를 설정한 뒤 추가1000틱을 실행했다. QA MapProbe는 global counter와 foreign chronological getter를 실제 target execution에서 읽어 결과 필드에 보존했다. fastEcology=true를 강제한 ECOLOGY 1 native tick도 별도로 실행했다.

**ORACLE:** approved projection/helper 외의 world/foreign mutation과 target input/result contamination이 없어야 한다. 필요한 helper는 clock/read-set/output scope가 정의돼야 한다. 단순히 export에서 foreign 값을 버리는 것은 충분하지 않다. fastEcology로 foreign plant age/growth가 진행되면 안 된다.

**OBSERVED:**

| 경로/상태 | 실제 결과 |
|---|---|
| World/WorldComponents/FactionManager/Factions/History/Tales | 관측한 primitive state 및 relevant counters에서 2000틱 동안 변화 없음 |
| WorldObjects / 이동 Caravan | WorldObject_200002, Human214723, Tile50878,0 → next1816,0 native StartPath. 추가1000틱 후 path/movement state 유지 |
| off-map/caravan Pawn | ordinary biology/needs progression은 막힘. chronological getter는 G advancement를 반영 |
| GameComponents | 기존 GameProbe 및 GlobalProbe **0 → 2000** |
| native Anomaly | `GameComponent_Anomaly.nextHarbingerTreeCheckTick` **-99999 → 37572** |
| target MapProbe causal output | `lastGlobalRead=1999`, `lastForeignChronological=698111106` 저장 |
| foreign map MapProbe | ticks=0, foreign food/job/plant 및 관측 local state 진행 없음 |
| forced fastEcology test | current profile warning 확인. target plant13개는 정상 native tick 경로에서 변화, **foreign changed plants=0** |

A 보고서의 retained World/History/Tale 설명을 실제 정책으로 받아들이면 안 된다. frozen source의 WorldTick/WorldPostTick/HistoryTick/TaleManagerTick prefix는 scoped mode에서 **false**다. 그 아래 Faction/WorldObjects/WorldPawns dispatch도 억제되는 실제 결과를 인정한다. 반면 **GameComponent dispatch는 blanket retained**이며 read-only가 아니다.

Native Anomaly GameComponentTick의 static IL은 G/TicksGame 검사, TrySpawnHarbingerTrees 호출, random interval 취득 및 다음 deadline 저장 경로를 갖는다. 이번 native timer 변경은 실제 실행 증거다. 이번 fixture에서 그 경로가 실제 추가 incident를 생성했다거나 target battle 승패를 바꿨다고 주장하지 않는다. 다만 전역 random/time-dependent helper를 무조건 passive로 분류할 수 없다.

QA-only target MapProbe가 변경된 global counter 및 foreign age getter를 읽고 target 결과에 남겼다. 이는 **허용된 target execution이 foreign/global clock query에 의존할 수 있는 causal 경로를 실제 검증한 것**이다. 격리되지 않은 query가 존재하며 현재 candidate에 이를 승인/차단하는 read-set contract가 없다. vanilla AI 특정 분기의 결과 오염은 별도 증명이 필요한 더 강한 주장이다.

**EVIDENCE:** [live 비교 summary](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/validated-observation-summary.json), [before](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/ready.xml), [after2000](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/after2000.xml), [native caravan setup](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/native-caravan-setup.json), [fastEcology plant delta](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/ecology-plant-delta.json), [engine IL](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/native-hardening-il.txt).

**SCOPE:** 실제 engine/GameComponent 상태 변경, native moving world object, causal QA query, debug plant escape. broad observer는 primitive fields/collection sizes와 specific native graph를 비교했으며 임의 mod의 모든 nested object state를 exhaustively serialize하지 않았다.

**DOES NOT PROVE:** 모든 world mechanic의 완전한 동결, 모든 incident 발생, vanilla AI의 구체적인 다른 승패, canonical graph merge의 무오염을 증명한 것은 아니다. foreign chronological 변화는 단순 save-field mutation과 구분한 **derived getter 변화**다.

**Severity / location / required fix:** 기존 QA-ENGINE-005 **High**, SRS-FR-003/153/155, SRS-NFR-007, ADR-006A. [WorkerBridge.cs:175](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:175), [235](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:235), [245](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:245), [531](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:531). 실제 retained dispatch inventory를 작성하고 GameComponent별 clock/read/write/output 계약으로 분류해야 한다. unsupported critical helper는 fail-closed 또는 explicit supported projection이 필요하다. fastEcology 수정만으로 이 결함 전체를 닫을 수 없다.

## 8. QA-ENGINE-006 — fixture validity / final oracle trust

**CLAIM:** engine-generated fixture와 11차원 strict predicate가 complete graph preservation을 증명한다.

**SETUP:** 동결 fixture를 실제 live engine으로 로드하고 상태를 읽었다. authorized target simulation/private export 후 **새 native process**에서 fresh reload해 재관측했다. A script의 frozen AST 중 실제 final predicate assign nodes를 그대로 추출·실행하고, native detailed summary 입력을 각 차원에서 하나씩 확실히 훼손했다. baseline predicate PASS도 먼저 확인했다.

**ORACLE:** native identity/reference/value의 유효성과 reload 보존을 관측해야 한다. 훼손된 각 차원의 final predicate는 FAIL해야 한다. 단순 type 이름 또는 라벨 존재는 원래 object/관계/value 보존의 증거가 아니다.

**OBSERVED — fixture 개선은 인정:**

| 실제 fixture 항목 | live engine 확인 |
|---|---|
| Thing/Verb/Hediff identity | 관측 graph에서 duplicate Thing numeric ID / Verb load ID / Hediff load ID **0** |
| 무기 / 의복 | Gun_Autopistol / Apparel_FlakVest native tracker에 존재 |
| inventory | MedicineIndustrial509004×10, Meat_Muffalo520001×10. frozen 입력과 live/reload 모두 같은 count |
| Hediff/body-part | Hediff_22 Stab/Leg(partIndex55), Hediff_200015 BionicEye/Eye(partIndex16), valid native identities |
| 침대 | 실제 bed owner Human302 참조 |
| 동물 | LabradorRetriever207367, master Human302, Obedience learned=true |
| bill | TableSculpting509106 → Bill_Make_SculptureSmall_0, valid RecipeDef Make_SculptureSmall |
| battery | Battery509102 storedPower=300 |
| 실제 crop | Plant_Rice207368, IsCrop=true, Growth0.5, 실제 fertile/growing 위치 |
| corpse/container | 기존 ancient casket의 실제 corpse/container graph 존재. 새 Sarcophagus207369는 **empty** |
| fresh reload | READY, G=4824 유지, autonomous native tick calls=0. 관계/value는 raw XML 이름보다 live graph로 확인 |

정상 primary load 구간에서 이전 synthetic fixture와 같은 serializer/registration 오류는 관찰하지 않았다. 단 startup에는 `Things/Item/Resource/Gold` texture를 WarEconomy_TacticalProofToken에서 찾지 못하는 별도 cosmetic error가 있다. **player.log 전체 error 0이라고 보고하지 않는다.** clean validated profile에서 observer HarmonyException은 없다.

Corpse dimension의 PASS는 기존 다른 ancient caskets의 corpse로도 충족된다. 따라서 **새로 만든 특정 sarcophagus/corpse pair**를 보존했다고 인정할 수 없다. 일반 corpse/container coverage는 존재한다.

**OBSERVED — exact final predicate negative oracle:**

| A dimension에 대응한 훼손 | 기대 final predicate | 실제 final predicate |
|---|---|---|
| pawn의 특정 identity를 다른 Human ID로 변경 | FAIL | **PASS — false negative** |
| 무기 kind 변경 | FAIL | FAIL |
| 의복 kind 변경 | FAIL | FAIL |
| Hediff body-part 참조 변경 | FAIL | **PASS — false negative** |
| Bed 접두를 유지하면서 owned reference ID 변경 | FAIL | **PASS — false negative** |
| animal master reference 변경 | FAIL | **PASS — false negative** |
| bill count 1 → 10 | FAIL | **PASS — Bills=1 substring가 Bills=10과 일치** |
| battery storedPower 300 → 0 | FAIL | **PASS — false negative** |
| crop growth → 0 | FAIL | **PASS — false negative** |
| corpse identity 변경 | FAIL | **PASS — false negative** |
| foreign food value → 0 | FAIL | **PASS — false negative** |
| 추가: inventory를 Inv=[]로 비움 | FAIL | **PASS — final predicate에 inventory 없음** |

11개 dimension 중 **9개 false negative**, 2개만 의도한 훼손을 검출했다. 추가 inventory 훼손도 PASS다. 모든 case에서 oracle input이 실제로 달라졌음을 확인했다. 이 결과를 11차원 strict 보존 검사로 사용할 수 없다. 첫20개 plant summary의 `sowable`/`Crop(...)` 라벨과 실제 재배 crop을 혼동하면 새 Rice 자체가 최종 oracle에서 빠질 수도 있다.

**EVIDENCE:** [negative oracle 결과](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/validated-oracle-negative-results.json), [정확한 predicate 추출/훼손 script](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/oracle_negatives_validated.py), [fresh reload live graph](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedFreshReload/reload-live.xml), [primary live graph](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/ready.xml), [선택 graph value/relationship 대조](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/fixture-live-reload-audit.json), [semantic load/reload 비교](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/semantic-audit.json).

**SCOPE:** fixture가 native engine으로 정상 materialize되는 근거는 강해졌다. negative oracle는 **실제 summary를 바꿔 exact PASS predicate의 검출력을 시험한 것**이다. 11개 negative save를 각각 native load한 시험이라고 보고하지 않는다. actual native loss는 §5의 별도 engine 시험이다.

**DOES NOT PROVE:** raw XML 비교 불일치가 모두 corruption은 아니다. fresh reload에는 nonpersistent lifeStage/cache/driver/ingredient-search 초기화 및 collection ordering 차이가 있다. semantic-audit의 raw flattened diff30331개를 30331개 손상으로 해석하지 않는다. arbitrary graph 모든 identity namespace의 중복 부재와 complete canonical merge를 입증한 것은 아니다.

**Severity / location / required fix:** 기존 QA-ENGINE-006 **High**, SRS-FR-155/166 및 SRS-NFR-004/006. [A regression script:492](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/run_hardening_regressions.py:492), [498](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/run_hardening_regressions.py:498), [506](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/run_hardening_regressions.py:506). entity ID별 structured records로 equipment/apparel/inventory counts·Hediff/body part·bed/master·bill identity/state·battery/crop values·corpse/container relationship·foreign state를 비교해야 한다. 의도된 tactical 변경, initialization normalization, temporal codec projection은 별도 기대 결과로 분리하고 각 dimension의 negative test가 FAIL함을 입증해야 한다.

## 9. QA-ENGINE-007 — pre-load mechanical fence

**CLAIM:** load가 Playing으로 넘어가도 READY/첫 authorized STEP 전 자동 simulation을 진행하지 않는다.

**SETUP:** clean observer로 LOAD request, native loader, FinalizeInit prefix/postfix, ProgramState, candidate lifecycle, frame tick 호출을 관측했다. foreign MapComponent 하나에 의존하지 않고 Pawn/jobs/needs/plants/timers, World/Faction/components 및 target graph를 FinalizeInit 전후/READY와 비교했다. 그 다음 authorized STEP1을 실행했다. 새 process의 private export fresh reload도 관측했다.

**ORACLE:** save에서 복원된 G와 local state는 unauthorized native ticks로 진행하지 않아야 한다. initialization/cache normalization은 business simulation effect와 구분한다. first authorized tick에서만 actual completed step 증가를 확인한다.

**OBSERVED:** 시각은 process-relative milliseconds다.

| lifecycle observation | ProgramState | G | native tick calls | scope / L-equivalent |
|---|---|---:|---:|---|
| LOAD request — 140.783ms | Entry | -1 | 0 | false / 0 |
| Loader prefix — 599.375ms | Entry | -1 | 0 | false / 0 |
| LOADING — 917.599ms | MapInitializing | 0 | 0 | false / 0 |
| FinalizeInit prefix — 7243.682ms | MapInitializing | 1823 | 0 | false / 0 |
| FinalizeInit postfix, pause effective — 7942.964ms | Playing | 1823 | 0 | false / 0 |
| LOADING/Playing — 7952.493ms | Playing | 1823 | 0 | false / 0 |
| READY — 12093.718ms | Playing | 1823 | 0 | true / 0 |
| first authorized STEP1 이후 | Playing | 1824 | 1 | true / 1 |

Playing 전환이 native FinalizeInit 내부에서 일어나므로 관측 prefix/postfix로 그 구간을 감쌌다. 임의의 lifecycle 순서를 만들지 않았다. G=0→1823은 save의 값 복원이며 1823회의 unauthorized tick 실행이 아니다.

FinalizeInit 전후의 관측 차이는 ProgramState 전환, Normal→Paused, WorldPawns query cache count0→21/15였다. Playing 이전에 읽을 수 없는 chronology placeholder는 이 비교에서 제외했다. Pawn/job/needs/plant business progression은 관측되지 않았다. Post-Finalize→READY는 scope/lifecycle/load-error tracking 전환과 WaterInfo.skyTex runtime cache materialization이 달랐으며 G/native ticks/local counters는 그대로였다. fresh reload에서도 G=4824, native tick calls=0이다.

**EVIDENCE:** [lifecycle TSV](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/observer-lifecycle.tsv), [FinalizeInit before](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/observer-finalize-before.xml), [FinalizeInit after](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/observer-finalize-after.xml), [semantic delta audit](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/semantic-audit.json), [first authorized STEP](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/first-authorized-step.json).

**SCOPE:** 검증된 DLC/mod 환경과 이 fixture에서 **vanilla autonomous ticking escape의 기계적 방어**는 해결 확인이다. [WorkerBridge.cs:89](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:89)의 TickManagerUpdate unconditional false와 [127](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:127)의 FinalizeInit pause가 실제 효과를 냈다. source의 ScopedTacticalSession 자체는 READY에서 활성화되지만 그 전에 vanilla tick scheduling이 막혔다.

**DOES NOT PROVE:** load normalization이 모든 mod/모든 temporal schema에서 canonical-safe라는 보장은 없다. arbitrary direct DoSingleTick callback이 fence를 통과할 수 없다는 증거도 아니다. READY의 semantic graph/typed anchor/revision/admission 검증 완료는 **QA-ENGINE-002/004 및 ADR-006A 구현 gate로 계속 OPEN**이다. 이 해결 판정은 해당 미구현 요구를 축소하지 않는다.

**Required follow-up:** 위 mechanical regression을 고정하고 typed post-load validation 및 authorized generation/lease execution gate를 그 위에 통합해야 한다. 모든 normalization을 허용하는 blanket exception을 두면 안 된다.

## 10. QA-ENGINE-004 — accepted temporal architecture / 아직 OPEN

**CLAIM:** Worker hardening이 temporal-authority 구현 완료를 뜻하는지 별도 확인한다. 기본값은 OPEN이다.

**SETUP:** authorized STEP2000 전후 target G/completed steps, frozen foreign Pawn Human100302의 native biological/chronological getter, private export/fresh reload 및 source를 대조했다.

**ORACLE:** Worker G는 W authority가 아니다. frozen foreign residence/local clock의 chronology는 incidental G를 따라 진행하면 안 된다. typed time materialization, LocalClock/revisions/lease 및 target-scoped graph+time publication이 실제 구현돼야 한다.

**OBSERVED:** G **1823→3823**, target completed step **0→2000**. foreign Pawn chronology **698109106→698111106 (+2000)**, biology **176109104 그대로**, foreign map probe0, foreign job/needs/plant progression 없음. native absolute-anchor derived getter는 Map tick 차단만으로 고정되지 않는다. Candidate에는 typed temporal codec, accepted LocalClockId/TimeRevision/SaveRevision admission, target-scoped outcome/canonical merge 구현 증거가 없다. fresh reload의 TicksSimulated=0은 worker-session counter reset이며 durable LocalTick=0이라는 뜻으로 사용할 수 없다.

전체 final 관측은 G=4824, TicksSimulated=3000, native tick calls=3001이다. 추가1회는 **QA가 명시적으로 실행한 ECOLOGY diagnostic native tick**이므로 이를 정상 STEP counting loss로 신고하지 않는다. 이 구분 없이 G−L 차이를 새 결함으로 만들지 않는다.

**EVIDENCE:** [live clock summary](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/validated-observation-summary.json), [ready / foreign state](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/ready.xml), [after2000](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedBoundary/after2000.xml), [fresh reload](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/ValidatedFreshReload/reload-live.xml), [Worker activation source:72](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:72).

**SCOPE:** temporal boundary 미구현 및 derived chronology의 재현이다. ADR-006A의 ACCEPTED 상태 자체에 대한 이의는 없다.

**DOES NOT PROVE:** B2 extraction/merge가 기술적으로 불가능하다거나, 이번 Worker 실행에서 W가 진행했다거나, 실제 운영에서 잘못된 save가 canonical 상태가 됐다는 주장은 아니다.

**Severity / required fix:** 기존 QA-ENGINE-004 **Critical**, SRS-FR-002/003/155 및 SRS-NFR-004/006/007. accepted ADR-006A의 typed temporal materialization/admission/publication을 구현·독립 검증해야 한다. blanket full-save tick rebase 또는 full-save 전체 승격은 허용하지 않는다. inventory/ownership/time horizon commit은 ADR-003/004 계약과 결합해야 한다.

## 11. QA-ENGINE-008 — START 이전 elapsed debt

**CLAIM:** 긴 LOAD/EXPORT/idle의 elapsed가 START60의 새 local execution budget으로 유입되지 않는다. pause/resume/cancel/restart도 새 pacing 기준을 사용한다.

**SETUP:** 실제 native LOAD 뒤, private EXPORT 뒤, idle3초 뒤, PAUSE/RESUME, CANCEL/RESTART에 각각 START_SIMULATION60을 실행했다. native DoSingleTick 호출을 frame별 관측하고 약3초의 completed steps/monotonic elapsed로 TPS를 구했다. 각 case 후 pause 상태의 안정도 확인했다.

**ORACLE:** 이전 대기 시간을 한꺼번에 실행하는 첫-frame burst가 없어야 한다. 해당 실행 동안 약60TPS로 진행하고 pause 후 증가가 멈춰야 한다.

**OBSERVED:**

| case | 초기8개 tick-bearing frame의 실제 tick 수 | 전체 관측 max ticks/frame | measured TPS | pause 안정 |
|---|---|---:|---:|---|
| START after long LOAD | 1,1,1,1,1,1,1,1 | 1 | 59.569 | 확인 |
| START after EXPORT | 1,1,1,1,1,1,1,1 | 1 | 59.962 | 확인 |
| START after idle3s | 1,1,1,1,1,1,1,1 | 1 | 59.689 | 확인 |
| pause/resume | 1,1,1,1,1,1,1,1 | 1 | 59.642 | 확인 |
| cancel/restart | 1,1,1,1,1,1,1,1 | 1 | 59.655 | 확인 |

**EVIDENCE:** [controls pacing 결과 및 raw sample](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/control-results.json), ConcurrentControls의 frame CSV, [WorkerBridge.cs:508](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:508), [980](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/Reviewed/WorkerBridge.cs:980).

**SCOPE:** prior wall-time START debt 결함의 해결 확인. raw 결과의 `first_tick_after_start_ms`는 이름과 달리 process-relative observer timestamp이므로 START→첫 tick latency로 인용하지 않았다.

**DOES NOT PROVE:** 모든 하드웨어/long-running jitter에서 정확60TPS, runtime stall 때 모든 wall-time debt 보존, canonical LocalTick persistence를 증명하지 않는다. interval1.5 clamp는 active elapsed budget을 버릴 수 있으며 product pacing/time contract는 QA-ENGINE-004와 별도다. M과 durable L을 혼동하지 않는다.

## 12. 후속 개발과 QA 승인 조건

1. **QA-ENGINE-002 우선:** typed dependency/graph validation을 READY 전에 넣는다. 이번 missing Recipe / cross-registry Thing / body-part corruption case는 READY=false·EXPORT 거부가 되어야 한다. 정상 fixture false rejection도 계속 시험한다.
2. **QA-ENGINE-006 oracle 정비:** A final predicate를 identity/reference/value 기반 structured comparison으로 교체한다. 11개 negative + inventory negative가 모두 FAIL해야 하며 intended simulation/normalization 변화는 기대 결과로 분리한다.
3. **QA-ENGINE-003 남은 request boundary:** session/worker lease/generation·deadline·cancellation·result query를 정의한다. timeout 후 effect를 “기본 server timeout”과 “client disconnect”로 분리해 검증한다. 공개 diagnostic monolithic path와 queue admission race를 봉쇄한다.
4. **QA-ENGINE-005 dispatch inventory:** 실제 suppressed/retained 경로 목록을 바로잡는다. GameComponents의 native timer/random/query를 시간·read-set·output scope별로 검증하고 unsupported state는 fail-closed한다. foreign causal contamination은 결과 discard만으로 해결하지 않는다.
5. **QA-ENGINE-004 temporal/B2 구현:** accepted ADR-006A를 기준으로 LocalClock identity, typed anchors, revision/lease admission, target graph+time extraction/publication을 구현한다. ADR-003/004의 inventory·distributed commit 세부 설계를 여기서 대신 확정하지 않는다.
6. **해결 회귀 유지:** QA-ENGINE-007의 pre-load native tick count0과 broad state assertions, QA-ENGINE-008의 5가지 START pacing case를 계속 보존한다. 이후 codec/lease 통합이 이 개선을 깨뜨리지 않게 검증한다.

추가 엔진 PoC를 자동으로 요구하지 않는다. 이번 loader 손실·negative oracle·queue fencing·native dispatch 목록은 이미 재현 또는 정적 근거가 있으므로 먼저 해당 구현/검증을 구체화해야 한다. B2의 target graph extraction과 temporal codec의 미확인 engine boundary는 실제 구현 범위가 정해진 뒤 최소 필요한 runtime 검증을 선택한다. offline 공격 금지나 기능 축소로 우회하지 않는다.

## 13. 종료·인계

QA-owned native process 9개 PID는 최종 `Get-Process` 재조회에서 모두 존재하지 않았다. 초기 Win32_Process CIM 조회는 접근 거부였으므로 그 null 결과를 종료 증거로 사용하지 않고 Get-Process 결과로 대체했다. [process 종료 확인](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/all-owned-processes-final.json).

실기 관측용으로 QA가 만든 **QA.Boundary02.Observer junction 하나만** exact target/LinkType를 확인한 뒤 제거했다. observer 코드/바이너리와 evidence는 보존했고 기존 WarEconomyMod/WorkerBridge/ProbeMod 연결은 제거하지 않았다. [junction 정리 기록](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/junction-cleanup.json).

최종 evidence inventory/hash는 [artifact manifest](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/artifact-manifest.json)에, 문서/기계 결과 교차 검사는 [report verification](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/BOUNDARY02-20261002/report-verification.json)에 기록한다. 재현 script는 새 isolated profile 이름을 요구하며 기존 evidence를 덮어쓰지 않는다. observer junction 제거 뒤 instrumented script를 재실행하려면 QA observer를 별도 모드로 연결해야 한다. 이를 Production/candidate 배포 변경으로 해석하면 안 된다.

**Master recommendation:** 이 exact revision의 전체 hardening gate는 **FAIL**, Architecture Gate는 **BLOCKED BY ARCHITECTURE 유지**, ADR-002는 **PROVISIONAL 유지**다. pre-load autonomous tick fence와 START debt 수정은 인정한다. Critical semantic-load 및 temporal boundary, High global/oracle 경계가 남아 있으므로 전체 Worker 또는 canonical tactical outcome을 승인하지 않는다. 최종 상태 변경은 Master에게 위임하며 다음 지시를 기다린다.
