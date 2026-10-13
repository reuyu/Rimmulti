# Phase 3 3차 사전 리뷰 — 2026-10-01

**판정: 반려. 사용자 인게임 테스트 승인 및 최종 수동 체크리스트 발행 보류.**

화면 제어와 제품 소스 수정 없이 검토했다. 테스트 러너와 보고서만 QA-Phase3에 추가했다. 기존 7777 서버는 사용하지 않았고 임시 포트 테스트 서버는 종료했다.

## 확인한 개선과 테스트 범위

- 솔루션 빌드: 경고 0 / 오류 0.
- 1.6 배포 Client/Common DLL: 현재 빌드와 SHA256 일치.
- Dev의 Round3Checks.cs: 재실행 19/19 통과. 인가된 세션 결과 수용, 다른 명시적 TransferId 거부, 오프라인 영주 거절, 정상 호스트 응답, 완료 요청 제거, 등록 패킷 처리 등 지정된 사례는 통과했다.
- BFS: WorldGrid null, 음수 타일, 없는 레이어, TilesCount 상한, 서로 다른 레이어를 검사하도록 수정된 소스를 확인했다. 실제 Unity 월드에서의 0/1/2/3칸 검사는 수행하지 않았다.
- 기존 null 레지스트리 호출 제거와 bool 결과 분기는 유지됐다.
- 영지 등록 송신 경로와 빈 목록 전송은 추가됐다. 그러나 등록/동기화 순환 및 소유권 덮어쓰기 결함이 생겼다.

19개 테스트에는 AtomicFiefTransferExecutor 실행/롤백, BFS 실행, 실제 클라이언트의 목록 수신→재등록→서버 방송 경로가 없다. 스위트 마지막의 ALL 5 DEFECT REVIEWS VERIFIED 문구는 검증 범위보다 넓으므로 전체 합격 근거로 사용할 수 없다.

## R3-1. High — 영지 목록 동기화가 재등록을 유발하는 무한 순환

위치:
- `WarEconomyMod/Source/Client/Networking/NetworkClient.cs:195` 및 `:200`, `:284`
- `WarEconomyMod/Source/Server/Managers/FeudalManager.cs:60`
- `WarEconomyMod/Source/Server/Program.cs:52`

SettlementListSync를 받을 때마다 RegisterAllLocalSettlements를 실행한다. 플레이 중이고 로컬 플레이어 정착지가 있으면 등록 패킷을 보낸다. 서버 RegisterSettlement는 동일 데이터인지 확인하지 않고 OnSettlementListUpdated를 발생시키며, Program은 목록을 전체 방송한다. 클라이언트가 이를 다시 받아 등록한다. 한 정착지만 있어도 정상 종료 조건이 없고, 여러 정착지/클라이언트가 있으면 요청과 전체 스냅샷 수가 더 늘어난다.

정적 연결 흐름으로 확인했고, 실제 관리자 DLL에 동일 데이터 10회 등록 시 목록 이벤트도 10회 발생함을 측정했다. 게임 클라이언트로 무한 루프를 장시간 실행하지는 않았다.

권장: 접속/게임 로드/신규 정착 등 명시적 이벤트에서만 등록하고 목록 수신은 수신 상태 갱신만 수행한다. 서버는 변경 없는 재등록에 방송하지 않도록 멱등성을 보장한다. 클라이언트 송신과 서버 이벤트를 함께 연결한 제한 횟수 통합 테스트를 추가한다.

## R3-2. High — 롤백 기록 전에 실패하면 변경된 객체가 복구 대상에서 빠짐

위치: `WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:77`, `:79`, `:91`, `:98`, `:124`, `:132`.

현재 순서는 SetFaction → EnableAndInitialize → transferredPawns.Add다. SetFaction이 성공한 후 작업 초기화가 실패하면 해당 폰은 이미 새 세력인데 복구 목록에는 없다. SetFaction 자체가 세력을 바꾼 뒤 콜백에서 실패해도 같은 결과다. Thing과 맵 부모의 변경 기록 역시 호출 뒤에 이루어진다.

원본 실행기 소스를 엔진 경계 테스트 대역과 함께 컴파일하여 다음 두 경우를 재현했다.
1. 작업 초기화 예외: Execute=false이지만 폰 세력은 새 세력, 맵 부모는 이전 세력.
2. 세력 변경 직후 콜백 예외: 동일한 불일치.

두 경우 모두 서버로 전송된 실패 패킷은 변경 수 0이었고, UI 메시지는 이전 상태로 롤백됐다고 표시한다. 실제 Unity 콜백을 실행한 실기 재현은 아니며 실패 주입 기반 제어 흐름 검증이다.

또한 기존 작업/침대·명상 소유권/허용구역/조련 마스터는 사전 정리 뒤 원상 복구되지 않는다. RollbackTransfer 내부의 복구 예외도 로그만 남기므로 완전 복구를 보장하지 않는다.

권장: 변경 전 복구 대상을 기록하고 이전 상태 스냅샷을 확보한다. 변경 도중 예외가 나도 복구 대상에 포함하고 복구 성공 여부를 별도로 검증·보고한다. 복구 불가능한 변경은 명시적 재동기화/복구 필요 상태로 처리하고 완료 문구를 출력하지 않는다.

