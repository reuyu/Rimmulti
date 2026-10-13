MASTER RELEASE — WP_PIPELINE_REV6
Status: PREPARED / NOT SENT (Antigravity route/idle 미확인)

실제 작업 루트: C:/Users/user/Desktop/RimMulti. 한국어로 소통한다.
local bootstrap 완료. 먼저 docs/MASTER_GOVERNANCE_CURRENT.md와 docs/WarEconomy_Master_Handoff_20261006/IDE_BOOTSTRAP_VERIFICATION.md를 읽는다. 이전/현재 WP가 처리 중이면 이 WP를 중복 시작하지 않고 상태를 보고한다.
대상은 unchanged exact Pipeline REV5이며 docs/QA_Production_Transaction_Pipeline_01_REV5.md가 controlling E2 FAIL이다. Root Git은 repository가 아니므로 Git clean/commit을 가정하지 않는다. Gate05 선택 DLL SHA2D64FF9C.../matching Debug PDB와 bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json을 작업 전후 보존한다.
아래 승인된 WP를 변경 없이 수행한다. Foundation/auth/gameplay/material/broad architecture 확장 금지.

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
