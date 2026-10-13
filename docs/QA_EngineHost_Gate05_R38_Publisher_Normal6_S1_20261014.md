# R38 원래 정상6 publisher 독립 QA / S1

**판정: SCOPED_R38_ORIGINAL6_NORMAL_CLI_PUBLICATION_PASS_GENERAL_CONTRACT_REVISION_REQUIRED_NATIVE_UNTESTED.** Master가 새 WP로 승인한 exact frozen publisher의 원래 정상6 CLI publication만 관측 범위 PASS다. 총6회, 사례당1회, 전부exit0이며 사전 등록 bundle/sidecar의 UTF8 원본 바이트·SHA·길이와 일치했다. 일반 계약 결함·High4·전체 Engine/native E2를 닫거나 승격하지 않는다.

Delivery `SOL-GATE05-R38-PUBLISHER-NORMAL6-S1-20261014-01`, WP `WP_QA_ENGINE_GATE05_R38_PUBLISHER_NORMAL6/S1`, result `SOL-GATE05-R38-PUBLISHER-NORMAL6-S1-20261014-1ae62caeb1684c5c9556d7fc74bd6ca0`. Original Sol/local→Master/local initialACK `CF9E888101BAC7C0AD4E67CADF9AA96E9CDF7DB04CC3E4A3BE70215BD1B589CD` /2253는 실행·fixture 생성 전 작성/직접 전송했고 불변이다.

## 정확한 admission과 기대값

동결 [publish_operator_pair.py](C:/Users/user/Desktop/RimMulti/Dispatcher/CANDIDATES/G05R38-10b9846e/scratch/OperatorStartupPairR29/publish_operator_pair.py) SHA `940CF77220C272D117CDBC278B64858EFB3077267141CC548A0105B47D6E1306` /43666/Python MVID 해당 없음. 실행은 mutable source가 아닌 이 파일만 사용했다. WP SHA `F7A36F6F091CC6AC0A45F456F97C2F72415DE4D89BEC652F6A553243AF9E400A`, Master admission `2044BAFFAB9BC46521E3F9855724276BB40CA0739006084ADF59F813047177AE`, 실행 전 등록 oracle `C2D667CC372D605FDEC680B5663A62636DEF81DFCD6133689055C2FB86D343CB`, baseline `7DC67B8B9AAC482C30ECCD78999B8E2A6F65DBF12F58AE44BC17D62380F2A90E`, frozen42 manifest `85F08534BD3BD47258A8AC3A247438702FB318EA7F298C952B452C2464AF99DD`. Explicit EXE `C:\Users\user\anaconda3\python.exe` SHA `388FE2CFFDA8A134E7D7DC4E978F7C478857ECE6B69694DAECBED25E51EC633A` /104264만 사용하고 network/packages/globalenv 변경0.

Recovery83 fulltexts와 최신 Master 정적 disposition·normal6 admission을 읽었다. R35 expected original literal bundle에서 두 expectedConfigPath의 JSON 문자열 token만 바꾼 Master 기대값을 independently 대조했다. 기대값은 후보 결과 관찰 이전에 고정됐고 실제 출력에 맞춰 재직렬화·수정하지 않았다. BOTH R29 upstream/R35 raw12 UTF8hexSHAbytes/config14/decl7/PairID를 확인했다. Parent2026-10-11T00:00:00.1234567Z/ALL6 Child2026-10-11T00:00:01.0000000Z다. 원래 opaque/policy/role/cap/args/rawbytes와 선언 other6fields는 불변, 선언 locator expectedConfigPath만 새 own 입력 경로다.

새 QAroot에서 입력12·spec6을 exclusive xb로 쓰고 read-only 속성으로 고정했다. Spec은 등록 literal 바이트 그대로/inline declaration 객체다. 각 publication leaf는 실제 호출 전 존재하지 않았으며 publisher가 fresh mkdir로 생성했다. Existing workspace/parents/ACL/설치/기존 oracle는 수정하지 않았다.

## 실제 호출·출력

