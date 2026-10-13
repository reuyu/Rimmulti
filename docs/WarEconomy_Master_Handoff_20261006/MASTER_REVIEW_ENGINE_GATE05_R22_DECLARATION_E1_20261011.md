# R22 명시적 기동 선언 E1 — Master 검토

검토 시각: 2026-10-11T16:26:55.493001+09:00. 결과 WE-A-ENGINE-GATE05-R22-DECLARATION-RESULT-01, envelope25. 판정: **EXPLICIT_REQUIRED_SEVEN_FIELDS_AND_PRIVATE_CAPTURE_CREDITED_M01_REVISION_REQUIRED_SCOPED_FRESH_QA_ADMITTED_NATIVE_UNTESTED**.

A의 완료 원문과 28개 산출물 SHA/크기, 이전 동결 R21 기준 BEFORE9/현재 AFTER9, 4개 허용 변경 구간 사이 고정 바이트 5개를 직접 대조했다. EngineHostCensus.cs와 csproj도 동일하다. WorkerBridge.cs SHA6AA281259A5760BFFFA432E392AC4480807E16C044EE599A7D31AD4BF6C10F1E/226714 bytes. R21 receipt UTC 메서드·11개 public 속성/schema·ParseStrict·Snapshot·기존 데이터 전용 AdmitBytes/File·global install/Awake/readiness는 변경되지 않았다.

새 Debug SHA278DA55F46B3646F981E79EF83D764F19959B6FEFAD6EEC83AFD4DAB0020864D/303104 bytes, MVID3d7d7cf7-541a-42ec-a642-b31539cc3f3f, PDB75C81993FEB72294789BB69E611FD3AFE7647D733568D405F1A672CF1DA74D84/72608 bytes, CodeView GUID35fc949d-90a4-415c-a8bc-fd377c16b02e. Release SHA BF170758FE5998919A860A17A33F04A36780D5419D735D95D8518DF631783955/286720 bytes, MVID0ad5d962-8354-4049-9f25-6851185a3b8c, PDB A4C0947FDD7CC7901C20951F11DF82B38FE6DF6CF73E48CB0ABD22C6E54BDEC1/53076 bytes, CodeView GUID5bf238db-f840-4428-837e-56d866a4a6c5. 두 모드 source4/4·CodeView 결속을 metadata 도구로 직접 확인했다. 프로젝트 1.6 배포본은 Debug와 같다. Master candidate 실행/빌드0.

새 후보 114개를 C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R22-9be1579a에 동결했다. Manifest C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R22-DECLARATION-20261011-DIRECT-9be1579a\MASTER_GATE05_R22_DECLARATION_REVIEW_FREEZE_MANIFEST.json, SHA8BD9FD9363549891703A3E5696FB44E4B2D806547E3B51CC87EC7142C7756BB5. 사후 보존 사본이며 사전 실행 결속을 대신하지 않는다. Archive19/이전 candidate2074/Pipeline206/보호 QA/managed4/runtime7은 실제 보존 검사와 대조했다. 기존 Steam DLL의 BB3B... 대 2D64... 불일치만 남아 있으며 actor/cause UNKNOWN, OPEN 유지. 외부 설치나 과거 manifest를 수정·정상화하지 않았다.

## 구현에서 인정하는 범위와 남은 M01

- 의미 있는 OperatorLaunchDescriptor 기본값을 빈 값으로 바꾸고 모든 7개 CLI 필드를 attachment 전에 요구했다. Factory entry에서 caller를 복사하고 7필드 완전성·path/SHA·raw bytes SHA를 승인 전에 확인한다. 파일 경로는 검증된 복사본을 bytes factory로 전달하면서 추가 복사한다. 원 caller는 다시 읽지 않으므로 caller 복사 경계 자체의 실패로 단정하지 않는다.
- Receipt는 7개 readonly string을 내부에 보관하고 validation이 이 선언과 bound origin/plan/configId/role/capability/path/SHA 및 snapshot을 비교한다. Scalar internal getters는 public schema나 mutable DTO export가 아니다. 기존 11public/redacted schema 유지. 내부 constructor/local IsTrusted는 hostile same-process 인증이나 실제 operator ownership 증거가 아니다.
- **기동 경로 WorkerBridge.cs:101~103의 origin.Trim()/plan.Trim()/cfgId.Trim()은 원문 codepoint/ordinal 보존 요구에 위배된다.** 동일 원문 지시를 약화하지 않으며 M01은 REVISION_REQUIRED다. Factory 직접 입력의 origin/plan 보존과 native CLI의 원문 보존은 별개다. Source-only 확인이며 bootstrap 실행0.
- Factory에서 expectedRole/capability를 Trim해 비교하지만 readonly 승인 capture는 원 문자열을 유지하고 validation은 Trim 없이 비교한다. 정규 role/capability 입력은 QA로 확인하고, whitespace/case 정규화의 일관성은 source-only 후속 우선순위로 검토한다. 불일치 입력/거절 경로를 실행해 PASS로 만들지 않는다.
- Snapshot.ConfigId의 기존 Trim은 고정 구간이다. R22에서 이를 바꾸라는 새 허가는 없으며 configId의 기존 canonical 계약과 ordinal 선언 비교를 구분한다. 원문 origin/plan를 configId의 기존 정규화에 편승하여 잘라서는 안 된다.

