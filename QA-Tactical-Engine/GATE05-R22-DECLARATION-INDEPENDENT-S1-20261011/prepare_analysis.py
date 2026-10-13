from review_setup import *
old=(ROOT/'QA-Tactical-Engine/GATE05-R21-RECEIPT-UTC-INDEPENDENT-S1-20261011/analyze_review.py').read_text(encoding='utf-8-sig')
prefix=old[:old.index("    scopeadmission=load(")].replace('descriptor5_fields=True','descriptor7_fields=True')
tail=(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8')
assert not (Q/'analyze_review.py').exists()
(Q/'analyze_review.py').write_text(prefix+tail,encoding='utf-8')
print('NewR22 independent post-execution analysis source prepared;oldtop-level code notexecuted')
