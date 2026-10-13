# IDE Bootstrap Verification — LOCAL-BOOT-20261007-01

검증 시각: 2026-10-07T17:23:56.891754+09:00 (Asia/Seoul). IDE Master의 로컬 context recovery 결과다. 구현·재설계·candidate 재빌드는 수행하지 않았다. `migration_bootstrap_verified=true`는 아래 대조와 불확실 항목 기록의 완료를 뜻하며 runtime PASS, 결함 closure, 모든 dispatch prerequisite 충족을 뜻하지 않는다.

## 1. 실제 저장소/SRS/AGENTS/Git

| 항목 | 실제 확인값 |
|---|---|
| 작업/source 루트 | `C:\Users\user\Desktop\RimMulti` |
| Production solution | `WarEconomyMod/WarEconomy.slnx` |
| 실제 handoff | `docs/WarEconomy_Master_Handoff_20261006/00_START_HERE.md` |
| Canonical SRS 원문 | `docs/요구사항_명세서.md`, SRS v1.0 / Requirements Baseline Draft |
| AGENTS | 루트 `AGENTS.md`; 설치 전 패키지 AGENTS SHA와 동일, 2,367 bytes |
| Git | `git status --short --branch`, `git rev-parse --show-toplevel`, `git log -5` 모두 `fatal: not a git repository` / exit 128. 작업 루트 하위 `.git` directory/file 검색 결과 없음 |
| branch/HEAD/dirty diff | 확인 불가. clean으로 선언하지 않으며 Git 초기화/commit/checkout하지 않음 |
| 환경 | .NET SDK 10.0.201, Python 3.13.5. 설치 runtime에 .NET 8.0.10/9.0.7/10.0.5 존재. 기존 Pipeline evidence는 .NET 8.0.10 / SQLite 3.41.2 |

루트 `요구사항_명세서.md`는 없고 실제 원문은 위 docs 경로다. `요구사항_정규화.md`나 brief로 원문을 대체하지 않았다. SRS FR-001/002/003, FR-153..158, FR-187/197..212, NFR-004..008/012, CON-008..010, AC-001/002/011/015, TBD-01..05를 accepted ADR/후속 correction과 대조했다. 서로 다른 Local Date/Season은 요구지만 한 client에서 divergent clocks의 동시 실행을 요구한다고 확대하지 않는다. SRS §77의 선호 candidate를 후속 accepted authority 결정 위에 두지 않는다.

Root AGENTS 기존 내용을 보존하고 실제 recovery 경로·durable governance pointer만 추가했다. premerge 원본과 기존 governance는 `bootstrap/premerge/`에 보존한다. Git checkpoint가 불가능하므로 이를 파일 백업으로 구분한다.

## 2. Candidate identity / evidence — MATCHED, CHANGED, MISSING

세부 절대경로·bytes·expected/actual SHA/MVID는 [로컬 inventory](bootstrap/local_identity_verification.json)에 있다. PE MVID는 ECMA-335 metadata를 byte로 읽었고, 소스/PDB 확인에는 기존 QA harness의 read-only `pdb` 모드만 사용했다. QA runtime battery나 게임 simulation을 다시 실행하지 않았다.

### Pipeline REV5

| Identity | 실제값 / 결과 |
|---|---|
| Server DLL SHA | `1143AE62FD74F0C93F0504B48C1501D5153F40C2E903BD4D69BA9BE1E6983479` MATCHED |
| Server MVID | `a5cba4c3-1e2f-4a19-a35c-0241ccf12e81` MATCHED |
| Common DLL SHA | `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB` MATCHED |
| Common MVID | `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7` MATCHED |
| manifest | `docs/RELEASE_MANIFEST_PIPELINE_REV5.json`, SHA `D609795D8B50ED98850B8C73E951EA7F8E9B21B6193E815CF4890B9E2BB7D9E6` MATCHED |
| release/schema/signature | WP REV5 / schema 6 / signature `64BDB62037D70303D7F2AE15D39FC7E7DFD9F01021B5E0AA0709A51FA507E721` |
| manifest entries | binary 5 + modified source 6 + E1 result 1 = 12/12 SHA MATCHED |
| Server PDB | CodeView/PDB GUID `6b39adbc-ea0a-4b50-a980-c6e09aa5725c`; actual document checksum 20/20 MATCHED |
| Common PDB | CodeView/PDB GUID `f46ba950-aebf-4e2a-9a7c-b346c7519b51`; actual document checksum 25/25 MATCHED |
| prior Production freeze | 353/353 recorded files SHA MATCHED; 旧 inventory 전체와 현재 directory 전체가 같다는 확장 주장은 하지 않음 |
| QA inventory | 515 entries 중 514 원래 위치 MATCHED. QA report 1개는 원래 root 위치 MISSING, `docs/QA_Production_Transaction_Pipeline_01_REV5.md`로 이동하여 SHA MATCHED |

