# A Recovery ACK — WP_ENGINE_GATE05_R10_PACKAGE_POLICY / GATE05-R10-PACKAGE-POLICY

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb`
- **Work Package**: `WP_ENGINE_GATE05_R10_PACKAGE_POLICY`
- **Revision**: `GATE05-R10-PACKAGE-POLICY` (Envelope 13)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-09T05:25:00+09:00

---

## 1. Concurrency & Pre-conditions Verification

1. **단일 Writer 및 Concurrency 확인**:
   - 현재 진행 중인 다른 활성 WP 없음 (`WP_ENGINE_GATE05_R9_VERSION_MEANING` 완료 및 Master/Sol 독립 검증 PASS 확인).
   - 결함 `ENGINE-CONTENT-VERSION-SEMANTIC-20261009-01`은 좁은 범위에서 `CLOSED_SCOPED_NORMAL_CODEC_VERSION_MEANING`으로 해결 및 보존됨.
   - Agent A의 단일 writer 원칙 유지.
2. **Controlling Documents 열람 완료**:
   - 지시문: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\INSTRUCTIONS.md` (WP SHA `6CC77C08...`, Release SHA `541BB524...` 대조)
   - 작업 명세서: `docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R10_PACKAGE_POLICY.md`
   - 릴리스: `docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R10_PACKAGE_POLICY_20261009.md`
   - 범위 베이스라인: `Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\MASTER_R10_SCOPE_BASELINE.json`
   - Master R9 E1 및 독립 S1 리뷰 문서: `MASTER_REVIEW_ENGINE_GATE05_R9_VERSION_MEANING_E1_20261009.md`, `MASTER_REVIEW_ENGINE_GATE05_R9_VERSION_MEANING_INDEPENDENT_S1_20261009.md`
   - Sol R9 독립 리뷰: `QA_EngineHost_Gate05_R9_Version_Meaning_Independent_S1_20261009.md`, `TARGETED_REGRESSION_INDEX.json`, `INPUT_EXPECTED_SEMANTICS.json`, `INDEPENDENT_FINDINGS.md`

---

## 2. 엄격한 수정 및 보존 경계 (Strict Scope & Preservation Boundary)

1. **단일 수정 허용 파일**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 **`ContentProfileProvider` 클래스 marker(`    public static class ContentProfileProvider`) 이후 suffix 및 typed package policy helper DTO/메서드**에만 한정.
2. **불변 보존 대상 (Immutable Baseline)**:
   - `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs`의 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.cs` (SHA `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`, 크기 156,431 bytes).
   - `scratch\WorkerBridgeMod\Source\WorkerBridge.csproj` (SHA `571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052`, 크기 1,774 bytes).
   - 아카이브 베이스라인 19개, 기존 후보 동결본 1,101개 (R1/R2/R3/R4/R5/R6/R7/R8/R9), Pipeline 206개, QA 증거 2,160개, 관리 의존성 4개.
   - Steam 설치 원본 디렉터리 및 알려진 불일치 사건(`UNKNOWN OPEN INCIDENT`, `BB3B52...` 대 `2D64FF...`).
3. **엄격한 실행 제한**:
   - 게임 / native 런타임 실행 절대 금지.
   - 실제 provider compute / getter / cache properties / `InvalidateCache` 호출 금지.
   - 이전 / adverse / rejection 하네스 재실행 금지.
   - 오직 **새로운 positive pure normal DTO / helper runner** 단위 검증만 허용.

---

## 3. R10 핵심 개발 목표 (PACKAGE_POLICY)

1. **Explicit Expected Package Policy Definition & Deterministic Digest**:
   - 실제 관측 매니페스트와 명확히 분리되는 타입화된 `ExpectedPackagePolicyRecord` (`policyId`, `revision`, `admittedPackageIds`, `policyDigest`) 정의.
   - 정책 ID, 리비전, 정렬된 승인 패키지 ID 시퀀스를 바인딩하는 결정론적 정규 다이제스트 계산 로직 구현.
2. **Pure Package Comparison & Admission Helper**:
   - 기대 정책과 관측 매니페스트의 활성 모드 목록을 엄격히 비교하는 순수 헬퍼 `CheckPackagePolicy` 및 `TryAdmitWithPackagePolicy` 구현.
   - 관측된 모드 목록을 그대로 복사하여 기대 정책을 날조하는 행위 원천 차단.
   - 제네릭 DTO 직렬화와 지원 프로필 승인을 분리하여 제네릭 전송이 프로필 거부로 왜곡되지 않도록 유지.
3. **ComputeActualContentProfileManifest Linkage & Fail-Closed Seam**:
   - 실제 `ComputeActualContentProfileManifest`에서 관측된 모드 목록을 `_configuredExpectedPackagePolicy`와 대조.
   - 정책 미구성 시 조용히 지원 경계를 선언하지 않고 방어적 fail-closed(`InvalidOperationException`) 적용.
   - 오퍼레이터 부트스트랩을 위한 명시적 불변 정책 구성 seam(`ConfigureExpectedPackagePolicy`) 제공.
4. **Remove Default-Only supportedModBoundary Claim**:
   - 하드코딩된 거짓 선언(`"POC_DECLARED_PACKAGES_ONLY"`)을 제거하고, 기본값을 `"UNCONFIGURED"`로 설정하며 실제 정책 검증 시 검증된 정책 식별자(`$"CHECKED_POLICY:{policyId}:{revision}"`) 및 `PackagePolicyDispositionRecord`로 바인딩.
5. **Preserve R9 Results & Robust Regression**:
   - R9의 `modVersion = null` 보존 및 양방향 상호 유추 제거, 자식 fail-closed 분류, 어셈블리 복합 키 유일성 100% 보존.
   - 신규 러너 `scratch\EngineGate05R10PackagePolicy\Harness\`를 통해 긍정적 정상 통제 검증.
