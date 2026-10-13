## 4. Real graphical GUI loop

주 실행 로그 시간은 UTC다. OS click은 computer-use로 수행했고, QA가 adapter 메서드를 대신 호출하지 않았다.

| 입력 | 실제 native/RPC chain | 결과 |
|---|---|---|
| own Human302 Draft | 05:41:47.954–.974, Frame3488; NATIVE_GIZMO → DRAFT_ENTER → REAL_GUI_GIZMO RPC → Worker ACCEPTED → guarded apply | **통과** |
| own Human302 Move | 05:42:50.035–.050, Frame7186; native terrain right-click → FloatMenu Go here click → ORDER_ENTER → REAL_GUI_FLOATMENU RPC → Worker native Goto → snapshot | **명령·실행 통과**, 화면 이동은 section5에서 실패 |
| foreign Human305 Draft | 05:44:47.750–.768, Frame14187; native Draft → REAL_GUI_GIZMO → AUTH_REJECTED | **통과**, 대상 Pawn native XML 전체 불변 |

Draft 응답 수신 직전까지 client Draft=false였다. 승인된 snapshot 적용 중에만 true로 바뀌었다. Move도 수신 전 local job=None이었고, 승인된 snapshot 적용 이후 IsReconciling=true 안에서 mirror Goto가 만들어졌다. 미승인 local final Draft/Goto 및 거부 이후 fake success는 관측되지 않았다.

실패한 입력 시도는 합격 근거에서 제외했다. 초기 우클릭은 own Pawn이 선택되지 않아 RPC가 없었고, 다른 우클릭은 FloatMenu만 열었다. 실제 `Go here` click의 native chain을 Move 근거로 사용한다. foreign 시험 중 잘못된 surface capture를 반환한 시도도 제외하고, returned RimWorld window를 재선택·재관찰해 실제 event/response를 확인한 입력만 채택했다.

증거: `GraphicalClient/qa-events.tsv`, `round2-after-draft-*.json`, `before-foreign-click-client.json`, `after-foreign-valid-client.json`, [own-drafted.jpg](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/own-drafted.jpg).

## 5. Operational replication — 내부 상태 PASS, graphical result FAIL

시험 준비에서 candidate `SET_REPLICATION 1`과 legitimate QA Worker cadence control을 사용했다. **Move 승인 이후 아래 구간에는 TestHarness GET_SNAPSHOT, QA refresh, refresh를 위한 두 번째 gameplay command가 없다.** QA는 read-only observer state만 읽었다.

polling은 정상 `RemoteClientController.Update():569–575`에서 실행된다. 명령 seq548 이후 **30개의 distinct automatic responses(seq549–578)**가 도착했고,15개의 서로 다른 Worker 위치를 client의 native Position에 적용했다. Worker는 QA STEP 없이 자율 이동했다.

아래 receive/apply 시간은 UTC05:42 기준이다. Worker state는 실제 wire, mirror는 native apply 이후 상태다.

| Seq | Worker tick | Worker position/job | Mirror position/job | Receive → Apply |
|---:|---:|---|---|---|
| 548(command) | 5275 | 139,142 / Goto | 139,142 / Goto | 50.045187 → 50.050182 |
| 552(auto) | 5311 | 140,141 / Goto | 140,141 / Goto | 50.641390 → 50.643895 |
| 554(auto) | 5329 | 141,140 / Goto | 141,140 / Goto | 50.941833 → 50.944345 |
| 557(auto) | 5356 | 142,140 / Goto | 142,140 / Goto | 51.393183 → 51.395690 |
| 562(auto) | 5404 | 145,142 / Goto | 145,142 / Goto | 52.192547 → 52.196092 |
| 567(auto) | 5452 | 148,142 / Goto | 148,142 / Goto | 52.994417 → 52.996419 |
| 573(auto) | 5509 | 151,142 / Goto | 151,142 / Goto | 53.956575 → 53.958605 |
| 576(auto) | 5538 | 153,142 / Wait_Combat | 153,142 / None | 54.434175 → 54.436185 |

cell 위치와 Goto 종료라는 **거친 completion/idle 분류**는 수렴한다. Worker Wait_Combat과 client None이 같은 job 상태라는 뜻은 아니다.

그러나 다음은 같은 이동의 실제 렌더링 관찰 결과다.

```text
client Position=(148,0,142), job=Goto, DrawPos=(139.50,8.41,142.50)
client Position=(151,0,142), job=Goto, DrawPos=(139.50,8.41,142.50)
client Position=(153,0,142), job=None, DrawPos=(139.50,8.41,142.50)
Worker final Position=(153,0,142), job=Wait_Combat
```

