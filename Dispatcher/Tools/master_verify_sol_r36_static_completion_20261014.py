"""Independent read-only terminal evidence, preservation and original raw literal verification."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
Q=m.R/'QA-Tactical-Engine/GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014'

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];co=m.read(Q/'COMPLETION.json');rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')
 assert c['active_operation'] is None and co['delivery_id']==d['delivery_id'] and co['result_id']==d['result_id'] and co['status']=='COMPLETED'
 assert not any(x.get('result_id')==co['result_id'] for x in rec['processed_results'])
 s=json.loads(m.read(m.C/'MASTER_SOL_R36_COMPLETE_IDLE_SNAPSHOT_20261014.json')['content'][0]['text'])['polls'][0]
 assert s['thread']['status']['type']=='idle' and s['latestTurn']['status']=='completed' and s['latestTurn']['id']==d['actual_new_turn_id'] and s['revision']==47
 em=m.read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==59
 evidence=[m.check(x) for x in em['files']]
 for x in co['artifacts']:m.check(x)
 ix=m.read(Q/'RESULT_INDEX.json')
 for k in ['manifest','report','preservation']:m.check(ix[k])
 for x in ix['operational_qualifications']:m.check(x)
 assert m.row(Q/'ACK_INITIAL.json')['sha256']==d['ACK_sha256'] and (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
 base=m.read(Path(d['baseline_path']));assert len(base['files'])==19380
 for x in base['files']:m.check(x)
 before=m.read(Q/'PRESERVATION_BEFORE.json');after=m.read(Q/'PRESERVATION_AFTER.json')
 assert before['protected_files']==after['protected_files'] and before['frozen_files']==after['frozen_files']
 expected={x['path'].lower():(x['sha256'],x['bytes']) for x in base['files']}
 assert expected=={x['path'].lower():(x['sha256'],x['bytes']) for x in after['protected_files']}
 frozen=m.read(Path(d['frozen_manifest']))['files'];assert len(frozen)==43
 for x in frozen:m.check(x,'frozen_path')
 tools=[]
 for stage in ['bootstrap','capture','review_r1','final_prepare','final_seal']:
  j=m.read(Q/(stage+'.TOOL.json'));pin=m.read(Q/(stage+'.INPUT.json'));assert j['exit_code']==0 and pin['at']<j['start']<j['end']
  for k in ['stdout','stderr','input_manifest']:m.check(j[k])
  for x in pin['files']+pin['launcher_default_module_observations']:m.check(x)
  tools.append(dict(stage=stage,PID=j['pid'],exit_code=0,stdout=j['stdout']['bytes'],stderr=j['stderr']['bytes']))
 fail=m.read(Q/'review.TOOL.json');assert fail['exit_code']==1
 for x in m.read(m.C/'MASTER_SOL_R36_OWN_METADATA_SYNTAX_FAILURE_PRESERVATION_20261014.json')['files']:m.check(x)
 ret=m.read(Q/'RETURN_TOOL_PROOF.json');assert not ret.get('isError',False)
 ds=m.read(Q/'DELIVERY_STATUS.json');assert ds['result_id']==co['result_id'] and ds['actual_tool_isError'] is False
 for x in ds['postseal_actual_artifacts']:m.check(x)
 oracle=m.read(m.R/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013/NORMAL_PUBLISHER_EXPECTATION_ORACLE.json')
 up1=m.read(Path(oracle['literal_pair']['path']));up2=m.read(Path(oracle['literal_combined']['path']))
 matrix=m.read(Q/'ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json');assert len(matrix['cases'])==6
 ids=[];rawcount=0
 for a,z in zip(oracle['cases'],matrix['cases']):
  assert a['case_id']==z['case_id'] and a['expected_aux4']==z['expected_aux4'];ids.append(a['case_id'])
  for inp,zi in zip(a['inputs'],z['inputs']):
   assert inp['config14']==zi['config14'] and inp['original_descriptor7']==zi['original_descriptor7']
   rb=inp['raw_config_expected'];data=rb['utf8_text'].encode('utf-8');assert len(data)==rb['bytes'] and hashlib.sha256(data).hexdigest().upper()==rb['sha256']
   for rows in [up1['prospective_cases'],up2['pair_cases']]:
    orig=next(x for x in rows if x['case_id']==a['case_id'])['independently_supplied_'+inp['role']+'14_7']
    assert orig['config14']==inp['config14'] and orig['original_descriptor7']==inp['original_descriptor7'] and orig['raw_config']['utf8_text']==rb['utf8_text'] and orig['raw_config']['sha256']==rb['sha256']
   rawcount+=1
 assert rawcount==12
 p=m.C/'MASTER_SOL_R36_STATIC_FINAL_INDEPENDENT_EVIDENCE_VERIFICATION_20261014.json'
 m.create(p,dict(at=m.now(),guard_session=64707,delivery_id=d['delivery_id'],result_id=co['result_id'],actual_snapshot=s,evidence_count=59,evidence=evidence,
  report=ix['report'],completion=m.row(Q/'COMPLETION.json'),initial_ACK=m.row(Q/'ACK_INITIAL.json'),protected19380_actual_rehash=True,frozen43_actual_rehash=True,
  before_after_full_lists_equal=True,successful_metadata5=tools,failed_metadata_originals_preserved=True,actual_direct_return=m.row(Q/'RETURN_TOOL_PROOF.json'),
  original_six_ids=ids,raw12_actual_SHA_bytes_utf8_and_two_upstream_matched=True,original_oracles_unchanged=True,
  source_verdict=co['verdict'],native_E2='NOT_RELEASED',Foundation='HOLD',production_candidate_execution_build_native=0))
 print(json.dumps(dict(status='SOL_R36_TERMINAL_INDEPENDENT_EVIDENCE_VERIFIED',proof=m.row(p),original_six=ids),ensure_ascii=False))

if __name__=='__main__':main()
