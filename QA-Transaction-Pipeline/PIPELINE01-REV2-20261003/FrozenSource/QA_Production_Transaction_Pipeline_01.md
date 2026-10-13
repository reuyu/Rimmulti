# QA Production Transaction Pipeline — Independent Review 01

[QA REVIEW]

- **Work Package:** WP-QA-PROD-TRANSACTION-PIPELINE-01
- **Target:** exact Production candidate in `Production_Transaction_Pipeline_Slice_01.md`
- **Verdict: FAIL**
- **Reviewer:** GPT-6.1 Sol, Independent QA / Architecture Reviewer
- **Execution date:** 2026-10-02, Windows, .NET 8.0.10
- **Production modification:** 없음. 테스트는 동결 DLL의 byte-identical QA 복사본 및 별도 DB에서 수행했다. Production 재빌드로 동결 바이너리를 덮어쓰지 않았다.
- **Master disposition:** 이 보고서는 QA 판정과 수정 권고다. Master의 ADR/게이트/결함 원장 상태는 변경하지 않았다.

## 1. Decision and scope

**단일 SQLite transaction 안의 ProbeRevision CAS, history, COMMITTED record, receipt, commit audit, outbox insert는 검증한 종료/쓰기 실패 경계에서 함께 커밋되거나 함께 롤백됐다.** 독립 프로세스 25개의 경쟁도 정확히 1건 성공했다. 이 부분은 재사용할 수 있는 기반이다.

그러나 이 후보를 올바른 E2 transaction foundation으로 승인할 수 없다. 서로 다른 actor/scope/revision/profile의 요청이 기존 성공 receipt를 반환하고, 불완전하거나 변형된 PREPARED가 재실행된다. 복구와 실행의 경쟁은 이미 PUBLISHED인 operation을 ABORTED로 되돌린다. Outbox에는 외부 효과 중복, FAILED 재시도 누락, DELIVERED/COMMITTED 고착이 재현됐다. 정상 서버 시작은 DB bootstrap/recovery를 수행하지 않고 gameplay socket을 연다.

이 테스트가 검증하는 canonical state는 **ProbeScopeId / ProbeRevision**이다. SettlementRevision, ArtifactBaseStateRevision, inventory, Tax, Trade, Tactical, ownership, Caravan, EntityId 이전 구현을 시험하거나 추가하지 않았다. 전체 SRS-NFR을 충족했다고 판정하지 않는다.

**Requirements Reviewed:** 이 slice의 기반 계약을 Canonical SRS-NFR-004(일관성), SRS-NFR-006(영속성), SRS-NFR-007(중앙 권한), SRS-NFR-012(감사 가능성), ADR-001의 operation identity/receipt/recovery acceptance 및 ADR-004 v2의 durable decision/publication 분리에 대조했다. SRS-NFR-005의 실제 gameplay transaction 원자성은 이 probe만으로 검증할 수 없다.

| Mandatory attack | Independent result |
|---|---|
| 1. Source/build/runtime provenance | Source/Server DLL/EXE 16개 보고 해시 일치, loaded DLL 확인, 별도 Server/Common build 성공. A의 기존 결과 JSON 해시는 불일치 |
| 2. Complete operation fingerprint | **FAIL:** scope/revision/actor/profile 변형이 기존 성공 receipt 반환. 제출한 hash를 검증 없이 신뢰 |
| 3. Independent CAS concurrency | **PASS for different OperationIds:** OS process 25개 → 1 winner/24 stale. 같은 ID 경쟁은 9/10 unique exception |
| 4. Hard-kill commit boundary | **PASS for atomic DB commit subset:** PREPARED, tx begin, CAS/receipt/audit/outbox 후, native commit hook, commit 후 실제 OS 종료 검증. Publication window는 실패 |
| 5. PREPARED recovery integrity | **FAIL:** 13개 변형 중 11개 자동 commit. hash/scope를 빈 문자열로 만든 두 경우만 abort |
| 6. External outbox duplicate window | **FAIL:** 외부 효과 1회 후 종료 → 같은 effect identity로 2회 실행. Consumer dedup 계약 없음 |
| 7. SQLite durability policy | WAL/NORMAL(1), busy_timeout=5000 실제 확인. FULL(2)은 QA opt-in 확인만 수행. Power/system failure 보장 미입증 |
| 8. Receipt/audit/state convergence | DB atomic subset 통과. **FAIL:** recovery race, FAILED 고착, DELIVERED/COMMITTED 고착, receipt 표현/hash 재계산 불일치 |
| 9. Gameplay isolation | **PASS for this exact probe:** enum/dispatch에 probe route 없음. 실제 undefined-header probe JSON 전송으로 DB effect 없음 |
| 10. Startup/migration/recovery ordering | **FAIL:** fresh 일반 시작 DB 생성 없음; restart PREPARED 방치하고 READY. 잘못된/미래 schema를 초기화 성공 처리 |

## 2. Artifact identity and build provenance

Evidence root:

`C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-20261002`

### 2.1 Frozen candidate

`freeze-before.json` 및 `Evidence/results.json`의 `manifest`, `freeze-final`에 전체 측정값을 보존했다. Production 아래 `.cs/.csproj/.dll/.exe/.json` 107개를 전후 대조했고 **107 → 107, 변경/추가/삭제 0개**였다. 다른 Production 파일에 쓰기를 수행하지 않았다.

