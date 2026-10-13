# Engine Gate05-R5 — codec/content만 구현

WP `WP_ENGINE_GATE05_R5_CODEC`,revision `GATE05-R5-CODEC`,delivery envelope8. Master가 승인한 좁은 개발 수정이다. 고유 dispatch와 exact instruction/release/reference paths는 task INSTRUCTIONS.md 및 MASTER_A_TASKS.json을 따른다. 같은 Engine source writer는 A 한 명이다. R4 terminal과 Sol 독립 결과는 수정 필요/runtime UNTESTED이며, R5만으로 전체 Gate05나 Engine002/006을 완료하지 않는다.

## Recovery / controlling scope

Actual root C:\Users\user\Desktop\RimMulti. Root AGENTS/current governance/canonical docs\요구사항_명세서.md와 docs\WarEconomy_Master_Handoff_20261006\00_START_HERE.md/MASTER_HANDOFF.md/C corrections/history/accepted ADR006B/MD125~132를 읽는다. Dedicated Server 최종 Domain Authority/WLGM/LocalClock/B2 target publication/C correction/G-Q1 OPEN을 유지한다.

Master controlling review는 MASTER_REVIEW_ENGINE_GATE05_R4_E1_20261008.md 및 MASTER_REVIEW_ENGINE_GATE05_R4_INDEPENDENT_QA_S1_20261008.md. QA 원문 docs\QA_EngineHost_Gate05_R4_Independent_Review_S1_20261008.md와 QA-Tactical-Engine\GATE05-R4-INDEPENDENT-REVIEW-S1-20261008\CORRECTION_PRIORITIES.md도 읽는다. Complete current Authority/Grant SIMULATION 존재와 task/result READ_ONLY 개선은 보존한다. Null-current acceptance라는 과장/모든 Def field·모든 sort 금지 요구는 채택하지 않는다.

R4 immutable232 manifest SHA D047D0095CEDDA8E5F0FB6871EA4C24AF0866CA569514049FFAD7E91B7C1460C. Selected Debug4F5663.../MVID ed98e6f9-aa63-47ee-ae21-84f59465d2bb/PDB CC796E...,alternate7532.../MVID d602525d-4248-442a-8f51-77e22f8484bf/PDB53E33...는 역사 baseline이며 새 build 후 identity를 승계하지 않는다. Task baseline 파일에 전체 SHA/size/source를 결속한다.

## 구현 결과

1. ContentProfileProvider의 supported loaded-content manifest를 **typed/versioned canonical records**로 구현한다. 기존8 Def family에서 이미 지원한 material field coverage를 최소 baseline으로 삼아 field명/type/requiredness/null-missing-empty 의미/collection key/order policy/available-unsupported-unknown disposition 표를 먼저 만든다. 구현한 범위와 미지원 범위를 explicit하게 남긴다. 현재 supported cost/material field와 actual core/mod assembly SHA/MVID/size,active mod order를 줄이지 않는다.
2. Mod/DLC/Def/loaded assembly records의 delimiter/sentinel 조합 대신 실제 typed records를 canonical serialize한다. Canonical outer JSON 안에 기존 delimiter string digest만 넣고 lossless라고 선언하지 않는다. 정상 Unicode/구두점/string 값은 serializer escaping으로 보존하고 null/empty/missing은 지원 계약에 맞게 구분한다. Ordered list는 order를 유지하고 set/mapping은 명시한 stable key로 canonicalize한다. 중복 identity/unsupported required input은 성공 프로필로 조용히 축약하지 않는다.
3. Supported patch/settings/DLC content identity의 충분한 자료를 실제 admitted runtime API/content bytes에서 결속하거나 명시 unsupported/unavailable로 판정한다. Patch count 또는 schema flag만으로 authority-relevant drift coverage를 선언하지 않는다. DLC 조회 예외를 빈 성공 collection으로 무시하지 않는다. Unknown 필수 material을 가진 프로필은 trusted admission에 사용할 수 없게 현재 provider 실패 경로와 연결한다. 모든 Def/property나 전체 mod compatibility를 이번 PoC에서 구현하라는 요구는 아니다.
4. Existing InvalidateCache/actual content admission lifetime을 문서화하고 provider의 cached bytes/digest가 어떤 immutable admitted content snapshot에 귀속되는지 명시한다. Worker/validator는 같은 supported schema에 따라 자신의 loaded content를 독립 계산한다. Operator bootstrap/lifecycle handler 수정이 필요하면 이 WP 범위를 넓혀 고치지 말고 remaining operator work로 기록한다. Cache helper만으로 native lifecycle PASS를 주장하지 않는다.
5. 정상 codec controls는 **실제 production codec 구현**을 직접 사용한다: typed 정상 대표 records의 canonical bytes/decoded semantic values,digest,동일입력 재계산,ordered collections 의미,공백·Unicode·null/empty·숫자 정밀도,두 정상 admitted content revision의 schema에 맞는 표현. 모든 production provider를 mock profile/census/hash로 바꾸는 예전 harness를 사용하지 않는다. Genuine loaded runtime를 사용하지 않았으면 단위 codec evidence로 표시한다. Test 이름/상수/assertion 개수만으로 runtime PASS를 선언하지 않는다. Forged/replay/tamper/bypass/adverse 보안 fixture·공격 절차·기존 Gate05R1~R4 harness 재실행은 만들거나 수행하지 않는다.

