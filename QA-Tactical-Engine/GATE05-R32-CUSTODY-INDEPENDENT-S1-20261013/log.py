from pathlib import Path
import sys,json,hashlib,runpy,traceback,datetime
Q=Path(__file__).resolve().parent;name=sys.argv[1];args=sys.argv[2:]
assert name in {'bootstrap.py','static_review.py','prepare.py','execution.py','finalize.py','post.py'} and (Q/name).is_file()
label=name[:-3]+('_'+'_'.join(args) if args else '')
out=Q/(label+'.STDOUT.txt');err=Q/(label+'.STDERR.txt');proof=Q/(label+'.TOOL.json')
assert not out.exists() and not err.exists() and not proof.exists()
code=0;started=datetime.datetime.now().isoformat();so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se;sys.argv=[str(Q/name)]+args
    try:runpy.run_path(str(Q/name),run_name='__main__')
    except SystemExit as ex:code=ex.code if isinstance(ex.code,int) else (0 if ex.code is None else 1)
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=so0,se0
def r(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper(),bytes=p.stat().st_size)
proof.write_bytes((json.dumps(dict(script=r(Q/name),argv=[str(Q/name)]+args,cwd=str(Path.cwd()),started_at=started,finished_at=datetime.datetime.now().isoformat(),exit_code=code,stdout=r(out),stderr=r(err),first_streams_complete=True),indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(stage=label,exit_code=code,stdout=r(out),stderr=r(err)),ensure_ascii=True));sys.exit(code)
