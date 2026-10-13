"""Frozen-only static evidence indexing; no candidate/runner import or execution."""
from review_setup import *
import re,collections
def main():
    inv=load(MAN)['files'];by={str(Path(x['original_path'])).lower():x for x in inv}
    def ref(rel):
        p=FROZEN/rel;assert str(ROOT/rel).lower() in by;return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
    w='scratch/WorkerBridgeMod/Source/WorkerBridge.cs';c='scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';r='scratch/EngineGate05R4/Harness/Program.cs'
    specs=[('M01',w,'Complete / Receipt / Promote',[2600,2607,2614,2619,2624,2706,2763]),('M01',c,'StageValidationReceipt',[62]),('M02',w,'admitted fields / launch / bind',[386,387,2128,2138,2154,2214,2231]),('M03',w,'Launch / Bind / Execute StartTime',[2172,2180,2240,2244,2363,2370]),('M04',w,'Execute / Promote target',[2320,2348,2352,2888,2903]),('M05',w,'Bind / Execute errors',[2216,2222,2267,2273,2282,2288,2293,2418,2426]),('M06',c,'ContentProfileProvider',[1535,1556,1561,1604,1611,1616,1638,1695,1702,1738,1763,1775,1897,1901,1908]),('M07',r,'Harmony/fixtures/writer/mock census/prof',[48,91,96,373,381,392,414,425,445,545,547,591,794,863,919,925])]
    anchors=[dict(finding=k,function=fn,lines=lines,**ref(rel)) for k,rel,fn,lines in specs]
    results=load(FROZEN/'scratch/EngineGate05R4/results.json');raw=(FROZEN/'scratch/EngineGate05R4/raw_console.txt').read_text(encoding='utf-8-sig');ids=[x['id'] for x in results['results']];rawids=re.findall(r'^\[PASS\] ([A-Z]+-\d+)',raw,re.M)
    assert len(ids)==43 and len(set(ids))==43 and ids==rawids and all(x['status']=='PASS' for x in results['results'])
    cov=[]
    for x in results['results']:
        i=x['id'];kind='metadata/hash observation' if i.startswith('PROV-') else 'OS child lifecycle inside fixture' if i=='GEN-02' else 'schema constant assertion' if i=='PROF-01' else 'cache helper state assertion' if i=='PROF-02' else 'reflection API inventory assertion' if i=='SEC-08' else 'mock/reflection fixture handler and file IO'
        limitations=['Submitted producer result; QA did not rerun','Native semantic execution not established']
        if i=='GEN-03':limitations.append('Actual writer is runner Program.cs:547, not OS child')
        if i=='GEN-07':limitations.append('Promote invoked with mocked Game, GenerateCensus and ComputeManifestHash')
        if i=='SEC-06':limitations.append('Result StartTime mismatch fixture does not exercise OS StartTime getter failure')
        if i=='CLAMP-03':limitations.append('Predicate excludes clamping error text; does not require successful validator result')
        if i=='PROF-01':limitations.append('Version constant equality does not test DLC encoding')
        if i=='PROF-02':limitations.append('InvalidateCache + IsCached false, no actual content lifecycle validation')
        cov.append(dict(id=i,producer_status=x['status'],producer_class=x['execution_class'],qa_class=kind,limitations=limitations,qa_execution=False))
    write(Q/'COVERAGE_INDEX.json',dict(at=now(),reported_total=43,reported_pass=43,raw_json_ids_counts_match=True,producer_class_counts=dict(collections.Counter(x['execution_class'] for x in results['results'])),qa_class_counts=dict(collections.Counter(x['qa_class'] for x in cov)),rows=cov,native_semantic_loop_observed=0,qa_candidate_runner_native_build_reproduction_count=0))
    comprel='Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1/COMPLETION.json';comp=load(FROZEN/comprel);checks=[]
    for a in comp['artifacts']:
        row=by[str(Path(a['path'])).lower()];p=Path(row['frozen_path']);assert sha(p)==a['sha256'] and p.stat().st_size==a['size'];checks.append(dict(role=a['role'],declared_path=a['path'],frozen_path=str(p),sha256=sha(p),bytes=p.stat().st_size,hash_size_match=True))
    pre=load(FROZEN/'scratch/EngineGate05R4/CANDIDATE_PRE_RUN_MANIFEST.json');prec=[]
    for role,obj in [('selected',pre['selected_candidate']),('selected_pdb',pre['selected_candidate']['matching_pdb']),('alternate',pre['alternate_release_candidate']),('alternate_pdb',pre['alternate_release_candidate']['matching_pdb'])]+[('source',x) for x in pre['sources']]:
        row=by[str(Path(obj['path'])).lower()];p=Path(row['frozen_path']);prec.append(dict(role=role,declared=obj,actual_frozen=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size),sha_match=obj['sha256']==sha(p),size_match=obj['size']==p.stat().st_size))
    oldman=load(ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/MASTER_GATE05_R3_REVIEW_FREEZE_MANIFEST.json');oldby={str(Path(x['original_path'])).lower():x for x in oldman['files']};bef=load(FROZEN/'scratch/EngineGate05R4/ENGINE_FREEZE_BEFORE.json');bc=[]
    for obj in bef['authorized_engine_paths']:
        row=oldby[str(Path(obj['path'])).lower()];p=Path(row['frozen_path']);bc.append(dict(declared=obj,actual_r3_frozen=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size),sha_match=obj['sha256']==sha(p),size_match=obj['size']==p.stat().st_size))
    assert sum(not x['size_match'] for x in bc)==7
    release=load(FROZEN/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R4.json');releasechecks=[]
    for x in release['source_files']:
        actual=ref(x['path']);assert actual['sha256']==x['sha256'] and actual['bytes']==x['bytes'];releasechecks.append(actual)
    report=(FROZEN/'docs/POC_EngineHost_Semantic_Authority_Gate_05_R4.md').read_text(encoding='utf-8-sig');report_rows=[]
    for line in report.splitlines():
        if line.startswith('| `'):
            cells=[s.strip().strip('`') for s in line.split('|')[1:-1]]
            if len(cells)>=4 and re.fullmatch('[A-F0-9]{64}',cells[2]):
                key=str(ROOT/cells[0].replace('\\','/')).lower();row=by[key];p=Path(row['frozen_path']);report_rows.append(dict(path=str(p),declared_sha256=cells[2],actual_sha256=sha(p),declared_bytes=int(cells[3].replace(',','')),actual_bytes=p.stat().st_size,match=cells[2]==sha(p) and int(cells[3].replace(',',''))==p.stat().st_size))
    write(Q/'PACKAGING_INDEX.json',dict(at=now(),completion=ref(comprel),completion_artifacts=checks,exact_standard_fields_present=all(x in comp for x in ['dispatch_id','wp_id','wp_revision','completed_at','e1_verdict','limitations']),limitations_present=True,limitations_type=type(comp['limitations']).__name__,limitations_object_content_readable=True,checker_string_or_list_type_contract_not_met=True,all_required_roles_present=all(x in [a['role'] for a in comp['artifacts']] for x in ['implementation_report','release_manifest','harness','results','raw_evidence','candidate_binary','source','pdb','engine_freeze_before','engine_freeze_after']),pre_run_manifest=ref('scratch/EngineGate05R4/CANDIDATE_PRE_RUN_MANIFEST.json'),pre_run_final_comparisons=prec,pre_run_sha_mismatch_count=sum(not x['sha_match'] for x in prec),before_baseline_vs_prior_frozen=bc,before_size_mismatch_count=7,release_sources_match=releasechecks,report_hash_table_checks=report_rows,post_completion_freeze_is_not_pre_execution_proof=True))
    runtime=[x for x in inv if '\\RuntimeCopy\\' in x['frozen_path']];assert len(runtime)==7
    worker=(FROZEN/w).read_text(encoding='utf-8-sig');promote=worker.split('private string HandlePromoteStaged',1)[1].split('private string ',1)[0]
    write(Q/'NORMAL_ROLE_TRACE.json',dict(at=now(),source=ref(w),r3_direct_equality_regression_removed=True,complete_authority_and_grant_required_simulation=[2600,2607],task_result_required_readonly=[2614,2619,2624],receipt_simulator_operation_mode_written_line=2706,receipt_simulator_operation_mode_checked_in_promote='simulatorOperationMode' in promote,admitted_sha_reference_count=worker.count('AdmittedOperatorValidatorSha'),admitted_exe_default_empty=True,execute_target_clamp_removed=True,promote_first_map_fallback_line=2903,normal_native_step_seal_stage_validate_complete_unobserved=True,executed=False))
    write(Q/'EVIDENCE_INDEX.json',dict(at=now(),manifest=dict(path=str(MAN),sha256=sha(MAN),files=232),frozen_inventory=inv,anchors=anchors,runtime_inventory=runtime,runtime_inventory_count=7,runtime_inventory_assets='root executable/library/text5 + selected mod DLL/PDB2',native_log=ref('scratch/EngineGate05R4/native_execution_observation.txt'),native_logged_pid=18816,native_logged_start_utc='2026-10-08T07:31:20.8191595Z',numeric_exit_loader_actual_core_profile_census_unobserved=True,installed_original_not_read=True,scope='frozen defensive static review only; candidate/runner/native/build/reproduction0'))
    print(json.dumps(dict(qa_counts=collections.Counter(x['qa_class'] for x in cov),producer_counts=collections.Counter(x['execution_class'] for x in results['results']),completion18=True,pre_run_sha_mismatches=sum(not x['sha_match'] for x in prec),before_size_mismatch=7,runtime_files=7,report_table_rows=len(report_rows),report_table_mismatch=sum(not x['match'] for x in report_rows)),indent=2))
if __name__=='__main__':main()