[현재 Server PDB](bootstrap/server-pdb-current.json), [현재 Common PDB](bootstrap/common-pdb-current.json), 기존 `Evidence/provenance-complete.json`, `runtime-metadata.json`, `execution-summary.json`, `semantic-results.json`, `lifetime-results.json`, `schema-collation-results.json`, `collation-confirmation-results.json`, 실제 READY/LISTEN raw log를 대조했다. 원시 결과의 historical-earlier/later/other-scope `ready=true`, current V6 collation 승인과 실제 actor/scope 구별 실패가 report의 FAIL과 일치한다. 5개 INVALID_REQUEST/durable0, final writer dead/post-dispose calls0/Main-return 증거도 좁은 closure 설명과 일치한다.

REV5 보고서 sample DDL과 실제 frozen DDL 차이는 보존한다: history PK=(ProbeScopeId,ProbeRevision), audit PK=AuditId, principal/op composite FK. 보고서 예시 DDL을 canonical 구현으로 재인용하지 않는다. manifest TimestampUtc가 2026-10-04인 것도 기록값으로 보존하고 최신 release 완료 시각으로 재해석하지 않는다.

### Engine Gate05

| Identity | 실제값 / 결과 |
|---|---|
| 선택한 Gate05 DLL | `scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll` |
| SHA / MVID | `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C` / `12bb9237-1b3e-4b20-89a7-69ad729861e1`, MATCHED |
| 같은 candidate copies | scratch 루트 DLL, `Source/bin/Debug/net472` DLL, 실제 game Mods 배포 DLL도 SHA/MVID MATCHED |
| WorkerBridge.cs | `BC9FD8DAA608892E97903BA56114B7186BABF29157ADAE45658238C3DD497549` MATCHED |
| EngineHostCensus.cs | `954C12F7500EC0BF4AE8265D2F66EFA39369A69F2C9DF3D1DBA20A9F54CBD024` MATCHED |
| recovered matching PDB | `scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb`, SHA `4B86A8634C8B13D2A20EA51D27B5A9F7B067FA976A8C0503107C18C5A7656862` |
| recovered lineage | CodeView/PDB GUID `3749afca-3905-4d55-a151-cc7e75b85649`, document checksums 4/4 MATCHED |
| clean fixture / V4 census | `scratch/TargetSettlement_Clean_ContextB.rws` SHA `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B`; census SHA `9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC`, MATCHED |
| game EXE/core assembly/probe | report SHA MATCHED; core MVID `61e41735-6189-4da4-9d21-0260257b5097` MATCHED |
| harness — CHANGED | expected `019CFB698EE54CF3AE92F6423C3FFBA46CE92FFD433604313B011D2503554DFD`; actual `4B7F1199BCF3181683D28B2DE7E8B3B4FF54C94F6FA11D1C591D1F36DBE529C5` |
| E1 results — CHANGED | expected `BE2C130AF5952CAE6370B02008E1905EAE060A6E0F89531BC50A2098495449A5`; actual `DA193776BDC61A9E4315D6E39B0B92760B3814B4C400F33F22CC9E7D7D9B855A` |
| different Release DLL | `Source/bin/Release/net472` SHA `F526ED47B505EC4D2F7436E700CAD58B01F9CE8FFEC2DFD8425B07C76EB9FC93`, MVID `3311985e-a8d8-464f-8e9c-66ccd8c677c8`; Gate05 대상 제외 |
| mismatched deployed PDB | 1.6/Assemblies 동반 PDB SHA `CF731E9B5CA6165B912A71A3D7E8374F2BF17D1D012C5A5A5533F72E19F90F65`, GUID `d3439e61-3fdd-4a2b-829b-a711637aec0f`; 선택 DLL과 불일치, lineage 증거로 사용 금지 |