**화면의 Strange는 출발점에 남았다.** 반복 snapshot으로 mirror cell은 진행하지만 rendered Pawn은 따라가지 않는다. foreign Nick도 cell148,140에 비해 DrawPos144.50,142.50에 남았다. 따라서 cell/hit target과 화면이 불일치하며, 내부 Position 성공을 graphical movement PASS로 바꿔 해석할 수 없다.

증거: [operational-wire-trace.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/operational-wire-trace.json), [round2-real-move-native.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/round2-real-move-native.json), [stale-render-after-arrival.jpg](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/stale-render-after-arrival.jpg). 초기 실행에서도 같은 화면 증상을 관측했고 `Round1Evidence/`에 보존했다.

### QA-PRESENT-004 — remaining High finding

- Requirement: SRS-FR-100, SRS-NFR-004/009/011.
- Location: `RemoteClientController.cs:347–360` Position reconciliation, `RemotePresentationMod.cs:132–139` client tick suppression.
- Reproduction: frozen graphical candidate에서 actual Draft → Go here를 수행하고 periodic replication만으로 도착을 기다린 뒤 Position/DrawPos/화면을 대조.
- Expected: 비권위 client의 rendered Pawn이 Worker 위치를 따라가고 selection/inspect/hit target과 일치.
- Actual: cell은 도착점으로 수렴하지만 DrawPos와 sprite는 출발점에 고정.
- Root Cause: 후보는 Position/job을 변경하면서 render state/cache의 일관성을 보장하지 않는다. client ticking은 억제된다. **PawnTweener 내부의 정확한 cache 유지 조건은 독립 decompile로 분리하지 않았으므로 추정으로 남긴다.** 관측된 불일치 자체는 native state와 화면으로 확인했다.
- Required Fix: 비권위 presentation 경로에서 render state를 보정하고 실제 GUI/화면/좌표를 동시에 재검증. QA가 DrawPos reset 또는 client simulation을 넣어 합격시키지 않는다.

## 6. Polling / liveness

| 항목 | 독립 결과 / 제한 |
|---|---|
| polling origin | 정상 Update timer. background/async subscription이 아님. |
| socket wait | `Update():575` → `FetchAndApplyReplicationUpdate():443–445` → **main Unity thread의 synchronous ReadLine** |
| overlapping / in-flight | 관측 overlap0, maximum in-flight1. 동기 직렬 실행의 결과이며 nonblocking 증거가 아님. |
| timeout | socket read deadline 설정 없음. 영구 무응답 시험 대신2초 delayed response로 blocking risk 검증. |
| delayed periodic response | client frame gap **2033.7723ms**, 동시에 보낸 control PING4건 RTT **1869.39–1875.15ms** |
| queue growth | 최소4개 control이 기다리는 조건 재현. 내부 queue count의 연속 측정은 하지 않음. unbounded drain은 정적으로 남음. |
| legacy execution | Worker의 monolithic command path가 남음. 이번에는 새로운 대형 flood를 수행하지 않음. |
| long-run memory | PeriodicMetrics에 poll마다 append하며 bound/eviction 없음. 정적 memory-growth risk; 실제 장기 memory ceiling은 미측정. |
| actual transport close | empty response/socket/IOException log 이후 STATUS는 ConnectedToWorker=False, AutoRepActive=True. control은 다시 응답했고 QA가 explicit disable/disconnect. 완전한 timeout/reconnect lifecycle 보장 아님. |

2초 지연은 같은 main thread의 native frame/UI 진행에도 영향을 준다. 단순한 작은 loopback RTT로 이 구조를 닫을 수 없다. **QA-PRESENT-007: STILL FAILING.**

Worker accumulator가 실제 executedTicks만 차감하도록 수정된 것은 정적으로 확인했다. post-tick soft8ms 검사와 global DoSingleTick 경로를 전체 ADR-006A 구현으로 인증하지 않는다.

증거: [periodic-fault-native-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/periodic-fault-native-results.json), `periodic-proxy-wire.json`, `qa-frame-gaps.tsv`, [periodic-disconnect-result.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/periodic-disconnect-result.json).

## 7. Snapshot fencing — actual periodic path

proxy는 **normal timer가 발행한** GET_SNAPSHOT을 Worker로 전달하고 실제 response를 한 번씩 변조했다. QA가 Fetch/GET_SNAPSHOT을 대신 호출하지 않았다.

각 vector에는 대상 Pawn의 위치99,99, Draft=false, job=None, rotation=North를 넣어 적용 여부를 검사했다.

