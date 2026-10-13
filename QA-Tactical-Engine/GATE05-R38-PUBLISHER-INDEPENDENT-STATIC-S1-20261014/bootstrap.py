from common import *
import uuid
before=preservation();write(Q/'PRESERVATION_BEFORE.json',before)
paths=[Path(r['path']) for r in load(OLDQ/'RECOVERY_AUTHORITY_AUDIT.json')['files'] if Path(r['path']).exists()]
paths += [WP,CORR,RAWWIT,PKG/'MASTER_REVIEW_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES_E1_20261014.md',PKG/'MASTER_R38_PUBLISHER_BOUNDARIES_IMPLEMENTATION_CONTRACT_20261014.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R37_INDEPENDENT_STATIC_S1_20261014.md']
aud=[];txt=[]
for p in dict.fromkeys(paths):
    t=p.read_bytes().decode('utf-8-sig');aud.append(dict(**row(p),full_read=True));txt.append(dict(path=str(p),full_text=t))
write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=aud));write(Q/'RECOVERY_FULL_TEXT.json',dict(at=now(),files=txt))
fixed=[WP,BASE,MAN,S,ORACLE,OLDQ/'ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json',CORR,RAWWIT,PKG/'MASTER_REVIEW_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES_E1_20261014.md',PKG/'MASTER_R38_PUBLISHER_BOUNDARIES_IMPLEMENTATION_CONTRACT_20261014.md']+[Path(r['frozen_path']) for r in load(MAN)['files']]
oracle=load(ORACLE)
for key in ['literal_pair','literal_combined']:check([oracle[key]]);fixed.append(Path(oracle[key]['path']))
write(Q/'PASSIVE_INPUT_MANIFEST.json',dict(at=now(),files=[row(p) for p in dict.fromkeys(fixed)],read_only=True))
rid='SOL-GATE05-R38-PUBLISHER-INDEPENDENT-STATIC-S1-20261014-'+uuid.uuid4().hex
a=dict(at=now(),delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R38_PUBLISHER_INDEPENDENT_STATIC',stage='S1',result_id=rid,status='ACKNOWLEDGED_INITIAL_SCOPE_BOUND',wp_identity=row(WP),freeze_manifest=row(MAN),protected_baseline=row(BASE),publisher=row(S),publisher_MVID='NOT_APPLICABLE',initial_inventory=row(Q/'PRESERVATION_BEFORE.json'),timestamp_correction=row(CORR),scope='FROZEN_PUBLISHER_TEXT_STATIC_ONLY',publisher_Engine_compiler_fixture_native_adverse=0,Foundation='HOLD',native_E2='NOT_RELEASED',Master_disposition='PENDING')
write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a)
print(json.dumps(dict(ACK=row(Q/'ACK_INITIAL.json'),result_id=rid,protected=19676,frozen=42,authority_files=len(aud),all_candidate_execution=0),ensure_ascii=False))
