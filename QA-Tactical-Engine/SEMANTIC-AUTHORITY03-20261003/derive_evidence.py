import setup as f
import json,socket,hashlib
Q=f.Q;E=Q/'Evidence'
r=json.loads((E/'results.json').read_text(encoding='utf-8'))
base=json.loads((E/'baseline.full-census.json').read_text(encoding='utf-8'))
def item(c,key,id):return next(x for x in c[key] if x.get('id')==id)
def value(c,k):
 p=item(c,'pawns','Human302');a=item(c,'animals','LabradorRetriever207367')
 if k==1:return next(x['count'] for x in p['inventory'] if x['id']=='MedicineIndustrial990005')
 if k==2:return p['skills']['Shooting']
 if k==3:return next(x['severity'] for x in p['hediffs'] if x['def']=='Stab')
 if k==4:return any(x['def']=='BionicTongue' for x in p['hediffs'])
 if k==5:return [a['master'],a['followDrafted'],a['followFieldwork']]
 if k==6:return item(c,'buildings','TableSculpting990014')['bills'][0]['targetCount']
 if k==7:return next(x['cells'] for x in c['zones'] if x['id']==0)
 if k==8:return sorted(x['target'] for x in c['designations'] if x['def']=='Mine')
 if k==9:return item(c,'fires','Fire990010')['fireSize']
 if k==10:return item(c,'plants','Plant_Rice990011')['growth']
 if k==11:return next(x['duration'] for x in c['conditions'] if x['def']=='Aurora')
 if k==12:return p['assignedBed']
 if k==13:return next(x['relationDef'] for x in p['relations'] if x['otherPawnId']=='Human309')
 if k==14:return item(c,'buildings','Battery509102')['batteryStoredEnergy']
 if k==15:return next(x for x in c['containerHierarchy'] if x['containerId']=='MinifiedThing990030')['items'][0]['def']
neg=[]
for i in range(1,16):
 key=f'{i:02}';c=json.loads((E/f'negative-{key}-live.full-census.json').read_text(encoding='utf-8'));gate=r[f'negative-{key}-gate']
 neg.append({'case':key,'expectedLiveValue':value(base,i),'finalLiveValue':value(c,i),'injectedInputPath':str(E/f'{key}-wrong-input.rws'),'inputSha':f.sha(E/f'{key}-wrong-input.rws'),'admission':gate['validation'],'simulationReady':gate['state']['trustedSimulationReady'],'commands':gate['commands'],'finalExists':gate['finalExists'],'candidateSelfApproval':gate['self']})
f.write(E/'independent-negative-summary.json',neg)
b=json.loads((Q/'candidate-before.json').read_text(encoding='utf-8'));a=f.candidates();pb=json.loads((Q/'production-before.json').read_text(encoding='utf-8'));pa=f.prod()
changes=[x for x in set(b)|set(a) if b.get(x)!=a.get(x)];pc=[x for x in set(pb)|set(pa) if pb.get(x)!=pa.get(x)]
ports=[]
for index in [1,2,3,4,5,6,7]:
 for prefix in [34200,34300,34400]:
  port=prefix+index
  with socket.socket() as s:
   try:s.bind(('127.0.0.1',port));ports.append({'port':port,'released':True})
   except OSError as e:ports.append({'port':port,'released':False,'error':str(e)})
f.write(Q/'candidate-after.json',a);f.write(Q/'production-after.json',pa)
summary={'candidateFiles':len(b),'candidateChanges':changes,'productionFiles':len(pb),'productionChanges':pc,'observerRemoved':not (f.PROBE/'1.6/Assemblies'/f.OBSERVER).exists(),'ports':ports,'negativeRejected':sum(x['admission'].startswith('INPUT_REJECTED') and not x['simulationReady'] and not x['finalExists'] for x in neg),'sameTickBlocked':sum(r[k]['stage'].startswith('STAGE_BLOCKED') for k in r if k.startswith('same-tick-')),'fields':r['declared-field-summary'],'reservationFields':r['reservation-field-gates'],'windowsControl':json.loads((E/'windows-replace-control.json').read_text(encoding='utf-8-sig'))}
f.write(E/'final-integrity-summary.json',summary)
assert not changes and summary['observerRemoved']
print(json.dumps(summary,ensure_ascii=False)[:3500])
