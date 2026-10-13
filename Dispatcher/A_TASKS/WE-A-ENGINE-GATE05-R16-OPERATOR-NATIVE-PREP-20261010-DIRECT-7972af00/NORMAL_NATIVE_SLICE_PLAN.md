# NORMAL_NATIVE_SLICE_PLAN

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R16-OPERATOR-NATIVE-PREP-20261010-DIRECT-7972af00`
- **Work Package**: `WP_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION`
- **Revision**: `GATE05-R16-OPERATOR-NATIVE-PREPARATION` (Envelope 19)
- **Status**: Prospective Implementation & Evidence Plan (Apply NONE in R16; All 9 Current Engine Paths Fixed)
- **Target Slice Objective**: One Operator-Owned Normal Worker `STEP` -> `SEAL` -> `STAGE` -> Fresh Validator Exact Staged SHA -> Independently Loaded Def/Census -> Protected Channel -> Internal Receipt Materialization

---

## 1. Slice Boundary & Architectural Scope

This plan specifies the minimum prospective implementation and ordered evidence requirements for executing a single normal native validation cycle under Gate05. 

### Explicit Boundary Exclusions:
1. **Zero Production Code Modifications in R16**: All 9 Engine source and binary files remain fixed to their baseline hashes.
2. **Promotion & Atomic Replacement Deferred (MD131)**: The execution of `PROMOTE_STAGED` and atomic replacement of existing final saves via same-volume atomic primitives is **strictly excluded** from this slice. This slice terminates upon successful materialization of `StageValidationReceipt` and transition of worker semantic state to `STAGED_VALIDATED`.
3. **No Dynamic Patch/User Settings Evaluation**: Mod patch AST execution and user mod settings evaluation remain qualified under existing ADR-006B-v5 boundaries.
4. **No Full Job Driver Graphs**: Job and reservation semantics remain bounded to V4 `ActiveJobRecord` and `ReservationRecord` per MD132.

---

## 2. Ordered Prerequisites Before Execution

Before any native executable run can be launched, the following prerequisites must be strictly satisfied and verified:

```
[Prereq 1: Candidate Admission]
  └── Master reviews and admits selected candidate binary (e.g. R15 Debug 835E8121... / MVID 4fb1a25f-72c8-426d-b93f-d6cba4f9af72)
[Prereq 2: Isolated Runtime Environment Staging]
  └── Master authorizes complete licensed runtime staging into scratch\EngineGate05NativeSlice\RuntimeCopy\
  └── Staged runtime includes RimWorldWin64_Data, Mono runtime, Managed assemblies, Data\Core, About.xml, ModsConfig.xml
[Prereq 3: Pre-Run Cryptographic Binding]
  └── Immutable snapshot recorded: CANDIDATE_PRE_RUN_MANIFEST.json and ENGINE_FREEZE_BEFORE.json
[Prereq 4: Initial Baseline Save Materialization]
  └── Verified baseline save SETTLEMENT-B.rws placed in isolated UserData\Saves\
```

---

## 3. End-to-End Execution Sequence & State Machine

```mermaid
sequenceDiagram
    autonumber
    participant Op as Operator Control Plane
    participant W as Worker (Simulation Host)
    participant FS as Isolated Filesystem
    participant V as Fresh Validator Process

    Note over Op,W: 1. Control Plane Setup
    Op->>W: REGISTER_AUTHORITY (AuthorityBundle, Mode=SIMULATION)
    Op->>W: REGISTER_GRANT (SimulationGrant, Mode=SIMULATION)
    Op->>W: LOAD_SAVE (SETTLEMENT-B) & VALIDATE_INPUT
    
    Note over W: 2. Proposal Stepping & Sealing
    Op->>W: STEP_TICKS 10
    Op->>W: SEAL_RESULT
    W->>W: Live Census & ComputeManifestHash
    W->>W: Generate immutable SealedResultId & ResultManifest
    
    Note over W,FS: 3. Staging & Task Generation
    Op->>W: STAGE_SAVE
    W->>FS: Write staged save (SETTLEMENT-B_Staged_*.rws)
    W->>W: Compute disk stagedSha & ValidateStagedXml
    W->>W: Generate 32-byte capabilityNonce & channelSecretToken
    W->>FS: Write ValidatorTask JSON ({taskId}.task.json)
    W->>W: State = STAGED_PENDING_VALIDATION
    
    Note over Op,V: 4. Operator Process Launch & Binding
    Op->>W: LAUNCH_OPERATOR_VALIDATOR (nonce, admittedExe, args)
    W->>W: Verify nonce & AdmittedOperatorValidatorExecutable
    W->>V: Process.Start (Fresh Child Process, PID != Simulator PID)
    W->>W: Capture Child PID & StartTime UTC; Bind process
    
    Note over V,FS: 5. Independent Validator Execution
    V->>FS: Load staged save into isolated engine
    V->>V: EXECUTE_VALIDATOR_TASK (taskFilePath, nonce)
    V->>FS: Re-verify staged save disk SHA == task.stagedSha
    V->>V: Verify loaded ContentProfileFingerprint == task.profileFingerprint
    V->>V: Live Census from loaded map & liveHash == task.sealedManifestHash
    V->>FS: Write ValidatorResult to protected channel file ({taskId}.protected_result.json)
    V-->>Op: Process Exits (ExitCode == 0)
    
    Note over Op,W: 6. Channel Consumption & Receipt Internalization
    Op->>W: COMPLETE_STAGE_VALIDATION (No caller payload!)
    W->>FS: Read {taskId}.protected_result.json
    W->>W: Verify Channel Secret Token & Capability Nonce
    W->>W: Verify Child PID == registeredPid & StartTime UTC == registeredStartTime
    W->>W: Verify 16 MD128 Closed-Context Dimensions
    W->>FS: Atomic Move: {taskId}.protected_result.json -> .consumed
    W->>W: Materialize StageValidationReceipt (Internal Receipt)
    W->>W: State = STAGED_VALIDATED
    W-->>Op: STAGE_VALIDATION_ACCEPTED (ReceiptId, ValidatorPid, TaskId)
