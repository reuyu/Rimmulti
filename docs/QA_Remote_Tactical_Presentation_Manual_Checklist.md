# Remote Tactical Presentation — 사용자 수동 검증 체크리스트

Work Package: WP-QA-REMOTE-TACTICAL-PRESENTATION-01

사용자 요청에 따라 QA의 Computer Use/마우스/키보드 조작은 중단한다. QA는 터미널·상태·로그를 검증하고, 실제 화면의 판단은 사용자가 수행한다. 사용자 실기 관찰과 QA 독립 로그 증거는 최종 보고서에서 별도로 표기한다.

## 준비된 테스트 환경

- 사용자 PC에서 직접 **Start_Remote_Tactical_Manual_QA.cmd**를 더블클릭해 실행한다. 위치는 `C:\Users\user\Desktop\RimMulti`다. 이 실행 파일은 별도 ManualSession3 profile로 Worker와 일반 그래픽 client를 시작한다. client에는 `-batchmode` 및 `-nographics`가 없다.
- Worker는 loopback **127.0.0.1:29800**을 사용한다. PID는 실행 후 ManualSession3/launch-pair.json에 기록된다. 이전 QA 자동 실행 PID16120/22040 및4904/20172는 모두 종료했다. 사용자에게 창이 보이지 않았으므로 이전 process 존재를 실제 UI 확인으로 인정하지 않는다.
- 테스트 클라이언트는 frozen RemotePresentation PoC이며 격리 save/profile을 사용한다. 기존 사용자 save를 열거나 덮어쓰지 않는다.
- 클라이언트 control port29801 및 QA observer port31701은 터미널 측정용이다. 사용자는 입력할 필요가 없다.
- **기존 메인 메뉴의 War-Economy 멀티 접속 버튼/7777 서버는 이번 PoC 경로가 아니다.** 준비된 RimWorld 창에서 진행한다.
- 앞선 터미널 session에서는 Map2개/Pawn51개 로드와 연결 응답을 확인했다. 새 launcher도 이를 대기하며 `Manual test ready`를 출력한다. 이것만으로 실제 화면 정상 렌더링을 승인한 것은 아니다.
- 대상 Pawn: **Strange / Human302**. 외국 참가자 Pawn: **Nick / Human305**, **Esme / Human308**.
- 새 ManualSession3는 generation1이다. static Player_A_Token은 PoC fixture token이며 실제 인증을 뜻하지 않는다. 앞선 터미널 시험의 generation2와 구분한다.
- 사용자 launcher의 process는 수동 시험을 위해 계속 실행된다. 검증이 끝났다고 알려주면 해당 QA process만 종료한다. 같은 launcher를 중복 실행하지 않는다.

## 검증 순서

각 단계에서 `PASS / FAIL / 확인 불가`를 기록한다. 붉은 로그가 이미 열려 있으면 기존 오류와 이번 행동 후 새 오류를 구분해 기록하고 로그 창을 닫는다. 기존 오류가 있어도 없었던 것으로 기록하지 않는다.

### 1. 실제 맵 렌더링

1. 작업 표시줄에서 준비된 **RimWorld** 창으로 전환한다.
2. 지형, 건물, Pawn이 실제 맵에 보이는지 확인한다.
3. 화면이 검거나 로딩 화면에 멈춰 있거나, 맵 대신 오류 창만 지속되면 FAIL로 기록한다.

기대: 맵과 객체가 정상적으로 보이며 화면을 조작할 수 있다. **Pawn이 가만히 있는 것만으로 FAIL은 아니다.** 이 PoC는 자동 simulation tick이 억제돼 있다.

### 2. 카메라 이동 및 확대/축소

1. 맵 위에서 방향키/WASD 또는 평소 사용하는 카메라 이동 조작을 한다.
2. 마우스 휠로 확대하고 다시 축소한다.

기대: 카메라가 이동하고 배율이 바뀌며 지형/Pawn이 계속 그려진다. 검은 화면, 렌더링 깨짐, 반복 예외가 없어야 한다.

### 3. Pawn 선택과 inspect pane

1. 상단 colonist bar에서 **Strange**를 클릭한다. 찾기 어려우면 다른 colonist를 선택해 이름을 확인한 후 Strange로 바꾼다.
2. 선택 표시와 화면 하단 inspect pane을 확인한다.
3. 이름·상태·장비 등 정보가 표시되는지 확인한다. 가능하면 건강/장비 탭도 한 번 연다.

