# R27 Capture15 독립 정상 관측 계약 — 준비 S1

이번 결과는 READ_ONLY_PREPARATION_COMPLETE이며 실행 PASS가 아니다. 동결 R25 source/binary/PDB와 보존 R26 literal prospective oracle, Master 승인 R27 WP 및 API 정정만 사용했다. A의 현재 R27 소스·bin·obj·runner·oracle·보고서는 읽지 않았다. R27 public class의 구현·candidate SHA/MVID·actual loaded identity는 NOT_REVIEWED/PENDING이다. 기존 R26 14group 제안은 입력 준비로만 재사용하고 다음 Master15 getter 그래프로 명시적으로 변환했다.

승인 class는 public sealed OperatorChildLaunchInputs, Capture(parentReceipt, childReceipt, task, taskFilePath), private constructor다. 아래 순서는 **향후 QA 관측 순서**이며 production wire schema를 만들지 않는다. 현재 R27 구현에 이 API가 존재한다고 확인한 것이 아니다.

| 순서 | 정확 getter / C# type | 독립 기대값 source |
|---|---|---|
| 1 | ParentReceipt / OperatorStartupAdmissionReceipt | 별도로 admitted된 SIMULATION receipt11와 nested snapshot15 |
| 2 | ChildReceipt / OperatorStartupAdmissionReceipt | 별도 READ_ONLY raw config14+original7에서 admitted된 receipt11/snapshot15 |
| 3 | ApprovedChildDeclaration / OperatorLaunchDescriptor | child 내부 Approved*7을 실제 소문자 fields7로 복사한 detached descriptor |
| 4 | Task / ValidatorTask | caller task27의 모든 원문 scalar를 private copy, 매 getter detached DTO |
| 5 | TaskFilePath / string | input taskFilePath 원문 absolute 문자열 |
| 6 | ExecutablePath / string | parent.Snapshot.AdmittedValidatorExecutablePath |
| 7 | ExecutableExpectedSha256 / string | parent.Snapshot.AdmittedValidatorExecutableSha256 |
| 8 | WorkingDirectory / string | child.Snapshot.ValidatorCwd |
| 9 | SelectedUserDataDirectory / string | child READ_ONLY selector의 ValidatorUserDataDirectory 선언값 |
| 10 | OperatorOptionValues / IReadOnlyList<string> | approved7 값을 별도 지정 순서로 저장한 read-only sequence7 |
| 11 | TaskInvocationValues / IReadOnlyList<string> | [원문 taskFilePath, copied task.capabilityNonce] |
| 12 | ResultChannelPath / string | copied task.resultChannelPath 원문 |
| 13 | StagedFilePath / string | copied task.stagedFilePath 원문 |
| 14 | StagedSha / string | copied task.stagedSha 원문 |
| 15 | Scope / string | DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED |

Controlling API correction SHA AA38D50D9B6EC9E2B74327BAB8348E1DEDD4EFB87BC0A2AECF0C85B27C39B7A3를 사용한다. Existing descriptor는 properties가 아니라 public string fields다. **반환 descriptor 선언 순서**는 `originId, expectedConfigId, expectedRole, expectedCapabilityBoundary, launchPlanId, expectedConfigPath, expectedConfigSha256`. **OperatorOptionValues 순서**는 `expectedConfigPath, expectedConfigSha256, originId, launchPlanId, expectedConfigId, expectedRole, expectedCapabilityBoundary`의 값이다. Semantic correction table의 row 순서를 descriptor 선언 순서로 사용하지 않는다. PascalCase field/property를 새로 만들거나 bound canonical Role/cap으로 approved original role/cap을 대체하지 않는다.

PLAIN/OPAQUE padded 정상 두 pair에서는 approved role/cap이 기존 factory의 private Trim 이후 `read_only`와 `local_sandboxed`인 반면 BoundRole/CapabilityBoundary는 `READ_ONLY`/`LOCAL_SANDBOXED`다. Oracle는 이 차이를 강제로 보존하여 잘못된 bound 값 사용을 관측할 수 있게 했다. 원문 origin/plan의 앞뒤 공백·Ω/config ID/opaque policy ID/revision/UTC .1234567Z 및 .0000000Z/Unicode 절대경로/array order는 새 normalization을 하지 않는다. Parent-child cross-policy pair는 원문 데이터를 복사하는 정상 제어이며 실제 pairing/content equality나 issuer authentication이 아니다.