| 원래 case ID | Publisher PID | exit | stdout/stderr bytes | Bundle SHA | bytes |
|---|---:|---:|---:|---|---:|
| PLAIN_PLAIN | 27916 | 0 | 899/0 | AB1B6619F3FEC698B1784FBE1C8F261822816BA40B656426E1807DFDBBC7691F | 1022 |
| OPAQUE_OPAQUE | 17980 | 0 | 905/0 | C8AE990C4B5C0814FEA88676346FAD5ED186CAA464FE575E6B848E524CFA563F | 1026 |
| PLAIN_OPAQUE_PADDED | 34620 | 0 | 923/0 | 018C7F4AFE66B99007871263B80E56C0CBC9623CFC0B8634315BB79866AA4885 | 1054 |
| OPAQUE_PLAIN_PADDED | 8360 | 0 | 923/0 | 4A7E83D91DF593E914E0B69054A20D1A7301F509C5666951544BF29A80664E76 | 1054 |
| OPAQUE_EQ_QUOTE_BACKSLASH | 4508 | 0 | 959/0 | 8DCD1C8066BC5A7327B14049ADC236CA57620D52A64B7089B22ABD3E3DE7DA7F | 1171 |
| OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | 2460 | 0 | 980/0 | 3874400DB8AE9A35CEFA14096F859A600E1E98451C25C31245E483F395E0C58D | 1201 |

6개 모두 실제 `EXE -B frozenpublisher --spec exactSpec` 신규 child를 순차적으로 한 번 호출했다. 각 실제 PID/start-end/numericexit 및 전체 FIRST stdout/stderr rawbinary를 PUBLISHER_TOOL/단일 호출 ledger에 기록하고 다음 호출 전 내용을 확인했다. 호출 재시도·추가 adverse/invalid 입력0, candidate 함수 별도 import-call0. CLI summary는PUBLISHED/원래PairID/정확한path/SHA/bytes와 일치했다.

Final bundle과 staging은 각각 preregistered expected_bundle과 byteexact, SHA sidecar는 정확한 ASCII64/noLF다. Bundle은BOM0/noLF/top4와decl7 propertyorder/originalUnicode·padding·lowercase/quote/backslash/=를 보존했다. 고정한 raw12 입력은 실행 전후 동일하고 config14 시각을 출력 설명 때문에 바꾸지 않았다. Case5/6의 실제 원래 PairID는 다음 JSON literal이다.

- `OPAQUE_EQ_QUOTE_BACKSLASH`: `"  operatorPairId=5 \"Ω\" \\ original  "`
- `OPAQUE_EQ_QUOTE_BACKSLASH_PADDED`: `"  operatorPairId=6 \"Ω\" \\ original  "`

## 출처·경로·hardlink 관측

PROVENANCE의 spec/config path·SHA·bytes가 실제 pre-run fixtures/spec pins와 일치했다. Raw parent/child ConfigId-role와 declaration7는原문+path-onlydelta에 맞고 prior/handle stat 객체가 실제 존재하며 size=읽은 byte 길이다. Publisher scriptPath/SHA와 pythonVersion은 실제 admitted source/explicitruntime과 일치한다. captured handle attrs가 N/A일 수 있는 관찰 한계는 그대로 보존하며 fstat를 pathname identity 보증으로 확대하지 않는다. PublishedAtUtc는 새 출력의 실제 관찰이며 preregistered constant나 UTC world authority가 아니다.

Cvolume의 실제 root/components lstat usable Windows attrs/int nonbool/no reparse·symlink/expected DIR·REG와 새 outputleaf 부재를 before-write/call에 기록했다. 사용자 지정 workspace에서 protected local owner/nohostile concurrentwriter를 가정한다. ACL ownership 또는 universal hostile race/nofollow-open/TOCTOU 면역을 입증하지 않는다. Synthetic exe/UserData/CWD는 lexical testdata이며 실제 game/native frontend 실행·존재 요구가 아니다.

| Case | Final ino / staging ino | nlink final / staging | 관측 |
|---|---|---|---|
| PLAIN_PLAIN | 2251799816202834 / 2251799816202834 | 2 / 2 | 현재dev/ino동일 |
| OPAQUE_OPAQUE | 2251799816202853 / 2251799816202853 | 2 / 2 | 현재dev/ino동일 |
| PLAIN_OPAQUE_PADDED | 1970324839492217 / 1970324839492217 | 2 / 2 | 현재dev/ino동일 |
| OPAQUE_PLAIN_PADDED | 1407374886074359 / 1407374886074359 | 2 / 2 | 현재dev/ino동일 |
| OPAQUE_EQ_QUOTE_BACKSLASH | 1407374886074378 / 1407374886074378 | 2 / 2 | 현재dev/ino동일 |
| OPAQUE_EQ_QUOTE_BACKSLASH_PADDED | 1407374886074396 / 1407374886074396 | 2 / 2 | 현재dev/ino동일 |

