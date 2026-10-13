from harness import *
import re,statistics,collections,hashlib
r=ROOT;p=r.parents[1]/'WarEconomyMod';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
after={str(v.relative_to(p)):sha(v) for v in p.rglob('*') if v.is_file()};before=json.loads((r/'production-before.json').read_text(encoding='utf-8'));write('production-after.json',after)
ids=json.loads((r/'identity-before.json').read_text(encoding='utf-8'));identityAfter=[dict(v,after=sha(Path(v['path'])),unchanged=sha(Path(v['path']))==v['actual']) for v in ids];write('identity-after.json',identityAfter)
ev=(r/'Phase1'/'GraphicalClient'/'qa-events.tsv').read_text(encoding='utf-8').splitlines();wev=(r/'Phase1'/'Worker'/'qa-events.tsv').read_text(encoding='utf-8').splitlines()
batch=json.loads((r/'queue-stress-batches.json').read_text());counts=[re.search(r'admitted=(\d+) rejected=(\d+)',v['response']).groups() for v in batch]
drains=[v for v in ev if 'RESULT_DRAIN' in v and '2026-10-02T11:35:1' in v]
sliceLines=(r/'Phase1'/'Worker'/'qa-worker-slices.tsv').read_text(encoding='utf-8').splitlines();ticks=[int(re.search(r'ticks=(\d+)',v)[1]) for v in sliceLines];elapsed=[float(re.search(r'elapsedMs=([0-9.]+)',v)[1]) for v in sliceLines]
matched=json.loads((r/'matched-movement-pose.json').read_text(encoding='utf-8'));rotmap=dict(North=0,East=1,South=2,West=3);bad=[v for v in matched if int(v['client']['rotation'])!=rotmap[v['wire']['Rotation']]]
aim=json.loads((r/'actual-engine-focus.json').read_text(encoding='utf-8'));aimMoving=[v for v in aim if v['worker']['pathMoving']=='true'];write('moving-focus-examples.json',aimMoving)
final=ET.fromstring(json.loads((r/'phase1-final-client.json').read_text(encoding='utf-8'))['response'])
data=dict(productionFiles=len(after),productionChanged=[k for k in set(before)|set(after) if before.get(k)!=after.get(k)],frozenChanges=[v['path'] for v in identityAfter if not v['unchanged']],stress=dict(requests=1000,admitted=sum(int(v[0]) for v in counts),rejected=sum(int(v[1]) for v in counts),drainEvents=drains),slices=dict(count=len(ticks),ticks=sum(ticks),maxTicks=max(ticks),medianMs=statistics.median(elapsed),maxMs=max(elapsed),over8Ms=sum(v>8 for v in elapsed)),pose=dict(matched=len(matched),rotationMismatches=len(bad),movingWithFocus=len(aimMoving)),finalGrid=[dict(v.attrib) for v in final.findall('.//grid')],finalMapDuplicates=[dict(v.attrib) for v in final.findall('mapState')])
write('final-audit-summary.json',data);print(json.dumps({k:v for k,v in data.items() if k!='stress'},indent=2));print('stress',data['stress']['admitted'],data['stress']['rejected'])