Task27은 frozen EngineHostCensus:74–100의 원래 field 순서로 관측한다. Strings22, Int64(simulatorGeneration,workerGeneration,resultEpoch)3, Int32(targetMapIndex)1, Boolean(isConsumed)1이다. JSON integer type만으로 CLR width를 증명하지 않으므로 향후 exact source/PE public field types 및 typed observation을 별도로 확인한다. CapabilityNonce/secret/processId/registeredProcess strings와 staged/result paths를 누락하거나 실제 process proof로 해석하지 않는다. Synthetic PID7001·nonce·config identities는 QA literal이며 actual operator 발급·OS 실행을 나타내지 않는다.

PROSPECTIVE_CAPTURE_ORACLE.json은 기존 R26 입력 자료 SHA C103E852…를 고정하여 네 pair를 작성했다. Parent14와 child14는 독립 작성된 원문을 그대로 보존했다. Config role 변경으로 child를 파생하지 않았고 actual candidate output을 기대값으로 복사하지 않았다. Raw UTF8 config text/SHA/bytes, original7/usedClone7, receipt11/public snapshot15/policyrecord4/redaction13, full nested receipt redaction11, task27 모두 정의한다. R27 getter names를 가진 Capture15와 별도의 QA observation envelope(complete Capture, two records, two snapshot redactions, two receipt redactions)를 정의했다. 이는 QA-owned observation schema이며 기존 DTO나 external schema를 바꾸지 않는다.

Compact Capture15/envelope/Task27/approved7/option7/invocation2 UTF8는 ordered expected data에서 독립 Python JSON writer로 생성한다. BOM과 trailing newline은 없다. Pretty receipt/snapshot redaction만 승인된 Windows CRLF 기대값을 사용한다. Compact policy digest는 기존 source의 별도 ordered serializer 입력으로 계산하며 pretty newline과 섞지 않는다. Future actual 결과를 Trim/normalize/ignore-whitespace하거나 DateTime으로 바꾸지 않는다. QA가 redaction JSON을 파싱해야 한다면 local DateParseHandling.None을 지정하거나 typed original string으로 관측 object를 직접 구성한다. 기존 R21 nested UTC와 R25 S2 Windows pretty correction을 입력 준비에 반영한 것이며 그 PASS를 R27 실행으로 승계하지 않는다.

각 pair의 BEFORE_EDITS, AFTER_CALLER_TASK27_AND_SUBMITTED_DESCRIPTORS, AFTER_RETURNED_TASK27_APPROVED7_POLICY_LIST_COPY_EDITS 세 단계 전체 기대값은 같다. 모든 getter를 Master 순서로 읽고 full typed/codepoint/order/rawbytes를 **변경 전에 저장**한다. Caller의 task27과 factory에 실제 제출한 parent/child descriptor7 각각을 모두 바꾼다. 이후 새 정상 receipt/factory/Capture로 재적용하지 않고 기존 capture 전체를 관측한다. Retained returned Task27와 Approved7을 모두 바꾸고, 기존 snapshot getter가 반환한 detached policy declaration/record의 ID/revision/list/digest를 바꾼다. Read-only list는 materialized detached copy만 바꾼다. Real read-only backing을 cast-mutate하거나 exception을 확인하는 부정 실행은 하지 않는다. 모든 원본 graph와 raw UTF8가 처음의 독립 기대값과 같아야 한다.

원문 config14는 raw factory bytes에서 decoded되는 내부 config이므로, 별도의 QA local config DTO를 수정했다고 caller-connected constructor proof를 주장하지 않는다. 실제 연결된 mutable 입력인 task27와 submitted descriptors, 반환 policy/record/task/descriptor를 명확하게 구분한다. 원래 fixture 파일·oracle·callplan/source는 before-build/calls pin 이후 재작성하지 않는다. Caller 및 returned edits는 소유한 메모리에만 적용하는 미래 정상 copy operation이다. Edited task의 role/nonce/consumed 등이 달라져도 admission/control plane/Capture를 다시 호출하지 않으므로 invalid-input guard 결과를 시험하지 않는다.

