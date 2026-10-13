# R36 publisher 독립 정적 QA / S1

**판정: INDEPENDENT_R36_CONFIG_CLI_SOURCE_GAINS_RECEIPT_ANCESTRY_TIME_ORACLE_PROVENANCE_REVISION_REQUIRED_PUBLICATION_NATIVE_NOT_ADMITTED.** R36 설정·CLI·독점 생성의 소스 개선을 인정한다. C# receipt 바인딩, 전체 경로 검사, ASCII 날짜 경계 및 입력·도구 출처 증거는 수정이 필요하다. Publication과 native 실행은 허용되지 않았고 실행하지 않았다. 정적 관찰 수는 테스트 PASS 수가 아니다.

Delivery `SOL-GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-01`, WP `WP_QA_ENGINE_GATE05_R36_PUBLISHER_INDEPENDENT_STATIC/S1`, result `SOL-GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-6ed51db08e3540c9b6b98a6a96f57e1d`. Original Sol/local → Master/local 직접 보고. Initial ACK/mirror SHA `038FA117B1B2EEED468A622A98D1E49C861D913C40A6A6ED63DF8F5AE191E4AC` /2071은 변경하지 않았다.

## 식별 정보와 범위

선택 Python 소스 [publish_operator_pair.py](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R36-d2d6556b/scratch/OperatorStartupPairR29/publish_operator_pair.py) SHA `F60CBC184C6627F0FE15A5A904D0C45A026E20C5138973066BB8174DD8FBFD3F` /31689, Python MVID 해당 없음. Frozen43 manifest `3F60458A4303F0B9CB8F1C0003D3E0E39E37F80E002B5FA06CACA4A3D197D130`, protected19380 baseline `4BD2C7789721BBA4DBB61A8F57B289837B9496CB104FA83CB5BFA70CA967554E`. Canonical SRS/AGENTS/C 정정본·history·accepted authority 및 현재 state/decision/defect/dispatch/monitor 69개 문서를 전체 읽었다. R36 WP와 supported-domain 계약, accepted R35 정책·filesystem 정정, Master E1 검토를 원문·증거와 대조했다.

Engine은 R34 Debug8091F441…/MVID7b08d3f4-27de-4685-b61b-8a312708a496/PDBFE75… 및 WorkerBridge544B2217…/276685, Census391F9645…/170135 그대로다. CLR 로드·PE 실행·Engine 재빌드 없음. Producer/old QA helper는 TEXT로만 읽고 import/실행하지 않았다. 대상 RimWorld1.6 유지, 1.7 이전·Steam 업데이트 없음.

Full before/after: protected19380 + frozen43 행, 19380 고유 경로 모두 SHA/bytes 일치. 원본 QA/oracle/manifest/설치 파일 수정0. Directory 이름이나 파일 존재만으로 독립 E2/완료/authority를 추론하지 않는다.

## 소스 개선과 실제 C# 차이

`main`619–681: --spec argc3 정확 일치, closed6 required + optional fixed bundleFilename, 타입·중복·unknown 검사. Inline API는 명시 unsupported. 선언은 spec 객체에 포함되므로 지원되지 않는 standalone declaration-file API를 새로 요구하지 않는다. Config와 spec raw bytes는 각각 한번 읽지만 fstat/handle identity witness와 spec SHA/bytes 전달이 없다.

`validate_config`312–441: exact bootstrap/raw SIMULATION·READ_ONLY, strict descriptor64 ASCIIhex/noTrim, executable SHA별도Trim64hex, lexical requiredpaths/UserData 분리, fingerprint NONBLANK, policy closed4/nonblank/revision bool 제외/ordered strings를 인정한다. UTF8/BOM·duplicate·fullEOF 검사와 원래 선언7/opaque PairID/compactUTF8 writer order도 유지된다. strict publisher decoder는 C# decoder와 동일하다는 보장이 아니라 승인된 좁은 safety 경계다.

