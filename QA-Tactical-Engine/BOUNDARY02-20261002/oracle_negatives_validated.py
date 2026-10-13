from harness import *
import ast, copy
tree=ast.parse((ROOT/'Reviewed/run_hardening_regressions.py').read_text(encoding='utf-8'))
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
names={'pawn_preserved','weapon_preserved','apparel_preserved','hediff_preserved','bed_preserved','animal_master_preserved','bills_preserved','battery_preserved','crop_preserved','casket_corpse_preserved','non_target_preserved','all_dimensions_pass'}
assignments=[x for x in main.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in x.targets)]
if len(assignments)!=12:raise RuntimeError('Frozen oracle AST does not match expected 11-dimension predicate')
oracle=compile(ast.fix_missing_locations(ast.Module(body=assignments,type_ignores=[])),str(ROOT/'Reviewed/run_hardening_regressions.py'),'exec')
def text(p):return json.loads(p.read_text(encoding='utf-8'))['response']
base={'snap_post_sim':text(ROOT/'ValidatedBoundary/map0-final.json'),'snap_reload_map0':text(ROOT/'ValidatedFreshReload/map0-reloaded.json'),'snap_map1_post':text(ROOT/'ValidatedBoundary/map1-final.json'),'snap_reload_map1':text(ROOT/'ValidatedFreshReload/map1-reloaded.json')}
def evaluate(context):
    ns={'re':re,**context};exec(oracle,ns)
    return {'all_dimensions_pass':ns['all_dimensions_pass'],'dimensions':{k:ns[k] for k in sorted(names-{'all_dimensions_pass'})}}
mutations={
 'pawn_identity':lambda s:re.sub(r'Pawn ID=Human\d+', 'Pawn ID=Human999999999',s),
 'weapon_kind':lambda s:s.replace('Weapon=Gun_Autopistol','Weapon=Gun_Revolver'),
 'apparel_kind':lambda s:s.replace('Apparel_FlakVest','Apparel_Parka'),
 'hediff_body_part':lambda s:s.replace('Stab[Torso]','Stab[Brain]').replace('BionicEye[Eye]','BionicEye[Torso]'),
 'bed_reference':lambda s:re.sub(r'Bed=Bed\d+','Bed=Bed999999999',s),
 'animal_master_reference':lambda s:re.sub(r'Master=(?!None|null)[^,]+','Master=IncorrectMaster',s),
 'bill_count':lambda s:s.replace('Bills=1','Bills=10'),
 'battery_storedPower':lambda s:re.sub(r'Battery\([^)]*\)','Battery(0/600)',s),
 'crop_growth':lambda s:re.sub(r'Growth=[\d.]+','Growth=0.0000',s),
 'corpse_identity':lambda s:re.sub(r'Corpse\([^)]*\)','Corpse(IncorrectPerson)',s),
 'foreign_state':lambda s:re.sub(r'Food=[\d.]+','Food=0.0000',s),
 'inventory_omitted_from_predicate':lambda s:re.sub(r'Inv=\[[^]]*\]','Inv=[]',s),
}
results={'oracle_source_hash':sha(SCRATCH/'run_hardening_regressions.py'),'baseline':evaluate(base),'negatives':{}}
for name,fn in mutations.items():
    ctx=copy.deepcopy(base);key='snap_reload_map1' if name=='foreign_state' else 'snap_reload_map0';ctx[key]=fn(ctx[key])
    (ROOT/('validated-oracle-negative-'+name+'.txt')).write_text(ctx[key],encoding='utf-8')
    results['negatives'][name]={'changed_oracle_input':ctx[key]!=base[key],'expected_final_pass':False,'actual':evaluate(ctx)}
write_json(ROOT/'validated-oracle-negative-results.json',results)
print(json.dumps({'baseline_pass':results['baseline']['all_dimensions_pass'],'false_negative_cases':[k for k,v in results['negatives'].items() if v['changed_oracle_input'] and v['actual']['all_dimensions_pass']],'ineffective_mutations':[k for k,v in results['negatives'].items() if not v['changed_oracle_input']]},ensure_ascii=False,indent=2))


