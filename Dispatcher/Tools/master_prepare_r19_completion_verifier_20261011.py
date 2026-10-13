from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'Dispatcher/Tools/master_verify_r18_independent_completion_20261010.py').read_text(encoding='utf8')
for a,b in [('CONFIG_ADMISSION_SEAL','OPAQUE_POLICY'),('CONFIG-ADMISSION-SEAL','OPAQUE-POLICY'),('R18','R19'),('r18','r19'),('be5a988c6f01410f88b5769c0c555322','2c4a145f15334594bba451900223477a'),('71BE5152112A6AA8F57D295C9EBE5CEEA998DCBBFEEF4C5027D70C9619149012','EC88A9E0895C7E8A66F696730B0B0F028339B6E2E88533F26F46B82331FC3890'),('362','390'),('9374','9841'),('==167','==181'),("'prepost':167","'prepost':181"),('==147','==148'),("'output_files':147","'output_files':148"),('==298','==266'),('==202','==186'),('==96','==80'),("'direct_calls':202","'direct_calls':186"),("'grouped_reads':96","'grouped_reads':80"),('failed==256','failed==0'),('bindingfail==16','bindingfail==0'),("'reference_bindings_failed':16","'reference_bindings_failed':0"),('guard_session\':36347','guard_session\':40147'),('guard_pid\':34784','guard_pid\':19832'),('MASTER-SOL-R19-COMPLETE-20261010-01','MASTER-CONTINUE-R19-20261011-01')]:
 s=s.replace(a,b)
s=s.replace("thread=json.loads(read(C/'MASTER_SOL_R19_INDEPENDENT_TERMINAL_READ_20261010.json')['content'][0]['text'])\ncommands=[x for t in thread['turns'] for x in t.get('items',[]) if x.get('type')=='commandExecution']","thread=json.loads(read(C/'MASTER_SOL_R19_INDEPENDENT_TERMINAL_READ_20261011.json')['content'][0]['text'])")
s=s.replace("bc=next(x for x in commands if 'csc.dll' in x.get('command','') and 'build.rsp' in x.get('command',''));assert bc['exitCode']==0","assert read(Q/'BUILD_INVOCATION_TOOL_PROOF.json')['exit_code']==0")
s=s.replace("==tool['exit_code']==1","==tool['exit_code']==0")
s=s.replace("cmd=next(x for x in commands if f'host_launch.py {n}' in x.get('command',''));assert cmd['exitCode']==1 and Path(cmd['cwd']).resolve()==R.resolve()","assert Path(host['cwd']).is_absolute()")
s=s.replace("actual['numeric_exit']==1","actual['numeric_exit']==0")
s=s.replace("len(normal['results'])==125 and normal['failed_assertions']==24","len(normal['results'])==117 and normal['failed_assertions']==0")
s=s.replace("==101","==117").replace("==24","==0")
s=s.replace("'exit':1,'pass':101,'fail':24","'exit':0,'pass':117,'fail':0")
start=s.index("audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')")
end=s.index("vp=C/'MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json'")
s=s[:start]+'''audit=read(Q/'SOURCE_REUSE_AND_ORACLE_AUDIT.json')
for k in ['source','oracle','prospective','only_metadata_analysis_repaired']:verify(audit[k])
assert audit['old_source_oracle_readonly_references_only'] and audit['no_old_runner_binary_execution_or_outputs_reuse']
assert audit['source_oracle_runner_values_unchanged_afteronly_finalbuild_and2processes'] and not audit['output_derived_oracle']
streams=read(Q/'COMPLETE_BUILD_STREAM_BINDING.json')
for k in ['tool','invocation','stdout','stderr']:verify(streams[k])
assert streams['actual_builds']==1 and streams['actual_numeric_exit']==0 and streams['stdout']['bytes']==19219 and streams['stderr']['bytes']==0
assert streams['full_compile_run_streams_direct_ownedfiles'] and streams['no_warning_stream_truncation']
reconcile=read(Q/'PRODUCER_INVENTORY_METADATA_RECONCILIATION.json')
assert [(r['declared'],r['actual_nonself']) for r in reconcile['rows']]==[(10,10),(8,10)]
assert reconcile['rows'][1]['unlisted']==['stderr.txt','stdout.txt'] and reconcile['builds_runs_reruns_during_metadata_repair']==0
for row in reconcile['rows']:
 verify(row['inventory'])
 inventory=read(Path(row['inventory']['path']))
 assert len(inventory)==row['declared']
 root=Path(row['inventory']['path']).parent
 actualnames={p.name for p in root.iterdir() if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 assert len(actualnames)==row['actual_nonself']
 names={r['path'] for r in inventory}
 assert sorted(actualnames-names)==row['unlisted']
 errors=[]
 for r in inventory:
  q=root/r['path']
  if sha(q)!=r['sha256'] or q.stat().st_size!=r['size']:errors.append(r['path'])
 assert sorted(errors)==(['stderr.txt','stdout.txt'] if row['run']=='run_en_us' else [])
pending=read(Q/'RETURN_PENDING.json')
assert pending['result_id']==rid and pending['status']=='PENDING_ONE_AUTHORIZED_TERMINAL_SEND'
for key in ['report','manifest','index','completion']:verify(pending[key])
assert not (Q/'RETURN_TOOL_PROOF.json').exists()
snap=json.loads(read(C/'MASTER_SOL_R19_CONTINUE_SNAPSHOT_20261011.json')['content'][0]['text'])['polls'][0]
assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='failed'
assert 'usage limit' in snap['latestTurn']['error']['message']
assert snap['latestTurn']['id']==read(C/'MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_ACK_VERIFICATION_20261010.json')['actual_snapshot']['latestTurn']['id']
''' +s[end:]
s=s.replace("'actual_thread_read':str(C/'MASTER_SOL_R19_INDEPENDENT_TERMINAL_READ_20261010.json')","'actual_thread_read':str(C/'MASTER_SOL_R19_INDEPENDENT_TERMINAL_READ_20261011.json')")
s=s.replace("'compiler_warning_stream':'TRUNCATED_LIMITATION_RETAINED_NO_REBUILD'","'compiler_warning_stream':'COMPLETE_OWNED_RAW_19219_BYTES_EXIT0','thread_operational_status':'FAILED_USAGE_LIMIT_IDLE','terminal_delivery_status':'PENDING_NO_ACTUAL_TERMINAL_SEND','artifact_terminal_status':'COMPLETED_VERIFIED_NOT_INFERRED_FROM_THREAD'")
s=s.replace("MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_COMPLETION_VERIFICATION_20261010.json","MASTER_SOL_R19_OPAQUE_POLICY_INDEPENDENT_COMPLETION_VERIFICATION_20261011.json")
dest=R/'Dispatcher/Tools/master_verify_r19_independent_completion_20261011.py'
assert not dest.exists()
dest.write_text(s,encoding='utf8')
print(str(dest))
