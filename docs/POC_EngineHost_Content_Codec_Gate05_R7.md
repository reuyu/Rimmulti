# POC EngineHost Content Codec Gate 05 R7 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R7_CONTENT_ADMISSION / GATE05-R7-CONTENT-ADMISSION` (Envelope 10)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-08
- **E1 Verdict**: `IMPLEMENTATION_PARTIAL` (Positive Pure Normal DTO & Content Admission Controls 14/14 PASS; Native Execution Prohibited/Untested per Scope Boundary)

---

## 1. 개요 및 배경

Gate05-R6에 대한 Sol QA의 독립 평가(S1) 및 Master의 수용 처분(`MASTER_REVIEW_ENGINE_GATE05_R6_CODEC_CONTRACT_INDEPENDENT_S1_20261008.md`)에 따라:
1. **R6 정상 코덱 성과 인정 및 보존**:
   - `ContentProfileProvider`의 ADR-006B-v5 기반 distinct-key 정렬 정규화, ordered list(verbs, stages, comps) 순서 및 다중성 보존, 실제 Debug 및 Release 독립 PE MVID 추출이 Sol 독립 S1에서 정상 통과(Scope PASS)되었습니다.
2. **R7 한정 인가 범위 (Content Admission & Executable Contract Binding)**:
   - **실제 프로필 생성과 계약 검증의 직접 연결 (`R6-M02`)**: R6에서 정의에만 머물렀던 `ValidateContract`를 실제 프로필 수집(`ComputeActualContentProfileManifest`) 및 지문 계산(`ComputeActualContentProfileFingerprint`) 루틴에 강제 바인딩하여, 미승인/불완전 프로필이 성공 지문을 발급받지 못하도록 admission gate를 확립.
   - **실행 가능한 커버리지 및 Disposition 명세 (`R6-M03`)**: 8개 Def family 전수 프로젝션에 대해 필수 필드 및 자식 요소의 누락/침묵 축약 방지, 정당한 옵셔널 부재(`legitimate optional absence`)와 미관측 필수 머티리얼(`unobserved required material`)의 엄격한 구분.
   - **패치/세팅 지원 경계의 실행 가능한 바인딩 (`R6-M04`)**: 문서상 고지에 머물던 `OUTSIDE_POC_SUPPORTED_ADMISSION`을 manifest 실행 속성(`contentContractVersion`, `supportedCoverageProfile`, `modPatchSupportStatus`) 및 계약 검증 로직으로 바인딩.
   - **결정론적 동순위 정렬 및 인-플레이스 변경 정책 명시 (`R6-M01`, `R6-M05`)**: 멀티-키 기반 결정론적 tie-breaking 및 `CanonicalNormalize`의 in-place mutation 계약 명문화.
   - **순수 긍정적 정상 DTO/헬퍼 검증 한정 (`R6-M06`, `R6-M07`)**: R6에서 발생한 캐시 프로퍼티/InvalidateCache 호출(TC13 일탈) 및 비정상 거부 입력(TC11)을 배제하고, 오직 긍정적 정상 DTO 및 계약 헬퍼 통제(14개 케이스)만으로 구성된 신규 하네스 실행 및 정밀 패키징 증거 산출.
