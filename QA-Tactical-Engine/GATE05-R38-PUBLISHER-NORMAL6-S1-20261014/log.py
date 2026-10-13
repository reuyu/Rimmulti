from common import *
import subprocess,importlib
stage=sys.argv[1];script=Q/('run_case.py' if stage.startswith('case') else stage+'.py')
pf=load(Q/(stage+'.PREFLIGHT_TOOL.json'));assert pf['exit_code']==0;check(pf['streams']);seed=load(Q/(stage+'.PREFLIGHT_SEED.json'));check(seed['files']);controls()
deps=[row(p) for p in [script,Q/'common.py',Path(__file__),Q/'invoke.ps1',EXE]+[p for p,h in PINS]]
if (Q/'PASSIVE_INPUT_MANIFEST.json').exists():deps+=load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']
mods=[]
for name in ['json','hashlib','pathlib','datetime','os','stat','subprocess','ast','re']:
    m=importlib.import_module(name);p=getattr(m,'__file__',None)
    if p:mods.append(dict(module=name,**row(p)))
args=[str(EXE),'-B',str(script)]+([stage] if stage.startswith('case') else []);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
write(Q/(stage+'.INPUT.json'),dict(at=now(),files=deps,argv=args,cwd=str(ROOT),interpreter_version=sys.version,launcher_sys_path=sys.path,launcher_modules=mods,selected_env={k:env.get(k) for k in ['PYTHONHOME','PYTHONPATH','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','PYTHONIOENCODING','LANG']},preflight_seed=row(Q/(stage+'.PREFLIGHT_SEED.json')),limitations='Partial observed resolved files/default launcher path; child imports not comprehensive attestation'))
start=now();p=subprocess.Popen(args,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate()
for name,b in [('STDOUT.bin',out),('STDERR.bin',err)]:
    with (Q/(stage+'.'+name)).open('xb') as f:f.write(b)
d=dict(start=start,end=now(),pid=p.pid,exit_code=p.returncode,stdout=row(Q/(stage+'.STDOUT.bin')),stderr=row(Q/(stage+'.STDERR.bin')),input_manifest=row(Q/(stage+'.INPUT.json')),preflight=row(Q/(stage+'.PREFLIGHT_TOOL.json')),scope='Own QA helper; candidate calls separately tracked percase')
write(Q/(stage+'.TOOL.json'),d);print(json.dumps(d,ensure_ascii=False));sys.exit(p.returncode)
