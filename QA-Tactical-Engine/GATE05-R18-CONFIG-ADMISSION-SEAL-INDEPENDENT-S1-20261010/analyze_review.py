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
    write(Q/'FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json',dict(at=now(),metadata=row(runs[0]/'PUBLIC_DTO_METADATA.json'),snapshot15_getonly_properties=True,result25fields_int64widths=True,descriptor5_fields=True,normal_source_and_detached_copy_metamorphic_PASS=True,lossless_original_opaque_PASS=False,source_schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),prospective_oracle=row(Q/'ORACLE_BEFORE_BUILD.json'),candidate_reference_bindings=bindings,typed_checks=typedcount,failed_typed_checks=typedfail,typed_files=typedfiles,loaded_independent_PE_bindings=loadedbindings,shared_standard_JsonNET_primitive_limit=True,oracle_afteroutput_modified=False))
    write(Q/'NORMAL_FAILURE_RECONCILIATION.json',dict(at=now(),rows=failure_rows,original_oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),failures_reported_unchanged=True,repair_rebuild_rerun_aftercalls=0,not_negative_adverse_controls=True))
    prior=ROOT/'Dispatcher/CANDIDATES/G05R17-57163c71/scratch/WorkerBridgeMod/Source';assert sha(CENSUS)==sha(prior/'EngineHostCensus.cs') and sha(SOURCE.parent/'WorkerBridge.csproj')==sha(prior/'WorkerBridge.csproj')
    src=SOURCE.read_text(encoding='utf-8-sig');lines=src.splitlines();(Q/'SOURCE_SCOPE_DIFF.txt').write_text(''.join(difflib.unified_diff((prior/'WorkerBridge.cs').read_text(encoding='utf-8-sig').splitlines(True),src.splitlines(True),fromfile=str(prior/'WorkerBridge.cs'),tofile=str(SOURCE))),encoding='utf-8')
    excerpts=[]
    for n,a,b in [('BOOTSTRAP',42,106),('INSTALLER',375,404),('USERDATA',404,424),('AWAKE',522,566),('INPUT_READINESS',1533,1615),('LAUNCH',2187,2270),('SNAPSHOT_POLICY',3448,3480),('SEMANTIC_VALIDATION',3494,3615),('ADMISSION',3645,3805),('PARSER',3806,3968),('PROCESS_ROLE',4030,4120)]:
        p=Q/'source_extracts'/(n+'.txt');p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(f'{i}: {lines[i-1]}' for i in range(a,b+1))+'\n',encoding='utf-8');excerpts.append(dict(name=n,artifact=row(p),**anchor(a,b)))
    validate=src[src.index('private string HandleValidateInput()'):src.index('private string HandleSetTargetMap')];assert '_activeStartupConfig' not in validate and 'trustedSimulationReady = true;' in validate
    admit=src[src.index('public static (bool isValid, string error, OperatorStartupConfigSnapshot? snapshot) AdmitConfigBytes'):src.index('public static (bool isValid, string error, OperatorStartupConfig? config) ParseStrict')]
    assert admit.count('configPath')==1 and 'originId' not in admit and 'launchPlanId' not in admit
    process=src[src.index('public static (bool isValid, string error) VerifyProcessIdentity'):src.index('public static class ValidatorResultExtensions')];assert process.count('expectedRole')==1
    assert '_policyId = config.expectedPackagePolicyDeclaration.policyId.Trim();' in src and '_policyRevision = config.expectedPackagePolicyDeclaration.revision.Trim();' in src
    findings=[
        dict(id='M01',status='STATIC_CREDIT_PLUS_AUTHORITY_GAP',priority='HIGH',issue='Publicglobal Configure/Resetremoved;internalone-time lock credits ownership. Installer acceptsanysnapshot,not unforgeable admissionresult;full origin/launchPlan/configPath approvedplan binding absent.',anchors=[anchor(375,403),anchor(3645,3805)]),
        dict(id='M02',status='POSITIVE_NORMAL_OPAQUE_LOSSLESS_FAIL',priority='HIGH',issue='FixedCensus opaque policyId/revision losslesscontract violated by snapshot Trim;bothroles/fourroutes/redaction/policyrecord digest allnormalcases. ParseStrict preservesoriginal. PackageID canonicalization is a separate contract.',anchors=[anchor(3611,3614),dict(source=row(CENSUS),first_line=1804,last_line=1844)],reproduction=row(Q/'NORMAL_FAILURE_RECONCILIATION.json')),
        dict(id='M03',status='STATIC_TRUSTED_READINESS_GAP',priority='HIGH',issue='Presentinvalidconfig returnsbeforecomponentattach,missingconfig warns thenattaches;Awake revoke followedlistener startup. HandleValidateInput noadmittedconfig guard andmay set trustedSimulationReady=true. Native refusal nottested.',anchors=[anchor(48,99),anchor(534,566),anchor(1533,1615)]),
        dict(id='M04',status='STATIC_ROLE_USERDATA_FRONTEND_OPEN',priority='HIGH',issue='SafeSaveData choosesWorkeruserdata alsoREAD_ONLY;role notconnectedtaskfrontend;--task-file/nonce childargs emitted butnoownedreceiverbootstrap. Childoperatorconfig/SHA/localapprovedplan/role/frontend notshown.',anchors=[anchor(404,424),anchor(2187,2270)]),
        dict(id='M05',status='STATIC_PROCESS_IDENTITY_QUALIFIED_NATIVE_UNTESTED',priority='HIGH',issue='Source checksactual imageSHA/PID/start nonempty/failures;expectedRole parameter unused,firstexpectedStart null/options-boundary proofs absent. HostQAchild telemetry notoperator/native authority.',anchors=[anchor(2253,2270),anchor(4030,4120)]),
        dict(id='M06',status='STATIC_SCHEMA_SEMANTICS_INCOMPLETE',priority='HIGH',issue='Required14/4fields unknown/duplicate/type guards sourcecredit;rooted notfullyqualified;DateTime.TryParse notexactUTC;profile merelynonempty;policy schema onlynonempty;revision acceptsinteger;packageitem semantics incomplete;Encoding.UTF8 replacement andtrailing document EOF strictness unproved. Noinvalid controls run.',anchors=[anchor(3494,3615),anchor(3741,3766),anchor(3806,3968)]),
        dict(id='M07',status='STATIC_GENERAL_GATE_CONTEXT_CONTENT_OPEN',priority='HIGH',issue='Target stableidentity/mapfallback,exacttask/result/receipt modes/controlplane parity/currentloadedcontent core/error/patchsettings/materialcontext/native obligations remain;purecodec/sourcecredit do notreplace MD125..132 independentruntimeproof.',anchors=[anchor(1560,1615)],native='UNTESTED_FULL_GATE_E2_NOT_RELEASED')]
    write(Q/'INDEPENDENT_REVIEW_FINDINGS.json',dict(at=now(),findings=findings,source_excerpts=excerpts,census_csproj_unchanged=True,opaque_identity_and_packageID_normalization_distinct=True,Master_release_closure=True,currentOpen='Engine002006/Pipeline007/currentschema/GQ1OPEN/FoundationHOLD',known_installed_incident='OPEN_ACTOR_CAUSE_UNKNOWN_ORIGINAL_NOT_REREAD_RESTORED'))
    base=FROZEN/'scratch/EngineGate05R18ConfigAdmissionSeal';mapping={str(Path(r['original_path'])).lower():Path(r['frozen_path']) for r in load(MAN)['files']};prod=[]
    host=load(base/'HOST_TELEMETRY.json')
    for label in ['run_en_us','run_de_de']:
        out=base/label;res=load(out/'RESULTS.json');ledger=load(out/'API_LEDGER.json');inv=load(out/'OUTPUT_INVENTORY.json');checked=[]
        for name,r in inv.items():
            p=mapping[str(Path(r['path'])).lower()];actual=row(p);checked.append(dict(name=name,recorded=r,actual=actual,self_entry=p.name=='OUTPUT_INVENTORY.json',matched=actual['sha256']==r['sha256'] and actual['bytes']==r['size']))
        direct=sum(v for k,v in ledger.items() if k not in ['ProcessApiCalls','VerifyProcessIdentityCalls','WorkerBridgeGlobalConfigureResetCalls','AwakeCalls','HarmonyCalls'])
        prod.append(dict(run=label,results=row(out/'RESULTS.json'),culture=res['Culture'],literal_ResultProcessId=res['ProcessId'],labels=res['TotalTests'],passed=res['PassedTests'],reported_exit=res['NumericExitCode'],host_record=next(r for r in host['runs'] if r['run_name']==label),manual_direct_counter=direct,ledger=ledger,inventory=row(out/'OUTPUT_INVENTORY.json'),recorded_rows=len(checked),matched_nonself=sum(r['matched'] for r in checked if not r['self_entry']),self_entries=[r for r in checked if r['self_entry']],rows=checked))
    write(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json',dict(at=now(),rows=prod,host=row(base/'HOST_TELEMETRY.json'),culture_correction_credited=True,manual17_notnestedprofiler=True,ResultProcessId0_literal_notOSPID0=True,current_nonself_SHA_size_credited=True,stale_enUS_self_entry_retained_unfixed=True,original_OS_buildnumericexit_fullinput_prepost_actualallloaded_graph='PARTIAL',firstbefore_after_inventory_ephemeral_locals_notdurable_receipts=True,claims_missing_unknown_duplicate_refusals='SOURCE_GUARDS_ONLY_NO_EXECUTED_ADVERSE_CONTROL',producer_replay_calls=0,fulltyped_partial_subset_roundtrip_notindependent_operator_authority=True))
    build=load(Q/'BUILD_TOOL_PROOF.json');truncated='truncated output' in build['output'];assert build['exit_code']==0
    write(Q/'BUILD_CAPTURE_LIMITATIONS.json',dict(at=now(),actual_builds=1,actual_numeric_exit=0,tool=row(Q/'BUILD_TOOL_PROOF.json'),raw=row(Q/'BUILD_RAW.txt'),compiler_warning_output_truncated_by_tool=truncated,full_compile_warning_stream_unavailable=True,recorded_original_token_count=build.get('original_token_count'),no_rebuild_to_recover_warning_output=True,source_runner_PE_PDB_pins_complete=True))
    verdict='SCOPED_NORMAL_OPAQUE_POLICY_LOSSLESS_FAIL_OWNERSHIP_FILESHA_REDACTION_LIMITED_CODEC_PASS_BOOTSTRAP_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED'
    summary=dict(at=now(),verdict=verdict,selected_sha256=observed[0]['selected_sha256'],selected_mvid=observed[0]['selected_mvid'],actual_build_exit=0,qa_runner_builds=1,actual_run_exits=[p['actual_numeric_exit'] for p in processes],assertions_per_run=[len(o['results']) for o in observed],failed_assertions_per_run=[o['failed_assertions'] for o in observed],passed_assertions_per_run=[sum(r['status']=='PASS' for r in o['results']) for o in observed],fulltyped_checks=typedcount,failed_typed_checks=typedfail,meaningful_crossprocess_byte_pairs=pairs,independent_reference_pairs=refpairs,independent_bindings_count=len(bindings),independent_bindings_failed=sum(not r['matched'] for r in bindings),actual_hostowned_processes=processes,pinned_files_per_run=[len(p['files']) for p in pres],loaded_managed_per_run=[len(load(r/'ACTUAL_LOADED_MANAGED.json')) for r in runs],output_files_per_run=[load(r/'OUTPUT_INVENTORY.json')['file_count'] for r in runs],explicit_call_scope=scope,all_Process_globalWorker_native_adverse_productionbuild_executions=0,repair_rebuild_rerun_aftercalls=0,qualifications=['NormalopaqueTrimFAIL retained;nooutputderivedoraclefix','Copyownership metamorphicPASS distinctfromlosslessFAIL','14parser fields/15snapshot props/25resultfields normalonly','ExternalhostPIDexitonly/notnativeissuerproof','Compilerwarningrawstreamtruncated;exit0 pinned PE/PDB sourcebinding preserved','Producer9PASS notinherited/currentinventoryselfgap retained','FullGateE2NOTRELEASED/FoundationHOLD/closureMaster'])
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',summary)
    print(json.dumps(dict(assertions=summary['assertions_per_run'],passed=summary['passed_assertions_per_run'],failed=summary['failed_assertions_per_run'],exits=summary['actual_run_exits'],typed_checks=typedcount,typed_failed=typedfail,byte_pairs=len(pairs),reference_pairs=len(refpairs),bindings=len(bindings),binding_failed=summary['independent_bindings_failed'],ledger=[dict(total=r['total_events'],direct=r['direct_pure_events'],grouped=r['grouped_snapshot_events']) for r in scope],buildraw_truncated=truncated),indent=2))
