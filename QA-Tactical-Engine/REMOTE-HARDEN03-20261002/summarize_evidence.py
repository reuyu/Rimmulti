from pathlib import Path
import json,re,statistics,hashlib,xml.etree.ElementTree as ET
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent
def read(name):return json.loads((Q/name).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest().upper()
events=(Q/'GraphicalClient/qa-events.tsv').read_text(encoding='utf-8-sig').splitlines()
wire=[]
for line in (Q/'GraphicalClient/qa-wire.tsv').read_text(encoding='utf-8-sig').splitlines():
 t,j=line.split('\t',1);wire.append(dict(utc=t,response=json.loads(j),bytes=len(j.encode())))
trace=[]
for row in wire:
 d=row['response'];s=d['Snapshot']
 if 548<=s['SnapshotSequence']<=578 and s['Pawns']:
  p=next(x for x in s['Pawns'] if x['PawnId']=='Human302');seq=s['SnapshotSequence']
  apply_index=next(i for i,x in enumerate(events) if f'APPLY_ENTER seq={seq} ' in x)
  exit_line=next(x for x in events[apply_index+1:] if 'APPLY_EXIT' in x)
  trace.append(dict(receive_utc=row['utc'],apply_utc=exit_line.split('\t')[0],sequence=seq,tick=s['AuthoritativeTick'],command_id=d['CommandId'],worker_position=[p['PosX'],p['PosZ']],worker_job=p['CurJobDef'],mirror_apply_evidence=exit_line,payload_bytes=row['bytes'],pawns=len(s['Pawns'])))
(Q/'operational-wire-trace.json').write_text(json.dumps(trace,indent=2),encoding='utf-8')
met=ET.fromstring(read('round2-real-move-metrics.json')['response'])
samples=[x.attrib for x in met if 548<int(x.get('seq'))<=578]
def stats(field):
 a=[float(x[field]) for x in samples];return dict(count=len(a),minimum=min(a),mean=statistics.mean(a),maximum=max(a))
gaps=[]
for line in (Q/'GraphicalClient/qa-frame-gaps.tsv').read_text(encoding='utf-8-sig').splitlines():
 t=line.split('\t')[0];gap=float(line.split('gapMs=')[1]);gaps.append(dict(utc=t,ms=gap))
delayproxy=read('periodic-proxy-wire.json');delay=next(x for x in delayproxy if x['kind']=='delay')
delaytime=datetime.fromtimestamp(delay['utc'],timezone.utc)
delaygaps=[g for g in gaps if abs((datetime.fromisoformat(g['utc'])-delaytime).total_seconds())<.8]
commands=[]
for x in wire:
 if not x['response']['CommandId'].startswith('AUTO_REP_'):
  commands.append(dict(utc=x['utc'],status=x['response']['Status'],bytes=x['bytes'],pawns=len(x['response']['Snapshot']['Pawns'])))
health=ET.fromstring(read('after-health-periodic-fault.json')['response']).find(".//pawn[@id='Human302']/hediff[@def='Stab']").attrib
loads={}
for role in ['Worker','GraphicalClient']:
 lines=(Q/role/'Player.log').read_text(encoding='utf-8',errors='replace').splitlines()
 needles=['Could not load Texture2D','MatFrom with null','Could not find class','Could not resolve','Could not load reference','Exception loading','could not be resolved','null spawn']
 loads[role]=[dict(line=i+1,text=x) for i,x in enumerate(lines) if any(n.lower() in x.lower() for n in needles)]
summary=dict(movement_trace_count=len(trace),automatic_after_move=sum(x['command_id'].startswith('AUTO_REP_') for x in trace),positions=sorted({tuple(x['worker_position']) for x in trace}),cadence_ms=stats('cadenceMs'),rtt_ms=stats('rttMs'),candidate_apply_ms=stats('applyMs'),periodic_bytes=stats('bytes'),command_responses=commands,delayed_frame_gaps=delaygaps,health_existing_stab_after_periodic=health,load_errors=loads)
(Q/'independent-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
frozen=[dict(path=x['path'],expected=x['expected'],actual=sha(x['path']),source=x['source']) for x in read('identity-before.json')]
protected=[dict(path=x['path'],expected=x['actual'],actual=sha(x['path'])) for x in read('production-before.json')]
for x in frozen+protected:x['match']=x['expected']==x['actual']
assert all(x['match'] for x in frozen+protected)
(Q/'integrity-after.json').write_text(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),frozen=frozen,production=protected),indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True)[:6200]);print('Identity:',len(frozen),'Production:',len(protected),'unchanged')
