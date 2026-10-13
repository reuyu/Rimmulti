import run_roundtrip as q
import json,xml.etree.ElementTree as E,collections,re,hashlib
def count_refs(path):
 t=E.parse(path);g=t.getroot().find('game');m=g.find('maps')[0];rows=[]
 for node in m.find('things').iter():
  id=node.findtext('id');defn=node.findtext('def')
  if id and defn and re.search(r'\d+$',id):rows.append((id,defn))
 bynum=collections.defaultdict(list)
 for id,d in rows:bynum[re.search(r'\d+$',id).group()].append(id)
 return {'explicitDeepEntities':len(rows),'numericIdCollisions':{k:v for k,v in bynum.items() if len(v)>1},'designations':[(d.findtext('def'),d.findtext('target')) for d in m.findall('designationManager/allDesignations/li')],'zones':[(z.get('Class'),z.findtext('ID')) for z in m.findall('zoneManager/allZones/li')],'royalTitles':len(m.findall('.//royalty/titles/li')),'royalPermits':len(m.findall('.//royalty/permits/li')),'quests':len(g.findall('questManager/quests/li')),'precepts':len(g.findall('world/ideoManager/ideos/li/precepts/li')),'rootSections':[x.tag for x in g],'worldSections':[x.tag for x in g.find('world')]}
def main():
 r=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'));summary={}
 for k,v in r.items():
  if k.startswith('silent-') and k.endswith('-result'):summary[k]={a:v.get(a) for a in ['engineReady','expectedLive','actualLive','independentLiveMismatch','candidateExportAllowed']};summary[k]['CSharpPASS']=v.get('candidateCSharpCompare',{}).get('isPass');summary[k]['PythonPASS']=v.get('candidatePythonCompare',{}).get('isPass')
 q.write(q.DATA/'silent-summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
 for key in ['A-baseline','B-before','B-posttick','C-reloaded']:
  s=json.loads((q.DATA/(key+'.snapshot.json')).read_text(encoding='utf-8'));m=s['maps'][0]
  summary={'pid':s['pid'],'maps':len(s['maps']),'objects':len(s['worldObjects']),'factions':len(s['factions']),'worldPawns':len(s['worldPawns']),'ideologies':len(s['ideologies']),'quests':len(s['quests']),'custody':len(q.normalize(s)['custody']),'environment':collections.Counter(v['def'] for v in m['entities'].values() if v['category'] in ['Plant','Filth'] or v['def']=='Fire' or v['def'] in q.GEO),'gameComponents':s['gameComponents'],'worldComponents':s['worldComponents'],'mapComponents':m['mapComponents'],'observerErrors':s['errors'],'workerAssembly':next(a for a in s['assemblies'] if a['name']=='WarEconomy.WorkerBridge.PoC')}
  q.write(q.DATA/(key+'.summary.json'),summary);print(key,json.dumps(summary,ensure_ascii=False)[:1700])
 stat={'source':count_refs(q.Q/'Frozen/ComplexSettlementFixture.rws'),'nativeExport':count_refs(q.Q/'Profiles/A_Source/Saves/A_FullExport.rws'),'target':count_refs(q.DATA/'A_TargetArtifact.rws')};q.write(q.DATA/'source-static-crosscheck.json',stat);print('STATIC',json.dumps(stat,ensure_ascii=False)[:2800])
 # Do not silently excuse live-reference failures: preserve jobGiverKey diffs as unresolved; only nullable reflected fields/cache flags separated.
 for name in ['A-to-B','B-to-C']:
  diff=json.loads((q.DATA/(name+'.diff.json')).read_text(encoding='utf-8'));categories=collections.Counter(d['path'].split('.')[-1] for d in diff);print(name,categories)
if __name__=='__main__':main()
