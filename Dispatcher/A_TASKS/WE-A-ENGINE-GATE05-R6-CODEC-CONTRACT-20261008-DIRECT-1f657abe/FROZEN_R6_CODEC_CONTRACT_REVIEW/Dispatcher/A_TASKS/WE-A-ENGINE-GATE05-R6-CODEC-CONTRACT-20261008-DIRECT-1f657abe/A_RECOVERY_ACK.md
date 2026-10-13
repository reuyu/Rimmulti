# A Recovery ACK — WP_ENGINE_GATE05_R6_CODEC_CONTRACT / GATE05-R6-CODEC-CONTRACT

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe`
- **Work Package**: `WP_ENGINE_GATE05_R6_CODEC_CONTRACT`
- **Revision**: `GATE05-R6-CODEC-CONTRACT` (Envelope 9)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-08T19:26:00+09:00

---

## 1. Concurrency & Pre-conditions Verification

1. **중복 작업 확인**:
   - 현재 진행 중인 다른 활성 WP 없음 (`WP_ENGINE_GATE05_R5_CODEC` 완료 및 Master/Sol 리뷰 보존 확인).
   - Agent A의 단일 writer 원칙 유지.
2. **Controlling Documents 열람 완료**:
   - 지시문: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe\INSTRUCTIONS.md`
   - 작업 명세서: `docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R6_CODEC_CONTRACT.md` (SHA `E926A624C6C684885FEA869C7F0D13B9D996F69282213ACB1729395970E4EFCD`)
   - 릴리스: `docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R6_CODEC_CONTRACT_20261008.md` (SHA `23A90E31D05D163E583AE0C448B7AFF91DDBB973CB9D879B0DEE19EE2ACD4B44`)
   - 범위 베이스라인: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe\MASTER_R6_SCOPE_BASELINE.json`
   - Master R5 리뷰: `MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_E1_20261008.md`, `MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_INDEPENDENT_S1_20261008.md`
   - Sol R5 독립 리뷰 보고서 및 메타데이터: `QA_EngineHost_Gate05_R5_Codec_Independent_S1_20261008.md`, `INDEPENDENT_FINDINGS.md`, `FIELD_COVERAGE_INDEX.json`

---

## 2. 엄격한 수정 및 보존 경계 (Strict Scope & Preservation Boundary)

1. **단일 수정 허용 파일**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 **`ContentProfileProvider` 클래스 marker(`    public static class ContentProfileProvider`) 이후 suffix 및 codec helper DTO/메서드**에만 한정.
2. **불변 보존 대상 (Immutable Baseline)**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs`의 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 크기 156,431 bytes).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 크기 1,774 bytes).
   - 아카이브 베이스라인 19개, 기존 후보 동결본 732개 (R1/R2/R3/R4/R5), Pipeline 206개, QA 증거 1,342개.
   - Steam 설치 원본 디렉터리 및 알려진 불일치 사건(`UNKNOWN OPEN INCIDENT`, `BB3B52...` 대 `2D64FF...`).
3. **엄격한 실행 제한**:
   - 게임 / native 런타임 실행 절대 금지.
   - 이전 / adverse 하네스 재실행 금지.
   - 실제 provider compute / cache getter 호출 금지.
   - 오직 순수 DTO normal codec controls 단위 검증만 허용.

---

## 3. R6 핵심 개발 목표

1. **Explicit Supported Content Contract & Disposition Specification (MD-130)**:
   - 8개 Def family projection에 대한 명시적 지원/미지원 계약 수립.
   - 필수 머티리얼(`required material`)과 합법적 부재(`legitimate optional absence`)의 엄격한 구분.
   - 미관측 필수 속성을 빈 성공 목록이나 센티넬로 축약하지 않고 Fail-Closed로 거부.
   - 모드 패치/세팅 머티리얼의 explicit disposition 공시.
2. **Canonical Sorting Boundary 확립**:
   - 선언된 unordered sets(`thingDefs`, `biomeDefs`, `stats`, `costList` 등)의 명시적 canonical normalization 구현.
   - `activeMods` (loadOrder), `verbs` (인덱스/다중성 순서), `stages` (심각도 순서), `comps`의 순서 및 다중성 엄격 보존.
3. **용어 및 Capability Flags 정렬**:
   - 실제 구현된 범위에 맞게 `TACTICAL_PROBE_V4`, `READ_ONLY`, `SIMULATION`, `GATE05_R6_CODEC_CONTRACT`, `ADR006B_LOSSLESS_CANONICAL_CONTENT_V5` 정렬.
4. **정확한 최종 패키징 (Debug 및 Release MVID 독립 추출)**:
   - 빌드된 PE 메타데이터에서 실제 Release MVID(`7552980a-c4e1-4126-9451-e2114be623ae` 등)와 Debug MVID를 별도 추출하여 바인딩.
5. **순수 Normal Codec 단위 증거 수집 (No Fake PASS / No TC11 Runtime Harness)**:
   - 순수 DTO normal input 기반 독립 하네스 실행 및 정규 증거 수집.
