# POC EngineHost Semantic Authority Gate 05 R21 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R21_RECEIPT_UTC_LITERAL / GATE05-R21-RECEIPT-UTC` (Envelope 24)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-11
- **E1 Verdict**: `IMPLEMENTED_SCOPED_RECEIPT_UTC_LITERAL_PASS_NATIVE_UNTESTED`

---

## 1. 개요 및 기술 목표

### 1.1 Master R20 검토 및 배경
Master의 R20 검토 및 Sol 독립 QA 결과(`MASTER_REVIEW_ENGINE_GATE05_R20_TRUSTED_STARTUP_INDEPENDENT_S1_20261011.md`, `QA_EngineHost_Gate05_R20_Trusted_Startup_Independent_S1_20261011.md`, Envelope 24) 및 R21 작업 명세(`WP_ENGINE_GATE05_R21_RECEIPT_UTC_LITERAL.md`)에 따라, 다음 핵심 원칙과 제약사항을 준수합니다:
1. **R20 결함의 극소 범위 한정 (Single Scoped Repair)**:
   - R20 독립 QA에서 지적된 유일한 결함은 `OperatorStartupAdmissionReceipt.ToRedactedJson` 내부에서 `JObject.Parse(Snapshot.ToRedactedJson())`를 호출할 때 기본 `DateParseHandling.DateTime` 설정에 의해 ISO-8601 날짜 문자열이 Date 토큰으로 강제 변환되어 `snapshot.issuedAtUtc`의 원래 문자열 정밀도(예: `.0000000Z`)가 손실된 점이었습니다.
   - 본 R21에서는 오직 `OperatorStartupAdmissionReceipt.ToRedactedJson` 내부에서 `Newtonsoft.Json.JsonTextReader`와 `DateParseHandling = DateParseHandling.None`을 명시적으로 설정하여 `snapshot.issuedAtUtc`의 원문 문자열을 100% 무손실 보존합니다.
2. **전후 접두/접미 바이트 100% 동결 (Strict Prefix/Suffix Byte Match)**:
   - `WorkerBridge.cs`의 수정 대상 메서드 이전 영역(`WORKER_FIXED_PREFIX.bin`, 0 ~ 179,745 오프셋, 크기 179,745 bytes, SHA-256 `D8502FC0A667DC819F62898885A6AA15618B17D3DD09D2F7DCDD237C7C7CE9F4`)과 이후 영역(`WORKER_FIXED_SUFFIX.bin`, 180,561 ~ 끝 오프셋, 크기 33,242 bytes, SHA-256 `1F4D372F0366DA5F44A3EA34A094BC997812C511D64A3F9E7BEFC37914BBCAA8`)을 바이트 단위로 100% 불변 보존했습니다.
   - `EngineHostCensus.cs` (크기 170,135 bytes, SHA `391F9645...`) 및 `WorkerBridge.csproj` (크기 1,774 bytes, SHA `571A58F5...`) 역시 100% 불변 유지되었습니다.
3. **긍정 정상 제어만 수행 (Positive Normal Controls Only)**:
   - R20의 `TEST_05`에서 수행되었던 7개 상대/무효 경로 거부 프로브를 전면 제거하고, 오직 유효한 절대 경로 및 정상 배터리만을 검증하는 순수 긍정 제어 환경을 구축했습니다.
   - 무효/거부/예외/부정 프로브는 일절 실행하지 않았습니다.
4. **C# Process API 호출 0건 및 호스트 텔레메트리 분리**:
   - 관리형 러너 내부에서 `Process.Start`, `Process.GetCurrentProcess`, `VerifyProcessIdentity` 등 프로세스 관련 C# API 일절 미호출.
   - 호스트 Python 오케스트레이터(`run_battery.py`)를 통해 독립 프로세스로 기동된 자식 PID와 OS 종료 코드만을 수집.
5. **스트림 닫힘 및 인벤토리 완전성**:
   - `stdout.txt` 및 `stderr.txt` 파일 핸들을 명시적으로 닫은 후 `OUTPUT_INVENTORY.json`을 작성하여 모든 산출물이 인벤토리에 100% 포함됨을 보장했습니다.

