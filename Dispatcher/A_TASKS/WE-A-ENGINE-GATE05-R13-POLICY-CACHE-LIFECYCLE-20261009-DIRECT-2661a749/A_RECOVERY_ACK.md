# Developer A Recovery & Task Acknowledgement — Envelope 16

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749`
- **Work Package**: `WP_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE`
- **Revision**: `GATE05-R13-POLICY-CACHE-LIFECYCLE` (Envelope 16)
- **Agent**: Antigravity A (Developer)
- **Time**: 2026-10-09T17:04:30+09:00

---

## 1. 지시문 및 통제 문서 접수 확인
- 마스터 작업 지시문 `INSTRUCTIONS.md` 접수 확인.
- 통제 문서 `WP_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE.md` (SHA `33CD55F21DF0BA7C6DDB53A9B9B968BDFB76F64EBE0DDF0B0E0D30D0D1C82282`) 및 `RELEASE_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_20261009.md` (SHA `4ED0382D9BDFAE27574342D87E162500413F156359AB522019CA78654BD86E8B`) 확인 완료.
- `MASTER_R13_SCOPE_BASELINE.json` (SHA `9A722883495F57C08D64601A9BF255953F9762FF93FBE802C4378A652EE56F05`) 및 이전 후보/QA/아카이브 보존 정책 확인 완료.
- Sol R12 독립 QA(S1) 265 PASS 성과(정상 0-based 순서, 복사 뷰, 물리적 치환 불변성, 고유 실행 순서 분기, 신선 원본 직렬화 바인딩) 정상 크레딧 수용 확인.

---

## 2. R13 단일 한정 기술 목표: `POLICY_CACHE_LIFECYCLE`
1. **프로세스 로컬 정책 구성 세대(generation) 및 일관된 캐시 엔트리 바인딩**:
   - `ConfigureExpectedPackagePolicy` (선언/레코드), `ClearConfiguredExpectedPackagePolicy`, 명시적 `InvalidateCache` 호출 시 원자적으로 오래된 핑거프린트/정규 JSON/매니페스트/오류를 무효화.
   - 오래된 매니페스트와 새 JSON, 또는 새 정책 간 혼합이 관측되지 않도록 보장.
   - 호출자의 입력 정책 객체/리스트 및 반환된 정책 스냅샷의 변경이 구성된 상태를 오염시키지 않도록 방어적 복사/불변성 확립.
2. **동기화 및 상태 해석 단일화**:
   - 구성, 캐시 조회, 캐시 발행 간 단일 동기화 규약 확립.
   - 네이티브 실제 연산은 캡처된 불변 스냅샷을 기반으로 락 외부에서 수행될 수 있으나, 발행 시점에는 현재 구성 세대와 일치하는지 검증.
   - 캐시 히트는 오직 현재 구성 세대/다이제스트/컨텍스트와 일치하는 엔트리만 반환하며, Clear 후 이전 핑거프린트가 접근되는 현상을 완전 차단.
3. **독립 순수 인스턴스 캐시 코어 분리**:
   - 동일한 캐시 상태 로직을 순수 인스턴스 소유 데이터 코어로 격리하여, 네이티브 수집 없이도 엔트리 수명주기를 정상 단위 검증할 수 있도록 분리.
   - 전역 프로바이더에는 어떠한 공개 정적 시드, 오버라이드, 리플렉션 변조, 테스트용 우회 경로도 추가하지 않음.
   - 전역 엔트리는 내부 실제 연산 및 일치 정책 스냅샷을 통해서만 발행됨.
4. **일관된 엔트리 소유권 및 스냅샷 무결성**:
   - 입력/출력 매니페스트/정책의 사후 변조가 캐시된 핑거프린트/정규 JSON을 변경하지 못하도록 보장.
5. **R13 신규 허용 실행 범위 준수**:
   - 오직 유효한 현재-v1 `ConfigureExpectedPackagePolicy`, `Configured`/`HasConfigured` 스냅샷, `ClearConfiguredExpectedPackagePolicy`, `InvalidateCache`, 순수 빈 캐시 진단, 그리고 격리된 순수 인스턴스 코어 단위 검증만 실행.
   - `GetActualContentProfileFingerprint`, `ComputeActual*`, 게임/네이티브/오퍼레이터 실행, 음성/거부/유해 테스트는 일체 금지.
6. **패키징 개선 및 프로세스별 완전 증거 보존**:
   - 프로세스별 독립 불변 디렉토리 및 완전한 출력 인벤토리 유지.
   - 사전 실행 핀, 유효 JSON 릴리즈 매니페스트, 일관된 `run_id` 결속.

---

## 3. 작업 착수 확약
- 소스 변경: `scratch\WorkerBridgeMod\Source\EngineHostCensus.cs` 내 `ContentProfileProvider` 이후 접미부만 한정 수정.
- 접두부 72,547 바이트 및 `WorkerBridge.cs`, `WorkerBridge.csproj` 절대 불변 보존.
- Dedicated Server가 최종 런타임 도메인 권위이며, 마스터가 릴리스 거버넌스를 수행하며, 자체 결함 종결을 선언하지 않음.
