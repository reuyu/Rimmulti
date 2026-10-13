# R37 publisher 독립 정적 QA / S1

**판정: INDEPENDENT_R37_BINDING_ROOT_READONCE_SOURCE_GAINS_DATE_ATTRIBUTES_DOMAIN_PROVENANCE_REVISION_REQUIRED_PUBLICATION_NATIVE_NOT_ADMITTED.** 실제 configId/raw capability 바인딩, 루트 포함 직접 lstat, read-once spec/config stat·SHA 출처 전달을 소스에서 확인했다. 날짜 전체 소비, 필수 Windows 속성 누락, 구조 문자열/opaque 구분 및 claim·prospective graph는 수정이 필요하다. Publication/native 실행0이며 sourcefinding 수는 runtime 테스트나 High closure 수가 아니다.

Delivery `SOL-GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-01`, WP `WP_QA_ENGINE_GATE05_R37_PUBLISHER_INDEPENDENT_STATIC/S1`, result `SOL-GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-0fa2809cbd3a47e698af81520072a193`. Original Sol/local→Master/local 직접 ACK와 완료 보고. 초기 ACK/mirror `20FB710B2B00678F1C1872FACC7252BC9EA5F5395486167EE39849D9DFA7C2DF` /2058은 불변이다.

## 식별·읽기·보존

새 exact frozen 소스 [publish_operator_pair.py](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R37-de39916a/scratch/OperatorStartupPairR29/publish_operator_pair.py) SHA `8F31D69A26A364BF727ABD029E096C0416B3C7B6BA54AC29A6A6E246FF537FD9` /40358, Python MVID 해당 없음. Frozen42 manifest `1916E40664113EDD90A1679336E37A6C6101C0184326C47ECF0B6734DA5119FC`; protected19530 baseline `79A53CB58F6CDE28E688705B6642DCC923C62FB498BEB6A50E4D04505B357618`. Canonical SRS/AGENTS/C correction/history/accepted ADR/current governance 및 state/decision/defect/dispatch/monitor 73개 문서를 full 읽고 최신 delta와 Master R37 contract/E1 review, accepted R36/R35 correction을 대조했다. Master 기술 finding은 독립 확인·정정 대상으로 취급했다.

Full before/after protected19530 + frozen42 기록 행, 19530 고유 경로의 SHA/bytes가 모두 일치한다. ALL Engine9/generated/oldQA/Pipeline/archive/current 설치/oracle 불변. EngineR34 WorkerBridge544B2217…/276685, Census391F9645…/170135, Debug8091F441…/MVID7b08d3f4-27de-4685-b61b-8a312708a496/PDBFE75…, Release9CBA…/MVID93bc…의 기존 lineage다. CLR/PE 실행·재빌드·설치0, 현재 SRS1.6/1.7 migration0.

## 실제 바인딩 개선과 남은 domain

R37 cfg_id != expected_id492, ascii_strip(cfg_id) != SAME expected_id496로 R36의 trimBOTH 중복 비교를 좁게 고쳤다. C# raw ConfigId Ordinal5064→Snapshot.Trim4709→receipt UNTRIMMEDdesc5315, clone role/cap-only trim5225/5226을 frozen actualsource에서 확인했다. R37 raw_cfg_cap505는 strip하지 않고 clonedtrimdesc504와 ASCII case 비교한다. Original padded/lowercase 선언은 변환하지 않고 그대로 aux4에 쓴다. 이 narrow bug는 **SOURCE ONLY 해결**이며 일반 Unicode/receipt/native authority PASS는 아니다.

ascii_upper203–205는 ASCII lowercase만 바꾸고 nonASCII 구조 case 문자도 그대로 통과시킨다. 명시 structuralASCII capability 지원 범위와 failclosed unsupported 경계는 아직 닫히지 않았다. Cap enum이나 새 프로토콜을 만들지 않는다. ascii_strip192–200은 모든 위치의 nonASCII whitespace를 거부하며 모든 선언7 val419, configId, fingerprint, policy schema/ID/revision에도 적용된다. Opaque origin/plan/policy·identity 내부 Unicode content를 NONBLANK 조건 이상으로 제한한다. Identity의 unsupported boundary trim과 opaque 내부 보존을 구분하고 원래 문자열을 normalize/rewrite하지 않아야 한다.

