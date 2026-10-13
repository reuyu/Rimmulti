from review_setup import *
import re

if __name__=='__main__':
    assert not REPORT.exists()
    ack=load(Q/'ACK.json');d=load(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');findings=load(Q/'INDEPENDENT_REVIEW_FINDINGS.json');producer=load(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json');criteria=load(Q/'CRITERIA_DISPOSITION.json')
    def link(n):return '['+n+']('+str(Q/n).replace('\\','/')+')'
    (Q/'INDEPENDENT_REVIEW_FINDINGS.md').write_text('# R11 independent findings\n\n'+'\n\n'.join('## '+r['id']+' / '+r['disposition']+'\n\n'+r['finding']+'\n\nFrozen lines: '+', '.join(str(a['first_line'])+'-'+str(a['last_line']) for a in r['anchors']) for r in findings['findings'])+'\n',encoding='utf-8')
    (Q/'CRITERIA_DISPOSITION.md').write_text('# R11 preparation criteria disposition\n\n|Criterion|Disposition|Evidence / limits|\n|---|---|---|\n'+'\n'.join('|'+r['preparation_criterion']['id']+'|'+r['disposition']+'|'+r['evidence']+'|' for r in criteria['normal'])+'\n\nStatic criteria14 reviewed with current-source schema/order/cache/native limits,not adverse execution.\n',encoding='utf-8')
    warnings=len(re.findall(r'warning CS\d+', (Q/'BUILD_RAW.txt').read_text(encoding='utf-8-sig')))
    table='\n'.join('|'+r['id']+'|'+r['disposition']+'|' for r in findings['findings'])
    text=f'''# R11 policy encoding 독립 QA S1

**현재 `WE-PACKAGE-POLICY-V1`의 정상 정책 encoding·opaque binding·codec helper는 관측 범위 PASS입니다.** 새 QA 러너 1회 빌드 뒤 en-US/de-DE의 새 프로세스에서 각각 247PASS/0FAIL, 실제 종료 코드0을 확인했습니다. General schema carrier/order/cache/native는 정적 제한과 미검증 범위로 남으며, producer release JSON은 원문 그대로 invalid입니다. Full Gate E2와 closure는 새로 주장하지 않습니다.

|Identity / evidence|실제 값|
|---|---|
|WP / revision|{ack['wp_id']} / S1|
|Delivery|{ack['delivery_id']}|
|Unique result|{ack['result_id']}|
|보고 시각|{now()} / Asia/Seoul;terminal 시각은 COMPLETION.completed_at|
|동결 후보|G05R11-bec3d350 / manifest74 SHA79151763B710FE37E59148E272C1C7BC6C3D606D275B5215AF4174187C209DB1|
|Selected Debug|SHA133348C3FBC20215B9C4E0E9CA25D731781FCE9AD8CBE91F5A145BDB3620F98D / MVIDe6c6f6fd-2915-4493-8ef9-dc5d87de1c6b|
|Matching PDB / source|BA3027651BA59976BBEC6E1D2454AA0A2F5D964862809618AD80C9F2C6647BDE / FA3E1EF5BB9E1B5EB94D001EC6A7B7B239C12A94F3105A388E553CC62BA5E2CA|
|QA runner|SHA{d['runner']['exe_sha256']} / MVID{d['runner']['exe_mvid']}|
|Build/run exits|0 / 0 / 0|
|새 정상 cases|Generic12 + current-policy15;각 process247assertions,version target6×5views|
|Typed/canonical 비교|37696 matched rows / 71 UTF8 cross-process pairs|
|Preservation|Master4189 unique SHA/size before/after|
|금지 범위 실행|Production modify/build0;config/cache/provider/game/native/operator/old/negative/rejection/tied/unknownschema/ambiguity/adverse0|

Master의 실제 admission sidecar SHA19A7A624349327D545DBF50FD00185739EBBD97FC333A2C91016345CBB80EDB0와 동결 manifest를 확인했습니다. Debug/alternateRelease의 PE MVID/CodeView/PDB/source/generated4/4를 별도 byte metadata로 대조했고, original source 대신 frozen document 경로로 checksum을 해석했습니다({link('R11_LINEAGE.json')}). ReleaseA5508965…/MVID35dfe68f…는 metadata만 읽었습니다. WorkerBridge.cs/csproj와Census72547byte prefix는 동결R10과 동일하고 변경 diff를 보존했습니다({link('FIXED_SOURCE_SCOPE.json')}). OriginalSteam/gamecore/ProbeMod/UserData/save/설치 incident를 읽거나 복원·정상화하지 않았습니다.

Escape convention은 실행 출력에 맞춰 고르지 않았습니다. Master가 동결 source/report를 근거로 실행 전에 선택한 LITERAL_UNICODE_MINIMAL을 확인했고, 준비 reference14개를 그대로 대조한 뒤 정상 다른 unique 목록1개를 독립 literal로 추가했습니다. 선택 시각/명시적 reference/SHA와 정책 ID·revision·목록 및 별도의 실제 inventory를 최종 빌드 전에 {link('INPUT_EXPECTED_SEMANTICS.json')}와 {link('ORACLE_BEFORE_BUILD.json')}에 확정했습니다. Actual inventory에서 승인 expected를 만들지 않았습니다.

Canonical 정책의 네 key는 schemaVersion,policyId,revision,admittedPackageIds의 고정 순서이고 digest는 input field가 아닙니다. 선택된 compact JSON UTF8/noBOM/literal Unicode와 quote/backslash/normal tab·CR·LF escape를 표준 JSON으로 독립 생성해 exact bytes와 uppercaseSHA를 비교했습니다. Ordinary Unicode/BMP/supplementary/combining sequence,quoted/backslash display text,leading/trailing spaces,case-sensitiveopaqueID,문자열revision`007`,packagecase와ID-only/revision-only/order-only(다른 dimension 고정)/equal 독립 선언을 검증했습니다. 일반 escaping/collision/injectivity의 모든 입력을 증명하지 않았습니다.

15정상 정책 모두 Serialize/Deserialize/재구성,EscapeJsonString,세 digest overload,ToRecord(default/explicit matchingdigest)와ToDeclaration의 current-version parity가 독립 기대값에 맞았습니다. 원래 rawpackage spelling은ToRecord와Check.expectedPackages에 유지되고,canonical declaration/record.ToDeclaration 및 observed 목록은 normal lowercase 의미를 따르는 것으로 빌드 전에 명시했습니다. Manifest activeMods.packageId는 observed literal spelling을 유지하는 별도 codec carrier입니다. 이 차이를 출력에 맞춰 oracle로 바꾼 것이 아닙니다.

각 matching fixture는 unique package와 sequentialloadOrder가 physical order에 맞습니다. Check의4개 overload와 record/declaration admission2개 overload를 모두 사용했습니다. 모든 checkfield/ID/revision/digest/expected·observed 목록의 element·순서,admitted content171leaves 및 caller post-state를 비교했고 record/declaration의 canonical output이 같았습니다. Checked status/count/nonempty만으로 PASS를 판정하지 않았습니다. Exactpolicy bytes의 독립 reference와실행 산출물30bindings,fullCheck/callerRows는 {link('INDEPENDENT_EXECUTION_SUMMARY.json')} 및각 case의policy artifacts에 있습니다. 직접 runner callsite수는process당policy Serialize45/Deserialize15/Escape30/digest45/ToRecord30/ToDeclaration30/Check60/admission30입니다. 내부 중첩 pure 호출은 별도로 계수하지 않았습니다.

R9 unknown/null/empty/known-distinct/reverse/generic/missingversion의6targets와5views를 새 R11에서 회귀했습니다. Generic12의 false transport,explicitNormalize,fresh originalSerialize(true),decoded/reconstructed instance는 구분했습니다. Historical65대표leaf와BASE168currentleaf,float32 exactbits/int32/9007199254740993Int64/Unicode/orderedmods-verbs-stages-Compmultiplicity 및distinct set permutation도 확인했습니다. PositiveValidate2/structuralTryAdmit2는 codec controls이며 expected policy authority가 아닙니다. 새로운 opaque content binding은 정상 admission이 내부 Normalize한 뒤의 caller/output과재구성 serialization으로 확인했습니다. 이를 pre-Normalize policy-bearing fresh-originaltrue control이라고 표현하지 않습니다({link('CRITERIA_DISPOSITION.json')},N12).

실제 SDK10.0.201/Roslyn5.3.0-2.26153.122/net472refs/WindowsCLR4.0.30319.42000으로 새 runner를 빌드했고 nullablewarning{warnings}개/fullraw를 보존했습니다. Buildexit0입니다. 각각125input/source/dependency/toolchain/runner/candidate files의pre/post가 일치했고 실제loadedmanaged12개가 모두pre-pin과 맞았습니다. ProcessID {d['actual_processes'][0]['process_id']} / {d['actual_processes'][1]['process_id']}의새en-US/de-DE command/run_id/argv/cwd/numericexit/fullraw/typedresults를 결속했습니다. 첫 결과는RUN1_ARCHIVE에 보존한 뒤같은 최종 runner로 두번째 process를 실행했습니다. Canonical pair는generic12+fresh-original12+structural2+policy15+matchingrecord15+matchingdeclaration15=71이고 policy typed observations도동일합니다. Candidate/oracle/최종runner를 실행후 바꾸거나 재빌드·재실행하지 않았습니다.

|Independent finding|Disposition|
|---|---|
{table}

M01: ad hoc delimiter가 current typedcanonical JSON으로 바뀌었고 ID/revision Trim이 제거됐습니다. Exactcurrentnormalencoding·opaqueCheck/admissionbinding을 credit합니다. M02: declaration schemaVersion은public writable이고 Serializer는nonempty값을사용하며 Deserialize는generalDTO입니다. ToRecord는schema를전달하지않고ToDeclaration은currentconstant를복원합니다. Check/result/disposition에는별도schemafield가없습니다. 이번 current version exactdigest tagging은PASS이지만generalversion/closedschema/carrierhandling은STATICOPEN입니다. Unknownschema/rejectionfixture는만들거나실행하지않았습니다. M03: physicalarray/loadOrder/cachegeneration/operatorinstallation/patchsettings/material/native는분리OPEN입니다. Digest/embeddedADMITTED나structuralhelper가trustedoperatororigin을증명하지않습니다. 모든 exactsourceanchors는 {link('INDEPENDENT_REVIEW_FINDINGS.json')}입니다.

M04: producer release JSON의 originalSHA290507994A0E13A3A8F04F77637F240F3C7F55E63308E387B216831219AA8F80를확인했고실제parse는`{producer['release_parse_error']['error']}`로실패합니다. Rawbytes를수정/대체하지않았습니다. Admission은Master의별도실측identitysidecar에근거합니다. M05: producer raw UTF16LEBOM을명시적으로decode해 원문SHA를유지했습니다. 14source/result/rawlabels를대조했으며 predicate를구분했습니다. TC01의literalJSON/TC02normalroundtrip은좁은credit,TC03은candidateSerialize결과에SHA를취한것,TC09/10은선택fields/counts,TC13/14는제한된version/sorting회귀입니다. Producerpre-run`{producer['producer_pre_run_id']}`와result`{producer['producer_result_run_id']}`가다르며추가culturefiles는완전한process/prepin/numericexit/toolchaingraph증거가아닙니다. NewQA graph는과거producerchronology를인증하지않습니다({link('PRODUCER_COVERAGE_AND_PACKAGING.json')}).

준비14normal/14static 기준을 actual current API와연결했으며일반schema/order/cache범위는해당항목에따로기록했습니다. Frozen candidate의재빌드나기존release원문수정이이루어진것은아닙니다. 원문R8FAIL/oldQA와R9historicalnarrowclosure를보존했고R10PASS나준비reference검사를새R11PASS로승계하지않았습니다. Scope안의이번freshnormalexecution만새증거입니다.

DedicatedServer가finalDomainAuthority이며Master가release/closuregovernance를판단합니다. Closure변경0/fullGateE2NOT_RELEASED,Engine002006/Pipeline007/current schema/G-Q1OPEN/FoundationHOLD입니다. 후속package문서정정이나generalSchema/order/cache/native작업은Master가새범위와원문보존정책을판단할항목입니다. 이번QA가A에추가WP나scheduler/governance변경을전달하지않았습니다.
'''
    REPORT.write_text(text,encoding='utf-8');print(json.dumps(row(REPORT),indent=2))
