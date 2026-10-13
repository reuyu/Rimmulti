from common import *
import ast,difflib
paths=[Path(r['path']) for r in load(OLD/'RECOVERY_AUTHORITY_AND_SUPPLEMENT_AUDIT.json')['files']]
paths += [WP,BINDING,PKG/'MASTER_REVIEW_ENGINE_GATE05_R33_INDEPENDENT_S1_20261013.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R34_ROLLBACK_E1_20261013.md',PKG/'MASTER_R34_ROLLBACK_ORDERING_CONTRACT_20261013.md']+[PKG/'coordination'/n for n in ['MASTER_GATE05_R34_ROLLBACK_E1_VERIFICATION_20261013.json','MASTER_R34_SOURCE_BUILD_EVIDENCE_AUDIT_20261013.json']]
audit=[]
for p in dict.fromkeys(paths):
    s=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+s);audit.append(dict(**row(p),full_read=True))
write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,full_read=True,Master_findings_not_oracle=True,no_native_authority=True))
write(Q/'PRESERVATION_BEFORE.json',preservation())
assert sha(BINDING)=='CAFA657377B413E188C1B86F9EBA733E42171DF1B14607E690A1701035EFAF3E'
bind=load(BINDING);entries=list(bind['literal_oracles'].values())+[bind['old_template_TEXT_only'],bind['old_callplan'],bind['old_combined_literal']];check(entries)
write(Q/'ORACLE_TEMPLATE_FULL_TEXT_INSPECTION.json',dict(at=now(),files=[dict(**row(Path(r['path'])),raw_utf8=Path(r['path']).read_bytes().decode('utf-8-sig'),TEXT_only=True) for r in entries],old_helper_EXEC_IMPORT=False))
copies=[]
for name in ['pe_pdb_reader.py','unity_reference_metadata.py']:
    p=OLD/name;s=p.read_bytes().decode('utf-8-sig');tree=ast.parse(s);assert all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) for n in tree.body)
    dest=Q/name;assert not dest.exists();dest.write_bytes(p.read_bytes());copies.append(dict(old_TEXT=row(p),new_definition=row(dest),raw_utf8=s,byte_exact=True))
write(Q/'DEFINITION_ONLY_READER_PROVENANCE.json',dict(at=now(),copies=copies,old_top_level_EXEC_IMPORT=False))
from pe_pdb_reader import pe_metadata,portable_pdb
mapping={}
for r in load(MAN)['files']:
    k=r['original_path'].replace('/','\\').lower();p=Path(r['frozen_path'])
    if k in mapping:assert sha(mapping[k])==sha(p)
    mapping[k]=p
ids=[]
for mode,mid in [('Debug',MVID),('Release','93bc479a-cd1d-4d11-8d86-3364fc5e4180')]:
    dll=FROZEN/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');pe=pe_metadata(dll);pd=portable_pdb(pdb,mapping)
    assert pe['mvid']==mid and pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==4 and all(d['matched'] for d in pd['documents']);ids.append(dict(mode=mode,DLL=row(dll),PDB=row(pdb),PE=pe,portable_PDB=pd,candidate_loaded=False))
assert sha(SELECTED)==SELECTED_SHA and SELECTED.stat().st_size==326144
assert sha(SELECTED.with_suffix('.pdb'))=='FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE'
assert sha(WORKER)=='544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD'
write(Q/'FROZEN_PE_PDB_IDENTITY.json',dict(at=now(),candidates=ids,source4of4_both=True,no_mutable_source_fallback=True,candidate_CLR_load=0))
assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481';check(load(DEP)['files'],'frozen_path','size');assert sha(NJ)=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D'
ack=dict(at=now(),delivery_id=DELIVERY,wp_id='WP_QA_ENGINE_GATE05_R34_ROLLBACK_INDEPENDENT',wp_revision='S1',result_id='SOL-GATE05-R34-ROLLBACK-INDEPENDENT-S1-20261013-'+uuid.uuid4().hex,status='ACKNOWLEDGED_STATIC_AND_FRESH_NORMAL_QA',WP=row(WP),baseline=row(BASELINE),freeze=row(MAN),selected=row(SELECTED),selected_mvid=MVID,PDB=row(SELECTED.with_suffix('.pdb')),source=row(WORKER),oracle_binding=row(BINDING),protected_count=18163,frozen_count=75,source4of4_both=True,initial_compiler_runner_candidate_calls=0,old_PASS_inherited=False,Foundation='HOLD',nativeE2='NOT_RELEASED',verdict='PENDING')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(result_id=ack['result_id'],protected=18163,frozen=75,source4of4_both=True,ACK=row(Q/'ACK_INITIAL.json'),compiler_runner_candidate_calls=0)))
