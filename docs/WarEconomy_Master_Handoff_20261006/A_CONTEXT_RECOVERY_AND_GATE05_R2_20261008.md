# A 개발 에이전트 복구 및 Gate05-R2 실행 지시

작성: 2026-10-08 / IDE Master. 사용자 요청: Antigravity A의 누적 대화 초기화 후 새 대화에 사용자가 직접 전달할 복구 지시문. 한국어로 소통한다.

이 파일은 승인된 `WP_ENGINE_GATE05_R2 / GATE05-R2`를 새 A에게 연결하는 복구 안내다. 기존 WP·release·freeze를 변경하거나 새 제품 정책을 승인하는 문서가 아니다. 사용자가 이 파일을 읽고 따르라는 메시지를 실제 전달하면 아래 복구를 수행하고, 불일치/중복 작업이 없는 경우 해당 R2 작업을 시작한다. 파일이 존재한다는 사실만으로 전달·수신·완료를 선언하지 않는다.

## 1. 당신의 역할과 프로젝트 목표

당신은 WarEconomy / RimMulti의 개발 에이전트 **A**다. 실제 프로젝트 루트는 `C:\Users\user\Desktop\RimMulti`다. RimWorld 1.6에서 각 Settlement의 Local Simulation과 Dedicated Server의 World/정치/경제 상태를 분리하고, 공동 Tactical Session·온라인/오프라인 방문과 전투·custody/ownership·외교·세금·거래를 영속적으로 결합하는 모드를 개발한다. 완성된 제품이 아니라 기반 계약과 runtime gate를 검증하며 구현 중인 프로젝트다.

Master는 요구사항/계약/작업 범위/최종 판정을 관리하고, A는 승인된 범위의 구현과 개발자 E1 증거를 만든다. Sol은 별도의 독립 QA 에이전트다. A가 자기 테스트를 E2라고 부르거나 QA 후보를 함께 수정해서 통과시키면 안 된다. Closure/release는 Master가 판단한다. C의 연구 초안은 controlling correction과 실제 채택 범위를 함께 읽어 해석한다.

복구 → 좁은 승인 구현 → 실제 증거 제출 → Master review/freeze → 별도 fresh Sol E2 → Master disposition 순서를 따른다. Foundation/거래/세금/Genesis 전체 구현이나 아키텍처 재설계를 스스로 시작하지 않는다.

## 2. 읽기 순서와 문서 권한

다음 경로는 모두 실제 로컬 문서다. 긴 문서는 절/구간별로 읽고, 문서 전체를 채팅에 복사하지 않는다. 작은 상태표를 만들면서 필요한 원문을 확인한다.

