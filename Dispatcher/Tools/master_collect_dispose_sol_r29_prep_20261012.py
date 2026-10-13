from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
def refs(x):
 if isinstance(x,dict):
  if all(k in x for k in ['path','sha256','bytes']):check(x)
  for z in x.values():refs(z)
 elif isinstance(x,list):
  for z in x:refs(z)
def raw(x):
 if isinstance(x,dict):
  if 'utf8_text' in x:
   by=x['utf8_text'].encode('utf8');assert len(by)==x['bytes'] and hashlib.sha256(by).hexdigest().upper()==x['sha256'] and by.hex().upper()==x['hex'].upper() and not by.startswith(b'\xef\xbb\xbf');return 1
  return sum(raw(z) for z in x.values())
 if isinstance(x,list):return sum(raw(z) for z in x)
 return 0
def typemap(x,path='$'):
 k='null' if x is None else 'boolean' if isinstance(x,bool) else 'integer' if isinstance(x,int) else 'number' if isinstance(x,float) else 'string' if isinstance(x,str) else 'array' if isinstance(x,list) else 'object'
 z=[{'path':path,'json_type':k,'ordered_keys':list(x) if isinstance(x,dict) else None,'length':len(x) if isinstance(x,list) else None}]
 if isinstance(x,dict):
  for a,b in x.items():z+=typemap(b,path+'.'+a)
 elif isinstance(x,list):
  for i,b in enumerate(x):z+=typemap(b,path+'['+str(i)+']')
 return z
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';bp=R/'Dispatcher/MASTER_A_TASKS.json';rp=R/'Dispatcher/MASTER_RECEIPTS.json';sp=H/'DISPATCHER_STATE.json';c=read(cp);b=read(bp);rr=read(rp);s=read(sp);d=c['sol_current_delivery'];Q=Path(d['qa_root']);t=b['tasks'][-1];x=read(Q/'COMPLETION.json');lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json')
assert lock['status']=='LOCKED' and lock['run_id']=='MASTER-R29-SOL-PREP-COMPLETE-20261012-01' and c['active_operation'] is None and t['dispatch_id'].endswith('46f60e2a') and t['status']=='IN_PROGRESS' and not Path(t['completion_path']).exists()
assert all(x[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and x['result_id']==c['sol_current_result_id'] and x['status']=='COMPLETED' and sha(Q/'COMPLETION.json')=='BF302C6946EA61832E0976CEF489E9D6886B42CA08C3B9C3B099E2FFA6EA6E22'
assert not any(z.get('result_id')==x['result_id'] for z in rr['processed_results'])
refs(x);refs(read(Q/'RESULT_INDEX.json'));refs(read(Q/'ACK_COMPLETION_BINDING.json'));em=read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==53
for f in em['files']:check(f)
assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='8B801439D5857404F93E99C343328F1881980E751112705F940B5322AD3FF97A'
base=read(Path(d['baseline_path']));assert len(base['files'])==14105
for f in base['files']:check(f)
expected={f['path']:(f['sha256'],f['bytes']) for f in base['files']}
for name in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 z=read(Q/name);assert z['all_matched'] and z['protected_unique_paths']==14105 and {f['path']:(f['sha256'],f['bytes']) for f in z['protected_files']}==expected
for f in t['production_fixed_files']:check(f)
sn=json.loads(read(C/'MASTER_SOL_R29_STARTUP_PAIR_PREP_COMPLETION_SNAPSHOT_20261012.json')['content'][0]['text'])['polls'][0];assert sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
o=read(Q/'PRE_RUN_EXPECTED_ORACLE.json');assert sha(Q/'PRE_RUN_EXPECTED_ORACLE.json')=='7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02';check(o['historical_input']);check(o['master_contract']);hist=read(Path(o['historical_input']['path']))
pin=read(Q/'PROSPECTIVE_INPUT_LITERAL_MANIFEST.json');assert len(pin['files'])==30
for f in pin['files']:check(f)
order=['originId','expectedConfigId','expectedRole','expectedCapabilityBoundary','launchPlanId','expectedConfigPath','expectedConfigSha256'];nraw=raw(o);nrows=0
for ci,z in enumerate(o['prospective_cases']):
 assert list(z['expected_bundle4'])==o['auxiliary_top4_writer_order']==['schemaVersion','operatorPairId','parentDeclaration','childDeclaration']
 assert z['expected_bundle4']['schemaVersion']=='we-operator-startup-pair/v1' and z['expected_bundle4']['operatorPairId']==z['operatorPairId_original']
 bundle=json.dumps(z['expected_bundle4'],ensure_ascii=False,separators=(',',':')).encode('utf8');assert bundle==z['expected_bundle_compact_UTF8_noLF']['utf8_text'].encode('utf8') and not bundle.endswith((b'\r',b'\n'))
 graph=z['expected_full_observation_graph'];assert json.dumps(graph,ensure_ascii=False,separators=(',',':')).encode('utf8')==z['expected_full_graph_compact_UTF8']['utf8_text'].encode('utf8')
 assert typemap(graph)==z['full_ordered_type_map'] and len(z['full_ordered_type_map'])==206;nrows+=206
 assert len(z['expected_same_graph_phases'])==3 and z['expected_pair_readonly4']==graph['PairReadonly4'] and list(z['expected_pair_readonly4'])==['ParentReceipt','ChildReceipt','OperatorPairId','Scope']
 assert z['expected_pair_readonly4']['Scope']=='DECLARED_OPERATOR_STARTUP_PAIR_CONSISTENCY_ONLY'
 for role,name,declkey,snapkey in [('parent','Parent','parentDeclaration','ParentReceipt'),('child','Child','childDeclaration','ChildReceipt')]:
  p=z['independently_supplied_'+role+'14_7'];cfg=p['config14'];decl=p['original_descriptor7'];used=p['factory_used_clone7'];assert len(cfg)==14 and list(decl)==order and decl==z['expected_bundle4'][declkey]==z['expected_'+name+'Declaration_fresh_original7']==graph[name+'Declaration7']
  assert json.loads(p['raw_config']['utf8_text'])==cfg and decl['expectedConfigSha256']==p['raw_config']['sha256']
  assert cfg['role']==('SIMULATION' if role=='parent' else 'READ_ONLY') and p['receipt11']['AdmittedAtUtc']==cfg['issuedAtUtc'] and p['receipt11']['Snapshot']==p['snapshot15']
  assert p['receipt11']==z['expected_pair_readonly4'][snapkey] and p['receipt11']['BoundOriginId']==decl['originId'] and p['receipt11']['BoundLaunchPlanId']==decl['launchPlanId']
  for field in order:assert used[field]==(decl[field].strip() if field in ['expectedRole','expectedCapabilityBoundary','expectedConfigPath','expectedConfigSha256'] else decl[field])
  assert Path(decl['expectedConfigPath']).read_bytes()==p['raw_config']['utf8_text'].encode('utf8') and Path(decl['expectedConfigPath']).is_relative_to(Q)
  if ci<4:
   historical=hist['normal_pairs'][ci]
   # Historical first4 identity is additionally checked using exact original sidecar/raw hashes already bound by the historical document.
   assert z['explicit_fixture_locator_rebind']['four_historical_raw14_byte_exact'] and z['historical_'+role+'_original7']['expectedConfigSha256']==p['raw_config']['sha256']
   assert {k:v for k,v in z['historical_'+role+'_original7'].items() if k!='expectedConfigPath'}=={k:v for k,v in decl.items() if k!='expectedConfigPath'}
 assert not Path(z['publisher_future_plan']['owned_output_root']).exists()
assert nrows==1236 and len(o['prospective_cases'])==6 and x['production_QA_compiler_producer_candidate_bootstrap_Unity_native_Process_adverse_rejection_executes']==0 and x['R29_candidate_verdict']=='NOT_REVIEWED'
note=read(Q/'PRESERVATION_HASH_SCOPE_NOTE.json');assert len(note['mandatory_baseline_fixed_generated_obj4'])==4 and note['no_blanket_zero_bytes_under_obj_claim'] and note['mutable7_excluded_unread']
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173
verdict='ACCEPTED_INDEPENDENT_R29_SIX_NORMAL_TYPED_RAW_COPY_ORACLE_PREPARATION_NO_CANDIDATE_VERDICT'
review=H/'MASTER_REVIEW_ENGINE_GATE05_R29_STARTUP_PAIR_QA_PREPARATION_S1_20261012.md';assert not review.exists()
review.write_text(f'''# R29 independent normal oracle preparation — Master
{at}; {x['result_id']}; **{verdict}**.

OriginalSol actualcompleted/idle178 same newturn01a12d75... and immutableACK/COMPLETION hash verified. Report/manifest53/index/terminalbindings andprotected14105/currentfixedCensus+csproj2/frozen83 before-after matched. Historical R28 usagefailed operationalstatus remains separate; currentactual R29 preparation completed.

Six prospective cases contain original two independently suppliedconfig14/descriptor7, compactUTF8 noBOM/noLF aux4/rawSHA/hex, fullreceipt11/snapshot15/policy/redactions/readonly4/two freshdecl7 with native/issuer claims absent. Master metadata/data checks verify{nraw} rawtext UTF8 length/SHA/hex bindings and1236 independently walked hierarchicaltyped rows/18 plannedphaseconditions, not candidate assertions/runtimeleaf coverage. Thirty own literal input/expected files pinned. First4 historicalrawSHA/7 unchanged except prospective expectedConfigPath rebound to own fixturefiles; oldoriginal7sidecars andprior raw unchanged. New2 opaque '=' quote/backslash/Ω are normalbundledata, notCLIvalueproof. ReceiptAdmittedAtUtc usesfixedIssuedAtUtc literal; raw7+new getters stay distinct from legacyfactory usedClone role/cap/path/SHA Trim. Nestedexisting SnapshotTrim/GetFullPath retained as frozen sourcefact. New packaging no opaque normalization does not erase oldnestedbehavior. Source-only guards/methodnames adoptedcontractonly untilnewcandidate actual metadata.

Own regex fieldmap initially missed ExpectedPackagePolicyDeclaration?; originalfailedscript/trace/partialmap preserved, correctedmetadata script exit0. No compiler/candidate/testfailure/retry inferred. Baselinefixedgeneratedobj4 hashedonly under explicitpreservation requirement; currentmutable7/newpublisher/bin/obj implementation unexamined. No blanket zero bytes under allobj claim. Futurepublisher outputroots uncreated. Producer/compiler/candidate/Awake/Unity/game/native/Process/adverse execution0; currentR29 NOT_REVIEWED/noPASS. WholeGate/issuer/currenttask/typedprotectedreceiver/nativeeffectivepaths still separate.

A same R29 actualSENT/ACKIN_PROGRESS/noCOMPLETION atverification; no duplicate/newWP/schedulerchange. Additiveprotect new53evidence and terminalgraph while preserving originallysentpolicy/baseline. Existing hourlyACTIVE60min/directSolcompletionreporting; nextAterminal→Masterexactreviewfreeze/pause→freshoriginalSolQA using independentsealedoracle, no inheritedR27PASS. FoundationHOLD/EnginePipelineSchemaGQ1OPEN/nativeE2NOTRELEASED/closure0.
''',encoding='utf8')
vp=C/'MASTER_SOL_R29_STARTUP_PAIR_PREP_COMPLETION_VERIFICATION_20261012.json';assert not vp.exists();proof={'at':at,'guard_run':lock['run_id'],'guard_session':7127,'guard_pid':27876,'delivery_id':d['delivery_id'],'wp_id':d['wp_id'],'wp_revision':'S1','result_id':x['result_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'actual_snapshot':sn,'evidence_count':53,'protected':14105,'prospective_normal_cases':6,'literalfiles':30,'Master_raw_UTF8_bindings':nraw,'Master_hierarchical_type_rows':1236,'not_runtime_assertions_or_leafcount':True,'plannedphaseconditions':18,'current_R29_verdict':'NOT_REVIEWED','master_verdict':verdict,'master_review':row(review),'verification_status':'MASTER_DISPOSED','build_execute':0,'A_completion_observed':False,'no_new_WP_or_duplicate':True,'scheduler_actual':cfg,'native_e2_released':False,'closure_changed':False,'foundation':'HOLD'};write(vp,proof)
rec=dict(proof,proof_path=str(vp),proof_sha256=sha(vp));rr['processed_results'].append(rec);rr['updated_at']=at;write(rp,rr)
t['preservation_policy']['qa_preserved_manifests'].append({'path':str(Q/'EVIDENCE_MANIFEST.json'),'sha256':sha(Q/'EVIDENCE_MANIFEST.json')});t['r29_additional_completed_QA_preservation']={'at':at,'completion':row(Q/'COMPLETION.json'),'result_index':row(Q/'RESULT_INDEX.json'),'return_tool_proof':row(Q/'RETURN_TOOL_PROOF.json'),'report':x['artifacts'][0],'master_review':row(review),'Master_verification':row(vp),'initial_sent_scope_and_baseline_unchanged':True};write(bp,b)
c.update(sol_status='R29_PREPARATION_COMPLETE_MASTER_ACCEPTED_NO_CANDIDATE_VERDICT',sol_latest_completion=rec,last_sol_cursor=sn['cursor'],sol_next_action='AWAIT_A_R29_TERMINAL_MASTER_EXACT_FROZEN_ADMISSION_THEN_FRESH_INDEPENDENT_QA',updated_at=at);c['last_monitor_run']={'run_id':lock['run_id'],'guard_pid':27876,'guard_session':7127,'at':at,'status':'R29_QA_PREP_COMPLETE_ACCEPTED_A_INPROGRESS_NO_DUPLICATE_MONITOR_UNCHANGED','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
s['endpoints']['sol'].update(execution_phase='TERMINAL_PREPARATION_ACCEPTED_WAIT_NEWFROZEN_CANDIDATE',current_runtime_idle_verified=True,last_result_id=x['result_id'],last_runtime_observation_cursor=sn['cursor'],latest_review=str(review));s['latest_master_review']=str(review)
for item in s['deliveries']:
 if item.get('delivery_id')==d['delivery_id']:item.update(status='COMPLETED_PREPARATION_MASTER_ACCEPTED_NO_CANDIDATE_VERDICT',master_review=str(review))
write(sp,s)
event={'at':at,'event_id':d['delivery_id']+'-MASTER-COMPLETE','type':'SOL_R29_PREPARATION_COMPLETE_INDEPENDENT_ORACLE_ACCEPTED_ADDITIVELY_PROTECTED_NO_DUPLICATE','proof':row(vp),'review':row(review)}
para=f'\n\n## LOCAL-SOL-R29-STARTUP-PAIR-PREP-S1-COMPLETE — {at}\n{verdict}. Originalactualcompletedidle178/evidence53/protected14105/frozen83/currentfixed2matched;6prospectiveliteralpairs/rawUTF8bindings{nraw}/typedhierarchical1236(plannednotruntimeleaf/assertions)/18phaseconditions/30owninputs. First4raw14/oldoriginal7sidecar unchanged;expectedConfigPath onlyprospectivereboundownfixtures/new2opaqueencoding/internalbundle/raw7distinctlegacyUsedClone/nestedTrimGetFullPathretained/fixedIssuedUTC. Ownregexnullablefieldfailure+correctedmetadata/rawpreserved/no candidateFAIL. Mandatoryfixedobj4hashonly/currentmutable7-newpublisher-semanticbinsobjunread/futurepublisheroutputsnotcreated. Compiler-publisher-candidate-native-Process-adverse0/R29NOTREVIEWED/noPASS. A sameR29IN_PROGRESS/ACK/noCOMPLETION;no duplicate/newWP/schedulerchange;new53terminalgraphadditivelyprotected/sentpolicybaselineunchanged. SameactualhourlyACTIVE60min/directSolpush,awaitAterminal→Masterreviewfreeze→freshindependentQA. EnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED/closure0. Review{review};proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps({'status':verdict,'evidence':53,'protected':14105,'raw':nraw,'rows':nrows,'A':'IN_PROGRESS_COMPLETION_ABSENT','monitor':'UNCHANGED_ACTIVE_HOURLY'},ensure_ascii=False))
