from pathlib import Path
import json,hashlib,datetime,shutil
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);op=c['active_operation'];assert op['type']=='SOL_R23_IDENTIFIER_MAPPING_INDEPENDENT' and op['delivery_status']=='PREPARED_NOT_SENT' and not op['unknown_delivery']
initial=Path(op['baseline_path']);old=C/'MASTER_R22_QA_INDEPENDENT_PROTECTED_BASELINE_20261011.json';paths={f['path']:f for f in read(old)['files']}
for f in read(initial)['files']:
 if f['path'] in paths:assert f['sha256']==paths[f['path']]['sha256'] and f['bytes']==paths[f['path']]['bytes']
 paths[f['path']]=f
for f in paths.values():
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
assert len(paths)>11650 and len(read(old)['files'])==11639
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();new=C/'MASTER_R23_QA_INDEPENDENT_PROTECTED_BASELINE_RECONCILED_20261011.json';assert not new.exists()
write(new,{'at':at,'delivery_id':op['delivery_id'],'protected_unique_paths':len(paths),'prior_baseline':str(old),'prior_baseline_sha256':sha(old),'initial_unsent_preparation_baseline':str(initial),'initial_unsent_preparation_sha256':sha(initial),'files':list(paths.values()),'scope':'Additive fullR22baseline+R22terminalQA+newR23frozen;no oldQA or candidate original mutation/manifest normalization'})
wp=Path(op['wp_path']);draft=C/'MASTER_R23_QA_WP_INITIAL_UNSENT_BEFORE_BASELINE_RECONCILIATION_20261011.md';assert not draft.exists();shutil.copy2(wp,draft)
text=wp.read_text(encoding='utf8');needle='Protectedbaseline'+str(initial)+'SHA'+op['baseline_sha256']+'/11650actualMasterrehashed paths.';assert needle in text
wp.write_text(text.replace(needle,'Protectedbaseline'+str(new)+'SHA'+sha(new)+'/'+str(len(paths))+'actualMasterrehashed paths.'),encoding='utf8')
qualification=C/'MASTER_R23_UNSENT_QA_BASELINE_RECONCILIATION_20261011.json';write(qualification,{'at':at,'reason':'Generator retained R21baseline instead of lastR22;detectedbefore anymessage/send/QAexecution','initial_protected':11650,'full_prior_protected':11639,'new_additive_protected':len(paths),'new_baseline':str(new),'new_baseline_sha256':sha(new),'initial_baseline_preserved':str(initial),'initial_WP_preserved':str(draft),'initial_WP_sha256':sha(draft),'corrected_unsent_WP_path':str(wp),'corrected_unsent_WP_sha256':sha(wp),'delivery':'NOT_SENT','scope_change':False,'production_candidate_or_QA_original_mutation':0,'initial_generator_no_output_error':'Substring generation error wrote0;corrected matching before successfulpreparation'})
op.update(wp_sha256=sha(wp),baseline_path=str(new),baseline_sha256=sha(new),protected_unique_paths=len(paths),preparation_reconciliation=str(qualification));c['updated_at']=at;write(cp,c)
e={'at':at,'event_id':op['delivery_id']+'-UNSENT-PREPARATION-RECONCILED','type':'R23_QA_ADDITIVE_BASELINE_RECONCILIATION_BEFORE_ANY_DELIVERY','proof':str(qualification),'proof_sha256':sha(qualification),'WP_sha256':sha(wp),'baseline_paths':len(paths),'delivery':'NOT_SENT'}
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
print(json.dumps({'paths':len(paths),'WP':str(wp),'WPsha':sha(wp),'baseline':str(new),'baselineSHA':sha(new),'delivery_id':op['delivery_id'],'status':'CORRECTED_PREPARED_NOT_SENT'}))
