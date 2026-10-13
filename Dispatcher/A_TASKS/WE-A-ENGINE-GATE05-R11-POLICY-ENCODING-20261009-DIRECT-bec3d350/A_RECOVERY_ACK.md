# A Recovery ACK — WP_ENGINE_GATE05_R11_POLICY_ENCODING / GATE05-R11-POLICY-ENCODING

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350`
- **Work Package**: `WP_ENGINE_GATE05_R11_POLICY_ENCODING`
- **Revision**: `GATE05-R11-POLICY-ENCODING` (Envelope 14)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-09T06:14:00+09:00

---

## 1. Concurrency & Pre-conditions Verification

1. **단일 Writer 및 Concurrency 확인**:
   - 현재 진행 중인 다른 활성 WP 없음 (`WP_ENGINE_GATE05_R10_PACKAGE_POLICY` 완료 및 Master/Sol 독립 검증 정상 helper PASS 수용 확인).
   - Agent A의 단일 writer 원칙 유지.
2. **Controlling Documents 열람 완료**:
   - 지시문: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\INSTRUCTIONS.md` (WP SHA `C2BFBFED...`, Release SHA `F3EB207A...` 대조)
   - 작업 명세서: `docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R11_POLICY_ENCODING.md`
   - 릴리스: `docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R11_POLICY_ENCODING_20261009.md`
   - 범위 베이스라인: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\MASTER_R11_SCOPE_BASELINE.json`
   - Master R10 E1 및 독립 S1 리뷰 문서: `MASTER_REVIEW_ENGINE_GATE05_R10_PACKAGE_POLICY_E1_20261009.md`, `MASTER_REVIEW_ENGINE_GATE05_R10_PACKAGE_POLICY_INDEPENDENT_S1_20261009.md`
   - Sol R10 독립 리뷰: `QA_EngineHost_Gate05_R10_Package_Policy_Independent_S1_20261009.md`, `INPUT_EXPECTED_SEMANTICS.json`, `INDEPENDENT_REVIEW_FINDINGS.json`, `CRITERIA_DISPOSITION.json`

---

## 2. 엄격한 수정 및 보존 경계 (Strict Scope & Preservation Boundary)

1. **단일 수정 허용 파일**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 **`ContentProfileProvider` 클래스 marker(`    public static class ContentProfileProvider`) 이후 suffix 및 typed policy declaration/helper DTO/메서드**에만 한정.
2. **불변 보존 대상 (Immutable Baseline)**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs`의 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 크기 156,431 bytes).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 크기 1,774 bytes).
   - 아카이브 베이스라인 19개, 기존 후보 동결본 1,177개 (R1/R2/R3/R4/R5/R6/R7/R8/R9/R10), Pipeline 206개, QA 증거 2,578개, 관리 의존성 4개.
   - Steam 설치 원본 디렉터리 및 알려진 불일치 사건(`UNKNOWN OPEN INCIDENT`, `BB3B52...` 대 `2D64FF...`).
3. **엄격한 실행 제한**:
   - 게임 / native 런타임 실행 절대 금지.
   - 실제 provider compute / getter / cache properties / `InvalidateCache` 호출 금지.
   - `ConfigureExpectedPackagePolicy` 등 configuration seam 런타임 호출 금지.
   - 이전 / adverse / negative / rejection / mismatch 하네스 실행 금지. Producer R10의 TC15/TC18negative/TC19configuration 실행 범위 일탈을 반복하지 않음.
   - 오직 **새로운 positive pure normal DTO / helper runner** 단위 검증만 허용.

---

## 3. R11 핵심 개발 목표 (POLICY_ENCODING)

1. **Concrete Typed Versioned Canonical Policy Declaration**:
   - `ExpectedPackagePolicyDeclaration` 레코드 정의:
     - 고정 필드 순서: `schemaVersion` (상수 `"WE-PACKAGE-POLICY-V1"`), `policyId` (string), `revision` (string), `admittedPackageIds` (ordered `List<string>`).
     - Digest는 선언 자체의 입력 필드가 아님.
2. **Pure Canonical Policy Serialize/Deserialize APIs**:
   - `SerializePackagePolicy(ExpectedPackagePolicyDeclaration policy)`:
     - 컴팩트 canonical JSON UTF-8 (BOM 없음, 공백 없음, 고정 필드 순서).
     - 결정론적/무손실/문화권 독립적 문자열 이스케이프.
   - `DeserializePackagePolicy(string json)`:
     - 정규 라운드트립으로 타입화된 선언을 정확히 재구성.
3. **Opaque Identity Preservation & No Trim**:
   - `policyId` 및 `revision`은 불투명(opaque) 비어있지 않은 문자열로, 서수(ordinal)로 비교.
   - 공백(앞/뒤/내부), 유니코드, 구두점, 원본 철자를 `Trim`, 대소문자 변환, 숫자 파싱, 유니코드 정규화 없이 그대로 보존.
   - `CanonicalNormalize` 등에서 `policyId`/`revision`을 `Trim()`하던 기존 변환을 완전히 제거.
4. **Digest Hashing Routed Through Canonical Declaration**:
   - 임의 구분자 결합(`$"{policyId}|{revision}|{pkg1,pkg2,...}"`) 대신, 정확한 컴팩트 정규 JSON 바이트의 SHA-256 대문자 16진수 해시로 계산.
   - 모든 순수 다이제스트 오버로드가 이 정규 선언 인코딩을 경유하도록 통일.
5. **Check / Admission / Content Codec Linkage**:
   - `CheckPackagePolicy`, `TryAdmitWithPackagePolicy`, 매니페스트 콘텐츠 바인딩이 동일한 불투명 identity 및 canonical digest 의미론을 엄격히 공유.
6. **Positive Normal Evidence Only**:
   - 오직 긍정적 정상 통제 케이스로만 하네스를 구성하고 실행.
   - R9 버전 의미론(미상 `null` 보존) 및 기존 수치/순서/다중성 정상 회귀 유지.
