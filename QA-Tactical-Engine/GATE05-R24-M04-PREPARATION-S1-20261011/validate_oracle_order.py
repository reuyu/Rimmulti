from review_setup import *
import copy
p=Q/'PROSPECTIVE_M04_NORMAL_ORACLE.json';d=load(p);assert not (Q/'PROSPECTIVE_M04_NORMAL_ORACLE_BEFORE_ORDER_RECONCILIATION.json').exists();write(Q/'PROSPECTIVE_M04_NORMAL_ORACLE_BEFORE_ORDER_RECONCILIATION.json',d)
keys=['schemaVersion','configId','role','admittedValidatorExecutablePath','admittedValidatorExecutableSha256','workerUserDataDirectory','validatorUserDataDirectory','workerCwd','validatorCwd','expectedPackagePolicyDeclaration','expectedContentProfileFingerprint','capabilityBoundary','issuedAtUtc']
for c in d['cases']:
    red={k:copy.deepcopy(c['config'][k]) for k in keys};assert len(red)==13;c['expected_snapshot_redacted13']=red;c['expected_receipt_redacted11']['snapshot']=red
    pol=c['config']['expectedPackagePolicyDeclaration'];c['expected_policy_record4']=dict(policyId=pol['policyId'],revision=pol['revision'],admittedPackageIds=pol['admittedPackageIds'],policyDigest=c['expected_policy_digest'])
    c['expected_snapshot_redacted_utf8_text']=json.dumps(red,ensure_ascii=False,indent=2);c['expected_receipt_redacted_utf8_text']=json.dumps(c['expected_receipt_redacted11'],ensure_ascii=False,indent=2)
    c['expected_redacted_order_source']=dict(file=row(SOURCE),snapshot_lines=[3661,3686],receipt_lines=[3806,3834])
d['ordered_fullbytes_expectations']='IndependentPython JSON syntax andexplicit frozen method fieldorder/literals. Draft futureunitoracle,notcandidateoutput/JsonNETexecution. Future admittedcompiler runner validatesstandardescaping limitation.'
write(p,d);print('Draftnormal oracle sourcefieldorder andwholeUTF8 representations reconciled beforeanybuild/calls;allcurrently0')
