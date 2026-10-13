# Master Review — Engine Gate05-R2 E1

판정: **REVISION_REQUIRED / E2_NOT_RELEASED**. A terminal 보고는 수집했지만 `PASS_WITH_DECLARED_LIMITS`를 전체 gate PASS/수정 완료로 채택하지 않는다. 기존 Engine002/006 OPEN, Pipeline007/current schema OPEN, G-Q1 OPEN, Foundation HOLD. 사용자 요청에 따라 기존 `wareconomy-master`는 **PAUSED**, interval60분/짧은 trigger/동일 Master target을 유지했다.

## 실제 식별과 보존

Dispatch `WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708`, WP_ENGINE_GATE05_R2/GATE05-R2. 원문 COMPLETION SHA `C1C24279EDF1626272E7A270E0BF91EBDDBF9CB6B09352CB46D9CC8371C4797C`.

| 항목 | 실제 Master 확인 |
|---|---|
| selected Debug DLL | SHA `57A4C8B75ABC2AD43E9A3E4215A23A35741E0E5B203CB57A63AA30BB59CBF54F`,192000bytes,MVID `8292a8ec-4a02-49dc-88e9-2c3d93e969f5` |
| matching Debug PDB | SHA `E0A7EC813C52AF3206DA6D0AE6122453027FF6CC1CB2A509AF9B80134CCFCA6E`, CodeView GUID 일치,source/generated documents4/4 |
| alternate Release | DLL SHA `25DEE284AC85F22031614541A4335FD78D1C0490DBB95BC77A28CED5329966C7`,MVID `556b3694-a49e-43dc-a019-3d529cabf069`;PDB SHA `5FD9E821CF86429D418D1D44BCFF52C3A5209D91340002DD077EFB751F6CD1B5`,CodeView/source4/4 |
| 명시 산출물 | completion.deliverables12 + Debug/Release DLL/PDB4 =16 실제 SHA/size matched |
| 집계 | results.json과 raw_console 양쪽24개,23PASS/1BLOCKED. 숫자 자체는 일치 |
| historical preservation | Engine archive19,Pipeline original+frozen206,R1 rejected147 matched; 정확한 허용 current Engine9 paths 변화는 승인 repair 범위 |
| installed incident | 기존 Steam WorkerBridge 실제SHA `BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61` 유지;expected old19 SHA2D64…와 불일치. 변경 주체/원인 UNKNOWN,incident OPEN |
| R2 snapshot | 원문/source/generated/bin/harness/raw/task 등107파일을 `FROZEN_GATE05_R2_REJECTED`에 보존. **검토 시점 snapshot**이며 실행 이전 snapshot을 소급 증명하지 않음 |

검증 JSON: `coordination/MASTER_GATE05_R2_E1_VERIFICATION_20261008.json`. Freeze manifest: 고유 task의 `MASTER_GATE05_R2_REJECTED_FREEZE_MANIFEST.json`. Master는 후보 재빌드/실행을 하지 않았고 제출 harness의 보안 변조·우회 검사를 재현하지 않았다. Inspector는 PE/PDB metadata만 읽었다.

## 수용한 좁은 진전

- 예전 public registration/receipt-submit 경로의 거절, public task response에서 nonce/secret redaction, 일부 mismatch의 readiness revocation이 소스에 추가됨.
- 실제 process handle을 저장하는 새 lifecycle 코드가 존재. 이것은 trusted operator origin/validator workload execution의 완료 증거가 아니다.
- float/double `ToString("R", InvariantCulture)` helper 및 ThingDef.statBases 이름/값 encoding이 추가됐고8 Def family empty gating이 존재한다. 오류는 outer catch에서 다시 throw한다.
- A는 E1/E2와 Master closure 역할을 구분했고 native 미실행 표식을 넣었다. 다만 보고서의 "fully remediates", "16 dimensions fully enforced", "genuine operator result", "preservation FULL", DRM 원인 설명은 아래 실제 근거와 충돌한다.

## 현재 blockers와 controlling correction

