# QA Production Transaction Pipeline — Independent Review 01 REV1

[QA REVIEW]

- **Work Package:** WP-QA-PROD-TRANSACTION-PIPELINE-01-REV1
- **Target:** exact Release candidate in [Production_Transaction_Pipeline_Slice_01_REV1.md](C:/Users/user/Desktop/RimMulti/Production_Transaction_Pipeline_Slice_01_REV1.md)
- **Verdict: FAIL**
- **Reviewer:** GPT-6.1 Sol — Independent QA / Architecture Reviewer
- **Execution:** 2026-10-02–03, Asia/Seoul, Windows / .NET 8.0.10.
- **Production modification:** 없음. 동결 Release bytes의 복사본과 QA 소유 DB만 시험했다. Production 소스/바이너리를 수정하거나 재빌드하지 않았다.
- **Master state:** 변경하지 않음. 아래 CLOSED/PARTIAL/STILL FAILING은 원장 변경이 아닌 독립 QA 권고다.

## 1. Verdict and scope

REV1은 실제 개선을 포함한다. 독립 OS process 25개의 CAS 경쟁은 **1 SUCCESS / 24 STALE_REVISION**, 같은 ID의 12개 process 경쟁은 **1 SUCCESS / 11 ALREADY_COMMITTED**였다. 단일 DB transaction의 revision/history/operation/receipt/audit/event 커밋 경계, pooled connection의 WAL/FULL 재설정, UTC epoch receipt 재조회는 시험한 범위에서 통과했다. Fast-path PREPARED도 제거됐다.

그러나 **E2 foundation은 FAIL**이다. 구분자 기반 fingerprint는 다른 envelope를 같은 요청으로 오인한다. 외부 durable 효과가 restart 후 두 번 실행됐고, publication cursor는 실패한 선행 event를 건너뛰었다. 일반 startup은 pending recovery나 일부 잘못된 schema를 남긴 채 READY에 진입했다. 추가로 v1 migration의 durable 기록 삭제, incarnation rotation 경쟁, 종료 시 수락한 요청 미완료, enqueue 이후 command 변경이 재현됐다.

원래 QA-PIPELINE-001..012의 권고는 **CLOSED 4 / PARTIAL 3 / STILL FAILING 5**다. 신규 QA-PIPELINE-013..018을 아래에 제안한다. A의 “all 12 closed” 주장은 독립 증거와 일치하지 않는다.

**Requirement boundary:** Canonical SRS-NFR-004(상태 일관성), SRS-NFR-006(영속성), SRS-NFR-007(중앙 상태 권한), SRS-NFR-012(감사 가능성)에 필요한 기반 계약을 검토했다. SRS-NFR-005의 실제 gameplay transaction 원자성은 probe만으로 인증하지 않는다. PrincipalId는 내부 fixture 입력이며 Production authentication 증거가 아니다.

## 2. Candidate identity / provenance

| Item | Independent evidence |
|---|---|
| A가 열거한 변경 source | **14/14 SHA-256 일치**; appendix 및 source-provenance.json |
| Primary Release Server DLL | **288AADC7C8B88A3492583797F2D4537F73EC88362723671E0222BF0AEDB3ED8C** |
| 실제 Harness loaded DLL SHA | 위 Release SHA와 동일 |
| Loaded Server MVID | **84fe126b-6b92-47b0-8d59-ec0988219e87** |
| Loaded DLL path | `C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV1-20261003\Harness\bin\Debug\net8.0\WarEconomy.Server.dll` |
| Before/after Production freeze | **148 → 148 files, 추가/삭제/변경 0**; .cs/.csproj/.dll/.exe/.json/.pdb 해시 전후 대조 |
| Runtime | .NET 8.0.10 |
| SQLite provider / native | Microsoft.Data.Sqlite loaded assembly 8.0.10.0 / native SQLite 3.41.2 |
| Package manifest | Microsoft.Data.Sqlite/Core 8.0.10; SQLitePCLRaw bundle/core/lib/provider 2.1.6; Newtonsoft.Json 13.0.3; System.Memory 4.5.3 |
| Effective DB identity | user_version=2; application_id=1463898693 = **0x57415245** |
| Effective canonical connection | WAL; synchronous=2 FULL; foreign_keys=1; busy_timeout=5000; provider DefaultTimeout=5 seconds |

Harness의 `Debug` 경로는 **QA executable의 output 위치**다. 로드한 Server DLL은 위 exact **Release** bytes이며 QA가 candidate를 Debug로 재빌드한 것이 아니다. `runtime-copy-identity`에는 FrozenRelease와 Harness에 실제 존재하는 dependency 파일의 해시 대조를 보존했다. Server/Common/SQLite/Newtonsoft 주요 실행 dependency의 byte identity를 확인했다. Server 전용 deps/runtimeconfig 파일이 Harness에 없는 경우는 누락으로 기록했으며 동일 파일이라고 간주하지 않았다.

일반 startup도 `Normal-fresh`, `Normal-pending`, `Normal-future-schema`, `Normal-missing-column`의 byte-identical Release 복사본을 별도 OS process로 실행했다. Harness에서 MVID를 읽었으며 일반 process의 CLR module MVID를 별도 attach로 읽었다고 주장하지 않는다. 기존 사용자 Server를 중지하지 않았고, 7777이 비어 있음을 확인한 뒤 QA Server를 실행/종료했다.

**Build discipline:** QA Harness만 빌드했다. Production의 exact Release assembly 실행과 source/manifest 동일성을 검증했지만, 이번 턴에 새 Production compilation이나 전체 Client/engine solution의 경고 0/오류 0을 독립 인증한 것은 아니다. A의 테스트 JSON을 증거로 재사용하지 않았으며, exact Release CLI battery를 별도 QA DB에서 직접 실행한 결과는 **19/19 PASS**였다. 이 battery의 한계는 section 9에 있다.

