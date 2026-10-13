from review_setup import *

if __name__=='__main__':
    assert not REPORT.exists()
    ack=load(Q/'ACK.json');oracle=load(Q/'NORMAL_REFERENCE_ORACLE.json');normal=load(Q/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json');static=load(Q/'STATIC_REVIEW_CRITERIA.json');fields=load(Q/'FROZEN_R10_FIELD_AND_CALLSITE_MATRIX.json');resume=load(Q/'RESUME_ACK.json')
    def link(n):return '['+n+']('+str(Q/n).replace('\\','/')+')'
    for filename,title,d,cols in [('POSITIVE_NORMAL_ACCEPTANCE_MATRIX.md','R11 positive normal acceptance preparation',normal,['id','topic','reference_case','exact_expected_assertion']),('STATIC_REVIEW_CRITERIA.md','R11 defensive static preparation',static,['id','topic','predicate']),('FROZEN_R10_FIELD_AND_CALLSITE_MATRIX.md','Frozen R10 field/callsite constraints',fields,['concept','current_type','first_line','last_line'])]:
        body='# '+title+'\n\nPreparation only / no candidate execution.\n\n|'+'|'.join(cols)+'|\n|'+'|'.join('---' for _ in cols)+'|\n'+'\n'.join('|'+'|'.join(str(r[c]).replace('|','\\|') for c in cols)+'|' for r in d['rows'])+'\n'
        (Q/filename).write_text(body,encoding='utf-8')
    variants='\n'.join('|'+name+'|'+v['non_ascii']+'|'+v['forward_slash']+'|NOT_SELECTED|' for name,v in oracle['variants'].items())
    cases='\n'.join('|'+n+'|'+','.join(v['references'])+'|' for n,v in oracle['cases'].items())
    convention='# Escape convention boundary\n\nTwo explicit reference variants are compatibility preparation,not a candidate convention decision.\n\n'+ '\n\n'.join(str(i+1)+'. '+x for i,x in enumerate(load(Q/'ESCAPE_CONVENTION_DECISION_CRITERIA.json')['criteria']))+'\n'
    (Q/'ESCAPE_CONVENTION_BOUNDARY.md').write_text(convention,encoding='utf-8')
    text=f'''# R11 policy encoding 독립 QA 준비 S1

**읽기 전용 준비 완료. R11 후보는 NOT_REVIEWED이며 controls/build/run은 0입니다.** 동결 R10의 제약12개,정상 acceptance14개,정적 리뷰14개,정상 reference 선언14개와명시적escape변형2개에대한UTF8파일28개를준비했습니다. 정책의선언된의미와아직관측하지않은R11API/escapeconvention을구분했습니다.

|Identity / scope|값|
|---|---|
|WP / revision|{ack['wp_id']} / S1|
|Delivery|{ack['delivery_id']}|
|Unique result|{ack['result_id']}|
|작성 시각|{now()} / Asia/Seoul;최종 시각은 COMPLETION.completed_at|
|동결 source reference|G05R10-81a28ecb/manifest76 SHA5BBDD6AA47C415783CDD0FCB256A87B852D227720FBD0B6E62B9F061680E8578|
|Source SHA|E855F60CB91F1207A03530842F65A6CECCEEA5B5DFF01511B86821AD2600D6AC|
|Historical selected identity|1772DF…/MVID7ef10d5b… 정적 참고;candidate 실행0|
|보호 대상|Master4047 unique SHA/size 전후 확인|
|실행 범위|Candidate/runner build0/process0/controls0;configuration/cache/provider/game/native/operator/oldrunner/negative/adverse0|
|Gate|FullGate E2 NOT_RELEASED/closure unchanged/Foundation HOLD|

같은result와부분파일로사용량실패후재개했습니다. 이전ACK전송은자동승인검토의usagefailure로실행되지않았다는실제toolreturn을 {link('ACK_TOOL_PROOF.json')}에보존했습니다. 원래failedturn01a11d5f-555e-7c20-87bc-d741f1940a93와실제재개turn{resume['actual_resume_turn_id']}를 {link('RESUME_ACK.json')}에별도결속했습니다. 기존ACK_INITIAL/ACK/PRESERVATION_BEFORE를변경하지않았고4047보존을재검사했습니다. 기존WP를다시시작하거나새result/대체Sol을만들지않았습니다. 재개ACK의실제성공return은 {link('RESUME_ACK_TOOL_PROOF.json')}입니다. 계정구매/설정/모델변경은하지않았습니다.

Canonical선언의normative키순서는schemaVersion,policyId,revision,admittedPackageIds이고schemaVersion은`WE-PACKAGE-POLICY-V1`입니다. ID와revision은opaque string으로원래공백·대소문자·Unicodecodepoint를exactordinal로보존합니다. Trim/casefold/숫자parse/Unicode정규화는허용하지않는기준입니다. NormalunpaddedASCII dot packageIDs만invariantlowercase로canonical표현하며listorder/multiplicity의표현을sort/dedupe로바꾸지않습니다. Digest자체는선언inputfield가아니며선택한compactcanonicalJSON UTF8/noBOM의SHA256uppercase입니다. 일반packagegrammar/order/ordinal승인범위를새로선정하지않았습니다.

{link('NORMAL_REFERENCE_ORACLE.json')}에는expectedtypedpolicy와actualinventory를각각별도수동literal로작성했습니다. Equal독립선언,ID-only,revision-only,order-only(다른dimension고정),normalpackagecase,ordinaryUnicode/quoted/backslash/tab/CR/LFdisplaytext,leading/trailingspaces,`007`revisiontext를준비했습니다. Opaque문자열의UTF16LEhex와codepointsequence도expectedmeaning으로남겼습니다. Actual목록에서expected를복사하거나정책digest를authority로인정하지않습니다. 각inventory는unique정상package/sequentialloadOrder가physical순서와일치합니다. Tied/duplicate/ambiguous/mismatch/rejectionfixture는만들지않았습니다. Declarationmultiplicity의sourcecriterion은generaladmission과별개입니다.

|Reference variant|Non-ASCII convention|Slash|Candidate adoption|
|---|---|---|---|
{variants}

두변형은같은선언의의미를보존하지만Unicode의literalUTF8와ASCIIu-escapebytes/digest는달라질수있습니다. Quote/backslash와제어문자는명시적JSONescape,hex는lowercase,slash는literal로정의했습니다. ASCII변형은supplementaryUnicode를surrogatepairescape로기록합니다. StandardPythonJSON/hash로독립referencebytes/digest와decode후정확한keyorder/types/값을준비한것이며candidate를검사한것이아닙니다. 모든reference는normal_references/아래28개파일로저장했습니다.

|Normal reference case|Available explicit variants|
|---|---|
{cases}

향후Master의exactfreeze/admission뒤문서화된escapeconvention을먼저확인하고그에대응하는reference를실행전에선택해야합니다. 출력에맞는변형을나중에골라PASS를만들지않습니다. Unicode/slash/HTML-sensitive처리/controlshortescape/u-escape/hexcase가두준비변형과다르다면선언된grammar를검토한뒤새prospectivereference를build/run전에작성해야합니다. 현재Serialize/DeserializeAPI명,DTOschemaCarrier,returnedraw-versus-normalizedpackage형태는UNOBSERVED입니다({link('ESCAPE_CONVENTION_BOUNDARY.md')}).

{link('POSITIVE_NORMAL_ACCEPTANCE_MATRIX.md')}의14기준은fixedschema/keyorder,no-digest-input,equalinstance,opaqueID/revision/order-only,Unicode/control/공백보존,packagecase,policyroundtrip,reconstruction과fulltypedbinding을요구합니다. 정상matchingCheck/admission/contentcodec의schema/ID/revision/digest/list/ordinal과전체content를독립oracle로비교하고caller변화는별도로관측하도록계획했습니다. Legacycomposedboundary는corroboratinglabel이며typedbinding이나expectedauthority를대체하지않습니다. Rawpackagecarrier가진단적으로원래대소문자를가지면그contract를별도명시하고canonicallowercase의미와일치함을검사할기준입니다. R9unknown/null/empty/known-distinct/reverse,65/currentnumericUnicode/orderedcontent와freshoriginaltrue회귀는새candidate가별도로허용된뒤수행할계획입니다. 실행했다고표현하지않습니다.

{link('STATIC_REVIEW_CRITERIA.md')}의14기준은concretetypedversion/schema/escaping,digestoverload공통경로,opaqueidentitynoTrim,typedreturnedbinding,정책특정normalization과exact새graph를확인하도록작성했습니다. Generalphysicalarray/loadOrder,cachegeneration,operator/nativeorigin,patch/settings는separateOPEN입니다. Setter/property/cache/provider또는unconfigured/rejectionbranch를읽거나실행하는준비가아닙니다. 기존actualCompute연결은동결R10source에서정적참고로만남겼습니다.

동결R10에서digest는1815~1839의delimiterjoin이고1697~1703에서typedbindingstrings를Trim합니다. Check1883~1937은ID/revision/digest/expectedlist/physicalobservedlist를설정하고,TryAdmit1953~2000은typeddisposition과formattedboundary를쓴뒤contentNormalize/Serialize합니다. Structural2094~2137과actualCompute2859~2885의binding및2945~2973의typedDTO는추적할현재제약입니다. R10정책에는별도의policy-schema/canonicalSerialize·DeserializeAPI가없습니다. 이12제약과새논리concept6개는 {link('FROZEN_R10_FIELD_AND_CALLSITE_MATRIX.json')}에exactsourcehash/line으로남겼습니다. CurrentmutableR11/source/bin/obj/runner/producercompletion은읽지않았습니다.

원래R10QA397manifest/report/oracle/findings/policyobservations는historicalreference로만읽었습니다({link('HISTORICAL_R10_REFERENCE_INDEX.json')}). R10scopedPASS를R11PASS로승계하지않았고원문R8FAIL/R9historicalnarrowclosure/oldQA를보존했습니다. Masterbaseline4047은authorizedmutableR11paths와Steam을제외하므로현재build변경을oldlineage나보존failure로가정하지않습니다. Baseline에있는originalWorkerBridge.cs/csproj고정2파일은hash보존만확인했고productiontext는frozenR10만읽었습니다({link('PROTECTED_PATH_SCOPE_AUDIT.json')}). 초기ownbaseline-reader의size/bytes키차이는ownadapter에서고쳤으며원본baseline을정상화하지않았습니다.

이결과는새R11candidate실행/verdict가아닌read-onlyreference준비입니다. Master/A작업/governance/scheduler변경이나A메시지/추가WP는없습니다. DedicatedServer가finalDomainAuthority,Master가governance/release/closure를판단합니다. Engine002006/Pipeline007/current schema/G-Q1OPEN,Foundation HOLD입니다. 준비graph완료후originalMaster에정확한hash와result를직접보고하며새exactR11independentWP는별도Masteradmission을기다립니다.
'''
    REPORT.write_text(text,encoding='utf-8');print(row(REPORT))
