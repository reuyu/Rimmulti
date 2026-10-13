# Pipeline REV6-R1 E2 보완 S2

**관측한 S2 repository 경계별 reliability controls 3개 PASS. 전체 gate는 INCONCLUSIVE_FULL_GATE / COMPLETED_SCOPE_LIMITED 유지.** 새 Production failure를 확인하지 않았으며 007/current schema closure, Foundation release나 governance 상태를 변경하지 않았다. 마지막 Master disposition이 공식 상태를 결정한다.

Result `SOL-PIPELINE-REV6-R1-E2-S2-20261008-2ed05cb01ecc46a49cd15551ea3ad89f`. WP `WP_QA_PIPELINE_REV6_R1_E2_SUPPLEMENT`, revision `S2`; delivery `SOL-PIPELINE-REV6-R1-E2-S2-20261008-d4da89a6e81e`. 완료 2026-10-08T00:09:37.315807+09:00 (Asia/Seoul). QA root의20261007 suffix는 exact WP 경로를 유지한 것이며 이번 실행·보고 날짜는2026-10-08이다.

## 후보와 실행 도구

| 항목 | 실제 확인값 |
|---|---|
| REV6-R1 Server DLL SHA / MVID | `65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78` / `bbb3d4f4-423c-4379-a931-58e4b3a50add` |
| Server PDB SHA | `7A99DAD44A6F32A7FDAFABA2534C5914C73C958B1F86E27A21CEBAE7F6A4A239` |
| Common SHA / MVID | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` / `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` |
| Master103 inventory SHA | `EBCDDBB9340DECBC9ED436845A231412B9003F42663E29D3EE767450319E53A0` |
| Schema / application ID / actual descriptor | `7` / `1463898693` / `079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C` |
| S2 Tooling R1 DLL SHA / MVID | `DADDC7AE65EFDA52B01815BA028973196D4D656702799E39CF4A29E05B589B1B` / `ac2f8373-5660-43a5-858d-07831c02cecd` |
| S2 Tooling PDB SHA | `F2BE2667761A5D6821B4789989C5EDD229643256D5DA40AEEDFA6E4218C96029` |
| Runtime | .NET8.0.10, Microsoft.Data.Sqlite8.0.10, native SQLite3.41.2 |
| Independent read-only metadata/oracle | Python3.13.5 / SQLite3.45.3 |

QA copy 준비 후 **첫 실행 전에** frozen103/원본103/copy103/Engine19/기존297/S1312 전체 hash를 확인했다. 전후 모두 변경0이다. Production/frozen/기존 evidence 수정·재빌드0. 독립 QA Harness만 한 번 빌드했고 실행 전에 source/generated-source/DLL/PDB/MVID/dependencies20파일과 명령을 R1로 보존했다. 각 실제 child log의 loaded tooling/Server SHA·MVID가 그 snapshot과 일치한다. DLL CodeView/PDB GUID 및 checksum Harness4/Server20/Common25가 일치한다. R1 snapshot20 후검사도 일치했다. build는 오류0, nullable scalar의 CS8604 warning1이었다. 이 경고는 QA Emit 매개변수 정적 nullability 경고이며 실행 오류는 없었다.

[실행 전 tooling snapshot](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json), [후보/tooling 실행 전 lineage](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/candidate-tooling-before.json), [first before freeze](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/freeze-before.json), [after freeze](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/freeze-after.json).

## 실제 위임·관측 경계

fresh DB3개에 actual default coordinator로 baseline commit1개씩 생성했다. 이후 genuine `InterruptedOperation` 요청은 정상 expected1 또는 stale expected0이었다. QA JournalObserver/AuditObserver는 같은 arguments를 실제 OperationJournal/AuditLogRepository에 그대로 위임했다. 후보 SQL/coordinator를 복사하거나 durable records·DDL을 수동 생성하지 않았다. 다른 repositories는 candidate 기본 구현이다.

**관측 시점은 실제 기본 repository 함수 반환 뒤, QA observer 반환 전, coordinator의 transaction commit 전이다.** QA는 이 시점에 same-connection SELECT와 bounded30초 pause를 추가했다. 신호에는 정확한 child PID, 구현 assembly SHA/MVID, tx.Connection attachment, process-local tx/connection identity 및 전체 같은 transaction readback이 있다. 외부 reader가 마지막 committed baseline만 보는 것도 별도 확인했다. process-local identity를 durable sequence/authority token으로 표현하지 않는다.

아래 개수는 baseline과 pending target을 합한 값이다. O/R/E/A/H는 OperationRecords/CommitReceipts/PublicationEvents/AuditRecords/ProbeRevisionHistory다.

| Case / 후보 source 지점 | 내부 pending O/R/E/A/H, head | 아직 미실행인 commit |
|---|---|---|
| commit-parent: Coordinator375, 실제 OperationJournal.InsertRecord 반환 | 2/1/1/1/1, head1. target COMMITTED parent만 pending | CAS/history 및 나머지 자식, tx.Commit463 미실행 |
| commit-audit: Coordinator447, 실제 COMMITTED AuditLogRepository.InsertAudit 반환 | 2/2/2/2/2, head2. 모든 target 효과가 pending | observer가 아직 반환하지 않아 tx.Commit463 미실행 |
| stale-audit: Coordinator333, 실제 REJECTED AuditLogRepository.InsertAudit 반환 | 2/1/1/2/1, head1. target ABORTED 및 reject audit pending | tx.Commit346 미실행 |

각 경계의 실제 AFTER_DELEGATED_WRITE 신호와 위 readback을 받은 후 그 실행에서 생성한 정확한 Popen handle/PID만 종료했다. 시간만 기다린 종료0, 신호 없는 boundary credit0, timeout0, unrelated process 종료0이다. 추가 반복은 없었고 새 tooling revision/rebuild도 필요하지 않았다. [실제 경계 지도](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/OBSERVED_BOUNDARIES.md), [wrapper source](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/Harness/Program.cs), [processes/argv/PID/시각/exit/raw](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/Evidence/processes.json).

## Rollback, recovery 및 retry

세 case 모두 외부 reader의 pause-time 전체 rows가 seed baseline과 동일했다. 강제 종료 직후 cold read도 baseline과 row 단위로 동일했다. 즉 pending target parent/자식/aggregate 증가는 committed state로 남지 않았다. DB integrity=`ok`, FK violation0이었다.

새 process에서 실제 candidate Initialize/Recovery 후 같은 genuine 요청을 재시도했다. 정상2개는 SUCCESS 및 후속 ALREADY_COMMITTED, stale1개는 STALE_REVISION 및 후속 ALREADY_ABORTED로 수렴했다. 정상 case의 반환 Receipt 모든 필드가 terminal repeat와 동일했다. baseline의 immutable records/receipt/event/audit/history와 incarnation은 유지됐고 새 요청의 효과는 정확히 한 번 append됐다.

| 최종 정상 상태 | O/R/E/A/H, head | 의미 |
|---|---|---|
| commit-parent / commit-audit 각각 | 2/2/2/2/2, head2 | baseline+target COMMITTED2개; target durable effect1개 |
| stale-audit | 2/1/1/2/1, head1 | baseline COMMITTED1 + target ABORTED1; reject audit1, target receipt/event/history0 |

최종3개 DB의6 operations(5 COMMITTED/1 ABORTED)을 별도 Python oracle로 검사했다. mandatory audit keys/type/count/status/reason/FailureReason, parent/scope/revision/cardinality/stream continuity, server fingerprint/derived IDs/receipt/payload hash가 일치했다. 실제 recovery는 retry 전후 각각 성공했다. actual schema descriptor도3개 DB에서 독립 재계산하여 exact expected signature와 일치했다. 이전 oracle의 함수만 AST로 읽고 S2 read-only DB에 적용했으며 이전 모듈 top-level/evidence write는 실행하지 않았다.

총9 OS-process=seed3+interrupted3+fresh retry3. 정상6개 exit0, 정확한 owned repository-boundary 종료3개는 의도한 nonzero exit다. [S2 raw 결과](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/Evidence/s2-results.json), [독립 최종 data/schema 결과](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/Evidence/independent-final-data-results.json), 각 case의 baseline/external-at-pause/cold/final JSON 및 DB를 보존했다.

## 정확한 범위와 남은 공백

이번에는 기존 repository seams를 통해 precommit reliability 경계3개를 실제 관측했다. S1의 post-ack baseline이나 synthetic raw-SQL transaction을 이3개의 근거로 재사용하지 않았다. Production default repositories가 실제 쓰기를 수행했고, 관측 신호/SELECT/대기는 QA 추가 행위다. 이것은 modified default timing을 가진 QA fault simulation이며 비계측 Production의 자연 crash 빈도/모든 시점을 재현한 것은 아니다.

**Native SQLite Commit 내부 진입/완료의 정확한 cut, commit 후 response-loss ambiguity, WAL/fsync/power-loss는 미검증이다.** tx.Commit 직접 hook은 없고 S2는 그 내부를 중단하지 않았다. 모든 repository 경계가 unsupported라는 종전 오해는 적용하지 않는다. 다른 write 경계/장시간 I/O/lock/WAL 장애, historical/audit/schema adverse rejection, forged authority, extreme exponent, clock rollback, timeline restore authority 및 universal maintenance ordering 공백은 유지한다. unsupported native cut을 시간·함수 진입·enqueue로 대신하지 않았다.

이 새 tooling provenance로 이전 R1 최초 QA binary 미보존을 소급 해소하지 않는다. 정상6 operations 및 세 interruption이 canonical SRS NFR004..007의 모든 제품 transaction을 인증하지 않는다. MAC-001의 single-scope fast path와 staged/multi-party 구분, Server final Domain Authority, publication append 이후 consumer delivery 별도 계약을 유지한다. Foundation 및 G-Q1/Engine gate의 공식 상태를 변경하지 않았다.

## 산출물과 보고

[QA root](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007), [result index](C:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/coordination/SOL_PIPELINE_REV6_R1_E2_S2_RESULT_INDEX_20261007.json), [full evidence inventory](C:/Users/user/Desktop/RimMulti/QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/EVIDENCE_MANIFEST.json)에 고유 result/delivery/candidate/tooling와 report·raw evidence SHA를 연결했다. manifest 자신의 SHA는 index에 있다. transport proof는 별도 coordination에 보존한다. Master에게 한 번 직접 보고하며 tool delivery 성공과 Master의 수집/closure disposition을 구분한다. QA는 state/defect closure/automation을 수정하지 않았다.
