import xml.etree.ElementTree as ET
from pathlib import Path
import copy

BASE_SAVE = Path(r"scratch/TargetSettlement_ContextB.rws")
OUT_DIR = Path(r"scratch/CorruptedFixtures")

def generate_corruptions():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print("GENERATING 6 DELIBERATE CORRUPTED FIXTURES FOR CENSUS ORACLE VALIDATION")
    print("=" * 80)

    # 1. Missing Held Item (remove MedicineIndustrial9004 from Strange's inventory)
    tree1 = ET.parse(BASE_SAVE)
    strange1 = tree1.find(".//thing[id='Human302']")
    inv_list1 = strange1.find("inventory/innerContainer/innerList")
    med = inv_list1.find("li[id='MedicineIndustrial9004']")
    if med is not None:
        inv_list1.remove(med)
    out1 = OUT_DIR / "Corrupt_1_MissingHeldItem.rws"
    tree1.write(out1, encoding="utf-8", xml_declaration=True)
    print(f"[1] Created {out1.name}: Removed MedicineIndustrial from Pawn inventory")

    # 2. Duplicate Entity Identity (Duplicate Gun_Autopistol9001 on map ground)
    tree2 = ET.parse(BASE_SAVE)
    map_things2 = tree2.find(".//maps/li[1]/things")
    dup_xml = """<thing Class="ThingWithComps">
        <def>Gun_Autopistol</def>
        <id>Gun_Autopistol9001</id>
        <map>0</map>
        <pos>(141, 0, 141)</pos>
        <rot>0</rot>
        <health>100</health>
        <questTags IsNull="True" />
        <spawnedTick>0</spawnedTick>
        <despawnedTick>-1</despawnedTick>
    </thing>"""
    map_things2.append(ET.fromstring(dup_xml))
    out2 = OUT_DIR / "Corrupt_2_DuplicateEntityId.rws"
    tree2.write(out2, encoding="utf-8", xml_declaration=True)
    print(f"[2] Created {out2.name}: Injected duplicate ThingID 'Gun_Autopistol9001'")

    # 3. Broken Container Relation (MinifiedThing innerContainer has corrupted pointer / invalid structure)
    tree3 = ET.parse(BASE_SAVE)
    minified3 = tree3.find(".//thing[id='MinifiedThing850150']")
    inner_list3 = minified3.find("innerContainer/innerList")
    if inner_list3 is not None:
        inner_list3.clear() # Container is present but inner object missing/null
    out3 = OUT_DIR / "Corrupt_3_BrokenContainer.rws"
    tree3.write(out3, encoding="utf-8", xml_declaration=True)
    print(f"[3] Created {out3.name}: Emptied innerContainer of MinifiedThing850150 (dropped held object)")

    # 4. Missing Def (Change TableSculpting to NonExistent_ArchotechPlasmaBench)
    tree4 = ET.parse(BASE_SAVE)
    bench4 = tree4.find(".//thing[id='TableSculpting9106']")
    if bench4 is not None:
        bench4.find("def").text = "NonExistent_ArchotechPlasmaBench"
    out4 = OUT_DIR / "Corrupt_4_MissingDef.rws"
    tree4.write(out4, encoding="utf-8", xml_declaration=True)
    print(f"[4] Created {out4.name}: Replaced Def with 'NonExistent_ArchotechPlasmaBench'")

    # 5. Assignment / Reference Corruption (Strange's ownedBed points to non-existent Bed9999)
    tree5 = ET.parse(BASE_SAVE)
    strange5 = tree5.find(".//thing[id='Human302']")
    owned_bed5 = strange5.find("ownership/ownedBed")
    if owned_bed5 is not None:
        owned_bed5.text = "Thing_Bed9999"
    out5 = OUT_DIR / "Corrupt_5_CorruptedAssignment.rws"
    tree5.write(out5, encoding="utf-8", xml_declaration=True)
    print(f"[5] Created {out5.name}: Corrupted Strange's ownedBed -> 'Thing_Bed9999'")

    # 6. Selected Global-State Dependency Omission (Remove Faction_10 from world/factionManager)
    tree6 = ET.parse(BASE_SAVE)
    factions6 = tree6.find(".//world/factionManager/allFactions")
    if factions6 is not None:
        for f in list(factions6):
            if f.findtext("loadID") == "10" or f.findtext("def") == "PlayerColony":
                factions6.remove(f)
                break
    out6 = OUT_DIR / "Corrupt_6_OmittedGlobalState.rws"
    tree6.write(out6, encoding="utf-8", xml_declaration=True)
    print(f"[6] Created {out6.name}: Omitted player faction Faction_10 from world/factionManager")

    print("\nAll 6 deliberate corruption test cases generated successfully.")

if __name__ == "__main__":
    generate_corruptions()
