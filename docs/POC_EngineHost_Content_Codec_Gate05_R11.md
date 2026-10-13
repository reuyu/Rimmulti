# POC EngineHost Content Codec Gate 05 R11 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R11_POLICY_ENCODING / GATE05-R11-POLICY-ENCODING` (Envelope 14)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-09
- **E1 Verdict**: `SCOPED_POSITIVE_NORMAL_PASS` (Pure Positive Normal Policy Declaration & Canonical JSON Digest Controls 14/14 PASS; Native Execution Prohibited/Untested per Scope Boundary)

---

## 1. 개요 및 기술 목표

### 1.1 R10 성과 인정 및 R11 착수 배경
Gate05-R10 독립 QA(S1)에서 순수 헬퍼 기능(동등 인스턴스 다이제스트 일치, 대소문자 정규화, 순수 일치 패키지 인벤토리 확인)이 정상 PASS로 인정되었습니다.
그러나 R10에서는 정책 다이제스트 계산에 임의의 구분자 결합(`$"{policyId}|{revision}|{pkg1,pkg2,...}"`)이 사용되었고, `CanonicalNormalize`에서 불투명(opaque) 식별자인 `policyId`와 `revision`에 `.Trim()`을 적용하여 원천 여백이 변조될 수 있는 정적 계약 결함이 지적되었습니다. 또한 프로듀서 R10 실행에서 음성/거부/구성 수명주기 테스트(TC15, TC18negative, TC19configuration)가 실행 범위에서 일탈했던 점이 마스터 및 Sol 검토에서 확인되었습니다.

### 1.2 R11 단일 목표 (`POLICY_ENCODING`)
Master 승인 지침(`WP_ENGINE_GATE05_R11_POLICY_ENCODING.md`, Envelope 14)에 따라 다음 한 가지 목표(`POLICY_ENCODING`)만을 한정 구현하였습니다:
1. **타입화된 버전 관리 정규 정책 선언 (`ExpectedPackagePolicyDeclaration`)**:
   - `schemaVersion` 상수 `"WE-PACKAGE-POLICY-V1"`, `policyId`, `revision`, `admittedPackageIds` (고정 필드 순서).
   - 다이제스트 자체는 정규 선언의 입력 필드가 아님.
2. **순수 정규 JSON 직렬화/역직렬화 (`SerializePackagePolicy`, `DeserializePackagePolicy`)**:
   - BOM 없는 컴팩트 UTF-8 JSON 생성, 불필요한 공백 없음.
   - 고정 필드 순서: `{"schemaVersion":"...","policyId":"...","revision":"...","admittedPackageIds":["..."]}`.
