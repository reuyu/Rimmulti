# 다음 A 작업 준비 — R30 handoff correction

상태: PREPARATION_ONLY / NOT SENT. 실제 WP·candidate preservation baseline·release envelope는 R29 S3 최종 독립 증거 판정 이후 확정한다. 이 파일 자체는 전달 승인이나 SENT 기록이 아니다.

R29의 PURE pair6/Capture4 정상 실행과 연결된 bootstrap/handoff 실행을 구분한다. 전자는 정상 결과가 관측됐으나 후자는 native 미검증이며 Source High3가 OPEN이다. 정상 unit 결과를 native closure로 승격하지 않는다.

첫 보정 우선순위는 ENGINE-G05-R29-HANDOFF-20261012-01이다. 좁은 WorkerBridge startup/handoff 경로에서 다음을 충족한다.

- pending parent receipt를 실제 설치된 동일 receipt reference와 결속한다. receipt와 Snapshot이라는 서로 다른 타입의 ReferenceEquals를 사용하지 않는다. Snapshot 일치만으로 실제 receipt 설치·issuer 권한을 주장하지 않는다.
- owner와 동일한 startup cohort에 결속된 one-use handoff를 사용한다. pending 상태의 무단 overwrite와 중복 취득을 막고 현재 receipt 교체·취소 이후 stale 상태를 취득하지 않는다.
- pair mode가 요구된다는 상태를 취득 성공 여부와 구분한다. Awake에서 필요한 handoff가 없거나 어긋나면 로그·정책·리스너 등 관련 실행 전에 fail closed한다. 성공한 private profile만을 조건으로 M05 hold를 결정해 실패가 legacy 실행으로 빠지지 않게 한다.
- cleanup은 동일 owner/cohort에 한정한다. 과거 인스턴스의 OnDestroy가 다른 owner의 pending 상태를 지우지 않는다. 초기 실패·취소에도 소유 범위를 벗어나 전역 상태를 정상화하지 않는다.

실제 허용 source spans와 새 declaration 필요 여부는 frozen R29 source에서 exact byte offsets 및 fixed remainder로 한정한다. PURE pair/capture/codec API와 원래 정상 기대값을 구현 편의에 맞춰 변경하지 않는다. publisher와 carrier는 이번 첫 보정의 범위를 넓히는 근거가 아니다. 두 다른 High가 해소되기 전 operator/native 실행을 승인하지 않는다.

A는 새 Source/DLL/PDB/MVID/manifest와 prospective compiler·normal evidence를 제출한다. static/source checks·fixture·pure execution·actual connected/native proof를 명확히 나눈다. 새 후보는 Master freeze/admission 후 새 독립 QA를 요구하며 R29 PASS를 새 identity로 승계하지 않는다.

후속 순서: R29 S3 terminal 수집·판정 → R30 handoff WP 확정 및 A 실제 전달 → 새 frozen candidate 독립 검증 → carrier/typed arguments/read-before-admission와 publisher non-overwrite/root/config binding 보정 → 필요한 operator/native E2의 별도 admission과 실행. 정확한 WP 분할은 새 증거에 따라 Master가 정하며 R 번호 자체를 완료 목표로 삼지 않는다.

Foundation HOLD, Engine002/006·Pipeline007/current V6 schema·G-Q1 OPEN. 실제 A 전달 전 기존 hourly monitor는 PAUSED 유지한다. C routine 새 WP는 없다.