3. **엄격한 변경 경계**:
   - Production 소스 변경은 `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 `ContentProfileProvider` suffix 및 typed content helper DTO/메서드로만 제한.
   - `WorkerBridge.cs`, `WorkerBridge.csproj`, `EngineHostCensus.cs` 접두부(72,547 bytes)는 100% 불변 보존.
   - 게임 실행, native 런타임 실행, 과거 adverse/security 하네스 실행 전면 금지.

---

## 2. Content Admission Gate 및 지원 계약 명세 (ADR-006B-v5-R7)

### 2.1 실제 프로필 생성과 계약의 결속 (Admission Wiring)
- `ComputeActualContentProfileManifest()` 메서드 종료 직전, 구성된 매니페스트에 대해 `ValidateContract(manifest, out failureReason)`를 강제 호출합니다.
- 계약 검증을 통과하지 못한 매니페스트는 즉시 `InvalidOperationException`을 발생시키며, `ComputeActualContentProfileFingerprint()`를 통해 성공 지문을 발급받을 수 없습니다.
- 외부 소비자를 위해 `TryAdmitManifest(manifest, out canonicalJson, out failureReason)` API를 제공하여, 정규 전송 전에 지원 계약 준수 여부를 검증하고 수용된 경우에만 canonical JSON을 산출하도록 경계를 분리했습니다.

### 2.2 버전 및 지원 경계 실행 속성
- `MANIFEST_SCHEMA_VERSION`: `"ADR-006B-v5"`
- `CONTENT_CONTRACT_VERSION`: `"ADR-006B-v5-R7"`
- `SUPPORTED_COVERAGE_PROFILE`: `"POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5"`
- `MOD_PATCH_SUPPORT_STATUS`: `"COUNT_ONLY_EXPLICIT_EXCLUSION_RAW_PATCHES_SETTINGS"`
- **역량 플래그**:
  - `TACTICAL_PROBE_V4`
  - `READ_ONLY`
  - `SIMULATION`
  - `GATE05_R7_CONTENT_ADMISSION`
  - `ADR006B_LOSSLESS_CANONICAL_CONTENT_V5`

### 2.3 필드 매핑 및 Disposition 명세표

| 영역 / Def Family | 필드명 | 데이터 타입 | 필수 여부 | Null / Empty 처리 의미 | 정렬 / 순서 보존 정책 | Disposition |
|---|---|---|---|---|---|---|
| **헤더 메타데이터** | `schemaVersion` | string | Required | `"ADR-006B-v5"` 고정 | 최상단 위치 | SUPPORTED |
| | `contentContractVersion` | string | Required | `"ADR-006B-v5-R7"` 고정 | 상단 위치 | SUPPORTED |
| | `supportedCoverageProfile`| string | Required | `"POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5"` | 상단 위치 | SUPPORTED |
| | `modPatchSupportStatus` | string | Required | `"COUNT_ONLY_EXPLICIT_EXCLUSION_RAW_PATCHES_SETTINGS"` | 상단 위치 | SUPPORTED |
| | `buildIdentity` | string | Required | 빌드 식별자 (미관측 시 Fail-Closed) | 단일 값 | SUPPORTED |
| | `assemblyCSharpMvid` | string (UUID) | Required | Core Game MVID (미관측 시 Fail-Closed) | 단일 값 | SUPPORTED |
| | `assemblyCSharpSha` | string (Hex) | Required | Assembly-CSharp SHA256 (미관측 시 Fail-Closed) | 단일 값 | SUPPORTED |
| | `capabilityFlags` | List\<string\> | Required | 5개 정규 플래그 완비 | 고정 순서 | SUPPORTED |
| **DLC Expansions** | `defName` | string | Required | DLC 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `status` | string | Required | 활성화 상태 (`Status.ToString()`) | 단일 값 | SUPPORTED |
| | `linkedMod` | string? | Optional | 연계 패키지 ID (null 허용) | null 보존 | SUPPORTED |
| | `statusDescription` | string? | Optional | 부가 설명 (null 허용) | null 보존 | SUPPORTED |
| **Active Mods** | `loadOrder` | int | Required | 모드 로드 인덱스 (0-based) | loadOrder 보존 (동순위 시 packageId) | SUPPORTED |
| | `packageId` | string | Required | 소문자 정규화 패키지 ID | 단일 값 | SUPPORTED |
| | `name` | string | Required | 모드 명칭 | 단일 값 | SUPPORTED |
| | `modVersion` | string | Required | 모드 버전 | 단일 값 | SUPPORTED |
| | `patchCount` | int | Required | 적용된 패치 개수 | 단일 값 | SUPPORTED |
| | *Mod Patches/Settings Raw Identity* | - | Unadmitted | PoC 범위 외 (실행 가능 속성 바인딩) | 미수집 | OUTSIDE_POC_SUPPORTED_ADMISSION |
| **Loaded Assemblies**| `packageId` | string | Required | 소속 모드 ID | packageId Ordinal 정렬 | SUPPORTED |
| | `assemblyName` | string | Required | 단순 어셈블리명 | assemblyName Ordinal 정렬 | SUPPORTED |
| | `mvid` | string (UUID) | Required | 모듈 버전 ID | mvid Ordinal tie-break | SUPPORTED |
| | `sha256` | string (Hex) | Required | 디스크 어셈블리 SHA256 | 단일 값 | SUPPORTED |
| | `sizeBytes` | long | Required | 어셈블리 바이트 크기 (> 0) | 단일 값 | SUPPORTED |
| **ThingDef** | `defName` | string | Required | 고유 식별자 (패밀리 내 중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `category` | string | Required | ThingCategory enum 문자열 | 단일 값 | SUPPORTED |
| | `useHitPoints` | bool | Required | 내구도 활성화 여부 | 단일 값 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 (null 보존) | null vs `""` 구분 | SUPPORTED |
| | `stats[]` | StatModifierRecord | Optional | statDef + float value | statDef Ordinal -> value 정렬 | SUPPORTED |
| | `race` | RacePropsRecord? | Optional | 종족/신체 속성 (null 보존) | null 보존 | SUPPORTED |
| | `building` | BuildingPropsRecord? | Optional | 건축물 속성 (null 보존) | null 보존 | SUPPORTED |
| | `ingestible` | IngestiblePropsRecord?| Optional | 섭취 속성 (null 보존) | null 보존 | SUPPORTED |
| | `costList[]` | ThingCostRecord | Optional | 재료 thingDef + count | thingDef Ordinal -> count 정렬 | SUPPORTED |
| | `stuffCategories[]` | List\<string\> | Optional | 소재 카테고리 | Ordinal 정렬 | SUPPORTED |
| | `costStuffCount` | int | Required | 소재 요구 수량 | 단일 값 | SUPPORTED |
| | `verbs[]` | VerbPropsRecord | Optional | verbClass + range | **정의 순서/다중성 엄격 보존** | SUPPORTED |
| | `comps[]` | List\<string\> | Optional | 컴포넌트 클래스 FullName | **정의 순서/다중성 엄격 보존** | SUPPORTED |
| **HediffDef** | `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `hediffClass` | string | Required | 구현 클래스 FullName | 단일 값 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null vs `""` 구분 | SUPPORTED |
| | `lethalSeverity` | float | Required | 치명 한계 심각도 | 단일 값 | SUPPORTED |
| | `isBad` | bool | Required | 유해 상태 여부 | 단일 값 | SUPPORTED |
| | `tendable` | bool | Required | 치료 가능 여부 | 단일 값 | SUPPORTED |
| | `stages[]` | HediffStageRecord | Optional | minSeverity + label | **심각도 순서 엄격 보존** | SUPPORTED |
| | `comps[]` | List\<string\> | Optional | 컴포넌트 FullName | **정의 순서/다중성 엄격 보존** | SUPPORTED |
| **JobDef** | `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `driverClass` | string | Required | 드라이버 클래스 FullName | 단일 값 | SUPPORTED |
| | `checkOverrideOnDamage`| string | Required | 피격 시 중단 정책 | 단일 값 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `reportString` | string? | Optional | 작업 보고 문자열 | null 보존 | SUPPORTED |
| | `playerInterruptible`| bool | Required | 플레이어 중단 가능 여부 | 단일 값 | SUPPORTED |
| | `casualInterruptible`| bool | Required | 일반 중단 가능 여부 | 단일 값 | SUPPORTED |
| | `suspendable` | bool | Required | 일시정지 가능 여부 | 단일 값 | SUPPORTED |
| | `makeTargetPrisoner` | bool | Required | 포로 체포 여부 | 단일 값 | SUPPORTED |
| **SkillDef** | `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `disablingWorkTags` | string | Required | 비활성화 작업 태그 | 단일 값 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `skillLabel` | string? | Optional | 스킬 레이블 | null 보존 | SUPPORTED |
| | `pawnCreatorSummaryVisible`| bool | Required | 생성기 요약 표시 | 단일 값 | SUPPORTED |
| **FactionDef** | `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `isPlayer` | bool | Required | 플레이어 세력 여부 | 단일 값 | SUPPORTED |
| | `settlementGenerationWeight`| float | Required | 생성 가중치 | 단일 값 | SUPPORTED |
| | `pawnGroupMakersCount`| int | Required | 폰 그룹 생성기 개수 | 단일 값 | SUPPORTED |
| **BiomeDef** | `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `animalDensity` | float | Required | 동물 밀도 | 단일 값 | SUPPORTED |
| | `plantDensity` | float | Required | 식물 밀도 | 단일 값 | SUPPORTED |
| | `forageability` | float | Required | 채집성 | 단일 값 | SUPPORTED |
| **WeatherDef** | `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `windSpeedFactor` | float | Required | 풍속 계수 | 단일 값 | SUPPORTED |
| | `rainRate` | float | Required | 강우량 계수 | 단일 값 | SUPPORTED |
| | `snowRate` | float | Required | 강설량 계수 | 단일 값 | SUPPORTED |
| **ResearchProjectDef**| `defName` | string | Required | 고유 식별자 (중복 불허) | defName Ordinal 정렬 | SUPPORTED |
| | `techLevel` | string | Required | 기술 수준 | 단일 값 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `baseCost` | float | Required | 연구 비용 | 단일 값 | SUPPORTED |
| | `requiredResearchBuilding`| string? | Optional | 필수 작업대 defName | null 보존 | SUPPORTED |

---

## 3. Canonical Contract & Caller Mutation 명세

1. **In-Place Mutation 계약**:
   - `CanonicalNormalize(manifest)`는 호출자에게 명문화된 정책으로서 manifest 인스턴스의 내부 컬렉션을 직접 인-플레이스로 정규화합니다.
   - 직렬화기 `SerializeCanonicalJson(manifest, canonicalNormalize: true)`는 기본값으로 인-플레이스 정규화를 수행하며, 원본 순서를 유지해야 하는 특수 전송 소비자는 `canonicalNormalize: false`를 지정할 수 있습니다.
2. **동순위(Tie-Breaking) 결정론적 정책**:
   - `loadedAssemblies`: `packageId` Ordinal -> `assemblyName` Ordinal -> `mvid` Ordinal 순서로 결정론적 정렬.
   - `stats`: `statDef` Ordinal -> `value` 부동소수점 오름차순.
   - `costList`: `thingDef` Ordinal -> `count` 정수 오름차순.
   - `activeMods`: `loadOrder` 정수 오름차순 -> `packageId` Ordinal 순서.
3. **비정렬 순서 엄격 보존**:
   - `verbs`: 인덱스 기반 공격 모드 및 우선순위를 표현하므로 임의 정렬하지 않고 원본 순서 및 다중성 엄격 보존.
   - `stages`: 질병 및 증상의 심각도 단계 순서를 보존.
   - `comps`: 컴포넌트 틱 실행 순서를 보존.

---

## 4. 변경 및 불변성 경계 검증

### 4.1 불변 소스 및 접두부 검증
- `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`:
  - 크기: `156,431` 바이트
  - SHA256: `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718` (100% 일치)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj`:
  - 크기: `1,774` 바이트
  - SHA256: `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` (100% 일치)
