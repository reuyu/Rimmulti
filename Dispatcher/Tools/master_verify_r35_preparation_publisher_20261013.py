"""Passive Master evidence verification; never imports producer or publisher code."""
from pathlib import Path
import json,sys,hashlib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
R=m.R;Q=R/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-PREPARATION-S1-20261013'
T=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e'
E=R/'scratch/EngineGate05R35Publisher-16a25a7e'
def ck(v,key='path'):
 p=Path(v[key]);a=m.row(p);assert a['sha256']==v['sha256'] and a['bytes']==v.get('bytes',v.get('size')),str(p);return a
def exact(a,b):
 assert type(a)==type(b),(type(a),type(b))
 if isinstance(a,dict):
  assert list(a)==list(b),(list(a),list(b))
  for k in a:exact(a[k],b[k])
 elif isinstance(a,list):
  assert len(a)==len(b)
  for x,y in zip(a,b):exact(x,y)
 else:assert a==b,(a,b)
def raw(v,obj=None):
 data=v['utf8_text'].encode('utf-8');assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest().upper()==v['sha256'] and data.hex().upper()==v['hex'].upper()
 assert not data.startswith(b'\xef\xbb\xbf') and not data.endswith(b'\n')
 if obj is not None:assert data==json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8')
 return data
def main():
 co=m.read(Q/'COMPLETION.json');em=m.read(Q/'EVIDENCE_MANIFEST.json');idx=m.read(Q/'RESULT_INDEX.json');bind=m.read(Q/'ACK_COMPLETION_BINDING.json')
 assert len(em['files'])==41
 for v in em['files']+co['artifacts']:ck(v)
 for k in ['report','manifest','initial_ACK','self_review','preservation']:ck(idx[k])
 for k in ['initial_ACK','mirror','index','manifest','report']:ck(bind[k])
 assert (Q/'ACK.json').read_bytes()==(Q/'ACK_INITIAL.json').read_bytes()
 for d in [idx,bind]:assert d['result_id']==co['result_id'] and d['delivery_id']==co['delivery_id']
 ba=m.read(Q/'PRESERVATION_BEFORE_AFTER.json');ck(ba['before']);ck(ba['after']);before=m.read(Path(ba['before']['path']));after=m.read(Path(ba['after']['path']))
 d=m.read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json')['sol_current_delivery'];base=m.read(Path(d['baseline_path']));assert len(base['files'])==19103
 exact(before['protected_files'],after['protected_files']);exact(before['additive_late_helper'],after['additive_late_helper']);exact(before['frozen_files'],after['frozen_files'])
 assert {x['path'].lower():(x['sha256'],x['bytes']) for x in before['protected_files']}=={x['path'].lower():(x['sha256'],x['bytes']) for x in base['files']}
 frozen=m.read(Path(d['frozen_manifest']))['files'];assert len(frozen)==75
 for v in frozen:ck(v,'frozen_path')
 check=m.read(m.C/'MASTER_R35_CURRENT_INVOCATION_CHECKER_20261013.json');assert check['actual_exec']['exit_code']==0 and check['guard_session']==23543
 snapshot=json.loads(check['actual_completed_snapshot']['content'][0]['text'])['polls'][0];assert snapshot['latestTurn']['status']=='completed' and snapshot['thread']['status']['type']=='idle'
 steps=[]
 for p in Q.glob('*.TOOL.json'):
  t=m.read(p);assert t['exit_code']==0 and t['first_streams_complete'];ck(t['script']);ck(t['stdout']);ck(t['stderr']);steps.append(dict(tool=m.row(p),exit=0,stdout_bytes=t['stdout']['bytes'],stderr_bytes=t['stderr']['bytes']))
 assert not m.read(Q/'RETURN_TOOL_PROOF.json').get('isError',False)
 o=m.read(Q/'NORMAL_PUBLISHER_EXPECTATION_ORACLE.json');ck(o['literal_pair']);ck(o['literal_combined']);original=m.read(Path(o['literal_pair']['path']))['prospective_cases'];combined=m.read(Path(o['literal_combined']['path']))['pair_cases'];exact(original,combined);assert len(o['cases'])==len(original)==6 and not Path(o['future_root']).exists()
 for case,old in zip(o['cases'],original):
  assert case['case_id']==old['case_id'];aux=dict(old['expected_bundle4'])
  for inp in case['inputs']:
   role=inp['role'];part=old['independently_supplied_'+role+'14_7'];exact(inp['config14'],part['config14']);exact(inp['original_descriptor7'],part['original_descriptor7']);assert raw(inp['raw_config_expected'],inp['config14'])==raw(part['raw_config'],part['config14'])
   new=dict(part['original_descriptor7']);new['expectedConfigPath']=inp['actual_future_path'];exact(new,inp['prospectively_approved_new_fixture_descriptor7']);raw(inp['descriptor_raw_expected'],new);aux[role+'Declaration']=new
   assert not Path(inp['actual_future_path']).exists() and not Path(inp['descriptor_future_path']).exists()
  exact(aux,case['expected_aux4']);bundle=raw(case['expected_bundle'],aux);sidecar=raw(case['expected_SHA_sidecar_ascii_noLF']);assert sidecar.decode('ascii')==hashlib.sha256(bundle).hexdigest().upper()
 a=m.read(T/'COMPLETION.json');assert a['status']=='COMPLETED' and a['envelope']==38 and len(a['artifacts'])==20
 for v in a['artifacts']:ck(v)
 ap=m.read(E/'AST_HOST_TOOL_PROOF.json');ai=m.read(E/'AST_INPUT_MANIFEST.json');ck(ai['exact_final_source']);ck(ai['helper']);ck(ap['input_source']);ck(ap['stdout'],'raw_path');ck(ap['stderr'],'raw_path');assert ap['exit_code']==0 and ap['pid']==11312 and ap['command']==ai['argv']
 parsed=json.loads(Path(ap['stdout']['raw_path']).read_text(encoding='utf-8-sig'));exact(parsed,ap['stdout']['parsed'])
 owned=m.read(E/'OWNED_OUTPUT_MANIFEST.json');assert len(owned['files'])==13
 for v in owned['files']:ck(v,'absolute_path')
 proof=dict(at=m.now(),actual_snapshot=snapshot,sol_result_id=co['result_id'],sol_completion=m.row(Q/'COMPLETION.json'),evidence41=True,original_combined_six_full_order_type_value_exact=True,raw_config12_byte_exact=True,only_descriptor_expectedConfigPath_rebound=True,compact_aux4_six_verified=True,fixturewriting_publisher_engine_native_execution=0,metadata_steps=steps,terminal_return_tool=m.row(Q/'RETURN_TOOL_PROOF.json'),protected19103_full_current_invocation_rehash=check['actual_exec'],additional1=True,frozen75_rehashed=True,beforeafter_full_rows_match=True,A_result_id=a['result_id'],A_artifacts20=True,A_completion=m.row(T/'COMPLETION.json'),A_AST_pid=11312,A_AST_exit=0,A_AST_full_stdout_bytes=750,A_AST_stderr_bytes=0,A_AST_interpreter_prospective_SHA_bytes_missing=True,A_owned13=True,A_publisher=m.row(Path(ai['exact_final_source']['path'])),Master_candidate_build_publisher_native_execution=0,full_native_E2='NOT_RELEASED',Foundation='HOLD')
 out=m.C/'MASTER_R35_PREPARATION_AND_PUBLISHER_PASSIVE_EVIDENCE_VERIFICATION_20261013.json';m.create(out,proof);print(json.dumps(dict(status='PASSIVE_EVIDENCE_VERIFIED_NOT_PUBLICATION_PASS',proof=m.row(out),metadata_steps=len(steps)),ensure_ascii=False))
if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');main()
