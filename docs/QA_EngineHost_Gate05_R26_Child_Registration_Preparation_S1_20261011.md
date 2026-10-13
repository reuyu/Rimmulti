# Gate05 R26 child 등록 — 독립 QA 준비 S1

별도의 operator-owned READ_ONLY 설정과 declaration을 private child 등록으로 전달할 **현재 producer와 등록 API가 소스에 없습니다**. 독립 READ_ONLY 계약 준비를 완료했으며 실행 PASS 판정은 아닙니다. A의 현재 R26 산출물은 읽거나 협의하지 않았습니다. 기존 config14/snapshot15/receipt11/descriptor7/task27·후속 native authority를 변경하거나 확정하지 않았습니다.

현재 bootstrap은 한 parent 시작 receipt를 발급·전역 seal합니다. Factory는 raw SHA/원문 declaration/config을 검증하고 approved7을 복사하며 IsTrusted=true를 설정하지만, public factory 호출과 receipt의 정합성만으로 실제 operator issuer·parent-child 승인 관계·보호 채널을 증명하지 못합니다. Launcher는 current task nonce를 확인하고 부모 active snapshot의 exe/SHA/free-form args/cwd를 쓰며 task-file/nonce 옵션을 붙입니다. 별도 child 발급·private lookup·frontend 소비 경로는 구현되어 있지 않습니다.

권장 첫 최소 구현은 별도 parent/child receipt와 owned task27/path를 immutable local 값으로 복사하는 PURE Capture seam입니다. **등록 authority는 만들지 않습니다.** WorkerBridge.cs byte166910/line3477의 Gate05-R18 앞 단일 zero-width insertion이 최소 제안입니다. Context SHA FB507B9410EBBDDDEE55B36B7E76CFA07B613601C3D4B0336F5E5F70ED864137. 실제 private registry/issuer wiring/launch/revoke는 조건부 후속 제안으로 별도 Master 승인과 source spans가 필요합니다.

Producer 선택 A는 parent bootstrap admission 성공 뒤 attachment 전 actual operator-owned typed provider이며 그 provider는 현재 없습니다. 선택 B는 current-task capability와 보호된 typed callback이며 child provisioning 연결이 현재 없습니다. 새 CLI/JSON carrier/schema/임의 origin·plan·configId/parent.role 교체/global receipt 교환/자유 args split을 채택하지 않았습니다. 실제 issuer와 channel이 미정이면 첫 data-only 구현을 분리하고 연결 authority는 OPEN으로 남기는 계약입니다.

| 준비 산출물 | 실제 확인 범위 |
|---|---|
| Full field source map | 114행, config14×2/snapshot15×2/receipt11×2/approved7/task27 |
| Closed local plan mapping | 14개 값 그룹; task/result/staged 절대경로와 nonce는 부모 owned task 그대로 |
| Source anchors | 20개 실제 line/byte/span SHA, conditional insertion context7개 |
| Lifetime source map | revoke/tick/grant/reset/seal/stage/load/consume/dispose 9곳 |
| Prospective oracle | 독립 literal parent/child normal pair4개, 전체 typed/order/original-string/copy 기대값; 실행0 |
| Prerequisites | actual issuer·typed carrier·M05 binding·M07 revoke·frontend·Genroot·staged/content·Master admission 8개 |
| Preservation | protected13419/frozen99/currentproduction9 before-after SHA/size 전부 동일 |
| Exact lineage | selected Debug A9C31DB0…/MVID5553a632-0557-433f-8840-bb12875cf577, Debug/Release CodeView/PDB source4/4 fresh metadata matched |

[구현 계약안](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011/IMPLEMENTATION_CONTRACT.md), [전체 필드 출처표](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011/OWNERSHIP_FIELD_SOURCE_MAP.json), [최소 변경 위치 제안](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011/PROPOSED_MINIMUM_PATCH_SPANS.json), [정상 prospective oracle](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011/PROSPECTIVE_NORMAL_ORACLE.json), [미충족 선행조건](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011/REGISTRATION_PREREQUISITES.json)에 상세 값을 결속했습니다.

Private task slot의 lookup 키는 owner instance/current outstanding task reference/currentGeneration/TaskId/resultEpoch/sealedResultId라는 제안입니다. 객체 보유·IsTrusted·PID만으로 등록 authority를 만들지 않습니다. Full task/context/channel equality는 M05, role-aware stale capability revoke는 M07이며 M04 copy-PURE PASS로 대체할 수 없습니다. Reset가 epoch0으로 돌아가는 현재 사실 때문에 epoch 하나를 unique lifetime으로 쓰지 않습니다. 완료된 task의 immutable plan은 진단 값이며 eligibility는 live private registry에서만 판단해야 합니다. Actual Process/nonce-channel proof와 scoped process cleanup은 후속 native admission이 필요합니다.

Oracle는 parent와 child raw config14를 각각 literal로 작성했습니다. PLAIN/PLAIN, OPAQUE/OPAQUE, PLAIN/OPAQUE padded descriptor, OPAQUE/PLAIN padded descriptor 정상 pair4개에 raw config SHA·original7·factory usedClone7·receipt11·snapshot15·policy record4·redaction13·nested receipt redaction11·task27·closed plan14 및 모든 ordered type을 사전에 정의했습니다. Origin/plan의 공백·Ω/opaque policy ID-revision/UTC .1234567Z 및 .0000000Z/Unicode 절대경로/array order를 보존합니다. Caller와 detached policy/list/task edits 후 전체 원본 값과 bytes가 같아야 하는 미래 정상 ownership 기대값입니다. 이 synthetic PID/nonce/config IDs는 실제 authority 발급 증거가 아닙니다. Fixture self-consistency metadata 검사만 수행했고 candidate/factory/selector/QA runner 호출0입니다.

자체 출처표 초안에서 reset/seal 위치를 method declaration 대신 먼저 등장하는 call token으로 찾은 두 메타데이터 오류를 수정했습니다. 최초 초안 파일과 correction 도구의 한 줄 위치 annotation assertion 실패(exit1)를 보존했습니다. 최종 source declaration과 byte/context SHA를 다시 대조했으며 candidate·compiler·QA runner 실행 또는 기존 보호 증거 변경은 없었습니다. 검색 diagnostic 두 건도 recovery audit에 기록했습니다. 이를 candidate 실패나 runtime 증거로 취급하지 않습니다.

R25 S2 Master 판정(QA newline만 scoped CLOSED/normal declared selection PASS)을 접수했으며 S1 raw8FAIL/exit1와 모든 원문은 보존했습니다. 과거 PASS를 R26 실행으로 승계하지 않았습니다. Original Steam/Workshop/UserData/save 읽기·restore·assets copy·installation0. 현재 provenance 의심 installed incident의 actor/cause는 UNKNOWN/OPEN으로 유지합니다. Reference Multiplayer HostUtil의 savedatafolder 사용은 exact checked-in source SHA/line 인용이며 현재 frontend 지원이나 native effective Genroot 증거가 아닙니다.

Production modify/build0, QA compiler/runner/candidate/native/game/Process/assetscopy 실행0, 새 external schema·wire·flags·governance·closure·WP·scheduler 변경0. Metadata Python 도구는 파일/hash/source/PE/PDB와 prospective literal 데이터만 처리했고 보호된 과거 도구의 named metadata functions는 AST로만 재사용했습니다. 전체 gate 및 native 실행 검증은 NOT_RELEASED, Engine002006/Pipeline007/schema/G-Q1/physical split OPEN/Foundation HOLD, closure/release는 Master 판정입니다.
