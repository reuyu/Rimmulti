# R38 publisher 독립 정적 QA / S1

**판정: R38_INDEPENDENT_STATIC_GAINS_CREDITED_GENERAL_CONTRACT_REVISION_REQUIRED_ORIGINAL6_SOURCE_REPRESENTABLE_RUNTIME_UNTESTED.** 날짜 전체 소비·필수 Windows 속성·구조 ASCII와 opaque 내부 보존·경로 형식 개선은 소스에서 확인했다. 일반 계약의 capability NONBLANK, identity/blank 지원 범위, 일부 claim 및 E1 provenance는 수정이 필요하다. 원래 정상 6개 literal은 새 소스에서 표현 가능하며, Master가 별도 한정 WP로 실행을 검토할 수 있다. 현재 actual publication은 NOT_ADMITTED, native/full E2 NOT_RELEASED다.

Delivery `SOL-GATE05-R38-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-01`, WP `WP_QA_ENGINE_GATE05_R38_PUBLISHER_INDEPENDENT_STATIC/S1`, result `SOL-GATE05-R38-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-c19c6459fa484d5bbee9c08ffe13caa4`. 최초 ACK/mirror SHA `1EE34CC318E4FC50B6BBA7F4EE08CE604D8870630601C1F27E0D77651802A3E9` /2355는 불변이다. Master의 R1/R2는 같은 WP의 own metadata 복구이며 후보 실행 권한이 아니다.

## 식별과 보존

새 exact frozen [publish_operator_pair.py](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R38-10b9846e/scratch/OperatorStartupPairR29/publish_operator_pair.py) SHA `940CF77220C272D117CDBC278B64858EFB3077267141CC548A0105B47D6E1306` /43666, Python MVID 해당 없음. Frozen42 manifest SHA `85F08534BD3BD47258A8AC3A247438702FB318EA7F298C952B452C2464AF99DD`, protected19676 baseline SHA `17DE6797EECAE6CFFEEACB068660354294AE37F6D6804C9CCFA378F87C485682`. Recovery에서 AGENTS/실제 canonical SRS1.6/C 정정·역사/accepted ADR/current state·decision·defect·dispatch·monitor와 범위별 Master correction 등79문서를 full 읽었다. Compaction 뒤 controlling 계약·최신 delta를 재확인했다. 기술 finding은 독립 raw/source 대조로 확인했다.

Full before/after protected19676+frozen42, 고유 19676 경로의 SHA/bytes가 일치한다. 실패한 자체 도구·부분 JSON도 별도 inventory로 보존했다. ALL Engine9/generated/설치/oldQA/oracle/Pipeline/archive 고정. WorkerBridge544B2217…/276685, Census391F9645…/170135의 unchanged R34 C# TEXT 계약을 비교했고 CLR/PE 실행·재빌드·설치0. 현재 Debug8091F441… MVID7b08d3f4-27de-4685-b61b-8a312708a496/Release9CBA… MVID93bc… lineage를 다른 candidate로 승계하지 않는다.

## 개선과 일반 계약 결함

validate_iso_utc_date146–175의149는 fullmatch이고 ASCII[0-9], year1..9999/calendar/leap/time/raw fraction 보존을 유지한다. R37의 마지막 newline 소비 문제가 좁게 SOURCE 수정됐다. 날짜 helper/adverse 사례는 호출하지 않았다. verify_path_ancestry314–404는 root와 기존 각 component를 직접 lstat하고 필수 Windows attributes를 usable int/bool 제외로 검사한다. Missing/None/nonint를 정상 검사 완료로 취급하지 않고 정확한 새 leaf FileNotFoundError만 생성 허용한다. 이는 SOURCE 개선이며 actual NTFS/reparse/runtime PASS가 아니다.

구조 role/cap는 ASCII strip/upper와 unsupported nonASCII 거부를 사용한다. Opaque origin/plan/PairID/policy/fingerprint 내부 Unicode·padding·Ω/한국어/café/quote/backslash/=를 보존한다. ConfigId는 raw==원래 UNTRIMMED 선언 AND snapshot 지원 trim(raw)==같은 UNTRIMMED 선언이다. Rawcap는 trim하지 않고 factory clone-trim descriptor와 case 비교한다. C# raw ConfigId Ordinal5064, Snapshot.Trim4709, receipt untrimmedexpected5315, clone role/cap-only trim5225/5226과 대조했다.

