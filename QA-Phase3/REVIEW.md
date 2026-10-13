# Phase 3 사전 코드 리뷰 — 2026-10-01

판정: **Dev 사전 수정 필요**. 화면 제어 및 게임 실행 없이 소스 정적 분석, 설치된 RimWorld 1.6 엔진 IL 대조, 터미널 단위/루프백 통신 검증만 수행했다. 제품 소스 수정 및 커밋은 하지 않았다.

## 검증 범위 및 결과

- 솔루션 빌드: 경고 0, 오류 0 (`dotnet build WarEconomyMod/WarEconomy.slnx --no-restore -m:1`).
- 배포 `1.6/Assemblies`의 Client/Common DLL은 현재 빌드 DLL과 SHA256 일치.
- 배포 Client DLL의 디버그 액션 3개는 실제 1.6 `LudeonTK.DebugActionAttribute`에 정상 바인딩. public static void, 무인자, Playing/PlayingOnMap 설정 확인. 실제 메뉴 표시 자체는 검증하지 않았다.
- `TestFiefTransfer`는 CurrentMap null을 검사한다. 현재 대상 코드에서 `UI.MouseCell()`은 사용하지 않는다. 엔진의 반환형은 nullable이 아닌 IntVec3이다.
- `VisitPatches`는 원본 GetGizmos 결과를 순서대로 yield한 뒤 버튼을 추가한다. 원본 컬렉션을 직접 수정하는 코드는 없다.
- 양도 루프는 ToList 스냅샷을 사용하고 폰의 사망/파괴/맵 이탈을 재검사한다. 직접적인 원본 컬렉션 열거 중 변경 위험은 완화됐으나 아래 결함으로 전체 원자성은 통과하지 못했다.

| 터미널 검증 | 결과 |
|---|---|
| 실제 Common DLL의 양도 결과 패킷 성공/실패 직렬화 왕복 | 2/2 통과: 헤더, 길이, Unicode, 수량, 성공 플래그 보존 |
| 실제 Server DLL, 단일 클라이언트 NPC 자동 승인 | 통과 |
| 방문 취소 패킷 상대 전달 | 통과 |
| 양도 실패 후 소유권 불일치 | 재현: 실패 보고 후에도 new-lord/new-faction 유지 |
| 취소한 방문창 정적 참조 잔존 | 재현 |
| 취소 후 늦은 승인 메시지 처리 | 재현: 닫힘 2회, 승인 메시지 발생, 상태 Pending 유지 |
| NPC 요청을 무관한 두 번째 클라이언트에 전달 | 재현 |
| 서버가 취소 이후 승인 응답 전달 | 재현 |

UI 흐름 테스트는 원본 Dialog_VisitWait.cs를 컴파일하고 Window/메시지/네트워크 경계에 테스트 대역을 사용했다. 게임 렌더링이나 Window 엔진 동작을 검증한 것은 아니다. 서버 통신은 실제 Server DLL을 임시 포트 61492에서 실행했다. 기존 7777 서버에는 요청하지 않았다. 테스트 서버는 종료했다. 테스트 프로젝트 최초 복원에는 NuGet 취약성 정보 접근 실패 NU1900 경고가 있었으나 컴파일과 실행은 완료됐다.

## 발견 사항

### 1. High — 양도 마지막 단계의 확정적 null 역참조

- 위치: `WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:115`
- `UpdateRegistryForPawn(null)`을 호출한다. 설치 엔진 IL은 DeRegisterPawn 호출 후 인자에 대해 `get_Spawned()`를 무조건 호출한다. null을 전체 레지스트리 갱신 신호로 처리하는 API가 아니다. 해당 줄까지 도달하는 양도는 예외로 끝난다.
- 폰/건물/맵 부모의 세력은 이미 변경된 상태이며, 외부 catch에서 실패 결과만 보낸다.
- 추가 위치: `WarEconomyMod/Source/Client/Debug/DebugActions_WarEconomy.cs:84`. 실행기가 실패를 내부에서 처리하고 반환해도 디버그 액션은 성공 메시지를 무조건 출력한다.
- 권장: 실제 Pawn을 받는 엔진 API 계약에 맞춰 갱신하고, 실행 결과를 호출자에 전달하여 성공 시에만 완료 메시지를 출력한다.
- 근거: `engine-inspection.log`의 UpdateRegistryForPawn IL.

### 2. High — 실패 결과가 소유권 확정 상태를 바로잡지 못함

- 위치: `WarEconomyMod/Source/Server/Managers/FeudalManager.cs:84`, `:104`.
- 실행 패킷 발송 전 서버 소유권을 변경하며, Result.Success=false는 로그만 남긴다. 실제 DLL 테스트에서 실패 회신 후에도 새 영주/세력이 그대로 남았다. 클라이언트에 맵이 없어 양도하지 못하는 경우에도 서버만 양도를 확정한다.
- 클라이언트 추가 위치: `WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:77`, `:94`, `:120`. 개별 폰 오류를 기록하고 계속하므로 115행 수정만으로도 부분 실패를 성공으로 보고할 위험이 남는다. 이미 변경한 클라이언트 상태도 복구하지 않는다.
- 권장: 거래 ID와 상태를 관리하고, 필요한 클라이언트 결과를 검증한 뒤 소유권을 확정한다. 부분 실패 시 복구/재동기화 절차와 폰별 실패 집계를 정의한다. 단순 서버 롤백만으로 이미 변경된 클라이언트가 복구되지는 않는다.
- Result DTO 직렬화 자체는 정상이다. 결함은 결과의 상태 반영이다.

