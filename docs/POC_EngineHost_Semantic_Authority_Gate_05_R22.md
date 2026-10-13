# POC EngineHost Semantic Authority Gate 05 R22 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R22_EXPLICIT_DECLARATION / GATE05-R22-DECLARATION` (Envelope 25)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R22-DECLARATION-20261011-DIRECT-9be1579a`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-11
- **E1 Verdict**: `IMPLEMENTED_EXPLICIT_DECLARATION_PASS_NATIVE_UNTESTED`

---

## 1. 개요 및 기술 목표

### 1.1 Master R21 검토 및 R22 기술 배경
Master의 R21 독립 QA 결과(`MASTER_REVIEW_ENGINE_GATE05_R21_RECEIPT_UTC_INDEPENDENT_S1_20261011.md`, Envelope 25) 및 R22 작업 명세(`WP_ENGINE_GATE05_R22_EXPLICIT_DECLARATION.md`)에 따라, 다음 핵심 원칙과 범위를 준수하여 작업을 완료했습니다:
1. **M01 결함의 극소 범위 정정 (Explicit 7-Field Declaration Only)**:
   - 이전 버전(R20/R21)의 부트스트랩 CLI에서 선택적 인자 검사 및 `OperatorLaunchDescriptor`의 유의미한 기본값(`"LOCAL_OPERATOR_LAUNCH"`, `"WE-LAUNCH-PLAN-V1"`, `"SIMULATION"`, `"LOCAL_SANDBOXED"`)으로 인해, 코디네이터가 불완전한 선언을 한 상태에서도 승인이 생성될 수 있는 취약점이 지적되었습니다.
   - 본 R22에서는 `OperatorLaunchDescriptor`의 모든 기본값을 빈 문자열(`""`)로 초기화하여 승인의 무단 제조를 원천 방지하고, 기동 시 필수 7개 필드(`originId`, `launchPlanId`, `expectedConfigId`, `expectedRole`, `expectedCapabilityBoundary`, `expectedConfigPath`, `expectedConfigSha256`)를 명시적으로 요구(Fail-Closed)하도록 변경했습니다.
2. **영수증 팩토리 진입 시 Descriptor 1회 복제 및 사전 검증**:
   - `IssueAdmissionReceipt` 및 `IssueAdmissionReceiptFromBytes` 진입 시 호출자의 디스크립터를 즉시 1회 복제(`Clone()`)하고, 파일/바이트 승인 전에 복제본의 7개 필드 완전성을 검증한 후 검증된 복제본만을 사용합니다.
3. **영수증 내 승인 선언 7개 필드의 비공개 불변 캡처 및 영수증 유효성 결속**:
   - `OperatorStartupAdmissionReceipt` 내부에 승인된 7개 필드 값을 비공개(`private readonly`)로 불변 저장하여 외부 노출 및 변경을 차단했습니다.
   - `ValidateAdmissionReceipt` 및 `receipt.IsValid()` 검증 시, 저장된 비공개 승인 선언 값과 바인딩된 영수증 필드, 스냅샷의 일치 여부를 대조 검증하며, 캡처가 누락되었거나 불일치할 경우 즉시 실패(Fail-Closed) 처리합니다.
   - 호출자가 영수증 발급 이후 원래의 디스크립터나 클론을 변조하더라도 이미 발급된 영수증의 유효성 및 내부 값은 100% 불변 보호됩니다.
4. **5개 고정 구간 100% 바이트 단위 일치 및 4개 허용 구간 한정 수정**:
   - `WorkerBridge.cs`의 수정은 Master 베이스라인(`MASTER_R22_SCOPE_BASELINE.json`)에 지정된 4개 허용 구간으로만 엄격히 제한되었으며, 5개 고정 바이너리 세그먼트(`WORKER_FIXED_SEGMENT_0..4.bin`)와 100% 바이트 단위로 일치합니다.
   - `EngineHostCensus.cs` (170,135 bytes, SHA `391F9645...`) 및 `WorkerBridge.csproj` (1,774 bytes, SHA `571A58F5...`)는 100% 동결 보존되었습니다.
5. **순수 긍정 제어 E1 배터리 및 C# Process API 0건**:
   - 무효/거부/예외 프로브를 0건으로 배제하고 순수 긍정 정상 제어만 검증했습니다.
   - 관리형 러너 내부에서 C# `Process`, `VerifyProcessIdentity`, 전역 `Awake`/Harmony 패치 일체 미호출.
   - 호스트 Python 서브프로세스를 통해 격리 기동 및 OS 종료 코드 0 수집 (`en-US` 및 `de-DE` 2개 배터리).

