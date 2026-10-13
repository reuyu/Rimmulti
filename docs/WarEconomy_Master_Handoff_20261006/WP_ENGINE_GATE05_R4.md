# WP_ENGINE_GATE05_R4 — GATE05-R4

Owner A / Antigravity / envelope7. 한국어로 소통·보고한다. R3 independent QA 후 같은 Engine repair 범위의 후속 수정이다. 실제 전달 상태는 고유 task/journal을 따른다. 기존 R3를 덮어쓰지 않는다.

Root `C:\Users\user\Desktop\RimMulti`. AGENTS, canonical SRS `docs\요구사항_명세서.md`, 현재 governance, controlling C corrections/history, accepted MD125~132/ADR006B를 읽는다. Controlling release는 `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R3_INDEPENDENT_QA_S1_20261008.md`다. R3 Master E1 review와 Sol report/INDEPENDENT_FINDINGS/CORRECTION_PRIORITIES를 같이 읽는다. R3는 REVISION_REQUIRED/E2_RUNTIME_NOT_RELEASED이며32 fixture PASS가 full native PASS가 아니다.

## 먼저 읽고 순서대로 수행

현재9 allowed Engine source/build paths만 변경한다. 새 task root, `scratch\EngineGate05R4`, R4 report/manifest는 새 산출물이다. Master governance/예약/QA 원문/과거 보고서 및 archive/R1/R2/R3frozen/Pipeline은 수정하지 않는다. 다른 WP 처리 중이면 중복 시작하지 말고 ACK로 알려준다. 첫 ACK와 WORK_LOG를 고유 task에 작성한다.

다음 단계마다 실제 수정·확인·남은 제약을 기록한다. 다음 단계의 근거가 없는데 모든 결함을 해결했다고 선언하지 않는다. 정상 native workload를 얻지 못하면 정확한 BLOCKED/UNTESTED로 끝내도 된다. Fixture를 새 이름으로 바꾸거나 expected field를 주입해 전체 gate PASS를 만드는 것은 완료 기준이 아니다.

### 1. 정상 operation/validator 역할 회귀를 먼저 수정

R3 STEP/SEAL은 READ_ONLY grant를 거부하고 STAGE가 READ_ONLY task를 만들지만 Complete는 SIMULATION grant와 같은 mode를 요구한다. Proposal operation mode와 validator execution role을 각각 명시하고 approved authority/grant→seal→immutable task→validator result→internal receipt→current state에 역할별로 결속한다. 원래 승인된 SIMULATION authority/grant를 READ_ONLY로 바꾸거나 비교를 삭제해서 통과시키지 않는다. READ_ONLY validator는 시뮬레이션 write authority가 아니다. 기존 unsupported field/version은 성공으로 처리하지 않는다.

정상 SIMULATION admission→STEP→SEAL→STAGE→fresh READ_ONLY validation→Complete 흐름을 대상으로 한다. Component normal fixture를 사용하면 fixture라고 명시하고 native와 분리한다. 부정 payload/위조/재전송/권한 우회 재현·새 exploit 절차를 만들거나 이전 adverse runner를 재실행하지 않는다.

### 2. admitted operator workload와 실제 결과 origin

요청자는 validation을 요청할 수 있지만 validator 실행 파일/config/expected sealed authority를 지명하지 못한다. Operator가 승인된 고정 executable의 path/SHA/해당 assembly MVID, 실제 selected R4 candidate/core/mod/profile/config를 선택하여 같은 immutable task와 fresh process instance를 소유한다. 전달된 exe label/nonce, 임의 process binding, 내부에서 nonce를 대신 넣는 overload를 trusted origin 증명으로 인정하지 않는다. 프로세스 생성/시작 시각의 실제 확인이 실패했는데 현재 시각을 넣어 identity 증명을 성공으로 만들지 않는다.

