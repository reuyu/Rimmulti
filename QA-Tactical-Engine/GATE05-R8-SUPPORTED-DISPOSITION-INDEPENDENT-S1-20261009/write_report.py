from review_setup import *
def link(n):return '['+n+']('+str(Q/n).replace('\\','/')+')'
if __name__=='__main__':
    report=ROOT/'docs/QA_EngineHost_Gate05_R8_Supported_Disposition_Independent_S1_20261009.md';assert not report.exists() and not (Q/'INDEPENDENT_FINDINGS.md').exists()
    a=load(Q/'ACK.json');c=load(Q/'INDEPENDENT_COVERAGE_INDEX.json');p=load(Q/'PRE_RUN2_MANIFEST.json');ids=load(Q/'R8_LINEAGE.json')['candidates'];src=str(FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs').replace('\\','/');warnings=sum('warning' in x for x in (Q/'BUILD_RAW.txt').read_text(encoding='utf-8-sig').splitlines())
    findings=f'''# R8 independent findings / S1

**정상 codec 의미 회귀 FAIL / fully declared positive helpers PASS / 정적 수정 필요 / native UNTESTED**.
Result {a['result_id']}; 작성 {now()}. WP {a['wp_id']}/S1. Dedicated Server final Domain Authority 및 accepted ADR006B/MD130의 content identity 의미를 유지한다. Master R8-M01~07은 독립 리뷰 입력이며 아래 source/실행 evidence로 판정했다.

| Finding | 독립 판정 | 근거·실질적 제한 |
|---|---|---|
| R8-M01 child observation | CREDITED_STATIC | C2181 assembly,2258/2260 stat,2309/2311 cost,2328 stuff,2343 verb,2363/2365 ThingComp,2403 stage,2418/2420 HediffComp에서 source append 전 명시적 관측 오류. R7 침묵 생략을 개선했다. C2578 ComputeManifest→Validate 및 fingerprint 의존도 유지. Optional collection 부재는 허용하며 실제 native source/오류 경로 실행은0. 전 native type/requiredness/noninterference의 증명은 아님. |
| R8-M02 supported boundary | High revision recommendation | Typed summary/per-mod fields가 serialization에 추가됐지만 Validate C1835~1855는 policy nonempty 및 total>=0,per-mod C1892~1893은nonempty 검사에 그친다. supportedModBoundary는 C2221 construction/C2636 default에만 있고 validator/package selection은 없음. 실제 supported packages/patch/settings material identity 또는 observation disposition을 강제한 증거가 없다. Report의 sum equality claim은 코드에 없고 Normalize C1648이 summary를 재계산해 덮어쓴다. 정책 문자열/카운트 재계산은 actual observation/provenance가 아니다. |
| R8-M03 version meaning | **OBSERVED NORMAL SEMANTIC FAIL / High correction recommendation** | C1597~1603 normalization은 compatibility↔modVersion을 cross-fill. Collector C2168~2169도 compatibility를 양 필드에 기록. 정상 generic optional unknown input(modVersion=null,compatibility=1.6)에 대해 false transport는 null 보존,Normalize/Serialize(true)는modVersion=1.6을 생성. en-US/de-DE 각각45assertions 중41PASS/4FAIL,실제exit1. 네 실패는 하나의root material meaning mismatch이며 requiredness rejection/adverse가아니다. ProducerTC16 cross-fill expected oracle는 채택하지 않음. |
| R8-M04 supported keys/caller | PARTIAL CREDIT / static qualification | Modpackage/loadOrder uniqueness,assembly composite uniqueness 및SHA sort key 개선. Fresh distinct normal composite/secondary names·ordered verbs/stages/comps/multiplicity와positive helper/normal caller mutation은관측. Case/composite representation/multiplicity 및tied material semantics는static-only. Normalization은 ordering 이외versionalias/default labels/summary rewrite도수행하므로 source observation과 구분해야함. Tied/malformed 실행0. |
| R8-M05 collection/type/origin | OPEN / bounded unobserved | 관측한정상65field/DTOwidth·선택string/numeric값은보존. Constructor defaults/list presence/nonempty enum/class strings는observed-empty/required unavailable/native registry/type evidence와같지않음. Legitimate XML-onlymod/optionalabsence를전부거부하라는요구는없음. Actual mod contentversion은compatibility로대체할수없음. |
| R8-M06 whole gate / attribution | OPEN / UNTESTED | Native/provider/cache/operator/worker-validator independent profile/issuer/context/task/staged/atomicpromotion은미승인. Producer 보고서의R7 Sol 전수Def projection PASS 표현은부정확:Sol은pureDTO/helper만실행,actualcollector는staticcredit였다. 기존원문수정0. Engine002006/Pipeline007/currentschema/G-Q1 OPEN,Foundation HOLD. |
| R8-M07 provenance | PARTIAL CREDIT / revision recommendation | Producer21artifacts/18beforeafter/Debug+ReleaseMVID/PDB/sourcegenerated4/4match. Harness four frozen managed references/Steamresolver제거 개선. Placeholder Roslyn C#10+/dependencylabel,pre-run/result run_id 차이,exact finalrunner/source/generated/compiler/framework/loadeddep/config/input/realnumericexit/canonical graph공백이남음. CodeViewpath는native executionproof가아님. QA의새completegraph는Achronology/authority를소급인증하지않음. |

Source SHA **28651CE9461694C5BBA8DC57ECC6D1982329A9BF6775D9FBE420C0FFDCB98D0E**. [Census]({src}:1581),{link('STATIC_CONTRACT_INDEX.json')}에 함수·원문·정확한 line/hash가 있다. {link('NORMAL_SEMANTIC_REGRESSION.json')}에 두 프로세스의 같은FAIL,독립 expected/actual,원문canonical/transport/oracleSHA를결속했다. 생산코드·candidate 수정/재빌드 및기대값을PASS로변경한일은없다.

Producer16PASS raw/JSON IDs·order·count는맞지만 관측범위가다르다. TC01header/count≠65field;TC03familycounts≠actualnativeprojection;TC04FormatLossless scalarformatter≠DTOallbits;TC06은실제로empty stats두목록만검사하고null/missing fixture가없음;TC07verbs/Comp만assert하고stage없음;TC14package/name만assert하고SHA/MVID/stats전체tie아님;TC15fixturepolicy/countserialization≠actualsupportedadmission;TC16은틀린cross-fill을기대값으로삼음. TC11positiveTryAdmit/TC13header는oldR6거부/cache와다르며QAproducer실행0. {link('PRODUCER_COVERAGE_INDEX.json')}에16predicate anchors/범위와TC06의더좁은독립정정을남겼다.
'''
    (Q/'INDEPENDENT_FINDINGS.md').write_text(findings,encoding='utf-8')
    body=f'''# R8 supported disposition 독립 QA S1

**정상 codec 의미 보존 FAIL을 확인했습니다.** Compatibility range와 실제 mod content version이 분리돼야 하는 정상 optional 입력에서 canonical normalization이 `modVersion=null`을 `"1.6"`으로 바꿨습니다. `Serialize(false)`는 null을 보존합니다. 두 culture 프로세스 모두 같은결과와 실제 exit code1을 기록했습니다. Fully declared BASE/revision의 positive ValidateContract/TryAdmit helper는 PASS지만 R8 정상 codec 전체PASS로판정하지않습니다. Native/fullGate E2는미검증입니다.

| Identity / execution | 관측값 |
|---|---|
| WP / revision | {a['wp_id']} / S1 |
| Delivery | {a['delivery_id']} |
| Unique result | {a['result_id']} |
| 작성 시각 | {now()} / Asia/Seoul;final completed_at은COMPLETION.json |
| Selected Debug | {ids[0]['dll_sha256']} / MVID {ids[0]['mvid']} |
| Matching PDB | {ids[0]['pdb_sha256']} |
| New QA runner | SHA {p['runner']['exe_sha256']} / MVID {p['runner']['exe_mvid']} |
| Actual runs | New QA build1;managed process2(en-US/de-DE);각7case/45assertions=41PASS+4FAIL;actual exit1,1 |
| Independent scopes | Historical65/BASE167leaf PASS;fullydeclared Validate2+TryAdmit2case/run PASS;optionalunknownversion1case FAIL |
| Forbidden counts | Production source/candidate/dependency 수정·build0;provider/cache/game/native/operator/oldrunner/rejection/tied/adverse0 |
| Whole gate | FullGate E2 NOT_RELEASED;Engine002006/Pipeline007/currentschema/G-Q1 OPEN;Foundation HOLD |

Immutable [R8 manifest]({str(MAN).replace(chr(92),'/')}) SHA **E7D9096EB7C4A9B074079952D550506C9259F733F64EC1A66FD4DBAA85D16FB4**의75frozen paths만 사용했습니다. Validroot `{FROZEN}`. Alternate Release는metadata-only:SHA{ids[1]['dll_sha256']}/MVID{ids[1]['mvid']}/PDB{ids[1]['pdb_sha256']}. 각CodeView/PDB 및source/generated4/4 checksummatch({link('R8_LINEAGE.json')});Worker/csproj/72547byteprefix도priorR7immutable와맞습니다({link('FIXED_SOURCE_SCOPE.json')}). Managed loader/metadata는승인된frozen4+R8Newtonsoft만사용하고원본Steam/game/mod/UserData/save·mutableSource/bin/obj·oldlongpathpartial에접근하지않았습니다.

새 {link('INPUT_EXPECTED_SEMANTICS.json')}은final build전에작성했습니다. 기존layout은설계참고이고기존runner/PASS승계0입니다. 정상fullydeclared case에는실제contentversion("1.0"/"1.1"등)과compatibility("1.6")를다르게지정했습니다. 별도OPTIONAL_UNKNOWN_VERSION은정상generictransport용선택적unknownversion이며admissionhelper를호출하지않습니다. Expected normalization은정렬만하고unknownactualversion을null로유지합니다. ProducerTC16의cross-fill을기대값에복사하거나결과에맞춰oracle를바꾸지않았습니다. 정상의미FAIL은missing-required/거부/adverse검사가아닙니다.

| Normal version meaning | Input / false transport | Normalize / canonical output | 독립 판정 |
|---|---|---|---|
| compatibilityVersionRange | "1.6" | "1.6" | 정상 보존 |
| actual modVersion | null(unknown) | "1.6" | **FAIL:content version 새생성** |

네FAIL predicates는NORMALIZE_OPTIONAL_UNKNOWN_VERSION_SEMANTICS,NORMAL_OPTIONAL_UNKNOWN_VERSION_SEMANTICS,CANONICAL_OPTIONAL_UNKNOWN_VERSION_NORMALIZE,C_VERSION_OPTIONAL_UNKNOWN입니다. 한rootsemantic결함을네관측단계에서확인한것이지서로다른네결함이아닙니다. Raw {link('RUN1_RAW.txt')}/{link('RUN2_RAW.txt')},actual numeric {link('RUN1_TOOL_PROOF.json')}/{link('RUN2_TOOL_PROOF.json')},정상 {link('OPTIONAL_UNKNOWN_VERSION.transport.json')}/{link('OPTIONAL_UNKNOWN_VERSION.canonical.json')}/{link('OPTIONAL_UNKNOWN_VERSION.semantic_checks.json')}/{link('NORMAL_SEMANTIC_REGRESSION.json')}을그대로보존했습니다. 결과파일은끝까지작성했고semanticFAIL을runnerexit1로반영했습니다.

나머지관측범위는역사65leaf/currentDTO Single/Int32/Int64/string/bool/List,Unicode/quotes/backslash/공백/tab/newline/literal '(null)',선택finiteFloat32bit/Int32/Int64 9007199254740993,legitimateoptionalnull/empty/missingconstructor defaults,orderedmodloadOrder/verbs/stages/Compmultiplicity,정상uniqueunorderedsetpermutation,두normalrevision/reconstruction입니다. 여섯canonicalsemanticcase는PASS이며모든일곱false-transportcase는PASS입니다. FullydeclaredBASE/revisionhelpers각2case/run은true/emptyreason/expectedsemantics+canonicalbytes일치입니다. Candidate의잘못된unknownversion결과도두culture에서동일bytes지만,determinism은그meaningFAIL을PASS로바꾸지않습니다. Codec7pair(그중1semanticFAIL)와admitted2pair의byteidentity를따로표시했습니다({link('INDEPENDENT_COVERAGE_INDEX.json')}).

R8childsourceobservation오류및modpackage/loadOrder/assemblycompositekey검사는정적으로개선됐습니다. 그러나supportedModBoundary는construction/default에만있고실제package선택/validator검사없음,policy문자열nonempty와카운트만으로필수patch/settingssupporteddisposition을강제하지못합니다. Summarysum검증은보고서claim과달리없고normalizer가재계산값으로덮어씁니다. 정상정렬/callermutation과이sourceclaim/default/alias변경을구분했습니다. Collection/type/nativeorigin및전면keypolicy는여전히미증명이며blanketallmod/allnull/allDef거부나새globalschema를요구하지않습니다. {link('INDEPENDENT_FINDINGS.md')}/{link('STATIC_CONTRACT_INDEX.json')}에R8-M01~07의독립판정과sourceanchors가있습니다.

Producer16PASS는원문과JSON순서/ID/countmatch입니다. 실제TC01은header/count,TC03은familycount,TC04는formatter샘플,TC06은empty두목록만,TC07은verb/Comp만,TC14는assembly보조키만,TC15는fixture정책/카운트serialization,TC16은잘못된versioncross-fillassertion입니다. R7Sol이실제Defprojection을통과했다는producer문장은채택하지않습니다. Sol은pureDTO/helper만실행했습니다. {link('PRODUCER_COVERAGE_INDEX.json')}/{link('PRODUCER_PACKAGING_INDEX.json')}. Producer21artifacts/18beforeafter/actualDebug+ReleaseMVID/PDB및승인frozenmanaged4참조개선은확인했지만compilerplaceholder/exactrunner/input/loadedgraph/numericexit/canonicalartifact공백과pre/result run_id차이는남습니다. Producerbinary실행·원문수정0,새QAgraph로producerchronology를소급인증하지않습니다.

Fresh final QA build→pre→normalprocess→postgraph는{link('Program.cs')}/{link('TOOLCHAIN_OBSERVED.json')},BUILD_RAW/BUILD_TOOL_PROOF,{link('PRE_RUN1_MANIFEST.json')}/{link('PRE_RUN2_MANIFEST.json')},RAW·TOOL_PROOF,{link('POST_RUN1_IDENTITY.json')}/{link('POST_RUN2_IDENTITY.json')}에결속했습니다. ObservedSDK10.0.201/Roslyn5.3.0-2.26153.122/net472refs/CLR4.0.30319.42000;각106pre/postinputsSHA·sizeunchanged,runnerPDBsource1checksummatch,모든실제loadedmanagedhash가pre-pin과일치({link('ACTUAL_LOADED_PREPIN_BINDING.json')}). QA buildexit0/warnings{warnings}raw보존;positive normalrun의semanticexit1을정상기록했습니다. RUN1_ARCHIVE는첫새R8의completeevidence이며실패를폐기하거나provisional로대체하지않았습니다. 후보/runner/oracle재빌드·수정후PASS만들기를하지않았습니다.

Masterbaseline2944uniqueprotectedpath의actualSHA·size를전후확인합니다(PRESERVATION_BEFORE/AFTER);R8frozen75/prior954/archive19/Pipeline206/QA1652/managed4및manifest·terminalbinding을보존합니다. InstalledincidentOPEN/actorUNKNOWN이며원본재독취/restore/정상화0. 최종EVIDENCE_MANIFEST/RESULT_INDEX/ACK_COMPLETION_BINDING/COMPLETION이보고서·증거를연결하고directMaster1회return은별도RETURN_TOOL_PROOF/DELIVERY_STATUS에기록합니다. QA완료와normaltestFAIL은구분하며closure/release는Master판단,FoundationHOLD입니다.
'''
    report.write_text(body,encoding='utf-8');print(json.dumps(dict(report_path=str(report),report_sha256=sha(report),verdict=c['verdict']),indent=2))
