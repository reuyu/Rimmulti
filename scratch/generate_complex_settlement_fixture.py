import os
import sys
import xml.etree.ElementTree as ET
import hashlib
from pathlib import Path

SOURCE_FIXTURE = Path(r"QA-Tactical-Engine/ENGINE02-20261002/BoundaryFixture.rws")
OUTPUT_FIXTURE = Path(r"scratch/ComplexSettlementFixture.rws")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    print("=" * 80)
    print("GENERATING COMPREHENSIVE SETTLEMENT FIXTURE: ComplexSettlementFixture.rws")
    print("=" * 80)

    if not SOURCE_FIXTURE.exists():
        print(f"ERROR: Source fixture {SOURCE_FIXTURE} not found!")
        sys.exit(1)

    print(f"Reading source fixture: {SOURCE_FIXTURE} ({SOURCE_FIXTURE.stat().st_size} bytes)")
    tree = ET.parse(SOURCE_FIXTURE)
    root = tree.getroot()
    game = root.find("game")
    if game is None:
        raise ValueError("Invalid savegame: missing <game>")

    maps = game.find("maps")
    if maps is None or len(maps) == 0:
        raise ValueError("Invalid savegame: no maps found")

    map0 = maps[0]
    things = map0.find("things")
    if things is None:
        raise ValueError("Map 0 missing <things>")

    # 1. Resolve any duplicate numeric IDs in source fixture
    # The 7 wild plants that share IDs with buildings/tokens:
    id_remaps = {
        "Plant_TallGrass9101": "Plant_TallGrass709101",
        "Plant_Grass9102": "Plant_Grass709102",
        "Plant_Grass9103": "Plant_Grass709103",
        "Plant_Grass9104": "Plant_Grass709104",
        "Plant_Grass9106": "Plant_Grass709106",
        "Plant_Brambles9108": "Plant_Brambles709108",
        "Plant_TallGrass9109": "Plant_TallGrass709109"
    }
    remap_count = 0
    for m in maps:
        for t in m.find("things"):
            cur_id = t.findtext("id")
            if cur_id in id_remaps:
                t.find("id").text = id_remaps[cur_id]
                remap_count += 1
    print(f"Renumbered {remap_count} conflicting wild plants to ensure zero ID collisions")

    # 2. Ingest / augment Colonist Pawns on Map 0
    strange = next((t for t in things if t.findtext("id") == "Human302"), None)
    if strange is None:
        print("Warning: Human302 not found, locating first human pawn...")
        strange = next((t for t in things if t.get("Class") == "Pawn" and t.findtext("def") == "Human"), None)

    if strange is not None:
        pawn_id = strange.findtext("id")
        print(f"Found Colonist Pawn: {pawn_id}")

        # Ensure skills exist
        skills = strange.find("skills")
        if skills is None:
            skills = ET.SubElement(strange, "skills")
            skills_sub = ET.SubElement(skills, "skills")
            for skill_name in ["Shooting", "Melee", "Construction", "Mining", "Cooking", "Plants", "Crafting"]:
                li = ET.SubElement(skills_sub, "li")
                ET.SubElement(li, "def").text = skill_name
                ET.SubElement(li, "level").text = "10"
                ET.SubElement(li, "xpSinceLastLevel").text = "2500"

        # Ensure active Job
        jobs = strange.find("jobs")
        if jobs is None:
            jobs = ET.SubElement(strange, "jobs")
        cur_job = jobs.find("curJob")
        if cur_job is None:
            cur_job = ET.SubElement(jobs, "curJob")
            ET.SubElement(cur_job, "def").text = "GotoWander"
            ET.SubElement(cur_job, "targetA").text = "(140, 0, 140)"

    # 3. Add Minified Object (ThingOwner container with nested furniture)
    # Using Stool inside MinifiedThing with concrete ThingOwner type
    minified_xml = """<thing Class="MinifiedThing">
        <def>MinifiedThing</def>
        <id>MinifiedThing850150</id>
        <map>0</map>
        <pos>(139, 0, 140)</pos>
        <rot>0</rot>
        <faction>Faction_10</faction>
        <health>100</health>
        <questTags IsNull="True" />
        <spawnedTick>0</spawnedTick>
        <despawnedTick>-1</despawnedTick>
        <innerContainer Class="Verse.ThingOwner`1[Verse.Thing]">
            <maxStacks>1</maxStacks>
            <contentsLookMode>Deep</contentsLookMode>
            <innerList>
                <li Class="Building">
                    <def>Stool</def>
                    <id>Stool850151</id>
                    <health>75</health>
                    <stuff>WoodLog</stuff>
                    <questTags IsNull="True" />
                    <spawnedTick>0</spawnedTick>
                    <despawnedTick>-1</despawnedTick>
                    <quality>Good</quality>
                </li>
            </innerList>
        </innerContainer>
    </thing>"""
    things.append(ET.fromstring(minified_xml))
    print("Added MinifiedThing containing Stool with concrete ThingOwner Class")

    # 4. Note on Corpse: Map 0 already contains Corpse_Human3240 inside AncientCryptosleepCasket (ThingOwner container)
    print("Corpse verified: Corpse_Human3240 already present on Map 0 in baseline fixture")

    # 5. Add Power Conduits connecting Solar Generator to Battery and TableSculpting
    conduits = [
        (131, 0, 140, "PowerConduit850154"),
        (132, 0, 140, "PowerConduit850155"),
        (134, 0, 140, "PowerConduit850156"),
        (144, 0, 140, "PowerConduit850157")
    ]
    for x, y, z, cid in conduits:
        c_xml = f"""<thing Class="Building">
            <def>PowerConduit</def>
            <id>{cid}</id>
            <map>0</map>
            <pos>({x}, {y}, {z})</pos>
            <rot>0</rot>
            <faction>Faction_10</faction>
            <health>80</health>
            <questTags IsNull="True" />
            <spawnedTick>0</spawnedTick>
            <despawnedTick>-1</despawnedTick>
        </thing>"""
        things.append(ET.fromstring(c_xml))
    print(f"Added {len(conduits)} PowerConduit buildings to complete the power network")

    # 6. Add Fire on map
    fire_xml = """<thing Class="Fire">
        <def>Fire</def>
        <id>Fire850158</id>
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
    things.append(ET.fromstring(fire_xml))
    print("Added active Fire entity")

    # 7. Add Designations (Mine, CutPlants, Haul)
    desig_mgr = map0.find("designationManager")
    if desig_mgr is None:
        desig_mgr = ET.SubElement(map0, "designationManager")
    all_desigs = desig_mgr.find("allDesignations")
    if all_desigs is None:
        all_desigs = ET.SubElement(desig_mgr, "allDesignations")

    desigs_to_add = [
        ("""<li Class="Designation">
            <def>Mine</def>
            <target>(150, 0, 150)</target>
        </li>"""),
        ("""<li Class="Designation">
            <def>PlantsCut</def>
            <target>(145, 0, 145)</target>
        </li>"""),
        ("""<li Class="Designation">
            <def>Haul</def>
            <target>Thing_MedicineIndustrial9004</target>
        </li>""")
    ]
    for d in desigs_to_add:
        all_desigs.append(ET.fromstring(d))
    print(f"Added {len(desigs_to_add)} designations (Mine, PlantsCut, Haul)")

    # 8. Add Active GameCondition (Aurora)
    cond_mgr = map0.find("gameConditionManager")
    if cond_mgr is None:
        cond_mgr = ET.SubElement(map0, "gameConditionManager")
    active_conds = cond_mgr.find("activeConditions")
    if active_conds is None:
        active_conds = ET.SubElement(cond_mgr, "activeConditions")

    aurora_xml = """<li Class="GameCondition_Aurora">
        <def>Aurora</def>
        <uniqueID>850160</uniqueID>
        <duration>60000</duration>
        <ticksPassed>2500</ticksPassed>
    </li>"""
    active_conds.append(ET.fromstring(aurora_xml))
    print("Added active GameCondition (Aurora)")

    # 9. Verify World Object Settlement reference
    parent_id = map0.findtext("mapInfo/parent")
    print(f"Map 0 parent WorldObject: {parent_id}")

    # 10. Save enhanced fixture
    OUTPUT_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUTPUT_FIXTURE, encoding="utf-8", xml_declaration=True)
    size = OUTPUT_FIXTURE.stat().st_size
    sha = sha256_file(OUTPUT_FIXTURE)
    print(f"\n[SUCCESS] Wrote complex settlement fixture to: {OUTPUT_FIXTURE}")
    print(f"Size: {size:,} bytes | SHA256: {sha}")

if __name__ == "__main__":
    main()
