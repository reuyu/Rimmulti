from pathlib import Path
import ast
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent
old=ROOT/'QA-Tactical-Engine/GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-INDEPENDENT-S1-20261010/review_setup.py'
s=old.read_text(encoding='utf-8-sig');s=s[:s.index("if __name__=='__main__':")]
s=s.replace('MASTER_R15_QA_INDEPENDENT_PROTECTED_BASELINE','MASTER_R16_QA_PREPARATION_PROTECTED_BASELINE').replace('31800C456401B3BDA72054586B2D740D6737CF61FF1B8F76C7A137E0748A02E4','4B567A39019F6033F81F8A97E91FD583674F8E799F2804A25E02405448444AE3').replace('7994','8932').replace('WP_QA_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY_INDEPENDENT_S1','WP_QA_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION_S1').replace('991B50388CCBD932C8C4F83D8B76D72012C94F014084013B1687489EDCBB1FE7','7EF30FCFB9638FFA92282350D9DB40C5D4EB4551D108BFAC2222689361E7C74E').replace('QA_EngineHost_Gate05_R15_Public_Manifest_Boundary_Independent_S1_20261010','QA_EngineHost_Gate05_R16_Operator_Native_Preparation_S1_20261010').replace('R15_LINEAGE.json','R16_FROZEN_LINEAGE.json')
s+='''\nif __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010-01',result_id='SOL-GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Independent read-only operator16dimension/source RuntimeCopy7 readiness andfuture normalnative QAcriteria only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Exact R15 source/PE-PDB metadata only;candidate orQA runnerbuildloadexecute0','RuntimeCopy7 existingfiles metadata only;no assets copy/install/native/operator/game/adverse0','A in-progress R16outputs notread','Preparation notnativePASS/E2/closure/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=8932,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
'''
assert not (Q/'review_setup.py').exists();(Q/'review_setup.py').write_text(s,encoding='utf-8')
print('Own R16 metadata setup written;no old top-level module import')