- `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 접두부(prefix):
  - Prefix Marker: `    public static class ContentProfileProvider`
  - 접두부 길이: `72,547` 바이트
  - 접두부 SHA256: `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (100% 일치)
- 전체 `EngineHostCensus.cs`:
  - 크기: `124,817` 바이트
  - SHA256: `D980225D8DBE04F9CAE95AD100DCF6640252A24A14599346E3B7F81CA8B9AF98`

### 4.2 보존 베이스라인
- `Archive 19`: 완전 보존
- `Prior 844` (R1 147 + R2 107 + R3 133 + R4 232 + R5 113 + R6 112): 완전 보존
- `Pipeline 206`: 완전 보존
- `QA Evidence 1,489`: 완전 보존
- `Managed Dependencies 4`: 완전 보존
- `Installed Steam DLL BB3B52...`: `UNKNOWN OPEN INCIDENT`로 공시 유지

---

## 5. E1 정상 코덱 및 헬퍼 검증 결과 (14 / 14 PASS)

- **하네스 프로젝트**: `scratch\EngineGate05R7ContentAdmission\Harness\Gate05R7ContentRunner.csproj`
- **하네스 실행 파일**: `scratch\EngineGate05R7ContentAdmission\Harness\bin\Debug\net472\Gate05R7ContentRunner.exe`
- **검증 일시**: `2026-10-08T13:05:49.0690921Z` (UTC)
- **대상 후보 어셈블리**: `scratch\EngineGate05R7ContentAdmission\Harness\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
- **어셈블리 SHA256**: `223B4055C0AFAA6F30488C9787AE6F68D65D62F395CFCA722EDA83674975CD2A`
- **산출물**:
  - `scratch\EngineGate05R7ContentAdmission\results.json`
  - `scratch\EngineGate05R7ContentAdmission\raw_console.txt`

### 5.1 테스트 결과표

| 테스트 ID | 검증 내용 및 목적 | 기대 결과 | 실제 결과 | 판정 |
|---|---|---|---|:---:|
| `TC01_RoundTrip_Canonical_Lossless` | 직렬화 -> 역직렬화 -> 재직렬화 후 SHA256 다이제스트 일치 검증 | $SHA_1 == SHA_2$, 무손실 round-trip | 일치 (`D0CFC22A...`) | **PASS** |
| `TC02_Deterministic_Identical_Input` | 동일 데이터 인스턴스의 직렬화 다이제스트 일치 검증 | 결정론적 JSON 및 SHA 일치 | 일치 | **PASS** |
| `TC03_All_Eight_Def_Families_No_Sentinels` | 8개 Def 패밀리 포괄 및 센티넬/구분자(`Stats[`, `Mod:`) 부재 검증 | 센티넬 0건 검출, 8개 패밀리 완비 | 완비 확인 | **PASS** |
| `TC04_Floating_Point_Lossless_Precision` | 부동소수점(`float`) 경계값 및 정밀도 round-trip 보존 검증 | IEEE 754 float 값 손실 없음 | 오차 0.0 확인 | **PASS** |
| `TC05_Unicode_SpecialChars_Lossless` | 한국어, 일본어, 특수기호, 줄바꿈의 이스케이프 보존 검증 | 문자열 원형 100% 보존 | 일치 | **PASS** |
| `TC06_Null_Missing_Empty_Distinction` | `null` vs `""` vs 옵셔널 객체 `null`의 명확한 구분 직렬화 검증 | 센티넬 축약 없이 null 보존 | 구분 보존 확인 | **PASS** |
| `TC07_Ordered_Collections_Preservation` | `activeMods` loadOrder, `Verbs`, `stages`, `comps` 정의 순서 및 다중성 보존 검증 | 비정렬 대상의 원본 순서 보존 | 순서 100% 보존 | **PASS** |
| `TC08_Stable_Sorting_Determinism` | 무작위 순서 Def 컬렉션의 defName Ordinal 안정 정렬 검증 | 결정론적 Ordinal 정렬 | 일치 | **PASS** |
| `TC09_Unordered_Input_Normalization_Equivalence` | 뒤섞인 unordered 입력과 정렬된 입력의 정규화 동일성 검증 | 정규화 후 동일 JSON/다이제스트 | 일치 | **PASS** |
| `TC10_ValidateContract_Positive_Compliant` | 계약 준수 매니페스트에 대한 `ValidateContract` 통과 검증 | `valid == true`, 에러 0건 | 에러 0건 통과 | **PASS** |
| `TC11_TryAdmitManifest_Positive_Admission` | `TryAdmitManifest`의 긍정적 계약 승인 및 canonical JSON 생성 검증 | `admitted == true`, 3482 bytes 산출 | 정상 승인 확인 | **PASS** |
| `TC12_Distinct_Manifests_Distinct_Digests` | 단일 스칼라 변이 시 다이제스트 충돌 저항성 검증 | 고유 다이제스트 산출 | 일치 | **PASS** |
| `TC13_Schema_Contract_Versions_And_Capability_Flags` | 스키마 버전, 계약 버전, 커버리지 프로필, 패치 상태, 플래그 준수 검증 | 필수 플래그 5종 및 버전 완비 | 완비 확인 | **PASS** |
| `TC14_Deterministic_Tie_Breaking` | 복수 동순위 키에 대한 multi-key tie-breaking 결정론 검증 | 보조 키 기준 결정론적 정렬 | 일치 | **PASS** |

**종합 결과: 14개 테스트 실행, 14개 PASS, 0개 FAIL (Verdict: PASS)**

---

## 6. 후보 바이너리 및 패키징 동일성 (Candidate Packaging Identity)

Debug와 Release 후보의 고유 ModuleVersionId(MVID) 및 실측 바이너리 메타데이터는 다음과 같습니다:

### 6.1 Primary Selected Candidate (Debug)
- **DLL 경로**: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
- **DLL 크기**: `220,672` 바이트
- **DLL SHA256**: `223B4055C0AFAA6F30488C9787AE6F68D65D62F395CFCA722EDA83674975CD2A`
- **PDB 경로**: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **PDB 크기**: `54,604` 바이트
- **PDB SHA256**: `146C5667DF4BB3C4C3F48328FD054A6C4BC87D22FEB5F010534A4428C8DA1579`
- **실제 MVID**: `bdf94567-be4d-4270-9a70-dbf2df9b5b4a`
- **Assemblies 동기화**: `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` (동일 바이너리)

### 6.2 Alternate Candidate (Release)
- **DLL 경로**: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
- **DLL 크기**: `209,920` 바이트
- **DLL SHA256**: `E9E409E95E225552B59D34FA1DE9D5AB021764988F1FADD25FDC11235CF87F35`
- **PDB 경로**: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **PDB 크기**: `40,312` 바이트
- **PDB SHA256**: `07C79C3C651EEB32BC0EFE56F552E90F414ED7F3AFFBDCCD8541B5CA49980188`
- **실제 MVID**: `db8d92c1-a284-4e67-8bcc-708e279944c1`

### 6.3 빌드 툴링 환경
- **.NET SDK**: `10.0.201`
- **대상 프레임워크**: `net472`
- **빌드 커맨드**: `dotnet build scratch\WorkerBridgeMod\Source\WorkerBridge.csproj -c Debug / Release`

---

## 7. 한계 및 보존 사항 (Limitations & Preservation Policy)

1. **`NATIVE_UNTESTED`**: 본 작업은 Master 작업 지시서에 따라 순수 DTO 정상 코덱 및 계약 유효성 단위 통제만 수행하였으며, RimWorld 게임 프로세스 및 native 런타임 실행은 수행하지 않았습니다 (UNTESTED 공시).
2. **`INSTALLED_DLL_INCIDENT_OPEN`**: Steam 설치 디렉터리의 어셈블리 SHA256(`BB3B52...`) 불일치 인시던트는 원인 규명 전까지 `UNKNOWN OPEN INCIDENT`로 유지되며, 임의 덮어쓰기나 정규화를 수행하지 않았습니다.
3. **`NO_SELF_CLOSURE`**: Developer 에이전트는 본 E1 검증 통과를 이유로 결함 클로저나 게이트 승인을 자의적으로 선언하지 않으며, 독립 QA(Sol)의 평가 및 Master의 거버넌스 처분을 대기합니다.
