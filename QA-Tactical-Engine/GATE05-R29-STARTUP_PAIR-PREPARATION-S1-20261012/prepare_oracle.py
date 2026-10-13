"""Prospective literal data only; no publisher, candidate, codec or runner calls."""
from bootstrap_review import *
import copy,re
DECL=['originId','expectedConfigId','expectedRole','expectedCapabilityBoundary','launchPlanId','expectedConfigPath','expectedConfigSha256']
TOP=['schemaVersion','operatorPairId','parentDeclaration','childDeclaration']
GET=['ParentReceipt','ChildReceipt','OperatorPairId','Scope']
SCOPE='DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY'
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def binding(t):
    b=t.encode('utf-8')
    return dict(utf8_text=t,sha256=hashlib.sha256(b).hexdigest().upper(),bytes=len(b),BOM=False,trailing_newline=False,hex=b.hex().upper())
def typemap(x,path='$'):
    row=dict(path=path,json_type='object' if isinstance(x,dict) else 'array' if isinstance(x,list) else 'boolean' if isinstance(x,bool) else 'integer' if isinstance(x,int) else 'string',ordered_keys=list(x) if isinstance(x,dict) else None,length=len(x) if isinstance(x,list) else None)
    out=[row]
    if isinstance(x,dict):
        for k,v in x.items():out+=typemap(v,path+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):out+=typemap(v,path+'['+str(i)+']')
    return out
def expect(c,d):
    raw=compact(c);rawsha=binding(raw)['sha256']
    assert d['expectedConfigSha256']==rawsha
    used=copy.deepcopy(d)
    for k in ['expectedRole','expectedCapabilityBoundary','expectedConfigPath','expectedConfigSha256']:used[k]=d[k].strip()
    policy=copy.deepcopy(c['expectedPackagePolicyDeclaration']);pd=binding(compact(policy))['sha256']
    # Inputs use already canonical fully-qualified fixture path spellings. Existing nested Snapshot normalization is source fact.
    snap=dict(SchemaVersion=c['schemaVersion'],ConfigId=c['configId'].strip(),
      AdmittedValidatorExecutablePath=c['admittedValidatorExecutablePath'],AdmittedValidatorExecutableSha256=c['admittedValidatorExecutableSha256'].strip().upper(),ValidatorArguments=c['validatorArguments'],
      WorkerUserDataDirectory=c['workerUserDataDirectory'],ValidatorUserDataDirectory=c['validatorUserDataDirectory'],WorkerCwd=c['workerCwd'],ValidatorCwd=c['validatorCwd'],
      ExpectedPackagePolicyDeclaration=policy,ExpectedContentProfileFingerprint=c['expectedContentProfileFingerprint'].strip(),Role=c['role'],CapabilityBoundary=c['capabilityBoundary'].strip(),IssuedAtUtc=c['issuedAtUtc'].strip(),PolicyAdmittedPackageIds=copy.deepcopy(policy['admittedPackageIds']))
    red=dict(schemaVersion=snap['SchemaVersion'],configId=snap['ConfigId'],role=snap['Role'],admittedValidatorExecutablePath=snap['AdmittedValidatorExecutablePath'],admittedValidatorExecutableSha256=snap['AdmittedValidatorExecutableSha256'],
      workerUserDataDirectory=snap['WorkerUserDataDirectory'],validatorUserDataDirectory=snap['ValidatorUserDataDirectory'],workerCwd=snap['WorkerCwd'],validatorCwd=snap['ValidatorCwd'],
      expectedPackagePolicyDeclaration=copy.deepcopy(policy),expectedContentProfileFingerprint=snap['ExpectedContentProfileFingerprint'],capabilityBoundary=snap['CapabilityBoundary'],issuedAtUtc=snap['IssuedAtUtc'])
    receipt=dict(ReceiptSchemaVersion='WE-OPERATOR-RECEIPT-V1',Snapshot=copy.deepcopy(snap),BoundConfigPath=used['expectedConfigPath'],BoundConfigSha256=rawsha,BoundOriginId=d['originId'],BoundLaunchPlanId=d['launchPlanId'],BoundConfigId=snap['ConfigId'],BoundRole=snap['Role'],BoundCapabilityBoundary=snap['CapabilityBoundary'],AdmittedAtUtc=snap['IssuedAtUtc'],IsTrusted=True)
    rred=dict(receiptSchemaVersion=receipt['ReceiptSchemaVersion'],isTrusted=True,boundOriginId=receipt['BoundOriginId'],boundLaunchPlanId=receipt['BoundLaunchPlanId'],boundConfigId=receipt['BoundConfigId'],boundRole=receipt['BoundRole'],boundCapabilityBoundary=receipt['BoundCapabilityBoundary'],boundConfigPath=receipt['BoundConfigPath'],boundConfigSha256=rawsha,admittedAtUtc=receipt['AdmittedAtUtc'],snapshot=copy.deepcopy(red))
    rec=dict(policyId=policy['policyId'],revision=policy['revision'],admittedPackageIds=copy.deepcopy(policy['admittedPackageIds']),policyDigest=pd)
    assert len(c)==14 and len(d)==7 and len(snap)==15 and len(receipt)==11 and len(red)==13 and len(rec)==4 and len(rred)==11
    return dict(config14=copy.deepcopy(c),original_descriptor7=copy.deepcopy(d),raw_config=binding(raw),factory_used_clone7=used,receipt11=receipt,snapshot15=snap,policy4=policy,policy_record4=rec,snapshot_redaction13=red,receipt_redaction11=rred,
      snapshot_compact_utf8=binding(compact(snap)),receipt_compact_utf8=binding(compact(receipt)),original_declaration7_compact_utf8=binding(compact(d)),policy_digest_input_utf8=binding(compact(policy)),
      snapshot_redacted_pretty_windows_utf8=binding(json.dumps(red,ensure_ascii=False,indent=2).replace('\n','\r\n')),
      receipt_redacted_pretty_windows_utf8=binding(json.dumps(rred,ensure_ascii=False,indent=2).replace('\n','\r\n')))
