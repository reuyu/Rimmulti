"""Read-only frozen evidence indexing; does not import or execute candidate/runner."""
from review_setup import *
import re,collections
def inspect():
    frozen=load(MAN)['files']
    by_original={str(Path(r['original_path'])).lower():r for r in frozen}
    def ref(rel):
        p=FROZEN/rel
        assert str(ROOT/rel).lower() in by_original
        return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
    w='scratch/WorkerBridgeMod/Source/WorkerBridge.cs';c='scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';r='scratch/EngineGate05R3/Program.cs'
    anchor_specs=[('M01',w,'HandleLaunchOperatorValidator',[2057,2081,2121,2187,2222]),('M02',w,'STEP / SEAL / STAGE / Complete',[1618,1760,1986,2347,2545]),('M02',r,'CreateArmedBridge',[286]),('M03',w,'Execute / Complete / Promote',[2230,2301,2331,2500,2545,2571,2586,2631,2742,2807]),('M03',c,'CensusManifestData / GenerateCensus',[344,405]),('M04',c,'ContentProfileProvider',[1534,1543,1555,1560,1622,1651,1681,1719,1745,1756,1878]),('M04',r,'FAIL-02',[590]),('M05',r,'Profile mock / armed fixture / child / runner IO',[244,263,286,399,413])]
    anchors=[dict(finding=k,function=fn,lines=lines,**ref(rel)) for k,rel,fn,lines in anchor_specs]
    res=load(FROZEN/'scratch/EngineGate05R3/results.json');raw=(FROZEN/'scratch/EngineGate05R3/raw_console.txt').read_text(encoding='utf-8-sig')
    rawids=re.findall(r'^\[PASS\] ([A-Z]+-\d+)',raw,re.M);ids=[x['id'] for x in res['results']]
    assert len(ids)==32 and len(set(ids))==32 and rawids==ids and all(x['status']=='PASS' for x in res['results'])
    coverage=[]
    for x in res['results']:
        i=x['id'];typ='metadata/hash observation' if i.startswith('PROV-') else 'OS child lifecycle inside armed fixture' if i=='GEN-02' else 'schema constant assertion' if i=='FAIL-02' else 'reflection fixture / handler and file IO'
        coverage.append(dict(id=i,status_as_reported=x['status'],producer_execution_class=x['execution_class'],qa_evidence_class=typ,native_semantic_validation=False,qa_rerun=False))
    write(Q/'COVERAGE_INDEX.json',dict(at=now(),reported_total=32,reported_pass=32,reported_fail=0,raw_pass_ids_agree=True,producer_class_counts=dict(collections.Counter(x['execution_class'] for x in res['results'])),qa_class_counts=dict(collections.Counter(x['qa_evidence_class'] for x in coverage)),rows=coverage,observed_native_full_flow=0,qa_process_or_candidate_executions=0))
    completionrel='Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/COMPLETION.json';comp=load(FROZEN/completionrel);checks=[]
    for a in comp['artifacts']:
        row=by_original[str(ROOT/a['path']).lower()];p=Path(row['frozen_path']);assert sha(p)==a['sha256'] and p.stat().st_size==a['size_bytes']
        checks.append(dict(role=a['role'],declared_path=a['path'],frozen_path=str(p),actual_sha256=sha(p),size_bytes=p.stat().st_size,hash_and_size_match=True,declared_path_absolute=Path(a['path']).is_absolute()))
    roles=['implementation_report','release_manifest','harness','results','raw_evidence','candidate_binary','source','pdb','engine_freeze_before','engine_freeze_after'];fields=['dispatch_id','wp_id','wp_revision','completed_at','e1_verdict','limitations']
    reportrel='docs/POC_EngineHost_Semantic_Authority_Gate_05_R3.md';rep=(FROZEN/reportrel).read_text(encoding='utf-8-sig');table=[]
    for line in rep.splitlines():
        if not line.startswith('| **'):continue
        cells=[s.strip() for s in line.split('|')[1:-1]];path=cells[1].strip('`');actual=ref(path);declared_sha=cells[3].strip('`');size=int(cells[2].replace(',',''))
        table.append(dict(role=cells[0].strip('*'),declared_sha256=declared_sha,declared_bytes=size,actual=actual,sha_match=declared_sha==actual['sha256'],size_match=size==actual['bytes']))
    assert sum(not t['sha_match'] for t in table)==4
    write(Q/'PACKAGING_INDEX.json',dict(at=now(),completion=ref(completionrel),completion_artifacts=checks,missing_exact_fields=[x for x in fields if x not in comp],missing_exact_roles=[x for x in roles if x not in [a['role'] for a in comp['artifacts']]],alias_identity_reconciled=True,external_artifacts_proved=False,report_table=table,post_completion_freeze_not_pre_execution_proof=True,pre_execution_dependency_content_tooling_snapshot_not_established_in_supplied_package=True))
    role=dict(at=now(),source=ref(w),grant_mode_for_proposal='SIMULATION',validator_task_mode='READ_ONLY',validator_result_mode='task.allowedMode',step_readonly_rejected_line=1618,seal_readonly_rejected_line=1760,stage_task_readonly_line=1986,result_task_copy_line=2347,complete_task_and_grant_equality_line=2545,fixture_readonly_grant_source=ref(r),fixture_readonly_grant_line=286,conclusion='Static normal-flow mode regression confirmed; runtime untested',repair_constraint='Keep approved SIMULATION proposal grant; explicitly distinguish validator execution role and proposal operation mode; compare both with admitted context',executed=False)
    write(Q/'NORMAL_ROLE_TRACE.json',role)
    text=(FROZEN/c).read_text(encoding='utf-8-sig');dto=text.split('public class ValidatorResult',1)[1].split('\n    }',1)[0];dtofields=re.findall(r'public\s+[\w?]+\s+(\w+)\s*=',dto)
    native=(FROZEN/'scratch/EngineGate05R3/native_execution_observation.txt').read_text(encoding='utf-8-sig')
    nativeindex=dict(evidence=ref('scratch/EngineGate05R3/native_execution_observation.txt'),execution_attempt=next(x for x in native.splitlines() if x.startswith('Execution Attempt:')),runtime_copy_label_is_execution_proof=False,raw_argv='-batchmode -nographics -quicktest',report_argv='-batchmode -nographics',reported_pid=16436,reported_start_utc='2026-10-08T04:07:06.0509655Z',numeric_exit_or_loader_trace_present=False,isolated_actual_userdata_mod_loaded_candidate_profile_census_unobserved=True,qa_classification='NATIVE_UNTESTED / CAUSE_UNKNOWN',qa_launches=0)
    write(Q/'EVIDENCE_INDEX.json',dict(at=now(),freeze_manifest=dict(path=str(MAN),sha256=sha(MAN),files=133),anchors=anchors,validator_result_dto_fields=dtofields,expanded_dto_credited=True,native=nativeindex,frozen_inventory=frozen,scope='static review only; no exploit demonstration, candidate/runner/native execution, or rebuild'))
    print(json.dumps(dict(counts=collections.Counter(x['qa_evidence_class'] for x in coverage),producer_class_counts=collections.Counter(x['execution_class'] for x in res['results']),dto_fields=len(dtofields),completion_checked=len(checks),report_sha_mismatches=4),indent=2))
if __name__=='__main__':inspect()
