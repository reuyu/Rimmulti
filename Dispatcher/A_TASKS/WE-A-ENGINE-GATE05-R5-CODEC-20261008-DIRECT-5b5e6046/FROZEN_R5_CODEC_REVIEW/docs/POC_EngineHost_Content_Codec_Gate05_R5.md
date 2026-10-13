# POC EngineHost Content Codec Gate 05 R5 — E1 Verification Report

- **Task**: `WP_ENGINE_GATE05_R5_CODEC / GATE05-R5-CODEC` (Envelope 8)
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046`
- **Agent Role**: Antigravity A (Developer)
- **Report Kind**: E1 Developer Implementation & Verification Report
- **Date**: 2026-10-08
- **E1 Verdict**: `IMPLEMENTATION_PARTIAL` (Normal Codec Unit Controls 12/12 PASS; Native Execution Prohibited/Untested per Scope Boundary)

---

## 1. 개요 및 배경

Gate05-R4에 대한 Sol QA의 독립 정적 평가(S1) 및 Master의 수용 처분(`MASTER_REVIEW_ENGINE_GATE05_R4_INDEPENDENT_QA_S1_20261008.md`)에 따라:
1. **R4 성과 인정 및 보존**:
   - `SIMULATION` 제안 동작 모드와 `READ_ONLY` 검증자 역할 분리,
   - Operator 사전 승인 고정 executable 강제 및 `StartTime` fail-closed 검증,
   - `MD-128` 16개 권위 차원 완결 컨텍스트 및 `targetMapIndex` clamping 금지,
   - 공식 DLC Expansions 인벤토리 바인딩 및 캐시 무효화 수명주기 구현은 정상 보존되었습니다.
2. **R5 한정 개발 인가 (Narrow Sequential R5 Codec/Content-First)**:
   - 이전 R4까지 존재했던 loaded-content 매니페스트의 문자열 구분자/센티넬 조합(`Stats[...]`, `Mod:...:Patches=`, `defCensusDigest`, `modContentDigest`)을 완전히 폐기하고,
   - `ContentProfileProvider`의 supported loaded-content 매니페스트를 **typed/versioned canonical records**(`ADR-006B-v5`)로 정식 구현하며,
   - 8개 Def family(ThingDef, HediffDef, JobDef, SkillDef, FactionDef, BiomeDef, WeatherDef, ResearchProjectDef)와 DLC, Mod, Assembly를 완전한 lossless canonical JSON으로 직렬화하고,
   - 정상 production codec 단위 통제(Normal Codec Verification) 증거를 수집하는 것으로 한정 인가되었습니다.
3. **엄격한 변경 경계**:
   - Production 소스 변경은 `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 `ContentProfileProvider` suffix 및 content codec DTO/helper로만 제한되었습니다.
   - `WorkerBridge.cs`, `WorkerBridge.csproj`, `EngineHostCensus.cs` 불변 접두부(prefix)는 1바이트의 오차도 없이 고정 해시로 보존되었습니다.
   - 게임 실행, native 런타임 실행, 과거 adverse/security 하네스 재실행은 전면 금지되었습니다.

---

## 2. 지원 스키마 및 필드 매핑 / Disposition 명세 (ADR-006B-v5)

`ContentProfileProvider`는 기존 R4에서 다루었던 필드 커버리지를 100% 포괄하며, 센티넬 축약 없이 typed canonical record로 직렬화합니다.

### 2.1 스키마 개요
- **스키마 버전**: `ADR-006B-v5`
- **직렬화 규칙**:
  - `Newtonsoft.Json`: `Formatting.None`, `NullValueHandling.Include`, `FloatFormatHandling.String`, `FloatParseHandling.Double`.
  - Ordered List (`activeMods`, `verbs`, `stages`): 원본 정의 순서(Index/LoadOrder/Severity Ordinal)를 그대로 보존.
  - Set / Collection (`dlcExpansions`, `loadedAssemblies`, Def family collections, `stats`, `comps`, `stuffCategories`): `defName` 또는 `packageId + assemblyName`의 ordinal 기준으로 결정론적 정렬.
  - Floating Point: IEEE 754 표준 정밀도(`float`/`double`)를 유지하여 round-trip 손실 없음.
  - Null vs Empty: `null`은 JSON `null`로, 빈 문자열은 `""`로 명확히 구분 직렬화 (센티넬 `"(null)"` 완전 제거).

