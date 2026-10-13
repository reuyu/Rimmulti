from common import *
import sys,subprocess,shutil,struct
from pe_pdb_reader import pe_metadata,portable_pdb,metadata_streams,table_header,guid,u16,u32
def mvid(path):
    b=path.read_bytes();pe=u32(b,60);assert b[pe:pe+4]==b'PE\0\0';opt=pe+24;magic=u16(b,opt);assert magic in (0x10b,0x20b);dd=opt+(96 if magic==0x10b else 112);ns=u16(b,pe+6);sections=opt+u16(b,pe+20)
    def rva(v):
        for k in range(ns):
            o=sections+k*40;vs,va,rs,rp=struct.unpack_from('<IIII',b,o+8)
            if va<=v<va+max(vs,rs):return rp+v-va
        raise ValueError('RVA outside sections')
    cli=rva(u32(b,dd+14*8));s=metadata_streams(b,rva(u32(b,cli+8)));t=s.get('#~',s.get('#-'));h,c,p=table_header(t);assert c.get(0)==1;sw=4 if h&1 else 2;gw=4 if h&2 else 2;idx=int.from_bytes(t[p+2+sw:p+2+sw+gw],'little');return guid(s['#GUID'],idx)
def runner_identity():
    exe=Q/'runner/QaPureRunner.exe';pdb=exe.with_suffix('.pdb');pe=pe_metadata(exe);pd=portable_pdb(pdb,{str(Q/'Harness/Program.cs').lower():Q/'Harness/Program.cs'})
    assert pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==1 and all(r['matched'] for r in pd['documents'])
    return dict(exe=row(exe),PDB=row(pdb),PE=pe,portable_PDB=pd)
