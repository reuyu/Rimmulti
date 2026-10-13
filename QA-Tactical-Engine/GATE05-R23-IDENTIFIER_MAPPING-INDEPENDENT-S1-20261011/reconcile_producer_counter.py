from review_setup import *
import shutil
archive=Q/'analysis_attempt1';assert not archive.exists();archive.mkdir()
for p in list(Q.glob('*.json'))+[Q/'analyze_review.py',Q/'AnalysisTail.py.txt']:
    if p.name in ['ACK_INITIAL.json','ACK.json','PRESERVATION_BEFORE.json','R23_FROZEN_LINEAGE.json','INPUT_EXPECTED_SEMANTICS.json','RECEIPT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','PRE_RUN1_MANIFEST.json','PRE_RUN2_MANIFEST.json','EXECUTION_ADMISSION_BEFORE_BUILD.json']:continue
    if p.name in ['FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json','ACTUAL_EXECUTION_SCOPE.json','FRESH_PROCESS_PROOF.json','NORMAL_FAILURE_RECONCILIATION.json','RECEIPT_FULLTYPED_GRAPH_AND_REFERENCE_BINDING.json','UTC_LITERAL_TYPE_AND_WHOLE_BYTES_BINDING.json','USED_CALLER_CLONE_AND_ORIGINAL_DECLARATION_BINDING.json','NORMAL_ROLECAP_EQUIVALENCE_FULLGRAPH_BINDING.json','INDEPENDENT_REVIEW_FINDINGS.json','analyze_review.py','AnalysisTail.py.txt']:shutil.copy2(p,archive/p.name)
rows=[]
for n in ['run_en_us','run_de_de']:
    p=FROZEN/'scratch/EngineGate05R23IdentifierMapping'/n/'E1_EXECUTION_REPORT.json';d=load(p);rows.append(dict(source=row(p),direct_count=sum(d['call_counts'].values()),raw_call_counts=d['call_counts']))
assert all(r['direct_count']==66 for r in rows)
write(Q/'PRODUCER_COUNTER_RECONCILIATION.json',dict(at=now(),source_results=rows,Master_E1_manual71_annotation_not_adopted=True,actual_sum66_expression='14+6+28+5+8+1+1+1+2',failed_postanalysis_attempt1_preserved=True,reason='Metadata evidence assertion71 contradicted actualrawsum66. Candidate/compiler executions unchanged build1/children2,allnormalPASS. Nooracle/candidate/runner/runoutputchange.',archive=[row(p) for p in sorted(archive.iterdir())],no_candidate_rerun_or_outputderived_oracle_change=True))
for n in ['analyze_review.py','AnalysisTail.py.txt']:
    p=Q/n;t=p.read_text(encoding='utf-8');assert 'direct==71' in t;t=t.replace('direct==71','direct==66').replace('manual71_excludes','manual66_excludes').replace('Producer7labels/manual71','Producer7labels/manual66');p.write_text(t,encoding='utf-8')
print('Metadata-only producer ledger contradiction preserved: actual66 ratherthanMaster71. No candidate/compiler rerun/inputoraclechange.')