## 3. Original defect identity reconciliation

번호 기준은 [Sol Review 01](C:/Users/user/Desktop/RimMulti/QA_Production_Transaction_Pipeline_01.md) 및 이번 Master work order의 원래 의미다. 작업 폴더에서 QDL-041 원문은 확보하지 못했으므로 원장 상태를 추정하거나 변경하지 않았다.

A의 REV1 resolution table은 원래 **009(내구성)**을 같은-ID 경쟁, **010(같은-ID 경쟁)**을 storage lock, **011(storage typing)**을 incarnation/receipt, **012(receipt)**를 constraint 오분류에 연결한다. 또한 원래 **007(startup)**을 WAL/FULL에 연결한다. 아래는 번호를 재정의하지 않고 원래 의미로 재검증한 결과다.

| Original ID / original meaning | Recommendation | Independent result / evidence keys |
|---|---|---|
| QA-PIPELINE-001 operation identity | **STILL FAILING** | 각 필드 단독 변경, canonical JSON, principal 분리, caller hash 무권한은 통과. 다른 profile/config 구분자 조합이 동일 fingerprint → 기존 성공 receipt. `identity`, `caller-hash-authority`, `delimiter-collision` |
| QA-PIPELINE-002 PREPARED integrity | **CLOSED — narrow fast-path only** | enum/schema/reconciler에 PREPARED 경로 없음. precommit kill에서 durable operation 없음. legacy PREPARED를 auto-forward하지 않음. 파괴적 migration은 별도 015. 미래 reservation semantics는 미인증. `legacy-prepared`, precommit kills |
| QA-PIPELINE-003 live/recovery race | **PARTIAL** | 실제 live after-commit 대기와 별도 recovery 경쟁에서 COMMITTED 유지/추가 canonical effect 없음. 그러나 public journal API로 COMMITTED→ABORTED 성공, receipt/history와 모순. `live-convergence`, `terminal-transition-api` |
| QA-PIPELINE-004 duplicate external effect | **STILL FAILING** | 실제 후보 consumer + 별도 durable balance 효과: kill/restart로 동일 EventId 효과 1→2, balance 7→14. payload만 변조하고 기존 fingerprint 유지해도 실제 consumer가 허용. `kill-after-consumer-effect`, `fixture-mismatch-same-process` |
| QA-PIPELINE-005 transient/failed delivery recovery | **PARTIAL** | old FAILED tombstone 제거, exception 후 명시 replay 회복 가능. permanent failure는 disposition 없이 삼켜지고 false/live 후속 event가 선행 실패를 건너뜀. `stream-throw-first`, `stream-false-first`, `live-stream-gap`, `startup-1-throw` |
| QA-PIPELINE-006 ACK/decision convergence | **PARTIAL** | old PUBLISHED/COMMITTED decision split 제거. Operation은 kill 경계에서 COMMITTED 유지. ACK durable/cursor 이전 kill은 replay하며 외부 효과 중복; cursor 이후 kill은 중복 없음. `kill-after-server-ack`, `kill-before-cursor`, `kill-after-cursor` |
| QA-PIPELINE-007 normal startup readiness | **STILL FAILING** | fresh bootstrap 순서 개선. 일반 restart pending event에 consumer 없이 READY; startup manager는 failing consumer 또는 65건 중 50건 처리 후 READY. `normal-*`, `startup-1-throw`, `startup-65-persistent` |
| QA-PIPELINE-008 logical schema | **STILL FAILING** | 미래 version/누락 table/v2 wrong app은 거절. 필수 column, 잘못된 PK/UNIQUE/FK/CHECK, active incarnation 중복을 허용. partial migration 이후 canonical 기록 삭제가 남음. `schema-*`, `legacy-partial-migration` |
| QA-PIPELINE-009 durability | **CLOSED — configuration contract** | 실제 pooled native handle을 재사용하며 NORMAL로 오염시킨 뒤 20회 open 모두 WAL/FULL 재확인. physical power loss 미시험. `pooled-durability`, `metadata` |
| QA-PIPELINE-010 same-ID concurrency | **CLOSED** | independent OS process 12개 → 1 SUCCESS/11 ALREADY_COMMITTED, 동일 receipt, raw UNIQUE 0. `same-id-race` |
| QA-PIPELINE-011 storage-error typing | **STILL FAILING** | BUSY/LOCKED 및 receipt/event constraint/IOException typing 개선. initial aggregate constraint는 여전히 STALE_REVISION, expected=actual=0. `storage-aggregate-constraint`, `busy`, `native-locked`, `io-like` |
| QA-PIPELINE-012 receipt canonicalization | **CLOSED** | immutable receipt의 epoch/hash/identity가 5개 culture 및 process-local time zone fixture에서 동일. publication 상태가 receipt를 바꾸지 않음. `receipt-process-timezones` |

### Remaining original defects: location / root cause / required fix

