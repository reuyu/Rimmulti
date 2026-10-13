from review_setup import *
import sys,shutil
def helper_ns():
    p=ROOT/'QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008/run_identity.py';defs=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in {'metadata_helpers','runner_metadata','inputs'}];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_helper_definitions','exec'),ns);return ns
def pinned_files():
    rows=helper_ns()['inputs']();seen={x['path'].lower() for x in rows}
    # Only OS framework addresses from historical graph;fresh bytes are hashed now.
    for r in load(PREVQ/'ACTUAL_LOADED_MANAGED.json'):
        p=Path(r['path']) if r['path'] else None
        if p is not None and not str(p).lower().startswith(str(ROOT).lower()) and str(p).lower() not in seen:rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size));seen.add(str(p).lower())
    for name in ['review_setup.py','run_identity.py','BUILD_TOOL_PROOF.json','TOOLCHAIN_OBSERVED.json']:
        p=Q/name;rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    return rows
def runner_meta():return helper_ns()['runner_metadata']()
if __name__=='__main__':
    mode=sys.argv[1];stage=sys.argv[2]
    if mode=='pre':
        path=Q/f'PRE_RUN{stage}_MANIFEST.json';assert not path.exists()
        if stage=='2':
            arc=Q/'RUN1_ARCHIVE';assert not arc.exists();arc.mkdir();names=[p.name for p in Q.iterdir() if p.is_file() and (p.name in ['NORMAL_RESULTS.json','HISTORICAL65_FIELD_RESULTS.json','BOUNDARY_OBSERVATIONS.json','DTO_FIELD_METADATA.json','UPSTREAM_MANAGED_FIELD_METADATA.json','ACTUAL_LOADED_MANAGED.json','VERSION_MEANING_OBSERVATIONS.json','TARGETED_VERSION_RESULTS.json'] or any(p.name.endswith(s) for s in ['.version_checks.json','.fresh_original_checks.json','.admission_checks.json','.admission_observation.json','.canonical.json','.decoded.json','.semantic_checks.json','.sha256.txt','.transport.json','.transport_checks.json','.normalize_checks.json','.mutation_observation.json']))]
            for n in names:shutil.copy2(Q/n,arc/n)
            write(arc/'ARCHIVE_MANIFEST.json',dict(at=now(),files=[dict(path=str(arc/n),sha256=sha(arc/n),bytes=(arc/n).stat().st_size) for n in names],reason='Preserve first fresh R9 positive run before separately identified second process/culture determinism run'))
        runid='RUN_SOL_R9_CODEC_S1_20261009_'+uuid.uuid4().hex;culture='en-US' if stage=='1' else 'de-DE'
        write(path,dict(at=now(),run_id=runid,stage=stage,culture=culture,files=pinned_files(),runner=runner_meta(),selected=load(Q/'R9_LINEAGE.json')['candidates'][0],alternate_metadata_only=load(Q/'R9_LINEAGE.json')['candidates'][1],argv=[str(Q/'runner/QaCodecRunner.exe'),str(Q),runid,culture],cwd=str(Q),sdk='10.0.201',compiler='Roslyn5.3.0-2.26153.122',framework='net472 refs/Windows CLR4.0.30319.42000;pure managed,not game/native runtime',same_final_runner_build=stage=='2',scope='Fresh normal R9 pure codec/positive Validate/TryAdmit helper;no rejection/provider/cache/game/native/operator/old runner'))
        print(runid+' '+culture)
    elif mode=='post':
        pre=load(Q/f'PRE_RUN{stage}_MANIFEST.json');post=pinned_files();assert {x['path']:(x['sha256'],x['bytes']) for x in pre['files']}=={x['path']:(x['sha256'],x['bytes']) for x in post};tool=load(Q/f'RUN{stage}_TOOL_PROOF.json');observed=load(Q/'NORMAL_RESULTS.json');assert tool['exit_code']==(1 if observed['failed_assertions'] else 0);write(Q/f'POST_RUN{stage}_IDENTITY.json',dict(at=now(),run_id=pre['run_id'],files=post,runner=runner_meta(),all_pre_post_sha_size_matched=True,actual_tool_exit_code=tool['exit_code'],actual_failed_assertions=observed['failed_assertions'],tool_proof_path=str(Q/f'RUN{stage}_TOOL_PROOF.json'),tool_proof_sha256=sha(Q/f'RUN{stage}_TOOL_PROOF.json')));print('Fresh R9 pre/post identity matched; actual tool exit='+str(tool['exit_code'])+';normal semantic failed assertions='+str(observed['failed_assertions']))
    else:raise ValueError(mode)