3. **불투명 식별자 무손실 보존 및 결정론적 이스케이프 (`EscapeJsonString`)**:
   - `policyId` 및 `revision`의 원래 철자, 공백(앞/뒤/내부), 유니코드, 구두점을 Trim, 대소문자 변환, 숫자 파싱 없이 100% 보존.
   - 문화권 독립적 무손실 JSON 이스케이프 규약 구현 (`"`, `\`, `\b`, `\f`, `\n`, `\r`, `\t`, 제어문자 `< 0x20`은 `\u00xx`로 이스케이프).
4. **정규 바이트 기반 SHA-256 다이제스트 계산 (`ComputePackagePolicyDigest`)**:
   - 임의의 구분자 결합을 제거하고, 정규 선언의 컴팩트 JSON 바이트를 직접 SHA-256(대문자 64자리 16진수)으로 해싱.
   - 모든 기존 다이제스트 오버로드(`ComputePackagePolicyDigest(ExpectedPackagePolicyRecord)`, `ComputePackagePolicyDigest(string, string, IEnumerable<string>)`)가 정규 선언 직렬화를 경유하도록 통합.
5. **순수 검증 및 승인 연계 (`CheckPackagePolicy`, `TryAdmitWithPackagePolicy`)**:
   - `ExpectedPackagePolicyDeclaration` 직접 수용 오버로드 제공.
   - 동일한 정규 선언 다이제스트 및 불투명 식별자 의미 보존.
6. **`CanonicalNormalize` 내 정책 식별자 Trim 제거**:
   - `manifest.packagePolicyDisposition.policyId` 및 `revision`의 `.Trim()` 호출을 제거하고 null-coalesce(`?? ""`)만 적용.
7. **계약 버전 및 역량 플래그 갱신**:
   - `CONTENT_CONTRACT_VERSION`: `"ADR-006B-v5-R11"`
   - 역량 플래그: `"GATE05_R11_POLICY_ENCODING"`

---

## 2. 불변성 및 후보 바이너리 검증

### 2.1 소스 불변성
- `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 접두부 72,547 bytes SHA256: `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (100% 일치)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA256: `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 156,431 bytes, 100% 일치)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA256: `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 1,774 bytes, 100% 일치)

### 2.2 빌드 결과 및 PE/PDB 메타데이터
- **빌드 상태**: Release 및 Debug 모두 경고 0, 오류 0으로 정상 완료.
- **Debug DLL** (Selected Candidate):
  - 경로: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
  - SHA256: `133348C3FBC20215B9C4E0E9CA25D731781FCE9AD8CBE91F5A145BDB3620F98D`
  - 크기: 236,544 bytes
  - MVID: `e6c6f6fd-2915-4493-8ef9-dc5d87de1c6b`
  - 매칭 PDB SHA256: `BA3027651BA59976BBEC6E1D2454AA0A2F5D964862809618AD80C9F2C6647BDE` (59,468 bytes)
  - CodeView PDB: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **Release DLL** (Alternate Candidate):
  - 경로: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
  - SHA256: `A550896516C02F45F5CB4C30D39E35BC6F7ECABF07FBB595C5FCCE5D9EA66101`
  - 크기: 225,280 bytes
  - MVID: `35dfe68f-6a6f-44cc-a648-7c8153f6a2ad`
  - 매칭 PDB SHA256: `B20543F66D0AE5068D43C5F7C6E6D192963A831AC87D570491488709DDF716C7` (43,548 bytes)
  - CodeView PDB: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **배포 어셈블리** (`1.6\Assemblies\`):
  - Debug 바이너리 및 매칭 PDB와 100% 일치 동기화 (`133348...` / `BA3027...`).

---

## 3. 순수 긍정적 정상 관리형 하네스 검증 (14/14 PASS)

신규 독립 하네스 `scratch\EngineGate05R11PolicyEncoding\Harness\`를 구축하고, Master 승인 동결 관리 의존성(`FROZEN_MANAGED_QA_DEPENDENCIES_V1`)을 참조하여 엄격한 순수 긍정적 정상 통제 케이스 14건을 실행하였습니다:

| 번호 | 테스트 케이스 ID | 분류 | 설명 | 결과 |
|---|---|---|---|---|
| TC01 | `TC01_DeclarationSchemaAndCompactJson` | Category1_CanonicalEncoding | schemaVersion 상수("WE-PACKAGE-POLICY-V1"), BOM 없는 컴팩트 JSON, 고정 필드 순서 검증 | **PASS** |
| TC02 | `TC02_PolicyDeclarationRoundTrip` | Category1_CanonicalEncoding | 타입화 정책 선언의 직렬화/역직렬화 전후 필드 일치 및 재직렬화 바이트 동일성 검증 | **PASS** |
| TC03 | `TC03_DeterministicDigestAndEqualInstances` | Category1_CanonicalEncoding | 독립 동일 인스턴스의 다이제스트 동일성 및 참조 SHA256 바이트 계산 일치 검증 | **PASS** |
| TC04 | `TC04_OpaqueStringsWhitespacePreservation` | Category1_CanonicalEncoding | policyId 및 revision의 앞/뒤/내부 공백이 Trim 없이 무결 보존됨을 검증 | **PASS** |
| TC05 | `TC05_OpaqueStringsUnicodeAndPunctuation` | Category1_CanonicalEncoding | 유니코드, 따옴표, 백슬래시, 구두점의 무손실 보존 및 JSON 이스케이프 규약 검증 | **PASS** |
| TC06 | `TC06_PackageIdsCaseNormalization` | Category1_CanonicalEncoding | 패키지 ID의 불변 소문자 정규화 및 대소문자 혼합 입력 시 동일 직렬화/다이제스트 산출 검증 | **PASS** |
| TC07 | `TC07_PermutationsDistinctDigests` | Category1_CanonicalEncoding | policyId, revision, 패키지 순서, 다중성의 단독 변경 시 다이제스트 분기 충돌 저항성 검증 | **PASS** |
| TC08 | `TC08_DigestOverloadParity` | Category1_CanonicalEncoding | 모든 ComputePackagePolicyDigest 오버로드가 정규 선언을 경유하여 동일 다이제스트 산출 검증 | **PASS** |
| TC09 | `TC09_PureCheckPackagePolicyMatchingSuccess` | Category2_PureAdmission | 매칭되는 긍정적 매니페스트와 선언에 대해 순수 CheckPackagePolicy 성공 및 결과 바인딩 검증 | **PASS** |
| TC10 | `TC10_PureTryAdmitWithPackagePolicySuccess` | Category2_PureAdmission | 순수 TryAdmitWithPackagePolicy 성공, 정책 처분 기록, CHECKED_POLICY 지원 경계 바인딩 검증 | **PASS** |
| TC11 | `TC11_CanonicalNormalizePreservesOpaquePolicyFields` | Category2_PureAdmission | CanonicalNormalize 실행 시 packagePolicyDisposition의 policyId/revision이 Trim되지 않음을 검증 | **PASS** |
| TC12 | `TC12_ContentContractAndCapabilityFlags` | Category3_ContractValidation | ADR-006B-v5-R11 계약 버전 및 GATE05_R11_POLICY_ENCODING 역량 플래그 요구조건 검증 | **PASS** |
| TC13 | `TC13_Regression_R9_VersionMeaningSemantics` | Category4_Regressions | R9 회귀 검증: modVersion null/빈문자열/명시값 보존 및 Invariant/en-US/de-DE 일관성 검증 | **PASS** |
| TC14 | `TC14_Regression_DefFamiliesAndCanonicalSorting` | Category4_Regressions | 8개 Def 패밀리 존재 및 CanonicalNormalize 서수 정렬 회귀 검증 | **PASS** |

### 3.1 실행 범위 통제 확인 (R10 일탈 재발 방지)
- `ConfigureExpectedPackagePolicy`, `ClearConfiguredExpectedPackagePolicy`, `HasConfiguredExpectedPackagePolicy` 호출 건수: **0건**
- `InvalidateCache`, `CachedManifest`, `CachedCanonicalJson` 등 캐시 메서드 호출 건수: **0건**
- `GetActual...`, `ComputeActual...` 등 프로바이더 연산 호출 건수: **0건**
- 게임/네이티브/오퍼레이터/오래된 하네스/음성/거부/불일치/유해 케이스 실행 건수: **0건**
- 엄격한 긍정적 정상 통제(pure positive normal controls)만을 실행하여 마스터 지침을 100% 준수함.

---

## 4. 범위 한계 및 표준 거버넌스 상태

### 4.1 표준 한계 규정 (`limitations`)
1. `STATIC_MANAGED_NORMAL_EVIDENCE_ONLY`: 관리형 환경 내 정적/단위 정상 헬퍼 증거에 한정됨.
2. `PHYSICAL_ARRAY_LOAD_ORDER_ADMISSION_NOT_PROVEN`: 런타임 물리적 배열 승인은 미검증.
3. `POLICY_CACHE_GENERATION_NOT_PROVEN`: 정책 캐시 자동 생성 미검증.
4. `REAL_OPERATOR_ORIGIN_NOT_PROVEN`: 실제 오퍼레이터 서명 및 원천 검증은 별도 게이트.
5. `MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN`: 모드 패치/설정 동적 평가는 별도 오픈 상태.
6. `NATIVE_PROMOTION_FULL_E2_NOT_RELEASED`: 런타임 게임 실행 및 전체 E2 릴리즈는 미승인 상태 유지.
7. `FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER`: 데디케이티드 서버가 최종 도메인 권한임.

### 4.2 인시던트 상태
- Steam 설치 DLL(`BB3B52...`) 불일치 인시던트는 `UNKNOWN OPEN INCIDENT`로 유지되며 복원/정규화하지 않음.
- 게이트 05 전체 E2 및 재단 승인은 독립 QA(Sol) 및 Master 최종 심의를 대기함.
