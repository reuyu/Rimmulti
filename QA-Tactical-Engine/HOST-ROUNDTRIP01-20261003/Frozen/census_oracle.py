import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple

class CensusOracle:
    @staticmethod
    def extract_from_xml(xml_path: Path, map_index: int = 0) -> Dict[str, Any]:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        game = root.find("game")
        if game is None:
            raise ValueError("Save file missing <game>")

        maps = game.find("maps")
        if maps is None or len(maps) <= map_index:
            raise ValueError(f"Save file does not have map at index {map_index}")

        m = maps[map_index]
        map_unique_id = m.findtext("uniqueID", str(map_index))
        map_parent = m.findtext("mapInfo/parent", "Unknown")
        player_faction = game.findtext("factionManager/allFactions/li[def='PlayerColony']/loadID", "Faction_10")
        ticks_game = int(game.findtext("tickManager/ticksGame", "0"))

        things = m.find("things")
        if things is None:
            things = []

        entity_ids = []
        def_counts = {}
        class_counts = {}
        stack_totals = {}
        container_hierarchy = []
        pawns = []
        animals = []
        buildings = []
        zones = []
        designations = []
        conditions = []
        referenced_defs = set()
        referenced_factions = set()
        referenced_world_objects = {map_parent}

        for t in things:
            tid = t.findtext("id")
            if not tid:
                continue
            entity_ids.append(tid)

            tdef = t.findtext("def", "Unknown")
            referenced_defs.add(tdef)
            def_counts[tdef] = def_counts.get(tdef, 0) + 1

            tclass = t.get("Class", "Thing")
            class_counts[tclass] = class_counts.get(tclass, 0) + 1

            t_faction = t.findtext("faction")
            if t_faction:
                referenced_factions.add(t_faction)

            stack_str = t.findtext("stackCount", "1")
            try:
                stack = int(stack_str)
                stack_totals[tdef] = stack_totals.get(tdef, 0) + stack
            except ValueError:
                pass

            # MinifiedThing
            if tclass == "MinifiedThing" or tdef == "MinifiedThing":
                inner = t.find("innerContainer/innerList/li")
                if inner is not None:
                    inner_id = inner.findtext("id")
                    inner_def = inner.findtext("def")
                    referenced_defs.add(inner_def)
                    container_hierarchy.append({
                        "containerId": tid,
                        "containerType": "MinifiedInner",
                        "items": [{"id": inner_id, "def": inner_def, "count": 1}]
                    })
                    if inner_id:
                        entity_ids.append(inner_id)

            # Corpse
            if tclass == "Corpse" or "Corpse" in tdef:
                inner_p = t.find("innerPawn")
                if inner_p is not None:
                    p_id = inner_p.findtext("id")
                    p_def = inner_p.findtext("def")
                    container_hierarchy.append({
                        "containerId": tid,
                        "containerType": "CorpseInnerPawn",
                        "items": [{"id": p_id, "def": p_def, "count": 1}]
                    })
                    if p_id:
                        entity_ids.append(p_id)

            # Pawns
            if tclass == "Pawn":
                p_kind = t.findtext("kindDef", "")
                is_human = (tdef == "Human")
                faction = t.findtext("faction", "None")

                if is_human:
                    name = t.findtext("name/first", "") + " " + t.findtext("name/last", "")
                    bed_assigned = t.findtext("ownership/ownedBed", "")
                    cur_job = t.findtext("jobs/curJob/def", "")

                    skills = {}
                    for sk in t.findall("skills/skills/li"):
                        s_def = sk.findtext("def")
                        s_lvl = int(sk.findtext("level", "0"))
                        skills[s_def] = s_lvl

                    hediffs = []
                    for h in t.findall("healthTracker/hediffSet/hediffs/li"):
                        h_def = h.findtext("def")
                        h_part = h.findtext("part/body", "body")
                        hediffs.append(f"{h_def}[{h_part}]")

                    eq_list = []
                    for eq in t.findall("equipment/equipment/innerList/li"):
                        eq_id = eq.findtext("id")
                        eq_def = eq.findtext("def")
                        eq_list.append(eq_id)
                        container_hierarchy.append({
                            "containerId": tid,
                            "containerType": "PawnEquipment",
                            "items": [{"id": eq_id, "def": eq_def, "count": 1}]
                        })

                    app_list = []
                    for app in t.findall("apparel/wornApparel/innerList/li"):
                        app_id = app.findtext("id")
                        app_def = app.findtext("def")
                        app_list.append(app_id)
                        container_hierarchy.append({
                            "containerId": tid,
                            "containerType": "PawnApparel",
                            "items": [{"id": app_id, "def": app_def, "count": 1}]
                        })

                    inv_list = []
                    for inv in t.findall("inventory/innerContainer/innerList/li"):
                        inv_id = inv.findtext("id")
                        inv_def = inv.findtext("def")
                        inv_count = int(inv.findtext("stackCount", "1"))
                        inv_list.append(inv_id)
                        container_hierarchy.append({
                            "containerId": tid,
                            "containerType": "PawnInventory",
                            "items": [{"id": inv_id, "def": inv_def, "count": inv_count}]
                        })

                    pawns.append({
                        "id": tid,
                        "name": name.strip(),
                        "faction": faction,
                        "isColonist": (faction == "Faction_10" or "Player" in faction),
                        "assignedBed": bed_assigned,
                        "curJob": cur_job,
                        "skills": skills,
                        "hediffs": hediffs,
                        "equipment": eq_list,
                        "apparel": app_list,
                        "inventory": inv_list
                    })
                else:
                    # Animal
                    master = t.findtext("playerSettings/master", "")
                    follow_drafted = (t.findtext("playerSettings/followDrafted", "False").lower() == "true")
                    animals.append({
                        "id": tid,
                        "def": tdef,
                        "faction": faction,
                        "master": master,
                        "followDrafted": follow_drafted
                    })

            # Colonist Buildings
            if "Building" in tclass:
                assigned_pawns = [li.text for li in t.findall("assignedPawns/li") if li.text]
                bills = len(t.findall("billStack/bills/li"))
                power = "None"
                if t.find("storedEnergy") is not None:
                    power = f"Battery({float(t.findtext('storedEnergy')):.0f})"
                elif tdef == "SolarGenerator":
                    power = "Generator"

                buildings.append({
                    "id": tid,
                    "def": tdef,
                    "stuff": t.findtext("stuff", ""),
                    "hp": int(t.findtext("health", "0")),
                    "power": power,
                    "assignedPawns": assigned_pawns,
                    "billCount": bills
                })

        # Zones
        for z in m.findall("zoneManager/allZones/li"):
            zid = int(z.findtext("ID", "0"))
            zlabel = z.findtext("label", "")
            zcells = len(z.findall("cells/li"))
            ztype = z.get("Class", "Zone")
            zones.append({"id": zid, "label": zlabel, "cellCount": zcells, "type": ztype})

        # Designations
        for d in m.findall("designationManager/allDesignations/li"):
            ddef = d.findtext("def", "")
            dtarget = d.findtext("target", "")
            designations.append({"def": ddef, "target": dtarget})

        # Conditions
        for c in m.findall("gameConditionManager/activeConditions/li"):
            cdef = c.findtext("def", "")
            cid = int(c.findtext("uniqueID", "0"))
            cdur = int(c.findtext("duration", "0"))
            conditions.append({"def": cdef, "id": cid, "duration": cdur})

        # Global Registries in World Context
        available_factions = []
        for idx, f in enumerate(game.findall("world/factionManager/allFactions/li")):
            lid = f.findtext("loadID")
            available_factions.append(f"Faction_{lid if lid is not None else idx}")
        available_world_objects = [f"WorldObject_{w.findtext('ID')}" for w in game.findall("world/worldObjects/worldObjects/li") if w.findtext("ID")]

        return {
            "manifestVersion": "1.0",
            "mapIndex": int(map_unique_id),
            "parentWorldObject": map_parent,
            "playerFaction": player_faction,
            "ticksGame": ticks_game,
            "entityCount": len(entity_ids),
            "entityIdSet": sorted(list(set(entity_ids))),
            "defCounts": def_counts,
            "classCounts": class_counts,
            "stackTotals": stack_totals,
            "containerHierarchy": container_hierarchy,
            "pawns": pawns,
            "animals": animals,
            "buildings": buildings,
            "zones": zones,
            "designations": designations,
            "conditions": conditions,
            "globalDependencies": {
                "playerFaction": player_faction,
                "factionsReferenced": sorted(list(referenced_factions)),
                "worldObjectsReferenced": sorted(list(referenced_world_objects)),
                "defsReferenced": sorted(list(referenced_defs)),
                "availableFactions": sorted(available_factions),
                "availableWorldObjects": sorted(available_world_objects)
            }
        }

    @staticmethod
    def compare(expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        missing_ids = []
        unexpected_ids = []
        count_mismatches = []
        container_errors = []
        assignment_errors = []
        dependency_errors = []

        # 1. Entity IDs
        exp_ids = set(expected.get("entityIdSet", []))
        act_ids = set(actual.get("entityIdSet", []))

        for eid in exp_ids:
            if eid not in act_ids:
                missing_ids.append(eid)
                errors.append(f"[MISSING_ENTITY] Expected entity ID '{eid}' missing in materialized state")

        for eid in act_ids:
            if eid not in exp_ids:
                unexpected_ids.append(eid)
                errors.append(f"[UNEXPECTED_ENTITY] Unexpected entity ID '{eid}' present in materialized state")

        # 2. Def Counts
        exp_defs = expected.get("defCounts", {})
        act_defs = actual.get("defCounts", {})
        for d, c in exp_defs.items():
            ac = act_defs.get(d, 0)
            if ac != c:
                count_mismatches.append(f"Def '{d}': Expected={c}, Actual={ac}")
                errors.append(f"[DEF_COUNT_MISMATCH] Def '{d}': Expected {c}, got {ac}")

        # 3. Stack totals
        exp_stacks = expected.get("stackTotals", {})
        act_stacks = actual.get("stackTotals", {})
        for item, st in exp_stacks.items():
            ast = act_stacks.get(item, 0)
            if ast != st:
                count_mismatches.append(f"Stack '{item}': Expected={st}, Actual={ast}")
                errors.append(f"[STACK_TOTAL_MISMATCH] Stack '{item}': Expected {st}, got {ast}")

        # 4. Containers
        exp_containers = {f"{c['containerId']}_{c['containerType']}": c for c in expected.get("containerHierarchy", [])}
        act_containers = {f"{c['containerId']}_{c['containerType']}": c for c in actual.get("containerHierarchy", [])}

        for key, exp_c in exp_containers.items():
            if key not in act_containers:
                container_errors.append(f"Container '{key}' missing")
                errors.append(f"[CONTAINER_MISSING] Container '{key}' missing")
            else:
                act_c = act_containers[key]
                exp_items = {i["id"]: i for i in exp_c.get("items", [])}
                act_items = {i["id"]: i for i in act_c.get("items", [])}
                for iid, it in exp_items.items():
                    if iid not in act_items:
                        container_errors.append(f"Item '{iid}' ({it.get('def')}) missing in container '{key}'")
                        errors.append(f"[CONTAINER_ITEM_MISSING] Item '{iid}' missing in container '{key}'")
                    elif act_items[iid].get("count") != it.get("count"):
                        container_errors.append(f"Item '{iid}' count mismatch in container '{key}': Expected {it.get('count')}, got {act_items[iid].get('count')}")
                        errors.append(f"[CONTAINER_ITEM_COUNT_MISMATCH] Item '{iid}' in container '{key}' count mismatch")

        # 5. Pawns & Assignments
        exp_pawns = {p["id"]: p for p in expected.get("pawns", [])}
        act_pawns = {p["id"]: p for p in actual.get("pawns", [])}

        for pid, p in exp_pawns.items():
            if pid not in act_pawns:
                assignment_errors.append(f"Pawn '{pid}' missing")
                errors.append(f"[PAWN_MISSING] Pawn '{pid}' missing")
            else:
                ap = act_pawns[pid]
                if p.get("assignedBed") and p.get("assignedBed") != ap.get("assignedBed"):
                    assignment_errors.append(f"Pawn '{pid}' Bed assignment mismatch: Expected '{p.get('assignedBed')}', got '{ap.get('assignedBed')}'")
                    errors.append(f"[BED_ASSIGNMENT_MISMATCH] Pawn '{pid}' bed mismatch")

        # 6. Animal Masters
        exp_animals = {a["id"]: a for a in expected.get("animals", [])}
        act_animals = {a["id"]: a for a in actual.get("animals", [])}
        for aid, a in exp_animals.items():
            if aid not in act_animals:
                assignment_errors.append(f"Animal '{aid}' missing")
                errors.append(f"[ANIMAL_MISSING] Animal '{aid}' missing")
            else:
                aa = act_animals[aid]
                if a.get("master") and a.get("master") != aa.get("master"):
                    assignment_errors.append(f"Animal '{aid}' Master mismatch: Expected '{a.get('master')}', got '{aa.get('master')}'")
                    errors.append(f"[ANIMAL_MASTER_MISMATCH] Animal '{aid}' master mismatch")

        # 7. Global Dependencies
        exp_factions = set(expected.get("globalDependencies", {}).get("factionsReferenced", []))
        act_factions = set(actual.get("globalDependencies", {}).get("factionsReferenced", []))
        act_avail_factions = set(actual.get("globalDependencies", {}).get("availableFactions", []))
        act_avail_objs = set(actual.get("globalDependencies", {}).get("availableWorldObjects", []))

        for f in exp_factions:
            if f not in act_factions:
                dependency_errors.append(f"Faction '{f}' missing from map reference set")
                errors.append(f"[DEPENDENCY_MISSING] Faction '{f}' missing in materialized context")
            if act_avail_factions and f not in act_avail_factions:
                dependency_errors.append(f"Referenced Faction '{f}' missing from World FactionManager registry")
                errors.append(f"[GLOBAL_REGISTRY_MISSING] Referenced Faction '{f}' not found in FactionManager registry!")

        exp_parent = expected.get("parentWorldObject", "")
        if exp_parent and act_avail_objs and exp_parent not in act_avail_objs:
            dependency_errors.append(f"Parent WorldObject '{exp_parent}' missing from WorldObjects registry")
            errors.append(f"[GLOBAL_REGISTRY_MISSING] Parent WorldObject '{exp_parent}' not found in WorldObjects registry!")

        is_pass = (len(errors) == 0)
        return {
            "isPass": is_pass,
            "totalErrors": len(errors),
            "errors": errors,
            "missingEntityIds": missing_ids,
            "unexpectedEntityIds": unexpected_ids,
            "countMismatches": count_mismatches,
            "containerErrors": container_errors,
            "assignmentErrors": assignment_errors,
            "dependencyErrors": dependency_errors
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: census_oracle.py <save_file.rws> [out_census.json]")
        sys.exit(1)

    in_save = Path(sys.argv[1])
    census = CensusOracle.extract_from_xml(in_save)
    print(f"Extracted Census from {in_save}:")
    print(f"  Entity Count: {census['entityCount']}")
    print(f"  Pawns: {len(census['pawns'])}, Animals: {len(census['animals'])}, Buildings: {len(census['buildings'])}")
    print(f"  Containers: {len(census['containerHierarchy'])}")

    if len(sys.argv) >= 3:
        out_json = Path(sys.argv[2])
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(census, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved Census to: {out_json}")
