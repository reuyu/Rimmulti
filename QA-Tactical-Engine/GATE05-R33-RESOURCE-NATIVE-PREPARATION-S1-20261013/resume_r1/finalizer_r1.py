from pathlib import Path
import json,hashlib,datetime,sys,traceback,os,difflib
R=Path(__file__).resolve().parent;Q=R.parent;ROOT=Q.parent.parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
BASELINE=PKG/'coordination/MASTER_R33_RESOURCE_COMMIT_PROTECTED_BASELINE_20261013.json'
EXTRA=PKG/'coordination/MASTER_R32_OUTSIDE_OWNED_HELPER_DISCOVERY_20261013.json'
PARTIAL=PKG/'coordination/MASTER_R33_SOL_PREP_PARTIAL_PRESERVATION_20261013.json'
AUTH=PKG/'MASTER_R33_PREPARATION_METADATA_FINALIZATION_RESUME_R1_20261013.md'
SCOPE=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5/MASTER_R33_AUTHORIZED_SOURCE_SCOPE.json'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R32-CUSTODY-20261012-DIRECT-64ad38e2/MASTER_GATE05_R32_CUSTODY_REVIEW_FREEZE_MANIFEST.json'
RESUME='SOL-GATE05-R33-RESOURCE-NATIVE-PREP-S1-RESUME-R1-20261013-01'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R33_Resource_Native_Preparation_S1_20261013.md'
VERDICT='PREPARATION_COMPLETE_NATIVE_NOT_READY_NOT_ADMITTED_R33_NOT_REVIEWED'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_bytes().decode('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert not p.exists(),str(p);p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows,key='path'):
    out=[]
    for r in rows:
        p=Path(r[key]);v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p);out.append(v)
    return out
def preserve():
    assert sha(BASELINE)=='DAE9DE6DE5AA170BF62476412EE5C0F4078357DE074164BEDC66F9894DBC4D1E'
    assert sha(EXTRA)=='74C4785667B26AFEC041298DFC5E21178AF645C495B6A343E4CC6E56FAF6EF2F'
    assert sha(MAN)=='F5EDD5DCBC021407B3598DEBCF80276F39C158EC38FABD37D10AD15E6098E6BF'
    scope=load(SCOPE);deny={p.lower() for p in scope['allowed_mutable_paths']+scope['allowed_generated_intermediate_paths']};assert len(deny)==22
    rows=load(BASELINE)['files'];ex=load(EXTRA)['files'];frozen=load(MAN)['files'];partial=load(PARTIAL)['files']
    assert len(rows)==16929 and len(ex)==5 and len(frozen)==64
    assert not any(r['path'].lower() in deny for r in rows+ex+partial)
    return dict(at=now(),protected_files=check(rows),additional_helper_files=check(ex),frozen_files=check(frozen,'frozen_path'),partial_files=check(partial),protected_count=16929,additional_count=5,frozen_count=64,partial_count=len(partial),mutable22_not_read_hashed=True,all_matched=True)
def ids():
    ack=load(Q/'ACK_INITIAL.json');assert ack['result_id']=='SOL-GATE05-R33-RESOURCE-NATIVE-PREP-S1-20261013-9c4a33b402fc4af68d5ac55a9c97009c'
    assert sha(Q/'ACK_INITIAL.json')=='2662A780B57BF625F77A64B22724E068215A9EF1153CBF9432A9BFB37F3446C8' and (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
    return ack
def resume():
    ack=ids();assert not (Q/'COMPLETION.json').exists()
    text=AUTH.read_bytes().decode('utf-8-sig');assert RESUME in text;print(str(AUTH)+'\n'+text)
    before=preserve();write(R/'RESUME_PRESERVATION_BEFORE.json',before)
    docs=[Path(r['path']) for r in load(Q/'RECOVERY_AND_PREPARATION_INPUT_AUDIT.json')['files']];audit=[]
    for p in docs:
        text=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text);audit.append(dict(**row(p),full_read=True))
    write(R/'RESUME_RECOVERY_AND_PLAN_READ_AUDIT.json',dict(at=now(),files=audit,full_read=True,old_helpers_not_executed=True,mutable_R33_reads_hashes=0))
    plans=[]
    for p in sorted(Q.glob('*.json')):
        text=p.read_bytes().decode('utf-8-sig');json.loads(text);print(str(p)+'\n'+text);plans.append(dict(**row(p),full_read=True))
    write(R/'OLD_PREPARATION_FULL_READ_AUDIT.json',dict(at=now(),files=plans,all_original_bytes_preserved=True))
    old=(Q/'common.py').read_bytes().decode('utf-8');new=Path(__file__).read_bytes().decode('utf-8');diff=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(Q/'common.py'),tofile=str(Path(__file__))))
    (R/'NEW_METADATA_PLUMBING_EXACT_DIFF.txt').write_bytes(diff.encode('utf-8'))
    write(R/'NEW_METADATA_TOOL_PROVENANCE.json',dict(at=now(),old_definition_TEXT_only=row(Q/'common.py'),old_full_text=old,new_additive_finalizer=row(Path(__file__)),exhaustive_diff=row(R/'NEW_METADATA_PLUMBING_EXACT_DIFF.txt'),old_top_level_import_execute=False,scope='New metadata-only hashing/JSON/read/final seal plumbing; no candidate/CLR/compiler/native calls.'))
    write(Q/'RESUME_ACK.json',dict(at=now(),resume_id=RESUME,delivery_id=ack['delivery_id'],wp_id=ack['wp_id'],wp_revision='S1',result_id=ack['result_id'],status='ACKNOWLEDGED_SAME_PREPARATION_METADATA_FINALIZATION_R1',authority=row(AUTH),partial_preservation_manifest=row(PARTIAL),partial_files_verified=len(before['partial_files']),initial_ACK=row(Q/'ACK_INITIAL.json'),initial_protected16929_additive5_frozen64_matched=True,all_execution=0,mutable_R33_reads_hashes=0,old_pending_ACK_not_rewritten=True,nativeE2='NOT_RELEASED',Foundation='HOLD'))
    print(json.dumps(dict(resume_id=RESUME,result_id=ack['result_id'],partial_count=len(before['partial_files']),protected=16929,additive=5,frozen=64,ACK=row(Q/'RESUME_ACK.json'),all_execution=0,mutable_R33_reads_hashes=0)))
