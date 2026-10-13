# S2 실제 reliability 관측 경계

Source base: Frozen/WarEconomyMod/Source/Server/Pipeline. Coordinator와 Storage 기본 구현은 동일 REV6-R1 DLL에서 실행했다. QA의 JournalObserver/AuditObserver는 arguments를 그대로 default repository에 위임한 뒤 read-only 관측·최대30초 대기만 추가한다. 수동 durable INSERT/UPDATE/DDL·기록 생성은 없다.

| Case | 후보 실제 경계 | 같은 transaction 관측 | Commit까지 남은 진행 |
|---|---|---|---|
| commit-parent | Coordinator:375 Journal.InsertRecord → 실제 OperationJournal.InsertRecord 반환 뒤 observer pause | target COMMITTED parent만 신규. 총op2/receipt1/event1/audit1/history1/head1 | CAS/history381, receipt414, event420, audit447, Commit463 미실행 |
| commit-audit | Coordinator:447 Audit.InsertAudit → 실제 AuditLogRepository.InsertAudit 반환 뒤 observer pause | 신규 parent/CAS/history/receipt/event/audit 존재. 각각2/head2 | observer가 coordinator로 반환하기 전. Commit463 미실행 |
| stale-audit | Coordinator:333 Audit.InsertAudit → 실제 reject audit 기본 구현 반환 뒤 observer pause | target ABORTED/reject audit 신규. op2/audit2/receipt1/event1/history1/head1 | Commit346 미실행 |

각 pause의 AFTER_DELEGATED_WRITE 신호는 정확한 child PID, loaded default implementation SHA/MVID, tx.Connection과 동일 connection의 attachment, process-local connection/transaction identity 및 cmd.Transaction=tx readback을 기록한다. 이 identity는 해당 프로세스의 관측용 값이며 durable global order나 authority proof로 쓰지 않는다.

외부 Python read-only reader는 모든 case에서 baseline만 본다. 정확한 새 Popen handle을 신호 확인 후 종료했다. 같은 DB의 cold read가 baseline과 row 단위로 같았고, 새 candidate Initialize/Recovery/default coordinator retry가 정상/STALE 및 ALREADY_COMMITTED/ALREADY_ABORTED로 수렴했다.

관측한 것은 **default repository 함수 반환 뒤, QA observer 반환 전, transaction commit 전**이다. 후보가 제공한 interface seam과 실제 기본 implementation은 Production이고, 신호/SELECT/대기는 QA 추가다. 관측 가능한 native repository-return 경계를 native SQLite Commit 진입/완료 내부 cut, response-loss ambiguity, WAL/fsync/power-loss로 승격하지 않는다. unsupported native commit cut은 반복 추측하지 않았다. S1 post-ack controls도 다시 전체 실행하지 않았다.

예상 외 동기 timeout은 발생0. 세 경계 모두 실제 신호를 관측했고 시간만 기다린 종료는0. timeout/미관측이면 해당 case를 UNOBSERVED로 남기고 재시도하지 않는 driver 경로가 있다. 사용되지 않은 cleanup 종료는 credited boundary count에 들어가지 않는다.
