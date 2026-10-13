# QA — EngineHost Semantic Authority Gate05

**독립 판정: FAIL.** 정상 native 기능 검증은 완료했지만, 요청자와 operator/validator 사이의 발급자 경계 및 gameplay content fingerprint 계약은 정적 검토에서 충족되지 않았다. 아래 결과는 fresh independent 실행과 읽기 전용 source/PDB 검토를 결합한 **범위가 제한된 E2**다. 필수 공격성 음성 사례 전부를 실행한 PASS 보고서가 아니다.

Reviewer: Sol / Independent QA. Thread `01a11583-ff90-73e0-8916-d021e2bb038d`. WP `WP_QA_ENGINE_GATE05`, Gate05 revision. Attempt `SOL-GATE05-E2-RESTART-8f58fb41362f4934a502e604a65f5896`. 완료 시각 `2026-10-07T18:30:57.461176+09:00` (Asia/Seoul). Master만 결함 closure와 release를 결정한다. 삭제된 이전 대화의 실행/PASS와 E1 자체 결과를 fresh E2로 승계하지 않았다.

## 검증 계약과 실제 실행 범위

Canonical 원문은 [요구사항_명세서.md](/C:/Users/user/Desktop/RimMulti/docs/요구사항_명세서.md)다. ADR-003/004/006A/006B/007 core acceptance는 MAC-001, MD-056/113/114/126..132와 controlling C correction을 함께 적용했다. Server가 final Domain Authority이며 Worker 결과는 bounded proposal이다. 이 QA의 final은 QA-owned profile의 PoC 저장 파일이고 canonical Production commit이 아니다.

선언된 PoC threat model에서 trusted operator/simulator가 validator task와 실제 실행/result channel을 소유해야 한다. 일반 requester는 검증을 요청할 수 있지만 임의의 issuer나 expected truth를 승격 근거로 지정할 수 없다. 전체 관리자/파일 시스템을 다시 쓰는 공격까지 방어한다는 요구는 추가하지 않았다. Loopback이라는 사실을 모든 요청자에게 operator 권한을 주는 근거로 채택하지 않았다.

새 QA-owned profiles와 복사 fixture에서 설치된 native RimWorld를 `-batchmode`로 직접 시작했고 프로세스 handle/PID/시각/argv, native load/command 응답, V4 census, task/receipt, stage/final/backup SHA를 저장했다. QA는 observer나 candidate를 재빌드·배포·교체하지 않았다. 정상 validator 결과만 사용했다. 우회/위조 재현, unrelated live-PID 수락 시도, replay/context tampering 및 content/saved-field corruption 재현은 실행 범위 제한으로 **UNTESTED**다. 이들을 PASS 또는 후보가 안전하다는 증거로 계산하지 않는다. 작은 malformed XML, 정상 READ_ONLY 및 malformed grant rejection은 별도 방어적 smoke control로 실행했다.

## Exact candidate / provenance