### 3. Medium — 방문 취소 후 늦은 승인을 유효하게 처리

- 위치: `WarEconomyMod/Source/Client/UI/Dialog_VisitWait.cs:50`, `:59`; `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:158`, `:167`.
- CancelRequest는 창만 닫고 정적 참조/RequestData.Status를 정리하지 않는다. 이후 같은 ID의 승인이 도착하면 승인 메시지가 발생한다. 응답이 오지 않으면 닫힌 창 참조도 남는다.
- 서버 역시 요청 상태를 저장하지 않고 취소 및 응답을 전달한다. 실제 소켓에서 취소가 전달된 뒤 보낸 승인이 방문자에게 전달되는 것을 확인했다.
- 권장: 서버에 Pending→Cancelled/Accepted의 단일 전이를 두고 요청자·호스트를 검증한다. 클라이언트도 종료 경로에서 참조와 상태를 정리하고 취소/만료된 요청의 응답을 무시한다.

### 4. Medium — NPC 방문 처리가 다른 접속자 존재 여부에 의존

- 위치: `WarEconomyMod/Source/Client/Patches/VisitPatches.cs:46`; `WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:125`.
- 클라이언트는 HostPlayerId를 비워 보내고 서버의 소유자 판정을 기대하지만 서버는 다른 모든 세션에 전달한다. 다른 세션이 없을 때만 자동 승인한다.
- 테스트에서 동일 NPC 정착지 요청이 단일 접속 시 자동 승인되고, 무관한 두 번째 클라이언트 접속 후에는 그 클라이언트에 전달됐다. 해당 클라이언트의 승인도 서버가 받아 전달한다.
- 권장: 정착지 ID로 소유자를 해석해 해당 호스트에만 전달한다. NPC 여부와 테스트 자동 승인 설정을 명시적으로 분리하고, 오프라인 소유자/없는 정착지에는 종료 가능한 응답을 보낸다.

### 5. Medium — 근사 거리를 정확한 2칸 국경으로 사용

- 위치: `WarEconomyMod/Source/Client/Patches/FogOfWarPatches.cs:123`, `:138`.
- 실제 엔진 ApproxDistanceInTiles는 구면 거리와 평균 타일 크기를 사용한다. 인접 타일 연결을 따라 이동한 횟수가 아니므로 `<=2`는 정확한 2칸 이내 판정을 보장하지 않는다. 경계 타일의 오판정 가능성이 있다. 특정 월드의 오판정 타일을 게임에서 실측한 것은 아니다.
- 권장: 같은 레이어의 타일 이웃을 최대 깊이 2로 탐색하거나 엔진의 그래프 거리 기능을 사용한다. 0/1/2/3칸 경계 사례를 검증한다.
- 인덱스 관련: 이 호출 경로의 엔진 GetTileCenter(int)는 범위를 검사하고 오류 로그 후 Vector3.zero를 반환한다. 따라서 이 경로에서 즉시 IndexOutOfRangeException이 난다고 판단하지 않았다. 모드 자체는 음수/범위 밖 타일을 검증하지 않아 잘못된 거리/로그가 발생할 수 있다.

### 6. Medium — RimWorld 1.6 타일 레이어 정보 손실

- 위치: `WarEconomyMod/Source/Client/Patches/FogOfWarPatches.cs:161`, `:113`, `:138`.
- Caravan.Tile(PlanetTile)을 int로 바꾸면서 layerId를 버린다. 실제 엔진의 int→PlanetTile 변환은 layerId=0으로 복원한다. 레이어가 다른 정착지와도 같은 타일 인덱스를 비교한다. PlanetLayer의 거리 계산은 두 인자의 레이어 일치를 검사하지 않는다.
- 다중 레이어 환경에서 서로 다른 레이어를 동일 위치로 취급하거나 잘못된 레이어의 인덱스로 거리 판정을 할 수 있다.
- 권장: PlanetTile 또는 (layerId,tileId)를 끝까지 보존하고 동일 레이어 여부와 각 레이어 인덱스 범위를 확인한다. 지표만 지원한다면 명시적으로 지표 외 입력을 제외한다.

### 7. Medium — 서버 정착지 국경 목록 동기화 연결 부재

- 위치: `WarEconomyMod/Source/Client/Patches/FogOfWarPatches.cs:111`, `:118`.
- KnownSettlements는 빈 목록으로 선언되며 현재 Source 전체에서 이를 채우는 코드가 없다. 따라서 서버 동기화 정착지 검사는 실제로 비어 있고 로컬 월드 정착지만 검사한다. 로컬에 표현되지 않은 원격 플레이어 영지의 국경은 차단할 수 없다.
- 권장: 서버 정착지 스냅샷 수신과 메인 스레드 목록 교체를 연결하고, 로컬 월드 객체가 없는 원격 영지에 대해서도 국경 테스트를 추가한다.

## 재검증 게이트

우선 1·2번을 수정하여 양도 성공/실패 상태를 신뢰할 수 있게 만든 뒤, 취소 경쟁 조건 및 호스트 라우팅을 재검증해야 한다. 국경은 거리 정의와 지원 레이어를 확정하고 구현에 반영해야 한다. 현재는 사용자 인게임 테스트 진행을 승인하지 않는다. 승인 조건부 수동 체크리스트는 수정 후 재검증 통과 시 제공한다.

증거 파일: `unit-results.log`, `engine-inspection.log`. 재현 러너: `Phase3Checks.csproj`, `Checks.cs`, `UIStubs.cs`. 로그의 REPRO 항목 PASS는 결함 재현 성공을 뜻하며 제품 합격을 뜻하지 않는다.