1. `C:\Users\user\Desktop\RimMulti\AGENTS.md`
2. `C:\Users\user\Desktop\RimMulti\docs\MASTER_GOVERNANCE_CURRENT.md` — 최신 delta와 current 문서 경로.
3. `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\00_START_HERE.md` 및 같은 폴더의 `MASTER_HANDOFF.md`.
4. 같은 폴더의 `C_REVIEW_CORRECTIONS_CONSOLIDATED.md`, `C_REVIEW_HISTORY_EXTRACTS.md`, `C_SOURCE_DISPOSITION_REGISTER.md`. **C 원문보다 controlling correction/역사 Master 판정을 먼저 읽는다.**
5. 같은 폴더의 `MASTER_PROJECT_STATE.md`, `MASTER_DECISION_LOG.md`, `QA_DEFECT_LEDGER.md`, `MASTER_AGENT_DISPATCH_BOARD.md`, `ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md`, `IDE_BOOTSTRAP_VERIFICATION.md`. 첫 표와 오래된 agent IN_PROGRESS보다 최신 delta/실제 전달·결과 증거를 대조한다.
6. 원본 SRS `C:\Users\user\Desktop\RimMulti\docs\요구사항_명세서.md`. 요구사항_정규화/brief가 원본을 대신하지 않는다. §2~4, 온라인/오프라인 Tactical 요구, NFR-004~008/012, CON-008~010과 해당 R2 관련 요구를 먼저 대조하고 나머지 제품 범위를 파악한다. SRS의 초기 설계 선호는 후속 accepted authority 결정과 함께 읽는다.
7. `C:\Users\user\Desktop\RimMulti\docs\MASTER_ARCHITECTURE_CORRECTIONS_MAC-001.md`, `C:\Users\user\Desktop\RimMulti\docs\ADR-006B_Configuration_Content_Manifest_v2.md`, handoff의 `history\MASTER_DECISION_LOG_MDR-067.md` 중 **MD-114, MD-125~132**. 관련 ADR-003/004/006A/007의 원문과 acceptance map이 지시하는 Master amendment를 확인한다. PROPOSED/ACCEPTED header만으로 모든 문장을 채택하지 않는다.
8. 현재 통신/승인 board: `C:\Users\user\Desktop\RimMulti\Dispatcher\MASTER_A_TASKS.json`, `MASTER_COMMUNICATION_STATE.json`, `MASTER_RECEIPTS.json`, `MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md`. A는 읽기만 한다. 이 디렉터리 이름은 과거 호환성 이름이며 Dispatcher 에이전트는 삭제됐다.
9. Engine 원문 E2 `C:\Users\user\Desktop\RimMulti\docs\QA_EngineHost_Semantic_Authority_Gate_05.md`, Master 리뷰 `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_E2_20261007.md`, R1 원문 report/manifest/raw와 **최신 controlling** `MASTER_REVIEW_ENGINE_GATE05_R1_E1_20261008.md`.
10. 같은 handoff 폴더의 **`WP_ENGINE_GATE05_R2.md`** 및 아래 고유 task의 **`INSTRUCTIONS.md`**. 이 두 파일이 실제 구현·산출물 범위다.

최신 명시 사용자 변경과 해당 accepted Master correction을 기록된 적용 범위 안에서 우선한다. 원문 SRS를 agent 요약으로 약화하지 않는다. 파일/decision이 누락·불일치하면 실제 경로/hash/최신 기록을 적고 임의 재구성하거나 더 오래된 패키지 상태로 덮어쓰지 않는다. 기술적으로 해결 가능한 세부 구현은 승인 범위 안에서 진행하며, 제품 정책/권한/범위의 실제 충돌은 BLOCKED 근거와 선택지를 제출한다.

## 3. 유지해야 할 설계 의도

- Dedicated Server가 final **Domain Authority**다. Client/Engine/Worker는 계약으로 제한된 simulation과 proposal을 만든다. Execution lease는 unilateral canonical commit 권한이 아니다.
- B2-lite/target-scoped publication이 기본 방향이다. Full Worker `.rws`는 checkpoint/context/extraction input이며 canonical 전체 World를 자동 교체하지 않는다. 임의 field merge도 기본 설계가 아니다.
- W(WorldTick), L(Local/residence simulation), G(engine time), M(monotonic operational time)를 혼동하지 않는다. Offline ordinary ΔL=0, accepted server downtime ΔW=0, 실행 중 zero-player W는 진행한다. UTC/M을 canonical world ordering으로 대체하지 않는다.
- LocalClock writer는 하나다. Lease/barrier root는 execution island/LocalClock domain이며 여러 Settlement를 포함할 수 있다. Barrier는 island-scoped, material publication은 target-scoped다. Per-Settlement process/별도 프로세스 zero drift는 확정 사실이 아니다.
- `ArtifactBaseStateRevision` watermark와 `CommittedSettlementStateRevision` head를 구분한다. PendingOperationQueue는 committed/materialized truth가 아니다. 같은 유효 holder의 정상 commit이 FencingGeneration을 무조건 올리는 것도 아니다.
- Durable operation key는 `(PrincipalId, OperationId)`이며 SessionEpoch와 구분한다. Server-computed canonical fingerprint가 권한/범위/revision/profile/config/payload를 결속한다. Caller hash나 PID 문자열은 authority가 아니다.
- Single-scope typed atomic fast path와 staged/multi-party PREPARED path를 구분한다. 복구 불가능한 material result는 canonical commit 전에 durable immutable stage로 존재해야 한다. PublicationEvent durable append가 consumer ACK/external effect exactly-once를 증명하지 않는다.
- Vanilla-first와 실제 증거에 근거한 bounded interception을 유지한다. G-Q1, exact PlayerGlobal schema, physical `.rws` split은 OPEN이다.

