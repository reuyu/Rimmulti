# A_ENGINE_GATE05_R29_STARTUP_PAIR_REPORT_20261012.md

- **과업 패키지**: `WP_ENGINE_GATE05_R29_STARTUP_PAIR`
- **개정/엔벨로프**: `GATE05-R29-STARTUP-PAIR` / `envelope32`
- **디스패치 ID**: `WE-A-ENGINE-GATE05-R29-STARTUP-PAIR-20261012-DIRECT-46f60e2a`
- **수행 에이전트**: Antigravity Development Agent A
- **판정 (E1 Verdict)**: `IMPLEMENTED_STARTUP_PAIR_PASS_NATIVE_UNTESTED`
- **작성 일시**: 2026-10-12 09:30:00 UTC+9
- **통제 계약**: [MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md)
- **인가 범위**: [MASTER_R29_AUTHORIZED_SOURCE_SCOPE.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R29-STARTUP-PAIR-20261012-DIRECT-46f60e2a/MASTER_R29_AUTHORIZED_SOURCE_SCOPE.json)

---

## 1. 개요 및 Master R28 정정 지침 수용

Master의 R28 심사 정정([MASTER_REVIEW_ENGINE_GATE05_R28_DUAL_OPERATOR_ROUTE_20261012.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/MASTER_REVIEW_ENGINE_GATE05_R28_DUAL_OPERATOR_ROUTE_20261012.md)) 및 controlling contract에 따라, 본 과업은 다음 네 가지 거부 항목을 엄격히 배제하고 지정된 6개 소스 구간 및 신규 퍼블리셔만을 구현했습니다:
1. **전역 자식 authority 슬롯 거부**: 프로세스 전역 public getter/setter나 전역 자식 등록 슬롯을 일체 생성하지 않음.
2. **미관측 동기 Awake 가정 거부**: Unity의 `AddComponent` 직후 즉시 `Awake`가 동기 실행된다거나 비활성 오브젝트 가정을 두지 않고, 부트스트랩 시 생성된 특정 `GameObject` 인스턴스 및 부모 영수증과 결속된 1회용 대기 핸드오프 슬롯을 통해 인스턴스 `Awake` 진입 시점에 획득하도록 함.
3. **CLI 비밀/논스 전달 방식 거부**: `--task-file`, `--nonce` 등 미검증 CLI 플래그를 추가하지 않으며, CLI 캐리어는 비공개 파일 절대 경로(`-operatorpairfile`) 및 기대 해시(`-operatorpairsha`)의 단일 2-part 토큰만을 사용.
4. **Task 라이프사이클 및 프로세스 기동 보류**: `ValidatorTask` 소비 플래그 변경, `RevokeReadiness`, OS `Process.Start` 호출을 일체 배제하고 `M05_NOT_ADMITTED` 보류 가드로 차단.

---

## 2. 신규 실제 오퍼레이터 페어 퍼블리셔 구현 (`publish_operator_pair.py`)

- **파일 위치**: `scratch\OperatorStartupPairR29\publish_operator_pair.py`
- **성격**: 표준 라이브러리 기반 독립형 플랜 전용(plan-only) 파이썬 유틸리티 (서브프로세스/네이티브 프로세스 기동 코드 전무).
- **입력 및 검증**:
  - 부모 설정 14필드 + 승인 선언 7필드 및 자식 설정 14필드 + 승인 선언 7필드를 독립 공급받음 (부모 역할 변경을 통한 자식 파생 금지).
  - 디스크 상의 실제 부모/자식 원시 설정 바이트를 재해시(SHA-256)하여 선언된 `expectedConfigSha256` 및 경로 관계를 사전 검증.
  - 역할 일관성 강제 검증: 부모 역할은 `SIMULATION`, 자식 역할은 `READ_ONLY`.
- **출력 번들 규격**:
  - 최상위 4개 필드: `schemaVersion` (`we-operator-startup-pair/v1`), `operatorPairId` (원문 보존, 트림/정규화 금지), `parentDeclaration`, `childDeclaration`.
  - 디스크립터 7개 필드 순서: `originId`, `expectedConfigId`, `expectedRole`, `expectedCapabilityBoundary`, `launchPlanId`, `expectedConfigPath`, `expectedConfigSha256`.
  - 인코딩: BOM 없는 UTF-8, 압축 구분자 `','` 및 `':'`, `ensure_ascii=False`, 후행 개행(`\n`) 없음.
  - 자체 프로비넌스 매니페스트(`PROVENANCE_MANIFEST.json`) 및 raw SHA 파일 출력.