`configId`: Python은 raw equal 뒤 cfg_id.strip()과 desc.expectedConfigId.strip()을 비교해 두 번째 조건이 중복된다. 실제 C# clone은 role/cap만 trim(5119–5120,5225–5226), raw configId Ordinal 비교5064, snapshot configId.Trim4709, receipt snapshot.ConfigId와 **원래 untrimmed expectedConfigId** Ordinal 비교5315다. 양쪽의 같은 padding을 허용하는 publisher 관계는 receipt 관계와 다르다. 원래 문자열·oracle을 normalize해서 숨기면 안 된다.

`capabilityBoundary`: C#5069는 RAW configcap와 factory-trimmed descriptor를 OrdinalIgnoreCase 비교한다. R36은 rawcap도 strip한 뒤 비교한다. 원래 padded/lowercase declaration은 그대로 보존하면서 rawcap에 실제 경계를 적용해야 한다. 일반 Unicode upper/strip과 CLR Trim/OrdinalIgnoreCase 동일성은 입증되지 않았다. 구조 문자열의 지원 whitespace/case 범위를 명시하되 opaque configId/origin/plan/policy Unicode를 일괄 ASCII로 제한하지 않는다.

Policy accepted correction 유지: Snapshot은 supplied schema NONBLANK를 요구하고 ToRecord→SerializePackagePolicy/ComputePackagePolicyDigest 경로는 비어 있지 않은 supplied schema를 보존한다. WE-PACKAGE-POLICY-V1 고정값 강제는 없다. Later CheckPackagePolicy는 별도 unexecuted content 경계다. Fingerprint64hex·package uniqueness/nonemptylist·새 PKI/authority 조건을 만들지 않는다.

`validate_iso_utc_date`130–157: 월/일/윤년/시분초 및 raw 1..7 fraction 보존 개선은 확인했다. 정규식\d는 Unicode-decimal이며 match/$는 마지막 newline 앞에서도 끝날 수 있고 year0000 범위 조건이 없다. 지원 계약의 ASCII 전체 소비와 year1..9999가 필요하다. 원래 text를 유지하고 Python6자리 재직렬화나 일반 CLR DateTime parity를 주장하지 않는다. 해당 반례 함수를 호출하지 않았다.

## 경로·출판 경계

`check_supported_local_dos_path`180–218은 control/ADS/traversal/일반 reserved DOS/trailing dot-space/unsupported root를 검사하며 Ω segment를 보존한다. 다만 drive isalpha는 명시 ASCII localDOS 지원 범위를 닫지 않는다. 이것은 accepted contract 범위 문제이고, Pythonisalpha vs C#char.IsLetter가 다르다는 단정은 아니다. 반복 separator/별칭/지원 도메인도 명시해야 한다.

`verify_path_ancestry`221–254의 drive root는 current에 대입만 하고 loop가 check_parts[1:]부터 시작해 lstat하지 않는다. 각 lstat는 lexists(current) 참일 때만 실행하므로 오류로 false가 반환되면 검사 자체를 건너뛸 수 있다. allow_leaf_missing의 absent/error 구별, parent isdir의 follow, 각 ancestor directory 및 leaf file의 동일 nofollow stat 타입 증거가 불완전하다. Windows attribute가 없을 때0 default도 지원 플랫폼/실패 도메인을 명시해야 한다. 정확히 새 output leaf 하나만 missing 허용, 나머지 필수 inspection 오류는 failclosed가 필요하다.

`publish_pair`444–616은 postmkdir/prelink 재검사, mkdir 새 root/xb stage-SHA-provenance/final-last os.link/no destructive fallback을 유지한다. 그러나 검사와 open/link 사이 TOCTOU는 남고 보호된 local owner/non-hostile writer 가정은 충분히 기록되지 않았다. 새 ACL/PKI/경쟁주입 설계로 확대하지 않는다. Hardlink stage/final은 contents를 공유하므로 immutable이 아니고 final entry 하나와 여러 sidecar의 원자적 transaction은 다르다. 실제 NTFS primitive 성공, crash durability/전체 publication/ownedwriter는 UNTESTED다.

## 원래 6개 정상 literal 대조