---

## 2. 소스 수정 4개 구간 상세

### 2.1 Region 1: `BOOTSTRAP_DECLARATION_ONLY` (오프셋 1,126 ~ 6,290)
부트스트랩의 정적 생성자에서 7개 필수 CLI 인자 전수 검증:
```csharp
    [StaticConstructorOnStartup]
    public static class WorkerBridgeBootstrapper
    {
        static WorkerBridgeBootstrapper()
        {
            try
            {
                // Gate05-R22: Explicit 7-field declaration startup gate (M01)
                bool hasConfigArg = GenCommandLine.TryGetCommandLineArg("operatorconfig", out string configPath) && !string.IsNullOrWhiteSpace(configPath);
                if (!hasConfigArg)
                {
                    Log.Warning("[WorkerBridge] Missing required '-operatorconfig' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasShaArg = GenCommandLine.TryGetCommandLineArg("operatorconfigsha", out string expectedSha) && !string.IsNullOrWhiteSpace(expectedSha);
                if (!hasShaArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorconfigsha' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasOriginArg = GenCommandLine.TryGetCommandLineArg("operatororigin", out string origin) && !string.IsNullOrWhiteSpace(origin);
                if (!hasOriginArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatororigin' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasPlanArg = GenCommandLine.TryGetCommandLineArg("operatorlaunchplan", out string plan) && !string.IsNullOrWhiteSpace(plan);
                if (!hasPlanArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorlaunchplan' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasConfigIdArg = GenCommandLine.TryGetCommandLineArg("operatorconfigid", out string cfgId) && !string.IsNullOrWhiteSpace(cfgId);
                if (!hasConfigIdArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorconfigid' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasRoleArg = GenCommandLine.TryGetCommandLineArg("operatorrole", out string role) && !string.IsNullOrWhiteSpace(role);
                if (!hasRoleArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorrole' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                bool hasCapArg = GenCommandLine.TryGetCommandLineArg("operatorcapability", out string cap) && !string.IsNullOrWhiteSpace(cap);
                if (!hasCapArg)
                {
                    Log.Error("[WorkerBridge] Missing required '-operatorcapability' CLI argument for operator config (Fail-Closed). Component will NOT attach.");
                    return;
                }

                var descriptor = new OperatorLaunchDescriptor
                {
                    originId = origin.Trim(),
                    launchPlanId = plan.Trim(),
                    expectedConfigId = cfgId.Trim(),
                    expectedRole = role.Trim(),
                    expectedCapabilityBoundary = cap.Trim(),
                    expectedConfigPath = configPath.Trim(),
                    expectedConfigSha256 = expectedSha.Trim()
                };

                var admissionResult = OperatorStartupConfigAdmissionFactory.IssueAdmissionReceipt(configPath, expectedSha, descriptor);
                if (!admissionResult.isValid || admissionResult.receipt == null)
                {
                    Log.Error($"[WorkerBridge] Operator config admission receipt issuance failed (Fail-Closed): {admissionResult.error}. Component will NOT attach.");
                    return;
                }

                bool installed = WorkerBridgeComponent.TryInstallOperatorStartupConfig(admissionResult.receipt);
                if (!installed)
                {
                    Log.Error("[WorkerBridge] Failed to install operator startup admission receipt (already installed or sealed). Component will NOT attach.");
                    return;
                }

                Log.Message($"[WorkerBridge] Successfully admitted and installed operator startup config from '{configPath}' (Id='{admissionResult.receipt.Snapshot.ConfigId}', Role='{admissionResult.receipt.Snapshot.Role}')");

                Log.Message("[WorkerBridge] StaticConstructorOnStartup fired. Attaching GameObject...");
                var go = new GameObject("WorkerBridgeController");
                UnityEngine.Object.DontDestroyOnLoad(go);
                go.AddComponent<WorkerBridgeComponent>();
                Log.Message("[WorkerBridge] Controller GameObject attached.");
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Bootstrapper error: " + ex);
            }
        }
    }
```

