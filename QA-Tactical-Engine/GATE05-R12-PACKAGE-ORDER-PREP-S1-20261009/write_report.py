from review_setup import *

if __name__=='__main__':
    assert not REPORT.exists();ack=load(Q/'ACK.json');o=load(Q/'NORMAL_ORDER_REFERENCE_ORACLE.json');n=load(Q/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json');s=load(Q/'STATIC_REVIEW_CRITERIA.json');f=load(Q/'FROZEN_R11_FIELD_AND_CALLSITE_MATRIX.json')
    def link(name):return '['+name+']('+str(Q/name).replace('\\','/')+')'
    for name,title,d,columns in [('POSITIVE_NORMAL_ACCEPTANCE_MATRIX.md','R12 normal acceptance preparation',n,['id','topic','fixture','exact_expected_assertion']),('STATIC_REVIEW_CRITERIA.md','R12 defensive static preparation',s,['id','topic','predicate']),('FROZEN_R11_FIELD_AND_CALLSITE_MATRIX.md','Frozen R11 source anchors',f,['concept','first_line','last_line'])]:
        (Q/name).write_text('# '+title+'\n\nPreparation only;no R12 candidate observation/execution.\n\n|'+'|'.join(columns)+'|\n|'+'|'.join('---' for _ in columns)+'|\n'+'\n'.join('|'+'|'.join(str(r[c]).replace('|','\\|') for c in columns)+'|' for r in d['rows'])+'\n',encoding='utf-8')
    steps=load(Q/'FRESH_ORIGINAL_BINDING_CONTROL_PLAN.json')['steps'];(Q/'FRESH_ORIGINAL_BINDING_CONTROL_PLAN.md').write_text('# Prospective fresh-original policy binding views\n\n'+'\n\n'.join(str(i+1)+'. '+step for i,step in enumerate(steps))+'\n',encoding='utf-8')
    relation_table='\n'.join('|'+r['left']+' / '+r['right']+'|'+r['relation']+'|'+str(r['reference_policy_digest_equal'])+'|'+str(r['reference_full_content_semantics_equal'])+'|' for r in o['relations'])
    text=f'''# R12 package order 독립 QA 준비 S1

**읽기 전용 준비 완료. R12 후보는 NOT_REVIEWED이며 controls/build/run/assembly load는 0입니다.** 정상 reference 사례14개,정상 acceptance14개,정적 리뷰14개,동결R11 source anchors10개와JSON reference70개를 작성했습니다. Expected execution sequence와raw physical array 및loadOrder의의미를 분리했고 package-version 연결과caller mutation 기대값을 명시했습니다.

|Identity / scope|값|
|---|---|
|WP / revision|{ack['wp_id']} / S1|
|Delivery|{ack['delivery_id']}|
|Unique result|{ack['result_id']}|
|작성 시각|{now()} / Asia/Seoul;최종 시각은 COMPLETION.completed_at|
|동결 reference|G05R11-bec3d350/manifest74 SHA79151763B710FE37E59148E272C1C7BC6C3D606D275B5215AF4174187C209DB1|
|Source SHA|FA3E1EF5BB9E1B5EB94D001EC6A7B7B239C12A94F3105A388E553CC62BA5E2CA|
|보호 대상|Master4901unique SHA/size before/after;baselineSHA150B60EFB482E95370444096F9658A49A1A47AD4FC8962F29BB7F3FADD70CC03|
|후보 실행|Production modify/build0;candidate/runner process0;assembly load0;controls0|
|금지 범위|MutableR12source/bin/obj/runner/ACK/completion unread;provider/cache/config/game/native/operator/old/rejection/adverse0|
|Gate|No newclosure/fullGateE2NOT_RELEASED/FoundationHOLD|

Source text는동결R11만 읽었습니다. Collector2538~2573의RunningMods enumeration은loadOrder를0으로시작해record마다증가시키므로지원된정상ordinal은0..count-1입니다. CurrentCheck1982~2016은physicalarray의package를읽지만Normalize1652~1674는loadOrder로sort하며packageIdtie-break를사용합니다. Validate2270~2293은negative/duplicatepackage/duplicateloadOrder를검사하지만contiguouszero-basedcontract의공통interpretation이충분히명시된것은아닙니다. 이source근거와overload/admission/codec/canonicalpolicy/binding을 {link('FROZEN_R11_FIELD_AND_CALLSITE_MATRIX.json')}에line/hash로남겼습니다. 실제collector/Compute/provider를실행하지않았고 A의R12목표를구현완료로해석하지않았습니다.

{link('NORMAL_ORDER_REFERENCE_ORACLE.json')}에는정책목록과rawactualinventory를별도literal로선언했습니다. 기본3record는core/alpha/beta이며ordinal0/1/2와version1.0.core/2.1.alpha/3.4.beta를연결합니다. PhysicalBCA/CAB/reverse는같은ordinals·versions를유지합니다. 별도executionACB는core0/beta1/alpha2와독립policyACB를함께선언하여실행의미를바꿉니다. ACB의physicalpermutation은그새실행의미를보존합니다. 정책을observedinventory에서생성하거나policylist를sort/dedupe하지않았습니다.

|Reference pair|관계|Policy digest equal|Expected content meaning equal|
|---|---|---|---|
{relation_table}

이표는standardPythonJSON/hash로준비한reference관계이며candidatePASS가아닙니다. Raw physical diagnostic order는정상permutation에서달라지고,effectiveexecutionsequence와fullcanonicalsemanticmapping은같아야한다는기준입니다. DifferentexecutionACB는동일ID/revision을유지하면서orderedpolicydigest와ordinal-to-package/version의미가달라져야합니다. ID-only/revision-only/equalinstances,normalpackagecase,opaque whitespace/Unicode/displaytext/007regression도분리했습니다. 모든matchinginventory는unique3packages와sequentialordinals의정상자료입니다. Gap/tie/duplicate/unsupported/mismatchfixture를만들지않았습니다.

각case의current-v1fixed-key/literalUnicodecompactpolicyJSON UTF8/noBOM과독립SHA14개를준비했습니다. 나머지reference는rawinventory14/effectiveexecutionliteral14/policy-bearingfreshoriginalboundinput14/fullcanonicalcontentsemantictemplate14로총70files입니다. CurrentR11Checkcarrier계획은rawexpectedpackage spelling과lowercaseeffectiveobservedlist를구분하며,manifestpackage spelling은whole record의관측literal로보존합니다. 새R12field/APIcarrier나정책header를구현돼있다고주장하지않습니다.

Fullcontenttemplate는원래독립R11입력의8Deffamilies/numeric/string/order와새3mods/3assemblynormalrecords를사용합니다. Currenttemplate당179expectedleaves와float32bits/Int32/9007199254740993Int64/exactordinalstrings를 {link('TYPED_CONTENT_REFERENCE_PLAN.json')}에준비했습니다. Package-versionrecord가sorting으로분리되거나잘못연결되면확인할수있도록fulltypedmeaning을기록했습니다. Contentcontract/flags는R11template표시이며R12에대한최종값이아닙니다. R12freeze/admission후actualtypes/headers/fieldorder/float32canonicalrendering을대조해fullcontentbyteoracle를후보호출·빌드전에완성해야합니다. 지금standardJSONsemanticreference바이트를미관측R12의canonicaloutput과같다고가정하지않습니다.

{link('POSITIVE_NORMAL_ACCEPTANCE_MATRIX.md')}의14기준은aligned/permutation/differentexecutionsequence를비교하고,everyordinal/ID/version/fullreturnedfield와typedpolicybinding을검사하도록계획합니다. PureCheck는copiedorderedview를사용하며rawcaller가전후완전히같아야합니다. Admission은문서화된in-placeNormalize가caller를canonicalorder로바꾸되package/version/contentassociation을유지해야합니다. Record/declaration4Checkoverload와2matchingadmissionoverload의같은의미를독립기대값으로비교하며status/count/nonempty만으로PASS하지않습니다.

R11N12의after-admissionNormalize한계를새검증으로승계하지않습니다. {link('FRESH_ORIGINAL_BINDING_CONTROL_PLAN.md')}에는independentpolicy-bearingrawinput에서각각새DTO를만들어false transport,externalNormalize/admission **이전** fresh-originalSerialize(true),별도explicitNormalize,decoded/reconstruction을수행하는순서를명시했습니다. Embeddedbinding자료는genericcodeccontrol이며trustedapproval이아닙니다. Check/admission의unboundinput과separateexpectedpolicy는다른정상fixture입니다. 아직어떤candidatecontrol도실행하지않았습니다.

Generic65/currentfulltyped/finitefloat32bits/int32/largeInt64/Unicode/R9optionalunknown-null-empty-known-distinct-reverse/orderedverbs-stages-Compsmultiplicity/distinctset회귀도미래새candidate에서수행할기준으로남겼습니다. GeneralSchema/cachegeneration/patchsettingsmaterial/native/operator는separateOPEN입니다. Order수정의정상PASS를nativeactualexecution이나trustedorigin으로확대하지않습니다.

{link('STATIC_REVIEW_CRITERIA.md')}의14기준에는source-onlyordinal/packageguards를포함했습니다. Null/negative/gapped/tied/duplicate/malformed/unsupported자료를실행하거나자동보정하는test를작성하지않았습니다. Negativebranch·unknownschema·forgery/replay/tamper/bypass/adverse재현은없습니다. FixedWorker/csproj/Census72547prefix보존과policycopiedview/callerownership/sharedorderinginterpretation을futurestaticreview에서검토하도록명시했습니다.

새packagingcriterion은serializer-generatedparseableJSON,finalproduction/runnerbuild→prepin→calls→post,각run_id가command/results/raw/pre/post와일치하는것입니다. Actualnumericexit/SDK/compiler/framework/source/generatedPDB/response/argv/cwd/literaloracle/loadedmanaged/PID/culture/fullraw를결속할계획입니다. 원래R11invalidreleaseJSON/UTF16raw/pre-resultIDmismatch/limitedproducercoverage와oldQA는 {link('HISTORICAL_R11_REFERENCE_INDEX.json')}에보존된역사이며새준비가이를수정하거나인증하지않습니다.

Masterbaseline4901은authorizedmutableR12paths와Steam을제외하므로현재A의새build를oldlineage로읽거나보존실패로취급하지않았습니다. OriginalWorkerBridge.cs/csproj고정2files는baselinehash만확인했고productiontext는frozenR11뿐입니다({link('PROTECTED_PATH_SCOPE_AUDIT.json')}). RootMastergovernance/Awork/scheduler/installation/oldQA변경0,A메시지/추가WP0입니다. Fullbefore/afterSHA-size와최종manifest/index/ACKbinding/COMPLETION으로준비증거를결속하고originalMaster에1회terminal보고합니다.

R12NOT_REVIEWED,controls/build/run0/assemblyload0이며원문R8FAIL/R9historicalnarrowclosure/R11scopedcurrent-v1PASS를보존하고새candidatePASS로승계하지않았습니다. DedicatedServerfinalDomainAuthority,Masterrelease/closuregovernance입니다. Engine002006/Pipeline007/current schema/G-Q1OPEN,FoundationHOLD이며exactR12candidate가새로freeze/admit된뒤별도independentWP를받을준비결과입니다.
'''
    REPORT.write_text(text,encoding='utf-8');print(json.dumps(row(REPORT),indent=2))