R35 준비 oracle 및 두 R29 upstream을 전체 읽고 raw12 UTF8/hex/bytes/SHA, config14, original declaration7, original PairID를 case별 대조했다. prospective descriptor 차이는 expectedConfigPath 하나뿐이며 fixture나 새 기대값을 만들지 않았다. 아래 소스 표현 가능 판정은 실행·전반적 admission PASS가 아니다. 실제 publication은 전체 후보 계약의 미해결 사항과 새 explicit WP 전까지 BLOCKED다.

| 원래 case ID | Parent raw SHA / bytes | Child raw SHA / bytes | 판정 |
|---|---|---|---|
| PLAIN_PLAIN | 25D3B88B03B708772B8C1B6CE9AAF66E4250EE84D3AAB6C53CBEC7BF9EE75A21 / 897 | D6E345FEB30873C6002102E4C13BC5815A781C7177233B2DF64D82E49DD2A6CD / 909 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_OPAQUE | 5077C839A2EFD38495FF553AD2F16F1B5C50F9CDA4A5D673E5014CEC2552124B / 919 | DAA3A0F16906EBF54B0A4CA8D2040B8BE9FE75A785DE1CD28573D17E8A5ACADA / 931 | SOURCE 표현 가능 / 실행0 |
| PLAIN_OPAQUE_PADDED | 25D3B88B03B708772B8C1B6CE9AAF66E4250EE84D3AAB6C53CBEC7BF9EE75A21 / 897 | DAA3A0F16906EBF54B0A4CA8D2040B8BE9FE75A785DE1CD28573D17E8A5ACADA / 931 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_PLAIN_PADDED | 5077C839A2EFD38495FF553AD2F16F1B5C50F9CDA4A5D673E5014CEC2552124B / 919 | D6E345FEB30873C6002102E4C13BC5815A781C7177233B2DF64D82E49DD2A6CD / 909 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_EQ_QUOTE_BACKSLASH | B0CB65941E0548E7809829F2B198EEA5CAA58F4C94A945DFAA207FF4A1B11CE0 / 914 | 871D13EB216C404A74F65A4603BE913B8AFB7919EE6CE6E236D03874C1270516 / 940 | SOURCE 표현 가능 / 실행0 |
| OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | E647B4CE8F245E4270C38DC2EAC25DF0092CE6FF58E9415906A7FFD10E1A10C6 / 936 | E1F0E41C784D7767D661588DAD839A3B9B547EBDBA89260484A62F5C964AC26A / 962 | SOURCE 표현 가능 / 실행0 |

Plain/opaque policy ID·revision, configId의 Ω/quotes/backslash/=, padded lowercase original role/capability와 모든 opaque PairID를 보존한다. Raw config role/cap는 exact이며 raw configId 자체에는 padding이 없어 현재 configId/cap 결함이 원래 6개를 막지는 않는다. 다른 입력 전반의 contract failure는 여전히 남는다. Parent issuedAtUtc는 정확히2026-10-11T00:00:00.1234567Z, child는2026-10-11T00:00:01Z다. Child .0000000Z를 새로 기대값에 넣지 않는다. 기존 spec closed6+fixed optional shape는 소스와 호환되지만 실제 root/file 존재·stat·byte SHA·future path rebind·전체 publication은 입증되지 않았다.

## Producer E1와 claim 정정

Producer COMPLETION의 size 스키마를 먼저 읽고 artifact 21개 SHA/size를 frozen43 bytes와 대조했다. AST_INPUT의 최종source·interpreterEXE·ast_checker hash/size와 AST_TOOL PID19052/exit0/raw stdout861/stderr0가 맞는다. JSON exact interpreter SHA `388FE2CFFDA8A134E7D7DC4E978F7C478857ECE6B69694DAECBED25E51EC633A` /104264는 현재 독립 read와 일치하되 이를 retroactive prospective pin으로 쓰지 않는다.

