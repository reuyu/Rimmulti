# Pipeline REV6-R1 현재 E2 coverage

공식 전체 판정 **INCONCLUSIVE_FULL_GATE**,007/current schema OPEN,Foundation HOLD. 날짜/패키지 번호/100% 문구로 gate를 승격하지 않는다. 각 exact result의 Master 리뷰/receipt가 근거다.

| 범위 | 현재 근거 | 상태 |
|---|---|---|
| 정상87 operations typed audit/receipt/event/history 및 actual schema descriptor | R1 E2 + Master 읽기 전용 재검사 | 관측 PASS |
| 실제8 PID CAS/4 PID same-operation/5 순차 process, Main/lifetime/UNKNOWN | R1 E2 raw | 범위 내 PASS |
| 정상 case-distinct/rollback canary/unsupported schema/WAL FULL/incarnation API | R1 E2 | 시험 범위 PASS |
| acknowledged commit 이후 종료/restart, 정상 copy/VACUUM/BackupDatabase | S1/두 run | 범위 내 PASS; universal ordering 아님 |
| 실제 default repository write 뒤 세 precommit interruption/recovery | S2/3 cases | 관측 PASS; native Commit 내부 아님 |
| 역사 false observation / invalid·false semantic durable audit / altered DDL·collation 전체 거절 | 정적 source 검토 일부, 전체 runtime 없음 | UNTESTED/전체 closure 미충족 |
| native commit 내부, postcommit response loss, power-loss/장시간I/O/WAL 장애 | 명시 hook/전체 runtime 없음 | 미검증 |
| clock rollback/same-time/운영 timeline restore ordering·rotation | 계약/API/정상 maintenance 일부 | 실제 restore/clock 미검증 |
| 최초 R1 QA Harness binary SHA/MVID | 실행 전 snapshot 미보존 | provenance 제한; S1/S2로 소급 해소 안 됨 |

Pipeline code 수정의 새 failure는 현재 확정되지 않았다. 추가 test 횟수가 이 공백을 자동 해소하지 않는다. 기존 exact Server65FD5E73.../MVIDbbb3d4f4-423c-4379-a931-58e4b3a50add/schema7 candidate는 보존한다. Engine 수정은 독립 track의 이미 확인된 contract failures를 대상으로 하며 Pipeline/Foundation gate를 해제하지 않는다.