| Artifact | Verified SHA-256 |
|---|---|
| Frozen Server DLL | `C43BA35C145C2366C4D52D01B1B0CF1BFA5F70BA1D02137AF124EE52BB0FA2AC` |
| Frozen Server EXE | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |
| Frozen Remote Presentation DLL, 별도 read-only 대조 | `55182E92E1E077181B3B944E4EA450F7623E47BCD45084E4FEB0ECD22BD34E3E` |

보고서에 열거된 Server csproj, Program, Models, DB context, migration, journal, aggregate store, outbox, audit, receipt, coordinator, recovery, internal surface, test battery 및 DLL/EXE **16개 모두** 일치했다. 경로·개별 expected/actual 해시는 `Evidence/results.json → manifest`에 있다.

QA harness에서 실제 로드된 Server assembly:

- Path: `C:\Users\user\Desktop\RimMulti\QA-Transaction-Pipeline\PIPELINE01-20261002\Harness\bin\Debug\net8.0\WarEconomy.Server.dll`
- SHA-256: 위 frozen Server DLL과 동일.
- **MVID:** `bcc80edd-be2b-493f-ba2a-dc23920cfa13`
- 일반 Production startup 테스트는 `StartupRuntime\WarEconomy.Server.dll`의 동일 SHA 복사본을 별도 OS process로 실행했다.
- 기존 사용자 소유 Server process를 검사했다고 주장하지 않는다. 이 보고서의 loaded identity는 QA가 실행한 정확한 후보에 대한 것이다.

### 2.2 Dependency and schema identity

- Runtime: **.NET 8.0.10**.
- `Microsoft.Data.Sqlite` / Core: **8.0.10**, loaded assembly version **8.0.10.0**.
- `SQLitePCLRaw.bundle_e_sqlite3/core/lib.e_sqlite3/provider.e_sqlite3`: **2.1.6**.
- `Newtonsoft.Json`: **13.0.3**; `System.Memory`: **4.5.3**.
- Loaded native SQLite: **3.41.2**.
- Fresh valid schema: `PRAGMA user_version = 1`, `integrity_check = ok`.
- Harness dependency DLL 및 win-x64 native DLL을 FrozenRuntime과 비교해 동일 bytes임을 확인했다. `package-versions.json`, `results.json → dependencies` 참조.

### 2.3 Build and A's evidence integrity

Server/Common source를 `BuildCopy`로 복사하고 cached packages로 restore하여 별도 빌드했다. **경고 0 / 오류 0**. 테스트에는 이 재빌드 DLL을 사용하지 않았다. 최초 `--no-restore` 시도는 복사본 assets가 없어 NETSDK1004가 났으며, offline cached restore 후 full compilation이 성공했다. 이것은 candidate source compile defect가 아니다. 이 작업에서 Client/엔진 전체 빌드를 새로 인증하지 않았다.

동결 Server의 `--test-pipeline-e1`도 독립 DB에서 **13/13 PASS**를 재현했다. 이 battery가 본 보고서의 추가 공격을 검증하지 못함은 section 8에 설명한다.

**Provenance observation:** A가 보고한 `scratch/pipeline_e1_results.json` SHA는 `5F82D3D0907297A6AC0D78580FFEB177579FD2BF8A0B2C42B02C4113106D94E9`이나, 원 경로에서 실제 읽은 bytes는 `548379EC09D8D650832EED7B64686E5EFCD7F077D6BD8A650233188D3BF90951`였다. 현재 파일을 `Evidence/developer-original-current.json`으로 보존했다. 이 파일을 A 보고서의 exact frozen evidence라고 인정하지 않는다. 원인/교체 경위는 입증되지 않았다. **Production 16개 해시는 일치하므로, QA는 그 정확한 코드/DLL을 독립 시험했다.**

## 3. Independent measurements

### 3.1 Operation fingerprint

실제 계산 경계는 `PipelineProbeRequest.ComputePayloadHash()`다. 제출한 `PayloadHash`가 있으면 그것을 그대로 반환한다. 없으면 **PayloadJson 문자열의 UTF-8 bytes만 SHA-256**한다. JSON canonicalization 또는 envelope hash가 아니다.

`OperationId`는 DB lookup/unique key이고, 비교 hash에 들어가지 않는다. `ProbeScopeId`, `ExpectedProbeRevision`, `ActorId`, `ContentProfileFingerprint`, `OperationType`은 저장되지만 idempotency 비교에 사용되지 않는다.

| Same OperationId challenge | Actual frozen DLL result |
|---|---|
| Exact retry | ALREADY_COMMITTED, same ReceiptId / ReceiptHash, revision 추가 없음 |
| Same JSON, different ProbeScopeId | **ALREADY_COMMITTED / Success=true**, 원래 SCOPE receipt 반환 |
| Same JSON, ExpectedProbeRevision 0 → 99 | **ALREADY_COMMITTED / Success=true** |
| Same JSON, Actor A → B | **ALREADY_COMMITTED / Success=true** |
| Same JSON, Profile A → B | **ALREADY_COMMITTED / Success=true** |
| Different JSON, auto-computed hash | COLLISION_REJECTED, 정상 |
| Different JSON + supplied original PayloadHash | **ALREADY_COMMITTED / Success=true** |
| Stored OperationType changed to OTHER_OPERATION, then original probe retry | **ALREADY_COMMITTED / Success=true** |