정확한 DLL과 matching Debug PDB/source를 **발견**했으며 파일 교체·PDB 덮어쓰기·재빌드는 하지 않았다. [초기 PDB 대조](bootstrap/engine-pdb-current.json), [PDB 검색](bootstrap/engine-pdb-search.json), [복구된 matching PDB 대조](bootstrap/engine-pdb-recovered.json)를 모두 보존한다.

Report byte sizes도 일부 틀리다: Worker DLL 104,960→실제166,400; probe DLL 6,656→실제11,264; census source77,543→실제77,542; harness82,060→실제82,065. SHA가 같아도 잘못된 size를 고쳐 읽어야 한다. Harness/results는 BOM/LF/CRLF/final-newline 변형으로도 expected SHA를 복구하지 못했다. 원인을 cosmetic change로 단정하지 않는다.

Gate05 E1 65/65는 이전 accepted **developer report** 상태로 보존하며 현재 raw result/harness를 그 보고서 identity와 같다고 인증하지 않는다. Independent E2는 위 unchanged exact DLL을 대상으로 QA-owned harness/fixtures에서 새 증거를 만들고 자체 before/after freeze를 기록해야 한다. Matching PDB를 복구했으므로 독립 audit 전달은 가능하지만, provenance drift의 원인/범위와 runtime loaded-content profile 재검증은 E2의 열린 확인 항목이다. Profile `7DDC73...F8D40`은 기존 E1 주장값이며 이번 bootstrap에서 live fingerprint를 다시 계산하지 않았다.

## 3. Blockers / CLOSED 범위 / Foundation HOLD

- Pipeline REV5 E2 **FAIL** 유지. 007 HIGH OPEN: original observed revision의 durable decision binding, full typed audit mandatory field/type/status/reason/FailureReason/parent/scope/event/receipt/revision consistency.
- `MIG-PIPE-V6-COLLATION` HIGH OPEN/provisional 유지. 기존 canonical ledger는 Pipeline019까지 및 WATCH020 등을 포함한다. WATCH를 새 defect 번호로 치환하지 않는다. Historical V5 008 CLOSED는 current V6/future schema 인증이 아니다.
- 001 CLOSED는 이번 typed input/exact JSON 시험 범위. 총 입력 크기·미래 serializer까지 인증하지 않는다.
- 013 CLOSED는 actual writer/coordinator/final Shutdown/Dispose/Main/UNKNOWN convergence 시험 범위. 무관한 server task나 모든 pooled handle lifetime까지 확대하지 않는다.
- 019 기존 tested closure/regression 유지. 다른 historical defects는 omission으로 닫지 않는다. 004/005/006/014는 P1 NOT APPLICABLE/DEFERRED CONCRETE-CONSUMER GATE이지 underlying delivery 문제 CLOSED가 아니다.
- Engine002 CRITICAL/006 HIGH OPEN. Gate05 E1 accepted / independent E2 pending. G-Q1 및 exact global fields/physical split OPEN.
- **Foundation HOLD**: Pipeline의 historical/audit/current schema admission이 independent E2 PASS 전이며 Master runtime release가 없다. Engine/G-Q1을 모든 metadata의 blocker로 확대하지 않는다. Production material/Trade execution/Tax/Genesis/Tactical은 각 relevant 추가 gate도 필요하다.

## 4. C 원문에서 채택 금지인 주장과 controlling correction

Consolidated correction을 먼저 읽고 역사 리뷰 MSR-003/009..026/033/034/037/040/042/046/047/049/056..060/062/065 및 MDR 후속 결정과 원문 3개를 대조했다. 아래 표는 새 정책이 아니라 이미 accepted correction의 적용이다.

