# QA — EngineHost Semantic Authority Gate04

[QA REVIEW]

- Work Package: **WP-QA-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-04**
- Reviewer: GPT-6.1 Sol — Independent QA / Architecture Reviewer
- Report date: **2026-10-05, Asia/Seoul**. Native evidence timestamps: 2026-10-04 UTC.
- Target: frozen `POC_EngineHost_Semantic_Authority_Gate_04.md`.
- Final verdict: **FAIL**.
- QA-ENGINE-002 recommendation: **STILL FAILING**.
- QA-ENGINE-006 recommendation: **STILL FAILING**.
- Master state is not changed by this report.

## 1. Executive finding

실제 RimWorld 프로세스에서 **발급자 증명이 없는 수제 receipt**가 수락됐고, 최종 `ARTIFACT_APPROVED`까지 도달했다. 더 강한 재현으로, 정상 결과 A를 봉인한 simulator와 별개로 변조된 저장 결과 B를 실제 validator에 로드하고 B를 설명하는 위조 기대 manifest를 전달했다. Validator는 receipt를 발급했고 simulator A가 이를 수락하여 **잘못된 followFieldwork와 bill suspended 값을 가진 저장 파일을 최종 승격했다**.

15개 잘못된 입력, 큰 Shooting/hediff/stack 저장 변조, malformed XML, 직접 승격, 경로 바꿔치기, 정상 reseal/reset 및 여러 변경 fence는 차단됐다. 실제 A→B→C transport, Goto/reservation 저장·재로드, 잠금 실패 보존과 정상 백업 교체도 확인했다. 이러한 개선은 인정하지만, receipt의 authority와 봉인 결과 결합을 증명하지 못하므로 Gate04 PASS는 불가하다.

## 2. Method and scope

QA는 동결 Production/PoC source, DLL, fixture를 수정하거나 재빌드하지 않았다. QA 전용 observer/harness만 작성·빌드했고, 복사한 profile/save로 실제 설치된 RimWorld를 독립 프로세스에서 실행했다. 실행은 `-batchmode`이며 실제 엔진의 load/save/control command를 사용했다. GUI 조작과 A의 최종 assertion 실행은 사용하지 않았다.

Silent saved-byte corruption은 **실제 SaveGame 직후, 후보가 staged SHA를 기록하기 전**의 QA-only fault injection으로 만들었다. 비활성 observer는 상태를 변경하지 않으며, mutation은 명시적인 QA 명령 또는 arm한 fault에서만 발생했다. 프로세스·로드된 assembly·native census·명령 응답·stage/final SHA를 직접 기록했다.

검토 계약은 Work Order 1~13과 ACCEPTED ADR-006B v2의 content-profile 경계다. 제품 SRS 전체, Production authentication, gameplay transaction 또는 final canonical publication 완료를 인증하지 않는다. 이전 UI 수동 체크리스트 통과는 이 Gate04 authority 판정과 별도다.

Evidence root: [SEMANTIC-AUTHORITY04-20261004](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004).

## 3. Exact provenance