**OperationType test limitation:** `PipelineProbeRequest`에는 OperationType 입력 필드가 없고 이 slice는 probe 하나만 허용한다. 따라서 정상 API로 다른 command type을 보내는 시험은 가능하지 않다. 위 마지막 행은 DB에 다른 type record가 존재할 때도 typed lookup이 검증하지 않는 것을 입증한 storage-level collision 시험이다. 다른 gameplay OperationType의 실행 경로를 만들거나 있다고 가정하지 않았다.

### 3.2 Independent process / SQLite concurrency

같은 expected revision=0, scope=SCOPE에 **각각 별도 OS process/connection**으로 실행했다. 첫 시험은 start barrier만 사용했다. 두 번째는 각 프로세스의 durable PREPARED insert 후 QA observer로 대기시켜 25개 모두가 commit 경쟁에 진입하게 했다. observer는 SQL/business effect를 변경하지 않았다.

| Test | Workers | Commits | Deterministic stale losers | Other outcomes | Controller elapsed |
|---|---:|---:|---:|---:|---:|
| Native process race | 25 | 1 | 24 | 0 | 458.202 ms |
| All-PREPARED process race | 25 | 1 | 24 | 0 | 1893.378 ms |
| Same OperationId / same payload, lookup barrier | 10 | 1 | 0 | **9 UNIQUE exceptions** | 299.843 ms |

앞의 두 시험은 revision/history/receipt/outbox 각각 1개 commit을 확인했다. 같은-ID 시험도 business effect는 1개지만 나머지 9개가 안정된 retry 결과 대신 SQLite code=19, extended=1555를 받았다.

별도 Python SQLite connection으로 write lock을 유지한 시험은 **33.314초 후 SQLITE_BUSY(code=5)** 예외였다. 후보는 이를 typed RETRYABLE/IN_PROGRESS/UNKNOWN outcome으로 정리하지 않았다. 이 시험에서는 PREPARED 이전에 실패하여 canonical effect=0이었다. 따라서 이 측정만으로 commit 결과 불명 상태를 입증했다고 주장하지 않는다.

초기 aggregate INSERT의 DB constraint failure를 유발하자 후보는 `STALE_REVISION_REJECTED`, **Expected=0 / Actual=0**을 반환하고 operation을 ABORTED로 기록했다. 모든 `SqliteException`을 CAS 경쟁으로 오인하는 경계도 재현됐다.

### 3.3 Actual hard OS termination

controller가 checkpoint signal을 확인한 후 child process를 Windows OS 종료로 중단했다. `SimulatedCrashException`을 catch한 in-process 시험으로 대체하지 않았다. `before-commit` hook은 candidate의 explicit rollback보다 앞에서 막은 후 종료했다. `native-commit`은 SQLite commit hook 안에서 정지하여 **tx.Commit 호출 중, commit 성립 전** 경계를 시험했다. 이를 commit 성립 후라고 분류하지 않는다.

| Kill boundary | Durable truth before recovery | Restart/retry result |
|---|---|---|
| PREPARED insert, prepared audit 이전 | PREPARED; revision/history/receipt/outbox 없음; prepared audit 없음 | 1회 commit/publish. Prepared audit는 복원되지 않음 |
| After PREPARED+audit | PREPARED; canonical effect 없음 | 1회 commit/publish |
| Tx begun, before CAS | PREPARED; canonical effect 없음 | 1회 commit/publish |
| After CAS statements | Uncommitted aggregate/history 소멸; PREPARED | 1회 commit/publish |
| After receipt insert | Uncommitted receipt 및 CAS 변경 소멸; PREPARED | 1회 commit/publish |
| After commit audit insert | Uncommitted audit 및 CAS 변경 소멸; PREPARED | 1회 commit/publish |
| After outbox insert, before commit | Uncommitted outbox 및 CAS 변경 소멸; PREPARED | 1회 commit/publish |
| Candidate BeforeCommit, rollback 실행 전 | PREPARED; canonical effect 없음 | 1회 commit/publish |
| Native commit hook inside tx.Commit | PREPARED; canonical effect 없음 | 1회 commit/publish |
| Immediately after tx.Commit / before dispatch | revision=1, COMMITTED, receipt/audit/outbox=PENDING 함께 존재 | 동일 receipt, revision 추가 없음, publish 성공 |
| External effect succeeded / before delivery marker | revision=1, COMMITTED, PENDING; 외부 효과 1개 | **같은 OutboxId 효과가 2개**, canonical revision은 여전히 1 |
| DELIVERED durable / before PUBLISHED | revision=1, COMMITTED, DELIVERED | **복구 2회 후에도 COMMITTED 고착** |

DB truth는 별도 SQLite connection에서 읽은 6개 table과 integrity_check로 판단했다. Kill된 프로세스의 stdout이나 반환 직전의 메모리 receipt를 canonical truth로 쓰지 않았다. 실제 system/power failure를 재현한 시험은 아니다.

### 3.4 PREPARED tampering

각 DB는 frozen coordinator가 실제 PREPARED를 기록한 뒤 프로세스를 종료하여 만들었다. 그 이후 별도 DB connection으로 변형하고 frozen recovery를 실행했다.

| Tamper | Recovery |
|---|---|
| Payload changed but original hash retained | **Committed** |
| Payload removed to empty string | **Committed** |
| Payload replaced by invalid JSON | **Committed** |
| PayloadHash replaced by BAD_HASH | **Committed** |
| PayloadHash empty | Aborted |
| Scope replaced by EVIL_SCOPE | **New altered scope committed** |
| Scope empty | Aborted |
| Actor changed / emptied | **Committed / Committed** |
| Profile changed / emptied | **Committed / Committed** |
| OperationType changed to NOT_PROBE | **Committed** |
| ExpectedRevision changed 0 → 1; canonical fixture head=1 | **Committed revision 2** |

