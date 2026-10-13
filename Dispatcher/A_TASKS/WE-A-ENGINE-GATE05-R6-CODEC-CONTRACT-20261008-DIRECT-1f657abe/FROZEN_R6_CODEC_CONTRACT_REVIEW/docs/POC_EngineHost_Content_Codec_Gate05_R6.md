# POC EngineHost Content Codec Gate 05 R6 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R6_CODEC_CONTRACT / GATE05-R6-CODEC-CONTRACT` (Envelope 9)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-08
- **E1 Verdict**: `IMPLEMENTATION_PARTIAL` (Normal Codec & Contract Controls 14/14 PASS; Native Execution Prohibited/Untested per Scope Boundary)

---

## 1. 개요 및 배경

Gate05-R5의 독립 QA 평가(Sol S1) 및 Master의 수용 처분(`MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_INDEPENDENT_S1_20261008.md`)에 따라:
1. **R5 정상 코덱 성과 인정 및 보존**:
   - `ContentProfileProvider`의 ADR-006B-v5 기반 typed lossless DTO 직렬화/역직렬화 구현이 Sol 독립 S1에서 정상 통과(Narrow PASS)되었습니다.
   - 기존의 문자열 센티넬 및 구분자(`Stats[...]`, `Mod:...:Patches=`, `defCensusDigest`, `modContentDigest`)는 완전히 제거되었습니다.
2. **R6 한정 인가 범위 (Explicit Supported Content Contract & Packaging Precision)**:
   - **명시적 지원/미지원 계약 확립 (MD-130)**: 8개 Def family 및 메타데이터에 대해 지원 필드, 필수 여부(`Requiredness`), Null/Empty 처리 규칙, 정렬 정책을 공시하고 `ValidateContract(manifest, out failureReason)` 구현.
   - **Canonical Sorting Boundary 확립**: 선언된 unordered set(`thingDefs`, `stats`, `costList`, `biomeDefs`, `dlcExpansions` 등)은 `CanonicalNormalize`를 통해 결정론적 Ordinal 정렬을 강제하되, 순서 및 다중성 의미가 있는 ordered list(`activeMods` loadOrder, `verbs` 정의 순서/다중성, `stages` 심각도 순서, `comps` 정의 순서)는 원본 순서를 엄격히 보존.
   - **Collector Mapping Fail-Closed 보강**: 런타임 수집 시 필수 머티리얼이 미관측되면 빈 리스트/센티넬 축약 대신 명시적 `InvalidOperationException`을 발생시킴. 모드 패치/세팅 머티리얼 identity는 PoC 지원 범위 외(`OUTSIDE_POC_SUPPORTED_ADMISSION`)로 정직 공시.
   - **바이너리 메타데이터 분리**: Debug MVID와 Release MVID를 실제 PE 헤더에서 독립 추출하여 빌드 산출물과 매니페스트에 일치시킴.
   - **순수 Normal Codec 단위 통제**: 런타임 미초기화 상태에서 fake PASS를 발생시키던 기존 TC11을 제거하고, 순수 DTO 정상 코덱 및 계약 유효성 검증(14개 케이스)으로만 하네스를 구성.
