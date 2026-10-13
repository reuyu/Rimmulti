from review_setup import *
if __name__=='__main__':
    assert not (Q/'analyze_review.py').exists()
    old=(PREVQ/'analyze_review.py').read_text(encoding='utf-8-sig');s=old[:old.index('    findings=[')]
    s=s.replace('G05R13-2661a749','G05R14-11e03c45').replace("==339","==360").replace("len(pairs)==115","len(pairs)==125")
    # Resolve actual R14 frozen directory from its immutable QA metadata; no guessed address.
    prior=Path(load(PREVQ/'R14_LINEAGE.json')['candidates'][0]['documents'][0]['frozen_source_path'])
    s=s.replace("OLD=ROOT/'Dispatcher/CANDIDATES/G05R14-11e03c45/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'","OLD=Path("+repr(str(prior))+")")
    start=s.index("            p=folder/(n+'.canonical.json')");end=s.index("        for p in folder.glob",start)
    s=s[:start]+'''            for suffix in ['.canonical.json','.legacy.canonical.json','.out.canonical.json']:
                p=folder/(n+suffix);expected=refs/('cache.'+policy+'.canonical.json');assert p.read_bytes()==expected.read_bytes();bindings.append(dict(actual=row(p),reference=row(expected),matched=True))
'''+s[end:]
    start=s.index("        ledger=load(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json')");end=s.index('    assert actual_scopes',start)
    s=s[:start]+'''        ledger=load(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json');counts=collections.Counter((x['scope'],x['api']) for x in ledger)
        assert counts[('standalone','TryPublishComputedEntry_LEGACY_CURRENT_MATCHING')]==5 and counts[('standalone','TryPublishComputedEntry_OUTENTRY_CURRENT_MATCHING')]==5
        assert counts[('standalone','CaptureStateSnapshot')]==5 and counts[('standalone','CaptureStateSnapshot_OUTENTRY')]==5
        direct=sum(v for (scope,api),v in counts.items() if scope=='direct_pure_provider');grouped=len(ledger)-direct
        assert not any(re.search(r'GetActual|ComputeActual|Seed|Override|SetComputationError|NonPublic|stale|mismatch',x['api'],re.I) for x in ledger)
        assert 'cache calls0' not in (folder/'RAW_CONSOLE.txt').read_text(encoding='utf-8-sig')
        scope=dict(run_id=load(folder/'NORMAL_RESULTS.json')['run_id'],actual_runtime_ledger=row(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json'),actual_logged_stages=len(ledger),direct_provider_API_calls=direct,core_or_global_grouped_stages=grouped,counts=[dict(scope=s,api=api,observed_logged_count=n) for (s,api),n in sorted(counts.items())],matching_standalone_publications=10,legacy_matching_publications=5,outcarrier_matching_publications=5,source_scope=row(Q/'FINAL_PROSPECTIVE_SOURCE_AUDIT.json'),pure_codec_order_coverage=dict(generic_cases=12,order_cases=14,historical_leaf_count=65),counter_limit='DirectownproviderAPIwrappers plus explicitcore/groupedgetterstages;not nestedinternalproduction profiling',actual_global_publication_getactual_compute_native_error_adverse_source_sites=0)
        actual_scopes.append(scope)
'''+s[end:]
    s=s.replace(",preexecution_pathlength_setup_failure=row(Q/'PRE_EXECUTION_METADATA_SETUP_FAILURE.json')",",preexecution_candidate_calls=0,priorR14setupfailure_not_inherited=True")
    s+=(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8-sig');(Q/'analyze_review.py').write_text(s,encoding='utf-8');print('OwnR15analysis sources written;no candidateexecutions')