마지막 fixture는 원 request의 expected=0을 유지한 채 DB package의 expected와 current head를 변경했다. 원래 요청과 달라진 package를 검증 없이 새로운 head에 적용할 수 있음을 보여준다. 임의의 DB 전체를 다시 쓸 수 있는 공격자를 로컬 checksum만으로 방어할 수 있다고 주장하지 않는다. 여기서 필요한 것은 durable package identity, 입력 완전성, actor/profile/revision 계약 검증이다.

### 3.5 Outbox, receipts, write failures and recovery competition

- 실제 candidate `DefaultPublicationOutboxDispatcher.OnDispatched`에 QA durable append consumer를 연결한 후속 시험에서도 **같은 OutboxId/OperationId/EffectType의 효과가 2건**이었다. FileStream.Flush(true) 후 marker 이전에 프로세스를 종료했다.
- 이 consumer는 의도적으로 멱등성을 갖지 않는 관측기다. 한 번의 delivery가 한 번의 semantic increment에 해당한다. 후보 consumer 경계에 dedup이 없음을 입증하며, 미구현 Trade/item duplication을 실게임에서 관측했다는 의미는 아니다.
- `dispatch-throws`: COMMITTED + FAILED outbox. recovery는 pending=0으로 무시하고 COMMITTED/FAILED 상태를 남겼다. 추가 `writefail-before-dispatch`는 외부 효과 실행 전 실패를 주입했으며 **effectCount=0, 재시작 후에도 FAILED 고착**을 확인했다.
- `before-delivered` write failure: COMMITTED + PENDING, 외부 효과는 이미 실행됐다. recovery 후 외부 효과는 2건이었다.
- `before-state-PUBLISHED` failure: COMMITTED + DELIVERED. recovery는 처리할 작업을 발견하지 못했다.
- Receipt/commit audit/outbox insert 각각에 QA wrapper exception 및 native SQLite trigger RAISE(ABORT)를 적용했다. **commit 대상 DB 변경은 전부 rollback**됐다. 장애 제거 후 PREPARED에서 commit할 수 있었다.
- Prepared audit failure: reservation은 남고 audit는 없는 상태로 recovery가 commit했다. Terminal commit audit는 생성되지만 원 prepared audit는 복원되지 않는다.
- **Live/recovery race:** 원 executor를 PREPARED 뒤 대기 → 별도 process의 recovery가 같은 operation을 commit/PUBLISHED → 원 executor 재개. 원 CAS failure branch가 **PUBLISHED record를 ABORTED로 덮어썼다**. Canonical revision/history/receipt/outbox는 commit을 나타내는데 retry는 ALREADY_ABORTED를 반환했다.
- Exact retry의 ReceiptId/ReceiptHash/committed instant는 유지됐다. 다만 최초 receipt.Status=PUBLISHED, DB/retry=COMMITTED였다. 시각 문자열은 `2026-10-02T12:48:31.1796308Z` → `2026-10-02T21:48:31.1796308+09:00`로 바뀌었다. **같은 instant이며 시각 데이터가 소실된 것은 아니다**. 그러나 반환 시각을 ComputeReceiptHash의 포맷으로 재계산하면 원 hash와 일치하지 않는다.

### 3.6 Startup, migration and actual network isolation

7777이 비어 있음을 확인하고 QA 소유의 exact Server process를 시작/종료했다. 기존 사용자 Server는 중지하지 않았다.

- Fresh normal startup: Listening / World clock / Server ready까지 진행됐고 quit으로 정상 종료됐다. **default pipeline DB가 생성되지 않았다**.
- Restart: `StartupRuntime/war_economy_pipeline.db`에 exact candidate가 만든 PREPARED를 배치했다. 일반 시작은 gameplay READY에 도달해 TCP client를 받아들였다. 종료 후에도 **PREPARED, revision/receipt/outbox 없음**이었다.
- `--run-reconciler`는 명시적 CLI branch에서만 실행된다. 일반 startup에는 recovery completion/admission gate가 없다.
- Bad version-0 schema (`ProbeAggregates(Bogus)`): migration은 user_version=1, INITIALIZED 성공. 실제 실행에서는 no such column: ProbeRevision.
- user_version=1인데 tables가 없는 경우: INITIALIZED 성공, 실행 시 no such table: OperationRecords.
- user_version=999: INITIALIZED 성공, 미래의 unknown schema를 거절하지 않음.
- 중도 DDL failure (`OperationRecords` view 사전 생성): migration 예외, **version=0, 시작 전의 view만 유지**. 새 DDL은 transaction rollback됐다. 이 atomic migration rollback은 정상임을 확인했다.
- Invalid SQLite file: InitializeDatabase는 SQLITE_NOTADB=26을 반환했다. 조용히 초기 데이터를 다시 생성하지 않았다. 그러나 일반 startup은 이 initialization 자체를 호출하지 않는다.
- `PacketHeader` 전체, 실제 `TcpNetworkServer.HandlePacket`, probe/coordinator 참조를 조사했다. probe header/case는 없다. Always-false helper만 isolation 증거로 사용하지 않았다.
- 실제 7777 socket에 undefined ushort header=65535 + valid probe-shaped JSON frame을 보내 receive/dispatch를 거쳤다. Restart DB의 operation/aggregate는 변하지 않았고 NETWORK_ATTACK operation도 생성되지 않았다. 기존 header에 probe routing이 없음은 정적으로 확인했다.
- **이 좁은 PASS는 Production authentication, 다른 기존 gameplay handler의 안전성, 다른 기능의 DB integration을 인증하지 않는다.**

