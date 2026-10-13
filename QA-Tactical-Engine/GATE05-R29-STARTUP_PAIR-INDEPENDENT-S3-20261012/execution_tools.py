"""New own QA host/compiler/runner evidence stages; gated invocation only."""
from review_setup import *
import sys,shutil,subprocess
def helpers():
    ns=dict(globals())
    for p,names in [(PKG/'bootstrap/verify_local_identity.py',{'mvid'}),(PKG/'coordination/sol_recovery_identity_20261007.py',{'metadata_streams','codeview_guid','portable_pdb'})]:
        nodes=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p)+'#metadata-functions-only','exec'),ns)
    return ns
def runner_meta():
    h=helpers();exe=Q/'runner/QaPureRunner.exe';pdb=exe.with_suffix('.pdb');d=h['portable_pdb'](pdb)
    assert d['guid']==h['codeview_guid'](exe) and all(x['matched'] for x in d['documents'])
    return dict(exe=row(exe),pdb=row(pdb),mvid=h['mvid'](exe),portable_pdb=d)
def check_rows(rows):
    for r in rows:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(p)
def pin_paths():
    paths=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    paths += [MAN,DEP,BASELINE,WP,ADMISSION,PREP/'PRE_RUN_EXPECTED_ORACLE.json',CAP/'PROSPECTIVE_CAPTURE_ORACLE.json']
    paths += [Q/n for n in ['review_setup.py','PREFLIGHT_PROOF.json','INITIAL_TOOL_EXIT_PROOF.json','ACK_INITIAL.json','ACK.json','R29_FROZEN_LINEAGE.json','prepare_runner.py','Harness/Program.cs','NORMAL_EXPECTED_ORACLE.json','PRIMARY_NORMAL_CALLPLAN.json','QA_RUNNER_CONFIG.json','RUN_ALLOCATION_PLAN.json','ORACLE_BEFORE_BUILD.json','TOOLCHAIN_OBSERVED.json','build.rsp','log_stage.py','execution_tools.py','build_once.py']]
    paths += [Q/n for n in ['static_review.py','static_review.TOOL.json','static_review.STDOUT.txt','static_review.STDERR.txt','STATIC_STOP_NOTICE_TOOL_PROOF.json','PROPOSED_STATIC_SELECTOR_CORRECTION.patch','RECOVERY_OUTPUT_ENCODING_STOP_20261012.json','RECOVERY_ENCODING_STOP_NOTICE_TOOL_PROOF.json','recovery_utf8_r1.py','RECOVERY_UTF8_R1_TOOL.json','RECOVERY_UTF8_R1_AUDIT.json','RECOVERY_UTF8_R1_STDOUT.txt','RECOVERY_UTF8_R1_STDERR.txt','log_stage_r1.py','selector_copy_preflight.py','selector_copy_preflight.TOOL.json','selector_copy_preflight.STDOUT.txt','selector_copy_preflight.STDERR.txt','STATIC_SELECTOR_R1_COPY_PROOF.json','STATIC_SELECTOR_R1_INDEPENDENT_EXACT_DIFF.txt','static_review_selector_r1.py','static_review_selector_r1.TOOL.json','static_review_selector_r1.STDOUT.txt','static_review_selector_r1.STDERR.txt','STATIC_SOURCE_SCOPE_BEFORE_BUILD.json']]
    paths += [PKG/'MASTER_R29_S3_STATIC_SELECTOR_R1_AUTHORIZATION_20261012.md',PKG/'MASTER_R29_S3_RECOVERY_OUTPUT_ENCODING_AUTHORIZATION_20261012.md',ROOT/'Dispatcher/Tools/MASTER_R29_S3_STATIC_SELECTOR_R1_TEMPLATE.py',PKG/'coordination/MASTER_R29_S3_STATIC_SELECTOR_R1_EXACT_DIFF_20261012.txt',PKG/'coordination/MASTER_R29_S3_STATIC_STOP_INITIAL_PROSPECTIVE_PRESERVATION_20261012.json',TASK/'MASTER_R29_AUTHORIZED_SOURCE_SCOPE.json']
    paths += [Path(r['path']) for r in load(PREP/'PROSPECTIVE_INPUT_LITERAL_MANIFEST.json')['files']]
    paths += [Path(sys.executable),Path(r'C:\Program Files\dotnet\dotnet.exe')]
    paths += list(Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore').glob('*.dll'))
    paths += list(Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore').glob('*.json'))
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    paths += [fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll']]
    prior=ROOT/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012'
    alloc=load(prior/'RUN_ALLOCATION_PLAN.json')['allocations'][0]
    paths += [Path(r['path']) for r in load(Path(alloc['output_root'])/'ACTUAL_LOADED_MANAGED.json') if not Path(r['path']).resolve().is_relative_to(ROOT.resolve())]
    for base in [Path(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_64')]:
        for name in ['System','System.Core','System.Xml','System.Numerics','System.Runtime.Serialization','System.Data','Microsoft.CSharp','System.Dynamic','System.ComponentModel.DataAnnotations','System.Configuration','System.Xml.Linq','System.Web','System.Net.Http']:
            if (base/name).exists():paths+=list((base/name).glob('*/'+name+'.dll'))
    return list({str(p).lower():p for p in paths}.values())
def inventory(out):
    return [dict(row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json']
def verify_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');assert d['files']==inventory(out) and d['file_count']==len(d['files'])
    return row(out/'OUTPUT_INVENTORY.json')
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='pin':
        assert not (Q/'runner/QaPureRunner.exe').exists() and not (Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json').exists()
        o=load(Q/'NORMAL_EXPECTED_ORACLE.json');assert len(o['normal_pairs'])==4 and len(o['pair_cases'])==6
        assert load(Q/'selector_copy_preflight.TOOL.json')['exit_code']==load(Q/'static_review_selector_r1.TOOL.json')['exit_code']==0
        witness=load(Q/'STATIC_SOURCE_SCOPE_BEFORE_BUILD.json')
        assert len(witness['findings'])==3 and len(witness['changed_six_spans'])==6 and witness['outside_total_bytes']==234431
        for r in witness['changed_six_spans']+[witness['additional_source_only_parser_boundaries']['anchor']]:
            b=Path(r['file']['path']).read_bytes()[r['byte_start']:r['byte_end']]
            assert b.decode('utf-8')==r['raw_utf8'] and hashlib.sha256(b).hexdigest().upper()==r['sha256']
        for f in witness['findings']:
            for r in f['anchors']:
                b=Path(r['file']['path']).read_bytes()[r['byte_start']:r['byte_end']]
                assert b.decode('utf-8')==r['raw_utf8'] and hashlib.sha256(b).hexdigest().upper()==r['sha256']
        assert Path(witness['publisher_source']['path']).read_text(encoding='utf-8-sig')==witness['whole_publisher_text']
        for r in load(PKG/'coordination/MASTER_R29_S3_STATIC_STOP_INITIAL_PROSPECTIVE_PRESERVATION_20261012.json')['files']:
            check_rows([r])
        write(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json',dict(at=now(),pins=[row(p) for p in pin_paths()],oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),source=row(Q/'Harness/Program.cs'),scope='R29S3 pure pair6/fulltypedraw-copy and Capture4/15 data regression only, no globals/native/Process/publisher/invalid',outputderived=False,candidate_calls_beforepin=0,builds_beforepin=0))
        print(json.dumps(dict(pins=len(pin_paths()),pair6=True,Capture4=True,builds=0,calls=0)))
    else:
        stage=int(sys.argv[2]);allocation=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][stage-1];out=Path(allocation['output_root']);prepath=Q/f'PRE_RUN{stage}_MANIFEST.json'
        if mode=='pre':
            assert load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0 and load(Q/'build_once.TOOL.json')['exit_code']==0
            assert not prepath.exists() and not any(out.iterdir());check_rows(load(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')['pins'])
            previous=None
            if stage==2:
                first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);previous=verify_inventory(first)
                write(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json',dict(at=now(),first_inventory=previous,unchanged=True))
            snaps=out/'input_snapshot';snaps.mkdir()
            for n in ['NORMAL_EXPECTED_ORACLE.json','PRIMARY_NORMAL_CALLPLAN.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json','EXECUTION_ADMISSION_BEFORE_BUILD.json']:shutil.copy2(Q/n,snaps/n)
            rows=[row(p) for p in pin_paths()]+[row(p) for p in sorted(snaps.iterdir())]+[row(Q/'runner/QaPureRunner.exe'),row(Q/'runner/QaPureRunner.pdb'),row(Q/'BUILD_STDOUT.txt'),row(Q/'BUILD_STDERR.txt'),row(Q/'BUILD_TOOL_PROOF.json'),row(Q/'build_once.TOOL.json')]
            pre=dict(at=now(),**allocation,files=rows,runner=runner_meta(),argv=[str(Q/'runner/QaPureRunner.exe'),str(Q),allocation['run_id'],allocation['culture'],str(out)],cwd=str(Q),previous_inventory=previous)
            write(prepath,pre);write(out/'PRE_RUN_INPUT_MANIFEST.json',pre)
            print(json.dumps(dict(stage=stage,run_id=pre['run_id'],pins=len(rows),runner_mvid=pre['runner']['mvid'])))
        elif mode=='run':
            pre=load(prepath);check_rows(pre['files']);assert not (out/'HOST_RUN_PROCESS_OBSERVATION.json').exists()
            assert Path(pre['argv'][0]).resolve()==(Q/'runner/QaPureRunner.exe').resolve()
            started=now()
            with (out/'STDOUT.txt').open('wb') as so,(out/'STDERR.txt').open('wb') as se:
                child=subprocess.Popen(pre['argv'],cwd=pre['cwd'],stdin=subprocess.DEVNULL,stdout=so,stderr=se)
                pid=child.pid;code=child.wait()
            ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json') if (out/'ACTUAL_PROCESS_CONTEXT.json').exists() else None
            write(out/'HOST_RUN_PROCESS_OBSERVATION.json',dict(started_at=started,completed_at=now(),run_id=pre['run_id'],owned_child_pid=pid,numeric_exit=code,argv=pre['argv'],cwd=pre['cwd'],culture=ctx['culture'] if ctx else 'UNOBSERVED',stdout=row(out/'STDOUT.txt'),stderr=row(out/'STDERR.txt'),only_owned_new_QA_runner=True,CSharp_Process_calls=0))
            print(json.dumps(dict(stage=stage,run_id=pre['run_id'],pid=pid,exit_code=code,culture=ctx['culture'] if ctx else None)))
            sys.exit(code)
        elif mode=='post':
            pre=load(prepath);check_rows(pre['files']);host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json')
            tool=load(Q/f'execution_tools_run_{stage}.TOOL.json')
            ctx=load(out/'ACTUAL_PROCESS_CONTEXT.json');res=load(out/'NORMAL_RESULTS.json')
            assert tool['exit_code']==host['numeric_exit']==0 and res['failed_assertions']==0
            assert ctx['argv']==host['argv']==pre['argv'] and ctx['cwd']==host['cwd']==pre['cwd'] and ctx['culture']==host['culture']==pre['culture']
            pins={r['path'].lower():r for r in pre['files']};h=helpers();loaded=[]
            for r in load(out/'ACTUAL_LOADED_MANAGED.json'):
                assert r['path'].lower() in pins and r['sha256']==pins[r['path'].lower()]['sha256'],r['path']
                assert h['mvid'](Path(r['path']))==r['mvid'];loaded.append(dict(r,prepin_sha_and_independent_PE_mvid_matched=True))
            cfg=load(Q/'QA_RUNNER_CONFIG.json');assert res['selected_sha256']==cfg['selected']['sha256'] and res['selected_mvid']==cfg['selected_mvid']
            assert not [r for r in load(out/'TYPED_CHECKS.json') if not r['matched']]
            write(out/'ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),files=loaded,all_matched=True,EnvironmentVersion=ctx.get('EnvironmentVersion','UNOBSERVED'),native_CLR_modules='UNOBSERVED'))
            write(out/'POST_RUN_IDENTITY.json',dict(at=now(),files=pre['files'],runner=runner_meta(),all_prepost_matched=True,host=row(out/'HOST_RUN_PROCESS_OBSERVATION.json'),tool=row(Q/f'execution_tools_run_{stage}.TOOL.json')))
            fs=inventory(out);write(out/'OUTPUT_INVENTORY.json',dict(at=now(),run_id=pre['run_id'],files=fs,file_count=len(fs),only_selfcycleexcluded=True))
            verify_inventory(out)
            if stage==2:
                first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);after=verify_inventory(first)
                assert after==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory']
                write(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json',dict(first_inventory=after,unchanged=True))
            print(json.dumps(dict(run_id=pre['run_id'],assertions=len(res['results']),failures=0,typed_rows=len(load(out/'TYPED_CHECKS.json')),pins=len(pre['files']),loaded=len(loaded),outputs=len(fs),actual_exit=host['numeric_exit'])))
        else:raise ValueError(mode)

