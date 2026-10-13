from review_setup import *
import copy
if __name__=='__main__':
    assert not (Q/'RECEIPT_EXPECTED_SEMANTICS.json').exists() and not (Q/'runner/QaPureRunner.exe').exists()
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json');cases={}
    for n,c in oracle['config_cases'].items():
        assert len(c['descriptor'])==7 and c['descriptor']['expectedConfigSha256']==c['expected_config_sha256']
        for route in ['FILE','BYTES']:
            name='RECEIPT_'+n+'_'+route;d=c['descriptor'];props=dict(ReceiptSchemaVersion='WE-OPERATOR-RECEIPT-V1',Snapshot=copy.deepcopy(c['expected_snapshot']),BoundConfigPath=c['file']['path'],BoundConfigSha256=c['expected_config_sha256'],BoundOriginId=d['originId'],BoundLaunchPlanId=d['launchPlanId'],BoundConfigId=d['expectedConfigId'],BoundRole=d['expectedRole'],BoundCapabilityBoundary=d['expectedCapabilityBoundary'],AdmittedAtUtc=c['input']['issuedAtUtc'],IsTrusted=True)
            redacted=dict(receiptSchemaVersion='WE-OPERATOR-RECEIPT-V1',isTrusted=True,boundOriginId=d['originId'],boundLaunchPlanId=d['launchPlanId'],boundConfigId=d['expectedConfigId'],boundRole=d['expectedRole'],boundCapabilityBoundary=d['expectedCapabilityBoundary'],boundConfigPath=c['file']['path'],boundConfigSha256=c['expected_config_sha256'],admittedAtUtc=c['input']['issuedAtUtc'],snapshot=copy.deepcopy(c['expected_redacted']))
            graph=dict(properties=props,snapshotGraph=dict(properties=copy.deepcopy(c['expected_snapshot']),declaration=copy.deepcopy(c['expected_declaration']),record=copy.deepcopy(c['expected_record']),readOnlyPackageIds=copy.deepcopy(c['expected_declaration']['admittedPackageIds'])))
            assert len(props)==11 and len(redacted)==11
            cases[name]=dict(route=route,input=copy.deepcopy(c['input']),descriptor=copy.deepcopy(d),file=copy.deepcopy(c['file']),expected_config_sha256=c['expected_config_sha256'],expected_graph=graph,expected_redacted=redacted,normal_only=True)
    write(Q/'RECEIPT_EXPECTED_SEMANTICS.json',dict(at=now(),cases=cases,source=row(FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'),independent_before_calls_build=True,output_derived_oracle=False,AdmittedAtUtc_configIssued_literal_notcurrentclock=True,IsTrusted_localflag_not_origin_authentication=True,original_string_expectation_not_JSONNET_date_output_normalization=True))
    print('8normal receipt full11+11/nested15+13/descriptor7 original-value expectations prepared beforebuild/calls')
