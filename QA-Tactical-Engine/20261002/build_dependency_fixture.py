import xml.etree.ElementTree as E,copy,json,pathlib
import independent_run as h
mod=h.ROOT/"RequiredDefFixtureMod"
(mod/"About").mkdir(parents=True,exist_ok=True);(mod/"Defs").mkdir(exist_ok=True)
(mod/"About/About.xml").write_text('''<?xml version="1.0" encoding="utf-8"?>
<ModMetaData><name>QA required-def fixture (scratch only)</name><author>Independent QA</author><packageId>qacodex.requireddef.fixture</packageId><supportedVersions><li>1.6</li></supportedVersions><description>Temporary scratch test dependency; not WarEconomy production.</description></ModMetaData>''',encoding="utf-8")
defs=E.parse(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\HediffDefs\BodyParts\Hediffs_BodyParts_Bionic.xml").getroot()
heart=next(x for x in defs if x.tag=="ThingDef" and x.findtext("defName")=="BionicHeart")
heart=copy.deepcopy(heart);heart.find("defName").text="QA_TestRequiredHeart";heart.find("label").text="QA required-def test item"
out=E.Element("Defs");out.append(heart);E.ElementTree(out).write(mod/"Defs/RequiredItem.xml",encoding="utf-8",xml_declaration=True)
r=E.parse(h.ORIGINAL).getroot()
things=r.find("game/maps")[0].find("things")
thing=next(x for x in things if x.findtext("def")=="BionicHeart")
thing.find("def").text="QA_TestRequiredHeart";thing.find("id").text="QA_TestRequiredHeart3233"
if r.find("meta/modIds") is not None:E.SubElement(r.find("meta/modIds"),"li").text="qacodex.requireddef.fixture"
if r.find("meta/modNames") is not None:E.SubElement(r.find("meta/modNames"),"li").text="QA required-def fixture (scratch only)"
E.ElementTree(r).write(h.ROOT/"RequiredDefInput.rws",encoding="utf-8",xml_declaration=True)
print("Prepared",mod)

