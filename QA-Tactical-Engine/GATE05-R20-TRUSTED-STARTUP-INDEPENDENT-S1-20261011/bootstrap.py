from pathlib import Path
Q=Path(__file__).resolve().parent;ROOT=Q.parent.parent;OLD=ROOT/'QA-Tactical-Engine/GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010'
def change(t):
    pairs=[('WE-A-ENGINE-GATE05-R19-OPAQUE-POLICY-20261010-DIRECT-5415a675','WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656'),('G05R19-5415a675','G05R20-e35ff656'),('MASTER_GATE05_R19_OPAQUE_POLICY','MASTER_GATE05_R20_TRUSTED_STARTUP'),('MASTER_R19_QA_INDEPENDENT_PROTECTED_BASELINE_20261010','MASTER_R20_QA_INDEPENDENT_PROTECTED_BASELINE_20261011'),('QA_EngineHost_Gate05_R19_Opaque_Policy_Independent_S1_20261010','QA_EngineHost_Gate05_R20_Trusted_Startup_Independent_S1_20261011'),('WP_QA_ENGINE_GATE05_R19_OPAQUE_POLICY_INDEPENDENT_S1','WP_QA_ENGINE_GATE05_R20_TRUSTED_STARTUP_INDEPENDENT_S1'),('WP_QA_ENGINE_GATE05_R19_OPAQUE_POLICY_INDEPENDENT','WP_QA_ENGINE_GATE05_R20_TRUSTED_STARTUP_INDEPENDENT'),('SOL-GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010','SOL-GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011'),('R19_FROZEN_LINEAGE','R20_FROZEN_LINEAGE'),('9F1B154C47D6434EF751FA8ED32915D472B4FB8FAB8DE50918C02379753A2D75','FD284886A8E6F08D063D845BE8962A6A06CE526C70B34562F8370B380DB9D1E4'),('746D9B76B8F338291D9B5F5602D3BF571C5BEFFBBB963F8C82E903177C179310','03BD6923AB97F948FF6BCF708ACFB551986F024EA1E698C3810AEDF3370D702B'),('D290ABF01C304CE56871F463C5E14AD273AFA3C6AF1E6DEFBCF020EF955C8C08','3CF8C1741BD40BB06985C4ED3EFB18BA30896EB187AD6521218F0727CE539782'),('9841','10346'),('FB69CB8385CF665AEBAFA1913A8A02CC7887F48F8BBA6FCDEE85CF67C8CB646D','482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0'),('4969ba0f-2bdf-4a27-b4f8-d7fa217f0b70','9e516c44-35c8-49b8-b3ec-f73ec58ba12f'),('4804693e-29fc-4acd-b51d-1c74046b417f','96ac6c7c-420a-4c16-a26e-7c0a18d4c360'),('ExactfrozenR19','ExactfrozenR20')]
    for a,b in pairs:t=t.replace(a,b)
    # Candidate E1 proof follows date 20261011.
    t=t.replace('MASTER_GATE05_R20_TRUSTED_STARTUP_E1_VERIFICATION_20261010','MASTER_GATE05_R20_TRUSTED_STARTUP_E1_VERIFICATION_20261011')
    return t
if __name__=='__main__':
    assert not (Q/'review_setup.py').exists()
    (Q/'review_setup.py').write_text(change((OLD/'review_setup.py').read_text(encoding='utf-8-sig')),encoding='utf-8')
    for n in ['prepare_runner.py','SnapshotControls.cs.txt','pin_admission.py','run_identity.py','host_launch.py','build_once.py']:
        t=change((OLD/n).read_text(encoding='utf-8-sig'))
        if n=='prepare_runner.py':
            t=t.replace('qa.R19','qa.R20').replace('R19 normal','R20 normal').replace('QA_LOCAL_OPERATOR_PLAN_R19','QA_LOCAL_OPERATOR_PLAN_R20').replace('QA.R19.EXPLICIT','QA.R20.EXPLICIT').replace('EngineGate05R19OpaquePolicy','EngineGate05R20TrustedStartup').replace("runid='R19-'","runid='R20-'").replace("replace('R17','R19')","replace('R17','R20')").replace("replace('freshR17','freshR19')","replace('freshR17','freshR20')")
            t=t.replace("descriptor=dict(originId='QA_LOCAL_OPERATOR_PLAN_R20',expectedConfigId=config['configId'],expectedRole=role,expectedCapabilityBoundary=config['capabilityBoundary'],launchPlanId='QA.R20.EXPLICIT.PLAN.'+name)","descriptor=dict(originId='QA_LOCAL_OPERATOR_PLAN_R20',expectedConfigId=config['configId'],expectedRole=role,expectedCapabilityBoundary=config['capabilityBoundary'],launchPlanId='QA.R20.EXPLICIT.PLAN.'+name,expectedConfigPath=str(p),expectedConfigSha256=sha(p))")
            t=t.replace("len(config)==14 and len(policy)==4","len(config)==14 and len(policy)==4")
            t=t.replace("template=template.replace('typeof(OperatorStartupConfigSnapshot),','typeof(OperatorStartupConfigSnapshot),typeof(OperatorLaunchDescriptor),')","template=template.replace('typeof(OperatorStartupConfigSnapshot),','typeof(OperatorStartupConfigSnapshot),typeof(OperatorLaunchDescriptor),typeof(OperatorStartupAdmissionReceipt),')")
            t=t.replace("template=template.replace('%%REFERENCE_FUNCTIONS%%'","template=template.replace('  static void RunFileHelpers(', (Q/'ReceiptControls.cs.txt').read_text(encoding='utf-8')+'\\n  static void RunFileHelpers(').replace('RunSnapshots(input);RunFileHelpers(input);','RunSnapshots(input);RunReceipts(input);RunFileHelpers(input);')\n    template=template.replace('%%REFERENCE_FUNCTIONS%%'")
        if n=='pin_admission.py':
            t=t.replace("len(c['descriptor'])==5","len(c['descriptor'])==7").replace("'verify_source_admission.py','EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json','EXACT_TWO_ASSIGNMENT_SOURCE_DIFF.txt'","'prepare_receipt_oracle.py','RECEIPT_EXPECTED_SEMANTICS.json','ReceiptControls.cs.txt'")
            t=t.replace("paths += [Q/'verify_source_admission.py',Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json',Q/'EXACT_TWO_ASSIGNMENT_SOURCE_DIFF.txt']","paths += [Q/'prepare_receipt_oracle.py',Q/'RECEIPT_EXPECTED_SEMANTICS.json',Q/'ReceiptControls.cs.txt']")
        if n=='run_identity.py':
            t=t.replace("'prepare_evidence_tools.py',","'prepare_receipt_oracle.py','ReceiptControls.cs.txt','RECEIPT_EXPECTED_SEMANTICS.json',")
            t=t.replace("paths.extend([Q/'verify_source_admission.py',Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json',Q/'EXACT_TWO_ASSIGNMENT_SOURCE_DIFF.txt'])","paths.extend([Q/'prepare_receipt_oracle.py',Q/'RECEIPT_EXPECTED_SEMANTICS.json',Q/'ReceiptControls.cs.txt'])")
            t=t.replace("'ORACLE_BEFORE_BUILD.json']:shutil.copy2","'ORACLE_BEFORE_BUILD.json','RECEIPT_EXPECTED_SEMANTICS.json']:shutil.copy2")
        (Q/n).write_text(t,encoding='utf-8')
    print('New R20 source tools prepared;old source read-only reference/no old top-level runner execution')
