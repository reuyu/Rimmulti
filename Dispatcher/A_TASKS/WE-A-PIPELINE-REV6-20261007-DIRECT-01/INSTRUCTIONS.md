# Master → A: Pipeline REV6 직접 전달

Dispatch ID: `WE-A-PIPELINE-REV6-20261007-DIRECT-01`
WP: `WP_PIPELINE_REV6`, revision `REV6`; delivery envelope revision **2**.
Owner: A (현재 Antigravity의 Primary Development Agent Bootstrap 대화).
Master는 최신 사용자 지시에 따라 Dispatcher를 폐기하고 직접 Computer Use로 이 파일 경로만 전달한다. 기존 Dispatcher 미전송 envelope는 취소된다. 원래 REV6 구현 범위는 유지한다.

## 시작

한국어로 소통한다. 실제 root는 `C:\Users\user\Desktop\RimMulti`다. 아래 절대 경로 문서와 이 파일 아래에 보존한 원래 WP를 읽고 실행한다.

- `C:\Users\user\Desktop\RimMulti\AGENTS.md`
- `C:\Users\user\Desktop\RimMulti\docs\MASTER_GOVERNANCE_CURRENT.md`
- `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\IDE_BOOTSTRAP_VERIFICATION.md`
- `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_PIPELINE_REV6.md`
- `C:\Users\user\Desktop\RimMulti\docs\QA_Production_Transaction_Pipeline_01_REV5.md`
- `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_PIPELINE_REV5_E2.md`
- `C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_PIPELINE_REV5.json`
- `C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\bootstrap\GATE05_LOCAL_FREEZE_MANIFEST.json`

새 작업 시작 전에 현재 진행 중 WP/이미 받은 REV6가 있는지 확인한다. 동일 WP가 이미 실행 중이면 중복 시작하지 않고 그 사실을 ACK에 기록한다. 다른 WP가 처리 중이면 BLOCKED로 보고하고 이 WP를 시작하지 않는다. Git repository/clean/HEAD를 가정하지 않는다.

선택 Gate05 DLL SHA `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C`, MVID `12bb9237-1b3e-4b20-89a7-69ad729861e1`와 matching Debug PDB 및 freeze manifest 19개 파일을 작업 전후 보존한다. Sol Gate05 QA 영역/Engine candidate/source/PDB/fixture/harness/results를 수정·재빌드하지 않는다. 필요하면 멈추고 보고한다. QA raw evidence를 Master 지시에 맞춰 다시 쓰지 않는다.

## 실행 및 보고

기존 승인 범위는 Pipeline 007 historical decision/complete typed audit 및 현재 schema collation의 좁은 수정이다. 기존 001/013 시험 범위 closure 회귀를 확인한다. Foundation/auth/gameplay/material/광범위 architecture 구현은 승인되지 않았다. E1 결과는 독립 E2와 Master closure를 대체하지 않는다. 안전 제약으로 수행할 수 없는 항목은 실제 제한으로 기록하고 미실행을 PASS로 세지 않는다.

Master는 30분 간격으로 파일만 읽는다. Dispatcher 또는 Master로 메시지를 보내려고 별도 agent/scheduler를 만들지 않는다. 아래 디렉터리에 A 소유 보고 파일을 쓴다.

`C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-20261007-DIRECT-01`

1. 먼저 `ACK.json`을 쓴다. 필수: dispatch_id(위 값), wp_id, wp_revision, recipient=`A`, acknowledged_at(ISO8601 +09:00), status=`IN_PROGRESS`/`ALREADY_IN_PROGRESS`/`BLOCKED`, current_wp, message. 이는 수신/시작 보고이며 완료 증거가 아니다.
2. 구현 보고서 권장 경로: `C:\Users\user\Desktop\RimMulti\docs\POC_Production_Transaction_Pipeline_01_REV6.md`.
3. release manifest 권장 경로: `C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_PIPELINE_REV6.json`. 실제 schema/descriptor/signature, Server/Common DLL SHA/MVID 및 matching source/PDB provenance, 실제 harness/results/raw evidence와 알려진 제한을 기록한다. 원본/새 candidate를 구분한다.
4. 원래 WP의 deliverables를 모두 보존한 뒤 **마지막에** `COMPLETION.json`을 쓴다. 임시 파일에 완성한 JSON을 쓴 뒤 동일 디렉터리에서 atomic replace로 공개한다. 완료 후 파일을 몰래 수정하지 말고 새로운 result_id로 amendment 파일과 변경 이유를 남긴다.