| Fault | Rejection | Native state |
|---|---|---|
| stale sequence | OUT_OF_ORDER | 두 맵의 전체 Pawn attributes 전후 동일 |
| wrong session | WRONG_SESSION | 동일 |
| wrong generation | WRONG_GENERATION | 동일 |
| wrong target map | WRONG_MAP | 동일 |
| unresolvable expected authority target | UNRESOLVED_MAP | 동일 |

각 trial에서 rejection counter는1 증가하고 position/Draft/job/rotation은 변하지 않았다. 마지막 trial은 expected-target 설정을 명시적으로 변경하여 resolution branch를 검사한 뒤 Map_0으로 복원했다. Production session identity/capability/operation replay까지 검증한 것이 아니다.

## 8. Authority-bound application / 4 rotations

fixture의 두 맵을 load한 상태에서 **viewed map=Map_1**, **authority target=Map_0**으로 유지했다. QA의 native Current.Game.CurrentMap 변경은 명시적인 view stimulus이며 candidate resolver를 대체하지 않는다.

정규 fixture control로 Worker Human302의 rotation을 바꾸고 client normal periodic path만으로 반영했다.

| Worker native | Actual wire | Client native on Map_0 | Map_1 Pawn states |
|---:|---|---:|---|
| 0 | North | 0 | unchanged |
| 1 | East | 1 | unchanged |
| 2 | South | 2 | unchanged |
| 3 | West | 3 | unchanged |

Map_0 target에만 적용되고 Map_1의 Pawn state 전건은 각 trial 전후 동일했다. client는 Find.CurrentMap 대신 snapshot TargetMapId를 해석한다. unresolvable target rejection은 앞 절의 actual periodic path로 확인했다.

**QA-PRESENT-005 / 010: CONFIRMED RESOLVED**, 시험한 client scope에 한정. native Map/Thing ID를 canonical context/entity identity로 승격한 판정은 아니다. Worker resolver`:199/:208`의 fallback-to-first-map은 별도 잔존 위험으로 구분한다.

증거: [map-bound-rotation-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/map-bound-rotation-results.json), `after-map-rotation-client.json`, client`:252–265`,`:304–333`, Worker`:573`, RotationWireContract.

## 9. Privileged control attack — boundary failed

`Protocols.cs:186`은 remote JSON의 Source를 읽고 Worker`:219`는 다음 식으로 권한을 부여한다.

```csharp
bool isPrivileged = cmd.Token == PrivilegedQaToken || cmd.Source == "QA_TEST_CONTROL";
```

Source는 **remote/client-controlled**이며 trusted role/channel/capability가 아니다.

| Attack | Result |
|---|---|
| Player_A + ordinary source → LOAD_SAVE/SET_GENERATION/SET_PROGRESSION/SET_ROTATION | 4건 모두 PRIVILEGE_REJECTED |
| INVALID_TOKEN + forged Source → 같은4controls | **4건 모두 ACCEPTED** |
| INVALID_TOKEN + stale Generation999 + forged Source → SET_PROGRESSION | **ACCEPTED** |
| INVALID_TOKEN + WRONG_SESSION + forged Source → SET_PROGRESSION | **ACCEPTED** |
| 실제 client gameplay transport + Player_A + Generation999 + WRONG_SESSION + forged Source → SET_ROTATION | **ACCEPTED** |
| INVALID_TOKEN + forged Source + SET_GENERATION777 | **실제로 GEN777 변경**, STATUS 대조 후 정규 QA control로1 복원 |
| INVALID_TOKEN + stale generation + wrong session + forged Source → LOAD_SAVE | **ACCEPTED**, Worker log에서 실제 fixture reload 확인 |

독립 Worker TCP와 기존 client gameplay transport 양쪽에서 공격했다. reload는 기존 QA fixture만 사용했으며 Production save/publication은 건드리지 않았다. static privileged key 및 Player_A/B token도 production authentication 근거가 아니다.

**QA-PRESENT-006: STILL FAILING.** ordinary source negative test만으로 closure할 수 없다. Source는 분류/telemetry일 수 있지만 authority proof가 될 수 없다. test control은 trusted 경계에서 도출해야 하며 Production 인증을 이번 QA에서 구현하거나 선결정하지 않는다.

증거: [map-rotation-security-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/map-rotation-security-results.json).

## 10. Dependency-clean evidence

fixture-declared10packages가 모두 actual active profile에 있다. GameProbe/MapProbe, proof-token Def 제공 mods도 load됐다. 이전 missing class/Def와 unresolved reference/null spawn이라는 profile 누락 증상은 재현되지 않았다.

