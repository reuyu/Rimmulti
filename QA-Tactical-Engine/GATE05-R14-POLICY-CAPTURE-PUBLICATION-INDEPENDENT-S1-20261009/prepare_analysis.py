from review_setup import *
if __name__=='__main__':
    assert not (Q/'analyze_review.py').exists()
    old=(PREVQ/'analyze_review.py').read_text(encoding='utf-8-sig');prefix=old[:old.index('    findings=[')]
    prefix=prefix.replace('G05R12-e9dcd1e6','G05R13-2661a749').replace('CACHE_B_AFTER_INVALIDATE_G2','CACHE_B_AFTER_INVALIDATE_G3').replace('CACHE_B_G3','CACHE_B_G4')
    first=prefix.index("        ledger=load(folder/'ACTUAL_CACHE_LIFECYCLE_CALL_LEDGER.json')");last=prefix.index('    processes=[]',first)
    prefix=prefix[:first]+'''        ledger=load(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json');counts=collections.Counter((x['scope'],x['api']) for x in ledger);assert counts[('standalone','TryPublishComputedEntry_CURRENT_MATCHING_ONLY')]==5 and counts[('standalone','CaptureStateSnapshot')]==5
        assert len(ledger)==835 and sum(v for (scope,api),v in counts.items() if scope=='direct_pure_provider')==763
        assert not any(re.search(r'GetActual|ComputeActual|Seed|Override|SetComputationError|NonPublic|stale|mismatch',x['api'],re.I) for x in ledger)
        assert 'cache calls0' not in (folder/'RAW_CONSOLE.txt').read_text(encoding='utf-8-sig')
        scope=dict(run_id=load(folder/'NORMAL_RESULTS.json')['run_id'],actual_runtime_ledger=row(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json'),actual_logged_stages=len(ledger),direct_provider_API_calls=763,core_or_global_grouped_stages=72,counts=[dict(scope=s,api=api,observed_logged_count=n) for (s,api),n in sorted(counts.items())],matching_standalone_publications=5,source_scope=row(Q/'PROSPECTIVE_SOURCE_EXECUTION_SCOPE.json'),pure_codec_order_coverage=dict(generic_cases=12,order_cases=14,historical_leaf_count=65),counter_limit='Directownprovider API wrappers plus explicitcore/groupedgetterstages;not nestedinternalproduction profiling',r13_false_zerofooter_not_inherited=True,actual_global_publication_getactual_compute_native_adverse_source_sites=0)
        actual_scopes.append(scope)
    assert actual_scopes[0]['counts']==actual_scopes[1]['counts'];write(Q/'ACTUAL_EXECUTION_SCOPE.json',dict(at=now(),rows=actual_scopes,raw_source_unchanged=True,actual_explicit_own_provider_invocations_observed=True,global_actual_native_adverse_methods_absent_fromrunner=True))
'''+prefix[last:]
    prefix=prefix.replace("PRE_RUN_DIRECTORY_ALLOCATION_FAILURE.json","PRE_EXECUTION_METADATA_SETUP_FAILURE.json")
    tail=(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8-sig');(Q/'analyze_review.py').write_text(prefix+tail,encoding='utf-8')
