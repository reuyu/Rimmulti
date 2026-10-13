# R6 codec contract 독립 QA S1

**관측한 정상 codec·positive helper 범위 PASS / 정적 계약 수정 필요 / native UNTESTED**. Fresh R6 production Serialize/Deserialize/CanonicalNormalize 및 정상 fully declared manifest의 ValidateContract만 호출했다. 6개 정상 synthetic case·각 process25assertion·역사65field semantics를 확인했고,별도 en-US/de-DE process의6 canonical JSON이 byte 단위로 같았다. Helper를 실제 profile admission과 연결한 증거는 없으며 R5 PASS를 승계하지 않았다.

| Identity / scope | 값 |
|---|---|
| WP / revision | WP_QA_ENGINE_GATE05_R6_CODEC_CONTRACT_INDEPENDENT / S1 |
| Delivery | SOL-GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008-01 |
| Unique result | SOL-GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008-562ad497021b4c36bd59c08df730b7ed |
| Time | Sol / 2026-10-08 Asia/Seoul;terminal completed_at은 COMPLETION.json |
| Selected Debug | 721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B / MVIDb3481641-2711-4b0e-96dd-db0983c2b689 |
| Matching PDB | 47FA9E93D5768175BF61EAB204CB4ED1BF6B45194407AA536F363B3497671C63 |
| QA execution | New runner build1 / managed positive normal runs2 / both actual tool exit0 |
| Framework | SDK10.0.201/Roslyn5.3.0-2.26153.122;net472 refs;CLR4.0.30319.42000;en-US/de-DE |
| Forbidden operations | Production modification/rebuild0;provider/compute/getter/cache/game/native/operator/old runner/TC11TC13/rejection/adverse0 |
| Gate | Full runtime E2 NOT_RELEASED,Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD |

유효 후보는 [manifest112](C:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe/MASTER_GATE05_R6_CODEC_CONTRACT_REVIEW_FREEZE_MANIFEST.json) SHA `61BCABD85920C84B978FD9E826DEB672B45F0935D5CC329C33A88F002A90CEEA`의 frozen_path다. Valid root는 `C:\Users\user\Desktop\RimMulti\Dispatcher\CANDIDATES\G05R6-1f657abe`이며 초기 long-path partial folder는 UNADMITTED로 사용하지 않았다. Managed loader/metadata는 승인된 frozen4와 후보의 Newtonsoft.Json만 사용했다. 원본 Steam/mod DLL/UserData 및 mutable Source/bin/obj를 후보로 읽지 않았다.

Debug/Release 실제 PE MVID,CodeView/PDB GUID,각4 document source/generated checksum이 matching frozen source와 맞았다. Alternate Release는 실행하지 않았고 SHA `2E6D66A16D2932155261034915E23B74B1BD73A0D28EE3D9F447A67152E2D3BC`/MVID `354737fd-10a8-4160-8307-3e186c2118e6`/PDB `3FF4D9F3ECF99D54857FD95A033CCDCE21786BE5722032A9DE5A46875B98C1BE`로 결속했다. [R6_LINEAGE.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/R6_LINEAGE.json)에 전체 metadata가 있다. Source Census SHA `E94EA163BD6041C1ACA057D7E698277C0165E7F535FBCDBB765F3F68929348B5`,WorkerBA28…/csproj571A…/Censusprefix72547bytesF3C4… fixed 비교는 FIXED_SOURCE_SCOPE.json에 있다.

Fresh [INPUT_EXPECTED_SEMANTICS.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/INPUT_EXPECTED_SEMANTICS.json)을 build 전에 작성했다. 역사 R5 입력 layout은 설계 참고만 했으며 새 후보 API와 normal key/order semantics에 맞춰 별도 기대값을 지정했다. 정상 distinct set keys와 loadOrder를 기준으로 예상 canonical order를 독립 정의했고 ordered verbs/stages/comps/multiplicity는 그대로 유지했다. Production output을 기대값으로 역생성하지 않았다. 모든 input은 SYNTHETIC_CODEC_INPUT이며 actual trusted loaded content가 아니다.

| 독립 관측 | 결과 / 제한 |
|---|---|
| Historical65/current DTO | 65representative leaf semantics PASS;BASE149leaf 독립 비교. 실제 DTO Single/Int32/Int64/string/bool/List metadata 결속 |
| String/number/optional | Unicode/구두점/quotes/backslash/공백/tab/newline/literal '(null)',finite Float32 bits·integer·큰Int64,normal optional null/empty 보존 |
| Canonical true / Normalize | 서로 다른 정상 set input order가 같은 bytes/digest로 정규화됨;Normalize와 default Serialize가 기대값과 일치 |
| Transport false | 원래 supplied order와 정상 typed values 보존;canonical profile 구성과 generic DTO transport 분리 |
| Ordered/multiplicity | 선언된 mod loadOrder와 verbs/Hediff stages/comps 순서·Comp multiplicity 보존;material noninterference proof 아님 |
| In-place mutation | same DTO의 before/after transport bytes가 canonical normalization으로 바뀜을 기록;caller mutation contract 필요 |
| Positive ValidateContract | fully declared BASE/NORMAL_REVISION_B2개에서 true/empty reason;실제 admission 연결·거부 동작 인증 아님 |
| Determinism | 동일입력/new/reconstructed DTO 및 en-US/de-DE2process6 canonical pairs byte equality |
| Normal revisions | 두 정상 synthetic revision의값/version/bytes/digest 변화 관측;general collision-resistance proof 아님 |
| Missing/unknown/ties/native | Optional missing→constructor null/empty defaults 관측. Required unknown/unavailable,tie-key policy,actual loaded profile/cache/native는 미관측/STATIC/UNTESTED |