## 정확한 변경/실행 경계

Production source 변경은 scratch\WorkerBridgeMod\Source\EngineHostCensus.cs **ContentProfileProvider 및 그 파일의 content codec DTO/helper에만** 허용한다. Census semantic 구현/Validator DTO 및 WorkerBridge.cs/operator/Promote/MD129/native launcher는 이 WP에서 바꾸지 않는다. WorkerBridge.cs와 csproj는 Master fixed-current hashes로 보존한다. 필요한 build의 bin/obj generated outputs와 프로젝트 내부 Debug/Release DLL/PDB 및 1.6\Assemblies 동반 DLL/PDB 갱신만 허용한다. 새 normal codec runner/docs는 scratch\EngineGate05R5Codec 및 고유 task 안에 쓴다. Source 구조상 별도 production 파일/csproj 변경이 꼭 필요하면 근거를 task 파일로 남겨 Master scope correction을 기다린다.

Steam 설치/core/ProbeMod/원래 UserData/saves, Pipeline206, archive19, R1/2/3frozen387,R4frozen232, QA1222 및 manifests/terminal 증거는 변경하지 않는다. Known installed BB3B... 대 old2D64... incident OPEN/actor UNKNOWN을 restore/normalization으로 해결하지 않는다. 게임/native runtime 실행·전체 Gate05 handler/adverse harness 실행·release/closure는 승인하지 않는다. 이번 R5는 codec E1 근거와 새 후보 packaging이다.

## 산출물 / packaging

docs\POC_EngineHost_Content_Codec_Gate05_R5.md,docs\RELEASE_MANIFEST_ENGINE_GATE05_R5_CODEC.json 및 scratch\EngineGate05R5Codec에 supported schema/coverage table,captured normal input/canonical bytes/digest/decoded semantic evidence,normal runner source/dependencies/build/run raw/log/results,ENGINE_FREEZE_BEFORE/AFTER를 쓴다. Before/after는 actual bytes에서 hash와 size를 생성한다.

**마지막 build 뒤, 정상 codec run 전** 정확한 selected Debug/alternate Release DLL SHA/size/MVID,matching PDB/CodeView/document checksum/source/generated/dependency/tooling/content/config identity와 unique run_id를 snapshot한다. Run 뒤 모두 다시 대조한다. Build/source/profile가 바뀌면 이전 pre-run을 재사용하지 말고 새 run/snapshot을 만든다. Runtime-loaded candidate proof가 없으면 NOT_OBSERVED라고 적는다. 사후 freeze를 실행 전 provenance로 소급하지 않는다.

Task ACK.json과 A_WORK_LOG를 실제 진행으로 기록한다. COMPLETION.json은 schema_version1,producer A,report_kind E1,exact dispatch/wp/revision,unique result_id,timezone 완료 시각,status,summary,e1_verdict,limitations **string/list**,artifacts array(role/absolute path/actual SHA/size)를 포함한다. Required roles implementation_report/release_manifest/harness/results/raw_evidence/candidate_binary/source/pdb/engine_freeze_before/engine_freeze_after 및 codec contract/normal evidence/pre-run manifest를 결속한다. BLOCKED/FAILED면 구체 이유/불확실/해제 조건을 적는다. 정상 codec 단위 E1은 fresh native E2/closure를 대체하지 않는다.

Sol은 별도 exact frozen candidate 독립 검토/허용된 normal codec QA를 수행한다. Final admitted operator/native candidate는 후속 Master WP/freeze/fresh runtime E2가 필요하다. Engine002006/Pipeline007/current schema7/G-Q1 OPEN,Foundation HOLD. C routine WP 없음.
