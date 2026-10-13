from pathlib import Path
import json,xml.etree.ElementTree as E,collections
import setup as f
Q=f.Q;D=Q/'Evidence';r=json.loads((D/'results.json').read_text(encoding='utf-8'))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def norm(v):
 if isinstance(v,dict):return {k:norm(x) for k,x in v.items() if k!='generatedAt'}
 if isinstance(v,list):return sorted([norm(x) for x in v],key=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False))
 return v
def diff(a,b,p='$',out=None):
 if out is None:out=[]
 if type(a)!=type(b):out.append({'path':p,'expected':a,'actual':b})
 elif isinstance(a,dict):
  for k in set(a)|set(b):
   if k not in a or k not in b:out.append({'path':p+'.'+k,'expected':a.get(k),'actual':b.get(k)})
   else:diff(a[k],b[k],p+'.'+k,out)
 elif isinstance(a,list):
  if len(a)!=len(b):out.append({'path':p+'.length','expected':len(a),'actual':len(b)})
  for i,(x,y) in enumerate(zip(a,b)):diff(x,y,p+f'[{i}]',out)
 elif a!=b:out.append({'path':p,'expected':a,'actual':b})
 return out
ac=read(D/'fresh-A.full-census.json');bb=read(D/'fresh-B-before.full-census.json');bp=read(D/'fresh-B-post.full-census.json');cc=read(D/'fresh-C.full-census.json')
f.write(D/'all-declared-fields-A-B.diff.json',diff(norm(ac),norm(bb)))
f.write(D/'all-declared-fields-B-C.diff.json',diff(norm(bp),norm(cc)))
jobs={}
for name in ['fresh-A','fresh-B-before','fresh-B-post','fresh-C']:
 s=read(D/(name+'.snapshot.json'));p=s['maps'][0]['entities']['Human302'];jobs[name]={'ticks':s['ticksGame'],'position':p['pos'],'job':p['pawn']['job'],'bio':p['pawn']['bio'],'chrono':p['pawn']['chrono'],'reservations':s['maps'][0]['reservations']}
f.write(D/'fresh-jobs-and-progress.json',jobs)
clock={}
for name in ['two-map-before','two-map-after20']:
 s=read(D/(name+'.snapshot.json'));clock[name]={'ticks':s['ticksGame'],'maps':[{'id':m['mapId'],'pawns':[{'id':v['id'],'pos':v['pos'],'bio':v['pawn']['bio'],'chrono':v['pawn']['chrono']} for v in m['entities'].values() if v['def']=='Human']} for m in s['maps']]}
f.write(D/'GQ1-regression-only.json',clock)
bad=Q/'Profiles/IndependentGateR3/Saves/SavedBytes_broken-tail.rws'
try:E.parse(bad);parse='unexpected wellformed'
except E.ParseError as e:parse=str(e)
f.write(D/'truncated-approved-xml-validation.json',{'path':str(bad),'sha':f.sha(bad),'parseError':parse})
claimed=json.loads((Q/'Frozen/semantic_gate_02_results.json').read_text(encoding='utf-8'))
f.write(D/'developer-evidence-observations.json',{'reportVsFrozenScriptHashes':{n:f.sha(Q/'Frozen'/n) for n in ['census_oracle.py','run_semantic_gate_02.py','semantic_gate_02_results.json']},'declaredAtoBFieldDifferences':len(diff(norm(ac),norm(bb))),'declaredBtoCFieldDifferences':len(diff(norm(bp),norm(cc))), 'candidateSourceFixtureRoot':len(E.parse(Q/'Frozen/CleanSettlementFixture.rws').getroot().find('game/maps')),'candidateContextRoot':len(E.parse(Q/'Frozen/TargetSettlement_Clean_ContextB.rws').getroot().find('game/maps'))})
print(json.dumps({'declaredAtoBDiffs':len(diff(norm(ac),norm(bb))),'declaredBtoCDiffs':len(diff(norm(bp),norm(cc))),'jobPositions':{k:v['position'] for k,v in jobs.items()},'badXMLParse':parse,'supplement':r.get('supplement-complete')},ensure_ascii=False))
