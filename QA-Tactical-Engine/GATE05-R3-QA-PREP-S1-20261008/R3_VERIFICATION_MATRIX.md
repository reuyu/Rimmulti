# R3 검증 matrix — 설계만 완료, 실행 UNTESTED

이 matrix는 별도 exact R3 admission/freeze와 fresh QA WP 뒤 사용할 acceptance evidence 설계다. 현재 모든 R3 native row는 UNTESTED다. static도 아직 읽지 않은 R3 구현에 PASS를 주지 않는다. 테스트 이름·개수는 coverage 판정의 대체가 아니다.

## Operator-owned lifecycle 및 normal flow

| ID | 필요한 정적 evidence | 필요한 genuine 정상/native control | 필수 raw·identity | UNTESTED/제한 조건 |
|---|---|---|---|---|
| P01 operator entry | request/status와 operator execution 구분; admitted fixed exe/binary/config/profile 선택 지점 | 승인된 정상 요청1개가 operator-owned launch로 이어짐 | operator config digest, executable path/SHA, admission/task/run IDs, loaded DLL SHA/MVID | caller 선택 exe/handle만 'operator'라고 이름 붙인 fixture는 불충분 |
| P02 task issuance | immutable current seal에서 task 생성, lifecycle/task capability 및 version schema | native Worker가 genuine staged save와 own task 생성 | staged path/SHA, source/base lineage, expected seal/epoch/hash, context snapshot | runner가 직접 task/result/receipt를 작성하면 native credit0 |
| P03 owned process | 정확한 생성 handle/PID/start/cwd/argv/timeout/channel ownership, trusted executable admission | fresh validator가 승인된 project runtime에서 시작하고 staged input을 읽음 | Process.Start/exit records, validator startup log, loaded candidate/core/mod profile | sleep child/임의 process binding/같은 process 재사용으로 대체 불가 |
| P04 result origin/consume | 보호 채널·process instance·task/result schema·consume failure/cleanup 정책 | 실제 child result의 operator 관측→소비 완료→내부 receipt | channel ownership/instance correlation, consume/cleanup success, protected-context digest, receipt origin | ordinary-result fallback, consume 예외 무시, public caller receipt는 불충분. public report에는 secret 원문을 노출하지 않음 |
| P05 A→B→C | bounded write-set, supported manifest equality, step/seal/stage/receipt/promotion 순서 | genuine staged save→fresh load→actual census→result→operator receipt→approved promotion, 다음 정상 generation 재-admission | 각 native PID, stage/final bytes SHA, actual census, task/result/receipt IDs, context epochs, 원문로그 | field/mode/context가 지원 범위 밖이면 UNSUPPORTED; 같은 schedule baseline 없이 zero drift 단정 금지 |
| P06 MD131 replacement | old final 존재 시 verified same-volume atomic primitive와 fail-closed 경로, first-final 분기 | 정상 existing-final replacement 및 새 final의 승인된 rename control | volume/path identity, before/after/backup SHA, actual primitive result | 이번 준비는 실행0. I/O 실패 주입/임의 덮어쓰기를 설계하지 않음; 이전 old E2 결과를 새 후보 PASS로 승계하지 않음 |

## MD128 supported authority context 전체

각 row는 task/result/receipt/current authority·grant·seal/current epoch의 **지원 계약에서 의미가 같은 값과 역할별 제약**을 비교해야 한다. Validator의 READ_ONLY 역할과 simulator의 SIMULATION grant를 무조건 같은 문자열로 강제하지 않는다. R3가 명시한 closed schema·역할 매핑·typed presence/equality·허용 field/version을 읽고 대응한다. 실제 public receipt에 비밀 capability를 복사하라는 요구도 아니다. operator 내부 task-reference/channel origin proof와 각 authority context의 결속을 검증한다.