기대: 클릭한 Pawn과 표시된 정보가 일치한다. 정보 창이 비거나 NullReferenceException 등이 반복되면 FAIL이다.

### 4. 실제 gizmo 표시와 징집 클릭 — 핵심

1. Strange를 선택한 상태에서 하단 **징집 / Draft** 버튼을 찾는다.
2. 현재 Draft 상태를 기록한다.
3. 버튼을 **한 번만** 클릭한다.
4. 버튼 표시/아이콘과 Pawn 상태가 바뀌는지 기록한다. 새 붉은 오류도 기록한다.

정상 remote-intent 경로의 기대: 실제 GUI 클릭이 client intent로 전환되고, Worker가 Human302의 권한을 검증·실행한 다음 authoritative 상태로 client가 갱신된다.

**화면의 Draft 상태만 바뀌면 전체 PASS가 아니다.** QA가 해당 시점의 `GIZMO_PROCESS → RPC → Worker response` 및 Worker Draft 상태를 대조한다.

현재 frozen source에는 이 GUI interception이 구현돼 있다는 근거가 없다. 따라서 이 단계는 그 결함을 실기로 확인하는 시험이기도 하다. QA는 이를 대신 고치는 패치를 추가하지 않았다.

### 5. 실제 우클릭 이동

1. Strange가 Draft 상태라면 가까운 이동 가능한 바닥을 우클릭한다.
2. 이동 메뉴가 뜨면 이동 항목을 한 번 선택한다. 바로 이동 지시가 생기는 UI라면 그 결과를 기록한다.
3. 메뉴 표시, 목적지 표시, Pawn 움직임 유무를 기록한다.

기대: 명령이 Worker로 전달되고 native Job/이동이 실행된 뒤 client에 authoritative 위치가 반영된다. **client tick이 정지해 있으므로 “멈춰 있는 로컬 Job만 설정됨”은 성공이 아니다.** 움직이지 않았다면 그대로 FAIL/확인 불가로 기록한다.

### 6. 보정 후 UI/reference 안정성

이 단계는 QA의 추가 터미널 보정과 동기화해서 수행한다.

1. Strange를 선택한 채로 `보정 테스트 준비됨`이라고 알려준다.
2. QA가 client mirror 위치를 시험적으로 바꾸고 Worker snapshot으로 복구한다. QA는 카메라나 마우스를 조작하지 않는다.
3. 복구 후 Pawn이 하나만 보이는지, 선택 표시가 같은 Pawn을 가리키는지, inspect pane이 유지되는지 확인한다.
4. 선택을 해제하고 Strange를 다시 선택한다.

기대: 렌더링/UI가 멈추거나 깨지지 않고, 중복 Pawn/유령 선택/다른 Pawn 정보가 없어야 한다. Worker state 및 Thing grid 중복은 QA가 별도로 측정한다.

### 7. 에러 구분

검증 시작부터 있던 오류와 Draft/우클릭/보정 후 추가된 오류를 구분한다. 오류 문구를 복사할 수 있으면 결과와 함께 제공한다. 화면 캡처는 가능하면 맵·선택 정보·gizmo 상태를 포함한다.

Dialog_Trade의 실제 거래 완료는 이 체크리스트의 필수 사용자 행동이 아니다. 이번 frozen PoC에는 Server domain/economic commit 연결이 없으므로 단순 로컬 거래 성공을 multiplayer 거래 성공으로 판정할 수 없다. 해당 경로는 QA가 engine/source authority boundary를 별도로 검토한다.

## 결과 전달 양식

아래를 복사해 결과를 보내면 된다.

```text
1. 맵 렌더링: PASS / FAIL / 확인 불가
2. 카메라 이동·줌: PASS / FAIL / 확인 불가
3. Strange 선택·inspect pane: PASS / FAIL / 확인 불가
4. Draft 버튼 표시: PASS / FAIL / 확인 불가
   클릭 전 상태:
   클릭 후 상태:
5. 우클릭 이동:
   메뉴/목적지 표시:
   Pawn 실제 움직임:
6. 보정 후 렌더링·선택·재선택: 대기 / PASS / FAIL
7. 기존 오류 / 새 오류:
8. 검증 완료 또는 보정 테스트 준비됨:
```

수동 결과 및 독립 로그 대조가 끝나기 전에는 그래픽 presentation/control gate를 통과로 기록하지 않는다. Candidate C도 PROVISIONAL을 유지한다.
