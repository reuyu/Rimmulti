# Gate05-R3 독립 정적 QA 검토 S1

**STATIC_REVISION_REQUIRED / RUNTIME_UNTESTED**. 정상 SIMULATION proposal에 대한 READ_ONLY validator 결과가 Complete의 mode equality에서 거부되는 회귀를 source로 확인했다. R3의 nonce/DTO/context/consume/mod hash 개선은 인정하지만 전체 issuer/content/native 계약을 충족했다고 볼 증거는 없다. Master R3-M01~08의 핵심 판단에 동의하며 target census, Promote 재검사, cache lifecycle, fixture 의존성에 대한 범위를 정밀화했다.

| 항목 | 값 |
|---|---|
| Producer / WP / revision | Sol / WP_QA_ENGINE_GATE05_R3_INDEPENDENT_REVIEW / S1 |
| Delivery | SOL-GATE05-R3-INDEPENDENT-REVIEW-S1-20261008-01 |
| Unique result | SOL-GATE05-R3-INDEPENDENT-REVIEW-S1-20261008-181d1792f7a440a88a7d1dc1532febdf |
| 시각 기준 | 2026-10-08 Asia/Seoul; 정확한 completed_at은 COMPLETION.json |
| 실행 범위 | frozen133 defensive source/raw/metadata 읽기. Game/candidate/runner/native 실행0, build0, adverse fixture 재실행0 |
| Native / E2 | UNTESTED; runtime E2 admission/release 없음 |
| Gate | Engine002/006, Pipeline007/current schema, G-Q1 OPEN; Foundation HOLD |

검토 대상은 [Master freeze manifest](C:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/MASTER_GATE05_R3_REVIEW_FREEZE_MANIFEST.json)의 frozen_path다. Manifest SHA `124C6AA900CB50ECE5C2F31B75BC197ACA194995BB90BDEDBD7EDA6B830E0972` 및133 file SHA를 독립 재검증했다. Mutable Engine source/bin과 원본 installed/game/userdata는 읽거나 수정하지 않았다.

| Lineage | DLL SHA / MVID / PDB SHA |
|---|---|
| Selected Debug | 9851351B4F3E8DD14D16AB5BBC5932F6A0F71E34ABF49648FA7366945516B1BB / 501e64f4-2135-42b0-b997-8829c99f5001 / 3B93B64C62CE37E7D5856846562A30448E574619A0D1E8C96B9025974ADEB9BE |
| Alternate Release | CC675EC3D7933C7A163D43FDD1941AADE3B53BC1A6A2575D3096C170FA678217 / 355d01bf-ea8e-4f09-a547-4038e9bbf46e / 895350A2D329DE6EDFB2BB0C671223B82B3391F69BCF0248455B35084CF4689C |

양쪽 CodeView GUID/PDB match와 document checksum4/4를 확인했다. PDB의 original document name은 matching frozen source로만 해석했다. [R3_LINEAGE.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/R3_LINEAGE.json)에 전체 identity가 있다. 해시/metadata match는 실행·issuer 권한 증명이 아니다.

정상 모드 흐름은 STEP/SEAL의 READ_ONLY 금지(W1618/W1760), STAGE의 READ_ONLY task 생성(W1986), Execute의 task mode 복사(W2347), Complete의 task와 activeGrant 양쪽 equality(W2545)로 이어진다. SIMULATION grant를 유지하면 마지막 비교가 실패한다. Runner R286은 READ_ONLY grant와 reflection 주입 seal/task를 사용하므로 실제 STEP→SEAL→STAGE 성공을 확인하지 않는다. 후속 수정은 proposal operation mode와 validator execution role을 각각 결속해야 한다. [NORMAL_ROLE_TRACE.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/NORMAL_ROLE_TRACE.json)에 source SHA/line을 기록했다.

R3 source의 nonce 검사, expanded ValidatorResult25 fields, task/result/seal equality, configured channel만 읽기, consume 예외 readiness 철회, receipt 필드 결속, mod assembly missing-file guard와 material cost fields를 인정한다. 남은 공백은 admitted fixed executable/config/workload/result origin, 역할을 구분한 complete current context, stable target mapping, MD129 실패/복구 state, 지원 material content의 typed encoding 및 actual loaded profile이다. Census에 index/tile/parent/faction context가 이미 있고 Promote의 authority/grant/generation/epoch/profile/live census/staged SHA 재검사도 존재한다. 따라서 단순히 'context가 없다'거나 '최종 promotion 우회가 입증됐다'고 주장하지 않는다. Cache invalidation 역시 존재하며 lifetime/재검증의 충분한 증거가 필요하다.

