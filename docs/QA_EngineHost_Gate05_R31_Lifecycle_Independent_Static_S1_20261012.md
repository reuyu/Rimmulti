# R31 lifecycle independent static QA — S1

Verdict: **MANAGED_CUSTODY_RESOURCE_AND_EVIDENCE_REVISION_REQUIRED_NATIVE_UNTESTED**. Durable required-pair mode, lifetime registration-spent protection, Update entry guards and retained-owner OnDestroy cleanup are source improvements. Managed custody and Awake failure cleanup remain incomplete, and the E1 declarations contain real hash/size/map discrepancies. This review executes no candidate, compiler, runner, Unity lifecycle or adverse case. The 20 source cases and 20 claim assessments are static analysis, not executable PASS. No historical candidate result is inherited.

Delivery `SOL-GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012-01`; WP `WP_QA_ENGINE_GATE05_R31_LIFECYCLE_INDEPENDENT_STATIC/S1`; result `SOL-GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012-4daa915adcc94695b0a5a572785cef27`. Original Sol endpoint `01a11583-ff90-73e0-8916-d021e2bb038d/local`, reporting directly to Master `01a1156b-97ec-7ce0-9e4a-dfc4a3acb174/local`. Initial ACK remains immutable; terminal binding is a separate file.

QA evidence root: `C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012`. The mandatory SRS, C corrections, accepted authority map, current governance/state/decision/defect/dispatch/journal and R31 contracts/review were read. Master review observations were challenged against actual frozen source, bytes and metadata. No governance, scheduler, dispatch or defect closure was changed.

## Exact identity and scope

Freeze manifest SHA `F8770090C7CB2D03077A9A7336D13F7F9F61E9F0D2DABB442BA62669B24EA3E4`, 131 files. Selected Debug SHA `F6C06D6B1392C5CF90483D047150D53A80193DED655850BF1A06FE65A72A52CE`, MVID `f8c7c77e-e2c5-4d3e-9371-a4e349d433c9`; PDB SHA `FDCE1F62777DC49C8F00DE1E7899B106564471983F2A34105F290491984BF466`, 78704 bytes. WorkerBridge source SHA `CB1EE0A55512A6F578B2D7ABCACBE36B62327D9F3E585B6E4221725B6DADFFDB`, 272607 bytes. Separate Release SHA `2B8220B6A02ADEBBB318BB5E5AA98569C7B89BE98E3DC77D725075538406458E`, MVID `130c2741-3e20-4275-9891-d4aea8adffd3` is metadata only.

Fresh QA file-byte readers independently bound both PE MVID/CodeView to matching PDB GUID and all four PDB source hashes to exact frozen mappings. Definition-only reader modules were byte-copied into the new QA root with provenance; no older QA or producer top-level helper was imported or executed, and no Assembly.Load was used. SHA/PDB identity is not runtime or authority proof.

Entire source comparison uses actual R30 frozen source `B1F8C00D1DF6E8E797EAC8E5A7F7FB462679BA06E79096D5C558C687BD413311` /268703 bytes and independently locates all eight unchanged chunks. Their total is 260917 bytes. PURE/Capture/currenttask/receiver/Census/csproj/publisher and the old Update body remain fixed by the protected inventory and outside-byte comparison. Actual seven changed half-open byte ranges are:

| Source span | R31 byte range |
|---|---:|
| Bootstrap mode/handoff | 7573..10098 |
| Private durable mode/owner state | 27259..33326 |
| Awake required-mode entry | 38131..39339 |
| Awake success/failure tail | 41273..42068 |
| Update entry guard | 42513..42762 |
| Pair-mode launch HOLD | 118113..118383 |
| Owner-scoped OnDestroy method | 185129..185705 |

All seven producer-declared new ranges and all seven corresponding new span hashes differ from actual bytes. Original-span declarations and whole-file headers do not cure those errors. `INDEPENDENT_SOURCE_BYTE_MAP.json` contains entire changed-span witnesses and the complete outside comparison; producer originals were preserved.

## Connected lifecycle findings

Bootstrap selects durable required mode against the exact installed parent receipt before creating/attaching the controller. Set marks registration spent, retains exact owner/parent cohort and pending payload under the lock. The spent flag has no reset after consume/cleanup/destruction, so the R30 per-slot re-registration weakness is addressed in source. Valid acquire transfers and clears only the child payload; required mode does not depend on slot availability. Missing, wrong-owner and post-consume instances in an already selected pair process cannot fall back to legacy under the normally reached acquisition branch.

