# Phase 3 2차 사전 리뷰 — 2026-10-01

**최종 판정: Dev 사전 수정 필요. 승인용 수동 실기 체크리스트 최종 발행 보류.**

화면 제어/게임 실행 없이 정적 분석, 실제 RimWorld 1.6 엔진 IL 확인, 실제 Server/Common DLL의 터미널 테스트를 수행했다. 제품 소스는 수정하지 않았다. 기존 7777 서버는 건드리지 않았으며 별도 테스트 서버(임시 포트 52671)를 종료했다.

## 이전 7건 회귀 판정

| 이전 결함 | 2차 결과 |
|---|---|
| 1. UpdateRegistryForPawn(null)와 무조건 성공 메시지 | 해소 확인. 실제 pawn 전달, bool 결과에 따른 메시지 분기 |
| 2. 실패한 양도 서버 소유권 확정 | 부분 해소. 단일 요청 실패 시 기존 소유권 유지 통과. 다중 클라이언트/중첩 양도와 클라이언트 부분 실패는 미해소 |
| 3. 취소 후 늦은 승인 | 부분 해소. UI 참조 정리와 순차 취소→승인 드롭 통과. 서버 상태 전이의 원자성, 발신자 검증, 완료 요청 정리는 없음 |
| 4. 무관한 접속자로 방문 요청 전달 | 부분 해소. 온라인 호스트 단독 전달 및 NPC 독립 자동 승인 통과. 오프라인 플레이어 영지도 NPC로 자동 승인 |
| 5. 근사 2칸 거리 | 유효한 동일 레이어 타일의 0/1/2-Hop 판정 구조로 수정됨. 실제 생성 월드 경계 실측은 미수행 |
| 6. 국경 판정 레이어 손실 | 국경 입력/SettlementData.LayerId/로컬 시야 키 경로는 보존 확인. 별도로 존재하지 않는 레이어·상한 밖 인덱스 방어 필요 |
| 7. KnownSettlements 미연결 | 전송/수신 연결은 추가됨. 하지만 제품 코드에 RegisterSettlement 호출자가 없어 실제 목록 생성 경로는 여전히 없음 |

빌드: 경고 0, 오류 0. 배포 1.6 Client/Common DLL과 빌드 DLL SHA256 일치.

## 남은 차단 결함

### R2-1. High — 잘못된 클라이언트/거래의 응답이 Pending 양도를 소모하거나 확정

위치:
- `WarEconomyMod/Source/Server/Program.cs:37`
- `WarEconomyMod/Source/Server/Managers/FeudalManager.cs:102`, `:125`
- `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:255`
- `WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:28`

실행 패킷은 모든 세션에 방송한다. 맵을 로드하지 않은 클라이언트도 실패 결과를 회신한다. 서버는 발신 세션/거래 ID 확인 없이 영지 ID로 첫 결과를 TryRemove한다.

실제 관리자 DLL에서 다음을 재현했다.
1. D에게 양도 대기 → 맵 없는 클라이언트 실패 → 실제 실행자 성공. 서버는 이전 소유자를 유지하고 실제 성공은 Standalone 로그로만 처리한다. 로컬 실행자와 서버 상태가 갈라진다.
2. B 양도 대기 → 같은 영지 C 양도 대기로 덮어쓰기 → B 실행 성공 결과. 서버는 C에게 양도를 확정한다. 결과 패킷에 거래 ID가 없어 구분할 수 없다.

권장: 실행 대상 세션을 지정하고 응답 세션을 검증한다. 거래 ID를 Execute/Result에 포함하고 동일 영지의 중첩 요청을 거절하거나 직렬화한다. 대상 클라이언트 결과만 처리하고 시간 초과/재접속 처리도 정의한다. ConcurrentDictionary는 복합 거래 전체를 원자적으로 만들지 않는다.

### R2-2. High — 클라이언트 부분 실패를 여전히 성공으로 회신

