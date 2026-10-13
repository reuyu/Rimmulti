# WP — Engine Gate05-R2 corrective repair

Owner A / Antigravity. ID `WP_ENGINE_GATE05_R2`, revision `GATE05-R2`, envelope5/new unique dispatch. 기존 승인 Engine issuer/content repair의 기술적 보완. 한국어 소통. 실제 UI submission 전 NOT SENT.

Project `C:\Users\user\Desktop\RimMulti`. Root AGENTS/current governance/SRS/accepted ADR006B/MAC-001/C corrections와 history MD126..132를 유지한다. 새 controlling release는 `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R1_E1_20261008.md`이다. 이전 Gate05 independent E2 FAIL 보고서·Master 리뷰와 R1 원본 report/manifest/harness/raw를 함께 읽는다.

## 승인 범위

1. Public requester가 validator identity/expected truth/result를 제출해 authority를 만들 수 있는 경계를 정리한다. Trusted operator/simulator가 own immutable task에서 **실제 fresh validator process를 launch/등록**하고 정확한 process instance/실행 binary·generation과 protected result channel을 소유해야 한다. Public request는 요청/상태 조회로 한정한다. 기존 caller process registration이나 data submit 경로는 authority transition을 하지 못하게 한다. Secret redaction뿐 아니라 보호된 channel origin과 lifetime/consumption을 구현한다. 파일 경로 명명이나 문자열 equality를 issuer proof로 부르지 않는다. MD128의 모든 closed context 항목과 MD129 readiness revocation을 보존한다. Public-key 도입/whole-admin attacker model/제품 인증정책을 새로 정하지 않는다.
2. MD130에 맞춰 실제 admitted loaded-content identity의 coverage를 작성하고 lossless/versioned canonical encoding을 구현한다. Authoritative numeric 값은 F1/F2/locale-dependent display strings로 줄이지 않는다. Field names/types/null-vs-missing/collection identity와 semantic order를 구분한다. 범위에 필요한 content/patch/DLC/Def fields를 report/source와 일치시키고, 누락/읽기 실패를 빈 hash/skip/count-only로 성공 처리하지 않는다. Runtime cache lifetime/revalidation과 Worker/validator 독립 actual profile computation을 연결한다. Schema string 변경을 accepted ADR amendment로 주장하지 않는다.
3. Fixture/mocked checks와 실제 native genuine controls를 분리한다. 이전30 raw checkpoints와11 completion 불일치를 새 보고서에서 정확히 정리한다. A는 CLOSED를 선언하지 않는다. 실제 authority-flow/loaded-content/native saved census를 증명하지 않는 source grep/reflection presence/mock profile 결과를 기능 PASS로 포장하지 않는다. Forged/replay/권한 우회/취약성 reproduction은 요청하지 않는다. Defensive source/contract review 및 genuine normal flows만 수행하고 미실행 필수 경계를 명시한다.

## Native runtime 분리

현재 설치된 Gate05 DLL/게임 core/ProbeMod는 그대로 유지한다. 기존 licensed RimWorld의 read-only 원본을 사용해 **프로젝트 내부 새 독립 runtime/mod/data/profile copy**에서 새 candidate를 실행할 수 있는지 확인한다. 게임 실행 파일과 대응 data/managed/native/content 경로를 실제 관찰하고 새 runtime이 설치 원본 Mods를 다시 사용하는지 확인한다. Native controls는 해당 복사본에 새 candidate를 두고 loaded path/SHA/MVID, argv/cwd/PID/launch/result/current context 및 실제 save load/census를 결속한다. Source/base game 원본·Steam/Workshop 설정·사용자 실제 saves는 변경하지 않는다. 생성한 owned process만 관리한다. Native isolation이 성립하지 않으면 그 증거/오류를 BLOCKED/UNTESTED로 제출하고 설치 원본을 바꾸지 않는다. Unity 경로 설명은 isolation 후보의 근거일 뿐 RimWorld 동작 보장이 아니다.

기존 authority state lifetime, READ_ONLY/reset/readmission, 실제 atomic replacement/backup/failure preservation 계약을 보존한다. Owner/PlayerGlobal/Quest/Weather 등의 C 미정 결정을 새로 freeze하지 않는다. G-Q1 및 W/L/G/M, target publication, Server final authority 유지.

## 보존 / 새 산출물

- 역사 Engine19: `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json`.
- 거절 R1 freeze147: `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780\MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json`, SHA `1196930576154C11351387B10EAB017C51D6BB027A1686317AB8DF8DAB73022E`.
- Pipeline original+frozen103 및 이전 QA297/S1312/S2238/raw를 보존한다. R1 원본 report/harness/results/completion도 덮어쓰지 않는다. Engine source/현재 build만 Master task의 allowed paths 안에서 수정하고 새 산출물은 전용 root를 사용한다.

새 root `C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R2`, report `C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Semantic_Authority_Gate_05_R2.md`, manifest `C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R2.json`. 하나의 selected candidate lineage를 명시하고 모든 native/tooling 실행 전에 SHA/MVID/source/matching PDB+CodeView/generated source/build args/dependencies/profile manifest/supported semantic version을 snapshot한다. Debug/Release alternate는 별도 표시한다. Actual source/report/runtime fields를 일치시키고 모든 count의 실제 실행 근거를 보존한다.

Envelope의 고유 ACK/COMPLETION 계약을 따른다. Terminal COMPLETION은 모든 실제 artifact hashes와 정확한 E1 partial/full scope를 계산한 뒤 마지막에 발행한다. 필요한 genuine native proof가 미실행이면 full E1 gate PASS나 closure를 선언하지 않는다. Partial 구현도 completed/blocked 구분과 reason/limitations/미실행 목록을 명확히 남긴다. Master가 새 raw/candidate를 검토·freeze 후 idle Sol에게 별도 fresh E2를 release한다. Engine002/006 OPEN,Pipeline full E2 INCONCLUSIVE/Foundation HOLD/G-Q1 OPEN;A는 governance/automation을 변경하지 않는다.