- **001 — High:** [Models:103](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:103)의 `string.Join("|", ...)`는 필드 경계를 escape/length-prefix하지 않는다. 최초 `profile="PROFILE|EXTRA", config="CONFIG"`와 retry `profile="PROFILE", config="EXTRA|CONFIG"`는 서로 다른 envelope지만 **ALREADY_COMMITTED / Success=true**를 반환했다. SHA-256 자체 충돌이 아닌 동일 preimage serialization 문제다. typed canonical envelope나 unambiguous encoding을 사용하고 허용 값 검증을 명시해야 한다. 현 구현은 A가 주장한 TargetScopes[]/ExpectedRevisions[]가 아니라 scalar ProbeScopeId/ExpectedProbeRevision이다.
- **003 — High, storage API boundary:** [OperationJournal:93](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/OperationJournal.cs:93)의 expected-state SQL은 compare-and-set이지 business monotonicity 검사가 아니다. `expected=COMMITTED,new=ABORTED` 호출이 true를 반환했고 receipt/history는 commit을 유지했다. normal reconciler 경로의 원래 race는 해결됐지만 기반 API의 “COMMITTED may never become ABORTED”는 미충족이다. terminal decision 변경을 금지하거나 불가능한 API로 제한해야 한다.
- **004 — High:** [Consumer:25](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Testing/DurableTestConsumer.cs:25) dedup는 ConcurrentDictionary에만 존재한다. [Consumer:69](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Testing/DurableTestConsumer.cs:69)는 제출된 fingerprint 문자열끼리만 비교하며 실제 payload를 재계산하지 않는다. [Consumer:81](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Testing/DurableTestConsumer.cs:81)의 effect callback도 redelivery마다 호출된다. consumer acceptance identity + 검증된 payload fingerprint + semantic effect를 consumer의 durable transaction에 함께 보존하는 계약이 필요하다. downstream external system이면 그 시스템의 idempotency receipt/조회 계약을 명시해야 한다. 특정 distributed commit 방식은 여기서 선결정하지 않는다.
- **005 — High:** [Coordinator:408](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:408), [Coordinator:477](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:477)의 delivery exception은 disposition을 남기지 않는다. explicit retry 가능한 append-only log는 개선이지만 permanent failure/repair 상태, mandatory consumer 여부, 순서가 있는 failure 정책이 필요하다. event 존재만으로 eventually delivered를 보장하지 않는다.
- **006 — High:** [Coordinator:429](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:429) / [Coordinator:430](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:430)의 ACK/cursor는 분리 저장된다. ACK 후 kill 시 cursor만 기준으로 다시 consumer를 호출한다. 소비자 durable dedup와 연동하여 ACK/cursor를 일관되게 재구성해야 한다. server ACK atomic write만으로 external effect-before-ACK 창 전체를 해결했다고 주장하면 안 된다.
- **007 — High:** [Program:120](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:120)는 consumer registry 없이 startup을 호출한다. [Recovery:56](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:56)는 1회, 최대 50개 page만 replay하고 [Recovery:60](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:60)는 성공을 반환한다. **필수 consumer recovery 완료/명시 degraded/repair** 중 하나를 근거 있게 선택하고 admission에 반영해야 한다. 지금은 “delivery 미설정”과 “회복 완료”가 구분되지 않는다.
- **008 — High:** [Migration:237](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:237)는 table 이름과 OperationRecords column 세 개만 확인한다. 전체 required column/type/PK/UNIQUE/FK/CHECK/필수 index 및 active incarnation singleton을 검증해야 한다. 단순 integrity_check=ok는 논리적 schema 동등성 증거가 아니다. 삭제/부분 migration은 신규 015로 연결한다.
- **011 — Medium:** [ProbeAggregateStore:54](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/ProbeAggregateStore.cs:54)에서 initial INSERT의 모든 SqliteException을 false로 바꾸어 storage 장애를 revision conflict로 durable ABORTED 처리한다. 원인별 native error 분류를 보존하고 expected=actual인 실패를 stale로 판단하지 않아야 한다.

## 4. Independent execution measurements

### 4.1 Identity / replay / ABORTED

동일 `(PrincipalId, OperationId)`로 scope, revision, profile, type, schema version, config reference, payload를 **각각 단독** 변경하면 COLLISION_REJECTED였다. JSON property 순서/공백만 바꾸면 동일 ReceiptId/ReceiptHash로 ALREADY_COMMITTED였다. 다른 principal의 동일 OperationId는 별도 scope에서 독립 커밋하며 원 principal receipt를 누출하지 않았다.

**Caller hash zero authority:** 동일 payload + 임의 wrong hash는 ALREADY_COMMITTED, 변경 payload + 실제 저장된 원 RequestFingerprint는 COLLISION_REJECTED였다. 그 개선은 인정한다. 001의 잔여 실패는 별도의 구분자 ambiguity다.

ExpectedRevision=5/current=0은 durable ABORTED. exact retry는 ALREADY_ABORTED와 원 FailureReason을 반환했고, 동일 ID의 expected 변경은 COLLISION_REJECTED였다. 새 ID로 동일 expected=5/payload를 제출하면 당시 head=1을 다시 평가해 STALE_REVISION/새 ABORTED를 만들었고 재시도는 ALREADY_ABORTED였다. 새 ID + expected=0은 앞선 head=0에서 정상 성공했다. **Terminal result 의미는 안정적이지만 retry의 structured ExpectedRevision/CurrentRevision은 null이며 최초 응답과 byte-identical 결과 DTO는 아니다.** 원 실패 이유는 문자열로 유지된다.

### 4.2 Independent processes / SQLite locks

| Test | Separate OS processes | Outcomes | Canonical commit effects | Measured wall time |
|---|---:|---|---:|---:|
| Different IDs, same scope/head=0 | 25 | 1 SUCCESS / 24 STALE_REVISION | revision/history/receipt/event 각 1; operation/audit 25(24 ABORTED 포함) | 978.265 ms |
| Same ID / identical request | 12 | 1 SUCCESS / 11 ALREADY_COMMITTED | 1; raw UNIQUE 0 | 691.776 ms |
| External BEGIN IMMEDIATE writer lock | independent SQLite connection | STORAGE_BUSY_RETRYABLE | 0 | 5504.221 ms |
| Native SQLite table lock code 6 | QA observer holds real native reader then DROP conflicts | STORAGE_BUSY_RETRYABLE | 0 | 5111.722 ms |