### 2.2 지원 필드 매핑 및 처리 (Disposition Table)

| Def Family / Scope | Field | Logical Type | Requiredness | Null / Empty 의미 | 정렬 / 순서 정책 | Disposition |
|-------------------|-------|--------------|--------------|-------------------|------------------|-------------|
| **Metadata** | `schemaVersion` | string | Required | `"ADR-006B-v5"` 고정 | 스키마 최상단 | SUPPORTED |
| | `buildIdentity` | string | Required | 빌드 식별자 (VersionControl) | 단일 값 | SUPPORTED |
| | `assemblyCSharpMvid` | string (UUID) | Required | Core Game MVID | 단일 값 | SUPPORTED |
| | `assemblyCSharpSha` | string (Hex) | Required | Assembly-CSharp.dll SHA256 | 단일 값 | SUPPORTED |
| | `capabilityFlags` | List\<string\> | Required | 5개 정규 capability flag 목록 | 고정 순서 | SUPPORTED |
| **DLC Expansions** | `defName` | string | Required | DLC 고유 식별자 | defName Ordinal | SUPPORTED |
| | `status` | string | Required | 활성화 상태 (`Status.ToString()`) | 단일 값 | SUPPORTED |
| | `linkedMod` | string? | Optional | 연계 패키지 ID (nullable) | null 보존 | SUPPORTED |
| | `statusDescription` | string? | Optional | 상태 부가 설명 (nullable) | null 보존 | SUPPORTED |
| **Active Mods** | `loadOrder` | int | Required | 모드 로드 순서 인덱스 (0-based) | loadOrder 보존 | SUPPORTED |
| | `packageId` | string | Required | 소문자 정규화 packageId | 단일 값 | SUPPORTED |
| | `name` | string | Required | 모드 표시 이름 | 단일 값 | SUPPORTED |
| | `modVersion` | string | Required | 모드 지원/버전 문자열 | 단일 값 | SUPPORTED |
| | `patchCount` | int | Required | 모드 내 Harmony/XML 패치 개수 | 단일 값 | SUPPORTED |
| **Loaded Assemblies** | `packageId` | string | Required | 소속 모드 packageId | packageId Ordinal | SUPPORTED |
| | `assemblyName` | string | Required | 어셈블리 단순 명칭 | assemblyName Ordinal | SUPPORTED |
| | `mvid` | string (UUID) | Required | 모듈 버전 ID | 단일 값 | SUPPORTED |
| | `sha256` | string (Hex) | Required | 디스크 어셈블리 SHA256 | 단일 값 | SUPPORTED |
| | `sizeBytes` | long | Required | 파일 바이트 크기 | 단일 값 | SUPPORTED |
| **ThingDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `category` | string | Required | ThingCategory enum string | 단일 값 | SUPPORTED |
| | `useHitPoints` | bool | Required | 내구도 사용 여부 | 단일 값 | SUPPORTED |
| | `stats[]` | StatModifierRecord | Optional | statDef + float value | statDef Ordinal | SUPPORTED |
| | `race` | RacePropsRecord? | Optional | 신체/건강/종족 속성 (nullable) | null 보존 | SUPPORTED |
| | `building` | BuildingPropsRecord? | Optional | 건축물 속성 (nullable) | null 보존 | SUPPORTED |
| | `ingestible` | IngestiblePropsRecord?| Optional | 섭취/영양 속성 (nullable) | null 보존 | SUPPORTED |
| | `costList[]` | ThingCostRecord | Optional | 재료 thingDef + count | thingDef Ordinal | SUPPORTED |
| | `stuffCategories[]` | List\<string\> | Optional | 허용 소재 카테고리 defName | defName Ordinal | SUPPORTED |
| | `costStuffCount` | int | Required | 필요 소재 수량 | 단일 값 | SUPPORTED |
| | `verbs[]` | VerbPropsRecord | Optional | verbClass + range | **정의 순서 보존** | SUPPORTED |
| | `comps[]` | List\<string\> | Optional | 컴포넌트 클래스 FullName | FullName Ordinal | SUPPORTED |
| **HediffDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `hediffClass` | string | Required | 구현 클래스 FullName | 단일 값 | SUPPORTED |
| | `lethalSeverity` | float | Required | 치명 한계 심각도 | 단일 값 | SUPPORTED |
| | `isBad` | bool | Required | 유해 여부 | 단일 값 | SUPPORTED |
| | `tendable` | bool | Required | 치료 가능 여부 | 단일 값 | SUPPORTED |
| | `stages[]` | HediffStageRecord | Optional | minSeverity + label | **심각도 순서 보존** | SUPPORTED |
| | `comps[]` | List\<string\> | Optional | 컴포넌트 클래스 FullName | FullName Ordinal | SUPPORTED |
| **JobDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `driverClass` | string | Required | 드라이버 클래스 FullName | 단일 값 | SUPPORTED |
| | `reportString` | string? | Optional | 작업 보고 문자열 (nullable) | null 보존 | SUPPORTED |
| | `playerInterruptible`| bool | Required | 플레이어 중단 가능 여부 | 단일 값 | SUPPORTED |
| | `casualInterruptible`| bool | Required | 캐주얼 중단 가능 여부 | 단일 값 | SUPPORTED |
| | `suspendable` | bool | Required | 일시정지 가능 여부 | 단일 값 | SUPPORTED |
| | `checkOverrideOnDamage`| string | Required | 피격 시 중단 정책 enum string | 단일 값 | SUPPORTED |
| | `makeTargetPrisoner` | bool | Required | 수감 대상 여부 | 단일 값 | SUPPORTED |
| **SkillDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `skillLabel` | string? | Optional | 스킬 레이블 (nullable) | null 보존 | SUPPORTED |
| | `disablingWorkTags` | string | Required | 비활성화 작업 태그 enum string | 단일 값 | SUPPORTED |
| | `pawnCreatorSummaryVisible`| bool | Required | 요약 표시 여부 | 단일 값 | SUPPORTED |
| **FactionDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `isPlayer` | bool | Required | 플레이어 세력 여부 | 단일 값 | SUPPORTED |
| | `settlementGenerationWeight`| float | Required | 정착지 생성 가중치 | 단일 값 | SUPPORTED |
| | `pawnGroupMakersCount`| int | Required | 폰 그룹 생성기 개수 투영 | 단일 값 | SUPPORTED |
| **BiomeDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `animalDensity` | float | Required | 동물 밀도 | 단일 값 | SUPPORTED |
| | `plantDensity` | float | Required | 식물 밀도 | 단일 값 | SUPPORTED |
| | `forageability` | float | Required | 채집성 계수 | 단일 값 | SUPPORTED |
| **WeatherDef** | `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `windSpeedFactor` | float | Required | 풍속 계수 | 단일 값 | SUPPORTED |
| | `rainRate` | float | Required | 강우량 계수 | 단일 값 | SUPPORTED |
| | `snowRate` | float | Required | 강설량 계수 | 단일 값 | SUPPORTED |
| **ResearchProjectDef**| `defName` | string | Required | stable identity key | defName Ordinal | SUPPORTED |
| | `label` | string? | Optional | presentation text (nullable) | null 보존 | SUPPORTED |
| | `baseCost` | float | Required | 기본 연구 비용 | 단일 값 | SUPPORTED |
| | `techLevel` | string | Required | 기술 수준 enum string | 단일 값 | SUPPORTED |
| | `requiredResearchBuilding`| string? | Optional | 필요 연구 작업대 defName (nullable)| null 보존 | SUPPORTED |

---

## 3. 변경 및 불변성 경계 검증

### 3.1 불변 대상 및 접두부 검증 결과
- `scratch\WorkerBridgeMod\Source\WorkerBridge.cs`:
  - 크기: `156,431` 바이트 (불변 일치)
  - SHA256: `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718` (불변 일치)
- `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj`:
  - 크기: `1,774` 바이트 (불변 일치)
  - SHA256: `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052` (불변 일치)
- `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 접두부(prefix):
  - Marker: `    public static class ContentProfileProvider`
  - 접두부 길이: `72,547` 바이트
  - 접두부 SHA256: `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887` (불변 일치 100%)
