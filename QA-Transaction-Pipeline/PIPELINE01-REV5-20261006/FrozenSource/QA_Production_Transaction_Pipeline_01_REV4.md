# QA Production Transaction Pipeline 01 — REV4 Independent E2

```yaml
Work Package: WP-QA-PROD-TRANSACTION-PIPELINE-01-REV4
Reviewer: GPT-6.1 Sol / Independent QA & Architecture Reviewer
Date: 2026-10-04 (Asia/Seoul)
Target: Production_Transaction_Pipeline_Slice_01_REV4.md
Verdict: FAIL
Production modification or rebuild: NONE
Production freeze: 353 files before / 353 files after / 0 changes
Master defect ledger or architecture status modified: NO
```

## 1. Master 판정 요약

**최종 판정: FAIL.** 원래 JSON 수치 충돌과 derivative ID delimiter 충돌은 해소됐고 Schema V5의 시험한 변조 방어도 통과했다. 그러나 다음 실제 Release 경로의 결함이 남아 있다.

1. 정상 CAS loser가 만든 **ABORTED 이력만으로 재시작이 거부된다.** 쓰기 측은 reject audit의 OldRevision에 실제 revision을 저장하지만 복구 측은 요청 ExpectedRevision과 같아야 한다고 검사한다. 두 값이 다른 것이 정상 CAS 거절의 정의다.
2. Operation envelope/fingerprint, audit detail, ReceiptId/EventId의 관계가 완전히 검증되지 않는다. 정상 READY fixture에서 **6개 의미 변조가 다시 READY**가 됐다. 그중 4개는 실제 Server.exe에서도 READY → TCP listen에 도달했다.
3. **Dispose/Shutdown/Main이 writer가 살아 있는 동안 반환한다.** 실제 Main의 활성 작업 종료 경로에서 약 6.2초 후 writerAlive=true, IsDisposed=false, ActiveCoordinator=null을 독립 관측했다. after-CAS barrier에서는 Dispose 반환 이후 repository observer 6회가 실행됐다.
4. 잘못된 escaped surrogate 및 최솟값 exponent가 INVALID_REQUEST 대신 STORAGE_FAILURE로 분류된다. durable OperationRecord는 남지 않지만 명시된 입력 오류 계약이 미완결이다.

| 결함 | Master에 대한 독립 권고 | 근거 |
|---|---|---|
| QA-PIPELINE-001 | **PARTIAL / OPEN** | exact numeric/duplicate/trailing/raw UTF-16 방어는 해결; escaped surrogate 4건 및 exponent 1건의 오류 분류 잔존 |
| QA-PIPELINE-007 | **STILL FAILING / OPEN** | 자연 생성된 ABORTED의 false rejection, principal 없는 history 매칭, 6개 false READY |
| QA-PIPELINE-008 | **CLOSED 권고 — 시험한 V5 계약 범위** | 34개 schema 변조 거절, independent descriptor 일치, canary durable mutation 0, 실제 legacy v1–v4 fail closed |
| QA-PIPELINE-013 | **STILL FAILING / OPEN** | live writer를 남긴 Dispose/Shutdown/Main 반환, after-CAS 후속 repository 호출 |
| QA-PIPELINE-019 | **CLOSED 권고 — 유효 admitted identity 범위** | 4쌍 × 2 정상 commit, 정확 retry, control/separator 10개 commit 및 10개 stored-ID retry, domain/revision 검사 |

이는 closure **권고**이며 Master 상태를 직접 변경하지 않았다. 이 gate는 P1 probe foundation에 한정한다. **ADR-001 Foundation runtime 완료나 다음 slice release를 승인하지 않는다.**

## 2. Exact freeze / provenance

증거 루트: [PIPELINE01-REV4-20261004](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004).

Production 전체를 동결한 뒤 Release 파일을 QA Candidate로 복사했다. QA harness만 새 DLL을 직접 참조하도록 빌드했다. Production/PoC source, binary, fixture는 수정·재빌드하지 않았다. 실제 coordinator, repositories, SQLite transactions를 사용했다. 관측 wrapper는 실제 repository에 위임하고 지정 지점에서 대기하거나 I/O-like 예외를 주입한다. commit/receipt/recovery 성공을 QA가 대신 구현하지 않는다.

실제 native commit/WAL hook과 별도 OS process 강제 종료를 사용했다. 모든 SQL/schema 변조는 QA-owned DB에서 수행했다. OS process kill은 crash 시험에만 사용했으며 clean shutdown 성공으로 계산하지 않았다.

### 바이너리

