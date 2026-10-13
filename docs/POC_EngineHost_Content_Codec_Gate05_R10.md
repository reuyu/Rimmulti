# POC EngineHost Content Codec Gate 05 R10 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R10_PACKAGE_POLICY / GATE05-R10-PACKAGE-POLICY` (Envelope 13)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-09
- **E1 Verdict**: `IMPLEMENTATION_PARTIAL` (Positive Pure Normal DTO & Package Policy Controls 19/19 PASS; Native Execution Prohibited/Untested per Scope Boundary)

---

## 1. 개요 및 배경

### 1.1 R9 성과 보존 및 R10 착수 배경
Gate05-R9에서 모드 버전 의미론 결함(`ENGINE-CONTENT-VERSION-SEMANTIC-20261009-01`)이 `CLOSED_SCOPED_NORMAL_CODEC_VERSION_MEANING`으로 독립 검증 및 수용되었습니다.
R9 후보의 좁은 수정 성과(`compatibilityVersionRange`와 `modVersion`의 상호 유추 제거, 미상 `null`의 문화권 전반 보존)는 그대로 유지됩니다.

그러나 이전 베이스라인에서는 실제 모드 인벤토리에 대한 승인 정책이 부재한 상태에서 매니페스트 기본값으로 `"POC_DECLARED_PACKAGES_ONLY"`라는 미구현 지원 경계 주장(default-only assertion)이 하드코딩되어 있었습니다. 이는 실제 관측된 패키지 목록을 대조하지 않고 스스로 승인된 것으로 단정하는 중대한 계약상 결함이었습니다.

### 1.2 R10 단일 목표 (PACKAGE_POLICY)
Master 승인 지침(`WP_ENGINE_GATE05_R10_PACKAGE_POLICY.md`, Envelope 13)에 따라 다음 한 가지 목표(`PACKAGE_POLICY`)만을 한정 구현하였습니다:
1. **타입화된 버전 관리 기대 패키지 정책 (Expected Package Policy)**:
   - `ExpectedPackagePolicyRecord` 정의 (`policyId`, `revision`, `admittedPackageIds`, `policyDigest`).
   - `PackagePolicyDispositionRecord` 정의 (`policyId`, `revision`, `policyDigest`, `status`).
   - `PackagePolicyCheckResult` 정의 (`isAdmitted`, `policyId`, `revision`, `policyDigest`, `status`, `failureReason`, `expectedPackages`, `observedPackages`).
2. **결정론적 표준 정책 다이제스트 계산 (`ComputePackagePolicyDigest`)**:
   - `policyId`, `revision`, 순서 보존된 소문자 패키지 ID 목록(`admittedPackageIds`)을 바인딩하여 64자리 SHA-256 16진수 대문자 다이제스트를 생성.
   - 대소문자 무관성(case-insensitivity)을 보장하되 순서 변경(permutation) 및 리비전/정책ID 변경 시 상이한 다이제스트를 생성하도록 구현.
3. **순수 패키지 비교 및 승인 헬퍼 (`CheckPackagePolicy`, `TryAdmitWithPackagePolicy`)**:
   - 관측된 매니페스트의 `activeMods` 순서 및 목록을 별도 공급된 기대 정책과 엄격히 대조.
   - 일치 시 `packagePolicyDisposition.status = "ADMITTED"`를 기록하고, `supportedModBoundary`를 명시적 검증 정책 식별자(`$"CHECKED_POLICY:{policyId}:{revision}"`)에 결속.
   - 불일치 시 상세 실패 사유와 상태(`COUNT_MISMATCH`, `ORDER_OR_PACKAGE_MISMATCH`, `DIGEST_MISMATCH` 등)를 반환.
4. **기본 하드코딩 지원 경계 주장 제거**:
   - `ModPatchSettingsDispositionRecord.supportedModBoundary`의 기본값을 `"UNCONFIGURED"`로 변경.
   - 계약 검증(`ValidateContract`)에서 레거시 `"POC_DECLARED_PACKAGES_ONLY"`가 발견될 경우 계약 위반으로 즉시 거부(fail-closed).
