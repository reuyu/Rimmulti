from review_setup import *
import copy
def make_case(c,route,kind):
    d=c['descriptor'];props=dict(ReceiptSchemaVersion='WE-OPERATOR-RECEIPT-V1',Snapshot=copy.deepcopy(c['expected_snapshot']),BoundConfigPath=c['file']['path'],BoundConfigSha256=c['expected_config_sha256'],BoundOriginId=d['originId'],BoundLaunchPlanId=d['launchPlanId'],BoundConfigId=d['expectedConfigId'],BoundRole=d['expectedRole'],BoundCapabilityBoundary=d['expectedCapabilityBoundary'],AdmittedAtUtc=c['input']['issuedAtUtc'],IsTrusted=True)
    redacted=dict(receiptSchemaVersion='WE-OPERATOR-RECEIPT-V1',isTrusted=True,boundOriginId=d['originId'],boundLaunchPlanId=d['launchPlanId'],boundConfigId=d['expectedConfigId'],boundRole=d['expectedRole'],boundCapabilityBoundary=d['expectedCapabilityBoundary'],boundConfigPath=c['file']['path'],boundConfigSha256=c['expected_config_sha256'],admittedAtUtc=c['input']['issuedAtUtc'],snapshot=copy.deepcopy(c['expected_redacted']))
    graph=dict(properties=props,snapshotGraph=dict(properties=copy.deepcopy(c['expected_snapshot']),declaration=copy.deepcopy(c['expected_declaration']),record=copy.deepcopy(c['expected_record']),readOnlyPackageIds=copy.deepcopy(c['expected_declaration']['admittedPackageIds'])))
    assert len(props)==11 and len(redacted)==11 and isinstance(c['input']['issuedAtUtc'],str)
    return dict(route=route,input=copy.deepcopy(c['input']),descriptor=copy.deepcopy(d),file=copy.deepcopy(c['file']),expected_config_sha256=c['expected_config_sha256'],expected_graph=graph,expected_redacted=redacted,normal_only=True,utc_kind=kind)
if __name__=='__main__':
    assert not (Q/'RECEIPT_EXPECTED_SEMANTICS.json').exists() and not (Q/'runner/QaPureRunner.exe').exists()
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json');cases={};variants={}
    for n,c in oracle['config_cases'].items():
        assert len(c['descriptor'])==7
        for route in ['FILE','BYTES']:cases['RECEIPT_'+n+'_'+route]=make_case(c,route,'ZERO_FRACTION7_MAIN')
    for role in ['SIMULATION','READ_ONLY']:
        for kind,literal in [('FRACTION7','2026-10-10T00:00:00.1234567Z'),('WHOLE_SECONDS','2026-10-10T00:00:00Z')]:
            c=copy.deepcopy(oracle['config_cases'][role+'_OPAQUE']);name=role+'_UTC_'+kind;c['input']['configId']='qa.R21.'+name;c['input']['issuedAtUtc']=literal
            p=Q/'normal_configs'/(name+'.json');write(p,c['input']);c['file']=row(p);c['expected_config_sha256']=sha(p)
            c['descriptor']['expectedConfigId']=c['input']['configId'];c['descriptor']['expectedConfigPath']=str(p);c['descriptor']['expectedConfigSha256']=sha(p);c['descriptor']['launchPlanId']='QA.R21.EXPLICIT.PLAN.'+name
            c['expected_snapshot']['ConfigId']=c['input']['configId'];c['expected_snapshot']['IssuedAtUtc']=literal;c['expected_redacted']['configId']=c['input']['configId'];c['expected_redacted']['issuedAtUtc']=literal;variants[name]=c
            for route in ['FILE','BYTES']:cases['RECEIPT_'+name+'_'+route]=make_case(c,route,kind)
    assert len(cases)==16
    write(Q/'RECEIPT_EXPECTED_SEMANTICS.json',dict(at=now(),cases=cases,main_cases=8,additional_variants=8,variants=variants,source=row(FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'),independent_before_calls_build=True,output_derived_oracle=False,expectedUTC_never_DateTime_parsed_or_canonicalized=True,fraction7_100ns_not_nanoseconds=True,AdmittedAtUtc_configIssued_literal_notcurrentclock=True,IsTrusted_localflag_not_origin_authentication=True))
    print('16normal receipt expected11+11/nested15+13/descriptor7;originalZERO7/fraction7/wholeUTC strings fixed independently beforebuild/calls')