위치: `WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:77`, `:94`, `:125`, `:135`, `:138`.

폰 정리/SetFaction/레지스트리 갱신에서 예외를 잡아 기록한 뒤 계속 실행하고 최종 Success=true를 보낸다. 새 bool 반환형 역시 이 경로에서 true라 성공 메시지를 막지 못한다. 외부 catch로 빠지는 경우에도 이미 바꾼 폰/건물/맵 상태를 되돌리지 않는다.

이는 정적 분석으로 확인한 제어 흐름이다. 실제 Unity 콜백 예외를 게임에서 주입한 것은 아니다. 서버의 기존 소유권 보존은 클라이언트 복구를 보장하지 않는다.

권장: 폰별 오류를 집계해 성공 조건을 엄격히 하고, 사전검증/복구 스냅샷/실패 후 재동기화 정책을 구현한다. 클라이언트 일부만 변경된 상태를 원자적 성공으로 보고하지 않는다.

### R2-3. Medium — 방문 라우팅 수정 후에도 권한·상태·수명 관리 미완료

위치: `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:137`, `:165`, `:186`, `:202`.

실제 3클라이언트 소켓 테스트 결과:
- 온라인 호스트만 요청을 받음: 통과.
- 무관한 세션이 있어도 NPC 자동 승인: 통과.
- 서버가 취소를 처리한 뒤 도착한 승인 드롭: 통과.
- 등록된 플레이어 영주가 오프라인이면 NPC로 자동 승인: 결함 재현.
- 무관한 observer가 호스트용 요청 ID로 응답해도 승인 전달: 결함 재현. 라우팅만 제한하고 응답 발신자는 검증하지 않는다.
- 이미 승인된 요청에 다시 거절 응답을 보내도 전달: 결함 재현. Cancelled만 검사하며 Pending 상태를 요구하지 않는다.
- 위 테스트의 완료/취소 요청 4개 모두 _activeVisitRequests에 잔존: 확인. 삭제/만료/접속 종료 정리 코드가 없다.

추가 정적 문제: 다른 세션의 수신 루프가 Cancel과 Response를 동시에 처리할 수 있는데 상태 확인→변경→전달에 동기화가 없다. 순차 늦은 응답 테스트 통과가 동시 경쟁 차단을 보장하지 않는다. 취소 발신자도 확인하지 않는다.

권장: 서버 등록 정보로 NPC/플레이어 소유자를 구분하고 오프라인 플레이어는 자동 승인하지 않는다. 요청자/호스트 세션 검증, Pending에서 한 번만 끝나는 원자적 상태 전이, 응답 목적지의 서버 저장값 사용, 완료 제거 또는 만료되는 이력 보관을 적용한다.

### R2-4. Medium — 정착지 목록 패킷은 연결됐지만 원본 목록이 생성되지 않음

위치: `WarEconomyMod/Source/Server/Managers/FeudalManager.cs:30`; `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:119`; `WarEconomyMod/Source/Client/Networking/NetworkClient.cs:192`.

Source 전체 검색에서 RegisterSettlement는 선언만 존재한다. Program의 로딩/시드, 클라이언트 정착지 등록, 저장 데이터 복원 등의 호출 경로가 없다. 따라서 일반 실행으로 생성된 서버에는 동기화할 영지가 없으며, 방문 소유자 해석도 등록 정보 없이 NPC로 흐른다.

테스트 러너가 직접 두 영지를 등록했을 때에 한해 핸드셰이크 목록 수신 및 LayerId 직렬화 보존을 확인했다. 이는 실제 게임→서버 등록 경로가 구현됐다는 뜻이 아니다.

추가: 빈 목록이면 핸드셰이크 스냅샷을 보내지 않는다(:121). 이전 서버의 KnownSettlements가 남아 있는 클라이언트는 빈 서버로 재접속해도 과거 국경 목록을 유지할 수 있다.

