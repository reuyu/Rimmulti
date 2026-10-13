import os
import sys
import json
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

WORKSPACE = Path(r"c:\Users\user\Desktop\RimMulti")
BASE_RWS = WORKSPACE / "scratch/TargetSettlement_Clean_ContextB.rws"
OUT_DIR = WORKSPACE / "scratch/CorruptedFixtures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def mutate(tag: str, root: ET.Element):
    game = root.find("game")
    m = game.find("maps/li")
    things = m.find("things")

    if tag == "01_held_item_stack":
        # MedicineIndustrial990005 in Strange's inventory
        for t in things:
            if t.findtext("id") == "Human302":
                for li in t.findall(".//inventory/innerContainer/innerList/li"):
                    if li.findtext("id") == "MedicineIndustrial990005":
                        li.find("stackCount").text = "4"
                        return

    elif tag == "02_pawn_skill":
        # Strange Shooting skill 10 -> 15
        for t in things:
            if t.findtext("id") == "Human302":
                for sk in t.findall("skills/skills/li"):
                    if sk.findtext("def") == "Shooting":
                        sk.find("level").text = "15"
                        return

    elif tag == "03_hediff_severity":
        # Strange Stab severity 3.0 -> 1.0
        for t in things:
            if t.findtext("id") == "Human302":
                for h in t.findall("healthTracker/hediffSet/hediffs/li"):
                    if h.findtext("def") == "Stab":
                        h.find("severity").text = "1.0"
                        return

    elif tag == "04_hediff_removal":
        # Remove BionicTongue
        for t in things:
            if t.findtext("id") == "Human302":
                hs = t.find("healthTracker/hediffSet/hediffs")
                for h in list(hs):
                    if h.findtext("def") == "BionicTongue":
                        hs.remove(h)
                        return

    elif tag == "05_animal_master_follow":
        # LabradorRetriever207367 master=null, followDrafted=False
        for t in things:
            if t.findtext("id") == "LabradorRetriever207367":
                ps = t.find("playerSettings")
                if ps is not None:
                    master = ps.find("master")
                    if master is not None: ps.remove(master)
                    fd = ps.find("followDrafted")
                    if fd is not None: fd.text = "False"
                    ff = ps.find("followFieldwork")
                    if ff is not None: ff.text = "False"
                return

    elif tag == "06_bill_change":
        # TableSculpting990014 bill targetCount 10 -> 25
        for t in things:
            if t.findtext("id") == "TableSculpting990014":
                bill = t.find("billStack/bills/li")
                if bill is not None:
                    tc = bill.find("targetCount")
                    if tc is not None: tc.text = "25"
                return

    elif tag == "07_zone_cell":
        # Growing zone cell moved (139, 0, 145) -> (139, 0, 146)
        for z in m.findall("zoneManager/allZones/li"):
            if z.findtext("label") == "Growing zone 1":
                for c in z.findall("cells/li"):
                    if c.text == "(139, 0, 145)":
                        c.text = "(139, 0, 146)"
                        return

    elif tag == "08_designation_change":
        # Mine designation moved (150, 0, 150) -> (150, 0, 151)
        for d in m.findall("designationManager/allDesignations/li"):
            if d.findtext("def") == "Mine":
                d.find("target").text = "(150, 0, 151)"
                return

    elif tag == "09_fire_size":
        # Fire990010 fireSize 0.45 -> 0.90
        for t in things:
            if t.findtext("id") == "Fire990010":
                t.find("fireSize").text = "0.90"
                return

    elif tag == "10_plant_growth":
        # Plant_Rice990011 growth 0.50 -> 0.25
        for t in things:
            if t.findtext("id") == "Plant_Rice990011":
                g = t.find("growth")
                if g is not None:
                    g.text = "0.25"
                else:
                    g2 = t.find("growthInt")
                    if g2 is not None: g2.text = "0.25"
                return

    elif tag == "11_condition_duration":
        # Aurora duration 60000 -> 12000
        for c in m.findall("gameConditionManager/activeConditions/li"):
            if c.findtext("def") == "Aurora":
                c.find("duration").text = "12000"
                return

    elif tag == "12_bed_assignment":
        # Clear Bed990012 assignedPawns and Strange ownedBed
        for t in things:
            if t.findtext("id") == "Bed990012":
                ap = t.find("assignedPawns")
                if ap is not None: ap.clear()
            if t.findtext("id") == "Human302":
                ob = t.find("ownership/ownedBed")
                if ob is not None: ob.text = "null"

    elif tag == "13_external_pawn_relation":
        # Strange spouse relation mutated to ExSpouse
        for t in things:
            if t.findtext("id") == "Human302":
                for r in t.findall("social/directRelations/li"):
                    if r.findtext("otherPawn") == "Thing_Human309":
                        r.find("def").text = "ExSpouse"
                        return

    elif tag == "14_power_scalar":
        # Battery509102 storedPower 600 -> 200
        for t in things:
            if t.findtext("id") == "Battery509102":
                sp = t.find("storedPower")
                if sp is not None: sp.text = "200"
                return

    elif tag == "15_nested_holder_content":
        # MinifiedThing990030 inner def Stool -> WoodLog
        for t in things:
            if t.findtext("id") == "MinifiedThing990030":
                inner = t.find("innerContainer/innerList/li")
                if inner is not None:
                    inner.find("def").text = "WoodLog"
                return

