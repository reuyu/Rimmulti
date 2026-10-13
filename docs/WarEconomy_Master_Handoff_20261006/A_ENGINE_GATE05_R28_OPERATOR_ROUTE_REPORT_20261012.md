# A_ENGINE_GATE05_R28_OPERATOR_ROUTE_REPORT_20261012.md
**과업 패키지**: `WP_ENGINE_GATE05_R28_OPERATOR_ROUTE`  
**개정/엔벨로프**: `GATE05-R28-OPERATOR-ROUTE` / `envelope31`  
**디스패치 ID**: `WE-A-ENGINE-GATE05-R28-OPERATOR-ROUTE-20261012-DIRECT-7c324c51`  
**수행 에이전트**: Antigravity Development Agent A  
**판정**: `READ_ONLY_CONNECTED_ROUTE_PROPOSAL_NOT_IMPLEMENTED`  
**실행 및 빌드 통계**: Production Code Mutations = 0, Compiler Builds = 0, Candidate/Native Executions = 0  
**작성 일시**: 2026-10-12 04:58:00 UTC+9  

---

## 1. 개요 및 Master 정정·지침 수용

Master의 controlling instructions ([INSTRUCTIONS.md](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R28-OPERATOR-ROUTE-20261012-DIRECT-7c324c51/INSTRUCTIONS.md), [WP_ENGINE_GATE05_R28_OPERATOR_ROUTE.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/WP_ENGINE_GATE05_R28_OPERATOR_ROUTE.md), [RELEASE_ENGINE_GATE05_R28_OPERATOR_ROUTE_20261012.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/RELEASE_ENGINE_GATE05_R28_OPERATOR_ROUTE_20261012.md), [MASTER_REVIEW_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2_20261012.md](file:///c:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/MASTER_REVIEW_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2_20261012.md))에 따라 수행된 **R28 읽기 전용 설계 및 첫 패치 제안 보고서**입니다.

### 1.1 Master R27 독립 QA 수용 사실
Master review에 의해 Sol QA의 R27 독립 S2 정상 168개 단위 검증이 공식 채택(`ACCEPTED_SCOPED_R27_NORMAL_CAPTURE15_TYPED_RAW_COPY_PASS_OPERATOR_REGISTRATION_AND_NATIVE_UNTESTED`)되었습니다. 본 R28 과업은 추가적인 제네릭 PURE API나 단순 준비 문서를 재작성하지 않고, **실제 오퍼레이터 프로듀서 → 부트스트랩/비공개 슬롯 → R27 Capture 소비 → 자식 프로세스 프론트엔드 인자 연결**의 구체적 첫 통합 경로를 확정하기 위해 배정되었습니다.

### 1.2 작업 범위 및 엄격한 읽기 전용 제약
- **생산 코드 수정 제로 (0)**: `WorkerBridge.cs`, `EngineHostCensus.cs`, `WorkerBridge.csproj` 등 모든 소스 파일 100% 불변 보존.
- **컴파일러 빌드 제로 (0)**: 후보 DLL/PDB 및 동반 산출물 재빌드 없음 (기존 R27 산출물 SHA-256 100% 일치 확인).
- **게임 및 네이티브 실행 제로 (0)**: Unity 라이프사이클, RimWorld 게임 엔진, OS 프로세스 실행 일체 없음.
- **기록 전용 경로**: Task 디렉터리 및 본 보고서 파일에만 텍스트 산출물 작성.

---

## 2. 핵심 질문: 실제 오퍼레이터 프로듀서 추적 결과

### 질문:
> "어떤 실제 오퍼레이터 소유 프로듀서가 `READ_ONLY` 자식 config14 + 원본 declaration7을 독립 공급하고, 비공개 소유자가 R27 Capture를 소비하기 전에 라이브 `SIMULATION` 시동과 이들의 페어링을 승인할 수 있는가?"

### 실체 소스 추적 및 실사 결과 (Observed vs Missing):
1. **전용 서버 소스 루트 ([WarEconomyMod\Source\Server\Program.cs](file:///c:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs))**:
   - `Program.cs` (114행, SHA `186F6929...`) 실사 결과: 월드 틱 관리자(`WorldTickManager`), 외교, 시장, 봉건 관리자 및 포트 7777 TCP 네트워크 서버만을 구동합니다.
   - 오퍼레이터 설정 생성, 워커 프로세스 실행, 자식 프로세스 오케스트레이션 코드는 **전혀 존재하지 않습니다 (MISSING)**.
2. **워커 브리지 소스 루트 ([scratch\WorkerBridgeMod\Source\WorkerBridge.cs](file:///c:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs))**:
   - `WorkerBridgeBootstrapper` (43~137행): 오직 현재 프로세스 자신을 위한 7개 CLI 플래그(`self7`)만을 파싱하여 자신의 영수증(역할 `SIMULATION`)만을 발급 및 설치합니다.
   - `WorkerBridgeComponent` (413~436행): `_activeAdmissionReceipt` 및 `_activeStartupConfig`라는 단일 슬롯만을 보유하며, 별도의 자식 영수증을 보관할 필드가 없습니다.
   - `HandleLaunchOperatorValidator` (2190~2345행): 부모의 `_activeStartupConfig`로부터 실행 파일 경로와 작업 디렉터리를 읽어 `--task-file ... --nonce ...`만을 인자로 넘겨 `Process.Start`를 호출합니다. 자식 영수증을 파생하거나 R27 `Capture`를 호출하지 않으며, 자식 프로세스에 필수적인 7개 오퍼레이터 CLI 플래그를 넘겨주지 않습니다.
   - **결과**: 만약 현재 상태에서 자식 RimWorld 프로세스가 실행된다면, 자식의 `WorkerBridgeBootstrapper`는 `-operatorconfig` 누락으로 인해 `Fail-Closed` 경고를 출력하고 컴포넌트를 부착하지 않게 됩니다.
3. **드라이버 스크립트 루트 ([scratch\run_semantic_authority_gate_05.py](file:///c:/Users/user/Desktop/RimMulti/scratch/run_semantic_authority_gate_05.py))**:
   - `launch_worker` (138~151행): RimWorld 실행 시 `[-batchmode, -savedatafolder=..., -logFile=..., -bridgeport=...]`만을 전달하며, Gate05-R18/R22에서 도입된 7개 오퍼레이터 플래그를 공급하지 않습니다.
4. **결론**:
   - 라이브 런타임 환경에서 자식 영수증을 별도 공급하고 부모와 페어링을 승인하는 실제 오퍼레이터 프로듀서는 **현재 코드베이스에 부재(MISSING)**합니다.

---

## 3. 동결 프론트엔드 IL 역어셈블리 분석 결과

`MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json`에 정의된 동결 라이브러리(`Assembly-CSharp.dll`, SHA `5CF1B5BE...`)를 `ildasm.exe` 메타데이터 도구를 사용하여 순수 정적 역어셈블리 분석했습니다:

### 3.1 `Verse.GenCommandLine.TryGetCommandLineArg` IL 검증
- **메서드 크기**: 96 바이트 (0x60).
- **핵심 IL 시퀀스**:
  - `IL_0000: call Environment.GetCommandLineArgs()`
  - `IL_000d: ldc.i4.s 61` (문자 `'='`)
  - `IL_000f: callvirt String.Contains(char)` → **`'='` 문자가 없으면 즉시 건너뜀 (`brfalse.s IL_0051`)!**
  - `IL_0019: ldc.i4.s 61; ldc.i4.0; callvirt String.Split(char, StringSplitOptions)`
  - `IL_0025: ldc.i4.2; bne.un.s IL_0051` → **분할된 토큰 배열의 길이가 정확히 2가 아니면 즉시 건너뜀!**
  - `IL_002d: call String.Compare(...)` → `key` 또는 `"-" + key`와 대소문자 무시 비교.
- **기술적 발견**:
  - RimWorld의 CLI 인자 파서는 **공백 구분 인자(`-key value`)를 완전히 무시**합니다.
  - 모든 인자는 반드시 **`-key=value`** 형식이어야 합니다.
  - 또한 값 내부에 이스케이프되지 않은 `'='`가 포함되면 `split.Length == 2` 검사에 실패하여 인식이 거부됩니다.

### 3.2 `Verse.GenFilePaths.get_SaveDataFolderPath` IL 검증
- **메서드 크기**: 266 바이트 (0x10a).
- **핵심 IL 시퀀스**:
  - `IL_0000: ldsfld saveDataPath; brtrue IL_0104` (이미 설정되어 있으면 즉시 반환)
  - `IL_000a: ldstr "savedatafolder"; call GenCommandLine.TryGetCommandLineArg(...)`
  - `IL_0054: stsfld saveDataPath; ldstr "Save data folder overridden to "; call Log.Message`
- **기술적 발견**:
  - 바닐라 RimWorld는 시동 극초기에 `-savedatafolder=<경로>` 인자를 스스로 확인하고, 저장 데이터 루트를 해당 경로로 덮어쓰며 디렉터리를 자동 생성합니다.
  - 따라서 자식 프로세스 실행 시 `-savedatafolder="{SelectedUserDataDirectory}"`를 넘겨주면, 바이트코드 패치 없이도 바닐라 프론트엔드가 자식 전용 UserData 격리 디렉터리를 네이티브하게 사용합니다.

### 3.3 `StaticConstructorOnStartup` 및 Unity `AddComponent`/`Awake` 순서
- `Verse.PlayDataLoader.DoPlayLoad` → `StaticConstructorOnStartupUtility.CallAll()` → `RuntimeHelpers.RunClassConstructor(type.TypeHandle)`.
- `WorkerBridgeBootstrapper.cctor()`가 실행되어 영수증을 설치한 후 `go.AddComponent<WorkerBridgeComponent>()`를 호출.
- Unity 엔진 내부 의미론상 `AddComponent` 호출 반환 이전에 동일 스레드에서 `MonoBehaviour.Awake()`가 동기적으로 즉시 실행됨.
- 따라서 Awake 이전에 부트스트랩 단계에서 부모와 자식 영수증이 완벽히 설치되어 있어야 함이 증명되었습니다.

---

## 4. 추천 연결 경로: 오퍼레이터 부트스트랩 페어 캐리어 경로

Master 지침에 따라 동적 TCP 등록 명령(공개 세터/글로벌 레지스트리)을 일체 배제하고, 시동 시점부터 불변 보관이 가능한 **부트스트랩 페어 캐리어 경로(OPERATOR_PAIRED_BOOTSTRAP_CLI_AND_CAPTURE_ROUTE)**를 단일 권장 경로로 제안합니다.

### 4.1 연결 라이프사이클 흐름
```
[1. 오퍼레이터 호스트] ──(시동 CLI: parent7 + child7)──> [2. WorkerBridgeBootstrapper]
                                                                │
                                         ┌──────────────────────┴──────────────────────┐
                                         ▼                                             ▼
                             부모 영수증 발급 (SIMULATION)                  자식 영수증 발급 (READ_ONLY)
                                         │                                             │
                                         └──────────────────────┬──────────────────────┘
                                                                ▼
                                      [3. WorkerBridgeComponent._configLock 비공개 설치]
                                          - _activeAdmissionReceipt (Parent)
                                          - _pairedChildAdmissionReceipt (Child)
                                                                │
[4. 제어 평면] ──(작업 발행/논스 생성)──> [5. currentValidatorTask 수립]
                                                                │
[6. LAUNCH_OPERATOR_VALIDATOR] ──(논스 검증)───────────────────┘
                                 │
                                 ▼
                     [7. OperatorChildLaunchInputs.Capture 호출]
                         (15개 getter로부터 불변 프로세스 파라미터 도출)
                                 │
                                 ▼
                     [8. 자식 ProcessStartInfo 구성 및 실행]
                         - FileName: inputs.ExecutablePath
                         - WorkingDir: inputs.WorkingDirectory
                         - CLI 인자:
                             -batchmode
                             -operatorconfig="{optVals[0]}"
                             -operatorconfigsha="{optVals[1]}"
                             -operatororigin="{optVals[2]}"
                             -operatorlaunchplan="{optVals[3]}"
                             -operatorconfigid="{optVals[4]}"
                             -operatorrole="{optVals[5]}"
                             -operatorcapability="{optVals[6]}"
                             -savedatafolder="{inputs.SelectedUserDataDirectory}"
                             --task-file="{inputs.TaskFilePath}"
                             --nonce="{capabilityNonce}"
                                 │
                                 ▼
                     [9. 자식 RimWorld 프로세스 정상 기동]
                         - GenFilePaths가 -savedatafolder를 인식하여 UserData 격리
                         - WorkerBridgeBootstrapper가 child7을 인식하여 READ_ONLY 컴포넌트 부착
```

### 4.2 본 경로의 설계적 장점
1. **SRS 및 ADR-006B / MD126 완벽 준수**: 새로운 와이어 스키마나 불필요한 공개키(PKI) 서명을 요구하지 않으며, 기존의 추측 불가능한 capabilityNonce 및 SHA-256 결속 모델을 유지합니다.
2. **공개 레지스트리 세터 배제**: TCP를 통한 임의의 자식 등록 명령을 차단하여 오퍼레이터 호스트만이 프로세스 기동 시점에 자식 페어를 확정하도록 강제합니다.
3. **R27 Capture의 완전한 소비**: R27에서 구현된 15개 getter와 방어적 복사본이 자식 프로세스 실행 인자 도출의 단일 원천으로 사용됩니다.

---

## 5. 변경 대상 소스 구간 및 패치 제안 요약

제안된 패치([IMPLEMENTATION_PATCH_PROPOSAL.diff](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R28-OPERATOR-ROUTE-20261012-DIRECT-7c324c51/IMPLEMENTATION_PATCH_PROPOSAL.diff))는 `WorkerBridge.cs`의 다음 3개 구간에 해당합니다:

1. **구간 1 (`WorkerBridgeBootstrapper`, 43~137행)**:
   - `-childoperatorconfig`, `-childoperatorconfigsha` 등 자식 7개 CLI 플래그 파싱 추가.
   - 자식 영수증을 발급하고 역할이 `"READ_ONLY"`인지 fail-closed 검증.
   - `WorkerBridgeComponent.TryInstallOperatorStartupConfig(admissionResult.receipt, childReceipt)` 호출.
2. **구간 2 (`WorkerBridgeComponent`, 413~436행)**:
   - 비공개 정적 필드 `private static OperatorStartupAdmissionReceipt? _pairedChildAdmissionReceipt = null;` 추가.
   - `TryInstallOperatorStartupConfig`에서 락 내 원자적 설치.
3. **구간 3 (`HandleLaunchOperatorValidator`, 2190~2345행)**:
   - `_pairedChildAdmissionReceipt`의 유효성 fail-closed 검증.
   - `OperatorChildLaunchInputs.Capture(_activeAdmissionReceipt, _pairedChildAdmissionReceipt, currentValidatorTask, currentValidatorTaskPath)` 호출.
   - `launchInputs`의 15개 getter를 사용하여 `-operator*`, `-savedatafolder`, `--task-file`, `--nonce` 인자 구성 및 프로세스 실행.

---

## 6. 구현 선행조건 및 거버넌스 안내

다음 구현 WP 착수 전에 필요한 선행조건([IMPLEMENTATION_PREREQUISITES.json](file:///c:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R28-OPERATOR-ROUTE-20261012-DIRECT-7c324c51/IMPLEMENTATION_PREREQUISITES.json))은 다음과 같습니다:
1. **Master의 자식 CLI 캐리어 스키마 승인**: `-childoperator*` 인자 형식 공식 채택.
2. **역할 페어링 불변성 정책 동결**: 부모는 반드시 `SIMULATION`, 자식은 반드시 `READ_ONLY`여야 하며 동일 역할 페어링 금지.
3. **인자 허용목록(Allowlist) 명시**: 임의 인자 주입을 방어하기 위한 바닐라 플래그 허용목록 확정.
4. **거버넌스 상태 유지**: Dedicated Server가 최종 도메인 권위(Final Domain Authority)를 유지하며, Foundation은 HOLD 상태입니다. 네이티브 런타임 실행은 NOT RELEASED 상태입니다.