3. **엄격한 변경 경계**:
   - Production 소스 변경은 `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 `ContentProfileProvider` suffix 및 content codec DTO/helper로만 한정.
   - `WorkerBridge.cs`, `WorkerBridge.csproj`, `EngineHostCensus.cs` 접두부(72,547 bytes)는 1바이트의 오차도 없이 고정 해시로 보존.
   - 게임 실행, native 런타임 실행, 과거 adverse/security 하네스 실행 전면 금지.

---

## 2. Explicit Supported Content Contract & Disposition Specification (MD-130 / ADR-006B-v5-R6)

`ContentProfileProvider`는 8개 Def family와 DLC, Mod, Assembly에 대한 명시적 필드 계약을 정의하며, `ValidateContract`를 통해 런타임 및 단위 수준에서 계약 준수 여부를 검증합니다.

### 2.1 스키마 및 계약 버전
- **매니페스트 스키마 버전**: `ADR-006B-v5`
- **콘텐츠 계약 버전**: `ADR-006B-v5-R6`
- **역량 플래그**:
  - `TACTICAL_PROBE_V4`
  - `READ_ONLY`
  - `SIMULATION`
  - `GATE05_R6_CODEC_CONTRACT`
  - `ADR006B_LOSSLESS_CANONICAL_CONTENT_V5`

### 2.2 지원 필드 매핑 및 Disposition 명세표

| 영역 / Def Family | 필드명 | 데이터 타입 | 필수 여부 | Null / Empty 처리 의미 | 정렬 / 순서 보존 정책 | Disposition |
|-------------------|--------|-------------|-----------|------------------------|-----------------------|-------------|
| **헤더 메타데이터** | `schemaVersion` | string | Required | `"ADR-006B-v5"` 고정 | 최상단 위치 | SUPPORTED |
| | `buildIdentity` | string | Required | 빌드 식별자 (미관측 시 Fail-Closed) | 단일 값 | SUPPORTED |
| | `assemblyCSharpMvid` | string (UUID) | Required | Core Game MVID (미관측 시 Fail-Closed) | 단일 값 | SUPPORTED |
| | `assemblyCSharpSha` | string (Hex) | Required | Assembly-CSharp SHA256 (미관측 시 Fail-Closed) | 단일 값 | SUPPORTED |
| | `capabilityFlags` | List\<string\> | Required | 5개 정규 플래그 | 고정 순서 | SUPPORTED |
| **DLC Expansions** | `defName` | string | Required | DLC 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `status` | string | Required | 활성화 상태 (`Status.ToString()`) | 단일 값 | SUPPORTED |
| | `linkedMod` | string? | Optional | 연계 패키지 ID (null 허용) | null 보존 | SUPPORTED |
| | `statusDescription` | string? | Optional | 부가 설명 (null 허용) | null 보존 | SUPPORTED |
| **Active Mods** | `loadOrder` | int | Required | 모드 로드 인덱스 (0-based) | **loadOrder 정렬/보존** | SUPPORTED |
| | `packageId` | string | Required | 소문자 정규화 패키지 ID | 단일 값 | SUPPORTED |
| | `name` | string | Required | 모드 명칭 | 단일 값 | SUPPORTED |
| | `modVersion` | string | Required | 모드 버전 | 단일 값 | SUPPORTED |
| | `patchCount` | int | Required | 적용된 패치 개수 | 단일 값 | SUPPORTED |
| | *Mod Patches/Settings Raw Identity* | - | Unadmitted | PoC 범위 외 (정직 공시) | 미수집 | OUTSIDE_POC_SUPPORTED_ADMISSION |
| **Loaded Assemblies**| `packageId` | string | Required | 소속 모드 ID | packageId Ordinal 정렬 | SUPPORTED |
| | `assemblyName` | string | Required | 단순 어셈블리명 | assemblyName Ordinal 정렬 | SUPPORTED |
| | `mvid` | string (UUID) | Required | 모듈 버전 ID | 단일 값 | SUPPORTED |
| | `sha256` | string (Hex) | Required | 디스크 어셈블리 SHA256 | 단일 값 | SUPPORTED |
| | `sizeBytes` | long | Required | 어셈블리 바이트 크기 | 단일 값 | SUPPORTED |
| **ThingDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 (null 보존) | null vs `""` 구분 | SUPPORTED |
| | `category` | string | Required | ThingCategory enum 문자열 | 단일 값 | SUPPORTED |
| | `useHitPoints` | bool | Required | 내구도 활성화 여부 | 단일 값 | SUPPORTED |
| | `stats[]` | StatModifierRecord | Optional | statDef + float value | statDef Ordinal 정렬 | SUPPORTED |
| | `race` | RacePropsRecord? | Optional | 종족/신체 속성 (null 보존) | null 보존 | SUPPORTED |
| | `building` | BuildingPropsRecord? | Optional | 건축물 속성 (null 보존) | null 보존 | SUPPORTED |
| | `ingestible` | IngestiblePropsRecord?| Optional | 섭취 속성 (null 보존) | null 보존 | SUPPORTED |
| | `costList[]` | ThingCostRecord | Optional | 재료 thingDef + count | thingDef Ordinal 정렬 | SUPPORTED |
| | `stuffCategories[]` | List\<string\> | Optional | 소재 카테고리 | Ordinal 정렬 | SUPPORTED |
| | `costStuffCount` | int | Required | 소재 요구 수량 | 단일 값 | SUPPORTED |
| | `verbs[]` | VerbPropsRecord | Optional | verbClass + range | **정의 순서/다중성 보존** | SUPPORTED |
| | `comps[]` | List\<string\> | Optional | 컴포넌트 클래스 FullName | **정의 순서 보존** | SUPPORTED |
| **HediffDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null vs `""` 구분 | SUPPORTED |
| | `hediffClass` | string | Required | 구현 클래스 FullName | 단일 값 | SUPPORTED |
| | `lethalSeverity` | float | Required | 치명 한계 심각도 | 단일 값 | SUPPORTED |
| | `isBad` | bool | Required | 유해 상태 여부 | 단일 값 | SUPPORTED |
| | `tendable` | bool | Required | 치료 가능 여부 | 단일 값 | SUPPORTED |
| | `stages[]` | HediffStageRecord | Optional | minSeverity + label | **심각도 순서 보존** | SUPPORTED |
| | `comps[]` | List\<string\> | Optional | 컴포넌트 FullName | **정의 순서 보존** | SUPPORTED |
| **JobDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `driverClass` | string | Required | 드라이버 클래스 FullName | 단일 값 | SUPPORTED |
| | `reportString` | string? | Optional | 작업 보고 문자열 | null 보존 | SUPPORTED |
| | `playerInterruptible`| bool | Required | 플레이어 중단 가능 여부 | 단일 값 | SUPPORTED |
| | `casualInterruptible`| bool | Required | 일반 중단 가능 여부 | 단일 값 | SUPPORTED |
| | `suspendable` | bool | Required | 일시정지 가능 여부 | 단일 값 | SUPPORTED |
| | `checkOverrideOnDamage`| string | Required | 피격 시 중단 정책 | 단일 값 | SUPPORTED |
| | `makeTargetPrisoner` | bool | Required | 포로 체포 여부 | 단일 값 | SUPPORTED |
| **SkillDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `skillLabel` | string? | Optional | 스킬 레이블 | null 보존 | SUPPORTED |
| | `disablingWorkTags` | string | Required | 비활성화 작업 태그 | 단일 값 | SUPPORTED |
| | `pawnCreatorSummaryVisible`| bool | Required | 생성기 요약 표시 | 단일 값 | SUPPORTED |
| **FactionDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `isPlayer` | bool | Required | 플레이어 세력 여부 | 단일 값 | SUPPORTED |
| | `settlementGenerationWeight`| float | Required | 생성 가중치 | 단일 값 | SUPPORTED |
| | `pawnGroupMakersCount`| int | Required | 폰 그룹 생성기 개수 | 단일 값 | SUPPORTED |
| **BiomeDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `animalDensity` | float | Required | 동물 밀도 | 단일 값 | SUPPORTED |
| | `plantDensity` | float | Required | 식물 밀도 | 단일 값 | SUPPORTED |
| | `forageability` | float | Required | 채집성 | 단일 값 | SUPPORTED |
| **WeatherDef** | `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `windSpeedFactor` | float | Required | 풍속 계수 | 단일 값 | SUPPORTED |
| | `rainRate` | float | Required | 강우량 계수 | 단일 값 | SUPPORTED |
| | `snowRate` | float | Required | 강설량 계수 | 단일 값 | SUPPORTED |
| **ResearchProjectDef**| `defName` | string | Required | 고유 식별자 | defName Ordinal 정렬 | SUPPORTED |
| | `label` | string? | Optional | 표시 명칭 | null 보존 | SUPPORTED |
| | `baseCost` | float | Required | 연구 비용 | 단일 값 | SUPPORTED |
| | `techLevel` | string | Required | 기술 수준 | 단일 값 | SUPPORTED |
| | `requiredResearchBuilding`| string? | Optional | 필수 작업대 defName | null 보존 | SUPPORTED |

