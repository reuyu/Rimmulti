# Gate05 R29 Startup Pair — 독립 QA S3

판정: `SCOPED_R29_POSITIVE_PURE_PAIR_AND_CAPTURE_DATA_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED`. 정상 PURE data 범위의 실제 두 실행과 후처리 비교는 PASS다. 연결 handoff, carrier, publisher의 High 3건은 OPEN이며 전체 Gate05/runtime E2, 실제 operator authority, native 동작은 승인·검증되지 않았다. Foundation HOLD, Engine/Pipeline/current schema/G-Q1 OPEN을 유지한다. 최종 타입 폭 witness는 Master 승인된 새 metadata-only continuation에서 실제 frozen Census class scope를 읽어 완결했다. 원래 실패 exit1과 성공 partial artifacts는 불변이다.

WP `WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT / S3`; delivery `SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012-01`; result `SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012-8d682aff4ebd4996a12529142c0d7431`. 후처리 resume `SOL-GATE05-R29-STARTUP_PAIR-S3-POSTANALYSIS-R1-20261012-01`. Original Sol endpoint에서 수행했다. 초기 ACK 및 이전 S1/S2 중단 증거는 불변이다. 운영 상태의 usage failure/후처리 재개를 candidate FAIL 또는 QA 완료로 승계하지 않는다.

## 실제 실행과 기대값

후보는 Master frozen132 manifest `006DE41FCB6EC9C9E183C877BD6E3D5C3FB48047454F4AF3902673C0B08D447E`의 Debug DLL `084C58CCD770AF90D2F2AE162FF5456C8CD2F0DB3167AE13394635BF8E567E7A`, MVID `5c410658-e435-4ae4-8aa3-d074fbcf4f5d`다. Matching PDB `7E76C8CEE38F98FB5B33639AAFB1AA9B4321D563DD483C35A1469A32229C1F3F`; Debug/Release 각각 CodeView/PDB/source4/4를 독립 메타데이터로 확인했다. Release는 별도 MVID이며 실행하지 않았다.

실행 전 봉인된 independent prep6 oracle `7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02`와 Capture4 oracle `5961CD18DA05B67F6DE40DA8A6EBB289D94ACF85054D57FB31FE4B8C5530C4C7`을 사용했다. 새 결합 oracle `89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D`, 새 Program `A57A6BB08DF8A6D07C0DBA6E276DF6C95A8B93A0CFD0CEA0998DB38CDA4DF940`와 컴파일 입력 253개를 BEFORE BUILD 고정했다. 후보 실행 결과로 기대값을 만들거나 바꾸지 않았다. 이전 QA 코드는 TEXT-only 패턴으로 사용했고 producer harness/publisher Python을 import하거나 실행하지 않았다.

QA-owned compiler 1회(exit0, nullable warnings/full stdout 보존), runner 2회만 실행했다. Runner SHA `10608E8E229F568085A5CF652C6ADA06E95F9FE376F4B05D43724EF25CDDAA1C`, MVID `4a281920-4376-419b-9f81-09f46cccb687`; portable PDB와 Program source 1doc 일치. Production candidate 수정·재빌드 0이다.

| 관측 | en-US | de-DE |
|---|---:|---:|
| 실제 owned runner PID | 21232 | 9224 |
| 실제 numeric exit | 0 | 0 |
| 정상 assertion PASS / FAIL | 438 / 0 | 438 / 0 |
| 타입·값·순서 hierarchical 비교 | 6,700 | 6,700 |
| independent expected raw UTF-8 비교 | 336 | 336 |
| 전체 graph/phase | 30 | 30 |
| 실행 전후 SHA/bytes identity pin | 264 | 264 |
| 실제 loaded managed path/SHA/MVID | 10 | 10 |
| recursive sealed outputs, inventory self 제외 | 402 | 402 |

두 프로세스/run ID는 서로 다르다. 실제 argv/cwd/culture/stdout/stderr, `Environment.Version=4.0.30319.42000`, corelib path/SHA/MVID를 기록했다. Loaded selected DLL, Newtonsoft 및 runtime libraries는 실행 전 pin과 독립 PE MVID 비교에 모두 일치했다. Native CLR modules는 관측하지 않았다. R5 frozen managed4는 admitted dependency metadata/load resolver 지원이며 실제 두 실행에서 로드되지 않은 파일을 로드됐다고 주장하지 않는다.

첫 실행 inventory를 두 번째 실행 전에 봉인·검증했고, 두 번째 실행 뒤 첫 봉인이 그대로임을 다시 확인했다. 두 실행의 실제 recursive path sets와 SHA/bytes는 후처리 및 최종 보존 검사에서도 일치했다. Raw 672개를 pre-run oracle와 비교했고, culture 사이 336개 raw 쌍과 30개 전체 graph 쌍도 일치했다. QA bundle projection은 반환 original7/PairId를 조합한 own wrapper이며 실제 publisher 출력·실행 증거가 아니다.

