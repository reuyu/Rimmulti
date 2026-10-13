"""Runs only a named NEW own QA stage with complete first-attempt streams."""
from pathlib import Path
import sys,json,hashlib,runpy,traceback,datetime
Q=Path(__file__).resolve().parent
name=sys.argv[1];args=sys.argv[2:]
allowed={'prepare_runner.py','static_review.py','execution_tools.py','build_once.py','post_analysis.py','finalize_review.py'}
assert name in allowed and (Q/name).is_file()
label=name[:-3]+('_'+'_'.join(args) if args else '')
out=Q/(label+'.STDOUT.txt');err=Q/(label+'.STDERR.txt');proof=Q/(label+'.TOOL.json')
assert not out.exists() and not err.exists() and not proof.exists()
argv=['python','-B',str(Q/name)]+args
started=datetime.datetime.now().isoformat();code=0
so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout=so;sys.stderr=se;sys.argv=[str(Q/name)]+args
    try:runpy.run_path(str(Q/name),run_name='__main__')
    except SystemExit as ex:code=ex.code if isinstance(ex.code,int) else (0 if ex.code is None else 1)
    except BaseException:
        code=1;traceback.print_exc()
    finally:sys.stdout=so0;sys.stderr=se0
def p(x):return dict(path=str(x),sha256=hashlib.sha256(x.read_bytes()).hexdigest().upper(),bytes=x.stat().st_size)
proof.write_bytes((json.dumps(dict(script=p(Q/name),argv=argv,cwd=str(Path.cwd()),started=started,finished=datetime.datetime.now().isoformat(),exit_code=code,stdout=p(out),stderr=p(err),streams_complete=True,old_script_top_level_executed=False),indent=2)+'\n').encode())
print(json.dumps(dict(stage=label,exit_code=code,stdout=p(out),stderr=p(err))))
sys.exit(code)

