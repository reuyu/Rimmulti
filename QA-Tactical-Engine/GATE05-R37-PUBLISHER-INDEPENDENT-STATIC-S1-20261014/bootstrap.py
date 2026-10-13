from common import *
import uuid
b=preservation();write(Q/'PRESERVATION_BEFORE.json',b)
catalog=load(OLDQ/'RECOVERY_AUTHORITY_AUDIT.json');paths=[Path(r['path']) for r in catalog['files'] if Path(r['path']).exists()]
paths += [WP,PKG/'MASTER_REVIEW_ENGINE_GATE05_R37_PUBLISHER_FINAL_E1_20261014.md',PKG/'MASTER_R37_PUBLISHER_FINAL_IMPLEMENTATION_CONTRACT_20261014.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R36_INDEPENDENT_STATIC_S1_20261014.md']
texts=[];audit=[]
for p in dict.fromkeys(paths):
    t=p.read_bytes().decode('utf-8-sig');audit.append(dict(**row(p),full_read=True));texts.append(dict(path=str(p),full_text=t))
write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=audit));write(Q/'RECOVERY_FULL_TEXT.json',dict(at=now(),files=texts))
fixed=[WP,BASE,MAN,S,ORACLE,OLDQ/'ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json',PKG/'MASTER_REVIEW_ENGINE_GATE05_R37_PUBLISHER_FINAL_E1_20261014.md',PKG/'MASTER_R37_PUBLISHER_FINAL_IMPLEMENTATION_CONTRACT_20261014.md',PKG/'MASTER_R35_POLICY_AND_FILESYSTEM_CLAIM_CORRECTIONS_20261013.md']+[Path(r['frozen_path']) for r in load(MAN)['files']]
oracle=load(ORACLE)
for key in ['literal_pair','literal_combined']:check([oracle[key]]);fixed.append(Path(oracle[key]['path']))
write(Q/'PASSIVE_INPUT_MANIFEST.json',dict(at=now(),files=[row(p) for p in dict.fromkeys(fixed)],read_only=True,old_helpers_executed=False))
rid='SOL-GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-'+uuid.uuid4().hex
ack=dict(at=now(),delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R37_PUBLISHER_INDEPENDENT_STATIC',stage='S1',result_id=rid,status='ACKNOWLEDGED_INITIAL_SCOPE_BOUND',wp_identity=row(WP),freeze_manifest=row(MAN),protected_baseline=row(BASE),publisher=row(S),publisher_MVID='NOT_APPLICABLE',initial_inventory=row(Q/'PRESERVATION_BEFORE.json'),scope='FROZEN_PUBLISHER_TEXT_STATIC_ONLY',publisher_Engine_compiler_fixture_native_adverse=0,Foundation='HOLD',native_E2='NOT_RELEASED',Master_disposition='PENDING')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(ACK=row(Q/'ACK_INITIAL.json'),result_id=rid,protected=19530,frozen=42,authority_files=len(audit),syntax_prechecked=True,all_candidate_execution=0),ensure_ascii=False))