### 2.2 Region 2: `DESCRIPTOR_DEFAULTS_HELPER_CLONE` (오프셋 178,061 ~ 178,983)
기본값 제거 및 클론 헬퍼:
```csharp
    public class OperatorLaunchDescriptor
    {
        public string originId = "";
        public string expectedConfigId = "";
        public string expectedRole = "";
        public string expectedCapabilityBoundary = "";
        public string launchPlanId = "";
        public string expectedConfigPath = "";
        public string expectedConfigSha256 = "";

        public OperatorLaunchDescriptor Clone()
        {
            return new OperatorLaunchDescriptor
            {
                originId = this.originId,
                expectedConfigId = this.expectedConfigId,
                expectedRole = this.expectedRole,
                expectedCapabilityBoundary = this.expectedCapabilityBoundary,
                launchPlanId = this.launchPlanId,
                expectedConfigPath = this.expectedConfigPath,
                expectedConfigSha256 = this.expectedConfigSha256
            };
        }
    }
```

### 2.3 Region 3: `PRIVATE_CAPTURE_AND_CONSTRUCTOR_ONLY` (오프셋 179,655 ~ 183,010)
비공개 승인 선언 캡처 및 생성자 연결:
```csharp
        private readonly string? _approvedOriginId;
        private readonly string? _approvedLaunchPlanId;
        private readonly string? _approvedExpectedConfigId;
        private readonly string? _approvedExpectedRole;
        private readonly string? _approvedExpectedCapabilityBoundary;
        private readonly string? _approvedExpectedConfigPath;
        private readonly string? _approvedExpectedConfigSha256;

        internal string? ApprovedOriginId => _approvedOriginId;
        internal string? ApprovedLaunchPlanId => _approvedLaunchPlanId;
        internal string? ApprovedExpectedConfigId => _approvedExpectedConfigId;
        internal string? ApprovedExpectedRole => _approvedExpectedRole;
        internal string? ApprovedExpectedCapabilityBoundary => _approvedExpectedCapabilityBoundary;
        internal string? ApprovedExpectedConfigPath => _approvedExpectedConfigPath;
        internal string? ApprovedExpectedConfigSha256 => _approvedExpectedConfigSha256;

        internal OperatorStartupAdmissionReceipt(
            OperatorStartupConfigSnapshot snapshot,
            string boundConfigPath,
            string boundConfigSha256,
            string boundOriginId,
            string boundLaunchPlanId,
            string boundConfigId,
            string boundRole,
            string boundCapabilityBoundary,
            string admittedAtUtc,
            bool isTrusted)
            : this(snapshot, boundConfigPath, boundConfigSha256, boundOriginId, boundLaunchPlanId, boundConfigId, boundRole, boundCapabilityBoundary, admittedAtUtc, isTrusted, null)
        {
        }

        internal OperatorStartupAdmissionReceipt(
            OperatorStartupConfigSnapshot snapshot,
            string boundConfigPath,
            string boundConfigSha256,
            string boundOriginId,
            string boundLaunchPlanId,
            string boundConfigId,
            string boundRole,
            string boundCapabilityBoundary,
            string admittedAtUtc,
            bool isTrusted,
            OperatorLaunchDescriptor? approvedDeclaration)
        {
            ReceiptSchemaVersion = RECEIPT_SCHEMA_VERSION;
            Snapshot = snapshot ?? throw new ArgumentNullException(nameof(snapshot));
            BoundConfigPath = boundConfigPath ?? "";
            BoundConfigSha256 = boundConfigSha256 ?? "";
            BoundOriginId = boundOriginId ?? "";
            BoundLaunchPlanId = boundLaunchPlanId ?? "";
            BoundConfigId = boundConfigId ?? "";
            BoundRole = boundRole ?? "";
            BoundCapabilityBoundary = boundCapabilityBoundary ?? "";
            AdmittedAtUtc = admittedAtUtc ?? "";
            IsTrusted = isTrusted;

            if (approvedDeclaration != null)
            {
                _approvedOriginId = approvedDeclaration.originId;
                _approvedLaunchPlanId = approvedDeclaration.launchPlanId;
                _approvedExpectedConfigId = approvedDeclaration.expectedConfigId;
                _approvedExpectedRole = approvedDeclaration.expectedRole;
                _approvedExpectedCapabilityBoundary = approvedDeclaration.expectedCapabilityBoundary;
                _approvedExpectedConfigPath = approvedDeclaration.expectedConfigPath;
                _approvedExpectedConfigSha256 = approvedDeclaration.expectedConfigSha256;
            }
        }
```

