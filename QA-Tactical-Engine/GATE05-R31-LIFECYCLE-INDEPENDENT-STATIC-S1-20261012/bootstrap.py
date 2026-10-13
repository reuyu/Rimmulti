from qa_common import *
import uuid
if __name__=='__main__':
    assert DELIVERY in WP.read_text(encoding='utf-8-sig')
    before=preservation();write(Q/'PRESERVATION_BEFORE.json',before)
    old=ROOT/'QA-Tactical-Engine/GATE05-R30-HANDOFF-INDEPENDENT-STATIC-S1-20261012';copied=[]
    for name in ['pe_pdb_reader.py','unity_reference_metadata.py']:
        src=old/name;dest=Q/name;assert not dest.exists();dest.write_bytes(src.read_bytes());assert dest.read_bytes()==src.read_bytes()
        copied.append(dict(old_source_TEXT_only=row(src),new_own_definition_module=row(dest),byte_exact_copy=True,old_top_level_helper_executed_or_imported=False))
    write(Q/'METADATA_READER_DEFINITION_PROVENANCE.json',dict(at=now(),copies=copied,scope='Only definition-only file-byte readers copied to new owned modules; never old top-level QA helpers or old verdict execution. No candidate/CLR load.'))
    from pe_pdb_reader import pe_metadata,portable_pdb
    mapping={r['original_path'].replace('/','\\').lower():Path(r['frozen_path']) for r in load(MAN)['files']};ids=[]
    for mode,mvid in [('Debug','f8c7c77e-e2c5-4d3e-9371-a4e349d433c9'),('Release','130c2741-3e20-4275-9891-d4aea8adffd3')]:
        dll=FROZEN/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');pe=pe_metadata(dll);pd=portable_pdb(pdb,mapping)
        assert pe['mvid']==mvid and pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==4 and all(r['matched'] for r in pd['documents'])
        ids.append(dict(mode=mode,DLL=row(dll),PDB=row(pdb),PE=pe,portable_PDB=pd,candidate_loaded=False))
    assert sha(SELECTED)=='F6C06D6B1392C5CF90483D047150D53A80193DED655850BF1A06FE65A72A52CE'
    assert sha(SELECTED.with_suffix('.pdb'))=='FDCE1F62777DC49C8F00DE1E7899B106564471983F2A34105F290491984BF466'
    assert sha(WORKER)=='CB1EE0A55512A6F578B2D7ABCACBE36B62327D9F3E585B6E4221725B6DADFFDB'
    write(Q/'INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json',dict(at=now(),reader=row(Q/'pe_pdb_reader.py'),candidates=ids,original_source_fallback=False,candidate_CLR_execution=0))
    files=[ROOT/'AGENTS.md',ROOT/'docs/요구사항_명세서.md',ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md']+[PKG/n for n in ['00_START_HERE.md','MASTER_HANDOFF.md','C_REVIEW_CORRECTIONS_CONSOLIDATED.md','C_REVIEW_HISTORY_EXTRACTS.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md','IDE_BOOTSTRAP_VERIFICATION.md','DISPATCHER_STATE.json','DISPATCH_JOURNAL.jsonl','ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md','reference_adrs/ADR-006B_Configuration_Content_Manifest_v2.md','MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md','MASTER_R31_DURABLE_STARTUP_LIFECYCLE_CONTRACT_20261012.md','MASTER_REVIEW_ENGINE_GATE05_R31_LIFECYCLE_E1_20261012.md']]+[PKG/'coordination'/n for n in ['MASTER_GATE05_R31_LIFECYCLE_E1_VERIFICATION_20261012.json','MASTER_R31_SOURCE_AND_EVIDENCE_AUDIT_20261012.json','MASTER_R31_RAW_STDOUT_HASH_DISCREPANCY_20261012.json']]+[ROOT/'Dispatcher'/n for n in ['README.md','MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md','MASTER_COMMUNICATION_STATE.json','MASTER_RECEIPTS.json','MASTER_MONITOR_JOURNAL.jsonl']]
    audit=[]
    for p in files:
        text=p.read_text(encoding='utf-8-sig');audit.append(dict(row(p),read_all=True));print('READ',p.name,len(text))
    write(Q/'RECOVERY_AND_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,read_all=True,Master_findings_not_oracle=True,C_guard_preserved=True,Dedicated_Server_final_DomainAuthority=True,Foundation='HOLD',nativeE2='NOT_RELEASED'))
    result='SOL-GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012-'+uuid.uuid4().hex
    ack=dict(at=now(),wp_id='WP_QA_ENGINE_GATE05_R31_LIFECYCLE_INDEPENDENT_STATIC',wp_revision='S1',delivery_id=DELIVERY,result_id=result,status='ACKNOWLEDGED_FROZEN_READONLY_INDEPENDENT_STATIC',wp=row(WP),baseline=row(BASELINE),freeze=row(MAN),selected=row(SELECTED),selected_mvid=ids[0]['PE']['mvid'],matching_PDB=row(SELECTED.with_suffix('.pdb')),source=row(WORKER),PE_PDB_sources_both='4/4',protected_paths=15854,frozen_files=131,candidate_compiler_runner_global_native_game_adverse_calls=0,prior_PASS_inherited=False,static_verdict='PENDING',Foundation='HOLD',nativeE2='NOT_RELEASED')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
    print(json.dumps(dict(result_id=result,protected=15854,frozen=131,source_PDB4of4_both=True,ACK=row(Q/'ACK_INITIAL.json'),candidate_calls=0)))
