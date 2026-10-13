# Gate05-R5 codec 독립 검증 준비 S1

**PREPARATION_COMPLETED_NO_R5_CANDIDATE_VERDICT**. Historical frozen R4의 실제 supported8 Def family를65 leaf field로 추출하고 type·requiredness·material 의미·null/missing/empty·collection identity/order를 표로 만들었다. Normal production codec 검증18 row와 final candidate provenance12 row를 준비했다. 새 R5 구현/candidate/codec 실행은 검토하지 않았다.

| Identity / scope | 값 |
|---|---|
| WP / revision | WP_QA_ENGINE_GATE05_R5_CODEC_PREPARATION / S1 |
| Delivery | SOL-GATE05-R5-CODEC-PREP-S1-20261008-01 |
| Unique result | SOL-GATE05-R5-CODEC-PREP-S1-20261008-718bbcc37d1147dc8f44476b979059a7 |
| Producer / 시각 기준 | Sol / 2026-10-08 Asia/Seoul; completed_at은 COMPLETION.json |
| Historical candidate | R4 frozen232, manifest SHA D047D0095CEDDA8E5F0FB6871EA4C24AF0866CA569514049FFAD7E91B7C1460C |
| QA 경계 | Mutable R5 source/bin/obj read0; candidate/runner/game/native execution0;build0;production 변경0;adverse reproduction0 |
| Release / closure | Runtime E2 NOT_RELEASED,Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD |

[Supported field matrix](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008/SUPPORTED_FIELD_MATRIX.md)와 [machine-readable65 rows](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008/SUPPORTED_FIELD_MATRIX.json)는 frozen EngineHostCensus.cs의 ContentProfileProvider.ComputeActualContentProfileFingerprint를 function/1-based line/SHA로 결속한다. Source SHA `09D57DF883576733C2BD4F40FBDE2C616E374FF1EFCCA50A4466C26DD6AA1333`. ThingDef의 stat/race/building/ingestible/cost/stuff/verb/comp, Hediff stage/comp, Job/Skill/Faction/Biome/Weather/Research 필드를 모두 현재 운반 범위 기준으로 정리했다. Label/report 등 baseline presentation fields를 material 비영향으로 자동 제외하지 않았다. Upstream numeric CLR width/enum metadata는 source 표현만으로 확정하지 않고 후속 admitted dependency 확인 대상으로 남겼다.

필수 scalar는 optional parent가 AVAILABLE일 때만 필요하다. 정상 optional object 부재를 오류로 바꾸지 않으며 UNKNOWN/API_UNAVAILABLE를 정상 null/empty와 분리한다. Ordered list는 실제 index/multiplicity/order를 보존하고 set/map은 의미상 order irrelevance와 stable key가 명세된 경우만 canonicalize한다. Class name만 unique collection key라 가정하지 않는다. 모든 Def field/모든 sort 금지/global ownership schema를 새로 요구하지 않았다. Faction pawnGroupMakers count, comp class-only와 verb class/range는 full property graph proof가 아니다.

[Content coverage matrix](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008/CONTENT_COVERAGE_MATRIX.md)는 core SHA/MVID/build, mod package/name/version/actual load order, loaded assemblies SHA/MVID/size, DLC/status/linked package, patch/settings, Def digests/capabilities 및 cache/lifecycle을 정리했다. R4의 actual assembly/Def census/R-format/cost fields/cache invalidation/DLC 추가를 인정하면서 delimiter/sentinel/opaque inner digest와 patch count를 typed lossless coverage와 분리했다. 필수 material 자료가 unavailable/unknown/unsupported라면 trusted fingerprint 성공으로 묵인하지 않는 disposition이 필요하다. Profile lineage/revision과 exact fingerprint는 별도이며 이번 codec에 새 물리적 global schema를 강제하지 않는다.

[Positive normal codec plan](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008/NORMAL_CODEC_VERIFICATION_PLAN.md)은 실제 production codec entry를 사용한65field semantic roundtrip, exact canonical bytes/digest determinism, Unicode/escaping/whitespace, 숫자 정밀도, 정상 optional states, ordered/set/map semantics, 두 정상 admitted content snapshot의 의미 변화와 coverage accounting을 다룬다. 계획은 version constant/mock provider/manifest/census/hash PASS를 oracle로 삼지 않는다. Unit codec proof와 actual loaded profile/Worker·validator 독립 계산/cache admission/native issuer lifecycle을 분리하며 latter runtime rows는 UNTESTED다. 모든 계획은 NOT_EXECUTED, future admitted candidate와 별도 Master 실행 WP를 요구한다.

[Provenance acceptance](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008/PROVENANCE_ACCEPTANCE.md)는 R4 pre-run5 final identity 차이/before7 size 오류를 concrete acceptance로 연결했다. 마지막 build 뒤 run 전 정확한 selected/alternate SHA·size·MVID/PDB·CodeView·source/generated/dependency/tooling/content/config/run_id를 고정하고 post-run unchanged를 비교해야 한다. 변경 후 old pre-run/evidence 재사용과 사후 snapshot 소급은 허용하지 않는다. R4 final report9/Completion18 match 개선을 유지하면서 R5는 표준 limitations string/list/absolute role/hash/size를 실제 bytes에서 계산해야 한다.

[Evidence boundaries](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008/EVIDENCE_CLASS_BOUNDARIES.md)에 codec unit·actual loaded profile·cache/lifecycle·native issuer·whole gate의 의미를 구분했다. R5 codec만으로 admitted operator/workload/MD128/MD129/native proof가 해결되거나 Engine002006 closure가 된다고 주장하지 않는다. Dedicated Server final authority/controlling C/MD125~132를 유지한다. A는 단일 source writer로 codec/content만 작업 중이며 QA는 mutable 후보를 읽거나 변경하지 않았다. Existing hourly scheduling은 실제 A dispatch에 따른 Master 운영 사항이며 QA가 변경하지 않았다.

Historical R4 selected Debug SHA `4F5663FDBBFA09A8B2BE460D09950FD22B9567459F7116E69D0B1C558F189B9E`,MVID `ed98e6f9-aa63-47ee-ae21-84f59465d2bb`; alternate Release SHA `7532FF152314892A4AB95A0117107C0845B0D7BAD170C3B840BA24F3EADA270B`,MVID `d602525d-4248-442a-8f51-77e22f8484bf`를 역사 reference로만 사용했다. Metadata-only PDB checks는 양쪽 CodeView/document4/4가 matching frozen source와 일치했다. 새 R5 lineage로 승계하지 않는다. R4frozen232/prior387/archive19/Pipeline206/QA1222 및 manifests/terminal 전후 hash·size 보존은 PRESERVATION_BEFORE/AFTER에 남기고 report/evidence/index/completion graph는 EVIDENCE_MANIFEST/RESULT_INDEX/COMPLETION에 결속한다. Installed incident actor/cause UNKNOWN/OPEN,원본 installed/UserData 재독취·restore·정상화 없음.

완료 준비 결과는 R5 candidate admission/독립 codec 실행/E2/closure가 아니다. 기존 승인에 따라 Master에게 직접 보고하며 실제 tool 반환은 RETURN_TOOL_PROOF/DELIVERY_STATUS에 따로 보존한다.
