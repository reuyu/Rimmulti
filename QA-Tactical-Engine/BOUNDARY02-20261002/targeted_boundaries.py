from harness import *
results={}
def read_queue(q,p,name):
    data=command(q,'NET_QUEUE',p,name);root=ET.fromstring(data['response']);return [x.attrib for x in root]
def blocked_request(b,q,p,duration,command_text,name,client_timeout=45):
    b.send('PAUSE_SIMULATION');before=parsed(b.send('STATUS'));marker=p/'observer-block-entered.txt'
    if marker.exists():marker.unlink()
    block_client=Bridge(31609,90);block_result={}
    def block():block_result['response']=block_client.send('BLOCKQUEUE '+str(duration))
    bt=threading.Thread(target=block);bt.start()
    while not marker.exists():time.sleep(.01)
    client=Bridge(29609,client_timeout);reply={}
    def send():
        t=time.monotonic()
        try:reply['response']=client.send(command_text)
        except Exception as e:reply['exception']=repr(e)
        finally:reply['ms']=(time.monotonic()-t)*1000;client.close()
    t=threading.Thread(target=send);t.start();queued=[];start=time.monotonic()
    while time.monotonic()-start<4:
        queued=read_queue(q,p,name+'-queued')
        if any(x['cmd']+' '+x['arg']==command_text for x in queued):break
        time.sleep(.05)
    t.join(timeout=50);bt.join(timeout=50);block_client.close()
    after=parsed(b.send('STATUS'));time.sleep(.4);late=parsed(b.send('STATUS'))
    return {'before':before,'queued_observed_while_blocked':queued,'reply':reply,'block_result':block_result,'after':after,'late':late,'G_delta':late['TicksGame']-before['TicksGame'],'L_delta':late['TicksSim']-before['TicksSim']}
try:
    p=profile('FreshSemanticNegatives',source=None,observer=True)
    shutil.copy2(ROOT/'DependencyDirectLoad/Saves/MissingRecipe.rws',p/'Saves/Input.rws')
    proc,b=launch(p,29609,30609,31609);q=Bridge(31609)
    first=load(b,p);export=command(b,'EXPORT_SAVE MissingRecipeExport',p,'missing-recipe-export')
    results['fresh_missing_recipe']={'ready':first['ready'],'terminal':first['states'][-1]['status'],'export':export,'original_bill_count':len(ET.parse(p/'Saves/Input.rws').getroot().findall('.//billStack/bills/li')),'exported_bill_count':len(ET.parse(p/'Saves/MissingRecipeExport.rws').getroot().findall('.//billStack/bills/li')) if (p/'Saves/MissingRecipeExport.rws').exists() else None}
    command(q,'SNAP',p,'missing-recipe-live')
    tree=ET.parse(FIXTURE);hediff=next(x for x in tree.getroot().findall('.//hediffs/li') if x.findtext('def')=='BionicEye');hediff.find('part/index').text='99999';tree.write(p/'Saves/InvalidPart.rws',encoding='utf-8',xml_declaration=True)
    part=load(b,p,'InvalidPart');part_export=command(b,'EXPORT_SAVE InvalidPartExport',p,'invalid-part-export')
    results['invalid_body_part']={'ready':part['ready'],'terminal':part['states'][-1]['status'],'export':part_export}
    write_json(ROOT/'targeted-boundary-results.json',results);print('fresh_recipe',results['fresh_missing_recipe'],flush=True);print('invalid_part',results['invalid_body_part'],flush=True)
    shutil.copy2(FIXTURE,p/'Saves/Valid.rws');valid=load(b,p,'Valid')
    if not valid['ready']:raise RuntimeError('Normal fixture did not recover READY')
    results['server_30s_timeout']=blocked_request(b,q,p,33000,'STEP_TICKS 777 1','server-timeout')
    print('server_timeout',results['server_30s_timeout'],flush=True)
    results['client_timeout_and_disconnect']=blocked_request(b,q,p,8000,'STEP_TICKS 79 1','client-timeout',5)
    # Accepted STEP may still be running after the 8s block. Allow bounded completion.
    while parsed(b.send('STATUS'))['RemainingStep']>0:time.sleep(.05)
    results['client_timeout_and_disconnect']['completed']=parsed(b.send('STATUS'))
    write_json(ROOT/'targeted-boundary-results.json',results);print('client_timeout',results['client_timeout_and_disconnect'],flush=True)
    command(q,'EVENTS',p,'lifecycle-events');q.close();stop(proc,b,p)
finally:cleanup()