실제 AST body33/functions13이다. Producer COMPLETION/implementation report의25 및 존재하지 않는 함수 이름과 interpreter digest를 정정한다. AST syntax는 publication semantics PASS가 아니다. Launcher sys.path/default_modules 리스트는 child actual context가 아니며 launcher 자기 코드·전체 helpergraph·environment/library hash가 prospectively 결속되지 않았다. interpreterEXE 해시만으로 stdlib/site/DLL 전체 identity는 증명되지 않는다.

Owned manifest12 vs frozen14: self OWNED_OUTPUT_MANIFEST.json 및 late verify_all_artifacts.py가 미기재다. 모두 해시를 확인하고 원본을 보존했으며 기존 manifest를 다시 쓰거나 소급 pin하지 않았다. 다음 revision은 complete recursive owned graph와 cycle/postseal exclusions를 명시해야 한다. Generic six categories/snippets/100% admitted 및 immutable/wholeancestry guarantees는 실제 원래 6개·동결 소스 증거로 인정하지 않는다. R35 historical prefix-schema/fingerprint64hex/datetimefromisoformat 설명 역시 원본 소스와 맞지 않는다.

## 최소 다음 수정 범위

MINIMAL_R37_CORRECTIVE_REQUIREMENTS.json의8개 요구는 Master 검토용이며 새 WP·승인·closure가 아니다. Publisher-only로 raw/snapshot ID·rawcap 바인딩, ASCII date/fullmatch/year, root 포함 direct lstat/타입/오류 failclosed, actual spec/config read bytes/stat provenance, explicit 보호된 writer/TOCTOU 및 hardlink claim, original6 증거, prospective full helper/environment/library graph를 고친다. 기존 strictCLI/exclusive creation/no deletion/원본 opaque 문자열을 유지하고 ALL Engine9/generated/current1.6은 고정한다. 새 exactfreeze·독립static 후 별도 positive6 publication WP가 필요하다.

## QA 도구 오류와 완료 증거

Optional upstream .cases[0] display는 실제 schema가 prospective_cases/pair_cases인 것을 출력한 뒤 null index로 exit1였다. Complete conversation4255b3과 OPTIONAL_DISPLAY_LIMITATION.json에 보존하고 해당 query를 재시도하지 않았다. 원본 전체 JSON을 실제 구조로 읽은 새 metadata 분석은 원래 pin을 사용한다. byte-complete stderr 파일을 발명하지 않았다.

Own review.py의 괄호 하나가 더 있어 Python parse 단계 SyntaxError/exit1, stdout0/stderr745가 발생했다. Body 실행/partial outputs0이다. 최초 source/log/INPUT/TOOL/raw를 변경하지 않고 review_r1.py/newlogger로 문법 한 곳만 고쳤으며 exact diff·새 prospective code/interpreter/input pins/first streams를 보존했다. 마스터에게 실제 오류와 좁은 수정 범위를 직접 보고했다. review_r1 actualexit0/stdout587/stderr0로 의미 출력과 완전한 결과를 확인했다. 실패를 후보 FAIL 또는 테스트 PASS로 바꾸지 않는다.

Own passive metadata successful bootstrap/capture/review_r1/final_prepare/final_seal 및 최초 실패 review의 모든 raw가 봉인 대상이다. QA launcher module pins는 부분적인 read-only 도구 관찰이며 종합적인 child import attestation이라고 주장하지 않는다. Final EM/index/Koreanreport/ACKterminal binding/COMPLETION last atomic, selfcycle·unfinished seal logger·postseal directreturn은 명시 제외하고 실제 numericexit/streams/returned proof를 별도로 보존한다. InitialACK/pendingintent/원본 오류를 수정하지 않는다.

Publisher import/call/publication/Engine/compiler/runner/fixture/native/operator/Process/adverse/rejection0, production modification/build/install0. Master governance/scheduler/dispatch 변경0. High4/Engine002006/Pipeline007/currentSchema/G-Q1/exactPlayerGlobal/physicalsplit OPEN, native/full E2 NOT_RELEASED, Foundation HOLD. Installed incident OPEN/actorUNKNOWN/no restore. DedicatedServer final DomainAuthority, W/L/G/M/one LocalClock writer/island barrier/target publication 유지. Master receipt/disposition/closure PENDING.
