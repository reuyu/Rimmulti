# QA Production Transaction Pipeline 01 — REV3 Independent E2

```yaml
Work Package: WP-QA-PROD-TRANSACTION-PIPELINE-01-REV3
Reviewer: GPT-6.1 Sol / Independent QA & Architecture Reviewer
Date: 2026-10-03
Target: Production_Transaction_Pipeline_Slice_01_REV3.md
Verdict: FAIL
Production modification or rebuild: NONE
Production freeze: 353 files before / 353 files after / 0 changes
Master defect ledger or architecture status modified: NO
```

## 1. 판정과 범위

**최종 판정: FAIL.** 동결 Release DLL에서 다음 5개 결함군을 독립 재현했다. QA-PIPELINE-001: 손실 있는 canonicalization 및 JSON ambiguity. 007: 불완전한 cross-table consistency와 정상 종료의 coordinator lifetime. 008: 의미가 다른 CHECK/index를 승인하는 schema signature. 013: Dispose 반환 후 살아 있는 Worker 및 후속 commit. 019: 서로 다른 유효 identity가 같은 ReceiptId/EventId를 생성한다.

수정된 부분도 인정한다. Production-opened connection을 통한 terminal SQL 공격 12개는 모두 차단됐다. constraint/BUSY/LOCKED/I/O-like 실패는 잘못된 STALE로 변환되지 않았다. 누락 incarnation은 INVALID_REQUEST이고, 별도 프로세스 rotation 이후 기존 요청은 거절됐다. 실제 OS process CAS/같은 ID/동일 stream 경쟁 및 강제 종료 후 원자성도 아래 범위에서 통과했다. 따라서 **003/011/016은 좁은 범위의 해결을 권고**한다.

이 문서는 closure **권고**다. Master의 상태를 변경하지 않았다. 거래·inventory·tax·Tactical·ownership·EntityId 이전을 구현하거나 검증 범위로 확장하지 않았다. P1 publication log의 원자성을 external consumer exactly-once로 해석하지 않았다.

## 2. Exact provenance와 방법

증거 루트: [PIPELINE01-REV3-20261003](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV3-20261003).

Production 전체를 먼저 동결하고 실제 Release package를 QA `Candidate`로 복사했다. QA harness만 빌드하여 **해당 DLL을 직접 reference**했다. coordinator/SQLite repositories의 실제 구현을 사용했다. fault observer는 repository 호출을 위임하면서 barrier 또는 I/O-like 예외를 추가한다. SQLite native commit/WAL hook은 반환 시점만 지연한다. 성공 판정, commit, receipt를 observer가 대신 생성하지 않는다. SQL/schema tamper는 QA-owned DB에만 적용했다.

### 바이너리와 환경

