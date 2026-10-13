# Phase 2 — RimWorld 1.6 실기 검증 결과

최종 판정: 추가 이슈 발생. 실제 게임의 TCP 연결은 성공했으나 전체 승인 불가.
프로젝트 소스 수정/커밋 없음. 별도 QA 테스트 러너만 갱신함.

## 회귀 결과
- 솔루션 빌드 경고 0, 오류 0.
- 배포 1.6/Assemblies/WarEconomy.Client.dll과 빌드 DLL SHA256 일치: 8773DFCCE18E412066DECAA38A63382913537D01B527F32C3EEDE267228F173E
- 60/120/144/240 FPS: 각각 180틱 처리.
- 원본 ClientWorldTickManager.cs + 엔진 대역 테스트: 1초 지연 후 정상 60 FPS 1초, 기대 360틱 / 실제 240틱. 60틱 누적 상한에서 120틱 소실.
- 실제 Server DLL의 BoundedChannel: 1100개 입력 후 큐 1024개, 첫 잔존 틱 번호 76. 연결은 유지됨. DropOldest에 의한 76개 유실 확인.
- 지속 포화 감지 후 연결 종료 확인.
- 실제 TCP 소켓의 수신 정지 테스트: 5.03초 후 Socket write timed out, 연결 종료 확인.
- 시장 동시 거래 80만 건은 3회 모두 기대 재고 800100 일치.

## 실제 게임
- RimWorld 1.6.4871 rev591 실행, 모드 목록에서 WarEconomyMod 활성화 및 적용 후 재시작.
- About.xml 25행 및 27행의 이스케이프되지 않은 &로 XML 파싱 실패. UI에 Anonymous/지원 버전 없음 표시. 활성화 설정에 anonymous189.wareconomymod 저장됨.
- 최초 기존 Multiplayer 로드에서는 Mono.Cecil 관련 TypeLoadException 발생. 사용자가 Multiplayer를 비활성화한 후 재시작된 구성에서는 WarEconomyMod Harmony 초기화 성공 확인.
- [WarEconomyMod] Initialized and Harmony patches applied successfully.
- 활성화 후 WarEconomyMod의 MissingMethodException/HarmonyException은 관찰되지 않음. About.xml 오류는 지속.
- War-Economy 멀티 접속 버튼이 메인 메뉴와 우측 링크 열 두 군데에 중복 렌더링됨.
- 접속 창에서 IP 127.0.0.1, 포트 7777, 닉네임 QA_Phase2_16 입력 후 연결 성공.
- 녹색 연결됨 라벨 및 접속 성공 메시지 확인. 성공 메시지 추가 후 연결 끊기 버튼은 현재 창에서 보이지 않음.
- 게임 로그: [NetworkClient] Connected to Dedicated Server at 127.0.0.1:7777 (Session: 1fd44dc7a0bc4d649bccc03b43974fc6)
- 서버 로그: [TcpNetworkServer] Client connected: f80cb370. Total clients: 1
- 서버 상태: [Status] Server World Tick: 67044, Clients Active: True
- 연결 시 별도 Handshake 패킷 송신 코드 없음. TCP 연결 성공과 플레이어 ID 등록/프로토콜 핸드셰이크 성공은 구분해야 함.
- 테스트 종료 시 게임과 서버를 실행 및 연결 상태로 유지. 정착지 생성/로드는 이번 지정 절차에 포함되지 않아 수행하지 않음.

## 수정 요청
1. High: ClientWorldTickManager.cs:80 — 60틱 상한으로 누적 시간을 버리지 말고 제한된 프레임 예산으로 잔여 틱을 처리하거나 권위 상태 재동기화 정책 구현.
2. High: ServerClientSession.cs:32 — 모든 패킷에 DropOldest를 적용하면 영지 양도/전쟁 이벤트도 무통보 유실 가능. 최신 상태 병합 가능 패킷과 유실 불가 명령을 분리하고 포화 시 재동기화/연결 종료 처리.
3. High: About/About.xml:25,27 — &를 &amp;로 이스케이프. XML 검증을 배포 검사에 추가. 수정 후 공식 packageId로 모드 활성화 재확인 필요.
4. Medium: Patches/MainMenuPatches.cs:37 — 메뉴 플래그만으로는 우측 링크 목록도 대상이 됨. 기본 메뉴 목록에만 버튼 삽입.
5. Medium: UI/Dialog_ConnectServer.cs:19 — 성공 상태 메시지가 추가돼도 버튼이 창 내부에 남도록 높이/스크롤 레이아웃 개선.
6. 프로토콜: 연결 완료와 별개로 Handshake/플레이어 등록 요청·응답을 구현하고 서버 로그로 검증 필요.
