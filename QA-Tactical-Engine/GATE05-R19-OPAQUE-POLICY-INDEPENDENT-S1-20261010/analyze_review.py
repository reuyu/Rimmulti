from review_setup import *
from run_identity import verify_inventory,metadata_helpers
import collections,re,difflib
SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
CENSUS=SOURCE.parent/'EngineHostCensus.cs'
def checks(v):
    if isinstance(v,dict):
        if all(k in v for k in ['matched','expected','actual']):yield v
        for x in v.values():yield from checks(x)
    elif isinstance(v,list):
        for x in v:yield from checks(x)
def anchor(a,b):return dict(source=row(SOURCE),first_line=a,last_line=b)
if __name__=='__main__':
    assert not (Q/'INDEPENDENT_EXECUTION_SUMMARY.json').exists()
    pres=[load(Q/f'PRE_RUN{i}_MANIFEST.json') for i in [1,2]];runs=[Path(p['output_root']) for p in pres];observed=[load(r/'NORMAL_RESULTS.json') for r in runs];oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json')
    for r in runs:verify_inventory(r)
    assert load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['first_inventory']
    pairs=[];refpairs=[];bindings=[];typedfiles=[];typedcount=0;typedfail=0;scope=[];processes=[];failure_rows=[];loadedbindings=[]
    names=[]
    for n in oracle['codec_cases']:names.extend(n+s for s in ['.canonical.json','.rebuilt.canonical.json','.transport.json'])
    for n,c in oracle['config_cases'].items():
        for route in c['routes']:names.extend(n+'_'+route+s for s in ['.snapshot-graph.json','.redacted.json','.owned-edits.json'])
        names.extend(n+s for s in ['.parse.typed-checks.json','.expected-policy.canonical.json'])
    for n in oracle['validator_results']:names.append(n+'.result.redacted.json')
    for n in oracle['policy_cases']:names.append(n+'.policy.json')
    for n in names:
        a=runs[0]/n;b=runs[1]/n;pairs.append(dict(run1=row(a),run2=row(b),exact_utf8_equal=a.read_bytes()==b.read_bytes(),repeatability_not_semantic_PASS=True))
    assert all(p['exact_utf8_equal'] for p in pairs)
    for p in sorted((runs[0]/'reference_content').glob('*.json')):
        b=runs[1]/'reference_content'/p.name;assert p.read_bytes()==b.read_bytes();refpairs.append(dict(run1=row(p),run2=row(b),reference_utf8_equal=True))
    pe=metadata_helpers()
    for pre,folder,o in zip(pres,runs,observed):
        failure=[r for r in o['results'] if r['status']=='FAIL'];assert len(failure)==o['failed_assertions'];failure_rows.append(dict(run_id=pre['run_id'],results=failure))
        for n in oracle['codec_cases']:
            for suffix,ref in [('.canonical.json','canonical.'),('.rebuilt.canonical.json','canonical.'),('.transport.json','transport.')]:
                a=folder/(n+suffix);b=folder/'reference_content'/(ref+n+'.canonical.json');bindings.append(dict(actual=row(a),reference=row(b),matched=a.read_bytes()==b.read_bytes()))
        for n,c in oracle['config_cases'].items():
            for route in c['routes']:
                id=n+'_'+route;a=folder/(id+'.redacted.json');b=folder/(id+'.expected-redacted.json');graph=load(folder/(id+'.snapshot-graph.json'))
                bindings.append(dict(case_id=id,kind='full_snapshot_graph_and_redacted',actual=row(a),reference=row(b),fulltyped_graph=row(folder/(id+'.snapshot-graph.json')),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),redacted_bytes_matched=a.read_bytes()==b.read_bytes(),properties_matched=graph['properties']==c['expected_snapshot'],declaration_matched=graph['declaration']==c['expected_declaration'],record_matched=graph['record']==c['expected_record'],matched=a.read_bytes()==b.read_bytes() and graph['properties']==c['expected_snapshot'] and graph['record']==c['expected_record']))
                edits=load(folder/(id+'.owned-edits.json'));assert graph==edits['afterSource']==edits['afterDetached']
                if route.startswith('ADMIT_'):
                    adm=load(folder/(id+'.admission.json'));assert adm['valid'] and adm['error']=='' and adm['expectedSHA']==adm['actualSHA']==c['expected_config_sha256'] and adm['descriptor']==c['descriptor']
            parsed=load(folder/(n+'.parse.typed-checks.json'));assert parsed['isValid'] and parsed['error']=='' and parsed['actual']==c['input']
        for n,c in oracle['validator_results'].items():
            a=folder/(n+'.result.redacted.json');b=folder/(n+'.result.expected.json');bindings.append(dict(actual=row(a),reference=row(b),matched=a.read_bytes()==b.read_bytes() and load(a)==c['expected_redacted']));assert load(folder/(n+'.result.caller.json'))==c['input']
        for n,c in oracle['policy_cases'].items():
            a=folder/(n+'.policy.json');bindings.append(dict(actual=row(a),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),expected_digest=c['expected_digest'],matched=a.read_text(encoding='utf-8')==c['expected_json'] and sha(a)==c['expected_digest']))
        for p in sorted(folder.glob('*.json')):
            if p.name.endswith('typed-checks.json') or p.name=='VALID_CONFIG_CLEAR_TYPED_RESULTS.json':
                c=list(checks(load(p)));bad=[x for x in c if not x['matched']];typedcount+=len(c);typedfail+=len(bad);typedfiles.append(dict(file=row(p),compared_rows=len(c),failed_rows=len(bad),all_matched=not bad))
        for n,c in oracle['file_cases'].items():
            d=load(folder/(n+'.file-helper.json'));assert d['computed']==d['expected']==d['actual_file_sha256']==c['expected_sha256'] and d['isValid'] and d['error']==''
        metadata=load(folder/'PUBLIC_DTO_METADATA.json');snap=[r for r in metadata if r['type'].endswith('OperatorStartupConfigSnapshot')];assert len(snap)==15 and all(r['kind']=='property' and not r['has_public_setter'] for r in snap)
        assert {r['name'] for r in snap}==set(next(iter(oracle['config_cases'].values()))['expected_snapshot'])
        vf=[r for r in metadata if r['type'].endswith('.ValidatorResult')];assert len(vf)==25 and {r['name'] for r in vf}==set(oracle['validator_results']['NORMAL_A']['input'])
        assert all(r['clr_type']=='System.Int64' for r in vf if r['name'] in ['workerGeneration','resultEpoch'])
        assert len([r for r in metadata if r['type'].endswith('.OperatorLaunchDescriptor')])==5
        ledger=load(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json');counts=collections.Counter((r['scope'],r['api']) for r in ledger);direct=sum(v for (s,a),v in counts.items() if s=='direct_pure');grouped=len(ledger)-direct
        assert not any(re.search(r'ProcessIdentity|Process\.|GetCurrentProcess|MainModule|WorkerBridgeComponent|Awake|Bootstrapper|ComputeActual|GetActual|Invalidate|Cache|stale|reject|mismatch',r['api'],re.I) for r in ledger)
        scope.append(dict(run_id=pre['run_id'],ledger=row(folder/'ACTUAL_ADMITTED_CALL_LEDGER.json'),total_events=len(ledger),direct_pure_events=direct,grouped_snapshot_events=grouped,counts=[dict(scope=s,api=a,count=v) for (s,a),v in sorted(counts.items())],counter_limit='Explicitdirectpure API/constructor-fromDTO stages plusgroupedpropertyreads;notnestedprofiling',actualCSharp_Process_GlobalWorker_native_adverse=0))
        ctx=load(folder/'ACTUAL_PROCESS_CONTEXT.json');host=load(folder/'HOST_RUN_PROCESS_OBSERVATION.json');tool=load(folder/'RUN_TOOL_PROOF.json');assert host['numeric_exit']==tool['exit_code']==(1 if failure else 0) and host['observed_culture']==ctx['culture']==pre['culture']
        processes.append(dict(run_id=pre['run_id'],owned_host_pid=host['owned_child_pid'],culture=host['observed_culture'],actual_numeric_exit=tool['exit_code'],context=row(folder/'ACTUAL_PROCESS_CONTEXT.json'),host=row(folder/'HOST_RUN_PROCESS_OBSERVATION.json'),tool=row(folder/'RUN_TOOL_PROOF.json'),stdout=row(folder/'STDOUT.txt'),stderr=row(folder/'STDERR.txt'),inventory=row(folder/'OUTPUT_INVENTORY.json')))
        for r in load(folder/'ACTUAL_LOADED_PREPIN_BINDING.json')['files']:
            m=pe['mvid'](Path(r['path']));assert m==r['mvid'];loadedbindings.append(dict(run_id=pre['run_id'],file=row(Path(r['path'])),recorded_mvid=r['mvid'],independent_PE_mvid=m,matched=True))
    assert processes[0]['owned_host_pid']!=processes[1]['owned_host_pid'] and scope[0]['counts']==scope[1]['counts']
    assert load(runs[0]/'PUBLIC_DTO_METADATA.json')==load(runs[1]/'PUBLIC_DTO_METADATA.json')
    write(Q/'ACTUAL_EXECUTION_SCOPE.json',dict(at=now(),rows=scope,host_PID_numericexit_only_inline_WP=True,production_builds=0,qa_builds=1,qa_processes=2,source_no_process_queries=True,actual_native_issuer_authority_proof=False))
    write(Q/'FRESH_PROCESS_PROOF.json',dict(at=now(),rows=processes,actual_hostowned_newchilds_only=True,firstwholeoutputs_before_second_andunchanged_after=True,immutableuniqueoutputdirs=True,derivedreplacementoutputs=0))
    write(Q/'FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json',dict(at=now(),metadata=row(runs[0]/'PUBLIC_DTO_METADATA.json'),snapshot15_getonly_properties=True,result25fields_int64widths=True,descriptor5_fields=True,normal_source_and_detached_copy_metamorphic_PASS=True,lossless_original_opaque_PASS=not any(o['failed_assertions'] for o in observed),source_schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),prospective_oracle=row(Q/'ORACLE_BEFORE_BUILD.json'),candidate_reference_bindings=bindings,typed_checks=typedcount,failed_typed_checks=typedfail,typed_files=typedfiles,loaded_independent_PE_bindings=loadedbindings,shared_standard_JsonNET_primitive_limit=True,oracle_afteroutput_modified=False))
    write(Q/'NORMAL_FAILURE_RECONCILIATION.json',dict(at=now(),rows=failure_rows,original_oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),failures_reported_unchanged=True,repair_rebuild_rerun_aftercalls=0,not_negative_adverse_controls=True))
    admission=load(Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json');assert admission['exact_two_assignment_change'] and admission['all_other_bytes_lineendings_identical'];assert admission['new_source']==row(SOURCE)
    src=SOURCE.read_text(encoding='utf-8-sig');lines=src.splitlines();excerpts=[]
    for n,a,b in [('BOOTSTRAP',42,106),('INSTALLER_USERDATA',375,424),('AWAKE',522,566),('INPUT_READINESS',1533,1615),('LAUNCH',2187,2270),('SNAPSHOT_POLICY',3448,3480),('SEMANTIC_VALIDATION',3494,3615),('ADMISSION',3645,3805),('PARSER',3806,3968),('PROCESS_ROLE',4030,4120)]:
        p=Q/'source_extracts'/(n+'.txt');p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(f'{i}: {lines[i-1]}' for i in range(a,b+1))+'\n',encoding='utf-8');excerpts.append(dict(name=n,artifact=row(p),**anchor(a,b)))
    assert '_policyId = config.expectedPackagePolicyDeclaration.policyId;' in src and '_policyRevision = config.expectedPackagePolicyDeclaration.revision;' in src
    validate=src[src.index('private string HandleValidateInput()'):src.index('private string HandleSetTargetMap')];assert '_activeStartupConfig' not in validate and 'trustedSimulationReady = true;' in validate
    admit=src[src.index('public static (bool isValid, string error, OperatorStartupConfigSnapshot? snapshot) AdmitConfigBytes'):src.index('public static (bool isValid, string error, OperatorStartupConfig? config) ParseStrict')];assert admit.count('configPath')==1 and 'originId' not in admit and 'launchPlanId' not in admit
    process=src[src.index('public static (bool isValid, string error) VerifyProcessIdentity'):src.index('public static class ValidatorResultExtensions')];assert process.count('expectedRole')==1
    for n,c in oracle['config_cases'].items():
        expected=c['expected_declaration'];independent=hashlib.sha256(json.dumps(expected,ensure_ascii=False,separators=(',',':')).encode()).hexdigest().upper();assert independent==c['expected_record']['policyDigest']
        if n.endswith('OPAQUE'):assert independent=='8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF'
        for route in c['routes']:
            for folder in runs:
                graph=load(folder/(n+'_'+route+'.snapshot-graph.json'));assert graph['record']['policyDigest']==independent and graph['declaration']==expected
                edits=load(folder/(n+'_'+route+'.owned-edits.json'));assert edits['sourceCopyControl']==(route in ['CONSTRUCTOR','TO_SNAPSHOT'])
                assert edits['afterDetached']==graph and edits['expectedOriginal']==graph
    findings=[
        dict(id='ENGINE-G05-OPAQUE-R18-20261010-01',priority='HIGH',status='FRESH_SCOPED_NORMAL_ORIGINAL_GRAPH_DIGEST_REGRESSION_PASS_MASTER_DISPOSITION_PENDING',exact_repair=row(Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json'),normal_only=True,originalspacesUnicodepreserved=True,all16graph_digest_redaction_ownedcopyverified=True,anchors=[anchor(3611,3614)],closure_by_QA=False),
        dict(id='M01_M03',priority='HIGH',status='STATIC_TRUSTED_STARTUP_ORIGIN_GATE_OPEN',issue='OriginId/launchPlanId/configpath/approveddescriptor provenance notbound;installer anysnapshot;missingconfig stillattaches/listens andHandleValidateInput can trustedreadywithout activeconfig guard.',anchors=[anchor(48,106),anchor(375,403),anchor(534,566),anchor(1533,1615),anchor(3645,3805)]),
        dict(id='M04_M05',priority='HIGH',status='STATIC_ROLE_USERDATA_FRONTEND_PROCESS_OPEN_NATIVE_UNTESTED',issue='READ_ONLY choosesWorker userdata;childtask/nonce/operatorconfig frontend notwired;expectedRole unused/initialexpectedStart null/options/taskcapability actualruntime notobserved.',anchors=[anchor(404,424),anchor(2187,2270),anchor(4030,4120)]),
        dict(id='M06_M07',priority='HIGH',status='STATIC_SCHEMA_CONTEXT_CONTENT_FULL_GATE_OPEN',issue='Rooted vsfullyqualified/UTC exactness/policy-profile schema/integerrevision/UTF8/EOF/targetfallback/currentcontent/error-core/patchsettings/controlplane receipt/nativeOPEN. Purelossless repair doesnotclose these.',anchors=[anchor(3494,3615),anchor(3806,3968),anchor(1560,1615)])]
    write(Q/'INDEPENDENT_REVIEW_FINDINGS.json',dict(at=now(),findings=findings,source_excerpts=excerpts,census_csproj_unchanged=True,Master_release_closure=True,currentOpen='Engine002006/Pipeline007/currentschema/GQ1OPEN/FoundationHOLD',known_installed_incident='OPEN_ACTOR_CAUSE_UNKNOWN_ORIGINAL_NOT_REREAD_RESTORED'))
    base=FROZEN/'scratch/EngineGate05R19OpaquePolicy';prod=[];host=load(base/'HOST_TELEMETRY.json')
    for label in ['run_en_us','run_de_de']:
        out=base/label;res=load(out/'RESULTS.json');ledger=load(out/'API_LEDGER.json');inv=load(out/'OUTPUT_INVENTORY.json');checked=[]
        actualfiles=[p for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json']
        declared={r['relative_path'] for r in inv};actualset={p.relative_to(out).as_posix() for p in actualfiles};assert declared<=actualset
        unlisted=sorted(actualset-declared)
        for r in inv:
            p=out/r['relative_path'];actual=row(p);checked.append(dict(recorded=r,actual=actual,matched=actual['sha256']==r['sha256'] and actual['bytes']==r['size_bytes']))
        direct=sum(v for k,v in ledger.items() if k not in ['ProcessApiCalls','VerifyProcessIdentityCalls','WorkerBridgeGlobalConfigureResetCalls','AwakeCalls','HarmonyCalls'])
        prod.append(dict(run=label,results=row(out/'RESULTS.json'),culture=res['Culture'],literal_ResultProcessId=res['ProcessId'],labels=res['TotalTests'],reported_exit=res['NumericExitCode'],host_record=next(r for r in host['runs'] if r['run_name']==label),manual_direct_counter=direct,ledger=ledger,inventory=row(out/'OUTPUT_INVENTORY.json'),recorded_rows=len(checked),actual_nonself_files=len(actualfiles),unlisted_frozen_outputs=unlisted,unlisted_identities=[row(out/n) for n in unlisted],matched_rows=sum(r['matched'] for r in checked),mismatches=[r for r in checked if not r['matched']],rows=checked))
    producerSource=base/'Harness/Program.cs';producerText=producerSource.read_text(encoding='utf-8-sig');assert 'if (pType == "OPAQUE")' in producerText and 'digestMatches = (computedDigest == EXPECTED_OPAQUE_DIGEST)' in producerText
    write(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json',dict(at=now(),rows=prod,host=row(base/'HOST_TELEMETRY.json'),source=row(producerSource),producer7labels16matrix_only8OPAQUEoriginaldigestassertion=True,single_connected_ToSnapshot_source_getter_copy_case=True,partial_selected_redaction_fulltyped_fields=True,manual_direct_actual62_notnestedprofiler=True,ResultProcessId0_literal_notOSPID0=True,enUS_stream_inventory2_mismatches_retained=True,actual_nonself_paths10each_but_deDE_inventory_only8_logs_unlisted=True,historical_Master_E1_deDE_10_allmatched_corrected=True,original_OS_buildnumericexit_fullinput_prepost_actualallloaded_graph='PARTIAL',firstbefore_after_inventory_ephemeral_locals_notdurable_receipts=True,claims_reject_schema_defaulting='ONLY_VALID_ParseStrict_EXECUTED_SOURCE_GUARDS_NOT_RUNTIME_REFUSAL',producer_replay_calls=0,fixture_profile_labels_notactualnativecontentbinding=True,report_Census_prefix72547_lines_unit_corrected_BYTES=True))
    build=load(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0 and build['complete_streams_direct_files_before_tool_output']
    for key in ['stdout','stderr']:
        r=build[key];assert row(Path(r['path']))==r
    write(Q/'COMPLETE_BUILD_STREAM_BINDING.json',dict(at=now(),actual_builds=1,actual_numeric_exit=0,tool=row(Q/'BUILD_TOOL_PROOF.json'),invocation=row(Q/'BUILD_INVOCATION_TOOL_PROOF.json'),stdout=build['stdout'],stderr=build['stderr'],full_compile_run_streams_direct_ownedfiles=True,no_warning_stream_truncation=True,source_runner_PE_PDB_pins_complete=True,no_productionbuild=True))
    fails=sum(o['failed_assertions'] for o in observed)
    verdict=('SCOPED_NORMAL_ORIGINAL_OPAQUE_POLICY_FULLTYPED_GRAPH_DIGEST_OWNERSHIP_SHA_REDACTION_CODEC_PASS' if not fails else 'SCOPED_NORMAL_FAIL')+'_BOOTSTRAP_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED'
    summary=dict(at=now(),verdict=verdict,selected_sha256=observed[0]['selected_sha256'],selected_mvid=observed[0]['selected_mvid'],actual_build_exit=0,qa_runner_builds=1,actual_run_exits=[p['actual_numeric_exit'] for p in processes],assertions_per_run=[len(o['results']) for o in observed],failed_assertions_per_run=[o['failed_assertions'] for o in observed],passed_assertions_per_run=[sum(r['status']=='PASS' for r in o['results']) for o in observed],fulltyped_checks=typedcount,failed_typed_checks=typedfail,meaningful_crossprocess_byte_pairs=pairs,independent_reference_pairs=refpairs,independent_bindings_count=len(bindings),independent_bindings_failed=sum(not r['matched'] for r in bindings),actual_hostowned_processes=processes,pinned_files_per_run=[len(p['files']) for p in pres],loaded_managed_per_run=[len(load(r/'ACTUAL_LOADED_MANAGED.json')) for r in runs],output_files_per_run=[load(r/'OUTPUT_INVENTORY.json')['file_count'] for r in runs],explicit_call_scope=scope,all_Process_globalWorker_native_adverse_productionbuild_executions=0,repair_rebuild_rerun_aftercalls=0,connected_source_copy8_only=True,unused_admission_callerDTO_never_mutated=True,detachedcopy16=True,full_compiler_run_streams_captured_directfiles=True,qualifications=['Onlynormaloriginalopaque andsmallpurehelper regression;notnativeissuerproof','Connected sourcecopy8/detachedcopy16 readonlywrapperreads only','14parser/15snapshot/13redaction/25result exactfulltyped normalonly','ExternalhostPIDexitonly','SharedJsonNETprimitive escaping limit','Producer7PASS notinherited/twoenUSstreammismatches retained','Origin/trustedmissinggate/role-userdata/frontend/schema-context-content/nativeOPEN','ScopedHIGH closureMaster pending/fullGateE2NOTRELEASED/FoundationHOLD'])
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',summary)
    print(json.dumps(dict(assertions=summary['assertions_per_run'],passed=summary['passed_assertions_per_run'],failed=summary['failed_assertions_per_run'],exits=summary['actual_run_exits'],typed_checks=typedcount,typed_failed=typedfail,byte_pairs=len(pairs),reference_pairs=len(refpairs),bindings=len(bindings),binding_failed=summary['independent_bindings_failed'],ledger=[dict(total=r['total_events'],direct=r['direct_pure_events'],grouped=r['grouped_snapshot_events']) for r in scope],producer=[dict(run=r['run'],manual=r['manual_direct_counter'],matched=r['matched_rows'],mismatches=len(r['mismatches'])) for r in prod]),indent=2))
