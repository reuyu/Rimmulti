from common import *
import os,ast,subprocess,importlib
stage=sys.argv[1];assert stage in ['bootstrap','capture','review','prepare','seal'];assert load(Q/(stage+'.PREFLIGHT_TOOL.json'))['exit_code']==0;script=Q/(stage+'.py')
deps=[row(p) for p in [script,Q/'common.py',Path(__file__),Q/'invoke.ps1',Path(sys.executable),WP,BASE,MAN,S]]
if (Q/'PASSIVE_INPUT_MANIFEST.json').exists():deps+=load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']
mods=[]
for name in ['json','hashlib','pathlib','datetime','ast','difflib','re','subprocess']:
    m=importlib.import_module(name);p=getattr(m,'__file__',None)
    if p:mods.append(dict(module=name,**row(p)))
write(Q/(stage+'.INPUT.json'),dict(at=now(),files=deps,argv=[sys.executable,'-B',str(script)],cwd=str(ROOT),interpreter_version=sys.version,launcher_modules=mods,launcher_sys_path=sys.path,selected_env={k:os.environ.get(k) for k in ['PYTHONHOME','PYTHONPATH','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','LANG']},preflight=row(Q/(stage+'.PREFLIGHT_TOOL.json')),context='OWN passive metadata; module observations partial, not comprehensive child import attestation'))
start=now();env=dict(os.environ,PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');p=subprocess.Popen([sys.executable,'-B',str(script)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate()
for suffix,data in [('STDOUT.txt',out),('STDERR.txt',err)]:
    fp=Q/(stage+'.'+suffix);assert not fp.exists();fp.write_bytes(data)
d=dict(start=start,end=now(),pid=p.pid,exit_code=p.returncode,stdout=row(Q/(stage+'.STDOUT.txt')),stderr=row(Q/(stage+'.STDERR.txt')),input_manifest=row(Q/(stage+'.INPUT.json')),preflight=row(Q/(stage+'.PREFLIGHT_TOOL.json')),scope='OWN metadata; candidate/publication/Engine/native0')
write(Q/(stage+'.TOOL.json'),d);print(json.dumps(d,ensure_ascii=False));sys.exit(p.returncode)
