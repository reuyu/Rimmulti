from pathlib import Path
import json,hashlib,collections,datetime,struct,uuid
import master_r29_s1_stop_prepare_s2_20261012 as m
import master_r29_s3_final_independent_verification_20261012 as old
exact=old.exact;rawbytes=old.rawbytes;ck=old.ck;rd=m.read
def mvid(p):
 b=p.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];us=lambda o:struct.unpack_from('<H',b,o)[0];pe=u(60);assert b[pe:pe+4]==b'PE\0\0';opt=pe+24;dd=opt+(96 if us(opt)==0x10b else 112);sec=opt+us(pe+20)
 def rva(x):
  for k in range(us(pe+6)):
   o=sec+40*k;vs,va,rs,rp=struct.unpack_from('<IIII',b,o+8)
   if va<=x<va+max(vs,rs):return rp+x-va
  raise ValueError('RVA not mapped')
 md=rva(u(rva(u(dd+14*8))+8));assert b[md:md+4]==b'BSJB';p0=(md+16+u(md+12)+3)&~3;count=us(p0+2);p0+=4;s={}
 for _ in range(count):
  off,size=struct.unpack_from('<II',b,p0);p0+=8;end=b.index(0,p0);name=b[p0:end].decode('ascii');p0=(end+1+3)&~3;s[name]=b[md+off:md+off+size]
 t=s.get('#~',s.get('#-'));heap=t[6];valid=struct.unpack_from('<Q',t,8)[0];pos=24;counts={}
 for i in range(64):
  if valid>>i&1:counts[i]=struct.unpack_from('<I',t,pos)[0];pos+=4
 assert counts[0]==1;sw=4 if heap&1 else 2;gw=4 if heap&2 else 2;gi=int.from_bytes(t[pos+2+sw:pos+2+sw+gw],'little');return str(uuid.UUID(bytes_le=s['#GUID'][(gi-1)*16:gi*16]))
