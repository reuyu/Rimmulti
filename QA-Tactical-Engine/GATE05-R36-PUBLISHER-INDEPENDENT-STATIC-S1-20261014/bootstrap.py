from common import *
import uuid
before=preserve();write(Q/'PRESERVATION_BEFORE.json',before)
old=load(ROOT/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-INDEPENDENT-STATIC-S1-20261013/RECOVERY_AUTHORITY_AUDIT.json')
authorities=[Path(r['path']) for r in old['files'] if Path(r['path']).exists()]
authorities += [WP,PKG/'MASTER_REVIEW_ENGINE_GATE05_R36_PUBLISHER_CONTRACT_E1_20261014.md',PKG/'MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md',PKG/'MASTER_R35_POLICY_AND_FILESYSTEM_CLAIM_CORRECTIONS_20261013.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R35_INDEPENDENT_STATIC_S1_20261013.md']
audit=[];texts=[]
for p in dict.fromkeys(authorities):
    b=p.read_bytes();text=b.decode('utf-8-sig');audit.append(dict(**row(p),full_read=True));texts.append(dict(path=str(p),text=text))
write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,latest_delta_read=True));write(Q/'RECOVERY_FULL_TEXT.json',dict(at=now(),texts=texts))
fixed=[WP,BASE,MAN,S,ORACLE,PKG/'MASTER_REVIEW_ENGINE_GATE05_R36_PUBLISHER_CONTRACT_E1_20261014.md',PKG/'MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md',PKG/'MASTER_R35_POLICY_AND_FILESYSTEM_CLAIM_CORRECTIONS_20261013.md']
fixed += [Path(r['frozen_path']) for r in load(MAN)['files']]
lit=load(ORACLE)
for key in ['literal_pair','literal_combined']:check([lit[key]]);fixed.append(Path(lit[key]['path']))
fixed += list(PREP.glob('*.json'))
write(Q/'PASSIVE_INPUT_MANIFEST.json',dict(at=now(),files=[row(p) for p in dict.fromkeys(fixed)],old_helpers_read_only_not_imported=True))
rid='SOL-GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-'+uuid.uuid4().hex
ack=dict(at=now(),delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R36_PUBLISHER_INDEPENDENT_STATIC',stage='S1',result_id=rid,status='ACKNOWLEDGED_INITIAL_SCOPE_BOUND',wp_identity=row(WP),freeze_manifest=row(MAN),protected_baseline=row(BASE),publisher=row(S),publisher_MVID='NOT_APPLICABLE',initial_inventory=row(Q/'PRESERVATION_BEFORE.json'),scope='FROZEN_SOURCE_TEXT_STATIC_ONLY',candidate_Engine_compiler_fixture_publisher_native_adverse=0,Foundation='HOLD',native_E2='NOT_RELEASED',master_disposition='PENDING')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(ACK=row(Q/'ACK_INITIAL.json'),result_id=rid,protected=len(before['protected_files']),frozen=len(before['frozen_files']),authority_files=len(audit),all_execution=0),ensure_ascii=False))
