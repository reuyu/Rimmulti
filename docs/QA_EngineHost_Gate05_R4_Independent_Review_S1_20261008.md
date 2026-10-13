# Gate05-R4 독립 정적 QA S1

**STATIC_REVISION_REQUIRED / RUNTIME_UNTESTED**. R4는 R3의 SIMULATION proposal와 READ_ONLY validator 사이 직접 mode 충돌을 제거했고 StartTime fallback·nonce 없는 Bind overload·Execute target clamp를 없앴다. 그러나 새 receipt proposal mode의 Promote 검사, admitted SHA/config/workload 정상 경로, stable target/MD129 state, typed content/native 증거와 최종 후보의 실행 전 provenance는 아직 충분하지 않다. Master R4-M01~10 핵심 관측에 독립 동의하며 개선과 남은 공백을 구분했다.

| Identity / scope | 값 |
|---|---|
| WP / revision | WP_QA_ENGINE_GATE05_R4_INDEPENDENT_REVIEW / S1 |
| Delivery | SOL-GATE05-R4-INDEPENDENT-REVIEW-S1-20261008-01 |
| Unique result | SOL-GATE05-R4-INDEPENDENT-REVIEW-S1-20261008-7b78d7a3b86e49ef8a0d611cc1bf8e33 |
| Producer / time | Sol / 2026-10-08 Asia/Seoul; terminal completed_at은 COMPLETION.json |
| 허용 범위 | exact frozen232 read-only static/raw/metadata review |
| 실제 QA 실행/변경 | Candidate/runner/game/native 실행0,build0,production 변경0,adverse reproduction0 |
| Gate | Runtime E2 NOT_RELEASED; Engine002006/Pipeline007/current schema/G-Q1 OPEN; Foundation HOLD |

[Immutable manifest](C:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1/MASTER_GATE05_R4_REVIEW_FREEZE_MANIFEST.json) SHA `D047D0095CEDDA8E5F0FB6871EA4C24AF0866CA569514049FFAD7E91B7C1460C`와232 file SHA를 독립 대조했다. Implementation/runner/raw/report/completion은 manifest frozen_path만 사용했다. Mutable Engine 및 원본 installed/UserData는 이번 QA에서 읽거나 수정하지 않았다. Post-completion snapshot은 pre-run proof가 아니다.

| Candidate | DLL SHA / MVID / matching PDB SHA |
|---|---|
| Selected Debug | 4F5663FDBBFA09A8B2BE460D09950FD22B9567459F7116E69D0B1C558F189B9E / ed98e6f9-aa63-47ee-ae21-84f59465d2bb / CC796E68C592C94345DF41D64609B5D207933B8F5FE805146875D9E61B8D12C4 |
| Alternate Release | 7532FF152314892A4AB95A0117107C0845B0D7BAD170C3B840BA24F3EADA270B / d602525d-4248-442a-8f51-77e22f8484bf / 53E33B734E2BF25110DC190FB461E5F011E808DF541742E1A56F52421E61EBDB |

양쪽 CodeView/PDB GUID와 각 document checksum4/4가 matching frozen sources와 일치했다. [R4_LINEAGE.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/R4_LINEAGE.json)에 전체 metadata를 기록했다. 해시/metadata는 runtime/authority proof가 아니다.

Complete는 W2600/2607에서 current Authority/Grant 존재와 SIMULATION을 요구하고 W2614/2619에서 Task/Result READ_ONLY를 요구한다. 따라서 R3의 direct equality 회귀는 정적으로 개선됐다. Receipt.simulatorOperationMode는 C62/W2706에 기록되지만 Promote가 참조하지 않으므로 closed-context 계약은 더 확인해야 한다. R4 Complete의 earlier nullable 비교만 보고 current authority가 없어도 통과한다고 주장하지 않는다. Promote의 기존 authority/grant/generation/epoch/profile/live recensus/staged SHA/atomic replacement 검사는 존재한다. 정상 전체 STEP→SEAL→STAGE→fresh validation은 아직 실제 native 관측이 없다.

Admitted executable path는 추가됐으나 기본 공백, 설정 존재 때만 supplied path 제한이며 AdmittedOperatorValidatorSha는 선언 외 사용이 없다. Approved binary/config/task/bootstrap/workload/result origin이 production 정상 경로로 연결됐다는 증거가 없다. Execute clamp 제거를 인정하지만 stable target↔loaded mapping과 Promote first-map fallback은 남았다. MD129의 Execute/Bind 실패를 operator state 철회와 clean readmission에 역할별로 연결해야 한다. Actual assembly/Def census/cache invalidation/R-format/cost material field 및 R4 DLC inventory 추가는 인정한다. 그러나 지원 typed encoding, null/missing/empty/order, patch/settings coverage와 DLC 조회 예외의 unknown 처리는 v4/LOSSLESS flag로 증명되지 않는다.

