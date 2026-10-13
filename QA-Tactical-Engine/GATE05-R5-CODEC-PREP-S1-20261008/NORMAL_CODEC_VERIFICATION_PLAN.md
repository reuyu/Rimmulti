# 후속 independent positive normal codec controls

**현재 모든 row PLANNED_NOT_EXECUTED.** 이번 QA에는 R5 final candidate/freeze/admission과 별도 Master 실행 WP가 발행되지 않았다. 이 문서는 계획이다. Historical R4 및 mutable R5 candidate/runner를 실행하지 않았다. Forged/replay/tamper/bypass/security adverse fixture·공격 절차는 만들지 않는다.

Future control은 admitted production assembly의 **동일 production codec**를 직접 호출해야 한다. 복사한 codec, mock provider/manifest/census/hash, flag equality는 oracle가 아니다. Captured 정상 typed input → canonical bytes → decoded supported values → digest 및 candidate/dependency/source/run identity를 raw evidence로 남긴다. 기대 semantic values는 정상 입력을 기준으로 독립 정리하고 실제 출력만 다시 기대값으로 삼지 않는다. Production이 decode API를 제공하지 않으면 canonical contract에 따라 decode된 값과 원래 typed input을 비교하고 decoder identity/한계를 명시한다. 지원 계약 자체가 의미를 보존하는지 검사한다.

