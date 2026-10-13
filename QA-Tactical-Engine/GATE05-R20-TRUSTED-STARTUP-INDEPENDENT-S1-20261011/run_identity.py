from review_setup import *
import sys,shutil
def metadata_helpers():
    ns=dict(globals())
    for p,names in [(PKG/'bootstrap/verify_local_identity.py',{'mvid'}),(PKG/'coordination/sol_recovery_identity_20261007.py',{'metadata_streams','codeview_guid','portable_pdb'})]:
        defs=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(ast.Module(body=defs,type_ignores=[]),'read_only_PE_PDB_functions_only','exec'),ns)
    return ns
def runner_metadata():
    ns=metadata_helpers();exe=Q/'runner/QaPureRunner.exe';pdb=exe.with_suffix('.pdb');r=ns['portable_pdb'](pdb);r.update(exe_path=str(exe),exe_sha256=sha(exe),exe_mvid=ns['mvid'](exe),pdb_path=str(pdb),pdb_sha256=sha(pdb),codeview_guid=ns['codeview_guid'](exe));assert r['guid']==r['codeview_guid'] and all(x['matched'] for x in r['documents']);return r
def inputs():
    paths=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    names=['bootstrap.py','review_setup.py','prepare_runner.py','RunnerTemplate.cs.txt','Program.cs','pin_admission.py','SnapshotControls.cs.txt','prepare_receipt_oracle.py','ReceiptControls.cs.txt','RECEIPT_EXPECTED_SEMANTICS.json','ORACLE_BEFORE_BUILD.json','INPUT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','QA_RUNNER_CONFIG.json','EXECUTION_ADMISSION_BEFORE_BUILD.json','RUN_ALLOCATION_PLAN.json','run_identity.py','host_launch.py','build.rsp','runner/QaPureRunner.exe','runner/QaPureRunner.pdb','build_once.py','BUILD_STDOUT.txt','BUILD_STDERR.txt','BUILD_INVOCATION_TOOL_PROOF.json','BUILD_TOOL_PROOF.json','TOOLCHAIN_OBSERVED.json','R20_FROZEN_LINEAGE.json'];paths.extend(Q/n for n in names);paths.extend((Q/'fixtures').glob('*'));paths.extend((Q/'normal_configs').glob('*'))
    paths.extend(p for p in (ROOT/'scratch/EngineGate05R4/RuntimeCopy').rglob('*') if p.is_file());paths.extend([MAN,DEP,BASELINE,ADMISSION,PKG/'WP_QA_ENGINE_GATE05_R20_TRUSTED_STARTUP_INDEPENDENT_S1.md',PKG/'coordination/MASTER_R17_QA_BASELINE_AUTHORIZED_SOURCE_RECONCILIATION_20261010.json'])
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');paths.extend(fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll'])
    paths.extend(Path(p) for p in [r'C:\Program Files\dotnet\dotnet.exe',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.CSharp.dll'])
    prior=ROOT/'QA-Tactical-Engine/GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010';oldout=Path(load(prior/'PRE_RUN1_MANIFEST.json')['output_root'])
    paths.extend(Path(r['path']) for r in load(oldout/'ACTUAL_LOADED_MANAGED.json') if r['path'] and not Path(r['path']).resolve().is_relative_to(ROOT.resolve()))
    for base in [Path(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_64'),Path(r'C:\Windows\Microsoft.NET\assembly\GAC_32')]:
        for n in ['System','System.Core','System.Xml','System.Numerics','System.Runtime.Serialization','System.Data','Microsoft.CSharp','System.Dynamic','System.ComponentModel.DataAnnotations']:
            if (base/n).exists():paths.extend((base/n).glob('*/'+n+'.dll'))
    paths.extend([Q/'prepare_receipt_oracle.py',Q/'RECEIPT_EXPECTED_SEMANTICS.json',Q/'ReceiptControls.cs.txt'])
    unique={str(p).lower():p for p in paths};return [row(p) for p in sorted(unique.values(),key=lambda p:str(p).lower())]
def inventory(out):return [dict(row(p),relative_path=p.relative_to(out).as_posix()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_INVENTORY.json']
def verify_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');assert d['files']==inventory(out) and d['file_count']==len(d['files']);return row(out/'OUTPUT_INVENTORY.json')
if __name__=='__main__':
    mode,stage=sys.argv[1:3];assert stage in ['1','2']
    if mode=='pre':
        assert not (Q/f'PRE_RUN{stage}_MANIFEST.json').exists() and load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
        previous=None
        if stage=='2':
            first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);previous=verify_inventory(first);write(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json',dict(at=now(),first_inventory=previous,allfirstoutputs_unchanged=True,second_not_started=True))
        allocation=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][int(stage)-1];out=Path(allocation['output_root']);assert out.exists() and not any(out.iterdir());snap=out/'input_snapshot';snap.mkdir()
        for n in ['INPUT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','QA_RUNNER_CONFIG.json','EXECUTION_ADMISSION_BEFORE_BUILD.json','ORACLE_BEFORE_BUILD.json','RECEIPT_EXPECTED_SEMANTICS.json']:shutil.copy2(Q/n,snap/n)
        shutil.copytree(Q/'fixtures',snap/'fixtures');shutil.copytree(Q/'normal_configs',snap/'normal_configs');pins=inputs()+[row(p) for p in sorted(snap.rglob('*')) if p.is_file()]
        pre=dict(at=now(),run_id=allocation['run_id'],culture=allocation['culture'],output_root=str(out),files=pins,runner=runner_metadata(),selected=load(Q/'R20_FROZEN_LINEAGE.json')['candidates'][0],argv=[str(Q/'runner/QaPureRunner.exe'),str(Q),allocation['run_id'],allocation['culture'],str(out)],cwd=str(Q),actual_build_exit=0,host_only_PID_scope=row(PKG/'WP_QA_ENGINE_GATE05_R20_TRUSTED_STARTUP_INDEPENDENT_S1.md'),first_inventory_verified=previous,CSharp_allProcessqueries_andVerifyProcessIdentity=0)
        write(Q/f'PRE_RUN{stage}_MANIFEST.json',pre);write(out/'PRE_RUN_INPUT_MANIFEST.json',pre);print(json.dumps(dict(run_id=pre['run_id'],culture=pre['culture'],output_root=str(out),pinned_files=len(pins))))
    elif mode=='post':
        pre=load(Q/f'PRE_RUN{stage}_MANIFEST.json');out=Path(pre['output_root']);observed=load(out/'NORMAL_RESULTS.json');context=load(out/'ACTUAL_PROCESS_CONTEXT.json');host=load(out/'HOST_RUN_PROCESS_OBSERVATION.json');tool=load(out/'RUN_TOOL_PROOF.json')
        assert context['run_id']==observed['run_id']==host['run_id']==tool['run_id']==pre['run_id'];assert context['argv']==host['argv']==pre['argv'] and context['cwd']==host['cwd']==pre['cwd'] and context['culture']==host['observed_culture']==pre['culture']
        assert host['owned_child_pid']>0 and host['numeric_exit']==tool['exit_code']==(1 if observed['failed_assertions'] else 0) and tool['exit_code']==host['numeric_exit']
        pins=inputs()+[row(p) for p in sorted((out/'input_snapshot').rglob('*')) if p.is_file()];assert {r['path'].lower():(r['sha256'],r['bytes']) for r in pins}=={r['path'].lower():(r['sha256'],r['bytes']) for r in pre['files']}
        pin={r['path'].lower():r for r in pins};loaded=[]
        for r in load(out/'ACTUAL_LOADED_MANAGED.json'):
            assert r['path'] and r['path'].lower() in pin,str(r);assert r['sha256']==pin[r['path'].lower()]['sha256'];loaded.append(dict(r,pre_pin_matched=True))
        assert observed['selected_mvid']==pre['selected']['mvid'] and observed['selected_sha256']==pre['selected']['dll_sha256']
        write(out/'ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),all_loaded_prepin_matched=True,files=loaded));write(out/'POST_RUN_IDENTITY.json',dict(at=now(),run_id=pre['run_id'],files=pins,runner=runner_metadata(),all_prepost_sha_size_matched=True,host_pid=host['owned_child_pid'],actual_numeric_exit=tool['exit_code'],failures=observed['failed_assertions'],host=row(out/'HOST_RUN_PROCESS_OBSERVATION.json'),tool=row(out/'RUN_TOOL_PROOF.json')))
        files=inventory(out);write(out/'OUTPUT_INVENTORY.json',dict(at=now(),run_id=pre['run_id'],root=str(out),file_count=len(files),files=files,every_generated_output_recursive=True,excluded_self_only=True));verify_inventory(out)
        if stage=='2':
            first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);after=verify_inventory(first);assert after==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory'];write(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json',dict(at=now(),first_inventory=after,all_firstoutputs_unchanged=True))
        write(Q/f'RUN{stage}_INVENTORY_RECEIPT.json',dict(at=now(),run_id=pre['run_id'],inventory=row(out/'OUTPUT_INVENTORY.json'),pinned_files=len(pins),loaded_managed=len(loaded),output_file_count=len(files),actual_exit=tool['exit_code']))
        print(json.dumps(dict(run_id=pre['run_id'],pinned_files=len(pins),loaded_managed=len(loaded),output_count=len(files),actual_exit=tool['exit_code'],assertions=len(observed['results']),failures=observed['failed_assertions'])))
    else:raise ValueError(mode)