def external_paths():
    cfg=load(Q/'TOOLCHAIN_OBSERVED.json');p=[Path(sys.executable),Path(cfg['dotnet']['path'])]+[Path(r['path']) for r in cfg['compiler_support']+cfg['exact_resolved_references']]
    for base in [Path(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_64'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_32')]:
        for name in ['System','System.Core','System.Xml','System.Numerics','System.Runtime.Serialization','System.Data','Microsoft.CSharp','System.Dynamic','System.ComponentModel.DataAnnotations','System.Configuration','System.Xml.Linq','System.Web','System.Net.Http']:
            if (base/name).exists():p+=list((base/name).glob('*/'+name+'.dll'))
    for base in [Path(r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319'),Path(r'C:\Windows\Microsoft.NET\Framework\v4.0.30319')]:
        p+=[base/'mscorlib.dll']
    return p
def input_paths():
    ps=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]+[NJ,MAN,BASELINE,DEP,WP,BINDING]
    ps+=[Path(r['path']) for r in load(BINDING)['independent_literal_oracles'].values()]
    unfinished={f'execution_pin.{x}' for x in ['STDOUT.txt','STDERR.txt','TOOL.json']}
    ps += [p for p in Q.rglob('*') if p.is_file() and p.name not in unfinished and not p.is_relative_to(Q/'runs')]
    ps+=external_paths();return list({str(p).lower():p for p in ps}.values())
def inventory(out):return [dict(**row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json']
def verify_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');assert d['files']==inventory(out) and d['file_count']==len(d['files']);return row(out/'OUTPUT_INVENTORY.json')
mode=sys.argv[1]
if mode=='pin':
    assert load(Q/'prepare.TOOL.json')['exit_code']==0 and load(Q/'static_review.TOOL.json')['exit_code']==0
    assert not (Q/'runner/QaPureRunner.exe').exists()
    assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')=='89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D'
    pins=[row(p) for p in input_paths()]
    write(Q/'BUILD_INPUTS.json',dict(at=now(),files=pins,input_count=len(pins),oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),callplan=row(Q/'PRIMARY_NORMAL_CALLPLAN.json'),compiler_plan=load(Q/'TOOLCHAIN_OBSERVED.json'),source=row(Q/'Harness/Program.cs'),compiler_attempts=0,runner_calls=0,production_builds=0,no_old_PASS_inheritance=True,in_progress_logger_excluded=['execution_pin.STDOUT.txt','execution_pin.STDERR.txt','execution_pin.TOOL.json']))
    print(json.dumps(dict(pins=len(pins),prospective=True,builds_runs=0)))
elif mode=='build':
    assert load(Q/'execution_pin.TOOL.json')['exit_code']==0
    assert not (Q/'BUILD_TOOL_PROOF.json').exists() and not (Q/'runner/QaPureRunner.exe').exists();check(load(Q/'BUILD_INPUTS.json')['files'])
    plan=load(Q/'TOOLCHAIN_OBSERVED.json');argv=plan['compiler_argv'];started=now()
    with (Q/'BUILD_STDOUT.raw').open('wb') as so,(Q/'BUILD_STDERR.raw').open('wb') as se:
        proc=subprocess.Popen(argv,cwd=plan['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se);pid=proc.pid;code=proc.wait()
    write(Q/'BUILD_TOOL_PROOF.json',dict(started_at=started,completed_at=now(),argv=argv,cwd=plan['cwd'],owned_compiler_child_pid=pid,exit_code=code,stdout=row(Q/'BUILD_STDOUT.raw'),stderr=row(Q/'BUILD_STDERR.raw'),compiler_attempts=1,production_candidate_builds=0,binary_first_full_streams=True))
    print(json.dumps(dict(compiler_attempts=1,exit_code=code,compiler_pid=pid)));sys.exit(code)
else:
    stage=int(sys.argv[2]);alloc=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][stage-1];out=Path(alloc['output_root']);prepath=Q/f'PRE_RUN{stage}_MANIFEST.json'
    if mode=='pre':
        assert load(Q/'execution_build.TOOL.json')['exit_code']==load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
        check(load(Q/'BUILD_INPUTS.json')['files']);assert not prepath.exists() and not any(out.iterdir())
        previous=None
        if stage==2:
            assert load(Q/'execution_post_1.TOOL.json')['exit_code']==0
            previous=verify_inventory(Path(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][0]['output_root']))
            write(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json',dict(at=now(),first_inventory=previous,unchanged=True))
        snaps=out/'input_snapshot';snaps.mkdir()
        for n in ['NORMAL_EXPECTED_ORACLE.json','PRIMARY_NORMAL_CALLPLAN.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json','BUILD_INPUTS.json','TEMPLATE_REBINDING.json']:shutil.copy2(Q/n,snaps/n)
        rows=load(Q/'BUILD_INPUTS.json')['files']+[row(p) for p in sorted(snaps.iterdir())]+[row(Q/n) for n in ['BUILD_INPUTS.json','BUILD_STDOUT.raw','BUILD_STDERR.raw','BUILD_TOOL_PROOF.json','execution_build.TOOL.json','runner/QaPureRunner.exe','runner/QaPureRunner.pdb']]
        pre=dict(at=now(),**alloc,files=rows,runner=runner_identity(),argv=[str(Q/'runner/QaPureRunner.exe'),str(Q),alloc['run_id'],alloc['culture'],str(out)],cwd=str(Q),previous_inventory=previous)
        write(prepath,pre);write(out/'PRE_RUN_INPUT_MANIFEST.json',pre);print(json.dumps(dict(stage=stage,pins=len(rows),runner_mvid=pre['runner']['PE']['mvid'],prospective=True)))
    elif mode=='run':
        assert load(Q/f'execution_pre_{stage}.TOOL.json')['exit_code']==0
        pre=load(prepath);check(pre['files']);assert not (out/'HOST_RUN_PROCESS_OBSERVATION.json').exists();started=now()
        with (out/'STDOUT.raw').open('wb') as so,(out/'STDERR.raw').open('wb') as se:
            proc=subprocess.Popen(pre['argv'],cwd=pre['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se);pid=proc.pid;code=proc.wait()
        write(out/'HOST_RUN_PROCESS_OBSERVATION.json',dict(started_at=started,completed_at=now(),run_id=pre['run_id'],owned_child_PID=pid,numeric_exit=code,argv=pre['argv'],cwd=pre['cwd'],stdout=row(out/'STDOUT.raw'),stderr=row(out/'STDERR.raw'),binary_first_full_streams=True,candidate_Process_calls=0))
        print(json.dumps(dict(stage=stage,PID=pid,exit_code=code)));sys.exit(code)
    elif mode=='post':
        pre=load(prepath);check(pre['files']);host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json');res=load(out/'NORMAL_RESULTS.json')
        assert load(Q/f'execution_run_{stage}.TOOL.json')['exit_code']==host['numeric_exit']==0 and res['failed_assertions']==0
        assert ctx['argv']==host['argv']==pre['argv'] and ctx['cwd']==host['cwd']==pre['cwd'] and ctx['culture']==pre['culture']
        pins={r['path'].lower():r for r in pre['files']};loaded=[]
        for phase in ['BEFORE','AFTER']:
            rows=load(out/f'ACTUAL_LOADED_MANAGED_{phase}.json')
            for r in rows:
                assert r['path'].lower() in pins and r['sha256']==pins[r['path'].lower()]['sha256'],r['path'];assert mvid(Path(r['path']))==r['mvid'];loaded.append(dict(phase=phase,**r,prospective_hash_and_independent_MVID_matched=True))
            selected=load(out/f'SELECTED_LOAD_{phase}.json');assert selected['path']==str(SELECTED) and selected['sha256']==sha(SELECTED) and selected['mvid']=='7d436c98-659a-4df1-a085-06fe9e55a0bc'
            assert selected['corelib_path'].lower() in pins and selected['corelib_sha256']==pins[selected['corelib_path'].lower()]['sha256'] and mvid(Path(selected['corelib_path']))==selected['corelib_mvid']
        assert res['selected_path']==str(SELECTED) and res['selected_sha256']==sha(SELECTED) and res['selected_mvid']=='7d436c98-659a-4df1-a085-06fe9e55a0bc'
        assert not [r for r in load(out/'TYPED_CHECKS.json') if not r['matched']]
        write(out/'ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),rows=loaded,all_matched=True,CLR_EnvironmentVersion=ctx['EnvironmentVersion'],native_CLR_modules='UNOBSERVED'))
        write(out/'POST_RUN_IDENTITY.json',dict(at=now(),files=pre['files'],runner=runner_identity(),prepost_all_matched=True,host=row(out/'HOST_RUN_PROCESS_OBSERVATION.json'),actual_exit=host['numeric_exit']))
        fs=inventory(out);write(out/'OUTPUT_INVENTORY.json',dict(at=now(),files=fs,file_count=len(fs),run_id=pre['run_id'],selfcycle_only_excluded=True));verify_inventory(out)
        if stage==2:
            first=Path(load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][0]['output_root']);after=verify_inventory(first);assert after==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory'];write(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json',dict(at=now(),first_inventory=after,unchanged=True))
        print(json.dumps(dict(stage=stage,assertions=len(res['results']),failures=0,typed_rows=len(load(out/'TYPED_CHECKS.json')),loaded_phase_rows=len(loaded),pins=len(pre['files']),outputs=len(fs),actual_exit=host['numeric_exit'])))
    else:raise ValueError(mode)
