from common import *
paths=[Path(r['path']) for r in load(OLD/'RECOVERY_AUTHORITY_AUDIT.json')['files']]
paths += [WP,EXTRA,SCOPE,PKG/'MASTER_REVIEW_ENGINE_GATE05_R34_INDEPENDENT_S1_20261013.md',PKG/'MASTER_R35_PLAN_ONLY_PUBLISHER_SAFETY_CONTRACT_20261013.md',PKG/'WP_ENGINE_GATE05_R35_PUBLISHER.md',PKG/'MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R29_STARTUP_PAIR_E1_20261012.md']
audit=[]
for p in dict.fromkeys(paths):
    text=permitted(p).read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text);audit.append(dict(**row(p),full_read=True))
write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,full_read=True,Master_findings_not_oracle=True))
write(Q/'PRESERVATION_BEFORE.json',preservation())
assert sha(PUBLISHER)=='0204609D1D9D8A697B1A0B88537419D78B9E506558C771CA3EDD4C50FD49D470'
assert sha(SOURCE)=='544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD'
assert sha(PAIR)=='7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02';assert sha(COMBINED)=='89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D'
write(Q/'FROZEN_ORIGINAL_INPUT_READS.json',dict(at=now(),files=[dict(**row(p),raw_utf8=p.read_bytes().decode('utf-8-sig'),TEXT_only=True) for p in [PUBLISHER,SOURCE,PAIR,COMBINED]],old_publisher_IMPORT_EXEC=False,mutable_R35_NOT_READ=True))
ack=dict(at=now(),delivery_id=DELIVERY,wp_id='WP_QA_ENGINE_GATE05_R35_PUBLISHER_PREPARATION',wp_revision='S1',result_id='SOL-GATE05-R35-PUBLISHER-PREP-S1-20261013-'+uuid.uuid4().hex,status='ACKNOWLEDGED_PASSIVE_PREPARATION',WP=row(WP),baseline=row(BASE),additional=row(EXTRA),freeze=row(MAN),frozen_publisher=row(PUBLISHER),frozen_source=row(SOURCE),literal_pair=row(PAIR),literal_combined=row(COMBINED),protected_count=19103,extra_count=1,frozen_count=75,compiler_candidate_fixturewriting_publisher_subprocess_native_adverse=0,R35='NOT_READ_NOT_REVIEWED',execution_admission=False,Foundation='HOLD',nativeE2='NOT_RELEASED',verdict='PENDING_PREPARATION')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(result_id=ack['result_id'],protected=19103,extra=1,frozen=75,ACK=row(Q/'ACK_INITIAL.json'),all_execution=0,R35='NOT_READ_NOT_REVIEWED')))