---

## 3. Canonical Sorting Boundary 명세

정규 직렬화에서 결정론적 다이제스트를 도출하기 위한 정렬 경계는 다음과 같이 엄격하게 분리됩니다:

1. **Unordered Set Collections (Ordinal Sort 강제)**:
   - `dlcExpansions`: `defName` 기준 Ordinal 정렬.
   - `loadedAssemblies`: `packageId` -> `assemblyName` 기준 Ordinal 정렬.
   - Def Collections (`thingDefs`, `hediffDefs`, `jobDefs`, `skillDefs`, `factionDefs`, `biomeDefs`, `weatherDefs`, `researchDefs`): `defName` 기준 Ordinal 정렬.
   - 하위 세트 컬렉션: `stats` (`statDef` Ordinal), `costList` (`thingDef` Ordinal), `stuffCategories` (Ordinal).
2. **Ordered List Collections (정의 순서 및 다중성 엄격 보존)**:
   - `activeMods`: `loadOrder` 속성값 기준 정렬 및 원본 리스트 순서 보존.
   - `verbs`: 게임플레이 로직에서 공격 모드 인덱스 및 우선순위를 나타내므로 **정렬하지 않고 원본 정의 순서 및 다중성 보존**.
   - `stages`: 질병의 심각도 진행 단계(`minSeverity`)를 나타내므로 **정렬하지 않고 정의 순서 보존**.
   - `comps`: 컴포넌트 틱 및 이벤트 처리 순서에 영향을 미치므로 **정렬하지 않고 정의 순서 보존**.
