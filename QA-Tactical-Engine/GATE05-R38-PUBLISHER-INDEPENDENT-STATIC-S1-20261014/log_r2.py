from common import *
import os,subprocess,importlib
stage=sys.argv[1];assert stage=='review_finalize_r2';assert load(Q/(stage+'.PREFLIGHT_TOOL.json'))['exit_code']==0
seed=load(Q/(stage+'.PREFLIGHT_SEED.json'));check(seed['files']);sup=load(Q/'RECOVERY_R2_PROSPECTIVE_SUPPLEMENT.json');check(sup['files'])
deps=[row(p) for p in [Q/(stage+'.py'),Q/'common.py',Path(__file__),Q/'invoke_r2.ps1',Path(sys.executable),Q/'RECOVERY_R2_PROSPECTIVE_SUPPLEMENT.json']]+load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']+load(Q/'STOP_REVIEW_PARTIAL_INVENTORY.json')['files']
mods=[]
for name in ['json','hashlib','pathlib','datetime','ast','difflib','re','subprocess']:
    m=importlib.import_module(name);p=getattr(m,'__file__',None)
    if p:mods.append(dict(module=name,**row(p)))
env=dict(os.environ,PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
write(Q/(stage+'.INPUT.json'),dict(at=now(),files=deps,preflight_seed=row(Q/(stage+'.PREFLIGHT_SEED.json')),argv=[sys.executable,'-B',str(Q/(stage+'.py'))],cwd=str(ROOT),interpreter_version=sys.version,launcher_modules=mods,launcher_sys_path=sys.path,selected_env={k:env.get(k) for k in ['PYTHONHOME','PYTHONPATH','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','PYTHONIOENCODING','LANG']},limitations=['launcher observation partial, child observations separately postrun','native syntax preflight PID UNOBSERVED','default ambient context not comprehensively attested']))
start=now();p=subprocess.Popen([sys.executable,'-B',str(Q/(stage+'.py'))],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate()
for suffix,data in [('STDOUT.txt',out),('STDERR.txt',err)]:
    fp=Q/(stage+'.'+suffix);assert not fp.exists();fp.write_bytes(data)
d=dict(start=start,end=now(),pid=p.pid,exit_code=p.returncode,stdout=row(Q/(stage+'.STDOUT.txt')),stderr=row(Q/(stage+'.STDERR.txt')),input_manifest=row(Q/(stage+'.INPUT.json')),preflight=row(Q/(stage+'.PREFLIGHT_TOOL.json')),scope='OWN metadata finalization; original review reruns0/candidate0')
write(Q/(stage+'.TOOL.json'),d);print(json.dumps(d,ensure_ascii=False));sys.exit(p.returncode)