## 4. Defects requiring correction

以下の QA-PIPELINE ID はこの報告内の local finding ID。Master の既存 defect ledger を変更/close/置換しない。9 High / 3 Medium。

### QA-PIPELINE-001 — Incomplete / caller-controlled operation fingerprint

- **Severity:** High
- **Requirement:** ADR-001 INV-OP-002 / AC-OP-02; SRS-NFR-004/007 foundation.
- **Location:** `WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:35`; `.../Coordinator/PipelineTransactionCoordinator.cs:93`.
- **Reproduction:** section 3.1 / `results.json → fingerprints`.
- **Expected:** same ID must bind the same actor/type/scope/expected revision/profile/semantic payload. Changed fields reject before returning receipt or causing effects.
- **Actual:** the original successful receipt is returned for different scope/actor/revision/profile; a forged supplied hash bypasses payload collision rejection.
- **Root cause:** stored hash is only PayloadJson hash and supplied PayloadHash is trusted. The durable identity fields are not compared.
- **Required fix:** server computes/validates a deterministic typed envelope fingerprint covering the semantic input and independently checks immutable identity fields. Exact retries keep stable receipts; mismatched type/actor must not reuse them. Define payload serialization/version explicitly. Do not add new gameplay operation types to this scope.

### QA-PIPELINE-002 — Corrupt / incomplete PREPARED auto-commit

- **Severity:** High
- **Requirement:** ADR-001 AC-PERSIST-03; ADR-004 durable recoverable input; SRS-NFR-004/006 foundation.
- **Location:** `.../Recovery/RecoveryReconciler.cs:73` and `:101`.
- **Reproduction:** section 3.4, `tamper-*` evidence.
- **Expected:** validate complete typed prepare package, immutable identity/hash, actor/profile and expected revision before autonomous replay. Invalid package never gets success/commit.
- **Actual:** 11/13 modified packages committed, including empty/invalid payload, invalid hash, altered operation type and altered scope/revision.
- **Root cause:** only nonblank PayloadHash/ProbeScopeId and current revision equality are checked.
- **Required fix:** validate recovered package through the same complete identity/type/input rules as execution; retain a trusted prepare-integrity boundary and fail closed/repair or abort appropriately on inconsistency. Recomputing JSON-only hash is insufficient to bind scope/actor/profile/revision.

### QA-PIPELINE-003 — Live execution / recovery can overwrite committed truth as ABORTED

- **Severity:** High
- **Requirement:** SRS-NFR-004/007; ADR-001 stable operation result; ADR-004 canonical commit monotonicity.
- **Location:** `.../Coordinator/PipelineTransactionCoordinator.cs:214`; `.../Storage/OperationJournal.cs:84`; `.../Recovery/RecoveryReconciler.cs:132`.
- **Reproduction:** `recovery_race_check.py`; `results.json → live-vs-recovery`.
- **Expected:** after recovery committed this same operation, original executor must resolve to the durable receipt, not abort a committed operation.
- **Actual:** PUBLISHED → ABORTED while revision/history/receipt remain committed; retry returns ALREADY_ABORTED.
- **Root cause:** CAS failure unconditionally aborts operation; state UPDATE has no expected-state guard or recovery execution ownership. PREPARED is not proof that original execution has stopped.
- **Required fix:** recovery execution fencing/ownership, conditional monotonic journal transitions and re-read of canonical receipt/history on CAS loss. Only genuinely uncommitted reservations may abort. State semantics must hold even if a recovery tool/process is invoked concurrently.

### QA-PIPELINE-004 — No consumer dedup contract for at-least-once external effect

- **Severity:** High (foundation gap; no implemented gameplay consumer duplication asserted)
- **Requirement:** ADR-004 publication contract; SRS-NFR-004/006/007 foundation.
- **Location:** `.../Coordinator/PipelineTransactionCoordinator.cs:27`, `:279`; `.../Recovery/RecoveryReconciler.cs:197`.
- **Reproduction:** `kill-after-effect`, `default-dispatch-duplicate`; same identity in two durable effect records.
- **Expected:** retries can deliver twice, but canonical semantic effect must be idempotent under an explicit consumer identity/dedup contract.
- **Actual:** revision stays 1 but external consumer applies twice. Interface is only `bool DispatchEffect(entry)`; Default dispatcher invokes callback and reports true, with no durable consumer acceptance/dedup proof.
- **Required fix:** define stable effect identity (e.g. existing OutboxId with operation/effect binding), immutable effect payload fingerprint and consumer-specific atomic dedup + effect/result contract or demonstrably idempotent state application. Consumer retry must return the same outcome. Do not implement Trade/Tax or prescribe generic two-phase commit here. If this slice has no real consumer, explicitly leave external semantic safety unproven and provide a validating dedup consumer test contract.

### QA-PIPELINE-005 — FAILED outbox permanently excluded from recovery

