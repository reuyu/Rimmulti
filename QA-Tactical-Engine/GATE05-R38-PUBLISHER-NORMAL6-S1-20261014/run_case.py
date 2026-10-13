from common import *
import subprocess,importlib
stage=sys.argv[1];assert stage in ['case01','case02','case03','case04','case05','case06'];index=int(stage[-2:])-1;c=load(EXPECTED)['cases'][index];cid=c['case_id'];cr=Q/cid
controls();assert load(Q/'ACK_RETURN_TOOL_PROOF.json')['isError'] is False
fxt=load(Q/'FIXTURE_FREEZE_MANIFEST.json');check(fxt['files']);assert all(statrow(r['path'])['attributes']&1 for r in fxt['files']);assert load(Q/'fixtures.TOOL.json')['exit_code']==0
for i in range(index):assert load(Q/load(EXPECTED)['cases'][i]['case_id']/'CASE_RESULT.json')['status']=='SCOPED_NORMAL_PASS'
for other in load(EXPECTED)['cases'][index:]:assert not (Q/other['case_id']/'CALL_INTENT.json').exists()
assert not (cr/'CALL_INTENT.json').exists();paths=[Path(inp['future_path']) for inp in c['inputs']]+[Path(c['future_spec_path'])]
stats=[dict(path=str(p),ancestry=ancestry(p),file=row(p)) for p in paths];outstats=ancestry(c['future_output_root'],new_leaf=True);ancestry(S);ancestry(EXE)
codefiles=[row(p) for p in sorted(Q.glob('*.py'))]+[row(Q/'invoke.ps1')]+[row(EXE),row(S),row(EXPECTED),row(ADMIT),row(WP),row(MAN),row(Q/'FIXTURE_FREEZE_MANIFEST.json')]+fxt['files'];check(codefiles)
modules=[]
for name in ['os','re','sys','json','stat','hashlib','datetime','collections','subprocess','pathlib']:
    m=importlib.import_module(name);p=getattr(m,'__file__',None)
    if p:modules.append(dict(module=name,**row(p)))
args=[str(EXE),'-B',str(S),'--spec',c['future_spec_path']];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
write(cr/'PUBLISHER_PROSPECTIVE_INPUT.json',dict(at=now(),case_id=cid,files=codefiles,argv=args,cwd=str(ROOT),interpreter_version=sys.version,launcher_sys_path=sys.path,launcher_resolved_module_observations=modules,selected_env={k:env.get(k) for k in ['PYTHONHOME','PYTHONPATH','PYTHONUTF8','PYTHONDONTWRITEBYTECODE','PYTHONIOENCODING','LANG']},fixture_stats=stats,absent_output_ancestry=outstats,expected_bundle=c['expected_bundle'],expected_sha_sidecar=c['expected_sha_sidecar'],expected_aux4=c['expected_aux4'],limitations=['Partial launcher resolved dependency observation, not comprehensive ambient attestation','Candidate actual child sys.path/importfile internals UNOBSERVED; original candidate logging not modified','Prior path observations not nofollow open or hostile race immunity','Protected local owner/nonhostile concurrent writer assumption']))
write(cr/'CALL_INTENT.json',dict(at=now(),case_id=cid,invocation_number=index+1,maximum=6,argv=args,input_manifest=row(cr/'PUBLISHER_PROSPECTIVE_INPUT.json'),status='ONE_CALL_INTENT_NO_RETRY'))
start=now();p=subprocess.Popen(args,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);stdout,stderr=p.communicate()
for name,b in [('PUBLISHER_STDOUT.bin',stdout),('PUBLISHER_STDERR.bin',stderr)]:
    with (cr/name).open('xb') as f:f.write(b)
tool=dict(case_id=cid,start=start,end=now(),pid=p.pid,exit_code=p.returncode,stdout=row(cr/'PUBLISHER_STDOUT.bin'),stderr=row(cr/'PUBLISHER_STDERR.bin'),argv=args,cwd=str(ROOT),input_manifest=row(cr/'PUBLISHER_PROSPECTIVE_INPUT.json'),candidate=row(S),actual_child_sys_path_importfiles='UNOBSERVED')
write(cr/'PUBLISHER_TOOL.json',tool)
if p.returncode!=0:
    write(cr/'CASE_RESULT.json',dict(at=now(),case_id=cid,status='ACTUAL_CANDIDATE_FAILURE_STOP',tool=tool,partial_outputs=[row(z) for z in cr.rglob('*') if z.is_file()],remaining_cases='UNTESTED',retry=0));print(stdout.decode('utf-8',errors='replace'));print(stderr.decode('utf-8',errors='replace'),file=sys.stderr);sys.exit(p.returncode)