| 항목 | 실제 검증값 |
|---|---|
| 원본 Server DLL | `C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.dll` |
| Server DLL SHA-256 | `8F140D23F8D1BD90A00F3F5B9000C1E01EA0D3CD5AB0615A967635E7668F0209` |
| Server DLL MVID | `19f86704-dcba-42bd-85a3-bda2ff1ccb78` |
| Server.exe SHA-256 | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |
| Server.pdb SHA-256 | `5B6E8FED585CA2998CE8E0A8E62F63471ABC4762167612ECE4C0FFE61967D8BF` |
| Common DLL SHA-256 | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` |
| Common DLL MVID | `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` |
| Release manifest SHA-256 | `AAB660794669FEE38A95D2F047AED68D110E841B83C1F4601C5955457031E304` |
| E1 result JSON SHA-256 | `DE00CAFD0FD37658E9D74F1E4D54B6FE5683A4ABF84DFB37A5BB359F7FBFCC34` |
| Native win-x64 SQLite DLL SHA-256 | `DCCBABB2BC7E7D4302C44D9CE41B70721A7D0914FA4D289E2F340D39766AD102` |
| QA loaded Server DLL | `C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV3-20261003\Harness\bin\Release\net8.0\WarEconomy.Server.dll` — 위 SHA/MVID와 일치 |
| QA loaded Common DLL | 같은 QA harness directory — 위 SHA/MVID와 일치 |
| Runtime / QA SDK | .NET 8.0.10 / SDK 10.0.201 |
| Packages | Microsoft.Data.Sqlite 8.0.10; SQLitePCLRaw 2.1.6; Newtonsoft.Json 13.0.3 |
| Native SQLite | 3.41.2 |
| application_id / schema | 1463898693 (`WARE`) / 4 |

Release manifest의 **32개 파일 모두 SHA/byte count 일치**. Release directory에서 `.db*`, test-name, `.log`, `.tmp` residue는 0개였다. Source candidate를 재빌드하지 않았다. Server CodeView GUID와 PDB GUID는 `89cd8037-988e-4ab1-b1e2-a8899cd714df`로 일치하며 PDB document 20개의 source checksum을 실제 파일과 대조해 모두 일치했다. 이는 동결 artifact/source의 일치 증거이며, QA가 Production build를 다시 했다는 의미가 아니다.

### 변경 소스의 실제 SHA-256

경로 기준: `WarEconomyMod/Source/Server/`.

| 파일 | SHA-256 |
|---|---|
| `Pipeline/Models/PipelineProbeModels.cs` | `E4D0A914EDB7712A1F8ED4A4E0BB2BD1751DCDF523B11F2799FC60DA574DABB3` |
| `Pipeline/Data/SqliteDatabaseContext.cs` | `AD83A9747ADE1D078B2D672EFDDF34E60F5B5A902DD672BF567500215977B903` |
| `Pipeline/Data/Migrations/PipelineSchemaMigration.cs` | `3F05A85A4E9EA0F2A41C2A32A12C76666E56FDA83E33039CC2F9724F48D1E06C` |
| `Pipeline/Storage/ProbeAggregateStore.cs` | `45D9B256A1E6ADF46BA2077D8D35148BC81E5F402FAF448A08DA665DFF661B86` |
| `Pipeline/Coordinator/PipelineTransactionCoordinator.cs` | `1CD4FBFDDBE6FDCE33E6CF546FD8A38228F51399E4289C9B7832CC8BE5FCB1E7` |
| `Pipeline/Recovery/RecoveryReconciler.cs` | `89993EB4D6431615CD02056078C0790AE1ACB0803CF824326D68FC0376D3ED4E` |

`freeze-before.json`, `freeze-after.json` 및 periodic/final comparison에서 Production 353개 파일의 추가·삭제·내용 변경은 0개다. 결과 JSON, frozen copy manifest, QA observer/harness hashes는 증거 directory에 보존했다.

## 3. 독립 측정 요약

| 시험 | 실제 결과 | 판정 |
|---|---|---|
| 25 independent OS process, 같은 expected revision | 1 SUCCESS / 24 STALE_REVISION | PASS |
| 12 independent OS process, 동일 identity/envelope | 1 SUCCESS / 11 ALREADY_COMMITTED | PASS |
| 동일 stream, 8 rounds × 6 OS process | 8 SUCCESS / 40 STALE; revision/Seq 1..8; paginated read/restart 유지 | PASS |
| terminal SQL, 2 states × 6 SQL shapes | 12/12 차단; SQLite error 19; 논리적 DB unchanged | PASS |
| raw malformed UTF-16, 3 shapes × 9 locations | 24 INVALID_REQUEST / **JSON key 3 SUCCESS** | FAIL |
| overflow ±1e309 / huge integers | INVALID_REQUEST; 해당 durable operation 없음 | PASS |
| under-scale/high-precision decimal | 서로 다른 값이 동일 canonical 값과 기존 success로 합쳐짐 | FAIL |
| schema mutants | 28개 중 26 거절 / **2 READY** | FAIL |
| cross-table consistency mutants | 26개 중 17 거절 / **9 READY** | FAIL |
| full ingress 1,205 submissions | 1 in-flight + 1,000 queued + 204 즉시 BUSY; unfinished caller 0 | admission PASS |
| full-queue shutdown | 약 6.03초 후 Dispose 반환 시 Worker alive; 이후 commit 가능 | shutdown FAIL |
| native DB lock | lock 38.377초; Dispose 이후 25초 관측까지 Worker alive | FAIL |
| 정상 Main의 quit 경로 | Main 반환 후 writerAlive=true, isDisposed=false, ready=true | FAIL |
| incarnation null/empty/blank | 3/3 INVALID_REQUEST | PASS |
| 별도 process admission → rotation | old admitted request INCARNATION_MISMATCH | PASS |
| ambiguous derivative identity, 4 pairs | first SUCCESS / distinct second STORAGE_FAILURE, 반복해도 실패 | FAIL |
| 실제 legacy v1/v2/v3 | fail closed, 모든 논리적 row/schema 보존 | PASS |
| 정상 server에 probe network frame | TCP 수신, probe canonical row 0; transport route 없음 | narrow isolation PASS |

같은 ID/key 및 valid envelope의 exact retry와 receipt identity는 확인했다. normal executable은 QA copy에서 실행했고 7777 listener의 기존 owner가 없음을 먼저 확인했다. 생성한 QA 프로세스만 종료했다.

## 4. OPEN 권고 결함

### QA-PIPELINE-001 — High — lossless input identity 미충족

**Location:** [PipelineProbeModels.cs:424](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:424), `CanonicalizeJson`, `NormalizeToken`(449), `FormatCanonicalDecimal`(503).

**Expected:** 유효하게 수락한 서로 다른 exact numeric value를 같은 operation identity로 합치지 않는다. 정확히 표현할 수 없는 입력은 INVALID_REQUEST이며 durable operation을 만들지 않는다. invalid UTF-16은 JSON key까지 거절한다. 계약 없는 duplicate-key collapse는 금지한다.

**Actual numeric reproduction:** 각각 별도 DB에서 같은 `(P, OP)`를 다음 두 payload로 실행했다.

| 첫 payload | 두 번째 payload | 실제 canonical / retry |
|---|---|---|
| `1e-29` | `-1e-29` | 둘 다 `0.0`; SUCCESS → ALREADY_COMMITTED |
| `1e-40` | `0.0` | 둘 다 `0.0`; SUCCESS → ALREADY_COMMITTED |
| `1.00000000000000000000000000001` | `1.00000000000000000000000000002` | 둘 다 `1.0`; SUCCESS → ALREADY_COMMITTED |
| `0.123456789012345678901234567891` | `0.123456789012345678901234567892` | 둘 다 `0.1234567890123456789012345679`; SUCCESS → ALREADY_COMMITTED |

`-1e-40`도 `0.0`으로 수락됐다. `1e-28`/`2e-28`, Decimal 최대치 주변의 두 representable 값은 구분됐다. `0`/`-0`은 같지만 integer `0`/float `0.0`, integer `1`/float `1.0`은 서로 다른 fingerprint다. `1.0`/`1e0`은 같았다. 이 숫자 spelling 정책의 불일치는 관측 사실이며, **FAIL의 직접 근거는 서로 다른 수학적 값의 합침**이다.

**Actual Unicode:** .NET request에서 직접 high-only `D800`, low-only `DC00`, reversed `DC00 D800`를 구성했다. principal/op/type/scope/profile/config/incarnation/JSON value 24개는 거절되고 durable operation도 없었다. 같은 3개 값을 JSON property name에 넣으면 모두 SUCCESS이고 3개 operation이 저장됐다. `NormalizeToken`은 string value만 검사하고 `prop.Name`을 검사하지 않는다.

**Actual JSON ambiguity:** `{"a":1,"a":2}` → `{"a":2}`, nested `{"x":{"a":1,"a":2}}` → `{"x":{"a":2}}`는 모두 SUCCESS → ALREADY_COMMITTED였다. array 내부 duplicate object도 수락됐다. 추가로 `{"a":1} {"evil":2}`는 첫 root만 읽고 `{"a":1}` 재시도를 ALREADY_COMMITTED로 처리했다. 뒤쪽 root/data를 검사하지 않는다. candidate 문서에는 이를 허용하는 duplicate-key/multiple-root 의미 계약이 없다.

**Root cause:** Decimal reader가 validation 전에 rounding/underflow하고, 기본 JObject loading은 duplicate key를 덮어쓴다. 첫 JToken 이후 EOF 검증도 없다. length-prefix fingerprint 자체가 제대로 분리되어도 그 전에 정보가 유실된다.

**Required fix:** exact numeric token 의미를 보존하거나 representability를 원본과 대조해 비정확 수치를 거절한다. JSON property name에도 UTF-16 validation을 적용하고, duplicate key와 추가 root/content는 명시 계약이 없는 한 fail closed 한다. overflow만 테스트하는 것으로 001을 닫지 말 것.

Evidence keys: `input-boundaries`, `input-truth`, `canonical-0..6-first/retry`, `fingerprint-complete`, `invalid-json-name-durable-restart`.

### QA-PIPELINE-007 — High — startup consistency와 service ownership 미완결

**Locations:** [RecoveryReconciler.cs:167](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:167), event verification(202), aggregate/history check(232), StartupManager(280); [Program.cs:103](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:103).

누락 receipt/event/history/audit, 잘못된 receipt hash/revision/principal/op, payload hash, orphan receipt/event, ABORTED+success rows 등 **17개 negative는 거절**했다. 하지만 다음 **9개 mutation은 STARTUP READY**다.

| mutation | 승인된 모순 / 원인 |
|---|---|
| receipt ScopeId → OTHER | history와 INNER JOIN이 없어져 hash/revision 검사를 통째로 건너뜀 |
| event EventType → WRONG | payload만 검사하고 operation effect type을 비교하지 않음 |
| event StreamId → OTHER | operation target와 stream을 대조하지 않음 |
| event Seq → Seq+100 | history/revision 대응 및 gap을 확인하지 않음 |
| event incarnation → OTHER | 해당 operation/receipt incarnation과 대조하지 않음 |
| aggregate 전체 삭제 | query가 aggregate에서 시작하므로 orphan history/committed scope를 보지 못함 |
| audit scope/revision/details 변경 | audit의 존재만 확인하고 semantic fields를 검증하지 않음 |
| 동일 operation의 duplicate event | 다른 EventId/Seq면 physical UNIQUE를 만족; logical cardinality 검사 없음 |
| 동일 operation의 duplicate receipt | 다른 ReceiptId와 올바르게 다시 계산한 hash면 READY; logical cardinality 검사 없음 |

잘못된 hash를 그대로 가진 duplicate receipt는 실패했지만 **hash를 정확히 재계산한 duplicate receipt는 통과**했다. 이는 logical duplicate를 검사한 것과 hash 검사에 우연히 걸린 것을 구별한다. receipt scope/event type/stream/audit/duplicate receipt/event는 정상 Server.exe에서도 실제 PIPELINE_READY와 **7777 listen**을 재현했다.

**Lifetime:** StartupManager가 실제 coordinator를 만들고 writerAlive=true인 것은 인정한다. 정상 executable `quit`은 exit 0이다. 그러나 원본 DLL의 실제 `Program.Main`을 QA process에서 호출하고 `quit`을 넣은 뒤 같은 `ActiveCoordinator`를 관측하면 writerAlive=true, `_isDisposed=false`, IsPipelineReady=true다. QA observer가 **관측 후 별도로 Dispose하여 정리**했다. candidate의 quit 경로는 tick/network만 stop하며 coordinator를 소유·정리하지 않는다. 단순 process exit가 service-lifetime disposal을 대체하지 않는다.

**Required fix:** 검증을 일대일 대응과 semantic field 일치에 기반해 구성하고, JOIN에서 탈락한 row도 fail closed 한다. committed effect와 receipt/history/event/audit의 target/revision/incarnation/type 관계, cardinality, orphan 방향 양쪽을 검증한다. 정상 종료 owner가 startup의 **같은 coordinator**를 dispose/join하고 readiness도 닫아야 한다.

Evidence keys: `consistency-*`, `normal-consistency-*`, `actual-main-shutdown-lifetime`, `service-coordinator-lifetime`.

### QA-PIPELINE-008 — High — schema signature가 semantic schema identity가 아님

**Location:** [PipelineSchemaMigration.cs:668](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:668), `ComputeCanonicalSchemaDescriptor`(716), index descriptor(790), CHECK normalization(829).

Python SQLite metadata로 7개 table의 column/PK/FK/index/trigger/CHECK를 독립 재구성했다. fresh v4 signature는 제출값 `0B9C2C39AA681138DD671F181299BBE66ED1660E50FDCB3D1FCE831DCFED7F56`와 일치한다. **matching signature 자체가 의미 보존 증명은 아니다.**

PK order/type/nullability/UNIQUE column 및 order/FK source·target·action/CHECK 확장/no-op trigger/RAISE lookalike `WHEN 0`/index column·order/active incarnation 등 일반적인 26개 mismatch는 거절했다. 특히 superficially similar RAISE trigger는 확실히 거절됐다. 다음 두 mismatch는 승인됐다.

1. OperationRecords CHECK를 `State IN ('committed', 'aborted')`로 변경한다. schema descriptor와 CHECK verifier가 SQL 전체를 lower-case 처리하여 원래 uppercase literal과 동일하게 취급한다. SQLite TEXT CHECK의 실제 의미는 다르다. **STARTUP READY → 정상 EXE listen** 후 실제 `COMMITTED` insert가 error 19 / STORAGE_FAILURE로 실패했다.
2. `IX_PublicationEvents_Stream_Seq`를 동일 column/order지만 `WHERE Seq<0`인 partial index로 재생성한다. index_info column만 기록하고 partial predicate/flag를 signature에 포함하지 않아 READY와 정상 EXE listen에 도달했다. canonical full index 계약과 다르다. 이것이 item duplication을 만들었다고 주장하지 않는다.

**Required fix:** SQL literal의 대소문자/의미를 지우는 normalization을 제거하고 CHECK/trigger predicate의 의미를 보존한다. index의 partial flag/predicate 및 계약상 필요한 DDL 정보를 포함한다. schema 검증 뒤 실제 canonical terminal values를 쓸 수 없는 DB를 READY로 승인해서는 안 된다.

Evidence: `independent-schema.json`, `schema-check-literal-case`, `schema-case-real-commit`, `schema-index-partial`, `normal-schema-*`.

### QA-PIPELINE-013 — High — bounded admission 개선, disposal fence는 실패

**Location:** [PipelineTransactionCoordinator.cs:150](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:150), writer loop(172), Dispose(459–516).

**Admitted load:** 1,205 submissions에서 1 in-flight, 1,000 queue, 204 immediate BUSY였다. 관측 managed memory 증가는 1,110,432 bytes다. full-queue shutdown에서 모든 1,205 caller가 완료됐으며 orphan/faulted task는 0이다. UNKNOWN 1개 + BUSY 1,204개이며 fabricated ABORTED는 없다. 즉 기존 invisible producer waiter 문제는 해소됐다.

**Actual failure:** Dispose는 Join 1,000+3,000+2,000 ms 후에도 Worker가 살아 있을 때 약 6.03초 만에 반환한다. 마지막 failed join을 오류로 승격하거나 소유권을 계속 보유하지 않는다. `_isDisposed=true`라 이후 Dispose도 다시 join하지 않는다.

| 지연 지점 / 부하 | Dispose 반환 시 | 이후 실제 truth |
|---|---|---|
| full queue + before-read observer barrier | Worker alive; UNKNOWN 1개 | barrier 해제 후 실제 commit; repository calls after Dispose=8 |
| native BEGIN lock, 반환 뒤 즉시 lock 해제 | Worker alive; UNKNOWN 1개 | lock 해제 후 commit; calls after Dispose=9 |
| after-CAS / after-audit / native pre-commit / native post-WAL | 4/4 Worker alive; UNKNOWN | observer 해제 후 COMMITTED; 원래 envelope exact retry는 ALREADY_COMMITTED |
| lock 38.377초, QA BusyTimeout=30초 | 반환 후 5/10/15/20/25초에 Worker alive | 반환 후 약 30초 관측에서 종료; durable operation NOT PRESENT |

native long-lock 시험은 후보의 정상 busy setting(5초)뿐 아니라 QA stress에서 확장한 30초보다 오래 lock을 유지했다. sqlite3_interrupt가 pending busy/retry를 즉시 끝내지 못했고 caller 완료와 worker 종료가 분리됐다. observer barrier는 인위적 지연이지만 **native lock도 같은 lifetime 실패를 재현**한다. freeze/repository 구현을 변경하지 않았다.

**Ambiguous-result convergence:** 원래 `(PrincipalId, OperationId)`를 observer가 보존해 실제 receipt 조회와 **원래 PROFILE를 포함한 exact retry**를 했다. commit된 4 boundaries 및 short-lock/full-queue 결과는 ALREADY_COMMITTED와 원래 IDs로 수렴했다. long-lock의 실제 pre-retry DB truth는 NOT PRESENT다. 보존한 그 논리적 snapshot을 명시적인 QA recovery fixture로 재구성한 equality check 후 receipt=null, exact retry SUCCESS를 확인했다. 이 마지막 exact-retry 보조 시험은 **물리적 crash DB의 추가 재시작**이 아닌 recorded durable snapshot 재구성이다. 원래 long-lock DB의 첫 재시도도 SUCCESS였지만 QA wrapper가 profile을 바꿨으므로 exact-envelope 증거로 사용하지 않았다.

UNKNOWN은 정직한 응답으로 볼 수 있으나 **no worker-after-dispose** 요구를 충족하지 않는다. 현재 좁은 scope에서 business effect가 한 번인 것과 disposal 후 effect가 없어야 하는 조건은 별개다.

**Required fix:** admission close, caller outcome, worker termination, connection/CTS ownership, process shutdown을 하나의 명시적인 lifecycle 계약으로 연결한다. join 실패 시 종료가 완료됐다고 취급하지 않는다. commit ambiguity는 identity를 보존해 조회하도록 하되 실제 writer가 resource owner의 종료 뒤 몰래 진행하지 않도록 한다. 정상 Main의 coordinator ownership도 007과 함께 수정한다.

Evidence: `queue-held`, `queue-lock-result`, `long-lock-results`, `shutdown-boundary-*`, `shutdown-query-exact-*`, `shutdown-retry-exact-*`, `actual-main-shutdown-lifetime`.

### QA-PIPELINE-019 — High — global derivative key의 delimiter collision

**Locations:** [PipelineTransactionCoordinator.cs:375](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:375), EventId(402).

**Reproduction:** 각 pair를 별도 fresh DB에서 각자의 scope, expected 0, revision 1로 실행했다. grammar는 underscore/Unicode/long principal을 허용한다.

| distinct `(PrincipalId, OperationId)` pair | 결과 |
|---|---|
| `(A_B, C)` / `(A, B_C)` | SUCCESS / STORAGE_FAILURE |
| `(A_, B)` / `(A, _B)` | SUCCESS / STORAGE_FAILURE |
| `(한_글, 림)` / `(한, 글_림)` | SUCCESS / STORAGE_FAILURE |
| colon + 300-character principal의 `_B,C` / `B_C` variant | SUCCESS / STORAGE_FAILURE |

첫 pair는 두 작업 모두 `RCPT_A_B_C_1`, `EVT_A_B_C_1`을 생성한다. 두 번째 작업은 CommitReceipts.ReceiptId UNIQUE error 19로 transaction 전체가 rollback된다. 해당 scope에는 canonical effect가 없다. 원래 작업 retry는 ALREADY_COMMITTED와 원래 IDs지만, 별개의 두 번째 작업은 반복해도 STORAGE_FAILURE다.

**Root cause:** journal identity는 composite key로 구분됐으나 receipt/event의 global derivative identity는 separator를 escape하거나 length-prefix하지 않았다. principal을 단순히 추가하는 것만으로 globally injective key가 되지 않는다.

**Required fix:** admission grammar와 실제 global key encoding을 일치시키고, 허용한 값 전체에서 distinct operation key를 구분하는 derivation을 쓴다. 독립 random ID를 택한다면 terminal retry가 새 ID를 만들지 않고 stored ID를 반환하는 계약을 유지한다. current scope에서는 receipt에서 먼저 실패하므로 **EventId 충돌은 source의 동일 construction으로 확인**, 이를 receipt 실패 뒤 실제 event insert까지 실행한 것으로 주장하지 않는다.

Evidence: `derivative-0..3-*`, `derivative-retry-*`, `derivative-truth-*`.

## 5. 해결/회귀 유지 권고의 증거

### QA-PIPELINE-003 — CONFIRMED RESOLVED, tested SQL boundary

실제 `SqliteDatabaseContext.CreateOpenConnection()`에서 recursive_triggers=1, foreign_keys=1이다. COMMITTED/ABORTED 각각 UPDATE, DELETE, INSERT OR REPLACE, REPLACE INTO, UPSERT DO UPDATE, same-key raw insert를 시도하여 **12/12 SQLite19로 거절**됐다. 논리적 DB before/after가 같고 재시작도 정상이다. exact retry는 기존 journal/receipt 조회로 ALREADY_COMMITTED 또는 ALREADY_ABORTED를 반환하며 replacement SQL을 실행하지 않는다. OS attacker가 schema/file을 바꾸는 방어까지 인증하지 않는다.

### QA-PIPELINE-011 — CONFIRMED RESOLVED, typed-failure scope

aggregate/receipt/event/audit 실제 SQLite INSERT에 각각 QA trigger RAISE(ABORT)를 넣었다. 네 경우 모두 STORAGE_FAILURE/SQLite19, canonical effect 0이다. 실제 SQLITE_BUSY(5), 실제 SQLITE_LOCKED(6)는 STORAGE_BUSY_RETRYABLE이며, 네 repository boundary의 IOException은 STORAGE_FAILURE다. genuine CAS mismatch만 STALE_REVISION/terminal ABORTED다. UNKNOWN shutdown convergence는 013의 위 설명과 같이 관측했다. 이 시험은 filesystem/disk controller I/O 오류나 power loss injection까지 포함하지 않는다.

### QA-PIPELINE-016 — CONFIRMED RESOLVED, explicit admission + rotation fence

null/empty/whitespace incarnation은 3/3 INVALID_REQUEST다. constructor blank도 거절한다. 별도 process에서 요청을 immutable admission시킨 후 다른 process가 store를 rotate하고 원래 Worker가 진행하도록 했다. transaction 안에서 active incarnation을 읽어 INCARNATION_MISMATCH로 거절했고 old operation은 저장되지 않았다. historical receipt 읽기는 가능하며 old incarnation이 새로운 mutation 권한을 주지 않는다. mutable DTO의 compatibility fingerprint helper에 fallback 표현이 남아 있어도 tested mutating route는 `FromRequest`의 mandatory validation을 통과해야 한다.

### Concurrency / atomic crash cuts

writer별 별도 SQLite connection과 **25/12/48개의 실제 OS process**를 사용했다. 단일 coordinator의 queue를 concurrency 대신 세는 시험이 아니다.

| hard-kill cut | kill 후 durable operation/effect | restart/retry |
|---|---|---|
| before CAS, BEGIN 후 | 0 | SUCCESS, revision 1 |
| after CAS / receipt / event / audit, commit 전 | 각 0 | SUCCESS, revision 1 |
| native commit hook, commit 성립 전 | 0 | SUCCESS, revision 1 |
| native WAL hook, durable commit 후 response 전 | COMMITTED 1 | ALREADY_COMMITTED, revision 1 |
| Execute return 후 response publish 전 | COMMITTED 1 | ALREADY_COMMITTED, revision 1 |

receipt/audit/event/history/aggregate도 동일 transaction에서 함께 존재하거나 모두 없다. post-WAL cut은 native observer이고 committed truth는 응답 문구가 아니라 재시작 후 DB에서 판정했다. P1에는 별도 publication state marker/consumer delivery 단계가 없으므로 이전 outbox publication crash case를 이 표로 닫지 않는다.

### Connection durability와 admission ordering

실제 application connections: **WAL, synchronous=2(FULL), busy_timeout=5000 ms, foreign_keys=1, recursive_triggers=1, DefaultTimeout=5**. pool에서 NORMAL로 변경해 반환한 connection도 20회 reopen 시 FULL로 재설정됐다. CreateOpenConnection는 매번 설정/검증한다. writer transaction은 Microsoft.Data.Sqlite non-deferred `BeginTransaction()`의 write-lock 경쟁으로 one winner를 보장했다. 이는 process-crash rollback/commit 관측이며 storage hardware 전원 장애에 대한 무조건적인 보증이 아니다.

valid fresh v4 및 8-operation DB restart는 실제 normal executable에서 verification → writer creation → PIPELINE_READY → network listen 순이었다. 거절된 schema/consistency DB는 exit2이며 ready/listen이 없다. **그 순서는 맞지만 검증 내용의 누락은 007/008을 OPEN으로 남긴다.**

### Legacy, release, gameplay boundary

과거 QA 실행에서 생성된 진짜 nonempty schema v1/v2/v3 DB를 복사하여 시험했다. fake version label만 붙인 DB가 아니다. v1은 original application_id=0이고 거절 후 logical state가 보존됐다. v2/v3도 LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET로 거절됐다. normal executable의 세 DB 및 foreign app0/version0 DB는 모두 exit2/NO READY/NO LISTEN이다. destructive migration 구현이나 migration 성공을 주장하지 않는다.

PacketHeader/actual TcpNetworkServer dispatch에 probe header/route가 없다. 정상 server에 PIPELINE_PROBE_CAS JSON을 가진 undefined header65535 frame을 송신했고 TCP 접속 로그는 있지만 ProbeAggregates/OperationRecords/receipt/event 등 probe row는 모두 0이다. `InternalProbeTestSurface.TryInvokeFromGameplayTransport=false`만으로 isolation을 인정하지 않았다. 기존 gameplay handlers가 probe를 호출하지 않는 것도 정적 대조했다.

normal executable에 과거 `--test-pipeline-e1 --db marker`, `--crash-worker --db marker --fault ...`를 넣어도 별도 test/crash 실행 없이 정상 시작/quit하며 marker DB는 unchanged다. compiled public `InternalProbeTestSurface`, `ResetReadinessForTesting`, delay option은 존재한다. **executable/network fault entry 제거 범위에서만 018 closure 유지**를 권고하며 in-process API 제거 또는 Production authentication을 인증하지 않는다. consumer/cursor/ACK table/dispatcher는 현재 P1 schema/loaded types에 없다. probe의 실제 SQL effect는 7개 pipeline tables에 한정된다. 기존 in-memory gameplay manager의 전체 SRS 충족 여부는 이 slice의 통과로 승격하지 않는다.

## 6. Defect-by-defect recommendation

| ID | 권고 | 근거/잔여 범위 |
|---|---|---|
| QA-PIPELINE-001 | **STILL FAILING / OPEN** | exact numeric identity 유실, invalid JSON keys, ambiguous/trailing JSON |
| QA-PIPELINE-002 | regression closure 유지 | PREPARED 없음; terminal-only journal, no auto-complete recovery; legacy fail closed |
| QA-PIPELINE-003 | **CONFIRMED RESOLVED** | 12 native SQL shapes 차단, lookup retry, no terminal replacement |
| QA-PIPELINE-004 | **NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE** | external semantic effect dedup 미인증; CLOSED 아님 |
| QA-PIPELINE-005 | **NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE** | consumer delivery failure recovery 미인증; CLOSED 아님 |
| QA-PIPELINE-006 | **NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE** | delivery/commit convergence 미인증; CLOSED 아님 |
| QA-PIPELINE-007 | **PARTIAL / OPEN** | verification/writer ordering 개선; 9 consistency false READY 및 정상 disposal 실패 |
| QA-PIPELINE-008 | **PARTIAL / OPEN** | 26 mutants 차단; semantic CHECK/partial index false READY |
| QA-PIPELINE-009 | regression closure 유지, configuration scope | 매 connection WAL/FULL; hardware power-loss 보증 아님 |
| QA-PIPELINE-010 | regression closure 유지 | 12-process exact retry: 1 SUCCESS, 11 ALREADY_COMMITTED |
| QA-PIPELINE-011 | **CONFIRMED RESOLVED**, typed-error scope | constraint/BUSY/LOCKED/I/O-like와 true STALE 구분 |
| QA-PIPELINE-012 | regression closure 유지 | 5 cultures의 stable receipt hash; reload/retry stored receipt; 019는 별도 |
| QA-PIPELINE-013 | **PARTIAL / OPEN** | bounded admission/no orphan 개선; ignored failed join/worker-after-dispose |
| QA-PIPELINE-014 | **NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE** | concrete cursor/ACK/gap semantics 미인증; CLOSED 아님 |
| QA-PIPELINE-015 | regression closure 유지 | 실제 legacy v1/v2/v3 fail closed 및 logical truth 보존 |
| QA-PIPELINE-016 | **CONFIRMED RESOLVED**, explicit-fence scope | mandatory incarnation 및 cross-process race 거절 |
| QA-PIPELINE-017 | regression closure 유지 | enqueue 후 caller DTO/list mutation이 실제 admitted command에 영향 없음 |
| QA-PIPELINE-018 | regression closure 유지, executable packaging scope | manifest 32/32, residue0, CLI controls 없음; public in-process test APIs 잔존 명시 |
| QA-PIPELINE-019 | **STILL FAILING / OPEN** | 4 delimiter/Unicode/long identity pairs가 global derivative ID 충돌 |

QDL의 기존 ID 의미를 유지했고 disposition은 Master 판단용 권고다. 제거한 기능은 검증 성공으로 닫지 않았다.

## 7. A의 E1 증거 평가와 필요한 회귀

A result의 20/20 PASS와 JSON hash는 실제 확인했다. 그 결과를 독립 검증의 대체 증거로 쓰지 않았다.

- E1 Test16은 한 coordinator에 25/12 Task를 제출한다. 이름의 `ProcessCasSameIdHardKillRegressions`와 달리 실제 OS process 또는 hard kill을 수행하지 않는다. QA는 별도 OS process와 native commit/WAL cuts로 보완했다.
- numeric E1은 overflow와 28-digit precision을 확인하지만 underflow/29+ precision collision은 검증하지 않는다.
- Test15는 다른 principal의 동일 OperationId만 비교해 `_` 경계 재분배 충돌을 놓친다.
- Test9는 default lock window와 20 submissions를 관측한다. 1,205 full queue, 장기 lock, 여러 commit cut에서 failed join은 여전히 재현된다.
- readiness tests의 존재/두 tamper만으로 semantic cardinality·scope/incarnation·정상 Main 종료 ownership이 입증되지 않는다.
- fake minimal legacy table와 real historical v1/v2/v3 graph는 다른 증거다. QA는 실제 과거 DB를 복사했다.

Dev는 001의 exact-token rejection/canonicalization, 019의 injective derivative identity, 008의 semantic schema fingerprint, 007의 complete convergence/lifetime, 013의 실제 worker termination fence를 수정한 새 후보를 제출해야 한다. 현재 후보는 조용히 고치지 않았다. 새 후보에서는 위 false-success/false-READY/post-dispose cases를 필수 regression으로 잠그고 003/011/016 및 기존 atomic cuts를 유지해야 한다.

## 8. Evidence index와 한계

- [results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV3-20261003/Evidence/results.json): 실제 process IDs, outcomes, native errors, truth/schema, normal logs.
- [independent-schema.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV3-20261003/Evidence/independent-schema.json): 독립 metadata/descriptor/signature.
- `freeze-before.json`, `freeze-after.json`, `copy-manifest.json`, `qa-evidence-manifest.json`: source/package/evidence identity.
- `Evidence/*process-results.json`, `*.stdout`, `normal-*.log`, request/SQL files 및 `DBs/*.db`: 재현 입력과 결과.
- QA `Harness/Program.cs`, `run_checks.py`, `extra_checks.py`, `final_checks.py`, `reconciliation_checks.py`: 독립 observer/orchestration. Production references 및 final QA harness hash는 manifest에 기록.

QA harness 초기 복원/빌드 설정 및 mode dispatch를 정리한 뒤 재실행했다. `fingerprint-matrix`의 초기 QA path exception은 candidate 결함으로 집계하지 않았으며 `fingerprint-complete`의 정상 실행을 사용했다. 초기 shutdown retry wrapper는 helper와 profile이 달라 COLLISION_REJECTED였다. 이는 candidate exact-retry regression이 아니며 `*-retry-exact-*`에서 원래 profile로 재검증했다. 모든 raw 로그를 보존해 이 구분을 추적할 수 있게 했다.

normal Server.exe는 QA directory copy에서 실행했다. 실제 Main lifetime observer는 원본 DLL의 entry method를 호출해 반환 직후 상태를 보는 방식으로, candidate Main을 재작성하지 않았다. observer가 넣은 delays와 genuine SQLite lock evidence를 구별했다. 장기 lock의 recorded-snapshot recovery 시험도 별도로 표시했다. filesystem power loss, external consumer effect, real gameplay transaction/authentication은 미검증이다.

**Master recommendation: REV3 E2 gate 반려. QA-PIPELINE-001/007/008/013/019는 다음 후보 전까지 OPEN 유지. 003/011/016은 위 범위에서 해결을 채택할 수 있다. 현재 E2 foundation을 후속 gameplay-domain transaction gate의 완료된 기반으로 승인하지 말 것.**
