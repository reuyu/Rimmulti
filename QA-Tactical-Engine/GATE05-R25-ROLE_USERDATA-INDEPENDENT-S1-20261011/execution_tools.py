from review_setup import *
import ast,sys,shutil,subprocess
def helpers():
    ns=dict(globals())
    for p,names in [(PKG/'bootstrap/verify_local_identity.py',{'mvid'}),(PKG/'coordination/sol_recovery_identity_20261007.py',{'metadata_streams','codeview_guid','portable_pdb'})]:
        nodes=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(ast.Module(body=nodes,type_ignores=[]),'metadata_only_AST_functions','exec'),ns)
    return ns
def runner_meta():
    h=helpers();exe=Q/'runner/QaPureRunner.exe';pdb=exe.with_suffix('.pdb');d=h['portable_pdb'](pdb);assert d['guid']==h['codeview_guid'](exe) and all(r['matched'] for r in d['documents']);return dict(exe=row(exe),pdb=row(pdb),mvid=h['mvid'](exe),portable_pdb=d)
def pin_paths():
    paths=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    paths += [Q/n for n in ['bootstrap.py','review_setup.py','verify_three_span_scope.py','verify_scope.old_schema_failure.py.txt','prepare_runner.py','Program.cs.txt','Program.cs','execution_tools.py','build_once.py','build.rsp','NORMAL_EXPECTED_ORACLE.json','QA_RUNNER_CONFIG.json','RUN_ALLOCATION_PLAN.json','ORACLE_BEFORE_BUILD.json','R25_FROZEN_LINEAGE.json','THREE_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json','THREE_SPAN_SCOPE_DIFF.txt','TOOLCHAIN_OBSERVED.json']]
    paths += [MAN,DEP,BASELINE,PKG/'WP_QA_ENGINE_GATE05_R25_ROLE_USERDATA_INDEPENDENT_S1.md',ADMISSION,Path(sys.executable),Path(r'C:\Program Files\dotnet\dotnet.exe')]
    paths += list(Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore').glob('*.dll'))
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');paths += [fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll']]
    old=ROOT/'QA-Tactical-Engine/GATE05-R23-IDENTIFIER_MAPPING-INDEPENDENT-S1-20261011';out=Path(load(old/'PRE_RUN1_MANIFEST.json')['output_root'])
    paths += [Path(r['path']) for r in load(out/'ACTUAL_LOADED_MANAGED.json') if not Path(r['path']).resolve().is_relative_to(ROOT.resolve())]
    for base in [Path(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_64')]:
        for name in ['System','System.Core','System.Xml','System.Numerics','System.Runtime.Serialization','System.Data','Microsoft.CSharp','System.Dynamic','System.ComponentModel.DataAnnotations']:
            if (base/name).exists():paths += list((base/name).glob('*/'+name+'.dll'))
    return list({str(p).lower():p for p in paths}.values())
def check_rows(rows):
    for r in rows:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(p)
def inventory(out):return [dict(row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json']
def verify_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');assert d['files']==inventory(out) and d['file_count']==len(d['files']);return row(out/'OUTPUT_INVENTORY.json')
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='pin':
        assert not (Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json').exists() and not (Q/'runner/QaPureRunner.exe').exists()
        o=load(Q/'NORMAL_EXPECTED_ORACLE.json');assert len(o['cases'])==4 and o['ToSnapshot_per_run']==4 and o['SelectUserData_per_run']==8
        write(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json',dict(at=now(),pins=[row(p) for p in pin_paths()],oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),source=row(Q/'Program.cs'),scope='Normal4 ToSnapshot4 Select8 only;publicsnapshot policy-UTC graph/normalownededits;nofixturepathIO/global/receipt/native/adverse',outputderived=False,candidate_calls_beforepin=0))
        print('Normal4 input/oracle/source/compiler/framework/frozen99-managed4 prospectivepins beforeonlybuild/calls')
    else:
        stage=int(sys.argv[2]);allocation=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][stage-1];out=Path(allocation['output_root']);prePath=Q/f'PRE_RUN{stage}_MANIFEST.json'
        if mode=='pre':
            assert load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0 and not prePath.exists() and not any(out.iterdir());check_rows(load(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')['pins'])
            previous=None
            if stage==2:
                first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);previous=verify_inventory(first);write(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json',dict(at=now(),first_inventory=previous,allfirstoutputs_unchanged=True))
            snaps=out/'input_snapshot';snaps.mkdir()
            for n in ['NORMAL_EXPECTED_ORACLE.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json','EXECUTION_ADMISSION_BEFORE_BUILD.json']:shutil.copy2(Q/n,snaps/n)
            rows=[row(p) for p in pin_paths()]+[row(p) for p in sorted(snaps.iterdir())]+[row(Q/'runner/QaPureRunner.exe'),row(Q/'runner/QaPureRunner.pdb'),row(Q/'BUILD_STDOUT.txt'),row(Q/'BUILD_STDERR.txt'),row(Q/'BUILD_TOOL_PROOF.json'),row(Q/'BUILD_INVOCATION_TOOL_PROOF.json')]
            pre=dict(at=now(),**allocation,files=rows,runner=runner_meta(),argv=[str(Q/'runner/QaPureRunner.exe'),str(Q),allocation['run_id'],allocation['culture'],str(out)],cwd=str(Q),previous_inventory=previous);write(prePath,pre);write(out/'PRE_RUN_INPUT_MANIFEST.json',pre);print(json.dumps(dict(stage=stage,run_id=pre['run_id'],pins=len(rows))))
        elif mode=='run':
            pre=load(prePath);check_rows(pre['files']);assert not (out/'HOST_RUN_PROCESS_OBSERVATION.json').exists();exe=Path(pre['argv'][0]);assert exe.resolve()==(Q/'runner/QaPureRunner.exe').resolve()
            started=now()
            with (out/'STDOUT.txt').open('wb') as so,(out/'STDERR.txt').open('wb') as se:
                child=subprocess.Popen(pre['argv'],cwd=pre['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se);pid=child.pid;code=child.wait()
            context=load(out/'ACTUAL_PROCESS_CONTEXT.json') if (out/'ACTUAL_PROCESS_CONTEXT.json').exists() else None
            write(out/'HOST_RUN_PROCESS_OBSERVATION.json',dict(started_at=started,completed_at=now(),run_id=pre['run_id'],owned_child_pid=pid,numeric_exit=code,argv=pre['argv'],cwd=pre['cwd'],observed_culture=context['culture'] if context else 'UNOBSERVED',stdout=row(out/'STDOUT.txt'),stderr=row(out/'STDERR.txt'),only_owned_newPURErunner_started=True,CSharpProcessqueries=0));print(json.dumps(dict(run_id=pre['run_id'],pid=pid,exit=code,culture=context['culture'] if context else None)));print((out/'STDOUT.txt').read_text(encoding='utf-8-sig')[-500:]);sys.exit(code)
        elif mode=='post':
            pre=load(prePath);check_rows(pre['files']);host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');tool=load(out/'RUN_TOOL_PROOF.json');ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json');res=load(out/'NORMAL_RESULTS.json');assert tool['exit_code']==host['numeric_exit']==(1 if res['failed_assertions'] else 0);assert ctx['argv']==host['argv']==pre['argv'] and ctx['cwd']==host['cwd']==pre['cwd'] and ctx['culture']==host['observed_culture']==pre['culture']
            pins={r['path'].lower():r for r in pre['files']};h=helpers();loaded=[]
            for r in load(out/'ACTUAL_LOADED_MANAGED.json'):
                assert r['path'].lower() in pins and r['sha256']==pins[r['path'].lower()]['sha256'];assert h['mvid'](Path(r['path']))==r['mvid'];loaded.append(dict(r,prepin_SHA_andindependent_PE_mvid_matched=True))
            cfg=load(Q/'QA_RUNNER_CONFIG.json');assert res['selected_sha256']==cfg['selected']['sha256'] and res['selected_mvid']==cfg['selected_mvid']
            write(out/'ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),files=loaded,all_matched=True));write(out/'POST_RUN_IDENTITY.json',dict(at=now(),files=pre['files'],runner=runner_meta(),all_prepost_matched=True,host=row(out/'HOST_RUN_PROCESS_OBSERVATION.json'),tool=row(out/'RUN_TOOL_PROOF.json')))
            fs=inventory(out);write(out/'OUTPUT_INVENTORY.json',dict(at=now(),run_id=pre['run_id'],files=fs,file_count=len(fs),selfcycleexcludedonly=True,all_recursive_outputs=True));verify_inventory(out)
            if stage==2:
                first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);after=verify_inventory(first);assert after==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory'];write(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json',dict(first_inventory=after,allfirstoutputs_unchanged=True))
            print(json.dumps(dict(run_id=pre['run_id'],assertions=len(res['results']),failures=res['failed_assertions'],pins=len(pre['files']),loaded=len(loaded),outputs=len(fs),actualexit=host['numeric_exit'])))
        else:raise ValueError(mode)