### 2.4 Region 4: `RECEIPT_FACTORY_AND_VALIDATION_ONLY` (오프셋 193,303 ~ 211,955)
팩토리 사전 복제 검증 및 `ValidateAdmissionReceipt` 비공개 캡처 결속:
```csharp
        public static (bool isValid, string error, OperatorStartupAdmissionReceipt? receipt) IssueAdmissionReceipt(
            string configPath,
            string expectedConfigSha256,
            OperatorLaunchDescriptor descriptor)
        {
            if (descriptor == null)
            {
                return (false, "Operator launch descriptor cannot be null for receipt issuance.", null);
            }
            var desc = descriptor.Clone();
            // ... 7개 필드 완전성 및 경로/SHA 유효성 사전 검증 ...
            return IssueAdmissionReceiptFromBytes(rawBytes, normalizedConfigPath, expectedConfigSha256, desc);
        }

        public static (bool isValid, string error, OperatorStartupAdmissionReceipt? receipt) IssueAdmissionReceiptFromBytes(
            byte[] rawBytes,
            string configPath,
            string expectedConfigSha256,
            OperatorLaunchDescriptor descriptor)
        {
            if (descriptor == null) return (false, "Operator launch descriptor cannot be null.", null);
            var desc = descriptor.Clone();
            // ... 7개 필드 완전성 사전 검증 및 AdmitConfigBytes 수행 ...
            // ... snapshot id(ordinal), role, capabilityBoundary 검증 ...
            var receipt = new OperatorStartupAdmissionReceipt(
                snapshot: snapshot,
                boundConfigPath: normalizedConfigPath,
                boundConfigSha256: actualByteSha,
                boundOriginId: desc.originId,
                boundLaunchPlanId: desc.launchPlanId,
                boundConfigId: snapshot.ConfigId,
                boundRole: snapshot.Role,
                boundCapabilityBoundary: snapshot.CapabilityBoundary,
                admittedAtUtc: snapshot.IssuedAtUtc,
                isTrusted: true,
                approvedDeclaration: desc
            );
            return (true, string.Empty, receipt);
        }

        public static (bool isValid, string error) ValidateAdmissionReceipt(OperatorStartupAdmissionReceipt? receipt)
        {
            // ... 기존 11개 속성 기본 검증 ...
            if (string.IsNullOrWhiteSpace(receipt.ApprovedOriginId) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedLaunchPlanId) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedConfigId) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedRole) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedCapabilityBoundary) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedConfigPath) ||
                string.IsNullOrWhiteSpace(receipt.ApprovedExpectedConfigSha256))
            {
                return (false, "Receipt approved launch declaration is missing or incomplete (Fail-Closed).");
            }
            // ... 저장된 승인값과 BoundOriginId, BoundLaunchPlanId, BoundConfigId/Snapshot.ConfigId,
            //     BoundRole/Snapshot.Role, BoundCapabilityBoundary/Snapshot.CapabilityBoundary,
            //     정규화된 경로, SHA의 상호 결속 검증 ...
            return (true, string.Empty);
        }
```

---

## 3. 고정 바이너리 세그먼트 및 불변 파일 검증

| 바이너리 세그먼트 | 크기 (bytes) | SHA-256 | 일치 여부 |
| :--- | :--- | :--- | :--- |
| `WORKER_FIXED_SEGMENT_0.bin` | 1,126 | `C2BF7585213119BBC50694E4C1DA4201FF5D46268D03A9D158265BC76F06C230` | **100% 일치** |
| `WORKER_FIXED_SEGMENT_1.bin` | 171,771 | `75A2088E972BBFF1FF7B3CB17EE5E71E6A48D81E1808DEAC9BC85CE6842CEFAE` | **100% 일치** |
| `WORKER_FIXED_SEGMENT_2.bin` | 672 | `CC1EFBBC83817694BAAF715FF6951F59D02C1D08ADD15434ABF4D1FBF1B2F75C` | **100% 일치** |
| `WORKER_FIXED_SEGMENT_3.bin` | 10,293 | `EDFBD2D5B33413B75889F9E2C18AFDD71CACF2E3CE5D509709D9965EB290389E` | **100% 일치** |
| `WORKER_FIXED_SEGMENT_4.bin` | 14,756 | `E5CEDFB5EF16CD89DF4BB17C5FF6D820C0889D6A31BB58848841BEE8589A83FC` | **100% 일치** |

