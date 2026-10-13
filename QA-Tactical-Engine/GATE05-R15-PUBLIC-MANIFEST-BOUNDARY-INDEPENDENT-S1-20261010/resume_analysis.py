from review_setup import *
if __name__=='__main__':
    current=Q/'analyze_review.py';s=current.read_text(encoding='utf-8-sig');assert not (Q/'analysis_initial').exists()
    archive=Q/'analysis_initial';archive.mkdir();(archive/'analyze_review.py.txt').write_text(s,encoding='utf-8')
    for name in ['ACTUAL_EXECUTION_SCOPE.json','FRESH_PROCESS_PROOF.json','FIXED_SOURCE_SCOPE.json','REFERENCE_SCHEMA_API_ACTUAL_BINDING.json','R15_PUBLIC_BOUNDARY_METADATA_BINDING.json','INDEPENDENT_REVIEW_FINDINGS.json','CRITERIA_DISPOSITION.json']:
        p=Q/name
        if p.exists():(archive/name).write_bytes(p.read_bytes())
    write(Q/'ANALYSIS_METADATA_COUNT_RECONCILIATION.json',dict(at=now(),initial_analysis_source=row(archive/'analyze_review.py.txt'),initial_tool_exit=1,initial_chunk='76cdc9',initial_failure='ProducerBEFORE assumed8 totalrows from shorthandMasterprose;actual frozen9rows (8priorR14rows plus1alreadyR15Census),AFTER9,total18',actual_metadata_before_count=9,actual_metadata_after_count=9,prior8_not_total_before_count=True,original_graph_outputs_unchanged=True,candidate_oracle_runner_sources_unchanged=True,candidate_reruns=0,QA_rebuilds=0,initial_derived_records_preserved=True))
    s=s.replace("len(before['files'])==8","len(before['files'])==9").replace('BEFORE8rowsCensusalreadyR15whilebinsR14','BEFORE9rows(8priorR14+1alreadyR15Census)whilebinsR14').replace('before8_rows=before_rows','before9_rows=before_rows')
    current.write_text(s,encoding='utf-8');print('Derived metadata count reconciled;no execution/oracle changes')
