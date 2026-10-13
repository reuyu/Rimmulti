# POC EngineHost Semantic Authority Gate 05 R20 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R20_TRUSTED_STARTUP_ORIGIN / GATE05-R20-TRUSTED-STARTUP` (Envelope 23)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-11
- **E1 Verdict**: `IMPLEMENTED_SCOPED_TRUSTED_STARTUP_ORIGIN_PASS_NATIVE_UNTESTED`

---

## 1. 개요 및 기술 목표

### 1.1 Master R19 검토 및 배경
Master의 R19 정정 및 평가(`MASTER_REVIEW_ENGINE_GATE05_R19_OPAQUE_POLICY_INDEPENDENT_S1_20261011.md`, `QA_EngineHost_Gate05_R19_Opaque_Policy_Independent_S1_20261010.md`, Envelope 23) 및 R20 작업 명세(`WP_ENGINE_GATE05_R20_TRUSTED_STARTUP_ORIGIN.md`)에 따라, 다음 핵심 원칙과 제약사항을 준수합니다:
1. **R19 불투명 정책 무손실 보존 상태 유지 (Defect Scoped Closed)**:
   - R19의 불투명 정책 ID/리비전 무손실 보존은 Sol 독립 QA에 의해 좁은 CLOSED 상태로 인정됨.
   - 본 R20에서는 M01/M03 6개 허용 영역 외의 모든 소스 바이트 및 R19 스냅샷/코덱 구현을 100% 동결 보존함.
2. **명시적 로컬 기동 선언 및 팩토리 발행 불변 승인 영수증 (Admission Receipt)**:
   - 코디네이터가 소유한 로컬 기동 선언(`OperatorLaunchDescriptor`)을 통해 `originId`, `launchPlanId`, `configId`, `role`, `capabilityBoundary`, 정규화된 절대 경로(`expectedConfigPath`), 예상 SHA-256(`expectedConfigSha256`)을 엄격히 검속.
   - 공개 생성자 호출에 의한 임의 스냅샷 대입을 차단하고, `OperatorStartupConfigAdmissionFactory`만이 내부(`internal`) 생성자를 통해 불변 승인 영수증(`OperatorStartupAdmissionReceipt`)을 발행.
3. **단일 설치 경로 및 신뢰 게이트 연결 (Connected Startup Gate)**:
   - `WorkerBridgeBootstrapper`는 `-operatorconfig` 또는 필수 선언 누락 시 컴포넌트(`GameObject`)를 일절 부착하지 않고 즉시 반환.
   - `WorkerBridgeComponent.TryInstallOperatorStartupConfig(receipt)`는 유효한 승인 영수증만을 독점 수용.
   - `Awake`의 심층 방어: 유효한 영수증이 부착되지 않은 경우 정책 설정, TCP 리스너 기동, 스레드 생성을 차단하고 즉시 반환하며 준비 상태를 취소(`RevokeReadiness`).
   - `HandleValidateInput`은 유효한 영수증이 설치되지 않은 경우 즉시 오류를 반환하여 `trustedSimulationReady = true` 전이를 원천 봉쇄.
4. **C# Process API 호출 0건 및 호스트 텔레메트리 분리**:
   - 관리형 러너 내부에서 `Process.Start`, `Process.GetCurrentProcess`, `VerifyProcessIdentity` 등 프로세스 관련 C# API 일절 미호출.
   - 호스트 Python 오케스트레이터(`run_battery.py`)를 통해 독립 프로세스로 기동된 자식 PID와 OS 종료 코드만을 수집.
5. **로그 스트림 닫힘 및 인벤토리 완전성 (Stream Inventory Closure)**:
   - 호스트 오케스트레이터가 `stdout.txt` 및 `stderr.txt`를 파일에 기록하고 완전히 닫은 후 `OUTPUT_INVENTORY.json`을 산출하여 인벤토리 누락을 원천 해결함 (R19 de-DE 누락 이슈 해결).

---

## 2. 소스 변경 및 9개 Engine 경로 보존 상태

