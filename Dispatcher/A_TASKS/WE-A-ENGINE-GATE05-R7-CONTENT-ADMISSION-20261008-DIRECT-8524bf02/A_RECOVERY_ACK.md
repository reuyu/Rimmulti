# A Recovery ACK — WP_ENGINE_GATE05_R7_CONTENT_ADMISSION / GATE05-R7-CONTENT-ADMISSION

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02`
- **Work Package**: `WP_ENGINE_GATE05_R7_CONTENT_ADMISSION`
- **Revision**: `GATE05-R7-CONTENT-ADMISSION` (Envelope 10)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-08T22:00:00+09:00

---

## 1. Concurrency & Pre-conditions Verification

1. **중복 작업 확인**:
   - 현재 진행 중인 다른 활성 WP 없음 (`WP_ENGINE_GATE05_R6_CODEC_CONTRACT` 완료, Master/Sol 리뷰 보존 확인).
   - Agent A의 단일 writer 원칙 유지.
2. **Controlling Documents 열람 완료**:
   - 지시문: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02\INSTRUCTIONS.md`
   - 작업 명세서: `docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R7_CONTENT_ADMISSION.md` (SHA `10640DB1668A5E7436B7AA7D8843862EC2A0E225A891C9A2AE4459206DDA077A`)
   - 릴리스: `docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R7_CONTENT_ADMISSION_20261008.md` (SHA `41DA9B67A17750B9C7AD39DD70405D6D17518FB97C797D2918E2C175795935B4`)
   - 범위 베이스라인: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R7-CONTENT-ADMISSION-20261008-DIRECT-8524bf02\MASTER_R7_SCOPE_BASELINE.json`
   - Master R6 리뷰: `MASTER_REVIEW_ENGINE_GATE05_R6_CODEC_CONTRACT_E1_20261008.md`, `MASTER_REVIEW_ENGINE_GATE05_R6_CODEC_CONTRACT_INDEPENDENT_S1_20261008.md`
   - Sol R6 독립 리뷰 보고서 및 메타데이터: `QA_EngineHost_Gate05_R6_Codec_Contract_Independent_S1_20261008.md`, `INDEPENDENT_FINDINGS.md`, `FIELD_COVERAGE_INDEX.json`, `PRODUCER_COVERAGE_INDEX.json`, `PRODUCER_PACKAGING_INDEX.json`

---

## 2. 엄격한 수정 및 보존 경계 (Strict Scope & Preservation Boundary)

1. **단일 수정 허용 파일**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 **`ContentProfileProvider` 클래스 marker(`    public static class ContentProfileProvider`) 이후 suffix 및 typed content helper DTO/메서드**에만 한정.
2. **불변 보존 대상 (Immutable Baseline)**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs`의 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 크기 156,431 bytes).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 크기 1,774 bytes).
   - 아카이브 베이스라인 19개, 기존 후보 동결본 844개 (R1/R2/R3/R4/R5/R6), Pipeline 206개, QA 증거 1,489개, 관리 의존성 4개.
   - Steam 설치 원본 디렉터리 및 알려진 불일치 사건(`UNKNOWN OPEN INCIDENT`, `BB3B52...` 대 `2D64FF...`).
3. **엄격한 실행 제한**:
   - 게임 / native 런타임 실행 절대 금지.
   - 실제 provider compute / getter / cache properties / `InvalidateCache` 호출 금지 (R6 TC13 일탈 재발 금지).
   - 이전 / adverse / rejection 하네스 재실행 금지 (R6 TC11 비정상 입력 재실행 금지).
   - 오직 **새로운 positive pure normal DTO / helper runner** 단위 검증만 허용.

---

## 3. R7 핵심 개발 목표

1. **Wire Actual Content Admission Validation (`R6-M02`)**:
   - 실제 profile 생성(`ComputeActualContentProfileManifest`, `ComputeActualContentProfileFingerprint`) 시점에 `ValidateContract`를 강제 호출하여, 유효하지 않은 profile이 성공 다이제스트를 발급받지 못하도록 admission gate 연결.
   - 제네릭 DTO transport(`SerializeCanonicalJson` / `DeserializeCanonicalJson`)와 실제 권위 profile admission 경계를 명확히 분리.
2. **Executable Coverage & Disposition (`R6-M03`)**:
   - 8개 Def family 전수 프로젝션에 대해 필수 필드 및 자식 요소의 누락/침묵 축약 방지.
   - 정당한 옵셔널 부재(`legitimate optional absence`)와 미관측 필수 머티리얼(`unobserved required material`)의 엄격한 구분.
   - 수집기의 비어있지 않음(`nonempty`) 규칙과 헬퍼의 목록 존재(`list-presence`) 규칙 분리 정리.
3. **Patch / Settings Support Enforced Boundary (`R6-M04`)**:
   - 문서상 고지만 존재하던 `OUTSIDE_POC_SUPPORTED_ADMISSION`을 실행 가능한 manifest 속성(`contentContractVersion`, `supportedCoverageProfile`, `modPatchSupportStatus`) 및 계약 검증 로직으로 바인딩.
   - 모드 패치 수량은 수집하되, 원시 패치 AST 및 사용자 모드 설정은 PoC 지원 경계 외로 명시 바인딩.
4. **Canonical Contract: Key Uniqueness, Tie Policy & Mutation Policy (`R6-M01`, `R6-M05`)**:
   - Distinct-key 정렬 규칙 및 동순위(tie-break) 결정론적 정책 명시.
   - `CanonicalNormalize`의 인-플레이스 변경 동작 명문화 및 비변경 전송(transport false) 경계 보존.
5. **Positive Pure Normal DTO / Helper Runner 및 정밀 패키징 (`R6-M06`, `R6-M07`)**:
   - 오직 긍정적 정상 DTO/헬퍼 테스트만으로 구성된 신규 하네스(`scratch\EngineGate05R7ContentAdmission\Harness\`) 구축.
   - 동적 타임스탬프, 실측 dotnet SDK 버전, PE MVID, CodeView PDB 경로, pre-run 및 post-run 그래프의 완결 바인딩.