## 커버리지와 복사 격리의 범위

6 Pair cases: historical4와 delimiter/quotes/backslash/Ω encoding 2개. 독립 parent/child raw14와 original declaration7, opaque 원문, fixed supplied UTC precision, padded role/capability, ordered policy IDs, receipt11/snapshot15/policy4/redactions/full graph를 모든 BEFORE/AFTER_CALLER/AFTER_RETURNED 단계에서 비교했다. original7과 legacy factory used-clone Trim/nested GetFullPath 결과를 구분했다. Pair scope는 `DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY`다.

4 Capture 정상 회귀는 새 후보에서 새로 실행했다. Capture15/task27/options7/invocation2와 전체 receipt/policy/redaction graph를 비교했다. Capture scope는 data-only/unregistered/not issuer authenticated다. 기존 R27 PASS를 상속하지 않았다. 본 비교는 JSON token 종류·값·object key 및 array 순서·shape를 확인하며 Integer token만으로 CLR width를 증명하지 않는다. 실제 public declared types/typed compiler와 PDB source 결속을 별도 근거로 구분한다.

438 assertions/run = Pair270 + Capture168. 6,700 hierarchical rows/run = Pair206 nodes×6×3=3,708, Capture244 nodes×4×3=2,928, 제출 descriptor purity64. 컨테이너 node와 반복 phase를 포함하므로 독립 leaf 요구사항 6,700개라고 부르지 않는다.

Own ledger 584 rows/run은 primary/direct38(AdmitPair6, direct factory8, IsValid20, Capture4), ordered public getter288(Pair108/Capture180), grouped snapshot helper60, observational helper180, QA bundle projection18로 분리된다. 수동 wrapper 기록이며 모든 내부/native 호출의 동적 추적이 아니다. Pair method의 두 factory 내부 호출×6=12는 SOURCE-only indirect 사실이고 direct factory8과 혼합하지 않는다.

성공 뒤 caller bundle/parent/child bytearrays를 편집했고 재입력하지 않았다. 반환 declaration7/policy declaration/record의 detached copies를 편집한 뒤 전체 graph가 기대값과 같고 새 declaration clones임을 확인했다. Pair detached ID arrays는 실제 in-place 편집했다. Capture ID control은 detached holder replacement만 수행했으며 in-place 격리 증거라고 확대하지 않는다. Capture task27/submitted descriptors/options/invocation copies의 편집도 실제 범위대로 기록했다. Readonly cast-write exception 또는 rejection/adverse reproduction은 0이다.

## 독립 정적 발견과 필요한 수정

허용된 startup 6개 변경 구간을 전체로 읽고, 그 밖의 7개 구간 234,431바이트가 old frozen source와 byte-exact임을 확인했다. 새로운 publisher는 전체 TEXT-only로 읽었다.

| High defect | 독립 static 관측과 영향 | 필요한 다음 검증 |
|---|---|---|
| ENGINE-G05-R29-HANDOFF-20261012-01 | Pending receipt와 active snapshot의 다른 sealed type 객체를 ReferenceEquals로 비교한다. Awake acquisition 실패가 pair required gate로 종료되지 않으며 M05 hold는 private profile 존재에 의존한다. SetPending overwrite/owner 무관 ClearPending·OnDestroy가 custody를 닫지 못한다. 실제 launch는 실행·주장하지 않는다. | 실제 installed receipt identity, owner/one-use custody, sideeffect 이전 required-pairmode failclosed, owner-scoped cleanup; 새 frozen candidate의 targeted regression 및 승인된 native proof |
| ENGINE-G05-R29-CARRIER-20261012-02 | 성공한 core TryGet/nonblank만으로 pair presence를 판별해 raw empty/multi-equals/duplicate 상태를 닫지 못한다. Bundle hash/typed header/path authority 검증 전에 declared file path에서 config IO를 한다. CLI validatorarguments를 확인하고 실제 admitted snapshots arguments는 검사하지 않는다. | Raw presence/conflict/duplicates closed carrier, hash/closed header/path boundary before IO, 실제 두 snapshot arguments 검증 |
| ENGINE-G05-R29-PUBLISHER-20261012-03 | wb temp→기존 final remove→rename 및 w SHA/manifest truncation; bundleFilename/root boundary와 실제 input path↔declaration path/raw14 semantics binding이 없다. Default json.load duplicates, early savedatafolder/cwd plan 증거가 없다. | Exclusive-new owned-root publication/no delete or truncation, full raw14/original7/path binding, closed parser, actual earlyroot/cwd plan; publisher 별도 admission 필요 |

