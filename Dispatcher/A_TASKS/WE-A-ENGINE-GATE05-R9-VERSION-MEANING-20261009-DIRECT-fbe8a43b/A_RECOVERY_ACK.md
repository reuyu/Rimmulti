# A Recovery ACK — WP_ENGINE_GATE05_R9_VERSION_MEANING / GATE05-R9-VERSION-MEANING

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b`
- **Work Package**: `WP_ENGINE_GATE05_R9_VERSION_MEANING`
- **Revision**: `GATE05-R9-VERSION-MEANING` (Envelope 12)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-09T02:28:00+09:00

---

## 1. Concurrency & Pre-conditions Verification

1. **단일 Writer 및 Concurrency 확인**:
   - 현재 진행 중인 다른 활성 WP 없음 (`WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION` 완료 및 보존, Master S1 리뷰 확인).
   - Agent A의 단일 writer 원칙 유지.
2. **Controlling Documents 열람 완료**:
   - 지시문: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b\INSTRUCTIONS.md` (SHA `75FED0DF...` WP 및 `7AB19FF7...` Release 확인)
   - 작업 명세서: `docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R9_VERSION_MEANING.md`
   - 릴리스: `docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R9_VERSION_MEANING_20261009.md`
   - 결함 기록: `docs\WarEconomy_Master_Handoff_20261006\DEFECT_ENGINE_CONTENT_VERSION_SEMANTIC_20261009_01.md`
   - 범위 베이스라인: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b\MASTER_R9_SCOPE_BASELINE.json`
   - Master R8 S1 독립 리뷰: `MASTER_REVIEW_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION_INDEPENDENT_S1_20261009.md`
   - Sol R8 독립 리뷰: `QA_EngineHost_Gate05_R8_Supported_Disposition_Independent_S1_20261009.md`, `NORMAL_SEMANTIC_REGRESSION.json`, `INPUT_EXPECTED_SEMANTICS.json`, `INDEPENDENT_FINDINGS.md`

---

## 2. 엄격한 수정 및 보존 경계 (Strict Scope & Preservation Boundary)

1. **단일 수정 허용 파일**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 **`ContentProfileProvider` 클래스 marker(`    public static class ContentProfileProvider`) 이후 suffix 및 typed version helper DTO/메서드**에만 한정.
2. **불변 보존 대상 (Immutable Baseline)**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs`의 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 크기 156,431 bytes).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 크기 1,774 bytes).
   - 아카이브 베이스라인 19개, 기존 후보 동결본 1,029개 (R1/R2/R3/R4/R5/R6/R7/R8), Pipeline 206개, QA 증거 1,834개, 관리 의존성 4개.
   - Steam 설치 원본 디렉터리 및 알려진 불일치 사건(`UNKNOWN OPEN INCIDENT`, `BB3B52...` 대 `2D64FF...`).
3. **엄격한 실행 제한**:
   - 게임 / native 런타임 실행 절대 금지.
   - 실제 provider compute / getter / cache properties / `InvalidateCache` 호출 금지.
   - 이전 / adverse / rejection 하네스 재실행 금지.
   - 오직 **새로운 positive pure normal DTO / helper runner** 단위 검증만 허용.

---

## 3. R9 핵심 개발 목표 (VERSION_MEANING Repair)

1. **Keep compatibility and content version distinct**:
   - `CanonicalNormalize`에서 `compatibilityVersionRange`와 `modVersion` 간의 양방향 cross-fill(상호 유추/동기화) 로직 전면 제거.
   - 정렬(sorting)은 정의된 세트/목록 순서만 변경할 수 있으며, 지원 게임 버전 범위로부터 실제 모드 콘텐츠 버전을 제조하거나 모드 버전으로부터 호환성 범위를 날조할 수 없음.
   - generic false transport와 canonical true 정규화/재구성 전반에 걸쳐 정당한 옵셔널 미상(unknown) `null` 상태 보존.
2. **Correct actual projection source meaning**:
   - `ComputeActualContentProfileManifest`에서 `mod.ModMetaData.SupportedVersionsReadOnly`를 `compatibilityVersionRange`에만 기록하고, `modVersion`에는 할당하지 않음 (`modVersion = null`).
   - 실제 관측 가능한 콘텐츠 버전 소스가 없는 경우 명시적 미상(`null`)을 유지하며, 지원 게임 버전을 모드 버전으로 날조하지 않음.
3. **Bind minimal changed contract honestly**:
   - 콘텐츠 계약 버전 `ADR-006B-v5-R9` 및 기능 플래그 `GATE05_R9_VERSION_MEANING` 선언.
   - DTO, 계약 검증(`ValidateContract`), 실제 수집기간 일관된 의미론적 규칙 유지.
   - R8에서 확립된 자식 원천 관측 fail-closed 분류, 모드 `loadOrder`/`packageId` 고유성, 로드된 어셈블리 복합 키 유일성 및 정렬 결정론은 100% 보존.
4. **Fresh normal targeted evidence**:
   - 신규 러너 `scratch\EngineGate05R9VersionMeaning\Harness\` 구축.
   - R8의 잘못된 TC16 cross-fill 오라클을 대체하여, 옵셔널 미상 `modVersion = null`이 정규화 및 직렬화(true/false) 후에도 `null`로 보존됨을 검증하는 독립 오라클 구현 (en-US 및 de-DE 양대 문화권 검증).
   - 실제 PE MVID, PDB, pre-run 및 post-run 동결본 생성 및 기록.