Update first rejects an incomplete/null-profile required instance and then any global abort, before the old request/simulation/clock body. M05 also holds on static mode/abort. OnDestroy uses retained owner rather than evaluating this.gameObject, catches owner cleanup failures, then sets its own isRunning=false and independently attempts callback/listener/thread cleanup. These are source gains, with no native timing or atomic rollback observation.

Remaining corrections and qualifications:

1. Both owner cleanup methods use overloaded Unity `owner==null` and `registeredOwner!=null` before ReferenceEquals. Acquire also short-circuits custody on overloaded null. Exact managed identity can therefore be excluded by native liveness in the conditional reference model. Mode/spent HOLD does not prove matching pending-payload cleanup.
2. Awake reads this.gameObject before marking instance required mode. If that getter throws, the catch marks global abort: Update remains blocked and M05 remains held. **This is not evidence of legacy simulation/launch bypass.** Retained owner may be absent, leaving matching cleanup unavailable. Actual getter exceptions were not executed.
3. Awake catch marks initialization incomplete/aborted and attempts own callback/listener/thread cleanup, but leaves isRunning=true. ListenLoop uses while(isRunning). Matching owner cleanup is outside a protective try and can escape the intended failure handler. Neither a surviving thread nor native socket behavior was observed; robust own cleanup cannot be claimed from Stop/Abort attempts.
4. Additional source countermodel: an unrelated/wrong component can mark global abort while the legitimate pending payload remains. Legitimate owner acquire does not check abort; with a valid profile its Awake can reach listener/thread setup and initialization-complete assignment while Update and M05 remain globally held. Master must clarify the resource boundary of the existing abort policy. QA does not authorize ignoring/resetting global abort or selecting a different isolation policy.
5. Registration-spent, consumed, aborted and ordinary cleanup/closed are different histories. Spent is explicit; null payload alone conflates successful transfer, ordinary cleanup and failure. Retained mode/spent protection is credited without inventing a new canonical lifecycle schema or asserting complete state instrumentation.
6. Legacy successful absence-of-pair remains separable. A caught legacy Awake exception now marks global abort too; the old invalid-parent direct return after callback subscription does not take that catch and is not covered by the pair-only initialization guard. Thus whole legacy failure semantics are not unchanged or comprehensively rolled back.
7. Escaping AddComponent cleanup applies to exceptions that actually escape that call. Awake catches its own exceptions. Neither synchronous Awake invocation nor propagation of every Awake failure is established.

`SOURCE_BRANCH_LIFECYCLE_REVIEW.json` retains 20 source cases, byte/line witnesses, state distinctions and limitations. `CLAIM_EVIDENCE_MATRIX.json` independently assesses 20 claims. These labels do not count as runtime tests.

Fresh Unity reference binding uses the frozen R5 CoreModule SHA `C5C58EA254834291780A1D6C388C241443D07167B4A4B890A23C9494F626DDBA`, 1386688 bytes, MVID `e422ced3-d0f6-4bb2-9423-e8338d57bc04`. Actual op==/op!=/implicit IL reaches CompareBaseObjects; managed-null ceq branches reach GetCachedPtr/IntPtr comparisons, and the both-non-null branch ends in ceq in this exact reference. AddComponent native entries have RVA0/InternalCall metadata. `UNITY_REFERENCE_CUSTODY_IL.json` binds actual bytes; no Unity load, destroyed-pointer probe, installed-module identity or lifecycle/event timing is inferred.

## E1 provenance and coverage

The new owned root `scratch/EngineGate05R31Lifecycle-b8d47a10` and both raw R31/revision/dispatch/envelope34 identities are genuine improvements. Producer host reports PID18656/9624 and exit0 with six Pair and four Capture labels. QA did not rerun them. They inspect selected fields/sentinels and API/fixture metadata, not the entire typed/value/order/raw graph at BEFORE/AFTER_CALLER/AFTER_RETURNED phases. `FULL_TYPED_RAW_COPY_BINDING.json` does not supply that missing executed graph, loaded selected SHA/MVID/CLR/corelib, compiler full streams/argv/PID or recursive sealed pre/post inventory. R29 unit PASS and R30 static review are not R31 evidence.