---

## 2. 소스 변경 및 9개 Engine 경로 보존 상태

### 2.1 OperatorStartupAdmissionReceipt.ToRedactedJson 변경 상세
```csharp
        public string ToRedactedJson()
        {
            Newtonsoft.Json.Linq.JObject? snapshotObject = null;
            if (Snapshot != null)
            {
                using (var stringReader = new System.IO.StringReader(Snapshot.ToRedactedJson()))
                using (var jsonReader = new Newtonsoft.Json.JsonTextReader(stringReader))
                {
                    jsonReader.DateParseHandling = Newtonsoft.Json.DateParseHandling.None;
                    snapshotObject = Newtonsoft.Json.Linq.JObject.Load(jsonReader);
                }
            }

            var redacted = new
            {
                receiptSchemaVersion = ReceiptSchemaVersion,
                isTrusted = IsTrusted,
                boundOriginId = BoundOriginId,
                boundLaunchPlanId = BoundLaunchPlanId,
                boundConfigId = BoundConfigId,
                boundRole = BoundRole,
                boundCapabilityBoundary = BoundCapabilityBoundary,
                boundConfigPath = BoundConfigPath,
                boundConfigSha256 = BoundConfigSha256,
                admittedAtUtc = AdmittedAtUtc,
                snapshot = snapshotObject
            };
            return JsonConvert.SerializeObject(redacted, Newtonsoft.Json.Formatting.Indented);
        }
```
- `Snapshot != null`인 경우, `StringReader` 및 `JsonTextReader`를 생성하고 `DateParseHandling = DateParseHandling.None`을 설정하여 날짜 토큰으로의 자동 파싱을 방지했습니다.
- 그 결과, `snapshot.issuedAtUtc`는 원래의 문자열 토큰(`JTokenType.String`) 그대로 보존되어 `.0000000Z` 등 어떠한 어휘적 정밀도 손실도 발생하지 않습니다.
- 독점 11개 프로퍼티 구성, 포매팅, 익명 객체 구조는 완벽히 유지되었습니다.

### 2.2 9개 Engine 경로 변경 및 보존 상태
| 파일 경로 | 상태 | 크기 (Bytes) | SHA-256 |
| :--- | :--- | :--- | :--- |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` | **MODIFIED** | 214,277 | `CD3FBAB2F3BEA22A2E81B8687352451CC695D477069FE1A788291A78A6F85E5D` |
| `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` | **IMMUTABLE** | 170,135 | `391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1` |
| `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` | **IMMUTABLE** | 1,774 | `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` |
| `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Debug)** | 295,424 | `31D7A2508ACFADE1B9430F43E6F3D2ACF3E9822C787D00DAF55C9E44CF8E5AC4` |
| `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Debug)** | 71,192 | `84C1F2D2BC339DFD00A9BBA29AEA655E92CBD6F77C64A27D0D54A4433370CDD8` |
| `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Debug)** | 295,424 | `31D7A2508ACFADE1B9430F43E6F3D2ACF3E9822C787D00DAF55C9E44CF8E5AC4` |
| `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Debug)** | 71,192 | `84C1F2D2BC339DFD00A9BBA29AEA655E92CBD6F77C64A27D0D54A4433370CDD8` |
| `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll` | **REBUILT (Release)** | 279,552 | `A2C4C5AD66E082C5F7BEC25A91FA8E7B237121398B94A59E5D60E3B401D0F840` |
| `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb` | **REBUILT (Release)** | 52,172 | `41330A059B468E9011C284068AAF0DA100EA7C5CBC1DCDCB56802E797E0E3A1E` |

- `EngineHostCensus.cs` 접두사 검증: 길이 72,547 bytes, SHA-256 `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (**100% 불변 확인**).

