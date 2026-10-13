from review_setup import *
if __name__=='__main__':
    assert not (Q/'run_identity.py').exists()
    s=(PREVQ/'run_identity.py').read_text(encoding='utf-8-sig')
    replacements={
      "'final_source_audit.py'":"'prepare_graph.py','ObservedProvider.cs.txt','RUN_ALLOCATION_PLAN.json'",
      'R13_LINEAGE.json':'R14_LINEAGE.json','WP_QA_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_INDEPENDENT_S1.md':'WP_QA_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_S1.md',
      "for r in load(PREVQ/'ACTUAL_LOADED_MANAGED.json'):":"for r in load(Path(load(PREVQ/'PRE_RUN1_MANIFEST.json')['output_root'])/'ACTUAL_LOADED_MANAGED.json'):",
      "runid='R13-'+uuid.uuid4().hex[:16];culture='en-US' if stage=='1' else 'de-DE';out=Q/'runs'/runid;assert not out.exists();out.mkdir(parents=True)":"allocation=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][int(stage)-1];runid=allocation['run_id'];culture=allocation['culture'];out=Path(allocation['output_root']);assert out.exists() and not any(out.iterdir()) and allocation['allocated_validated_before_final_build_calls']"}
    for a,b in replacements.items():assert a in s,a;s=s.replace(a,b)
    (Q/'run_identity.py').write_text(s,encoding='utf-8')
    write(Q/'SOURCE_REUSE_AUDIT.json',dict(at=now(),old_sources_readonly_text=[row(PREVQ/'review_setup.py'),row(PREVQ/'RunnerTemplate.cs.txt'),row(PREVQ/'CacheChecks.cs.txt'),row(PREVQ/'run_identity.py')],new_program=row(Q/'Program.cs'),new_direct_invocation_wrappers=row(Q/'ObservedProvider.cs.txt'),graph_source=row(Q/'run_identity.py'),old_binaries_executed=False,old_top_level_scripts_imported=False,prospective_invalidate_plusone_and_header_and_ledger_correction=True,actual_candidate_calls=0,all_runtime_outputs_unique_process_directory=True))
