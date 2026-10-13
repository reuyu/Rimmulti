from run_identity import *
import shutil,sys
def extra_inputs():
    rows=inputs();seen={x['path'].lower() for x in rows}
    for x in load(Q/'RUN1_ARCHIVE/ACTUAL_LOADED_MANAGED.json'):
        if x['path'] and x['path'].lower() not in seen:
            p=Path(x['path']);rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size));seen.add(str(p).lower())
    return rows
if __name__=='__main__':
    if sys.argv[1]=='pre':
        archive=Q/'RUN1_ARCHIVE';assert not archive.exists();archive.mkdir()
        outputs=['PRE_RUN_MANIFEST.json','POST_RUN_IDENTITY.json','RUN_RAW.txt','NORMAL_RESULTS.json','HISTORICAL65_FIELD_RESULTS.json','BOUNDARY_OBSERVATIONS.json','DTO_FIELD_METADATA.json','UPSTREAM_MANAGED_FIELD_METADATA.json','ACTUAL_LOADED_MANAGED.json']
        outputs += [p.name for p in Q.iterdir() if p.is_file() and any(p.name.endswith(x) for x in ['.canonical.json','.decoded.json','.semantic_checks.json','.sha256.txt'])]
        for name in outputs:shutil.copy2(Q/name,archive/name)
        write(archive/'ARCHIVE_MANIFEST.json',dict(at=now(),files=[dict(path=str(archive/n),sha256=sha(archive/n),bytes=(archive/n).stat().st_size) for n in outputs],reason='Retain first normal codec run before second fresh dependency-complete run; no candidate/runner/input rebuild or change',limitation='First POST_RUN_IDENTITY exit0 was inferred from successful managed completion, not saved numeric tool return; second run captures actual return'))
        assert not (Q/'PRE_RUN2_MANIFEST.json').exists();runid='RUN_SOL_R5_CODEC_S1_20261008_'+uuid.uuid4().hex
        write(Q/'PRE_RUN2_MANIFEST.json',dict(at=now(),run_id=runid,files=extra_inputs(),runner=runner_metadata(),argv=[str(Q/'runner/QaCodecRunner.exe'),str(Q),runid],cwd=str(Q),same_final_build_and_oracle_as_run1=True,reason='Explicit pre-run binding of resolved CLR framework dependencies and actual numeric exit capture',codec_scope_only=True));print(runid)
    elif sys.argv[1]=='post':
        pre=load(Q/'PRE_RUN2_MANIFEST.json');after=extra_inputs();assert {x['path']:(x['sha256'],x['bytes']) for x in pre['files']}=={x['path']:(x['sha256'],x['bytes']) for x in after};tool=load(Q/'RUN2_TOOL_PROOF.json');assert tool['exit_code']==0
        write(Q/'POST_RUN2_IDENTITY.json',dict(at=now(),run_id=pre['run_id'],files=after,runner=runner_metadata(),all_pre_post_sha_size_matched=True,actual_tool_exit_code=tool['exit_code'],tool_proof_path=str(Q/'RUN2_TOOL_PROOF.json'),tool_proof_sha256=sha(Q/'RUN2_TOOL_PROOF.json')));print('Second-run pre/post exact dependencies unchanged; actual tool exit0 captured')
    else:raise ValueError(sys.argv[1])