| 채택하면 안 되는 단정 | controlling source / 적용 |
|---|---|
| Research/Ideology/History/Genes의 exact owner=PlayerGlobal 확정 | consolidated§3, MSR-065, MD-104/116: taxonomy retained, fields/owner OPEN |
| Quest/WorldPawns는 read-only projection | consolidated§3/7, MSR-047/065: lifecycle/mutator/reference/custody/GC proof 필요 |
| Tales/PlayLog는 discardable | consolidated§3/11, MD-119: discard/rebuild noninterference runtime evidence 필요 |
| Storyteller/Incidents session별 re-roll 허용 | consolidated§3, MSR-062/065: 미채택, temporal/domain/material 결과 미증명 |
| Weather/Sky는 visual-only이므로 사전 허용 | consolidated§3/11, MD-105/119: plant/job/condition/material 영향 증명 필요 |
| UTC가 canonical World ordering/deadline 소유 | consolidated§4, accepted ADR-006A§2/8/9: committed Server W; UTC/M은 operational/logging |
| frozen resident chronological age는 global chronology로 진행 가능 | consolidated§4/11, ADR-006A§7: biological/chronological 모두 authorized residence/local policy |
| Faction/SharedWorld revision은 일괄 diagnostic | consolidated§5, MD-118: material dependency이면 hard-bound, independence proof 없이 diagnostic 금지 |
| literal .rws→MapBlob+PlayerGlobalBlob split이 E-B/Genesis PoC 선행조건 | consolidated§6, MSR-065, MD-116/120: physical split OPEN; bounded dependency/revision으로 probe 가능 |
| one Settlement=one process / separate process guaranteed zero drift | consolidated§9/11, MSR-062, corrected runtime contract: island/LocalClock가 unit, isolation도 test hypothesis |
| lease holder가 canonical PlayerGlobal revision을 독자 commit | consolidated§2, MD-117: Engine/Client bounded proposal, Server final Domain Authority |
| raw XML/SHA equality가 semantic oracle | consolidated§10, MD-103: fresh-load supported census/manifest, allowed differences, identity/custody/conservation controls |
| no null reference=minimum context proof, Model A fail=massive B/자동 C | consolidated§8/9: Pruned Target-Map Owner Context non-minimal/unproven; bounded evidence-driven comparison |
| resume 후 sibling B는 absolute unchanged여야 함; Silver spawn 자동 neutral | consolidated§11, corrected contract Controls/Barrier: same-tick-schedule control, explicit grant/write-set/material accounting |

`UNOBSERVED/UNSUPPORTED`를 PASS로 쓰지 않는다. C runtime contract는 experiment specification이며 runtime closure가 아니다. docs의 원문 bytes는 유지하고 각 sidecar와 `MASTER_GOVERNANCE_CURRENT.md`에 controlling pointer를 둔다.

## 5. 다음 WP / 전달 전 checkpoint

검증 완료 직전 두 WP 모두 **NOT SENT**다. 승인된 원본 [A REV6](WP_PIPELINE_REV6.md), [Sol Gate05 E2](WP_QA_ENGINE_GATE05.md)는 그대로 보존한다. 전달 이후 상태는 `DISPATCHER_STATE.json`, `DISPATCH_JOURNAL.jsonl`, dispatch board에 실제 message/turn evidence로 갱신한다.

- A: 최신 사용자 답변은 **별도 Antigravity IDE에서 작업**한다는 위치 정보다. 현재 tools는 native app 제어를 제공하지 않아 직접 전송/idle/active WP를 확인할 수 없다. 기존 완료 보고만으로 새 idle을 주장하지 않는다. REV6 문구를 `DISPATCH_MESSAGE_A_REV6.md`에 준비, NOT SENT 유지; Engine candidate before/after 보존을 원본 WP 그대로 요구한다.
- Sol: `Review WarEconomyMod QA`, thread `01a10fd9-2f90-79e2-a1c4-a1079c99f3ac`, host local, cwd 실제 root. 사용자 Work Order상 GPT-6.1 Sol이며 최근 REV5 E2 final FAIL/완료와 idle을 읽어 확인했다. 동일 candidate source/PDB lineage를 복구했고 전달 직전 freeze/idle를 재확인하여 기존 승인된 WP만 보낸다. Drift sidecar를 함께 전달하고 stale Release output 재빌드/교체를 허용하지 않는다.
- C: routine 새 WP 없음/on-demand only. 새 agent/chat 생성하지 않는다.
- Dispatcher: endpoints의 A route 미확인, unattended non-overlap lock/scheduler 미설정. journal/state 경로를 명시하되 `automation_enabled=false` 유지. bootstrap=true만으로 활성화하지 않는다.
- 후속 Pipeline REV6 E2: A E1 freeze + Sol Gate05 완료/idle 이후 Master 승인 전달. Foundation은 별도 scoped release 전 HOLD.

## 6. Governance 대조 / 병합 / 불확실 항목

