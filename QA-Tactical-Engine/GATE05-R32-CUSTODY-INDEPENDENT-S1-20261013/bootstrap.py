from common import *
import ast,sys
files=[Path(r['path']) for r in load(ROOT/'QA-Tactical-Engine/GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012/RECOVERY_AND_AUTHORITY_AUDIT.json')['files']]
files += [WP,PKG/'MASTER_REVIEW_ENGINE_GATE05_R32_CUSTODY_E1_20261013.md',PKG/'MASTER_R32_MANAGED_CUSTODY_RESOURCE_CONTRACT_20261012.md',PKG/'MASTER_REVIEW_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S3_20261012.md',BINDING]+[PKG/'coordination'/n for n in ['MASTER_GATE05_R32_CUSTODY_E1_VERIFICATION_20261013.json','MASTER_R32_SOURCE_BUILD_EVIDENCE_AUDIT_20261013.json']]
audit=[]
for p in files:
    text=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text);audit.append(dict(**row(p),read_all=True))
write(Q/'RECOVERY_AND_AUTHORITY_AUDIT.json',dict(at=now(),files=audit,full_read=True,Master_inputs_not_oracle=True,Foundation='HOLD',nativeE2='NOT_RELEASED'))
write(Q/'PRESERVATION_BEFORE.json',preservation())
assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
check(load(DEP)['files'],'frozen_path','size')
assert sha(NJ)=='E1E27AF7B07EEEDF5CE71A9255F0422816A6FC5849A483C6714E1B472044FA9D' and NJ.stat().st_size==711952
assert sha(BINDING)=='0149D8E9B9B98848B541A0B6A75A23FCE300878E83EEF3F21E7FE352D083B318'
binding=load(BINDING)
check(list(binding['independent_literal_oracles'].values())+[binding['old_template_source'],binding['old_full_callplan']])
texts=[]
for entry in list(binding['independent_literal_oracles'].values())+[binding['old_template_source'],binding['old_full_callplan']]:
    p=Path(entry['path']);text=p.read_bytes().decode('utf-8-sig');texts.append(dict(**row(p),raw_utf8=text,TEXT_only=True))
write(Q/'ORACLE_TEMPLATE_TEXT_INSPECTION.json',dict(at=now(),files=texts,old_helper_executed_imported=False,expected_not_candidate_derived=True))
copied=[]
prior=ROOT/'QA-Tactical-Engine/GATE05-R31-LIFECYCLE-INDEPENDENT-STATIC-S1-20261012'
for name in ['pe_pdb_reader.py','unity_reference_metadata.py']:
    p=prior/name;txt=p.read_bytes().decode('utf-8-sig');tree=ast.parse(txt)
    assert all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) for n in tree.body)
    dest=Q/name;assert not dest.exists();dest.write_bytes(p.read_bytes());copied.append(dict(source_TEXT_only=row(p),new_definition=row(dest),raw_utf8=txt,old_top_level_executed=False))
write(Q/'METADATA_DEFINITION_PROVENANCE.json',dict(at=now(),copies=copied))
from pe_pdb_reader import pe_metadata,portable_pdb
mapping={}
for r in load(MAN)['files']:
    key=r['original_path'].replace('/','\\').lower();p=Path(r['frozen_path'])
    if key in mapping:assert sha(mapping[key])==sha(p)
    mapping[key]=p
ids=[]
for mode,mvid in [('Debug','7d436c98-659a-4df1-a085-06fe9e55a0bc'),('Release','cee8068e-e814-4203-8135-8c0fd5107005')]:
    dll=FROZEN/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');pe=pe_metadata(dll);pd=portable_pdb(pdb,mapping)
    assert pe['mvid']==mvid and pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==4 and all(d['matched'] for d in pd['documents'])
    ids.append(dict(mode=mode,DLL=row(dll),PDB=row(pdb),PE=pe,portable_PDB=pd,candidate_loaded=False))
assert sha(SELECTED)=='0B23C358E8C8FC16FCD02DDE654AD8AE763EA177460BB15F5F1E1B1F0CB67E26' and SELECTED.stat().st_size==325632
assert sha(SELECTED.with_suffix('.pdb'))=='226DF5428AB94D48E0B08DC237AF3FC2E9F193315FE4D2F6EE2A8654B512E90D'
assert sha(WORKER)=='214F1F95C6BF7F547ED47FD91B787A70B2E52DFF129A882DCD8C1AC1471A24E8'
write(Q/'FROZEN_PE_PDB_IDENTITY.json',dict(at=now(),candidates=ids,frozen_mapping_only=True,source4of4_both=True,candidate_CLR_load=0))
ack=dict(at=now(),delivery_id=DELIVERY,wp_id='WP_QA_ENGINE_GATE05_R32_CUSTODY_INDEPENDENT',wp_revision='S1',result_id='SOL-GATE05-R32-CUSTODY-INDEPENDENT-S1-20261013-'+uuid.uuid4().hex,status='ACKNOWLEDGED_STATIC_AND_FRESH_NORMAL_QA',wp=row(WP),freeze=row(MAN),baseline=row(BASELINE),oracle_template_binding=row(BINDING),selected=row(SELECTED),selected_mvid=ids[0]['PE']['mvid'],PDB=row(SELECTED.with_suffix('.pdb')),source=row(WORKER),protected_paths=16026,frozen_files=64,initial_build_runner_calls=0,production_build_modify=0,native_execution=0,prior_PASS_inherited=False,verdict='PENDING',Foundation='HOLD')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(result_id=ack['result_id'],protected=16026,frozen=64,source4of4_both=True,ACK=row(Q/'ACK_INITIAL.json'),candidate_calls=0)))