- 전체 `EngineHostCensus.cs`:
  - 크기: `99,735` 바이트
  - SHA256: `591408E898E1663732DAF362955248CE6C33CCBD213253D75C56FCE8E999D28C`

### 3.2 이전 동결본 및 환경 보호 상태
- `Archive 19`: 완전 보존
- `Prior 619` (R1 147 + R2 107 + R3 133 + R4 232): 완전 보존
- `Pipeline 206`: 완전 보존
- `QA Evidence 1,222`: 완전 보존
- `Installed Steam DLL BB3B52...` vs Archive `2D64FF...`: 임의 복구/정규화 없이 `UNKNOWN OPEN INCIDENT`로 공시 유지

---

## 4. E1 정상 코덱 검증 결과 (12 / 12 PASS)

- **하네스 프로젝트**: `scratch\EngineGate05R5Codec\Harness\Gate05R5CodecRunner.csproj`
- **하네스 실행 파일**: `scratch\EngineGate05R5Codec\Harness\bin\Debug\net472\Gate05R5CodecRunner.exe`
- **검증 일시**: `2026-10-08T08:57:16.2189205Z` (UTC)
- **대상 어셈블리**: `scratch\EngineGate05R5Codec\Harness\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
- **어셈블리 SHA256**: `930B69D012F34BFD3BB50F97B86629BAEA082D201A3A81696549DF1450075AE8`
- **결과 산출물**:
  - `scratch\EngineGate05R5Codec\results.json`
  - `scratch\EngineGate05R5Codec\raw_console.txt`

### 4.1 전수 테스트 통제 결과표

| 테스트 ID | 검증 내용 및 목적 | 기대 결과 | 실제 결과 | 판정 |
|-----------|------------------|-----------|-----------|:----:|
| `TC01_RoundTrip_Canonical_Lossless` | 직렬화 -> 역직렬화 -> 재직렬화 후 SHA256 다이제스트 일치 검증 | $SHA_1 == SHA_2$, 손실 없는 round-trip | 일치 (`866CA551...`) | **PASS** |
| `TC02_Deterministic_Identical_Input` | 동일 데이터를 가진 두 독립 인스턴스의 직렬화 다이제스트 일치 검증 | 결정론적 JSON 및 SHA 일치 | 일치 | **PASS** |
| `TC03_All_Eight_Def_Families_No_Sentinels` | 8개 Def 패밀리 전수 포괄 및 기존 센티넬/구분자(`Stats[`, `Mod:`) 부재 검증 | 센티넬 문자열 0건 검출 | 센티넬 전무, 8개 패밀리 완비 | **PASS** |
| `TC04_Floating_Point_Lossless_Precision` | 부동소수점(`float`) 경계값 및 소수점 정밀도 round-trip 보존 검증 | IEEE 754 float 값 손실 없음 | 오차 0.0 확인 | **PASS** |
| `TC05_Unicode_SpecialChars_Lossless` | 한국어, 일본어, 독일어 움라우트, 특수기호, 줄바꿈의 이스케이프 보존 검증 | 문자열 원형 100% 보존 | 원형 일치 | **PASS** |
| `TC06_Null_Missing_Empty_Distinction` | `null` vs 빈 문자열 `""` vs 옵셔널 객체 `null`의 명확한 구분 직렬화 검증 | 센티넬 축약 없이 null 보존 | 구분 보존 확인 | **PASS** |
| `TC07_Ordered_Collections_Preservation` | `activeMods` loadOrder, `Verbs` 정의 순서, `stages` 심각도 순서 보존 검증 | 순서 변경 없이 인덱스 보존 | 순서 100% 보존 | **PASS** |
| `TC08_Stable_Sorting_Determinism` | 무작위 순서로 입력된 Def 컬렉션의 defName Ordinal 안정 정렬 검증 | 입력 순서와 무관한 결정론적 JSON | 일치 | **PASS** |
| `TC09_Distinct_Manifests_Distinct_Digests` | 단일 스칼라 값 변이 시 다이제스트 충돌 저항성 검증 | $SHA(A) \neq SHA(B)$ | 고유 다이제스트 산출 | **PASS** |
| `TC10_Cache_Invalidation_Lifecycle` | `InvalidateCache()` 호출 시 캐시 변수 및 에러 상태의 초기화 수명주기 검증 | IsCached false, 캐시 null | 초기화 확인 | **PASS** |
| `TC11_FailClosed_Unadmitted_Runtime_Rejection` | 미승인/미초기화 런타임 환경에서 호출 시 fail-closed 거부 검증 | 예외 발생 및 fail-closed 거부 | Fail-Closed 확인 | **PASS** |
| `TC12_Schema_Version_And_Capability_Flags` | `ADR-006B-v5` 스키마 및 필수 capability flags 준수 검증 | 필수 플래그 5종 포함 | 완비 확인 | **PASS** |

**종합 결과: 12개 테스트 실행, 12개 PASS, 0개 FAIL (Verdict: PASS)**

---

## 5. 후보 바이너리 및 패키징 동일성 (Candidate Packaging Identity)

### 5.1 Primary Selected Candidate (Debug)
- **DLL 경로**: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll`
- **DLL 크기**: `204,800` 바이트
- **DLL SHA256**: `930B69D012F34BFD3BB50F97B86629BAEA082D201A3A81696549DF1450075AE8`
- **PDB 경로**: `scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **PDB 크기**: `49,920` 바이트
- **PDB SHA256**: `06F616C6FD54E07AE87AE2B16E60B1F4AB6FA0AB664D77D71CED084ABC38D2E4`
- **MVID**: `0e6b7cca-e02c-4af5-97da-5de31ec7aec3`
- **Assemblies 동기화**: `scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` (동일 바이너리)

### 5.2 Alternate Candidate (Release)
- **DLL 경로**: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll`
- **DLL 크기**: `195,584` 바이트
- **DLL SHA256**: `77AF633BBA063304E74C9F1D5AE7102CAE856D591201646226AFE6DD23B81EC7`
- **PDB 경로**: `scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb`
- **PDB 크기**: `37,584` 바이트
- **PDB SHA256**: `E53DE9504FE257D19D789EFD196DA907704690F3F5CD6A5914B3AC7C59E77233`
- **MVID**: `0e6b7cca-e02c-4af5-97da-5de31ec7aec3`

---

## 6. 한계 공시 (Limitations) 및 거버넌스 준수

1. **정상 코덱 단위 검증 한정 (Codec E1 Only)**:
   - 본 검증은 프로덕션 코덱 구현체의 정규 데이터 직렬화/역직렬화/결정론/정밀도/정렬/수명주기 단위 통제만을 수행하였습니다.
   - 실제 게임 프로세스 및 Unity 엔진 로딩 런타임 환경은 작업 지침(`WP_ENGINE_GATE05_R5_CODEC.md`)상 실행이 금지되었으므로 `NATIVE_UNTESTED` 상태입니다.
2. **권위 처분 및 닫힘 선언 불가**:
   - 개발자 A는 본 단위 검증 통과를 결함 해결(Closure)이나 E2 릴리스로 자의 승격하지 않습니다.
   - 모든 Gate05 및 Engine 결함의 최종 승인 및 릴리스는 Master의 처분과 Sol QA의 독립 정적/동적 평가에 따릅니다.
3. **Steam 설치 바이너리 불일치 사건**:
   - `BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61` 건은 미해결 오픈 상태(`UNKNOWN OPEN INCIDENT`)를 유지하며 임의 조작하지 않았습니다.
