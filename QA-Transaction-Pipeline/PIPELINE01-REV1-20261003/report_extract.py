import json
from pathlib import Path
r=json.loads((Path(__file__).parent/'Evidence/results.json').read_text(encoding='utf-8'))
for k in ['caller-hash-authority','queue-starved-proof','aborted','fixture-mismatch-same-process','terminal-transition-api','storage-aggregate-constraint','native-locked','schema-wrong-pk-valid','schema-no-event-unique-valid']:
 v=r[k]
 if k=='terminal-transition-api':v={'transition':v['transition'],'statesBefore':[x['State'] for x in v['before']['OperationRecords']],'statesAfter':[x['State'] for x in v['after']['OperationRecords']]}
 if k.startswith('schema-'):v={a:b for a,b in v.items() if a!='db'}
 if k=='aborted':v={a:b for a,b in v.items() if a!='db'}
 if k in ['storage-aggregate-constraint','native-locked']:v={a:b for a,b in v.items() if a!='db'}
 print(k,json.dumps(v,ensure_ascii=False)[:4500])
for k in ['kill-after-consumer-effect','kill-after-server-ack','kill-before-cursor','kill-after-cursor']:
 v=r[k];print(k,json.dumps({'before':v.get('consumerBefore'),'after':v.get('consumerAfter'),'restart':v.get('restart')},ensure_ascii=False)[:2300])
