from pathlib import Path
Q=Path(__file__).resolve().parent;ROOT=Q.parent.parent;OLD=ROOT/'QA-Tactical-Engine/GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011'
def change(t):
    pairs=[('WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656','WE-A-ENGINE-GATE05-R21-RECEIPT-UTC-20261011-DIRECT-49256586'),('G05R20-e35ff656','G05R21-49256586'),('MASTER_GATE05_R20_TRUSTED_STARTUP','MASTER_GATE05_R21_RECEIPT_UTC'),('MASTER_R20_QA_INDEPENDENT_PROTECTED_BASELINE','MASTER_R21_QA_INDEPENDENT_PROTECTED_BASELINE'),('QA_EngineHost_Gate05_R20_Trusted_Startup','QA_EngineHost_Gate05_R21_Receipt_Utc'),('WP_QA_ENGINE_GATE05_R20_TRUSTED_STARTUP','WP_QA_ENGINE_GATE05_R21_RECEIPT_UTC'),('SOL-GATE05-R20-TRUSTED-STARTUP','SOL-GATE05-R21-RECEIPT-UTC'),('R20_FROZEN_LINEAGE','R21_FROZEN_LINEAGE'),('FD284886A8E6F08D063D845BE8962A6A06CE526C70B34562F8370B380DB9D1E4','B3A4F1CC59D73E9774580216A03647336687A43637AA30F3FC6FBECED1421B6F'),('03BD6923AB97F948FF6BCF708ACFB551986F024EA1E698C3810AEDF3370D702B','D2E2FEF82674B9C2C8F4C90045D9F75AE8C3463C82BC4AB1A9CB2502008623DB'),('3CF8C1741BD40BB06985C4ED3EFB18BA30896EB187AD6521218F0727CE539782','1D70407D24EC6DC3195DEDBF31CC10A746F72C5CE8825577763E2EA7F1C15F4F'),('10346','10939'),('482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0','31D7A2508ACFADE1B9430F43E6F3D2ACF3E9822C787D00DAF55C9E44CF8E5AC4'),('9e516c44-35c8-49b8-b3ec-f73ec58ba12f','7a8b444a-3a07-4dee-9d37-4fa7ed3c461c'),('96ac6c7c-420a-4c16-a26e-7c0a18d4c360','28abd2eb-3220-4e97-aa99-c4ff1edb5900'),('ExactfrozenR20','ExactfrozenR21')]
    for a,b in pairs:t=t.replace(a,b)
    return t
if __name__=='__main__':
    assert not (Q/'review_setup.py').exists()
    for n in ['review_setup.py','prepare_runner.py','SnapshotControls.cs.txt','ReceiptControls.cs.txt','pin_admission.py','run_identity.py','host_launch.py','build_once.py']:
        t=change((OLD/n).read_text(encoding='utf-8-sig'))
        if n=='prepare_runner.py':t=t.replace('qa.R20','qa.R21').replace('R20 normal','R21 normal').replace('QA_LOCAL_OPERATOR_PLAN_R20','QA_LOCAL_OPERATOR_PLAN_R21').replace('QA.R20.EXPLICIT','QA.R21.EXPLICIT').replace('EngineGate05R20TrustedStartup','EngineGate05R21ReceiptUtc').replace("runid='R20-'","runid='R21-'").replace("replace('R17','R20')","replace('R17','R21')").replace("replace('freshR17','freshR20')","replace('freshR17','freshR21')")
        if n=='pin_admission.py':t=t.replace("len(receiptOracle['cases'])==8","len(receiptOracle['cases'])==16").replace("annotation['receipt_cases']=8","annotation['receipt_cases']=16").replace('Full R20','Full R21')
        (Q/n).write_text(t,encoding='utf-8')
    print('Fresh R21 source-only QA tools prepared;no old main/runner/output execution or reuse')
