from pathlib import Path
import sys,json,hashlib,runpy,traceback,datetime
Q=Path(__file__).resolve().parent;name='finalize_r2.py';args=sys.argv[1:];assert args in [['prepare'],['seal']]
label='finalize_r2_'+'_'.join(args);out=Q/(label+'.STDOUT.txt');err=Q/(label+'.STDERR.txt');proof=Q/(label+'.TOOL.json');pin=Q/(label+'.INPUT.json');assert not any(p.exists() for p in [out,err,proof,pin])
def r(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper(),bytes=p.stat().st_size)
PKG=Q.parent.parent/'docs/WarEconomy_Master_Handoff_20261006'
ps=[Q/name,Q/'common.py',Q/'log_finalize_r2.py',Path(sys.executable),PKG/'MASTER_R35_STATIC_R2_SKIP_OPTIONAL_QUERY_FINALIZE_20261013.md',PKG/'coordination/MASTER_R35_STATIC_R2_OPTIONAL_QUERY_STOP_PRESERVATION_20261013.json'];inputs=[r(p) for p in ps]
for fname in ['PASSIVE_INPUT_MANIFEST.json','PASSIVE_R1_INPUT_MANIFEST.json']:
    d=json.loads((Q/fname).read_bytes().decode('utf-8'))
    for v in d['files']:assert r(Path(v['path']))==v
    inputs+=d['files']
pin.write_bytes((json.dumps(dict(at=datetime.datetime.now().isoformat(),files=inputs,source_interpreter_authorization_before_finalization=True,argv=[str(Q/name)]+args,cwd=str(Path.cwd()),metadata_only=True),indent=2)+'\n').encode('utf-8'))
code=0;started=datetime.datetime.now().isoformat();so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se;sys.argv=[str(Q/name)]+args
    try:runpy.run_path(str(Q/name),run_name='__main__')
    except SystemExit as ex:code=ex.code if isinstance(ex.code,int) else (0 if ex.code is None else 1)
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=so0,se0
proof.write_bytes((json.dumps(dict(script=r(Q/name),input_pin=r(pin),argv=[str(Q/name)]+args,cwd=str(Path.cwd()),started_at=started,finished_at=datetime.datetime.now().isoformat(),exit_code=code,stdout=r(out),stderr=r(err),first_streams_complete=True),indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(stage=label,exit_code=code,stdout=r(out),stderr=r(err))));sys.exit(code)
