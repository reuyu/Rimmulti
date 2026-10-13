# Master Handoff
Checkpoint: 2026-10-06. Prepared: 2026-10-07.

## 목표
Dedicated Server canonical authority 위에 ordinary settlement, shared Tactical, lawful offline combat, custody/ownership, diplomacy/economy를 통합하는 RimWorld 1.6 모드다.
전체 요구사항은 root SRS로 복구한다. 이 요약은 SRS를 대체하지 않는다.

## 현재 위치
P1 Transaction Pipeline repair와 shared Engine Host semantic authority가 병목이다.
전체 진행 약 25~35%, 기반 PoC 약 65~75%라는 과거 수치는 대화상 추정이며 WBS 측정·일정·gate 근거가 아니다.

| Track | Evidence | Master disposition | Next |
|---|---|---|---|
| Pipeline REV5 | Sol E2 FAIL | 001/013 좁은 CLOSED, 007·V6 collation OPEN | A REV6 |
| Engine Gate05 | A E1 65/65 reported PASS | E1 accepted, E2 required, 002/006 OPEN | Sol Gate05 E2 |
| G-Q1 contract | C analysis/no code | accepted with corrections; no runtime verdict | corrected runtime contract |
| Migration | 사용자가 문서 생성 승인 | package prepared, local bootstrap pending | IDE Master |

## 보존할 계약
1. Server final Domain Authority; execution authority는 final custody가 아니다.
2. W(WorldTick), L(residence/local simulation), G(engine), M(monotonic operational time)는 별도다.
3. Offline ordinary ΔL=0. Authorized asset transaction을 금지하는 뜻은 아니다.
4. Accepted server downtime ΔW=0; 실행 중 zero-player W는 진행.
5. one LocalClock writer; island-scoped barrier. Divergent simultaneous clocks는 G-Q1 증거가 필요하다.
6. Full Worker save는 context/checkpoint/extraction input. Target write-set와 explicit transfer만 canonical merge.
7. ArtifactBaseStateRevision watermark와 CommittedSettlementStateRevision head를 구분.
8. PendingOperationQueue를 committed인 것처럼 materialize하지 않는다.
9. Durable operation key=(PrincipalId, OperationId). Principal과 SessionEpoch는 별도.
10. Caller hash는 authority가 아니다. StoreIncarnation은 ordinary restart 유지, timeline restore/rollback 등에 rotate.
11. Single-scope typed atomic path와 staged/multi-party PREPARED path를 구분.
12. Pipeline 현재 slice는 PublicationEvent durable append까지만. Consumer ACK/dedup/external effect exactly-once는 별도다.
13. ADR acceptance ≠ runtime completion. Material/trade/tax/tactical release는 아직 HOLD.

## C 기억 복구
C taxonomy는 유효하나 exact subsystem owner·physical split은 미확정이다.
Canonical PlayerGlobal revision은 Server-authorized다. Quest/WorldPawns read-only, Tales/PlayLog/Storyteller/Weather discard/re-roll은 미증명이다.
현재 correction과 history 추출을 필수로 읽는다.

## 다음 순서
Local bootstrap → A REV6/Sol Gate05 E2 → A freeze·Sol idle 후 Pipeline REV6 E2.
G-Q1 probe는 corrected contract로 후속 실행.
Pipeline E2 PASS 뒤 Foundation release 검토. G-Q1을 모든 metadata 작업의 blocker로 확대하지 않는다.

현재 사용자가 보고한 A/Sol/C 완료 상태를 전달 직전에 다시 확인한다. 새 WP는 아직 전송하지 않았다.
