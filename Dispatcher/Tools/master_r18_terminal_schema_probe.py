from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf8');Q=Path.cwd()/'QA-Tactical-Engine/GATE05-R18-CONFIG-ADMISSION-SEAL-INDEPENDENT-S1-20261010'
r=lambda n:json.loads((Q/n).read_text(encoding='utf-8-sig'))
s=r('INDEPENDENT_EXECUTION_SUMMARY.json');f=r('FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json')
print('SummaryKeys',list(s));print('runner',s.get('runner'));print('audit',r('SOURCE_REUSE_AND_ORACLE_AUDIT.json'));print('bindings tail',f['candidate_reference_bindings'][-3:])
tf=r('FULLTYPED_SCHEMA_AND_REFERENCE_BINDING.json')['typed_files'][10];print('typed sample',json.loads(Path(tf['file']['path']).read_text(encoding='utf8')))
print('thread keys',json.loads((Path.cwd()/'docs/WarEconomy_Master_Handoff_20261006/coordination/MASTER_SOL_R18_INDEPENDENT_TERMINAL_READ_20261010.json').read_text())['content'][0]['text'][:1000])
print('buildkeys',list(r('BUILD_TOOL_PROOF.json')));print('failurekeys',list(r('NORMAL_FAILURE_RECONCILIATION.json')));print('inventory firstcheck',r('RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json'))
print('producerkeys',list(r('PRODUCER_COVERAGE_AND_PACKAGING.json')))
print('completion',r('COMPLETION.json'))

