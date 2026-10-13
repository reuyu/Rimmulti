from harness import *
import re,collections,datetime,statistics
ev=(ROOT/'GraphicalClient'/'qa-events.tsv').read_text(encoding='utf-8-sig').splitlines()
frames=(ROOT/'GraphicalClient'/'qa-frame-gaps.tsv').read_text(encoding='utf-8-sig').splitlines()
proxy=json.loads((ROOT/'proxy-records.json').read_text(encoding='utf-8'))
commands=[]
for rec in proxy:
 c=rec['command'];id=c['CommandId'];lines=[e for e in ev if id in e and ('NETWORK_BEGIN' in e or 'NETWORK_END' in e or 'ASYNC_EXIT' in e)]
 begin=next((e for e in lines if 'NETWORK_BEGIN' in e),None);end=next((e for e in lines if 'NETWORK_END' in e),None)
 a=rec['utc'];b=rec.get('forwardedUTC',a+6)
 gaps=[float(re.search(r'gapMs=([0-9.]+)',x)[1]) for x in frames if a<=datetime.datetime.fromisoformat(x.split('\t')[0]).timestamp()<=b]
 commands.append(dict(command=c,fault=rec.get('fault'),workerDraft=pawn(rec['response'].get('Snapshot',{})).get('Drafted') if rec['response'].get('Snapshot') else None,begin=begin,end=end,maxFrameGapMs=max(gaps) if gaps else None,frames=len(gaps)))
write('command-fault-summary.json',commands)
rows=[]
for name in ['menu-east','west-turn','north','south','east']:
 samples=json.loads((ROOT/(name+'-samples.json')).read_text(encoding='utf-8'));a=[]
 for i in samples:
  w=ET.fromstring(i['worker']['response']).find("pawn[@id='Human302']");c=ET.fromstring(i['client']['response']).find("pawn[@id='Human302']")
  a.append(dict(utc=i['utc'],worker=dict(w.attrib),client=dict(c.attrib)))
 write(name+'-pose-table.json',a)
 moving=[x for x in a if x['worker']['pathMoving']=='true'];rots=collections.Counter(x['worker']['rotation'] for x in moving)
 rows.append(dict(name=name,movingSamples=len(moving),rotations=dict(rots),workerStart=a[0]['worker']['position'],workerEnd=a[-1]['worker']['position']))
write('movement-summary.json',rows)
g=json.loads((ROOT/'regression-checks.json').read_text(encoding='utf-8'));batches=json.loads((ROOT/'queue-stress-batches.json').read_text(encoding='utf-8'))
print(json.dumps(dict(movement=rows,queues=[e['response'].split(' ',2)[:2] for e in batches],auth=[r['parsed']['Status'] for r in g['auth']],priv=[r['parsed']['Status'] for r in g['privilege']],fences=[r['response']['response'].split('\t')[0] for r in g['fences']],rotation=[dict(expected=r['rotation'],wire=pawn(r['wire']['parsed']['Snapshot'])['Rotation'],native=ET.fromstring(r['client']['response']).find("pawn[@id='Human302']").get('rotation')) for r in g['rotation']],faults=[dict(kind=r['command']['CommandType'],fault=r['fault'],end=r['end'].split('response=')[0] if r['end'] else None,gap=r['maxFrameGapMs']) for r in commands]),indent=2))

