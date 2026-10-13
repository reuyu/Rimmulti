from review_setup import *
import difflib
if __name__=='__main__':
    assert not (Q/'COMPLETION.json').exists() and not (Q/'runner/QaPureRunner.exe').exists()
    notice=PKG/'MASTER_R29_S3_STATIC_SELECTOR_R1_AUTHORIZATION_20261012.md'
    operational=PKG/'MASTER_R29_S3_RECOVERY_OUTPUT_ENCODING_AUTHORIZATION_20261012.md'
    template=ROOT/'Dispatcher/Tools/MASTER_R29_S3_STATIC_SELECTOR_R1_TEMPLATE.py'
    assert sha(notice)=='9EB47BEC7D3EBAF15A213C8DDCDA445ECF900110167E374F873AACE10F085BD5'
    assert sha(operational)=='C5D0FFD0B6789DD25F27B50CC7985963B11D452BC406C0979A204BC8768313BA'
    assert sha(template)=='C0F617C8C8A967780C990967BE994A7AC160850A5E0F77A2BC26E1DA441A5BF0' and template.stat().st_size==7446
    assert load(Q/'RECOVERY_UTF8_R1_TOOL.json')['exit_code']==0 and load(Q/'RECOVERY_UTF8_R1_AUDIT.json')['completed']
    preserve=PKG/'coordination/MASTER_R29_S3_STATIC_STOP_INITIAL_PROSPECTIVE_PRESERVATION_20261012.json'
    for r in load(preserve)['files']:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(p)
    original=(Q/'static_review.py').read_bytes();candidate=template.read_bytes()
    replacements=[(b"'NEW_PAIR_MODE_M05_NOT_ADMITTED'",b"'if (_privatePairProfile != null)'"),(b"around(p,'json = Encoding.UTF8.GetString(bundleBytes);'",b"around(p,'                json = Encoding.UTF8.GetString(bundleBytes);'")]
    expected=original
    for a,b in replacements:
        assert expected.count(a)==1 and candidate.count(b)==1
        expected=expected.replace(a,b)
    assert expected==candidate
    inverse=candidate
    for a,b in reversed(replacements):inverse=inverse.replace(b,a)
    assert inverse==original
    worker=(FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs').read_bytes()
    publisher=(FROZEN/'scratch/OperatorStartupPairR29/publish_operator_pair.py').read_bytes()
    anchors=[]
    for n in ast.walk(ast.parse(candidate.decode('utf-8'))):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='around':
            needle=n.args[1].value;source=worker if n.args[0].id=='p' else publisher
            assert source.count(needle.encode('utf-8'))==1,needle
            anchors.append(dict(needle=needle,occurrences=1))
    assert len(anchors)==12
    destination=Q/'static_review_selector_r1.py';assert not destination.exists();destination.write_bytes(template.read_bytes())
    assert destination.read_bytes()==candidate and sha(destination)==sha(template)
    diff=''.join(difflib.unified_diff(original.decode('utf-8').splitlines(True),candidate.decode('utf-8').splitlines(True),fromfile='original-static-failure',tofile='new-static-selector-R1'))
    dp=Q/'STATIC_SELECTOR_R1_INDEPENDENT_EXACT_DIFF.txt';assert not dp.exists();dp.write_bytes(diff.encode('utf-8'))
    write(Q/'STATIC_SELECTOR_R1_COPY_PROOF.json',dict(at=now(),notice=row(notice),operational_notice=row(operational),template=row(template),original=row(Q/'static_review.py'),copied=row(destination),exact_two_literal_only=True,inverse_original_bytes_equal=True,unique_anchors=anchors,prospective_19_files=load(preserve)['files'],actual_candidate_compiler_calls=0))
    print(json.dumps(dict(copy_sha=sha(destination),bytes=destination.stat().st_size,exact_two_literals=True,anchors=len(anchors),candidate_compiler_calls=0)))
