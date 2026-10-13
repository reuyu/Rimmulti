from pathlib import Path
import json,hashlib,datetime,struct,sys
sys.stdout.reconfigure(encoding='utf-8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R12-PACKAGE-ORDER-PREP-S1-20261009'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def verify(x):
 p=Path(x['path']);assert p.resolve().is_relative_to(R) and sha(p)==x['sha256'] and p.stat().st_size==x.get('bytes',x.get('size',p.stat().st_size)),str(p)
def flat(x,p=''):
 if isinstance(x,dict):return {k:v for n,y in x.items() for k,v in flat(y,p+'.'+n if p else n).items()}
 if isinstance(x,list):return {k:v for i,y in enumerate(x) for k,v in flat(y,f'{p}[{i}]').items()}
 return {p:x}
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();comp=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json');assert comp['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R12-PACKAGE-ORDER-PREP-S1-20261009-8c52852591474a1990b0ea65594fc981';assert comp['delivery_id']=='SOL-GATE05-R12-PACKAGE-ORDER-PREP-S1-20261009-01' and comp['status']=='COMPLETED' and comp['wp_revision']=='S1'
assert sha(Q/'COMPLETION.json')=='298658D6AE6AF224A6D525D7B15D14B3CC493108D9EAECEA7225F38966F63B97'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(comp[k])
assert len(m['files'])==94
for x in m['files']:verify(x)
before={x['path']:x for x in read(Q/'PRESERVATION_BEFORE.json')['files']};after={x['path']:x for x in read(Q/'PRESERVATION_AFTER.json')['files']};assert before==after and len(after)==4901
for x in after.values():verify(x)
assert all(comp[k]==0 for k in ['controls_executed','qa_runner_builds','candidate_runner_processes','assembly_loads','production_modify_builds','provider_cache_config_game_native_operator_old_negative_rejection_tied_gapped_unknownschema_ambiguity_adverse']) and comp['r12_candidate_verdict']=='NOT_REVIEWED'
o=read(Q/'NORMAL_ORDER_REFERENCE_ORACLE.json');typed=read(Q/'TYPED_CONTENT_REFERENCE_PLAN.json');assert len(o['cases'])==14 and o['reference_files']==70 and o['expected_policy_not_derived_from_actual'] and o['reference_only_json_hash_tools'];refs=[]
for name,x in o['cases'].items():
 policy=x['expected_input_policy'];canonical=x['expected_policy_canonical'];raw=x['independent_raw_inventory_literal'];execution=x['independent_expected_execution_records'];assert len(raw)==3 and sorted(y['loadOrder'] for y in raw)==[0,1,2] and len({y['packageId'].lower() for y in raw})==3 and execution==sorted(raw,key=lambda y:y['loadOrder'])
 assert canonical==dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId=policy['policyId'],revision=policy['revision'],admittedPackageIds=[y.lower() for y in policy['admittedPackageIds']]);assert canonical['admittedPackageIds']==[y['packageId'].lower() for y in execution]
 ref=x['policy_reference'];verify(ref);rawbytes=Path(ref['path']).read_bytes();assert rawbytes==json.dumps(canonical,ensure_ascii=False,separators=(',',':')).encode('utf8') and sha(Path(ref['path']))==x['expected_digest']
 check=x['expected_full_check_current_carrier_plan'];assert check==dict(isAdmitted=True,policyId=policy['policyId'],revision=policy['revision'],policyDigest=x['expected_digest'],status='ADMITTED',failureReason='',expectedPackages=policy['admittedPackageIds'],observedPackages=[y['packageId'].lower() for y in execution])
 assert x['expected_check_caller_after']==x['independent_unbound_input_manifest_template'] and x['expected_false_transport_semantics']==x['independent_policy_bearing_freshoriginal_input_template']
 content=x['expected_admitted_content_and_caller_after'];assert content==x['expected_explicit_normalize_and_freshtrue_semantics'] and content['activeMods']==execution and content['packagePolicyDisposition']==dict(policyId=policy['policyId'],revision=policy['revision'],policyDigest=x['expected_digest'],status='ADMITTED') and not x['candidate_observed']
 mapping={'raw.inventory.literal.json':raw,'expected.execution.literal.json':execution,'binding.freshoriginal.input.reference.json':x['independent_policy_bearing_freshoriginal_input_template'],'canonical.content.semanticreference.json':content}
 for suffix,v in mapping.items():assert read(Q/'normal_references'/f'{name}.{suffix}')==v
 leaves=flat(content);rows=typed['case_expected_leaves'][name];assert len(rows)==179 and {y['path']:y['expected_semantic'] for y in rows}==leaves
 for row in rows:
  val=row['expected_semantic']
  if isinstance(val,str):assert val.encode('utf-16-le').hex()==row['expected_utf16le_hex']
  if isinstance(val,float):assert struct.pack('<f',val).hex()==row['expected_float32_hex']
 refs.append({'case':name,'policy_sha':x['expected_digest'],'reference_files':5,'typed_semantic_leaves':len(rows)})
assert len(list((Q/'normal_references').glob('*.json')))==70
for relation in o['relations']:
 l=o['cases'][relation['left']];r=o['cases'][relation['right']];assert (l['expected_digest']==r['expected_digest'])==relation['reference_policy_digest_equal'] and (l['expected_admitted_content_and_caller_after']==r['expected_admitted_content_and_caller_after'])==relation['reference_full_content_semantics_equal'] and not relation['candidate_observed']
