# POC EngineHost Content Codec Gate 05 R15 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY / GATE05-R15-PUBLIC-MANIFEST-BOUNDARY` (Envelope 18)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-09
- **E1 Verdict**: `SCOPED_POSITIVE_NORMAL_PASS` (Public Manifest Boundary, Single Trusted Provider Success Linearization, Sealed Caller-Policy Collector & Standalone Matching Core Pure Normal Controls 25/25 PASS; Native Actual Computation Prohibited/Untested per Scope Boundary)

---

## 1. 개요 및 기술 목표

### 1.1 R14 독립 QA(S1) 성과 크레딧 및 R15 착수 배경
Gate05-R14 독립 QA(Sol S1) 평가에서 정책 캡처, 캐시 발행 예외 처리, `InvalidateCache()` 시 세대 전진(`+1`) 및 독립 코어 수명주기 통제가 정상 PASS로 확인되었습니다. R14의 339개 독립 정상 통제 성과는 과거 성과로 온전히 인정(Credit)되나, R15 신규 후보는 이전 PASS를 자동 상속하지 않으며 독립적인 E1 검증을 요구합니다.

R14 분석 결과, 공개 API 경계에서 다음과 같은 단일 기술적 결함이 식별되었습니다:
1. **공개 매개변수 없는 매니페스트 성공 경로의 검증 누락**:
   - `ComputeActualContentProfileManifest()`가 상태 스냅샷을 캡처한 후 실제 수집기 결과를 직접 반환하면서, 최종 현재 스탬프(`current-stamp`) 및 현재 구성 정책과의 일치 여부를 검증하지 않고 성공 결과를 반환함.
2. **임의 호출자 정책 수집기 공개 노출**:
   - `ComputeActualContentProfileManifest(ExpectedPackagePolicyRecord capturedPolicy)`가 공개(`public`) 오버로드로 노출되어, 호출자가 임의의 정책 객체를 주입하여 전역 프로바이더의 기원/스탬프와 무관하게 네이티브 수집을 트리거할 수 있는 우회로가 존재함.
3. **지문과 매니페스트의 성공 선형화 불일치**:
   - `ComputeActualContentProfileFingerprint()`는 발행 실패를 검증하여 차단하는 반면, 매니페스트는 검증 없이 반환될 수 있어 두 공개 엔트리 포인트 간 일관된 성공 보장이 부재함.

### 1.2 R15 단일 목표 (`PUBLIC_MANIFEST_BOUNDARY`)
Master 승인 지침(`WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.md`, Envelope 18)에 따라 다음 한 가지 목표(`PUBLIC_MANIFEST_BOUNDARY`)만을 한정 구현하였습니다:
1. **임의 호출자 정책 수집기 공개 경로 차단 및 내부 봉인**:
   - `ComputeActualContentProfileManifest(ExpectedPackagePolicyRecord)` 공개 오버로드를 완전히 제거.
   - 실제 수집 로직은 내부 전용 `private static ContentProfileManifest CollectActualContentProfileManifestInternal(ExpectedPackagePolicyRecord capturedPolicy)`로 봉인하여 외부 호출자의 임의 정책 주입 수집을 원천 차단.
2. **단일 신뢰 프로바이더 계산 및 성공 선형화 경계 (`Single Synchronized Success Linearization`)**:
   - 매개변수 없는 두 공개 엔트리 포인트(`ComputeActualContentProfileManifest()`, `ComputeActualContentProfileFingerprint()`)는 동일한 내부 실행 메서드(`ComputeAndPublishActualContentProfile()`)를 공유.
   - 연산 시작 시 프로세스 로컬 스냅샷(`long generation`, `ExpectedPackagePolicyRecord policy`)을 1회 캡처하고, 수집/정규화/JSON/해시 생성 후 단일 코어 동기화 락 하에서 현재 프로바이더 상태(세대 및 구성 정책 다이제스트)와 캡처된 스탬프의 동일성을 검증.
   - 현재 스탬프 검증 및 캐시 발행 실패 시 명시적 예외(`InvalidOperationException`)를 던져 비정상/무효화된 결과의 성공 반환을 원천 차단 (경고 후 성공 반환/폴백/재조회 금지).
   - 계산 결과는 소유된 매니페스트, 정규 JSON, 지문 및 발행 엔트리를 포함하는 `ComputedContentProfileResult` 객체로 반환되어 두 공개 API가 동일한 검증 성공 결과를 소비.