Exact bootstrap/raw SIMULATION·READ_ONLY/UTF8/BOM/duplicate/closed14·7·policy4, originaldescriptorSHA64 ASCII noTrim/exeSHA별도Trim, fingerprint NONBLANK, revision string/int bool-excluded/ordered packages는 유지된다. Policy schema NONBLANK는 WE-PACKAGE-POLICY-V1 equality가 아니다. Actual ToRecord→SerializePackagePolicy/ComputePackagePolicyDigest는 nonempty suppliedschema를 보존하며 later content check는 별도다. Fingerprint64hex/package uniqueness/nonemptylist/새 PKI를 요구하지 않는다.

validate_iso_utc_date140–169: ASCII [0-9], year1..9999, calendar/leap/time 및 원래 1..7fraction 보존은 개선됐다. 그러나143은 _ISO_UTC_REGEX.match이고 패턴은 $로 끝나므로 마지막 newline 앞에서도 끝날 수 있다. Whole-input consumption/fullmatch claim은 구현과 다르다. Fullmatch 또는 explicitend 일치로 닫아야 하며 rawUTC text를 재직렬화·6자리 rounding하지 않는다. 후보 date/rejection 함수를 호출하지 않았다.

## 경로·read-once·publication

verify_path_ancestry253–337은 root부터 직접 lstat, 필수 ancestorDIR와 inputREG/outputDIR 타입, 정확히 새 output leaf의 FileNotFoundError만 허용, postmkdir/prelink DIR 검사로 이전 root/lexists 실패 masking 문제를 개선했다. ASCII drive와 normal Ω segment 지원도 확인했다. 그러나 ancestor/기존 leaf attrs=getattr(...,None), 거부는 attrs is not None일 때만 실행된다. 계약상 필수 Windows attributes가 없으면 unsupported/failclosed여야 한다. Missing attributes를 정상 검사 완료로 볼 수 없다.

LocalDOS helper208–250은 slash→backslash 및 빈 separator segment 제거로 repeated separators를 접는다. 이 지원 normalform/alias 범위를 명시하거나 unsupported ambiguity를 거부해야 한다. 관찰된 우회나 hostile-race reproduction을 주장하지 않는다. Synthetic runtime exe/UserData/CWD path는 lexical predicate이며 native existence/ownership 허가가 아니다.

read_once_file_and_stat340–382는 priorlstat, open handle fstat(dev/ino/mode/size/mtime_ns/attributes), 한 번 read한 bytes, SHA와 handlesize=length를 기록한다. Main spec witness가 publish_pair의 specFile로 전달되고 config witnesses도 provenance에 결속된다. 이 전달 결함은 narrow SOURCE 개선이다. Prior path stat과 handle stat을 서로 비교하거나 open을 nofollow로 보호한 증거는 아니며 afterread 동일성/actualhandle ownership을 보장하지 않는다. Protected owner/non-hostile concurrentwriter assumptions는 이제 flag로 보인다. 이를 바탕으로 관찰과 보장/TOCTOU/native 한계를 정확히 적으면 되며 새 ACL/PKI·보편적 race immunity 설계는 필요 없다.

mkdir 새 root/xb staging·SHA·provenance/final-last os.link/no destructivefallback·delete·retry는 유지된다. Hardlink contents shared/mutable flags와 주석이 추가됐지만 topdoc에는 immutable staging이 남고 publish_pair docstring의 bundle+manifest atomically writes도 넓은 주장이다. 동일 volume에서도 sidecars 전체가 단일 transaction은 아니다. Final entry 원자 생성 의도, crash durability, 전체 publication 성공을 구분하고 오류 partialroot를 보존한다. 실제 NTFS primitive/publication/game/native는 UNTESTED다.

## 원래 6개 literal의 독립 대조