Operator-owned launch→actual exact staged bytes load→independently computed actual profile/census→validator가 생성한 result→operator channel 관측/소비→internal receipt→approved promotion을 이어야 한다. Runner가 만든 result/sleep/echo child는 native proof가 아니다. File channel은 equivalent operator-controlled mechanism으로 사용할 수 있고 정상 result-after-exit도 허용할 수 있다. 구체 ownership/context/instance/consume/cleanup/lifecycle 계약을 구현·기록한다. Receipt 공개 필드에 secret을 추가 복사하는 것을 새 요구로 만들지 않는다. 승인 채널이 없는 경우 임의 파일 fallback은 실패로 처리한다.

### 3. complete supported context와 실패·복구

MD128의16 logical dimensions를 proposal operation과 validator role 의미에 맞게 표로 정리하고 모든 supported presence/equality/current authority·grant·generation·seal·epoch·profile·source/store/target/mode/version을 검사한다. Result에서 task context를 운반하는 것과 validator/operator가 그 context를 검증하는 것을 구분한다. 타깃 index clamp로 잘못된 대상을 대신 선택하지 않는다. 실제 census의 index/tile/parent/faction context와 manifest 검사를 보존하면서 승인된 stable target↔loaded mapping을 입증한다. G-Q1/PlayerGlobal/global schema를 새로 확정하지 않는다.

MD129는 역할별 failure/cancel/parse/load/complete/consume/cleanup→relevant capability 철회→명시 clean reset/re-admission 표를 실제 handler/wrapper와 대조한다. 별도 READ_ONLY process의 오류를 어떤 operator 상태와 연결하는지 규정한다. 일반 query 오류 전역 revoke를 새 요구로 만들지 않는다. 기존 Promote current authority/grant 존재/generation/epoch/profile/live recensus/staged SHA 및 MD131 same-volume atomic replacement fail-closed를 보존한다. Complete 공백을 실제 promotion exploit로 주장하지 않는다.

### 4. 지원 material content의 typed/versioned encoding

현재 delimiter signature에 schema/capability flag만 바꾸는 것은 typed lossless encoding이 아니다. 지원 field/type/null/missing/empty/collection identity 및 의미 있는 order를 분명하게 encoding한다. 순서 정규화가 의미를 보존하는 범위와 ordered list를 구분한다. 기존 R-format/mod assembly missing-file guard/material cost fields는 유지한다. 실제 core/mod assembly SHA/MVID/order/DLC/지원 material Def/patch/settings/capabilities를 충분히 결속한다. 누락을 skip/empty hash/count-only 성공으로 처리하지 않는다. 모든 Def serialization/모든 sort 금지/모든-mod 호환을 새 요구로 만들지 않는다.

Worker와 fresh validator가 actual admitted loaded profile을 각각 계산·검증해야 한다. 기존 cache invalidation은 존재하므로 없는 것으로 서술하지 않는다. Cache의 admitted content 불변 lifetime/key/epoch와 admission/load/reset/fresh validation 재계산을 source 및 정상 evidence로 결속한다. v3 상수 equality/Contains/cache bool 하나로 lossless full PASS를 선언하지 않는다. 새 codec/schema/version은 이 PoC supported content 계약이며 canonical PlayerGlobal schema 결정이 아니다.

### 5. 실제 project-isolated 정상 native 관측

새 `C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R4\RuntimeCopy`의 licensed runtime/game data/native/Managed/mod copy를 준비하고 source provenance 및 copy bytes를 기록한다. **원래 Steam executable에서 실행하지 않는다.** Steam/Workshop 설정·installed mod/core/ProbeMod·실제 userdata/save는 변경하지 않는다. 원본 asset은 읽기/승인된 copy source로만 사용하며 보호/DRM를 우회하지 않는다. 참조 MP MIT launcher는 참고 가능하나 그 모드의 검증을 우리 PASS로 승계하지 않는다.