3. **불변 상태 및 세대 규약 보존**:
   - R14의 `InvalidateCache()` 시 세대 전진(`_generation++`), 순수 코어 소유권, 방어적 복사, 순수 코덱 로직 온전히 유지.
   - `SetComputationError(long capturedGeneration, string? error)`를 도입하여 이전 세대의 지연된 계산 오류가 현재 세대의 오류 상태를 덮어쓰지 않도록 세대 범위 격리 적용.
4. **버전 및 기능 식별자 갱신**:
   - `CONTENT_CONTRACT_VERSION`: `"ADR-006B-v5-R15"`
   - `CONTENT_CAPABILITY_FLAGS`: `"GATE05_R15_PUBLIC_MANIFEST_BOUNDARY"`
5. **엄격한 정상 범위 한정 및 금지 사항 준수**:
   - 독립 순수 인스턴스 코어(`ContentProfileCacheCore`)의 정상 일치 발행, 유효 구성, 무효화, 방어적 복사, 공개 인터페이스 리플렉션 검사 및 정상 회귀(R12 순서, R11 인코딩, R9 버전)만을 검증 (25/25 PASS).
   - 실제 `ComputeActual*`, `GetActual*`, 게임/네이티브/오퍼레이터 실행, 음성/적대적/경합 테스트는 엄격히 금지 및 미실행.

---

## 2. 소스 불변성 및 후보 바이너리 메타데이터

### 2.1 소스 무결성 검증
- `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 접두부 72,547 bytes SHA-256: `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (**100% 불변 일치**)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`: SHA-256 `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718` (156,431 bytes, **100% 불변 보존**)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj`: SHA-256 `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` (1,774 bytes, **100% 불변 보존**)

### 2.2 빌드 결과 및 PE/PDB 메타데이터
- **빌드 상태**: Release 및 Debug 모두 경고 0, 오류 0으로 정상 완료.
- **Debug DLL** (Selected Candidate):
  - 경로: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
  - SHA-256: `835E81216B850B571577677AB724FAC9A515465F79888A5CACC13C51FF832877`
  - 크기: 244,224 bytes
  - MVID: `4fb1a25f-72c8-426d-b93f-d6cba4f9af72`
  - 매칭 PDB SHA-256: `0CBC164CDAF5AD188C71E28C9AED664F066950ACEA3CE09B5F8238DAAF9630BE` (62,416 bytes)
- **Release DLL** (Alternate Candidate):
  - 경로: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
  - SHA-256: `4D198076B84C3FC44EEB75CBE22FE1A2575659009293FBA7E14E937996DD0358`
  - 크기: 231,936 bytes
  - MVID: `58766cdc-afee-4682-858a-dab68c96e36e`
  - 매칭 PDB SHA-256: `9BC98A4A92D7E2FA0051DCE46ED03E98CDC2A014449AA32FDDAB3DF0A9FCEE15` (45,808 bytes)
