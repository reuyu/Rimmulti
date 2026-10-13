from common import *
import ast,sys
paths=[Path(r['path']) for r in load(OLD/'RECOVERY_AND_AUTHORITY_AUDIT.json')['files']]
paths += [WP,SUP,HELPERS,BINDING,PKG/'MASTER_REVIEW_ENGINE_GATE05_R33_RESOURCE_COMMIT_E1_20261013.md',PKG/'MASTER_R33_RESOURCE_ADMISSION_ORDERING_CONTRACT_20261013.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R32_INDEPENDENT_S1_20261013.md']+[PKG/'coordination'/n for n in ['MASTER_GATE05_R33_RESOURCE_COMMIT_E1_VERIFICATION_20261013.json','MASTER_R33_SOURCE_BUILD_EVIDENCE_AUDIT_20261013.json']]
paths += [Path(load(SUP)[k]['path']) for k in ['preparation_review','preparation_proof','additional_protected_manifest']]
audit=[]
for p in dict.fromkeys(paths):
    text=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text);audit.append(dict(**row(p),full_read=True))
write(Q/'RECOVERY_AUTHORITY_AND_SUPPLEMENT_AUDIT.json',dict(at=now(),files=audit,full_read=True,Master_findings_not_oracle=True,no_native_authority=True))
write(Q/'PRESERVATION_BEFORE.json',preservation())
assert sha(BINDING)=='213ED11C59A5C66CAB0FB4D8E8C7E1D2F6B5232CB263545B5D08FBDA6D5D787F'
bind=load(BINDING);entries=list(bind['literal_oracles'].values())+[bind['old_template_TEXT_only'],bind['old_callplan'],bind['old_combined_literal']];check(entries)
write(Q/'ORACLE_TEMPLATE_FULL_TEXT_INSPECTION.json',dict(at=now(),files=[dict(**row(Path(r['path'])),raw_utf8=Path(r['path']).read_bytes().decode('utf-8-sig'),TEXT_only=True) for r in entries],old_helper_EXEC_IMPORT=False))
copies=[]
for name in ['pe_pdb_reader.py','unity_reference_metadata.py']:
    p=OLD/name;text=p.read_bytes().decode('utf-8-sig');tree=ast.parse(text);assert all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) for n in tree.body)
    dest=Q/name;assert not dest.exists();dest.write_bytes(p.read_bytes());copies.append(dict(old_TEXT=row(p),new_definition=row(dest),raw_utf8=text))
write(Q/'DEFINITION_ONLY_READER_PROVENANCE.json',dict(at=now(),copies=copies,old_top_level_EXEC_IMPORT=False))
from pe_pdb_reader import pe_metadata,portable_pdb
mapping={}
for r in load(MAN)['files']:
    k=r['original_path'].replace('/','\\').lower();p=Path(r['frozen_path'])
    if k in mapping:assert sha(mapping[k])==sha(p)
    mapping[k]=p
ids=[]
for mode,mvid in [('Debug','adb6cbc8-c4f9-4436-b137-d550d683f493'),('Release','c739a55b-d61c-43b0-a16d-6e38edf57e62')]:
    dll=FROZEN/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');pe=pe_metadata(dll);pd=portable_pdb(pdb,mapping);assert pe['mvid']==mvid and pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==4 and all(d['matched'] for d in pd['documents']);ids.append(dict(mode=mode,DLL=row(dll),PDB=row(pdb),PE=pe,portable_PDB=pd,candidate_loaded=False))
assert sha(SELECTED)=='EC01A3B368E385B2EAA35064BBD5EFC3971FCBED7609ADF3CEE8490146241764' and SELECTED.stat().st_size==326144
assert sha(SELECTED.with_suffix('.pdb'))=='E4A047822B52CC09608512E6D0714B99BE9A670676DAB5AF747FC2094DD6EF40'
assert sha(WORKER)=='6E45362C4D34566F7612AA626E31DD8E15BCCE5232FB3815117E43B019CA597D'
write(Q/'FROZEN_PE_PDB_IDENTITY.json',dict(at=now(),candidates=ids,source4of4_both=True,no_mutable_source_fallback=True,candidate_CLR_load=0))
assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481';check(load(DEP)['files'],'frozen_path','size');assert sha(NJ)=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D'
ack=dict(at=now(),delivery_id=DELIVERY,wp_id='WP_QA_ENGINE_GATE05_R33_RESOURCE_COMMIT_INDEPENDENT',wp_revision='S1',result_id='SOL-GATE05-R33-RESOURCE-COMMIT-INDEPENDENT-S1-20261013-'+uuid.uuid4().hex,status='ACKNOWLEDGED_STATIC_AND_NEW_NORMAL_QA',WP=row(WP),baseline=row(BASELINE),supplement=row(SUP),freeze=row(MAN),selected=row(SELECTED),selected_mvid=ids[0]['PE']['mvid'],PDB=row(SELECTED.with_suffix('.pdb')),source=row(WORKER),oracle_binding=row(BINDING),protected17099=True,prep_terminal54=True,outside_helpers6=True,source4of4_both=True,initial_compiler_runner_candidate_calls=0,old_PASS_inherited=False,Foundation='HOLD',nativeE2='NOT_RELEASED',verdict='PENDING')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(result_id=ack['result_id'],protected=17099,terminal=54,helpers=6,frozen=71,source4of4_both=True,ACK=row(Q/'ACK_INITIAL.json'),compiler_runner_candidate_calls=0)))
