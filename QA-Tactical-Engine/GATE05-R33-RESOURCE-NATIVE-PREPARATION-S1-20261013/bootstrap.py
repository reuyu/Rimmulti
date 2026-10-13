from common import *
import ast,sys
old=ROOT/'QA-Tactical-Engine/GATE05-R32-CUSTODY-INDEPENDENT-S1-20261013'
files=[Path(r['path']) for r in load(old/'RECOVERY_AND_AUTHORITY_AUDIT.json')['files']]
files += [WP,SCOPE,PKG/'MASTER_REVIEW_ENGINE_GATE05_R32_INDEPENDENT_S1_20261013.md',PKG/'MASTER_R33_RESOURCE_ADMISSION_ORDERING_CONTRACT_20261013.md',PKG/'WP_ENGINE_GATE05_R33_RESOURCE_COMMIT.md',PKG/'coordination/MASTER_SOL_R32_COMPLETION_VERIFICATION_20261013.json',ROOT/'docs/QA_EngineHost_Gate05_R32_Custody_Independent_S1_20261013.md',old/'STATIC_CUSTODY_RESOURCE_REVIEW.json',old/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json']
hist=ROOT/'QA-Tactical-Engine/GATE05-R16-OPERATOR-NATIVE-PREP-S1-20261010'
files += [hist/n for n in ['PROSPECTIVE_ADMISSION_CRITERIA.json','NORMAL_NATIVE_QA_PLAN.md','NATIVE_PHASE_OUTPUT_PROTOCOL.json','INDEPENDENT_OPERATOR_AUTHORITY_MATRIX.json','RUNTIME_GAP_REVIEW.json','ACTUAL_PREPARATION_SCOPE.json']]
files += [PKG/'WP_QA_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION_S1.md',ROOT/'docs/QA_EngineHost_Gate05_R16_Operator_Native_Preparation_S1_20261010.md',ROOT/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012/PROVENANCE_AND_NATIVE_BOUNDARY_CRITERIA.json']
audit=[]
for p in dict.fromkeys(files):
    text=p.read_bytes().decode('utf-8-sig');print(str(p)+'\n'+text);audit.append(dict(**row(p),read_all=True))
write(Q/'RECOVERY_AND_PREPARATION_INPUT_AUDIT.json',dict(at=now(),files=audit,full_read=True,historical_inputs_not_execution_admission=True,R33_mutable_not_read=True))
write(Q/'PRESERVATION_BEFORE.json',preservation())
p=old/'pe_pdb_reader.py';text=p.read_bytes().decode('utf-8');tree=ast.parse(text)
assert all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) for n in tree.body)
dest=Q/'pe_pdb_reader.py';assert not dest.exists();dest.write_bytes(p.read_bytes())
write(Q/'PASSIVE_READER_INPUT_PIN.json',dict(at=now(),source_TEXT_only=row(p),new_definition=row(dest),python=row(Path(sys.executable)),script=row(Path(__file__)),old_top_level_helper_executed=False,candidate_load=0))
from pe_pdb_reader import pe_metadata,portable_pdb
mapping={}
for r in load(MAN)['files']:
    key=r['original_path'].replace('/','\\').lower();path=Path(r['frozen_path'])
    if key in mapping:assert sha(mapping[key])==sha(path)
    mapping[key]=path
pe=pe_metadata(SELECTED);pd=portable_pdb(SELECTED.with_suffix('.pdb'),mapping)
assert sha(SELECTED)=='0B23C358E8C8FC16FCD02DDE654AD8AE763EA177460BB15F5F1E1B1F0CB67E26' and pe['mvid']=='7d436c98-659a-4df1-a085-06fe9e55a0bc'
assert sha(SELECTED.with_suffix('.pdb'))=='226DF5428AB94D48E0B08DC237AF3FC2E9F193315FE4D2F6EE2A8654B512E90D'
assert sha(WORKER)=='214F1F95C6BF7F547ED47FD91B787A70B2E52DFF129A882DCD8C1AC1471A24E8'
assert pe['codeview']['guid']==pd['pdb_guid'] and len(pd['documents'])==4 and all(d['matched'] for d in pd['documents'])
write(Q/'FROZEN_R32_PASSIVE_IDENTITY.json',dict(at=now(),selected=row(SELECTED),PDB=row(SELECTED.with_suffix('.pdb')),source=row(WORKER),PE=pe,portable_PDB=pd,R33_candidate='NOT_READ_NOT_REVIEWED',candidate_execution=0))
ack=dict(at=now(),delivery_id=DELIVERY,wp_id='WP_QA_ENGINE_GATE05_R33_RESOURCE_NATIVE_PREPARATION',wp_revision='S1',result_id='SOL-GATE05-R33-RESOURCE-NATIVE-PREP-S1-20261013-'+uuid.uuid4().hex,status='ACKNOWLEDGED_FROZEN_R32_PREPARATION_ONLY',wp=row(WP),protected_baseline=row(BASELINE),additive_helper_manifest=row(EXTRA),freeze=row(MAN),selected=row(SELECTED),selected_mvid=pe['mvid'],PDB=row(SELECTED.with_suffix('.pdb')),source=row(WORKER),R33='NOT_READ_NOT_REVIEWED',candidate_compiler_runner_native_global_operator_adverse_execution=0,prior_PASS_inherited=False,readiness='PENDING_PREPARATION',nativeE2='NOT_RELEASED',Foundation='HOLD')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(result_id=ack['result_id'],protected=16929,additional_helpers=5,frozen_R32=64,PDBsource4of4=True,ACK=row(Q/'ACK_INITIAL.json'),mutable_R33_reads_hashes=0,executions=0)))