- **배포 어셈블리** (`1.6\Assemblies\`):
  - Debug 바이너리 및 매칭 PDB와 100% 일치 동기화 (`835E81...` / `0CBC16...`).

---

## 3. 순수 긍정적 정상 관리형 하네스 검증 (25/25 PASS)

신규 독립 러너 `scratch\EngineGate05R15PublicManifestBoundary\Harness\Gate05R15BoundaryRunner.exe`를 구축하고, 동결 관리 의존성(`FROZEN_MANAGED_QA_DEPENDENCIES_V1`)을 참조하여 25건의 순수 정상 통제 케이스를 실행하였습니다:

| 번호 | 테스트 케이스 ID | 분류 | 요약 | 결과 |
|---|---|---|---|---|
| TC01 | `TC01_Provider_InitialState_Unconfigured_Diagnostics` | Category1_ProviderLifecycle | 전역 프로바이더 미구성 초기 상태 진단 (IsCached=false, generation=0 등) | **PASS** |
| TC02 | `TC02_Provider_ConfigurePolicy_MonotonicGenerationAdvance` | Category1_ProviderLifecycle | 전역 프로바이더 정책 구성 시 세대 단조 증가(0->1) 및 구성 바인딩 검증 | **PASS** |
| TC03 | `TC03_Provider_ReconfigureSamePolicy_AdvancesGeneration` | Category1_ProviderLifecycle | 동일 정책 재구성 시 세대 단조 증가(1->2) 검증 | **PASS** |
| TC04 | `TC04_Provider_ExplicitInvalidate_AdvancesGeneration` | Category1_ProviderLifecycle | R15 명시적 InvalidateCache 호출 시 세대 +1 증가(2->3) 및 캐시 해제 검증 | **PASS** |
| TC05 | `TC05_Provider_ClearConfiguredPolicy_AdvancesGeneration` | Category1_ProviderLifecycle | ClearConfiguredExpectedPackagePolicy 호출 시 세대 증가(3->4) 및 정책 해제 | **PASS** |
| TC06 | `TC06_StandaloneCore_InitialState_Clean` | Category2_StandaloneCacheCoreLifecycle | 독립 인스턴스 코어 초기화 시 세대 0, 미구성, 빈 캐시 진단 | **PASS** |
| TC07 | `TC07_StandaloneCore_ConfigurePolicy_GenerationAdvance` | Category2_StandaloneCacheCoreLifecycle | 독립 코어 정책 구성 시 세대 1 전진 및 정책 레코드 바인딩 | **PASS** |
| TC08 | `TC08_StandaloneCore_CaptureStateSnapshot_MatchesGenerationAndPolicy` | Category2_StandaloneCacheCoreLifecycle | CaptureStateSnapshot이 현재 세대(1) 및 복제된 불변 정책을 반환함을 검증 | **PASS** |
| TC09 | `TC09_StandaloneCore_PublishCoherentEntry_NormalMatching_Success` | Category2_StandaloneCacheCoreLifecycle | 세대/정책 일치 엔트리 정상 발행 성공, IsCached=true, 핑거프린트/정규 JSON 일치 | **PASS** |
| TC10 | `TC10_StandaloneCore_TryGetCoherentEntry_ReturnsMatchingSnapshot` | Category2_StandaloneCacheCoreLifecycle | TryGetCoherentEntry가 불변 스냅샷을 반환하며 R15 계약 버전 확인 | **PASS** |
| TC11 | `TC11_StandaloneCore_DefensiveManifestImmutability_ResistsCallerMutation` | Category2_StandaloneCacheCoreLifecycle | CachedManifest 조회 결과 변조 시 내부 캐시 불변 보장 (방어적 복사) | **PASS** |
| TC12 | `TC12_StandaloneCore_InvalidateCache_AdvancesGeneration_ClearsEntry` | Category2_StandaloneCacheCoreLifecycle | 코어 InvalidateCache 호출 시 세대 1->2 전진 및 캐시 엔트리 즉시 무효화 | **PASS** |
| TC13 | `TC13_StandaloneCore_ReconfigureToNewPolicy_AdvancesGeneration_ClearsOldCache` | Category2_StandaloneCacheCoreLifecycle | 신규 정책 재구성 시 세대 전진 및 이전 캐시 완전 초기화 검증 | **PASS** |
| TC14 | `TC14_StandaloneCore_PublishNewPolicyEntry_NormalMatching_Success` | Category2_StandaloneCacheCoreLifecycle | 신규 정책 엔트리 정상 발행 성공 및 캐시 갱신 검증 | **PASS** |
| TC15 | `TC15_StandaloneCore_TryPublishComputedEntry_ReturnsPublishedEntryDirectly` | Category2_StandaloneCacheCoreLifecycle | R15 TryPublishComputedEntry 오버로드가 out 파라미터로 동기화 락 하에서 발행 엔트리를 직접 반환함을 검증 | **PASS** |
| TC16 | `TC16_StandaloneCore_SetComputationError_GenerationScoped_Protection` | Category2_StandaloneCacheCoreLifecycle | R15 SetComputationError(capturedGen)가 세대 전진 후의 구 스냅샷 오류 기록을 차단함을 검증 | **PASS** |
| TC17 | `TC17_R12_PackageOrder_LoadOrderZeroBasedSorting` | Category3_Regressions | R12 회귀: 0-based 연속 loadOrder 정렬 정상 동작 검증 | **PASS** |
| TC18 | `TC18_R12_PackageOrder_PhysicalPermutationInvariance` | Category3_Regressions | R12 회귀: 물리적 치환 배열 정규 승인 시 동일 정규 JSON 및 동일 핑거프린트 | **PASS** |
| TC19 | `TC19_R12_PackageOrder_DistinctValidSequences_MatchSeparatePolicies` | Category3_Regressions | R12 회귀: 고유한 실행 순서가 각각 고유한 정책과 정상 매칭 (긍정 통제만 실행) | **PASS** |
| TC20 | `TC20_R12_PackageOrder_FreshOriginal_SerializeTrue_BeforeAdmission` | Category3_Regressions | R12 회귀: 외부 승인 전 원본 직렬화 시 loadOrder 정렬 보장 | **PASS** |
| TC21 | `TC21_R11_PolicyDeclaration_Encoding_Whitespace_Unicode_Digest` | Category3_Regressions | R11 회귀: 컴팩트 JSON, 불투명 식별자 공백/유니코드 보존, SHA-256 다이제스트 | **PASS** |
| TC22 | `TC22_R9_VersionMeaningSemantics` | Category3_Regressions | R9 회귀: modVersion null/빈문자열/명시값 보존 | **PASS** |
| TC23 | `TC23_ContractVersion_And_CapabilityFlag` | Category3_Regressions | ADR-006B-v5-R15 계약 버전 및 GATE05_R15_PUBLIC_MANIFEST_BOUNDARY 플래그 검증 | **PASS** |
| TC24 | `TC24_DefFamilies_CanonicalSorting` | Category3_Regressions | Def 패밀리 결정론적 순서 정렬 정상 동작 검증 | **PASS** |
| TC25 | `TC25_Reflection_SealedCallerPolicyCollector_NoPublicOverload` | Category3_Regressions | 리플렉션 검증: 공개 호출자 정책 수집기 오버로드가 완전히 제거/봉인되었으며 매개변수 없는 엔트리만 공개됨을 검증 | **PASS** |

### 3.1 다중 프로세스 및 다중 문화권 격리 검증
각 프로세스는 고유의 격리 디렉터리(`run_default`, `run_en_us`, `run_de_de`)에서 독립 실행되었으며, 실행 직후 디렉터리 전체 출력물 인벤토리(`OUTPUT_INVENTORY.json`)를 동결하여 상호 간섭을 원천 배제하였습니다:

1. **`run_default`** (`ko-KR`, PID 24440):
   - 종료 코드: **0** (283ms)
   - 결과: 25/25 PASS (0 FAIL)
   - 인벤토리 SHA-256: `660D8A3C38DA820F2D852477CC5167D98A4E38C8B144A3EE1A24DAE0958E7038`
2. **`run_en_us`** (`en-US`, PID 2432):
   - 종료 코드: **0** (117ms)
   - 결과: 25/25 PASS (0 FAIL)
   - 인벤토리 SHA-256: `66E401A2403E9632853B1A190C5AB006A49213B43FA5D623D75B14E2783A86B1`
3. **`run_de_de`** (`de-DE`, PID 33632):
   - 종료 코드: **0** (120ms)
   - 결과: 25/25 PASS (0 FAIL)
   - 인벤토리 SHA-256: `1F16CD48C3A54382AAEF20528B243F77070CAA87092A9F311C6C1402D9949DA1`

### 3.2 정밀 캐시 회계 및 명시적 API 원장
- **총 정상 캐시 수명주기 호출**: **55회**
  - `normal_provider_configure_calls`: 2회
  - `normal_provider_clear_calls`: 2회
  - `normal_provider_invalidate_calls`: 1회
  - `normal_provider_diagnostics_calls`: 15회
  - `normal_core_instance_creations`: 11회
  - `normal_core_configure_calls`: 11회
  - `normal_core_publish_calls`: 7회
  - `normal_core_query_calls`: 12회
  - `normal_core_invalidate_calls`: 2회
  - `normal_core_error_calls`: 3회
- **금지 경로 호출**: **0회**
  - `prohibited_compute_calls`: 0
  - `prohibited_getactual_calls`: 0
  - `prohibited_native_calls`: 0
  - `prohibited_adverse_calls`: 0
- **API 호출 원장(`api_ledger.json`)**: 각 테스트 단계별로 호출 대상, 메서드명, 분류 및 결과를 42개 시퀀스로 누락 없이 상세 기록.

---

## 4. 실행 범위 한정 및 금지 사항 준수

1. **실제 연산 및 네이티브 실행 미수행**:
   - `GetActualContentProfileFingerprint`, `ComputeActualContentProfileFingerprint`, `ComputeActualContentProfileManifest`의 관리되지 않는 하네스 직접 실행을 전면 배제하였습니다.
   - 게임 엔진 런타임(`Verse.Game`, `DefDatabase`) 호출, 네이티브 실행, 오퍼레이터 프로모션은 수행되지 않았습니다.
2. **부정/거부/지연/경합 테스트 전면 배제**:
   - 구 R13 TC13(지연 세대 거부) 및 TC19(교차 정책 불일치 거부) 등 실패를 유도하는 테스트를 일체 실행하지 않았습니다.
3. **전역 캐시 임의 조작 배제**:
   - 전역 프로바이더의 내부 필드 리플렉션 주입이나 임의 시딩을 일체 수행하지 않았습니다.

---

## 5. 권위 원칙 및 한계점 명시

1. **최종 권위**: Dedicated Server가 최종 도메인 권위(Domain Authority)이며, 릴리스 승인 및 게이트 종결(Closure)은 Master 관할입니다. 개발자 A는 자체 릴리스나 클로저를 선언하지 않습니다.
2. **Foundation 상태**: Foundation 파이프라인은 E2 PASS 전까지 HOLD 상태를 엄격히 유지합니다.
3. **Steam 설치 DLL 미해결 이슈**: Steam 설치 DLL(`BB3B52...`) 불일치 인시던트는 `UNKNOWN OPEN INCIDENT`로 유지되며, 임의 복원이나 설치 덮어쓰기를 수행하지 않았습니다.
4. **한계점 (Limitations)**:
   - `STATIC_MANAGED_NORMAL_EVIDENCE_ONLY`
   - `PURE_INSTANCE_CORE_AND_NORMAL_CONFIGURATION_LIFECYCLE_EVIDENCE_ONLY`
   - `NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED`
   - `PRODUCER_GLOBAL_PROVIDER_REAL_ENTRY_STATIC_UNTESTED`
   - `MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN`
   - `NATIVE_PROMOTION_FULL_E2_NOT_RELEASED`
   - `FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER`