| 항목 | 독립 확인값 |
|---|---|
| 원본 DLL | `C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.dll` |
| Server DLL SHA-256 | `EACBDD3AE976515779E25C4450C549CB2AD20E8F699C738E05D747EADD211A92` — Work Order 기대값 일치 |
| **Server MVID** | **`72eda58c-0deb-41fb-8834-b41274e2c35f`** — A 보고서에 없는 값을 직접 확인 |
| Server EXE SHA-256 | `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C` |
| Server PDB SHA-256 | `A8A8998992F80885F50EBCF35F60CDF1F8F12FA0926E92B034FD54CFDF469464` |
| Common DLL SHA-256 | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` |
| Common MVID | `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` |
| Server CodeView / PDB GUID | 양쪽 `3ee7603f-3b7c-403a-98cc-dfb26532814b` |
| E1 result SHA-256 | `F3E971600E95D6D1696124BE304FC6AFAB741B47EE9A809C93E42DE86BD182FB` |
| 실제 QA loaded DLL | QA `Harness/bin/Release/net8.0/WarEconomy.Server.dll` 및 `HarnessExt/bin/Release/net8.0/WarEconomy.Server.dll` — 위 SHA/MVID 동일 |
| Runtime | .NET 8.0.10 |
| Native SQLite | 3.41.2 |
| Packages | Microsoft.Data.Sqlite 8.0.10 / SQLitePCLRaw 2.1.6 / Newtonsoft.Json 13.0.3 |
| DB identity | application_id 1463898693 (`WARE`), user_version **5** |

PDB의 source document **20/20** 실제 checksum 일치. Release candidate source/binary lineage를 확인했으며 Production build를 다시 실행하지 않았다. A의 build 경고 0/오류 0 주장은 QA가 독립 재빌드해 인증한 값이 아니다. 실제 바이너리 실행과 PDB 연결을 검증했다.

### 변경 소스와 lineage

경로 기준 `WarEconomyMod/Source/Server/`.

| 파일 | SHA-256 |
|---|---|
| `Pipeline/Models/PipelineProbeModels.cs` | `64D6FA0CA82DE08754B0390CAA7795D551FB3172F2FC39E1A794928F1E4585BF` |
| `Pipeline/Coordinator/PipelineTransactionCoordinator.cs` | `CA70B98561D07CE704D9327756ED7701C632AC5A5AB36193BD8E0BD478FDCD07` |
| `Pipeline/Data/Migrations/PipelineSchemaMigration.cs` | `38406479C47D5038AE8E574849E5FF708EB932606278364CE72649A616793AB1` |
| `Pipeline/Recovery/RecoveryReconciler.cs` | `B91B093363D876D012235F2E7FCC5B6422F2F6F7A5DFD401A168C6D87C83097A` |
| `Program.cs` | `5BB90D98BA55E9AA62DC96985F27180981E5361F7817400A5B206CBA768C37E8` |
| `Pipeline/Data/SqliteDatabaseContext.cs` — 이전 버전 유지 | `AD83A9747ADE1D078B2D672EFDDF34E60F5B5A902DD672BF567500215977B903` |

### Release manifest의 불일치 — 해결하지 않음

정식 REV4 Release manifest는 발견되지 않았다. 존재하는 `RELEASE_MANIFEST_PIPELINE_REV3.json`은 SchemaVersion=4이며 32개 entry 중 **Server DLL/PDB 2개가 현재 파일과 불일치**, 나머지 30개는 일치한다. 이전 manifest의 Server DLL은 `8F140D23...`인 REV3이다. 이번 후보의 SHA/MVID/source lineage는 별도 QA freeze로 확정했으므로 시험 대상 혼동은 없다. 다만 **REV4 package manifest 완료라는 보증은 할 수 없다.** Dev가 다음 후보에서 공식 manifest를 갱신해야 한다. QA가 이를 조용히 고치지 않았다.

원본 Release의 DB/WAL/SHM, test-name, log/tmp 잔여 파일은 없다. QA가 native SQLite 해석에 필요한 DLL을 QA harness root에 복사한 것은 시험 도구 배포일 뿐 Candidate 변경이 아니다.

증거: [provenance-complete.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/provenance-complete.json), [runtime-metadata.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/runtime-metadata.json), [extension-runtime-metadata.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/extension-runtime-metadata.json), [pdb-lineage.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/pdb-lineage.json).

## 3. 독립 실행 요약

| 시험 | 실제 결과 | 해석 |
|---|---|---|
| CAS, 25 separate OS processes / connections, 동일 expected revision | 1 SUCCESS / 24 STALE_REVISION | 경쟁 원자성 PASS; 해당 ABORTED 포함 DB의 재시작은 별도 FAIL |
| 같은 identity/envelope, 12 OS processes | 1 SUCCESS / 11 ALREADY_COMMITTED | 중복 effect 없음 |
| 같은 stream, 8 rounds × 6 OS processes | 8 SUCCESS / 40 STALE; revision/Seq 1..8 | 경쟁/순서 PASS; 혼합 terminal 이력 recovery는 FAIL |
| REV3 small/29+precision 4쌍 | 첫 SUCCESS, 다른 값 retry COLLISION_REJECTED | 손실 canonicalization 해결 |
| equivalent numbers / zero | 동일 Operation 재요청 ALREADY_COMMITTED, 기존 receipt 유지 | PASS |
| malformed raw UTF-16, 3 shapes × 9 fields | **27/27 INVALID_REQUEST** | durable rejected operation 없음 |
| escaped malformed surrogates 4건 + int.MinValue exponent | **5 STORAGE_FAILURE**, durable record 0 | typed input rejection PARTIAL |
| schema 변조 | **34/34 거절** | V5 시험 범위 PASS |
| startup canary 반복 | 3회 READY, logical DB/schema 전후 동일 | rollback-only, durable mutation 0 |
| 실제 nonempty legacy v1/v2/v3/v4 | 모두 fail closed, row/schema 보존 | PASS |
| READY인 8-commit fixture 기반 기존 graph negatives | 25개 거절; 추가 valid-hash balanced duplicate도 거절 | 이전 false-READY 방어 개선 인정 |
| READY인 4-commit/2-scope fixture의 새 graph attacks | **6개 false READY** | 007 FAIL |
| 자연 생성된 4 COMMITTED + 2 ABORTED / 2 scopes | 재시작 거절 | 정상 state convergence FAIL |
| derivative 기존 4쌍 | 8 SUCCESS; 모든 정확 retry 원래 ID | 019 PASS |
| control/separator identity | 10 SUCCESS / 10 ALREADY_COMMITTED, 정상 restart | 019 PASS |
| terminal SQL, 2 states × 6 shapes | 12/12 SQLite19, row unchanged | terminal immutability PASS; 혼합 DB restart는 007에 의해 FAIL |
| full queue 1,205 | 204 즉시 BUSY; 1 in-flight + 1,000 queued; 최종 pending 0 | bounded admission PASS |
| Shutdown/Dispose observer barrier | 약 6.0초에 반환, writerAlive=true / IsDisposed=false | 013 FAIL |
| native lock, after-CAS/audit/commit/WAL shutdown | writerAlive 상태 반환; after-CAS 이후 observer 6회 | 013 FAIL |
| 실제 Production Main의 활성 작업 quit | 약 6.2초에 Main 반환, writerAlive=true, ready=false | 정상 Main cleanup FAIL |
| real hard-kill 8 cuts | commit 전 전체 0; WAL 후 및 return 후 전체 1; retry 안정 | tested crash atomicity PASS |
| gameplay isolation | probe packet/CLI route 없음; 정상 EXE에 unknown probe frame 후 canonical operation 0 | narrow isolation 유지 |
| Production before/after | 353 files, changes 0 | freeze 유지 |

전체 결과 집계와 원시 값은 [execution-summary.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/execution-summary.json)에 있다. 범주 통과와 구체적 실패를 분리했고 A의 27/27이라는 수치를 독립 gate 결과로 재사용하지 않았다.

## 4. QA-PIPELINE-001 — exact JSON identity

### 해결 확인

실제 `ExecuteProbeCas` admission에서 아래 서로 다른 수치를 같은 OperationId로 재시도했다. 모두 **기존 successful receipt 재사용 대신 COLLISION_REJECTED**, 원래 effect는 revision 1에 머물렀다.

- `1e-29` / `-1e-29`
- `1e-40` / `0`
- `1.00000000000000000000000000001` / `1.00000000000000000000000000002`
- `0.123456789012345678901234567891` / `0.123456789012345678901234567892`

`1`, `1.0`, `1e0`, `1E+000`과 `0`, `-0`, `0.0`, `0e308`, `-0e-308`은 각각 동일 canonical identity와 stored receipt에 수렴했다. root/nested/array-object duplicate, `"a"`/`"\u0061"` escaped-equivalent duplicate는 INVALID_REQUEST. 두 번째 root/비공백 trailing content는 거절하고 whitespace trailing은 수락했다.

`1e308`, `1e-308` 수락; ±309 거절. `1e2147483648` 거절. 1,000 nonzero mantissa digits 수락, 1,001 거절. 64-level nesting 수락, 65 거절. valid escaped surrogate pair 수락. 실제 UTF-16 문자열의 unpaired/reversed surrogates는 9개 field 위치 모두 거절했다.

시험한 JSON 거절 **18건 전체 durable OperationRecord 합계 0**이며 여기에는 아래 5건의 잘못된 status도 포함된다. raw UTF-16 거절 역시 durable BAD operation을 생성하지 않았다.

### 잔존 결함 — Medium — 잘못된 입력을 storage 장애로 보고

위치:
- [PipelineProbeModels.cs:606](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:606), `reader.GetString()` — property name
- [PipelineProbeModels.cs:647](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:647), string value
- [PipelineProbeModels.cs:739](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Models/PipelineProbeModels.cs:739), `Math.Abs(exp)`
- [PipelineTransactionCoordinator.cs:122](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:122), admission catch 분기

Reproduction: PayloadJson에 `{"\ud800":1}`, `{"a":"\ud800"}`, `"\udc00"`, `"\udc00\ud800"` 또는 `1e-2147483648` 제출.

Expected: unsupported/malformed input으로 INVALID_REQUEST, durable record 0.

Actual: STORAGE_FAILURE / admission validation failed; record는 0. escaped surrogate를 해석하는 `GetString()`은 InvalidOperationException을, int.MinValue의 절댓값은 OverflowException을 발생시킨다. canonicalizer는 JsonException만 입력 오류로 변환하고 나머지는 coordinator의 일반 storage-failure catch로 내려간다.

Required fix: JSON decoding/number-domain 검사 단계에서 이 구체적 입력 예외를 typed invalid-input으로 변환하고 int.MinValue 절댓값 overflow를 피한다. 실제 DB/I/O 예외를 INVALID_REQUEST로 뭉뚱그려 잡아서는 안 된다.

### Size-bound 관찰

1 MiB / 4 MiB string payload가 실제로 수락됐고 후자는 약 291ms였다. candidate에는 depth64, numeric digits1000, scale308 제한은 있으나 이 경로의 total JSON byte limit은 확인되지 않았다. 이것을 임의의 미정 byte cap 위반으로 판정하지는 않는다. **전체 size bound가 있다고 인증하지도 않는다.** 또한 blank payload는 `{}`로 처리되는 기존 계약이다. 허용 size/admission memory budget을 다음 계약에서 명시하고 경계 시험을 추가할 필요가 있다.

증거: `deep2-results.json/json-full`, `input-validation-results.json/all-inputs`, `results.json/canonical-*`.

## 5. QA-PIPELINE-019 — derivative identity

기존 4쌍을 그대로 재실행했다.

1. `(A_B, C)` / `(A, B_C)`
2. `(A_, B)` / `(A, _B)`
3. `(한_글, 림)` / `(한, 글_림)`
4. `(A: + x×300 + _B, C)` / `(A: + x×300, B_C)`

각 pair의 두 실제 operation이 모두 SUCCESS. 모든 exact retry는 원래 stored ReceiptId/EventId를 유지했다. 추가로 colon, NUL, CRLF, U+2028, U+001F를 principal/operation 사이에서 재분배한 **10개의 admitted request**도 모두 다른 ID로 commit됐고 10개의 retry는 ALREADY_COMMITTED. 이 DB는 READY로 재시작했다.

직접 generator에서 long.MinValue / -1 / 0 / 1 / long.MaxValue-1 / long.MaxValue와 10 tuple을 확인했다. receipt/event domain이 분리되고 revision 경계도 다른 입력 bytes/IDs를 만든다. 음수 revision generator 확인은 production에서 해당 revision의 business effect를 허용한다는 인증이 아니다.

실제 구현은 BinaryWriter의 length-prefixed strings + Int64와 domain-separated SHA-256이다. **tuple encoding의 injectivity**는 valid admitted strings에서 구조적으로 확인했다. SHA-256 출력에 수학적 절대 무충돌을 주장하는 A의 “can never collide” 문장은 과도하다. 암호학적 충돌 저항과 명백한 delimiter 충돌 제거를 구별한다. null/empty는 generator 내부에서는 통합되나 principal/operation admission에서 둘 다 거절되어 이 closure 범위의 충돌이 되지 않는다.

권고: **019 CLOSED**, 이 유효 admission/derivation 범위에 한정. recovery가 stored ID와 derivation의 관계를 검증하지 않는 문제는 아래 007에 남긴다.

## 6. QA-PIPELINE-008 — Schema V5

독립 Python/SQLite introspection으로 table columns/type/nullability/PK order, FK source/target/actions, indexes uniqueness/order/partial predicates, trigger SQL, CHECK literals, active incarnation count의 descriptor를 재구성했다. candidate validator의 결과를 복사하지 않고 얻은 SHA:

`3DD745591298C7C7BB84C889C98D0B2B0A3EF0E5145F719D6973DEFA4BBB5A73`

실제 V5 expected signature와 일치한다. [schema-independent-descriptor.txt](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/schema-independent-descriptor.txt)와 `schema-introspection`에 전체 PRAGMA graph를 보존했다.

**34/34 schema mutants** 모두 fail closed. 포함 범위:

- literal case 및 escaped quote 변화, true CHECK를 comment lookalike로 대체;
- CHECK 삭제/다른 predicate, type/nullability/PK/unique order 변조;
- full index를 partial index로 변경, column order/uniqueness 변경;
- missing/no-op trigger, WHEN0 및 WHEN1=0, RAISE를 comment로 숨긴 body;
- FK source/target columns, UPDATE/DELETE actions;
- app identity/future version/missing table-column-index;
- zero/multiple active incarnation.

대표 schema 거절은 실제 Server.exe에서도 exit2, NO READY, NO LISTEN. fresh V5는 READY. 정상 committed-only DB도 실제 EXE 재시작 READY.

Startup canary는 실제 candidate가 transaction + SAVEPOINT를 실행한다. 정상 DB 3회 startup 전후 **모든 durable row/schema 동일**. trigger comment/false WHEN처럼 canary 중 실패하는 DB도 rollback 후 논리적 DB 동일. 이는 physical WAL 파일 byte identity가 아니라 **durable canonical state 무변경** 증거다.

과거 실제 실행 DB의 nonempty v1/v2/v3/v4를 복사해 시험했다. version label만 바꾼 가짜 legacy가 아니다. 모두 migration/reset 요구로 거절했고 rows/schema 보존. normal executable에서도 exit2/NO READY/NO LISTEN. foreign app0/version0 DB도 보존하며 거절했다.

**권고 008 CLOSED**, 시험한 canonical V5 schema/admission 범위. regex 기반 CHECK 추출이 임의 SQLite 문법의 완전한 semantic theorem prover라고 인증한 것은 아니다. 기존 V5의 고정 signature 및 이번 공격 표본을 통과했다.

## 7. QA-PIPELINE-007 — consistency graph

### 7.1 인정하는 개선

정상 READY인 **8개 COMMITTED-only** DB를 실제 coordinator로 새로 만들었다. 이 fixture에서 기존 missing/hash/scope/revision/principal/op/event type/stream/seq/incarnation/history/aggregate/audit/child orphan/duplicate 등 23개 mutation과 ABORTED에 receipt/event를 붙이는 2개 mutation이 모두 거절됐다. hash를 정확히 재계산한 duplicate receipt를 추가하고 다른 operation의 receipt를 지워 global count를 맞춘 공격도 거절됐다.

2 scopes × 2 commits의 별도 READY fixture에서도 balanced missing/extra audit, missing parent, history orphan/gap, aggregate gap, logical duplicate-parent receipt 공격을 거절했다. **global counts만 검사하는 구현은 아니다.** 이러한 개선을 인정한다.

### 7.2 High — 정상 ABORTED가 재시작을 막음

위치: [PipelineTransactionCoordinator.cs:335](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:335), reject audit 작성; [RecoveryReconciler.cs:453](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:453), ABORTED OldRevision 검증.

Reproduction: SA/SB 각 scope를 정상 revision2까지 진행 → expected0 명령을 각 1회 보내 STALE_REVISION/ABORTED 생성 → 같은 DLL로 startup.

Expected: 두 ABORTED는 정당한 terminal failure; READY, committed state 유지.

Actual: `reject audit ... old revision 2 contradicts expected revision 0`로 startup 거절. SQL tamper 없이 candidate가 만든 이력이다. actual EXE에서 8 winner/40 loser의 정상 경쟁 DB 재시작도 exit2/NO LISTEN. terminal SQL용 COMMITTED+ABORTED DB도 같은 회귀로 startup 실패.

Root cause: writer는 OldRevision=`effectiveCurrent`, recovery는 OldRevision=`ExpectedProbeRevision`를 요구한다. CAS mismatch에서는 둘이 반드시 다르다.

Required fix: reject audit의 **observed revision / requested expected revision** 의미를 분리·일치시킨다. 나중의 current aggregate revision으로 과거 observation을 대체하지 말고 당시 관찰값과 rejection reason을 durable 계약으로 검증한다. 정상 loser를 포함하는 restart positive test를 필수화한다.

### 7.3 High — operation identity의 principal boundary 유실

위치: [RecoveryReconciler.cs:292](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:292), committed history lookup; [RecoveryReconciler.cs:409](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:409), aborted history lookup; `ProbeRevisionHistory` schema / `ProbeAggregateStore.InsertRevisionHistory`.

두 독립 자연 생성 사례:

- P1/SAME이 S revision1 commit, P2/SAME이 S revision2 commit → 모두 SUCCESS지만 restart는 P1에 duplicate history라고 거절.
- P1/SAME이 S commit, P2/SAME이 OTHER에서 STALE/ABORTED → restart는 P2 ABORTED에 history가 있다고 거절. 다른 principal·scope의 P1 history를 주워 온 것이다.

Canonical operation key는 `(PrincipalId, OperationId)`인데 history에는 principal이 없고 lookup은 `(scope, op)` 또는 **op만** 사용한다.

Required fix: history parent relationship을 canonical operation key에 맞추거나 모호하지 않은 durable internal key를 사용한다. 실제 합법 cross-principal same-OperationId를 금지해서 결함을 숨기지 않는다. FK와 양방향 reconciliation도 동일 key를 사용해야 한다.

### 7.4 High — 의미가 변조된 graph의 false READY

정상 READY인 4 COMMITTED / 2-scope fixture를 QA DB로 복사했다. immutable trigger는 **QA tamper 동안만** 제거하고 원래 SQL 그대로 복원했다. schema signature는 다시 동일하므로 이 공격은 schema mismatch가 아닌 recovery semantics를 시험한다. candidate code는 변경하지 않았다.

| 독립 mutation | runtime 결과 | actual Server.exe |
|---|---|---|
| SAC1/SBC1 ReceiptId 교환, 각 parent metadata에 맞춰 ReceiptHash 재계산 | **READY** | READY + LISTEN |
| SAC1/SBC1 EventId 교환, payload/hash/parents/stream/seq 유지 | **READY** | READY + LISTEN |
| AuditRecords.DetailsJson의 receipt/fingerprint를 WRONG으로 변경 | **READY** | READY + LISTEN |
| OperationRecords.OperationType=WRONG | **READY** | harness에서 확인 |
| OperationRecords.ContentProfileFingerprint=WRONG | **READY** | harness에서 확인 |
| OperationRecords.RequestFingerprint=WRONG | **READY** | READY + LISTEN |

Root cause / locations:

- [RecoveryReconciler.cs:143](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:143): operation envelope의 type/schema/profile/config 등을 가져와 fingerprint를 재계산하지 않는다. 읽은 RequestFingerprint도 semantic parent 검증에 사용하지 않는다.
- [RecoveryReconciler.cs:212](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:212): receipt hash를 **현재 stored ReceiptId**로 재계산할 뿐 DerivativeIdGenerator의 expected ID와 비교하지 않는다.
- [RecoveryReconciler.cs:237](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:237): EventId를 읽지만 canonical derivative identity와 대조하지 않는다.
- [RecoveryReconciler.cs:335](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:335): `aDetails`를 읽고도 receipt/fingerprint 내용은 검증하지 않는다.

Expected: required parent/child semantic identity가 일치하지 않으면 NO READY. Actual: global counts와 일부 metadata/hash가 맞으면 위 altered state를 승인한다.

Required fix: terminal record의 저장된 envelope에서 fingerprint를 독립 재계산하고 지원 type/schema/profile/config/incarnation 관계를 검사한다. ReceiptId/EventId를 해당 operation의 canonical derivation과 연결하고 audit details를 typed 내용으로 대조한다. 임의 hash re-sign으로 parent 의미 변경을 통과시켜서는 안 된다.

이는 DB 접근권한이 없는 일반 network client가 파일을 변조할 수 있다는 보안 주장이나 malicious disk 관리자에 대한 cryptographic authenticity 보증 요구가 아니다. **Work Order가 요구한 damaged persistence graph의 fail-closed consistency**가 불완전하다는 증거다.

### 7.5 Masking을 피한 증거 구분

처음의 자연 생성 COMMITTED+ABORTED fixture는 7.2 때문에 baseline부터 NO READY였다. 그 fixture의 다른 mutation이 거절됐다는 것을 해당 mutation 탐지 성공으로 세지 않았다. `deep-graph-*` 원시 결과는 이 초기 masking을 보존한다. definitive false READY 증거는 **정상 baseline READY가 먼저 확인된 `confirmed-graph-*`**만 사용했다. `confirmed-graph-operation-incarnation-aborted`는 ABORTED row가 없는 DB에서 affected row 0이므로 공격 성공/탐지 결과에 포함하지 않았다.

따라서 arbitrary malformed ABORTED의 모든 field에 대한 closure는 인증하지 않는다. natural ABORTED 자체가 회귀 실패한다는 것이 우선 차단 요인이다.

## 8. QA-PIPELINE-013 — service lifetime / Main

### 실제 Production service 관측

Actual `PipelineStartupManager.InitializeAndVerifyPipeline`이 만든 coordinator에 transparent repository observer만 연결했다. service state machine/queue/writer/shutdown 구현은 candidate 그대로다. before-read barrier를 잡고 1,205 submissions, 별도 task에서 actual Shutdown을 호출했다.

관측:

- shutdown 시작 후 ready=false, 새 admission 거절: 정상;
- 204 backpressure + 1,000 queued + 1 in-flight, 모든 caller terminal: 정상;
- **6,035ms 후 Shutdown 반환, writerAlive=true, IsDisposed=false, ActiveCoordinator=null**: 실패;
- barrier 해제 후 writer 종료를 별도로 기다리고 Dispose를 반복하면 최종 writerAlive=false/IsDisposed=true: 이 마지막 QA cleanup은 앞선 실패를 PASS로 바꾸지 않는다.

### 실제 Main의 활성 작업 quit

실제 DLL의 `WarEconomy.Server.Program.Main`을 실행했다. QA TextReader는 actual service coordinator를 포착하고 candidate의 기존 `SimulatedWriterDelayMs=12000` fault knob만 설정한 뒤 실제 operation을 제출하고 `quit`를 반환했다. fake Main/Shutdown을 구현하지 않았다.

**6,205ms 후 Main 반환:** writerAlive=true, IsDisposed=false, ready=false, ActiveCoordinator=null. caller는 UNKNOWN_QUERY_REQUIRED. 살아 있는 writer는 이후 별도로 join/Dispose했다. Master 요구 “Main does not return while coordinator alive”를 위반한다. 외부에서 강제 종료한 clean-shutdown 주장이 아니다.

### Repository/commit boundary 시험

| held boundary | Dispose 반환 ms | 반환 때 writerAlive | 반환 후 관측 observer 호출 |
|---|---:|---|---:|
| after-CAS | 6,019 | true | **6** |
| after-audit | 6,026 | true | 0 |
| native pre-commit hook | 6,021 | true | 0 |
| native post-WAL hook | 6,035 | true | 0 |
| SQLite write lock | 6,014 | true | 1 |

observer 횟수는 실제 repository 위임 지점의 관측값이다. after-audit/commit/WAL의 0회는 transaction 내부의 commit/cleanup이 끝났다는 뜻이 아니다. writer가 살아 있다는 사실 자체가 final disposal gate를 실패시킨다. after-CAS 해제 후 receipt/event/audit 실제 쓰기가 진행되어 commit했고 original request retry는 ALREADY_COMMITTED로 수렴했다.

### Root cause / required fix

위치: [PipelineTransactionCoordinator.cs:470](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Coordinator/PipelineTransactionCoordinator.cs:470), Dispose; [RecoveryReconciler.cs:665](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs:665), Shutdown; [Program.cs:98](C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:98), quit cleanup 경로.

Dispose는 Join(1000) → interrupt/cancel → Join(3000) → UNKNOWN → Join(2000) 후에도 미종료이면 **그대로 반환**한다. `_isDisposed=true`를 worker 종료 후에만 설정한 것은 정확하지만 **method return을 종료에 묶지 않았다.** Shutdown은 반환된 객체를 null로 버리고 Main은 이어서 반환한다. after-CAS에는 admission guard가 이미 지난 뒤라 후속 repository calls를 막지 않는다.

Required fix: 응답 deadline과 service lifetime 종료를 분리한다. caller는 timely UNKNOWN으로 종료할 수 있으나 final shutdown/dispose 완료는 writer exit와 DB handle cleanup에 실제로 묶어야 한다. writer가 live이면 service ownership을 유지하고 cleanup pending 상태를 명시한다. cancellation 가능한 작업은 취소하고 취소 불가능한 구간은 끝날 때까지 final completion을 반환하지 않는다. Master의 요구와 다른 “시간 제한 후 반환하되 IsDisposed=false” 계약으로 조용히 축소하지 않는다.

반복 Dispose는 최종 cleanup 후 안전했으나 최초 반환의 위반은 남는다. readiness/admission/caller terminal 개선은 인정한다.

### UNKNOWN identity / convergence

응답 모델은 UNKNOWN 시 Receipt=null이고 Player/Operation 식별자 필드는 포함하지 않는다. 다만 원래 caller envelope의 `(PrincipalId, OperationId, incarnation, profile...)`를 QA가 보존했으므로 식별자는 **호출자 기준으로 queryable**했다. committed after-CAS/WAL 사례는 실제 stored receipt 조회 및 exact retry로 ALREADY_COMMITTED; native-lock 사례는 receipt=null/NOT PRESENT 후 **동일 envelope retry SUCCESS**였다.

따라서 identity가 완전히 사라졌다거나 retry가 중복 commit됐다고 주장하지 않는다. 호출자가 원래 OperationId를 반드시 보존해야 하는 계약을 명시해야 한다. 현재 service final-completion fence는 여전히 FAIL이다. Options.AdmissionTimeout=2s는 이 actual await 경로의 강제 response deadline으로 사용되지 않는다. 별도 3s held-queue 시험도 최종 종료를 Dispose가 만들었다. 배포 latency/SLO나 WAN 성능을 인증하지 않았다.

## 9. Hard-kill / storage / fencing regressions

Separate OS process를 다음 8개 지점에서 강제 종료하고 새 process에서 durable DB만으로 판단했다.

| kill cut | 재시작 전 durable truth | 동일 request retry |
|---|---|---|
| SQLite transaction 시작 후 / CAS 전 | operation/receipt/event/audit/history/aggregate 모두 0 | SUCCESS revision1 |
| CAS 후 / receipt 후 / event 후 / audit 후 | 각 cut 모두 business rows 전체 0 | SUCCESS revision1 |
| native commit hook — commit 전 | 전체 0 | SUCCESS revision1 |
| native WAL hook — durable commit 후 응답 전 | operation/receipt/event/audit/history/aggregate 각 1 | ALREADY_COMMITTED, 원래 receipt |
| actual Execute 반환 후 응답 출력 전 | 각 1 | ALREADY_COMMITTED, 원래 receipt |

공통 전체 commit graph가 0 또는 1로 유지됐다. terminal 상태는 COMMITTED/ABORTED만 존재하며 이 후보의 P1 모델에 PREPARED recovery가 있다고 간주하지 않는다.

Constraint failures 4 repositories, I/O-like failures 4 boundaries는 STORAGE_FAILURE; 실제 SQLITE_BUSY(5)/LOCKED(6)는 STORAGE_BUSY_RETRYABLE, 잘못된 STALE 전환 없음. 손상 schema를 valid하다고 열었다는 뜻이 아니라 writer 오류 처리용 QA-owned constraint fixture다.

COMMITTED/ABORTED에 UPDATE/DELETE/INSERT OR REPLACE/REPLACE INTO/raw same-key INSERT/UPSERT DO UPDATE를 actual Production-opened connection으로 시도해 **12/12 error19 차단**, terminal rows 변형 0. ABORTED restart 실패를 숨기지 않았으며 이 immutability 통과와 recovery fail은 별개다.

incarnation null/empty/blank INVALID_REQUEST 유지. 별도 process에서 admission 후 incarnation을 rotate하자 old admitted request는 INCARNATION_MISMATCH. historical receipt는 계속 조회 가능하다. immutable DTO snapshot은 admission 이후 원본 principal/op/scope/profile/config/payload 등을 바꿔도 admitted command를 바꾸지 않았다.

WAL, synchronous=2/FULL, FK=1, recursive_triggers=1, 기본 busy_timeout=5000ms / DefaultTimeout=5s를 actual connection에서 확인했다. connection pool을 NORMAL로 오염시킨 20회 시험에서도 다음 Production CreateOpenConnection은 다시 FULL을 설정했다. native lock stress에서 timeout만 QA profile로 연장한 것과 production 기본값을 구별한다. **power-cut/hardware cache durability 시험은 수행하지 않았다.** OS process kill을 물리적 전원 손실 인증으로 확대하지 않는다.

## 10. Startup / gameplay / consumer boundary

Fresh actual Server.exe는 schema/bootstrap → recovery → dedicated writer → PIPELINE_READY → TCP listen 순서다. 정상 committed-only restart도 성공. malformed schema, 실제 nonempty legacy/foreign DB는 exit2로 gameplay admission 전에 거절했다. 하지만 valid ABORTED 이력의 거절과 false READY가 있으므로 **startup ordering이 맞는 것만으로 recovery 완료를 인증하지 않는다.**

`PacketHeader`에는 probe command가 없고 `TcpNetworkServer` dispatch에 pipeline probe route가 없다. Program.Main은 이전 `--test-pipeline-e1` / `--crash-worker` 인수를 test runner로 분기하지 않는다. 실제 copied EXE에 unknown header + probe payload를 보내 canonical operation/material row가 생기지 않았고 과거 CLI flag 실행 시 별도 marker DB도 unchanged였다.

Pipeline tables는 probe/journal/receipt/history/audit/publication/incarnation뿐이다. TradeConfiguration, Inventory, Tax, Tactical, Ownership, EntityId 이전을 구현·변경하지 않았다. 이 격리 시험은 일반 gameplay 인증 체계 완성이나 기존 정치/경제 network path 안전성 인증이 아니다.

PublicationEvents는 append-only durable log다. consumer dispatch나 DELIVERED/PUBLISHED marker path는 없다. 이번 atomic publication row 시험을 **외부 semantic side effect의 exactly-once/dedup 인증으로 계산하지 않는다.**

## 11. A의 E1 test evidence와 독립 검증 차이

A 결과 JSON의 27/27 및 SHA는 원본 그대로 기록했다. 그 숫자가 이번 blocking 조건을 검사했다는 의미는 아니다. 별도 보존한 `FrozenSource/A_E1_Runner/Program.cs`에서 확인한 주요 coverage gap:

- Test15는 queue submissions 후 **Task.WaitAll부터 실행**하고 scope Dispose에 들어간다. active full-queue shutdown을 검사하지 않는다.
- Test16은 500ms delay/50ms sleep 후 Dispose이며 장시간 held observer나 writer liveness 검사를 하지 않는다.
- Test18의 이름에는 CAS/audit/precommit/WAL cuts가 있지만 실제로는 **한 번 정상 commit 후 새 coordinator retry**를 수행한다. 실제 hook/barrier/kill cut이 아니다.
- Test19는 **아무 작업 없는 coordinator Dispose** 후 IsDisposed만 검사한다. repository observer의 post-return activity 측정이 없다.
- Test20은 idle StartupManager.Shutdown을 호출한다. actual Main 및 활성 writer를 검사하지 않는다.
- 정상 loser가 durable ABORTED를 만든 **mixed-state restart positive**, cross-principal same OperationId history, envelope/audit identity tamper가 독립 proof로 빠져 있다.

따라서 Dev 설명을 신뢰 근거로 사용하지 않고 actual Release paths를 재현했다. 개선된 code/test evidence는 인정하면서 coverage 밖의 성공을 추론하지 않았다.

## 12. QA 도구 한계와 재현 자산

사용한 QA 파일: `run_checks.py`, `extra_battery.py`, `deep_checks.py`, `confirmed_checks.py`, `valid_consistency_checks.py`, `completion_checks.py`, `normal_checks.py`, `input_validation_checks.py`, `provenance_checks.py`; harness `Harness/Program.cs` 및 `HarnessExt/Extended.cs`.

다음은 **QA 도구 준비 오류로 분리**하고 candidate 실패 수에 넣지 않았다: 초기 native e_sqlite3 search path 누락, QA extension의 options type 오타, 역사 DB folder date 오타, Windows Python encoding 누락, 중복 fixture 생성 assertion, 상대/절대 freeze-key 혼동. QA 폴더에서 수정 후 해당 범위만 재실행했다. 초기 혼합 ABORTED fixture의 masking과 affected-row0 시험도 앞에서 구분했다.

이전 fingerprint helper는 invalid surrogate를 direct hash 비교하려다 exception으로 끝나 완전한 matrix 결과를 출력하지 않았다. 그 helper의 미완료 결과를 성공으로 쓰지 않았다. invalid-field admission은 별도 `inputs` actual route 27건으로, envelope collisions는 독립 request/retry로 검증했다.

QA-only build의 NU1900은 제한된 네트워크에서 NuGet vulnerability metadata 조회 실패이며 후보 Production build warning으로 계산하지 않았다. 최종 실행은 frozen DLL direct reference. 모든 clean shutdown 검증의 outer timeout은 안전장치이며 forced kill을 성공 판정에 사용하지 않았다.

증거 파일 및 hashes:

- [qa-evidence-manifest.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/qa-evidence-manifest.json)
- [results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/results.json): OS concurrency, storage/cuts, identities, 기존 schema/negative
- [deep2-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/deep2-results.json): JSON boundary, independent deep schema, natural ABORTED/history failures, real Main, shutdown cuts
- [confirmed-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/confirmed-results.json): READY baseline 기반 false READY, actual service observer, control identities, UNKNOWN query/retry
- [valid-consistency-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/valid-consistency-results.json): 정상 8-commit baseline의 regression negatives
- [normal-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/normal-results.json), [completion-results.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/Evidence/completion-results.json): actual EXE startup/listen/false READY, extra hard-kill, valid-hash balanced duplicate
- [freeze-before.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/freeze-before.json) / [freeze-after.json](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/freeze-after.json): Production 353 / 353, diff 0

## 13. Master에 대한 최종 권고

1. **이번 REV4 gate는 FAIL.** ADR-001 Foundation next slice release를 이 결과로 승인하지 않는다.
2. 008/019의 좁은 closure를 채택할 수 있으나 007/013은 유지한다. 001은 5개 typed input exception과 명시적 size 계약 확인까지 PARTIAL.
3. 다음 candidate에는 정상 ABORTED 포함 restart와 cross-principal identity history 계약을 먼저 수정하고, semantic graph envelope/derived ID/audit 내용을 대조해야 한다.
4. caller 응답 종료와 writer service 종료를 분리하면서 **final Dispose/Shutdown/Main 완료가 actual writer exit를 기다리는** 계약을 구현해야 한다. readiness false나 모든 Task 완료로 worker termination을 대체하지 않는다.
5. 수정 candidate의 fresh SHA/MVID/PDB 및 공식 REV4 이후 Release manifest를 제출하고, 이 문서의 active shutdown / legitimate-restart / false-READY / typed input 사례를 mandatory regression으로 실행한다.

**Final verdict: FAIL.** Production 수정·재빌드 없이 독립 검증을 완료했으며 다음 지시를 기다린다.