남은 capability NONBLANK 회귀: validate_declaration512는 structural_ascii_strip(expectedCapabilityBoundary)의 결과를 버린다. Empty-after-trim 검사 없이 validate_config592–595의 rawempty와 clonedempty가 같아질 수 있다. C# originaldecl5137/factory5243 IsNullOrWhiteSpace는 이를 거부한다. 소스 흐름으로 도출한 결함이며 invalid 입력 생성·호출0. 명시 nonblank structural cap를 검사하되 원래 선언 문자열을 보존하고 cap enum을 추가하지 않는 좁은 수정이 필요하다. 원래 12개 cap는 모두 nonblank LOCAL_SANDBOXED라 이 결함이 정상6 실패를 증명하지 않는다.

identity_boundary_trim213–219는 ASCII strip만 하며 nonASCII boundary unsupported 처리가 없다. .NET Trim을 거치는 identity/exeSHA/blankArgs의 지원 범위를 명시해야 한다. Opaque 내부까지 제한하면 안 된다. check_opaque_non_blank198–210의 Python isspace 역시 bounded CLR NONBLANK equivalence/disposition 증거가 없다. 모든 Unicode blank parity를 주장하지 않고 명시 support 한계를 둬야 한다. 후보 adverse/parity reproduction0. 정상6은 unpadded ConfigId/ASCII SHA/emptyArgs/명백한 nonblank opaque text라 이 넓은 지원 결함과 구분된다.

Closed config14/decl7/policy4, exact bootstrap/raw role, duplicate/BOM/UTF8/string 타입, descriptorSHA64 ASCII noTrim/exeSHA 별도 boundaryTrim, policy revision string/int bool 제외/ordered packages를 유지한다. Fingerprint는 NONBLANK이지64hex가 아니며 policy schema는 NONBLANK이지 WE-PACKAGE-POLICY-V1 고정값이 아니다. Package uniqueness/empty list 금지·새 PKI를 요구하지 않는다. Main867–932의 --spec closed6+fixed optional API는 선언을 객체로 포함한다. Standalone 선언 파일 API를 요구하지 않는다.

## 경로·read-once·publication 해석

LocalDOS helper251–311은 repeated/empty separator·UNC/device/ADS/traversal/control/reserved/trailing dotspace를 명시 거부하고 drive-root와 정상 space/Ω segment를 보존한다. Synthetic executable/UserData/CWD는 lexical predicate이므로 실제 파일 존재 요구를 추가하지 않는다. UserData 분리 검사와 root/component type 확인·fresh mkdir·xb staging/sidecars·postmkdir/prelink checks·final-last link/no destructivefallback·partialroot 보존을 소스에서 확인했다.

read_once407–459는 priorlstat와 handlefstat/dev/ino/mode/size/mtime/attributes 및 한 번 읽은 bytes의 SHA를 전달한다. Main spec도 동일 witness를 publish_pair에 넘긴다. Prior stat은 nofollow-open이 아니며 pathname/handle 동일성 보증이나 hostile TOCTOU 면역 증거가 아니다. Protected local owner/nonhostile concurrentwriter 가정과 실제 관찰을 분리한다. 별도 universal race/ACL/PKI 설계를 요구하지 않는다.

Hardlink contents는 staging/final에서 shared mutable이고 directory-entry 생성 의도는 sidecars 전체 transaction과 다르다. Functiondoc677–679의 한계 설명은 정확해졌다. Topdoc32–33의 cross-volume/volume-journaling caveat 및 provenance cross-volume-only flag는 더 좁은 표현이다. 동일 volume에서도 bundle+sidecars 원자 transaction·crash durability가 검증되지 않았음을 모든 claim에서 일관되게 적어야 한다. Native primitive/path/ownership/실행은 UNTESTED다.

## 원래 raw12의 시각 정정과 정상6

R35 original oracle UTF8 text·hex·SHA·bytes를 BOTH R29 upstream raw JSON 및 Master raw witness와 독립 대조했다. 모든 Parent는 2026-10-11T00:00:00.1234567Z, 모든 Child는 **2026-10-11T00:00:01.0000000Z**다. 기존 저장 config14와 raw decode에도 차이가 없다. 이전 QA의 no-fraction Child prose는 잘못됐고 이번 new sidecar/report가 정정한다. 기존 oracle/report/ACK/raw byte를 바꾸지 않았다. Capture previous_QA_prose의 간접 표시 설명은 원인 입증이 아니며 parser/display의 인과 원인은 UNVERIFIED다. Actual raw가 해석 기준이다.

