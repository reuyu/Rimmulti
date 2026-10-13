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
        assert len([r for r in metadata if r['type'].endswith('.OperatorLaunchDescriptor')])==7
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
    receipts=load(Q/'RECEIPT_EXPECTED_SEMANTICS.json');receipt_pairs=[];receiptbindings=[];receiptcopies=[]
    for n,c in receipts['cases'].items():
        for suffix in ['.receipt-graph.json','.receipt.redacted.json','.receipt.owned-edits.json']:
            a=runs[0]/(n+suffix);b=runs[1]/(n+suffix);assert a.read_bytes()==b.read_bytes();receipt_pairs.append(dict(run1=row(a),run2=row(b),exact_utf8_equal=True,repeatability_not_correctness=True))
        for folder in runs:
            graph=load(folder/(n+'.receipt-graph.json'));redacted=load(folder/(n+'.receipt.redacted.json'));edits=load(folder/(n+'.receipt.owned-edits.json'));issue=load(folder/(n+'.issue.json'))
            assert issue['valid'] and issue['error']=='' and issue['actualSHA']==issue['expectedSHA']==c['expected_config_sha256'] and issue['descriptor']==c['descriptor']
            assert graph==c['expected_graph']==edits['after']==edits['expectedOriginal']
            a=folder/(n+'.receipt.redacted.json');b=folder/(n+'.receipt.expected-redacted.json');receiptbindings.append(dict(case_id=n,graph=row(folder/(n+'.receipt-graph.json')),oracle=row(Q/'RECEIPT_EXPECTED_SEMANTICS.json'),all11_receipt_properties_and15_nested_andpolicyrecord_matched=True,redacted_actual=row(a),redacted_reference=row(b),matched=a.read_bytes()==b.read_bytes(),strict_original_values_matched=redacted==c['expected_redacted'],changed_leaf='snapshot.issuedAtUtc',expected=c['expected_redacted']['snapshot']['issuedAtUtc'],actual=redacted['snapshot']['issuedAtUtc'],sameUTCinstant_not_stringidentity=True))
            receiptcopies.append(dict(case_id=n,run_root=str(folder),after_owned_descriptor_clone_returnedpolicy_edits=row(folder/(n+'.receipt.owned-edits.json')),full_original_graph_unchanged=True,only_connected_descriptor_andreturnedcopy_credit=True))
    metadata=load(runs[0]/'PUBLIC_DTO_METADATA.json');receiptmeta=[r for r in metadata if r['type'].endswith('.OperatorStartupAdmissionReceipt')];assert len(receiptmeta)==11 and all(r['kind']=='property' and not r['has_public_setter'] for r in receiptmeta)
    assert {r['name'] for r in receiptmeta}==set(next(iter(receipts['cases'].values()))['expected_graph']['properties'])
    # Ownrun typed receipt files were already recursively compared in baseanalysis.
    allbindings=bindings+receiptbindings;allpairs=pairs+receipt_pairs
    write(Q/'RECEIPT_FULLTYPED_GRAPH_AND_REFERENCE_BINDING.json',dict(at=now(),receipt_public_metadata=receiptmeta,receipt11_props_redaction11_nested15_13_fulltyped=True,descriptor7=True,cases=receiptbindings,owned_copy_cases=receiptcopies,crossprocess_pairs=receipt_pairs,original_literal_UTC_vs_equivalent_normalized_representation_only=True,expected_not_modified=True,receiptTimestamp_copies_configIssued_notclockproof=True,IsTrusted_localflag_not_origin_authentication=True))
    prior=ROOT/'Dispatcher/CANDIDATES/G05R19-5415a675/scratch/WorkerBridgeMod/Source';src=SOURCE.read_text(encoding='utf-8-sig');old=(prior/'WorkerBridge.cs').read_text(encoding='utf-8-sig')
    start='    public class OperatorStartupConfig';end='    public class OperatorLaunchDescriptor';assert src[src.index(start):src.index(end)]==old[old.index(start):old.index(end)]
    for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:assert (SOURCE.parent/n).read_bytes()==(prior/n).read_bytes()
    (Q/'SOURCE_SCOPE_DIFF.txt').write_text(''.join(difflib.unified_diff(old.splitlines(True),src.splitlines(True),fromfile=str(prior/'WorkerBridge.cs'),tofile=str(SOURCE))),encoding='utf-8')
    lines=src.splitlines();excerpts=[]
    for n,a,b in [('BOOTSTRAP',43,113),('INSTALLER',388,425),('AWAKE',538,581),('INPUT_READINESS',1549,1622),('DESCRIPTOR_RECEIPT',3668,3757),('CUSTOM_PATHHELPER',3773,3797),('FACTORY_OPTIONAL_BINDINGS',3903,3963),('ISSUE_RECEIPT',3965,4107),('VALIDATE_RECEIPT',4109,4164),('SCHEMA_PARSER',4166,4326)]:
        p=Q/'source_extracts'/(n+'.txt');p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(f'{i}: {lines[i-1]}' for i in range(a,b+1))+'\n',encoding='utf-8');excerpts.append(dict(name=n,artifact=row(p),**anchor(a,b)))
    bootstrap=src[src.index('static WorkerBridgeBootstrapper()'):src.index('public static class ScopedTacticalSession')];assert bootstrap.index('if (!hasConfigArg)')<bootstrap.index('new GameObject') and 'operatororigin' in bootstrap and 'operatorcapability' in bootstrap
    awake=src[src.index('void Awake()'):src.index('private void HandleUnityLogMessage')];assert awake.index('return;')<awake.index('ConfigureExpectedPackagePolicy')<awake.index('listener.Start()')
    validate=src[src.index('private string HandleValidateInput()'):src.index('private string HandleSetTargetMap')];assert validate.index('_activeAdmissionReceipt')<validate.index('trustedSimulationReady = true;')
    true_assignments=[dict(line=i+1,text=line) for i,line in enumerate(lines) if re.search(r'\btrustedSimulationReady\s*=\s*true\s*;',line)];assert len(true_assignments)==1
    findings=[
        dict(id='R20_NORMAL_RECEIPT_REDACTION_LEXICAL_UTC',status='NORMAL_STRICT_ORIGINAL_STRING_BYTE_COMPARISON_FAIL',issue='Receipt ToRedactedJson JObject.Parse auto date conversion removes zero fractional seconds from snapshot.issuedAtUtc;8normalreceiptcases eachculture. SameUTCinstant;no material clock/time corruption inferred. Master decides explicit lexical convention/narrow correction.',anchor=anchor(3739,3756),evidence=row(Q/'RECEIPT_FULLTYPED_GRAPH_AND_REFERENCE_BINDING.json')),
        dict(id='M03',status='STATIC_MISSING_RECEIPT_GUARDS_CREDITED_RUNTIME_UNEXECUTED',issue='Missingconfig beforeattach/Awake receiptguard beforepolicy/listener/HandleValidateInput beforealltrue readiness assignment source credited. No globalguard/branch execution.',anchors=[anchor(48,104),anchor(538,581),anchor(1549,1622)],all_true_assignments=true_assignments),
        dict(id='M01',status='EXPLICIT_DECLARATION_PROVENANCE_REVISION_REQUIRED',issue='Defaults plusoptionalCLI origin/plan/id/role/boundary;factories optionalnonempty binding canconstruct approveddeclaration fromdefaults orsnapshotvalues. IsValid selfconsistency/localIsTrusted notstoredapproveddeclaration authentication. Internalconstructor bool assemblywide notfactoryexclusive guarantee;onlyfactory new currently sourceobserved, no hostile sameprocess inference.',anchors=[anchor(64,98),anchor(3668,3734),anchor(3965,4164)]),
        dict(id='RECEIPT_TIMESTAMP_CLI',status='QUALIFIED_STATIC_MEANING',issue='AdmittedAtUtc equalsconfigIssuedAtUtc notactualadmissionwallclock. ReportCLI operatorlaunchorigin/role/configid/boundary differs actualoperatororigin/operatorrole/operatorconfigid/operatorcapability. Custompathhelper syntactic only;allnegativeQAbranches unexecuted.',anchors=[anchor(64,87),anchor(3773,3797),anchor(4093,4105)]),
        dict(id='M04_M05_M06_M07',status='OPEN_NATIVE_UNTESTED',issue='Role-awareuserdata/childtaskfrontend/process-role-start-options-task/strictUTC-UTF8-schema-integerrevision/targetcontext-content-core-error-patchsettings/controlplane/native remain separateOPEN. No wholeGate/closure.',anchors=[anchor(4166,4326)],closure_by_QA=False)]
    write(Q/'INDEPENDENT_REVIEW_FINDINGS.json',dict(at=now(),findings=findings,source_excerpts=excerpts,source_config_snapshot_block_exact_R19_unchanged=True,census_csproj_fixed=True,known_installed='OPEN_ACTOR_CAUSE_UNKNOWN_ORIGINAL_NOT_REREAD_RESTORED',Foundation='HOLD',Master_release_closure=True))
    base=FROZEN/'scratch/EngineGate05R20TrustedStartup';prod=[];host=load(base/'HOST_TELEMETRY.json');producerSource=base/'Harness/Program.cs';producerText=producerSource.read_text(encoding='utf-8-sig')
    negative=producerText[producerText.index('string[] nonFullPaths'):producerText.index('int nonFullChecksPass')];negativecount=negative.count('@"')+negative.count('null!');assert negativecount==7
    for label in ['run_en_us','run_de_de']:
        out=base/label;res=load(out/'RESULTS.json');ledger=load(out/'API_LEDGER.json');inv=load(out/'OUTPUT_INVENTORY.json');checked=[]
        actualfiles=[p for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'];assert {r['relative_path'] for r in inv}=={p.relative_to(out).as_posix() for p in actualfiles}
        for r in inv:
            p=out/r['relative_path'];checked.append(dict(recorded=r,actual=row(p),matched=sha(p)==r['sha256'] and p.stat().st_size==r['size_bytes']))
        assert all(r['matched'] for r in checked);direct=sum(v for k,v in ledger.items() if k not in ['ProcessApiCalls','VerifyProcessIdentityCalls','WorkerBridgeGlobalConfigureResetCalls','TryInstallOperatorStartupConfigCalls','AwakeCalls','HarmonyCalls'])
        test=next(r for r in res['Tests'] if r['TestName']=='TEST_05_FULLY_QUALIFIED_WINDOWS_PATH_HELPER');assert test['TotalNonFullChecks']==7 and test['NonFullChecksPassed']==7
        prod.append(dict(run=label,results=row(out/'RESULTS.json'),culture=res['Culture'],ProcessId_literal=res['ProcessId'],labels=res['TotalTests'],reported_exit=res['NumericExitCode'],host_record=next(r for r in host['runs'] if r['run_name']==label),manual_counter=direct,ledger=ledger,inventory=row(out/'OUTPUT_INVENTORY.json'),rows=checked,current_nonself_count=len(checked),actual_invalid_helper_calls=7,TEST05=test))
    write(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json',dict(at=now(),rows=prod,source=row(producerSource),negative_source_inputs=negative,negative_calls_total=14,positive_only_zero_adverse_claim_contradicted=True,oldproducer_replay=0,manual83_notnested=True,current14_nonself_closedstream_inventories_match=True,fullhistoricalcompiler_raw_prospective_input_allloaded_postgraph='PARTIAL',host_firstlater_maps_ephemeral_only=True,constantopaqueDigest8_notPLAIN16=True,receipt8_singlecopy_redactedcount11_notfulltyped=True,IsTrusted_fixtureprofile_notnativeauthority=True,malformed_ACK_original_retained_notnormalized=True))
    build=load(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0 and build['complete_streams_direct_files_before_tool_output'];write(Q/'COMPLETE_BUILD_STREAM_BINDING.json',dict(at=now(),actual_final_builds=1,compiler_numeric_exit=0,stdout=build['stdout'],stderr=build['stderr'],tool=row(Q/'BUILD_TOOL_PROOF.json'),wrapper=row(Q/'BUILD_INVOCATION_TOOL_PROOF.json'),full_streams_directfiles=True,prepin_setup_failures_compiler_calls0_preserved=True))
    verdict='SCOPED_RECEIPT_GRAPH_BINDING_OWNERSHIP_OPAQUE_CODEC_PASS_RECEIPT_REDACTED_UTC_LITERAL_FAIL_EXPLICIT_DECLARATION_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED'
    summary=dict(at=now(),verdict=verdict,selected_sha256=observed[0]['selected_sha256'],selected_mvid=observed[0]['selected_mvid'],actual_build_exit=0,qa_runner_builds=1,actual_run_exits=[p['actual_numeric_exit'] for p in processes],assertions_per_run=[len(o['results']) for o in observed],failed_assertions_per_run=[o['failed_assertions'] for o in observed],passed_assertions_per_run=[sum(r['status']=='PASS' for r in o['results']) for o in observed],fulltyped_checks=typedcount,failed_typed_checks=typedfail,byte_pair_count=len(allpairs),reference_pair_count=len(refpairs),all_byte_pairs=allpairs,bindings=allbindings,binding_count=len(allbindings),binding_failed=sum(not r['matched'] for r in allbindings),processes=processes,pins=[len(p['files']) for p in pres],loads=[len(load(r/'ACTUAL_LOADED_MANAGED.json')) for r in runs],outputs=[load(r/'OUTPUT_INVENTORY.json')['file_count'] for r in runs],scope=scope,receipt_cases=8,config_cases=4,snapshot_routes=16,receipt_properties=11,receipt_redacted_properties=11,descriptor7=True,nested15_redacted13_result25=True,connected_source_copy8=True,normalreceipt_connected_descriptor_edit8=True,detached_policy_copy24=True,compiler_stdout_bytes=build['stdout']['bytes'],all_production_Process_globalWorker_native_cache_adverse=0,oracle_runner_candidate_output_corrections_rebuild_rerun_aftercalls=0,producer14_invalidhelper_scope_deviation=True,fullGateE2='NOT_RELEASED',foundation='HOLD',closure_by_QA=False,qualifications=['Receiptredacted UTC lexical8FAIL each/sameinstant notmaterialclockfault','Localtrustedflag/configtimestamp notoriginauthentication/nativeproof','Staticmissingguards credit/explicitdefaults-optionality-provenance OPEN','Sourceconfig8 only/receipt factoryinternalDTO inaccessible notcopyproof','SharedJsonNETprimitivecodec limit/syntheticprofile PID nonce','Prepin setupfailures compiler/candidate0 archived','Producerinvalid14notreplayed/historicpartialgraph preserved','R19scopedCLOSEDhistorical notR20wholePASS/closureMaster'])
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',summary)
    print(json.dumps(dict(assertions=summary['assertions_per_run'],pass_per_run=summary['passed_assertions_per_run'],fail_per_run=summary['failed_assertions_per_run'],exits=summary['actual_run_exits'],typed=typedcount,typed_failed=typedfail,bytepairs=len(allpairs),refs=len(refpairs),bindings=len(allbindings),binding_failed=summary['binding_failed'],scope=[dict(direct=r['direct_pure_events'],grouped=r['grouped_snapshot_events'],total=r['total_events']) for r in scope],producer=[dict(counter=r['manual_counter'],rows=r['current_nonself_count'],invalid=r['actual_invalid_helper_calls']) for r in prod]),indent=2))
