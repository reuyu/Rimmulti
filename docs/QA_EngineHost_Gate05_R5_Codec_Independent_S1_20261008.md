# Gate05-R5 codec 독립 QA S1

**관측된 순수 codec unit 범위 PASS / 정적 계약 수정 필요 / native UNTESTED**. 선택 frozen Debug의 실제 production SerializeCanonicalJson/DeserializeCanonicalJson에 정상 synthetic DTO만 호출했다. 독립 기대값을 먼저 작성한6case·역사65field semantics가 보존됐고, 각 run17assertion 및 두 process의6 canonical JSON byte equality를 확인했다. Collector/admitted loaded content/order/disposition/issuer/native 전체 계약은 이 결과로 인증되지 않는다.

| Identity / scope | 값 |
|---|---|
| WP / revision | WP_QA_ENGINE_GATE05_R5_CODEC_INDEPENDENT / S1 |
| Delivery | SOL-GATE05-R5-CODEC-INDEPENDENT-S1-20261008-01 |
| Unique result | SOL-GATE05-R5-CODEC-INDEPENDENT-S1-20261008-2b7ccd63bcd44eb5ab0c2bd9adb4b959 |
| Producer / 시각 | Sol / 2026-10-08 Asia/Seoul; completed_at은 COMPLETION.json |
| Selected | Debug930B69D012F34BFD3BB50F97B86629BAEA082D201A3A81696549DF1450075AE8 / MVID0e6b7cca-e02c-4af5-97da-5de31ec7aec3 |
| Selected PDB | 06F616C6FD54E07AE87AE2B16E60B1F4AB6FA0AB664D77D71CED084ABC38D2E4 |
| Final QA run | RUN_SOL_R5_CODEC_S1_20261008_077be54754084a6998646e5d4beb77c6 / actual exit0 / PID22128 |
| QA toolchain | SDK10.0.201/Roslyn5.3.0-2.26153.122;net472 ref assemblies;actual CLR4.0.30319.42000 |
| Actual execution | QA runner build1 / managed pure-codec runs2 / selected candidate only |
| Forbidden execution/changes | Production build·source 변경0;actual provider/cache/game/native/operator/task/promotion/A runner/TC11/adverse execution0 |
| Gate | Full Gate05 runtime E2 NOT_RELEASED;Engine002006/Pipeline007/current schema/G-Q1 OPEN;Foundation HOLD |

[Frozen113 manifest](C:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_GATE05_R5_CODEC_REVIEW_FREEZE_MANIFEST.json) SHA `C8FFA291F9B67074AE4C9E916FE2761D3A10D2A691F44F96D58E05E0CDED1692` 및 [managed dependency4 manifest](C:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json) SHA `7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481`의 frozen_path만 사용했다. 원본 Steam/mod DLL/UserData·mutable production은 읽거나 수정하지 않았다. Game/Core/Unity managed files는 허용된 loader/metadata 지원이며 game/native 실행 또는 actual profile admission이 아니다.

양쪽 CodeView/PDB GUID 및 각 source/generated4 document checksum이 matching frozen sources와 맞았다. Alternate Release는 metadata만 검토했고 실제 MVID `7552980a-c4e1-4126-9451-e2114be623ae`가 producer 원문의 copied Debug MVID와 다르다. DLL SHA `77AF633BBA063304E74C9F1D5AE7102CAE856D591201646226AFE6DD23B81EC7`,PDB `E53DE9504FE257D19D789EFD196DA907704690F3F5CD6A5914B3AC7C59E77233`. [R5_LINEAGE.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/R5_LINEAGE.json)에 전체 identity가 있다. Source Census SHA `591408E898E1663732DAF362955248CE6C33CCBD213253D75C56FCE8E999D28C`,Worker `BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718`;Worker/csproj/Census prefix72547bytes R4 동일 여부를 FIXED_SOURCE_SCOPE.json에 기록했다.

독립 input oracle는 build 전에 [INPUT_EXPECTED_SEMANTICS.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/INPUT_EXPECTED_SEMANTICS.json)에 작성했다. BASE,OPTIONAL_NULL,OPTIONAL_EMPTY,NORMAL_REVISION_B,NORMAL_SET_ORDER,OPTIONAL_MISSING6개는 SYNTHETIC_CODEC_INPUT이며 trusted loaded runtime가 아니다. 기대 semantics를 production 출력에서 다시 만들지 않았다. Production DTO/Serialize/Deserialize의 출력 raw UTF8,decoded values,field checks,digest를 각 case 파일로 저장했다. Floating field는 정확한 Single bits,integer는 exact Int64,value/string/boolean/null은 독립 기대값과 비교했다. Unit 함수의 특정 test 개수나 SHA를 권한 증명으로 해석하지 않는다.

