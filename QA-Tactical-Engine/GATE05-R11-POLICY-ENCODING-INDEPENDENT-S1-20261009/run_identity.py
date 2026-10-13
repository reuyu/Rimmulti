from review_setup import *
import sys,shutil

def metadata_helpers():
    ns=dict(globals())
    for p,names in [(PKG/'bootstrap/verify_local_identity.py',{'mvid'}),(PKG/'coordination/sol_recovery_identity_20261007.py',{'metadata_streams','codeview_guid','portable_pdb'})]:
        nodes=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'metadata_only_definitions','exec'),ns)
    return ns

def runner_metadata():
    ns=metadata_helpers();exe=Q/'runner/QaCodecRunner.exe';pdb=exe.with_suffix('.pdb');r=ns['portable_pdb'](pdb)
    r.update(exe_path=str(exe),exe_sha256=sha(exe),exe_mvid=ns['mvid'](exe),pdb_path=str(pdb),pdb_sha256=sha(pdb),codeview_guid=ns['codeview_guid'](exe))
    assert r['guid']==r['codeview_guid'] and all(d['matched'] for d in r['documents']);return r

def inputs():
    paths=[Path(x['frozen_path']) for x in load(MAN)['files']]+[Path(x['frozen_path']) for x in load(DEP)['files']]
    names=['Program.cs','build.rsp','INPUT_EXPECTED_SEMANTICS.json','QA_RUNNER_CONFIG.json','ORACLE_BEFORE_BUILD.json','runner/QaCodecRunner.exe','runner/QaCodecRunner.pdb','BUILD_RAW.txt','BUILD_TOOL_PROOF.json','TOOLCHAIN_OBSERVED.json','prepare_runner.py','RunnerTemplate.cs.txt','PolicyChecks.cs.txt','review_setup.py','run_identity.py','R11_LINEAGE.json']
    paths.extend(Q/n for n in names);paths.extend((Q/'policy_references').glob('*.json'));paths.extend([SELECTION,ADMISSION])
    refs=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');paths.extend(refs/x for x in ['mscorlib.dll','System.dll','System.Core.dll'])
    paths.extend(Path(x) for x in [r'C:\Program Files\dotnet\dotnet.exe',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.CSharp.dll'])
    previous=ROOT/'QA-Tactical-Engine/GATE05-R9-VERSION-MEANING-INDEPENDENT-S1-20261009/ACTUAL_LOADED_MANAGED.json'
    for r in load(previous):
        if r['path']:
            p=Path(r['path'])
            if not p.resolve().is_relative_to(ROOT.resolve()):paths.append(p)
    unique={str(p).lower():p for p in paths};return [dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(unique.values(),key=lambda p:str(p).lower())]

if __name__=='__main__':
    mode,stage=sys.argv[1:3]
    if mode=='pre':
        assert stage in ['1','2'] and not (Q/f'PRE_RUN{stage}_MANIFEST.json').exists();assert load(Q/'BUILD_TOOL_PROOF.json')['exit_code']==0
        if stage=='2':
            pre1=load(Q/'PRE_RUN1_MANIFEST.json');assert load(Q/'POST_RUN1_IDENTITY.json')['all_pre_post_sha_size_matched']
            arc=Q/'RUN1_ARCHIVE';assert not arc.exists();arc.mkdir()
            inp=load(Q/'INPUT_EXPECTED_SEMANTICS.json');prefixes=tuple(n+'.' for n in set(inp['cases'])|set(inp['policy_cases']))
            central={'NORMAL_RESULTS.json','HISTORICAL65_FIELD_RESULTS.json','BOUNDARY_OBSERVATIONS.json','DTO_FIELD_METADATA.json','UPSTREAM_MANAGED_FIELD_METADATA.json','ACTUAL_LOADED_MANAGED.json','VERSION_MEANING_OBSERVATIONS.json','TARGETED_VERSION_RESULTS.json','POLICY_ENCODING_RESULTS.json'}
            names=[p.name for p in Q.iterdir() if p.is_file() and (p.name in central or p.name.startswith(prefixes))]
            for n in names:shutil.copy2(Q/n,arc/n)
            write(arc/'ARCHIVE_MANIFEST.json',dict(at=now(),run_id=pre1['run_id'],files=[dict(path=str(arc/n),sha256=sha(arc/n),bytes=(arc/n).stat().st_size) for n in names],reason='Preserve first positive fresh process before distinct second culture process; no old runner execution'))
        runid='RUN_SOL_R11_POLICY_ENCODING_S1_20261009_'+uuid.uuid4().hex;culture='en-US' if stage=='1' else 'de-DE'
        write(Q/f'PRE_RUN{stage}_MANIFEST.json',dict(at=now(),run_id=runid,stage=stage,culture=culture,files=inputs(),runner=runner_metadata(),selected=load(Q/'R11_LINEAGE.json')['candidates'][0],alternate_metadata_only=load(Q/'R11_LINEAGE.json')['candidates'][1],argv=[str(Q/'runner/QaCodecRunner.exe'),str(Q),runid,culture],cwd=str(Q),actual_build_exit=load(Q/'BUILD_TOOL_PROOF.json')['exit_code'],observed_toolchain=load(Q/'TOOLCHAIN_OBSERVED.json'),scope='Fresh current-version normal policy declaration/codec helpers only',input_oracle_before_final_build=True,same_final_runner_build=stage=='2'))
        print(runid+' '+culture)
    elif mode=='post':
        pre=load(Q/f'PRE_RUN{stage}_MANIFEST.json');post=inputs();assert {r['path']:(r['sha256'],r['bytes']) for r in pre['files']}=={r['path']:(r['sha256'],r['bytes']) for r in post}
        tool=load(Q/f'RUN{stage}_TOOL_PROOF.json');observed=load(Q/'NORMAL_RESULTS.json');assert observed['run_id']==pre['run_id'];assert tool['exit_code']==(1 if observed['failed_assertions'] else 0)
        pin={r['path'].lower():r for r in pre['files']};loaded=[]
        for r in load(Q/'ACTUAL_LOADED_MANAGED.json'):
            assert r['path'] and r['path'].lower() in pin,str(r)
            assert r['sha256']==pin[r['path'].lower()]['sha256'];loaded.append(dict(r,pre_pin_matched=True))
        write(Q/f'RUN{stage}_ACTUAL_LOADED_PREPIN_BINDING.json',dict(at=now(),run_id=pre['run_id'],all_loaded_pre_pin_matched=True,files=loaded))
        write(Q/f'POST_RUN{stage}_IDENTITY.json',dict(at=now(),run_id=pre['run_id'],files=post,runner=runner_metadata(),all_pre_post_sha_size_matched=True,actual_tool_exit_code=tool['exit_code'],actual_failed_assertions=observed['failed_assertions'],tool_proof_path=str(Q/f'RUN{stage}_TOOL_PROOF.json'),tool_proof_sha256=sha(Q/f'RUN{stage}_TOOL_PROOF.json')))
        print(json.dumps(dict(run_id=pre['run_id'],pinned_files=len(post),loaded_files=len(loaded),actual_exit=tool['exit_code'],assertions=len(observed['results']),failures=observed['failed_assertions'])))
    else:raise ValueError(mode)
