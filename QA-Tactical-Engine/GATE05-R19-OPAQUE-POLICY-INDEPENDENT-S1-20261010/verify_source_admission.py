from review_setup import *
import difflib
if __name__=='__main__':
    old=ROOT/'Dispatcher/CANDIDATES/G05R18-befc4fba/scratch/WorkerBridgeMod/Source';source=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';prior=old/'WorkerBridge.cs';b=prior.read_bytes();expected=b
    changes=[]
    for field in ['policyId','revision']:
        a=('config.expectedPackagePolicyDeclaration.'+field+'.Trim();').encode();z=('config.expectedPackagePolicyDeclaration.'+field+';').encode();assert b.count(a)==1;expected=expected.replace(a,z);changes.append(dict(before=a.decode(),after=z.decode()))
    assert source.read_bytes()==expected and sha(source)=='AE55E5A6DC0802728A41DE661F825F8734699B82E9F1A21657DA5B83758616CE'
    assert len(load(MAN)['files'])==98
    fixed=[]
    for name in ['EngineHostCensus.cs','WorkerBridge.csproj']:
        p=source.parent/name;assert p.read_bytes()==(old/name).read_bytes();fixed.append(row(p))
    diff=''.join(difflib.unified_diff(b.decode('utf-8-sig').splitlines(True),expected.decode('utf-8-sig').splitlines(True),fromfile=str(prior),tofile=str(source)))
    (Q/'EXACT_TWO_ASSIGNMENT_SOURCE_DIFF.txt').write_text(diff,encoding='utf-8')
    write(Q/'EXACT_SOURCE_ADMISSION_BEFORE_CALLS.json',dict(at=now(),new_source=row(source),previous_frozen_source=row(prior),exact_two_assignment_change=True,all_other_bytes_lineendings_identical=True,changes=changes,fixed=fixed,freeze98=True,WP=row(PKG/'WP_QA_ENGINE_GATE05_R19_OPAQUE_POLICY_INDEPENDENT_S1.md'),source_execution=False,independent_runtime_result_pending=True))
    print('Exact two assignment byte diff/fixedCensus-csproj/freeze98 independently verified;implementation credit only')
