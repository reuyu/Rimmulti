from pathlib import Path
import json,re,collections,xml.etree.ElementTree as E
import setup as f
q=f.Q;data=q/'Evidence';r=json.loads((data/'results.json').read_text(encoding='utf-8'))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def pawn(c):return next(p for p in c['pawns'] if p['id']=='Human302')
def build(c,id):return next(x for x in c['buildings'] if x['id']==id)
def dim(c,k):
 p=pawn(c)
 if k=='01':return [x for x in c['containerHierarchy'] if x['containerId']=='Human302' and x['containerType']=='PawnInventory']
 if k=='02':return p['skills']['Shooting']
 if k=='03':return [x for x in p['hediffs'] if x['def']=='Stab']
 if k=='04':return [x for x in p['hediffs'] if x['def']=='BionicTongue']
 if k=='05':return next(x for x in c['animals'] if x['id']=='LabradorRetriever207367')
 if k=='06':return build(c,'TableSculpting990014')['bills']
 if k=='07':return next(x for x in c['zones'] if x['type']=='Zone_Growing')
 if k=='08':return [x for x in c['designations'] if x['def']=='Mine']
 if k=='09':return next(x for x in c['fires'] if x['id']=='Fire990010')
 if k=='10':return next(x for x in c['plants'] if x['id']=='Plant_Rice990011')
 if k=='11':return c['conditions']
 if k=='12':return {'ownedBed':p['assignedBed'],'bedOwners':build(c,'Bed990012')['assignedPawns']}
 if k=='13':return p['relations']
 if k=='14':return build(c,'Battery509102')['batteryStoredEnergy']
 if k=='15':return [x for x in c['containerHierarchy'] if x['containerId']=='MinifiedThing990030']
baseline=read(data/'clean-live.full-census.json');negative=[]
for i in range(1,16):
 k=f'{i:02}'
 if 'negative-'+k+'-gate' not in r:continue
 live=read(data/('negative-'+k+'-live.full-census.json'))
 negative.append({'case':k,'expected':dim(baseline,k),'injectedFacts':r['negative-'+k+'-input']['injected'],'live':dim(live,k),'comparator':r['negative-'+k+'-comparator'],'gate':r['negative-'+k+'-gate']})
f.write(data/'negative-independent-summary.json',negative)
provenance={str(p):{'sha':f.sha(p),'bytes':p.stat().st_size} for p in (q/'Frozen').rglob('*') if p.is_file()}
f.write(data/'frozen-artifacts.json',provenance)
warnings={}
for p in (q/'Profiles').glob('*/player.log'):
 text=p.read_text(encoding='utf-8',errors='replace');warnings[str(p)]=[{'line':i,'text':line} for i,line in enumerate(text.splitlines(),1) if re.search('Could not resolve|Could not load|Exception|duplicate|Error while|error while|could not save|jobGiver|had no .*Adding|precept was missing',line)]
f.write(data/'log-semantic-warnings.json',warnings)
summary={'negativeCount':len(negative),'negativeDetected':sum(not x['comparator']['isPass'] for x in negative),'negativeExportsBlocked':sum(not x['gate']['finalExists'] for x in negative),'selfBaseline':{k:v for k,v in r.items() if k.startswith('self-baseline-')},'nonTick':{k:{'ticks':v['mutation'],'comparatorPass':v['comparator']['isPass'],'finalExists':v['finalExists'],'export':v['export']} for k,v in r.items() if k.startswith('non-tick-')},'saveFaults':{k:v for k,v in r.items() if k.startswith('save-fault-')},'saveErrors':{k:v for k,v in r.items() if k.startswith('save-error-')},'sourceManifestComparator':r.get('source-manifest-comparator'),'complete':r.get('all-complete',False),'unhandled':r.get('unhandled'),'qaHarnessInterruptions':r.get('qa-harness-interruptions')}
f.write(data/'summary.json',summary)
summary['generationBoundaryRace']=r.get('generation-at-save-boundary')
summary['supplementComplete']=r.get('supplement-complete',False)
summary['invalidInitialGenerationInjection']='save-fault-generation used an incorrect QA int cast against a long field; its failure is not a generation-fence PASS. See generation-at-save-boundary for the corrected independently reproduced attack.'
summary['savedWrongFreshReload']=r.get('saved-wrong-fresh-reload')
f.write(data/'summary.json',summary)
pb=read(q/'production-before.json');pa=f.prod();cb=read(q/'candidate-before.json');ca=f.candidates();f.write(data/'final-integrity.json',{'candidateBefore':len(cb),'candidateAfter':len(ca),'candidateChanges':[p for p in set(cb)|set(ca) if cb.get(p)!=ca.get(p)],'productionBefore':len(pb),'productionAfter':len(pa),'productionChanges':[p for p in set(pb)|set(pa) if pb.get(p)!=pa.get(p)]})
f.write(q/'qa-harness-manifest.json',{str(p.relative_to(q)):{'sha':f.sha(p),'bytes':p.stat().st_size} for p in q.rglob('*') if p.is_file() and p.suffix in ['.cs','.csproj','.py','.dll','.exe'] and not any(x in p.parts for x in ['Frozen','Profiles','obj'])})
print(json.dumps({'negative':len(negative),'detected':summary['negativeDetected'],'blocked':summary['negativeExportsBlocked'],'selfBypass':len(summary['selfBaseline']),'nonTick':[(k,v['finalExists'],v['comparatorPass']) for k,v in summary['nonTick'].items()],'complete':summary['complete'],'unhandled':summary['unhandled']},ensure_ascii=False))