기존 receipt/snapshot은 validated immutable object이고 policy와 list getter는 defensive copy/read-only wrapper다. Master는 ParentReceipt/ChildReceipt의 동일 기존 reference 보관·반환을 허용한다. 새 receipt constructor/deep serialization clone을 요구하지 않는다. 잘못된 재구성이 approved7/opaque policy/UTC를 바꾸는 위험을 source/whole graph로 확인한다. Task는 caller reference를 보관하거나 private copy를 그대로 공개하면 안 된다. Approved7도 getter마다 새 descriptor를 반환해야 한다. Constructor-copy strategy와 각 backing visibility는 새 candidate freeze 뒤 독립 static review에서 확인한다.

IReadOnlyList<string> interface만으로 private backing 불변성을 증명하지 않는다. Raw mutable array/list가 getter에서 노출되는지 future source/PE/static audit가 필요하다. Detached copies를 수정한 뒤 원본이 그대로인 정상 관측은 그 자체로 backing을 숨긴다는 증거가 아니다. COPY_OWNERSHIP_MATRIX.json과 CONSTRUCTION_COPY_RISKS.json에서 정상 실행 제어와 SOURCE_ONLY backing 판정을 분리했다. Private field reflection, readonly collection mutation exception, malformed/default/null/rejection/adverse probes는 실행 계획에 없다.

미래 명시 QA WP가 승인하면 한 run의 primary direct counts는 normal IssueAdmissionReceiptFromBytes8, direct IsValid8, Capture4다. Capture 내부의 receipt validation/selector/factory Clone/parser는 nested calls로 별도 구분한다. Fifteen ordered getter observation는4pair×3phase=180이다. 두 receipt와 snapshot의 redaction helper 및 policy-record helper는 각각 phase별24회로 사전 명시했다. ParentReceipt/ChildReceipt를 다시 읽는 암묵적 추가 call 대신 각 phase의 보관한 getter refs를 observational helper에 사용한다. 이 카운트는 callplan 제안이고 실제 측정값·nested profiler·PASS label이 아니다.

Frozen ValidateAdmissionReceipt는 기존 Path.GetFullPath로 bound/approved paths를 비교한다는 source 사실을 기록했다. Master가 허용한 existing IsValid 호출과 새 Capture 안의 direct/new output normalization 금지를 구분한다. 모든 transitive helper에서 Path.GetFullPath 호출0이라고 주장하지 않는다. 새 taskFilePath/result/stage 문자열은 input 그대로, child declared root/cwd는 이미 admitted된 child snapshot 그대로 관측한다. Directory/File/Process/global state/registration/launcher/IO를 Capture에 추가할 권한은 없다. 기존 fully-qualified predicate 이름은 OperatorStartupConfigAdmissionFactory.IsFullyQualifiedWindowsPath다.

FUTURE_EXECUTION_PROVENANCE_CHECKLIST.json의 7단계는 새 candidate Master admission→before-build expectation/toolchain/all references pin→QA final build1→fresh en-US→fresh de-DE→recursive seal/immutable terminal이다. 현재 compiler/QA runner/factory/Capture/load/native/Process/assetscopy0이다. Old R25 SHA/MVID/PDB source4/4는 정확한 역사 lineage 정적 관측이며 R27 candidate identity가 아니다. A terminal→Master new freeze/admission→별도 original Sol execution WP 전에는 실행하지 않는다. Complete streams/actual OS exit/PID/argv/cwd/all managed loaded SHA+independent MVID/pre-post/all recursive first-before-second/all-after proof가 필요하다. 실패는 raw 보존·Master 보고이며 자체 oracle 수정/재빌드/재실행으로 PASS를 만들지 않는다.

CaptureScope·private constructor·IsValid/IsTrusted/정상 equality·typed graph success는 operator issuer/pairing/current task authentication이나 native admission이 아니다. R27에 parent-child exe/profile/policy equality나 task/nonce/currentgeneration authority 검사, 실제 registration/global receipt/nonce 생성/ProcessStart/cwd/frontend/Genroot/revocation 연결을 넣지 않는다. 이들은 M04/M05/M06/M07 후속 scope OPEN이다. Dedicated Server final Domain Authority, closure/release Master, Engine002006/Pipeline007/schema/G-Q1/exact PlayerGlobal/physical split OPEN, Foundation HOLD/fullnativeE2 NOT_RELEASED를 유지한다.