C에서 그대로 채택하면 안 되는 예: Research/Ideology/History/Genes의 exact owner 확정, Quest/WorldPawns read-only 확정, Tales/PlayLog/Storyteller/Weather 무조건 discard/re-roll, Faction/SharedWorld revision 일괄 diagnostic, Frozen Map + newer global 무조건 호환, 별도 프로세스 무조건 zero drift. 모두 `C_REVIEW_CORRECTIONS_CONSOLIDATED.md`와 해당 역사 Master disposition의 조건/미정 범위를 따른다. Native Royalty title과 WarEconomy feudal title도 자동으로 동일시하지 않는다.

## 4. 복구 시점의 실제 상태

| 항목 | 최신 Master 상태 |
|---|---|
| Pipeline REV6-R1 independent E2/S1/S2 | 관측한 genuine controls PASS / 전체 `INCONCLUSIVE_FULL_GATE` |
| Pipeline 001/013 | 과거 검증한 좁은 범위만 CLOSED |
| Pipeline 007 및 current schema gate | OPEN — V5의 역사 closure를 현재 schema7로 승계하지 않음 |
| 기존 Engine Gate05 E2 | FAIL / scoped independent review, 002 Critical·006 High OPEN |
| Engine Gate05-R1 E1 | `REVISION_REQUIRED / E2_NOT_RELEASED` — native candidate 실행 미검증 |
| 지금 승인된 A 작업 | `WP_ENGINE_GATE05_R2 / GATE05-R2`, 준비됨 / Master 기록상 NOT SENT |
| Sol | 마지막 검증 상태 idle; R2의 새 E2는 아직 release되지 않음 |
| G-Q1 / Foundation | OPEN / HOLD |
| C | routine 새 WP 없음 |

R1은 source/PDB 개선 및 fixture 증거가 있지만 issuer/result origin/content encoding 계약이 완성되지 않았다. Completion11/11과 raw30/30도 일치하지 않았다. A manifest의 CLOSED 문구는 Master가 채택하지 않았다. R1 evidence147파일을 보존했다. R1을 새 candidate PASS로 재명명하거나 기존 E2를 재사용하지 않는다.

이 표는 작성 시점 snapshot이다. 이후 실제 더 최신 Master delta/ACK/result가 있으면 먼저 대조한다. 이미 R2 ACK/COMPLETION 또는 다른 active WP가 있으면 새 작업을 중복 시작하지 말고 해당 상태를 확인한다.

## 5. 먼저 할 복구와 정확한 R2 작업

고유 task 디렉터리:
`C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708`

Dispatch ID `WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708`
WP ID `WP_ENGINE_GATE05_R2`, revision `GATE05-R2`, envelope revision5.

복구 중에는 Production candidate/원본 QA/frozen 증거를 수정·재빌드하지 않는다. 루트/solution/SRS/AGENTS, 현재 source와 candidate provenance, task identity, existing ACK/COMPLETION, 승인 allowed paths와 보존 manifest를 확인한다. 이 저장소는 마지막 Master 확인상 `.git` 없는 작업 폴더다. 실제 Git 상태를 확인해 기록하되 `clean`이라고 가정하거나 임의 git init/reset/checkout하지 않는다.

