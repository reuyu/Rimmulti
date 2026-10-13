# WarEconomy IDE Master Handoff
Project: WarEconomy / RimMulti / RimWorld 1.6
Decision checkpoint: 2026-10-06 Asia/Seoul
Package produced: 2026-10-07 Asia/Seoul
Status: DOCUMENTS PREPARED / LOCAL INSTALLATION AND BOOTSTRAP NOT EXECUTED

어제 통합 메시지로 전달한 문서를 실제 파일로 완성한 패키지다. 새 QA 결과나 이후 구현 진척을 가정하지 않는다.

## 설치
1. 실제 저장소 docs/master-handoff-20261006/에 ZIP 내용물을 푼다.
2. 기존 루트 AGENTS.md가 있으면 보존하고 이 패키지 AGENTS.md 지침을 병합한다. 없으면 복사한다.
3. IDE_MASTER_BOOTSTRAP_PROMPT.md 본문을 새 마스터의 첫 메시지로 전달한다.
4. 새 마스터는 SRS·현재 git 상태·governance·candidate·raw evidence를 대조한다.
5. 검증 후에만 다음 승인된 WP를 전달한다. 이 패키지 생성은 전송 증거가 아니다.

## 필수 읽기
- [Master handoff](MASTER_HANDOFF.md)
- [C 정정본](C_REVIEW_CORRECTIONS_CONSOLIDATED.md)
- [C 원문 판정표](C_SOURCE_DISPOSITION_REGISTER.md)
- [현재 상태](MASTER_PROJECT_STATE.md)
- [결정 delta](MASTER_DECISION_LOG.md)
- [QA delta](QA_DEFECT_LEDGER.md)
- [Dispatch](MASTER_AGENT_DISPATCH_BOARD.md)
- [ADR acceptance](ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md)
- [원문 목록](SOURCE_REGISTER.md)
- 해당 원문과 raw evidence

## 핵심 현재 상태
Pipeline REV5 E2 FAIL. 001/013만 시험 범위 내 CLOSED. 007·현재 V6 collation OPEN.
Engine Gate05 E1 accepted / E2 pending. Engine 002/006 OPEN.
G-Q1 OPEN. Foundation HOLD. 다음 작업 A Pipeline REV6, Sol Gate05 E2, 모두 NOT SENT.
C는 정규 배치에서 제외하고 필요할 때 분석자로 사용한다. 계정·대화를 삭제한 것이 아니다.
Dispatcher는 미설정이며 예약을 생성하지 않았다.

## 권한 해석
C 원문·ADR PROPOSED header·자체 PASS·과거 ledger 첫 표만 보고 현재 상태를 확정하지 않는다.
Master 정정과 범위별 acceptance를 함께 읽는다. 역사 자료는 history/, 원문 보고서는 source_reports/, ADR는 reference_adrs/에 보존했다.

## 없는 자료
Root 요구사항_명세서.md, 실제 source/git/binaries/raw logs/fixtures는 이 패키지에 없다.
모든 과거 C 원문을 확보한 것은 아니다. 역사 리뷰 추출은 포함했으며 미확보 원문은 재구성하지 않았다.
코드·실행 증거·로컬 설치를 직접 검증했다고 주장하지 않는다.