---

## 3. `WorkerBridge.cs` 인가 6개 소스 구간 정밀 구현 내역

| 구간 ID | 원본 바이트 범위 | 변경 크기 | 변경 후 바이트 범위 | 변경 내용 및 방어 조치 |
| :--- | :--- | :--- | :--- | :--- |
| `BOOTSTRAP_CLASS` | `1126 .. 6269` | 12,987 B | `1126 .. 14113` | `WorkerBridgeBootstrapper` 교체. 명시적 페어 모드(`operatorpairfile`, `operatorpairsha`) 처리 및 레거시 `self7` fallback 완전 보존. 페어 경로 내 `'='` 거부, 레거시 키 공존 시 fail-closed, 비어있지 않은 `validatorarguments` 거부. 비공개 IO 어댑터 단 1회 읽기 후 `AdmitPairBytes` 호출. 생성된 `GameObject` 및 부모 영수증 결속 1회성 핸드오프 설정 후 `AddComponent`. |
| `INSTANCE_PRIVATE_PROFILE` | `16357 .. 16357` | 1,842 B | `24201 .. 26043` | `WorkerBridgeComponent` 내 `_privatePairProfile` 프라이빗 인스턴스 필드 및 `SetPendingStartupHandoff`, `ClearPendingStartupHandoff`, `TryAcquirePendingStartupHandoff` 내부/비공개 헬퍼 삽입. (공개 getter 없음). |
| `AWAKE_EARLY_ACQUIRE` | `21162 .. 21162` | 338 B | `30848 .. 31186` | `Awake()` 진입 `try` 블록 최상단에 조기 획득 로직 삽입. `fastEcology`, 로그 콜백, 폴리시, 리스너 등 어떠한 부작용 발생 전에 인스턴스 프라이빗 프로필로 핸드오프 수납. |
| `NEW_PAIR_MODE_LAUNCH_HOLD` | `99112 .. 99112` | 165 B | `109136 .. 109301` | `HandleLaunchOperatorValidator` 진입 시 `_privatePairProfile != null` 검사. 페어 모드 활성 시 `ERROR: M05_NOT_ADMITTED: Child launch execution withheld in R29.` 즉시 반환. task 소비나 프로세스 기동 일체 차단. |
| `ONDESTROY_PRIVATE_PROFILE_CLEAR` | `165893 .. 165893` | 82 B | `176082 .. 176164` | `OnDestroy()` 진입 시 `_privatePairProfile = null;` 및 `ClearPendingStartupHandoff();` 호출. 기존 프로세스/태스크 정리 코드는 불변 유지. |
| `PURE_PAIR_ADMISSION_TYPES` | `178847 .. 178847` | 10,428 B | `189118 .. 199546` | 불변 클래스 `OperatorStartupPairSnapshot` (ParentReceipt, ChildReceipt, OperatorPairId, Scope, GetParentDeclaration(), GetChildDeclaration()) 및 순수 승인 헬퍼 `OperatorStartupPairAdmission.AdmitPairBytes(...)` 삽입. 순수 메모리 연산만 수행. |

### 외부 바이트 불변성 검증 (Source Scope Fidelity)
- 외부 7개 세그먼트 (총 234,431 바이트) 원본 대조 100% 비트 단위 일치 확인 (`SOURCE_SCOPE_DIFF.json`).
- `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` (170,135 B, SHA `391F9645...`) 및 `WorkerBridge.csproj` (1,774 B, SHA `571A58F5...`) 완전 보존.

---

## 4. 후보 바이너리 및 빌드 신원 (Candidate Identity)

- **빌드 환경**: Roslyn C# Compiler (csc 4.8.9232.0), .NET Framework 4.7.2, 경고 0, 오류 0.
- **Debug Candidate DLL**:
  - 경로: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
  - 크기: 322,560 bytes | SHA-256: `084C58CCD770AF90D2F2AE162FF5456C8CD2F0DB3167AE13394635BF8E567E7A`
  - MVID: `5c410658-e435-4ae4-8aa3-d074fbcf4f5d`
  - CodeView: RSDS, GUID `4b83c0af-9116-4158-b47e-a4d8a1581cf5`, Age 1
  - PDB: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb` (77,724 bytes, SHA `7E76C8CE...`)
- **Release Candidate DLL**:
  - 경로: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
  - 크기: 305,152 bytes | SHA-256: `4B4FBD87DDF6B4B39D419F5FDF28428F1E0869CA208E159094409A8D1102463E`
  - MVID: `3bf83c4d-c38b-43b4-8f9c-520e3e277200`
  - CodeView: RSDS, GUID `bddd0aa3-ed8b-4253-957a-ea18011d4f36`, Age 1
  - PDB: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb` (56,876 bytes, SHA `EE705B6F...`)
