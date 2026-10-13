# QA Production Transaction Pipeline Slice 01 — REV2 Independent E2

```yaml
Work Package: WP-QA-PROD-TRANSACTION-PIPELINE-01-REV2
Reviewer: GPT-6.1 Sol / Independent QA & Architecture Review
Date: 2026-10-03
Target: Production_Transaction_Pipeline_Slice_01_REV2.md
Verdict: FAIL
Candidate Rebuilt or Fixed: No
Production Source/Binary Modification by QA: None
Production Freeze: 358 files before / 358 after / 0 changes
Master Ledger or Architecture State Modified: No
```

## 1. 판정

**최종 판정: FAIL.** 실제 동결 Release DLL에서 terminal decision 변경, shutdown 이후 미완료 요청, 잘못된 schema의 READY 승인, incarnation 생략 허용 및 fingerprint false retry를 독립 재현했다. A의 “22/22 E1 PASS”는 이 실패를 닫는 증거가 아니다.

인정할 개선도 있다. 별도 OS process25개의 CAS 경쟁은 1 SUCCESS/24 STALE, 동일 ID12개의 경쟁은 1 SUCCESS/11 ALREADY_COMMITTED였다. 커밋 전 강제 종료에서는 canonical effect가 없고, 커밋 후 응답 전 종료에서는 재시도가 기존 receipt를 반환했다. 정상 JSON key 순서 재시도, immutable admission, explicit incarnation rotation fence, WAL/FULL, legacy v1/v2 데이터 보존 및 destructive CLI 제거는 좁은 시험에서 통과했다.

QDL-047을 기준으로 001..018의 **공식 의미를 유지하여** 아래 권고를 작성했다. 004/005/006/014는 제거된 generic consumer 경로의 문제가 미래 concrete consumer로 넘어가는 것이며 CLOSED로 처리하지 않는다.

## 2. Exact candidate provenance

증거 루트: [PIPELINE01-REV2-20261003](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003).

먼저 Production 전체를 hash하고 QA `Candidate`에 실제 Release 바이너리를 복사했다. Production을 빌드하거나 동작을 고치지 않았다. 이후의 harness는 **실제 복사 DLL reference**로 빌드했다. QA hook은 공개 repository dependency를 위임 호출하면서 barrier/exception을 추가하거나 native SQLite commit hook으로 멈춘다. 결과를 대신 계산하는 mock coordinator를 사용하지 않았다.

### 바이너리 / runtime / schema

