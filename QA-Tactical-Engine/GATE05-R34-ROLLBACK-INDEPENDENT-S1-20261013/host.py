from common import *
from normal_tools import mvid,runner_identity,external_paths,inventory,verify_inventory
import sys,shutil,subprocess

def pin_paths():
    paths=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    paths += [MAN,BASELINE,WP,BINDING,DEP,NJ]+[Path(r['path']) for r in load(BINDING)['literal_oracles'].values()]
    unfinished={f'host_pin.{s}' for s in ['STDOUT.txt','STDERR.txt','TOOL.json']}
    paths += [p for p in Q.rglob('*') if p.is_file() and p.relative_to(Q).as_posix() not in unfinished and not p.is_relative_to(Q/'runs')]+external_paths()
    return list({str(p).lower():p for p in paths}.values())

def build():
    assert load(Q/'host_pin.TOOL.json')['exit_code']==0 and not (Q/'BUILD_TOOL_PROOF.json').exists() and not (Q/'runner/QaPureRunner.exe').exists();check(load(Q/'BUILD_INPUTS.json')['files'])
    plan=load(Q/'TOOLCHAIN_OBSERVED.json');started=now()
    with (Q/'BUILD_STDOUT.raw').open('wb') as so,(Q/'BUILD_STDERR.raw').open('wb') as se:
        p=subprocess.Popen(plan['compiler_argv'],cwd=plan['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se);pid=p.pid;code=p.wait()
    write(Q/'BUILD_TOOL_PROOF.json',dict(started_at=started,completed_at=now(),argv=plan['compiler_argv'],cwd=plan['cwd'],owned_compiler_child_pid=pid,exit_code=code,stdout=row(Q/'BUILD_STDOUT.raw'),stderr=row(Q/'BUILD_STDERR.raw'),compiler_attempts=1,production_candidate_builds=0,binary_first_full_streams=True));print(json.dumps(dict(compiler_attempts=1,exit_code=code,PID=pid)));sys.exit(code)

def pre(stage):
    assert load(Q/'host_build.TOOL.json')['exit_code']==load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
    alloc=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][stage-1];out=Path(alloc['output_root']);check(load(Q/'BUILD_INPUTS.json')['files']);assert not (Q/f'PRE_RUN{stage}_MANIFEST.json').exists() and not any(out.iterdir());previous=None
    if stage==2:
        assert load(Q/'host_post_1.TOOL.json')['exit_code']==0;previous=verify_inventory(Path(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][0]['output_root']));write(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json',dict(at=now(),first_inventory=previous,unchanged=True))
    snap=out/'input_snapshot';snap.mkdir()
    for n in ['NORMAL_EXPECTED_ORACLE.json','PRIMARY_NORMAL_CALLPLAN.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json','BUILD_INPUTS.json','TEMPLATE_REBINDING.json']:shutil.copy2(Q/n,snap/n)
    rows=load(Q/'BUILD_INPUTS.json')['files']+[row(p) for p in sorted(snap.iterdir())]+[row(Q/n) for n in ['BUILD_INPUTS.json','BUILD_STDOUT.raw','BUILD_STDERR.raw','BUILD_TOOL_PROOF.json','host_build.TOOL.json','runner/QaPureRunner.exe','runner/QaPureRunner.pdb']]
    ctx=dict(at=now(),**alloc,files=rows,runner=runner_identity(),argv=[str(Q/'runner/QaPureRunner.exe'),str(Q),alloc['run_id'],alloc['culture'],str(out)],cwd=str(Q),previous_inventory=previous);write(Q/f'PRE_RUN{stage}_MANIFEST.json',ctx);write(out/'PRE_RUN_INPUT_MANIFEST.json',ctx);print(json.dumps(dict(stage=stage,pins=len(rows),runner_mvid=ctx['runner']['PE']['mvid'],prospective=True)))

def run(stage):
    assert load(Q/f'host_pre_{stage}.TOOL.json')['exit_code']==0
    ctx=load(Q/f'PRE_RUN{stage}_MANIFEST.json');out=Path(ctx['output_root']);check(ctx['files']);assert not (out/'HOST_RUN_PROCESS_OBSERVATION.json').exists();started=now()
    with (out/'STDOUT.raw').open('wb') as so,(out/'STDERR.raw').open('wb') as se:
        p=subprocess.Popen(ctx['argv'],cwd=ctx['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se);pid=p.pid;code=p.wait()
    write(out/'HOST_RUN_PROCESS_OBSERVATION.json',dict(started_at=started,completed_at=now(),run_id=ctx['run_id'],owned_child_PID=pid,numeric_exit=code,argv=ctx['argv'],cwd=ctx['cwd'],stdout=row(out/'STDOUT.raw'),stderr=row(out/'STDERR.raw'),binary_first_full_streams=True,candidate_Process_calls=0));print(json.dumps(dict(stage=stage,PID=pid,exit_code=code)));sys.exit(code)

def post(stage):
    pre=load(Q/f'PRE_RUN{stage}_MANIFEST.json');out=Path(pre['output_root']);check(pre['files']);host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json');res=load(out/'NORMAL_RESULTS.json')
    assert load(Q/f'host_run_{stage}.TOOL.json')['exit_code']==host['numeric_exit']==0 and res['failed_assertions']==0
    assert ctx['argv']==host['argv']==pre['argv'] and ctx['cwd']==host['cwd']==pre['cwd'] and ctx['culture']==pre['culture']
    pins={r['path'].lower():r for r in pre['files']};loaded=[]
    for phase,filename in [('BEFORE','ACTUAL_LOADED_MANAGED_BEFORE.json'),('AFTER','ACTUAL_LOADED_MANAGED_AFTER.json'),('FINAL','ACTUAL_LOADED_MANAGED.json')]:
        rows=load(out/filename)
        for r in rows:assert r['path'].lower() in pins and r['sha256']==pins[r['path'].lower()]['sha256'];assert mvid(Path(r['path']))==r['mvid'];loaded.append(dict(phase=phase,**r,prospective_hash_and_independent_MVID_matched=True))
    for phase in ['BEFORE','AFTER']:
        s=load(out/f'SELECTED_LOAD_{phase}.json');assert s['path']==str(SELECTED) and s['sha256']==sha(SELECTED) and s['mvid']=='7b08d3f4-27de-4685-b61b-8a312708a496';assert s['corelib_path'].lower() in pins and s['corelib_sha256']==pins[s['corelib_path'].lower()]['sha256'] and mvid(Path(s['corelib_path']))==s['corelib_mvid']
    assert res['selected_path']==str(SELECTED) and res['selected_sha256']==sha(SELECTED) and res['selected_mvid']=='7b08d3f4-27de-4685-b61b-8a312708a496';assert not [r for r in load(out/'TYPED_CHECKS.json') if not r['matched']]
    write(out/'ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),rows=loaded,all_matched=True,CLR_EnvironmentVersion=ctx['EnvironmentVersion'],native_CLR_modules='UNOBSERVED'))
    write(out/'POST_RUN_IDENTITY.json',dict(at=now(),files=pre['files'],runner=runner_identity(),prepost_all_matched=True,host=row(out/'HOST_RUN_PROCESS_OBSERVATION.json'),actual_exit=host['numeric_exit']))
    fs=inventory(out);write(out/'OUTPUT_INVENTORY.json',dict(at=now(),files=fs,file_count=len(fs),run_id=pre['run_id'],selfcycle_only_excluded=True));verify_inventory(out)
    if stage==2:
        first=Path(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][0]['output_root']);after=verify_inventory(first);assert after==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory'];write(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json',dict(at=now(),first_inventory=after,unchanged=True))
    print(json.dumps(dict(stage=stage,assertions=len(res['results']),failures=0,typed_rows=len(load(out/'TYPED_CHECKS.json')),loaded_rows=len(loaded),pins=len(pre['files']),outputs=len(fs),actual_exit=host['numeric_exit'])))
mode=sys.argv[1]
if mode=='pin':
    assert load(Q/'prepare.TOOL.json')['exit_code']==load(Q/'plumbing.TOOL.json')['exit_code']==load(Q/'static_r1.TOOL.json')['exit_code']==0
    assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')=='89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D' and not (Q/'runner/QaPureRunner.exe').exists()
    rows=[row(p) for p in pin_paths()]
    write(Q/'BUILD_INPUTS.json',dict(at=now(),files=rows,input_count=len(rows),oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),callplan=row(Q/'PRIMARY_NORMAL_CALLPLAN.json'),source=row(Q/'Harness/Program.cs'),toolchain=load(Q/'TOOLCHAIN_OBSERVED.json'),compiler_attempts=0,runner_calls=0,production_builds=0,old_PASS_inherited=False,unfinished_logger_exclusions=['host_pin.STDOUT.txt','host_pin.STDERR.txt','host_pin.TOOL.json']))
    print(json.dumps(dict(pins=len(rows),prospective=True,builds_runs=0)))
elif mode=='build':build()
elif mode in ['pre','run','post']:
    stage=int(sys.argv[2]);assert stage in [1,2];globals()[mode](stage)
else:raise ValueError(mode)