- **Severity:** High
- **Requirement:** ADR-004 forward publication recovery; SRS-NFR-004/006 foundation.
- **Location:** `.../Storage/PublicationOutboxStore.cs:68`, `:87`; `.../Recovery/RecoveryReconciler.cs:189`.
- **Reproduction:** `writefail-dispatch-throws` and `writefail-before-dispatch`: exception → FAILED; restart pending=0 and no retry. The latter has zero external effects, demonstrating undelivered publication remains abandoned.
- **Expected:** retryable delivery errors remain recoverable; terminal failures have an explicit repair/operator path and cannot silently disappear.
- **Actual:** COMMITTED / FAILED is abandoned. GetPendingEntries filters PENDING only.
- **Required fix:** distinguish retryable/terminal failure, durable retry schedule and attempt history, bounded retry/backoff or explicit repair classification; reattempt transient FAILED entries without reapplying canonical CAS.

### QA-PIPELINE-006 — DELIVERED / COMMITTED split never converges

- **Severity:** High
- **Requirement:** SRS-NFR-004; ADR-004 decision/publication convergence.
- **Location:** `.../Coordinator/PipelineTransactionCoordinator.cs:291`; `.../Recovery/RecoveryReconciler.cs:208`.
- **Reproduction:** `kill-after-delivered`, `writefail-before-state-PUBLISHED`.
- **Expected:** successful effect receipt and publication marker converge after restart, without repeating completed semantic effect.
- **Actual:** MarkDelivered autocommit succeeds; crash/failure before UpdateState leaves COMMITTED + DELIVERED. Subsequent recovery finds no work.
- **Required fix:** locally atomically persist delivery acknowledgement/publication state when appropriate, and/or reconcile already-delivered entries against operation state from durable evidence. This addresses two local DB marker writes, not the external-effect atomicity gap in QA-PIPELINE-004.

### QA-PIPELINE-007 — Ordinary startup has no bootstrap/recovery admission barrier

- **Severity:** High
- **Requirement:** ADR-001 AC-PERSIST-03; SRS-NFR-004/006/007 foundation; mandatory startup ordering.
- **Location:** `WarEconomyMod/Source/Server/Program.cs:85`, `:103`, `:121`.
- **Reproduction:** `startup-fresh.server.log`, `startup-restart.server.log`; before/after DB in results.
- **Expected:** schema/config/integrity and pending-state recovery gates finish, or fail closed, before admission of later canonical mutations.
- **Actual:** fresh startup never creates pipeline DB; restart leaves PREPARED unchanged while server accepts TCP clients and runs old gameplay handlers.
- **Required fix:** integrate initialization/recovery/repair disposition into normal server lifecycle with explicit admission readiness. Standalone CLI `--run-reconciler` is not an autonomous startup/background recovery implementation. Keep probe inaccessible from gameplay; do not expand domain scope while wiring infrastructure readiness.

### QA-PIPELINE-008 — Schema version is trusted without schema validation

- **Severity:** High
- **Requirement:** ADR-001 AC-PERSIST-03; SRS-NFR-006 foundation.
- **Location:** `.../Data/Migrations/PipelineSchemaMigration.cs:14`, `:30`.
- **Reproduction:** `migration-bad-v0`, `migration-broken-v1`, `migration-future-v999`.
- **Expected:** incompatible/missing table/column/index schema or future version blocks canonical admission with clear error; partial migration never advances to usable schema.
- **Actual:** malformed v0 table is retained by IF NOT EXISTS and promoted to v1; missing v1 tables / future version are accepted. integrity_check=ok does not catch logical schema incompatibility.
- **Required fix:** reject unsupported future schema; validate expected schema/constraints before readiness and before/after migration. Preserve tested atomic DDL rollback; do not silently replace or reseed corrupt state.

### QA-PIPELINE-009 — Production durability wording exceeds default WAL/NORMAL policy

- **Severity:** High for canonical durability contract; no actual power-loss data loss reproduced
- **Requirement:** SRS-NFR-006; ADR-004 durable commit boundary.
- **Location:** `.../Data/SqliteDatabaseContext.cs:12`, `:49`; `.../Coordinator/PipelineTransactionCoordinator.cs:255`; A report durability statements.
- **Reproduction:** `metadata-normal`, developer battery: synchronous=1. Only QA explicit context override showed synchronous=2.
- **Expected:** canonical durability guarantee states its failure model and uses a matching verified production policy.
- **Actual:** normal context always defaults to NORMAL, while report describes commit as irreversible and mixes NORMAL/FULL without a demonstrated production profile selection.
- **Required fix:** separate benchmark/test durability policy from canonical production policy, validate effective connection settings and state the accepted failure model. If acknowledged canonical commits must survive system/power failure, use a policy justified for that guarantee (WAL/FULL is the relevant candidate), subject to storage support and validation. Do not claim power-loss safety from process-kill tests.

### QA-PIPELINE-010 — Concurrent exact retry escapes as UNIQUE exception

- **Severity:** Medium
- **Requirement:** ADR-001 AC-OP-01; stable retry foundation.
- **Location:** `.../Coordinator/PipelineTransactionCoordinator.cs:93`, `:152`; `.../Storage/OperationJournal.cs:53`.
- **Reproduction:** `same-id-race`: 10 matching requests; 1 commit, 9 SQLite UNIQUE exceptions.
- **Expected:** atomic operation reservation identifies exact duplicate/conflict and returns durable receipt or explicit in-progress outcome.
- **Actual:** lookup-then-insert race throws; caller cannot interpret it as stable duplicate receipt without additional logic.
- **Required fix:** atomic uniqueness arbitration followed by complete fingerprint comparison and state/receipt resolution. Do not merely swallow all constraint exceptions or declare success.

