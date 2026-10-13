from pathlib import Path
import json
Q=Path('QA-Tactical-Engine/GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def small(d):
 if isinstance(d,dict):return {k:small(v) for k,v in d.items()}
 if isinstance(d,list):return {'count':len(d),'sample':small(d[0]) if d else None}
 if isinstance(d,str) and len(d)>250:return d[:250]+'...'
 return d
for n in ['ORACLE_BEFORE_BUILD.json','INDEPENDENT_EXECUTION_SUMMARY.json','ACTUAL_EXECUTION_SCOPE.json','RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json','PRODUCER_COVERAGE_AND_PACKAGING.json']:
 print(n,json.dumps(small(read(Q/n)),ensure_ascii=True))
root=next((Q/'runs').iterdir())
for n in ['RUN_TOOL_PROOF.json','HOST_RUN_PROCESS_OBSERVATION.json','ACTUAL_PROCESS_CONTEXT.json','POST_RUN_IDENTITY.json','ACTUAL_LOADED_PREPIN_BINDING.json','NORMAL_RESULTS.json']:
 print(n,json.dumps(small(read(root/n)),ensure_ascii=True))
