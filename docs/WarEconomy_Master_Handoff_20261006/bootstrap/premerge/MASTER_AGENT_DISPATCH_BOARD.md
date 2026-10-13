# Dispatch — MADB-025
Checkpoint: 2026-10-06. All new work NOT SENT.

| Agent | Latest completed | Current | Next |
|---|---|---|---|
| A | Engine Gate05 E1 | Frozen/idle; recheck | WP_PIPELINE_REV6 |
| Sol | Pipeline REV5 E2 FAIL | Idle; recheck | WP_QA_ENGINE_GATE05 |
| C | G-Q1 contract | Complete/on-demand | none |
| Master | package | bootstrap pending | reconcile/dispatch |
| Dispatcher | none | not configured | approved deliveries |

A prerequisite: bootstrap verified, correct repo/worktree, Engine frozen boundary preserved, idle.
Sol prerequisite: exact Gate05 freeze/evidence identity, QA copies/harness, idle.

Queue: Pipeline REV6 E2 after A E1 freeze + Sol Gate05 completion.
G-Q1 runtime after capacity and bounded fixture/oracle readiness.
Foundation release only after Pipeline E2 PASS and scoped Master release.

Delivery lifecycle: READY_TO_DISPATCH → SENT → ACKNOWLEDGED → IN_PROGRESS → COMPLETED.
BLOCKED/DELIVERY_UNCERTAIN are separate. Recheck uncertain delivery before retry.
