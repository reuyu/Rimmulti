"""Read-only independent source branch/custody and frozen evidence analysis."""
from qa_common import *
import sys,traceback
FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R30-HANDOFF-20261012-DIRECT-16ce928f'
WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
OLDMAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R29-STARTUP-PAIR-20261012-DIRECT-46f60e2a/MASTER_GATE05_R29_STARTUP_PAIR_REVIEW_FREEZE_MANIFEST.json'
def source_witness(start,end,label):
    b=WORKER.read_bytes();x=b.index(start.encode('utf-8'));y=b.index(end.encode('utf-8'),x+len(start));v=b[x:y]
    return dict(id=label,file=row(WORKER),byte_range=[x,y],line_range=[b[:x].count(b'\n')+1,b[:y].count(b'\n')+1],sha256=hashlib.sha256(v).hexdigest().upper(),raw_utf8=v.decode('utf-8'))
def branch_review():
    assert load(Q/'review_static_r1_source.TOOL.json')['exit_code']==load(Q/'review_static_r1_references.TOOL.json')['exit_code']==0
    s=WORKER.read_text(encoding='utf-8-sig');assert s.count('_isPairRequiredMode = true;')==1 and s.count('_isPairRequiredMode = false;')==1
    ws=[source_witness('internal static bool TryInstallOperatorStartupConfig(', 'private OperatorStartupPairSnapshot?', 'PARENT_SEAL_FIXED'),source_witness('private OperatorStartupPairSnapshot?', 'private TcpListener?', 'ALL_PENDING_MODE_OWNER_COHORT_STATE'),source_witness('void Awake()', 'private void HandleUnityLogMessage(', 'AWAKE_ALL_EARLY_GATES_SIDEEFFECTS_AND_LOCAL_CATCH'),source_witness('void OnDestroy()', 'public static class OperatorRolePathSelector','DESTROY_CLEANUP_AND_FOLLOWING_STOP'),source_witness('void Update()', 'private void ListenLoop(', 'UPDATE_AFTER_AWAKE_RETURN_SOURCE_ONLY')]
    for w in ws:assert w['raw_utf8'] and w['byte_range'][1]>w['byte_range'][0]
    cases=[
      dict(id='B01_SET_VALID_BEFORE_ADD',precondition='Fresh live owner; exact installed receipt/parent/snapshot; all pending slots empty',source_result='Set returns true, writes owner/receipt/pair; bootstrap checks bool before AddComponent. Pending encodes pair context before attachment, but no durable independent required-mode/consumed-owner record.',mode='Instance field default false until acquire owner match',status='PARTIAL_SOURCE_CREDIT'),
      dict(id='B02_SET_INVALID_OR_EXISTING_SLOT',precondition='Unity-null owner, missing receipt/pair, nonempty pending triple, or any cohort mismatch',source_result='Set returns false before pending mutation; bool branch destroys fresh go and returns without AddComponent.',mode='No component instance attached in this bootstrap branch',status='SOURCE_GUARD_SUPPORTED'),
      dict(id='B03_ACQUIRE_MATCH_VALID',precondition='Pending owner Unity-non-null and ReferenceEquals(this.gameObject); exact receipt+snapshot cohort',source_result='Mode true, acquired pair returned; three pending fields cleared inside lock; Awake assigns private profile. Payload transferred per registration.',mode='true retained in this instance',status='SOURCE_GUARD_SUPPORTED'),
      dict(id='B04_ACQUIRE_MATCH_BAD_COHORT',precondition='Matched live owner but missing/mismatched receipt, pair or active config',source_result='Mode true before cohort checks; pending triple cleared; false/null return; Awake required-mode/profile-null returns before fastEcology/callback/policy/listener.',mode='true retained, profile null',status='SOURCE_GUARD_SUPPORTED'),
      dict(id='B05_INITIAL_PENDING_ABSENT',precondition='Fresh instance; pending absent or cleaned before acquire; installed pair parent receipt still valid',source_result='False/null acquire with mode false; required-mode early gate false. fastEcology and callback reached; valid parent receipt allows later policy/listener code.',mode='false; no durable pair-required lookup',status='REQUIRED_MODE_GAP_SOURCE_ONLY'),
      dict(id='B06_OTHER_OWNER',precondition='Live pending A; fresh component B, ReferenceEquals(owner,B.gameObject) false; active parent receipt valid',source_result='Pending A untouched; acquire false/null and B mode false; B can fall through source gates to legacy-style policy/listener body using globally installed parent receipt.',mode='false',status='REQUIRED_MODE_GAP_SOURCE_ONLY'),
      dict(id='B07_SECOND_SAME_INSTANCE_CALL',precondition='Same already-acquired instance invokes acquire again after slots consumed',source_result='False/null return, but existing true mode/profile not cleared by acquire. One payload retrieval per registration; no extra execution performed.',mode='previous true retained',status='PER_SLOT_ONE_USE_SOURCE_SUPPORTED'),
      dict(id='B08_FRESH_COMPONENT_AFTER_CONSUMPTION',precondition='Fresh component on same/other owner after previous successful consumption',source_result='Pending absent; new instance has mode false, although installed pair receipt remains. No consumed owner/cohort bookkeeping read.',mode='false',status='REQUIRED_MODE_AND_LIFETIME_GAP_SOURCE_ONLY'),
      dict(id='B09_SAME_COHORT_REREGISTRATION',precondition='Explicit repeat internal Set call after successful consumption with same live owner/receipt/pair; no new native/runtime call made',source_result='All three slots empty and same cohort checks pass again. No consumed-owner/cohort predicate rejects this repeat registration. Current bootstrap has one visible Set callsite; no actual repeat/native exploit observed.',mode='No lifetime one-use state in Set',status='LIFETIME_ONE_USE_NOT_ESTABLISHED'),
      dict(id='B10_PROFILE_CLEAR_AFTER_TRUE_MODE',precondition='Instance previously marked required; profile cleared by cleanup/destroy',source_result='OnDestroy does not reset mode. M05 OR guard still true and returns R30 M05_NOT_ADMITTED.',mode='true',status='SOURCE_GUARD_SUPPORTED'),
      dict(id='B11_ALIVE_MATCHING_OWNER_CLEANUP',precondition='owner compares Unity-non-null and ReferenceEquals current pending owner',source_result='Clears only matching pending triple; unrelated live owner cannot clear it. Cohort is implicit from Set identity; cleanup itself accepts owner only.',mode='Instance mode not touched',status='SOURCE_GUARD_SUPPORTED_WITH_LIFETIME_LIMIT'),
      dict(id='B12_UNRELATED_OWNER_CLEANUP',precondition='Unrelated alive owner or ordinary managed null',source_result='Unrelated reference fails clear predicate; managed null returns before lock. Existing unrelated pending remains.',mode='unchanged',status='SOURCE_GUARD_SUPPORTED'),
      dict(id='B13_UNITY_NULL_MANAGED_NON_NULL_OWNER',precondition='Conditional frozen-reference state: managed owner wrapper non-null but cached native pointer zero',source_result='Unity owner==null may select early cleanup return before ReferenceEquals. Pending!=null may prevent acquire and leave fresh mode false; non-null receipt/pair still reject overwrite. Exact native destruction/getter timing unobserved.',mode='fresh false on no-match path',status='LIFETIME_CUSTODY_GAP_REFERENCE_IL_ONLY'),
      dict(id='B14_BOOTSTRAP_ADD_EXCEPTION',precondition='Exception escaping actual AddComponent call',source_result='Bootstrap catch invokes owner cleanup, Destroy(go), return. Awake has its own catch and no rethrow, so guarantee that every Awake exception reaches bootstrap catch is false; native synchronous Awake timing remains unobserved.',mode='No additional guarantee',status='PARTIAL_CATCH_CREDIT'),
      dict(id='B15_AWAKE_RETURN_IS_NOT_LIFECYCLE_STOP',precondition='Matched-owner cohort failure causes required early return',source_result='Awake return does not disable/destroy component or gate unchanged Update. Update suppression/readiness code and initializer isRunning=true remain. Actual later native scheduling/side effects not observed.',mode='true but Update has no pair failure gate',status='SOURCE_LIMITATION_NO_NATIVE_CLAIM'),
      dict(id='B16_DESTROY_GETTER_OR_CLEANUP_EXCEPTION',precondition='Hypothetical failure while evaluating this.gameObject or cleanup in OnDestroy',source_result='Profile clears first; cleanup precedes isRunning=false and unsubscribe/listener try blocks. No whole-method catch protects these early operations. Actual getter failure/lifetime not observed.',mode='not reset by source',status='SOURCE_LIMITATION_NO_NATIVE_CLAIM')]
    reference=load(Q/'UNITY_REFERENCE_NULL_AND_ADDCOMPONENT_IL.json')
    methods={m['name']:m for m in reference['methods']}
    assert [i['target']['name'] for i in methods['op_Equality']['instructions'] if 'target' in i]==['CompareBaseObjects']
    assert '0203fe01' in methods['CompareBaseObjects']['IL_hex']
    interpretation=dict(reference=row(Path(reference['input']['path'])),reference_mvid=reference['reference_mvid'],equality='op==/op!= delegate CompareBaseObjects. Managed-null comparisons use ceq; one-null branch calls IsNativeObjectAlive; both non-null branch uses ceq in this exact frozen reference.',alive='IsNativeObjectAlive calls GetCachedPtr and System.IntPtr.op_Inequality; GetCachedPtr reads cached field. Native lifetime of actual GameObject not observed.',AddComponent='Managed wrappers delegate to RVA0 InternalCall methods; no IL establishes immediate Awake or bootstrap catch propagation.',reference_assumption='Reference metadata is static evidence, not proof of actual installed/loaded native Unity module or callback timing')
    write(Q/'SOURCE_BRANCH_CUSTODY_REVIEW.json',dict(at=now(),verdict='REQUIRED_MODE_AND_LIFETIME_CUSTODY_REVISION_REQUIRED_NATIVE_UNTESTED',source=row(WORKER),whole_changed_span_witness=row(Q/'SOURCE_BYTE_MAP_AND_FULL_CHANGED_SPANS.json'),witnesses=ws,source_only_cases=cases,case_count=len(cases),Unity_reference=interpretation,required_mode_before_acquire='Not established as durable independent instance/owner state; pending pair context does exist before AddComponent, so blanket no-context wording would be inaccurate.',sideeffects='Matched-owner failure gate precedes four named Awake sideeffects; absence/wrong-owner/fresh-postconsume modefalse paths do not select it.',one_use='Lock+clear supports one retrieval per current registration; lifetime same-cohort rereuse not prevented.',sourceHigh1='OPEN',carrier_publisher='UNCHANGED_OPEN',candidate_native_adverse_calls=0,abstract_branch_review_not_executed_tests=True))
    print(json.dumps(dict(source_cases=len(cases),required_mode_gap=True,lifetime_one_use_not_established=True,Unity_cached_pointer_null_boundary=True,unconditional_Awake_catch_claim_falsified=True,native='UNTESTED',candidate_calls=0)))