5-second setting은 실제 전체 경과시간 5.000초 이하를 뜻하지 않는다. 연결/코드 실행 overhead를 포함하여 위 수치를 기록했다. LOCKED는 실제 provider code 6을 발생시킨 제한적 native lock fixture이며 일반 다중 프로세스 경쟁을 code 6으로 과장하지 않는다. IOException은 observer 기반 I/O-like failure다. 실제 disk full/device loss는 시험하지 않았다.

receipt/event INSERT constraint 및 pre-receipt IOException은 STORAGE_FAILURE이고 DB atomic subset이 모두 rollback됐다. initial aggregate constraint만 STALE_REVISION(0==0)로 오분류됐다.

### 4.3 Actual hard-kill boundaries

Python controller가 child PID/checkpoint를 확인한 뒤 OS process를 실제 종료했다. 실행 중 SimulatedCrashException만 catch한 시험과 구분한다. wrapper는 후보의 실제 journal/store/receipt/audit/event SQL 호출을 유지하고 전후 대기만 삽입했다. native-commit은 SQLite commit hook 내부 **commit 성립 전** 경계다.

| Hard-kill boundary | Durable state after kill | Recovery / exact retry |
|---|---|---|
| before lookup; transaction begun before CAS; after CAS; operation insert; receipt insert; audit insert; event insert; explicit BeforeCommit rollback 이전; native commit hook | canonical operation/revision/history/receipt/audit/event **0**; PREPARED 없음 | recovery가 phantom commit하지 않음; 실제 재시도로 한 번 커밋 |
| after tx.Commit before delivery | COMMITTED + revision/history/receipt/audit/event 모두 1 | 동일 stored receipt; revision 추가 없음 |
| external durable effect 이후, server ACK 이전 | COMMITTED; 동일 EventId 외부 효과=1, balance=7 | actual fixture consumer restart로 **효과=2 / balance=14** |
| server ACK durable 이후, cursor 이전 | COMMITTED + durable ACK; cursor 없음; 효과=1 | ACK 존재에도 다시 호출, **효과=2** |
| cursor write 직전 | COMMITTED, 효과=1 | **효과=2** |
| cursor durable 이후 | COMMITTED + cursor=1; 효과=1 | replay=0, 효과=1 유지 |

총 **14개 별도 kill 경계**를 보존했다. durable truth는 다시 연 별도 DB connection/table 조회로 판정했다. 최종 canonical revision이 한 번 증가했다는 사실을 외부 효과 exactly-once 증거로 사용하지 않았다.

### 4.4 Durable consumer / payload mismatch evidence discipline

`fixture` 모드는 **동결 후보 DurableTestConsumer**의 실제 ProcessEvent/OnAfterApplyEffectBeforeAck 경로에 별도 SQLite WAL/FULL ledger를 연결한다. 매 효과는 다른 DB에서 balance +7 및 ledger append를 transaction으로 durable commit한다. 그 후 kill하여 실제 외부 효과가 commit됐는지 restart에도 읽는다. observer에 QA dedup를 넣지 않았다. 후보가 구현한 game economy 효과라고 주장하지 않으며, 이름만 Durable인 fixture와 consumer 계약의 공백을 시험한다. callback이 duplicate에도 호출된다는 한계도 숨기지 않는다.

동일 process/consumer에 원 event를 적용한 뒤 **같은 EventId와 supplied fingerprint, 다른 PayloadJson**을 제출하면 accepted=true였다. 재계산 payload hash는 달랐으며 candidate semanticCount=1을 유지하더라도 **변조 package를 fail closed한 것은 아니다**.

`persistent` 모드는 별도 **QA contract example**이다. durable Accepted key `(ConsumerId, EventId)` + recomputed payload fingerprint + balance effect를 consumer DB의 같은 transaction에 넣는다. 실제 kill/restart에서 효과=1/balance=7이고 변조를 거절했다. 이는 interface가 이러한 consumer를 수용할 수 있음을 보여주지만 **Production candidate fix도, 004 CLOSED 근거도 아니다.**

### 4.5 Publication streams and startup

| Scenario | Actual result |
|---|---|
| Per-stream append | 검증한 CAS stream에서 Seq 1,2,3 단조 증가 |
| Consumer A ACK then consumer B lag/replay | A/B cursor 독립, 각 3 effects/balance=21; A ACK가 B suppress하지 않음 |
| Replay first event throws | 첫 pass cursor 진전 없음; 명시 retry에서 Seq 1→2→3 성공 |
| Replay first event returns false | **Seq2/3 ACK, cursor=3; Seq1 영구 누락**, retry replay=0 |
| Live Seq1 throws, subsequent live Seq2 succeeds | **cursor=2; Seq1 누락**, replay=0 |
| Normal fresh entrypoint | DB schema2/bootstrap 먼저, 이후 PIPELINE_READY / 7777 Listening / world clock. 통과 |
| Normal restart with pending event | consumer 미등록으로 replay=0, ACK/cursor 없음에도 **READY/Listening** |
| Startup manager with unavailable consumer | delivery exception을 삼킨 뒤 **READY=true**, pending event 그대로. 실제 normal Program에는 consumer injection 경로가 없으므로 별도 public startup API 시험으로 표시 |
| Startup manager with healthy consumer / 1 pending | ACK/cursor 1 이후 READY; 통과 |
| Startup manager with healthy consumer / 65 pending | **50 ACK, cursor50, 15 pending인데 READY=true** |
| Normal future schema | exit2, READY/Listening 없음; 통과 |
| Normal required OperationType column missing | **READY/Listening 성공**; 논리적 schema gate 실패 |

