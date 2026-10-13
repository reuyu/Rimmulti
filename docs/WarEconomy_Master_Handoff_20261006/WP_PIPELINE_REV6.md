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