5. **실제 `ComputeActualContentProfileManifest` 연결 및 부트스트랩 Seam**:
   - 신뢰할 수 있는 지문 성공 전 실제 관측 인벤토리를 순수 패키지 검사에 연결.
   - 명시적 기대 정책이 설정되지 않은 경우 fail-closed(`UNCONFIGURED / BLOCKED_NO_POLICY`)로 동작.
   - 향후 신뢰할 수 있는 오퍼레이터 부트스트랩을 위한 thread-safe 구성 seam(`ConfigureExpectedPackagePolicy`, `ClearConfiguredExpectedPackagePolicy`, `HasConfiguredExpectedPackagePolicy`) 제공.
6. **계약 버전 및 역량 플래그 갱신**:
   - `CONTENT_CONTRACT_VERSION`: `"ADR-006B-v5-R10"`
   - 역량 플래그: `"GATE05_R10_PACKAGE_POLICY"`

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
  - SHA256: `1772DFBD1674B7CF8450CAF42FDE7AC6F92FD3A22183B7DDE5AA705CCEC24721`
  - 크기: 234,496 bytes
  - MVID: `7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb`
  - 매칭 PDB SHA256: `58FE3A765BB95C5C7FB044FE5E4627B66BF245ABA72C0CF95A05BC29EFF9B342` (58,376 bytes)
  - CodeView PDB: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **Release DLL** (Alternate Candidate):
  - 경로: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
  - SHA256: `659CFE704DBCE60AC8DF93D7C784FDA81FF312C0D42B502CA743720B7C30A706`
  - 크기: 223,232 bytes
  - MVID: `afe11c93-fc73-4002-a9e2-b976ce10f9e3`
  - 매칭 PDB SHA256: `3B1F51AC6E99D55794FB6BD83D373DAFFDAB443E62E91B5DEB64EEA170953553` (42,804 bytes)
  - CodeView PDB: `C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **배포 어셈블리** (`1.6\Assemblies\`):
  - Debug 바이너리 및 매칭 PDB와 100% 일치 동기화.

---

## 3. 순수 긍정적 정상 관리형 하네스 검증 (19/19 PASS)

신규 독립 하네스 `scratch\EngineGate05R10PackagePolicy\Harness\`를 구축하고, Master 승인 동결 관리 의존성(`FROZEN_MANAGED_QA_DEPENDENCIES_V1`)을 참조하여 19개 통제 케이스를 실행하였습니다:

| 번호 | 테스트 케이스 ID | 설명 | 결과 |
|---|---|---|---|
| TC01 | `TC01_Lossless_Float_Double_Formatting` | FormatLossless IEEE 754 'R' 무손실 표현 및 불변 문화권 유지 | **PASS** |
| TC02 | `TC02_Canonical_Normalize_ActiveMods_Preserved` | CanonicalNormalize activeMods loadOrder 순서 및 다중성 보존 | **PASS** |
| TC03 | `TC03_Canonical_Normalize_DefFamilies_Sorting` | CanonicalNormalize 미정렬 Def 패밀리 defName 서수 정렬 | **PASS** |
| TC04 | `TC04_Canonical_JSON_Serialization_Roundtrip` | 정규 JSON 직렬화 및 역직렬화 전후 모든 타입화 필드 보존 | **PASS** |
| TC05 | `TC05_Patch_Settings_Disposition_Sync` | activeMods 패치 수로부터 totalObservedPatches 자동 동기화 | **PASS** |
| TC06 | `TC06_Culture_Invariance_Serialization` | Invariant, en-US, de-DE 문화권 전반 바이트 단위 직렬화 동일성 | **PASS** |
| TC07 | `TC07_Assemblies_Ordinal_MultiKey_Sorting` | 로드된 어셈블리 복합 키 서수 정렬 결정론 | **PASS** |
| TC08 | `TC08_Verbs_And_Comps_Material_Sequence_Preserved` | verbs 및 comps의 원천 작성 순서 및 다중성 엄격 보존 | **PASS** |
| TC09 | `TC09_Hediff_Stages_minSeverity_Preserved` | HediffDef stages minSeverity 순서 엄격 보존 | **PASS** |
| TC10 | `TC10_DefDatabase_8_Families_Structure_Validation` | 8개 Def 패밀리 전수 구조 및 계약 오류 0건 검증 | **PASS** |
| TC11 | `TC11_TryAdmitManifest_Positive_Admission` | TryAdmitManifest 정상 승인 및 canonical JSON 생성 | **PASS** |
| TC12 | `TC12_Distinct_Manifests_Distinct_Digests` | 필드 변경 시 SHA256 다이제스트 충돌 저항성 | **PASS** |
| TC13 | `TC13_Schema_Contract_Versions_And_Capability_Flags` | `ADR-006B-v5`, `ADR-006B-v5-R10`, `GATE05_R10_PACKAGE_POLICY` 플래그 확인 | **PASS** |
| TC14 | `TC14_Deterministic_Tie_Breaking` | 어셈블리 복합 키 tie-breaking 정렬 검증 | **PASS** |
| TC15 | `TC15_Typed_Patch_And_Settings_Disposition` | **[R10 검증]** 기본값 `UNCONFIGURED` 확인 및 레거시 `POC_DECLARED_PACKAGES_ONLY` 거부 | **PASS** |
| TC16 | `TC16_Distinct_Version_Meaning_And_Optional_Unknown_Preservation` | **[R9 회귀 방지]** `modVersion = null`이 Invariant, en-US, de-DE 문화권에서 무결 보존 | **PASS** |
| TC17 | `TC17_Deterministic_Policy_Digest_And_Instance_Equality` | **[R10 신규]** 동일 정책 동등 인스턴스의 다이제스트 동일성, 대소문자 무관성, 순서 변경 시 다이제스트 분기 | **PASS** |
| TC18 | `TC18_Pure_Package_Comparison_And_Admission_Helper` | **[R10 신규]** 일치 정책 승인 및 `CHECKED_POLICY` 바인딩, 대체 정책 승인, 순서 불일치 감지 | **PASS** |
| TC19 | `TC19_Configuration_Seam_Lifecycle_And_Defensive_Unconfigured` | **[R10 신규]** 부트스트랩 seam 설정, 격리된 스냅샷 반환, 클리어 수명주기 thread-safe 검증 | **PASS** |

---

## 4. 한계점 및 거버넌스 준수

1. **NATIVE_UNTESTED**:
   - `WP_ENGINE_GATE05_R10_PACKAGE_POLICY` 지침에 따라 실제 RimWorld 게임 런타임 및 native 환경 실행은 엄격히 금지되었습니다.
   - 검증은 동결 관리 의존성을 참조하는 순수 정상 DTO/헬퍼 격리 하네스를 통해서만 수행되었습니다.
2. **INSTALLED_DLL_INCIDENT_OPEN**:
   - Steam 설치 경로의 DLL 불일치 사건(`BB3B52...` 대 아카이브 `2D64FF...`)은 `UNKNOWN OPEN INCIDENT`로 유지되며, 일체 임의 복구하거나 덮어쓰지 않았습니다.
3. **SEPARATE_OPERATOR_NATIVE_GATE**:
   - 부트스트랩 Seam의 구현은 오퍼레이터 원천 증명을 대체하지 않으며, 실제 오퍼레이터 배포 및 검증자 네이티브 증명은 별도 게이트로 유지됩니다.
4. **NO_SELF_CLOSURE**:
   - 개발자 A는 결함의 자체 종료(self-closure)나 전체 게이트 E2 릴리스를 주장하지 않습니다.
   - 런타임 최종 도메인 권한은 Dedicated Server에 있으며, 릴리스 및 결함 종결 권한은 Master 및 Sol QA의 독립 검증에 귀속됩니다.
   - 본 보고서는 개발자 E1 구현 완료 보고서입니다.