| Artifact | Independently verified SHA-256 | Identity |
|---|---|---|
| RimWorldWin64.exe | `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D` | 1.6.4871 rev591; Unity 2022.3.35f1 |
| Assembly-CSharp.dll | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` | loaded MVID `61e41735-6189-4da4-9d21-0260257b5097` |
| WorkerBridge DLL | `8DB1D5A34DE2E3B2B6A61F078933D5828F2A99FB4E14E5694F7C3A8C80917EC9` | loaded MVID `9424f95c-8a3b-43b3-b99f-dd0b377d37b2` |
| WorkerBridge.cs | `A2AB7352B3069E94670F938A2404D83FFE0FB49B558B11E7E0754E6481091DB8` | PDB document checksum MATCH |
| EngineHostCensus.cs | `00985787D67FA2629B4A63FCF178842D3A48941AE6EDFEA78AC37B0DFA8D8B50` | PDB document checksum MATCH |
| WorkerBridge PDB | `92C10429F21AABEBD73B74831E6B6D5E6EF76D4AC2B53018C18016E39C782D01` | CodeView/PDB GUID `154dd5bb-fb9b-47af-a3b3-026697268cd2` |
| Clean source fixture | `BCDEA94EFEE63A609EA6652B24B8913CD8C74A5ABB1A36489D386E892FC44FC4` | historical source, not minimal closure proof |
| TargetSettlement_Clean_ContextB.rws | `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B` | actual independent QA input |
| A harness | `AD6FA026F7EA38005A8EF63AFE8CF2EEA03F56A788AF30F5E9EAC22581FFDBF9` | matches report; actual 62,461 bytes, reported 62,502 |
| A results | `A051DD4D93484DA61C96334A9720EC327E21EFD4AA9E8513251FEB6D06D1F4CC` | developer evidence only |
| Shipped census JSON | `DC27EF1C21E2C908C305F5E9426D6D98D0D6CA8417A671003B046733B2AC6ACC` | actual manifestVersion **3.0**, not V4 oracle |

The actual WorkerBridge load path was `C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll`. The installed junction resolves to `.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/WorkerBridgeMod`. Installed and local frozen candidate bytes match. DLL CodeView/PDB GUID and **4/4 source/generated document checksums** match; no candidate rebuild was used to establish lineage.

Actual load order:

1. brrainz.harmony
2. ludeon.rimworld
3. ludeon.rimworld.royalty
4. ludeon.rimworld.ideology
5. ludeon.rimworld.biotech
6. ludeon.rimworld.anomaly
7. ludeon.rimworld.odyssey
8. wareconomy.hybridmultiplayer
9. wareconomy.workerbridge.poc
10. qacodex.engine02.probe

Actual ModsConfig SHA: `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C`.

Independent clean V4 **engine manifest digest**, not file SHA: `9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC`.

A's Gate04 exported A/B artifacts were found by full path, with hashes `6D19520C1264E2B633C135538F5443EDC6A388474869C870AF2BDADE6152A877` and `5AEB809B1AEBE804F7122B37E0D21D80D88FBDEBD4DE41FA0C93713258093210`. Older same-named artifacts in other profiles have different hashes; they were not substituted.

Loaded path/SHA/MVID evidence: [native snapshot](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/job-target-native.snapshot.json), [mod metadata](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/RegressionBattery-metadata.json), [PDB lineage](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/pdb-provenance.json).

### Freeze limitation disclosed

**Exact engine candidate: 456 → 456 files; zero SHA/size changes.** This covers installed/local PoC, target fixtures, original profiles/A evidence, engine, Harmony, original QAProbe files and deployed WarEconomy Client/Common. Only the explicitly allowed QA observer filename is excluded and separately hashed.

**Whole Production tree: 353 → 353 files; 18 changes observed.** Six Server sources (`Program`, Pipeline coordinator/migration/models/recovery/aggregate store) and twelve Server build outputs changed during the run. QA did not write those files; the modifying actor is not established. No changed Server DLL was loaded by the tested RimWorld processes. Consequently exact EngineHost evidence remains tied to the unchanged candidate, but **repository-wide “Production unchanged” cannot be asserted**. This report is not a Server/Pipeline freeze certificate.

[Final freeze](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/final-freeze.json), [detailed Production drift](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/production-drift.json), [candidate before](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/candidate-before.json), [candidate after](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/candidate-after.json).

## 4. Critical attacks

### G04-01 — Critical — receipt issuer is not authenticated

- Requirement: Work Order 3; QA-ENGINE-002.
- Location: [StageValidationReceipt schema](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:42), [submission handler](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1852).
- Reproduction: clean admission → valid grant → seal/stage → caller-crafted visible receipt fields, `validatorProcessId=2147483646`, PASS → submit → promote.
- Expected: caller-created receipt cannot establish STAGED_VALIDATED.
- Actual: `STAGE_VALIDATION_ACCEPTED`, then `ARTIFACT_APPROVED`, receipt `QA-CRAFT-1791117039267876200`.
- Approved final SHA: `E0C9FE80BB34B3A56816632678CA7EF1196DDC1F2966DDAFB8A10DB98F8D26AF`.

Receipt has no MAC/signature, secret capability, nonce binding, protected issuer registry or trusted IPC/process-handle proof. Only equality with the simulator's own PID is rejected. Fake different PID works; **empty PID also works**. No validator issued the handcrafted receipt. A's “cryptographically validated” / “signed” description is unsupported by actual code.

Required fix: establish a real operator/orchestrator-controlled validator-task/issuer boundary and attest the exact task/result. A caller-provided PID or hash of visible data is not issuer proof. Public-key crypto specifically is not required.

Evidence: [critical results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/results.json), keys `handcrafted-bypass`; [fence results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/fences-results.json), `receipt-validatorProcessId`.

### G04-02 — Critical — forged expected B is promoted under sealed A

- Requirements: Work Order 4/8; QA-ENGINE-002/006.
- Location: [validator command](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1749), [receipt binding](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1886), [promotion](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1956), [subset saved-XML checks](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:1147).

Reproduction:

1. Simulator seals legitimate A, digest `9F7AA0CD…E8CC`.
2. QA changes a supported saved field after real serialization but before staged SHA capture. Live simulator A remains unchanged; staging B returns STAGED_OK.
3. Distinct real validator loads B. The **legitimate A expected digest rejects B**.
4. Caller substitutes B's self-census as expected `manifestJson`/`sealedManifestHash` in sealedResB64, preserving A's result ID/epoch/authority/grant.
5. Validator validates B against caller-nominated B and issues a real receipt.
6. Simulator does not compare receipt.sealedManifestHash with immutable sealed A. Live A→A and disk B→B checks pass separately; wrong B reaches ARTIFACT_APPROVED.

| Supported saved field | Legitimate A | Injected / reloaded B | B live digest | Approved B SHA |
|---|---|---|---|---|
| Labrador followFieldwork | True | False | `9EE09D2B80B4477FA98BE44C8456F22F466FFF8555D2ADC6D08CEB08CFD9CFB8` | `B345EED22CA632C1D579C7642889792ECACE1AA6E83355003965DC2101FA0715` |
| Sculpting bill suspended | False | True | `F1E4E249EF79D4967FEF0B44EB66EF867146021811656F5863099190C5C98B27` | `DAEBD5A7ABC77E4E66EC3217362C60B66FBA6BDA113E56C36C429BD537BFA371` |

Follow simulator/validator PIDs: **31984/27196**. Bill simulator/validator PIDs: **10328/34076**. Both produced a real STAGE_VALIDATED receipt, simulator acceptance and final artifact. The final stage/receipt/file SHAs match the wrong B bytes. This is supported-graph corruption, not an out-of-scope field or a forged success log.

Separately, caller-supplied **wrong SealedResultId, AuthorityId, GrantId, ResultEpoch** with unchanged correct manifest produced validator receipts but simulator rejected each. Those four equality fences work; they do not prevent manifest substitution.

Required fix: expected truth must originate from the immutable authorized result, not caller/self-baselined JSON. Submission/promotion must bind complete schema/digest/source/scope/map/epoch/generation/profile and authenticated validator task to that result. Exact byte validation must prove the supported graph of B equals trusted A, rather than disconnected A→A and B→B checks.

Evidence: [critical results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/results.json), `forged-expected-silent-follow`, `savedB-legit-A-silent-follow`; [supplement results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/supplement-results.json), `forged-silent-bill`; [fence results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/fences-results.json), `forged-metadata-*`.

## 5. Receipt fields / replay

| Single changed field in otherwise correctly bound receipt fixture | Submit | Final exists |
|---|---|---|
| stagedSha | REJECTED | False |
| stagedFilePath | REJECTED | False |
| workerGeneration | REJECTED | False |
| authorityId | REJECTED | False |
| grantId | REJECTED | False |
| contentProfileFingerprint | REJECTED | False |
| sealedResultId | REJECTED | False |
| resultEpoch | REJECTED | False |
| scopeId | ACCEPTED | True |
| targetMapIndex=999 | ACCEPTED | True |
| manifestVersion | ACCEPTED | True |
| sealedManifestHash | ACCEPTED | True |
| sourceArtifactHash | ACCEPTED | True |
| validatorProcessId empty | ACCEPTED | True |

Single-field tests deliberately use caller-crafted structures to isolate predicates; they do not claim authenticated provenance. The scope/schema/source/semantic-hash omissions also affect the actual validator-issued forged-B receipt.

An actual candidate-issued clean receipt from process 27196 was replayed into another simulator (15468) and rejected at result/epoch mismatch. Old stage after normal reseal (epoch1→2) and receipt after RESET were rejected. **Mixed replay cases are masked by earlier result/epoch checks**; they do not establish a process-bound identity check or each later binding. Isolated fixtures and real-validator wrong-metadata tests distinguish these cases.

Evidence: [fences-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/fences-results.json).

## 6. Fifteen persistent input regressions

Each test registered the real SHA of its corrupted copied XML, retained clean V4 expected digest, loaded the actual engine graph, then invoked VALIDATE_INPUT/STEP/SEAL/STAGE/PROMOTE. **15/15 rejected; zero final approved files**. Native final values matched the corresponding injections, so rejection was not merely a source-SHA mismatch.

| Case | Source expected → persistent injection | Native result | Correct V4 comparator errors |
|---|---|---|---|
| 01 | held Medicine count 5→4 | 4 | 1 |
| 02 | Shooting 10→15 | 15 | 1 |
| 03 | Stab severity 3→1 | 1 | 1 |
| 04 | BionicTongue present→remove | absent | 2 |
| 05 | master Human302→none; follow flags True→False | master empty; flags False | 3 |
| 06 | bill targetCount 10→25 | 25 | 1 |
| 07 | grow cell (139,145)→(139,146) | changed cell | 1 |
| 08 | Mine (150,150)→(150,151) | changed target | 1 |
| 09 | fireSize .45→.90 | .90 | 1 |
| 10 | Rice growth .5→.4 | .4 | 1 |
| 11 | Aurora duration 60000→12000 | 12000 | 1 |
| 12 | Bed990012 assignment→none | unassigned | 1 |
| 13 | Spouse Human309→ExSpouse | ExSpouse | 1 |
| 14 | battery 600→200 | 200 | 1 |
| 15 | nested Stool→WoodLog | WoodLog990031 | 3 |

[battery-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/battery-results.json), `input-01..15`, retains expected/injected source facts, input SHA, actual full live manifest, all command outputs and final absence. [canonical-comparators.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/canonical-comparators.json) records candidate CompareCensus against an independently obtained clean **V4** baseline in real engine process 6016.

The shipped `.census.json` is V3. Initial helper comparisons therefore included unrelated schema/normalization differences. Those raw outputs are preserved but **not the pass/fail oracle**. QA subsequently compared all recorded actual native V4 graphs against the correct V4 baseline, obtaining the case-specific errors above. Primary admission independently rejected exact V4 digest mismatches. No candidate fixture was edited.

## 7. Saved bytes / malformed XML / save errors

| Attack at native serialization boundary | Actual result | Final |
|---|---|---|
| Shooting 10→15 | STAGE_FAILED: saved skill mismatch | absent |
| Stab severity 3→1 | STAGE_FAILED: saved hediff mismatch | absent |
| held Medicine count 5→4 | STAGE_FAILED: saved stack mismatch | absent |
| EOF truncation | STAGE_FAILED: malformed XML | absent |
| second root | STAGE_FAILED: multiple roots | absent |
| DTD | STAGE_FAILED: DTD prohibited | absent |
| actual save-time Log.Error | quarantine; VALIDATION_FAILED | old approved file SHA unchanged |
| actual save-time exception | quarantine; VALIDATION_FAILED | old approved file SHA unchanged |

The first six were caught during STAGE_SAVE, before receipt issuance; do not label them independently passing fresh-validator tests. Follow/bill counterexamples passed subset staging, were correctly rejected under legitimate A by fresh reload, then bypassed through substituted B expectation.

The initial QA bill injector assumed an explicit suspended node; default False was omitted. QA corrected only its injector, then completed the bill bypass. Two optional staged plant-age tag attempts threw QA injector errors because the assumed default tag was absent; **they are neither candidate defects nor passed saved-byte plant tests**. Required native live plant-age mutation was completed separately.

Evidence: `stage-*` in [battery results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/battery-results.json), `native-save-*` / `forged-silent-bill` in [supplement results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/supplement-results.json), actual profile save-fault evidence and quarantines.

## 8. Authority / grant lifecycle

### G04-03 — High — validation failures retain capabilities

- Requirement: Work Order 7.
- Location: [RegisterAuthority](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1004), [RegisterGrant](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1109), [Submit receipt](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1852).

Invalid grant mode or blank grantId returns ERROR while retaining old valid grant/readiness; subsequent actual STEP and SEAL succeed. After receipt acceptance, empty REGISTER_GRANT / empty REGISTER_AUTHORITY / empty SUBMIT, or malformed grant/receipt JSON, returns ERROR yet the old stage can reach ARTIFACT_APPROVED. Malformed REGISTER_AUTHORITY after admission is different: its earlier post-load guard revokes and blocks correctly.

Expected: any specified validation failure revokes STEP/SEAL/STAGE/PROMOTE until explicit clean reset/re-admission. Required fix: one consistent failure transition covering early returns and exception paths, with retained diagnostics but no stale capabilities.

Evidence: `grant-allowedMode`, `grant-grantId` in [battery results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/battery-results.json); `malformed-*` in [supplement results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/supplement-results.json).

### G04-04 — High — scope / immutable identity omissions

Locations: [authority identity](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1059), [grant checks](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1109), [seal checks](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1522).

A grant with scopeId different from its registered authority is accepted; STEP/SEAL succeed. Replacing grant scope after receipt, keeping grantId, still permits final promotion. Receipt scope/map are unchecked. Same AuthorityId with changed **storeIncarnation** or **baseLineage** falsely returns AUTHORITY_ACK_UNCHANGED; those fields are omitted from equality. The old object is retained, but a semantically different bundle is acknowledged as identical.

Required fix: bind nominated source/context/map/scope across authority, grant, result and receipt. Include authority-defining lineage/incarnation in immutable identity, or explicitly remove them from the contract. Arbitrary initial opaque scope labels alone do not prove wrong ownership without a fixture-scope oracle; the definite mismatch is grant versus authority.

Correct cases: identical bundle ACK; changed targetMap bundle rejected; new authority after admission rejected; wrong source/hash/version/profile/map/generation rejected; foreign/stale-generation/wrong-map grant revoked readiness; unknown/blank seal grant rejected; old grant after RESET rejected. READ_ONLY STEP/SEAL remained blocked even when grant mode was changed to SIMULATION.

Additional scoped observation: tickBudget=1 still allowed five actual sliced ticks. This is not complete ADR-006A validation; grant budget/execution-class semantics must be defined before expanded use.

Evidence: [battery](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/battery-results.json), [fences](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/fences-results.json), [supplement](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/supplement-results.json); keys `grant-scopeId`, `fence-scopeGrant`, `authority-immutability-*`, `readonly-downgrade`, `grant-budget`.

## 9. Promotion fences

| Post-receipt attack | Native result |
|---|---|
| current epoch counter 1→2 | **ARTIFACT_APPROVED** |
| generation counter change | BLOCKED |
| live skill change | BLOCKED |
| staged SHA change | BLOCKED |
| caller path substitution | BLOCKED |
| normal reseal | BLOCKED; old receipt cleared |
| RESET | BLOCKED |
| profile XML bytes change | BLOCKED |
| active grant scope change, same ID | **ARTIFACT_APPROVED** |
| malformed receipt submission after accepted receipt | **ARTIFACT_APPROVED** |

### G04-05 — High — current epoch not fenced

Location: [promotion epoch check](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1984). Work Order 9.

QA changed currentResultEpoch 1→2 after receipt; old seal and receipt remained epoch1. Candidate compared seal to receipt, not current counter, and approved epoch1 bytes. This is **private-state fault injection**, not a demonstrated ordinary-client exploit. Normal SEAL_RESULT clears old receipt and works correctly.

Required fix: invalidate/bind against the current immutable result epoch on every permitted context/epoch transition. Test actual transition paths as well as injected inconsistent state.

Tests were deterministic mutations immediately after acceptance and before promotion, not exhaustive thread scheduling. Candidate closes its staged hash read handle before move/replace; no concurrent TOCTOU mutation in that interval was reproduced. That window is an untested limit, not a claimed reproduced corruption.

Evidence: [fence results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/fences-results.json), `fence-*`, `old-stage-reseal`.

## 10. Actual ContentProfile

### G04-06 — High — ModsConfig-only hash violates accepted content contract

Location: [GetActualContentProfileFingerprint](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:370). Requirement: [ADR-006B v2](C:/Users/user/Desktop/RimMulti/ADR-006B_Configuration_Content_Manifest_v2.md:10), including lines 82–83; Work Order 6.

Implementation hashes only ModsConfig XML. It does not hash actual loaded build/DLC/mod versions/assemblies/Defs/capability set.

Safe independent admitted-byte drift changed only the QA-owned observer in the active QAProbe package by a PE overlay. A fresh engine loaded it with:

- Original QA DLL SHA: `C0C7D0FE193E65F3132EB5E013584E7D19076C56D4E400D91A212F2DE75087EB`.
- Changed QA DLL SHA: `ED6E646709CA7FC4E11FC98EB00D9D6C743BA6981799449E7AB32E37DE43F1FD`.
- Same MVID: `819719f4-9b74-4b4a-93e3-dd6d55d8b9a6`.
- Same fingerprint: `FF23B58C…3207C`.
- INPUT_VALIDATED and one actual STEP tick succeeded.

This tests admitted assembly-byte coverage with a permitted QA-only input; it is not a runtime mutation of frozen gameplay DLLs/versions. A separate live WoodLog label change also retained fingerprint; a label alone is not proof of gameplay impact, but confirms no Def census enters this function. Static implementation establishes broader missing content coverage under ADR-006B.

Wrong config bytes, a post-load XML comment and post-load reordered mod entries change the hash and block the corresponding admission/step/seal/promotion. These test config fencing, not a fresh successful reverse-order dependency load. A content-identical comment can falsely reject: this is neither canonical semantic profile hashing nor an actual loaded-content manifest.

Required fix: operator-approved canonical content manifest fingerprint and independent actual-loaded-content admission. Freeze inventories cannot substitute for runtime content-profile binding.

Evidence: [content drift](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/content-drift-results.json), `same-config-assembly-byte-drift`; supplement `def-drift`, `reordered-profile`; fences `fence-profile`.

## 11. Manifest scope / non-tick mutations

Candidate hashes native ToJson. **102/102** changed representative declared primitive fields changed full digest. Partial CompareCensus still returned PASS for **68/102**, confirming that helper is not a complete equality oracle.

Actual same-tick changes from RESULT_SEALED, before first staging: skill, hediff severity, holder count, zone, designation, relation, bed assignment, followFieldwork, plant age, bill suspended, hediff part and loadID. **12/12** changed full hash without advancing TicksGame; no final was produced. Actual plant age became 12001, bill suspended True and followFieldwork False. Clearing a real reservation also changed full hash.

### G04-07 — Medium — revocation causes diagnostic NullReferenceException

Location: [stage recensus failure branch](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1667).

RevokeReadiness clears sealedResult; the immediately returned message dereferences sealedResult.sealedManifestHash. All twelve above returned `ERROR: NullReferenceException` rather than intended STAGE_BLOCKED. Readiness was correctly revoked and final output blocked. Required fix: preserve diagnostic data before revoking, then return the intended terminal error. This is not a successful corruption bypass.

The initial five representative attempts were masked because a helper had already staged before mutation, so a second STAGE hit STAGED_PENDING_VALIDATION. QA reran all twelve **before first staging** in supplement_resume.py. Only the unmasked rerun supports this conclusion.

### G04-08 — Medium — job/reference documentation differs from frozen implementation

A's report and Work Order say JobDef-only. **Actual code is stronger:** activeJob includes JobDef, loadID, targetA/B/C. Changing actual Goto target `(140,0,148)→(139,0,143)` changed full digest; the only native manifest difference was activeJob.targetA. Reservations include claimant, JobDef/jobLoadID, target, maxPawns and stackCount. This upgrade is recognized independently.

Complete job/job-driver graph remains unproven: arbitrary expiry/count/flags/toil/path-driver progress are not in ActiveJobRecord. Transport of this Goto and reservation cannot certify all active jobs. Also shipped census JSON is V3 while report's baseline is V4. Required fix: correct supported-field/evidence claims and freeze an explicitly versioned expected manifest/authority artifact. No candidate fix was made during QA.

Native clean loads emitted normalization messages: missing zero-valued skills added and hidden funeral precepts added. V4 baseline includes those skills. No missing Def/duplicate-load-ID/save exception was observed in clean positive runs. This is **not a warning-free whole-save source claim**; global precept normalization/unclassified state remain outside target graph proof.

Evidence: [battery](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/battery-results.json), `declared-field-matrix`, `job-target-scope`, `reservation-gate`; [supplement](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/supplement-results.json), `same-tick-*`; [ActiveJobRecord](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:111), [native job extraction](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:458), [reservation extraction](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:701).

## 12. Fresh validator / A→B→C

| Role | Simulator PID | Validator PID | Exact staged/final or input SHA | Sealed / loaded digest |
|---|---|---|---|---|
| A: input +20 ticks | 19048 | 19164 | `61EF1CC60530247DF8296CA6159BF4FE73E5F9970CE1BE79D7AA4BFE6ACA5F3B` | `38612A7DFBDD28D62677402A45FC7873ACC052AB02A64D5913480EDB0EC7E48A` |
| B: A input +20 ticks | 32512 | 32028 | `F49864AEBCD0EF2EE8F8A46522D28C33258C772F0300DF9FCAD751A0DC8B7B65` | `3C373210CD09D66C682E4D901299C8D53DAB084FDFF52FBF35CB0E61A415A168` |
| C: B input, transport only | 16220 | none | `F49864AEBCD0EF2EE8F8A46522D28C33258C772F0300DF9FCAD751A0DC8B7B65` | `3C373210CD09D66C682E4D901299C8D53DAB084FDFF52FBF35CB0E61A415A168` |

A started from exact clean target SHA and native clean V4 digest. B validated A's sealed digest; C validated B at TicksGame1863. Fresh distinct validators A/B used READ_ONLY profiles, SHA-identical staged copies with exact staged basenames, and native full manifest comparison. The expected seal, receipt ID, simulator/validator PID, savedata, actual profile hash, source/staged SHA, actual loaded manifest, simulator acceptance and final SHA are retained in `ChainAFresh-fresh-proof` / `ChainBFresh-fresh-proof`.

Both final SHAs equal stage SHAs. QA directly observed process separation, but candidate has no issuer authentication. **A/B are transport/functionality regressions, not authority-valid positive promotions under Work Order12.** C is post-promotion transport only. Post-tick self-census/seal is evidence output, not independently trusted expected authority by itself.

Real Goto/reservation trial: Human302, target `(140,0,148)`, Job_200006, maxPawns1/stackCount−1. Fresh validator **7048** preserved job target/loadID and reservation; both native digests were `3AF1B61C3B7A2EA7C4CE0AC383DF4A931529C1B86D3F3CF5BE886624E569D922`. Detailed before/after native snapshots retain job fields. This is persistence evidence for the tested slice, not full driver-state canonicalization.

Evidence: [positive results](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/positive-results.json), [fresh chain](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/fresh-chain.json).

## 13. Replacement safety

Exclusive Windows FileShare.None lock caused PROMOTION_FAILED. Prior final SHA `61EF1CC60530247DF8296CA6159BF4FE73E5F9970CE1BE79D7AA4BFE6ACA5F3B` stayed unchanged; staged SHA `BD79B8C5C4D6B0D6E8D18169972AFD9ED37755BD76D07CC86A03332354687422` remained recoverable; readiness revoked. Lock helper exited normally.

After explicit clean reset/re-admission and new fresh validator, successful replacement produced:

- Correct prior-file backup SHA: `61EF1CC60530247DF8296CA6159BF4FE73E5F9970CE1BE79D7AA4BFE6ACA5F3B`.
- New stage and final SHA: `5406D46002905BC1DC2DA50EC3D1381CFE32DF64BB64592421E90E91E4616E70`.
- Exact stage/final bytes and correct backup: True.

No receipt/direct RESULT_SEALED/staged-pending promotion was blocked. Tested ordinary replacement/lock behavior holds. Static UnauthorizedAccessException fallback uses copy-overwrite then delete, **not crash-atomic replacement**; that fallback/crash boundary was not forced. It remains a durability limitation, not a claimed reproduced corrupted artifact. Final G-Q6 stays open.

Evidence: positive `exclusive-lock`, `successful-replacement`; fences `no-receipt`.

## 14. Disposition

| Existing defect / prior finding | Recommendation | Basis |
|---|---|---|
| QA-ENGINE-002 | **STILL FAILING** | unauthenticated issuer; actual expected-B substitution approval; profile/lifecycle gaps |
| QA-ENGINE-006 | **STILL FAILING** | supported follow/bill corruption approved under sealed A |
| G03-01 saved-byte proof | PARTIAL | fresh reload added; trusted-A comparison works; substituted-B bypass remains |
| G03-02 direct/path promotion | PARTIAL | no-receipt/path blocked; forged receipt bypasses gate |
| G03-03 malformed XML | tested regression holds | EOF/second-root/DTD rejected; no final |
| G03-04 lifecycle | PARTIAL | many id/read-only fences work; failure branches/lineage equality incomplete |
| G03-05 epoch | PARTIAL | normal reseal/reset works; current-counter inconsistency not fenced |
| G03-06 full manifest/scope | PARTIAL | complete declared digest, job targets observed; documentation/reference mismatch; full drivers unsupported |

Master/A should establish trusted validator-task/receipt issuance, bind expected truth to immutable sealed result, cover every authority/result/receipt context field, finish failure revocation, and implement accepted actual-content fingerprint contract. Correct job/V4 evidence and revoked-result error reporting. Then freeze a new candidate and rerun these exact native counterexamples plus positive transport/replacement. QA did not implement those fixes.

## 15. Limits / cleanup / final recommendation

Context remains **Pruned Target-Map Owner Context**. Minimal dependency closure is not certified. **G-Q1, PlayerGlobal schema, final G-Q6, material-state Production, Trade/Tax remain open.** No complete ADR-006A temporal implementation, whole-save canonicalization, gameplay transaction or Production authentication is certified.

QA observer was rebuilt only to correct instrumentation assumptions. Initial bill/plant XML assumptions and a concurrent evidence-read JSON parse error were QA tool interruptions, not candidate defects; bill and V4 comparison were completed afterward. Optional saved plant-tag injection did not establish corruption and is not counted. Required live plant-age coverage completed. Deterministic changes are not exhaustive concurrency proof. Windows command-length rejection while drafting this report caused no candidate write.

Every QA-owned RimWorld process exited code0; no forced kill was required. Lock helper exited code0. Temporary observer was removed after owned SHA verification. A system-wide CIM query was denied; cleanup proof is owned process handles/exit records and no RimWorld returned by Get-Process. No unrelated process was terminated. Candidate original fixtures were not overwritten/repaired.

[QA hash inventory](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/qa-evidence-manifest.json), [observer removal record](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Evidence/observer-removal.json). The inventory is regenerated after final report emission; per-process native evidence remains preserved.

**FAIL. QA-ENGINE-002 and QA-ENGINE-006: STILL FAILING.** Transport and fresh-load mechanisms improved, but authenticated semantic approval is not established. Retain the relevant authority/publication blockers and request a new frozen candidate closing G04-01/02. Repository-wide Production drift is separately disclosed; no blanket unchanged claim is made. Master state is unchanged by QA.