append log가 유지돼도 cursor가 선행 failure를 넘어가면 recovery query `Seq > cursor`가 누락 event를 다시 선택하지 못한다. per-consumer sequence-gap 처리 및 ordered dispatcher가 필요하다. 추가 background convergence scheduler/mandatory consumer registry는 실제 ordinary entrypoint에서 발견하지 못했다. **retention/compaction 구현 없음**; 안전한 보존/삭제 정책을 인증하지 않는다.

### 4.6 Logical schema / migration

- v2 wrong application_id, future user_version=999, missing required table는 fail closed했다.
- OperationType/ReceiptHash 필수 column 누락은 VALIDATED/READY였다. missing CHECK/FK, material EventId UNIQUE 누락, multiple active incarnations도 허용했다.
- **유효 SQLite schema**로 OperationRecords PK를 PrincipalId 단독으로 변경하고 `(PrincipalId,OperationId)` UNIQUE는 보존했다. integrity_check=ok / VALIDATED / READY. 첫 command는 성공, 같은 principal의 새 command는 잘못된 PK 탓에 STORAGE_FAILURE였다.
- EventId UNIQUE만 빠진 별도 **integrity_check=ok** fixture도 VALIDATED/READY였다. 초기 writable_schema PK/UNIQUE 제거 시험은 orphan internal index로 malformed DB를 만들었고 reject됐다. 그 초기 fixture를 논리적 constraint 검증 통과/실패 증거로 쓰지 않고, 위 유효 fixtures로 대체했다.
- 일반 scope index 누락도 허용됐으나 이것만으로 원자성 위반을 주장하지 않는다. correctness에 영향을 주는 unique/singleton/schema 구조와 구분한다.
- actual REV0 committed DB의 SQLite backup copy를 v1→v2 변환하면 **receipt/operation/history/aggregate/audit/outbox가 삭제**돼 empty v2가 됐다.
- 같은 committed v1 DB에 incompatible ConsumerCursors view가 남아 있으면 migration이 schema2 변경/삭제를 commit한 뒤 ValidateSchemaStructure에서 예외를 냈다. **실패 후에도 schema2와 deleted canonical truth가 남았다.**
- foreign application_id=42/user_version=0 DB는 migration으로 WARE에 편입됐다. foreign app의 상위 schema라서 거절한 v2 case와 구분한다.

### 4.7 Incarnation / receipt / durability

순차 rotation은 새 active incarnation을 durable 보존했고 normal restart는 spuriously rotate하지 않았다. strict old-incarnation request는 INCARNATION_MISMATCH였다. old receipt 조회는 old incarnation을 유지했으며, current-incarnation으로 같은 completed operation을 조회하면 historical receipt를 반환하되 새 mutation은 하지 않았다. 새 ID + current expected revision은 정상 평가됐다.

그러나 **read-before-BEGIN race는 실패**했다. actual active SELECT 완료 직후 QA-only native SQLite PROFILE observer로 executor를 정지하고, 다른 OS process가 actual RotateStoreIncarnation을 commit한 뒤 executor를 재개했다. 새 active=`c571567e46aa400bbc404897a55dbc78`인데 old request는 SUCCESS/revision1, receipt/operation/event incarnation=`563936e4113a46ccb0d5feaa7647e01f`로 커밋됐다. observer는 returned value/SQL/business logic을 변경하지 않았다. request의 StoreIncarnationId가 null/blank이면 check가 생략되는 점도 존재하므로 미래 canonical API에는 필수 fencing context를 정의해야 한다.

pool 시험은 20회 동일 native handle 재사용 시 이전 connection의 synchronous를 NORMAL로 일부러 바꾸어 닫고 다음 CreateOpenConnection에서 FULL로 되돌아오는 것을 확인했다. NORMAL은 **QA 오염 fixture**이며 후보 canonical default는 FULL이다. WAL/FULL 설정을 physical power-loss proof로 승격하지 않는다.

receipt는 5개 culture(en-US, ko-KR, tr-TR, ar-SA, de-DE)와 5개 process-local time zone fixture(UTC, Korea, Turkey, Arab, W. Europe)에서 동일 hash/epoch/identity를 유지했다. Windows `TZ` 환경 변수만 바꾸는 최초 시험은 실제 zone을 바꾸지 못했다. 후속 시험은 **process-only TimeZoneInfo.Local cache fixture**로 actual Local zone을 바꾸어 측정했다. 시스템/사용자 time zone은 바꾸지 않았고 candidate code도 patch하지 않았다. publication 상태 필드는 immutable receipt에 없었다.

## 5. Executor overload / shutdown

| Measurement | Delayed active DB writer | Worker not yet scheduled / thread-pool starvation fixture |
|---|---:|---:|
| Submitted / accepted in-memory tasks | 1202 | 1202 |
| Queue configuration / admission rejection | Unbounded / 0 | Unbounded / 0 |
| Backlog at observation | active1 + queued1201 이상 | queued1202 |
| Managed memory delta | 40,075,864 bytes | 40,006,440 bytes |
| Working set delta | 56,320,000 bytes | 50,102,272 bytes |
| Dispose duration | 1001.832 ms | 1008.584 ms |
| After allowing progression | completed1202, pending0; 첫 observer crash exception1 포함 | **completed0, pending1202, caller task fault0** |
| Candidate writer state | 진행 후 처리 | **Faulted ObjectDisposedException** at `_cts.Token` |