| 원래 case ID | Parent raw SHA / bytes | Child raw SHA / bytes | 새 소스 판단 |
|---|---|---|---|
| PLAIN_PLAIN | 25D3B88B03B708772B8C1B6CE9AAF66E4250EE84D3AAB6C53CBEC7BF9EE75A21 / 897 | D6E345FEB30873C6002102E4C13BC5815A781C7177233B2DF64D82E49DD2A6CD / 909 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_OPAQUE | 5077C839A2EFD38495FF553AD2F16F1B5C50F9CDA4A5D673E5014CEC2552124B / 919 | DAA3A0F16906EBF54B0A4CA8D2040B8BE9FE75A785DE1CD28573D17E8A5ACADA / 931 | SOURCE 표현 가능 / 실행0 |
| PLAIN_OPAQUE_PADDED | 25D3B88B03B708772B8C1B6CE9AAF66E4250EE84D3AAB6C53CBEC7BF9EE75A21 / 897 | DAA3A0F16906EBF54B0A4CA8D2040B8BE9FE75A785DE1CD28573D17E8A5ACADA / 931 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_PLAIN_PADDED | 5077C839A2EFD38495FF553AD2F16F1B5C50F9CDA4A5D673E5014CEC2552124B / 919 | D6E345FEB30873C6002102E4C13BC5815A781C7177233B2DF64D82E49DD2A6CD / 909 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_EQ_QUOTE_BACKSLASH | B0CB65941E0548E7809829F2B198EEA5CAA58F4C94A945DFAA207FF4A1B11CE0 / 914 | 871D13EB216C404A74F65A4603BE913B8AFB7919EE6CE6E236D03874C1270516 / 940 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | E647B4CE8F245E4270C38DC2EAC25DF0092CE6FF58E9415906A7FFD10E1A10C6 / 936 | E1F0E41C784D7767D661588DAD839A3B9B547EBDBA89260484A62F5C964AC26A / 962 | SOURCE 표현 가능 / 실행0 |

Full config14/decl7/PairID를 matrix에 그대로 기록했다. Future locator delta는 expectedConfigPath뿐이며 fixture/spec/output을 생성하지 않았다. Case5/6은 다음 실제 JSON literal이며 producer Markdown의 중복 escape를 원본으로 복사하지 않는다.

- `OPAQUE_EQ_QUOTE_BACKSLASH`: `"  operatorPairId=5 \"Ω\" \\ original  "`
- `OPAQUE_EQ_QUOTE_BACKSLASH_PADDED`: `"  operatorPairId=6 \"Ω\" \\ original  "`

남은 넓은 cap/Unicode support 결함은 exact6 raw값이 사용하는 정상 범위를 실패시키는 source 근거가 아니다. 따라서 Master가 **동결940CF772/43666+exact6 oracle/raw12+fresh own 코드/EXE/dependency/context pins+사용 가능한 Windows attributes의 새 owned localDOS root+protected writer 가정**을 명시한 별도 positive6 publication WP를 검토하도록 권고한다. 첫 raw stdout/stderr/numericexit/PID/time과 partial outputs를 보존하고 기대값은 input oracle로 통제해야 한다. 추가 adverse/Engine/game/operator promotion/native/fullGate 실행으로 확대하지 않는다. 현재 WP에서 실행하거나 스스로 admission하지 않는다. General contract REVISION_REQUIRED와 좁은 정상 실행 권고는 별도다.

## E1 provenance 독립 대조

COMPLETION의 size와 frozen rows의 bytes 스키마를 읽고22 artifact SHA/size를 모두 확인했다. AST_INPUT manifest, final publisher/child/outerlauncher pins와 proof의 manifestSHA, actual child PID9668 exit0/fullFIRSTstdout2699/stderr0를 frozenraw로 검증했다. Raw summary 4926ASTnodes/18functions와 own passive AST가 일치한다. Own body nodes38은 별도 수치이며 runtime 테스트 수가 아니다. Producer helper/launcher는 읽기만 하고 재실행0.

Outerlauncher selfpin/일부 resolved stdlib file observations 추가를 인정한다. Declared count65 대비 실제 manifest rows는20 sampled launcher modules다. Child 실제 sys.path/resolved import filenames+SHA가 없고 PYTHONHOME/PYTHONPATH/default ambient path context, 모든 helper의 beforebody syntax/full graph 및 outer FIRST raw stream은 미완전하다. EXE/AST pins를 complete ambient attestation으로 확대하거나 뒤에서 관찰한 hash를 소급 prospective pin으로 바꾸지 않는다.