3. **`CanonicalNormalize` 및 `SerializeCanonicalJson` 연동**:
   - `SerializeCanonicalJson(manifest, canonicalNormalize: true)` 호출 시 자동으로 사전 정규화가 수행되어, 임의 순서로 삽입된 unordered set 입력이라도 동일한 canonical JSON 텍스트와 SHA256 다이제스트를 생성함 (TC08, TC09 검증 완료).

---

## 4. 변경 및 불변성 경계 검증

### 4.1 불변 소스 및 접두부 검증
- `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`:
  - 크기: `156,431` 바이트
  - SHA256: `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718` (불변 일치 100%)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj`:
  - 크기: `1,774` 바이트
  - SHA256: `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` (불변 일치 100%)
- `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 접두부(prefix):
  - Prefix Marker: `    public static class ContentProfileProvider`
  - 접두부 길이: `72,547` 바이트
  - 접두부 SHA256: `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (불변 일치 100%)
- 전체 `EngineHostCensus.cs`:
  - 크기: `112,873` 바이트
  - SHA256: `E94EA163BD6041C1ACA057D7E698277C0165E7F535FBCDBB765F3F68929348B5`

### 4.2 보존 베이스라인
- `Archive 19`: 완전 보존
- `Prior 732` (R1 147 + R2 107 + R3 133 + R4 232 + R5 113): 완전 보존
- `Pipeline 206`: 완전 보존
- `QA Evidence 1,342`: 완전 보존
- `Installed Steam DLL BB3B52...`: `UNKNOWN OPEN INCIDENT`로 공시 유지 (임의 조작 없음)

---

## 5. E1 정상 코덱 및 계약 검증 결과 (14 / 14 PASS)

- **하네스 프로젝트**: `scratch\EngineGate05R6CodecContract\Harness\Gate05R6CodecRunner.csproj`
- **하네스 실행 파일**: `scratch\EngineGate05R6CodecContract\Harness\bin\Debug\net472\Gate05R6CodecRunner.exe`
- **검증 일시**: `2026-10-08T10:35:00.9551037Z` (UTC)
- **대상 후보 어셈블리**: `scratch\EngineGate05R6CodecContract\Harness\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
- **어셈블리 SHA256**: `721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B`
- **산출물**:
  - `scratch\EngineGate05R6CodecContract\results.json`
  - `scratch\EngineGate05R6CodecContract\raw_console.txt`

### 5.1 테스트 결과표

