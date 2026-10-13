from review_setup import *
if __name__=='__main__':
    assert not (Q/'analyze_review.py').exists()
    old=ROOT/'QA-Tactical-Engine/GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011/analyze_review.py';t=old.read_text(encoding='utf-8-sig');t=t[:t.index("    receipts=load(Q/'RECEIPT_EXPECTED_SEMANTICS.json')")]
    t+=(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8');(Q/'analyze_review.py').write_text(t,encoding='utf-8')
    print('Fresh R21 ownrun-only fulltyped source/reference analysis prepared;old source read as reference only')
