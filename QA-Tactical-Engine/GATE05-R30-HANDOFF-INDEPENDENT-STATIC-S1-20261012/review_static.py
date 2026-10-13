from qa_common import *
import sys
from unity_reference_metadata import read_object_methods
FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R30-HANDOFF-20261012-DIRECT-16ce928f'
WORKER=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
OLD=ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
def witness(p,a,z,label):
    b=p.read_bytes();raw=b[a:z]
    return dict(id=label,file=row(p),byte_start=a,byte_end=z,line_start=b[:a].count(b'\n')+1,line_end=b[:z].count(b'\n')+1,sha256=hashlib.sha256(raw).hexdigest().upper(),raw_utf8=raw.decode('utf-8'))
def guard():
    assert load(Q/'bootstrap.TOOL.json')['exit_code']==0
    assert load(Q/'ACK_INITIAL.json')['delivery_id']==DELIVERY
    verify(load(MAN)['files'],'frozen_path')
if __name__=='__main__':
    guard();mode=sys.argv[1]
    if mode=='references':
        dep=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
        assert sha(dep)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
        refrow=next(r for r in load(dep)['files'] if Path(r['frozen_path']).name=='UnityEngine.CoreModule.dll')
        ref=Path(refrow['frozen_path']);assert sha(ref)==refrow['sha256'] and ref.stat().st_size==refrow['bytes']
        write(Q/'UNITY_METADATA_READER_INPUT_PIN.json',dict(at=now(),manifest=row(dep),input=row(ref),reader=row(Q/'unity_reference_metadata.py'),candidate_calls=0,scope='Metadata file reader only; frozen reference, no original Steam'))
        observed=read_object_methods(ref)
        write(Q/'UNITY_REFERENCE_NULL_AND_ADDCOMPONENT_IL.json',dict(at=now(),input=row(ref),dependency_manifest=row(dep),**observed,candidate_or_Unity_code_execution=0))
        print(json.dumps(dict(reference_mvid=observed['reference_mvid'],methods=[dict(name=m['name'],rva=m['rva'],calls=[i['target'] for i in m['instructions'] if 'target' in i]) for m in observed['methods']],AddComponent=[dict(name=m['name'],rva=m['rva'],impl_flags=m['impl_flags']) for m in observed['GameObject_AddComponent_methods']],native_timing='UNOBSERVED')))
    elif mode=='source':
        a=OLD.read_bytes();b=WORKER.read_bytes();scope=load(FT/'MASTER_R30_AUTHORIZED_SOURCE_SCOPE.json');diff=load(FT/'SOURCE_SCOPE_DIFF.json');custody=load(FT/'HANDOFF_CONTROL_FLOW_AND_CUSTODY.json')
        assert sha(OLD)==scope['Worker_original']['sha256']=='55441CE93DF32F5E5940D99A4A9CA8449B3F7839840CA3A3832C9DB31396FBDE'
        assert sha(WORKER)=='B1F8C00D1DF6E8E797EAC8E5A7F7FB462679BA06E79096D5C558C687BD413311'
        ranges=sorted(scope['allowed_byte_spans'],key=lambda r:r['start']);mapped={r['span_id']:r for r in diff['authorized_spans']};outside=[];changes=[];oa=ob=0
        for r in ranges:
            v=mapped[r['id']];x,y=v['new_range']
            assert v['orig_range']==[r['start'],r['end']]
            assert hashlib.sha256(a[r['start']:r['end']]).hexdigest().upper()==r['before_sha256']==v['orig_sha256']
            assert a[oa:r['start']]==b[ob:x]
            outside.append(dict(old_range=[oa,r['start']],new_range=[ob,x],bytes=r['start']-oa,sha256=hashlib.sha256(a[oa:r['start']]).hexdigest().upper(),entire_equal=True))
            w=witness(WORKER,x,y,r['id']);assert w['sha256']==v['new_sha256'] and y-x==v['new_bytes'];changes.append(w);oa=r['end'];ob=y
        assert a[oa:]==b[ob:]
        outside.append(dict(old_range=[oa,len(a)],new_range=[ob,len(b)],bytes=len(a)-oa,sha256=hashlib.sha256(a[oa:]).hexdigest().upper(),entire_equal=True))
        assert len(changes)==5 and len(outside)==6 and sum(v['bytes'] for v in outside)==261380
        prose=[]
        for c in custody['control_flow_table']:
            actual=mapped[c['authorized_span_id']]['new_range'];prose.append(dict(phase=c['phase'],claimed=c['span_range'],actual=actual,matched=c['span_range']==actual))
        write(Q/'SOURCE_BYTE_MAP_AND_FULL_CHANGED_SPANS.json',dict(at=now(),source=row(WORKER),old_source=row(OLD),scope_manifest=row(FT/'MASTER_R30_AUTHORIZED_SOURCE_SCOPE.json'),producer_diff=row(FT/'SOURCE_SCOPE_DIFF.json'),whole_changed_five=changes,outside_six=outside,total_outside=261380,all_outside_equal=True,custody_prose_ranges=prose,Pair_Capture_factory_currenttask_bytes='Covered by whole outside segments, not PASS inherited',candidate_calls=0))
        print(json.dumps(dict(source_bytes=len(b),changed5=True,outside261380=True,custody_prose_ranges=prose,candidate_calls=0)))
    else:raise ValueError(mode)
