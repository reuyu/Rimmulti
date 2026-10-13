from qa_common import *
from pe_pdb_reader import pe_metadata,portable_pdb
import uuid
if __name__=='__main__':
    assert sha(WP)=='99CA237E250CE2D714101526C18A7AF1DCBED86A7DCBD636E87E4670AD571503'
    before=preservation();write(Q/'PRESERVATION_BEFORE.json',before)
    mapping={r['original_path'].replace('/','\\').lower():Path(r['frozen_path']) for r in load(MAN)['files']}
    identities=[]
    for mode,mvid in [('Debug','71b83cb9-f67f-4520-b611-6b8d0d4d2860'),('Release','7ffbba39-9a18-434b-ac07-93886e829c9f')]:
        dll=FROZEN/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb')
        pe=pe_metadata(dll);pd=portable_pdb(pdb,mapping)
        assert pe['mvid']==mvid and pe['codeview']['guid']==pd['pdb_guid']
        assert len(pd['documents'])==4 and all(d['matched'] for d in pd['documents'])
        identities.append(dict(mode=mode,dll=row(dll),PDB=row(pdb),PE=pe,portable_PDB=pd,candidate_loaded=False))
    assert sha(SELECTED)=='9142C63AF18E2AE028D9E44AC36277F2FEBFFBB7AE8B6AF2437D12CED288C706'
    assert sha(SELECTED.with_suffix('.pdb'))=='4BCF43B7E9FBF84D11FF677708C050415E68032CF1A0BACADA3CF46E13B8E28A'
    write(Q/'INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json',dict(at=now(),reader=row(Q/'pe_pdb_reader.py'),candidates=identities,Assembly_Load_and_CLR_candidate_execution=0))
    recovery=[ROOT/'AGENTS.md',ROOT/'docs/요구사항_명세서.md',ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md']+[PKG/n for n in ['00_START_HERE.md','MASTER_HANDOFF.md','C_REVIEW_CORRECTIONS_CONSOLIDATED.md','C_REVIEW_HISTORY_EXTRACTS.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md','IDE_BOOTSTRAP_VERIFICATION.md','DISPATCHER_STATE.json','DISPATCH_JOURNAL.jsonl','ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md','reference_adrs/ADR-006B_Configuration_Content_Manifest_v2.md','MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md','WP_ENGINE_GATE05_R30_HANDOFF.md','MASTER_REVIEW_ENGINE_GATE05_R30_HANDOFF_E1_20261012.md']]+[ROOT/'Dispatcher'/n for n in ['README.md','MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md','MASTER_COMMUNICATION_STATE.json','MASTER_RECEIPTS.json','MASTER_MONITOR_JOURNAL.jsonl']]
    audit=[]
    for p in recovery:
        text=p.read_text(encoding='utf-8-sig');audit.append(dict(row(p),read_all=True))
        print('\nRECOVERY',p.name);print('\n'.join(text.splitlines()[:3]+text.splitlines()[-3:]))
    write(Q/'RECOVERY_AND_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,read_all=True,Dedicated_Server_final_authority=True,C_guards_unchanged=True,Foundation='HOLD',native_E2='NOT_RELEASED'))
    result='SOL-GATE05-R30-HANDOFF-INDEPENDENT-STATIC-S1-20261012-'+uuid.uuid4().hex
    ack=dict(at=now(),wp_id='WP_QA_ENGINE_GATE05_R30_HANDOFF_INDEPENDENT_STATIC',wp_revision='S1',delivery_id=DELIVERY,result_id=result,status='ACKNOWLEDGED_READONLY_INDEPENDENT_STATIC',wp=row(WP),freeze=row(MAN),baseline=row(BASELINE),selected=row(SELECTED),selected_mvid=identities[0]['PE']['mvid'],matching_PDB=row(SELECTED.with_suffix('.pdb')),initial_protected_paths=15549,frozen_files=128,PE_PDB_sources_both='4/4',candidate_compiler_runner_game_native_global_adverse_calls=0,static_verdict='PENDING',R29_PASS_inherited=False,Foundation='HOLD',native_E2='NOT_RELEASED')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
    print(json.dumps(dict(result_id=result,protected=15549,frozen=128,source_PDB_docs='both4of4',selected_mvid=identities[0]['PE']['mvid'],ACK=row(Q/'ACK_INITIAL.json'),candidate_compiler_runner_native_calls=0)))
