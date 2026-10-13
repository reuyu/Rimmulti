# A Recovery ACK — WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY / GATE05-R15-PUBLIC-MANIFEST-BOUNDARY

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052`
- **Work Package**: `WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY`
- **Revision**: `GATE05-R15-PUBLIC-MANIFEST-BOUNDARY` (Envelope 18)
- **Agent**: Antigravity Development Agent A
- **Timestamp**: 2026-10-09T22:54:20+09:00

---

## 1. 지시문 및 제어 문서 수신 확인

- [INSTRUCTIONS.md](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052/INSTRUCTIONS.md) (Envelope 18, Master 승인 확인)
- [WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.md) (SHA `58C3BCB8423D6F6345FC3F89110B79351E4BADCAFD988502FF4A4FD1DA7DC01D`)
- [RELEASE_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_20261009.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/RELEASE_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_20261009.md) (SHA `6BCFA9F804E8CF1D655019FFCDB0CCC971D4C4D5756C09D06EE15CB8D92E6CAF`)
- [MASTER_R15_SCOPE_BASELINE.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052/MASTER_R15_SCOPE_BASELINE.json)
- 독립 Sol R14 QA(S1) 339 PASS 성과(정책 캡처, 캐시 발행 예외 처리, Invalidate +1) 크레딧 수용 및 보존 확인. 신규 후보는 이전 PASS를 상속하지 않음.

---

## 2. 단일 기술 목표: `PUBLIC_MANIFEST_BOUNDARY`

1. **외부 호출자 정책 수집기 차단 및 내부 헬퍼 봉인**:
   - R14에서 노출되었던 `ComputeActualContentProfileManifest(ExpectedPackagePolicyRecord)` 공개 오버로드를 완전히 제거.
   - 캡처된 정책을 기반으로 실제 매니페스트를 수집하는 로직은 내부 전용 `private static ContentProfileManifest CollectActualContentProfileManifestInternal(ExpectedPackagePolicyRecord capturedPolicy)`로 봉인.
2. **단일 신뢰 프로바이더 계산 및 성공 선형화 경계**:
   - 매개변수 없는 공개 엔트리 포인트(`ComputeActualContentProfileManifest()`, `ComputeActualContentProfileFingerprint()`)는 동일한 내부 실행 메서드(`ComputeAndPublishActualContentProfile()`)를 공유.
   - 단일 코어 동기화 락 하에서 현재 프로바이더 상태(세대 및 구성 정책)와 캡처된 스탬프의 동일성을 검증하고, 발행 실패 시 명시적 `InvalidOperationException`을 던짐 (경고 후 성공 반환/폴백/재조회 금지).
3. **불변 상태 및 세대 규약 유지**:
   - R14의 `InvalidateCache()` 시 세대 전진(`_generation++`), 순수 코어 소유권, 방어적 복사, 순수 코덱 로직을 온전히 유지.
4. **버전 및 기능 식별자 갱신**:
   - `CONTENT_CONTRACT_VERSION` = `"ADR-006B-v5-R15"`
   - `CONTENT_CAPABILITY_FLAGS` = `"GATE05_R15_PUBLIC_MANIFEST_BOUNDARY"`

---

## 3. 엄격한 실행 통제 및 금지 사항 준수

- **실행 허용 범위**:
  - 독립 순수 인스턴스 `ContentProfileCacheCore`의 정상 일치 엔트리 발행, 세대 스냅샷, 복사 쿼리 단위 검증.
  - 글로벌 프로바이더 `ContentProfileProvider`의 정상 설정(`Configure`), 초기화(`Clear`), 명시적 무효화(`InvalidateCache`), 빈 상태 진단 호출.
  - 공개 인터페이스 리플렉션 검사 (공개 호출자 정책 수집 메서드 부재 입증).
  - 기존 정상 회귀 검증 (R12 패키지 순서, R11 인코딩, R9 버전 시맨틱스 등).
- **엄격 금지 사항**:
  - `GetActualContentProfileFingerprint`, `ComputeActualContentProfileFingerprint`, `ComputeActualContentProfileManifest`의 하네스 직접 실행 금지.
  - 게임 런타임, 네이티브 실행, 오퍼레이터 프로모션 금지.
  - 글로벌 캐시 시딩/재정의/리플렉션 임의 조작 금지.
  - 부정/거부/지연/경합/불일치 테스트 금지.
  - 자체 릴리스 선언 또는 게이트 종결(Closure) 선언 금지 (Dedicated Server 최종 권위, Master 관할).
- **보고 무결성**:
  - 프로세스별 독립 디렉터리, 실제 수치형 종료 코드(0), 완전한 입력-기대치 오라클, 명시적 API 원장 기록.

---

## 4. 소스 및 불변 기준선 보존 서약

- [EngineHostCensus.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs) 접두부 72,547 바이트 (SHA `F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887`) 불변 보존.
- [WorkerBridge.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs) 및 [WorkerBridge.csproj](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.csproj) 완전 보존.
- 기존 모든 후보 아카이브(Archive 19, R1~R14) 및 Steam 설치 DLL(`BB3B52...`) 상태 보존.
