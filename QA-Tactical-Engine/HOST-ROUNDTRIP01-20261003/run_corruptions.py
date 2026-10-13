import run_roundtrip as q
from pathlib import Path
import json,copy,xml.etree.ElementTree as E,re,shutil
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
TARGET=q.DATA/'A_TargetArtifact.rws'
baseline=json.loads((q.DATA/'B-before.snapshot.json').read_text(encoding='utf-8'))
census=json.loads((q.DATA/'B-before.census.json').read_text(encoding='utf-8'))
def node(root,id):return next(x for x in root.find('game/maps')[0].find('things') if x.findtext('id')==id)
def filter_census(c):
 c=copy.deepcopy(c)
 def env(id):return id.startswith('Filth') or any(re.fullmatch(re.escape(d)+r'\d+',id) for d in q.GEO)
 c['entityIdSet']=[id for id in c['entityIdSet'] if not env(id)]
 for name in ['defCounts','stackTotals']:
  c[name]={k:v for k,v in c[name].items() if k not in q.GEO and not k.startswith('Filth')}
 return c
def expected_value(root,name):
 m=root.find('game/maps')[0];p=node(root,'Human302');a=node(root,'Boomrat3383')
 if name=='stack':return node(root,'Human302').findtext('inventory/innerContainer/innerList/li/stackCount')
 if name=='skill':return p.findtext('skills/skills/li/level','0')
 if name=='health-severity':return p.findtext('healthTracker/hediffSet/hediffs/li/severity')
 if name=='hediff-removed':return len(p.findall('healthTracker/hediffSet/hediffs/li'))
 if name=='animal-follow':return a.findtext('playerSettings/followDrafted','False')
 if name=='bill-removed':return len(next(t for t in m.find('things') if t.findtext('def')=='TableSculpting').findall('billStack/bills/li'))
 if name=='zone-cell':return m.findtext('zoneManager/allZones/li/cells/li')
 if name=='fire-size':return node(root,'Fire850158').findtext('fireSize')
 if name=='bed-omission':return p.findtext('ownership/ownedBed')
 if name=='condition-duration':return m.findtext('gameConditionManager/activeConditions/li/duration')
def mutate(root,name):
 m=root.find('game/maps')[0];p=node(root,'Human302');a=node(root,'Boomrat3383')
 if name=='stack':p.find('inventory/innerContainer/innerList/li/stackCount').text='4'
 elif name=='skill':p.find('skills/skills/li/level').text='11'
 elif name=='health-severity':p.find('healthTracker/hediffSet/hediffs/li/severity').text='1'
 elif name=='hediff-removed':hs=p.find('healthTracker/hediffSet/hediffs');hs.remove(hs[0])
 elif name=='animal-follow':E.SubElement(a.find('playerSettings'),'followDrafted').text='True'
 elif name=='bill-removed':bs=next(t for t in m.find('things') if t.findtext('def')=='TableSculpting').find('billStack/bills');bs.remove(bs[0])
 elif name=='zone-cell':m.find('zoneManager/allZones/li/cells/li').text='(140, 0, 141)'
 elif name=='fire-size':node(root,'Fire850158').find('fireSize').text='0.9'
 elif name=='bed-omission':p.find('ownership/ownedBed').text='null'
 elif name=='condition-duration':m.find('gameConditionManager/activeConditions/li/duration').text='12000'
def targeted_live(s,name):
 m=s['maps'][0];p=m['entities']['Human302']['pawn'];a=m['entities']['Boomrat3383']['pawn']
 if name=='stack':return p['inventory'][0]['count']
 if name=='skill':return next(x['level'] for x in p['skills'] if x['def']=='Shooting')
 if name=='health-severity':return next(x['severity'] for x in p['hediffs'] if x['def']=='Stab')
 if name=='hediff-removed':return len(p['hediffs'])
 if name=='animal-follow':return a['followDrafted']
 if name=='bill-removed':return len(next(v for v in m['entities'].values() if v['def']=='TableSculpting')['bills'])
 if name=='zone-cell':return m['zones'][0]['cells']
 if name=='fire-size':return m['entities']['Fire850158']['fields'].get('fireSize')
 if name=='bed-omission':return p['ownedBed']
 if name=='condition-duration':return m['conditions'][0]['duration']
def main():
 assert not q.MOD.exists();shutil.copy2(q.Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll',q.MOD)
 try:
  for i,name in enumerate(['stack','skill','health-severity','hediff-removed','animal-follow','bill-removed','zone-cell','fire-size','bed-omission','condition-duration'],10):
   t=E.parse(TARGET);expected=expected_value(t.getroot(),name);mutate(t.getroot(),name);actual=expected_value(t.getroot(),name);path=q.DATA/('silent-'+name+'.rws');t.write(path,encoding='utf-8',xml_declaration=True)
   q.record('silent-'+name+'-input',{'sourceSha':q.sha(TARGET),'mutatedSha':q.sha(path),'expectedStatic':expected,'actualStatic':actual,'staticMismatch':expected!=actual,'baselineExistedBeforeMutation':(q.DATA/'A-baseline.snapshot.json').stat().st_mtime<path.stat().st_mtime})
   h=q.Host('Silent_'+name,path,i)
   if h.ready:
    s=h.snap('silent-'+name);c=h.census('silent-'+name);pair=q.DATA/('silent-'+name+'.pair.json');q.write(pair,{'expected':filter_census(census),'actual':filter_census(c)})
    cand=json.loads(h.o.send('COMPAREPAIR '+str(pair)));py=q.CensusOracle.compare(filter_census(census),filter_census(c));liveExpected=targeted_live(baseline,name);liveActual=targeted_live(s,name)
    # Observe candidate export AFTER QA determines failure. Never promote output into canonical storage.
    exported=h.export('Quarantined_'+name)
    q.record('silent-'+name+'-result',{'engineReady':True,'expectedLive':liveExpected,'actualLive':liveActual,'independentLiveMismatch':liveExpected!=liveActual,'candidateCSharpCompare':cand,'candidatePythonCompare':py,'candidateExportAllowed':exported.exists(),'quarantinedPath':str(exported),'observerErrors':s['errors']})
   else:q.record('silent-'+name+'-result',{'engineReady':False,'status':h.states[-1],'exportResponse':h.b.send('EXPORT_SAVE Rejected_'+name)})
   h.close()
 except Exception as ex:q.record('corruptions-unhandled',{'error':repr(ex)});raise
 finally:
  for h in q.OWNED:
   if h.p.poll() is None:
    try:h.close()
    except Exception:h.p.kill();h.p.wait()
  if q.MOD.exists() and q.sha(q.MOD)==q.sha(q.Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll'):q.MOD.unlink()
if __name__=='__main__':main()