### 2.3 PE MVID 및 CodeView 바인딩 정보
- **Debug Candidate DLL**:
  - SHA-256: `31D7A2508ACFADE1B9430F43E6F3D2ACF3E9822C787D00DAF55C9E44CF8E5AC4`
  - MVID: `7a8b444a-3a07-4dee-9d37-4fa7ed3c461c`
  - CodeView Path: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
  - CodeView GUID: `8d435f4d-06a1-4b6a-a50a-b2fa31d92bbb`
  - CodeView Age: `1`
- **Release Candidate DLL**:
  - SHA-256: `A2C4C5AD66E082C5F7BEC25A91FA8E7B237121398B94A59E5D60E3B401D0F840`
  - MVID: `28abd2eb-3220-4e97-aa99-c4ff1edb5900`
  - CodeView Path: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
  - CodeView GUID: `1123d112-6825-4f2d-9f34-54aaf6c32f03`
  - CodeView Age: `1`

---

## 3. Detached Pure Runner 검증 및 호스트 프로세스 격리 실행

### 3.1 러너 아키텍처 및 무결성 보장
- 프로젝트: `scratch\EngineGate05R21ReceiptUtc\Harness\Gate05R21ReceiptUtcRunner.csproj`
- 러너 바이너리: `scratch\EngineGate05R21ReceiptUtc\Harness\bin\Debug\net472\Gate05R21ReceiptUtcRunner.exe` (SHA `B5FC0260440B29E5631148F1682BF952B35CF96B6C2C5204C66F1DB73D83F6E9`, 크기 40,448)
- 러너 PDB: `scratch\EngineGate05R21ReceiptUtc\Harness\bin\Debug\net472\Gate05R21ReceiptUtcRunner.pdb` (SHA `CA04C13A0166A1D392698611A832C432AC86999F57199BECE69405FC4E438415`, 크기 9,484)
- **호스트 Python 오케스트레이터 (`run_battery.py`) 배터리 실행**:
  - `en-US` 문화권: 자식 PID 15684, Exit Code 0, 소요시간 0.276초, 7/7 PASS.
  - `de-DE` 문화권: 자식 PID 32936, Exit Code 0, 소요시간 0.165초, 7/7 PASS.
  - **격리 무결성 검증**: Run 1 완료 후 산출된 17개 파일을 인벤토리에 등록하고, Run 2 완료 후 Run 1의 파일들을 재해싱하여 100% 바이트 불변임을 확인 (`isolation_verified: true`).
  - **스트림 인벤토리 닫힘 보장**: `stdout.txt` 및 `stderr.txt`를 명시적으로 flush/close한 후 `OUTPUT_INVENTORY.json`을 작성하여 인벤토리 누락 0건 확인.

### 3.2 테스트 항목별 검증 결과 (7/7 PASS)
1. **TEST_01_OPAQUE_POLICY_LOSSLESS_PRESERVATION (PASS, 16/16 Matrix)**:
   - 2개 역할(`SIMULATION`, `READ_ONLY`) × 2개 정책(`PLAIN`, `OPAQUE`) × 4개 경로(`SnapshotDirectConstructor`, `ToSnapshot`, `AdmitConfigBytes`, `AdmitConfigFile`) 전수 검증.
   - 불투명 식별자 `"  qa.R18 정책 Ω  "` 및 리비전 `"  007 café Ω  "`의 앞뒤 공백 및 유니코드 문자가 트리밍 없이 원본 그대로 보존됨을 확인.
   - 계산된 원시 선언 다이제스트 `8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF`가 16개 경로 전체에서 100% 동일하게 산출됨을 확인.
2. **TEST_02_ADMISSION_RECEIPT_ISSUANCE_AND_BOUND_PROVENANCE (PASS, 8/8 Routes)**:
   - 2개 역할 × 2개 정책 × 2개 방식(`IssueAdmissionReceipt` 파일 경로, `IssueAdmissionReceiptFromBytes` 바이트 배열) = 8개 경로 전수 통과.
   - `ReceiptSchemaVersion == "WE-OPERATOR-RECEIPT-V1"`, `IsTrusted == true`, `IsValid() == true` 확인.
   - 모든 결속 프로버넌스 필드(`BoundOriginId`, `BoundLaunchPlanId`, `BoundConfigId`, `BoundRole`, `BoundCapabilityBoundary`, `BoundConfigPath`, `BoundConfigSha256`) 정합성 확인.
