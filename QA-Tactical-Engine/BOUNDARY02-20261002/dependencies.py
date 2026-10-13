from harness import *
def mutate(p,name,action):
    tree=ET.parse(FIXTURE);action(tree.getroot());tree.write(p/'Saves'/f'{name}.rws',encoding='utf-8',xml_declaration=True)
def missing_mod(r):ET.SubElement(r.find('meta/modIds'),'li').text='qa.boundary02.missing.mod'
def missing_thing(r):next(x for x in r.iter('def') if x.text=='Battery').text='QA_Boundary02_MissingThingDef'
def missing_hediff(r):next(x for x in r.findall('.//hediffs/li/def') if x.text=='Stab').text='QA_Boundary02_MissingHediffDef'
def missing_recipe(r):next(iter(r.findall('.//billStack/bills/li/recipe'))).text='QA_Boundary02_MissingRecipeDef'
def cross_registry(r):next(x for x in r.iter('def') if x.text=='Battery').text='Stab'
def invalid_part(r):
    h=next(x for x in r.findall('.//hediffs/li') if x.findtext('def')=='BionicEye')
    part=h.find('partIndex')
    if part is None:part=h.find('bodyPartIndex')
    if part is None:raise RuntimeError('Missing body part index in actual fixture: '+ET.tostring(h,encoding='unicode'))
    part.text='99999'
def wrong_version(r):r.find('meta/gameVersion').text='1.5.4104 rev435'
results={}
try:
    p=profile('DependencyDirectLoad');proc,b=launch(p,29603,30603)
    command(b,'GET_ENVIRONMENT_MANIFEST',p,'environment')
    valid=load(b,p);results['normal_valid']={'ready':valid['ready'],'export':command(b,'EXPORT_SAVE NormalValid',p,'normal-export')['response']}
    for name,action in [('MissingMod',missing_mod),('MissingThing',missing_thing),('MissingHediff',missing_hediff),('MissingRecipe',missing_recipe),('CrossRegistryThing',cross_registry),('InvalidBodyPart',invalid_part),('WrongVersion',wrong_version)]:
        try:
            mutate(p,name,action)
            # Intentionally never call VALIDATE_MANIFEST, exercising LOAD_SAVE itself.
            r=load(b,p,name);ex=command(b,'EXPORT_SAVE Export_'+name,p,name+'-export')['response']
            results[name]={'ready':r['ready'],'request':r['request'],'terminal':r['states'][-1]['status'],'export':ex,'export_exists':(p/'Saves'/('Export_'+name+'.rws')).exists()}
        except Exception as e:results[name]={'test_setup_or_runtime_error':repr(e)}
        write_json(ROOT/'dependency-results.json',results);print(name,results[name],flush=True)
    validagain=load(b,p);results['valid_after_negatives']={'ready':validagain['ready'],'terminal':validagain['states'][-1]['status']}
    stop(proc,b,p)
    dp=profile('DLCMismatch',omit_mod='ludeon.rimworld.royalty');dproc,db=launch(dp,29604,30604)
    command(db,'GET_ENVIRONMENT_MANIFEST',dp,'environment')
    dr=load(db,dp);results['dlc_config_missing_royalty']={'ready':dr['ready'],'request':dr['request'],'terminal':dr['states'][-1]['status'],'export':command(db,'EXPORT_SAVE DLCRejected',dp,'dlc-export')['response']}
    stop(dproc,db,dp)
    write_json(ROOT/'dependency-results.json',results)
finally:cleanup()
