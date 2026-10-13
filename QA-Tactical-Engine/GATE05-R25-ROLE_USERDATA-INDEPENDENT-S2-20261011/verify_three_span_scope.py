from review_setup import *
import difflib
if __name__=='__main__':
    scope=TASK/'MASTER_R25_SCOPE_BASELINE.json';d=load(scope);prior=ROOT/'Dispatcher/CANDIDATES/G05R23-31bd3af2/scratch/WorkerBridgeMod/Source';old=(prior/'WorkerBridge.cs').read_bytes();source=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';new=source.read_bytes()
    assert sha(prior/'WorkerBridge.cs')==d['source_before']['sha256'] and sha(source)=='AB5AD60F16A62FC4473712ABF03AF10A3BB22A66DD8E283F0EC241857BD25BD2'
    regions=d['authorized_spans'];assert len(regions)==3 and len(d['fixed_segments'])==4
    slices=[];pos=0
    for r in regions:slices.append(old[pos:r['start']]);pos=r['end']
    slices.append(old[pos:]);matches=[];newpos=0
    for i,(b,r) in enumerate(zip(slices,d['fixed_segments'])):
        p=Path(r['path']);assert p.read_bytes()==b and sha(p)==r['sha256'] and p.stat().st_size==r['bytes'];at=new.find(b,newpos);assert at>=newpos
        if i==0:assert at==0
        matches.append(dict(index=i,original_fixed_file=row(p),size=len(b),new_start=at,new_end=at+len(b),bytes_exact=True));newpos=at+len(b)
    assert newpos==len(new)
    fixed=[]
    for n in ['EngineHostCensus.cs','WorkerBridge.csproj']:
        p=source.parent/n;assert p.read_bytes()==(prior/n).read_bytes();fixed.append(row(p))
    assert len(load(MAN)['files'])==99
    (Q/'THREE_SPAN_SCOPE_DIFF.txt').write_text(''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True),new.decode('utf-8-sig').splitlines(True),fromfile=str(prior/'WorkerBridge.cs'),tofile=str(source))),encoding='utf-8')
    write(Q/'THREE_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json',dict(at=now(),source=row(source),scope_baseline=row(scope),previous_frozen_source=row(prior/'WorkerBridge.cs'),three_authorized_spans=regions,four_fixed_ordered_segments=matches,all_other_bytes_exact=True,fixed=fixed,freeze99=True,source_R21_UTC_public11_Snapshot_ParseStrict_AdmitBytesFile_globalguards_fixed=True,candidate_execution=False,independent_result_pending=True))
    print('Three authorized spans/fouroriginal fixed byte segments independently matched;Census-csproj/freeze99 beforecalls verified')