summary=json.loads(stdout.decode('utf-8'));assert summary['status']=='PUBLISHED' and summary['operatorPairId']==c['operatorPairId'];assert summary['bundlePath']==c['future_bundle_path'] and summary['bundleSha256']==c['expected_bundle']['sha256'] and summary['bundleBytes']==c['expected_bundle']['bytes']
out=Path(c['future_output_root']);ancestry(out,leaf_dir=True);bp=out/'operator_startup_pair.json';sp=out/'operator_startup_pair.staging.json';hp=out/'operator_startup_pair.sha256.txt';mp=out/'PROVENANCE_MANIFEST.json'
assert {z.name for z in out.iterdir()}=={bp.name,sp.name,hp.name,mp.name}
assert summary['stagingPath']==str(sp) and summary['manifestPath']==str(mp)
bundle=bp.read_bytes();staging=sp.read_bytes();assert bundle==staging==literal(c['expected_bundle']);assert hp.read_bytes()==literal(c['expected_sha_sidecar']);assert len(hp.read_bytes())==64 and not bundle.startswith(b'\xef\xbb\xbf') and not bundle.endswith(b'\n')
aux=json.loads(bundle.decode('utf-8'));assert aux==c['expected_aux4'];assert list(aux)==['schemaVersion','operatorPairId','parentDeclaration','childDeclaration'];expected_order=['originId','expectedConfigId','expectedRole','expectedCapabilityBoundary','launchPlanId','expectedConfigPath','expectedConfigSha256']
assert list(aux['parentDeclaration'])==list(aux['childDeclaration'])==expected_order
provenance=load(mp);assert provenance['schemaVersion']=='we-operator-pair-provenance/v1' and provenance['operatorPairId']==c['operatorPairId'];assert isinstance(provenance['publishedAtUtc'],str) and provenance['publishedAtUtc'];inputrows=[]
for key,pth in [('specFile',Path(c['future_spec_path'])),('parentConfig',Path(c['inputs'][0]['future_path'])),('childConfig',Path(c['inputs'][1]['future_path']))]:
    actual=row(pth);r=provenance['inputs'][key];assert r['path']==actual['path'] and r['sha256']==actual['sha256'] and r['bytes']==actual['bytes'];assert isinstance(r['prior_stat'],dict) and isinstance(r['handle_stat'],dict);assert r['prior_stat']['size']==r['handle_stat']['size']==actual['bytes'];assert isinstance(r['prior_stat']['attributes'],int) and not isinstance(r['prior_stat']['attributes'],bool);inputrows.append(dict(input=key,actual=actual,captured_prior=r['prior_stat'],captured_handle=r['handle_stat']))
for inp in c['inputs']:
    role=inp['role'];cfg=json.loads(Path(inp['future_path']).read_bytes().decode('utf-8'));assert provenance['inputs'][role+'Declaration']==inp['prospective_descriptor7'];r=provenance['inputs'][role+'Config'];assert r['configId']==cfg['configId'] and r['role']==cfg['role'];assert summary[role+'ConfigSha256']==inp['raw_config']['sha256']
for key,path in [('bundleFile',bp),('stagingFile',sp)]:
    rr=row(path);pr=provenance[key];assert pr['path']==rr['path'] and pr['sha256']==rr['sha256'] and pr['bytes']==rr['bytes']
assert provenance['publisher']['scriptPath']==str(S) and provenance['publisher']['scriptSha256']==sha(S) and provenance['publisher']['pythonVersion']==sys.version
check(fxt['files']);controls();bs=statrow(bp);ss=statrow(sp);observed_identity_available=bool(bs['ino'] and ss['ino'] and bs['dev'] and ss['dev']);same_identity=bs['ino']==ss['ino'] and bs['dev']==ss['dev']
if observed_identity_available:assert same_identity and bs['nlink']>=2 and ss['nlink']>=2
write(cr/'CASE_RESULT.json',dict(at=now(),case_id=cid,status='SCOPED_NORMAL_PASS',publisher_tool=tool,summary=summary,preregistered_expected=row(EXPECTED),outputs=[row(z) for z in [bp,sp,hp,mp]],bundle_exact_bytes=True,BOM=False,trailing_newline=False,field_order_preserved=True,raw_inputs_unchanged=True,PairID=c['operatorPairId'],provenance_input_observations=inputrows,provenance=row(mp),hardlink_observation=dict(final_stat=bs,staging_stat=ss,identity_available=observed_identity_available,same_identity=same_identity,limit='Observed current link identity only; shared mutable bytes, no multifile transaction/crash or universal TOCTOU guarantee'),publisher_child_internals='UNOBSERVED_NO_CANDIDATE_INSTRUMENTATION',publishedAtUtc_observed=provenance['publishedAtUtc'],timestamp_world_authority=False,general_contract='REVISION_REQUIRED',native_Engine_adverse=0))
print(json.dumps(dict(case_id=cid,status='SCOPED_NORMAL_PASS',publisher_pid=p.pid,publisher_exit=p.returncode,publisher_stdout_bytes=len(stdout),publisher_stderr_bytes=len(stderr),expected_actual_bundle_sha=sha(bp),bundle_bytes=len(bundle),candidate_calls_this_case=1,result=row(cr/'CASE_RESULT.json')),ensure_ascii=False))