정상 run에서 현재 shared hardlink identity를 관측했으며 staging/final 내용은 shared mutable이다. Bundle+sidecars는 동일 volume에서도 하나의 atomic transaction이 아니며 crash durability/PKI/engine authority를 입증하지 않는다. 새로운 24개 publisher files를 recursive own inventory에 포함하고 첫 로그를 재생성하지 않는다.

## own 실행 graph와 최종 보존

모든 own helper body 전에 신규 코드/common/logger/wrapper/explicitEXE/argv/cwd를 pin하고 자체 AST syntax preflight를 별도 실제 process로 수행했다. New wrapper의 rawbinary streams/PID/start-end/exit는 .NET Process에서 캡처했다. Toolconsole의 VoidTaskResult 표시는 CopyToAsync await 반환 표시일 뿐 child stdout으로 합성하지 않았다. 후보는 원래 코드 그대로 실행했으며 실제 child sys.path/importfile internals는 UNOBSERVED다. 외부 실제argv/cwd/env(PYTHONHOME/PYTHONPATH/PYTHONUTF8/PYTHONDONTWRITEBYTECODE/PYTHONIOENCODING/LANG), launcher defaultsys.path와 부분 resolved dependencyfiles를 pre-run에 기록했으나 comprehensive ambient/import attestation이 아니다.

Bootstrap/fixtures/6 owncase launchers/prepare/seal은10개 own bodychild, 각 own syntax preflight도10개다. 이20 subprocess는 실제PID를 별도 기록했다. 각 bodychild를 시작한 own Python logger native interpreter invocation도10개이며 loggerPID는 별도 캡처하지 않았다. Own metadata Python invocations를 합하면30개(10syntax+10logger+10body), 후보 publisher6개와 구분한다. Own metadata 오류·숨은 retry0, compiler/Engine/CLR/unitrunner/RimWorld/Unity/validator/frontend/game/worker/operatorProcess/native/adverse0.

Full protected19785+freeze42 pre/post SHAbytes lists equal, unique 19785 paths; raw fixture12+spec6 모두 read-only 유지/동일SHAbytes. Candidate SHA도 최종 재확인했다. ALL9 Engine/source/PDB/bin/generated/install/currentpublisher/archives/priorQA/originaloracles를 바꾸지 않았다. 새 QAroot metadata/fixture/output 및 지정 보고서만 작성했다. Governance/AGENTS/Masterstate/scheduler 변경0.

EVIDENCE_MANIFEST/RESULT_INDEX/report/initialACKcompletionbinding/COMPLETIONlastatomic와 complete finite own inventory를 남긴다. Selfmanifest/index/binding/ongoing seal streams/actualdirectreturn 자기cycle는 명시 제외하고 actualpostseal raw/tool/return을 별도 결속한다. 초기ACK와 RETURN_PENDING intent를 receipt로 덮어쓰지 않는다. Master actual receipt/disposition이 최종 판단이다.

## 결과 범위

이 결과는 fresh independent exact original6 positive Python CLI publication 관측 PASS다. Prior STATIC no-execution scope는 그 역사적 task에서 그대로 유효하고 이번 explicit new WP에서만6calls가 승인됐다. Capability NONBLANK 회귀·identity/blank broaddomain·producer evidence graph/claim 수정 요구는 계속 OPEN/REVISION_REQUIRED다. Positive6는 rejection/nonblank/Unicode edge-case proof나 일반 안전 계약을 대체하지 않는다.

High4/Engine002006/Pipeline007/currentSchema/GQ1/exactPlayerGlobal/physicalsplit OPEN, whole/native runtime E2 NOT_RELEASED, Foundation HOLD. Current SRS1.6/no1.7migration, 설치 mismatch OPEN/actorUNKNOWN/no restore. DedicatedServer finalDomainAuthority/W-L-G-M/oneLocalClockwriter/islandbarrier/targetpublication 유지. Test publication은 plan-only data이며 canonicalDomain wholesale replacement/engine promotion/server release가 아니다. Master closure/nextrepair/native work disposition PENDING.