| Observed control | 독립 결과 / 제한 |
|---|---|
| 8family65 historical leaf | 65/65 representative semantics PASS;BASE 전체102leaf도 독립 비교. FIELD_COVERAGE_INDEX.json에 type/path/source/result 결속 |
| Unicode/string/precision | Korean/문장부호/quotes/backslash/tab/newline/공백/literal '(null)',finite Float32 precision,큰 Int64 `9007199254740993` 보존 |
| 정상 null/empty/order | nullable strings/optional objects·empty lists,mod/verb/Hediff stages/comp multiplicity·order 보존. Material noninterference는 미검증 |
| Determinism | 동일입력/new DTO/decoded DTO 반복 byte equality;두 run의6 canonical JSON exact SHA equality |
| 정상 content DTO revisions | 값·modVersion이 다른 두 정상 synthetic snapshot의 decoded values/bytes/digest 차이 확인. Actual profile revision/loaded content proof 아님 |
| Set canonicalization | 같은 정상 Biome Def set의 input order가 다르면 serializer bytes도 다름. Collector sort가 canonical boundary이며 sorted-input precondition/normalization 정책 필요 |
| Missing optional | label/race→null,stats→constructor empty list 관측. Missing presence·unknown disposition의 losslessness는 인증되지 않음 |
| Actual patch/settings/profile/cache/native | C12 coverage gaps STATIC;C14~18 및 actual provider/runtime는 UNTESTED_NOT_EXECUTED |

[INDEPENDENT_COVERAGE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/INDEPENDENT_COVERAGE_INDEX.json)은 C01~C13의 PASS_SCOPED/PARTIAL/STATIC_BOUNDARY_GAP을 구분한다. [HISTORICAL65_FIELD_RESULTS.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/HISTORICAL65_FIELD_RESULTS.json)에65row 실제 기대·decoded 비교가 있다. DTO_FIELD_METADATA.json은 실제 DTO Single/Int32/Int64/string/bool/List 타입을 기록한다. 허용된 upstream managed metadata에서는 JobDef.checkOverrideOnDamage가 Verse.CheckJobOverrideOnDamageMode enum임을 확인했으므로 준비 matrix의 provisional boolean을 이번 보고서에서 정정했다. R5는 string으로 운반한다. Ingestible preferability도 enum metadata를 확인했고 기타 upstream type name/width는 미관측이다. Enum-name admission validation이나 actual game field material 의미를 unit strings로 인증하지 않는다.

Master R5-M01~07 핵심 관측에 독립 동의한다. [INDEPENDENT_FINDINGS.md](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/INDEPENDENT_FINDINGS.md)에 source function/line/SHA와 이견·제한을 적었다. Typed records와 DLC exception rethrow 개선은 인정한다. Collector의 null/unknown/empty normalization,patch count/settings 미지원,Comps/set order 의미,cache admission은 지원 contract와 actual loaded evidence가 필요하다. Public serializer의 canonical precondition을 정리해야 하며 모든 null 오류/모든 sort 금지/all RimWorld field 요구는 없다. Remaining operator/MD128/MD129/native는 codec-only scope 밖이다. TACTICAL_PROBE_V5 flag는 unchanged supported semantic V4/MD132 proof를 대체하지 않는다.

Producer12 PASS raw/JSON IDs·order·counts는 맞지만 TC01 bytes roundtrip과65field semantic oracle,TC06 null/empty와 missing,TC07 label과 actual mod/verb predicate,TC08 caller sort,TC10cache helper,TC12flags를 분리했다. TC11은 unexpected-success exception도 catch해 PASS로 기록하며 raw ECall SecurityException은 intended complete admission proof가 아니다. 원래 A runner/TC11은 재실행하지 않았다. Producer21artifact SHA/size,before-after18rows,PDB4/4 개선은 확인했고 Release MVID/tooling/dependency/config/generated/raw semantic graph 문제는 남긴다. 새 QA evidence는 A prior provenance를 소급 보완하지 않는다.

QA [Program.cs](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/Program.cs)는 allowed managed resolver와 순수 DTO codec만 호출한다. 최종 runner MVID `b14a8d59-ce73-4201-81a4-5d3f17d016ec`,SHA `B8524025ED35CA1FB7F900905292787F9CE15BC0CA7206E47E09C9B958C0BFA2`,portable PDB/source1/1 match. Compiler warnings는 BUILD_RAW.txt에 원문 보존. 첫 run의 resolved framework graph post 관측/numeric tool exit 미저장 한계를 RUN1_ARCHIVE로 보존하고 동일 build·input의 새 run2로 pre-pin했다. [PRE_RUN2_MANIFEST.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/PRE_RUN2_MANIFEST.json)→[RUN2_TOOL_PROOF.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/RUN2_TOOL_PROOF.json)→[POST_RUN2_IDENTITY.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/POST_RUN2_IDENTITY.json)은 selected/source/generated/PDB/runner/oracle/managed deps/framework/tooling exact bytes와 actual exit0를 결속한다. ACTUAL_LOADED_MANAGED.json에 actual selected/dependency SHA/MVID/path가 있다. 사후113 freeze를 A execution 전 proof로 소급하지 않았다.

R5frozen113+managed4/prior619/archive19/Pipeline206/QA1241/manifests/terminal의 전후 hash·size 보존은 PRESERVATION_BEFORE/AFTER에 기록한다. Installed incident actor·cause UNKNOWN/OPEN,원본 재독취/restore/정상화 없음. 전체 QA artifact graph는 EVIDENCE_MANIFEST/RESULT_INDEX/COMPLETION,Master 직접 전송 실제 tool proof는 별도 RETURN_TOOL_PROOF/DELIVERY_STATUS에 보존한다. Scoped codec PASS는 full Gate05 runtime E2/release/closure가 아니다.
