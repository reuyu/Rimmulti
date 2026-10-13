# WarEconomy A 전용 Dispatcher 파일 계약

사용자 2026-10-07 지시: Master↔Sol은 직접 thread tools로 소통한다. Dispatcher는 Antigravity의 Gemini A만 담당한다. 매시간 A 결과를 Master에게 제출하고 approved A work를 전달한다. 이 파일 생성은 Dispatcher scheduler/Antigravity endpoint의 실행 확인이 아니다.

## 파일 소유권과 경로

- Master 소유 approved outbox: `C:\Users\user\Desktop\RimMulti\Dispatcher\MASTER_TO_A_OUTBOX.json`.
- Dispatcher 소유 A 결과 inbox: `C:\Users\user\Desktop\RimMulti\Dispatcher\A_TO_MASTER_INBOX.jsonl`.
- Dispatcher 소유 전달 journal: `C:\Users\user\Desktop\RimMulti\Dispatcher\DISPATCHER_JOURNAL.jsonl`.
- Master의 최종 판정/수집 dedupe: `MASTER_RECEIPTS.json`, `MASTER_COMMUNICATION_STATE.json`.
- Current substantive governance: `docs/MASTER_GOVERNANCE_CURRENT.md` 및 handoff current state/decision/defect/dispatch.

Outbox schema의 `items` 각각은 고유 dispatch_id, recipient A, approved true/false, wp_id/wp_revision, delivery_envelope_revision, absolute WP/release/references, exact message, prerequisites, created_at, approval evidence, status를 가진다. Master가 approval/revision/cancel만 관리하며 Dispatcher가 approved payload를 덮어쓰지 않는다. 수정된 payload는 새 dispatch_id/revision이다. 취소는 기존 미전송 항목에 cancellation delta를 명시한다.

## 매시간 처리 순서

1. 실제 Antigravity endpoint/대화, 현재 WP, 이전 전달 journal을 확인한다. A가 작업 중이면 새 WP를 보내지 않는다. 일시 침묵/화면 상태/PASS 단어만으로 완료 판정하지 않는다.
2. OS exclusive non-overlap lock을 확보한다. `DISPATCHER_RUN.lock`를 `FileShare.None`/동등한 실제 exclusive primitive로 유지할 수 없으면 BLOCKED. lock 파일 존재만으로 lock을 주장하지 않는다.
3. A 새 완료 원문/실제 파일·증거/시각/현재 WP를 inbox에 immutable result_id로 추가한다. Original report/evidence의 absolute paths와 SHA를 남긴다. E1/E2를 구분한다.
4. Master thread `01a1156b-97ec-7ce0-9e4a-dfc4a3acb174`, host local에 새 result_id와 원문 paths를 제출한다. 전송 불가면 inbox를 남기고 limitation을 기록한다. Master heartbeat가 직접 파일을 수집할 수 있다.
5. 승인 outbox의 유효·미취소 항목만 확인하고 prerequisites·idle·candidate freeze·동일 WP 비중복·journal을 전달 직전에 재확인한다.
6. exact message를 제출하고 실제 대화의 제출/수신을 확인한다. journal에 dispatch_id, source/recipient endpoint, wp_id/revision, at, SENT, message identity/전송 근거를 남긴다. 불확실하면 DELIVERY_UNCERTAIN, 재시도 전 inspect.
7. Outbox 등록/읽음은 SENT가 아니다. Master는 Dispatcher journal의 검증된 SENT 후 자신의 dispatch board를 갱신한다.
8. 신규 WP/게이트/architecture/closure를 만들지 않는다. QA에게 WP를 전달하지 않는다. 잠금 해제 후 종료한다. 변경이 없으면 조용히 끝낸다.

Inbox는 기존 hourly Dispatcher가 사용하는 JSONL이며 한 줄에 immutable event/result 하나를 기록한다. 결과 item에는 result_id, recipient Master, producer A, wp_id/wp_revision, completion_status, original_report_paths, evidence_paths, artifact hashes, observed_at, source_endpoint, original_message/proof, report_kind(E1)을 담는다. 전달 journal JSONL 각 event에는 event_id, dispatch_id/result_id, event(SENT/ACKNOWLEDGED/IN_PROGRESS/COMPLETED/BLOCKED/DELIVERY_UNCERTAIN), at, endpoint, proof를 담는다. Master는 이런 item을 읽고 별도 receipts에 수집/판정 결과를 기록한다.

현재 로컬에서 Dispatcher 실행/endpoint/scheduler는 미검증이다. 사용자 설명상 매시간 운용을 예정/운영 중이라고 기록하되 실제 구동을 가정하지 않는다. 원래 package의 null endpoint/disabled 설정을 근거 없이 true로 바꾸지 않는다.


## 실제 기존 자동화 확인 — 2026-10-07T18:02:53.308457+09:00
기존 app 자동화 WarEconomy 전달 업무 실행(id wareconomy-dispatcher-master-a)은 매시간 정각/ACTIVE, target thread01a1158a-c15a-76f0-a6fb-6b192cc2f23a로 설정되어 있고 QA 제외/A-only다. 이 기존 설정의 파일 이름(A_TO_MASTER_INBOX.jsonl, DISPATCHER_JOURNAL.jsonl, DISPATCHER_STATE.json)을 canonical Dispatcher-owned paths로 사용한다. 해당 thread history/wait은 현재 missing source rollout 오류로 접근되지 않으므로 runtime/SENT는 미검증. Master가 기존 1시간 일정을 변경하거나 새 Dispatcher로 대체하지 않았다.


## Superseded communication contract — 2026-10-07T18:28:00.650060+09:00
Latest user removed Dispatcher. Current contract: MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md; current A task board: MASTER_A_TASKS.json. Above hourly Dispatcher/10min instructions are historical, not active authorization. No Dispatcher recreation.
