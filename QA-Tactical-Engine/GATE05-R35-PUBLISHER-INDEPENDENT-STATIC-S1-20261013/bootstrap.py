from common import *
paths=[Path(r['path']) for r in load(PREP/'RECOVERY_AUTHORITY_AUDIT.json')['files']]+[WP,PKG/'MASTER_REVIEW_ENGINE_GATE05_R35_PUBLISHER_PREPARATION_S1_20261013.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R35_PUBLISHER_E1_20261013.md',PKG/'coordination/MASTER_R35_PREPARATION_AND_PUBLISHER_PASSIVE_EVIDENCE_VERIFICATION_20261013.json']
audit=[]
for p in dict.fromkeys(paths):
    t=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+t);audit.append(dict(**row(p),full_read=True))
write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,Master_findings_independently_challengeable=True,full_read=True))
write(Q/'PRESERVATION_BEFORE.json',preservation())
assert sha(PUBLISHER)=='9CAEA2DF0B8F3517DFCBEF080F7D26EC4343CDF4D2FD761453EFA2E4F3B86B4A' and PUBLISHER.stat().st_size==22371
assert sha(SOURCE)=='544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD'
prepnames=['NORMAL_PUBLISHER_EXPECTATION_ORACLE.json','STRICT14_DECL7_BINDING_MATRIX.json','PROSPECTIVE_NORMAL_PUBLICATION_PLAN.json','PROSPECTIVE_PATH_HASH_BINDING_MATRIX.json','NO_OVERWRITE_SOURCE_OBLIGATIONS.json','READINESS_DELTA_FROM_R34.json','R35_ADMISSION_CRITERIA.json']
inputs=[Path(r['frozen_path']) for r in load(MAN)['files']]+[SOURCE,WP,MAN,BASE]+[PREP/n for n in prepnames]
records=[]
for p in inputs:
    if p.suffix.lower() in {'.py','.json','.md','.txt','.cs'}:records.append(dict(**row(p),raw_utf8=p.read_bytes().decode('utf-8-sig'),TEXT_only=True))
write(Q/'FULL_FROZEN_AND_PREPARATION_TEXT_READ.json',dict(at=now(),files=records,old_and_producer_helper_EXEC_IMPORT=False,publisher_EXEC_IMPORT=False,Engine_CLR_load=0))
write(Q/'PASSIVE_INPUT_MANIFEST.json',dict(at=now(),files=[row(p) for p in dict.fromkeys(inputs)],metadata_scope='Fresh own TEXT/JSON/AST only; no candidate import or execution'))
ack=dict(at=now(),delivery_id=DELIVERY,wp_id='WP_QA_ENGINE_GATE05_R35_PUBLISHER_INDEPENDENT_STATIC',wp_revision='S1',result_id='SOL-GATE05-R35-PUBLISHER-INDEPENDENT-STATIC-S1-20261013-'+uuid.uuid4().hex,status='ACKNOWLEDGED_EXACT_FROZEN_STATIC_ONLY',WP=row(WP),baseline=row(BASE),freeze=row(MAN),selected_publisher=row(PUBLISHER),frozen_Engine_source=row(SOURCE),python_source_MVID='NOT_APPLICABLE',protected_count=19229,frozen_count=34,initial_publisher_Engine_compiler_fixture_native_adverse=0,verdict='PENDING_SOURCE_REVIEW',Foundation='HOLD',nativeE2='NOT_RELEASED')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(result_id=ack['result_id'],protected=19229,frozen=34,selected=row(PUBLISHER),ACK=row(Q/'ACK_INITIAL.json'),all_execution=0)))
