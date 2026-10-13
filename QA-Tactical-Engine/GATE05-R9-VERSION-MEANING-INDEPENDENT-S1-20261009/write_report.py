from review_setup import *
def link(n):return '['+n+']('+str(Q/n).replace('\\','/')+')'
if __name__=='__main__':
    report=ROOT/'docs/QA_EngineHost_Gate05_R9_Version_Meaning_Independent_S1_20261009.md';assert not report.exists() and not (Q/'INDEPENDENT_FINDINGS.md').exists()
    a=load(Q/'ACK.json');p=load(Q/'PRE_RUN2_MANIFEST.json');ids=load(Q/'R9_LINEAGE.json')['candidates'];c=load(Q/'INDEPENDENT_COVERAGE_INDEX.json');src=str(FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs').replace('\\','/')
    findings=f'''# R9 independent targeted findings / S1

**정상 버전 의미 targeted regression PASS / fully declared helpers PASS / native UNTESTED / fullGate NOT_RELEASED**.
Result {a['result_id']}; 작성 {now()}. Defect ENGINE-CONTENT-VERSION-SEMANTIC-20261009-01의 한 가지 회귀를 검증했다. Closure는 Master disposition이 필요하다.

| Finding | 독립 판정 | 증거와 제한 |
|---|---|---|
| R9-M01 narrow source repair | CREDITED_STATIC | Frozen R8↔R9 전체 normalized text diff가 두 cross-fill 분기 제거,collector modVersion=compatRange→null 및contract/capability/comment R9 binding만으로 일치한다. Worker/csproj/72547byte prefix는byte-identical. 기존child/key/order/patch/settings의다른행동은변경없음. {link('SOURCE_SCOPE_DIFF.txt')}/{link('FIXED_SOURCE_SCOPE.json')}. |
| R9-M02 version semantics | **TARGETED INDEPENDENT PASS** | Compatibility와actualcontentversion을독립기대값으로지정. Null·empty·known-distinct·reverseblankcompatibility·genericUnicode/whitespace·optionalmissingdefault 6case를각5view에서검증. Fresh original Serialize(true)를explicitNormalize instance와별도로검사했다. en-US/de-DE 각각12normalcase/88assertions PASS,actualexit0/0. Actualcollector nullassignment는staticcredit이며native actualversionavailability/requiredness proof는아님. |
| R9-M03 E1 predicates | CREDITED_WITH_PRECISE_SCOPE | Producer16raw/JSONID·order·countmatch. TC16의correctedunknown/known/reverse기대값은인정되지만cultureloop는sameprocess이고trueSerialize는explicitNormalize후객체를사용한다. 독립QA는freshoriginaltrue/process/culturegraph를추가했다. TC01은reconstruction text/SHA equality,TC02는3회serialization(100회아님),TC04는DTOStat값3개를tolerance로비교(FormatLosslessformatter검사가아님),TC05sameprocessculture+Korean substring. Masterreview의formatter범위표현은실제R9source에따라더정확히분류했다. TC06empty-only/TC07stage미assert/TC14fulltie미assert/TC15supportedprofile미관측은유지. {link('PRODUCER_COVERAGE_INDEX.json')}. |
| R9-M04 packaging | PARTIAL CREDIT / separate limitation | Producer21artifacts/18beforeafter/actualDebug·ReleaseMVID/PDBsourcegenerated4/4match. Exactrunner/compiler/framework/resolveddeps/config/argv/cwd/inputoracle/canonical/numerictoolgraph는불완전하며pre/result run_id다름. 새QA는자신의completegraph를prospective하게기록했고producerchronology를소급인증하지않음. {link('PRODUCER_PACKAGING_INDEX.json')}. |

Source SHA **BBB1343E4C9084276296DD9CC4C517AC44E02426064BC9C314E1D261167AB2AB**. [Normalize]({src}:1581),[Serialize]({src}:1728),[TryAdmit]({src}:2054),[collector unknown assignment]({src}:2161). 실제provider/cache/game/native/operator/oldrunner/rejection/tied/adverse실행0,production수정·build0.

R8의진짜FAIL/oracle/runner/원문은그대로보호했고재실행하지않았다. 신규targetedPASS는R8FAIL을덮어쓰지않으며R5~R7PASS승계도없다. Patch/settingssupportedboundary/defaultsource/type/key/native/operator등다른OPEN항목을이단일회귀의수용시험으로재묶지않는다. DedicatedServer final runtime DomainAuthority,Master governance/release/closure disposition. Engine002006/Pipeline007/currentschema/G-Q1 OPEN,FoundationHOLD.
'''
    (Q/'INDEPENDENT_FINDINGS.md').write_text(findings,encoding='utf-8')
    body=f'''# R9 version meaning 독립 targeted QA S1

**R8의 정상 버전 의미 회귀가 새 R9 후보에서 수정됐음을 관측 범위 내 확인했습니다.** Unknown/null/empty actual modVersion과 compatibility range가 서로 추론되지 않고 보존됐습니다. Fresh 원본 `Serialize(true)`와 explicit `CanonicalNormalize` 후 경로를 별도로 검증했습니다. 두 fresh process(en-US/de-DE)가 각각88assertions를통과했고actualexit0/0입니다. Targeted PASS와positivehelper PASS는native/fullGate검증을뜻하지않으며Highdefectclosure는Master판단입니다.

| Identity / execution | 관측값 |
|---|---|
| WP / revision | {a['wp_id']} / S1 |
| Delivery | {a['delivery_id']} |
| Unique result | {a['result_id']} |
| 작성 시각 | {now()} / Asia/Seoul;최종completed_at은COMPLETION.json |
| Selected Debug | {ids[0]['dll_sha256']} / MVID {ids[0]['mvid']} |
| Matching PDB | {ids[0]['pdb_sha256']} |
| New QA runner | SHA {p['runner']['exe_sha256']} / MVID {p['runner']['exe_mvid']} |
| Actual QA counts | Newrunnerbuild1 / process2 / 각12normalcase·6targetedcase·88PASS·0FAIL;actualexit0,0 |
| Retained controls | Historical65/BASE167leaf;positiveValidate2+TryAdmit2case/run PASS |
| Forbidden counts | Production수정·rebuild0;provider/cache/game/native/operator/oldrunner/rejection/tied/adverse0 |
| Whole gate | NativeUNTESTED/fullGateE2NOT_RELEASED;Engine002006/Pipeline007/currentschema/G-Q1OPEN;FoundationHOLD |

Exact [manifest72]({str(MAN).replace(chr(92),'/')}) SHA **F3130B707E0B99690E6E724654EE794C61BBADFD34F8F9C07297C4AB481BD193**의frozen_path만후보로사용했습니다. Validroot `{FROZEN}`. AlternateRelease는metadata-only:SHA{ids[1]['dll_sha256']}/MVID{ids[1]['mvid']}/PDB{ids[1]['pdb_sha256']}. Debug/ReleaseCodeView/PDB/sourcegenerated4/4match는{link('R9_LINEAGE.json')},fixedWorker/csproj/prefix·단일수정diff는{link('FIXED_SOURCE_SCOPE.json')}에있습니다. 승인된frozenmanaged4+후보Newtonsoft만loader/metadata로사용했고originalSteam/UserData/save/gamecontent초기화는0입니다.

새 {link('INPUT_EXPECTED_SEMANTICS.json')}에build/run전독립expectedsemantics를작성했습니다. OriginalR8oracle를rationale로연결하되oldrunner/PASS를실행·승계하지않았습니다. Materialvalues는정렬이외바뀌지않고,optionalactualversion이없으면constructordefaultnull,empty는empty,declaredknownstring은그대로라는기대값입니다. Productionoutput을oracle로역생성하거나결과에맞춰고치지않았습니다.

| Targeted normal case | 독립 기대값 | 결과 |
|---|---|---|
| Optional unknown | compatibility="1.6",actualversion=null | PASS:null 유지 |
| Known distinct | compatibility="1.5;1.6",actualversion="2.1.0" | PASS:별도값 유지 |
| Reverse inference | compatibility="",actualversion="2.1.0" | PASS:compatibility empty 유지 |
| Optional empty version | compatibility="1.6",actualversion="" | PASS:empty와null 구분 |
| Generic version text | 별도Unicode/구두점/공백/tab/newline strings | PASS:genericDTO값 보존 |
| Optional missing actual version | suppliedfield없음,constructoractualversion=null | PASS:null정상default;wirepresence보존인증은아님 |

각targetcase는false-transport,explicitNormalize상태,freshoriginaltrue,canonicaldecoded,reconstructedrepeat의5view를independentexpectedversionrows와비교했습니다. 모든12normalcase의freshoriginaltrue전체semantics도Normalize보다먼저독립instance에서검사했습니다. {link('TARGETED_VERSION_RESULTS.json')}/{link('TARGETED_REGRESSION_INDEX.json')}와case별version_checks/fresh_original_checks/transport/decoded/canonical/digest가원문입니다. Optionalgenericcases를required-profilehelper에보내지않았고positivehelpers는fullydeclaredBASE/revision2case만사용했습니다.

Compactregression은65representativefields/currentSingle·Int32·Int64·string·bool·List,finiteFloat32bits/largeInt64 9007199254740993/Unicode/escapes/literal '(null)'/optionalnull-empty-default/orderedmods·verbs·stages·Compmultiplicity/normaldistinctsetpermutation/두revision을유지했습니다({link('FIELD_COVERAGE_INDEX.json')}). Canonical12pairs,fresh-original12pairs,admitted2pairs가두culture에서동일UTF8bytes이며freshoriginal과Normalize후bytes도일치합니다. Bytesame만으로meaning을판정하지않고먼저typedsemanticoracle를통과했습니다({link('INDEPENDENT_COVERAGE_INDEX.json')}). 모든floatbit/allnativecontent/registry/unknownrequiredsupport/generaldigestcollision/tie정책은인증하지않습니다.

Source[Normalize]({src}:1581)의양방향cross-fill제거와collector[modVersion=null]({src}:2161)은정적으로확인했습니다. 전체R8↔R9normalizedtext는해당수정과R9contract/capability/comments외변화가없었습니다. Childobservation/key/order/patchsettings의다른행동은그대로입니다. Actualcollector/nativeprofile는실행하지않았습니다. Source/nativeorigin/patchsettingssupportedboundary/defaults/type/key/operator등별도OPENgate는이번단일회귀의targetedPASS로닫지않습니다. {link('INDEPENDENT_FINDINGS.md')}/{link('STATIC_TARGETED_REVIEW.json')}.

ProducerTC16의수정된unknown/known/reverse기대값과16raw/JSONPASSID·order·count는확인했습니다. 문화권loop는sameprocess이며trueSerialize가pre-normalizedobject를사용하므로독립QA의freshoriginaltrue증거와구분합니다. 실제R9TC01은canonicalreconstructiontext/SHA,TC02는3serializations,TC04는3DTOStatfloat의tolerance검사이며formatter가아닙니다. TC06empty-only/TC07stage미검사/TC14전체tie미검사/TC15actualsupportedadmission미검사도정확히한정했습니다({link('PRODUCER_COVERAGE_INDEX.json')}). Producer21artifact/18beforeafter/MVID/PDB는match지만Roslynplaceholder/exactrunner/input/dependency/numericexit/chronologygraph공백은미완성입니다. Raw16PASS나새QA로소급인증하지않습니다({link('PRODUCER_PACKAGING_INDEX.json')}). QA-onlymetadatareader는R9freeze의absolute-patharray형식에맞춰수정했고candidate재실행없이분류를완료했습니다(METADATA_FORMAT_ADAPTATION.json).

Fresh finalbuild→pre→normalprocess→postgraph는{link('Program.cs')}/{link('TOOLCHAIN_OBSERVED.json')},BUILD_RAW/BUILD_TOOL_PROOF,{link('PRE_RUN1_MANIFEST.json')}/{link('PRE_RUN2_MANIFEST.json')},RUN1/2RAW·TOOL_PROOF,{link('POST_RUN1_IDENTITY.json')}/{link('POST_RUN2_IDENTITY.json')}에있습니다. ObservedSDK10.0.201/Roslyn5.3.0-2.26153.122/net472refs/CLR4.0.30319.42000. 각103pre/postinputSHA·size동일,runnerPDBsource1checksum/actualMVID결속,actualloadedmanagedSHA모두pre-pinmatch({link('ACTUAL_LOADED_PREPIN_BINDING.json')}). RUN1_ARCHIVE는첫completefreshR9process의원문이며oldR8결과를대체하지않습니다. 추가production수정·재빌드·oldrunner실행은하지않았습니다.

Masterbaseline3206uniqueprotectedpaths의전후actualSHA·size를검증합니다(PRESERVATION_BEFORE/AFTER);R9frozen72/prior1029/archive19/Pipeline206/QA1834/managed4및manifest·terminalbinding을보존합니다. OriginalR8FAIL/oracle/runnerbyte는그대로이고installedincidentOPEN/actorUNKNOWN에재독취/restore/정상화0입니다. FinalEVIDENCE_MANIFEST/RESULT_INDEX/ACK_COMPLETION_BINDING/COMPLETION이보고서·evidence를결속하고directMaster1회return은별도RETURN_TOOL_PROOF/DELIVERY_STATUS에기록합니다. Narrowtargetdisposition만Master에요청하며FoundationHOLD를유지합니다.
'''
    report.write_text(body,encoding='utf-8');print(json.dumps(dict(report_path=str(report),report_sha256=sha(report),target_verdict=c['target_regression']),indent=2))
