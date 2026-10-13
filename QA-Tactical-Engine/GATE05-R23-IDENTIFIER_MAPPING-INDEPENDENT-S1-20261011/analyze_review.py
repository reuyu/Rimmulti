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
    write(Q/'FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json',dict(at=now(),metadata=row(runs[0]/'PUBLIC_DTO_METADATA.json'),snapshot15_getonly_properties=True,result25fields_int64widths=True,descriptor7_fields=True,normal_source_and_detached_copy_metamorphic_PASS=True,lossless_original_opaque_PASS=not any(o['failed_assertions'] for o in observed),source_schema=row(Q/'REFERENCE_DTO_SCHEMA.json'),prospective_oracle=row(Q/'ORACLE_BEFORE_BUILD.json'),candidate_reference_bindings=bindings,typed_checks=typedcount,failed_typed_checks=typedfail,typed_files=typedfiles,loaded_independent_PE_bindings=loadedbindings,shared_standard_JsonNET_primitive_limit=True,oracle_afteroutput_modified=False))
    write(Q/'NORMAL_FAILURE_RECONCILIATION.json',dict(at=now(),rows=failure_rows,original_oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),failures_reported_unchanged=True,repair_rebuild_rerun_aftercalls=0,not_negative_adverse_controls=True))
    receipts=load(Q/'RECEIPT_EXPECTED_SEMANTICS.json');receipt_pairs=[];receiptbindings=[];receiptcopies=[];utc_types=[]
    for n,c in receipts['cases'].items():
        for suffix in ['.receipt-graph.json','.receipt.redacted.json','.receipt.owned-edits.json']:
            a=runs[0]/(n+suffix);b=runs[1]/(n+suffix);assert a.read_bytes()==b.read_bytes();receipt_pairs.append(dict(run1=row(a),run2=row(b),exact_utf8_equal=True,repeatability_not_correctness=True))
        for folder in runs:
            graph=load(folder/(n+'.receipt-graph.json'));redacted=load(folder/(n+'.receipt.redacted.json'));edits=load(folder/(n+'.receipt.owned-edits.json'));issue=load(folder/(n+'.issue.json'));literal=c['input']['issuedAtUtc']
            assert issue['valid'] and issue['error']=='' and issue['actualSHA']==issue['expectedSHA']==c['expected_config_sha256'] and issue['descriptor']==c['descriptor']
            assert graph==c['expected_graph']==edits['after']==edits['expectedOriginal'] and redacted==c['expected_redacted']
            a=folder/(n+'.receipt.redacted.json');b=folder/(n+'.receipt.expected-redacted.json');assert a.read_bytes()==b.read_bytes()
            assert isinstance(redacted['snapshot']['issuedAtUtc'],str) and redacted['snapshot']['issuedAtUtc']==redacted['admittedAtUtc']==graph['properties']['AdmittedAtUtc']==graph['properties']['Snapshot']['IssuedAtUtc']==literal
            utc_types.append(dict(case_id=n,utc_kind=c['utc_kind'],run_root=str(folder),literal=literal,actual_nested=redacted['snapshot']['issuedAtUtc'],actual_admitted=redacted['admittedAtUtc'],actual_token='String',all_stringtypes_matched=True,entire11receipt_redaction_bytes_matched=True,actual=row(a),reference=row(b),not_DateTime_parsed_or_canonicalized=True))
            receiptbindings.append(dict(case_id=n,graph=row(folder/(n+'.receipt-graph.json')),oracle=row(Q/'RECEIPT_EXPECTED_SEMANTICS.json'),all11_receipt15_nested_policyrecord_matched=True,redacted_actual=row(a),redacted_reference=row(b),matched=True,strict_original_values_matched=True,utc_kind=c['utc_kind'],literal=literal))
            receiptcopies.append(dict(case_id=n,run_root=str(folder),after_owned_descriptor_clone_returnedpolicy_edits=row(folder/(n+'.receipt.owned-edits.json')),full_original_graph_unchanged=True,only_connected_descriptor_andreturnedcopy_credit=True))
    metadata=load(runs[0]/'PUBLIC_DTO_METADATA.json');receiptmeta=[r for r in metadata if r['type'].endswith('.OperatorStartupAdmissionReceipt')];assert len(receiptmeta)==11 and all(r['kind']=='property' and not r['has_public_setter'] for r in receiptmeta)
    assert {r['name'] for r in receiptmeta}==set(next(iter(receipts['cases'].values()))['expected_graph']['properties'])
    allbindings=bindings+receiptbindings;allpairs=pairs+receipt_pairs
    write(Q/'RECEIPT_FULLTYPED_GRAPH_AND_REFERENCE_BINDING.json',dict(at=now(),receipt_public_metadata=receiptmeta,receipt11_props_redaction11_nested15_13_fulltyped=True,descriptor7=True,cases=receiptbindings,owned_copy_cases=receiptcopies,crossprocess_pairs=receipt_pairs,original_literal_UTC_STRING_BYTE_PASS=True,expected_not_modified=True,receiptTimestamp_copies_configIssued_notclockproof=True,IsTrusted_localflag_not_origin_authentication=True))
    write(Q/'UTC_LITERAL_TYPE_AND_WHOLE_BYTES_BINDING.json',dict(at=now(),rows=utc_types,main8_originalZERO7=True,variant_fraction7_four=True,variant_whole_seconds_four=True,eachculture20_fullgraphcases=True,expectedstrings_neverdatetime_canonicalized=True,fraction7_100ns_notnanoseconds=True,whole_graph_andbytes_notleafonly=True))
    # Entirely fresh R22 observations; original caller plus ACTUAL used Clone.
    copyproof=[];originproof=[]
    for folder,o in zip(runs,observed):
        resultmap={r['id']:r for r in o['results']} if 'id' in o['results'][0] else {r['name']:r for r in o['results']}
        for n,c in receipts['cases'].items():
            d=c['descriptor'];graph=load(folder/(n+'.receipt-graph.json'));edit=load(folder/(n+'.receipt.owned-edits.json'))
            assert d['originId'].strip()!=d['originId'] and d['launchPlanId'].strip()!=d['launchPlanId']
            assert graph['properties']['BoundOriginId']==d['originId'] and graph['properties']['BoundLaunchPlanId']==d['launchPlanId']
            assert all(edit['descriptor'][k]!=d[k] and edit['cloned'][k]!=d[k] for k in d)
            checksAfter=[r for r in o['results'] if r.get('id',r.get('name',r.get('case_id')))==n+'_VALID_AFTER_USED_CLONE_EDIT']
            if not checksAfter:checksAfter=[r for r in o['results'] if n+'_VALID_AFTER_USED_CLONE_EDIT' in str(r)]
            assert len(checksAfter)==1 and checksAfter[0]['status']=='PASS'
            assert graph==edit['after']==c['expected_graph']
            copyproof.append(dict(case_id=n,run_root=str(folder),usedClone_asactualfactoryarg_source=row(Q/'Program.cs'),actual_edited_caller7_andusedClone7=row(folder/(n+'.receipt.owned-edits.json')),all14fields_changed=True,original_fullgraph_preserved=True,normal_validafteredit=checksAfter[0],editedDTO_neverreapplied=True))
            originproof.append(dict(case_id=n,run_root=str(folder),original_origin=d['originId'],original_plan=d['launchPlanId'],bound_origin=graph['properties']['BoundOriginId'],bound_plan=graph['properties']['BoundLaunchPlanId'],ordinal_codepoints_matched=True,originalleadingtrailingWhitespaceUnicode=True,factoryDATA_only_notbootstrap=True))
    write(Q/'USED_CALLER_CLONE_AND_ORIGINAL_DECLARATION_BINDING.json',dict(at=now(),actualfactoryarg='cloned',cases=copyproof,originalDeclaration=originproof,entire11receipt15snapshot_afteredits_PASS=True,normalValidateAdmissionReceipt_IsValid_aftercopy20each=True,no_privatecapture_getter_mutation_execution=True))
    equiv=[]
    for n,c in receipts['cases'].items():
        if 'ROLECAP_EQUIVALENCE' not in n:continue
        d=c['descriptor'];assert d['expectedRole'] in ['  simulation  ','  read_only  '] and d['expectedCapabilityBoundary']=='  local_sandboxed  '
        assert c['input']['role'] in ['SIMULATION','READ_ONLY'] and c['input']['capabilityBoundary']=='LOCAL_SANDBOXED'
        for folder in runs:
            typed=load(folder/(n+'.receipt.typed-checks.json'));assert all(x['matched'] for x in checks(typed))
            graph=load(folder/(n+'.receipt-graph.json'));assert graph==c['expected_graph']
            assert graph['properties']['BoundRole']==c['input']['role'] and graph['properties']['BoundCapabilityBoundary']=='LOCAL_SANDBOXED'
            equiv.append(dict(case_id=n,run_root=str(folder),original_descriptor=d,originalcaller_andusedClone_verbatim_before_edits=True,fulltyped_original_purity=row(folder/(n+'.receipt.typed-checks.json')),bound_role=graph['properties']['BoundRole'],bound_capability=graph['properties']['BoundCapabilityBoundary'],entiregraph_andredactedBytes_matched=True,positive_semantically_equivalent_contract_explicitly_admitted=True,negative_rejection=False))
    assert len(equiv)==8 and len(receipts['cases'])==20
    write(Q/'NORMAL_ROLECAP_EQUIVALENCE_FULLGRAPH_BINDING.json',dict(at=now(),cases=equiv,exact4positivecases_each=True,privatecopyTrim_existingOrdinalIgnoreCase_credit=True,no_lowercase_orTrim_mutation_to_callerClone=True))
    scopeadmission=load(Q/'THREE_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json')
    assert scopeadmission['source']==row(SOURCE) and len(scopeadmission['four_fixed_ordered_segments'])==4 and all(r['bytes_exact'] for r in scopeadmission['four_fixed_ordered_segments'])
    src=SOURCE.read_text(encoding='utf-8-sig');lines=src.splitlines();excerpts=[]
    assert 'originId = origin.Trim()' not in src and 'launchPlanId = plan.Trim()' not in src and 'expectedConfigId = cfgId.Trim()' not in src
    assert 'originId = origin,' in src and 'launchPlanId = plan,' in src and 'expectedConfigId = cfgId,' in src
    assert src.count('desc.expectedRole = desc.expectedRole?.Trim() ?? "";')==2 and src.count('desc.expectedCapabilityBoundary = desc.expectedCapabilityBoundary?.Trim() ?? "";')==2
    for n,a,b in [('BOOTSTRAP_ORIGINAL_MAPPING',43,130),('CLONE_PRIVATE_CAPTURE_FIXED',3680,3846),('FILE_PRIVATECOPY_NORMALIZATION',4043,4149),('BYTES_PRIVATECOPY_NORMALIZATION',4150,4280),('FIXED_CAPTURE_VALIDATION',4281,4408)]:
        p=Q/'source_extracts'/(n+'.txt');p.parent.mkdir(exist_ok=True);p.write_text('\n'.join(f'{i}: {lines[i-1]}' for i in range(a,b+1))+'\n',encoding='utf-8');excerpts.append(dict(name=n,artifact=row(p),**anchor(a,b)))
    findings=[
        dict(id='ENGINE-G05-DECLARATION-TRIM-R22-20261011-01',status='FRESH_TARGETED_SOURCE_ORIGINAL_MAPPING_AND_NORMAL_FULLGRAPH_PRIVATECOPY_EQUIVALENCE_PASS_MASTER_DISPOSITION_PENDING',source=row(Q/'THREE_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json'),proof=row(Q/'NORMAL_ROLECAP_EQUIVALENCE_FULLGRAPH_BINDING.json'),issue='CLI assignments nowverb atim;factory privatecloned rolecap nullsafeTrim beforeguards/admission/capture. OriginalUnicodeoriginplan andactualusedClone/caller14 mutations preserveall20 graphs/normalValidateIsValid. No nativeCLI execution/no QA closure.',anchors=[anchor(99,106),anchor(4043,4071),anchor(4150,4177)],closure_by_QA=False),
        dict(id='M01_NATIVE_CLI_AUTHORITY',status='NATIVE_UNTESTED_SEPARATE_OPEN',issue='Sourcepatch/publiccloneverbatim/private7readonlycapture/localIsTrusted selfconsistency doesnotprove actualCLI/bootstrap execution/operator/authentication/factoryexclusivecrypto/hostilesameprocess. Missingdefault/null/failclosed branches SOURCEONLY.'),
        dict(id='R19_OPAQUE_R21_UTC',status='FRESH_R23_NORMAL_REGRESSION_PASS_HISTORICAL_SCOPED_CLOSURE_NOT_INHERITED',proof=row(Q/'UTC_LITERAL_TYPE_AND_WHOLE_BYTES_BINDING.json'),closure_by_QA=False),
        dict(id='M04_M05_M06_M07',status='OPEN_NATIVE_UNTESTED',issue='Role userdata/childfrontend/processstart-options/taskidentity/currentcontext-content-corepatchsettings/controlplane/native separatework. Globalinstaller/Awake/readiness fixedsource only,fullGateE2NOTRELEASED.')]
    write(Q/'INDEPENDENT_REVIEW_FINDINGS.json',dict(at=now(),findings=findings,source_excerpts=excerpts,three_spans_four_fixedsegments_verified=True,census_csproj_fixed=True,Master_release_closure=True,Foundation='HOLD',known_installed='OPEN_ACTOR_CAUSE_UNKNOWN_ORIGINAL_NOT_REREAD_RESTORED'))
    base=FROZEN/'scratch/EngineGate05R23IdentifierMapping';prod=[];host=load(base/'HOST_TELEMETRY.json');producerSource=base/'Harness/Program.cs';producerText=producerSource.read_text(encoding='utf-8-sig')
    for ix,label in enumerate(['run_en_us','run_de_de']):
        out=base/label;res=load(out/'E1_EXECUTION_REPORT.json');ledger=res['call_counts'];inv=load(out/'OUTPUT_INVENTORY.json');checked=[]
        actualfiles=[p for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'];assert {r['relative_path'] for r in inv}=={p.relative_to(out).as_posix() for p in actualfiles}
        for r in inv:
            p=out/r['relative_path'];checked.append(dict(recorded=r,actual=row(p),matched=sha(p)==r['sha256'] and p.stat().st_size==r['size_bytes']))
        assert all(r['matched'] for r in checked);direct=sum(ledger.values());assert direct==66 and len(checked)==24
        assert ledger['ParseStrict']==ledger['AdmitConfigBytes']==ledger['AdmitConfigFile']==ledger['ToSnapshot']==ledger['ToRedactedJsonSnapshot']==0
        tests=res['tests'];assert len(tests)==7 and all(t['status']=='PASS' for t in tests)
        assert tests[3]['total_count']==8 and tests[4]['rolecap_receipt_pass_count']==4 and res['total_receipts_issued']==20
        assert tests[6]['digest']=='0A635BB38E49F04552CEA48A5A7A41B3448AC1AF59D8CE7D80EB8706F19C12EE'
        prod.append(dict(run=label,results=row(out/'E1_EXECUTION_REPORT.json'),culture=res['culture'],labels=7,host_record=host['runs'][ix],manual_counter=direct,ledger=ledger,inventory=row(out/'OUTPUT_INVENTORY.json'),rows=checked,current_nonself_count=24,producerUTC8bothroles_FILE_PLAIN_leafonly=True,normal16snapshot_executed=0,main8selectedreceipt_andcaller8_only=True,rolecap4selectedboundfields=True,stdout=row(out/'stdout.txt'),stderr=row(out/'stderr.txt')))
    write(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json',dict(at=now(),rows=prod,source=row(producerSource),manual66_excludesIsValidCloneConstructor_notnestedprofiler=True,normal16snapshot_report_claim_notobserved=True,defaultDTOmetadatainspection_only_nottrustedreject=True,defaultprobe_vsWPpositiveonly_deviation_noQA_replay=True,UTC8_FILE_PLAIN_leaf_duplicateZERO7_notrequiredOPAQUE_FILEBYTES8fullgraph=True,main8selectedfields_notfullgraphBytes_actualusedClone14absent=True,rolecap4boundfields_notfullgraphBytes=True,TEST07_plain_digest0A635_notopaque8A9C=True,wrong_report_CLI_method_name='WorkerBridgeComponent.TryReadOperatorLaunchDescriptorFromCommandLine',actual_CLI_source='WorkerBridgeBootstrapper constructor',current_closedstreams_inventory_match=True,original_buildraw_fullprospective_input_compiler_refs_loaded_postgraph='PARTIAL',firstbefore_after_maps_ephemeral_only=True,producer_runner_execution=0,syntheticprofile_notnativeauthority=True))
    build=load(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0 and build['complete_streams_direct_files_before_tool_output']
    write(Q/'COMPLETE_BUILD_STREAM_BINDING.json',dict(at=now(),actual_final_builds=1,compiler_numeric_exit=0,stdout=build['stdout'],stderr=build['stderr'],tool=row(Q/'BUILD_TOOL_PROOF.json'),wrapper=row(Q/'BUILD_INVOCATION_TOOL_PROOF.json'),full_streams_directfiles=True,no_compiler_retry_or_candidate_rerun=True))
    failures=sum(o['failed_assertions'] for o in observed);assert not failures and not typedfail and all(r['matched'] for r in allbindings)
    summary=dict(at=now(),verdict='SCOPED_R23_ORIGINAL_CLI_MAPPING_SOURCE_PRIVATECOPY_ROLECAP_EQUIVALENCE20_NORMAL_RECEIPT_USEDCLONE_FULLGRAPH_UTC_OPAQUE_CODEC_PASS_MASTER_DISPOSITION_PENDING_NATIVE_UNTESTED',selected_sha256=observed[0]['selected_sha256'],selected_mvid=observed[0]['selected_mvid'],actual_build_exit=0,qa_runner_builds=1,actual_run_exits=[p['actual_numeric_exit'] for p in processes],assertions_per_run=[len(o['results']) for o in observed],failed_assertions_per_run=[o['failed_assertions'] for o in observed],passed_assertions_per_run=[sum(r['status']=='PASS' for r in o['results']) for o in observed],fulltyped_checks=typedcount,failed_typed_checks=typedfail,byte_pair_count=len(allpairs),reference_pair_count=len(refpairs),all_byte_pairs=allpairs,bindings=allbindings,binding_count=len(allbindings),binding_failed=0,processes=processes,pins=[len(p['files']) for p in pres],loads=[len(load(r/'ACTUAL_LOADED_MANAGED.json')) for r in runs],outputs=[load(r/'OUTPUT_INVENTORY.json')['file_count'] for r in runs],scope=scope,receipt_cases=20,main8=True,additional_valid_UTC8=True,normal_rolecap_equivalence4=True,config_cases=4,snapshot_routes=16,receipt_properties=11,receipt_redacted_properties=11,descriptor7=True,nested15_redacted13_result25=True,connected_source_copy8=True,normalreceipt_actual_usedClone_andcaller_copy20=True,detached_policy_copy36=True,compiler_stdout_bytes=build['stdout']['bytes'],all_production_Process_globalWorker_native_cache_query_adverse=0,valid_policy_ConfigureClear_directcalls_allowed=True,oracle_runner_candidate_output_corrections_rebuild_rerun_aftercalls=0,fullGateE2='NOT_RELEASED',foundation='HOLD',closure_by_QA=False,qualifications=['CLIoriginalmapping SOURCEONLY/nativebootstrap UNTESTED','Privatecloned rolecap Trim+OrdinalIgnoreCase normal4casePASS/callerhelperverbatim','Normalactualcaller7-usedClone7/copygraphValidateIsValid20/no privatecapture mutation','Localtrustedflag/configtimestamp/syntheticprofile PID nonce notnativeauthority','SharedJsonNETprimitiveescaping;independentstructure-order-inputliterals','Producer7labels/manual66/UTC8FILEPLAINleaf/normal16snapshot0/partialpackaging','R19opaqueR21UTCscopedCLOSEDhistoricalnotinherited;oldR20FAIL preserved;M01closureMasterpending'])
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',summary)
    print(json.dumps(dict(assertions=summary['assertions_per_run'],passed=summary['passed_assertions_per_run'],failed=summary['failed_assertions_per_run'],exits=summary['actual_run_exits'],typed=typedcount,typed_failed=typedfail,bytepairs=len(allpairs),refs=len(refpairs),bindings=len(allbindings),scope=[dict(direct=r['direct_pure_events'],grouped=r['grouped_snapshot_events'],total=r['total_events']) for r in scope],producer=[dict(counter=r['manual_counter'],rows=r['current_nonself_count']) for r in prod]),indent=2))