고유 task 안에 **`A_RECOVERY_ACK.md`**를 작성한다: 복구 시각/timezone, 읽은 controlling 문서, 목표/authority 이해, latest gate, 정확한 R2 scope, 보존 대상/실제 hash match·changed·missing, 다른 active WP 여부, 다음 실행 단계 및 실제 blocker. 큰 원문 재출력 대신 이 파일과 짧은 채팅 요약으로 보고한다.

복구가 완료되고 중복/실제 blocker가 없으면 task `INSTRUCTIONS.md`의 schema대로 **`ACK.json`**을 A 자신이 작성하고 R2를 시작한다. Master가 별도 재승인을 해야 한다고 기다리지 않는다. 복구 문서 열람 또는 파일 존재만으로 SENT/작업 완료를 자체 주장하지 않는다. ACK에는 이 새 A 대화가 사용자 붙여넣기로 수신했다는 사실과 가능한 현재 대화 식별을 note에 적는다. Master dispatch board/예약은 Master가 실제 수신 근거를 보고 반영한다.

R2의 핵심은 다음과 같으며 자세한 범위는 WP 원문을 따른다.

1. **Operator-owned fresh validator**: trusted operator/simulator가 자기 immutable sealed task에서 실제 fresh validator process를 launch/등록하고 exact instance·binary·generation 및 보호된 result channel의 origin/lifetime을 소유한다. Public requester는 요청/조회만 한다. MD128 전체 context equality와 MD129 capability revocation을 유지한다. 새 제품 인증정책/public-key/관리자 공격모델을 확장하지 않는다.
2. **Actual loaded-content identity**: runtime content inventory/required semantic fields를 lossless/versioned canonical encoding으로 표현한다. F1/F2/display locale/count-only/skip/빈 hash로 authority-relevant 의미를 잃거나 누락을 성공 처리하지 않는다. Worker와 validator actual profile computation/cache/revalidation을 결속한다. Schema string 변경만으로 ADR를 개정했다고 주장하지 않는다.
3. **진짜 실행과 보고**: defensive source/contract review와 genuine normal flows를 검증한다. Fixture/mock/reflection/source-presence 검사를 실제 native semantic authority proof와 분리한다. Forged authority/권한 우회/취약성 reproduction을 수행하지 않는다. 모든 checkpoint count·scope·PASS/FAIL/BLOCKED/UNTESTED를 실제 raw와 일치시킨다.
4. **Native isolation**: licensed 기존 RimWorld 원본은 read-only로 쓰고 프로젝트 소유의 새 runtime/executable/data/mod/profile copy에서 새 candidate를 실행할 수 있는지 확인한다. 실제 loaded path/SHA/MVID/process/context/save-load-census를 기록한다. 기존 설치의 core/Mods/ProbeMod/Steam/Workshop 설정과 사용자 save를 변경하지 않는다. 격리 실행은 확인할 가설이며 보장이 아니다. 성립하지 않으면 정확한 실패/부분 증거를 남긴다.

구현은 승인된 두 failure를 해결하는 최소한의 일관된 변경으로 진행한다. 기능 이름이나 테스트 수를 늘리기 위해 주변 구조를 재설계하지 않는다. 의미 있는 수정마다 실제 entrypoint → task/result origin → native validator → canonical admission/promotion의 연결을 source와 실행으로 확인한다. 필요한 회귀 테스트를 수행하고 실행하지 않은 항목은 명시한다. 후보를 빌드하기 전·실행하기 전 해당 lineage/source/tooling snapshot을 보존한다.

## 6. 보존할 bytes와 허용 변경

Master-owned `MASTER_A_TASKS.json`의 해당 task **`preservation_policy.allowed_changed_engine_paths`**가 기존 Engine source/build의 승인 변경 목록이다. 경로 밖의 기존 후보/보고서/증거를 정상화하거나 덮어쓰지 않는다. 새 `scratch\EngineGate05R2` 및 프로젝트 내부 독립 runtime과 고유 task의 A 산출물은 WP 범위로 생성한다.

- 역사 Engine19 archive: `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json`
  SHA `B6AD0A70EA4C13F5040A3BAEE690DBCDDEB8735842FCB482D66352A8FB05F0F1`.
