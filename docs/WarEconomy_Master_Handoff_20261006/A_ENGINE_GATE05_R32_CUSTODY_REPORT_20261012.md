# Gate05-R32 관리된 소유권 및 소유 자원 실패 처리 기술 보고서

**작업 패키지**: `WP_ENGINE_GATE05_R32_CUSTODY` (Envelope 35)  
**발행 ID**: `WE-A-ENGINE-GATE05-R32-CUSTODY-20261012-DIRECT-64ad38e2`  
**수행자**: Antigravity A  
**작성일시**: 2026-10-12T23:31:00+09:00  
**E1 판정**: `BUILT_SOURCE_CORRECTION_RUNTIME_NOT_EXECUTED`

---

## 1. 개요 및 결함 수선 내용

R31 독립 정적 검토 및 Master 지침에 따라 `scratch/WorkerBridgeMod/Source/WorkerBridge.cs`의 인가된 **지정 4개 구간**에서 관리된 소유권 및 소유 자원 실패 처리 수선을 완료했습니다:

1. **관리된 ReferenceEquals 및 이전 중단 시 페이로드 전송 차단 (`PRIVATE_DURABLE_MODE_OWNER_CONSUMED_STATE`, 27259..33326)**:
   - 유니티 오버로딩 `==` 연산자 대신 순수 관리 참조 비교 `object.ReferenceEquals`를 전면 적용하여 파괴된 네이티브 피어를 가진 GameObject 래퍼가 소유권 정리를 우회하지 못하도록 수정.
   - `TryAcquirePendingStartupHandoff` 진입 시 `_staticStartupAborted` 상태를 락 하에서 사전 검사하여, 이전 중단 발생 시 등록된 소유자와 일치하는 페이로드만 안전하게 비우고 `false` 반환.
2. **getter 이전 모드 설정 및 자원 설정 전 중단 가드 (`AWAKE_REQUIRED_MODE_ENTRY`, 38131..39339)**:
   - `this.gameObject` 속성 읽기 전에 `lock (_startupHandoffLock)` 하에서 정적 마커 `_staticPairModeRequired`를 기반으로 인스턴스 `_isPairRequiredMode = true`를 선제 확립.
   - `this.gameObject` 읽기를 try/catch로 보호하여 `_retainedOwner` 안전 보관.
   - 자원 생성(로그 콜백, 정책, TCP 리스너, 스레드) 이전에 이전 중단(`_staticStartupAborted`) 여부를 확인하여 중단 시 즉시 `_startupInitializationComplete = false`, `isRunning = false` 설정 후 fail-closed 종료.
   - 페어 모드 필수 상태에서 프로필 미획득 시 즉시 `isRunning = false`, `_staticStartupAborted = true` 설정 후 fail-closed 조기 종료.
3. **Awake catch 실패 시 isRunning=false 및 독립적 안전 정리 (`AWAKE_SUCCESS_AND_FAILURE_TAIL`, 41273..42068)**:
   - catch 진입 즉시 `_startupInitializationComplete = false`, `isRunning = false`, `_staticStartupAborted = true` 확립.
   - catch 내부 로그 출력을 try/catch로 보호하여 로거 예외가 자원 정리를 가로막지 않도록 보장.
   - 로그 핸들러 해제, TCP 리스너 중지, 스레드 중단, 소유자 한정 페이로드 정리를 각각 독립된 try/catch 블록으로 분리하여 상호 실패 전파 차단.
4. **OnDestroy finally 블록 기반 안전한 정리 보장 (`OWNER_SCOPED_DESTROY_WHOLE_METHOD`, 185129..185705)**:
   - 보관된 `_retainedOwner`를 사용하여 `CleanupOwnerPendingHandoff` 호출.
   - 예외 로깅을 안전하게 감싸고, `finally` 블록에서 `isRunning = false` 및 자체 자원 정리가 예외 발생 여부와 무관하게 무조건 실행되도록 보장.

---

## 2. 파일 보존 및 소스 충실도

- **소스 코드 보존**:
  - `WorkerBridge.cs`: 인가 4개 구간 외 5개 외부 세그먼트(총 263,961 바이트) **100% 비트 동일** 검증 완료.
  - `EngineHostCensus.cs` (170135 B), `WorkerBridge.csproj` (1774 B), `publish_operator_pair.py` (10442 B) 바이트 완전 불변 유지.
- **후보 DLL / PDB 신규 생성**:
  - Debug DLL: 325632 B, SHA256 `0B23C358E8C8FC16FCD02DDE654AD8AE763EA177460BB15F5F1E1B1F0CB67E26`, MVID `7d436c98-659a-4df1-a085-06fe9e55a0bc`, CV GUID `0155713e-2a25-4b6e-94e4-e0a9897f8d46`
  - Debug PDB: 79124 B, SHA256 `226DF5428AB94D48E0B08DC237AF3FC2E9F193315FE4D2F6EE2A8654B512E90D`
  - Release DLL: 308224 B, SHA256 `19F2CA8D466B10E99B86C8F5DD380102CCA14555B1FC7052AAB2B5DCFA98806F`, MVID `cee8068e-e814-4203-8135-8c0fd5107005`, CV GUID `feca9121-d053-4f9b-b835-591428998f7c`
  - Release PDB: 57712 B, SHA256 `A0F37D4437406AFF7FC329B8286B921ADE82F6C3F788D1C89FE4486D0C739347`
  - `1.6/Assemblies`: Debug DLL 및 PDB와 정확히 동기화.

---

## 3. 빌드 증거 및 실행 제약 준수

- **사전 빌드 입력 매니페스트**: `BUILD_INPUT_MANIFEST.json`에 실제 C# 소스, 생성된 속성 문서, 실제 Steam HintPath 참조, 닷넷 툴체인 바이너리 해시 사전 바인딩.
- **빌드 프로세스 텔레메트리**: Debug (PID 34256, 0 종료), Release (PID 12188, 0 종료) 프로세스의 원시 stdout/stderr 바이트 캡처 및 `BUILD_HOST_TOOL_TELEMETRY.json` 기록.
- **단위 러너 및 런타임 제약**: 본 작업(A)은 소스 수선 및 빌드 증거 제출로 한정되며, 단위 러너 실행 및 네이티브 엔진 실행은 0건입니다. 신규 후보에 대한 독립 실행 회귀 검증은 Sol이 별도 수행합니다.

---

## 4. 거버넌스 및 제약 사항

- Dedicated Server가 유일한 최종 도메인 권한(Domain Authority)입니다.
- Carrier(High 2), Publisher(High 3), E1 lineage(High 4) 및 네이티브 런타임 실행은 계속 보류(WITHHELD)됩니다.
- Foundation은 HOLD 상태를 유지합니다.
