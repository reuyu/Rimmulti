from harness import *
import collections,re,statistics,datetime
sys=__import__('sys');sys.stdout.reconfigure(encoding='utf-8')
def load(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def xml(n):return ET.fromstring(load(n)['response'])
def utc(s):return datetime.datetime.fromisoformat(s).timestamp()
phase=ROOT/'Phase1';events=(phase/'GraphicalClient'/'qa-events.tsv').read_text(encoding='utf-8-sig').splitlines();workerEvents=(phase/'Worker'/'qa-events.tsv').read_text(encoding='utf-8-sig').splitlines()
wires=[]
for line in (phase/'GraphicalClient'/'qa-wire.tsv').read_text(encoding='utf-8-sig').splitlines():
 try:
  fields=line.split('\t',3);wires.append(dict(utc=fields[0],thread=fields[1],response=json.loads(fields[3]),bytes=len(fields[3].encode())))
 except Exception:pass
wireSeq={v['response']['Snapshot']['SnapshotSequence']:v for v in wires if v['response'].get('Snapshot')}
workerSeq={int(re.search(r'seq=(\d+)',v)[1]):v for v in workerEvents if 'WORKER_POSE' in v}
matched=[]
for name in ['menu-east','west-turn','north','south','east']:
 for row in load(name+'-samples.json'):
  c=ET.fromstring(row['client']['response']);seq=int(c.get('seq'));w=wireSeq.get(seq)
  if not w:continue
  dto=pawn(w['response']['Snapshot']);p=c.find("pawn[@id='Human302']")
  if dto['CurJobDef']!='Goto':continue
  matched.append(dict(path=name,utc=c.get('utc'),sequence=seq,worker=workerSeq.get(seq),wire={k:dto[k] for k in ['PosX','PosZ','DrawPosX','DrawPosZ','Rotation','PoseSource','Drafted','CurJobDef']},client=dict(p.attrib)))
write('matched-movement-pose.json',matched)
metrics={}
for label,subset in [('periodic',[w for w in wires if w['response']['CommandId'].startswith('AUTO_REP')]),('draft',[w for w in wires if 'Drafted toggled' in w['response'].get('Message','')]),('move',[w for w in wires if 'to move to' in w['response'].get('Message','')]),('foreignReject',[w for w in wires if w['response'].get('Status')=='AUTH_REJECTED'])]:
 b=[w['bytes'] for w in subset];metrics[label]=dict(count=len(b),minimum=min(b) if b else None,maximum=max(b) if b else None,median=statistics.median(b) if b else None,pawnCounts=dict(collections.Counter(len(w['response'].get('Snapshot',{}).get('Pawns',[])) for w in subset)))
rx=[float(re.search(r'receiveToEnterMs=([0-9.]+)',l)[1]) for l in events if re.search(r'receiveToEnterMs=([0-9.]+)',l)]
apply=[float(re.search(r'applyMs=([0-9.]+)',l)[1]) for l in events if 'APPLY_EXIT' in l]
metrics['receiveToApplyEnter']=dict(median=statistics.median(rx),max=max(rx));metrics['applyExecution']=dict(median=statistics.median(apply),max=max(apply))
metrics['normalGuiCallbackMs']=[dict(line=l.split(' callbackMs=')[0],ms=float(re.search(r'callbackMs=([0-9.]+)',l)[1])) for l in events if 'ASYNC_EXIT' in l and 'ID=CMD_' in l]
write('independent-metrics.json',metrics)
faults=[]
for v in load('proxy-records.json'):
 id=v['command']['CommandId'];end=next((l for l in events if 'NETWORK_END ID='+id+' ' in l),None);begin=next((l for l in events if 'NETWORK_BEGIN ID='+id+' ' in l),None)
 if not begin:continue
 faults.append(dict(id=id,proxy=v.get('fault'),begin=begin,end=end.split(' response=')[0] if end else None,proxyForwardedUTC=v.get('forwardedUTC'),responseBytes=len(json.dumps(v['response'],separators=(',',':'),ensure_ascii=False).encode())))
write('phase1-command-faults.json',faults)
aim=[]
for v in load('aim-progress-samples.json'):
 dto=pawn(v['wire']['parsed']['Snapshot'])
 if dto['PoseSource']=='Aiming':
  w=ET.fromstring(v['worker']['response']).find("pawn[@id='Human302']");c=ET.fromstring(v['client']['response']).find("pawn[@id='Human302']")
  aim.append(dict(dto={k:dto[k] for k in ['PosX','PosZ','Rotation','PoseSource','FocusTargetX','FocusTargetZ','CurJobDef']},worker=dict(w.attrib),client=dict(c.attrib)))
write('actual-engine-focus.json',aim)
logAudit=[]
for role in ['Worker','GraphicalClient']:
 for name,folder in [('phase1',phase/role),('phase2',ROOT/role)]:
  text=(folder/'Player.log').read_text(encoding='utf-8-sig',errors='replace');d=dict(phase=name,role=role)
  for k,pat in {'unresolvedClass':'Could not find class','unresolvedDef':'Could not load reference to Verse','unresolvedCrossRef':'Could not resolve cross-reference','missingMethod':'MissingMethodException','harmonyFailure':'Harmony patch error','socketException':'SocketException','nullReference':'NullReferenceException','shaderUnsupported':'Shader.*not supported'}.items():d[k]=len(re.findall(pat,text))
  d['bindLines']=[s for s in text.splitlines() if 'SocketException' in s or 'listener error' in s or 'listening on port' in s or 'Bridge listening' in s];logAudit.append(d)
write('runtime-log-audit.json',logAudit)
stale=dict(before=dict(xml('old-epoch-new-session-before-release.json').attrib),after=dict(xml('old-epoch-stale-mutated-client.json').attrib),beforePawn=dict(xml('old-epoch-new-session-before-release.json').find("pawn[@id='Human302']").attrib),afterPawn=dict(xml('old-epoch-stale-mutated-client.json').find("pawn[@id='Human302']").attrib),currentWorker=pawn(load('old-epoch-worker-draft-off.json')['parsed']['Snapshot']))
write('epoch-race-summary.json',stale)
print(json.dumps(dict(payload=metrics,matchingMovementSamples=len(matched),focusSamples=len(aim),movingWithFocus=sum(a['worker']['pathMoving']=='true' for a in aim),logAudit=logAudit,epochRace=dict(beforeEpoch=stale['before']['epoch'],afterEpoch=stale['after']['epoch'],beforeDraft=stale['beforePawn']['drafted'],afterDraft=stale['afterPawn']['drafted'],workerDraft=stale['currentWorker']['Drafted'])),ensure_ascii=False,indent=2))