* **수정 후 `WorkerBridge.cs`**:
  * 크기: 226,714 bytes
  * SHA-256: `6AA281259A5760BFFFA432E392AC4480807E16C044EE599A7D31AD4BF6C10F1E`
* **동결 유지 대상**:
  * `EngineHostCensus.cs`: 170,135 bytes, SHA-256 `391F9645511A3E502B0F85A20C28A463DFE4647C8092B0D235F8E24CFFBC2F0D` (100% 보존)
  * `WorkerBridge.csproj`: 1,774 bytes, SHA-256 `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` (100% 보존)

---

## 4. 후보 바이너리 빌드 및 PE 메타데이터

`WorkerBridge.csproj`를 통해 `Release` 및 `Debug` 구성을 빌드했습니다. 경고 0개, 오류 0개로 빌드 완료되었습니다.

| 빌드 구성 | 아티팩트 | 크기 (bytes) | SHA-256 | MVID / CodeView PDB GUID |
| :--- | :--- | :--- | :--- | :--- |
| **Release** | `WarEconomy.WorkerBridge.PoC.dll` | 286,720 | `BF170758FE5998919A860A17A33F04A36780D5419D735D95D8518DF631783955` | MVID: `0ad5d962-8354-4049-9f25-6851185a3b8c`<br>CV GUID: `5bf238db-f840-4428-837e-56d866a4a6c5` |
| **Release** | `WarEconomy.WorkerBridge.PoC.pdb` | 53,076 | `A4C0947FDD7CC7901C20951F11DF82B38FE6DF6CF73E48CB0ABD22C6E54BDEC1` | - |
| **Debug** | `WarEconomy.WorkerBridge.PoC.dll` | 303,104 | `278DA55F46B3646F981E79EF83D764F19959B6FEFAD6EEC83AFD4DAB0020864D` | MVID: `3d7d7cf7-541a-42ec-a642-b31539cc3f3f`<br>CV GUID: `35fc949d-90a4-415c-a8bc-fd377c16b02e` |
| **Debug** | `WarEconomy.WorkerBridge.PoC.pdb` | 72,608 | `75C81993FEB72294789BB69E611FD3AFE7647D733568D405F1A672CF1DA74D84` | - |