`COMPLETION.json` 필수 계약:

- schema_version: 1
- dispatch_id / wp_id / wp_revision: 위 값
- result_id: 고유하고 재사용하지 않는 ID
- producer: A
- status: COMPLETED / BLOCKED / FAILED (PASS/FAIL은 별도 e1_verdict)
- report_kind: E1
- completed_at: timezone 포함 ISO8601
- e1_verdict: 실제 결과 또는 NOT_EXECUTED
- summary / limitations: 실제 결과와 미실행·증거 제한
- artifacts: 각 항목에 role, **절대 path**, sha256. 모든 실제 evidence 파일을 포함한다.
- COMPLETED 시 필수 role: implementation_report, release_manifest, harness, results, raw_evidence, candidate_binary, source, pdb, engine_freeze_before, engine_freeze_after. 여러 binary/source/PDB 항목을 각각 나열한다. manifest에는 DLL마다 MVID와 matching PDB/source document checksum 관계를 기록한다.
- BLOCKED/FAILED 시에도 reason과 현재 보고/증거 artifacts를 기록한다. 만들지 못한 산출물을 임의 hash/PASS로 채우지 않는다.

파일 존재는 완료 판정이 아니다. Master가 dispatch identity/hash/freeze 및 원문 결과를 검토한 후 수집 완료를 기록하고 예약을 일시 정지한다. 독립 Pipeline REV6 E2는 A exact freeze + Sol idle 확인 후 별도 release다.

## 원래 승인 WP (본문 변경 없이 첨부)

# WP — Production Transaction Pipeline REV6
Owner: A. READY AFTER VERIFIED BOOTSTRAP / NOT SENT.
Baseline: exact REV5 + source_reports/QA_Production_Transaction_Pipeline_01_REV5.md.

## Objective
Narrow repair of historical decision/audit semantics and current schema comparison; preserve closed input/lifetime behavior.

## Required work
1. Define historical decision witness/order and threat boundary. Explain how observed revision at decision is established; reject reported coherent-history rewrites. Range, mutable duplicate or recomputable hash alone insufficient. Expose unsatisfied limits rather than claim PASS.
2. Complete required typed audit semantics. Validate mandatory key/type/status/reason/FailureReason/parent/scope/event/receipt/old-new revisions; reject omission/contradiction/unsupported facts; state extra-field/version policy.
3. Canonical key/index collations and relevant comparison semantics in descriptor/validation; rollback-safe case-distinct runtime canary. Do not normalize original identity semantics away.
4. Explicit versions: REV6 release is not schema version. Persistence change requires schema bump. Descriptor/signature contract change needs explicit version/documentation. Do not silently reuse old V6 identity with new meaning. Legacy handling explicit fail-closed/offline policy.
5. Actual DDL/test coverage/current manifest/source-PDB lineage/freeze documentation. Protect frozen Engine candidate.

## Regressions
Natural mixed restart/CAS losers/principal IDs; historical/audit mutations and required omissions; schema semantics/canaries; exact JSON; actual shutdown/Main/UNKNOWN; process concurrency/real hard-kill; terminal/incarnation/WAL FULL.
When claiming OS-process or kill coverage actually execute those categories.

## Deliverables
Implementation report, design rationale, actual descriptor/schema/signature, current release manifest, harness/results, negative proof, binary SHA/MVID/source/PDB identities, before/after Engine freeze proof.

## Stop
No auth/Foundation/gameplay/material/broad architecture expansion.
E1 does not close 007/schema. Independent E2 follows.