payload는 대부분 약16KiB이며 memory 값은 해당 fixture의 차이값으로 최종 workload capacity/SLO가 아니다. Channel Reader.CanCount=false이므로 `Count=-1`을 실제 high-water 값으로 해석하지 않는다. 제출/실행 대기 상태로 확인한 backlog lower bound를 위에 기록했다.

첫 warm-writer case는 Dispose가 1초 후 반환해도 worker 재개 후 모두 처리됐다. 그것을 request loss로 보고하지 않는다. 두 번째 case는 **process-local ThreadPool max1과 선행 blocker**로 후보 Task.Run의 시작을 지연했다. Dispose가 CTS를 먼저 폐기했고 blocker 해제 후 실제 writer가 `_cts.Token` 접근에서 faulted. accepted request 1202개의 TCS에 success/failure/cancellation이 전달되지 않았다. DB commit0이며 수락은 durable commit/ACK와 다르다. nonetheless async caller가 영구 대기하고 무제한 ingress에 backpressure가 없다는 결함은 재현됐다.

## 6. New defect proposals

### QA-PIPELINE-013 — Unbounded admission / shutdown abandons accepted promises

- **Severity:** High
- **Requirement:** 이번 work order §7; SRS-NFR-004/006 기반 operation lifecycle.
- **Location:** [Coordinator:81](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:81), [Coordinator:137](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:137), [Coordinator:489](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:489).
- **Reproduction:** queue-starved-proof: writer scheduling을 늦추고 1202개 제출 → Dispose → blocker 해제.
- **Expected:** bounded admission/backpressure 및 수락한 각 요청에 drain 결과 또는 명시 cancelled/shutdown/unknown 결과. resources는 worker가 종료한 뒤 dispose.
- **Actual:** Unbounded acceptance, 약40MB managed 증가, worker ObjectDisposedException, pending1202 / completed0.
- **Root cause:** 1-second wait timeout을 무시하고 CTS를 폐기한다. outer writer-loop fault/cancellation이 outstanding TCS를 완료하지 않는다.
- **Required fix:** immutable bounded ingress, 명시 shutdown state, async drain/cancel completion 및 worker failure 관측. 미커밋 요청의 종료 결과와 already-committed ambiguous 결과를 구분.
- **Evidence:** `queue-delay`, `queue-starved-proof`.

### QA-PIPELINE-014 — Cursor jumps over unaccepted stream event

- **Severity:** High
- **Requirement:** work order §6 ordered publication; SRS-NFR-004/006.
- **Location:** [Coordinator:408](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:408), [Coordinator:463](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:463), [Coordinator:472](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:472).
- **Reproduction:** Seq1 false 또는 live Seq1 throw → Seq2/3 success → recover.
- **Expected:** cursor는 해당 consumer가 연속적으로 처리한 prefix만 표시. 선행 실패는 명시 repair/disposition 전까지 후속 semantic order를 건너뛰지 않음.
- **Actual:** cursor3/2, Seq1 미적용, retry replay0.
- **Root cause:** live direct delivery는 pending predecessor 검사 없음. replay false branch도 다음 event로 계속 진행. SaveCursor는 max advancement.
- **Required fix:** consumer/stream별 ordered dispatch와 gap-aware cursor; false/exception의 명시 failure contract. 필요한 경우 repaired/skipped decision도 durable policy로 정의.
- **Evidence:** `stream-false-first`, `live-stream-gap`; 원래005/007과 연결하고 그 ID를 바꾸지 않음.

### QA-PIPELINE-015 — Migration destroys canonical history and commits before validation

- **Severity:** Critical — 실제 probe durable truth loss; gameplay data loss를 재현했다는 의미는 아님.
- **Requirement:** work order §1/2 logical schema/partial migration; SRS-NFR-006/012.
- **Location:** [Migration:48](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:48), [Migration:75](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:75), [Migration:228](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:228), [Migration:55](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:55).
- **Reproduction:** committed REV0 v1 DB backup을 Initialize/Validate; 추가로 incompatible ConsumerCursors view fixture.
- **Expected:** supported durable state/receipt/audit identity를 보존하는 검증된 conversion, 또는 사전 fail closed/explicit isolated-probe reset. 실패 시 기존 durable truth 유지.
- **Actual:** 완료 operation/receipt/history 삭제. partial validation failure 후에도 삭제된 schema2가 남음. foreign app v0도 WARE로 편입.
- **Root cause:** noninitial migration은 DROP/recreate; 후속 검증은 tx.Commit 뒤. foreign application guard가 version<2 conversion 이전에 없음.
- **Required fix:** non-destructive migration/backup+verified migration contract 또는 공식 legacy rejection policy. reset이 의도라면 disposable fixture에만 격리하고 Production startup에서 암묵 수행 금지. foreign DB reject 및 validation-before-publication.
- **Evidence:** `legacy-v1`, `legacy-partial-migration`, `foreign-app-v0`; 원래008과 연계.

### QA-PIPELINE-016 — Store incarnation fencing TOCTOU

- **Severity:** High
- **Requirement:** work order §5; SRS-NFR-004/006/007.
- **Location:** [Coordinator:185](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:185), [Coordinator:195](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:195); [DatabaseContext rotation](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/SqliteDatabaseContext.cs:138).
- **Reproduction:** actual active incarnation SELECT 후 대기 → separate process rotation durable commit → old request 재개.
- **Expected:** rotated store의 current mutation은 old context를 거절; historical receipt만 read-only 조회 가능.
- **Actual:** old incarnation operation/receipt/event가 새 active store에 SUCCESS로 commit.
- **Root cause:** read/check가 canonical writer transaction 밖에 존재하고 rotation과 원자적 fencing이 없음.
- **Required fix:** incarnation validation과 commit을 같은 writer lock/transaction boundary에서 보장; rotation에도 동일 fencing discipline. 요청 incarnation 필수 여부를 명시.
- **Evidence:** `incarnation-race`; 단순 순차 rotation PASS를 경쟁 경계 PASS로 확대 금지.