최소 먼저 실제 isolated executable/cwd/argv/userdata/profile/mod/task/stage/log paths가 일치함을 확인한다. 정상 startup부터 실제 loaded new selected candidate SHA/MVID,core/mod identity,actual supported content profile,task/staged bytes/native census/result/receipt를 같은 run에 결속한다. 자신이 만든 정확한 handle/PID만 종료·관리하고 numeric exit 및 loader log를 남긴다. RuntimeCopy label/파일 존재/PID/5초 실행으로 정상 loader·semantic PASS를 선언하지 않는다. CLI 옵션은 실제 supported runtime/launcher에 맞춰 확정하고 보고서와 raw가 일치하게 한다.

실행 불가/부분 실행이면 actual error/raw와 관측된 단계/미관측 단계만 기록한다. 원인 없으면 UNKNOWN, 미실행이면 UNTESTED다. 이유 없이 DRM/Steam/headless 불가능을 단정하지 않는다. 정상 전체 flow가 없으면 native gate PASS를 선언하지 않는다.

### 6. actual-byte packaging / 완료 계약

새 report `C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Semantic_Authority_Gate_05_R4.md`, release manifest `C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R4.json`. Harness/normal-runner/raw/logs는 새 scratch\EngineGate05R4에만 쓴다. 기존 R3 task/COMPLETION/133 freeze 및 QA report/evidence를 수정하지 않는다. Installed old2D64… vs observedBB3B…는 UNKNOWN OPEN incident이며 actor/cause 추정·restore/hash 정상화 금지다.

실행 **전** selected/alternate SHA/MVID/matching PDB+CodeView/source/generated/build args/dependency/tooling/content/schema/config와 run ID를 immutable CANDIDATE_PRE_RUN_MANIFEST.json으로 결속한다. Hash를 실제 계산하고 실행 후 해당 identity와 pre-run snapshot을 확인한다. 이후 candidate 변경/재빌드가 필요하면 새 run/snapshot으로 기록하고 이전 evidence를 재사용하지 않는다. 사후 snapshot을 실행 전 증거로 소급하지 않는다. 실제 보호 대상의 ENGINE_FREEZE_BEFORE.json/ENGINE_FREEZE_AFTER.json도 남긴다.

보고서 표는 최종 actual bytes/manifest에서 생성한다. SHA/size/argv/counts/provenance가 서로 같아야 한다. Metadata/normal component fixture/OS child/native workload/UNTESTED를 구분한다. Native/full required gate와 부분 정상 evidence를 분리한다.

Terminal COMPLETION.json은 고유 task에 마지막으로 발행한다. **schema_version1,producer A,report_kind E1,exact dispatch_id/wp_id WP_ENGINE_GATE05_R4/wp_revision GATE05-R4,unique result_id,status COMPLETED|BLOCKED|FAILED,completed_at timezone,summary,e1_verdict,limitations,artifacts**. task_id/work_package_id/completed_at_utc/verdict aliases만으로 대체하지 않는다. entry는 role/프로젝트 내부 **절대**path/sha256/size다. COMPLETED 필수 roles implementation_report,release_manifest,harness,results,raw_evidence,candidate_binary,source,pdb,engine_freeze_before,engine_freeze_after와 추가 source2개/alternate/profile/config/provenance/dependency/native log를 결속한다. BLOCKED/FAILED는 reason·partial artifacts·observed outcome·미관측 한계를 명시한다. Native 정상 flow가 없으면 IMPLEMENTATION_PARTIAL/NATIVE_UNTESTED를 쓰고 full PASS_WITH_LIMITS로 전면 해소를 선언하지 않는다.

## 보존·최종 판정

Task preservation_policy exact9 allowed paths가 mutable repair 대상이다. Engine archive19/R1frozen147/R2frozen107/R3frozen133/Pipeline original+frozen206/기존 QA 및 prep17/독립R3QA17은 보호한다. Mutable current source/bin을 이전 lineage로 주장하지 않는다. A는 Master governance/예약/closure를 만들지 않는다. 새 후보 Master review/freeze/admission와 fresh independent Sol E2 전 Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. E1/normal fixture PASS는 E2를 대체하지 않는다.
