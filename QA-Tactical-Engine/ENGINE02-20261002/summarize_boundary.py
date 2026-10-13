import json, pathlib, statistics, re, xml.etree.ElementTree as E
R=pathlib.Path(__file__).resolve().parent
def idx(p):return {e.findtext('id'):e for e in E.parse(p).getroot().iter() if e.find('id') is not None}
out={}
for profile in ['Symmetric','CleanBoundary']:
 a=idx(R/profile/'Saves/Before.rws');b=idx(R/profile/'Saves/After.rws')
 out[profile]={}
 for ident in ['Human302','Human100302','Boomrat3383','Battery509102','Battery609102','Bed509104','Bed609104','Meat_Muffalo520001','Meat_Muffalo520002','Fire530001','Fire530002','Plant_Rice509108','Plant_Rice609108']:
  out[profile][ident]={}
  for k,d in [('before',a),('after',b)]:
   e=d.get(ident)
   out[profile][ident][k]=None if e is None else {'def':e.findtext('def'),'pos':e.findtext('pos'),'stack':e.findtext('stackCount'),'storedPower':e.findtext('storedPower'),'rotProg':e.findtext('rotProg'),'master':e.findtext('playerSettings/master'),'growth':e.findtext('growth'),'fireSize':e.findtext('fireSize')}
 if profile=='CleanBoundary':
  c=idx(R/profile/'Saves/Ecology.rws');changes=[]
  for ident in b.keys()&c.keys():
   if ident.startswith('Plant_') and b[ident].findtext('map')=='1':
    bv,cv=b[ident].findtext('age'),c[ident].findtext('age')
    if bv!=cv:changes.append({'id':ident,'age_before':bv,'age_after':cv})
  out['ecology_non_target_plant_age_changes']=changes
r=json.loads((R/'results.json').read_text(encoding='utf-8'));s=r['warm-realtime-samples'];l=[x['ms'] for x in s];ticks=lambda x:int(re.search(r'TicksSim=(\d+)',x['state'])[1]);out['warm_cadence']={'samples':len(s),'avg_ms':statistics.mean(l),'max_ms':max(l),'p95_ms':sorted(l)[int(len(l)*.95)],'tps':(ticks(s[-1])-ticks(s[0]))/(s[-1]['t']-s[0]['t']),'first':ticks(s[0]),'last':ticks(s[-1]),'poll_jitter_ms_max':max((b['t']-a['t'])*1000 for a,b in zip(s,s[1:]))}
(R/'boundary-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('warmed',out['warm_cadence']);print('ecology nonTarget plant changes',len(out['ecology_non_target_plant_age_changes']),out['ecology_non_target_plant_age_changes'][:3]);print(json.dumps(out['CleanBoundary'],indent=2))
