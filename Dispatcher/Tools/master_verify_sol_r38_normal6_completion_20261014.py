"""Read/hash completed independent normal6 filesystem evidence; no candidate reruns."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];Q=Path(d['qa_root']);co=m.read(Q/'COMPLETION.json');assert c.get('active_operation') is None and co['status']=='COMPLETED' and co['delivery_id']==d['delivery_id'] and co['result_id']==d['result_id']
 assert not any(x.get('result_id')==co['result_id'] for x in m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
 snap=json.loads(m.read(m.C/'MASTER_SOL_R38_NORMAL6_COMPLETE_IDLE_SNAPSHOT_20261014.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed' and snap['latestTurn']['id']==d['actual_new_turn_id']
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==184;evidence=[m.check(x) for x in em['files']]
 for x in co['artifacts']:m.check(x)
 ix=m.read(Q/'RESULT_INDEX.json')
 for k in ['manifest','report','preservation','case_ledger','expected_actual','execution_accounting']:m.check(ix[k])
 assert m.row(Q/'ACK_INITIAL.json')['sha256']==d['ACK_sha256'] and (Q/'ACK.json').read_bytes()==(Q/'ACK_INITIAL.json').read_bytes()
 base=m.read(Path(d['baseline_path']));assert len(base['files'])==19785
 for x in base['files']:m.check(x)
 before=m.read(Q/'PRESERVATION_BEFORE.json');after=m.read(Q/'PRESERVATION_AFTER.json');assert before['protected_files']==after['protected_files'] and before['frozen_files']==after['frozen_files']
 assert {x['path'].lower():(x['sha256'],x['bytes']) for x in base['files']}=={x['path'].lower():(x['sha256'],x['bytes']) for x in after['protected_files']}
 for x in m.read(Path(d['frozen_manifest']))['files']:m.check(x,'frozen_path')
 m.check(d['expected_oracle']);m.check(d['admission']);o=m.read(Path(d['expected_oracle']['path']));ledger=m.read(Q/'SINGLE_CALL_CASE_LEDGER.json');assert ledger['total_calls']==ledger['maximum_admitted']==6 and ledger['extra_calls']==0
 stages=['bootstrap','fixtures']+['case%02d'%i for i in range(1,7)]+['prepare','seal'];metadata=[]
 for stage in stages:
  t=m.read(Q/(stage+'.TOOL.json'));pin=m.read(Path(t['input_manifest']['path']));assert t['exit_code']==0 and pin['at']<t['start']<t['end']
  for k in ['stdout','stderr','input_manifest','preflight']:m.check(t[k])
  for x in pin['files']+pin['launcher_modules']:m.check(x)
  pre=m.read(Path(t['preflight']['path']));seed=m.read(Path(pre['seed']));assert pre['exit_code']==0 and seed['at']<pre['started']<pre['ended']<t['start'] and pre['pid']>0 and pre['helper_body_executed']==False
  for x in seed['files']+pre['streams']:m.check(x)
  metadata.append(dict(stage=stage,body_PID=t['pid'],exit_code=0,syntax_PID=pre['pid'],syntax_exit=0,stdout=t['stdout']['bytes'],stderr=t['stderr']['bytes'],logger_PID='UNOBSERVED'))
 cases=[];last_end=None
 for a,l in zip(o['cases'],ledger['cases']):
  case=Q/a['case_id'];assert l['case_id']==a['case_id'] and l['calls']==1 and l['retries']==0 and l['exit_code']==0;m.check(l['result']);t=m.read(case/'PUBLISHER_TOOL.json');pin=m.read(Path(t['input_manifest']['path']));m.check(t['input_manifest']);m.check(t['candidate'])
  assert pin['at']<t['start']<t['end'] and t['pid']==l['pid'] and t['exit_code']==0
  if last_end:assert last_end<t['start']
  last_end=t['end'];assert t['argv']==[r'C:\Users\user\anaconda3\python.exe','-B',d['selected_path'],'--spec',a['future_spec_path']]
  for x in pin['files']+pin['launcher_resolved_module_observations']:m.check(x)
  for k in ['stdout','stderr']:m.check(t[k]);assert t[k]==l['raw_'+k]
  summary=m.read(Path(t['stdout']['path']));assert summary['status']=='PUBLISHED' and summary['operatorPairId']==a['operatorPairId'] and summary['bundleSha256']==a['expected_bundle']['sha256'] and summary['bundleBytes']==a['expected_bundle']['bytes']
  result=m.read(case/'CASE_RESULT.json');assert result['status']=='SCOPED_NORMAL_PASS' and result['publisher_tool']==t and result['summary']==summary
  for x in result['outputs']:m.check(x)
  bundle=Path(a['future_bundle_path']);staging=bundle.with_name('operator_startup_pair.staging.json');side=bundle.with_name('operator_startup_pair.sha256.txt');manifest=bundle.with_name('PROVENANCE_MANIFEST.json')
  expected=bytes.fromhex(a['expected_bundle']['hex']);assert expected==a['expected_bundle']['utf8_text'].encode('utf-8') and bundle.read_bytes()==staging.read_bytes()==expected and side.read_bytes()==a['expected_bundle']['sha256'].encode('ascii')
  parsed=json.loads(expected,object_pairs_hook=dict);assert parsed==a['expected_aux4'] and list(parsed)==['schemaVersion','operatorPairId','parentDeclaration','childDeclaration']
  statb=bundle.stat();stats=staging.stat();assert statb.st_dev==stats.st_dev and statb.st_ino==stats.st_ino and statb.st_nlink==stats.st_nlink==2
  specp=Path(a['future_spec_path']);assert specp.read_bytes()==bytes.fromhex(a['spec_literal']['hex']);prov=m.read(manifest)
  assert prov['publisher']['scriptPath']==d['selected_path'] and prov['publisher']['scriptSha256']==d['selected_sha256'] and prov['operatorPairId']==a['operatorPairId']
  actualinputs=dict(specFile=specp)
  for inp in a['inputs']:
   p=Path(inp['future_path']);raw=bytes.fromhex(inp['raw_config']['hex']);assert p.read_bytes()==raw and json.loads(raw)==json.loads(inp['raw_config']['utf8_text']);actualinputs[inp['role']+'Config']=p
   assert (p.stat().st_file_attributes&1)!=0
   assert prov['inputs'][inp['role']+'Declaration']==inp['prospective_descriptor7']
  assert (specp.stat().st_file_attributes&1)!=0
  for k,p in actualinputs.items():
   obs=prov['inputs'][k];ident=m.row(p);assert obs['path']==str(p) and obs['sha256']==ident['sha256'] and obs['bytes']==ident['bytes'];assert obs['prior_stat']['size']==obs['handle_stat']['size']==ident['bytes']
  cases.append(dict(case_id=a['case_id'],PID=t['pid'],exit_code=0,stdout=t['stdout']['bytes'],stderr=t['stderr']['bytes'],bundle=m.row(bundle),staging=m.row(staging),spec=m.row(specp),manifest=m.row(manifest),expected_byte_exact=True,hardlink_current_identity_nlink2_observed=True))
 ds=m.read(Q/'DELIVERY_STATUS.json');assert ds['result_id']==co['result_id'] and ds['isError'] is False
 for x in ds['postseal_actual_rows']:m.check(x)
 assert co['publisher_calls']==co['normal_passed']==6 and co['publisher_retries']==co['publisher_extra_calls']==co['own_metadata_errors']==0
 p=m.C/'MASTER_SOL_R38_NORMAL6_FINAL_INDEPENDENT_EVIDENCE_VERIFICATION_20261014.json'
 m.create(p,dict(at=m.now(),guard_session=97827,delivery_id=d['delivery_id'],result_id=co['result_id'],actual_snapshot=snap,evidence_count=184,evidence=evidence,report=ix['report'],completion=m.row(Q/'COMPLETION.json'),initial_ACK=m.row(Q/'ACK_INITIAL.json'),protected19785_actual_rehash=True,frozen42_actual_rehash=True,before_after_full_lists_equal=True,own_body_syntax10=metadata,own_logger_invocations10_PID_unobserved=True,publisher_actual_calls6_exit0_retries0=cases,expected_literal_bytes_and_provenance_inputs_and_readonly_fixtures_matched=True,actual_child_import_context_unobserved=True,hardlink_shared_mutable_not_multifile_transaction=True,general_contract='REVISION_REQUIRED',High4='OPEN',whole_runtime_E2='NOT_RELEASED',Foundation='HOLD',Master_candidate_reruns=0))
 print(json.dumps(dict(status='NORMAL6_SCOPED_ACTUAL_EXECUTION_AND_RAW_VERIFIED',proof=m.row(p),normal6=True),ensure_ascii=False))

if __name__=='__main__':main()
