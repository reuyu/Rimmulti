import xml.etree.ElementTree as E,json,pathlib
p=pathlib.Path(r"C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch\OriginalSave\QA_Phase3_Baseline_20261001.rws")
r=E.parse(p).getroot()
g=r.find("game")
print("root",r.tag,"game",[(x.tag,len(x), (x.text or "")[:90]) for x in g][:45])
maps=g.find("maps")
m=maps[0]
print("map",[(x.tag,len(x),(x.text or "")[:80]) for x in m][:55])
w=g.find("world")
print("world",[(x.tag,len(x),(x.text or "")[:80]) for x in w])
print("map-info",E.tostring(m.find("mapInfo"),encoding="unicode"))
objs=w.find("worldObjects")
print("worldObjects",[(x.tag,len(x)) for x in objs])
print("firstwo",E.tostring(list(objs.iter("li"))[0],encoding="unicode")[:1800])
print("pawn", E.tostring(next(t for t in m.find("things") if t.get("Class")=="Pawn"),encoding="unicode")[:2600])
print("manager", E.tostring(g.find("uniqueIDsManager"),encoding="unicode"))

