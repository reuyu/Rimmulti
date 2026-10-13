# R29 startup pair 독립 정상 오라클 준비 S1

**PREPARATION_COMPLETE / R29_CANDIDATE_NOT_REVIEWED / NO_EXECUTABLE_TEST_PASS**. Master의 새 보조 pair 계약을 기준으로 6개 정상 입력, 사전 예상 bundle UTF8 원문·SHA, 전체 typed/raw/copy oracle와 후속 provenance 기준을 작성했다. 생산기·QA compiler·candidate·Bootstrap/Awake·Unity/game/native·Process·adverse/rejection 실행은 모두 0이다.

- delivery: SOL-GATE05-R29-STARTUP_PAIR-PREP-S1-20261012-01
- WP: WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_PREPARATION / S1
- result: SOL-GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012-2b883a31352547c6bda6f398d204600f
- QA root: C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012

## 근거와 독립성

Controlling Master R28 dual review SHA 7C574B269562FAA000E9A70F77C2D593684C38FB41C0569F70C3AB0585A3DB42, R29 pair contract SHA 2EEE68E2E3B6D0FD3777D8F1F13EDDE3239D7697CD9339B03B324D108CE9A531, frozen R27 manifest SHA 1FD4B9EFB368EE03F327241418C5CC0ACC08F9210E6E1BD271AECC373D219EE3가 기준이다. R28 source/IL 증거와 R26/R27 독립 historical literal data만 재사용했고 기존 PASS를 새 candidate에 승계하지 않는다.

현재 A R29 Worker source·publisher·빌드 출력 및 새 구현을 분석하지 않았다. 현재 승인 mutable7은 보호 baseline에서 제외하고 읽지 않았다. 현재 fixed Census·csproj는 SHA·size만 확인했다. 필수 baseline14105에는 fixed generated obj metadata 4개가 포함되어 그 **보호용 해시만 읽었다**. 따라서 모든 obj 경로에서 단 한 바이트도 읽지 않았다는 포괄 주장은 하지 않는다. 그 4개는 semantic 분석 대상이나 승인 mutable7이 아니며 PRESERVATION_HASH_SCOPE_NOTE.json에 exact paths를 기록했다.

R28 completed artifact의 Master 채택과 actual usagefailed/notLoaded175는 별도 상태로 보존했다. 이번 R29는 원래 endpoint의 새 active delivery와 immutable ACK에 따른 작업이며 모델·계정·대체 QA·중복 WP를 만들지 않았다.

## 새 계약의 정확한 경계

Master가 채택한 **새 PoC 보조 schema**는 we-operator-startup-pair/v1이다. 기존 canonical config14/descriptor7/task27은 변경되지 않는다.

| Bundle writer 순서 | 타입·원문 조건 |
|---|---|
| schemaVersion | string, we-operator-startup-pair/v1 |
| operatorPairId | opaque nonempty string, 원문 유지 |
| parentDeclaration | 기존 descriptor7, 독립 SIMULATION 선언 |
| childDeclaration | 별도 기존 descriptor7, 독립 READ_ONLY 선언 |

Descriptor writer 순서는 originId, expectedConfigId, expectedRole, expectedCapabilityBoundary, launchPlanId, expectedConfigPath, expectedConfigSha256다. Bundle은 UTF8/no BOM, compact comma·colon, ensure_ascii false, 마지막 LF 없이 쓴다. Decoder는 exact closed keys/types/duplicate/missing/additional/null guards를 기존 두 receipt factory보다 먼저 적용해야 한다. Writer canonical order와 arbitrary decoder property order rejection은 다르다. Raw whole bundle SHA와 semantic field/type identity는 함께 검증한다.

새 non-secret operatorpairfile/operatorpairsha carrier는 각각 단일 -key=value argv다. 모든 opaque 7개 값은 bundle에 둔다. 공개 locator path의 추가 =는 core exact2part parser로 표현할 수 없으므로 source guard로 거부하며 값을 재작성하지 않는다. BOTH absent일 때만 legacy self7을 유지하고, malformed/incomplete/duplicate pair나 pair+self7 conflict를 legacy로 낮추지 않는다. Optional ValidatorArguments는 새 mode에서 blank만 허용하며 blind concat·unproven native flags·task/nonce/secret CLI를 승인하지 않는다. 이것은 계약의 source-review 조건이며 해당 invalid guard를 실행하지 않았다.

## 6개 사전 정상 입력