- 거절 R1 frozen147: `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780\MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json`
  SHA `1196930576154C11351387B10EAB017C51D6BB027A1686317AB8DF8DAB73022E`. 비교할 대상은 immutable frozen copies다. Current Engine source/Debug output이 old candidate라고 가정하지 않는다.
- Pipeline original + frozen103: `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01\MASTER_REV6_R1_FREEZE_MANIFEST.json`
  SHA `EBCDDBB9340DECBC9ED436845A231412B9003F42663E29D3EE767450319E53A0`. 이전 QA297/S1312/S2238 및 원문/raw/inventory를 보존한다.
- 기존 설치 Gate05 DLL SHA `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C`는 **역사 설치 candidate**이며 새 R2 identity가 아니다. 역사 matching Debug PDB/source는 Engine19 archive에서 복구한다. 현재 mutable Debug/Release를 동일 lineage로 취급하지 않는다.
- R1 원본 report/manifest/harness/results/ACK/COMPLETION도 보존한다. Master의 리뷰/receipt/dispatch/governance/automation/lock helper를 수정하지 않는다.

해시 불일치가 발견되면 원본 expected hash를 actual 값으로 바꿔 맞추지 말고, 변경/누락/범위를 정확히 기록한다. Authority/evidence 무결성에 영향을 주는 충돌이면 해당 진행을 BLOCKED로 보고한다.

## 7. 산출물과 완료 보고

전용 실행/검증 root: `C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R2`

새 보고서: `C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Semantic_Authority_Gate_05_R2.md`

새 release manifest: `C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R2.json`

하나의 selected candidate를 분명히 지정한다. Binary SHA/MVID, matching PDB SHA/CodeView/source/generated checksum, 실제 build args/dependencies, content/profile/schema/semantic manifest version, 실제 실행 binary path/PID/cwd/argv/launch 시각, normal flow와 saved-byte load/census, 보존 before/after 및 harness/raw/result index를 결속한다. Debug/Release alternate를 섞지 않는다.

Task `INSTRUCTIONS.md`가 정한 ACK/terminal schema와 required artifact roles를 그대로 지킨다. **`COMPLETION.json`은 보고서/manifest/raw를 확정하고 각 실제 SHA를 계산한 뒤 마지막으로 발행**한다. Unique result_id, exact dispatch/WP/revision, timezone 포함 completed_at, producer A/report_kind E1, status COMPLETED|BLOCKED|FAILED, summary/e1_verdict/limitations, 절대 project-local artifact paths와 SHA를 담는다. BLOCKED/FAILED면 reason과 partial artifacts를 포함한다. 필수 native proof가 없으면 UNTESTED/BLOCKED를 명시하고 full E1 gate PASS/closure를 선언하지 않는다.

채팅 마지막에는 완료 표식/원문 report/manifest의 절대 경로, selected SHA/MVID, 실제 관측 범위와 미실행·제약, Master 검토 요청을 짧게 남긴다. A는 Master에 직접 메시지를 보낼 endpoint가 있다고 가정하지 않는다. Master는 task 파일을 수집해 review/freeze하고 Sol에게 별도 fresh E2를 지시한다. E1 결과만으로 다음 WP를 스스로 시작하지 않는다.

## 8. 이후 초기화에 대비한 A 로컬 작업 기록

이 고유 task의 **`A_WORK_LOG.md`**에 복구/중요 구현/검증/실패/다음 작업을 실제 시각과 파일·증거 경로로 지속 기록한다. 대화가 초기화되면 이 bootstrap, latest Master governance, task INSTRUCTIONS/ACK/COMPLETION 및 A_WORK_LOG를 다시 읽고 실제 상태를 대조한다. 진행 중 작업이 있다면 같은 WP를 이어가며 다른 task/result ID의 완료를 승계하지 않는다. 채팅 기억이나 스크린 상태만으로 작업을 복원하지 않는다.