### 2.1 WorkerBridge.cs 6개 영역 변경 상세
1. **Region 1 (`WorkerBridgeBootstrapper.Initialize`)**:
   - `-operatorconfig` 및 `-operatorconfigsha` 인자 확인. 미존재 시 컴포넌트 미부착 조기 반환.
   - 로컬 기동 선언 인자(`-operatorlaunchorigin`, `-operatorlaunchplan`, `-operatorlaunchrole`, `-operatorlaunchconfigid`, `-operatorlaunchboundary`) 파싱.
   - `OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configPath, expectedSha, launchDesc)` 호출.
   - 영수증 검증 실패 시 컴포넌트 미부착 조기 반환.
   - `TryInstallOperatorStartupConfig(receipt)` 성공 시에만 `GameObject` 부착.
2. **Region 2 (`WorkerBridgeComponent` 상태 필드 및 설치자)**:
   - `_activeAdmissionReceipt` 및 `ActiveAdmissionReceipt` 추가.
   - `TryInstallOperatorStartupConfig(OperatorStartupAdmissionReceipt receipt)`: 팩토리 발행 영수증 독점 수용 및 스냅샷 동결 저장.
3. **Region 3 (`Awake`)**:
   - `_activeAdmissionReceipt == null || !_activeAdmissionReceipt.IsValid()` 검사.
   - 미충족 시 `RevokeReadiness`, 에러 로깅 후 즉시 반환 (리스너/스레드 생성 차단).
4. **Region 4 (`HandleValidateInput`)**:
   - 영수증 미충족 시 즉시 거부 및 준비 상태 취소, `trustedSimulationReady = true` 진입 차단.
5. **Region 5 (`OperatorLaunchDescriptor` 및 `OperatorStartupAdmissionReceipt`)**:
   - `OperatorLaunchDescriptor`: 기존 5개 필드 보존 + `expectedConfigPath`, `expectedConfigSha256`, `Clone()` 추가.
   - `OperatorStartupAdmissionReceipt`: 불변 봉인 클래스(`sealed`), `internal` 생성자, get-only 프로퍼티 11종, `IsValid()`, `ToRedactedJson()`.
6. **Region 6 (`OperatorStartupConfigAdmissionFactory`)**:
   - `IsFullyQualifiedWindowsPath(string? path)`: DOS 드라이브 루트 및 UNC 루트 검속.
   - `ValidateAdmissionReceipt(...)`, `IssueAdmissionReceipt(...)`, `IssueAdmissionReceiptFromBytes(...)` 구현.

### 2.2 9개 Engine 경로 변경 및 보존 상태
| 파일 경로 | 상태 | 크기 (Bytes) | SHA-256 |
| :--- | :--- | :--- | :--- |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` | **MODIFIED** | 213,803 | `AB56CC423C6FB915476104D22B32F0A91B446D6788552830A9730A2DEF11898D` |
| `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` | **IMMUTABLE** | 170,135 | `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` | **IMMUTABLE** | 1,774 | `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` |
| `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Debug)** | 295,424 | `482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0` |
| `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Debug)** | 71,020 | `EC05783A49CA30FECD9E615020A71206F2AE388D8053D750B3EECEDF9B97455F` |
| `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Debug)** | 295,424 | `482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0` |
| `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Debug)** | 71,020 | `EC05783A49CA30FECD9E615020A71206F2AE388D8053D750B3EECEDF9B97455F` |
| `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Release)** | 279,552 | `90FDAF96404913D917CEE3EFCDC81A94C05B348DBF1BFE3F44852096A32B2C4C` |
| `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Release)** | 52,036 | `749A540D23FF0A77CD0A7E0D53E5927B303B40615A7DEDF11A0E4C8D91B4C051` |

- `EngineHostCensus.cs` 접두사 검증: 길이 72,547 bytes, SHA-256 `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (**100% 불변 확인**).

### 2.3 PE MVID 및 CodeView 바인딩 정보
- **Debug Candidate DLL**:
  - SHA-256: `482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0`
  - MVID: `9e516c44-35c8-49b8-b3ec-f73ec58ba12f`
  - CodeView Path: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
  - CodeView GUID: `b89d72d6-b70a-4e6e-afec-d6654fcfeff7`
  - CodeView Age: `1`
- **Release Candidate DLL**:
  - SHA-256: `90FDAF96404913D917CEE3EFCDC81A94C05B348DBF1BFE3F44852096A32B2C4C`
  - MVID: `96ac6c7c-420a-4c16-a26e-7c0a18d4c360`
  - CodeView Path: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
  - CodeView GUID: `727f832b-dcb4-4ccd-aed3-4f15239091a1`
  - CodeView Age: `1`

---

## 3. Detached Pure Runner 검증 및 호스트 프로세스 격리 실행