원문 JSON43 PASS와 raw43 PASS의 ID·순서·counts는 일치했다. QA 재실행은 없다.

| 독립 coverage 분류 | Count | 인정 범위 |
|---|---:|---|
| Metadata/hash | 4 | 제출 binary/file/MVID identity observations |
| Mock/reflection fixture handler·file IO | 35 | 주입 state/profile/Game/census/hash를 사용한 component controls |
| OS child lifecycle inside fixture | 1 | 실제 OS child launch; native semantic validator 아님 |
| Reflection API inventory | 1 | Nonce-less overload 부재 검사 |
| Schema constant | 1 | v4 constant; DLC/typed encoding proof 아님 |
| Cache helper state | 1 | InvalidateCache/IsCached 검사; 실제 content lifecycle proof 아님 |
| Native semantic normal loop | 0 | actual loaded profile/stage/census/result/receipt 미관측 |

Producer class counts는 GENUINE_CONTROL_FLOW41/GENUINE_SUBPROCESS1/HARNESS_FIXTURE_ASSERTION1이다. GEN-03의 actual result writer는 child가 아니라 runner R547이다. GEN-07은 mocked Game/GenerateCensus/ComputeManifestHash로 Promote를 호출한다. SEC-06은 result StartTime mismatch이고 OS getter 실패를 실행한 증거가 아니다. CLAMP-03은 특정 error 문구 부재만 검사해서 성공 validator result를 요구하지 않는다. [COVERAGE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/COVERAGE_INDEX.json)에43 row별 범위가 있다.

Native RuntimeCopy inventory는 root binaries/text5 + selected mod DLL/PDB2, 총7개다. Raw는 project exe/cwd/CLI/PID18816/start/5000ms 후 kill을 보고하지만 numeric exit/loader log/실제 data·Managed·core·DLC·mod/config/userdata·selected candidate/profile/census/result/receipt는 미관측이다. Actual userdata isolation을 CLI label만으로 인증하지 않는다. Assets 공백은 관측되지만 이를 유일한 실제 failure cause로 확정하지 않는다. Producer IMPLEMENTATION_PARTIAL/NATIVE_UNTESTED 공시는 인정하고 DRM/Steam/headless/actor/cause를 추정하지 않는다.

Packaging은 R3보다 개선됐다. Completion18 artifact SHA/size 및 final report9 SHA/size row가 실제 frozen bytes와 맞고 exact task/WP/revision/e1_verdict/limitations/required roles/absolute paths가 있다. Limitations는 의미 있는 객체이며 checker string/list 자료형 계약 불일치다. 이를 자료 부재로 표현하지 않는다. 다만 pre-run7 identity row 중 selected/alternate/PDB/Worker5 SHA·size가 final과 다르다. Before9 baseline row는 prior R3 SHA가 맞지만7 size가 다르다. [PACKAGING_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/PACKAGING_INDEX.json)에 exact declared/actual 차이를 기록했다. Final raw PROV 보고나 사후232 freeze는 stale pre-run을 final 실행 전 provenance로 바꾸지 않는다.

[독립 findings](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/INDEPENDENT_FINDINGS.md)는 R4-M01~10별 동의/제한과 function/line/SHA를 설명한다. [EVIDENCE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/EVIDENCE_INDEX.json)은 frozen inventory/source anchors/runtime7을 결속하며 [NORMAL_ROLE_TRACE.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/NORMAL_ROLE_TRACE.json)은 R3→R4 role 변화와 남은 carried field를 기록한다. [최소 corrective priorities](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008/CORRECTION_PRIORITIES.md)는 좁은 codec/content 작업과 operator/native packaging 작업을 나누는 방향을 권고한다. Master가 소유권/순서/통합후보/새 WP를 결정한다.

R4frozen232/prior387/archive19/Pipeline206/QA1205 및 manifests/이전 terminal bindings는 전후 독립 hashes로 보존했다. 상세 시각/결과는 PRESERVATION_BEFORE.json/PRESERVATION_AFTER.json, 최종 report·manifest·index 결속은 EVIDENCE_MANIFEST.json/RESULT_INDEX.json/COMPLETION.json에 있다. Installed old2D64… 대 observedBB3B… incident는 기존 OPEN/UNKNOWN이며 원본 재독취/restore/정상화 없음. 보존 inventory를 installed baseline 보존으로 확대하지 않는다. 사용자 승인 직접 Master 보고의 실제 tool 증거는 RETURN_TOOL_PROOF.json/DELIVERY_STATUS.json에 따로 남긴다. Static 계약 공백은 exploitation proof가 아니며 새 E2 PASS/closure/Foundation release도 없다.