그러나 **zero-error clean load는 아니다**.

- client log`:32–33`, Worker`:2587–2588`: proof-token Texture2D `Things/Item/Resource/Gold` 누락 및 `MatFrom with null sourceTex`.
- Worker`:4147` 부근: auxiliary WorkerBridge listener의 port29100 충돌. QAEngine02.Boot의 listener SocketException도 있다. candidate29900 / observer31800–31801과 다르다. A의 dependency profile을 그대로 사용했고 이 설정을 조용히 고치지 않았다.
- headless Worker의 unsupported shader 및 native atlas bake post-long-event NullReferenceException도 있다. missing class/reference로 오분류하지 않고 graphics/headless lifecycle 문제로 구분한다.
- proxy 종료의 socket error, 의도한 fencing reject, LOAD_SAVE attack의 loading gap/default snapshot reject는 fault injection 결과이며 dependency 오류와 혼합하지 않는다.

**QA-PRESENT-009: PARTIAL.** declared dependency 일치와 이전 class/Def 결함 해소는 인정한다. asset/init errors가 남아 전체 clean canonical load를 인증하지 않는다. QA-ENGINE-002는 global OPEN 유지이며 이 보고서로 닫거나 중복 ID를 만들지 않는다.

## 11. Reconciliation scope / remaining accuracy

position/Draft/rotation/Goto destination 및 거친 idle 표시는 개선됐다. 하지만 renderer 불일치가 남고, 일반 job graph는 지원하지 않는다.

checkpoints에서 Human302/Human305의 ThingGrid reference는 각1, spawned ThingID duplication은0이었다. foreign rejection 전후 selection/reference도 유지됐다. spawn/despawn/death/map migration으로 범위를 넓혀 인증하지 않는다.

health 코드는 기존 def가 없으면 추가하는 수준이다. severity/body part/occurrence ID/removal/Dead/Downed 전체를 복원하지 않는다. local Stab severity3→4 fault 후 **4건의 valid automatic apply 증가를 대조해도 severity4가 유지됐다**. 거부된 snapshot만을 보정 실패 oracle로 사용하지 않았다. `before-health-periodic-fault.json` / `after-health-periodic-fault.json`, client`:403–416`.

동일 fixture의 native ThingID와51-Pawn set을 검증했다. ADR-003 canonical inventory/entity conversion, reservations/projectiles/items/buildings/fire/zones/power/bills 등 full-map replication은 미검증이다.

## 12. Independent metrics / evidence discipline

실제 GUI Move 직후30automatic updates의 수치다. QA observer overhead를 포함한 해당 Windows loopback 환경에 한정한다.

| Measurement | Independent result |
|---|---|
| GUI Draft response | **16,827 UTF-8 bytes**,51Pawns |
| GUI Move response | **16,860 UTF-8 bytes**,51Pawns |
| foreign GUI rejection response | **16,936 UTF-8 bytes**,51Pawns |
| periodic full-response payload | **16,812–16,860 bytes**,mean16,835.4,51Pawns |
| automatic cadence | mean**157.98ms**(~6.33Hz),range137.41–180.62ms |
| periodic send→receive loopback RTT | mean**8.73ms**,range3.26–17.77ms; apply 제외 |
| candidate validate/reconcile duration | mean**2.46ms**,range2.03–5.31ms; displayed-frame latency 아님 |
| receive/apply timestamps | per-sequence wire/apply observer 기록 별도 보존 |
| delayed periodic fault | delay2초 → frame gap2033.77ms / control RTT 약1.87초 |

payload는 full51-Pawn response이고 delta가 아니다. snapshot JSON section과 envelope 전체를 `qa-events.tsv`에 따로 기록했다. PING을 snapshot으로 측정하지 않았으며 WAN/final NFR SLO/displayed-frame latency/full-map bandwidth는 인증하지 않는다.

A의 periodic byte/cadence/parse-apply 측정은 개선됐다. 그러나 GUI benchmark는 client`:239`의 `respJson.Length`를 bytes로 부르고 harness`:203`이 이를 사용한다. harness`:193/:229`의 direct ProcessInput/TryTakeOrderedJob를 REAL_GRAPHICAL_OBSERVATION으로 분류하는 문제도 남았다. Move oracle은 Position/job만 검사해 이번 DrawPos 실패를 검출하지 않는다.

**QA-PRESENT-008: PARTIAL.** 올바른 periodic metrics는 인정하지만 GUI evidence 분류와 표시 oracle 때문에 closure하지 않는다.

