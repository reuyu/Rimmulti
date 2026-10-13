import pathlib,xml.etree.ElementTree as E,json,collections,re
root=pathlib.Path(__file__).resolve().parent
def canon(n):
    if n is None:return None
    return (n.tag,tuple(sorted(n.attrib.items())),(n.text or "").strip(),tuple(canon(c) for c in n))
def pawns(path):
    r=E.parse(path).getroot()
    out={}
    for m in r.find("game/maps"):
        out[m.findtext("uniqueID")]={t.findtext("id"):t for t in m.find("things") if t.get("Class")=="Pawn"}
    return out
a=pawns(root/"Independent1/Saves/IndependentExport.rws")["0"]
b=pawns(root/"Independent2/Saves/ReloadExport.rws")["0"]
human_ids=[i for i,t in a.items() if t.findtext("def")=="Human"]
fields=["def","id","map","pos","faction","healthTracker","health","needs","jobs","equipment","apparel","inventory","ownership","playerSettings"]
diffs={}
for i in human_ids:
    diffs[i]={f:{"before":E.tostring(a[i].find(f),encoding="unicode") if a[i].find(f) is not None else None,"after":E.tostring(b[i].find(f),encoding="unicode") if b[i].find(f) is not None else None} for f in fields if canon(a[i].find(f))!=canon(b[i].find(f))}
summary={"roundtrip":{"human_ids":human_ids,"human_field_diffs":{i:list(d) for i,d in diffs.items()},"xml_fields_reviewed":fields,"other_top_level_pawn_defs":dict(collections.Counter(t.findtext("def") for t in a.values() if t.findtext("def")!="Human"))}}
summary["roundtrip"]["pawn_xml_children"]=[n.tag for n in a[human_ids[0]]]
animal_before=[l for l in (root/"Independent1/after.txt").read_text(encoding="utf-8").splitlines() if l.startswith("Animal ID=")]
animal_after=[l for l in (root/"Independent2/reloaded.txt").read_text(encoding="utf-8").splitlines() if l.startswith("Animal ID=")]
summary["roundtrip"]["animal_dump_rows"]={"before":len(animal_before),"after":len(animal_after),"same_rows":sorted(animal_before)==sorted(animal_after),"scope":"47 rows in this fixture; Bridge caps at 50"}
def manufactured(path):
    r=E.parse(path)
    return {t.findtext("id"):{f:t.findtext(f) for f in ("id","def","pos","stackCount","health")} for t in r.find("game/maps")[0].find("things") if t.findtext("def") in {"Apparel_AdvancedHelmet","Apparel_FlakPants","Apparel_FlakVest","BionicHeart"}}
mi1=manufactured(root/"Independent1/Saves/IndependentExport.rws");mi2=manufactured(root/"Independent2/Saves/ReloadExport.rws")
summary["roundtrip"]["manufactured_item_native_xml"]={"before_count":len(mi1),"after_count":len(mi2),"same_reviewed_fields":mi1==mi2,"records":mi1}
summary["roundtrip"]["loose_item_dump_rows"]={"before":len([l for l in (root/"Independent1/after.txt").read_text(encoding="utf-8").splitlines() if l.startswith("Item ID=")]),"after":len([l for l in (root/"Independent2/reloaded.txt").read_text(encoding="utf-8").splitlines() if l.startswith("Item ID=")]),"complete_1206_natural_item_graph_verified":False}
for prefix in ("Independent1","MultiMapV2"):
    pass
pre=pawns(root/"MultiMapV2/Saves/Before.rws");post=pawns(root/"MultiMapV2/Saves/After.rws")
mapchanges={}
for mid,ps in pre.items():
    rows=[]
    for pid,p in ps.items():
        if p.findtext("def")!="Human":continue
        q=post[mid][pid]
        def food(n):return next((x.findtext("curLevel") for x in n.findall("needs/needs/li") if x.findtext("def")=="Food"),None)
        rows.append({"pawn_id":pid,"pos_before":p.findtext("pos"),"pos_after":q.findtext("pos"),"food_before":food(p),"food_after":food(q),"changed_needs":canon(p.find("needs"))!=canon(q.find("needs")),"changed_jobs":canon(p.find("jobs"))!=canon(q.find("jobs"))})
    mapchanges[mid]=rows
summary["multi_map_changes"]=mapchanges
pre_r=E.parse(root/"MultiMapV2/Saves/Before.rws").getroot();post_r=E.parse(root/"MultiMapV2/Saves/After.rws").getroot()
summary["world_objects_tickdelta_sample"]=[{"id":o.findtext("ID"),"before":o.findtext("tickDelta"),"after":next((x.findtext("tickDelta") for x in post_r.findall("game/world/worldObjects/worldObjects/li") if x.findtext("ID")==o.findtext("ID")),None)} for o in pre_r.findall("game/world/worldObjects/worldObjects/li")[:5]]
summary["world_changed_components"]=[n.tag for n in pre_r.find("game/world") if canon(n)!=canon(post_r.find("game/world/"+n.tag))]
summary["complete_graph_test"]="NOT TESTED; observed baseline is insufficient for required player buildings/bed/equipped weapon/inventory/assignments"
(root/"semantic-audit.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"human-field-diffs.json").write_text(json.dumps(diffs,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))

