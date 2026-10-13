from review_setup import *

def link(name):return '['+name+']('+str(Q/name).replace('\\','/')+')'
if __name__=='__main__':
    report=ROOT/'docs/QA_EngineHost_Gate05_R7_Content_Admission_Independent_S1_20261008.md';assert not report.exists() and not (Q/'INDEPENDENT_FINDINGS.md').exists()
    a=load(Q/'ACK.json');s=load(Q/'STATIC_CONTRACT_INDEX.json');c=load(Q/'INDEPENDENT_COVERAGE_INDEX.json');p=load(Q/'PRE_RUN2_MANIFEST.json');ids=load(Q/'R7_LINEAGE.json')['candidates'];src=str(FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs').replace('\\','/')
    findings=f'''# R7 independent findings / S1

Result {a['result_id']}; 작성 {now()}. 판정 **SCOPED_R7_POSITIVE_CODEC_ADMISSION_HELPER_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED**.
Controlling MD130/accepted ADR006B/SRS와 실제 frozen source를 대조했다. Master R7-M01~07의 개선 인정/잔여 revision 필요에 동의하며,현재 관측 범위는 아래와 같다. 이전 R6 PASS는 새 후보 PASS로 승계하지 않았다.

| Review | 독립 확인·판정 | source/evidence·실질적 제한 |
|---|---|---|
| R7-M01 linkage | **CREDITED_STATIC / positive helper PASS** | ComputeActualManifest C1976/2433에서 ValidateContract 호출 후 반환,ComputeFingerprint C2441은 그 계산 뒤 serialization. TryAdmit C1965는 같은 validator+canonical serialization만 호출. R6 definition-only 결함은 정적으로 수정됨. QA positive2case/run에서 true/empty reason/독립 expected semantics 및 canonical bytes 확인. 실제 collector/loaded-profile/cache 경로는 실행하지 않음. |
| R7-M02 coverage binding | **PARTIAL CREDIT / High revision recommendation** | C1536~1538/C1738~1767/C2637:contentContractVersion/supportedCoverageProfile/modPatchSupportStatus가 DTO에 포함되고 직렬화·동등 비교됨. R6 constant-only와 달리 표현 결속 개선은 실제로 있음. 그러나 COUNT_ONLY_EXPLICIT_EXCLUSION_RAW_PATCHES_SETTINGS equality와 C2058 patchCount만으로 실제 mod/patch/settings의 supported disposition을 강제하지 않음. Required material identity 또는 좁은 실제 supported-profile selection/typed disposition이 필요. 문서 제외/모든 profile 비활성화/complete mod compatibility 선언은 해법으로 채택하지 않음. |
| R7-M03 collector disposition | **PARTIAL CREDIT / High revision recommendation** | C2074 null assembly continue,2138stats/2184cost/2200stuff/2212verbs/2227comps/2262stages/2276Hediff comps 필터가 원소를 생략. Validator는 이미 생략된 source material을 복원하지 못함. Optional collection 부재와 collection 내 required identity/reference 관측 실패를 구분해야 함. Hediff/Job class empty는 새 validator가 downstream에서 검사하므로 그 좁은 개선은 인정. Legitimate optional null/empty 및 명시된 정상화를 무조건 실패로 만들지 않음. |
| R7-M04 requiredness/type/inventory | **PARTIAL CREDIT / High remaining** | C1728~1958:header/nonempty strings,capability inclusion,DLC/Def unique names,일부 children 검사 추가. 목록 존재/constructor default는 observed-empty 대 unavailable 구분이 아님. Collector DLC/activeMods는 empty 오류지만 Def families는 null만 오류;명시된 지원 정책/관측 상태가 필요. C2064~2065의 modVersion은 SupportedVersionsReadOnly compatibility range이며 실제 mod content version 아님. Enum/class strings는 nonempty이며 native registry/정상 enum membership·numeric observation/presence는 인증되지 않음. New positive input의 synthetic class/core metadata를 native authority로 사용하지 않음. |
| R7-M05 keys/caller | **CREDITED_NORMAL / static qualification** | C1580~1696:assembly(packageId,name,MVID),stat(name,value),cost(name,count),mod(loadOrder,packageId) comparator와 report caller in-place declaration 개선. Fresh normal unique composite keys/secondary assembly names와 permutation byte equality 관측. Mod loadOrder/package uniqueness,assembly composite/multiplicity 및 comparator-identical remaining material policy는 충분히 선언·검사되지 않음. Tied/malformed 입력 실행0. Ordered verbs/stages/comps/multiplicity 유지;material noninterference 또는 모든 float bit 증명 아님. Normalize/Serialize(true)/TryAdmit의 같은 DTO list mutation을 정상 입력에서 실제 기록함. |
| R7-M06 whole-gate/native | **OPEN / UNTESTED** | WorkerBridge/csproj/Census prefix는 immutable. MD125~129 issuer/context/target/task/result/receipt/native/exact staged bytes/atomic promotion 및 실제 worker-validator profile 독립 관측은 이 codec WP에서 미승인·미검증. Dedicated Server final Domain Authority;Master governance disposition. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. |
| R7-M07 packaging/claims | **PARTIAL CREDIT / provenance revision recommendation** | Producer21 artifacts/18before-after/Debug+Release MVID/PDB/generated-source4/4 match. Generator의 datetime.now와 실제 SDK query는 R6 hardcoded time/SDK8.0+보다 개선. Timestamp text 순서는 일관되지만 compiler/framework/runner/input/oracle/resolved dependency/actual numeric exit/canonical evidence graph는 미완성. Producer resolver에는 원본 Steam 경로 존재;QA는 그 경로를 사용하지 않음. 새 QA evidence로 producer execution chronology/authority를 소급 인증하지 않음. |

원문 source SHA **D980225D8DBE04F9CAE95AD100DCF6640252A24A14599346E3B7F81CA8B9AF98**. Exact function/line/SHA,child filtering 원문은 {link('STATIC_CONTRACT_INDEX.json')}에 있다. Source [Census]({src}:1728),normal oracle/coverage/raw는 같은 QA root에 별도 저장했다.

Producer14 labels는 normal codec11+positive helpers2+header metadata1의 범위다. TC11은 새 R7 positive TryAdmit,TC13은 새 R7 header/flags이며 과거 R6 rejection/cache와 다르다. Inspected Main에 provider/cache 호출 없음;producer runner 실행0. TC03 family count/substrings는65decoded oracle 아님,TC04 numeric equality는모든bit/signed-zero 아님,TC06explicit null/empty는missing input 관측 아님,TC12scalar change는general collision-resistance 아님,TC14는assembly package/name 보조 키만 assert하며stats/MVID tertiary key는assert하지 않음. json.Length의3482는UTF16 code-unit count이며UTF8 byte size가 아님. {link('PRODUCER_COVERAGE_INDEX.json')}에14실제source predicate anchors/raw JSON ID·order match를 기록했다.
'''
    (Q/'INDEPENDENT_FINDINGS.md').write_text(findings,encoding='utf-8')
    body=f'''# R7 content admission 독립 QA S1

**관측한 정상 codec·positive admission helper 범위 PASS / 정적 계약 수정 필요 / native UNTESTED**. 새 후보의 실제 validator linkage와3개 contract field binding 개선을 정적으로 인정한다. 정상 synthetic6case를 en-US/de-DE의 새 process2에서 실행해 각27assertion·대표65field·BASE157leaf를 확인했다. Positive ValidateContract와 TryAdmitManifest 각각2case/run이 true/empty reason이며 admission JSON이 독립 지정한 정상 semantics와 canonical bytes에 맞았다. Actual loaded content/프로필 authority/full Gate05 E2는 미검증이다.

| Identity / execution | 관측값 |
|---|---|
| WP / revision | {a['wp_id']} / S1 |
| Delivery | {a['delivery_id']} |
| Unique result | {a['result_id']} |
| 작성 시각 | {now()} / Asia/Seoul;최종 completed_at은 COMPLETION.json |
| Selected Debug | {ids[0]['dll_sha256']} / MVID {ids[0]['mvid']} |
| Matching Debug PDB | {ids[0]['pdb_sha256']} |
| New QA runner | SHA {p['runner']['exe_sha256']} / MVID {p['runner']['exe_mvid']} |
| Actual counts | QA build1 / positive managed runs2 / 각27PASS / real tool exit0,0 |
| Toolchain | observed SDK10.0.201/Roslyn5.3.0-2.26153.122/net472 refs/CLR4.0.30319.42000 |
| Forbidden counts | Production modification/build0;provider/compute/getter/cache/game/native/operator/old A·QA runner/rejection/adverse0 |
| Gate | Full runtime E2 NOT_RELEASED;Engine002006/Pipeline007/current schema/G-Q1 OPEN;Foundation HOLD |

Immutable [freeze manifest]({str(MAN).replace(chr(92),'/')}) SHA **DE49655C30976C254F59B022C7DD768806B90EB6F566055936B05EAFFE3F13CF**의110 frozen_path만 후보로 사용했다. Valid root는 `{FROZEN}`. Additional managed loader/metadata는 승인된 frozen4 manifest SHA7FCB91EE…와R7frozen Newtonsoft.Json이며 원본 Steam/game/mod/UserData/save나 mutable Source/bin/obj·old long-path partial은 사용하지 않았다. Alternate Release는 metadata-only:SHA {ids[1]['dll_sha256']}/MVID {ids[1]['mvid']}/PDB {ids[1]['pdb_sha256']}. 각CodeView/portable PDB/generated+source document4/4가 frozen byte checksum과 맞는다({link('R7_LINEAGE.json')}). Worker/csproj 및72547byteprefix도R6 immutable와 일치한다({link('FIXED_SOURCE_SCOPE.json')}).

{link('INPUT_EXPECTED_SEMANTICS.json')}의 새 R7 input/expected normalization을 final build 전에 작성했다. 역사 input layout/mapping은 설계 참고이며 prior runner binary/PASS 실행·승계0.3개R7contract fields/정상 required class/category/enum strings를 지정했다. 기대값은 production output으로 만들지 않았다. Mod declared loadOrder,ordinal normal unique keys와 assembly secondary names의 예상 순서를 별도 지정했고 verbs/stages/comps/multiplicity는 유지했다. JSON property order/숫자 lexical 표현을 독립 byte oracle로 전수 인증했다는 주장은 하지 않으며,typed semantic oracle와 저장된 canonical byte reconstruction/culture determinism을 구분한다.

| 독립 정상 관측 | 결과·제한 |
|---|---|
| Representative fields | Historical65leaf·current DTO Single/Int32/Int64/string/bool/List metadata 및BASE157 expected leaves PASS |
| String/number | Unicode/quotes/backslash/공백/tab/newline/literal '(null)',선택 finiteFloat32 exact bits·integer·Int64 9007199254740993 보존;모든bit/all-content 인증 아님 |
| Optional generic transport | 정상 explicit null/empty 구분,optional missing→constructor null/empty default 관측;missing-required/unavailable material 인증 아님 |
| Canonical / false transport | Normalize/Serialize(true) 정상 unordered permutation 동일bytes;false supplied order/typed values 유지 |
| Ordered data | Declared modloadOrder 및verbs/stages/comps 순서·Comp multiplicity 유지;actual native material noninterference 미관측 |
| Positive Validate/TryAdmit | BASE/NORMAL_REVISION_B 각각true/empty reason;admission JSON의expected semantics/canonical equality/UTF8 bytes·SHA 기록 |
| Caller mutation | Normalize/Serialize(true)/TryAdmit의same DTO before/after list change를실제기록;report의in-place 선언과 일치 |
| Fresh process/culture | Codec6canonical pairs와admitted2pairs가en-US/de-DE byte equality;같은final build 사용 |
| Normal revisions | 두 정상 scalar/version content revision의bytes/digest 변화;general collision-resistance 증명 아님 |
| Static-only | Tied keys/unsupported/rejection/missing-required/native/cache/provider/operator 실행0,UNOBSERVED/STATIC/UNTESTED |

Raw canonical UTF8/false transport/decoded semantics/expected checks/digests와positive admission checks·before/after observation을 case별 보존했다. {link('FIELD_COVERAGE_INDEX.json')}와{link('INDEPENDENT_COVERAGE_INDEX.json')}는 실제관측·미관측을구분한다. Native Job damage/food preference enum metadata는허용된managed copy에서읽었지만 모든upstream type name/enum/class identity/admission을인증하지않는다. Synthetic core/version/class strings는actual trusted inventory가아니다.

{link('INDEPENDENT_FINDINGS.md')}의R7-M01~07이Master findings와독립source/evidence 대조를담는다. R6unwired helper는수정됐고 R7serialized/validated contract fields binding도개선됐다. 잔여핵심은actual patch/settings support enforcement,source child filtering을앞서는required/optional/unknown/unavailable disposition,observed-empty inventory 상태,modVersion의compatibility-range 의미,완전한supportedkey/multiplicity정책이다. Blanket every-null/all-Def rejection이나새globalschema를요구하지않는다. Whole-gateissuer/native/operator는별도후속범위다.

Producer14raw/JSON PASS IDs·order·countmatch. R7TC11positiveTryAdmit와TC13headerflag는oldR6거부/cache와구분했다. TC03/04/06/12/14의실제predicate범위를각각65leaf/all-bit/missing/collision/fulltieclaim과분리했다. `json.Length bytes`는UTF16 length다. Producer21artifacts·18beforeafter·actualDebug/ReleaseMVID/PDB개선과dynamic timestamp/SDKquery를인정하지만producerlast-build/compiler/framework/loadeddep/runner/oracle/canonical/numericexitgraph는미완성이다. {link('PRODUCER_COVERAGE_INDEX.json')}/{link('PRODUCER_PACKAGING_INDEX.json')}. Producerrunner실행·원문수정0이며QA증거로producerchronology를소급인증하지않는다.

Final QA build→pre-run→positive process→post-rungraph는{link('Program.cs')},{link('TOOLCHAIN_OBSERVED.json')},BUILD_RAW/BUILD_TOOL_PROOF,{link('PRE_RUN1_MANIFEST.json')}/{link('PRE_RUN2_MANIFEST.json')},RUN1/2RAW·TOOL_PROOF,{link('POST_RUN1_IDENTITY.json')}/{link('POST_RUN2_IDENTITY.json')}에있다. 각141pre/postinputhash·sizeunchanged,runnerPDB1sourcechecksum/actualMVID결속. {link('ACTUAL_LOADED_PREPIN_BINDING.json')}의모든실제loadedmanagedSHA가pre-pin과맞았다. RUN1_ARCHIVE는첫freshR7의completecaseevidence를보존한것이며incomplete/provisional/oldR6결과가아니다. Buildwarnings25는raw보존,actualcompilerexit0. 추가test실행불필요.

Masterbaseline2701uniqueprotectedpath를전후SHA·size로확인한다(PRESERVATION_BEFORE/AFTER). R7frozen110/prior844/archive19/Pipeline206/QA1489/managed4및manifest·terminalbinding을보존한다. 기존externalinstalledincidentOPEN/actorUNKNOWN은변경·재독취·restore·정상화0. 최종EVIDENCE_MANIFEST/RESULT_INDEX/ACK_COMPLETION_BINDING/COMPLETION으로보고서·산출물을연결하고,directMaster1회return은별도RETURN_TOOL_PROOF/DELIVERY_STATUS에저장한다. Masterdisposition과freshnativegate가없으므로FoundationHOLD다.
'''
    report.write_text(body,encoding='utf-8');print(json.dumps(dict(report_path=str(report),report_sha256=sha(report),findings_sha256=sha(Q/'INDEPENDENT_FINDINGS.md')),indent=2))
