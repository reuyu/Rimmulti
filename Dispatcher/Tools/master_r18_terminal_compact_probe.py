from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf8');Q=Path.cwd()/'QA-Tactical-Engine/GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010'
for name in ['INDEPENDENT_EXECUTION_SUMMARY.json','FRESH_PROCESS_PROOF.json','ORACLE_BEFORE_BUILD.json','EXECUTION_ADMISSION_BEFORE_BUILD.json','METADATA_REVIEW_RECONCILIATION.json','NORMAL_FAILURE_RECONCILIATION.json','SOURCE_REUSE_AND_ORACLE_AUDIT.json','FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json','BUILD_TOOL_PROOF.json','BUILD_CAPTURE_LIMITATIONS.json','ACTUAL_EXECUTION_SCOPE.json']:
 d=json.loads((Q/name).read_text(encoding='utf-8-sig'));out={}
 for k,v in d.items():
  if isinstance(v,list):out[k]={'count':len(v),'sample':v[:1]}
  else:out[k]=v
 s=json.dumps(out,ensure_ascii=False,indent=2);print(name+'\n'+s[:6200])