## R3-3. High — TransferId 필수 검증과 거래 상태 원자성이 여전히 불완전

위치: `WarEconomyMod/Source/Server/Managers/FeudalManager.cs:129`, `:191`, `:203`, `:213`; `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:282`.

TransferId가 비어 있으면 SettlementId의 현재 거래로 대체한다. 실제 관리자 DLL에서 TransferId 없는 성공 응답이 tx-current를 커밋하는 것을 재현했다. 따라서 명시적 과거 ID 거부 테스트가 통과해도 ID 누락 응답은 이전 문제를 다시 만든다. 디버그/이전 클라이언트의 결과를 현재 거래에 붙이면 안 된다.

추가 정적 문제:
- authorizedSessionId를 클라이언트가 제공한 CurrentLordPlayerId로 찾아 지정한다. 실제 등록 영주와 제안 발신자가 일치하는지 확인하지 않는다. 세션을 찾지 못하면 빈 값으로 진행해 결과 인가 검증을 건너뛴다.
- 동일 영지 중첩 검사는 조회 후 대입 방식으로, 복합 연산이 원자적이지 않다.
- 결과 처리도 조회 후 TryRemove 결과와 무관하게 커밋한다. 거래 ID와 SettlementId/TileId 일치 검사도 없다.

권장: 서버가 거래 ID와 등록 영주 기반 실행 세션을 정하고 둘 다 필수로 검증한다. ID 없는 결과는 별도 디버그 경로로 분리하거나 거절한다. 생성·완료는 거래/영지 단위 잠금 또는 원자적 상태 전이로 한 번만 허용한다. 응답의 영지/타일도 검증한다.

## R3-4. High — 등록 패킷이 타 영지의 소유권을 검증 없이 덮어씀

위치: `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:130`, `:138`; `WarEconomyMod/Source/Server/Managers/FeudalManager.cs:60`.

새 영지 등록과 기존 영지 갱신을 구분하지 않고 전달받은 SettlementData를 그대로 대입한다. LordPlayerId가 비어 있지 않으면 발신자와 일치하는지도 확인하지 않는다.

실제 소켓 테스트에서 observer 세션이 기존 host 소유의 owned ID로 등록하자 서버 영주가 observer로 변경됐다. 기존 소유권 검증 없이 등록으로 양도 절차를 우회할 수 있다. 재접속 시의 오래된 클라이언트 등록으로도 서버 커밋 상태를 되돌릴 여지가 있다.

권장: 신규 생성과 기존 갱신을 분리하고 영지 식별자·소유자·세계의 귀속을 검증한다. 기존 소유권은 등록 패킷으로 바꾸지 말고 인가된 양도 절차로만 변경한다. 클라이언트의 로컬 ID 충돌을 피할 서버 영지 ID 체계도 필요하다.

## R3-5. Medium — 방문 취소 권한과 대기 요청 수명 관리 미완료

위치: `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:208`, `:224`, `:245`, `:95`.

VisitCancel은 발신자가 실제 요청자인지 검사하기 전에 TryRemove한다. 실제 소켓 테스트에서 observer가 다른 방문자의 요청을 취소하고 호스트가 취소 패킷을 받는 것을 재현했다.

완료 요청 제거는 개선됐으나 응답 조회→상태 확인→전송→제거는 취소와 하나의 원자적 전이가 아니다. 응답을 보내지 않고 접속을 끊은 요청은 만료/세션 종료 정리 경로가 없다. 따라서 정상 완료 후 0건 검사만으로 수명주기 전체 누수 방지를 입증할 수 없다. VisitRequest에서 sender.PlayerId를 패킷 값으로 다시 대입하므로 응답 인가의 기준 ID도 고정돼 있지 않다(:147).

권장: 접속 식별자를 고정하고 저장된 요청자/호스트 세션을 확인한 후 Pending→종료를 원자적으로 처리한다. 타임아웃 및 양측 연결 종료 시 정리하고 무단 취소, 동시 취소/승인, 무응답 후 연결 종료를 회귀 테스트에 추가한다.

## 증거 및 다음 게이트

- `build-round3-review.log`: 경고 0 / 오류 0.
- `round3-devsuite-review.log`: Dev 테스트 19/19 통과.
- `round3-independent-results.log`: 원본 실행기 실패 주입 2종, TransferId 누락, 동일 등록의 반복 동기화 이벤트, 타 세션 취소, 기존 영지 소유권 덮어쓰기 재현.
- `R3Independent.csproj`, `R3Independent.cs`, `R3EngineStubs.cs`: 독립 QA 러너. 제품 소스 수정 없음.

REPRO PASS는 결함 재현 성공이며 릴리스 합격이 아니다. R3-1과 R3-2는 단일 클라이언트 실기에서도 영향을 줄 수 있어 승인 차단 사항이다. 위 결함 수정 및 실패 경로 재검증 이후에 수동 체크리스트를 최종 발행한다.
