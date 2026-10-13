import independent_run as h
import xml.etree.ElementTree as E,copy,re,json,time
from collections import Counter
root=E.parse(h.ORIGINAL).getroot()
g=root.find("game");maps=g.find("maps");source=maps[0];clone=copy.deepcopy(source)
ids={n.text for n in clone.iter("id") if n.text and re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*\d+",n.text)}
remap={x:re.sub(r"\d+$",lambda m:str(int(m.group())+100000),x) for x in ids}
remap.update({"Thing_"+x:"Thing_"+v for x,v in list(remap.items())})
for lord in clone.findall("lordManager/lords/li"):
    lid=lord.find("loadID")
    if lid is None:lid=E.SubElement(lord,"loadID")
    lid.text="100001"
for n in clone.iter():
    if n.text:
        value=n.text.strip()
        if value in remap:n.text=remap[value]
    if n.tag=="map" and n.text=="0":n.text="1"
    if n.tag=="loadID" and n.text and n.text.isdigit():n.text=str(int(n.text)+100000)
clone.find("uniqueID").text="1"
clone.find("generatedId").text="29"
objects=g.find("world/worldObjects/worldObjects")
target_parent=next(o for o in objects if o.findtext("ID")=="0")
source_parent=next(o for o in objects if o.findtext("ID")=="91")
target_parent.find("faction").text=source_parent.findtext("faction")
clone.find("mapInfo/parent").text="WorldObject_0"
for n in clone.iter("ID"):
    if n.text and n.text.isdigit():n.text=str(int(n.text)+100000)
# Local area IDs are referenced by Area_<ID>; avoid cloned ID collisions.
for n in clone.iter():
    if n.text and re.fullmatch(r"Area_\d+",n.text.strip()):
        n.text=re.sub(r"\d+$",lambda m:str(int(m.group())+100000),n.text.strip())
maps.append(clone)
manager=g.find("uniqueIDsManager")
for n in manager:
    if n.text and n.text.isdigit():n.text=str(max(int(n.text),200000))
manager.find("nextMapID").text="2"
fixture=h.ROOT/"TwoMapFixtureV2.rws"
E.ElementTree(root).write(fixture,encoding="utf-8",xml_declaration=True)
(h.ROOT/"two-map-fixture-contract-v2.json").write_text(json.dumps({"source":str(h.ORIGINAL),"source_sha256":h.sha(h.ORIGINAL),"fixture":str(fixture),"fixture_sha256":h.sha(fixture),"purpose":"Scratch cloned actual map with remapped Thing IDs/references and Lord IDs and existing second Settlement parent; not a user canonical save","maps":2,"target_map_id":"0","non_target_map_id":"1","remapped_thing_ids":len(remap),"all_graph_semantics_proven":False},indent=2),encoding="utf-8")
h.results={"date":"2026-10-02","tests":{}}
def write():
    (h.ROOT/"multi-map-results-v2.json").write_text(json.dumps(h.results,ensure_ascii=False,indent=2),encoding="utf-8")
h.write=write
try:
    profile=h.prepare("MultiMapV2",fixture);p,b=h.launch(profile,29222)
    h.record("load",h.load(b,"Input",profile))
    h.record("maps",h.command(b,"GET_MAP_INFO",profile,"map-info"))
    h.record("before",h.command(b,"EXPORT_SAVE Before",profile,"before-export"))
    h.record("tick",h.command(b,"RUN_TICKS 1000",profile,"tick"))
    h.record("after",h.command(b,"EXPORT_SAVE After",profile,"after-export"))
    h.shutdown(p,b,profile)
except Exception as e:
    h.record("FATAL",{"error":repr(e)})
    raise
finally:
    for p in h.owned:
        if p.poll() is None:p.kill();p.wait(timeout=10)
    write()