원문 JSON/raw의32 PASS ID·순서·counts는 일치했다. QA는 원문을 재실행하지 않았다.

| QA가 분류한 제출 evidence | Count | 의미 |
|---|---:|---|
| Metadata/hash observation | 4 | 파일/해시/MVID 항목; native workload 증명 아님 |
| Reflection fixture / handler / file IO | 26 | profile mock와 주입 state를 사용하는 component control evidence |
| OS child lifecycle inside fixture | 1 | 실제 OS child launch; native semantic validator 아님 |
| Schema constant assertion | 1 | ADR-006B-v3 상수 equality; typed lossless content 검증 아님 |
| Native full semantic normal flow | 0 | actual fresh load/profile/census/result/acceptance 미관측 |

Producer labels는 GENUINE_CONTROL_FLOW30 / GENUINE_SUBPROCESS1 / HARNESS_FIXTURE_ASSERTION1이다. R3 csproj는 실제 game/Unity/Harmony dependency를 참조하므로 R3가 전부 game stub이라는 해석도 하지 않는다. 정상 child의 result 파일은 runner가 작성한다. [COVERAGE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/COVERAGE_INDEX.json)에32 row별 분류가 있다. Native log는 original Steam exe의 PID/start와5000ms 후 종료 문구를 남겼으며 실제 argv는 `-batchmode -nographics -quicktest`다. 보고서는 `-quicktest`를 생략한다. RuntimeCopy directory label은 isolated 실행 증거가 아니며 numeric exit/loader trace/실제 isolated userdata·mods/new candidate/profile/census가 없다. 원인 UNKNOWN이며 DRM/Steam 제약 또는 실제 saves 변경을 추정하지 않는다.

Original COMPLETION10 declared artifact SHA/size는 frozen 실제 파일과 맞았다. 그러나 exact dispatch_id/wp_id/wp_revision/completed_at/e1_verdict/limitations와 required roles 및 absolute paths는 계약에 맞지 않는다. Aliases는 같은 task로 해석되고 relative path는 프로젝트 내부 원문으로 대응된다. Report table의 Worker/Census/results/raw4 SHA 및 Worker/raw2 size가 실제/manifest와 다르다. 실제 manifest/source/PDB match와 보고서 표 오류를 분리했다. [PACKAGING_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/PACKAGING_INDEX.json)에 exact declared/actual SHA·size·completion 계약 차이가 있다. 실행 전 candidate/dependency/tooling/content 결속은 제출 패키지로 확립되지 않았고 사후133 freeze를 실행 전 proof로 소급하지 않는다.

[독립 findings](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/INDEPENDENT_FINDINGS.md)는 R3-M01~08의 동의/범위 제한/우선순위/function/line/SHA를 설명한다. [EVIDENCE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/EVIDENCE_INDEX.json)은 frozen133 inventory, source anchors, DTO/native evidence를 결속한다. [후속 최소 수정 권고](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/CORRECTION_PRIORITIES.md)는 정상 role 흐름, admitted operator/workload, closed context/MD129, typed content, isolated native 관측, 실제 hash와 표준 completion의 순서다. 새 후보 수정·실행·E2·closure를 QA가 승인하지 않는다.

보존 전후 검사 대상은 R3frozen133/R2frozen107/R1frozen147/archive19/Pipeline206/QA324·297·312·238/prep17이다. 실제 결과와 시각은 PRESERVATION_BEFORE.json/PRESERVATION_AFTER.json, 최종 hash 결속은 EVIDENCE_MANIFEST.json/RESULT_INDEX.json/COMPLETION.json에 있다. Installed old expected2D64… vs observedBB3B… incident는 기존 OPEN/actor·cause UNKNOWN이며 archive 보존을 installed baseline 보존으로 확대하지 않는다. Query 오류, public validation 요청, file channel, 정상 result-after-exit를 새 금지로 만들지 않았다. MD131 안전 replacement 및 MD132의 제한된 V4 scope를 유지했다. 최종 전송 증거는 별도 RETURN_TOOL_PROOF.json/DELIVERY_STATUS.json이며 manifest 자체에 순환 결속하지 않는다.