| 항목 | 독립 확인값 |
|---|---|
| 선택 및 실제 설치 PoC DLL SHA | `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C` |
| PE MVID / 실제 크기 | `12bb9237-1b3e-4b20-89a7-69ad729861e1` / 166,400 bytes |
| matching Debug PDB SHA | `4B86A8634C8B13D2A20EA51D27B5A9F7B067FA976A8C0503107C18C5A7656862` |
| DLL CodeView / PDB GUID | `3749afca-3905-4d55-a151-cc7e75b85649`; 직접 portable PDB source/generated checksum 4/4 MATCHED |
| WorkerBridge.cs SHA | `BC9FD8DAA608892E97903BA56114B7186BABF29157ADAE45658238C3DD497549` |
| EngineHostCensus.cs SHA | `954C12F7500EC0BF4AE8265D2F66EFA39369A69F2C9DF3D1DBA20A9F54CBD024` |
| RimWorld executable SHA | `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D` |
| Assembly-CSharp SHA / MVID | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` / `61e41735-6189-4da4-9d21-0260257b5097` |
| clean fixture SHA | `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B` |
| clean V4 JSON SHA / declared manifest digest | `9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC`; 이 파일과 native serialized JSON에서 같음을 실제 계산 |
| native loaded-profile fingerprint | 모든 credited simulator/validator에서 `7DDC73B75FA4AA1B00177EA4C73380A7E233A972968D5C0BF91852CD1C2F8D40` |

matching PDB는 `scratch/WorkerBridgeMod/Source/bin/Debug/net472`의 별도 lineage 자료다. 다른 Release DLL과 배포 동반 PDB는 제외했다. 독립 byte/PE/PDB 근거: [SOL_RECOVERY_IDENTITY_20261007.json](/C:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/coordination/SOL_RECOVERY_IDENTITY_20261007.json); 새 복사 자료: [frozen-copy-index.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/frozen-copy-index.json). 각 native process는 자체 profile provider를 실행했지만 별도 QA module observer로 loaded DLL image를 추출하지는 않았다. PE/on-disk freeze와 native fingerprint/실제 API 동작을 결합한 식별 근거이며 모든 프로세스 메모리의 독립 attestation은 아니다.

E1 harness의 보고서 SHA `019CFB...`와 실제 `4B7F1199...`, E1 results의 보고서 SHA `BE2C130A...`와 실제 `DA193776...`는 여전히 불일치한다. 정확한 full hash는 identity evidence에 있다. cosmetic change로 정상화하지 않았고 원인도 확정하지 않았다. QA는 복사한 E1 harness를 실행하지 않았다.

## 정상 runtime 및 실패 보존 결과

| 실행군 | 내부 checkpoint 수 | 통과 checkpoint | fresh process 수 | 실제 원문 |
|---|---:|---:|---:|---|
| positive_chain | 52 | 52 | 5 | [native-positive-results.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/native-positive-results.json) |
| input_hygiene | 14 | 14 | 1 | [native-positive-results.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/InputHygiene/native-positive-results.json) |
| normal_replacement | 38 | 38 | 3 | [native-positive-results.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/ReplacementWithoutLockUnsandboxed/native-positive-results.json) |
| lock_and_recovery | 60 | 60 | 4 | [native-positive-results.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/ReplacementUnsandboxed/native-positive-results.json) |

Checkpoint는 각 protocol 응답·SHA·load·state predicate의 기록 수다. 독립 보안 사례 수나 필수 WP의 완전한 coverage 수가 아니다. 모두 통과한 이 실행군으로 Gate05 security PASS를 추론하지 않는다.

| 체인 | Simulator/consumer PID | Validator PID | 입장 engine G | 입력 SHA | final SHA | 봉인/입장 V4 digest |
|---|---:|---:|---:|---|---|---|
| A | 32908 | 28380 | 1823 | EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B | 58FBBC14F04208DC50CF7BEDABEDE2A210E2281B07D998378ECFE4141173C7A7 | 25C35E3B846E33E987B62F59A3A8FCE22E54466C922F086A25184982E197013C |
| B | 19364 | 26780 | 1828 | 58FBBC14F04208DC50CF7BEDABEDE2A210E2281B07D998378ECFE4141173C7A7 | 49DD4ED5A8D0E7A26F2259043A6476AF3EE927A4AD757886D546316F38902939 | 6C41F21786A7C78C6EFD13AFF4E0300B06E7619B937BCD5866955F0A4973F79F |
| C | 29804 | — | 1833 | 49DD4ED5A8D0E7A26F2259043A6476AF3EE927A4AD757886D546316F38902939 | consumer only | 6C41F21786A7C78C6EFD13AFF4E0300B06E7619B937BCD5866955F0A4973F79F |

A/B는 각각 허가된 5 tick을 실제 실행했다. Native G는 1823→1828→1833이며 Server W나 canonical Settlement L 구현 전체를 인증하는 수치가 아니다. Fresh distinct validator는 SHA-identical staged copy를 실제 로드했다. QA가 native `ToJson()` bytes의 SHA를 별도로 계산했고 전체 declared V4 object를 봉인 manifest JSON과 비교했다. A/B stage SHA=final SHA이고 C가 B 결과를 새 프로세스에서 로드해 동일 digest를 확인했다. QA의 실제 validator launch/handle proof는 기능 관측이며 candidate 내부 issuer 인증의 대체물이 아니다.

Input hygiene: EOF, second root, 내부 선언만 있는 작은 DTD fixture는 실제 LOAD preflight에서 거부됐다. 정상 clean READ_ONLY load는 성공했고 STEP/SEAL은 거부되며 전체 census와 tick이 유지됐다. Malformed grant는 input readiness를 VALIDATION_FAILED로 바꾸고 STEP/SEAL/STAGE/PROMOTE를 차단했다. 이는 **valid READ_ONLY input 상태에서의 검사**이며 outstanding seal/stage/receipt가 있는 모든 실패 경로의 revocation을 증명하지 않는다. XML 사례도 fresh staged semantic rejection으로 재명명하지 않는다.

Promotion: first-final move, 정상 existing-final replacement와 정확한 prior-file backup이 실제 통과했다. QA-owned final에 delete sharing을 막는 실제 handle을 잡았을 때 File.Replace가 실패했고 기존 final과 stage SHA가 보존되며 readiness가 해제됐다. Handle 해제 후 명시적 reset, 새 load/task/validator로 재검증한 교체는 성공했다.

초기 sandbox native replacement와 별도 .NET small-file primitive가 Access denied로 실패했다. 승인된 unsandboxed primitive 및 **새 native profiles**에서 정상 교체와 실제 lock→preserve→reset→replace가 성공했다. 따라서 sandbox 결과를 candidate atomic-replacement 결함으로 채택하지 않는다. 실행환경 차이 및 원본 실패는 [execution-environment-diagnostic.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/execution-environment-diagnostic.json)에 보존했다. Machine crash/power loss 또는 모든 파일 시스템의 atomicity는 검증하지 않았다.

## 독립 정적 FAIL / 열린 경계

**G05-S01 — CRITICAL — validator 발급자·task 실행 결속 부재.** Task nonce가 같은 request surface에 노출되고 task query에서도 제공된다. Completion/debug intake는 전달된 값의 equality와 다른 현재 살아 있는 PID를 확인하지만 simulator가 시작한 정확한 validator handle/executable/generation 및 보호된 result channel을 확인하지 않는다. 형식상 nonce와 내부 receipt 생성만으로 requester/operator 경계가 성립하지 않는다. 근거: [WorkerBridge.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1909), [WorkerBridge.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:2028), [WorkerBridge.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:2175). 실제 bypass 또는 forged publication은 이번 실행에서 재현하지 않았다. 권고: orchestrator-only task/capability 접근, launched-validator 등록과 protected channel의 result acceptance, authority를 변경하는 debug intake 제거 후 fresh E2.

**G05-S02 — HIGH — gameplay content semantics를 포함하지 않는 Def digest.** Core/mod assembly SHA/MVID와 load order는 포함된다. 그러나 Def digest는 Thing/Hediff/Skill/Job의 defName/label만 사용한다. 실제 gameplay 필드, 다른 Def 계열과 content/patch XML identity가 빠져 있어 동일 name/label을 가진 gameplay 내용의 차이를 그 digest로 구별할 수 없다. 이것은 count-only보다 개선됐지만 MD-130의 authority-relevant semantic content coverage를 충족하지 않는다. Provider는 첫 값을 cache하며 reviewed bridge/census에서 InvalidateCache 호출도 없다. 근거: [EngineHostCensus.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:1505), [EngineHostCensus.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:1581). 실제 content drift 주입은 실행하지 않았다. 권고: admitted gameplay Def/patch/content/schema/codec 경계와 digest를 정의하고 fresh independent loaded-content 검증을 추가한다.

**G05-O01 — concurrency UNTESTED.** Stage hash read handle은 move/replace 전에 닫힌다. 그 사이의 stage immutability/held-handle 보호는 확립되지 않았다. 정상 실행에서 단계별 SHA 안정성은 관측했지만 concurrent bad publication이나 TOCTOU corruption을 재현한 것은 아니다. [WorkerBridge.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:2559).

**G05-O02 — XML helper 반환값의 한정.** expected JSON이 없는 helper 경로는 구조 parse 뒤 supplied expected hash를 반환한다. 이는 독립 saved-byte manifest 계산이 아니다. 이번 정상 검증의 근거는 실제 fresh native census equality다. [EngineHostCensus.cs](/C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:1260).

정적 분석 원문/line 범위: [static-review.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/static-review.json). Genuine issued 7개 task/receipt에서 16개 context field equality도 별도로 계산했다: [genuine-context-field-comparison.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/genuine-context-field-comparison.json). 이는 잘못된 field를 보내는 mutation matrix나 issuer proof가 아니다. Result/current epoch의 inconsistent-state fault, unrelated live process, replay/stale-generation, substituted expected task, full context mutation, saved supported-field corruption, core/mod/DLC/Def drift, concurrent stage change는 **UNTESTED**로 남긴다.

## 필수 WP 추적표

| WP | 실제 근거 / 미검증 범위 | 판정 |
|---:|---|---|
| 1 | fresh file/PE/PDB + original E1 hash drift 명시 + QA manifest | identity MATCHED / provenance finding OPEN |
| 2 | QA operator의 genuine task/native launch/result 관측; candidate issuer binding 부재 | 기능 관측 / G05-S01 FAIL |
| 3 | nonce/requester 경계 및 PID binding 정적 검토; unrelated PID/replay/stale negative 미실행 | G05-S01 FAIL / 나머지 UNTESTED |
| 4 | own seal hash와 실제 loaded JSON equality; 보호된 task/result origin 미증명 | 정상 equality 확인 / authority HOLD |
| 5 | 여러 fresh native validator staged load | 정상 control 확인 |
| 6 | 7 genuine records ×16 field equality, promotion predicate 정적 확인; adversarial context/current-epoch matrix 없음 | PARTIAL |
| 7 | malformed grant/input readiness, READ_ONLY, lock failure revocation; budget/re-grant/reseal 등 음성 경로 없음 | PARTIAL |
| 8 | distinct processes 자체 fingerprint 일치; semantic Def coverage 부족, drift 주입 없음 | G05-S02 FAIL / negative UNTESTED |
| 9 | 정상 stage/validation/final SHA equality; concurrent interval 미검증 | PARTIAL |
| 10 | 정상 native saved equality + input parser hygiene; saved-field corruption negative 없음 | PARTIAL |
| 11 | first final, actual lock preserve/revocation, approved native normal replace/backup; unsafe overwrite fallback 없는 코드 확인 | 관측 범위 PASS / crash durability OPEN |
| 12 | fresh A→B→C + full declared V4 JSON equality | 정상 기능 PASS / security 인증 아님 |
| 13 | bounded V4 선언 및 unsupported dimensions 기록 | 범위 명시 완료 |

## Freeze / 지원 범위 / 권고

Before/after **2,255→2,255 files, SHA/size/identity 변경 0**. Bootstrap 19개 항목도 사전 재확인했고 phase별로 대조했다. 범위는 명시된 Engine/source/managed assembly/content XML 및 Production file inventory이며 전체 OS나 외부 저장소 보존을 인증하지 않는다. [freeze-before.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/freeze-before.json), [freeze-after.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/freeze-after.json), [freeze-comparison.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/freeze-comparison.json). Git repository/HEAD/clean은 확인되지 않았고 초기화하지 않았다.

Credited fresh processes 13개, QA interruption/sandbox diagnostic을 포함한 owned process instances 21개가 모두 exit0으로 종료했다. Forced cleanup 및 무관한 프로세스 종료는 없었다. [cleanup.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/cleanup.json). QA는 기존 Master governance 및 원본 recovery ACK bytes를 변경하지 않았다. UTF-8 canonical SRS 경로 정정은 별도 [SOL_RECOVERY_ACK_UTF8_CORRECTION_20261007.json](/C:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/coordination/SOL_RECOVERY_ACK_UTF8_CORRECTION_20261007.json)이다.

V4 baseline은 31975 entities, 48 animals, 1 bill과 nonempty GotoWander JobDef/loadID/target records를 포함한다. Baseline reservations는 0이어서 nonempty reservation persistence를 별도로 주장하지 않는다. 완전한 JobDriver/toil/path/expiry/queue, 전체 save/global graph, 모든 mod, 최소 dependency closure, G-Q1, exact PlayerGlobal ownership/physical split, W/L temporal implementation, Material Production/Trade/Tax/Foundation integration은 인증하지 않는다. Tales/PlayLog/Storyteller/Weather discardability 또는 separate-process zero drift도 채택하지 않았다.

**QA-ENGINE-002: OPEN / independent issuer-content contract FAIL 권고. QA-ENGINE-006: OPEN 유지 권고.** 정상 supported saved equality는 확인했지만 필수 adverse closure evidence를 완성하지 못했다. 새 candidate 수정·재빌드가 있으면 이 evidence를 그대로 재사용하지 않고 새 freeze와 targeted regression 및 필요한 fresh E2를 수행한다. Foundation HOLD와 G-Q1/정확한 global schema의 OPEN은 유지한다. Master의 scoped disposition 전 closure/release는 없다.

Completed raw summary: [independent-summary.json](/C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/Evidence/independent-summary.json). QA evidence hash inventory는 `qa-evidence-manifest.json`, completed result index는 `docs/WarEconomy_Master_Handoff_20261006/coordination/SOL_GATE05_E2_RESULT_INDEX_20261007.json`에 저장한다. 해당 index의 delivery block/sidecar가 실제 Master 보고 상태를 통제한다.
