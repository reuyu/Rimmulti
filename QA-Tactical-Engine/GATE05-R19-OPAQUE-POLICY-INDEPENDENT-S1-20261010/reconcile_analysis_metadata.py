from review_setup import *
import shutil
if __name__=='__main__':
    archive=Q/'analysis_initial_attempt';assert not archive.exists();archive.mkdir()
    for n in ['analyze_review.py','ACTUAL_EXECUTION_SCOPE.json','FRESH_PROCESS_PROOF.json','FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json','NORMAL_FAILURE_RECONCILIATION.json','INDEPENDENT_REVIEW_FINDINGS.json']:
        p=Q/n
        if p.exists():shutil.copy2(p,archive/n)
    if (Q/'source_extracts').exists():shutil.copytree(Q/'source_extracts',archive/'source_extracts')
    write(archive/'ANALYSIS_FAILURE_TOOL_PROOF.json',dict(exit_code=1,phase='metadata-only producer inventory enumeration',line=98,error='AssertionError exact pathset assumption failed',candidate_build_calls=0,candidate_run_calls=0))
    text=(archive/'analyze_review.py').read_text(encoding='utf-8');prefix=text[:text.index("    admission=load(Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json')")]
    (Q/'analyze_review.py').write_text(prefix+(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8'),encoding='utf-8')
    observed=[];base=FROZEN/'scratch/EngineGate05R19OpaquePolicy'
    for label in ['run_en_us','run_de_de']:
        out=base/label;d=load(out/'OUTPUT_INVENTORY.json');actual={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'};declared={r['relative_path'] for r in d};observed.append(dict(run=label,inventory=row(out/'OUTPUT_INVENTORY.json'),declared=len(declared),actual_nonself=len(actual),unlisted=sorted(actual-declared)))
    write(Q/'PRODUCER_INVENTORY_METADATA_RECONCILIATION.json',dict(at=now(),rows=observed,initial_metadata_assertion_failure_archived=True,controlling_independent_interpretation='deDE8declared/8matched plus2unlistedlogs;Master E1 10allmatched historicalannotation superseded. enUS10declared/2streammismatch. Producer/raw untouched.',candidate_oracle_source_runner_frozen_and_runoutputs_changed=False,builds_runs_reruns_during_metadata_repair=0,analysis_only=True))
    print('Metadata-only producer inventory discrepancy reconciled;initial attempt archived,actual candidate outputs/oracle unchanged')