| MD128 row | 정적으로 확인할 비교·주체 | 정상 fresh native evidence | 미충족 조건 |
|---|---|---|---|
| C01 ValidatorTaskId/capability | outstanding immutable task와 protected result, internal receipt origin/reference | 동일 operator-generated task/run의 발급·결과·소비·receipt trace | 이름/PID만 일치하거나 외부 result를 authority로 채택 |
| C02 staged path + SHA | operator stage 및 실제 loader input·result·receipt·promotion | fresh process가 읽은 정확한 경로/bytes SHA와 census correlation | basename 표시/파일 존재/나중에 hash한 파일만으로 actual loaded bytes를 추정 |
| C03 source artifact hash | operator-approved original artifact와 task/result/receipt/current context | source input identity 및 새 stage lineage linkage | task 값의 후단 복사만 있고 validator context proof 없음 |
| C04 AuthorityId | task/result/receipt와 현재 승인 authority | 해당 정상 authority lifecycle의 validation trace | carried-but-unchecked, 미지원/누락 field |
| C05 StoreIncarnation/baseLineage | 지원 lineage representation과 current authority·seal | 동일 immutable baseline에서 발급한 정상 run의 linkage | placeholder 값을 전역 복구 정책이나 실제 canonical lineage로 자동 인증 |
| C06 GrantId | approved active grant와 seal/task/result/receipt | 정상 bounded grant를 수행·검증한 native logs | validator가 grant context를 검증하지 않음 |
| C07 WorkerGeneration | 발급/결과/receipt/current generation | 정상 generation1 및 새 승인 generation의 별개 immutable run | 기존 결과를 새 generation으로 재사용; result에 context 부재 |
| C08 scopeId | hard-bound approved target write-set | 정상 대상 scope의 native census와 proposal manifest | scope가 diagnostic로만 취급되거나 전체 save가 wholesale canonical replacement |
| C09 stable target/map context | 지원 stable identity와 runtime map/index 매핑 및 equality | actual loaded target identity/선택 근거/census | index나 clamp만으로 stable target 증명을 대신 |
| C10 allowed operation mode | simulator grant mode·validator role의 명시적 매핑·제약 | 정상 승인 SIMULATION proposal과 READ_ONLY validation log | 역할 혼합/누락/단순 복사 |
| C11 ContentProfileFingerprint | expected approved profile와 Worker/validator independently computed actual | 양 process의 actual admitted loaded profile/version/capabilities 및 동일 digest | ModsConfig/hash stub/cache flag만 관찰 |
| C12 supported semantic manifest version | exact supported codec/schema 및 field support | native census/result/receipt version과 supported field 목록 | old V3/V4 corpus를 새 버전의 oracle로 묵시 사용 |
| C13 SealedResultId | immutable seal/task/result/receipt/current sealed result | genuine seal→staged bytes→validator result association | receipt에 task 값을 복사한 것만 존재 |
| C14 ResultEpoch/current epoch | task/result/receipt/seal/current epoch와 lifecycle invalidation | 정상 seal epoch와 새 clean re-admission epoch trace | field가 운반되지만 current state와 미비교 |
| C15 sealed manifest hash | expected operator-owned sealed bytes/semantics와 result context | exact expected manifest와 actual supported census equality | caller-nominated expected manifest 또는 task-only receipt 복사 |
| C16 actual validator manifest hash | native fresh-load에서 계산한 actual manifest와 expected supported fields | actual census 원문·manifest canonical bytes/hash·receipt linkage | runner-generated result, XML hash만으로 native semantics를 추정 |

각 row의 equality rejection branches는 defensive source review로 확인한다. 이 준비는 altered/forged authority·receipt·history·schema fixtures 또는 공격 절차를 설계/실행하지 않는다. 정상 flow만으로 모든 adverse rejection의 runtime 증거가 생겼다고 계산하지 않는다. 추가 evidence가 필요한 미관측 branch는 UNTESTED로 남기며 gate 요구를 줄이지 않는다.

## MD129 failure→re-admission

