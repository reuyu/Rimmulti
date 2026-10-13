from common import *
import os,subprocess,importlib,platform
stage=sys.argv[1];assert stage in ['bootstrap','capture','review','final_prepare','final_seal'];script=Q/(stage+'.py')
deps=[row(p) for p in [script,Q/'common.py',Path(__file__),Path(sys.executable),WP,BASE,MAN,S]]
if (Q/'PASSIVE_INPUT_MANIFEST.json').exists():deps+=load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']
modules=[]
for name in ['json','hashlib','pathlib','datetime','ast','difflib','ntpath','re','subprocess']:
    m=importlib.import_module(name);p=getattr(m,'__file__',None)
    if p:modules.append(dict(module=name,**row(p)))
write(Q/(stage+'.INPUT.json'),dict(at=now(),files=deps,argv=[sys.executable,'-B',str(script)],cwd=str(ROOT),interpreter_version=sys.version,host_platform=platform.platform(),launcher_default_module_observations=modules,sys_path=sys.path,environment={k:os.environ.get(k) for k in ['PYTHONHOME','PYTHONPATH','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','LANG']},context='OWN_PASSIVE_METADATA_CHILD_ONLY; launcher module observations are not comprehensive child import attestations'))
start=now();env=dict(os.environ,PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');p=subprocess.Popen([sys.executable,'-B',str(script)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate()
for suffix,data in [('STDOUT.txt',out),('STDERR.txt',err)]:
    pp=Q/(stage+'.'+suffix);assert not pp.exists();pp.write_bytes(data)
proof=dict(start=start,end=now(),pid=p.pid,exit_code=p.returncode,stdout=row(Q/(stage+'.STDOUT.txt')),stderr=row(Q/(stage+'.STDERR.txt')),input_manifest=row(Q/(stage+'.INPUT.json')),child_scope='ownpassivemetadata, no candidate import/call; candidate/native/fixture/compiler0')
write(Q/(stage+'.TOOL.json'),proof);print(json.dumps(proof,ensure_ascii=False));sys.exit(p.returncode)
