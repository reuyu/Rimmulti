from review_setup import *
from analyze_review import row
import re

if __name__=='__main__':
    report=ROOT/'docs/QA_EngineHost_Gate05_R10_Package_Policy_Independent_S1_20261009.md';assert not report.exists()
    d=load(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');ack=load(Q/'ACK.json');f=load(Q/'INDEPENDENT_REVIEW_FINDINGS.json');c=load(Q/'CRITERIA_DISPOSITION.json');p=load(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json')
    def link(name):return '['+name+']('+str(Q/name).replace('\\','/')+')'
    table='\n'.join('|'+r['id']+'|'+r['disposition']+'|' for r in f['findings'])
    findings_md='# Exact frozen R10 independent findings\n\n'+ '\n\n'.join('## '+r['id']+' / '+r['disposition']+'\n\n'+r['finding']+'\n\nFrozen source lines: '+', '.join(str(x['first_line'])+'-'+str(x['last_line']) for x in r['anchors']) for r in f['findings'])+'\n'
    (Q/'INDEPENDENT_REVIEW_FINDINGS.md').write_text(findings_md,encoding='utf-8')
    (Q/'CRITERIA_DISPOSITION.md').write_text('# R10 criteria disposition\n\n|Criterion|Disposition|Evidence / limits|\n|---|---|---|\n'+'\n'.join('|'+r['preparation_criterion']['id']+'|'+r['disposition']+'|'+r['evidence']+'|' for r in c['normal'])+'\n\nStatic criteria14: see JSON mappings and exact findings;no branch runtime reproductions.\n',encoding='utf-8')
    warnings=len(re.findall(r'warning CS\d+', (Q/'BUILD_RAW.txt').read_text(encoding='utf-8-sig')))
    text=f'''# R10 package policy 독립 QA S1

**정상 package/codec 순수 helper는 관측 범위 PASS입니다. 일반 정책 encoding·order 계약·cache binding은 STATIC REVISION_REQUIRED이며 native/operator와 full Gate E2는 UNTESTED/NOT_RELEASED입니다.** 새 QA 러너 1회 빌드 후 새 en-US/de-DE 프로세스에서 각각135PASS/0FAIL,실제 종료코드0을 확인했습니다. 기존 R9 PASS를 승계하지 않았습니다.

|Identity / 실행|실제 값|
|---|---|
|WP / revision|{ack['wp_id']} / S1|
|Delivery|{ack['delivery_id']}|
|Unique result|{ack['result_id']}|
|보고 시각|{now()} / Asia/Seoul;terminal 시각은 COMPLETION.completed_at|
|동결 후보|G05R10-81a28ecb / manifest76 SHA5BBDD6AA47C415783CDD0FCB256A87B852D227720FBD0B6E62B9F061680E8578|
|Selected Debug|SHA1772DFBD1674B7CF8450CAF42FDE7AC6F92FD3A22183B7DDE5AA705CCEC24721 / MVID7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb|
|PDB/source|DebugPDB58FE3A765BB95C5C7FB044FE5E4627B66BF245ABA72C0CF95A05BC29EFF9B342 / CensusE855F60CB91F1207A03530842F65A6CECCEEA5B5DFF01511B86821AD2600D6AC|
|QA runner|SHA{d['runner']['exe_sha256']} / MVID{d['runner']['exe_mvid']}|
|Build/run 실제 exits|0 / 0 / 0|
|새 controls|generic12+matching package6;각 process135assertions;target version6×5views|
|보존 대상|Masterbaseline3644 unique SHA/size 전후 확인|
|금지 범위 호출|Production modify/build0;configuration/cache/provider/game/native/operator/oldrunner/negative/rejection/tied/ambiguity/adverse0|

동결 manifest와 Master baseline을 실제로 대조했고,Debug 및 alternateRelease의 PE MVID/CodeView/PDB/source/generated4/4를 byte metadata로 확인했습니다. AlternateRelease659CFE…/MVIDafe11c93…는 metadata만 읽었습니다. WorkerBridge.cs/csproj와Census72547byte prefix는 동결R9와 동일합니다({link('R10_LINEAGE.json')}, {link('FIXED_SOURCE_SCOPE.json')}). 변경 source는 {link('SOURCE_SCOPE_DIFF.txt')}로 보존했습니다. 원본 Steam/UserData/save/설치 incident 재독취·restore·정상화는 하지 않았습니다.

독립 입력/기대 의미는 최종빌드 전에 {link('INPUT_EXPECTED_SEMANTICS.json')}와 {link('ORACLE_BEFORE_BUILD.json')}에 확정했습니다. 정책 expected ID/revision/list와 actual package literal을 별도 선언했고,관측 결과에서 승인 목록을 만들지 않았습니다. 현재 string revision/정상 unpadded ID/dot package/case normalization과 sequentialloadOrder에 맞춘6사례를 사용했습니다. Equal 독립 instance,policyId만 변경,revision만 변경,order만 변경(같은ID/revision),정상 다른 목록을 각각검사했습니다.

현재 구현의 정상 preimage `policyId|revision|lowercased comma-separated package IDs`를 독립 UTF8 bytes와SHA로 실행 전에 만들었습니다. 두 digest overload의 직접 호출12개/process가 referenceSHA와 일치했고,Check두 overload 직접 호출12개/process 및 fullydeclared TryAdmitWithPackagePolicy6개/process가 통과했습니다. 내부 helper 호출은 별도 계수하지 않았습니다. Check 결과의 모든 field/정확한 expected list/observed lowercase list,그리고 admitted전체 content171leaves/case와ordinal/ID/revision/digest/status/manifest boundary를 비교했습니다. Check는caller를 보존했고,admission의in-place caller 변화는별도expectedfullmanifest와맞았습니다. 단순status/nonempty/count로PASS를판정하지않았습니다({link('PACKAGE_POLICY_RESULTS.json')}).

정책의 일반 typed/injective/escaping/length framing schema와 별도 reconstructiblecanonical policy API는 구현돼 있지 않습니다. 정상sample preimage/digest 일치가 그범위를닫지않습니다. 준비N07은부분검증+STATIC_REVISION_REQUIRED이고N02/05/11의일반representation/order/normalization범위도열려있습니다. 구분자 ambiguity/tied/unconfigured/unsupported/rejectionfixture를만들거나실행하지않았습니다. 정책digest/ADMITTED/setter는trustedoperatororigin이아닙니다.

Codec회귀는false transport,explicitNormalize,freshoriginalSerialize(true),decoded/reconstructed5views를분리했습니다. R9의unknown/null/empty/known-distinct/reverse/generictext/missingversion6targets가새R10에서통과했습니다. Historical65대표leaf,BASE168currentleaf,float32exactbits/int32/9007199254740993Int64/Unicode/orderedmods-verbs-stages-Compmultiplicity와정상distinctsetpermutation을확인했습니다. BASE/revision의positiveValidate2+structuralTryAdmit2는codeccontrol이며packageauthority가아닙니다. Nativeallfield/actualsourceavailability/unknownversionrequiredsupport를증명하지않습니다.

빌드는실제SDK10.0.201/Roslyn5.3.0-2.26153.122/net472reference/WindowsCLR4.0환경입니다. Nullablewarning{warnings}개와전체buildraw를보존했고실제buildexit0입니다. QAProgram.cs/PDBmatchingdocument와최종runner를결속했습니다. 각run의input/source/runner/candidate/dependencies/toolchain116filespre/post가동일했고실제loadedmanaged12개모두pre-pin과일치했습니다. 각run_id/argv/cwd/raw/숫자exit/typedresult를별도저장했고,첫process산출물을RUN1_ARCHIVE에보존한뒤같은최종runner로두번째새process를실행했습니다. 두프로세스의canonicalUTF8는generic12+freshoriginal12+structuraladmitted2+packageadmitted6=32pairs동일하고정책typedobservations도동일합니다({link('INDEPENDENT_EXECUTION_SUMMARY.json')}). 이graph는QA의이번실행만증명하며producer의과거chronology를복구하지않습니다.

|독립 finding|Disposition|
|---|---|
{table}

R10-QA-M01:distinctexpected/completephysicalinventory/actualComputebefore newlycomputedsuccess연결은정적으로채택하고정상순수helper결과를credit합니다. ActualCompute는실행하지않았습니다. M02:opaque문자열구분자encoding과bindingTrim에는선언된일반grammar/typedcanonicalrepresentation/identitynormalization계약이없습니다. M03:Check는physicalarray순서를비교하고loadOrder를검사하지않으며,후속Normalize는loadOrder로sort합니다. 이번alignedpositive는PASS이고일반ordercontract는미확정입니다. M04:embeddedstatus/digest와structuralhelper는trustedexpectedapproval이아닙니다. M05:Configure/Clear는policy를바꾸지만cachegeneration/invalidationbinding이없고GetActual은cache를먼저반환합니다. Source-onlyfinding이며설정/property/cache실행은하지않았습니다. M06:patch/settingslabels·summaryrewrite/nativeoperator·C owner/schema/topology는별도OPEN입니다. 상세exactanchors는 {link('INDEPENDENT_REVIEW_FINDINGS.json')};준비12normal/14static의판정은 {link('CRITERIA_DISPOSITION.json')}에남겼습니다.

Producer19label/source/result/raw의identity는일치하지만predicatecoverage를그대로채택하지않습니다. TC04는header/일부count이고TC14는assemblypackage/name이며stats미검증입니다. TC17은normalcaseequal/order/revisiondigest지만독립preimage/ID-onlyassertion/canonicalpolicyserialization이없습니다. TC18positive는status/count/boundary중심이며negativeportion이포함됩니다. TC15negative/TC18negative/TC19configurationlifecycle는승인범위위반으로보존하고재현하지않았습니다. 모든19predicate는 {link('PRODUCER_COVERAGE_AND_PACKAGING.json')}에구분했습니다. Producerpre-runID `{p['producer_pre_run_id']}`와resultsID `{p['producer_result_run_id']}`가다르며numericexit/compiler/framework/resolvedgraph/독립oracle/typedcanonicalartifact기록은완전하지않습니다. Freeze는postcompletionidentity이며pre-runchronology인증이아닙니다.

초기QAsetup의taskpath/미전송draftlabel오류는새QA소유파일에서수정했고원본draftbytes/정정기록을보존했습니다. 실제ACK는올바른WP/delivery/result와결속한뒤1회보냈습니다. 그전에candidate실행/build/외부전달은없었고,실행후candidate/oracle/runner를수정하거나재빌드·재실행하지않았습니다.

원래R8FAIL과R9narrowCLOSEDlineage/oldQA를보존했습니다. 새정상PASS는이exactselectedR10의관측범위만을의미합니다. Closure/release는Mastergovernance이며DedicatedServer가finalDomainAuthority입니다. Engine002006/Pipeline007/current schema/G-Q1OPEN,FoundationHOLD이고새fullGateE2/다른defectclosure를주장하지않습니다. 다음boundedcorrectiveWP는Master가독립finding을검토해발행합니다.
'''
    report.write_text(text,encoding='utf-8');print(json.dumps(row(report),indent=2))