새 소스 의미를 R35 prep/R36 accepted matrix/두 R29 upstream과 대조했다. 원래 case IDs/PairIDs/raw12 UTF8hex SHAbytes/config14/decl7가 모두 불변이고 future descriptor 차이는 expectedConfigPath 하나다. 원본 파일·기대값을 수정하지 않았으며 새 fixture를 쓰거나 후보를 호출하지 않았다. CLI exact --spec closed6+fixedoptional은 기존 계획과 호환되고 선언은 spec의 객체에 포함된다. Standalone declaration-file API 조건을 만들지 않는다.

| 원래 case ID | Parent raw SHA / bytes | Child raw SHA / bytes | 판정 |
|---|---|---|---|
| PLAIN_PLAIN | 25D3B88B03B708772B8C1B6CE9AAF66E4250EE84D3AAB6C53CBEC7BF9EE75A21 / 897 | D6E345FEB30873C6002102E4C13BC5815A781C7177233B2DF64D82E49DD2A6CD / 909 | 새 R37 SOURCE 표현 가능 / 실행0 |
| OPAQUE_OPAQUE | 5077C839A2EFD38495FF553AD2F16F1B5C50F9CDA4A5D673E5014CEC2552124B / 919 | DAA3A0F16906EBF54B0A4CA8D2040B8BE9FE75A785DE1CD28573D17E8A5ACADA / 931 | 새 R37 SOURCE 표현 가능 / 실행0 |
| PLAIN_OPAQUE_PADDED | 25D3B88B03B708772B8C1B6CE9AAF66E4250EE84D3AAB6C53CBEC7BF9EE75A21 / 897 | DAA3A0F16906EBF54B0A4CA8D2040B8BE9FE75A785DE1CD28573D17E8A5ACADA / 931 | 새 R37 SOURCE 표현 가능 / 실행0 |
| OPAQUE_PLAIN_PADDED | 5077C839A2EFD38495FF553AD2F16F1B5C50F9CDA4A5D673E5014CEC2552124B / 919 | D6E345FEB30873C6002102E4C13BC5815A781C7177233B2DF64D82E49DD2A6CD / 909 | 새 R37 SOURCE 표현 가능 / 실행0 |
| OPAQUE_EQ_QUOTE_BACKSLASH | B0CB65941E0548E7809829F2B198EEA5CAA58F4C94A945DFAA207FF4A1B11CE0 / 914 | 871D13EB216C404A74F65A4603BE913B8AFB7919EE6CE6E236D03874C1270516 / 940 | 새 R37 SOURCE 표현 가능 / 실행0 |
| OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | E647B4CE8F245E4270C38DC2EAC25DF0092CE6FF58E9415906A7FFD10E1A10C6 / 936 | E1F0E41C784D7767D661588DAD839A3B9B547EBDBA89260484A62F5C964AC26A / 962 | 새 R37 SOURCE 표현 가능 / 실행0 |

원래 six에는 unsupported Unicode whitespace가 없고 ASCII padding과 opaque Ω/한국어/café/quote/backslash/=는 현재 predicates로 표현 가능하다. 이 점은 일반 opaque 값의 과도 제한을 해소하지 않는다. Parent2026-10-11T00:00:00.1234567Z/child2026-10-11T00:00:01Z를 정확히 유지한다. Child .0000000Z를 발명하지 않는다. Publication은 safe candidate 수정/freeze·새 explicit normal WP 전까지 모두 BLOCKED다. R36 source representability나 이전 PURE PASS를 runtime 결과로 승계하지 않는다.

추가 독립 정정: producer compatibility report는 case5 PairID를 qa.R29.pair.05 Ω, case6을 qa.R29.pair.06 Ω로 설명했다. 실제 원래 값은 아래와 같다. 원래 oracle을 수정하여 producer 설명에 맞추면 안 된다.

- `OPAQUE_EQ_QUOTE_BACKSLASH`: `"  operatorPairId=5 \"Ω\" \\ original  "`
- `OPAQUE_EQ_QUOTE_BACKSLASH_PADDED`: `"  operatorPairId=6 \"Ω\" \\ original  "`

