from review_setup import *
import sys,shutil
def metadata_helpers():
    ns=dict(globals())
    for p,names in [(PKG/'bootstrap/verify_local_identity.py',{'mvid'}),(PKG/'coordination/sol_recovery_identity_20261007.py',{'metadata_streams','codeview_guid','portable_pdb'})]:
        defs=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_readonly_functions','exec'),ns)
    return ns
def runner_metadata():
    ns=metadata_helpers();exe=Q/'runner/QaCodecRunner.exe';pdb=exe.with_suffix('.pdb');r=ns['portable_pdb'](pdb);r.update(exe_path=str(exe),exe_sha256=sha(exe),exe_mvid=ns['mvid'](exe),pdb_path=str(pdb),pdb_sha256=sha(pdb),codeview_guid=ns['codeview_guid'](exe));assert r['guid']==r['codeview_guid'] and all(x['matched'] for x in r['documents']);return r
def inputs():
    paths=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    names=['bootstrap_review.py','review_setup.py','prepare_runner.py','CacheChecks.cs.txt','prepare_graph.py','ObservedProvider.cs.txt','RUN_ALLOCATION_PLAN.json','Program.cs','RunnerTemplate.cs.txt','build.rsp','INPUT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','API_AND_GENERATION_RECONCILIATION.json','ORACLE_BEFORE_BUILD.json','PROSPECTIVE_SOURCE_EXECUTION_SCOPE.json','QA_RUNNER_CONFIG.json','runner/QaCodecRunner.exe','runner/QaCodecRunner.pdb','BUILD_RAW.txt','BUILD_TOOL_PROOF.json','TOOLCHAIN_OBSERVED.json','R14_LINEAGE.json','run_identity.py']
    paths.extend(Q/n for n in names);paths.extend((Q/'policy_references').glob('*.json'));paths.extend([ADMISSION,MAN,DEP,BASELINE,PREP/'NORMAL_LIFECYCLE_REFERENCE_ORACLE.json',PKG/'WP_QA_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION_INDEPENDENT_S1.md'])
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');paths.extend(fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll'])
    paths.extend(Path(p) for p in [r'C:\Program Files\dotnet\dotnet.exe',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.CSharp.dll'])
    previous_output=Path(load(PREVQ/'PRE_RUN1_MANIFEST.json')['output_root'])
    for r in load(previous_output/'ACTUAL_LOADED_MANAGED.json'):
        if r['path'] and not Path(r['path']).resolve().is_relative_to(ROOT.resolve()):paths.append(Path(r['path']))
    unique={str(p).lower():p for p in paths};return [row(p) for p in sorted(unique.values(),key=lambda p:str(p).lower())]
def inventory(out):
    files=[]
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.name!='OUTPUT_INVENTORY.json':
            assert p.resolve().is_relative_to(out.resolve());files.append(dict(row(p),relative_path=p.relative_to(out).as_posix()))
    return files
def verify_inventory(out):
    d=load(out/'OUTPUT_INVENTORY.json');assert d['files']==inventory(out) and d['file_count']==len(d['files']);return row(out/'OUTPUT_INVENTORY.json')
if __name__=='__main__':
    mode,stage=sys.argv[1:3];assert stage in ['1','2']
    if mode=='pre':
        assert not (Q/f'PRE_RUN{stage}_MANIFEST.json').exists() and load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
        previous=None
        if stage=='2':
            first=load(Q/'PRE_RUN1_MANIFEST.json');previous=verify_inventory(Path(first['output_root']));assert load(Path(first['output_root'])/'POST_RUN_IDENTITY.json')['all_pre_post_sha_size_matched'];write(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json',dict(at=now(),first_inventory=previous,first_output_unchanged=True,actual_second_run_not_started=True))
        allocation=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'][int(stage)-1];runid=allocation['run_id'];culture=allocation['culture'];out=Path(allocation['output_root']);assert out.exists() and allocation['allocated_validated_before_final_build_calls']
        snap=out/'input_snapshot'
        if snap.exists():
            assert stage=='1' and (Q/'PRE_EXECUTION_METADATA_SETUP_FAILURE.json').exists() and set(p.name for p in out.iterdir())=={'input_snapshot'}
            for p in snap.rglob('*'):
                if p.is_file():assert sha(p)==sha(Q/p.relative_to(snap)) and p.stat().st_size==(Q/p.relative_to(snap)).stat().st_size
        else:
            assert not any(out.iterdir());snap.mkdir()
            for n in ['INPUT_EXPECTED_SEMANTICS.json','REFERENCE_DTO_SCHEMA.json','API_AND_GENERATION_RECONCILIATION.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json']:shutil.copy2(Q/n,snap/n)
            shutil.copytree(Q/'policy_references',snap/'policy_references')
        pins=inputs()+[row(p) for p in sorted(snap.rglob('*')) if p.is_file()]
        pre=dict(at=now(),run_id=runid,stage=stage,culture=culture,output_root=str(out),files=pins,runner=runner_metadata(),selected=load(Q/'R14_LINEAGE.json')['candidates'][0],alternate_metadata_only=load(Q/'R14_LINEAGE.json')['candidates'][1],argv=[str(Q/'runner/QaCodecRunner.exe'),str(Q),runid,culture,str(out)],cwd=str(Q),actual_build_exit=0,observed_toolchain=load(Q/'TOOLCHAIN_OBSERVED.json'),source_oracle_before_build_calls=True,first_inventory_verified_before_this_run=previous,output_policy='Allgeneratedfilesenumeratedrecursively;each uniqueimmutable processdir;no sharedruntimeoutputs')
        write(Q/f'PRE_RUN{stage}_MANIFEST.json',pre);write(out/'PRE_RUN_INPUT_MANIFEST.json',pre);print(json.dumps(dict(run_id=runid,culture=culture,output_root=str(out),pinned_files=len(pins))))
    elif mode=='post':
        pre=load(Q/f'PRE_RUN{stage}_MANIFEST.json');out=Path(pre['output_root']);tool=load(out/'RUN_TOOL_PROOF.json');observed=load(out/'NORMAL_RESULTS.json');context=load(out/'ACTUAL_PROCESS_CONTEXT.json');assert observed['run_id']==context['run_id']==pre['run_id'] and context['argv']==pre['argv'] and context['cwd']==pre['cwd'] and context['output_directory']==str(out)
        assert tool['exit_code']==(1 if observed['failed_assertions'] else 0) and tool['run_id']==pre['run_id'] and tool['culture']==pre['culture'] and pre['run_id'] in tool['cmd']
        pins=inputs()+[row(p) for p in sorted((out/'input_snapshot').rglob('*')) if p.is_file()];assert {r['path']:(r['sha256'],r['bytes']) for r in pins}=={r['path']:(r['sha256'],r['bytes']) for r in pre['files']}
        pin={r['path'].lower():r for r in pins};loaded=[]
        for r in load(out/'ACTUAL_LOADED_MANAGED.json'):
            assert r['path'] and r['path'].lower() in pin,str(r);assert r['sha256']==pin[r['path'].lower()]['sha256'];loaded.append(dict(r,pre_pin_matched=True))
        write(out/'ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),run_id=pre['run_id'],all_loaded_pre_pin_matched=True,files=loaded))
        write(out/'POST_RUN_IDENTITY.json',dict(at=now(),run_id=pre['run_id'],files=pins,runner=runner_metadata(),all_pre_post_sha_size_matched=True,actual_tool_exit_code=tool['exit_code'],actual_failed_assertions=observed['failed_assertions'],tool_proof=row(out/'RUN_TOOL_PROOF.json'),raw=row(out/'RAW_CONSOLE.txt'),context=row(out/'ACTUAL_PROCESS_CONTEXT.json')))
        files=inventory(out);write(out/'OUTPUT_INVENTORY.json',dict(at=now(),run_id=pre['run_id'],root=str(out),file_count=len(files),files=files,recursive_every_generatedfile=True,no_hardcoded_central_selection=True,excluded_self='OUTPUT_INVENTORY.json only;ownSHA externallybound',process_completed_before_inventory=True));verify_inventory(out)
        if stage=='2':
            first=Path(load(Q/'PRE_RUN1_MANIFEST.json')['output_root']);before=load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory'];after=verify_inventory(first);assert before==after;write(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json',dict(at=now(),first_inventory=after,all_first_outputs_unchanged=True))
        write(Q/f'RUN{stage}_INVENTORY_RECEIPT.json',dict(at=now(),run_id=pre['run_id'],output_inventory=row(out/'OUTPUT_INVENTORY.json'),actual_exit=tool['exit_code'],all_prepost_pins=len(pins),loaded_files=len(loaded),full_generated_file_count=len(files)))
        print(json.dumps(dict(run_id=pre['run_id'],pinned_files=len(pins),loaded_files=len(loaded),output_file_count=len(files),actual_exit=tool['exit_code'],assertions=len(observed['results']),failures=observed['failed_assertions'])))
    else:raise ValueError(mode)