| Case | 값의 특징 | 예상 bundle bytes |
|---|---|---:|
| PLAIN_PLAIN | 양쪽 plain policy | 1036 |
| OPAQUE_OPAQUE | 양쪽 원문 opaque policy | 1040 |
| PLAIN_OPAQUE_PADDED | plain/opaque, padded lowercase 원문 role·cap | 1068 |
| OPAQUE_PLAIN_PADDED | opaque/plain, padded lowercase 원문 role·cap | 1068 |
| OPAQUE_EQ_QUOTE_BACKSLASH | 양쪽 ID·origin·plan·PairId의 =·quote·backslash·Ω | 1185 |
| OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | 같은 encoding, padded role·cap | 1215 |

첫 4개의 parent/child raw config14는 역사 입력과 byte exact다. 원래 historical descriptor7은 sidecar에 그대로 보존했고 새 fixture의 expectedConfigPath만 자체 QA 실제 입력 위치로 명시적으로 재결속했다. 이는 publisher가 가상 C:\QA 경로를 생성하거나 읽게 하지 않고 실제 raw 입력 파일과 approved path/SHA 관계를 사전에 검증하기 위한 **새 prospective fixture locator**다. 역사 파일은 수정하지 않았다.

추가 2개도 parent와 child 입력을 각각 독립적으로 작성했다. Parent role을 바꿔 child를 만들지 않았다. ConfigId의 =·따옴표·역슬래시·Ω는 내부 문자로 넣고 origin/plan/PairId의 outer padding을 유지했다. 기존 nested Snapshot이 수행하는 ConfigId/IssuedAtUtc Trim·path GetFullPath 사실을 없애는 전이적 무정규화 주장을 하지 않는다. 새 pair 포장과 getter가 원문 declaration7/PairId에 추가 정규화를 해서는 안 된다는 조건은 별개다.

각 case에 parent.config.json, child.config.json, parent.approved7.json, child.approved7.json, expected.bundle.json을 **독립 예상·입력 파일**로 작성했다. 30개 파일은 사전 SHA·size·hex·UTF8 literal로 결속했고 publisher output이 아니다. Future publisher outputroot는 아직 생성하지 않았다. 실제 publisher filename·invocation·output provenance manifest 형식은 새 frozen source를 읽기 전까지 UNFROZEN이다.

PRE_RUN_EXPECTED_ORACLE.json SHA 7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02 /1030401 bytes에 각 bundle full raw·SHA, 두 config14/original7, factory usedClone7, receipt11/snapshot15/policy4/record4/redaction13/receipt-redaction11과 예상 UTF8를 기록했다. Receipt AdmittedAtUtc의 기대값은 기존 source처럼 Snapshot.IssuedAtUtc의 원문 literal이며 새 실행 시각을 사용하지 않는다.

전체 observation envelope당 206개, 합계 **1,236개 계층별 타입 행**이다. Object·array·boolean·string과 ordered keys/array 길이를 포함하므로 primitive leaf나 실행 assertion 1,236개로 부르지 않는다. 3단계×6case=18개의 **예상 graph 유지 조건**이며 관측된 runtime graph가 아니다.

## 원문 선언과 receipt usedClone 분리

Master 계약 이름만 ADOPTED_CONTRACT_NOT_YET_IMPLEMENTATION_REVIEWED로 기록했다. 실제 R29 type/method token·signature·구현 상태는 새 candidate까지 동결하지 않는다.

| 계약 API | 사전 기대 |
|---|---|
| OperatorStartupPairSnapshot.ParentReceipt | readonly 기존 receipt, parent 전체 graph |
| ChildReceipt | readonly 별도 child receipt 전체 graph |
| OperatorPairId | 원문 string |
| Scope | DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY |
| GetParentDeclaration() | 매 호출 fresh detached 원본 parent7 |
| GetChildDeclaration() | 매 호출 fresh detached 원본 child7 |
| OperatorStartupPairAdmission.AdmitPairBytes(bundleBytes, expectedBundleSha, parentConfigBytes, childConfigBytes) | positive tuple true/empty-error/non-null pair; PURE data-only |

새 AdmitPairBytes에는 mutable caller descriptor를 추가로 전달하지 않는다. 기존 factory가 만든 usedClone의 role/cap/path/SHA trim과 새 pair getter의 **original bundle declaration7**은 서로 다르다. Padded case에서 trim된 usedClone을 pair getter로 반환하면 미래 원문 oracle가 구분할 수 있다. Native publisher/운영 issuer approval이나 registration 권한은 public PURE success·scope 문자열·readonly type·IsTrusted에서 나오지 않는다.

## 후속 정상 copy 검증 계획

모두 미래 candidate admission 이후의 계획이며 현재 실행하지 않았다.

