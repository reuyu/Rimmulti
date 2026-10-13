# Phase 3 5차 사전 리뷰 — 2026-10-01

**판정: 반려. 세력 복구 실패 보고는 개선됐으나, 소유권/설정 복원 실패를 완전 복구로 판정하는 경로가 남았다. 최종 인게임 수동 체크리스트는 보류한다.**

## 검증 결과

- 화면 제어/게임 실행/제품 코드 수정 없음. QA 러너와 보고서만 추가했다.
- 솔루션 빌드: 경고 0 / 오류 0.
- 현재 Round4Checks.cs 재실행: **23/23 통과**.
- 배포 1.6 Client DLL과 현재 빌드 Client DLL SHA256 일치.
- 원 세력으로 복구하지 못했을 때 불완전 복구 UI 및 ErrorMessage 분기: 기존 테스트에서 통과.
- 스냅샷의 허용구역/마스터 및 테스트용 Claimed 필드 복원: 기존 테스트에서 통과.
- 설치된 실제 RimWorld 1.6 Pawn_Ownership 어셈블리에서 OwnedBed/AssignedGrave/AssignedThrone/AssignedMeditationSpot/AssignedDeathrestCasket 프로퍼티와 Claim 메서드 이름을 대조했다. 이름은 일치하며 Claim 메서드들의 반환형은 bool이다.

## 남은 결함 — High

**위치:** `WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:229`, `:235`, `:239`, `:283`, `:362`, `:371`.

TryInvokeClaim은 Claim 메서드의 반환값을 버리고, 예외가 나면 경고만 기록한다. 설정 복원의 예외 역시 내부에서 삼킨다. RollbackTransfer는 이 결과를 받지 않고, 마지막에 세력만 비교하여 true를 반환한다. 따라서 세력이 복구됐지만 침대/설정이 복구되지 않은 경우에도 UI는 “이전 상태로 롤백되었습니다”를 출력하고 패킷에는 불완전 복구 표시가 없다.

실제 엔진 IL상 ClaimBedIfNonMedical은 의료용 침대인 경우 false로 반환하며 소유권을 복구하지 않는다. 이미 소유한 경우에도 false이므로 **false를 무조건 실패로 해석하는 것 역시 부정확하다. 최종 소유권 상태를 비교해야 한다.**

독립 검증은 테스트용 Claimed 필드가 없는, 실제 API 형태의 OwnedBed 프로퍼티와 bool ClaimBedIfNonMedical을 가진 대역을 사용했다. 원본 실행기는 수정하지 않았다.

| 실패 주입/대조 조건 | 결과 |
|---|---|
| 작업 초기화 실패 후 Claim 성공 | 세력과 이전 침대 복구 통과 |
| 작업 초기화 실패 후 Claim 거절(false), 침대 미복원 | 세력만 복구, 침대 null인데 UI는 완전 복구 보고 — 재현 |
| 작업 초기화 실패 후 Claim 예외 | 세력만 복구, 침대 null인데 UI는 완전 복구 보고 — 재현 |
| 위 두 실패의 결과 패킷 | 모두 Incomplete rollback 표시 누락 — 재현 |

실제 Unity에서 의료용 침대 전환이나 콜백 예외를 유발한 실기 테스트는 아니다. 엔진 API 대조와 원본 실행기의 실패 주입 제어 흐름 검증이다.

### 기존 테스트가 이를 놓치는 이유

기존 소유권 테스트는 R3EngineStubs.Ownership.Claimed bool이 true로 돌아오는지만 검사한다. 제품 코드에도 이 테스트 전용 필드를 직접 복원하는 경로가 추가돼 있다. 이 경로는 실제 Pawn_Ownership의 침대 Claim 성공 여부를 검증하지 않는다.

### 필요한 수정과 재검증 조건

1. RestorePawnSnapshot이 복구 결과를 반환하고, 누락된 메서드/예외/복원 후 상태 불일치를 상위 결과에 반영한다.
2. 이전 침대·무덤·왕좌·명상 위치·죽음안식 관·허용구역·마스터와 최종 상태를 비교한다. 파괴되어 복원 불가능한 대상은 명시적인 불완전 복구로 분류한다.
3. 하나라도 불완전하면 완료 문구 대신 불완전 복구 UI와 서버 결과를 사용한다. 복구 오류 원인도 보존한다.
4. 기존 Claimed 필드 테스트에 더해 실제 엔진 API 형태의 Claim 성공/이미 복원됨/거절/예외 및 설정 복원 예외를 검증한다. 세력이 정상이라는 이유만으로 전체 복구를 통과시키지 않는다.

## 서버 보고에 관한 확인

현재 치명적 상태 표시는 PKT_FiefTransferResult의 전용 bool/enum 필드가 아니라 ErrorMessage의 `Incomplete rollback: resync required` 문자열이다. FeudalManager는 이를 일반 실패 로그에 포함하며, 이 문자열에 따른 별도 재동기화 동작은 구현돼 있지 않다. 따라서 현 상태를 “치명적 플래그에 따른 자동 복구 완료”로 안내하면 안 된다.

## 증거

- `build-round5-review.log`: 빌드.
- `round5-devsuite-review.log`: Dev 테스트 23/23.
- `round5-engine-ownership.log`, `round5-engine-claim-il.log`: 실제 설치 엔진 API 및 Claim 동작 대조.
- `round5-independent-results.log`: 성공 대조 1종, 실패 주입 2종.
- `R5Independent.csproj`, `R5Independent.cs`, `R5EngineStubs.cs`: 독립 QA 러너. REPRO PASS는 결함 재현 성공을 의미한다.

기존 7777 서버는 사용하지 않았다. Dev 스위트가 생성한 임시 포트 서버는 정상 종료됐다.