1. 패키지 premerge 48 entries: 47 MATCHED, package AGENTS만 MISSING. Root AGENTS가 동일 SHA로 설치돼 있어 relocation/install 차이로 판정한다. `PACKAGE_MANIFEST.json`은 원본 package provenance로 보존하고 current mutable governance checksum이라고 재생성하지 않는다.
2. 실제 docs MSR-043/MDR-043/QDL-047은 패키지 history MSR-067/MDR-067/QDL-064보다 내용상 앞선 checkpoint다. 표의 과거 active/CLOSED/consumer wording은 후속 delta/MD-056/MAC-001/MD-060/122/123/126..132와 current migration delta를 함께 적용한다. 파일 번호만으로 overwrite하지 않았다.
3. docs `ADR-007_..._v5.md`가 별도 존재하지만 본문 title은 v4다. Local SHA `A7F57D298D823A0DAB95021E7232EC915F3DC60BF6943170B0F9BCFCE49D610A`는 package v4 SHA `4E29479D74EC8A55A2D6C0640217514502C08436E764DA0B9324C7C687387D24`와 **다르다**. [실제 diff](bootstrap/adr007-local-v5-vs-reference-v4.diff)는 단순 format 차이 외에도 ACCEPTED header/acceptance clarifications, DELTA_BARRIER designated checkpoint, responsive writer의 current committed head 평가, lease base와 artifact watermark 구별을 포함한다. 이 local amendment를 구형 package v4로 덮어쓰지 않는다. 더 큰 filename 숫자만으로 전체 본문 ratification도 추론하지 않는다. Controlling core acceptance는 MD-026이고 scope/fence/grace 및 material stage-before-commit은 MAC-001/MD-056/MSR-046/060/후속 correction을 함께 적용한다.
4. package source_reports와 로컬 named report 7개 SHA MATCHED. Gate05 raw harness/results drift는 report file 자체가 달라진 것이 아니다. Original QA report의 root/file URI 링크가 docs relocation으로 stale인 것도 pointer에 남긴다.
5. 최신 사용자 지시(한국어/local bootstrap first/A Antigravity/authorized WP after verified idle/C routine 제외/durable logging)를 decision log에 기록한다. accepted ADR/closure는 새로 만들지 않고 recovery disposition/dispatch readiness만 추가한다.
6. Git HEAD/dirty 상태는 미확인이고 source tree를 clean이라고 주장하지 않는다. A의 active WP/idle/자동화 endpoint, E1 harness/results mismatch 원인, live loaded-content fingerprint, 모든 역사 C 원문 확보 여부는 OPEN/UNVERIFIED다. 별도 IDE의 상태를 Codex endpoint로 추측하지 않는다.

최종 local post-check와 전달 근거는 bootstrap의 후속 inventory 및 dispatch journal로 남긴다. 앞으로 결정/리뷰/closure/dispatch마다 이 active governance와 journal에 durable delta를 기록한다.


## 전달 후 checkpoint — 2026-10-07T17:27:10.236005+09:00

Sol Gate05 독립 E2는 **SENT → ACKNOWLEDGED → IN_PROGRESS**로 확인했다. 전송 tool 성공, 새 turn `01a11577-1a0d-7c30-9e57-9f09aaa9f695`, acknowledgment message `msg_0cbd636361551f57016ac601ebc87c87d099b177cf040290ec` 및 “Gate05 bootstrap·동결 자료를 확인한 뒤 지정 DLL의 독립 검증을 진행”이라는 실제 commentary가 근거다. 원본 WP 전체가 prepared prompt에 포함되고 검증/freeze/raw evidence의 실제 local paths를 함께 전달했다. [전송 근거](bootstrap/sol-postdelivery-proof-confirmed.json). E2 완료나 PASS를 주장하지 않는다.
A REV6 **NOT SENT** 유지, [Antigravity 전달 준비 문구](DISPATCH_MESSAGE_A_REV6.md). 사용자 위치 정보 외 idle/활성 WP/direct endpoint 미확인. C routine 새 WP 없음. 자동화 config directory C:/Users/user/.codex/automations는 관측 시 존재하지 않았으며 Dispatcher는 endpoint/non-overlap/scheduler 미충족으로 disabled 유지한다.
Bootstrap 완료 시점의 원본 보고서는 [immutable checkpoint](bootstrap/IDE_BOOTSTRAP_VERIFICATION_at_bootstrap.md)에 보존했다. 후속 state는 current report SHA와 immutable bootstrap report SHA를 별도로 저장한다.