1. 성공 후 caller bundleBytes/parentConfigBytes/childConfigBytes 배열을 편집하고, 재-admission 없이 기존 pair graph가 같은지 확인한다.
2. 반환 parent7·child7 각각 모든 scalar를 편집한 뒤 다시 getter를 호출해 새 detached instance와 original7을 확인한다.
3. 각 receipt의 반환 policy declaration/record/ordered ID list를 정상 detached object에서 편집하고 전체 receipt/snapshot/policy/raw 값 유지 여부를 확인한다.
4. readonly4는 source/metadata getter-only·private immutable backing과 정상 조회를 따로 확인한다. Readonly backing cast-write·예외 재현·reflection setter·invalid case를 만들지 않는다.
5. BEFORE_EDITS / AFTER_CALLER_BYTE_ARRAY_EDITS / AFTER_RETURNED_DECLARATION_POLICY_DETACHED_EDITS에서 같은 사전 full graph를 비교한다. 실제 출력으로 기대값을 고치거나 Date/Unicode/경로/pretty newline을 사후 정규화하지 않는다.

기존 receipt/snapshot redaction pretty의 사전 Windows CRLF 기대값과 새 bundle compact/noLF 기대값을 구분한다. 과거 raw FAIL·R27 S1 stop은 유지한다.

## 생산기·bootstrap·native provenance 기준

PROVENANCE_AND_NATIVE_BOUNDARY_CRITERIA.json은 사전 literals→Master freeze→fresh compiler→plan-only publisher→new PURE pair 정상2culture→최종 lineage의 6단계 요구를 기록한다.

Publisher는 actual parent/child raw 입력·original approved7·PairId·outputroot, Python source/interpreter/argv/cwd/PID/numeric exit/full stdoutstderr와 실제 input/output manifest를 결속해야 한다. Exclusive new files/owned root/atomic publish·no overwrite·no subprocess/Process/native-launch source 증거가 필요하다. Output bundle은 사전 UTF8와 byte exact 비교하며 input/source를 before/after 재검증한다. Fixture publisher 실행은 local producer 구현의 좁은 증거이지 operational operator authorization/ACL/host launch 증거가 아니다.

새 candidate QA는 selected Debug/Release 실제 SHA/MVID, CodeView·matching PDB/source, 모든 compiler references, prospective inputs/oracle/callplan, actual loaded modules 및 recursive run evidence를 새로 결속해야 한다. 새 runner·fresh en-US/de-DE 실행과 첫 run 봉인·두 번째 후 재확인은 향후 승인 범위다. 현재 compiler를 실행하지 않았다.

Bootstrap source 리뷰는 pair를 AddComponent 전에 완성하고 pending transfer를 **created GameObject reference와 exact parent receipt**에 결속하는지 확인해야 한다. Awake는 side effect 전에 matching one-use acquisition으로 instance private profile을 가져가야 한다. Persistent global child registry/public getter/setter를 허용하지 않는다. AddComponent 후 바로 pending을 지워 synchronous Awake를 가정해서도 안 된다. 실패/destroy cleanup과 acquired profile OnDestroy clearing은 future source 확인 대상이다.

새 pairmode launcher는 M05 미승인 guard로 기존 launch body 전에 반환하고 task.isConsumed·RevokeReadiness·Process를 건드리지 않아야 한다. 기존 parent TryInstall·legacy launch/task/result/consume body는 유지한다. R29는 instance private startup profile까지만 다루며 current owned task capture/registration/protected typed receiver/single launch claim/M05/M07/actual content/native는 후속 별도 gate다.

Actual operator authorization/protected filesystem, core early effective root/config/prefs/cwd, OS quoting, native AddComponent/Awake timing, loaded profile 및 full stage/result authority는 여전히 미관측이다. R28의 argv logging 경로 때문에 새 CLI에 nonce/secret/taskcapability를 넣지 않는다. 별도 local channel은 MD126 범위이며 새 PKI를 요구하지 않는다.

## 자체 metadata 정정과 보존

소스 필드 집계의 첫 QA regex가 ExpectedPackagePolicyDeclaration?를 빠뜨려 own Python metadata AssertionError/exit1을 냈다. Failed script·trace·부분 source-map을 그대로 보존하고 새 corrected script에서 nullable 타입명만 인식하도록 바로잡아 config14를 확인했다. 후보·생산기 failure나 executable test FAIL이 아니다.

Protected baseline14105, frozen83, fixed Census·csproj의 before/after SHA·size를 검증하고 immutable ACK·manifest/index·COMPLETION에 exact identity를 결속한다. Mutable7/new publisher 및 current R29 구현을 읽지 않았고 보호 baseline fixed obj4는 hash-only 별도 기록했다.

R29 candidate NOT_REVIEWED, 실행 verdict/PASS 없음. Full Engine002006/Pipeline007/current schema/G-Q1/exact PlayerGlobal/physicalsplit OPEN, Foundation HOLD, full/native E2 NOT_RELEASED. Master만 다음 candidate admission·closure·release를 판단한다.

