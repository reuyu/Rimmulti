from review_setup import *
old=(ROOT/'QA-Tactical-Engine/GATE05-R22-DECLARATION-INDEPENDENT-S1-20261011/analyze_review.py').read_text(encoding='utf-8-sig')
prefix=old[:old.index("    scopeadmission=load(")].replace('eachculture16_fullgraphcases=True','eachculture20_fullgraphcases=True').replace('normalValidateAdmissionReceipt_IsValid_aftercopy16each=True','normalValidateAdmissionReceipt_IsValid_aftercopy20each=True')
assert not (Q/'analyze_review.py').exists()
(Q/'analyze_review.py').write_text(prefix+(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8'),encoding='utf-8')
print('R23 post-analysis tools generated fromread-only reference source;no oldtop-levelmodule execution')