3. **TEST_03_RECEIPT_REDACTED_JSON_EXACT_LITERAL_UTC_PRESERVATION (PASS, 3/3 UTC Variants)**:
   - `2026-10-10T00:00:00.0000000Z` (나노초 7자리 0 정밀도), `2026-10-11T05:30:15.1234567Z` (분수 초), `2026-10-11T12:00:00Z` (정수 초) 3개 대표 케이스 전수 검증.
   - 영수증 직렬화 결과(`ToRedactedJson()`) 내부에서 `snapshot.issuedAtUtc`가 Date 토큰으로 변환되지 않고 정확한 원문 문자열 리터럴로 보존됨을 확인 (`token.Type == JTokenType.String`, 원문 일치 확인).
4. **TEST_04_DECLARATION_AND_RECEIPT_DEFENSIVE_IMMUTABILITY (PASS)**:
   - 영수증 발행 후 호출자의 `OperatorLaunchDescriptor` 속성을 사후 변조하더라도 이미 발행된 영수증의 결속 필드에 일절 영향이 없음을 확인.
   - `launchDesc.Clone()` 호출 시 독립된 복제본이 생성됨을 확인.
   - 영수증 스냅샷의 패키지 정책 리스트 변조 시도시 내부 격리 유지 확인.
5. **TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_POSITIVE_HELPER (PASS, 5/5 Positive Paths)**:
   - 긍정 정상 제어만 검증: DOS 드라이브 루트(`C:\`, `D:/`) 및 UNC 공유 루트(`\\server\share\`)는 정상 승인(5/5 통과). 무효/상대 경로 거부 프로브 0건.
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
  "IssueAdmissionReceiptCalls": 8,
  "IssueAdmissionReceiptFromBytesCalls": 4,
  "ValidateAdmissionReceiptCalls": 8,
  "IsFullyQualifiedWindowsPathCalls": 5,
  "ToSnapshotCalls": 4,
  "ToRedactedJsonSnapshotCalls": 0,
  "ToRedactedJsonReceiptCalls": 3,
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
   - 본 검증은 분리된 순수 관리형 테스트 환경에서 정상 제어 경로만을 대상으로 수행됨 (7/7 PASS, 16/16 매트릭스 PASS, 8/8 영수증 배터리 PASS, 3/3 UTC 리터럴 PASS, exit 0).
2. **ZERO_PROCESS_API_CALLS_IN_MANAGED_TESTS**:
   - 관리형 러너 코드 내에서 `Process.Start`, `Process.GetCurrentProcess`, `VerifyProcessIdentity` 일절 미호출.
3. **HOST_PYTHON_TELEMETRY_CHILD_PID_AND_EXIT_CODE_ONLY**:
   - 호스트 서브프로세스 텔레메트리는 운영상 관측 기록이며 네이티브 권위가 아님.
4. **NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED**:
   - 림월드 게임 루프, Unity 씬 기동, 네이티브 실행, Awake 이벤트 루프, 오퍼레이터 프로모션은 본 WP에서 명시적으로 금지되었으며 실행되지 않음.
5. **ZERO_INVALID_OR_REJECTION_PROBES**:
   - R21 작업 지침에 따라 모든 무효/거부/예외 프로브는 일절 실행하지 않았으며, Fail-closed 경로는 정적 소스 분석으로만 확인됨.
6. **INSTALLED_DLL_INCIDENT_OPEN**:
   - Steam 설치 경로의 DLL과 아카이브 간 해시 불일치 인시던트는 원인 미상의 오픈 상태로 유지되며 임의 변경하지 않음.
7. **FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER**:
   - 전용 서버(Dedicated Server)가 최종 도메인 권위이며, 엔진/클라이언트는 한정된 시뮬레이션 제안만을 생성함.
8. **FOUNDATION_HOLD**:
   - Foundation 파이프라인 E2 PASS 전까지 전체 Foundation 및 릴리스는 HOLD 상태를 유지함.
