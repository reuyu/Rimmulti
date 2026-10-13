import sys, traceback, json
from common import *
out=Q/'RECOVERY_FINALIZE.STDOUT.txt';err=Q/'RECOVERY_FINALIZE.STDERR.txt'
assert not out.exists() and not err.exists()
code=0
with out.open('w',encoding='utf-8',newline='\n') as o,err.open('w',encoding='utf-8',newline='\n') as e:
    try:
        records=[]
        for r in load(Q/'RECOVERY_AUTHORITY_AND_SUPPLEMENT_AUDIT.json')['files']:
            p=Path(r['path']);s=p.read_bytes().decode('utf-8-sig');o.write('\nFILE '+str(p)+'\n'+s+'\n');v=row(p);v['same_as_initial']=v['sha256']==r['sha256'];records.append(v)
        write(Q/'RECOVERY_FINALIZE_AUDIT.json',dict(at=now(),files=records,full_read=True,changed=[v for v in records if not v['same_as_initial']]))
    except BaseException:
        code=1;traceback.print_exc(file=e)
write(Q/'RECOVERY_FINALIZE.TOOL.json',dict(exit_code=code,stdout=row(out),stderr=row(err),at=now()))
print(json.dumps(load(Q/'RECOVERY_FINALIZE_AUDIT.json').get('changed',[]),ensure_ascii=False) if code==0 else err.read_text(encoding='utf-8'))
sys.exit(code)