### QA-PIPELINE-017 — Mutable request changes actor/target after admission

- **Severity:** High — internal API integrity; remote identity bypass를 주장하지 않음.
- **Requirement:** work order §2 operation identity / §7 admitted command; SRS-NFR-004/007.
- **Location:** [Coordinator:42](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:42), [Coordinator:125](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:125), [Coordinator:143](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:143).
- **Reproduction:** delayed writer 뒤 P_ORIGINAL/ORIGINAL_SCOPE request enqueue → caller가 같은 object의 principal/scope/payload 변경 → writer 실행.
- **Expected:** admitted command의 validated identity/target/payload가 불변.
- **Actual:** **P_CHANGED/CHANGED_SCOPE**의 receipt와 canonical mutation 생성.
- **Root cause:** queue task가 mutable caller object를 그대로 보관하며 processing 때 fingerprint/permission context를 읽음.
- **Required fix:** admission에서 complete immutable command/envelope 복사 및 validated principal binding; downstream shared reference mutation 금지.
- **Evidence:** `queue-delay.metrics.mutableResult`, queue-delay DB.

### QA-PIPELINE-018 — Dangerous local test controls ship in ordinary Release

- **Severity:** Medium — packaging/operational isolation; remote exploit 주장이 아님.
- **Requirement:** work order §8 Release/test-surface isolation.
- **Location:** [Program:21](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:21), [Program:49](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:49), [Server csproj](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/WarEconomy.Server.csproj:1).
- **Reproduction:** exact Release `--test-pipeline-e1 --db <QA-owned DB>`로 19개 mutation test 실제 실행. source의 `--crash-worker --db/--scope/--op/--principal/--fault`는 probe execution 및 Environment.FailFast 분기.
- **Expected:** ordinary canonical server deployment와 destructive test/control surfaces 사이에 명시적 packaging/operator boundary.
- **Actual:** Release에 TestBattery/DurableTestConsumer/InternalProbeTestSurface/fault types 모두 포함; local CLI로 활성화 가능, 별도 test build/profile/admin opt-in guard 없음.
- **Root cause:** SDK default compilation 및 unconditional early CLI branches.
- **Required fix:** test executable/build separation, 또는 Master가 승인한 explicit test profile + isolated DB + privilege/operator guard. Production operator의 OS 권한과 remote packet 권한을 혼동하지 말 것.
- **Evidence/limit:** runtime reflection `metadata.testTypes`, actual `release-battery`, Program static routing. explicit existing --db를 무조건 삭제한다고 주장하지 않는다. default test DB cleanup과 explicit DB를 구분했다. crash-worker branch는 static evidence이며 이 보고서에서 별도 native CLI FailFast run을 실행했다고 주장하지 않는다.

## 7. Gameplay isolation / no gameplay mutation guard

actual PacketHeader/TcpNetworkServer dispatch에 PIPELINE_PROBE_CAS route가 없는 것을 정적으로 확인했다. 실제 normal Release socket에 undefined header65535 + probe JSON을 보낸 뒤 REMOTE_ATTACK / REMOTE_SCOPE operation/aggregate가 생성되지 않았다. 이는 단독 helper의 always-false 결과보다 강한 증거지만 모든 malformed/network attack을 exhaustive 인증한 것은 아니다.

probe execution은 ProbeAggregates/History, OperationRecords, CommitReceipts, AuditRecords, PublicationEvents, Consumer ACK/cursor 및 incarnation metadata에 한정된다. 실제 Settlement material, CommittedSettlementStateRevision, ArtifactBaseStateRevision, EntityId, Tax/Trade/Tactical state로 mutation route를 추가하거나 실행하지 않았다. ordinary Server의 기존 default settlement seed/clock 초기화는 기존 startup behavior이며 probe의 gameplay effect로 분류하지 않았다. **network probe isolation은 PASS for this exact route; Release local test-control isolation은 018과 별도다.**

## 8. Evidence and reproducibility

Evidence root: `C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV1-20261003`

- [Independent results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/Evidence/results.json): 모든 독립 run의 typed result, timings, durable table snapshots, process checkpoint/PID/exit code, consumer ledger 및 freeze 결과. 본문의 backtick key로 찾을 수 있다.
- [source-provenance.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/source-provenance.json) / [freeze-before.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/freeze-before.json) / [package-versions.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/package-versions.json).
- [QA Harness source](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/Harness/Program.cs): exact candidate API/SQL wrappers, actual consumer callback, queue observer, native commit/profile hooks. Production IL patch 없음.
- [Main process/kill controller](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/run_checks.py); [Normal entrypoint/CLI controller](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/startup_checks.py); [Follow-up boundary checks](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/followup_checks.py); [Valid logical-schema fixtures](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/schema_valid_fixtures.py).
- [Independent Release battery JSON](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/Evidence/release-battery.json); [Normal pending startup log](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/Evidence/pending.normal.log); [Malformed-column normal startup log](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV1-20261003/Evidence/missing-column.normal.log).

Controller는 evidence fixture 이름이 이미 있으면 새 DB 생성을 거절한다. 같은 root에 무작정 재실행/덮어쓰지 말고 다음 검증은 새 QA evidence directory에 수행해야 한다. 기존 Production DB를 시험 입력으로 직접 쓰지 않았다. legacy fixtures는 QA REV0 DB의 SQLite backup이며 active WAL file 단순 복사로 만든 것이 아니다.