### QA-PIPELINE-011 — Storage error is misreported as stale CAS; error/outcome policy absent

- **Severity:** Medium
- **Requirement:** SRS-NFR-004/006 foundation; error diagnosis and retry contract.
- **Location:** `.../Storage/ProbeAggregateStore.cs:54`; `.../Coordinator/PipelineTransactionCoordinator.cs:88`, `:206`.
- **Reproduction:** `cas-storage-error` → STALE with expected=actual=0; `busy-lock` → raw SQLITE_BUSY after 33.314s.
- **Expected:** distinguish actual revision conflict from SQLITE_BUSY/LOCKED/constraint/I/O/commit uncertainty; identify when durable operation query is required.
- **Actual:** initial insert catches every SqliteException as CAS loss. Other DB errors escape without a pipeline-level result/query policy.
- **Required fix:** narrow error handling to proven concurrency cases, retain original storage diagnostics, define bounded retries and safe durable-state resolution of ambiguous completion. Never report a committed operation as aborted solely because a response/publication write failed.

### QA-PIPELINE-012 — Receipt is not represented canonically across reload

- **Severity:** Medium
- **Requirement:** ADR-001 stable receipt contract; SRS-NFR-004 foundation.
- **Location:** `.../Storage/CommitReceiptRepository.cs:63`; `.../Models/PipelineProbeModels.cs:72`; `.../Coordinator/PipelineTransactionCoordinator.cs:293`.
- **Reproduction:** `receipt-wire-stability`.
- **Expected:** immutable receipt fields/hash are reproducible after reload; mutable publication status, if separate, has clear semantics.
- **Actual:** DateTime.Parse converts persisted UTC to local representation; recomputing receipt hash from returned O-format date fails. First response says PUBLISHED although persisted receipt says COMMITTED.
- **Required fix:** canonical UTC representation and deterministic receipt hash input; distinguish immutable commit receipt from mutable operation/publication status, or persist/respond consistently. ReceiptId/hash already remain stable; retain that working property.

## 5. SQLite durability / locking interpretation

| Setting | Actual |
|---|---|
| journal_mode | WAL |
| synchronous, normal candidate context | NORMAL = 1 |
| synchronous, explicit QA override | FULL = 2 |
| busy_timeout | 5000 ms |
| Provider DefaultTimeout | 30 s |
| Default actual transaction IsolationLevel | Serializable |
| Connection cache | Shared |
| Canonical DB transaction | CAS/history + operation COMMITTED + receipt + commit audit + outbox insert; tx.Commit is the logical decision boundary |
| Outside that transaction | PREPARED and its audit; external dispatch; MarkDelivered; PUBLISHED update |

Microsoft.Data.Sqlite retries busy/locked errors up to the command/provider timeout. Therefore PRAGMA busy_timeout=5000 is **not evidence of a 5-second end-to-end request bound**; the measured 33.314s failure is consistent with the provider's separate timeout layer. [Microsoft database error/timeout documentation](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/database-errors)

The default Serializable transaction and single-writer locking serialize this candidate's DB writes; separate process CAS tests and rollback evidence support the measured atomic subset. These do not serialize earlier operation identity lookup/PREPARED insertion or external effects. [Microsoft SQLite transaction documentation](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions)

WAL/NORMAL preserves consistency and durability across application-process crash, but a committed transaction can be lost after power/system failure. WAL/FULL adds commit WAL synchronization. The report's hard-kill tests only establish application-process behavior; storage/power-failure certification was not performed. [SQLite synchronous policy](https://www.sqlite.org/pragma.html#pragma_synchronous)

FULL is selectable by a context property; this alone does not prove a Production FULL policy. A report mentioning NORMAL/FULL must specify which mode ran each battery. This independent boundary battery used the normal/default context; FULL was measured as an explicit metadata check.

## 6. Audit / convergence details

- Receipt uniqueness by OperationId and history uniqueness by scope/revision worked in tested different-ID CAS competition.
- Commit audit/receipt/outbox records did not survive pre-commit kills individually; all committed records survived the tested post-commit process kill.
- Prepared audit insert is not atomic with PREPARED reservation. Recovery can produce a terminal commit audit without a prepared audit. The actor is still in OperationRecords; this is **not proof that original actor identity is lost**.
- No runtime insertion of `PROBE_OUTBOX_PUBLISHED` was found; it is only listed as a model comment. Publication acknowledgement is not represented as a dedicated immutable audit event.
- A default dispatcher with no OnDispatched consumer does no actual external publication and returns true. Passing the developer battery with this default cannot establish consumer effect dedup or real subscriber acknowledgement.
- Receipt/audit/outbox convergence depends on durable decisions, not on assuming that a bool return proves external semantic completion. Publication receipt identity, consumer idempotency and terminal repair disposition must be part of the infrastructure contract.

## 7. Architecture concerns and regression risks

1. Preserve the successful **single local DB decision transaction**; fix identity/reservation/recovery/publication contracts around it.
2. PREPARED rows plus revision CAS are not an execution lease. A live operation and recovery must not compete without ownership/fencing and monotonic state transitions.
3. Outbox at-least-once delivery is acceptable only with an explicit safe consumer contract. Do not equate no repeated ProbeRevision with no repeated economic effect.
4. Do not wire future gameplay commands into this infrastructure before normal startup readiness and invalid-package fail-closed behavior are corrected.
5. Probe-specific autonomous replay must not be generalized to every gameplay transaction. Later commands need their own complete durable input/authority/policy and repair rules under accepted ADRs.
6. ActorId in the internal request is fixture metadata here. This test does not prove authenticated actor binding. Existing authentication/authority gaps remain separate.
7. Do not infer complete ownership, materialization, InventoryRevision or Tactical publication safety from this policy-neutral probe. No such claim was tested.

