from harness import *

def native(port=31801):
 r=observation(port)
 return dict(counters=r['xml'].attrib,pawns=[p.attrib for p in r['xml'].findall('.//pawn')],maps=[m.attrib for m in r['xml'].findall('mapState')])

if __name__=='__main__':
 result={}
 before=native();assert {m['id'] for m in before['maps']}=={'0','1'}
 write('view-other-map-stimulus.json',send(31801,'VIEW_MAP 1'))
 viewed_before=native();foreign_before=[p for p in viewed_before['pawns'] if p['map']=='1']
 rotations=[]
 for i in range(4):
  request=worker(cmd('SET_ROTATION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',Source='QA_TEST_CONTROL',TargetPawnId='Human302',CustomData=str(i)))
  time.sleep(.35);c=native();w=native(31800)
  cp=next(p for p in c['pawns'] if p['id']=='Human302');wp=next(p for p in w['pawns'] if p['id']=='Human302')
  rotations.append(dict(request=request,wire_rotation=pawn(request['parsed']['Snapshot'])['Rotation'],worker=wp,client=cp,viewed_map=c['counters']['map'],map1_unchanged=foreign_before==[p for p in c['pawns'] if p['map']=='1']))
 result['rotations_with_view_map1']=rotations
 write('map-bound-rotation-results.json',result);write('after-map-rotation-client.json',send(31801,'DUMP'))
 send(31801,'VIEW_MAP 0')
 # Small health regression is explicitly a local fault, not a candidate repair.
 send(31801,'SEVERITY Human302 Stab 4');time.sleep(.35);result['health_after_periodic']=native();send(31801,'SEVERITY Human302 Stab 3')
 attack=[]
 controls={'SET_PROGRESSION':dict(CustomData='0'),'SET_GENERATION':dict(Generation=1),'SET_ROTATION':dict(TargetPawnId='Human302',CustomData='North')}
 for kind,args in controls.items():
  attack.append(dict(vector='ordinary gameplay source',result=worker(cmd(kind,Source='REAL_GUI_GIZMO',**args))))
  attack.append(dict(vector='invalid token forged Source',result=worker(cmd(kind,Token='INVALID_TOKEN',Source='QA_TEST_CONTROL',**args))))
 attack.append(dict(vector='actual client gameplay transport + stale generation + wrong session + forged Source',result=rpc(cmd('SET_ROTATION',Token='Player_A_Token',Generation=999,TacticalSessionId='WRONG_SESSION',Source='QA_TEST_CONTROL',TargetPawnId='Human302',CustomData='East'))))
 attack.append(dict(vector='stale generation forged Source',result=worker(cmd('SET_PROGRESSION',Token='INVALID_TOKEN',Generation=999,Source='QA_TEST_CONTROL',CustomData='1'))))
 attack.append(dict(vector='wrong session forged Source',result=worker(cmd('SET_PROGRESSION',Token='INVALID_TOKEN',TacticalSessionId='WRONG_SESSION',Source='QA_TEST_CONTROL',CustomData='0'))))
 # Demonstrate generation mutation, then restore fixture generation via legitimate QA control.
 attack.append(dict(vector='invalid token mutates generation',result=worker(cmd('SET_GENERATION',Token='INVALID_TOKEN',Generation=777,Source='QA_TEST_CONTROL'))))
 result['after_forged_generation']=worker(cmd('STATUS'))
 result['restore_fixture_generation']=worker(cmd('SET_GENERATION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',Source='QA_TEST_CONTROL',Generation=1))
 attack.append(dict(vector='ordinary gameplay LOAD_SAVE',result=worker(cmd('LOAD_SAVE',Source='REAL_GUI_GIZMO',CustomData='EngineComplexFixture'))))
 # Perform real reload last: this is the existing QA fixture, no save publication.
 attack.append(dict(vector='invalid token forged Source LOAD_SAVE',result=worker(cmd('LOAD_SAVE',Token='INVALID_TOKEN',Generation=999,TacticalSessionId='WRONG_SESSION',Source='QA_TEST_CONTROL',CustomData='EngineComplexFixture'))))
 result['privileged_attacks']=attack
 write('map-rotation-security-results.json',result)
 print('Rotations:',[(x['worker']['rotation'],x['wire_rotation'],x['client']['rotation'],x['map1_unchanged']) for x in rotations])
 print('Security:',[(x['vector'],x['result']['command']['CommandType'],x['result']['parsed']['Status']) for x in attack])