권장: 실제 등록/복원 경로를 연결하고 빈 목록도 완전한 스냅샷으로 전송한다. 재접속/월드 변경 시 캐시를 정리한다.

### R2-5. Medium — PlanetTile.Valid를 범위·레이어 존재 검증으로 오인

위치: `WarEconomyMod/Source/Client/Patches/FogOfWarPatches.cs:156`, `:158`, `:168`, `:203`.

실제 1.6 엔진 IL에서 Valid는 tileId >= 0만 확인한다. Layer 속성은 WorldGrid.PlanetLayers[layerId]를 직접 조회한다. 따라서 존재하지 않는 LayerId는 `?.LayerID`로 보호되지 않고 예외를 발생시킬 수 있다. 상한 밖 양수 TileId도 Valid를 통과하며 이웃 버퍼 접근으로 전달된다. 이번 BFS 경로는 이전 근사 거리의 GetTileCenter 범위 검사 경로와 다르다.

권장: WorldGrid 존재를 먼저 검사하고, 레이어 TryGetValue 및 `0 <= tileId < layer.TilesCount` 확인 후 이웃 탐색을 수행한다. 서버 스냅샷 항목 null/잘못된 ID도 거절해야 한다.

## 수동 체크리스트 최종 발행 전 바로잡아야 할 기대 결과

현재 사전 게이트 미통과이므로 사용자 실행을 승인하는 최종 체크리스트는 발행하지 않는다. 다음 사항은 수정 후 체크리스트에 반드시 반영해야 한다.

- **방문**: 1인 NPC는 즉시 승인하므로 대기 창이 짧게 표시되거나 취소를 누르기 전에 닫힐 수 있다. 수동 취소 검증은 응답을 보류할 수 있는 온라인 호스트 또는 명시적 테스트 지연이 필요하다. 자동 승인과 취소를 같은 1인 즉시 응답 조건에서 모두 필수 클릭으로 요구하면 재현성이 없다. 실제 전술 맵 진입은 현재 TODO이므로 승인 메시지를 맵 로딩 성공으로 판정하지 않는다.
- **영지 양도**: 디버그 액션은 로컬 Execute를 직접 호출한다. 정상적인 Offer→Pending→Commit 경로가 아니어서 서버의 `Standalone Fief Transfer Confirmed` 로그만으로 소유권 커밋을 검증할 수 없다. 양도 테스트는 사본 세이브에서 시행하고 서버에 등록된 영지로 전체 거래 경로를 따로 검증해야 한다.
- **안개/국경**: 토글은 선택 타일의 비플레이어 월드 객체 가시성을 검사하는 기능이다. 지형 전체가 안개로 덮이는 효과를 기대하지 않는다. History는 현재 실제 객체를 숨기고 스냅샷 잔상 렌더러는 연결돼 있지 않다. 1·2칸 차단과 3칸에서 이 모드의 국경 메시지가 발생하지 않는 대조 검사가 필요하다. 바닐라 정착 제한으로 버튼부터 비활성화되는 경우는 이 패치의 통과 증거가 아니다.

## 증거와 한계

- `build-round2.log`: 솔루션 빌드 결과.
- `round2-results.log`: 실제 서버 관리자/소켓 테스트 및 원본 UI 소스의 테스트 대역 기반 로직 검사. REPRO PASS는 결함 재현 성공이며 제품 합격이 아니다.
- `engine-round2.log`: PlanetTile.Valid/Layer 및 이웃 조회의 실제 설치 엔진 IL.
- `Round2Checks.cs`, `Round2Checks.csproj`: 재현 러너. UI 렌더링이나 Unity 콜백 실행은 검증하지 않았다. 무수신 확인은 각 300ms 관측이며 무한 시간 보장을 의미하지 않는다.

테스트 명령: `dotnet run --project QA-Phase3/Round2Checks.csproj -p:NuGetAudit=false --ignore-failed-sources`