| ID / 심각도 | 독립적으로 읽은 근거 | 판정/해제 조건 |
|---|---|---|
| R2-M01 / CRITICAL | WorkerBridge.cs HandleClient/ProcessCommandMainThread·새 launch/bind 코드: 일반 command path에서 launch가 도달하고 trusted operator의 고정 candidate/config에서 기동하는 경계가 없음. 새 handle binding 역시 launch ownership의 출처를 검증하지 않음 | **MD126/127 미충족**. 요청자 요청과 operator 실행 경로를 구분하고 admitted immutable executable/binary/profile/task에서 기동해야 함. Process PID/이름만 권한으로 삼지 않음. 실제 genuine operator-owned fresh validator가 staged bytes를 읽는 증거 필요 |
| R2-M02 / CRITICAL | EngineHostCensus.cs ValidatorResult DTO와 WorkerBridge.cs HandleCompleteStageValidation(2322~2527): task/stage/PID/nonce/profile/manifest 일부를 비교하지만 source artifact/authority/store-lineage/grant/generation/scope/map/mode/version/seal/epoch 전체 result context를 운반·검증하지 않음. Receipt 필드는 task에서 다시 복사함 | **MD128 실패**. supported closed schema 모든 authority field가 result와 task/current seal/authority/grant/current epoch에 결속돼야 함. Promote의 task/receipt 후속 비교가 validator result의 빠진 field proof를 대신하지 못함 |
| R2-M03 / HIGH | protected-result reader는 원래 channel이 없을 때 다른 일반 result 파일도 찾음. result DTO의 process start time은 completion에서 비교하지 않고 receipt는 저장한 start time을 이용. 파일 소비 rename의 예외를 무시하고 다음 authority state로 진행 | **MD126/127 + lifecycle 미완료**. named file/secret string과 실제 operator-controlled origin/lifetime/consumption을 구분. 승인 채널·정확한 process instance·owned result 관측·실패 처리 계약 필요 |
| R2-M04 / HIGH | ContentProfileProvider(1516~1878): R formatting 개선과 별개로 Def entry를 delimiter string으로 구성. null collection과 empty를 합치고 null entries를 skip하며 verbs/comps를 sort. material property 일부만 담고 mod patch count 및 일부 loaded assembly의 hash/size가 없을 때도 record가 생성됨 | **MD130 lossless typed coverage 미완료**. 지원 profile의 field/type/null/missing/entry identity/order를 표로 규정하고 손실 없는 versioned encoding·누락 fail-closed·actual loaded content/patch/settings coverage를 구현. domain과 무관한 모든 Def 완전 serialization을 요구하는 것이 아니라 승인 scope의 material 의미를 명시·검증 |
| R2-M05 / HIGH | Program.cs S01은 uninitialized component, reflection 상태주입, fingerprint stub, sleep-only subprocess와 runner-generated result를 사용. S02 일부는 source Contains 또는 cache clear assertion. 실제 full profile revalidation/culture round-trip/census 실행으로 전체 PASS를 증명하지 않음 | **WP evidence 요구 미충족**. tests의 실제 assertion 범위만 credit. genuine staged save→fresh native load→actual census/result→operator acceptance를 분리하고 필요한 MD128/129 coverage를 정상 flow 및 defensive review로 제공. 취약성·권한 우회 reproduction은 요청하지 않음 |
| R2-M06 / HIGH | Program.cs NAT03은 파일 존재 bool 후 unconditional BLOCKED record를 추가. raw는 steam_api64 존재 False인데 report는 DRM redirect를 실제 원인처럼 단정. project runtime copy/exe launch/argv/PID/exit/loader 로그가 없음 | **NATIVE_UNTESTED / blocker cause UNKNOWN**. DRM/redirect 진단 미채택. 허용된 licensed project copy 정상 실행을 실제 관찰하거나 실행하지 못한 정확한 제약을 UNTESTED로 보고. Steam 원본 변경/보호 우회 없이 설명 |
| R2-M07 / HIGH evidence | NAT02의 PASS는 archivedDLL SHA equality만 검사; installed SHA는 출력만 함. completion/report는 preservation FULL을 주장하지만 old installed SHA 불일치가 계속 존재 | **installed incident OPEN**. archive 보존은 수용, Steam old candidate 보존 FULL은 거절. 언제/누가/어떤 경로로 바뀌었는지 미확정. 새 candidate·현 설치·역사 archive를 혼합하지 말고 A가 작업 기록으로 설명. 자동 restore/expected hash 정상화 금지 |
| R2-M08 / delivery contract | COMPLETION은 task_id/work_package_id/revision/completed_at_utc/deliverables/e1_verification_summary aliases를 사용; envelope의 schema_version/producer/report_kind/result_id/artifacts roles 및 freeze_before/after가 없음 | 정확한 task alias와 실제16 hashes는 Master 별도로 reconciled. 다른 task라고 단정하지 않는다. 그러나 정규 completion contract는 FAIL/EVIDENCE_INCOMPLETE. 원문을 Master가 고치지 않고 원문SHA 기반 별도 collection key로 dedupe. 후속 revision은 규정 schema/unique result_id/실제 limitations/freeze proof 필요 |

MD129: 일부 RevokeReadiness 진전은 수용하지만 모든 control-plane 실패의 coverage가 없다. Validator task/bind의 여러 early return과 wrapper 경계를 읽어 stale capability 처리가 구현·증거에 맞는지 후속 review가 필요하다. claimed full revocation PASS는 미채택. Native 실제 loaded profile computation, cache lifetime/revalidation, current authority state binding도 미검증이다.

NAT01은 exe 존재 관측만 credit. NAT02는 archive hash credit. NAT03은 native 미실행 disclosure만 credit하며 DRM 실패 재현으로 credit하지 않는다. 제출 checkpoint 이름/수24/23PASS는 mandatory gate coverage24/완료23을 뜻하지 않는다. static contract 실패와 미실행을 구분한다.

## 후속 범위와 통신

후속 범위는 동일 approved Engine repair의 기술적 보완이다. trusted operator entry/launch/result lifecycle, complete MD128/129 result equality, typed lossless content coverage, truthful genuine/native/evidence schema, installed incident reconciliation를 수정해야 한다. 새로운 게임 기능/전체 architecture 재설계/원본 Steam 배포/Multiplayer 전체 설치를 승인하지 않는다. MP HostUtil 등은 launcher 참고일 뿐 native PASS의 대체 증거가 아니다.

구체적인 후속 scope 파일 `ENGINE_GATE05_R3_CORRECTIVE_SCOPE_20261008.md`는 **PREPARED_NOT_DISPATCHED**다. 현재 사용자의 확인·예약 일시정지 요청을 수행했고, 이 검토에서 새 A/QA WP를 실제 전송하지 않았다. 새 dispatch가 필요할 때 새로운 revision/고유 ID·candidate preservation·actual A idle/submission을 결속한다. 지금 예약은 PAUSED 유지, Sol 새 E2 미발행. Sol snapshot은 notLoaded/동일 completed cursor19이며 삭제/오류/새 완료로 추정하지 않는다.

E2 release 조건: 위 critical/static contract 결함 해소, new exact candidate/source/PDB/profile·genuine required evidence·old preservation/incident 검토, Master admission/freeze 후 original idle Sol에 별도 fresh independent WP. 지금 R2로 closure/release를 하지 않는다.
