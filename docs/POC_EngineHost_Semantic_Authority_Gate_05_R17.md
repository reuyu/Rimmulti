# POC EngineHost Semantic Authority Gate 05 R17 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R17_OWNED_BOOTSTRAP / GATE05-R17-OWNED-BOOTSTRAP` (Envelope 20)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R17-OWNED-BOOTSTRAP-20261010-DIRECT-57163c71`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-10
- **E1 Verdict**: `IMPLEMENTED_SCOPED_NORMAL_HELPER_PASS_NATIVE_UNTESTED`

---

## 1. 개요 및 기술 목표

### 1.1 Master R16 정정 및 배경
Master의 R16 정정(`MASTER_REVIEW_ENGINE_GATE05_R16_DUAL_OPERATOR_NATIVE_PREPARATION_20261010.md`, Envelope 20)에 따라, 과거 분석의 인과적 과잉 주장(권한/백신/DRM 증명 배제 및 자산 부재 원인 단정)을 배제하고 다음 원칙을 준수합니다:
1. **자산 부재는 준비 상태 결함(Readiness Gap)이며, 과거 R4 5초 종료 원인은 `UNKNOWN`으로 유지**.
2. **단순 XML/대기시간 수정이 아닌 운영자 소유 정상 시동(Operator-Owned Normal Startup) 및 강제 실행파일 인가(Mandatory Executable Admission) 구현**.
3. **Census 및 csproj는 100% 불변 보존하며 오직 `WorkerBridge.cs` 단일 파일만 수정**.
4. **실제 Awake, 네이티브 런타임, 게임 루프, Process.Start, live 바인딩, 과거 러너, 부정 프로브, 자산 복사 엄격 금지**. 순수 정상 관리 헬퍼(Positive Pure Helper) 검증만을 수행.

### 1.2 R17 구현 핵심 목표 (`OWNED_BOOTSTRAP`)
1. **타입화된 불변 시동 구성 스냅샷 (`OperatorStartupConfig` & `OperatorStartupConfigSnapshot`)**:
   - 스키마 버전: `WE-OPERATOR-BOOTSTRAP-V1`.
   - 운영자 인가 실행파일 절대 정규화 경로(`AdmittedValidatorExecutablePath`) 및 64자리 16진수 SHA-256(`AdmittedValidatorExecutableSha256`).
   - 격리된 작업자 및 검증자 유저데이터 경로(`WorkerUserDataDirectory`, `ValidatorUserDataDirectory` 상호 배타성 검증).
   - 유효 패키지 정책 선언(`ExpectedPackagePolicyDeclaration`) 및 예상 지문, 역할(`SIMULATION`/`READ_ONLY`), 역량 경계(`LOCAL_SANDBOXED`).
   - 누락/비정상 구성 시 fail-closed 차단. 외부 문자열 대입에 의한 권한 우회 차단.
2. **`WorkerBridgeComponent` 소스 레벨 시동 바인딩**:
   - `SafeSaveDataFolderPath`: 활성 운영자 구성 존재 시 `WorkerUserDataDirectory`로 세이브/태스크 경로 격리 라우팅.
   - `Awake()`: 컴포넌트 시동 시 프로필 평가 이전 단계에서 `ContentProfileProvider.ConfigureExpectedPackagePolicy(_activeStartupConfig.ExpectedPackagePolicyDeclaration)` 호출 선행 바인딩.
   - 부트스트래퍼(`WorkerBridgeBootstrapper`): `-operatorconfig <path>` 인자 감지 및 시동 전 구성 적재 지원.
   - 공개 조회 명령 `GET_OPERATOR_CONFIG` 추가 (민감 토큰 마스킹 반환, 원격 변경 명령은 제공하지 않음).
3. **강제 실행파일 검증 및 실제 프로세스 신원 바인딩 (`ExecutableAdmissionHelper`)**:
   - `VerifyAdmittedExecutable`: 디스크 파일 실존 및 실제 계산된 SHA-256이 운영자 승인 해시와 일치하는지 `Process.Start` 이전에 사전 검증(Preflight).
   - `VerifyProcessIdentity`: 프로세스의 `MainModule.FileName` 정규화 경로, 디스크 상의 실행파일 SHA-256, PID, StartTimeUtc, 역할 일치 여부를 fail-closed로 검증. 자기-PID 검증(Self-Validation) 원천 차단.
   - `HandleLaunchOperatorValidator`: 호출자의 임의 인자/실행파일 지정을 거부하고, 비공개 승인 구성에서 실행파일/인자/CWD를 도출하며 사전 검증 및 실행 후 프로세스 신원 바인딩 적용.
   - `BindOperatorLaunchedProcess`: 동일한 비공개 승인 구성 및 `VerifyProcessIdentity` 헬퍼를 적용하여 실제 `MainModule` 신원 검증.