증거: [independent-summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN03-20261002/independent-summary.json), `round2-real-move-metrics.json`, `GraphicalClient/qa-wire.tsv`.

## 13. Defect recommendations — Master decision pending

| Defect | Recommendation | Scope / basis |
|---|---|---|
| QA-PRESENT-002 | **CONFIRMED RESOLVED** | 자율 Worker + 정상 Update timer +30automatic applies, cell/destination/coarse idle 수렴. cadence 누락 원증상 해소. render 실패는004로 분리. |
| QA-PRESENT-004 | **STILL FAILING** | rendered DrawPos 고정과 cell/화면/hit target 불일치. health graph도 미복원. |
| QA-PRESENT-005 | **CONFIRMED RESOLVED** | Worker native→actual wire→periodic client native의4방향 일치. |
| QA-PRESENT-006 | **STILL FAILING** | forged Source로 invalid token/stale generation/wrong session을 우회해 control 실행. |
| QA-PRESENT-007 | **STILL FAILING** | main-thread ReadLine,2초 delay/control/frame stall 재현. queue/list/legacy 위험 잔존. |
| QA-PRESENT-008 | **PARTIAL** | periodic 수치 개선. method call/OS input 분류, 문자수/byte 명명, Position-only oracle 잔존. |
| QA-PRESENT-009 | **PARTIAL** | declared dependency와 class/Def 증상 개선. texture/null material/listener/native headless init 오류로 전체 clean load 미인증. |
| QA-PRESENT-010 | **CONFIRMED RESOLVED** | client authority target만 적용, viewed Map_1 불변, periodic UNRESOLVED_MAP 거부. canonical context identity 보장까지는 아님. |

001의 GUI adapter/negative-local-side-effect 및003의 response guard도 실제 GUI/periodic path로 회귀 확인했다. 공식 ledger는 편집하지 않았다.

## 14. Required next fixes / smallest verification

1. **Rendered mirror correction:** 비권위 presentation으로 Position/DrawPos/selection-hit coordinates를 일치시킬 것. actual Move의 중간3위치 이상, arrival/selection/inspect를 다시 검증. QA renderer patch나 native client simulation으로 대신 합격시키지 않는다.
2. **Control boundary:** untrusted Source 권한 분기를 제거하고 trusted role/channel/capability에서 도출할 것. 이번 forgedSource vectors를 negative regression으로 유지.
3. **Main-thread liveness:** periodic network wait를 main Unity thread에서 분리하고 in-flight bound/deadline/disconnect fencing을 명시.2초 delay/close 및 control responsiveness 재검증.
4. **Fixture/init evidence:** texture와 auxiliary listener 충돌을 정리하고 headless init 실패 범위를 명시. activeMods 일치만으로 clean load라고 선언하지 않는다.
5. **Evidence oracle:** direct method invocation과 actual OS click을 구분하고 rendered 위치를 검사. 이미 통과한 rotation/map/fencing은 변경 범위에 맞춘 focused regression으로 유지.

광범위 신규 PoC나 full-map prototype을 자동 요청하지 않는다. 수정한 새 frozen candidate에 위 조건을 한정해 재검증해야 한다.

## 15. Completion / architecture conclusion

QA process는 path/PID/start time 대조 후 종료했고, 이번 observer junction만 제거했다. candidate/Production junction은 유지했으며 source/DLL/log/frame/test scripts는 보존했다. `cleanup.json`.

1. **P2 Draft/Move slice:** Draft 실제 GUI loop와 Move autonomous 내부 상태 replication은 입증. **rendered Move가 따라가지 않아 전체 slice는 아직 proven이 아니다.**
2. **Candidate C:** PROVISIONAL 유지 권고. Master가 최종 결정한다.
3. **New existential blocker:** 새롭고 구체적인 gate blocker인 render-state divergence를 발견했다. P2/C가 원리적으로 불가능하다는 증거는 없으며, engine cache 수정 가능성을 이미 검증했다고도 주장하지 않는다.
4. **ADR-002 final acceptance:** render/control/liveness/fixture 조건과 별도로 기존 QA-ENGINE blockers, ADR-003 canonical inventory/provenance, ADR-006A temporal domain, ADR-007 remote authority/미결 정책, 후속 ADR-004/008 durable publication/transport/lifecycle 계약과 구현의 정합성이 필요하다. 이번 좁은 성공으로 이들을 닫거나 Production auth/WAN SLO/full-map replication을 인증하지 않는다.

**본 보고서로 작업을 종료한다. Master state를 변경하지 않고 다음 지시를 기다린다.**