## 9. Developer battery assessment / missing tests

exact Release battery **19/19 PASS**를 독립 재현했다. 그렇지만 아래 test scope가 보고서의 표현보다 좁다.

| Developer test | Actual code scope | Missing adversarial evidence |
|---|---|---|
| E1_05 IndependentProcessRace | Test_05에서 Task.Run; 별도 OS process 아님 | 독립 writer concurrency 및 locking; 본 QA는 25 OS processes로 보완 |
| E1_08 Hard kill | SimulatedCrashException을 in-process catch | actual OS termination / native commit boundary; 본 QA 14개 경계 |
| E1_09 Consumer crash/restart | 같은 DurableTestConsumer instance/dictionary를 계속 사용 | 새 process dedup persistence, durable nontrivial effect, payload recomputation |
| E1_12/13 Normal startup | direct PipelineStartupManager API 호출, 작은 pending set | normal entrypoint consumer wiring, mandatory failure disposition, multiple-page convergence |
| E1_14 Strict schema | future version / missing table 중심 | required columns / valid PK, UNIQUE, FK, CHECK / partial migration / foreign app |
| E1_16 Timezone/culture | cultures 변경 중심 | 실제 Local zone 차이; 본 QA process-only zone fixtures |
| E1_18 Dispatcher isolation | always-deny helper 호출 | 실제 PacketHeader/dispatch + wire; 본 QA 좁은 unknown-header 경로로 보완 |

추가 필수 regression: delimiter-separated envelope ambiguity, terminal journal transition denial, external durable acceptance/effect atomicity, false/throw stream gap, permanent consumer disposition, >50 startup pending, v1 history-preserving migration/rejection, incarnation read/rotate/commit race, overloaded delayed writer drain 및 never-started worker Dispose, immutable admitted command, packaged Release test surface guard.

## 10. Final recommendation to Master

**FAIL.** 검증된 단일 SQLite commit subset, process CAS, effective FULL policy, canonical receipt 구조는 유지할 가치가 있다. 하지만 completed-operation identity / publication / readiness / migration / fencing / lifecycle 실패를 해결하기 전 이 candidate를 real gameplay-domain E2 foundation으로 승격하지 말 것을 권고한다.

우선 순서는 (1) destructive migration 및 logical schema/readiness, (2) operation envelope serialization/immutable admission/incarnation transaction fence, (3) durable consumer contract 및 stream gap/ACK convergence, (4) bounded admission/async shutdown, (5) Release test-control boundary와 독립 failure tests다. callback 또는 generic two-phase commit을 제안해 actual consumer contract를 대체하지 않는다.

CLOSED 권고 002/009/010/012는 이 probe 범위에 한정한다. PARTIAL/잔여 실패 및 신규 결함의 최종 원장 등록/종결과 acceptance 결정은 Master가 수행한다. 이 보고서 제출 후 추가 구현을 시작하지 않는다.

## Appendix — exact changed-source manifest

| Source | SHA-256 | Match |
|---|---|---|
| [PipelineTransactionCoordinator.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs) | `5F761BE57316A81680EF148F38B3C1B9A9B6074F721D3B7B902AA2F792F808A1` | YES |
| [SqliteDatabaseContext.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/SqliteDatabaseContext.cs) | `384709312E389B22C4F5A34025F574B20E87114655BB40B011632795B8BE1624` | YES |
| [PipelineSchemaMigration.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs) | `3C10FE553549AD545054D6CC1FC10EF885B8B8E99C79BDD8F8EE7C2BA7C96FE2` | YES |
| [PipelineProbeModels.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs) | `B898A0DA9464F94D7771CFE152E0CD468702B06D3A56FCE349EE584240FF35BA` | YES |
| [RecoveryReconciler.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs) | `460A249834A1D78C335BBFB5D3029ED1D10042F1AE2E74FA4CAD8545F6BFBEE1` | YES |
| [InternalProbeTestSurface.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Security/InternalProbeTestSurface.cs) | `3B81699D95F45C920DEA1764B223196DA7560A08B226E231DF3E59B2CF8FA9A3` | YES |
| [AuditLogRepository.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/AuditLogRepository.cs) | `5A885964386BE2587A859C5345A3D55593E4499E924C546C8E7F6FB89A0387AE` | YES |
| [CommitReceiptRepository.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/CommitReceiptRepository.cs) | `BC13BE5F360642CC5CBC53B36A3776E3B9B35658D0BFDD044BEEE18FBEEB9AA2` | YES |
| [OperationJournal.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/OperationJournal.cs) | `4050C7788F48E62BD00E122CDA9528050C75B95A7E9898E868C59E80CE73CFA5` | YES |
| [ProbeAggregateStore.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/ProbeAggregateStore.cs) | `BCBC7203281ECE909AF02A8343AB4BF932F6B816928BC5A39F3AC49AA28CCE29` | YES |
| [PublicationEventStore.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/PublicationEventStore.cs) | `1780F4074B46EEF844D1C3E2652DAEF36D6A9251EA1659207827D53F9FB7AC22` | YES |
| [DurableTestConsumer.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Testing/DurableTestConsumer.cs) | `2BD955246DED26780DACF5EA4AA85F183D45ECBF28A0874AA9690218411D5873` | YES |
| [PipelineE1TestBattery.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Testing/PipelineE1TestBattery.cs) | `00A06D4BB00E1562DDCD347AB0E0B6D7F8A2C90A7332F98C58AE5D2C679FA079` | YES |
| [Program.cs](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs) | `2753E74BEACD37FC5E8A2C27A027868A78E65DB0C0A10B74ABB97998DFF10915` | YES |
