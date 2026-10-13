# A Recovery ACK — WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION / GATE05-R14-POLICY-CAPTURE-PUBLICATION

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b`
- **Work Package**: `WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION`
- **Revision**: `GATE05-R14-POLICY-CAPTURE-PUBLICATION` (Envelope 17)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-09T21:03:00+09:00

---

## 1. 지시문 및 제어 문서 수신 확인

- [INSTRUCTIONS.md](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b/INSTRUCTIONS.md) (Envelope 17, Master CU 승인 확인)
- [WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION.md) (SHA `3A1124519123452324B8621A20C1E199DCBED8C6CC11B30498A18D9521C97158`)
- [RELEASE_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION_20261009.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/RELEASE_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION_20261009.md) (SHA `4E142EF1BC71D5DB75B675F2217C56D6CEB129FBC08E6F4245F727699778BAA8`)
- [MASTER_R14_SCOPE_BASELINE.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b/MASTER_R14_SCOPE_BASELINE.json)
- 독립 Sol R13 QA(S1) 339 PASS 성과(정상 수명주기, 코어 소유권, 코덱) 수용 및 보존 확인.

---

## 2. 단일 기술 목표: `POLICY_CAPTURE_PUBLICATION`

1. **단일 캡처 정책 일관성 보장**:
   - 실제 수집 시작 전 프로세스 로컬 상태 스냅샷(`long generation`, `ExpectedPackagePolicyRecord policy`)을 1회 캡처.
   - 수집 및 패키지 정책 검사/정규화/JSON/지문 생성 전 과정에서 캡처된 동일한 정책 인스턴스를 사용하며, 중간에 글로벌 설정 정책을 재조회하지 않음.
2. **거부된 발행에 대한 성공 지문 반환 금지**:
   - 캐시 발행(`TryPublishComputedEntry`) 실패 시 단순 경고 로그 후 지문을 반환하던 결함을 제거.
   - 발행 거부 시 명시적 예외(`InvalidOperationException`)를 발생시키고 실패로 처리하여 비정상/무효화된 지문이 성공 결과로 누출되는 것을 원천 차단.
3. **명시적 무효화 시 세대 증가 (`InvalidateCache` generation + 1)**:
   - `InvalidateCache()` 호출 시에도 `_generation++`를 적용하여 이전 스냅샷의 지연 발행 시도를 무효화.
4. **버전 및 기능 식별자 갱신**:
   - `CONTENT_CONTRACT_VERSION` = `"ADR-006B-v5-R14"`
   - `CONTENT_CAPABILITY_FLAGS` = `"GATE05_R14_POLICY_CAPTURE_PUBLICATION"`

---

## 3. 엄격한 실행 통제 및 금지 사항 준수

- **실행 범위**:
  - 독립 순수 인스턴스 [ContentProfileCacheCore](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs)의 정상 일치 엔트리 발행, 세대 스냅샷, 복사 쿼리 단위 검증.
  - 글로벌 프로바이더 [ContentProfileProvider](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs)의 정상 설정(`Configure`), 초기화(`Clear`), 명시적 무효화(`InvalidateCache`), 빈 상태 진단 호출.
  - R12 패키지 순서, R11 인코딩, R9 버전 시맨틱스 등 기존 정상 회귀 검증.
- **엄격 금지 사항**:
  - `GetActualContentProfileFingerprint`, `ComputeActualContentProfileFingerprint`, `ComputeActualContentProfileManifest`의 관리되지 않는 하네스 직접 실행 금지.
  - 게임 런타임, 네이티브 실행, 오퍼레이터 프로모션 금지.
  - 글로벌 캐시 시딩/재정의/리플렉션 주입 금지.
  - **부정/거부/지연/경합 테스트 전면 금지**: 구 R13 TC13(지연 세대 거부) 및 TC19(부정적 패키지 순서 거부) 호출 제외.
  - 자체 릴리스 선언 또는 게이트 종결(Closure) 선언 금지 (Dedicated Server 최종 권위, Master 관할).
- **보고 무결성**:
  - 정상 캐시 호출이 발생하므로 푸터에 무차별적 "0 cache calls" 표기 금지 (정상 캐시 호출 수와 금지 경로 0회 명확 구분).

---

## 4. 소스 및 불변 기준선 보존 서약

- [EngineHostCensus.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs) 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`) 불변 보존.
- [WorkerBridge.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs) 및 [WorkerBridge.csproj](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.csproj) 완전 보존.
- 기존 모든 후보 아카이브(Archive 19, R1~R13) 및 Steam 설치 DLL(`BB3B52...`) 상태 보존.