| 테스트 ID | 검증 내용 및 목적 | 기대 결과 | 실제 결과 | 판정 |
|-----------|------------------|-----------|-----------|:----:|
| `TC01_RoundTrip_Canonical_Lossless` | 직렬화 -> 역직렬화 -> 재직렬화 후 SHA256 다이제스트 일치 검증 | $SHA_1 == SHA_2$, 무손실 round-trip | 일치 (`425049BD...`) | **PASS** |
| `TC02_Deterministic_Identical_Input` | 동일 데이터 인스턴스의 직렬화 다이제스트 일치 검증 | 결정론적 JSON 및 SHA 일치 | 일치 | **PASS** |
| `TC03_All_Eight_Def_Families_No_Sentinels` | 8개 Def 패밀리 포괄 및 센티넬/구분자(`Stats[`, `Mod:`) 부재 검증 | 센티넬 0건 검출, 8개 패밀리 완비 | 완비 확인 | **PASS** |
| `TC04_Floating_Point_Lossless_Precision` | 부동소수점(`float`) 경계값 및 정밀도 round-trip 보존 검증 | IEEE 754 float 값 손실 없음 | 오차 0.0 확인 | **PASS** |
| `TC05_Unicode_SpecialChars_Lossless` | 한국어, 일본어, 특수기호, 줄바꿈의 이스케이프 보존 검증 | 문자열 원형 100% 보존 | 일치 | **PASS** |
| `TC06_Null_Missing_Empty_Distinction` | `null` vs `""` vs 옵셔널 객체 `null`의 명확한 구분 직렬화 검증 | 센티넬 축약 없이 null 보존 | 구분 보존 확인 | **PASS** |
| `TC07_Ordered_Collections_Preservation` | `activeMods` loadOrder, `Verbs`, `stages`, `comps` 정의 순서 보존 검증 | 비정렬 대상의 원본 순서 보존 | 순서 100% 보존 | **PASS** |
| `TC08_Stable_Sorting_Determinism` | 무작위 순서 Def 컬렉션의 defName Ordinal 안정 정렬 검증 | 결정론적 Ordinal 정렬 | 일치 | **PASS** |
| `TC09_Unordered_Input_Normalization_Equivalence` | 뒤섞인 unordered 입력과 정렬된 입력의 정규화 동일성 검증 | 정규화 후 동일 JSON/다이제스트 | 일치 | **PASS** |
| `TC10_ValidateContract_Valid_Manifest` | 계약 준수 매니페스트에 대한 `ValidateContract` 통과 검증 | `valid == true`, 에러 0건 | 에러 0건 통과 | **PASS** |
| `TC11_ValidateContract_FailClosed_Violations` | 필수 필드 누락 시 계약 검증기의 Fail-Closed 위반 감지 검증 | `valid == false`, 사유 명시 | 위반 정확 감지 | **PASS** |
| `TC12_Distinct_Manifests_Distinct_Digests` | 단일 스칼라 변이 시 다이제스트 충돌 저항성 검증 | 고유 다이제스트 산출 | 일치 | **PASS** |
| `TC13_Cache_Invalidation_Lifecycle` | `InvalidateCache()` 호출 시 캐시 수명주기 초기화 검증 | IsCached false, 캐시 null | 초기화 확인 | **PASS** |
| `TC14_Schema_Version_And_Capability_Flags` | 스키마 버전, 계약 버전, 필수 capability flags 준수 검증 | 필수 플래그 5종 포함 | 완비 확인 | **PASS** |

**종합 결과: 14개 테스트 실행, 14개 PASS, 0개 FAIL (Verdict: PASS)**

---

## 6. 후보 바이너리 및 패키징 동일성 (Candidate Packaging Identity)

R5의 결함이었던 MVID 복제를 해결하고, PE 메타데이터로부터 Debug와 Release의 고유 MVID를 독립적으로 추출하여 바인딩했습니다.

### 6.1 Primary Selected Candidate (Debug)
- **DLL 경로**: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
- **DLL 크기**: `215,040` 바이트
- **DLL SHA256**: `721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B`
- **PDB 경로**: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **PDB 크기**: `52,280` 바이트
- **PDB SHA256**: `47FA9E93D5768175BF61EAB204CB4ED1BF6B45194407AA536F363B3497671C63`
- **실제 MVID**: `b3481641-2711-4b0e-96dd-db0983c2b689`
- **Assemblies 동기화**: `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` (동일 바이너리)

### 6.2 Alternate Candidate (Release)
- **DLL 경로**: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
- **DLL 크기**: `205,312` 바이트
- **DLL SHA256**: `2E6D66A16D2932155261034915E23B74B1BD73A0D28EE3D9F447A67152E2D3BC`
- **PDB 경로**: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **PDB 크기**: `39,032` 바이트
- **PDB SHA256**: `3FF4D9F3ECF99D54857FD95A033CCDCE21786BE5722032A9DE5A46875B98C1BE`
- **실제 MVID**: `354737fd-10a8-4160-8307-3e186c2118e6`

---

## 7. 한계 및 보존 사항 (Limitations & Preservation Policy)

1. **`NATIVE_UNTESTED`**: 본 작업은 Master 작업 지시서 및 범위 경계에 따라 순수 DTO 정상 코덱 및 계약 유효성 검증만 수행하였으며, RimWorld 게임 프로세스 및 native 런타임 실행은 수행하지 않았습니다 (UNTESTED 공시).
2. **`INSTALLED_DLL_INCIDENT_OPEN`**: Steam 설치 디렉터리의 어셈블리 SHA256(`BB3B52...`) 불일치 인시던트는 원인 규명 전까지 `UNKNOWN OPEN INCIDENT`로 유지되며, 임의 덮어쓰기나 정규화를 수행하지 않았습니다.
3. **`NO_SELF_CLOSURE`**: Developer 에이전트는 본 E1 검증 통과를 이유로 결함 클로저나 게이트 승인을 자의적으로 선언하지 않으며, 독립 QA(Sol)의 정적/동적 평가 및 Master의 거버넌스 처분을 대기합니다.