## E1 raw/prospective graph와 claim

Producer size schema를 먼저 읽어 COMPLETION artifact22 SHA/size를 frozen42 bytes와 대조했다. AST_INPUT finalsource/interpreterEXE104264/checker2253 prospective pins, actual PID15208/exit0/first rawstdout3022/stderr0를 확인했다. 실제 body36/functions16와 raw/proof가 일치한다. Exact interpreter `388FE2CFFDA8A134E7D7DC4E978F7C478857ECE6B69694DAECBED25E51EC633A` currentread match는 독립 현재 관찰이며 소급 prospective pin이 아니다.

Actual child sys.path/modules가 launcher observations와 분리되어 새로 기록된 점을 인정한다. 하지만 child module names/path 목록은 resolved importfile SHA나 실행 전 input attestation이 아니고 outerlauncher self/fullhelpergraph/selectedenvironment/stdlib-library hashes가 prospective graph에서 빠져 있다. EXE hash만으로 ambient Python 전체를 결속했다는 주장을 할 수 없다.

OWNED_OUTPUT_MANIFEST는10개, 실제 frozenowned는12개: selfmanifest와 late verify_all_artifacts.py가 미기재다. All rows/hashbytes 확인 후 원본을 보존했으며 manifest/raw를 재작성하거나 producer helper를 재실행하지 않았다. Explicit cycle/postseal exclusions와 complete recursive helper inventory가 필요하다. REQUIREMENT8_SOURCE_WITNESS의 stale ranges(예: cfgId357–367 claim vs actual492/496, capability369–378 vs504/505, readhelper308–348 vs340–382, main632–680 vs777–843)와 모든 IMPLEMENTED_VERIFIED claim도 수정 대상이다. Syntax·원래 six 설명은 wholecontract/publication/math100% admission 증거가 아니다.

## 최소 후속 수정·증거 제한

MINIMAL_NEXT_PUBLISHER_CORRECTIVE_REQUIREMENTS.json의8개 항목은 Master 판단용이고 신규 WP가 아니다. 날짜 full consumption/requiredattrsNone failclosed/structuralASCII와 opaqueNONBLANK 구분/explicitseparator domain, accurate bounded handle·hardlink claims, exact originalsix PairIDs/actuallinewitness, prospective fullhelper-env-library/cycle graph만 좁게 고친다. Corrected binding/root/readonce/strictCLI/nonoverwrite 개선은 유지하고 Engine9/generated/current1.6은 고정한다. Engine rebuild를 prose 정정에 추가하지 않는다. Master exactnewfreeze/freshstatic 이후에만 별도 positive6 actualpublication WP가 필요하다.

모든 own metadata helper는 신규 QAroot에 있고 BEFORE review/prepare/seal body 실행에 source/interpreter/dependency/inputcontext prospective pins와 own AST syntaxprecheck를 남겼다. Successful bootstrap/capture/review/prepare/seal 각각 actualnumericexit/fullFIRSTraw를 검사한다. 이번 own metadata 오류·숨은 retry0; 이전 R36 실패/helper/oracle는 TEXT만 읽고 수정·실행0. Full before/after inventory, EM/index/Koreanreport/initialACK terminalbinding/COMPLETION lastatomic, selfcycle/unfinished seal logger/postseal directreturn exclusions를 명시한다. 실제 seal raw/return은 별도로 남기고 초기 ACK/pending intent를 수락 기록으로 덮어쓰지 않는다. QA launcher module file observations 역시 complete child import attestation으로 확대하지 않는다.

Candidate/producer/oldQA import-call/publisher/publication/fixture/compiler/Engine/runner/game/native/operator/Process/adverse/rejection0, production modification/build/install0. Governance/AGENTS/Masterstate/scheduler 변경0. High4/Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplit OPEN, native/full E2 NOT_RELEASED, Foundation HOLD, installed incident OPEN/actorUNKNOWN/no restore. DedicatedServer final DomainAuthority/W-L-G-M/oneLocalClock writer/island barrier/target publication 유지. Master receipt/disposition/closure PENDING.
