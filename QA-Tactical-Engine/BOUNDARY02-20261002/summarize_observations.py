from harness import *
import collections
p=ROOT/'ObservedBoundary'
ready=ET.parse(p/'ready.xml').getroot();after=ET.parse(p/'after2000.xml').getroot()
def scalars(e):return {x.get('name'):x.get('value') for x in e.findall('field')}
def blocks(r,tag,key='Type'):
    return {e.get(key):ET.tostring(e,encoding='unicode') for e in r.findall(tag)}
def changes(a,b):return {k:{'before':a.get(k),'after':b.get(k)} for k in sorted(a.keys()|b.keys()) if a.get(k)!=b.get(k)}
global_delta={tag:changes(blocks(ready,tag,'id' if tag in ['faction','worldObject'] else 'Type'),blocks(after,tag,'id' if tag in ['faction','worldObject'] else 'Type')) for tag in ['world','worldComponent','factionManager','faction','worldObject','history','tales','worldPawns','gameComponent']}
map_probes={m.get('index'):{c.get('Type'):scalars(c) for c in m.findall('mapComponent') if 'Probe' in c.get('Type','')} for m in after.findall('map')}
foreign_pawns=[]
for a in ready.find("map[@index='1']").findall('pawn'):
    b=after.find("map[@index='1']/pawn[@id='%s']"%a.get('id'))
    if b is not None and ET.tostring(a)!=ET.tostring(b):foreign_pawns.append({'id':a.get('id'),'before':a.attrib,'after':b.attrib})
caravan_before=ET.parse(p/'caravan-before.xml').getroot();caravan_after=ET.parse(p/'caravan-after.xml').getroot()
caravan_delta=changes(blocks(caravan_before,'worldObject','id'),blocks(caravan_after,'worldObject','id'))
plants=[{'map':m.get('index'),**c.attrib} for m in ready.findall('map') for c in m.findall('plant') if c.get('def')=='Plant_Rice']
bills=[{'map':m.get('index'),'building':b.get('id'),**bill.attrib} for m in ready.findall('map') for b in m.findall('building') for bill in b.findall('bill')]
caskets=[{'map':m.get('index'),**c.attrib} for m in ready.findall('map') for c in m.findall('building') if c.get('contained') and c.get('contained')!='null']
baseline=ET.parse(FIXTURE).getroot();things=[x for x in baseline.iter() if x.find('id') is not None and (x.tag=='thing' or x.get('Class') in ['Pawn','Corpse'])]
numeric=collections.defaultdict(list)
for t in things:
    value=t.findtext('id');match=re.search(r'(\d+)$',value or '')
    if match:numeric[match.group(1)].append(value)
duplicates={k:v for k,v in numeric.items() if len(v)>1}
verbids=[x.text for x in baseline.findall('.//verbs/li/loadID')]
hediffids=[x.findtext('loadID') for x in baseline.findall('.//hediffs/li')]
reloadp=ROOT/'ObservedFreshReload';reload=ET.parse(reloadp/'reload-live.xml').getroot();final=ET.parse(p/'final-live.xml').getroot()
finalmap={m.get('index'):ET.tostring(m,encoding='unicode') for m in final.findall('map')};reloadmap={m.get('index'):ET.tostring(m,encoding='unicode') for m in reload.findall('map')}
result={'ready':ready.attrib,'after2000':after.attrib,'global_changed_types':{k:list(v) for k,v in global_delta.items()},'global_deltas':global_delta,'map_probes_after2000':map_probes,'foreign_pawn_deltas':foreign_pawns,'caravan_delta':caravan_delta,'valid_rice_plants':plants,'bills':bills,'contained_entities':caskets,'duplicate_thing_numeric_ids':duplicates,'duplicate_verb_load_ids':{k:v for k,v in collections.Counter(verbids).items() if v>1},'duplicate_hediff_load_ids':{k:v for k,v in collections.Counter(hediffids).items() if v>1},'map_exact_match_fresh_reload':{k:finalmap[k]==reloadmap.get(k) for k in finalmap},'final_clock':final.attrib,'reload_clock':reload.attrib}
write_json(ROOT/'observation-summary.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['global_deltas','foreign_pawn_deltas','caravan_delta','contained_entities']},ensure_ascii=False,indent=2))
