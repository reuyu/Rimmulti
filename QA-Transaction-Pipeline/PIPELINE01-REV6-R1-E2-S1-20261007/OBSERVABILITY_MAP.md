# S1 reliability boundary 관측 지도

후보: REV6-R1 Server SHA65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78. Source는 새 Frozen QA copy와 원본 freeze에 일치한다. 아래 line은 Pipeline/Coordinator/PipelineTransactionCoordinator.cs 기준이다.

| 경계 | 실제 source / seam | S1 관측 및 분류 |
|---|---|---|
| DTO admission/channel enqueue | ExecuteProbeCasAsync, TryWrite155 | public API로 호출함. enqueue를 SQLite decision/durable point로 부르지 않음 |
| writer in-flight / delay | _currentInFlightItem192, SimulatedWriterDelayMs193..195, ExecuteSingleWriterCommit199 | delay는 transaction 전. 기존 QA UNKNOWN baseline이며 S1 재실행하지 않음 |
| SQLite transaction 시작 | BeginTransaction243 | static 확인. S1 exact internal cut UNSUPPORTED; 외부 enqueue/시간으로 대체하지 않음 |
| ABORTED record/audit | InsertRecord320 / InsertAudit333 / Commit346 | 2개 genuine stale decisions와 restart 관찰. write 사이 runtime cut UNOBSERVED |
| COMMITTED parent insert | InsertRecord375 | constructor64..78의 IOperationJournal injection seam은 존재함. wrapper는 실제 repository 호출 전후를 관측할 수 있지만 S1 설치/중단 없음. 이 호출의 반환은 durable commit이 아님 |
| CAS/history write | TryExecuteCas381 | IProbeAggregateStore seam 존재. 같은 메서드 내부 update/history SQL 개별 경계 관측은 S1 미설치. exact 내부 cut UNOBSERVED |
| receipt/event/audit append | InsertReceipt414 / AppendEvent420 / InsertAudit447 | 해당 repository interface seam은 존재. 본 S1은 default 실제 repositories 사용. callback으로 Commit463 자체를 관측했다고 하지 않음 |
| 실제 commit 진입/반환 | tx.Commit463 | 직접 전용 callback/hook은 확인되지 않음. S1 내부 commit cut UNSUPPORTED; patch/rebuild/debugger mutation 없음 |
| 결과 반환 | Ok465→writer TCS200→public blocking result | SUCCESS 결과 실제 관측. 그 이후 child 내부 SELECT와 독립 외부 read-only SELECT가 durable row를 확인 |
| acknowledged 결과 이후 종료 | 이번 QA child가 SUCCESS/READBACK 신호 후 stdin 대기 | 정확한 생성 Process handle/PID만 Kill. 내부 transaction은 완료된 상태이며 writer idle. OBSERVED_POST_ACK_BASELINE |
| 새 process recovery/retry | 실제 InitializeDatabase/ReconcileAndVerify/coordinator | ALREADY_COMMITTED와 동일 receipt/head/cardinality/incarnation 확인. 응답 유실 또는 power-loss proof 아님 |
| VACUUM/backup/closed copy | QA DB 정상 closure 후 새 QA copies, native SQLite3.41.2 | semantic records/rowid relation/integrity/FK/schema/recovery/retry 정상 관측. universal ordering theorem으로 채택하지 않음 |

Interface injection이 가능하다는 정적 사실과 이번 실제 사용한 관측을 구분한다. 모든 write seam이 절대 관측 불가능하다고 결론내리지 않는다. 이번 WP는 내부 cut 시험을 요청하지 않았으며, Production native commit 내부의 정확한 crash 시점이나 WAL/fsync/power-loss는 관측하지 않았다.

SqliteDatabaseContext.cs:154..182의 RotateStoreIncarnation은 새 active ID를 transaction으로 기록하는 API다. Initialize/ValidateReadiness는 기존 active incarnation을 유지/확인한다. current frozen Pipeline source에서 backup/VACUUM/restore workflow orchestration 또는 timeline rollback 감지·자동 rotation을 찾지 못했다. MASTER_HANDOFF.md의 accepted ordinary restart 유지 / timeline restore·rollback rotation은 요구 계약으로 유지한다. 단순 정상 backup/copy 관측이 timeline 교체 정책을 확정하지 않는다. 이번 QA는 rotation 정책이나 fencing 연동을 새로 정하지 않는다.
