from review_setup import *
import sys,subprocess
if __name__=='__main__':
    stage=sys.argv[1];assert stage in ['1','2'];pre=load(Q/f'PRE_RUN{stage}_MANIFEST.json');out=Path(pre['output_root']);assert not (out/'HOST_RUN_PROCESS_OBSERVATION.json').exists()
    exe=Path(pre['argv'][0]);assert exe.resolve()==(Q/'runner/QaPureRunner.exe').resolve() and exe.resolve().is_relative_to(Q.resolve()) and sha(exe)==pre['runner']['exe_sha256']
    assert sha(PKG/'MASTER_R17_QA_HOST_LAUNCHER_TELEMETRY_SCOPE_CLARIFICATION_20261010.md')=='B35BF9836E70B162571730D301CF2452F7E01F080568F80C69D0FD47414BAB59'
    started=now()
    with (out/'STDOUT.txt').open('wb') as stdout,(out/'STDERR.txt').open('wb') as stderr:
        child=subprocess.Popen(pre['argv'],cwd=pre['cwd'],stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
        pid=child.pid;code=child.wait()
    context=load(out/'ACTUAL_PROCESS_CONTEXT.json') if (out/'ACTUAL_PROCESS_CONTEXT.json').exists() else None
    write(out/'HOST_RUN_PROCESS_OBSERVATION.json',dict(started_at=started,completed_at=now(),run_id=pre['run_id'],owned_child_pid=pid,numeric_exit=code,argv=pre['argv'],cwd=pre['cwd'],requested_culture=pre['culture'],observed_culture=context['culture'] if context else 'UNOBSERVED',only_new_pinned_QA_runner_launched=True,host_static_launcher=row(Q/'host_launch.py'),CSharp_Process_identity_queries=0,host_arbitrary_process_enumeration_or_native_launcher=False,stdout=row(out/'STDOUT.txt'),stderr=row(out/'STDERR.txt')))
    print(json.dumps(dict(run_id=pre['run_id'],owned_child_pid=pid,numeric_exit=code,observed_culture=context['culture'] if context else 'UNOBSERVED')));print((out/'STDOUT.txt').read_text(encoding='utf-8-sig')[-2200:]);sys.exit(code)