def provenance_review():
    assert load(Q/'review_static_r1_source.TOOL.json')['exit_code']==0
    manifest=load(MAN);mapping={r['original_path'].lower():r for r in manifest['files']}
    oldrows=load(OLDMAN)['files'];old_verified=verify(oldrows,'frozen_path')
    assert len(old_verified)==132
    baseline={r['path'].lower():r for r in load(BASELINE)['files']};drift=[];unchanged=[];missing=[]
    prefix=str(ROOT/'scratch/EngineGate05R29StartupPair').lower()+'\\'
    for r in oldrows:
        if not r['original_path'].lower().startswith(prefix):continue
        p=Path(r['original_path'])
        if not p.is_file():missing.append(r['original_path']);continue
        v=row(p)
        if p.as_posix().lower().replace('/','\\') in baseline:pass
        if str(p).lower() in baseline:
            assert v['sha256']==baseline[str(p).lower()]['sha256'] and v['bytes']==baseline[str(p).lower()]['bytes']
        entry=dict(old_frozen_reference=row(Path(r['frozen_path'])),old_declared_sha=r['sha256'],current_original=v,original_path=r['original_path'],frozen_preserved=True)
        (drift if v['sha256']!=r['sha256'] or v['bytes']!=r['bytes'] else unchanged).append(entry)
    master_drift=load(PKG/'coordination/MASTER_R30_ORIGINAL_R29_E1_LINEAGE_DRIFT_20261012.json')
    master_set={r['current_original']['path'].lower() for r in master_drift['files']}
    independent_set={r['current_original']['path'].lower() for r in drift}
    pre=load(FT/'FINAL_PRE_RUN_MANIFEST.json');stale=[]
    for r in pre['built_candidates']:
        frozen=mapping.get(r['path'].lower())
        if frozen:
            actual=row(Path(frozen['frozen_path']));stale.append(dict(original_declared=r,actual_R30_frozen=actual,sha_matches=r['sha256']==actual['sha256'],size_matches=r['bytes']==actual['bytes']))
        else:stale.append(dict(original_declared=r,actual_R30_frozen='NOT_IN_FROZEN_MANIFEST',sha_matches=False))
    host=load(FROZEN/'scratch/EngineGate05R29StartupPair/HOST_TELEMETRY.json');runs=[]
    declared_pre=datetime.datetime.fromisoformat(pre['generated_at'])
    for r in host['runs']:
        reportrow=mapping[r['execution_report_path'].lower()];report=load(Path(reportrow['frozen_path']))
        t=datetime.datetime.fromisoformat(report['timestamp_utc'].replace('Z','+00:00'))
        pins=[]
        for pathkey,hashkey in [('stdout_path','stdout_sha256'),('stderr_path','stderr_sha256'),('execution_report_path','execution_report_sha256')]:
            fr=mapping[r[pathkey].lower()];p=Path(fr['frozen_path']);pins.append(dict(file=row(p),host_declared_sha=r[hashkey],matched=sha(p)==r[hashkey]))
        assert all(v['matched'] for v in pins)
        runs.append(dict(culture=r['culture'],owned_PID_claim=r['pid'],numeric_exit_claim=r['exit_code'],producer_raw_bindings=pins,actual_report_identity={k:report[k] for k in ['wp_id','wp_revision','dispatch_id','envelope']},timestamp_original=report['timestamp_utc'],prepin_generated_at=pre['generated_at'],declared_prepin_after_report_seconds=(declared_pre-t).total_seconds(),Pair_labels=len(report['pair_cases']),Capture_labels=len(report['r27_regression_cases']),status=report['status'],claim_scope='Producer-owned host/raw observations only; no fresh independent runtime verification'))
    program=FROZEN/'scratch/EngineGate05R29StartupPair/Harness/Program.cs';program_old=ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/EngineGate05R29StartupPair/Harness/Program.cs'
    text=program.read_text(encoding='utf-8-sig')
    ack=load(FT/'ACK.json');scope_actual=row(FT/'MASTER_R30_AUTHORIZED_SOURCE_SCOPE.json')
    inventories=[r['original_path'] for r in manifest['files'] if any(k in Path(r['original_path']).name.upper() for k in ['LOADED_MANAGED','TYPED_CHECK','RAW_FILE','GETTER_LEDGER','OUTPUT_INVENTORY','COMPILER'])]
    report=dict(at=now(),verdict='ORIGINAL_E1_LINEAGE_AND_PROSPECTIVE_PROVENANCE_REVISION_REQUIRED',old_manifest=row(OLDMAN),old_frozen132_verified=old_verified,original_E1_scope_current_changed=drift,unchanged_count=len(unchanged),missing_current_originals=missing,independent_drift_count=len(drift),master_drift_source=row(PKG/'coordination/MASTER_R30_ORIGINAL_R29_E1_LINEAGE_DRIFT_20261012.json'),master_drift_pathset_match=master_set==independent_set,FINAL_PRE_RUN_manifest=row(FT/'FINAL_PRE_RUN_MANIFEST.json'),declared_built_candidates_vs_actual_frozen=stale,stale_declared_built_count=sum(not r['sha_matches'] for r in stale),producer_run_raw=runs,host=row(FROZEN/'scratch/EngineGate05R29StartupPair/HOST_TELEMETRY.json'),runner_program=row(program),old_runner_program=row(program_old),program_bytes_identical=program.read_bytes()==program_old.read_bytes(),runner_source_R29_envelope32=('executionReport["envelope"] = 32;' in text),fresh_R30_runner_owned_output_boundary='NOT_IMPLEMENTED: reused old R29 root and rebuilt runner/overwritten original outputs',ack_scope_declared=ack['scope_sha256'],scope_actual=scope_actual,ack_scope_matches=ack['scope_sha256']==scope_actual['sha256'],available_metadata_like_inventory_names=inventories,limitations=['Producer10 normal labels support recorded selected field/sentinel tests, not fulltyped/raw/copy independence, handoff branches/native or E2.','Actual loadedmanaged path/SHA/MVID/corelib/CLR and prospective compiler/exact references/full oracle pins not found in producer evidence graph.','Declared generated_at ordering is producer metadata; no UTC world ordering or independently observed file-creation timeline inferred.','7 stale built candidate declarations additionally contradict exact selected R30 and current runner lineage.','Original E1 drift is a reported preservation violation, not silently repaired; frozen old QA PASS stays exact historic candidate only.'],candidate_compiler_runner_game_native_global_adverse_execution=0,Foundation='HOLD',Highclosure=0)
    write(Q/'PROVENANCE_AND_ORIGINAL_DRIFT_REVIEW.json',report)
    print(json.dumps(dict(old_frozen132_intact=True,original_E1_drift=len(drift),master_drift_pathset_match=master_set==independent_set,stale_predeclared_candidates=sum(not r['sha_matches'] for r in stale),built_declarations=len(stale),runs=runs,runner_source_same_as_old=report['program_bytes_identical'],ack_scope_matches=report['ack_scope_matches'],candidate_calls=0)))
if __name__=='__main__':
    mode=sys.argv[1];assert mode in ['branches','provenance']
    out=Q/f'EVIDENCE_REVIEW_{mode}_STDOUT.txt';err=Q/f'EVIDENCE_REVIEW_{mode}_STDERR.txt';proof=Q/f'EVIDENCE_REVIEW_{mode}_TOOL.json'
    assert not out.exists() and not err.exists() and not proof.exists()
    code=0;so0,se0=sys.stdout,sys.stderr;started=now()
    with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
        sys.stdout,sys.stderr=so,se
        try:
            verify(load(MAN)['files'],'frozen_path')
            if mode=='branches':branch_review()
            else:provenance_review()
        except BaseException:code=1;traceback.print_exc()
        finally:sys.stdout,sys.stderr=so0,se0
    write(proof,dict(at=now(),started_at=started,script=row(Path(__file__)),mode=mode,exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True,candidate_execution=0));print(json.dumps(dict(mode=mode,exit_code=code,stdout=row(out),stderr=row(err))));sys.exit(code)