Raw UTF8 canonical/transport,decoded values,독립 semantic checks,Normalize checks,mutation before/after digests를 각 case 파일로 저장했다. [FIELD_COVERAGE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/FIELD_COVERAGE_INDEX.json)와 [INDEPENDENT_COVERAGE_INDEX.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/INDEPENDENT_COVERAGE_INDEX.json)에 scope별 관측·미관측을 구분했다. Native Job damage-mode/food-preference enum을 허용된 metadata에서 확인했지만 synthetic string의 enum/class admission이나 다른 upstream type name/width 전체를 인증하지 않았다.

[Independent findings](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/INDEPENDENT_FINDINGS.md)에 R6-M01~08의 독립 동의/제한·source function/line/SHA를 남겼다. Canonical 경계/Comps order/일부 top-level missing 오류/actual MVID/capability V4 label 개선을 인정한다. ValidateContract는 정의만 있고 production Serialize/collector/fingerprint 호출이 없어 unwired helper다. Checks도 report-required material을 전부 운반·검증하지 않는다. Collector child skip/fallback·assembly inventory·optional/default/count projection과 required disposition이 남아 있다. Document-only patch/settings exclusion은 profile admission에서 강제되지 않으며 CONTENT_CONTRACT_VERSION 상수는 자체적으로 manifest/승인 binding이 아니다. 같은 key/tie/multiplicity policy와 좁은8family nonempty 가정을 명시해야 한다. 모든 null/Def/sort 실패나 새로운 global owner schema를 요구하지 않는다.

Producer14 raw/JSON PASS IDs/order/count는 맞다. TC13은 금지된 InvalidateCache/cache properties 실행으로 승인된 normal codec evidence와 lifecycle proof에 포함하지 않는다. TC11은 올바른 failed-return predicate를 가진 non-positive 형식 검사이며 R5 ECall/catch 오류와 혼동하지 않는다. QA는 두 항목·producer/old QA runner를 실행하지 않았다. TC03family count/TC04numeric sample/TC06missing scope/TC12두 revision/TC14flags를65field·all-bit·missing presence·collision·runtime authority proof와 분리했다. PRODUCER_COVERAGE_INDEX.json에14row를 기록했다.

Producer21 artifact SHA/size,18before-after row 및 actual Debug/Release MVID/PDB 개선은 검증했다. Pre-run generator의19:30 hardcoded timestamp/SDK8.0+와 compiler/dependency/generated/config/input/raw-byte/run chronology graph 공백은 남긴다. Producer packaging index에 exact 원문을 보존했다. 새 QA evidence나 사후112 freeze로 A pre-run authority/chronology를 소급 인증하지 않는다.

New [Program.cs](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/Program.cs)의 허용된 method/DTO만 실행했다. 두 process 모두 마지막 같은 runner build 뒤 exact selected/source/generated/PDB/input/managed deps/resolved OS framework/toolchain을 pre-pin하고 actual numeric tool return·raw·post unchanged를 저장했다. [PRE_RUN1_MANIFEST.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/PRE_RUN1_MANIFEST.json),[PRE_RUN2_MANIFEST.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/PRE_RUN2_MANIFEST.json),[RUN2_TOOL_PROOF.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/RUN2_TOOL_PROOF.json),[POST_RUN2_IDENTITY.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008/POST_RUN2_IDENTITY.json)로 결속했다. RUN1_ARCHIVE는 첫 새 R6 process의 raw case evidence를 보존하며 incomplete run이나 R5 inherited result가 아니다. Compiler warnings는 BUILD_RAW에 원문 보존했다.

R6frozen112/previous732/archive19/Pipeline206/QA1342/managed4/manifests/terminal2453 unique paths를 전후 실제 hash·size로 보존했다. Installed incident actor/cause UNKNOWN/OPEN,원본 installed/UserData 재독취/restore/정상화0. 최종 graph는 EVIDENCE_MANIFEST/RESULT_INDEX/COMPLETION,Master direct tool 증거는 별도 RETURN_TOOL_PROOF/DELIVERY_STATUS에 남긴다. Operator/MD128/MD129/native와 full Gate05 E2/closure는 미승인 범위이며 Foundation HOLD다.
