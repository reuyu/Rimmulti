import independent_run as h, time,json,xml.etree.ElementTree as E
h.results={"date":"2026-10-02","tests":{}}
def write():(h.ROOT/"dependency-results.json").write_text(json.dumps(h.results,ensure_ascii=False,indent=2),encoding="utf-8")
h.write=write
try:
    pp=h.prepare("DependencyPresent",h.ROOT/"RequiredDefInput.rws")
    config=pp/"Config/ModsConfig.xml"
    config.write_text(config.read_text(encoding="utf-8").replace("</activeMods>","<li>qacodex.requireddef.fixture</li></activeMods>"),encoding="utf-8")
    p,b=h.launch(pp,29224)
    h.record("present_load",h.load(b,"Input",pp))
    h.record("present_summary",h.command(b,"GET_ENTITY_SUMMARY",pp,"summary"))
    h.record("present_export",h.command(b,"EXPORT_SAVE RequiresCustomDef",pp,"export"))
    h.shutdown(p,b,pp)
    exported=pp/"Saves/RequiresCustomDef.rws"
    r=E.parse(exported)
    h.record("required_dependency_native",{"saved_modids":[x.text for x in r.findall("meta/modIds/li")],"custom_item_count":len([x for x in r.findall("game/maps/li/things/thing") if x.findtext("def")=="QA_TestRequiredHeart"])})
    pa=h.prepare("DependencyAbsent",exported,"RequiresCustomDef")
    p,b=h.launch(pa,29225)
    start=time.monotonic()
    response=b.send("LOAD_SAVE RequiresCustomDef")
    states=[]
    for _ in range(100):
        s=b.send("STATUS");states.append(s)
        if s.startswith("STATE: Playing"):break
        time.sleep(.25)
    (pa/"load.txt").write_text(response+"\n"+"\n".join(states),encoding="utf-8")
    h.record("absent_load",{"request":response,"last_status":s,"elapsed_ms":round((time.monotonic()-start)*1000,1)})
    if s.startswith("STATE: Playing"):
        h.record("absent_summary",h.command(b,"GET_ENTITY_SUMMARY",pa,"summary"))
        h.record("absent_export",h.command(b,"EXPORT_SAVE MissingDefResult",pa,"export"))
        r=E.parse(pa/"Saves/MissingDefResult.rws")
        h.record("missing_effect",{"custom_item_count":len([x for x in r.findall("game/maps/li/things/thing") if x.findtext("def")=="QA_TestRequiredHeart"]),"export_accepted":True})
    h.shutdown(p,b,pa)
except Exception as e:h.record("FATAL",{"error":repr(e)});raise
finally:
    for p in h.owned:
        if p.poll() is None:p.kill();p.wait(timeout=10)
    write()