assert len(read(Q/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json')['rows'])==14 and len(read(Q/'STATIC_REVIEW_CRITERIA.json')['rows'])==14
src=read(Q/'FROZEN_R11_FIELD_AND_CALLSITE_MATRIX.json');verify(src['source']);verify(src['manifest']);assert len(src['rows'])==10
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and transport['terminal_attempt_count']==1 and sha(Path(transport['exact_tool_return_file']))==transport['exact_tool_return_sha256']
actual=read(C/'MASTER_R12_PREP_ACTUAL_THREAD_READ_20261009.json');data=json.loads(next(x['text'] for x in actual['content'] if x['type']=='text'));assert data['thread']['status']['type']=='idle' and data['turns'][0]['id']=='01a11f7a-2db9-7ef0-85e3-d4bed33c6591' and data['turns'][0]['status']=='completed'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp);assert comm['active_operation'] is None and comm['sol_current_attempt_id']==comp['delivery_id'] and not any(x.get('result_id')==comp['result_id'] for x in receipts['processed_results'])
review=H/'MASTER_REVIEW_ENGINE_GATE05_R12_PACKAGE_ORDER_QA_PREPARATION_S1_20261009.md';proof={'at':at,'result_id':comp['result_id'],'delivery_id':comp['delivery_id'],'wp_id':comp['wp_id'],'wp_revision':'S1','completion_sha256':sha(Q/'COMPLETION.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'report_path':comp['report']['path'],'report_sha256':comp['report']['sha256'],'evidence_files':94,'protected_unique_paths_master_rehashed':4901,'references_verified':refs,'reference_files':70,'normal_criteria':14,'static_criteria':14,'source_anchors':10,'controls_build_runs':0,'master_verdict':'ACCEPTED_R12_NORMAL_ORDER_REFERENCE_PREPARATION_NO_CANDIDATE_VERDICT','r12_candidate':'NOT_REVIEWED','actual_thread_id':data['thread']['id'],'actual_completed_turn':data['turns'][0]['id'],'actual_cursor':'2745552a-f142-41a1-8eaf-3fe7b2d500ca:80','actual_thread_read':str(C/'MASTER_R12_PREP_ACTUAL_THREAD_READ_20261009.json'),'master_review':str(review),'master_review_sha256':sha(review),'guard_run':'MASTER-SOL-R12-PREP-COMPLETE-20261009-01','guard_session':88603,'runtime_e2_released':False,'closure_changed':False,'Foundation':'HOLD'}
vp=C/'MASTER_SOL_R12_PACKAGE_ORDER_PREP_COMPLETION_VERIFICATION_20261009.json';write(vp,proof);receipt=dict(proof,verification_path=str(vp),verification_sha256=sha(vp));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(rp,receipts)
comm.update(sol_status='R12_PREPARATION_COMPLETE_ACCEPTED_IDLE',sol_latest_result=receipt,last_sol_cursor=proof['actual_cursor'],updated_at=at);comm['sol_current_delivery'].update(status='COMPLETED_PREPARATION_ACCEPTED_NO_CANDIDATE_VERDICT',result_id=comp['result_id']);write(cp,comm)
bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];assert t['dispatch_id']=='WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6';qm=Q/'EVIDENCE_MANIFEST.json';t['preservation_policy']['qa_preserved_manifests'].append({'path':str(qm),'sha256':sha(qm)})
for n in ['COMPLETION.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
 p=Q/n;t['preservation_policy']['fixed_current_files'].append({'path':str(p),'sha256':sha(p),'size':p.stat().st_size})
t['preparation_evidence_added_after_completion']={'at':at,'files':94,'terminal_graph':5,'initial_qa_baseline_3335_not_replaced':True,'sent_WP_unchanged':True};b['updated_at']=at;write(bp,b)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',current_runtime_idle_verified=True,last_result_id=comp['result_id'],last_runtime_observation_cursor=proof['actual_cursor'],latest_review=str(review));state['updated_at']=at;write(sp,state)
paragraph=f'\n\n## LOCAL-SOL-R12-PACKAGE-ORDER-PREPARATION-COMPLETE — {at}\nOriginalSol {comp["result_id"]} actualcompletedidle80. MasterACCEPTED_R12_NORMAL_ORDER_REFERENCE_PREPARATION_NO_CANDIDATE_VERDICT;94evidence/4901protected/14normal14static10anchors70references/179typedleaves-per-template verified. Physicalarray and0-basedexecutionordinal meaning/independentpolicy/fullpackage-versionassociation andfreshoriginalbeforeNormalize plans adopted;actualfutureR12APIs/headers/canonicalformatterUNOBSERVED/controlsbuildrun0/R12NOT_REVIEWED. NewQA94+terminal5additivelyprotected AQA3429,initialsentQA3335baseline/WPunchanged. A R12terminalfile observedpendingMasteractualsource/identity/rawgraphreview/freeze;no duplicateA/newcandidatePASS/fullGateE2/closure. SamehourlylifecycleuntilAterminaldispositionthenpause,originalSolidleawaitsadmittedcandidate. Engine002006/Pipeline007/current schema/G-Q1OPEN,FoundationHOLD. Review {review};proof {vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(paragraph)
event=dict(receipt,event_id='MASTER-SOL-R12-PREP-COMPLETION-DISPOSITION-20261009-01',type='QA_PREPARATION_ADOPTED_NO_CANDIDATE_VERDICT')
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps({'accepted':'REFERENCE_PREPARATION_ONLY','evidence':94,'protected':4901,'references':70,'Sol':'IDLE80','R12_candidate':'NOT_REVIEWED'}))
