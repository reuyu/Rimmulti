from review_setup import *
import subprocess,sys
if __name__=='__main__':
    assert not (Q/'runner/QaPureRunner.exe').exists() and not (Q/'BUILD_TOOL_PROOF.json').exists()
    for r in load(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')['pins']:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes']
    argv=[r'C:\Program Files\dotnet\dotnet.exe',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll','@'+str(Q/'build.rsp')]
    started=now()
    with (Q/'BUILD_STDOUT.txt').open('wb') as so,(Q/'BUILD_STDERR.txt').open('wb') as se:
        proc=subprocess.Popen(argv,cwd=str(ROOT),stdin=subprocess.DEVNULL,stdout=so,stderr=se)
        pid=proc.pid;code=proc.wait()
    write(Q/'BUILD_TOOL_PROOF.json',dict(started_at=started,completed_at=now(),argv=argv,cwd=str(ROOT),owned_compiler_child_pid=pid,exit_code=code,stdout=row(Q/'BUILD_STDOUT.txt'),stderr=row(Q/'BUILD_STDERR.txt'),build_attempts=1,production_candidate_builds=0,full_streams_before_output=True))
    print(json.dumps(dict(exit_code=code,compiler_pid=pid,stdout=row(Q/'BUILD_STDOUT.txt'),stderr=row(Q/'BUILD_STDERR.txt'))))
    sys.exit(code)

