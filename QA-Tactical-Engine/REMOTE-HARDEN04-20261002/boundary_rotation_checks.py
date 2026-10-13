from harness import *
import copy
out=[]; before=worker(cmd('STATUS'))
controls={'LOAD_SAVE':{'CustomData':'EngineComplexFixture'},'SET_GENERATION':{'Generation':777},'SET_PROGRESSION':{'CustomData':'1'},'SET_ROTATION':{'TargetPawnId':'Human302','CustomData':'South'},'SIMULATE_DELAY':{'CustomData':'2000'}}
vectors=[('forged source / invalid token',{'Token':'INVALID_TOKEN','Source':'QA_TEST_CONTROL'}),('ordinary token',{'Source':'QA_TEST_CONTROL'}),('known privileged token',{'Token':'QA_CONTROL_SURFACE_KEY_PRIVILEGED','Source':'QA_TEST_CONTROL'}),('stale generation',{'Token':'INVALID_TOKEN','Generation':999,'Source':'QA_TEST_CONTROL'}),('wrong session',{'Token':'INVALID_TOKEN','TacticalSessionId':'WRONG_SESSION','Source':'QA_TEST_CONTROL'}),('alternate source field',{'CommandSource':'QA_TEST_CONTROL','source':'QA_TEST_CONTROL'}),('object source',{'Source':{'IsControlSurface':True}}),('claimed control channel',{'Source':'QA_TEST_CONTROL','IsControlSurface':True,'Token':'QA_CONTROL_SURFACE_KEY_PRIVILEGED'})]
for kind,args in controls.items():
 for label,extra in vectors:
  r=worker(cmd(kind,**{**args,**extra}));out.append(dict(vector=label,result=r));assert r['parsed']['Success'] is False,(kind,label)
 for spelling in [kind.lower(),' '+kind,kind+' ']:
  r=worker(cmd(spelling,**args,Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',Source='QA_TEST_CONTROL'));out.append(dict(vector='alternate command spelling',result=r));assert not r['parsed']['Success']
neg=[]
for kind,args in controls.items():
 for token in ['INVALID_TOKEN','Player_A_Token']:
  r=control(cmd(kind,**args,Token=token,Source='QA_TEST_CONTROL'));neg.append(r);assert r['parsed']['Status']=='PRIVILEGE_REJECTED'
write('privileged-boundary-results.json',dict(before=before,after=worker(cmd('STATUS')),gameplay=out,control_negative=neg,control_positive=control(cmd('SET_PROGRESSION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',CustomData='0',Source='UNTRUSTED_SOURCE'))))
# Bound map + rotation on automatic replication; never SendCommand as GUI evidence.
send(31801,'VIEW_MAP 1');a=observation();map1=[{k:v for k,v in p.attrib.items() if k not in ['screen','selected']} for p in a['xml'].findall("mapState[@id='1']/pawn")];rots=[]
for i in range(4):
 rr=control(cmd('SET_ROTATION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',TargetPawnId='Human302',CustomData=str(i)));time.sleep(.35);c=observation();w=observation(31800)
 rots.append(dict(wire=pawn(rr['parsed']['Snapshot'])['Rotation'],client=live_pawn(c).attrib,worker=live_pawn(w).attrib,viewed=c['xml'].attrib['map'],map1_unchanged=map1==[{k:v for k,v in p.attrib.items() if k not in ['screen','selected']} for p in c['xml'].findall("mapState[@id='1']/pawn")]))
send(31801,'VIEW_MAP 0');write('map-rotation-results.json',rots)
print('Gameplay rejected',len(out),'Control rejected',len(neg));print('Rotations',[(x['wire'],x['client']['rotation'],x['map1_unchanged']) for x in rots])
