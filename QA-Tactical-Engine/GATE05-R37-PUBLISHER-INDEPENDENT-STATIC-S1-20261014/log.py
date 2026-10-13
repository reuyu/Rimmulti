from common import *
import os,ast,subprocess,importlib,platform
stage=sys.argv[1];assert stage in ['bootstrap','capture','review','prepare','seal'];script=Q/(stage+'.py')
deps=[row(p) for p in [script,Q/'common.py',Path(__file__),Path(sys.executable),WP,BASE,MAN,S]]
if (Q/'PASSIVE_INPUT_MANIFEST.json').exists():deps+=load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']
modules=[]
for name in ['json','hashlib','pathlib','datetime','ast','difflib','re','subprocess']:
    m=importlib.import_module(name);p=getattr(m,'__file__',None)
    if p:modules.append(dict(module=name,**row(p)))
write(Q/(stage+'.INPUT.json'),dict(at=now(),files=deps,argv=[sys.executable,'-B',str(script)],cwd=str(ROOT),interpreter_version=sys.version,launcher_module_observations=modules,launcher_sys_path=sys.path,environment={k:os.environ.get(k) for k in ['PYTHONHOME','PYTHONPATH','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','LANG']},context='OWN_PASSIVE_METADATA_ONLY; launcher observations not comprehensive child import attestation'))
syntax=[]
try:
    for p in [script,Q/'common.py',Path(__file__)]:
        tree=ast.parse(p.read_bytes().decode('utf-8'),filename=str(p));syntax.append(dict(**row(p),body_node_count=len(tree.body),syntax='PASS_PARSE_ONLY'))
except SyntaxError as ex:
    write(Q/(stage+'.SYNTAX_PRECHECK.json'),dict(at=now(),files=syntax,error=str(ex),exit_code=1,helper_executed=False));raise
write(Q/(stage+'.SYNTAX_PRECHECK.json'),dict(at=now(),files=syntax,interpreter=row(sys.executable),version=sys.version,exit_code=0,helper_body_executed_before_check=False,candidate_parsed_by_this_check=False))
start=now();env=dict(os.environ,PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');p=subprocess.Popen([sys.executable,'-B',str(script)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate()
for suf,data in [('STDOUT.txt',out),('STDERR.txt',err)]:
    fp=Q/(stage+'.'+suf);assert not fp.exists();fp.write_bytes(data)
d=dict(start=start,end=now(),pid=p.pid,exit_code=p.returncode,stdout=row(Q/(stage+'.STDOUT.txt')),stderr=row(Q/(stage+'.STDERR.txt')),input_manifest=row(Q/(stage+'.INPUT.json')),syntax_precheck=row(Q/(stage+'.SYNTAX_PRECHECK.json')),scope='OWNMETADATA child; candidate/publication/fixture/Engine/native0')
write(Q/(stage+'.TOOL.json'),d);print(json.dumps(d,ensure_ascii=False));sys.exit(p.returncode)
