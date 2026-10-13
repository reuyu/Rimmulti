from review_setup import *
if __name__=='__main__':
    assert not (Q/'analyze_review.py').exists()
    old=ROOT/'QA-Tactical-Engine/GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010/analyze_review.py'
    t=old.read_text(encoding='utf-8-sig');t=t[:t.index("    prior=ROOT/'Dispatcher/CANDIDATES/G05R17-")]
    t=t.replace('lossless_original_opaque_PASS=False','lossless_original_opaque_PASS=not any(o[\'failed_assertions\'] for o in observed)')
    t += (Q/'AnalysisTail.py.txt').read_text(encoding='utf-8')
    (Q/'analyze_review.py').write_text(t,encoding='utf-8');print('Fresh R19 read-only analysis prepared;all observed data read from own new R19 runs only')