def prepare():
    ack=ids();assert load(R/'resume.TOOL.json')['exit_code']==0 and load(Q/'prepare.TOOL.json')['exit_code']==0
    after=preserve();old=load(Q/'PRESERVATION_BEFORE.json');resumed=load(R/'RESUME_PRESERVATION_BEFORE.json')
    for key in ['protected_files','additional_helper_files','frozen_files']:assert old[key]==after[key]==resumed[key]
    assert resumed['partial_files']==after['partial_files']
    assert REPORT.exists()
    write(Q/'FINAL_PRESERVATION_R1.json',after)
    write(Q/'PRESERVATION_BEFORE_AFTER_R1.json',dict(at=now(),original_before=row(Q/'PRESERVATION_BEFORE.json'),resume_before=row(R/'RESUME_PRESERVATION_BEFORE.json'),after=row(Q/'FINAL_PRESERVATION_R1.json'),partial_manifest=row(PARTIAL),protected_count=16929,additive5=True,frozen64=True,partial_count=after['partial_count'],all_SHA_bytes_unchanged=True,mutable_R33_reads_hashes=0,all_execution=0))
    supplement=dict(at=now(),resume_id=RESUME,original_plans_not_modified=True,status='NOT_READY_NOT_EXECUTION_ADMITTED',qualifications=[
        'R33 completion observed by Master is not candidate admission. No R33 source/bin/obj/project1.6 read/hash/rebuild or candidate verdict.',
        'Historical R4 seven-file runtime/missing asset findings are historical, not freshly established current completeness or causal diagnosis; immutable rows only checked. A fresh isolated runtime inventory and Master disposition remain required.',
        'Precommit/commit/postcommit abort labels are source obligations. No forced abort, synthetic destroyed wrapper, failure injection, invalid receipt or race replay in the proposed normal plan.',
        'Normal positive lifecycle cannot prove every concurrency/getterfailure/postcommit abort teardown history; unobserved cases remain open and require separate exact admission, never a false normal PASS.',
        'Resource counts and plan rows are preparation coverage, not tests. R32 scoped unit PASS remains its exact old lineage only.',
        'Safe actual event/owner/lock/socket/thread/callback/native observation surface has not been supplied or admitted. This plan does not add production probes/functions or authorize private reflection.',
        'Historical 16 logical context dimensions must be rebound to the actual new frozen current issuer/receiver and Master requirements; no canonical schema/PKI/authority adoption.',
        'Global update/M05 hold is separate from successful resource teardown. Normal admission must preserve target scope, W/L/G/M, oneLocalClock writer/island barrier and dedicated server authority; STOP before promotion.',
        'All prior source/authority documents retain snapshot hashes and dates. Current governance deltas are recovery inputs; old plan artifacts are not silently updated to a new candidate.'],readiness_blockers=row(Q/'READINESS_BLOCKERS.json'),next_admission_proposal=row(Q/'PROPOSED_NEXT_QA_ADMISSION.json'),Foundation='HOLD',full_native_E2='NOT_RELEASED',all_execution=0)
    write(Q/'FINAL_PREPARATION_QUALIFICATIONS_R1.json',supplement)
    print(json.dumps(dict(status=VERDICT,protected=16929,additive=5,frozen=64,partial_count=after['partial_count'],report=row(REPORT),all_execution=0,mutable_R33_reads_hashes=0)))
