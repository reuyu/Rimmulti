# WP — Engine Gate05 R1 bounded repair

Owner A / Antigravity. ID `WP_ENGINE_GATE05_R1`, revision `GATE05-R1`. Master가 채택된 두 contract failure의 기술적 수정을 승인한다. 별도 고유 dispatch ID/envelope4를 사용한다. 실제 제출 전 NOT SENT. 한국어 소통.

## Controlling references / baseline

Project `C:\Users\user\Desktop\RimMulti`. AGENTS.md, docs/MASTER_GOVERNANCE_CURRENT.md, docs/요구사항_명세서.md, docs/MASTER_ARCHITECTURE_CORRECTIONS_MAC-001.md, handoff C corrections/ADR acceptance map을 읽는다. Scope의 accepted ADR006B 및 history/MASTER_DECISION_LOG_MDR-067.md의 MD126..132가 controlling이다.

- `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_E2_20261007.md`
- `C:\Users\user\Desktop\RimMulti\docs\QA_EngineHost_Semantic_Authority_Gate_05.md`와 그 원본 raw evidence
- 기존 source `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs`, EngineHostCensus.cs, WorkerBridge.csproj
- 보존 archive `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json`, SHA `B6AD0A70EA4C13F5040A3BAEE690DBCDDEB8735842FCB482D66352A8FB05F0F1`.19개 역사 파일의 exact copies이며 선택 DLL SHA2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C/MVID12bb9237-1b3e-4b20-89a7-69ad729861e1 및 matching Debug PDB lineage를 보존했다.

Pipeline current candidate는 별도 frozen103이며 original/source/outputs도 변경·재빌드하지 않는다. 기존 QA reports/raw/inventories/Engine archive/historical E1 reports·runner·results·fixtures를 덮어쓰지 않는다. 새 산출물은 `_gate05_r1` 또는 전용새root를 쓴다. 기존 engine source 및 프로젝트 내부 새 candidate/build 영역만 수정한다. 기존 설치 Gate05 PoC DLL/게임 executable/core/ProbeMod는 변경하지 않는다. Native E1은 QA-owned 독립 runtime/mod/profile에서 해당 새 candidate를 실제 로드한다. 실행 방법/환경 제약이 있으면 구현·candidate를 보존하고 native 항목을 BLOCKED/UNTESTED로 보고한다. 이전 설치 DLL의 실행을 새 candidate 실행으로 계산하지 않는다.

## 승인된 수정

1. **G05-S01 발급자/실행 결속.** Operator/simulator가 own immutable sealed result로 task를 만들고 fresh validator를 시작/등록한다. 임의 requester가 expected truth/receipt/validator identity를 지정해 authority를 바꾸는 경로를 제거한다. 정확한 operator-owned process instance/실행 identity/generation과 protected task-bound result channel이 receipt 생성의 근거여야 한다. Public request/query는 capability secret을 노출하지 않으며 debug/caller receipt submission은 authority transition을 하지 못한다. PID inequality/live PID/반환된 nonce equality만 issuer proof로 삼지 않는다. MD126의 local pipe+task capability 등 허용된 방식 중 기술적 구현을 선택하되 public-key 요구나 whole-admin threat model을 새로 만들지 않는다.
2. **G05-S02 실제 loaded-content identity.** 기존 name/label 네 Def-family digest를 충분한 semantic content identity로 대체한다. 실제 build/core·active package/order·loaded assemblies SHA/MVID·DLC/mod content/version·admitted content/patch 및 선언한 supported semantics에 영향을 주는 실제 gameplay Def fields/capabilities를 versioned canonical manifest로 묶는다. Operator 승인 expected와 Worker/validator 독립 actual computation을 비교한다. Missing/unreadable/unsupported authority-relevant component를 빈 hash/UNKNOWN_PROFILE로 silently admit하지 않는다. Cache lifetime/재검증·invalidate를 실제 admission/context/content lifetime에 연결한다. 어떤 자료를 hash했고 실제 loaded 상태와 어떻게 연결되는지 coverage table을 작성한다. Source XML hash나 field count만으로 모든 runtime Def semantics/all-mod coverage를 주장하지 않는다.
3. MD128 closed context equality,MD129 control-plane invalidation, exact stage SHA/fresh native validator,MD131 first-final/atomic replacement/backup/failure-preservation 등 기존 계약을 보존한다. Stage interval O01과 XML helper O02는 관측/검토 한계를 명시하며 실제 fresh saved census를 genuine positive oracle로 사용한다. 새로운 독립 실패로 증명하지 않은 corruption/exploit을 보고하지 않는다. W/L/G/M/target publication/G-Q1/PlayerGlobal owner를 변경하지 않는다.

## E1 / evidence

구현과 읽기 전용 authority-flow review, genuine operator task→exact fresh validator→actual saved-byte census→protected result→receipt→promotion→fresh consumer controls를 분리한다. 실제 process PID/handle/launch executable·SHA/MVID/argv/cwd/시각/exit/result origin와 complete context fields를 기록한다. Candidate/build/PDB/source는 exact matching lineage를 선택하고 Debug/Release/installed 차이를 숨기지 않는다. Declared supported semantic equality와 issuer proof가 각각 있어야 한다.

정상 READ_ONLY, reset/readmission, readiness failure handling, existing-final replacement/backup/실제 QA-owned lock preserve 같은 허용된 defensive regressions만 수행한다. 취약성·권한 우회/forged/replay/content corruption의 공격성 재현을 요구하지 않는다. 제한된 미실행 범위는 정직하게 UNTESTED로 남긴다. 테스트 이름·assertion 수·static method presence를 mandatory category runtime PASS로 바꾸지 않는다. E1은 independent E2/closure를 대체하지 않는다.

Report `C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Semantic_Authority_Gate_05_R1.md`; manifest `C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R1.json`. Fresh E1 tooling/results/raw/process/fixture/evidence inventory는 `C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1`에 보존한다. Manifest에 candidate release revision/SHA/MVID/matching PDB+CodeView/source checksums/build args/dependencies/profile schema+content manifest/supported semantic version/limitations 및 모든 raw evidence hashes를 연결한다. 실제 변경 Engine source/build 목록과 before/after hashes, 역사 archive19와 Pipeline original/frozen103 보존 결과도 제출한다. 기존 installer artifacts는 만지지 않는다.

## 완료와 gate

전달 envelope의 ACK/COMPLETION 계약을 따른다. Complete result의 실제 artifacts를 hash 후 COMPLETION.json을 마지막에 원자적으로 발행한다. BLOCKED/FAILED도 이유와 구현된/미실행 경계를 기록한다. A는 Master governance/closure/automation을 변경하지 않는다. Engine002/006 OPEN,Pipeline full E2 INCONCLUSIVE/G-Q1 OPEN/Foundation HOLD 유지. Master가 raw review/new exact freeze 후 idle Sol에게 별도 fresh E2를 전달한다. C routine WP 없음.