## 8. Test quality review / required regression additions

Developer battery **13/13 PASS** is reproducible but insufficient for this work order:

- Idempotency tests vary PayloadJson only, not scope/actor/revision/profile/type or caller-supplied hash.
- Same-ID concurrent lookup/insert is not tested.
- Its 25 Tasks are useful positive evidence; the independent OS-process tests confirm the successful different-ID CAS behavior.
- In-process rollback and only two developer hard-crash points omit delivered-before-published and several actual commit insert boundaries.
- Recovery tests do not validate package completeness/hash/type/identity tampering or live-vs-recovery competition.
- The outbox replay test checks revision, not an external consumer's semantic effect.
- Isolation test calls an always-false helper; actual routing must be reviewed/tested separately.
- The battery constructs its own DB context and calls recovery explicitly; it does not run ordinary startup.
- PRAGMA integrity_check and user_version do not validate logical schema or production readiness.

Required regression gates for the replacement frozen candidate:

1. Complete envelope collision matrix including PREPARED, COMMITTED, PUBLISHED and ABORTED states; server-verified payload hash.
2. 25+ independent processes plus same-ID exact/conﬂict retries; typed stable outcomes and one canonical effect.
3. All measured OS-kill checkpoints retained, including native commit bracket and externally successful delivery before marker.
4. Invalid/tampered PREPARED never completes; recovery ownership and committed-state monotonicity under live/recovery concurrency.
5. Consumer dedup proven by semantic effect count, stable effect receipt and duplicate payload mismatch rejection.
6. Transient FAILED, delivered-with-unpublished and DB marker failure converge without canonical re-CAS or duplicate consumer effect.
7. Fresh/restart ordinary entrypoint admission gate; invalid future/malformed schema fail closed and operator diagnostics preserved.
8. Effective production durability profile and provider timeouts measured; receipt canonical UTC/hash verification after reload.
9. Internal probe remains unreachable from actual gameplay dispatcher and material revisions remain untouched.

These are correction/acceptance recommendations. QA did not implement the fixes.

## 9. Evidence index and execution limitations

Primary machine-readable results:

- [results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/results.json)
- [Frozen source/artifact manifest](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/freeze-before.json)
- [Dependency versions](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/package-versions.json)
- [Independent QA harness source](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/Harness/Program.cs)
- [Boundary/concurrency/tamper runner](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/run_checks.py)
- [Startup/migration/dependency follow-up](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/supplement_checks.py)
- [Recovery race reproduction](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/recovery_race_check.py)
- [Independent developer battery result](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/developer-battery.json)
- [Fresh startup log](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/startup-fresh.server.log)
- [Restart/admission log](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/startup-restart.server.log)
- [Isolated Production build log](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/isolated-production-build.txt)

각 request JSON, checkpoint signal/PID, OS-process stdout, effect JSONL, independent SQLite DB를 같은 Evidence 폴더에 보존했다. `results.json` key가 본문의 test name과 일치한다.

QA observers는 existing interfaces를 forward하고 checkpoint 대기 또는 지정 failure만 주입했다. Production method/IL을 patch하거나 수정된 Production source를 실행하지 않았다. 마지막 follow-up에서 QA dispatcher를 candidate DefaultPublicationOutboxDispatcher callback을 forward하도록 바꾸고 같은 중복 window를 다시 확인했다. 앞선 시험의 interface consumer와 이 direct-default follow-up을 구분해 보존했다. Candidate DLL은 동일했다.

초기 runner에서 signal file 생성 직후 JSON을 읽는 QA 측 race로 한 번 중단됐다. 해당 QA child를 종료하고 완전히 기록된 signal만 읽도록 observer/controller를 고친 후 미완료 cases를 이어서 실행했다. 완료한 candidate 결과를 수정하거나 이 QA runner 오류를 candidate 결함으로 세지 않았다. `resume_checks.py`와 `kill-before-commit-attempt2.db`에 이 이력이 남아 있다.

모든 QA가 소유한 Server/Harness process는 종료했다. GUI/Computer Use는 수행하지 않았다. 실제 power loss, 최종 gameplay domain transaction, authenticated remote production command, storage hardware fsync 보장은 이 검증의 완료 주장에 포함하지 않는다.

## 10. Final recommendation

**FAIL.** PIPELINE_PROBE_CAS는 현재 정확한 후보에서 올바른 E2 foundation으로 입증되지 않았다. 성공한 DB atomic commit/CAS subset은 유지하되, complete operation identity, PREPARED integrity, recovery concurrency, outbox consumer/retry/convergence, ordinary startup admission 및 schema validation을 수정한 새 frozen candidate를 제출해야 한다. Production durability/receipt 표현 계약도 명확히 해야 한다.

실제 Trade/Tax/inventory/Tactical/ownership 구현으로 scope를 확대하는 권고가 아니다. 이번 slice의 결함을 먼저 닫고 동일한 독립 failure battery를 통과시킨 뒤 Master가 다음 단계를 결정해야 한다.