def main():
 c=rd(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];assert c['active_operation'] is None;Q=Path(d['qa_root']);comp=rd(Q/'COMPLETION.json');assert all(comp[k]==d[k] for k in ['delivery_id','wp_id','wp_revision','result_id']) and comp['status']=='COMPLETED';assert comp['own_runner_builds']==1 and comp['normal_runs']==2 and comp['failed']==0 and comp['production_modify_build']==comp['changed_lifecycle_global_Unity_native_operator_Process_provider_cache_publisher_adverse_execution']==0
 assert m.row(Q/'COMPLETION.json')['sha256']=='1342E1B2880393484B524B3A2D2463E2E49606053A9C21FB92624560528BB517'
 for k in ['report','evidence_manifest','initial_ACK','result_index','ACK_binding','preservation','selected']:ck(comp[k])
 em=rd(Q/'EVIDENCE_MANIFEST.json');assert em['result_id']==comp['result_id'] and len(em['files'])==em['artifact_count']==911
 for v in em['files']:ck(v)
 actual={str(p) for p in Q.rglob('*') if p.is_file()};included={v['path'] for v in em['files'] if str(Q) in v['path']};exclusions=em['cycle_exclusions']+em['unfinished_seal_logger_exclusions'];excluded={str(Q/n) for n in exclusions if (Q/n).exists()};assert actual-included==excluded
 for p in Q.glob('*.TOOL.json'):
  tool=rd(p);assert tool['exit_code']==0,p
  for key in ['script','stdout','stderr']:ck(tool[key])
 assert not rd(Q/'RETURN_TOOL_PROOF.json').get('isError',False)
 for k in ['immutable_initial_ACK','result_index']:ck(rd(Q/'ACK_COMPLETION_BINDING.json')[k])
 base=rd(Path(d['baseline_path']));assert len(base['files'])==16026
 for v in base['files']:ck(v)
 fm=rd(Path(d['frozen_manifest']));assert len(fm['files'])==64
 for v in fm['files']:ck(v,'frozen_path')
 pb=rd(Q/'BUILD_INPUTS.json');assert pb['input_count']==len(pb['files'])==159 and pb['compiler_attempts']==pb['runner_calls']==pb['production_builds']==0
 for v in pb['files']:ck(v)
 build=rd(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0 and build['compiler_attempts']==1 and build['production_candidate_builds']==0 and build['binary_first_full_streams'];assert datetime.datetime.fromisoformat(pb['at'])<datetime.datetime.fromisoformat(build['started_at']);ck(build['stdout']);ck(build['stderr'])
 oracle=rd(Q/'NORMAL_EXPECTED_ORACLE.json');ck(pb['oracle']);pairprep=m.R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012/PRE_RUN_EXPECTED_ORACLE.json';capprep=m.R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/PROSPECTIVE_CAPTURE_ORACLE.json'
 assert m.row(pairprep)['sha256']=='7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02' and m.row(capprep)['sha256']=='5961CD18DA05B67F6DE40DA8A6EBB289D94ACF85054D57FB31FE4B8C5530C4C7';exact(oracle['pair_cases'],rd(pairprep)['prospective_cases']);exact(oracle['normal_pairs'],rd(capprep)['normal_pairs'])
 rawmap={};graphmap={}
 for case in oracle['pair_cases']:
  cid='PAIR_'+case['case_id'];p=case['independently_supplied_parent14_7'];ch=case['independently_supplied_child14_7'];entries={'pair.envelope':case['expected_full_graph_compact_UTF8'],'pair.bundleProjection':case['expected_bundle_compact_UTF8_noLF']}
  for name,part in [('parent',p),('child',ch)]:
   for suffix,key in [('original7','original_declaration7_compact_utf8'),('receipt11','receipt_compact_utf8'),('snapshot15','snapshot_compact_utf8'),('receipt.pretty','receipt_redacted_pretty_windows_utf8'),('snapshot.pretty','snapshot_redacted_pretty_windows_utf8')]:entries['pair.'+name+'.'+suffix]=part[key]
  for phase in ['BEFORE','AFTER_CALLER','AFTER_RETURNED']:
   for name,v in entries.items():rawmap[cid+'.'+phase+'.'+name+'.utf8']=rawbytes(v)
   graphmap[cid+'.'+phase+'.pair.graph.json']=case['expected_full_observation_graph']
 for case in oracle['normal_pairs']:
  cid=case['case_id'];entries={}
  for name,key in [('capture','expected_Capture15_compact_utf8'),('envelope','expected_full_envelope_compact_utf8'),('approved7','expected_approved7_compact_utf8'),('task27','expected_task27_compact_utf8'),('options7','expected_option7_compact_utf8'),('invocation2','expected_invocation2_compact_utf8')]:entries[name]=case[key]
  for name,key in [('receipt','expected_receipt_pretty_utf8'),('snapshot','expected_snapshot_pretty_utf8')]:entries[name+'Parent']=case[key]['parent'];entries[name+'Child']=case[key]['child']
  for phase in ['BEFORE','AFTER_CALLER','AFTER_RETURNED']:
   for name,v in entries.items():rawmap[cid+'.'+phase+'.'+name+'.utf8']=rawbytes(v)
   graphmap[cid+'.'+phase+'.graph.json']=case['expected_observation_envelope']
 assert len(rawmap)==336 and len(graphmap)==30;summaries=[];roots=[Q/'runs/1-en-US',Q/'runs/2-de-DE']
 for run in roots:
  inv=rd(run/'OUTPUT_INVENTORY.json');assert len(inv['files'])==inv['file_count']==407
  for v in inv['files']:ck(v)
  assert {str(p) for p in run.rglob('*') if p.is_file()}=={v['path'] for v in inv['files']}|{str(run/'OUTPUT_INVENTORY.json')};assert {p.name for p in run.glob('*.utf8')}==set(rawmap)
  for name,data in rawmap.items():assert (run/name).read_bytes()==data,name
  for name,g in graphmap.items():exact(g,rd(run/name),name)
  nr=rd(run/'NORMAL_RESULTS.json');assert nr['failed_assertions']==0 and len(nr['results'])==438 and all(v['status']=='PASS' for v in nr['results']) and len({v['id'] for v in nr['results']})==438;assert nr['selected_sha256']==d['selected_sha256'] and nr['selected_mvid']==d['selected_mvid']
  typed=rd(run/'TYPED_CHECKS.json');assert len(typed)==6700 and len({v['path'] for v in typed})==6700 and all(v['matched'] and v['expected_type']==v['actual_type'] for v in typed)
  for v in typed:exact(v['expected'],v['actual'],v['path'])
  ledger=rd(run/'ACTUAL_ADMITTED_CALL_LEDGER.json');counts=dict(collections.Counter(v['scope'] for v in ledger));assert counts==dict(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18)
  for case in oracle['pair_cases']:
   cid='PAIR_'+case['case_id'];x=rd(run/(cid+'.returned_owned_mutations.json'));e=case['planned_copy_controls']
   for actualkey,expectedkey in [('ParentDeclaration7','returnedParentDeclaration7'),('ChildDeclaration7','returnedChildDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4')]:exact(e[expectedkey],x[actualkey],cid+'.'+actualkey)
   for role in ['Parent','Child']:assert x[role+'IdsDetachedInplace'] and all(v==f'edited.{role.lower()}.ids.{k}' for k,v in enumerate(x[role+'IdsDetachedInplace']))
   mutation=rd(run/(cid+'.caller_array_mutation.json'));assert mutation['arrays_edited_after_success_only'] and not mutation['readmitted']
   for field,v in [('bundle_sha_after',case['expected_bundle_compact_UTF8_noLF']),('parent_sha_after',case['independently_supplied_parent14_7']['raw_config']),('child_sha_after',case['independently_supplied_child14_7']['raw_config'])]:assert mutation[field]!=v['sha256']
  for case in oracle['normal_pairs']:
   cid=case['case_id'];e=case['mutations_after_successful_capture_only'];x=rd(run/(cid+'.returned_owned_mutations.json'));caller=rd(run/(cid+'.caller_owned_mutations.json'))
   for a,k in [('Task','callerTask27'),('ParentDescriptor','submittedParentDescriptor7'),('ChildDescriptor','submittedChildDescriptor7')]:exact(e[k],caller[a],cid+'.'+a)
   for a,k in [('Task','returnedTask27'),('ApprovedChildDeclaration','returnedApprovedDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4'),('OptionCopy','detachedOperatorOptionCopy7'),('InvocationCopy','detachedTaskInvocationCopy2'),('ParentIdsCopy','detachedParentReadOnlyPolicyIdCopy'),('ChildIdsCopy','detachedChildReadOnlyPolicyIdCopy')]:exact(e[k],x[a],cid+'.'+a)
  pre=rd(run/'PRE_RUN_INPUT_MANIFEST.json');post=rd(run/'POST_RUN_IDENTITY.json');assert len(pre['files'])==len(post['files'])==172 and post['prepost_all_matched'] and pre['files']==post['files']
  for v in pre['files']:ck(v)
  host=rd(run/'HOST_RUN_PROCESS_OBSERVATION.json');ctx=rd(run/'ACTUAL_PROCESS_CONTEXT.json');assert host['numeric_exit']==host['candidate_Process_calls']==0 and host['binary_first_full_streams'] and ctx['run_id']==host['run_id']==nr['run_id'];assert host['argv'][0]==str(Q/'runner/QaPureRunner.exe');ck(host['stdout']);ck(host['stderr']);assert datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at'])
  for phase,n,count in [('BEFORE','ACTUAL_LOADED_MANAGED_BEFORE.json',8),('AFTER','ACTUAL_LOADED_MANAGED_AFTER.json',10),('FINAL','ACTUAL_LOADED_MANAGED.json',10)]:
   loaded=rd(run/n);assert len(loaded)==count;pinmap={v['path'].lower():v for v in pre['files']}
   for v in loaded:assert v['path'].lower() in pinmap and m.row(Path(v['path']))['sha256']==v['sha256']==pinmap[v['path'].lower()]['sha256'] and mvid(Path(v['path']))==v['mvid']
  for n in ['SELECTED_LOAD_BEFORE.json','SELECTED_LOAD_AFTER.json']:
   z=rd(run/n);assert z['sha256']==d['selected_sha256'] and z['mvid']==d['selected_mvid'] and z['path']==d['selected_path'] and z['CLR_EnvironmentVersion']==ctx['EnvironmentVersion'];assert m.row(Path(z['corelib_path']))['sha256']==z['corelib_sha256'] and mvid(Path(z['corelib_path']))==z['corelib_mvid']
  summaries.append(dict(run_id=nr['run_id'],culture=ctx['culture'],pid=host['owned_child_PID'],exit_code=0,assertions=438,typed_rows=6700,raw_files=336,graphs=30,output_files=407,prepost_pins=172,loaded_counts=[8,10,10],ledger=counts))
 assert summaries[0]['pid']!=summaries[1]['pid'] and summaries[0]['run_id']!=summaries[1]['run_id']
 for name in rawmap:assert (roots[0]/name).read_bytes()==(roots[1]/name).read_bytes()
 for name in graphmap:exact(rd(roots[0]/name),rd(roots[1]/name),name)
 for n in ['RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json','RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json']:assert rd(Q/n)['unchanged'];ck(rd(Q/n)['first_inventory'])
 scope=rd(Q/'SOURCE_FULL_SCOPE_COMPARISON.json');assert scope['outside_bytes']==263961 and scope['all_maps_correct'];ck(scope['old_source']);ck(scope['new_source']);ck(scope['scope'])
 snap=json.loads(rd(m.C/'MASTER_SOL_R32_COMPLETION_SNAPSHOT_20261013.json')['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
 proof=m.C/'MASTER_SOL_R32_FINAL_INDEPENDENT_EVIDENCE_VERIFICATION_20261013.json';result=dict(at=m.now(),result_id=comp['result_id'],delivery_id=comp['delivery_id'],completion=m.row(Q/'COMPLETION.json'),report=comp['report'],evidence_manifest=m.row(Q/'EVIDENCE_MANIFEST.json'),evidence_files=911,protected_paths=16026,frozen_files=64,prospective_build_inputs=159,independent_raw_literal_bindings=672,ordered_full_graphs=60,crossculture_raw_pairs=336,crossculture_graph_pairs=30,copy_mutations_independently_compared=True,loaded_PE_MVID_filebyte_independent=True,oracle_semantics_independently_original_bound=True,runs=summaries,own_QA_builds=1,Master_candidate_build_execution=0,source_High4='OPEN',native_E2='NOT_RELEASED',Foundation='HOLD',actual_snapshot=snap,limitations='Positive PURE graph/copy only; modified lifecycle/native0; managed resources attempts/abort concurrency/unknown owner/legacy failure remain; Capture IDs holder replacement; no publisher/issuer proof');m.create(proof,result);print(json.dumps(dict(status='R32_MASTER_FRESH_POSITIVE_PURE_VERIFIED_SCOPED',proof=m.row(proof),normal_raw=672,graphs=60)))
if __name__=='__main__':main()