* `scratch\WorkerBridgeMod\1.6\Assemblies\` 내의 `WarEconomy.WorkerBridge.PoC.dll` 및 `.pdb`는 Debug 후보 바이너리와 100% 동일하게 동기화되었습니다.

---

## 5. 순수 정상 통제 E1 러너 검증 결과

### 5.1 러너 아티팩트
* 러너 실행 파일: `scratch\EngineGate05R22Declaration\Harness\bin\Debug\net472\Gate05R22DeclarationRunner.exe`
* 러너 크기: 37,376 bytes
* 러너 SHA-256: `12F5C2D4D8D110669C83CD8C52CB5DE02123111F355BF9A9D9AEF21AA4225FB4`

### 5.2 테스트 스위트 세부 결과 (7/7 PASS)
1. **TEST01_ExplicitDeclarationDefaultsRemoval** (`PASS`):
   - `new OperatorLaunchDescriptor()`의 7개 필드가 모두 빈 문자열(`""`)로 초기화됨을 확인.
   - `Clone()` 호출 시 7개 필드가 정상 복제되며 원본 수정 시 클론에 영향이 없음을 확인.
2. **TEST02_MainEightAdmissionReceiptIssuance** (`PASS`):
   - 2개 역할(`SIMULATION`, `READ_ONLY`) × 2개 정책(`PLAIN`, `OPAQUE`) × 2개 방식(`File`, `Bytes`) = 8개 주요 영수증 발급.
   - 11개 공개 속성, nested snapshot 속성, `ValidateAdmissionReceipt(receipt)`, `receipt.IsValid()` 전수 통과.
   - `ToRedactedJson()` 출력에서 11개 필드 및 nested snapshot의 `.0000000Z` 문자열 보존 확인.
3. **TEST03_DeclarationAndReceiptCallerMutationProtection** (`PASS`):
   - 발급 완료된 8개 영수증에 대해 호출자의 `descriptor` 7개 필드를 모두 임의 변조한 후 재검증.
   - `ValidateAdmissionReceipt(receipt)` 및 `receipt.IsValid()`가 여전히 정상 `true`를 반환함을 확인 (비공개 캡처 격리 증명).
4. **TEST04_LiteralUtcPreservationRegression** (`PASS`):
   - 3개 포맷(`.0000000Z`, `.1234567Z`, `Z`)에 대한 6개 영수증 발급 및 `DateParseHandling.None` 검증 통과.
5. **TEST05_PositiveFullyQualifiedWindowsPathHelper** (`PASS`):
   - 드라이브 루트 및 UNC 유효 경로 5건에 대해 `IsFullyQualifiedWindowsPath` 정상 `true` 확인.
6. **TEST06_ValidatorResultRedactionRegression** (`PASS`):
   - `ValidatorResult.ToRedactedJson()`의 `[REDACTED_PROTECTED_OPERATOR_CAPABILITY]` 및 `[REDACTED_PROTECTED_CHANNEL_SECRET]` 마스킹 확인.
7. **TEST07_CensusPackagePolicyRegression** (`PASS`):
   - Plain 패키지 정책 라운드트립 및 OPAQUE 정책 다이제스트(`8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`) 일치 확인.

### 5.3 호스트 서브프로세스 텔레메트리 (`run_battery.py`)
* **Run 1 (`en-US`)**:
  - 자식 프로세스 PID: 25356
  - OS 종료 코드: 0
  - 소요 시간: 0.230초
  - 산출물 인벤토리: 18개 항목 정상 기록 (`OUTPUT_INVENTORY.json`)
* **Run 2 (`de-DE`)**:
  - 자식 프로세스 PID: 29248
  - OS 종료 코드: 0
  - 소요 시간: 0.132초
  - 산출물 인벤토리: 18개 항목 정상 기록 (`OUTPUT_INVENTORY.json`)
* **격리 및 불변성 검증**:
  - Run 1 산출물 해시가 Run 2 실행 후에도 100% 동일 유지 (`isolation_verified: true`).
  - 러너 실행 파일 실행 전/후 무결성 일치 (`runner_unmodified: true`).

---

## 6. 호출 카운트 회계 (API Ledger)

```json
{
  "ParseStrict": 0,
  "AdmitConfigBytes": 0,
  "AdmitConfigFile": 0,
  "IssueAdmissionReceipt": 10,
  "IssueAdmissionReceiptFromBytes": 4,
  "ValidateAdmissionReceipt": 16,
  "IsFullyQualifiedWindowsPath": 5,
  "ToSnapshot": 0,
  "ToRedactedJsonSnapshot": 0,
  "ToRedactedJsonReceipt": 14,
  "ToRedactedJsonValidatorResult": 1,
  "SerializePackagePolicy": 1,
  "DeserializePackagePolicy": 1,
  "ComputePackagePolicyDigest": 2,
  "ProcessApiCalls": 0,
  "VerifyProcessIdentityCalls": 0,
  "WorkerBridgeGlobalConfigureResetCalls": 0,
  "TryInstallOperatorStartupConfigCalls": 0,
  "AwakeCalls": 0,
  "HarmonyCalls": 0
}
```

---

## 7. 한계 및 거버넌스 준수 (Limitations)

1. **정적 관리형 정상 제어 증거 한정**: 모든 검증은 격리된 순수 관리형 러너(7/7 PASS)를 통해 수행되었습니다.
2. **C# Process API 0건**: 러너 내부에서 Process API 일체 미호출, 자식 PID 및 종료 코드는 호스트 Python 텔레메트리로만 수집되었습니다.
3. **네이티브/게임 엔진 미실행**: 인게임 런타임, Awake 루프, 네이티브 실행, 운영자 권한 승격은 엄격히 금지되었으며 실행되지 않았습니다.
4. **부정/거부 프로브 배제**: WP 지침에 따라 무효/거부 프로브는 실행되지 않았으며, fail-closed 동작은 소스 코드 리뷰로 한정됩니다.
5. **도메인 권위 유지**: Dedicated Server가 최종 도메인 권위(Final Domain Authority)이며, 클라이언트/엔진은 경계 시뮬레이션 제안만을 생성합니다.
6. **Foundation HOLD 유지**: Sol 독립 QA 및 Master 거버넌스 승인 전까지 전체 Gate05 및 Foundation은 HOLD 상태를 유지합니다.
