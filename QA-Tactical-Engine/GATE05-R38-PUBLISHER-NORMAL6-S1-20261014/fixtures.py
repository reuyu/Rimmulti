from common import *
controls();d=load(Q/'bootstrap.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']]);check(load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']);assert load(Q/'ACK_RETURN_TOOL_PROOF.json')['isError'] is False
assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json');ancestry(Q,leaf_dir=True);cases=load(EXPECTED)['cases'];allfiles=[];maps=[]
for c in cases:ancestry(Q/c['case_id'],new_leaf=True)
for c in cases:
    cr=Q/c['case_id'];os.mkdir(cr);ancestry(cr,leaf_dir=True);inputs=cr/'inputs';ancestry(inputs,new_leaf=True);os.mkdir(inputs);ancestry(inputs,leaf_dir=True);rr=[]
    for inp in c['inputs']:
        p=Path(inp['future_path']);assert p.parent==inputs;ancestry(p,new_leaf=True);b=literal(inp['raw_config'])
        with p.open('xb') as f:f.write(b)
        os.chmod(p,stat.S_IREAD);r=row(p);assert r['sha256']==inp['raw_config']['sha256'] and r['bytes']==inp['raw_config']['bytes'];rr.append(dict(role=inp['role'],file=r,stat=statrow(p)));allfiles.append(r)
    sp=Path(c['future_spec_path']);assert sp.parent==inputs;ancestry(sp,new_leaf=True)
    with sp.open('xb') as f:f.write(literal(c['spec_literal']))
    os.chmod(sp,stat.S_IREAD);sr=row(sp);assert sr['sha256']==c['spec_literal']['sha256'];allfiles.append(sr);assert all(statrow(r['path'])['attributes']&1 for r in allfiles)
    maps.append(dict(case_id=c['case_id'],raw_inputs=rr,spec=sr,spec_stat=statrow(sp),output_ancestry=ancestry(c['future_output_root'],new_leaf=True),candidate_calls=0))
write(Q/'FIXTURE_FREEZE_MANIFEST.json',dict(at=now(),files=allfiles,cases=maps,raw_config_files=12,spec_files=6,total_files=18,read_only=True,only_descriptor_delta='expectedConfigPath',oracle=row(EXPECTED),candidate_calls=0))
print(json.dumps(dict(status='FROZEN_ORIGINAL12_AND_SPEC6_EXCLUSIVE_READONLY',raw_config_files=12,spec_files=6,outputs_precreated=0,candidate_calls=0,manifest=row(Q/'FIXTURE_FREEZE_MANIFEST.json')),ensure_ascii=False))
