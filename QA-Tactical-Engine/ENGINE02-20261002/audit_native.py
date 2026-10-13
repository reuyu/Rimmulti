import json,pathlib,xml.etree.ElementTree as E,collections,re,statistics
R=pathlib.Path(__file__).resolve().parent
S=pathlib.Path(r'C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch')
def tree(p):return E.parse(p).getroot()
def text(e):return (e.text or '').strip()
def flatten(e,path=''):
 out={};counts=collections.Counter()
 if text(e):out[path]=text(e)
 for a,v in e.attrib.items():out[path+'@'+a]=v
 for c in e:
  counts[c.tag]+=1;k=c.tag+'['+str(counts[c.tag])+']';out.update(flatten(c,path+'/'+k))
 return out
def diffs(a,b):
 x,y=flatten(a),flatten(b);return [{'path':k,'before':x.get(k),'after':y.get(k)} for k in sorted(x.keys()|y.keys()) if x.get(k)!=y.get(k)]
def indexed(r):return {e.findtext('id'):e for e in r.iter() if e.find('id') is not None and e.find('def') is not None}
def native(p):
 r=tree(p);idx=indexed(r);nums=collections.defaultdict(list)
 for ident in idx:
  m=re.search(r'(\d+)$',ident or '')
  if m:nums[int(m[1])].append(ident)
 return r,idx,{k:v for k,v in nums.items() if len(v)>1}
out={}
fixtures={'Gemini':S/'OriginalSave/POC_TAC_ENGINE_02_MultiMap_Complex.rws','Baseline':R/'Scoped/Saves/Baseline.rws','After1000':R/'Scoped/Saves/Scoped1000.rws','Long':R/'Scoped/Saves/LongScoped.rws','Reload':R/'Fresh/Saves/ReloadBaseline.rws','ResumeOne':R/'Fresh/Saves/ResumeOne.rws','Resume1000':R/'Fresh/Saves/Resume1000.rws','MissingInput':R/'OmittedDependency.rws','MissingExport':R/'Omitted/Saves/AfterLoss.rws'}
all={}
for label,p in fixtures.items():
 if not p.exists():continue
 r,idx,dups=native(p);all[label]=(r,idx)
 out[label]={'ticks':r.findtext('game/tickManager/ticksGame'),'things_with_xml_id':len(idx),'duplicate_numeric_ids':dups,'missing_token_count':sum(e.findtext('def')=='QA_UndeclaredMissingToken' for e in idx.values()),'maps':[]}
 for m in r.find('game/maps'):
  things=list(m.find('things'));pawns=[e for e in things if e.get('Class')=='Pawn'];out[label]['maps'].append({'ID':m.findtext('uniqueID'),'pawn_count':len(pawns),'plant_xml_count':sum(e.get('Class')=='Plant' for e in things),'buildings':[e.findtext('id') for e in things if 'Building' in e.get('Class','')],'animal_masters':[(e.findtext('id'),e.findtext('playerSettings/master')) for e in pawns if e.findtext('playerSettings/master') not in [None,'null']],'bill_count':len(m.findall('.//billStack/bills/li'))})
 out[label]['important_entities']={k:flatten(v) for k,v in idx.items() if k in ['Human302','Human100302','Gun_Autopistol9001','Apparel_FlakVest9002','MedicineIndustrial9004','Bed9104','Battery9102','Boomrat3383','Corpse_Human3240','Human3237','Plant_Rice9108']}
for a,b in [('Gemini','Baseline'),('Baseline','After1000'),('Long','Reload'),('Reload','ResumeOne'),('Reload','Resume1000')]:
 if a not in all or b not in all:continue
 ar,ai=all[a];br,bi=all[b]
 out[a+'__'+b]={'entity_ids_lost':sorted(ai.keys()-bi.keys()),'entity_ids_added':sorted(bi.keys()-ai.keys()),'non_target_map_diffs':diffs(ar.find('game/maps')[1],br.find('game/maps')[1]),'world_diffs':diffs(ar.find('game/world'),br.find('game/world')),'game_component_diffs':diffs(ar.find('game/components'),br.find('game/components')) if ar.find('game/components') is not None and br.find('game/components') is not None else [],'important_entity_diffs':{k:diffs(ai[k],bi[k]) for k in ai.keys()&bi.keys() if k in ['Human302','Human100302','Gun_Autopistol9001','MedicineIndustrial9004','Bed9104','Battery9102','Boomrat3383','Corpse_Human3240','Human3237']}}
rr=json.loads((R/'results.json').read_text(encoding='utf-8'));samples=rr.get('realtime-samples',[])
if samples:
 lat=[s['ms'] for s in samples];f=samples[0];l=samples[-1]
 ticks=lambda s:int(re.search('TicksSim=(\d+)',s['state'])[1])
 out['realtime']={'samples':len(samples),'avg_ms':statistics.mean(lat),'max_ms':max(lat),'min_ms':min(lat),'p95_ms':sorted(lat)[int(len(lat)*.95)],'first_sim_ticks':ticks(f),'last_sim_ticks':ticks(l),'measured_tps':(ticks(l)-ticks(f))/(l['t']-f['t']),'sample_tick_increments':[(ticks(b)-ticks(a)) for a,b in zip(samples,samples[1:])]}
for p in R.glob('*/player.log'):
 lines=p.read_text(encoding='utf-8',errors='replace').splitlines();out[p.parent.name+'_log_errors']=[{'line':i+1,'message':l} for i,l in enumerate(lines) if re.search('Exception|Error|Could not resolve|Could not load|Could not find',l)]
(R/'native-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for k,v in out.items():
 if '__' in k:print(k,{n:len(x) if isinstance(x,(dict,list)) else x for n,x in v.items()})
 elif k=='realtime':print(k,v)
 elif k.endswith('log_errors'):print(k,len(v))
 else:print(k,'ticks',v['ticks'],'duplicates',len(v['duplicate_numeric_ids']),'missing_token',v['missing_token_count'],'maps',v['maps'])
