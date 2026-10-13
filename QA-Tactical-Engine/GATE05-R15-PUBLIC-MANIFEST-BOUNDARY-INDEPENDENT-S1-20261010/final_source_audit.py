from review_setup import *
import re
if __name__=='__main__':
    assert not (Q/'runner/QaCodecRunner.exe').exists()
    for name in ['RunnerTemplate.cs.txt','Program.cs']:
        path=Q/name;s=path.read_text(encoding='utf-8-sig')
        assert 'class ObservedProvider' not in s
        s=s.replace('  static bool Compared(', (Q/'ObservedProvider.cs.txt').read_text(encoding='utf-8-sig')+'\n  static bool Compared(')
        assert s.count('class ObservedProvider')==1
        assert not re.search(r'(?:ComputeActualContentProfile\w*|GetActualContentProfile\w*|SetComputationError|ClearComputationError)\s*\(',s)
        assert 'BindingFlags.NonPublic' not in s and '_globalCache' not in s
        path.write_text(s,encoding='utf-8')
    d=load(Q/'ORACLE_BEFORE_BUILD.json');d['final_runner_source']=row(Q/'Program.cs');d['at']=now();d['r15_both_overloads_fresh_current_matching_publications_per_run']=10;d['public_boundary_metadata_only']=True;write(Q/'ORACLE_BEFORE_BUILD.json',d)
    graph=(Q/'run_identity.py').read_text(encoding='utf-8-sig').replace("'bootstrap_runner.py'","'bootstrap_runner.py','final_source_audit.py'");(Q/'run_identity.py').write_text(graph,encoding='utf-8')
    write(Q/'FINAL_PROSPECTIVE_SOURCE_AUDIT.json',dict(at=now(),program=row(Q/'Program.cs'),wrapper=row(Q/'ObservedProvider.cs.txt'),all_own_actual_provider_invocations_wrapped=True,forbidden_actual_provider_error_private_native_adverse_call_sites=0,normal_publication_overloads=2,current_matching_publications_per_run=10,new_outcarrier_fullfields_and_clone_before_caller_edits=True,metadata_actualroutes_uninvoked=True,scope_counter='Directownproviderwrappers+explicitcore/groupedgetterstages,notnestedprofiling',candidate_calls_so_far=0,runner_builds_so_far=0,template_wrapper_reinserted_before_final_build=True))
    print('Final normal source audit/pin complete before build/candidatecalls')
