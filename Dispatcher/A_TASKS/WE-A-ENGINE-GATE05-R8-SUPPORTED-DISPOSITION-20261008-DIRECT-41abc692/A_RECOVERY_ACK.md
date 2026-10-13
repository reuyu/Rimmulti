# A Recovery ACK — WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION / GATE05-R8-SUPPORTED-DISPOSITION

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692`
- **Work Package**: `WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION`
- **Revision**: `GATE05-R8-SUPPORTED-DISPOSITION` (Envelope 11)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-08T23:36:00+09:00

---

## 1. Concurrency & Pre-conditions Verification

1. **단일 Writer 및 Concurrency 확인**:
   - 현재 진행 중인 다른 활성 WP 없음 (`WP_ENGINE_GATE05_R7_CONTENT_ADMISSION` 완료 및 Master/Sol 승인·보존 확인).
   - Agent A의 단일 writer 원칙 유지.
2. **Controlling Documents 열람 완료**:
   - 지시문: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692\INSTRUCTIONS.md`
   - 작업 명세서: `docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION.md` (SHA `04899B58C8363454EB3B08DBB4BEE08A4A5948271516C7A192EE18339546D2DA`)
   - 릴리스: `docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R8_SUPPORTED_DISPOSITION_20261008.md` (SHA `CD684466CD7BB2CAA98D1E08E38B636260C9AC79CE6E03E1B6C4E436CDC3C709`)
   - 범위 베이스라인: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R8-SUPPORTED-DISPOSITION-20261008-DIRECT-41abc692\MASTER_R8_SCOPE_BASELINE.json`
   - Master R7 리뷰: `MASTER_REVIEW_ENGINE_GATE05_R7_CONTENT_ADMISSION_E1_20261008.md`, `MASTER_REVIEW_ENGINE_GATE05_R7_CONTENT_ADMISSION_INDEPENDENT_S1_20261008.md`
   - Sol R7 독립 리뷰: `QA_EngineHost_Gate05_R7_Content_Admission_Independent_S1_20261008.md`, `INDEPENDENT_FINDINGS.md`, `FIELD_COVERAGE_INDEX.json`, `PRODUCER_COVERAGE_INDEX.json`, `PRODUCER_PACKAGING_INDEX.json`

---

## 2. 엄격한 수정 및 보존 경계 (Strict Scope & Preservation Boundary)

1. **단일 수정 허용 파일**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 **`ContentProfileProvider` 클래스 marker(`    public static class ContentProfileProvider`) 이후 suffix 및 typed content helper DTO/메서드**에만 한정.
2. **불변 보존 대상 (Immutable Baseline)**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs`의 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 크기 156,431 bytes).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 크기 1,774 bytes).
   - 아카이브 베이스라인 19개, 기존 후보 동결본 954개 (R1/R2/R3/R4/R5/R6/R7), Pipeline 206개, QA 증거 1,652개, 관리 의존성 4개.
   - Steam 설치 원본 디렉터리 및 알려진 불일치 사건(`UNKNOWN OPEN INCIDENT`, `BB3B52...` 대 `2D64FF...`).
3. **엄격한 실행 제한**:
   - 게임 / native 런타임 실행 절대 금지.
   - 실제 provider compute / getter / cache properties / `InvalidateCache` 호출 금지.
   - 이전 / adverse / rejection 하네스 재실행 금지.
   - 오직 **새로운 positive pure normal DTO / helper runner** 단위 검증만 허용.

---

## 3. R8 핵심 개발 목표

1. **Replace Label-Only Patch/Settings Support with Actual Typed Disposition (`R7-M02`)**:
   - 단순 상수 문자열 동등 비교나 `patchCount` 비교를 넘어서, 관측된 mod/patch/settings에 대한 명시적 관측 상태(`ObservationStatus`) 및 지원 정책(`SupportDisposition`)을 도입.
   - 지원 범위 내의 PoC 프로필 경계를 명확히 하고 누락되거나 미지원되는 차원을 침묵 축약하지 않음.
2. **Classify Source Observations Before Projecting Children (`R7-M03`)**:
   - 수집기가 null 원소를 단순히 생략(continue)하여 하류 검증자가 누락을 파악하지 못하던 문제를 해결.
   - 정당한 옵셔널 부재(`legitimate optional absence`)와 필수 참조/데이터 관측 실패를 투영 전에 분류.
   - 유효한 빈 컬렉션(empty)과 미관측/초기화되지 않은 컬렉션을 엄격히 구분.
3. **Correct Content/Type Semantics & Supported Keys (`R7-M04`, `R7-M05`)**:
   - `SupportedVersionsReadOnly` 호환성 범위와 실제 관측된 모드 콘텐츠/패키지 버전을 구별하여 명명/표현.
   - Mod `loadOrder`/`packageId`, Assembly 복합 키의 유일성/다중성/tie-break 정책 명문화.
   - 기존의 결정론적 정렬, verbs/stages/comps 순서 및 다중성 보존, 동일 인스턴스 인-플레이스 변형 계약 유지.
4. **Bind New Disposition to Actual Admission (`R7-M01`)**:
   - R7의 `ComputeActualContentProfileManifest` -> `ValidateContract` 연결과 `ComputeActualContentProfileFingerprint` 지문 게이트를 유지하고, 새로운 관측/disposition 규칙을 검증에 일관되게 바인딩.
5. **Fresh Positive Pure Normal DTO / Helper Runner 및 정밀 패키징 (`R7-M06`, `R7-M07`)**:
   - 오직 긍정적 정상 DTO/헬퍼 검증으로 구성된 신규 하네스(`scratch\EngineGate05R8SupportedDisposition\Harness\`) 구축.
   - 실제 도구체인, dotnet SDK 버전, PE MVID, CodeView PDB, pre-run 및 post-run 그래프의 완결 바인딩.