def seal():
    ack=ids();assert load(R/'prepare.TOOL.json')['exit_code']==0
    cycles=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING_R1.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING_R1.json','RETURN_TOOL_PROOF_R1.json','DELIVERY_STATUS_R1.json']
    logger=['resume_r1/seal.STDOUT.txt','resume_r1/seal.STDERR.txt','resume_r1/seal.TOOL.json'];excluded=cycles+logger
    files=[p for p in sorted(Q.rglob('*')) if p.is_file() and p.relative_to(Q).as_posix() not in excluded]+[REPORT];assert not any(p.suffix=='.pyc' for p in files)
    rows=[row(p) for p in files]
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),delivery_id=ack['delivery_id'],result_id=ack['result_id'],resume_id=RESUME,files=rows,artifact_count=len(rows),cycle_exclusions=cycles,unfinished_logger_exclusions=logger,postseal_logger_and_actual_tool_return='Preserved separately after actual numeric exit/submission; no fabricated success.'))
    em=row(Q/'EVIDENCE_MANIFEST.json');index=dict(at=now(),delivery_id=ack['delivery_id'],wp_id=ack['wp_id'],wp_revision='S1',result_id=ack['result_id'],resume_id=RESUME,verdict=VERDICT,source_obligations=9,normal_observation_phases=8,ownership_rows=8,readiness_blockers=7,proposed_future_admission_tracks=3,plan_counts_not_executions=True,R33_candidate='NOT_READ_NOT_REVIEWED',selected_frozen_R32=ack['selected'],selected_mvid=ack['selected_mvid'],all_candidate_compiler_runner_global_Unity_native_operator_Process_adverse_executions=0,mutable_R33_reads_hashes=0,old_PASS_inherited=False,nativeE2='NOT_RELEASED',Foundation='HOLD',Master_disposition='PENDING',report=row(REPORT),evidence_manifest=em,preservation=row(Q/'PRESERVATION_BEFORE_AFTER_R1.json'),initial_ACK=row(Q/'ACK_INITIAL.json'),resume_ACK=row(Q/'RESUME_ACK.json'))
    write(Q/'RESULT_INDEX.json',index)
    write(Q/'ACK_COMPLETION_BINDING_R1.json',dict(at=now(),delivery_id=ack['delivery_id'],result_id=ack['result_id'],resume_id=RESUME,initial_ACK=row(Q/'ACK_INITIAL.json'),resume_ACK=row(Q/'RESUME_ACK.json'),initial_pending_ACK_not_rewritten=True,result_index=row(Q/'RESULT_INDEX.json')))
    write(Q/'RETURN_PENDING_R1.json',dict(at=now(),resume_id=RESUME,result_id=ack['result_id'],submission='PENDING_ACTUAL_TOOL',Master_receipt='PENDING',immutable_intent=True))
    check(rows);check([em,row(Q/'RESULT_INDEX.json'),row(Q/'ACK_COMPLETION_BINDING_R1.json')])
    completion=dict(**index,status='COMPLETED',artifact_count=len(rows),result_index=row(Q/'RESULT_INDEX.json'),ACK_binding=row(Q/'ACK_COMPLETION_BINDING_R1.json'),COMPLETION_last_atomic=True,exclusions=excluded,no_new_admission_closure_release=True)
    tmp=Q/'COMPLETION.json.tmp';target=Q/'COMPLETION.json';assert not tmp.exists() and not target.exists();write(tmp,completion);os.replace(tmp,target)
    print(json.dumps(dict(status='COMPLETED',verdict=VERDICT,artifact_count=len(rows),completion=row(target),evidence_manifest=em,report=row(REPORT),all_execution=0,mutable_R33_reads_hashes=0)))
def main():
    mode=sys.argv[1];assert mode in ['resume','prepare','seal'];out=R/(mode+'.STDOUT.txt');err=R/(mode+'.STDERR.txt');proof=R/(mode+'.TOOL.json');assert not out.exists() and not err.exists() and not proof.exists()
    so0,se0=sys.stdout,sys.stderr;code=0;started=now()
    with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
        sys.stdout,sys.stderr=so,se
        try:globals()[mode]()
        except BaseException:code=1;traceback.print_exc()
        finally:sys.stdout,sys.stderr=so0,se0
    write(proof,dict(script=row(Path(__file__)),argv=sys.argv,cwd=str(Path.cwd()),started_at=started,completed_at=now(),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True,all_execution=0,mutable_R33_reads_hashes=0))
    print(json.dumps(dict(stage=mode,exit_code=code,stdout=row(out),stderr=row(err))));sys.exit(code)
if __name__=='__main__':main()