### 3.1 러너 아키텍처 및 무결성 보장
- 프로젝트: `scratch\EngineGate05R20TrustedStartup\Harness\Gate05R20TrustedStartupRunner.csproj`
- 러너 바이너리: `scratch\EngineGate05R20TrustedStartup\Harness\bin\Debug\net472\Gate05R20TrustedStartupRunner.exe` (SHA `5C2DD36A9480D20CC488FD075A6DCBDEF5F754978C46EF5BB66BB5643924A3EF`, 크기 40,960)
- 러너 PDB: `scratch\EngineGate05R20TrustedStartup\Harness\bin\Debug\net472\Gate05R20TrustedStartupRunner.pdb` (SHA `35E2EE57768FD1CFE1E9F6CDC2BD100E806FE1BA046057F38F974185F5B2B4A5`, 크기 9,248)
- **호스트 Python 오케스트레이터 (`run_battery.py`) 배터리 실행**:
  - `en-US` 문화권: 자식 PID 32552, Exit Code 0, 소요시간 0.31초, 7/7 PASS (16/16 매트릭스 PASS, 8/8 영수증 배터리 PASS).
  - `de-DE` 문화권: 자식 PID 8020, Exit Code 0, 소요시간 0.17초, 7/7 PASS (16/16 매트릭스 PASS, 8/8 영수증 배터리 PASS).
  - **격리 무결성 검증**: Run 1 완료 후 산출된 15개 파일을 인벤토리에 등록하고, Run 2 완료 후 Run 1의 파일들을 재해싱하여 100% 바이트 불변임을 확인 (`isolation_verified: true`).
  - **스트림 인벤토리 닫힘 보장**: `stdout.txt` 및 `stderr.txt`를 명시적으로 flush/close한 후 `OUTPUT_INVENTORY.json`을 작성하여 인벤토리 내 100% 반영 확인.

### 3.2 테스트 항목별 검증 결과 (7/7 PASS)
1. **TEST_01_OPAQUE_POLICY_LOSSLESS_PRESERVATION (PASS, 16/16 Matrix)**:
   - 2개 역할(`SIMULATION`, `READ_ONLY`) × 2개 정책(`PLAIN`, `OPAQUE`) × 4개 경로(`SnapshotDirectConstructor`, `ToSnapshot`, `AdmitConfigBytes`, `AdmitConfigFile`) 전수 검증.
   - 불투명 식별자 `"  qa.R18 정책 Ω  "` 및 리비전 `"  007 café Ω  "`의 앞뒤 공백 및 유니코드 문자가 트리밍 없이 원본 그대로 보존됨을 확인.
   - 계산된 원시 선언 다이제스트 `8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`가 16개 경로 전체에서 100% 동일하게 산출됨을 확인.
2. **TEST_02_ADMISSION_RECEIPT_ISSUANCE_AND_BOUND_PROVENANCE (PASS, 8/8 Routes)**:
   - 2개 역할 × 2개 정책 × 2개 방식(`IssueAdmissionReceipt` 파일 경로, `IssueAdmissionReceiptFromBytes` 바이트 배열) = 8개 경로 전수 통과.
   - `ReceiptSchemaVersion == "WE-OPERATOR-RECEIPT-V1"`, `IsTrusted == true`, `IsValid() == true` 확인.
   - 모든 결속 프로버넌스 필드(`BoundOriginId`, `BoundLaunchPlanId`, `BoundConfigId`, `BoundRole`, `BoundCapabilityBoundary`, `BoundConfigPath`, `BoundConfigSha256`) 정합성 확인.
3. **TEST_03_DECLARATION_AND_RECEIPT_DEFENSIVE_IMMUTABILITY (PASS)**:
   - 영수증 발행 후 호출자의 `OperatorLaunchDescriptor` 속성을 사후 변조하더라도 이미 발행된 영수증의 결속 필드에 일절 영향이 없음을 확인.
   - `launchDesc.Clone()` 호출 시 독립된 복제본이 생성됨을 확인.
   - 영수증 스냅샷의 패키지 정책 리스트 변조 시도시 내부 격리 유지 확인.
4. **TEST_04_RECEIPT_REDACTED_JSON_REPRESENTATION (PASS)**:
   - `receipt.ToRedactedJson()` 호출 시 정확히 11개 프로퍼티 출력 및 스냅샷 내부의 불투명 정책 식별자/리비전 무손실 직렬화 확인.