4. **민감 정보 누출 차단 (`ValidatorResultExtensions.ToRedactedJson`)**:
   - 공개 반환 명령(`VALIDATOR_RESULT`)에서 `capabilityNonce` 및 `channelSecretToken`을 `[REDACTED_PROTECTED_OPERATOR_CAPABILITY]` 및 `[REDACTED_PROTECTED_CHANNEL_SECRET]`으로 마스킹.
   - 비공개 보호 채널 파일(`resultChannelPath`)에는 전체 원본 결과 유지.

---

## 2. 소스 불변성 및 빌드 후보 바이너리 메타데이터

### 2.1 9개 Engine 경로 변경 및 보존 상태
| 파일 경로 | 변경 여부 | 크기 (Bytes) | SHA-256 |
| :--- | :--- | :--- | :--- |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` | **MODIFIED** | 177,533 | `EE63FB50ED84C1E0313EF7E2F160F38B0ABEA7E96A59CEBC30506FC9C7F338A9` |
| `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` | **IMMUTABLE** | 170,135 | `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` | **IMMUTABLE** | 1,774 | `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` |
| `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Debug)** | 268,800 | `F7946FED1F4FB896DD8F46B7C253C4DB24E6CF2AA6D9C0528CD5B59CD05DBAA3` |
| `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Debug)** | 65,700 | `F0EE8BF22E66B43EF5B37AE5BD7E905D09A64AE40FE2AEAA8FCA71A2C50BB28F` |
| `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Debug)** | 268,800 | `F7946FED1F4FB896DD8F46B7C253C4DB24E6CF2AA6D9C0528CD5B59CD05DBAA3` |
| `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Debug)** | 65,700 | `F0EE8BF22E66B43EF5B37AE5BD7E905D09A64AE40FE2AEAA8FCA71A2C50BB28F` |
| `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Release)** | 254,976 | `3CC5BB71A5A25F091677A57B69493522AC4FC0BC20B3562926F8942455D11591` |
| `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Release)** | 48,376 | `CE42762A3029C030646E1CB4635F053F932D0A2C66B5309CCDDDA17C28AC8E30` |

### 2.2 PE MVID 및 CodeView 바인딩 정보
- **Debug Candidate DLL**:
  - SHA-256: `F7946FED1F4FB896DD8F46B7C253C4DB24E6CF2AA6D9C0528CD5B59CD05DBAA3`
  - MVID: `d5a25e43-567c-414f-b7bd-4d4aa0b47050`
  - CodeView Path: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
  - CodeView Guid: `a776277f-e9de-4dc1-8e4b-225d260d445c`
  - CodeView Age: `1`
- **Release Candidate DLL**:
  - SHA-256: `3CC5BB71A5A25F091677A57B69493522AC4FC0BC20B3562926F8942455D11591`
  - MVID: `ab67e9ac-0c30-4718-98a3-cbfe9af31c87`
  - CodeView Path: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
  - CodeView Guid: `16912007-a180-4564-9ad4-6ebf68b32648`
  - CodeView Age: `1`

---

## 3. 순수 관리 러너 검증 (`Gate05R17BootstrapRunner`)

### 3.1 러너 구조 및 격리 실행 환경
- 프로젝트: `scratch\EngineGate05R17OwnedBootstrap\Harness\Gate05R17BootstrapRunner.csproj`
- 참조: 동결 QA 의존성(`FROZEN_MANAGED_QA_DEPENDENCIES`), `Newtonsoft.Json.dll`, 신규 후보 `WarEconomy.WorkerBridge.PoC.dll`
- 독립 실행 디렉터리:
  - `run_default`: 기본 로캘(`ko-KR`)
  - `run_en_us`: `en-US` 로캘
  - `run_de_de`: `de-DE` 로캘
- 3개 실행 모두 **종료 코드 0 (Exit Code 0)** 정상 완료.

### 3.2 테스트 항목별 검증 결과 (5/5 PASS)
1. **TEST_01_OPERATOR_STARTUP_CONFIG_SNAPSHOT_IMMUTABLE (PASS)**:
   - `OperatorStartupConfig` 객체 생성, `ToSnapshot()`을 통한 불변 스냅샷 변환 검증.
   - 스키마(`WE-OPERATOR-BOOTSTRAP-V1`), 실행파일 절대경로, 64자리 SHA, 격리 유저데이터 디렉터리 검증.
   - `WorkerBridgeComponent.SafeSaveDataFolderPath`가 구성된 `WorkerUserDataDirectory`로 정확히 라우팅됨을 확인.
   - `AdmittedOperatorValidatorExecutable` 및 `AdmittedOperatorValidatorSha` 프로퍼티가 스냅샷 값을 반환함을 검증.
2. **TEST_02_ADMITTED_EXECUTABLE_SHA_PATH_VALIDATION (PASS)**:
   - 실제 디스크 상의 프로젝트 런타임 바이너리 2종(`UnityCrashHandler64.exe`, `RimWorldWin64.exe`)을 순수 파일로만 읽어 해시 계산.
   - `ExecutableAdmissionHelper.ComputeFileSha256` 및 `VerifyAdmittedExecutable` 통과 확인. (실행/복사/설치 0).
3. **TEST_03_PROCESS_IDENTITY_BINDING_HELPER (PASS)**:
   - `VerifyProcessIdentity` 헬퍼의 자기-PID 검증 차단(Fail-closed against self-validation) 동작 검증.
   - `currentProc.Id == myPid`일 때 명시적 거부(`Self-validation prohibited. Target PID cannot match simulator PID.`) 확인.
4. **TEST_04_PACKAGE_POLICY_LIFECYCLE (PASS)**:
   - `ContentProfileProvider.ConfigureExpectedPackagePolicy(declaration)` 및 `ClearConfiguredExpectedPackagePolicy()` 수명주기 호출 검증. 전역 캐시 오염 없이 정상 초기화 확인.
5. **TEST_05_SECRET_REDACTION_PUBLIC_VIEW (PASS)**:
   - `ValidatorResult`의 `ToRedactedJson()` 호출 시 `capabilityNonce` 및 `channelSecretToken`이 공개 JSON에 누출되지 않고 `[REDACTED_PROTECTED_OPERATOR_CAPABILITY]`, `[REDACTED_PROTECTED_CHANNEL_SECRET]`으로 안전하게 마스킹됨을 검증.

### 3.3 명시적 API 원장 (`API_LEDGER.json`)
```json
{
  "ConfigureOperatorStartupCalls": 1,
  "ResetOperatorStartupConfigCalls": 1,
  "SafeSaveDataFolderPathCalls": 1,
  "AdmittedExecutablePropertyCalls": 1,
  "AdmittedShaPropertyCalls": 1,
  "ComputeFileSha256Calls": 2,
  "VerifyAdmittedExecutableCalls": 2,
  "VerifyProcessIdentityCalls": 1,
  "ConfigureExpectedPackagePolicyCalls": 1,
  "ClearConfiguredExpectedPackagePolicyCalls": 1,
  "ToRedactedJsonValidatorResultCalls": 1,
  "ToRedactedJsonSnapshotCalls": 1
}
```

---

## 4. 제약 사항 및 거버넌스 준수 (Limitations)

1. **STATIC_MANAGED_NORMAL_EVIDENCE_ONLY**: 본 E1 검증은 컴파일 및 순수 관리형 단위 제어 검증에 한정되며, 게임 엔진 내부 런타임 실행을 의미하지 않음.
2. **NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED**: 실제 네이티브 프로필 연산, Awake 이벤트 루프 트리거, Unity 메인 스레드 대기 등은 작업 범위 외로 미실행.
3. **PROCESS_START_AND_LIVE_BINDING_UNTESTED**: `Process.Start` 및 실시간 프로세스 바인딩은 본 WP에서 실행되지 않았으며, 헬퍼 논리 검증으로 한정됨.
4. **NO_CAUSAL_OVERCLAIMS**: 이전 R4의 5초 프로세스 강제 종료 원인은 여전히 `UNKNOWN`이며, 본 수정으로 인과적 문제가 완전 해결되었다고 주장하지 않음.
5. **FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER**: 최종 도메인 권한은 전용 서버(Dedicated Server)에 있으며, Worker는 바운디드 시뮬레이션 제안자임.
6. **FOUNDATION_HOLD**: Foundation 승인은 Pipeline E2 통과 전까지 보류 상태를 유지함.
