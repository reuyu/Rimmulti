import run_engine02 as t
from run_engine02 import *
import copy
t.res=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
def make():
 r=ET.parse(FIX);root=r.getroot();maps=root.find('game/maps');a,b=maps
 replacements={x:x[:-4]+str(500000+int(x[-4:])) for x in ['Gun_Autopistol9001','Apparel_FlakVest9002','MedicineIndustrial9004','Bed9104','Door9103','TableSculpting9106','SolarGenerator9101','Battery9102','Plant_Rice9108','WarEconomy_TacticalProofToken9109']}
 for e in root.iter():
  if e.text:
   for old,new in replacements.items():e.text=e.text.replace(old,new)
 # Snapshot fixture repair only, not the developer bridge.
 for hd in root.findall('.//hediffs/li'):
  if hd.findtext('def')=='BionicTongue':ET.SubElement(hd,'loadID').text='500001'
 pawn=next(e for e in a.find('things') if e.findtext('id')=='Boomrat3383')
 settings=pawn.findall('playerSettings')
 for extra in settings[1:]:pawn.remove(extra)
 if not settings:settings=[ET.SubElement(pawn,'playerSettings')]
 master=settings[0].find('master')
 if master is None:master=ET.SubElement(settings[0],'master')
 master.text='Thing_Human302'
 for m in maps:
  for thing in m.find('things'):
   if thing.findtext('def')=='Battery':
    old=thing.find('storedEnergy')
    if old is not None:thing.remove(old)
    ET.SubElement(thing,'storedPower').text='600'
 for thing in list(a.find('things')):
  if thing.findtext('id') not in replacements.values():continue
  if thing.get('Class')=='Pawn':continue
  clone=copy.deepcopy(thing);idnode=clone.find('id');old=idnode.text;num=int(re.search(r'(\d+)$',old)[1]);idnode.text=old.replace(str(num),str(num+100000))
  if clone.find('map') is not None:clone.find('map').text='1'
  for e in clone.iter():
   if e.text:e.text=e.text.replace('Thing_Human302','Thing_Human100302')
  b.find('things').append(clone)
 for i,m in enumerate(maps):
  human=next(e for e in m.find('things') if e.findtext('id') in ['Human302','Human100302'])
  inv=human.find('inventory/innerContainer/innerList')
  if inv is None:
   n=human.find('inventory/innerContainer');inv=ET.SubElement(n,'innerList')
  inv.append(ET.fromstring(f'<li Class="ThingWithComps"><def>Meat_Muffalo</def><id>Meat_Muffalo{520001+i}</id><health>100</health><stackCount>5</stackCount><rotProgress>0</rotProgress><despawnedTick>-1</despawnedTick></li>'))
  m.find('things').append(ET.fromstring(f'<thing Class="Fire"><def>Fire</def><id>Fire{530001+i}</id><map>{i}</map><pos>(170, 0, 170)</pos><fireSize>0.5</fireSize><despawnedTick>-1</despawnedTick></thing>'))
  # Workbench recipe node exists for serialization, execution is not automatically forced.
  bench=next(e for e in m.find('things') if e.findtext('def')=='TableSculpting')
  bench.find('billStack/bills').append(ET.fromstring(f'<li Class="Bill_Production"><loadID>{540001+i}</loadID><recipe>Make_SculptureSmall</recipe><repeatMode>RepeatCount</repeatMode><repeatCount>1</repeatCount><targetCount>1</targetCount><storeMode>BestStockpile</storeMode></li>'))
 path=ROOT/'IndependentSymmetric.rws';r.write(path,encoding='utf-8',xml_declaration=True);return path
def main():
 p=profile('Symmetric',make());proc,b=launch(p,29344,30340);q=h.Bridge(30340,60);ready(b,p)
 cmd(q,'SNAP',p,'before');cmd(b,'EXPORT_SAVE Before',p,'export-before');steps(b,p,4000)
 cmd(q,'SNAP',p,'after');cmd(b,'GET_MAP_DETAILED_SUMMARY 0',p,'after-target');cmd(b,'GET_MAP_DETAILED_SUMMARY 1',p,'after-nontarget');cmd(b,'EXPORT_SAVE After',p,'export-after')
 # Warmed realtime cadence avoids charging previous export duration to START.
 time.sleep(.2);cmd(b,'START_SIMULATION 60',p,'warm-start');samples=[];start=time.monotonic()
 while time.monotonic()-start<3:
  now=time.monotonic();s=b.send('STATUS');samples.append({'t':now,'ms':(time.monotonic()-now)*1000,'state':s});time.sleep(.02)
 cmd(b,'PAUSE_SIMULATION',p,'warm-pause');log('warm-realtime-samples',samples)
 q.close();start=time.monotonic();stop(proc,b,p);log('shutdown-responsiveness-ms',(time.monotonic()-start)*1000)
try:main()
except Exception as ex:log('augmented-fatal',repr(ex));raise
finally:
 for proc in h.owned:
  if proc.poll() is None:proc.kill();proc.wait(timeout=10)
 log('augmented-owned-cleanup',{'pids':[p.pid for p in h.owned],'all_terminated':all(p.poll() is not None for p in h.owned)})
