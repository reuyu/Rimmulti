from qa_common import *
import sys,traceback
out=Q/'RECOVERY_CAPTURED_STDOUT.txt';err=Q/'RECOVERY_CAPTURED_STDERR.txt';proof=Q/'RECOVERY_CAPTURED_TOOL.json'
assert not out.exists() and not err.exists() and not proof.exists()
code=0;so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se
    try:
        audit=load(Q/'RECOVERY_AFTER_COMPACTION.json');rows=[]
        for item in audit['files']:
            p=Path(item['path']);text=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text);rows.append(dict(**row(p),read_all=True))
        write(Q/'RECOVERY_CAPTURED_AUDIT.json',dict(at=now(),files=rows,candidate_calls=0,earlier_console_truncation='Earlier recovery console output was bounded; this fresh read captures entire required document streams, no analysis or candidate rerun.'))
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=so0,se0
write(proof,dict(at=now(),script=row(Path(__file__)),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True,candidate_calls=0))
print(json.dumps(dict(exit_code=code,required_documents=len(rows),candidate_calls=0)));sys.exit(code)