OWNED_OUTPUT_MANIFEST11개 rows와 실제 owned12개가 일치하며 미기재는 자기 manifest 하나다. Late verify_all_artifacts.py가 포함된 수정은 인정한다. Selfhash를 요구하는 것은 아니고 selfcycle/unfinishedlogger/postseal explicit exclusions와 finite inventory policy가 여전히 필요하다. Current REQUIREMENT8_SOURCE_WITNESS의 line ranges/ SOURCE_IMPLEMENTED_UNVERIFIED 표기는 개선됐다. Cap nonblank comment 자체는 검사 구현이나 verification oracle가 아니다.

Compatibility 보고서에는 authority SHA3개가 틀리다. Actual artifact/binary hash 변조 사건을 추론하지 않는다. Actual ACK/task authority pins 및 fixed source와 잘못된 prose ref를 구분하고 새 metadata에서 정확한 identity를 기록한다.

| Authority | 실제 SHA | Producer prose SHA |
|---|---|---|
| MASTER_R38_PUBLISHER_BOUNDARIES_IMPLEMENTATION_CONTRACT_20261014.md | BFE455E5E3A9C1C71735AFEDB8732BD3A8AA444E1F03B9DE1FD348E6FC2B69B6 | BFE455E5E3A9C1C7D52F179EDDC96068694086E64B01B7A490FA3E817BD03D14 |
| MASTER_R37_ORIGINAL_LITERAL_TIMESTAMP_CORRECTION_20261014.md | FEC2A1C44D1BD6CEDF4E0EF15F23B7B51E940C863A3E246F09AC0C5AA56026E0 | FEC2A1C44D1BD6CE514338BFBC323495FD5CD390E2551A077FD5EE082DA4E9EE |
| MASTER_R37_ORIGINAL_LITERAL_TIMESTAMP_RAW_WITNESS_20261014.json | 5C54C5570D88FEDAEA1EFD28329DB0078B0D8AA7D5485B6666844B025491A0F1 | 5C54C5570D88FEDA004A81CDA806875225E0A72B28DC7A5F4829986A8ED0109C |

## 자체 오류 복구와 최종 증거

최초 WindowsApps alias Get-FileHash 실패는 Python AST/logger/bootstrap 이전의 native locator exit1이다. 원래 invoke/common/log/bootstrap와 STOP5를 보존했고 Master R1은 신규 invoke_r1의 locator 한 줄만 명시 AnacondaEXE388FE2…/104264로 바꿨다. DynamicPSCommandPath seed가 실제 새 wrapper를 beforebody 결속한다. 기존 log INPUT의 oldinvoke 행은 failed historical dependency일 뿐 actual launcher 증거가 아니다. Supplement/각 seed/index에 새 wrapper를 따로 결속했다. Native syntax preflight PID는 미캡처 UNOBSERVED이며 stagechild PID/time/full firststreams는 실제다. Partial launcher/module observations를 comprehensive child import attestation으로 주장하지 않는다.

BootstrapPID16604 exit0, capturePID13060 exit0 후 own reviewPID10324는 syntaxprecheck0/bodyexit1/stdout0/stderr1915였다. 마지막 out()의 duplicate scope 때문에 종료했으며 기존 검토 JSON을 보존했다. 원래 review를 재실행하거나 exit0으로 재명명하지 않았다. Master R2 신규 driver/logger/review_finalize_r2는 beforebody syntax·code/EXE/inputcontext를 결속하고 기존partial55/첫오류를 검증한 후 누락 MINIMAL_NEXT만 allowed_change_scope 키로 작성했다. ActualPID17348 exit0/stdout468/stderr0, original replay0이다.

새 prepare/seal은 성공 R2와 원래 실패를 모두 accounting하고 fullbeforeafter inventory/보고서/EM/index/initialACK-completionbinding/COMPLETIONlastatomic를 봉인한다. EM 자기cycle·unfinished seal logger streams·actualdirectreturn은 명시 제외하고 후속 실제 rows를 별도 retained한다. InitialACK/PENDING intent는 receipt로 덮어쓰지 않는다. Master가 final receipt/disposition을 판단한다.

Candidate/producer/oldQA import-call/publisher/publication/fixture/compiler/Engine/CLR/unitrunner/native/game/operatorProcess/adverse/rejection0, production modify/build/install0, governance/AGENTS/Masterstate/scheduler writes0. High4/Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplit OPEN, native/full E2 NOT_RELEASED, Foundation HOLD, installed mismatch OPEN/actorUNKNOWN/no restore, currentSRS1.6/no1.7migration. DedicatedServer finalDomainAuthority/W-L-G-M/oneLocalClockwriter/islandbarrier/targetpublication 유지. Master final disposition PENDING.