All five BUILD_INPUT_MANIFEST dependency hashes **and sizes** differ from actual immutable files. Actual sizes: Assembly-CSharp15777280, CoreModule1386688, UnityEngine125120, Harmony2456064, Newtonsoft711952. `PROVENANCE_REVIEW.json` preserves every exact declared/actual SHA and size. These are genuine producer discrepancies, not expected values repaired by QA.

Newtonsoft's declared original reference `WarEconomyMod/1.6/Assemblies/Newtonsoft.Json.dll` has no entry in the 15854-path initial QA baseline. The unique current frozen Harness copy is SHA `E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D` /711952. Current original read-only observation matches that copy, but this is not prospective original compile-reference coverage. Final checking compares the additive observation without rewriting the baseline or treating the frozen copy as before-build proof.

Both 1973-byte stdout files differ from declared hashes. Actual en-US SHA `67DBD6CC0109086CC27B1C25C90A7968B9938DF106D9405BE961E515C7D8AB17`; actual de-DE SHA `690CC19135D9A63FEB4806343C8F230EA2211F68FF9E18B9838114BF9256608F`. Each contains 20 CRCRLF sequences. A read-only in-memory CRCRLF→CRLF comparison **still does not match either declared SHA**. Host text decoding/writing explains a possible translation mechanism, not the hash discrepancy itself. Missing first binary pipe streams cannot be replaced by normalized/reconstructed bytes. No original was rewritten.

BUILD_INPUT generated_at20:55 follows its own raw report timestamps around20:48:31 by 388.945009/388.861384 seconds. This is producer-internal declared chronology, not independently observed creation time or UTC world ordering. Current selected/runner PRE_RUN declarations match bytes but do not prove before-run existence, complete reference/tool/oracle/callplan binding or actual runtime verification. Six copied fixture descriptors/provenance records retain historical R29 paths/time/publisher labels; literal normal inputs may be reused, but they do not prove a new publication. No publisher was executed/adopted.

## Own helper failure, preservation and delivery

The first provenance helper stopped with numeric exit1 because it assumed every declared dependency path belonged to the baseline. Original full stdout/stderr/tool proof and helper remain unchanged; this failure is not counted as PASS. The WP permits passive locator/schema correction: a new `review_r1.py` locates the unique frozen Newtonsoft entry and records the uncovered original path separately. Exact corrective diff/input pins and first corrected invocation exit0/full streams are retained. All five genuine dependency mismatches, two stdout mismatches and seven map mismatches remain findings. Core bootstrap/metadata/provenance/lifecycle helpers have first streams and actual numeric exits. Post-compaction recovery console was bounded; a fresh passive recovery read captures the full required-document streams separately, without candidate or analysis reruns.

Final `PRESERVATION_BEFORE_AFTER.json` binds independent before/after inventories of all 15854 protected unique paths and 131 frozen files; old R30 frozen128 are also rehashed. `EVIDENCE_MANIFEST.json`, `RESULT_INDEX.json` and last-atomic `COMPLETION.json` bind actual report/artifact SHA and sizes. Cycle files and the not-yet-finished seal logger are explicitly excluded; final seal logger and actual direct-message tool return are preserved separately. A tool-confirmed submission is not Master acceptance.

`NEXT_MINIMAL_REPAIR.md` retains the valid R31 gains and recommends managed ReferenceEquals custody before optional liveness checks, mode-before-getter ordering, own isRunning=false and isolated failure cleanup, explicit abort/resource policy, and truthful binary/prospective/full-graph packaging. It creates no new WP, canonical policy or closure. Fresh normal/native verification requires a new exact frozen admission and separate authorized QA scope.

All candidate/build/load/compiler/runner/bootstrap/receipt/Set/acquire/Awake/Update/OnDestroy/reflection/Unity/game/native/operator/Process/provider/cache/publisher/currenttask/rejection/adverse executions are **0**. Engine002006/Pipeline007/currentSchema/G-Q1/exactPlayerGlobal/physicalsplit and existing Highs remain OPEN; full/native E2 NOT_RELEASED; Foundation HOLD; Master disposition PENDING. Dedicated Server remains final Domain Authority and C corrections remain controlling.