| Plane | 필요한 source/state 관계 | 별도 release 후 정상·방어적 control | raw / 남는 제한 |
|---|---|---|---|
| authority/grant/profile/input | 실패가 readiness·relevant seal/task/receipt/grant/epoch를 철회하고 STEP/SEAL/STAGE/PROMOTE를 막는지 | 허용된 정상 admission 및 운영자가 의도한 정상 실패/취소 후 clean reset·재-admission | before/after state/epoch와 새 승인 proof. forged payload/권한 우회로 실패를 만들지 않음 |
| task/launch/bind/execute | early return·exception·wrapper·owned process/channel cleanup 전부 분류 | 정상 operator cancellation 또는 실제 실행 제한을 관측한 뒤 re-admission | timeout/exit/cleanup logs. elapsed time을 내부 native load/commit hook으로 부르지 않음 |
| complete/consume/promotion | result parse/instance/context·consume/cleanup 성공 전 authority 승격 없음 | 정상 결과 소비 및 다음 승인된 task lifecycle; 실제 자연 실패가 있으면 제한 보고 | 파일 존재만으로 성공 추정 금지. 실패 주입을 요구하지 않음 |
| query/status | ordinary read/query syntax와 control-plane 오류 범위 구분 | 정상 read/status가 authority를 바꾸지 않는 관찰 | 정책은 accepted MD129 그대로; 모든 query 오류에 전역 revoke를 새로 강제하지 않음 |

## MD130 typed content / cache

| ID | 정적 acceptance | 필요한 native normal evidence | UNTESTED 조건 |
|---|---|---|---|
| T01 encoding | versioned field/type/null/missing/empty/collection identity·order 계약; finite/nonfinite numeric support 명시 | 승인된 정상 loaded content를 양 process에서 독립 encoding; 지원 culture의 정상 round-trip/same-profile 비교 | R-format helper 하나/source Contains만으로 lossless 전체 PASS 금지 |
| T02 actual binaries/mods | relevant core/game build, active package IDs/order, admitted assembly SHA/MVID/size, DLC/mod content identity | actual loaded paths/assembly inventory·profile JSON 원문·digest | location 없거나 identity 누락인데 empty hash/size0로 success |
| T03 semantic fields | 지원 scope의 material Def/patch/settings/dependency coverage 표와 제외 근거 | normal supported Def census에 이름/값/타입/order 반영, approved profile/capabilities 제시 | count-only/label-only 또는 모든-mod/모든 Def 호환 자동 주장 |
| T04 lifecycle cache | cache keyed/lifetime/invalidation/recomputation이 실제 admission/load/reset/validation epoch와 연결 | fresh Worker와 fresh validator compute, 정상 reset/re-admission에서 cache epoch/actual manifest 재확인 | cache clear bool, fingerprint stub, expected digest 재복사 |

## Installation / provenance / completion

| ID | acceptance evidence | 제한 |
|---|---|---|
| E01 installed incident | historical2D64 archive·observedBB3B incident·새 R3 candidate·실제 isolated loaded identity 분리. known deploy/copy 로그가 없으면 actor/cause UNKNOWN | 원본 installed 자동 restore, old expected hash 정상화, 누가 바꿨는지 추정하지 않음 |
| E02 immutable before/after | exact selected/alternate SHA/MVID/source/PDB/CodeView/generated/tooling/dependency/content manifest 및 실행 전 snapshot, protected archives/Pipeline/QA 전후 | 완료 뒤 snapshot을 실행 전 증거로 소급하지 않음. mutable R3 source를 old R2/R1 lineage로 읽지 않음 |
| E03 native evidence packaging | PID/argv/cwd/start/end/exit·loader logs·actual loaded profile·stage/result/receipt/census identity, raw process/fixture inventory | expected PASS label/수와 actual exercise 분리; E1→E2 promotion 없음 |
| E04 standard completion | producer/report_kind/exact dispatch/WP/revision/result_id/time/status/limitations/artifacts roles/path/SHA + freeze evidence | aliases identity를 reconcile해도 missing result/schema를 완전 계약 PASS로 치환하지 않음 |

현재 outcome: matrix 작성 완료, R3 static/runtime evidence 아직 수집하지 않음. Engine002/006/Pipeline007/current schema/G-Q1 OPEN, Foundation HOLD를 변경하지 않는다. PlayerGlobal owner/schema/physical split 및 C의 read-only/discardability 가정을 freeze하지 않는다.
