# Phase 2 최종 재검증 — 2026-09-30

판정: 추가 이슈. 소스 수정/커밋 없음. QA 러너만 수정.

## 검증 대상 및 범위
- 실제 RimWorld 1.6.4871 rev591, Harmony 2.4.1.0 + Core + WarEconomy 활성 구성.
- Client DLL SHA256: 76ACAE8C8CB77AB24819BC418F8F05CC30570A503EEB4500F174F44FE00EBE5C (배포/빌드 일치).
- Server DLL SHA256: 14F5E654ACC3E46616BC22CE1CD11F86F2CF911CD46EB95C95761B94B031D1B1.
- 처음 7777 포트는 10061 접속 거부. QA에서 최신 Server.exe를 가동한 뒤 실기 테스트 진행.
- 틱 테스트는 원본 소스와 엔진 대역, 송신은 실제 서버 DLL 및 루프백 TCP 사용.
- 큐 과부하는 재현성을 위해 송신 소비 시작을 지연하고 틱/검증 패킷을 병렬 인큐한 후 실제 소켓으로 전량 읽음. 영지/시장/외교 헤더 45/60/21과 고유 번호를 가진 테스트 페이로드 사용. 실제 게임 내 거래 처리 테스트와는 구분.

## 회귀
- About.xml XML 파싱 성공, packageId WarEconomy.HybridMultiplayer.
- 실제 모드 UI에서 정식 ID wareconomy.hybridmultiplayer 확인. ModsConfig.xml도 정식 ID 활성화 확인.
- 새 로드의 XML 오류, MissingMethodException, HarmonyException 관찰 없음. Harmony 패치 성공 로그 확인. 한국어 번역 경고 36건은 남음.
- 60/120/144/240 FPS: 각 180틱/초.
- 1초 지연 + 60 FPS 1초: 기대 360틱 / 실행 360틱 PASS.
- 틱 100000 + Reliable 300: 300/300 수신, 영지/시장/외교 각각 100개 PASS.
- 틱 100000 + Reliable 2100: 2048/2100 수신, 52개 유실, 연결 유지 FAIL.

## 실제 UI와 접속
- 메인 메뉴 접속 버튼 2개(기본 메뉴 및 오른쪽 링크 열). 중복 제거 FAIL.
- 첫 접속: 녹색 연결 표시 및 서버 [Auth] Player cacao659 registered. 확인 PASS.
- 접속 성공 직후에는 Disconnect 버튼이 보이지 않음 FAIL.
- 창을 닫고 다시 열면 Disconnect 버튼 표시됨.
- 버튼 클릭: 미연결 및 종료 성공 메시지와 Connect 버튼 복귀, 서버 graceful disconnect 로그 확인 PASS.
- 이어서 Connect 클릭: 신규 세션 ed4f4dc9, [Auth] 재등록 로그와 녹색 연결 표시 확인 PASS.
- 테스트 종료 시 게임/서버는 실행 및 재연결 상태로 유지.

## Dev 수정 요청
1. High — Source/Server/Network/ServerClientSession.cs:112
   FullMode.Wait여도 TryWrite는 큐가 가득 차면 false를 반환한다. 반환값을 무시해 유실 불가 패킷이 조용히 소실된다. 실패를 명시적으로 처리하고 제한된 비동기 대기/보존 또는 연결 종료 및 재동기화 정책을 구현해야 한다. 틱 스레드에서 동기 대기는 금지.
2. Medium — Source/Client/Patches/MainMenuPatches.cs:41,45
   optList.Exists는 각 리스트 내부 중복만 막는다. 기본 메뉴와 링크 열은 서로 다른 리스트라 두 곳 모두 삽입된다. NewColony가 없는 리스트에서는 삽입하지 않는 등 대상을 제한해야 한다.
3. Medium — Source/Client/UI/Dialog_ConnectServer.cs:19 및 상태/버튼 배치
   350 높이에 세션/성공 메시지가 추가되면 Disconnect가 표시되지 않는다. 실제 창 내부 높이에 맞게 상태 영역과 고정 하단 버튼을 배치하거나 충분한 높이/스크롤을 확보해야 한다.

증거: final-regression.txt, final-menu.png, final-connected.png, final-disconnected.png, final-server-observed.log, final-Player.log, final-ModsConfig.xml.