- **Synchronized 1.6 Assemblies**:
  - DLL: `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` (322,560 bytes, SHA `084C58CC...`, Debug 일치)
  - PDB: `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb` (77,724 bytes, SHA `7E76C8CE...`, Debug 일치)

---

## 5. 개발자 E1 검증 결과

### 5.1 오퍼레이터 퍼블리셔 6개 정상 케이스 실행
1. `PLAIN_PLAIN`: PairId `WE-PAIR-DEV-R29-PLAIN-PLAIN-01`, Bundle SHA `7C0AB26E...`, 0.0788s, 종료코드 0
2. `OPAQUE_OPAQUE`: PairId `WE-PAIR-DEV-R29-OPAQUE-OPAQUE-02`, Bundle SHA `39E6CF2F...`, 0.0795s, 종료코드 0
3. `PLAIN_OPAQUE_PADDED`: PairId `WE-PAIR-DEV-R29-PLAIN-OPAQUE-03`, Bundle SHA `9BB5E55D...`, 0.0777s, 종료코드 0
4. `OPAQUE_PLAIN_PADDED`: PairId `WE-PAIR-DEV-R29-OPAQUE-PLAIN-04`, Bundle SHA `BECA6A3F...`, 0.0791s, 종료코드 0
5. `PAIR_ID_WITH_EQUALS`: PairId `WE=PAIR=DEV=R29=EQUALS=05` (불투명 `'='` 보존), Bundle SHA `9FDEF442...`, 0.0785s, 종료코드 0
6. `UNICODE_BACKSLASH_QUOTE_EQUALS`: PairId `WE-PAIR-DEV-R29-Ω-"QUOTE"=\BACKSLASH\-06` (특수 유니코드, 따옴표, 역슬래시, `'='` 보존), Bundle SHA `30D4CAE5...`, 0.0790s, 종료코드 0

### 5.2 분리 관리형 단위 테스트 러너 (`Gate05R29StartupPairRunner`)
- **실행 문화권**: `en-US` (PID 34228, 0.1515s, 종료코드 0) 및 `de-DE` (PID 12948, 0.0803s, 종료코드 0).
- **단위 검증 내역**:
  - `AdmitPairBytes` 6건: 스코프 마커 `DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY` 일치, 부모 역할 `SIMULATION` 및 자식 역할 `READ_ONLY` 영수증 발급 검증.
  - 불변 복제 및 격리 검증: 반환된 선언 객체 변조 시 후속 게터 호출에 무영향 확인; 호출자의 입력 배열(`bundleBytes`, `parentBytes`, `childBytes`) 변조 시에도 스냅샷 및 영수증 손상 없음 확인.
  - 레거시 R27 회귀 검증: `OperatorChildLaunchInputs.Capture` 4개 페어 15개 게터 및 호출자/분리 격리 100% PASS.
  - C# Process 호출: 0회 (순수 호스트 텔레메트리 관측).
  - 거부/부정 프로브: 0회.

---

## 6. 결론 및 거버넌스 준수

1. 본 구현은 Master의 지침에 따라 전역 상태 오염, 비공개 권한 남용, 미검증 CLI 노출을 원천 배제하고 **지정된 인가 구간만을 정확히 구현**했습니다.
2. `OperatorStartupPairSnapshot` 및 퍼블리셔는 선언 일관성 데이터 전용이며, 실제 오퍼레이터 서명 인증, 자식 등록 슬롯, 네이티브 실행 권한을 부여하지 않습니다.
3. Steam 설치 DLL 불일치 건은 UNKNOWN OPEN INCIDENT로 유지되며 임의 복원되지 않았습니다.
4. 전용 서버(Dedicated Server)가 최종 도메인 권한을 유지하며, Pipeline independent E2 PASS 전까지 Foundation은 HOLD 상태를 엄격히 유지합니다.
