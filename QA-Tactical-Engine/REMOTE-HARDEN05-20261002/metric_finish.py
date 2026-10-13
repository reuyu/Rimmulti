from harness import *
import statistics,re,datetime
d=json.loads((ROOT/'final-metrics.json').read_text(encoding='utf-8'))
x=ET.fromstring(d['response']);rows=[dict(v.attrib) for v in x]
result={}
for k in ['bytes','cadenceMs','applyMs','rttMs']:
 vals=[float(v[k]) for v in rows];result[k]=dict(min=min(vals),max=max(vals),median=statistics.median(vals))
ev=(ROOT/'Phase1'/'GraphicalClient'/'qa-events.tsv').read_text(encoding='utf-8').splitlines();drains=[v for v in ev if 'RESULT_DRAIN' in v and '2026-10-02T11:35:1' in v]
result['stressDrainFirst']=drains[0] if drains else None;result['stressDrainLast']=drains[-1] if drains else None
result['stressDrainMs']=(datetime.datetime.fromisoformat(drains[-1].split('\t')[0])-datetime.datetime.fromisoformat(drains[0].split('\t')[0])).total_seconds()*1000 if drains else None
result['normalNetwork']=[v.split(' response=')[0] for v in ev if 'NETWORK_END ID=CMD_ee35c72e ' in v]
write('final-metric-summary.json',result);print(json.dumps(result,indent=2))
