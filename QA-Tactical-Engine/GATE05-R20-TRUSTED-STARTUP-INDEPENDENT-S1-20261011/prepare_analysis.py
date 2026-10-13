from review_setup import *
if __name__=='__main__':
    assert not (Q/'analyze_review.py').exists()
    old=ROOT/'QA-Tactical-Engine/GATE05-R19-OPAQUE-POLICY-INDEPENDENT-S1-20261010/analyze_review.py';t=old.read_text(encoding='utf-8-sig');t=t[:t.index("    admission=load(Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json')")]
    t=t.replace("endswith('.OperatorLaunchDescriptor')])==5","endswith('.OperatorLaunchDescriptor')])==7")
    t+=(Q/'AnalysisTail.py.txt').read_text(encoding='utf-8');(Q/'analyze_review.py').write_text(t,encoding='utf-8')
    print('New R20 ownrun-only fulltyped/baseanalysis source prepared;old source reference only')
