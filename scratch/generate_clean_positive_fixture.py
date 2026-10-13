import os
import sys
import xml.etree.ElementTree as ET
import hashlib
import re
from pathlib import Path

SOURCE_FIXTURE = Path(r"QA-Tactical-Engine/REMOTE-HARDEN02-20261002/Worker/Saves/EngineComplexFixture.rws")
CLEAN_SOURCE = Path(r"scratch/CleanSettlementFixture.rws")
CLEAN_CONTEXT_B = Path(r"scratch/TargetSettlement_Clean_ContextB.rws")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    print("=" * 80)
    print("GENERATING PRISTINE SETTLEMENT FIXTURE WITH GUARANTEED UNIQUE INTEGER IDS")
    print("=" * 80)

    if not SOURCE_FIXTURE.exists():
        print(f"ERROR: {SOURCE_FIXTURE} not found!")
        sys.exit(1)

    tree = ET.parse(SOURCE_FIXTURE)
    root = tree.getroot()
    game = root.find("game")
    maps = game.find("maps")
    map0 = maps[0]
    things0 = map0.find("things")

    # 1. On Map 1 (if present), offset all integer suffixes by +1000000 to eliminate any cross-map duplicate ID errors
    if len(maps) > 1:
        map1 = maps[1]
        for elem in map1.iter("id"):
            if elem.text:
                m = re.search(r"\d+$", elem.text)
                if m:
                    prefix = elem.text[:m.start()]
                    num = int(m.group())
                    elem.text = f"{prefix}{num + 1000000}"
        for elem in map1.iter("loadID"):
            if elem.text:
                m = re.search(r"\d+$", elem.text)
                if m:
                    prefix = elem.text[:m.start()]
                    num = int(m.group())
                    elem.text = f"{prefix}{num + 1000000}"

    # 2. Configure Colonist Human302 ('Strange')
    strange = next((t for t in things0 if t.findtext("id") == "Human302"), None)
    if strange is not None:
        print("Configuring Colonist Human302 ('Strange')...")
        # Skills
        skills = strange.find("skills")
        if skills is None:
            skills = ET.SubElement(strange, "skills")
        skills_sub = skills.find("skills")
        if skills_sub is None:
            skills_sub = ET.SubElement(skills, "skills")
        skills_sub.clear()
        skill_data = [
            ("Shooting", 10, 2500),
            ("Melee", 8, 1200),
            ("Construction", 10, 3100),
            ("Mining", 6, 800),
            ("Cooking", 9, 1500),
            ("Plants", 11, 4000),
            ("Crafting", 12, 5500)
        ]
        for sname, slvl, sxp in skill_data:
            li = ET.SubElement(skills_sub, "li")
            ET.SubElement(li, "def").text = sname
            ET.SubElement(li, "level").text = str(slvl)
            ET.SubElement(li, "xpSinceLastLevel").text = str(sxp)

        # Hediffs: BionicTongue (sev 1.0) and Stab (sev 3.0) with unique loadIDs
        hediffs = strange.find("healthTracker/hediffSet/hediffs")
        if hediffs is None:
            ht = strange.find("healthTracker") or ET.SubElement(strange, "healthTracker")
            hs = ht.find("hediffSet") or ET.SubElement(ht, "hediffSet")
            hediffs = hs.find("hediffs") or ET.SubElement(hs, "hediffs")
        hediffs.clear()

        bt_xml = """<li Class="Hediff_AddedPart">
            <def>BionicTongue</def>
            <loadID>990001</loadID>
            <part>
                <body>Human</body>
                <index>43</index>
            </part>
            <severity>1.0</severity>
        </li>"""
        hediffs.append(ET.fromstring(bt_xml))

        stab_xml = """<li Class="Hediff_Injury">
            <def>Stab</def>
            <loadID>990002</loadID>
            <part>
                <body>Human</body>
                <index>0</index>
            </part>
            <severity>3.0</severity>
            <isPermanent>False</isPermanent>
        </li>"""
        hediffs.append(ET.fromstring(stab_xml))

        # Equipment: Autopistol ID 990003
        eq = strange.find("equipment")
        if eq is None:
            eq = ET.SubElement(strange, "equipment")
        eq_inner = eq.find("innerContainer/innerList") or eq.find("equipment/innerList")
        if eq_inner is None:
            eq.clear()
            eq_inner = ET.SubElement(ET.SubElement(eq, "primary"), "innerList")

        # Inventory: 5x Industrial Medicine ID 990005
        inv = strange.find("inventory")
        if inv is None:
            inv = ET.SubElement(strange, "inventory")
        inv_inner = inv.find("innerContainer/innerList")
        if inv_inner is None:
            inv_inner = ET.SubElement(ET.SubElement(inv, "innerContainer"), "innerList")
        inv_inner.clear()
        med_xml = """<li Class="Medicine">
            <def>MedicineIndustrial</def>
            <id>MedicineIndustrial990005</id>
            <health>100</health>
            <stackCount>5</stackCount>
        </li>"""
        inv_inner.append(ET.fromstring(med_xml))

        # Bed assignment: Bed990012
        own = strange.find("ownership")
        if own is None:
            own = ET.SubElement(strange, "ownership")
        bed = own.find("ownedBed")
        if bed is None:
            bed = ET.SubElement(own, "ownedBed")
        bed.text = "Thing_Bed990012"

        # External relationship: Spouse Human309 (in world pawns)
        soc = strange.find("social")
        if soc is None:
            soc = ET.SubElement(strange, "social")
        rels = soc.find("directRelations")
        if rels is None:
            rels = ET.SubElement(soc, "directRelations")
        rels.clear()
        rel_xml = """<li>
            <def>Spouse</def>
            <otherPawn>Thing_Human309</otherPawn>
            <startTicks>1000</startTicks>
        </li>"""
        rels.append(ET.fromstring(rel_xml))

    # 3. Configure LabradorRetriever207367 with master Strange and followDrafted=True
    lab = next((t for t in things0 if t.findtext("id") == "LabradorRetriever207367"), None)
    if lab is not None:
        print("Configuring animal LabradorRetriever207367 (Master=Strange, followDrafted=True)...")
        ps = lab.find("playerSettings")
        if ps is None:
            ps = ET.SubElement(lab, "playerSettings")
        master_elem = ps.find("master")
        if master_elem is None:
            master_elem = ET.SubElement(ps, "master")
        master_elem.text = "Thing_Human302"

        fd = ps.find("followDrafted")
        if fd is None:
            fd = ET.SubElement(ps, "followDrafted")
        fd.text = "True"

        ff = ps.find("followFieldwork")
        if ff is None:
            ff = ET.SubElement(ps, "followFieldwork")
        ff.text = "True"

    # 4. TableSculpting990014 with valid Bill_ProductionWithUft
    sculpt_table = next((t for t in things0 if "TableSculpting" in t.findtext("id", "")), None)
    if sculpt_table is not None:
        sculpt_table.find("id").text = "TableSculpting990014"
        print("Configuring valid Bill_ProductionWithUft on TableSculpting990014...")
        bs = sculpt_table.find("billStack")
        if bs is None:
            bs = ET.SubElement(sculpt_table, "billStack")
        bills = bs.find("bills")
        if bills is None:
            bills = ET.SubElement(bs, "bills")
        bills.clear()
        bill_xml = """<li Class="Bill_ProductionWithUft">
            <recipe>Make_SculptureSmall</recipe>
            <allowedSkillRange>0~20</allowedSkillRange>
            <pawnRestriction>null</pawnRestriction>
            <precept>null</precept>
            <xenogerm>null</xenogerm>
            <ingredientFilter>
                <disallowedSpecialFilters />
                <allowedDefs>
                    <li>WoodLog</li>
                    <li>Steel</li>
                    <li>Silver</li>
                    <li>Gold</li>
                    <li>BlocksGranite</li>
                    <li>BlocksSlate</li>
                    <li>BlocksLimestone</li>
                    <li>BlocksMarble</li>
                    <li>BlocksSandstone</li>
                </allowedDefs>
                <allowedHitPointsPercents>0~1</allowedHitPointsPercents>
                <allowedMentalBreakChance>0~1</allowedMentalBreakChance>
                <allowedQualityLevels>Awful~Legendary</allowedQualityLevels>
            </ingredientFilter>
            <repeatMode>RepeatCount</repeatMode>
            <repeatCount>1</repeatCount>
            <storeMode>BestStockpile</storeMode>
            <targetCount>10</targetCount>
            <unpauseWhenYouHave: 5</unpauseWhenYouHave>
            <storeGroup: null</storeGroup>
            <includeGroup: null</includeGroup>
            <boundUft: null</boundUft>
        </li>""".replace(": ", ">").replace(": null<", ">null<")
        bills.append(ET.fromstring(bill_xml))

    # 5. Bed990012 assigned to Human302
    bed_obj = next((t for t in things0 if "Bed" in t.findtext("id", "") and "Door" not in t.findtext("id", "")), None)
    if bed_obj is not None:
        bed_obj.find("id").text = "Bed990012"
        print("Configuring Bed990012 assignment to Human302...")
        assigned = bed_obj.find("assignedPawns")
        if assigned is None:
            assigned = ET.SubElement(bed_obj, "assignedPawns")
        assigned.clear()
        ET.SubElement(assigned, "li").text = "Thing_Human302"

    # 6. Zones: Zone_Stockpile and Zone_Growing
    zm = map0.find("zoneManager")
    if zm is None:
        zm = ET.SubElement(map0, "zoneManager")
    all_zones = zm.find("allZones")
    if all_zones is None:
        all_zones = ET.SubElement(zm, "allZones")

    growing_zone = next((z for z in all_zones.findall("li") if z.get("Class") == "Zone_Growing"), None)
    if growing_zone is None:
        print("Adding Zone_Growing (Plant_Rice)...")
        gz_xml = """<li Class="Zone_Growing">
            <ID>2</ID>
            <label>Growing zone 1</label>
            <baseLabel>Growing zone</baseLabel>
            <color>RGBA(0.250, 0.750, 0.250, 0.090)</color>
            <cells>
                <li>(139, 0, 145)</li>
                <li>(140, 0, 145)</li>
            </cells>
            <plantDefToGrow>Plant_Rice</plantDefToGrow>
        </li>"""
        all_zones.append(ET.fromstring(gz_xml))

    # 7. Designations: Mine, CutPlants, Haul
    dm = map0.find("designationManager")
    if dm is None:
        dm = ET.SubElement(map0, "designationManager")
    all_desigs = dm.find("allDesignations")
    if all_desigs is None:
        all_desigs = ET.SubElement(dm, "allDesignations")
    all_desigs.clear()
    desig_xmls = [
        """<li Class="Designation">
            <def>Mine</def>
            <target>(150, 0, 150)</target>
        </li>""",
        """<li Class="Designation">
            <def>CutPlant</def>
            <target>Thing_Plant_Rice990011</target>
        </li>""",
        """<li Class="Designation">
            <def>Haul</def>
            <target>Thing_MedicineIndustrial990005</target>
        </li>"""
    ]
    for dx in desig_xmls:
        all_desigs.append(ET.fromstring(dx))
    print(f"Added {len(desig_xmls)} clean designations (Mine, CutPlant, Haul)")

    # 8. Fire990010
    fire = next((t for t in things0 if t.findtext("def") == "Fire"), None)
    if fire is None:
        print("Adding Fire990010...")
        f_xml = """<thing Class="Fire">
            <def>Fire</def>
            <id>Fire990010</id>
            <map>0</map>
            <pos>(146, 0, 146)</pos>
            <rot>0</rot>
            <health>100</health>
            <questTags IsNull="True" />
            <spawnedTick>0</spawnedTick>
            <despawnedTick>-1</despawnedTick>
            <fireSize>0.45</fireSize>
            <ticksSinceSpawn>50</ticksSinceSpawn>
        </thing>"""
        things0.append(ET.fromstring(f_xml))
    else:
        fire.find("id").text = "Fire990010"
        fs = fire.find("fireSize")
        if fs is not None:
            fs.text = "0.45"

    # 9. Plant_Rice990011 with growth=0.85
    rice = next((t for t in things0 if t.findtext("def") == "Plant_Rice"), None)
    if rice is None:
        print("Adding Plant_Rice990011...")
        r_xml = """<thing Class="Plant">
            <def>Plant_Rice</def>
            <id>Plant_Rice990011</id>
            <map>0</map>
            <pos>(139, 0, 145)</pos>
            <rot>0</rot>
            <health>85</health>
            <questTags IsNull="True" />
            <spawnedTick>0</spawnedTick>
            <despawnedTick>-1</despawnedTick>
            <growthInt>0.85</growthInt>
            <ageInt>12000</ageInt>
        </thing>"""
        things0.append(ET.fromstring(r_xml))
    else:
        rice.find("id").text = "Plant_Rice990011"
        g = rice.find("growthInt")
        if g is not None:
            g.text = "0.85"

    # 10. Aurora GameCondition (duration 60000, uniqueID 850160)
    gcm = map0.find("gameConditionManager")
    if gcm is None:
        gcm = ET.SubElement(map0, "gameConditionManager")
    active_conds = gcm.find("activeConditions")
    if active_conds is None:
        active_conds = ET.SubElement(gcm, "activeConditions")
    active_conds.clear()
    aurora_xml = """<li Class="GameCondition_Aurora">
        <def>Aurora</def>
        <uniqueID>850160</uniqueID>
        <duration>60000</duration>
        <ticksPassed>2500</ticksPassed>
    </li>"""
    active_conds.append(ET.fromstring(aurora_xml))

    # 11. Battery509102 storedPower 600
    bat = next((t for t in things0 if t.findtext("id") == "Battery509102"), None)
    if bat is not None:
        sp = bat.find("storedPower")
        if sp is None:
            sp = ET.SubElement(bat, "storedPower")
        sp.text = "600"
        print("Configured Battery509102 storedPower=600")

    # 12. MinifiedThing990030 containing Stool990031
    mini = next((t for t in things0 if t.findtext("id") == "MinifiedThing990030"), None)
    if mini is None:
        mini_xml = """<thing Class="MinifiedThing">
            <def>MinifiedThing</def>
            <id>MinifiedThing990030</id>
            <map>0</map>
            <pos>(142, 0, 142)</pos>
            <rot>0</rot>
            <health>100</health>
            <stackCount>1</stackCount>
            <faction>Faction_10</faction>
            <questTags IsNull="True" />
            <spawnedTick>0</spawnedTick>
            <despawnedTick>-1</despawnedTick>
            <innerContainer Class="Verse.ThingOwner`1[Verse.Thing]">
                <innerList>
                    <li Class="Building">
                        <def>Stool</def>
                        <id>Stool990031</id>
                        <health>100</health>
                        <stackCount>1</stackCount>
                        <stuff>WoodLog</stuff>
                        <questTags IsNull="True" />
                        <quality>Good</quality>
                    </li>
                </innerList>
            </innerContainer>
        </thing>"""
        things0.append(ET.fromstring(mini_xml))
        print("Added MinifiedThing990030 with inner Stool990031")

    # 14. Write CleanSettlementFixture.rws
    CLEAN_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    tree.write(CLEAN_SOURCE, encoding="utf-8", xml_declaration=True)
    sha_src = sha256_file(CLEAN_SOURCE)
    print(f"\n[SUCCESS] Wrote clean source fixture: {CLEAN_SOURCE} ({CLEAN_SOURCE.stat().st_size:,} bytes, SHA256: {sha_src})")

    # 12. Prune to Context B
    tree_b = ET.parse(CLEAN_SOURCE)
    root_b = tree_b.getroot()
    game_b = root_b.find("game")
    maps_b = game_b.find("maps")
    parent_id = maps_b[0].findtext("mapInfo/parent").split("_")[-1]

    for m in list(maps_b)[1:]:
        maps_b.remove(m)

    w_objs = game_b.find("world/worldObjects/worldObjects")
    for obj in list(w_objs):
        if obj.findtext("ID") != parent_id:
            w_objs.remove(obj)

    CLEAN_CONTEXT_B.parent.mkdir(parents=True, exist_ok=True)
    tree_b.write(CLEAN_CONTEXT_B, encoding="utf-8", xml_declaration=True)
    sha_b = sha256_file(CLEAN_CONTEXT_B)
    print(f"[SUCCESS] Wrote clean Context B target fixture: {CLEAN_CONTEXT_B} ({CLEAN_CONTEXT_B.stat().st_size:,} bytes, SHA256: {sha_b})")

if __name__ == "__main__":
    main()