## E1가 실제로 보여주는 것

Host en-US PID25356/de-DE PID29248, 기록된 OS exit0/0, 두 결과 모두7 label PASS. 각 OUTPUT_INVENTORY는 self 제외18개의 실제 nonself 파일과 정확히 일치하며 모든 SHA/크기 확인, stdout1348 bytes/stderr0. Source host는 첫 inventory를 두 번째 전에 쓰고 이후 첫 산출물 hash를 다시 확인한다. 모든 둘째 output/loaded refs/전체 candidate-source-PDB-input-oracle-toolchain pre/post 결속은 없다. Runner 사전 SHA 하나와 ephemeral map만으로 전체 prospective proof가 되지 않는다. 전체 compiler raw/pin도 별도 산출물이 없다.

Main receipt8은 11getter의 snapshot nonnull과 selected redacted 필드·nested issuedAt literal만 비교한다. Caller7fields 수정 후8개 receipt valid/selected public fields 확인은 인정하지만 전체 graph·typed order·whole UTF8 bytes oracle는 없다. UTC6은 양 역할의 세 형식 file route selected issuedAt leaf/tokenString이며 요구된16 receipt fullgraph 회귀를 채우지 않는다. ToSnapshot/AdmitBytesFile 직접 계수0, normal16 snapshot regression 미실행; report의16/16 regression 언급은 실제 결과와 다르다. TEST07 digest32CBD507...은 별도 plain policy sample이고 opaque8A9C... 전체 검증이 아니다.

Default DTO를 생성해 빈 필드를 읽는 TEST01은 metadata/default inspection이며 trusted admission 거절 실행은 없다. WP의 default-descriptor probe0 경계와의 차이를 기록한다. Sol에서는 빈/default/null DTO 생성/검증도 SOURCEONLY로 제한한다. Manual direct call ledger54(10+4+16+5+14+1+1+1+2)는 IsValid/Clone/constructor 등 미계수 direct calls를 제외하며 내부 nested total/권한 proof가 아니다. Negative/global/C#Process/native0에 대한 새 실행 증명은 없으며 reviewed runner 범위의 source와 producer 제한을 구분한다. 모든 테스트는 synthetic profile/PID/exe fixture/정상 managed data 범위다.

Standard checker EVIDENCE_INCOMPLETE의7 missing role는 원 producer의 candidate_dll_debug/pdb_debug/source_worker_bridge/results_en_us/동일 freeze aliases 등이다. Master가 원문을 바꾸지 않고 실제 28개 경로와 identity로 대조했다. Semantic/prospective coverage gaps는 alias 대조로 해결되지 않는다. Collector 첫 시도는 ENGINE_FREEZE가 object가 아닌 list인 것을 읽다 중단했다. Artifact/preservation/diff만 기록되고 candidate 실행·freeze·governance mutation0. List 형태를 지원한 metadata-only 두 번째 시도로 성공; 원문 JSON은 수정하지 않았다.

## 다음 독립 QA 승인

Original Sol에 새 exact Debug만 defensive STATIC + 새 정상 positive PURE receipt/declaration fullgraph와 R21 UTC/opaque regression을 승인한다. 새 candidate PASS는 R21 PASS를 승계하지 않는다. Normal fully specified seven-field caller/used Clone의 승인 후 수정과 detached policy copy 경계 검증; origin/plan의 정상 Unicode·앞뒤 공백 원문은 factory data 경로에서만 확인하고 CLI는 SOURCEONLY. 기존 canonical configId와 uppercase valid role/boundary를 사용한다. 내부 receipt constructor·private capture mutation·빈/invalid/default 선언·rejection·global startup·Process/native/operator/provider/cache execution은0. 독립 oracle/compile/ref/loaded SHA-MVID/pre-post/full streams/seals을 QA가 새로 작성한다.

M01/기동 원문 trim OPEN, M04..07/실제 native·operator proof OPEN. Engine002006/Pipeline007/current schema/G-Q1 OPEN, Foundation HOLD. 역사 R19opaque/R21UTC 좁은 CLOSED만 유지하며 R22의 fresh regression은 아직 PENDING. Full Gate E2 NOT_RELEASED, closure 변화0. 다음 A corrective WP는 독립 QA findings 후 bounded scope로 준비·전달한다.

예약 실제 config는 현재 PAUSED/hourly60min/173char/동일 Master다. Local ACTIVE는 R22 전달 당시의 과거 기록이며 이번에 실제 PAUSED로 대조한다. 누가 기존 pause를 수행했는지는 UNKNOWN; Master가 이전에 pause했다고 소급 주장하지 않는다. 수신된 R22 heartbeat23:30:03.796Z는 실제 trigger 관측이며 그 handler 완료는 UNVERIFIED. QA direct 완료 보고와 승인된 기술 후속은 계속한다.