| 항목 | 실제 값 |
|---|---|
| 원본 Server DLL | `C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.dll` |
| Server DLL SHA-256 | `3DDA6E077F19583C456FA64CECC5C65F3057E1D8CC4E4B32B411F4D70F39F3FA` |
| Server DLL MVID | `0a999e64-335e-4fc3-8998-ba152e7e7340` |
| Release Server.exe SHA-256 | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |
| Common DLL SHA-256 | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` |
| win-x64 native e_sqlite3.dll SHA-256 | `DCCBABB2BC7E7D4302C44D9CE41B70721A7D0914FA4D289E2F340D39766AD102` |
| 실제 QA loaded Server DLL | `C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-REV2-20261003\Harness\bin\Release\net8.0\WarEconomy.Server.dll` — 원본/복사본 SHA 일치 |
| 실제 framework | .NET **8.0.10**; QA SDK10.0.201 |
| Microsoft.Data.Sqlite / Core | **8.0.10**, 실제 assembly8.0.10.0 |
| SQLite native | **3.41.2** (`sqlite_version()` 실제 조회) |
| SQLitePCLRaw bundle/core/provider/lib | **2.1.6** |
| Newtonsoft.Json | **13.0.3** |
| fresh schema / application_id | **3 / 1463898693 (`0x57415245`, WARE)** |
| 실제 매 connection 정책 | `journal_mode=wal`, `synchronous=2 (FULL)`, `busy_timeout=5000`, `foreign_keys=1`, `recursive_triggers=0`, provider DefaultTimeout5s |

[metadata-preinit.jsonl](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/Evidence/metadata-preinit.jsonl)는 시험 전에 SHA/MVID를 확인한 기록이다. 초기 QA identity DB의 schema0을 final schema3으로 오인하지 않는다. schema3 이후 metadata는 `Evidence/results.json`의 `metadata` 항목이다. package hashes/versions는 [package-versions.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/package-versions.json)과 `copy-manifest.json`에 있다.

### 변경 source SHA

REV1 동결 manifest의 상대 경로를 현재 절대 경로로 정규화하여 비교했다. Production Server 변경 source8개이며 **Common source 변경은 없다**. 모든 Common source와 관련 Server source를 별도로 hash했다. 아래 파일은 `WarEconomyMod/Source/Server/` 기준이며 전체 절대 경로/hash/bytes는 [source-provenance.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/source-provenance.json)에 있다.

| 변경 파일 | SHA-256 |
|---|---|
| Pipeline/Coordinator/PipelineTransactionCoordinator.cs | `0A3C6A280F20D6CD9A11B7255A64845AAEECF1B3837C72D3AB68883777F0DE3F` |
| Pipeline/Data/Migrations/PipelineSchemaMigration.cs | `ADBC603B772B9C4E78F8CD59AD21CA1A7D4A19EA26FA1D053968208C71042DF9` |
| Pipeline/Data/SqliteDatabaseContext.cs | `3F87284D840607D00F28850F3F424B1AA12136D845E9AE63E25472E49EA7953C` |
| Pipeline/Models/PipelineProbeModels.cs | `1905BC907A4331DB37B5588836C16D7B0D1417B01AB6FFDC11B067C30E5F3D42` |
| Pipeline/Recovery/RecoveryReconciler.cs | `91E87790094023CDD7CBA6322E7ABB8E501E8A995638362AFBB6AA1D79CF6500` |
| Pipeline/Storage/OperationJournal.cs | `5B2E11B4EF86251C839AF25118596354F018CEEC7E7C13155353E0DF2043386B` |
| Pipeline/Storage/PublicationEventStore.cs | `F15E85941327149355ADB6477D492061CCF6987D1DD110A4C1883963AEFFA62D` |
| Program.cs | `C032509DBE2262198E5F4CB6AECD09E018BEAA4D60303617DA08DD2E77A3476A` |

원래 Server의 `Pipeline/Testing/DurableTestConsumer.cs`, `PipelineE1TestBattery.cs`는 삭제됐다. 실제 변경 모델/FingerprintV2는 **Server 모델 파일 안**에 있으며 A 보고서의 Common/Pipeline 파일 배치도와 다르다.

Server PE CodeView GUID와 portable PDB GUID는 `4ea37a64-52e1-42d3-95b6-9f6b48abe1a2`로 일치하고 **20 document checksum 모두 실제 source와 일치**했다. Common도 PDB GUID `f46ba950-aebf-4e2a-9a7c-b346c7519b51` 및 **25 document checksum 일치**. 이 결과는 [server-pdb.jsonl](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/Evidence/server-pdb.jsonl), [common-pdb.jsonl](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/Evidence/common-pdb.jsonl)에 보존했다. 후보를 재빌드하여 동일성을 만들어 내지 않았다.

Production 트리를 시험 중에도 반복 hash했다. [final-integrity.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/Evidence/final-integrity.json): 전체 **358/358, 변경0**. 도중 변경으로 증거를 무효화해야 하는 상황은 발생하지 않았다. QA harness만 빌드했으며 오류0, 네트워크 제한으로 NuGet 취약성 정보 조회 경고 NU1900이 발생했다. Production 경고0/오류0 재빌드를 이번 QA가 수행했다고 주장하지 않는다.

## 3. QDL-047 결함별 권고

아래는 **Master에게 제출하는 권고**이며 공식 ledger를 직접 바꾸지 않았다. 기존 CLOSED 항목의 범위를 확대하지 않는다.

| 공식 ID / 의미 | REV2 QA 권고 | 판정 근거 / evidence key |
|---|---|---|
| 001 operation fingerprint | **STILL FAILING** | 구분자 V2 개선은 통과. invalid UTF-16 및 JSON number→string 정규화 충돌이 실제 `ALREADY_COMMITTED`를 반환. `fingerprint-matrix`, `numeric-*`, `infinity-*` |
| 002 corrupt PREPARED forward recovery | **CLOSED 유지 — narrow fast-path only** | enum/schema 정상 경로에 PREPARED 없음. native precommit kills 후 durable operation0. recovery가 legacy PREPARED를 auto-commit하지 않음 |
| 003 terminal truth overwrite / race | **STILL FAILING** | mutable API는 제거되고 일반 UPDATE/DELETE/UPSERT는 차단. native connection의 REPLACE로 COMMITTED→ABORTED, restart READY, retry ALREADY_ABORTED. `native-terminal-flip` |
| 004 external duplicate effect | **NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE** | consumer 실행/ACK/자동 delivery 제거. 외부 exactly-once 효과는 인증하지 않음 |
| 005 failed delivery abandonment | **동일 DEFERRED 권고** | P1에는 delivery 상태/재전송 실행 없음. 미래 concrete consumer의 실패 disposition은 별도 gate |
| 006 ACK/decision convergence | **동일 DEFERRED 권고** | ACK/cursor/PUBLISHED 제거. durable event availability가 delivery를 뜻하지 않음 |
| 007 startup readiness | **PARTIAL** | DB barrier는 listen 전에 존재. 하지만 무효 schema 및 손상 receipt/event/audit/history도 READY; Program은 writer를 만들지 않고 ready 선언. `normal-*`, `consistency-*` |
| 008 logical schema integrity | **STILL FAILING** | integrity_check=ok인 구조 변조22개 중9개 READY. `schema-*-summary` |
| 009 WAL/FULL durability | **CLOSED 유지 — configuration contract** | 같은 pooled native handle을 NORMAL로 오염 후20회 open 모두 FULL/WAL. physical power-loss 미시험 |
| 010 same-ID process race | **CLOSED 유지** | OS process12개, 1 SUCCESS/11 ALREADY_COMMITTED, 동일 receipt와 단일 event. `same-id-summary` |
| 011 storage typing | **STILL FAILING** | aggregate insert constraint를 expected=actual=0인 STALE로 보고. BUSY5/LOCKED6 및 receipt/event/audit constraint/IO typing은 개선 |
| 012 receipt format/hash regression | **CLOSED 유지 — original representation scope** | 5 culture hash 동일, exact retry/restart receipt/epoch/hash 동일. 직접 DB tamper의 검증 누락은 007에서 별도 취급 |
| 013 ingress/shutdown | **STILL FAILING** | cap1000 있지만 full-queue 종료에서 orphan task204건. dispose 반환 후 writer alive/실행 지속. `bounded-shutdown`, `queue-native-lock` |
| 014 stream cursor skips gap | **동일 DEFERRED 권고** | cursor와 generic dispatcher 없음. 본 P1의 순서 있는 durable ReadAfter만 인증 |
| 015 destructive legacy migration | **CLOSED 권고 — fail-closed preservation** | 실제 REV0 v1/REV1 v2 backup의 operation/receipt/history/audit 보존, startup reject. WAL/SHM 동반 사례도 논리적 truth 동일 |
| 016 incarnation TOCTOU | **PARTIAL** | 명시 old-incarnation의 admitted request는 독립 process rotation 후 reject. 그러나 null/empty/blank를 current incarnation으로 보충해 commit 허용 |
| 017 mutable request admission | **CLOSED 권고 — tested DTO/collections** | 모든 mutable DTO field 변경에도 원래 command commit. scope/revision collections 복사 및 readonly mutation 차단 |
| 018 destructive Release packaging | **CLOSED 권고 — executable test-control scope** | test battery/fault worker/FailFast와 CLI 분기 없음. 실제 old flags는 normal startup만 실행하며 지정 marker DB 불변. bin의 오래된 test DB residue는 아래 운영 메모 |

Watch 해석:

- **WATCH-019 foreign zero-identity adoption:** **NOT REPRODUCED / tested rejection PASS**. 데이터 있는 DB와 빈 unrelated table DB 둘 다 거절되고 canonical rows/schema/app/version 유지.
- **WATCH-020 strict schema:** **CONFIRMED**, 기존008에 연결.
- **WATCH-021 shutdown:** **CONFIRMED**, 기존013에 연결.
- **WATCH-022 independent same-stream sequence:** **NOT REPRODUCED for tested contention**. 48 processes/8 rounds에서 sequence1..8 단일 event/committed revision. 영구 무결성 보장을 모든 부하로 확대하지 않음.
- **QA-EVIDENCE-WATCH-001:** 개발자 제출 freeze hash 부재는 사실이나 이번 QA에서 정확한 SHA/MVID/PDB provenance를 독립 확립했다. Master가 채택 가능한 QA 후보 identity다.

## 4. 상세 실패 및 필요한 수정

### 4.1 001 — 정규화 전에 정보가 소실되어 다른 payload가 exact retry로 승인됨

**Severity: High.** Work Order §3의 다른 semantic envelope 구분 요구 위반.

**Location:** [PipelineProbeModels.cs:138](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:138), UTF-8 encoding; [CanonicalizeJson:334](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:334).

실제 encoder는 `FP`+version2, tags, length-prefix, fixed-width LE 값을 사용한다. nullable string은 보고서의 1-byte presence가 아니라 **Int32 -1 sentinel**이다. `|`, `:`, NUL, CR/LF, null/empty, concatenation-collision scope arrays, NFC/NFD 구분, 1,000,000-char 값은 해당 경계 시험에서 구별됐다. OperationId는 fingerprint에 없지만 `(PrincipalId, OperationId)` DB key로 arbitration한다. caller hash 필드/API는 현재 DTO에 없다.

실패는 length-prefix 자체가 아니라 **그 전에 동일한 bytes/value로 바뀌는 입력**이다.

1. ConfigSnapshotRef의 단독 unpaired UTF-16 `U+D800`/`U+D801` 두 값이 `Encoding.UTF8` replacement fallback으로 같은 bytes/fingerprint가 됐다. 첫 SUCCESS 뒤 다른 값으로 재시도하자 **ALREADY_COMMITTED**. 지원하지 않는 문자열이면 admission에서 거부해야 하며 두 다른 값을 조용히 같은 identity로 승인하면 안 된다.
2. `1.0000000000000001`→`1.0` canonicalization으로 실제 retry가 **ALREADY_COMMITTED**. JSON numeric precision 계약이 불명확하다.
3. 더 명확한 타입 충돌: `{"n":1e309}`(number)이 `{"n":"Infinity"}`(string)로 정규화됐다. 두 번째 string payload 제출이 **ALREADY_COMMITTED**. overflow number를 지원하지 않는다면 typed rejection이어야 한다.

정상 재시도: reordered object keys는 ALREADY_COMMITTED. `[1,2]`→`[2,1]`은 COLLISION_REJECTED. int `9007199254740993`/`9007199254740992`는 보존/구별됐다. `1`/`1.0`은 구별되고 `1.0`/`1e0`은 같으며 `-0`/`0`은 같았다. 모든 숫자 표기를 무조건 같게 취급해야 한다는 요구를 새로 만들지 않는다.

**Required Fix:** 명시적인 지원 JSON/number/Unicode 입력 계약에 따라 invalid/overflow를 거부하거나 정보 보존 정규화를 정의할 것. 이미 정의한 object-key normalization과 material array order를 보존할 것. UTF-8 이전의 lossy conversion을 테스트해야 한다.

### 4.2 003 — REPLACE가 physical terminal immutability를 우회

**Severity: High.** 실제 probe terminal truth corruption; gameplay 데이터 손상을 재현했다는 뜻은 아니다.

**Location:** [Migration:190](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:190)의 UPDATE/DELETE trigger, [DatabaseContext:44](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/SqliteDatabaseContext.cs:44)의 connection policy.

실제 COMMITTED와 ABORTED rows에 UPDATE/DELETE/ON CONFLICT DO UPDATE는 차단됐다. repository duplicate Insert도 UNIQUE19로 거절하고 mutable state-update API는 없어졌다.

그러나 **실제 Production `CreateOpenConnection`**, foreign_keys1/recursive_triggers0에서 `INSERT OR REPLACE … SELECT`로 COMMITTED row를 ABORTED로 치환할 수 있었다. native SQL rows1. receipt/history/aggregate/event는 기존 commit 상태를 유지했다. startup은 READY, 같은 operation 재시도는 **ALREADY_ABORTED**였다. 두 terminal row의 payload replacement도 허용됐다.

**Root Cause:** SQLite REPLACE의 implicit delete는 현재 recursive trigger 설정에서 delete guard를 호출하지 않는다. “insert-only”는 update/delete 두 trigger만으로 보장되지 않는다. Recovery는 ABORTED에 성공 receipt가 붙은 모순도 검사하지 않는다.

**Required Fix:** supported connection/SQL 경로에서 replacement까지 막는 terminal guard와 schema/behavior 검증을 정의할 것. protection을 trigger 이름의 존재로 인증하지 말 것. arbitrary administrator가 모든 trigger를 제거하는 위협까지 본 시험이 인증하는 것은 아니다.

### 4.3 008 — Schema V3 validator가 이름/부분 구조를 실제 invariant와 혼동

**Severity: High.** Work Order §10 strict-equivalence 위반.

**Location:** [Migration:404](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:404), triggers; [434](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:434), unique index; [524](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:524), FK.

각 DB는 SQLite table rebuild/일반 DDL로 만들고 `integrity_check=ok`를 확인했다. malformed-file 검사가 아니다.

| 단독 변경 | startup |
|---|---|
| wrong app, zero app/v3, future version | 거절 |
| missing table/column, wrong type/nullability/PK order | 거절 |
| EventId PK 제거, FK 제거, trigger 제거 | 거절 |
| active incarnation0 또는2 | 거절 |
| **(StreamId,Seq) UNIQUE 제거 또는 다른 columns UNIQUE로 대체** | **READY 둘 다** |
| **FK referenced table는 같고 source column mapping 변경** | **READY** |
| **FK ON DELETE CASCADE로 변경** | **READY** |
| **ProbeRevision CHECK 제거** | **READY** |
| **State CHECK에 PREPARED 추가** | **READY** |
| **같은 이름 no-op update trigger** | **READY** |
| **필수 explicit index 제거 또는 다른 columns로 변경** | **READY 둘 다** |

총22개 중9개 false READY. unique validator는 아무 unique index 하나를 발견하면 통과하여 EventId PK를 StreamId/Seq UNIQUE의 증거로 오인한다. FK는 referenced table name만 보고 mapping/action을 검사하지 않는다. CHECK/index/trigger body는 검증하지 않는다.

실제 normal Release PID32224의 `normal-noop-trigger`에서도 **PIPELINE_READY→7777 listen→Server ready**였다. 모든 schema 사례는 실제 Production startup routine을 호출했고 representative no-op trigger는 ordinary entrypoint까지 검증했다.

**Required Fix:** required constraint의 column/order/uniqueness/mapping/actions와 CHECK/explicit index 및 trigger 의미·행동을 검사할 것. schema signature 함수가 존재하는 것과 기대 schema와 대조하는 것은 다르다. 위 fixtures를 실제 readiness regression으로 사용할 것.

### 4.4 011 — 실제 storage constraint가 revision0==0의 STALE로 변환됨

**Severity: Medium, 기존 분류 유지.**

**Location:** [ProbeAggregateStore.cs:54](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Storage/ProbeAggregateStore.cs:54), broad SqliteException catch; [Coordinator:350](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:350), false CAS 분기.

QA-owned DB의 ProbeAggregates INSERT trigger가 실제 SQLite constraint19를 발생시켰다. 실제 result는 **STALE_REVISION, expected0 / actual0**, storage error detail 소실. 이 경로의 durable ABORTED row는 생성되지 않았으므로 “잘못된 STALE가 durableized됐다”고 과장하지 않는다.

receipt/event/audit constraint는 STORAGE_FAILURE, true SQLITE_BUSY5/LOCKED6는 STORAGE_BUSY_RETRYABLE, injected IOException은 STORAGE_FAILURE로 개선됐다. 그러나 broad initial-insert catch가 모든 SQLite error를 false CAS로 바꾼다. BEGIN IMMEDIATE writer 내부의 actual mismatch 증거 없이 STALE로 반환할 수 없다.

**Required Fix:** 실제 aggregate revision race와 storage exception을 분리하고 결과와 durable decision을 맞출 것. 별도의 operation query/idempotent retry 경로로 commit 후 응답 소실을 처리할 것.

### 4.5 013 — channel-close waiters가 orphan되고 join timeout을 무시

**Severity: High.**

**Location:** [Coordinator:154](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:154), WaitToWrite; [461](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:461), shutdown/join/CTS dispose.

default actual capacity1000, admission timeout2s. 1 active writer +1000 queued +204 waiting producer requests로 **총1,205**를 제출했다.

| 시험 | Dispose 반환 | worker 종료 후 결과 |
|---|---|---|
| repository barrier로 writer 지연, queue full 즉시 shutdown | 약7.012s, worker alive | SUCCESS1 / STORAGE_BUSY_RETRYABLE1000 / **pending204** |
| timeout을 먼저3s 기다린 뒤 shutdown | 약7.018s, worker alive | SUCCESS1 / STORAGE_BUSY_RETRYABLE1204 / pending0 |
| 독립 SQLite writer connection이 BEGIN IMMEDIATE로 lock 유지, busy_timeout30s | 약7.016s, worker alive | lock release 후 SUCCESS1 / STORAGE_BUSY_RETRYABLE1000 / **pending204** |

실제 native-lock case는 DB 동작을 모방한 mock이 아니다. 외부 connection이 lock을 보유했고 Dispose 반환 신호 이후 lock을 풀었다. coordinator writer가 아직 살아 있는 동안 CTS를 폐기한 상태였고, 해당 writer의 repository 동작이 반환 이후 계속됐다. 별도의 disposed DB 접근 예외를 관측했다고 주장하지 않는다.

**Root Cause:** channel close 때 `WaitToWriteAsync`가 false를 반환하면 enqueue하지 않은 item의 TCS를 그대로 await한다. queue drain으로는 채널에 없던 waiters를 찾을 수 없다. 두 번째 Join도 성공 여부를 무시한다.

**Required Fix:** admission 결과를 accepted/rejected/closed로 명시하고 enqueue 안 된 모든 caller를 반드시 종료시킬 것. active writer의 drain/cancel/unknown outcome 계약을 유지하고 완전 종료 전 관련 자원을 폐기하지 말 것.

bounded channel 자체와 2s timeout backpressure는 존재한다. 그러나 pending admission objects는 producer 수에 비례하며 전체 memory 상한까지 인증하지 않는다. 측정 managed 증가 약1.40MB는 이 작은 payload workload의 값일 뿐이다. 별도 “writer 미시작” 모드는 API가 노출하지 않는다(생성자에서 Thread.Start). dedicated writer가 첫 업무에서 멈춘 경우와 실제 DB lock으로 장기 blocked인 경우를 검증했다.

`SERVER_BUSY_RETRYABLE`는 message 안의 구분일 뿐 enum Status는 queue-full과 SQLite-lock 모두 **STORAGE_BUSY_RETRYABLE**이다. 서로 다른 typed outcome이라고 보고하지 않는다.

### 4.6 016 — mandatory incarnation을 생략하면 current epoch에 자동 재결속

**Severity: High.**

**Location:** [PipelineProbeModels.cs:286](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:286), FromRequest; [Coordinator:113](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:113).

normal API에 null, empty, whitespace StoreIncarnationId를 각각 제출해 **3/3 SUCCESS**. direct immutable constructor는 blank를 거절하지만 FromRequest가 먼저 active incarnation으로 채운다. explicit old ID의 in-tx TOCTOU는 고쳐졌지만 생략된 old context까지 현재 권한으로 보충할 수 있다.

긍정 시험: actual admitted request가 writer delay 중일 때 별도 OS process가 incarnation을 ROTATED_QA로 변경·commit. resumed request는 INCARNATION_MISMATCH, canonical effect0. 재시작 후 ROTATED_QA 유지. historical receipt는 조회 가능하나 old explicit envelope 재시도는 reject. Static Player/principal fixtures는 Production authentication proof가 아니다.

**Required Fix:** 모든 mutating admission API에서 명시적인 nonblank incarnation을 요구할 것. server convenience default와 fencing 증명값을 혼동하지 말 것.

### 4.7 007 — readiness의 존재와 완전 consistency 증명을 구분해야 함

**Location:** [RecoveryReconciler.cs:45](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:45), receipt/event 존재 검사; [Program.cs:34](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:34).

기존보다 개선된 정상 bootstrap/검증 barrier는 listen 전에 실행된다. 그러나 receipt revision999, receipt hash변조, event payload변조, event type변조, audit전체삭제, history전체삭제의 **6종 valid SQLite fixture 모두 READY**였다. existence LEFT JOIN/count만으로 canonical logical consistency를 인증한다. ABORTED+성공 receipt 모순도 위 REPLACE 시험에서 통과했다.

Program의 startup manager는 coordinator/dedicated writer를 생성하지 않는다. 그러므로 “writer running이 확인된 PIPELINE_READY”라는 A 주장은 실제 entrypoint와 다르다. P1이 서비스-lifetime writer를 요구하는 현재 readiness 계약을 유지한다면 lifecycle을 실제로 연결해야 한다. 미래 gameplay 구현을 QA가 대신 추가하지 않는다.

**Required Fix:** P1에 맞는 receipt/operation/history/event/audit consistency invariant를 검증하고 명시한 writer readiness를 실제 lifetime과 결속할 것. consumer가 없다는 것은 정상이며 **available event를 자동 deliver/catch-up할 필요는 없다**.

### 추가 발견 — principal별 OperationId가 global receipt/event ID에서 충돌

**Severity: High, 새 공식 번호는 Master 배정 요청.**

[Coordinator:372](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:372), [399](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:399): global IDs는 `RCPT_{OperationId}_{Revision}`, `EVT_{OperationId}_{Revision}`로 principal/scope를 포함하지 않는다.

P/OP/S revision1 commit 후 P2/OP/S2 expected0의 정상 별도 operation이 **CommitReceipts.ReceiptId UNIQUE STORAGE_FAILURE**로 rollback됐다. `(PrincipalId,OperationId)` key를 분리했지만 downstream ID namespace가 이를 반영하지 않는다. event ID도 같은 구조 위험이나 receipt에서 먼저 실패하므로 두 번째 actual event constraint를 별도 재현했다고 주장하지 않는다.

**Required Fix:** journal key와 receipt/event global identity 계약을 일치시키고 retry 때 동일한 identity가 유지되도록 정의할 것. 명칭 변경만으로 operation key semantics를 축소하지 말 것.

## 5. 통과한 원자성 / concurrency / durability 증거

- **CAS:** OS process25, 각 별도 SQLite connection/coordinator, 동일 scope expected0 → SUCCESS1/STALE24. aggregate/history/receipt/event의 canonical revision winner1. STALE들의 terminal ABORTED/audit는 실제 mismatch 기록이다.
- **Same ID:** OS process12 → SUCCESS1/ALREADY_COMMITTED11. receipt/hash/epoch 동일, canonical revision/event1.
- **Same stream:** 8 rounds×6 independent OS processes=48; 각 round에서1 commit/5 genuine stale → SUCCESS8/STALE40. Seq1..8, unique EventId, `(StreamId,Seq)` 중복0. ReadAfter pages1..3,4..6 및 fresh-process 재조회1..8은 ascending 동일. 이 부하에서 busy/UNIQUE corruption은 관측되지 않았다. 별도 true native BUSY/LOCKED typing 시험과 구분한다.
- **Hard kill:** after-CAS, after-receipt, after-event, after-audit, native sqlite commit hook(before actual durable commit)에서 Process.kill. 각각 재시작 전 operation/aggregate/history/receipt/event/audit0. 재시도 후 각각1. commit 완료 후 response emit 이전(`after-return`) kill에서는 처음부터 각각1, retry ALREADY_COMMITTED. OS kill은 power loss 시험이 아니다.
- **Fault atomicity:** real receipt/event/audit constraint 또는 QA I/O-like exception의 실패에서는 부분 canonical write가 남지 않았다. PublicationEvents는 actual canonical transaction 안에서 append됐다. commit 후 generic callback consumer 실행은 없다.
- **Immutable admission:** writer를 repository read 직전에 멈추고 원본 DTO의 principal/op/type/schema/scope/revision/profile/config/payload/incarnation 전부 변경. 원래 principal/target/nested JSON payload가 commit됐다. caller scope/revision List 변경 및 IReadOnlyCollection cast mutation도 admitted snapshot을 바꾸지 못했다. DTO payload는 string이므로 caller-owned JObject graph가 이 API에 존재한다고 가정하지 않는다.
- **WAL/FULL:** pooled 동일 native handle에 NORMAL을 남긴 뒤20 open 모두 FULL/WAL. actual timeout과 journal policy를 기록했다. 물리 power-loss durable guarantee를 이 시험만으로 인증하지 않는다.

## 6. Legacy / foreign DB / normal Release / packaging

### Fail-closed preservation

실제 이전 QA DB backup 사용:

- REV0 v1 fingerprints DB: operation1, receipt1, aggregate1, history1, audit2, outbox1.
- REV1 v2 identity DB: operation2, receipt2, aggregate2, history2, audit2, events2, incarnation1.

REV2 startup은 LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET으로 거절, 모든 logical rows/schema/version/application_id 불변. main+WAL+SHM이 존재하는 legacy 변형도 불변 logical truth를 확인하고 각 파일 hash/bytes를 전후 기록했다. opening/journal metadata의 harmless 변화와 canonical 삭제/채택을 구분한다. 모든 원래 QA backup은 읽고 복제하여 시험했으며 Production DB를 대상으로 하지 않았다.

app0/version0의 unrelated table/data가 있는 DB와 unrelated empty table DB는 둘 다 거절했다. 잘못 WARE로 adopt하거나 unrelated rows/schema를 지우지 않았다. reject message는 LEGACY 계열이며 foreign-specific 진단 개선은 별도 사항이다.

### Ordinary Release startup

fresh v3와 valid event8개 DB의 restart는 PIPELINE_READY→7777 listen→Server ready. valid pending delivery 상태는 P1에 없으므로 event8개의 “미전달”을 startup failure로 취급하지 않는다. event bytes/rows는 유지됐다.

missing-column, legacy v1/v2, foreign-zero는 exit2, READY/listen 없음. no-op trigger DB는 **잘못 READY/listen**. normal logs, PID와 종료코드는 `Evidence/normal-*.log`/results에 있다. 생성한 QA 서버는 모두 종료했다.

### Release controls / gameplay isolation

actual Server DLL reflection에는 E1 battery, DurableTestConsumer, crash-worker/fault type이 없다. Production source/actual compiled document set에 `--test-pipeline-e1`, `--crash-worker`, Environment.FailFast execution branch가 없다. operation enum은 COMMITTED/ABORTED만 있다. ResetReadinessForTesting 및 local simulation-delay options는 남아 있지만 destructive CLI와 동일시하지 않는다.

실제 copied Release.exe에 old test/crash flags+`--db`를 제출했다. 별도 marker DB는 변경0, test battery/FailFast가 실행되지 않고 default QA-directory DB로 normal startup했다. unknown flags는 거절되는 것이 아니라 무시된다. 운영 UX에서 명시적 unknown-argument reject를 고려할 수 있으나 기존018 destructive path는 제거됐다.

실제 ordinary socket7777에 undefined header65535+probe JSON frame을 전송했다. native connection 로그와 dispatch 조사, QA default DB의 probe/operation/event0을 확인했다. actual PacketHeader/dispatch에 probe route 없음. `InternalProbeTestSurface.TryInvokeFromGameplayTransport`의 always-false helper만으로 판정하지 않았다. Production authentication 전체를 인증한 것이 아니다.

원래 `Server/bin/Release/net8.0`에는 과거 테스트 DB5개(fresh/future/malformed/restart/test_pipeline)가 남아 있다. executable TestHarness DLL은 포함되지 않는다. 본 QA normal copies는 binaries/runtime dependency만 복사했다. “원본 output 전체가 clean deployment package”라고 인증하지 않는다. 배포 manifest에서 해당 DB residue를 제외하고 canonical default DB와 혼동하지 않도록 할 필요가 있다.

## 7. Production P1 범위와 architecture 경계

실제 fresh schema는 StoreIncarnations, ProbeAggregates, ProbeRevisionHistory, OperationRecords, CommitReceipts, AuditRecords, PublicationEvents의 **7 tables**다. ConsumerCursors/ConsumerDurableAcks/outbox delivery state 없음. actual binary/source에 generic callback consumer registration/executor, automatic replay delivery, PUBLISHED operation state 또는 외부 exactly-once execution path가 없다. RecoveryReconciler는 delivery 대신 readiness/consistency 확인을 수행한다. **P1의 durable available event가 외부 효과 dedup을 입증하지 않는다.**

004/005/006/014는 미래 concrete consumer gate에서 다시 검증해야 한다. 그 때 consumer 자체 effect/idempotency 계약, 실패 disposition, ordered gap 처리와 crash window를 구체적인 gameplay consumer 기준으로 검증해야 하며 이번 P1에서 generic two-phase commit을 강요하거나 새 구현을 추가하지 않았다.

pipeline의 actual mutation은 probe revision/history와 operation/receipt/audit/event/incarnation에 한정된다. Settlement material, CommittedSettlementStateRevision, ArtifactBaseStateRevision, EntityId, Trade/Tax/Caravan/Tactical을 mutation 대상으로 연결하지 않았다. normal server의 기존 feudal seed/clock startup은 probe transaction effect와 구분한다.

Immutable command의 scopes/revisions 배열과 single-probe 실행 범위를 future multi-aggregate transaction 지원으로 확대 해석하지 않는다. 현재 coordinator는 first scope/revision만 실행한다. support cardinality와 paired scope/revision normalization은 concrete multi-target command 도입 전에 계약/검증해야 한다.

## 8. E1 evidence 평가 및 QA 재현 한계

A Test04/05는 이름이 MultiProcess지만 실제 구현은 **Task.Run + independent coordinators in one OS process**다. 이번 QA는 진짜 OS process25/12 및 same-stream48로 대체하여 검증했다.

Test06은 UPDATE/DELETE만 검사하여 REPLACE 우회를 놓쳤다. storage typing test는 aggregate insert constraint 경로를 닫지 않았다. malformed-schema test와 short shutdown happy path는 same-name no-op trigger/constraint mapping 및 join-timeout/closed waiters를 검증하지 못한다. passing assertion을 requirement 만족으로 승격하지 않는다.

QA 실행 초반 이미 metadata 용도로 만든 empty identity DB에 fresh helper가 assertion하여 한 번 중단됐다. QA helper만 수정하여 empty/no-table 상태를 확인하고 이어 실행했다. candidate 실패로 계산하지 않았다. source comparison의 상대/절대 경로도 정규화하여 근거 없는 “모든 source 변경” 결과를 최종 보고에 사용하지 않았다. 후보 수정/재빌드는 없었다.

main evidence: [results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/Evidence/results.json), [summary.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/Evidence/summary.json), [qa-harness-manifest.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV2-20261003/qa-harness-manifest.json). Independent process stdout, request JSON, DBs, before/after manifests와 PDB checks는 증거 루트에 보존했다. harness가 직접 호출한 method, QA repository fault, native SQLite error, real ordinary entrypoint를 각 항목에서 구분했다.

## 9. Final recommendation

**FAIL.** 다음 수정 후보는 001 fingerprint의 lossy input, 003 REPLACE, 008 strict schema, 011 aggregate error, 013 closed-queue/shutdown, 016 mandatory incarnation을 우선 닫아야 한다. 007 readiness의 실제 consistency/lifetime 및 principal별 global receipt/event ID namespace도 정리해야 한다.

017/015/018의 좁은 closure 권고와 기존002/009/010/012 regression lock은 인정한다. 004/005/006/014는 **NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE**로 넘길 수 있다. 이것을 전체 Pipeline E2 PASS, gameplay transaction 승인, 미래 consumer exactly-once 보장으로 사용하지 않는다. Master ledger를 수정하지 않았으며 보고서 제출 후 추가 구현을 시작하지 않는다.
