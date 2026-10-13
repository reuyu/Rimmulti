# QA Production Transaction Pipeline 01 — REV5 Independent E2

```yaml
Work Package: WP-QA-PROD-TRANSACTION-PIPELINE-01-REV5
Release: queued Work Order activated by Master delivery
Reviewer: GPT-6.1 Sol / Independent QA & Architecture Reviewer
Date: 2026-10-06 (Asia/Seoul)
Target: Production_Transaction_Pipeline_Slice_01_REV5.md
Verdict: FAIL
Production modification or rebuild: NONE
Production freeze: 353 files before / 353 files after / 0 changes
Master ledger / architecture status modified: NO
```

## 1. Master 판정 요약

**최종 판정: FAIL.** 이전 escaped-surrogate/exponent 오류와 실제 service lifetime 결함은 해소됐다. 정상 COMMITTED/ABORTED 이력 및 cross-principal operation identity도 복구된다. 그러나 mandatory historical observed-revision tamper와 typed audit semantics 검증은 통과하지 못했고, 추가 V6 schema identity-collation 변조도 READY로 승인됐다.

| 대상 | 독립 권고 | 근거 |
|---|---|---|
| QA-PIPELINE-001 | **CLOSED 권고 — 이번 입력 계약 범위** | 기존 5개 오류 모두 INVALID_REQUEST / durable OperationRecord 0; exact JSON regressions 유지 |
| QA-PIPELINE-007 | **STILL FAILING / OPEN** | plausibly rewritten historical observation, false status/reason, incomplete typed audit fields가 READY |
| QA-PIPELINE-013 | **CLOSED 권고 — 실제 final service lifecycle 시험 범위** | 6/8/13초 및 CAS/audit/commit/WAL/lock에서 writer 종료 전 final return 없음; actual Main도 통과 |
| QA-PIPELINE-008 | **historical V5 closure 유지 / current V6 schema blocker OPEN 권고** | 기존 schema 공격 39개 차단; 새 NOCASE key-collation 공격 2개는 READY 및 actual EXE LISTEN |
| QA-PIPELINE-019 | **기존 closure 유지 — admitted identity/derivation** | delimiter/Unicode/long/control 재검증 통과; canonical ReceiptId/EventId swap은 복구 거절 |

이번 결과로 **ADR-001 Foundation을 직접 승인하지 않는다.** closure와 차단 결함은 Master에 대한 권고이며, 공식 상태를 직접 변경하지 않았다. candidate를 조용히 고치거나 다시 빌드하지 않았다.

## 2. Exact provenance / package

증거 루트: [PIPELINE01-REV5-20261006](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006).

Production을 동결한 뒤 Release package를 QA Candidate에 복사했다. QA harness만 actual Release DLL을 reference하여 빌드했다. 실제 coordinator/repository/SQLite 및 actual Program.Main을 호출했다. wrapper는 원래 repository에 위임하면서 observer/barrier/I/O-like failure만 제공한다. QA가 commit, receipt, recovery 성공을 대신 구현하지 않는다. SQL/schema 변조는 QA-owned DB에서만 실행했고 terminal triggers를 제거한 공격은 원래 trigger SQL을 그대로 복원한 뒤 검증했다.

### 바이너리와 manifest