5. **TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_HELPER (PASS)**:
   - `IsFullyQualifiedWindowsPath` 순수 헬퍼 정합성 확인: DOS 드라이브 루트(`C:\`, `D:/`) 및 UNC 공유 루트(`\\server\share\`)는 정상 승인(5/5 통과), 상대 경로/루트 상대 경로/드라이브 상대 경로는 거부(7/7 통과).
6. **TEST_06_VALIDATOR_RESULT_REDACTION_REGRESSION (PASS)**:
   - `ValidatorResult.ToRedactedJson()` 호출 시 민감 필드(`capabilityNonce`, `channelSecretToken`)가 마스킹됨을 확인.
7. **TEST_07_CENSUS_PACKAGE_POLICY_REGRESSION (PASS)**:
   - `ContentProfileProvider` 패키지 정책의 직렬화, 역직렬화 및 결정론적 다이제스트 계산 회귀 검증 통과 확인.

### 3.3 명시적 API 원장 (`API_LEDGER.json`)
```json
{
  "ParseStrictCalls": 4,
  "AdmitConfigBytesCalls": 4,
  "AdmitConfigFileCalls": 4,
  "IssueAdmissionReceiptCalls": 6,
  "IssueAdmissionReceiptFromBytesCalls": 4,
  "ValidateAdmissionReceiptCalls": 8,
  "IsFullyQualifiedWindowsPathCalls": 12,
  "ToSnapshotCalls": 4,
  "ToRedactedJsonSnapshotCalls": 0,
  "ToRedactedJsonReceiptCalls": 1,
  "GetExpectedPackagePolicyDeclarationCalls": 16,
  "ComputeFileSha256Calls": 0,
  "VerifyAdmittedExecutableCalls": 0,
  "ToRedactedJsonValidatorResultCalls": 1,
  "SerializePackagePolicyCalls": 1,
  "DeserializePackagePolicyCalls": 1,
  "ComputePackagePolicyDigestCalls": 17,
  "ProcessApiCalls": 0,
  "VerifyProcessIdentityCalls": 0,
  "WorkerBridgeGlobalConfigureResetCalls": 0,
  "TryInstallOperatorStartupConfigCalls": 0,
  "AwakeCalls": 0,
  "HarmonyCalls": 0
}
```

---

## 4. 제약 사항 및 거버넌스 준수 (Limitations)

1. **STATIC_MANAGED_NORMAL_EVIDENCE_ONLY**:
   - 본 검증은 분리된 순수 관리형 테스트 환경에서 정상 제어 경로만을 대상으로 수행됨 (7/7 PASS, 16/16 매트릭스 PASS, 8/8 영수증 배터리 PASS, exit 0).
2. **ZERO_PROCESS_API_CALLS_IN_MANAGED_TESTS**:
   - 관리형 러너 코드 내에서 `Process.Start`, `Process.GetCurrentProcess`, `VerifyProcessIdentity` 일절 미호출.
3. **HOST_PYTHON_TELEMETRY_CHILD_PID_AND_EXIT_CODE_ONLY**:
   - 호스트 서브프로세스 텔레메트리는 운영상 관측 기록이며 네이티브 권위가 아님.
4. **NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED**:
   - 림월드 게임 루프, Unity 씬 기동, 네이티브 실행, Awake 이벤트 루프, 오퍼레이터 프로모션은 본 WP에서 명시적으로 금지되었으며 실행되지 않음.
5. **FAIL_CLOSED_BRANCHES_UNEXECUTED**:
   - 부트스트랩 미승인 조기 반환, Awake 신뢰 취소 조기 반환, HandleValidateInput 거부 브랜치는 정적 소스 코드 검토를 통해서만 확인되었으며, 부정 프로브/예외 실행은 수행하지 않음.
6. **INSTALLED_DLL_INCIDENT_OPEN**:
   - Steam 설치 경로의 DLL과 아카이브 간 해시 불일치 인시던트는 원인 미상의 오픈 상태로 유지되며 임의 변경하지 않음.
7. **FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER**:
   - 전용 서버(Dedicated Server)가 최종 도메인 권위이며, 엔진/클라이언트는 한정된 시뮬레이션 제안만을 생성함.
8. **FOUNDATION_HOLD**:
   - Foundation 파이프라인 E2 PASS 전까지 전체 Foundation 및 릴리스는 HOLD 상태를 유지함.