def freeze_bytes(p,t):
    assert not p.exists()
    p.write_bytes(t.encode('utf-8'))
if __name__=='__main__':
    assert sha(OLD)=='5961CD18DA05B67F6DE40DA8A6EBB289D94ACF85054D57FB31FE4B8C5530C4C7'
    prior=load(OLD);cases=[];rawpins=[]
    for i in range(6):
        historical=prior['normal_pairs'][i] if i<4 else prior['normal_pairs'][0 if i==4 else 1]
        pold=historical['input_parent14_and_original7'];cold=historical['input_child14_and_original7']
        # Each side independently supplied. Never manufacture child by parent.role mutation.
        pc=copy.deepcopy(pold['config14']);cc=copy.deepcopy(cold['config14'])
        pd=copy.deepcopy(pold['original_descriptor7']);cd=copy.deepcopy(cold['original_descriptor7'])
        case_id=historical['case_id'] if i<4 else ['OPAQUE_EQ_QUOTE_BACKSLASH','OPAQUE_EQ_QUOTE_BACKSLASH_PADDED'][i-4]
        pairid=f'  qa.R29.pair.{i+1:02d} Ω  '
        if i>=4:
            pc['configId']='qa.R29.parent='+str(i+1)+' "Ω" \\ literal'
            cc['configId']='qa.R29.child='+str(i+1)+' "Ω" \\ independently literal'
            pd['originId']='  parent origin='+str(i+1)+' "Ω" \\ original  '
            cd['originId']='  child origin='+str(i+1)+' "Ω" \\ separately approved  '
            pd['launchPlanId']='  parent plan='+str(i+1)+' "Ω" \\ original  '
            cd['launchPlanId']='  child plan='+str(i+1)+' "Ω" \\ original  '
            pairid='  operatorPairId='+str(i+1)+' "Ω" \\ original  '
            pd['expectedConfigId']=pc['configId'];cd['expectedConfigId']=cc['configId']
            if i==5:
                pd['expectedRole']='  simulation  ';cd['expectedRole']='  read_only  '
                pd['expectedCapabilityBoundary']='  local_sandboxed  ';cd['expectedCapabilityBoundary']='  local_sandboxed  '
        inputs=Q/'inputs'/case_id;inputs.mkdir(parents=True,exist_ok=True)
        pp=inputs/'parent.config.json';cp=inputs/'child.config.json'
        # Explicit new prospective fixture locator only; historical original7 remains preserved below.
        pd['expectedConfigPath']=str(pp);cd['expectedConfigPath']=str(cp)
        pd['expectedConfigSha256']=binding(compact(pc))['sha256'];cd['expectedConfigSha256']=binding(compact(cc))['sha256']
        parent=expect(pc,pd);child=expect(cc,cd)
        if i<4:
            assert parent['raw_config']['utf8_text']==pold['raw_config_utf8_text']
            assert child['raw_config']['utf8_text']==cold['raw_config_utf8_text']
        assert parent['config14']['role']=='SIMULATION' and child['config14']['role']=='READ_ONLY'
        assert pc['validatorArguments']=='' and cc['validatorArguments']==''
        bundle=dict(schemaVersion='we-operator-startup-pair/v1',operatorPairId=pairid,parentDeclaration=copy.deepcopy(pd),childDeclaration=copy.deepcopy(cd))
        assert list(bundle)==TOP and list(pd)==DECL and list(cd)==DECL
        pair=dict(ParentReceipt=copy.deepcopy(parent['receipt11']),ChildReceipt=copy.deepcopy(child['receipt11']),OperatorPairId=pairid,Scope=SCOPE)
        envelope=dict(PairReadonly4=pair,ParentDeclaration7=copy.deepcopy(pd),ChildDeclaration7=copy.deepcopy(cd),ParentPolicyRecord4=copy.deepcopy(parent['policy_record4']),ChildPolicyRecord4=copy.deepcopy(child['policy_record4']),
          ParentSnapshotRedaction13=copy.deepcopy(parent['snapshot_redaction13']),ChildSnapshotRedaction13=copy.deepcopy(child['snapshot_redaction13']),ParentReceiptRedaction11=copy.deepcopy(parent['receipt_redaction11']),ChildReceiptRedaction11=copy.deepcopy(child['receipt_redaction11']))
        paths=[pp,cp,inputs/'parent.approved7.json',inputs/'child.approved7.json',inputs/'expected.bundle.json']
        texts=[parent['raw_config']['utf8_text'],child['raw_config']['utf8_text'],compact(pd),compact(cd),compact(bundle)]
        for path,t in zip(paths,texts):freeze_bytes(path,t);rawpins.append(pin(path))
        mutations=dict(input_byte_arrays_after_successful_admit_only=['bundleBytes','parentConfigBytes','childConfigBytes'],
          returnedParentDeclaration7={k:'returnedParent_'+k+'_EDIT_Ω' for k in DECL},returnedChildDeclaration7={k:'returnedChild_'+k+'_EDIT_Ω' for k in DECL},
          returnedParentPolicyDeclaration4=dict(schemaVersion='EDIT_PARENT_SCHEMA',policyId='EDIT_PARENT_ID_Ω',revision='EDIT_PARENT_REV',admittedPackageIds=['edited.parent']),
          returnedChildPolicyDeclaration4=dict(schemaVersion='EDIT_CHILD_SCHEMA',policyId='EDIT_CHILD_ID_Ω',revision='EDIT_CHILD_REV',admittedPackageIds=['edited.child']),
          returnedParentPolicyRecord4=dict(policyId='EDIT_PARENT_RECORD',revision='EDIT_PARENT_RECORD_REV',admittedPackageIds=['edited.parent.record'],policyDigest='2'*64),
          returnedChildPolicyRecord4=dict(policyId='EDIT_CHILD_RECORD',revision='EDIT_CHILD_RECORD_REV',admittedPackageIds=['edited.child.record'],policyDigest='3'*64),
          detachedParentPolicyIds=['edited.parent.ids'],detachedChildPolicyIds=['edited.child.ids'])
        cases.append(dict(case_id=case_id,kind='PROSPECTIVE_POSITIVE_NO_TEST_EXECUTION',historical_template_case=historical['case_id'],
          historical_parent_original7=copy.deepcopy(pold['original_descriptor7']),historical_child_original7=copy.deepcopy(cold['original_descriptor7']),
          explicit_fixture_locator_rebind=dict(reason='Own QA actual literal raw config fixture files enable future publisher SHA/path relation without external dummy paths',four_historical_raw14_byte_exact=i<4,original_history_untouched=True,rebound_field='expectedConfigPath',future_fixture_parent_path=str(pp),future_fixture_child_path=str(cp)),
          independently_supplied_parent14_7=parent,independently_supplied_child14_7=child,operatorPairId_original=pairid,
          expected_bundle4=bundle,expected_bundle_compact_UTF8_noLF=binding(compact(bundle)),expected_pair_readonly4=pair,expected_ParentDeclaration_fresh_original7=copy.deepcopy(pd),expected_ChildDeclaration_fresh_original7=copy.deepcopy(cd),
          expected_full_observation_graph=envelope,expected_full_graph_compact_UTF8=binding(compact(envelope)),full_ordered_type_map=typemap(envelope),
          expected_same_graph_phases=['BEFORE_EDITS','AFTER_CALLER_BYTE_ARRAY_EDITS','AFTER_RETURNED_DECLARATION_POLICY_DETACHED_EDITS'],
          planned_copy_controls=mutations,readonly4_property_source_and_metadata_check_only=True,
          declarations_original_vs_factory_used_clone_distinct=True,byte_arrays_not_readmitted_after_mutation=True,
          publisher_future_plan=dict(input_files=[pin(p) for p in paths[:4]],operatorPairId=pairid,owned_output_root=str(Q/'future-publisher-outputs'/case_id),root_not_created=True,expected_bundle_sha256=binding(compact(bundle))['sha256'],expected_compact_bundle_bytes=binding(compact(bundle))['bytes'],output_file_names_and_cli_invocation='UNFROZEN_UNTIL_NEW_SOURCE_ADMISSION',never_overwrite_expected_input_files=True,plan_only_no_spawn=True),
          factory_pair_getter_publisher_calls_now=0,native_or_issuer_authentication_claim=False))
    write(Q/'PRE_RUN_EXPECTED_ORACLE.json',dict(at=now(),kind='INDEPENDENT_PROSPECTIVE_LITERAL_DATA_ONLY_NOT_TEST_PASS',historical_input=pin(OLD),master_contract=pin(C),
      adopted_contract_not_yet_implemented_independently_reviewed=True,auxiliary_top4_writer_order=TOP,descriptor7_writer_order=DECL,readonly4_order=GET,scope=SCOPE,
      prospective_cases=cases,normal_cases=6,original7_not_factory_usedclone=True,
      decoder_property_order='Arbitrary input order not an automatic rejection; exact keys/types/no duplicates required, rawSHA bound independently',
      old_nested_snapshot_behavior='Existing Snapshot performs Trim/GetFullPath for some fields. New pair packaging must not normalize original declaration7/PairId; positive input configId/UTC/path spellings avoid adding a new normalization oracle.',
      issuedAtUtc='Original supplied fixed literal; receipt AdmittedAtUtc comes from snapshot.IssuedAtUtc, not new wall-clock time',
      pair_id='Packaging approval locator only, not task identity/capability',
      build_factory_publisher_candidate_qa_runtime_executes=0,mutable_R29_read=False,R29_candidate_verdict='NOT_REVIEWED',future_final_names_tokens='PENDING_EXACT_NEW_CANDIDATE',foundation='HOLD',native_E2='NOT_RELEASED'))
    write(Q/'PROSPECTIVE_INPUT_LITERAL_MANIFEST.json',dict(at=now(),files=rawpins,expected_files_not_producer_outputs=True,producer_calls=0))
    print(json.dumps(dict(normal_cases=6,literal_files=len(rawpins),typed_rows=sum(len(c['full_ordered_type_map']) for c in cases),raw_bundles=[dict(case_id=c['case_id'],sha256=c['expected_bundle_compact_UTF8_noLF']['sha256'],bytes=c['expected_bundle_compact_UTF8_noLF']['bytes']) for c in cases],oracle=pin(Q/'PRE_RUN_EXPECTED_ORACLE.json'),executed=0)))