| 항목 | 독립 검증값 |
|---|---|
| Server DLL SHA-256 | `1143AE62FD74F0C93F0504B48C1501D5153F40C2E903BD4D69BA9BE1E6983479` — Work Order 일치 |
| Server MVID | `a5cba4c3-1e2f-4a19-a35c-0241ccf12e81` — Work Order 일치 |
| Server EXE SHA-256 | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |
| Server PDB SHA-256 | `754752E0E97E5FA7ACC09B5568B7780C86CB3C57CCD8E5F82CC8C3CC31BB90F1` |
| Common DLL SHA-256 | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` |
| Common MVID | `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` |
| Common PDB SHA-256 | `5119FE41A0FD3BB6B6DCA299B85FD3EEF0F91D4FB7B1AC77DAEDA762E9B2D0F0` |
| E1 results SHA-256 | `4B44749D3EBD2DFF0ABEE881620BE8E4A311B6260A233C11D3D2E713B62C9AFB` |
| **현재 manifest filename** | **`RELEASE_MANIFEST_PIPELINE_REV5.json`** — 현재 파일 존재, stale 아님 |
| Manifest SHA-256 | `D609795D8B50ED98850B8C73E951EA7F8E9B21B6193E815CF4890B9E2BB7D9E6` |
| Manifest contents | WorkPackage REV5 / SchemaVersion6 / expected signature / 5 binary artifacts + 6 modified-source entries + E1 entry; **12/12 actual SHA match** |
| Native/runtime | .NET 8.0.10 / SQLite 3.41.2 |
| Packages | Microsoft.Data.Sqlite 8.0.10 / SQLitePCLRaw 2.1.6 / Newtonsoft.Json 13.0.3 |
| DB identity | application_id 1463898693 (`WARE`) / user_version6 |
| Independent V6 signature | `64BDB62037D70303D7F2AE15D39FC7E7DFD9F01021B5E0AA0709A51FA507E721` |

Server/Common DLL를 실제 QA `Harness/bin/Release/net8.0`와 `HarnessExt/bin/Release/net8.0`에서 로드한 SHA/MVID를 확인했다. actual Server.exe는 같은 frozen package의 QA copy에서만 실행했다. candidate EXE/PDB와 source를 Production에서 재빌드하지 않았다.

Server PDB document **20/20**, Common PDB document **25/25** actual checksum match. Server CodeView/PDB GUID는 양쪽 `6b39adbc-ea0a-4b50-a980-c6e09aa5725c`; Common은 `f46ba950-aebf-4e2a-9a7c-b346c7519b51`. 현재 바이너리/source lineage가 확정됐다.

원본 Release DB/WAL/SHM/test/log/tmp residue는 없다. manifest가 다루지 않는 native/dependency file도 QA 전체 package hash로 고정했다. 정식 manifest는 32-file full package inventory라고 과장하지 않는다. 정확한 현재 filename/contents/SHA와 그 entry들의 일치를 확인했다.

### 수정 소스 SHA-256

경로 기준 `WarEconomyMod/Source/Server/`.

| 파일 | SHA-256 |
|---|---|
| `Pipeline/Models/PipelineProbeModels.cs` | `E545A2689898DBECF57D7FD52C257290352CFC51A312F71A0A319BF415424182` |
| `Pipeline/Coordinator/PipelineTransactionCoordinator.cs` | `9F987535E8B84C4F812884F53EFF34914555CE45A8F042769C0F8AD24E2D3456` |
| `Pipeline/Data/Migrations/PipelineSchemaMigration.cs` | `27273373379CA15ADB48A0C7EEE241E699663D324F21E6336845C69E9CF374D5` |
| `Pipeline/Recovery/RecoveryReconciler.cs` | `92B1B024CF6D3A67D8996D0B8D91FA523CEA9C74EACC6EE5C6B80F3390364EAC` |
| `Pipeline/Storage/ProbeAggregateStore.cs` | `B1C34B4F57B4D1A4508FF59B318B6A9A8249217C360816141F842A9FF4C1B149` |
| `Program.cs` | `8A4013701A1E8DC1B915E5C383560CD9D8C35E2134C376413CC584FA59F6BF2C` |

증거: [provenance-complete.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/provenance-complete.json), [server-pdb-lineage.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/server-pdb-lineage.json), [common-pdb-lineage.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/common-pdb-lineage.json), `runtime-metadata.json`, `extension-runtime-metadata.json`.

## 3. 독립 측정 요약

| 시험 | 실제 결과 | 판정 |
|---|---|---|
| 기존 5개 typed input failures | 5 INVALID_REQUEST / OperationRecord 0 | PASS |
| exact small/high-precision/equivalent/duplicate/trailing/depth/mantissa | distinct values 보존, equivalent retry 정상, unsupported inputs durable0 | PASS |
| 25 OS-process CAS, same expected revision | 1 SUCCESS / 24 STALE_REVISION, actual EXE restart READY/LISTEN | PASS |
| 12 OS-process same ID | 1 SUCCESS / 11 ALREADY_COMMITTED | PASS |
| same stream, 8 rounds × 6 OS processes | 8 SUCCESS / 40 STALE, revision/Seq1..8, actual restart READY/LISTEN | PASS |
| 2 scopes, natural 7 COMMITTED + 2 ABORTED | READY/LISTEN, before/after canonical unchanged | PASS |
| P1/SAME vs P2/SAME, same/different scopes | valid cases READY/LISTEN | PASS |
| existing valid composite parents 간 receipt/event/history/audit principal swap | FK 자체는 valid, recovery 4/4 거절 | PASS |
| envelope mutation, 2 states × 11 fields | 22/22 거절 | PASS |
| canonical receipt/event swap + recomputed child hash | 2/2 거절 | PASS |
| plausible historical observed revision rewrite | **3/3 READY**, actual EXE LISTEN | FAIL |
| status / reason / separate FailureReason 변경 | **READY**, 일부 actual EXE LISTEN | FAIL |
| typed audit의 다른 field 변경/삭제 | 여러 **READY** | FAIL |
| conventional V6 schema mutants | 39/39 거절 | PASS |
| V6 key column collation → NOCASE | **2/2 READY/LISTEN**, actor/scope identity 합쳐짐 | FAIL |
| mixed-state startup canaries 3회 | durable row/schema mutation0 | PASS |
| actual nonempty v1–v5 | 모두 fail closed / canonical state 보존 | PASS |
| active writer 6/8/13초 | caller UNKNOWN, final shutdown은 writer 종료 후 반환 | PASS |
| CAS/audit/precommit/post-WAL 8초 barrier | coordinator 유지, final return 때 writer dead / post-dispose calls0 | PASS |
| SQLite lock 약13초 | UNKNOWN 후 actual Dispose는 resolution까지 대기 | PASS |
| actual Main, 12초 active operation quit | Main return 때 writerAlive=false, IsDisposed=true | PASS |
| UNKNOWN committed / uncommitted | original receipt ALREADY_COMMITTED / clean SUCCESS, duplicate0 | PASS |
| real hard-kill 8 cuts | precommit graph0 / durable graph1, retry 안정 | PASS |
| terminal SQL 2 states × 6 shapes | 12/12 nativeSQLite19, row unchanged, mixed restart 정상 | PASS |
| storage typing / incarnation / WAL FULL / scope isolation | 이전 좁은 regression 유지 | PASS |
| Production freeze | 353 / 353, diff0 | PASS |

전체 raw result와 집계는 [execution-summary.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/execution-summary.json)에 있다. E1의 21/21을 독립 gate 통과 수치로 재사용하지 않았다.

## 4. QA-PIPELINE-001 — 입력 오류 및 exact JSON

actual Release `ExecuteProbeCas`로 다음을 재현했다.

- `{"\ud800":1}`
- `{"a":"\ud800"}`
- `"\udc00"`
- `"\udc00\ud800"`
- `1e-2147483648`

**모두 INVALID_REQUEST, durable OperationRecord0.** storage-error misclassification은 사라졌다. escaped valid surrogate pair는 수락한다. 실제 .NET 문자열의 isolated/reversed UTF-16을 9 fields에 주입한 27개 admission도 모두 INVALID_REQUEST.

이전 mathematical collision 4쌍을 actual same-OperationId retry로 재검증했다. 첫 SUCCESS 뒤 semantically distinct payload는 모두 COLLISION_REJECTED, 기존 successful receipt를 반환하지 않는다.

- `1e-29` / `-1e-29`
- `1e-40` / `0`
- `1.00000000000000000000000000001` / `1.00000000000000000000000000002`
- `0.123456789012345678901234567891` / `0.123456789012345678901234567892`

`1/1.0/1e0/1E+000` 및 zero spellings는 ALREADY_COMMITTED로 원래 receipt에 수렴한다. root/nested/array-object duplicate, escaped-equivalent `"a"/"\u0061"`, second root/trailing data는 거절한다. whitespace trailing은 수락. ±308 boundary, ±309/overflow rejection, 1,000/1,001 nonzero digit boundary, depth64/65도 재검증했다. JSON batch의 **18 rejection 모두 durable record0**.

total payload byte cap을 새로 인증하지 않는다. 기존 1MiB/4MiB string payload는 여전히 수락되며 이번 closure는 Work Order의 surrogate/exact-number/depth/numeric-limit 계약이다. 후보의 정해지지 않은 크기 제한을 QA가 임의로 요구로 만들지 않았다.

권고: **001 CLOSED**.

## 5. QA-PIPELINE-007 — 해결된 부분

### 정상 자연 생성 mixed 이력

QA가 SQL로 ABORTED를 만들어 baseline을 고친 것이 아니다. actual coordinator로 scope A를 revision4, B를 revision3까지 진행하고 각 revision2 시점에 expected0 request를 제출해 자연 STALE/ABORTED를 생성했다. 7 COMMITTED + 2 ABORTED, success children은 committed당 정확히 1개이며 aborted에는 없다.

이 DB는 normal startup READY 및 actual Server.exe LISTEN; canonical logical state unchanged. 25 independent process의 one-winner/24 losers와 same-stream 8 winner/40 losers DB도 실제 EXE 재시작 통과. REV4의 OldRevision==ExpectedRevision false rejection은 해소됐다.

### Full canonical parent identity

P1/SAME과 P2/SAME을 same scope의 연속 revision으로 commit했다. 다른 scope의 commit/abort 조합도 정상 READY. 추가로 **존재하는 두 valid composite parent** 사이에서 child PrincipalId를 교환했다. receipt/event/history/audit의 모든 swap은 `foreign_key_check` 자체는 clean이지만 semantic recovery가 거절했다. 단순히 UNKNOWN principal을 orphan으로 만든 것만을 identity proof로 사용하지 않았다.

### Fingerprint / canonical child IDs

COMMITTED/ABORTED 각각 PrincipalId, OperationId, ProbeScopeId, ExpectedProbeRevision, OperationType, OperationSchemaVersion, ContentProfileFingerprint, ConfigSnapshotRef, StoreIncarnationId, canonical PayloadJson, RequestFingerprint를 one-field mutate: **22/22 NO READY**. stored fingerprint를 다시 읽어 자기 자신과만 비교하던 결함은 개선됐다.

valid ReceiptId와 EventId를 서로 다른 operation 사이에서 swap하고 receipt hash를 현재 tuple로 정확히 다시 계산해도 **NO READY**. expected IDs가 canonical parent/revision에서 독립 derivation되는 것을 확인했다. 정확 retry의 stored original ID는 유지된다.

## 6. QA-PIPELINE-007 — 잔존 High: 과거 관찰의 자가 정당화

### Reproduction / actual evidence

정상 READY인 mixed fixture의 AAB는 다음 original decision이었다.

```text
PrincipalId=P, OperationId=AAB, Scope=A
ExpectedRevision=0
ObservedRevision=2
FailureReason="STALE_REVISION: expected 0 != actual 2"
A current revision at audit = 4
B current revision at audit = 3
```

QA copy에서 Audit.OldRevision과 DetailsJson.observedRevision을 함께 변경했다. reason JSON과 separate FailureReason도 새 숫자와 일치하게 다시 작성했다. 원래 request/payload/fingerprint, created timestamps, parent count, schema, committed history는 유지했다. terminal triggers는 공격 후 원본으로 복원했다.

| inject | 원래 관찰 | 변조 내용 | actual recovery | actual EXE |
|---|---:|---|---|---|
| historical-earlier | 2 | A의 더 이른 값1 | **READY** | READY/LISTEN |
| historical-later | 2 | A의 더 늦은 값4 | **READY** | READY/LISTEN |
| other-scope-observed | 2 | B의 현재 값3을 A의 observed로 제출 | **READY** | READY/LISTEN |
| column-json-mismatch | 2 | column1, JSON2 | NO READY | harness proof |
| json-column-mismatch | 2 | column2, JSON1 | NO READY | harness proof |

B의3은 A에도 이후 revision3이 존재한다. 이 시험은 숫자의 출처를 protocol이 기록했다는 뜻이 아니라, **다른 scope에서 가져온 그럴듯한 값도 원래 A decision에 연결되지 않은 채 수락된다**는 경계 시험이다. 현재 값의 범위/불일치만으로 원래 관찰2를 증명할 수 없다.

### 원인

위치: [RecoveryReconciler.cs:575](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:575), [RecoveryReconciler.cs:581](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:581), typed details comparison around602.

검사는 `0 <= observed <= currentScopeRevision`, `observed != expected`, `JSON observed == column`뿐이다. request fingerprint는 requested expected revision을 묶지만 **observed decision witness를 묶지 않는다.** root/column 두 값을 함께 바꾸면 서로를 승인 근거로 사용한다. FailureReason도 독립 corroboration으로 검증되지 않는다.

Expected: Work Order §4의 altered historical decision은 genuine original decision과 연결되지 않으면 NO READY.

Actual: schema/count/hash consistency를 보존한 위 변경은 READY; 실제 canonical service와 network도 열린다.

Required fix: original decision의 authoritative witness/순서를 durable하게 정의하고 observation을 그 witness와 검증해야 한다. 예를 들어 결정 당시의 scope history/order와 변경 불가능한 decision provenance를 연결한다. 두 mutable copies를 대조하거나 누구나 다시 계산할 수 있는 hash를 추가하는 것만으로 original observation이 증명되지는 않는다. 구체적 설계는 Master/Dev가 결정해야 하며 QA가 새로운 Production 구현을 대신 만들지 않았다.

이 결함은 generic network client가 DB 파일을 임의 편집할 수 있다는 주장이나 malicious disk administrator 전체에 대한 cryptographic authenticity 인증 요구가 아니다. **명시적으로 요청된 historical decision tamper recovery gate**의 실패다.

## 7. QA-PIPELINE-007 — 잔존 High: typed audit / status 의미 검사 누락

### ABORTED

아래 parseable JSON/column mutation이 모두 READY:

- status=`SUCCESS`
- reason=`WRONG`
- separate OperationRecord.FailureReason=`SUCCESS`
- JSON의 scopeId/principalId/operationId/status/reason 각각 삭제

status/reason/FailureReason 변조 일부는 actual Server.exe에서도 READY/LISTEN. 반면 expectedRevision/observedRevision mismatch, 제공된 principal/op/scope의 잘못된 값, EventType 변조는 거절한다. 검사되는 일부 field의 성공을 전체 typed contract 성공으로 확대하지 않았다.

위치: [RecoveryReconciler.cs:602](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:602) 이후 ABORTED details 검사. required expected/observed는 대조하지만 **status/reason을 읽지 않는다**. IDs는 `TryGetProperty && mismatch`이어서 없으면 검사를 통과한다. FailureReason은 이 semantic validation의 입력에 포함되지 않는다.

Expected: STALE_REVISION terminal failure의 reason/status/expected/observed/parent가 정합하고 required key가 모두 존재해야 한다.

Actual: success라고 표시한 reject record, wrong reason, missing parent metadata를 승인한다.

Required fix: required typed fields를 빠짐없이 요구하고 status/reason과 separate FailureReason의 의미를 original decision과 일치시키며 missing/unknown/contradictory typed data는 fail closed한다. 새 JSON serializer를 호출하는 것만으로 검증이 완성되지 않는다.

### COMMITTED

실제로 저장된 DetailsJson의 eventId/principalId/operationId/scopeId/oldRevision/newRevision을 변경하거나 필수 key를 삭제해도 READY. `receiptId`/`fingerprint` 변조 또는 삭제는 거절한다.

- eventId=`WRONG`: READY 및 actual EXE LISTEN;
- principalId/operationId/scopeId=`WRONG`: READY;
- oldRevision/newRevision=999: READY;
- event/actor/scope/old/new required field omission: READY.

위치: [RecoveryReconciler.cs:408](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:408). root object라는 것과 receiptId/fingerprint 두 항목만 검사한다. 같은 writer가 실제로 저장한 다른 typed fields의 semantics를 대조하지 않는다.

Required fix: event reference, full parent/scope, old/new revisions를 expected canonical operation/receipt/event와 연결한다. table columns의 값이 맞더라도 JSON에 서로 다른 사실을 승인해서는 안 된다.

시험 중 추가한 `expectedRevision`은 COMMITTED의 실제 field가 아니라 extra key였다. 해당 extra-key ignored 결과는 false semantic failure의 필수 증거로 계산하지 않았다. 실제 `oldRevision`의 변조/삭제 proof를 별도로 확보했다.

권고: 원래 007의 natural-restart/composite identity/envelope/derived-ID subfindings는 해결됐으나, **historical observation과 typed audit gate가 남아 007 전체는 STILL FAILING**.

## 8. Schema V6 independent verification / current blocker

### 정상 V6와 conventional mutants

independent SQLite introspection으로 tables, columns/type/nullability/PK, composite FK source/target/actions, indexes/order/unique/partial predicates, CHECK literals, triggers, active-incarnation count를 재구성했다. 후보 validator 반환값을 복사한 것이 아니라 [schema-independent-descriptor.txt](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/schema-independent-descriptor.txt)의 SHA를 별도로 계산했고 expected V6와 일치했다.

기존 literal case/escaping/CHECK comments/trigger lookalikes/partial indexes/index order/FK actions/PK/type/nullability/active cardinality, V6 history PrincipalId type/nullability/parent FK까지 **39/39 conventional mutations 거절**. canary 중 실패하는 변조 DB도 logical canonical mutation을 남기지 않았다. 정상 mixed fixture 3회 startup 전후 rows/schema 동일.

actual nonempty legacy v1/v2/v3/v4/v5는 이전 QA run의 진짜 DB를 복사했다. 모두 fail closed, state/schema 보존. actual EXE도 NO READY/NO LISTEN/exit2. fresh V6 및 normal restart는 성공한다.

### 추가 High — NOCASE primary-key 의미를 descriptor가 놓침

QA-owned empty canonical V6에서 다음 두 mutation을 각각 적용했다.

```sql
-- Actual CREATE TABLE 내 선언만 변경; type/PK/FK/index column names는 그대로
OperationRecords.PrincipalId: TEXT NOT NULL -> TEXT COLLATE NOCASE NOT NULL
ProbeAggregates.ProbeScopeId: TEXT PRIMARY KEY ... -> TEXT COLLATE NOCASE PRIMARY KEY ...
```

**둘 다 startup READY와 actual EXE LISTEN.** 실제 의미 차이도 coordinator로 재현했다.

| fixture | request1 | request2 | 결과 |
|---|---|---|---|
| normal BINARY control | actor P, SAME, scope S | actor p, SAME, scope s | **두 SUCCESS**, 두 독립 identity |
| PrincipalId NOCASE | P, SAME, scope S1 | p, SAME, scope S2 | 첫 SUCCESS / 둘째 **COLLISION_REJECTED** |
| ScopeId NOCASE | ONE, scope S expected0 | TWO, scope s expected0 | 첫 SUCCESS / 둘째 **STALE_REVISION actual1** |

canonical fingerprint와 admission은 서로 다른 문자열인데 changed DB key equality가 두 identity를 합친다. 요청값의 소문자 normalization 정책을 새로 만들거나 두 actor/scope를 같은 요구로 해석하지 않았다. baseline control이 실제로 distinct identity를 허용한다.

위치: [PipelineSchemaMigration.cs:953](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:953) column descriptor와 [PipelineSchemaMigration.cs:1002](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs:1002) index_info 사용.

Root cause: table_info는 declared collation을 제공하지 않고 index_info도 key collation을 포함하지 않는다. 현재 descriptor는 name/type/null/PK 및 index column names를 hash하지만 **identity equality semantics를 담지 않는다.** startup canaries에도 case-distinct key probe가 없다. `index_xinfo`로 실제 BINARY/NOCASE 차이를 확인해 evidence에 저장했다.

Required fix: canonical key/index collation 및 필요한 comparison semantics를 descriptor/validation에 포함하고 case-distinct admitted keys가 DB에서도 구별되는 runtime canary를 추가한다. 모든 문자열을 lowercase 처리하여 이 실패를 숨기지 않는다.

**현재 V6 candidate blocker다.** historical V5 008 closure를 Master 승인 없이 변경하지 않는다. 그 closure는 이전에 시험한 V5 범위였고, 이번 결과는 현재 V6 schema gate의 추가 미해결 finding으로 제출한다.

### 보고서 DDL과 실제 DDL의 차이

A 보고서 §2.2의 예시에는 HistoryId AUTOINCREMENT, 별도 history indexes, AuditRecords `(PrincipalId,OperationId,AuditId)` PK가 있다. 실제 동결 V6는 **history PK=(ProbeScopeId,ProbeRevision), Audit PK=AuditId**이며 두 테이블의 principal/op composite FK가 있다. 이번 검증과 independent signature는 실제 frozen DDL 기준이다. 예시 DDL을 실제 구현이라고 재인용하지 않았으며 다음 보고서에서 문서 일치 수정이 필요하다.

## 9. QA-PIPELINE-013 — actual service lifetime

### Observer 방식

actual StartupManager가 만든 coordinator에 transparent actual repository observer를 연결했다. queue/writer/Shutdown 구현은 candidate 그대로다. 별도 timer가 6/8/13초 뒤 barrier를 해제하므로 Dispose 반환에 의존해 barrier를 푸는 잘못된 시험이 아니다. Shutdown 중 매초 writerAlive, IsDisposed, coordinator ownership, readiness, caller completion을 관측했다.

| active cut | hold | final elapsed | final writer | post-final repository calls |
|---|---:|---:|---|---:|
| before-read + 1,205 submissions | 6s | 6,586ms | dead | 0 |
| before-read | 8s | 8,493ms | dead | 0 |
| before-read | 13s | 13,545ms | dead | 0 |
| after-CAS | 8s | 8,468ms | dead | 0 |
| after-audit | 8s | 8,478ms | dead | 0 |
| native pre-commit | 8s | 8,486ms | dead | 0 |
| native post-WAL | 8s | 8,500ms | dead | 0 |

writerAlive 중 final shutdown 미반환, readiness=false, coordinatorRetained=true를 확인했다. caller는 deadline 이후 UNKNOWN. late admission은 거절된다. final Shutdown 이후 IsDisposed=true, pending0, ActiveCoordinator=null. 반복 Dispose/Shutdown도 안전했다.

SQLite lock은 separate connection의 real BEGIN IMMEDIATE로 약13초 유지한 뒤 독립 해제했다. candidate Dispose는 transaction resolution을 기다렸고 final return 때 writer dead, 관측 repository post-dispose calls0, caller terminal. 새 process의 startup/query/retry도 성공해 writer transaction/connection을 붙잡은 채 반환한 이전 실패는 재현되지 않았다. SQLite pool의 모든 idle handle을 제거하는 별도 계약까지 인증한 것은 아니다.

### actual Program.Main

actual Main을 QA working directory에서 실행했다. QA TextReader가 actual service coordinator에 candidate의 기존 SimulatedWriterDelayMs=12000을 설정하고 operation을 제출한 뒤 `quit`를 반환했다.

약2.2초 관측: writerAlive=true, ready=false, coordinatorRetained=true, callerDone=true. **Main은 아직 반환하지 않았다.**

12,021ms 후 Main return: writerAlive=false, IsDisposed=true, ready=false, ActiveCoordinator=null. post-return repository calls0. fake Main/Shutdown으로 대체한 시험이 아니다. world/network의 모든 unrelated background task까지 완성된 service lifecycle이라고 확대하지 않았다.

### UNKNOWN convergence

원래 `(PrincipalId,OperationId,incarnation,profile...)` envelope를 보존했다.

- 각 committed hold 및 lock resolution: receipt query 성공, exact retry **ALREADY_COMMITTED**, 원래 ID/graph 유지;
- 별도 before-read 8초 hold 후 before-CAS I/O failure: caller UNKNOWN이지만 durable graph0, receipt=null, 새 process에서 same-envelope retry **SUCCESS revision1**;
- duplicate business effect0.

UNKNOWN response 자체에는 operation identifiers가 없으므로 호출자는 원래 key를 보존해야 한다. 이번 test는 그 key를 유지했고 queryable identity를 잃지 않았다. 이것을 Production authentication/session protocol 완성으로 해석하지 않는다.

권고: **013 CLOSED**, 위 final shutdown/actual Main/UNKNOWN 경계 범위.

## 10. Regression locks

실제 별도 OS-process/connection으로 CAS25, same-ID12, same-stream48를 실행했다. 각각 1/24, 1/11, 8/40의 예상 outcomes. natural losers까지 durable terminal이며 이번에는 startup convergence도 정상이다.

8 hard-kill cuts: transaction 시작 후 CAS 전, CAS/receipt/event/audit 후, native pre-commit, native post-WAL, actual Execute return 후 응답 전. precommit kill은 operation/receipt/event/audit/history/aggregate 모두0; durable WAL/return cut은 각1. restart는 canonical DB truth만으로 판단했고 exact retry는 새 SUCCESS 또는 original ALREADY_COMMITTED. outer safety kill을 clean shutdown PASS로 계산하지 않았다.

terminal COMMITTED/ABORTED에 UPDATE/DELETE/INSERT OR REPLACE/REPLACE INTO/raw same-key INSERT/UPSERT DO UPDATE, **12/12 nativeSQLite19** 및 rows unchanged. mixed-state restart도 통과한다. constraint/I/O-like failures는 STORAGE_FAILURE, real SQLITE_BUSY5/LOCKED6는 STORAGE_BUSY_RETRYABLE; 잘못된 STALE로 변환되지 않는다.

incarnation null/empty/blank INVALID_REQUEST, 별도-process rotation 뒤 old admitted request INCARNATION_MISMATCH, historical receipt lookup 유지. DTO admission 이후 원본 fields를 바꿔도 actual immutable command effect는 바뀌지 않는다.

actual CreateOpenConnection에서 WAL, synchronous=2/FULL, FK1, recursive_triggers1, 기본 busy_timeout5000/DefaultTimeout5s. pool을 NORMAL로 바꾼 후에도 새 Production-opened connection은 FULL로 복원. long lock profile timeout만 QA에서 연장했다. hardware/power-cut durability는 인증하지 않는다.

019의 기존 4 delimiter/Unicode/long pairs는 8 SUCCESS와 정확 retry. 추가 NUL/colon/CRLF/U+2028/U+001F redistribution의 actual admitted 10 commands 및 10 retries도 정상; generator long revision 경계와 receipt/event domain separation 확인. SHA-256를 수학적으로 절대 무충돌이라고 표현하지 않았다.

## 11. Gameplay / consumer / Startup ordering

fresh/valid mixed DB는 bootstrap → schema/recovery → writer → PIPELINE_READY → TCP listen 순서. current stale-history/schema-collation false READY도 같은 정상 서비스 순서로 진행되므로 **순서가 맞다는 사실이 validation 내용의 결함을 막아주지 않는다.** legacy/거절된 DB는 admission 전 exit2.

PacketHeader/TcpNetworkServer에 probe route가 없고 Main에는 old test/crash CLI dispatcher가 없다. actual EXE에 unknown-header probe JSON을 보내 canonical probe/material row0, old CLI flags는 별도 marker DB unchanged. 이 좁은 isolation은 일반 gameplay authentication completeness의 증거가 아니다.

PublicationEvents는 immutable append-only log이며 consumer/cursor/ACK/PUBLISHED 실행 경로는 없다. external side-effect exactly-once/dedup을 이번 crash log 원자성으로 인증하지 않는다. TradeConfiguration/Inventory/Tax/Tactical/Ownership/EntityId 구현을 추가하거나 수정하지 않았다. GUI/Computer Use는 사용하지 않았다.

## 12. E1 evidence와 QA 재현 범위

E1 JSON은 21/21이며 원본 SHA로 고정했다. developer evidence로 보존했지만 이름과 실제 coverage를 분리했다.

- Battery15 `OsProcessCasSameIdSameStream`은 source상 한 coordinator의 **8 sequential commits**다. independent OS-process contention proof가 아니다.
- Battery16 `HardKillCommitCuts`는 한 정상 commit 뒤 table cardinality를 검사한다. 실제 process kill/hook cut이 없다.
- Battery21은 DLL/MVID/DB residue를 확인하지만 current manifest filename/contents와 SHA를 실제로 대조하지 않는다. QA는 그 별도 대조를 수행했다.
- audit test가 DetailsJson을 `{"status":"TAMPERED"}`로 통째로 바꾸면 required expected/observed가 없어 거절된다. **정상 required fields를 유지하면서 status만 바꾸는** 이번 독립 시험을 대신하지 못한다.

따라서 E1을 반박하기 위한 숫자 경쟁이 아니라 actual candidate 경계의 누락을 검증했다. 이번 service lifetime/code 개선은 독립 evidence로 인정한다.

QA harness만 빌드했고 interface의 새 principal argument를 QA adapter에 반영했다. 이전 REV4의 Dispose-return-dependent barrier helper는 이번 final-lifetime proof에 사용하지 않았다. timer-based observer가 candidate 행동을 수정하지 않고 해제 시점만 제어했다. independent comparison/hash/static inspection과 actual runtime result를 구분했다.

## 13. 증거 목록과 freeze

- [execution-summary.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/execution-summary.json)
- [semantic-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/semantic-results.json): natural mixed baseline, historical/status/audit/envelope/ID attacks
- [lifetime-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/lifetime-results.json): 6/8/13s service, cuts, real Main, query/retry
- [json-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/json-results.json): typed input + exact numeric/JSON boundaries
- [completion-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/completion-results.json): actual EXE READY/LISTEN, mixed canary, legacy, hard-kill, required commit field omissions
- [final-attacks-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/final-attacks-results.json): valid composite reparenting, UNKNOWN uncommitted resolution, actual control identities
- [schema-collation-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/schema-collation-results.json) / [collation-confirmation-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/Evidence/collation-confirmation-results.json): V6 altered key equality, normal BINARY control, index_xinfo, actual EXE
- `results.json`, `extra-results.json`, `schema-extra-results.json`: base/closed-group regression, conventional mutants
- [freeze-before.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/freeze-before.json) / [freeze-after.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/freeze-after.json): **353/353, added/deleted/changed0**
- [qa-evidence-manifest.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/qa-evidence-manifest.json): QA tools/evidence/frozen copies SHA inventory

candidate report/current manifest/E1 result도 frozen copies와 전후 같음을 확인했다. SHA가 달라지는 candidate를 계속 시험하거나 조용히 수정하지 않았다.

## 14. 최종 Master 권고

**Final verdict: FAIL.**

001/013은 이번 범위에서 closure를 채택할 수 있다. 007은 historical observation, status/reason/FailureReason 및 full typed audit 검증이 남아 OPEN 유지. 008의 historical V5 closure와 별개로 **현재 V6의 collation-blind schema admission은 blocker**다. 019와 prior closed groups의 시험한 regressions는 유지됐다.

다음 frozen candidate에서는 original observation의 trusted decision binding, audit의 모든 required semantics/keys, canonical identity collation을 먼저 수정하고 이 보고서의 coherent-history rewrite / one-field status / required-field omission / NOCASE identity tests를 mandatory regressions로 추가해야 한다.

Production 수정·재빌드 없이 Work Order 검증을 완료했다. ADR-001 Foundation release 또는 공식 architecture state를 변경하지 않았으며 Master의 다음 지시를 기다린다.
