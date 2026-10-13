from harness import *
def normalized(element):
    return {'tag':element.tag,'attributes':dict(sorted(element.attrib.items())),'text':(element.text or '').strip(),'children':sorted([normalized(x) for x in element],key=lambda x:json.dumps(x,sort_keys=True))}
def diff(a,b,path=''):
    out=[]
    for key in sorted(a.keys()|b.keys()):
        if a.get(key)!=b.get(key):out.append({'path':path+'/'+key,'before':a.get(key),'after':b.get(key)})
    return out
def map_units(root):
    result={}
    for m in root.findall('map'):
        for node in m:
            key=m.get('index')+'/'+node.tag+'/'+(node.get('id') or node.get('Type') or '?')
            result[key]=normalized(node)
    return result
bp=ROOT/'ValidatedBoundary';rp=ROOT/'ValidatedFreshReload'
before=ET.parse(bp/'observer-finalize-before.xml').getroot();after=ET.parse(bp/'observer-finalize-after.xml').getroot();ready=ET.parse(bp/'ready.xml').getroot()
final=ET.parse(bp/'final-live.xml').getroot();reload=ET.parse(rp/'reload-live.xml').getroot()
init_delta=diff(map_units(before),map_units(after),'FinalizeInit')
ready_delta=diff(map_units(after),map_units(ready),'AfterFinalizeToREADY')
reload_delta=diff(map_units(final),map_units(reload),'FreshReload')
root_delta={}
for name,a,b in [('FinalizeToReady',after,ready),('FreshReload',final,reload)]:
    root_delta[name]=diff({x.tag+'/'+(x.get('Type') or x.get('id') or '?'):normalized(x) for x in a if x.tag!='map'},{x.tag+'/'+(x.get('Type') or x.get('id') or '?'):normalized(x) for x in b if x.tag!='map'},name)
def compact(record):
    if record is None:return None
    if isinstance(record,list):return [compact(x) for x in record]
    if isinstance(record,dict):return {k:compact(v) for k,v in record.items()}
    return record
result={'finalize_before':before.attrib,'finalize_after':after.attrib,'ready':ready.attrib,'finalize_delta_count':len(init_delta),'ready_delta_count':len(ready_delta),'fresh_reload_map_delta_count':len(reload_delta),'finalize_deltas':init_delta,'ready_deltas':ready_delta,'reload_deltas':reload_delta,'root_deltas':root_delta}
def flat(e,path='',ignore_chrono=False):
    data={}
    for k,v in e.attrib.items():
        if ignore_chrono and k=='chronological':continue
        data[path+'/@'+k]=v
    if (e.text or '').strip():data[path+'/text']=e.text.strip()
    counters={}
    for child in e:
        key=child.tag+'['+(child.get('id') or child.get('Type') or child.get('name') or child.get('def') or '')+']'
        n=counters.get(key,0);counters[key]=n+1
        data.update(flat(child,path+'/'+key+('#'+str(n) if n else ''),ignore_chrono))
    return data
result['finalize_semantic_diff_excluding_unavailable_chrono']=diff(flat(before,ignore_chrono=True),flat(after,ignore_chrono=True),'init')
result['post_finalize_to_ready_semantic_diff']=diff(flat(after),flat(ready),'ready')
result['fresh_reload_semantic_diff']=diff(flat(final),flat(reload),'reload')
write_json(ROOT/'semantic-audit.json',result)
print(json.dumps({'finalize_before':before.attrib,'finalize_after':after.attrib,'ready':ready.attrib,'finalize_changed_units':[x['path'] for x in init_delta],'ready_changed_units':[x['path'] for x in ready_delta],'reload_changed_units':[x['path'] for x in reload_delta],'root_changed_units':{k:[x['path'] for x in v] for k,v in root_delta.items()}},ensure_ascii=False,indent=2))
