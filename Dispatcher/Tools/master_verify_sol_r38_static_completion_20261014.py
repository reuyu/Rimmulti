"""Independent read-only R38 terminal evidence and original-literal checks."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
Q=m.R/'QA-Tactical-Engine/GATE05-R38-PUBLISHER-INDEPENDENT-STATIC-S1-20261014'

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];co=m.read(Q/'COMPLETION.json')
 assert c.get('active_operation') is None and co['status']=='COMPLETED' and co['delivery_id']==d['delivery_id'] and co['result_id']==d['result_id']
 assert not any(x.get('result_id')==co['result_id'] for x in m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
 s=json.loads(m.read(m.C/'MASTER_SOL_R38_COMPLETE_IDLE_SNAPSHOT_20261014.json')['content'][0]['text'])['polls'][0]
 assert s['thread']['status']['type']=='idle' and s['latestTurn']['status']=='completed' and s['latestTurn']['id']==d['actual_new_turn_id']
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==94;evidence=[m.check(x) for x in em['files']]
 for x in co['artifacts']:m.check(x)
 ix=m.read(Q/'RESULT_INDEX.json')
 for k in ['manifest','report','preservation','R1_supplement','R2_supplement']:m.check(ix[k])
 for x in ix['actual_new_wrapper_graph']:
  for k in ['prospective_seed','preflight','input']:m.check(x[k])
 assert m.row(Q/'ACK_INITIAL.json')['sha256']==d['ACK_sha256'] and (Q/'ACK.json').read_bytes()==(Q/'ACK_INITIAL.json').read_bytes()
 base=m.read(Path(d['baseline_path']));assert len(base['files'])==19676
 for x in base['files']:m.check(x)
 before=m.read(Q/'PRESERVATION_BEFORE.json');after=m.read(Q/'PRESERVATION_AFTER.json')
 assert before['protected_files']==after['protected_files'] and before['frozen_files']==after['frozen_files']
 assert {x['path'].lower():(x['sha256'],x['bytes']) for x in base['files']}=={x['path'].lower():(x['sha256'],x['bytes']) for x in after['protected_files']}
 for x in m.read(Path(d['frozen_manifest']))['files']:m.check(x,'frozen_path')
 tools=[]
 for stage in ['bootstrap','capture','review_finalize_r2','prepare','seal']:
  j=m.read(Q/(stage+'.TOOL.json'));pin=m.read(Path(j['input_manifest']['path']));assert j['exit_code']==0 and pin['at']<j['start']<j['end']
  for k in ['stdout','stderr','input_manifest','preflight']:m.check(j[k])
  for x in pin['files']+pin['launcher_modules']:m.check(x)
  pre=m.read(Path(j['preflight']['path']));seed=m.read(Path(pre['seed']));assert pre['exit_code']==0 and seed['at']<pre['at']<j['start'] and pre['helper_body_executed']==False
  for x in seed['files']+pre['streams']:m.check(x)
  tools.append(dict(stage=stage,PID=j['pid'],exit_code=0,stdout=j['stdout']['bytes'],stderr=j['stderr']['bytes'],native_preflight_PID='UNOBSERVED',seed=m.row(Path(pre['seed']))))
 fail=m.read(Q/'review.TOOL.json');assert fail['pid']==10324 and fail['exit_code']==1 and fail['stderr']['bytes']==1915
 for k in ['stdout','stderr','input_manifest','preflight']:m.check(fail[k])
 for inv in ['STOP_INITIAL_PARTIAL_PRESERVATION.json','STOP_REVIEW_PARTIAL_INVENTORY.json']:
  for x in m.read(Q/inv)['files']:m.check(x)
 acct=m.read(Q/'REVIEW_PARTIAL_FINALIZATION_ACCOUNTING.json');assert acct['original_review_replay']==0 and acct['old_files_changed']==False
 for x in acct['partial_outputs']+[acct['completed_missing_output'],acct['authorization']]:m.check(x)
 ret=m.read(Q/'RETURN_TOOL_PROOF.json');assert not ret.get('isError',False)
 ds=m.read(Q/'DELIVERY_STATUS.json');assert ds['result_id']==co['result_id'] and ds['actual_tool_isError'] is False
 for x in ds['postseal_actual_rows']:m.check(x)
 oraclep=m.R/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013/NORMAL_PUBLISHER_EXPECTATION_ORACLE.json';oracle=m.read(oraclep)
 up1=m.read(Path(oracle['literal_pair']['path']));up2=m.read(Path(oracle['literal_combined']['path']))
 matrix=m.read(Q/'ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json');assert len(matrix['cases'])==6;ids=[];witness=[]
 for a,z in zip(oracle['cases'],matrix['cases']):
  assert a['case_id']==z['case_id'] and a['expected_aux4']==z['expected_aux4_original'] and a['expected_aux4']['operatorPairId']==z['operatorPairId_original'];ids.append(a['case_id'])
  for inp,zi in zip(a['inputs'],z['inputs']):
   rb=inp['raw_config_expected'];data=rb['utf8_text'].encode('utf-8');assert len(data)==rb['bytes'] and hashlib.sha256(data).hexdigest().upper()==rb['sha256'] and bytes.fromhex(rb['hex'])==data
   decoded=json.loads(rb['utf8_text']);assert zi['config14_raw_decoded']==decoded and zi['original_descriptor7']==inp['original_descriptor7'] and zi['raw_sha256']==rb['sha256'] and not zi['legacy_metadata_differences']
   assert decoded['issuedAtUtc']==('2026-10-11T00:00:00.1234567Z' if inp['role']=='parent' else '2026-10-11T00:00:01.0000000Z')
   assert decoded['capabilityBoundary']=='LOCAL_SANDBOXED' and decoded['configId']==decoded['configId'].strip(' \t\r\n\v\f') and decoded['validatorArguments']==''
   for rows in [up1['prospective_cases'],up2['pair_cases']]:
    orig=next(x for x in rows if x['case_id']==a['case_id'])['independently_supplied_'+inp['role']+'14_7'];assert orig['raw_config']['utf8_text']==rb['utf8_text'] and orig['raw_config']['sha256']==rb['sha256'] and orig['config14']==decoded
   witness.append(dict(case_id=a['case_id'],role=inp['role'],raw_sha256=rb['sha256'],bytes=len(data),original_child_parent_UTC=decoded['issuedAtUtc']))
 p=m.C/'MASTER_SOL_R38_STATIC_FINAL_INDEPENDENT_EVIDENCE_VERIFICATION_20261014.json'
 m.create(p,dict(at=m.now(),guard_session=44442,delivery_id=d['delivery_id'],result_id=co['result_id'],actual_snapshot=s,evidence_count=94,evidence=evidence,report=ix['report'],completion=m.row(Q/'COMPLETION.json'),initial_ACK=m.row(Q/'ACK_INITIAL.json'),protected19676_actual_rehash=True,frozen42_actual_rehash=True,before_after_full_lists_equal=True,successful_metadata5=tools,original_review_failed_preserved=True,native_locator_failed_preserved=True,review_replay=0,actual_direct_return=m.row(Q/'RETURN_TOOL_PROOF.json'),original_six_ids=ids,raw12_actual_SHA_bytes_UTF8hex_and_two_upstream_matched=witness,all_original12_cap_nonblank_ASCII_ID_unpadded_Args_empty=True,source_verdict=co['verdict'],native_E2='NOT_RELEASED',Foundation='HOLD',Master_candidate_execution_build_publication_native=0))
 print(json.dumps(dict(status='SOL_R38_TERMINAL_INDEPENDENT_EVIDENCE_VERIFIED',proof=m.row(p),six_ids=ids),ensure_ascii=False))

if __name__=='__main__':main()