| Control | 정상 대표 범위 / 방법 | 필요한 관측 / 의미 | 현재 상태 |
|---|---|---|---|
| C01 Production linkage | Future selected assembly의 codec entry/DTO 사용, injected hash/provider 없이 정상 encode | SHA/MVID/loaded entry/source/PDB + input/bytes/decoded/digest; 실제 production codec임을 확인 | NOT_RELEASED |
| C02 Scalar roundtrip | 8family65 leaf를 최소 representative set으로 모두 운반; available parent의 supported scalar | 각 field logical type·actual CLR width/enum·value·requiredness가 decoded record에 보존, row ID↔artifact mapping | NOT_EXECUTED |
| C03 String/Unicode | 정상 Korean label/report/name, whitespace, quotes/backslash/구두점, literal 문자열 '(null)' 등 일상 문구 | serializer escaping을 거친 decoded 원문 codepoints/공백/문구 보존; sentinel을 데이터 값과 혼동하지 않음 | NOT_EXECUTED |
| C04 Number precision | 실제 supported float/double/int/long의 정상 captured values와 반복 encode/decode | declared numeric width/range, finite value precision/roundtrip 및 invariant canonical bytes. Supported signed-zero policy 명세; nonfinite 지원을 새로 요구하지 않음 | NOT_EXECUTED |
| C05 Null/absence/empty | API가 확정한 정상 optional race/building/ingestible/reference/label/collection states | ABSENT/NULL/EMPTY와 schema-level omitted field 정책의 값·encoding·disposition 비교. API unavailable을 정상 empty로 대체하지 않음 | NOT_EXECUTED |
| C06 Determinism | 동일 정상 captured typed snapshot을 반복 encode; 허용된 서로 다른 process/library context에서 동일 schema/config | canonical bytes 및 digest exact equality; volatile timestamp/path/presentation state가 결속된다면 명세·snapshot으로 설명 | NOT_EXECUTED |
| C07 Ordered children | 정상 Hediff stages 및 Verb/Comp/기타 ordered 정책의 input sequence | 원래 index/multiplicity/order가 decoded values에 유지. Stable key 정렬은 order irrelevance를 지원 계약이 입증한 collection만 사용 | NOT_EXECUTED |
| C08 Set/map identity | 정상 Def family set/stat/cost/stuff/assembly collection 중 set/map으로 명세한 항목 | Stable key·ordinal comparator·canonical record order, 정상 iteration order 차이에서 같은 semantic set bytes. 의미 있는 multiplicity는 손실 없음 | NOT_EXECUTED |
| C09 Active mod order | 두 정상 승인된 load-order snapshot | 동일 snapshot 반복 안정성, 실제 order decoded 보존; list를 set으로 바꾸지 않음 | NOT_EXECUTED |
| C10 Normal content revisions | 서로 다른 정상 승인 content A/B snapshot을 지원 contract로 encode | changed material field/version/profile가 어떤 typed value/record bytes/digest에 반영됐는지 trace; revision counter만 profile truth라 가정 없음 | NOT_EXECUTED |
| C11 DLC/mod/assembly typed | 정상 AVAILABLE/disabled/확정 no-DLL mod 등 명세된 상태 | exact inventory/reference/type/SHA/MVID/long size/version/order가 typed records로 보존; unavailable 자료는 별도 disposition | NOT_EXECUTED |
| C12 Patch/settings supported | 정상 admitted patch/settings source 또는 actual applied content snapshot | count-only가 아닌 지원 identity evidence와 typed canonical records/digest 결속. 미지원 필수 material은 성공 결과 아님 | NOT_EXECUTED |
| C13 Coverage accounting | 65leaf + content matrix rows의 captured 정상 input/oracle/result inventory | row별 VERIFIED_CODEC/UNOBSERVED/UNSUPPORTED/OPTIONAL_DISPOSITION, 축약 projection과 full property graph를 구분. 총 PASS count만으로 coverage100% 금지 | NOT_EXECUTED |
| C14 Worker loaded profile | 승인된 정상 loaded game/core/mod/DLC/config/Def snapshot에서 provider compute | actual runtime inputs→typed canonical manifest→digest, no whole-provider mocks; approved expected profile와 비교 | UNTESTED_RUNTIME |
| C15 Validator loaded profile | 별도 승인된 READ_ONLY validator가 자기 loaded content에서 같은 schema compute | exact independent candidate/dependency/content/config/process/run의 actual profile; Worker 결과 복사로 대체하지 않음 | UNTESTED_RUNTIME |
| C16 Cache/admission lifecycle | approved immutable content snapshot의 profile generation 및 명시 re-admission | cached bytes/digest snapshot identity, 실제 invalidate 후 recompute/clean admission; helper IsCached=false만으로 부족 | UNTESTED_RUNTIME |
| C17 Native issuer/lifecycle | operator workload/task/staged exact bytes/fresh loader/census/result/consume/receipt 정상 flow | operator-owned admitted identity, MD128/MD129 state, semantic V4/load/promotion evidence | OUTSIDE_R5_CODEC / UNTESTED |
| C18 Whole gate | 후속 admitted 통합후보와 별도 Master E2 WP | codec/actual loaded profile/native issuer scopes가 각각 충족돼야 검토; old E1/E2/fixture verdict 재사용 없음 | NOT_RELEASED |

Normal unit data는 현재8family 지원 필드를 충분히 대표할 수 있어야 한다. 모든 family가 game state owner라는 뜻은 아니고 전체RimWorld schema를 test generator에 복제하라는 뜻도 아니다. Optional normal states의 합리적 normalization은 의미 보존 근거와 supported contract가 있을 때 평가하며 이름만 lossless로 붙이는 것을 검증으로 보지 않는다. 비교가 어려운 field는 UNOBSERVED/UNSUPPORTED로 남긴다.

자료 묶음: CONTRACT_VERSION + INPUT_SNAPSHOT(raw values/types/states/order/source) + PRODUCTION_ENTRY_IDENTITY + CANONICAL_BYTES(raw exact UTF8) + DECODED_SEMANTICS + DIGEST + EXPECTED_NORMAL_ORACLE + RESULT_ROW + RUN_LOG + PRE_RUN/POST_RUN_GRAPH. Executed codec proof와 실제 loaded-content proof는 별도 label로 보고한다. 현재 A R5는 codec-only E1 normal controls를 수행할 수 있지만 QA 준비 작업은 실행을 승인하지 않는다.
