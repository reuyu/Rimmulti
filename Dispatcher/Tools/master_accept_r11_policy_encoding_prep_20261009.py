from pathlib import Path
import json,hashlib,datetime,copy
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R11-POLICY-ENCODING-PREP-S1-20261009'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify(x):
 p=Path(x['path']);assert p.resolve().is_relative_to(R) and sha(p)==x['sha256'] and p.stat().st_size==x.get('bytes',x.get('size',p.stat().st_size))
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(Q/'COMPLETION.json');m=read(Q/'EVIDENCE_MANIFEST.json');idx=read(Q/'RESULT_INDEX.json')
assert c['result_id']==m['result_id']==idx['result_id']=='SOL-GATE05-R11-POLICY-ENCODING-PREP-S1-20261009-661be88f72724c34b7185bdcf48b2861'
assert c['delivery_id']=='SOL-GATE05-R11-POLICY-ENCODING-PREP-S1-20261009-01' and c['wp_id']=='WP_QA_ENGINE_GATE05_R11_POLICY_ENCODING_PREPARATION' and c['wp_revision']=='S1' and c['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='9476707B60E88CAC2FBFC299C812D9311D062096E7A9E8B037E59DA92C13DECD'
for k in ['report','evidence_manifest','result_index','ack_completion_binding']:verify(c[k])
assert len(m['files'])==54
for x in m['files']:verify(x)
before={x['path']:x for x in read(Q/'PRESERVATION_BEFORE.json')['files']};after={x['path']:x for x in read(Q/'PRESERVATION_AFTER.json')['files']};assert before==after and len(after)==4047
for x in after.values():verify(x)
assert all(c[k]==0 for k in ['controls_executed','qa_runner_builds','candidate_runner_processes','production_modify_builds','configuration_cache_provider_game_native_operator_old_negative_rejection_tied_ambiguity_adverse']) and c['r11_candidate_verdict']=='NOT_REVIEWED'
o=read(Q/'NORMAL_REFERENCE_ORACLE.json');assert len(o['cases'])==14 and len(o['variants'])==2
references=[]
for name,case in o['cases'].items():
 expected=case['expected_canonical_declaration'];original=case['expected_input']
 assert expected['policyId']==original['policyId'] and expected['revision']==original['revision'] and expected['admittedPackageIds']==[x.lower() for x in original['admittedPackageIds']]
 assert case['actual_not_used_to_construct_expected'] and [x['packageId'].lower() for x in case['separate_observed_inventory_literal']]==expected['admittedPackageIds']
 for k in ['policyId','revision']:assert original[k].encode('utf-16-le').hex()==case['expected_opaque_utf16le_hex'][k] and [ord(x) for x in original[k]]==case['expected_opaque_codepoints'][k]
 for variant,ref in case['references'].items():
  verify(ref['reference']);raw=Path(ref['reference']['path']).read_bytes();independent=json.dumps(expected,ensure_ascii=variant=='ASCII_UNICODE_ESCAPED',separators=(',',':')).encode('utf-8')
  assert raw==independent==bytes.fromhex(ref['utf8_hex']) and sha(Path(ref['reference']['path']))==ref['expected_sha256'] and json.loads(raw)==expected
  references.append({'case':name,'variant':variant,'sha256':ref['expected_sha256'],'bytes':len(raw)})
assert len(references)==28
for relation in o['reference_relations']:
 left=o['cases'][relation['left']]['references'][relation['variant']]['expected_sha256'];right=o['cases'][relation['right']]['references'][relation['variant']]['expected_sha256'];assert (left==right)==relation['reference_bytes_and_digest_equal']
transport=read(Q/'DELIVERY_STATUS.json');assert transport['status']=='SENT_TOOL_RETURNED' and sha(Path(transport['exact_tool_return_file']))==transport['exact_tool_return_sha256']
snap=read(C/'MASTER_SOL_R11_POLICY_ENCODING_PREP_COMPLETION_SNAPSHOT_20261009.json');poll=json.loads(next(x['text'] for x in snap['content'] if x['type']=='text'))['polls'][0];assert poll['thread']['status']['type']=='idle' and poll['latestTurn']['status']=='completed' and poll['latestTurn']['id']=='01a11dd4-3687-7831-83ff-78900f2f64fe'
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=read(rp);assert comm['active_operation'] is None and comm['sol_current_attempt_id']==c['delivery_id'] and not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
review=H/'MASTER_REVIEW_ENGINE_GATE05_R11_POLICY_ENCODING_QA_PREPARATION_S1_20261009.md';assert review.exists()
proof={'at':at,'result_id':c['result_id'],'delivery_id':c['delivery_id'],'wp_id':c['wp_id'],'wp_revision':'S1','completion_sha256':sha(Q/'COMPLETION.json'),'evidence_manifest_sha256':sha(Q/'EVIDENCE_MANIFEST.json'),'report_path':c['report']['path'],'report_sha256':c['report']['sha256'],'evidence_files':54,'protected_unique_paths_master_rehashed':4047,'reference_bytes_and_typed_fields_master_verified':references,'normal_criteria':14,'static_criteria':14,'frozen_source_constraints':12,'controls_build_runs':0,'master_verdict':'ACCEPTED_R11_REFERENCE_CRITERIA_PREPARATION_NO_CANDIDATE_VERDICT','r11_candidate':'NOT_REVIEWED','actual_thread':poll,'original_failed_turn_retained':c['prior_failed_turn_id'],'same_WP_result_resumed':True,'master_review':str(review),'master_review_sha256':sha(review),'runtime_e2_released':False,'closure_changed':False,'Foundation':'HOLD'}
vp=C/'MASTER_SOL_R11_POLICY_ENCODING_PREP_COMPLETION_VERIFICATION_20261009.json';write(vp,proof);receipt=dict(proof,verification_path=str(vp),verification_sha256=sha(vp));receipts['processed_results'].append(receipt);receipts['updated_at']=at;write(rp,receipts)
comm.update(sol_status='R11_PREPARATION_COMPLETE_ACCEPTED_IDLE',sol_latest_result=receipt,last_sol_cursor=poll['cursor'],updated_at=at);comm['sol_current_delivery'].update(status='COMPLETED_PREPARATION_ACCEPTED_NO_CANDIDATE_VERDICT',result_id=c['result_id']);write(cp,comm)
bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];assert t['dispatch_id']=='WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350';qm=Q/'EVIDENCE_MANIFEST.json';t['preservation_policy']['qa_preserved_manifests'].append({'path':str(qm),'sha256':sha(qm)})
for n in ['COMPLETION.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
 p=Q/n;t['preservation_policy']['fixed_current_files'].append({'path':str(p),'sha256':sha(p),'size':p.stat().st_size})
t['preparation_evidence_added_after_completion']={'at':at,'files':54,'terminal_graph':5,'initial_qa_baseline_2578_not_replaced':True,'sent_WP_unchanged':True};b['updated_at']=at;write(bp,b)
sp=H/'DISPATCHER_STATE.json';state=read(sp);state['endpoints']['sol'].update(execution_phase='COMPLETED_IDLE',current_runtime_idle_verified=True,last_result_id=c['result_id'],last_runtime_observation_cursor=poll['cursor'],latest_review=str(review));state['updated_at']=at;write(sp,state)
paragraph=f'\n\n## LOCAL-SOL-R11-POLICY-ENCODING-PREPARATION-COMPLETE — {at}\nOriginal Sol sameWP/result{c["result_id"]} actual completedidle/resumedturn/cursor74. MasterACCEPTED_R11_REFERENCE_CRITERIA_PREPARATION_NO_CANDIDATE_VERDICT;54evidence/4047protected/28referencebytes and14declaredtypednormalmeaning independentlyverified;14normal14static12frozenconstraints/controlsbuildrun0/R11NOT_REVIEWED. Priorusagefailure/failedACKnotexecuted/originalpartialbytes preserved. Source-based literalUnicode convention selected separately BEFORE futurecandidateexecution,not afterobservedoutputs. NewQA54andterminal5additivelyprotected currentAQA2632;initialsentbaseline2578/WPunchanged. A R11terminalreviewed/frozen74/invalidreleaseJSONoriginalretained;fresh originalSol independentWP preparingNOT_SENT untilactualnewdelivery,newbaseline. SamehourlyPAUSED,no newA/fullGateE2/closure;Engine002006/Pipeline007/current schema/G-Q1OPEN,FoundationHOLD. Review {review};proof {vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf-8') as f:f.write(paragraph)
event=dict(receipt,event_id='MASTER-SOL-R11-PREP-COMPLETION-DISPOSITION-20261009-01',type='QA_PREPARATION_ADOPTED_NO_CANDIDATE_VERDICT')
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps({'accepted':'REFERENCE_PREPARATION_ONLY','evidence':54,'protected':4047,'references':28,'Sol':'IDLE74','R11_candidate':'NOT_REVIEWED'}))
