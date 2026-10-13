from common import *
import os
check(load(Q/'STOP_REVIEW_PARTIAL_INVENTORY.json')['files']);check(load(Q/'RECOVERY_R2_PROSPECTIVE_SUPPLEMENT.json')['files']);check(load(Q/'review.INPUT.json')['files'])
old=load(Q/'review.TOOL.json');assert old['exit_code']==1 and old['pid']==10324;check([old['stdout'],old['stderr'],old['input_manifest'],old['preflight']]);assert old['stdout']['bytes']==0 and old['stderr']['bytes']==1915
assert 'TypeError: dict() got multiple values for keyword argument' in (Q/'review.STDERR.txt').read_bytes().decode('utf-8')
flow=load(Q/'SOURCE_FLOW_REVIEW.json');ready=load(Q/'SCOPED_ORIGINAL6_NORMAL_PUBLICATION_READINESS_RECOMMENDATION.json');e1=load(Q/'E1_PROVENANCE_ASSESSMENT.json');matrix=load(Q/'ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json');raw=load(Q/'TIMESTAMP_RAW_CORRECTION_ASSESSMENT.json')
assert flow['source_verdict']=='GAINS_CREDITED_GENERAL_CONTRACT_REVISION_REQUIRED' and len(flow['findings'])==4
assert len(matrix['cases'])==6 and matrix['executed_cases']==0 and len(raw['raw12'])==12
assert all(not r['legacy_metadata_differences'] and r['both_upstream_raw_match'] for r in raw['raw12'])
assert len(e1['producer_artifacts'])==22 and e1['module_sample_actual_count']==20 and e1['module_declared_count']==65
assert ready['publication_now']=='NOT_ADMITTED' and ready['Master_disposition']=='PENDING'
target=Q/'MINIMAL_NEXT_PUBLISHER_CORRECTIVE_REQUIREMENTS.json';assert not target.exists()
data=dict(requirements=[dict(id=f['id'],requirement=f['description'],exact_normal6_blocker=f['original6_blocker']) for f in flow['findings']]+[dict(id='R38-EVIDENCE-GRAPH',requirement='Correct three prose authority SHAs; explicitly delimit module sampling/child context/helper preflight graph/first outer streams; enumerate finite owned inventory with selfcycle/postseal exclusions; no retro-pins')],allowed_change_scope='Publisher-only and new producer-owned metadata, all Engine/generated/install/oracle/oldQA fixed',separate_normal6=ready,closure_authority='MASTER_ONLY',High4='OPEN',Foundation='HOLD')
base=dict(at=now(),publisher=row(S),scope='SOURCE_ONLY_NOT_RUNTIME_TEST');assert not set(base).intersection(data);payload=dict(base);payload.update(data);write(target,payload)
observed=[]
for name in ['json','hashlib','pathlib','datetime','os']:
    m=sys.modules[name];p=getattr(m,'__file__',None)
    if p:observed.append(dict(module=name,**row(p)))
write(Q/'REVIEW_PARTIAL_FINALIZATION_ACCOUNTING.json',dict(at=now(),authorization=row(PKG/'MASTER_R38_SAME_WP_PARTIAL_REVIEW_FINALIZATION_R2_20261014.md'),original_failed_review=old,partial_inventory=row(Q/'STOP_REVIEW_PARTIAL_INVENTORY.json'),checked_partial_count=len(load(Q/'STOP_REVIEW_PARTIAL_INVENTORY.json')['files']),completed_missing_output=row(target),partial_outputs=[row(Q/(n+'.json')) for n in ['SOURCE_FLOW_REVIEW','CONFIG14_DECL7_SEMANTICS_COMPARISON','PATH_ANCESTRY_NONOVERWRITE_ASSESSMENT','ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX','CLAIM_CORRECTIONS','E1_PROVENANCE_ASSESSMENT','SCOPED_ORIGINAL6_NORMAL_PUBLICATION_READINESS_RECOMMENDATION','TIMESTAMP_CORRECTION_DESCRIPTION_QUALIFICATION']],original_review_replay=0,old_files_changed=False,child_post_body_observation=dict(pid=os.getpid(),sys_path=sys.path,modules=observed,context='partial observations afterrun, not retrospective prospective pins'),candidate_publication_native_adverse=0))
print(json.dumps(dict(status='R2_MISSING_METADATA_FINALIZED_ORIGINAL_FAILURE_PRESERVED',checked_partial_count=len(load(Q/'STOP_REVIEW_PARTIAL_INVENTORY.json')['files']),missing_output=row(target),original_review_exit=1,original_review_replay=0,candidate_execution=0),ensure_ascii=False))