```

---

## 4. Verification & Evidence Collection Protocol

For the slice to be considered complete, the following physical evidence must be collected and packaged:

1. **Process Evidence (`PROCESS_EVIDENCE_INVENTORY.json`)**:
   - Simulator Process: PID, StartTime UTC, WorkingDirectory, CommandLine arguments.
   - Validator Process: PID, StartTime UTC, ExitTime UTC, ExitCode (`0`), WorkingDirectory, CommandLine arguments.
   - Verification that `SimulatorPid != ValidatorPid`.
2. **Channel Evidence (`PROTECTED_CHANNEL_EVIDENCE.json`)**:
   - Exact path of `.task.json`, byte size, and SHA256.
   - Exact path of `.protected_result.json.consumed`, byte size, and SHA256.
   - Proof of atomic consumption (absence of unconsumed file, presence of `.consumed` file).
3. **Artifact Integrity Proof (`STAGED_ARTIFACT_DIGEST.json`)**:
   - Exact staged file path and disk SHA256.
   - Worker pre-staging hash vs Validator independent disk hash (must match bit-for-bit).
4. **Census Oracle Proof (`CENSUS_ORACLE_EVIDENCE.json`)**:
   - Worker sealed census manifest JSON, byte size, and SHA256.
   - Validator live census manifest JSON, byte size, and SHA256.
   - Equality comparison of both manifest hashes against `task.sealedManifestHash`.
5. **Receipt Binding (`STAGE_VALIDATION_RECEIPT.json`)**:
   - Complete serialized `StageValidationReceipt` containing all 16 bound dimensions.

---

## 5. Rejection-to-Hold Conditions

The execution must immediately fail-closed and transition to `HOLD` upon any of the following conditions:

| Condition | Failure Trigger | Action Taken |
|---|---|---|
| **Staged SHA Divergence** | Disk SHA != `task.stagedSha` | Validator returns `VALIDATION_FAILED`; operator revokes readiness; task marked failed |
| **Manifest Divergence** | Validator live hash != `task.sealedManifestHash` | Validator returns `VALIDATION_FAILED`; no receipt generated |
| **Caller Payload Injection** | Caller passes JSON to `COMPLETE_STAGE_VALIDATION` | Rejected with `RevokeReadiness("Caller-supplied validation result payload prohibited")` |
| **Unadmitted Executable** | Caller attempts to launch unadmitted validator binary | Rejected with `RevokeReadiness("Caller cannot nominate arbitrary validator executable")` |
| **Channel Forgery** | Channel secret token or capability nonce mismatch | Rejected with `RevokeReadiness("Forged or unauthorized result origin")` |
| **Process Impersonation** | PID or StartTime UTC mismatch on child result | Rejected with `RevokeReadiness("Unregistered validator PID / StartTime mismatch")` |
| **Target Map Clamping** | `task.targetMapIndex < 0` or out of bounds | Rejected fail-closed; target clamping strictly prohibited |
| **Child Timeout / Crash** | Validator child fails to exit within budget or non-zero exit | Child terminated; operator state reset; readiness revoked |

---

## 6. Prospective Write-Set Declaration

To support this slice when admitted, the prospective write-set is declared in [NEXT_IMPLEMENTATION_WRITESET.json](file:///C:/Users/user/Desktop/RimMulti/Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R16-OPERATOR-NATIVE-PREP-20261010-DIRECT-7972af00/NEXT_IMPLEMENTATION_WRITESET.json). 

**Zero modifications are applied during R16**. All 9 Engine source and binary paths remain 100% immutable and identical to baseline.