CORRUPTIONS = [
    ("01_held_item_stack", "MedicineIndustrial stack count mutated 5 -> 4"),
    ("02_pawn_skill", "Strange Shooting skill mutated 10 -> 15"),
    ("03_hediff_severity", "Strange Stab severity mutated 3.0 -> 1.0"),
    ("04_hediff_removal", "Strange BionicTongue removed"),
    ("05_animal_master_follow", "Labrador master cleared, followDrafted False"),
    ("06_bill_change", "Sculpting bill targetCount mutated 10 -> 25"),
    ("07_zone_cell", "Growing zone cell moved (139, 0, 145) -> (139, 0, 146)"),
    ("08_designation_change", "Mine designation moved (150, 0, 150) -> (150, 0, 151)"),
    ("09_fire_size", "Fire fireSize mutated 0.45 -> 0.90"),
    ("10_plant_growth", "Rice growth mutated 0.50 -> 0.25"),
    ("11_condition_duration", "Aurora duration mutated 60000 -> 12000"),
    ("12_bed_assignment", "Bed990012 assignment cleared"),
    ("13_external_pawn_relation", "Spouse relation mutated to ExSpouse"),
    ("14_power_scalar", "Battery509102 storedPower mutated 600 -> 200"),
    ("15_nested_holder_content", "MinifiedThing inner item def mutated Stool -> WoodLog")
]

def main():
    print(f"Reading base fixture XML: {BASE_RWS}")
    base_bytes = BASE_RWS.read_bytes()

    results = []
    saves_dir = Path(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"))

    for tag, desc in CORRUPTIONS:
        root = ET.fromstring(base_bytes)
        mutate(tag, root)
        out_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        out_path = OUT_DIR / f"Corrupted_{tag}.rws"
        out_path.write_bytes(out_bytes)
        sha = sha256_file(out_path)

        # Also copy to Saves dir
        save_copy = saves_dir / f"Corrupted_{tag}.rws"
        save_copy.write_bytes(out_bytes)

        print(f"[{tag}] {desc}")
        print(f"  Path: {out_path} ({len(out_bytes):,} bytes, SHA: {sha})")
        results.append({
            "tag": tag,
            "description": desc,
            "file": out_path.name,
            "bytes": len(out_bytes),
            "sha256": sha
        })

    summary_file = OUT_DIR / "corruption_battery_manifest.json"
    summary_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nManifest written to: {summary_file}")

if __name__ == "__main__":
    main()
