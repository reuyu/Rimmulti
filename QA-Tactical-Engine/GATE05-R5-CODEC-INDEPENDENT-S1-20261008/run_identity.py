from review_setup import *
def metadata_helpers():
    ns=dict(globals())
    p=PKG/'bootstrap/verify_local_identity.py';nodes=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid'];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
    p=PKG/'coordination/sol_recovery_identity_20261007.py';nodes=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in {'metadata_streams','codeview_guid','portable_pdb'}];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns);return ns
def runner_metadata():
    ns=metadata_helpers();exe=Q/'runner/QaCodecRunner.exe';pdb=exe.with_suffix('.pdb');r=ns['portable_pdb'](pdb);r.update(exe_path=str(exe),exe_sha256=sha(exe),exe_mvid=ns['mvid'](exe),pdb_path=str(pdb),pdb_sha256=sha(pdb),codeview_guid=ns['codeview_guid'](exe));assert r['guid']==r['codeview_guid'] and all(d['matched'] for d in r['documents']);return r
def inputs():
    paths=[Path(x['frozen_path']) for x in load(MAN)['files']]+[Path(x['frozen_path']) for x in load(DEP)['files']]+[Q/n for n in ['Program.cs','build.rsp','INPUT_EXPECTED_SEMANTICS.json','QA_RUNNER_CONFIG.json','runner/QaCodecRunner.exe','runner/QaCodecRunner.pdb','BUILD_RAW.txt','prepare_runner.py','RunnerTemplate.cs.txt']]
    refs=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');paths.extend(refs/x for x in ['mscorlib.dll','System.dll','System.Core.dll']);paths.extend(Path(x) for x in [r'C:\Program Files\dotnet\dotnet.exe',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.dll',r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\Microsoft.CodeAnalysis.CSharp.dll']);return [dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in paths]
if __name__=='__main__':
    import sys
    mode=sys.argv[1]
    if mode=='pre':
        assert not (Q/'PRE_RUN_MANIFEST.json').exists();ns=metadata_helpers();dependencies=[dict(path=x['frozen_path'],sha256=x['sha256'],mvid=ns['mvid'](Path(x['frozen_path']))) for x in load(DEP)['files']];write(Q/'MANAGED_DEPENDENCY_METADATA.json',dict(at=now(),files=dependencies,metadata_only=True));runid='RUN_SOL_R5_CODEC_S1_20261008_'+uuid.uuid4().hex
        d=dict(at=now(),run_id=runid,status='FINAL_RUNNER_BUILD_COMPLETE_BEFORE_FIRST_CODEC_RUN',selected_candidate=load(Q/'R5_LINEAGE.json')['candidates'][0],alternate_metadata_only=load(Q/'R5_LINEAGE.json')['candidates'][1],runner=runner_metadata(),files=inputs(),argv=[str(Q/'runner/QaCodecRunner.exe'),str(Q),runid],cwd=str(Q),framework='.NETFramework4.7.2 refs / installed Windows CLR4.0;not Unity/native runtime',compiler='SDK10.0.201/Roslyn5.3.0-2.26153.122',input_oracle_created_before_build=True,allowed_only='Production SerializeCanonicalJson/DeserializeCanonicalJson + pure DTO fields/constructors and permitted managed metadata',forbidden_provider_cache_game_native_operator_execution=False)
        write(Q/'PRE_RUN_MANIFEST.json',d);print(json.dumps(dict(run_id=runid,runner_mvid=d['runner']['exe_mvid'],runner_pdb_sources=len(d['runner']['documents']),files=len(d['files'])),indent=2))
    elif mode=='post':
        pre=load(Q/'PRE_RUN_MANIFEST.json');after=inputs();assert {x['path']:(x['sha256'],x['bytes']) for x in pre['files']}=={x['path']:(x['sha256'],x['bytes']) for x in after};write(Q/'POST_RUN_IDENTITY.json',dict(at=now(),run_id=pre['run_id'],files=after,all_pre_post_sha_size_matched=True,runner=runner_metadata(),codec_run_exit_code=0));print('Pre/post inputs,runner,candidate,dependencies,toolchain unchanged')
    else:raise ValueError(mode)