Pure method UTF-8 default replacement decoder와 explicit trailing-content read-to-end guard 부재도 SOURCE-only로 남겼다. Malformed UTF-8/duplicate/invalid role/nonempty arguments/lifetime/rejection/adverse/native case를 실행하지 않았다. Source guard 존재 또는 정상 데이터 PASS로 실제 연결·issuer authority를 인증하지 않는다. High closure와 release는 Master만 판단한다.

## 보존, 자체 오류, 제한

Initial14365 보호 경로와 frozen132, prospective253 pins, Master-pinned original failure/initial/prospective19를 최종 재해시했다. Production/source/publisher, 기존 QA/S1/S2, installed incident baseline, frozen dependency 원문을 변경하지 않았다. Known installed SHA incident의 actor·해결은 주장하지 않는다.

S1 schema `size` 가정, S2 넓은 문자열 치환/EOF 오염 및 orchestration 중단, S3 잘못된 static anchor, cp949 recovery display 오류, postrun 추측 출력 파일 조회, 마지막 width witness 파일 선택 오류를 원문·capture 한계와 함께 보존했다. 오류 자체는 PASS가 아니다. Master precise2-selector R1과 UTF-8 recovery 및 inventory-based postanalysis 정정 승인 뒤 성공한 범위만 별도 증거로 기록했다. Candidate/compiler/runner stage full streams는 첫 invocation부터 보존했다. 수동 recovery/조회 error excerpt는 tool-returned Unicode text이며 독립 original byte stream이라고 주장하지 않는다. 마지막 width selection은 실제 mapped EngineHostCensus.cs의 unique ValidatorTask class72..101, long3/int1/bool1로 후속 witness를 작성했다. SOURCE-only이며 runtime edge/native evidence로 확대하지 않는다.

No global receipt bootstrap/setpending/Awake/private reflection/currenttask/registry/Process/provider/cache/game/native/Unity lifecycle/operator publisher/adverse calls. SHA, receipt IsTrusted/IsValid, readonly/private class, consistency pair scope가 operator approval이나 protected result channel provenance를 대체하지 않는다. Old/producer E1 label 또는 100% PASS를 전체 E2로 전환하지 않는다. Master의 최종 채택, closure/release는 PENDING이다.

주요 artifact: `STATIC_SOURCE_SCOPE_BEFORE_BUILD.json`, `R29_FROZEN_LINEAGE.json`, `EXECUTION_ADMISSION_BEFORE_BUILD.json`, `PRE_RUN1_MANIFEST.json`, `PRE_RUN2_MANIFEST.json`, 두 run의 `OUTPUT_INVENTORY.json`, `postanalysis-r1/INDEPENDENT_NORMAL_RESULT_ANALYSIS.json`, `RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json`, `PRESERVATION_FINAL.json`, `FINAL_BOTH_RUN_INVENTORY_VERIFICATION.json`. 완성 terminal graph는 보고서/manifest/index/초기·resume ACK/COMPLETION을 exact SHA/bytes로 결속하고 COMPLETION을 마지막 atomic write로 봉인한다.


추가 소스 witness와 node/leaf 후처리 수치는 `VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json`, `WIDTH_COVERAGE_COUNTERS_AND_LIMITATIONS_R1.json`에 기록했다. Pre-run oracle을 바꾸지 않았다. API return 증거 일부는 chat tool-returned text를 옮긴 reconstruction이며 원래 wire bytes/serialized return 파일을 독립 보존했다고 주장하지 않는다. 실제 terminal return은 구조화된 tool return을 별도 파일로 보존한다.

| Family/case | 전체 nodes/phase | scalar leaves/phase | phases |
|---|---:|---:|---:|
| PAIR/PLAIN_PLAIN | 206 | 174 | 3 |
| PAIR/OPAQUE_OPAQUE | 206 | 174 | 3 |
| PAIR/PLAIN_OPAQUE_PADDED | 206 | 174 | 3 |
| PAIR/OPAQUE_PLAIN_PADDED | 206 | 174 | 3 |
| PAIR/OPAQUE_EQ_QUOTE_BACKSLASH | 206 | 174 | 3 |
| PAIR/OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | 206 | 174 | 3 |
| Capture/PLAIN_PLAIN | 244 | 210 | 3 |
| Capture/OPAQUE_OPAQUE | 244 | 210 | 3 |
| Capture/PLAIN_OPAQUE_PADDED | 244 | 210 | 3 |
| Capture/OPAQUE_PLAIN_PADDED | 244 | 210 | 3 |
