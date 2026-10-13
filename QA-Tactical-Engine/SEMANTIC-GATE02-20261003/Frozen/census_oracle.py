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
        fires = []
        plants = []
        referenced_defs = set()
        referenced_factions = set()
        referenced_world_objects = {map_parent}

        for t in things:
            tid = t.findtext("id")
            if not tid:
                continue
            tdef = t.findtext("def", "Unknown")
            tclass = t.get("Class", "Thing")
            is_unstable = (
                tdef in ("Granite", "Marble", "Slate", "Sandstone", "Limestone") or
                tdef.startswith("Chunk") or 
                tdef.startswith("Rock_") or 
                tdef.startswith("Mineable") or 
                tdef.startswith("Filth_") or 
                tdef.startswith("Slag") or 
                "Filth" in tclass
            )
            if not is_unstable:
                entity_ids.append(tid)

            referenced_defs.add(tdef)
            def_counts[tdef] = def_counts.get(tdef, 0) + 1
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

            pos = t.findtext("pos", "")

            # MinifiedThing
            if tclass == "MinifiedThing" or tdef == "MinifiedThing":
                inner = t.find("innerContainer/innerList/li")
                if inner is not None:
                    inner_id = inner.findtext("id", "")
                    inner_def = inner.findtext("def", "")
                    referenced_defs.add(inner_def)
                    container_hierarchy.append({
                        "containerId": tid,
                        "containerType": "MinifiedInner",
                        "items": [{"id": inner_id, "def": inner_def, "count": 1}]
                    })
                    if inner_id:
                        entity_ids.append(inner_id)

            # Corpse / Casket
            if tclass == "Corpse" or "Corpse" in tdef:
                inner_p = t.find("innerPawn")
                if inner_p is not None:
                    p_id = inner_p.findtext("id", "")
                    p_def = inner_p.findtext("def", "")
                    container_hierarchy.append({
                        "containerId": tid,
                        "containerType": "CorpseInnerPawn",
                        "items": [{"id": p_id, "def": p_def, "count": 1}]
                    })
                    if p_id:
                        entity_ids.append(p_id)

            # Fire
            if tdef == "Fire":
                fire_size = float(t.findtext("fireSize", "0.1"))
                fires.append({
                    "id": tid,
                    "pos": pos,
                    "fireSize": fire_size
                })

            # Plant / Crop
            if "Plant" in tclass or tdef.startswith("Plant_"):
                growth = float(t.findtext("growth", "0.0"))
                age = int(t.findtext("age", "0"))
                plants.append({
                    "id": tid,
                    "def": tdef,
                    "pos": pos,
                    "growth": growth,
                    "age": age
                })

            # Pawns
            if tclass == "Pawn":
                is_human = (tdef == "Human")
                faction = t.findtext("faction", "None")

                if is_human:
                    name = t.findtext("name/first", "") + " " + t.findtext("name/last", "")
                    bed_assigned = t.findtext("ownership/ownedBed", "").replace("Thing_", "")
                    if bed_assigned == "null":
                        bed_assigned = ""
                    cur_job = t.findtext("jobs/curJob/def", "")

                    skills = {}
                    for sk in t.findall("skills/skills/li"):
                        s_def = sk.findtext("def", "")
                        s_lvl = int(sk.findtext("level", "0"))
                        skills[s_def] = s_lvl

                    hediffs = []
                    for h in t.findall("healthTracker/hediffSet/hediffs/li"):
                        h_def = h.findtext("def", "")
                        h_part = h.findtext("part/body", "body")
                        h_sev = float(h.findtext("severity", "1.0"))
                        h_lid = h.findtext("loadID", "")
                        hediffs.append({
                            "def": h_def,
                            "part": h_part,
                            "severity": h_sev,
                            "loadID": h_lid
                        })

                    relations = []
                    for r in t.findall("social/directRelations/li"):
                        r_def = r.findtext("def", "")
                        r_other = r.findtext("otherPawn", "").replace("Thing_", "")
                        if r_def and r_other:
                            relations.append({
                                "def": r_def,
                                "otherPawn": r_other,
                                "relationDef": r_def,
                                "otherPawnId": r_other
                            })

                    eq_list = []
                    for eq in t.findall("equipment/equipment/innerList/li"):
                        eq_id = eq.findtext("id", "")
                        eq_def = eq.findtext("def", "")
                        eq_item = {"id": eq_id, "def": eq_def, "count": 1}
                        eq_list.append(eq_item)
                        container_hierarchy.append({
                            "containerId": tid,
                            "containerType": "PawnEquipment",
                            "items": [eq_item]
                        })

                    app_list = []
                    app_items = []
                    for app in t.findall("apparel/wornApparel/innerList/li"):
                        app_id = app.findtext("id", "")
                        app_def = app.findtext("def", "")
                        app_item = {"id": app_id, "def": app_def, "count": 1}
                        app_list.append(app_item)
                        app_items.append(app_item)
                    if app_items:
                        container_hierarchy.append({
                            "containerId": tid,
                            "containerType": "PawnApparel",
                            "items": app_items
                        })

                    inv_list = []
                    for inv in t.findall("inventory/innerContainer/innerList/li"):
                        inv_id = inv.findtext("id", "")
                        inv_def = inv.findtext("def", "")
                        inv_count = int(inv.findtext("stackCount", "1"))
                        inv_item = {"id": inv_id, "def": inv_def, "count": inv_count}
                        inv_list.append(inv_item)
                        container_hierarchy.append({
                            "containerId": tid,
                            "containerType": "PawnInventory",
                            "items": [inv_item]
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
                        "relations": relations,
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

            # Buildings & Power & Bills
            if "Building" in tclass:
                assigned_pawns = [li.text for li in t.findall("assignedPawns/li") if li.text]
                power = "None"
                battery_energy = 0.0
                if t.find("storedEnergy") is not None:
                    battery_energy = float(t.findtext("storedEnergy", "0.0"))
                    power = f"Battery({battery_energy:.0f})"
                elif t.find("storedPower") is not None:
                    battery_energy = float(t.findtext("storedPower", "0.0"))
                    power = f"Battery({battery_energy:.0f})"
                elif tdef == "SolarGenerator":
                    power = "Generator"

                bills = []
                for b in t.findall("billStack/bills/li"):
                    b_recipe = b.findtext("recipe", "")
                    b_mode = b.findtext("repeatMode", "")
                    b_target = int(b.findtext("targetCount", "1"))
                    b_count = int(b.findtext("repeatCount", "1"))
                    bills.append({
                        "recipe": b_recipe,
                        "repeatMode": b_mode,
                        "targetCount": b_target,
                        "repeatCount": b_count
                    })

                buildings.append({
                    "id": tid,
                    "def": tdef,
                    "stuff": t.findtext("stuff", ""),
                    "hp": int(t.findtext("health", "0")),
                    "power": power,
                    "batteryStoredEnergy": battery_energy,
                    "assignedPawns": assigned_pawns,
                    "bills": bills
                })

        # Zones: cells & crop
        for z in m.findall("zoneManager/allZones/li"):
            zid = int(z.findtext("ID", "0"))
            zlabel = z.findtext("label", "")
            zcells = [c.text for c in z.findall("cells/li") if c.text]
            ztype = z.get("Class", "Zone")
            z_crop = z.findtext("plantDefToGrow", "")
            zones.append({
                "id": zid,
                "label": zlabel,
                "cells": sorted(zcells),
                "cellCount": len(zcells),
                "type": ztype,
                "plantDefToGrow": z_crop
            })

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

        return {
            "manifestVersion": "2.0",
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
            "fires": fires,
            "plants": plants,
            "globalDependencies": {
                "playerFaction": player_faction,
                "factionsReferenced": sorted(list(referenced_factions)),
                "worldObjectsReferenced": sorted(list(referenced_world_objects)),
                "defsReferenced": sorted(list(referenced_defs))
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
        skill_errors = []
        hediff_errors = []
        bill_errors = []
        zone_errors = []
        designation_errors = []
        dynamic_state_errors = []
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
                    else:
                        found = act_items[iid]
                        if found.get("count") != it.get("count"):
                            container_errors.append(f"Item '{iid}' count mismatch in container '{key}': Expected {it.get('count')}, got {found.get('count')}")
                            errors.append(f"[CONTAINER_ITEM_COUNT_MISMATCH] Item '{iid}' count mismatch in '{key}': Expected {it.get('count')}, got {found.get('count')}")
                        if found.get("def") != it.get("def"):
                            container_errors.append(f"Item '{iid}' def mismatch in container '{key}': Expected {it.get('def')}, got {found.get('def')}")
                            errors.append(f"[CONTAINER_ITEM_DEF_MISMATCH] Item '{iid}' def mismatch in '{key}'")

        # 5. Pawns, Skills, Hediffs, Assignments & Relations
        exp_pawns = {p["id"]: p for p in expected.get("pawns", [])}
        act_pawns = {p["id"]: p for p in actual.get("pawns", [])}

        for pid, p in exp_pawns.items():
            if pid not in act_pawns:
                assignment_errors.append(f"Pawn '{pid}' missing")
                errors.append(f"[PAWN_MISSING] Pawn '{pid}' missing")
            else:
                ap = act_pawns[pid]
                if p.get("assignedBed") != ap.get("assignedBed"):
                    assignment_errors.append(f"Pawn '{pid}' Bed assignment mismatch: Expected '{p.get('assignedBed')}', got '{ap.get('assignedBed')}'")
                    errors.append(f"[BED_ASSIGNMENT_MISMATCH] Pawn '{pid}' bed mismatch: Expected '{p.get('assignedBed')}', got '{ap.get('assignedBed')}'")

                # Skills
                for sk_name, sk_lvl in p.get("skills", {}).items():
                    act_lvl = ap.get("skills", {}).get(sk_name, 0)
                    if act_lvl != sk_lvl:
                        skill_errors.append(f"Pawn '{pid}' Skill '{sk_name}': Expected {sk_lvl}, got {act_lvl}")
                        errors.append(f"[SKILL_MISMATCH] Pawn '{pid}' Skill '{sk_name}': Expected {sk_lvl}, got {act_lvl}")

                # Hediffs
                exp_hediffs = p.get("hediffs", [])
                act_hediffs = ap.get("hediffs", [])
                if len(exp_hediffs) != len(act_hediffs):
                    hediff_errors.append(f"Pawn '{pid}' hediff count mismatch: Expected {len(exp_hediffs)}, got {len(act_hediffs)}")
                    errors.append(f"[HEDIFF_COUNT_MISMATCH] Pawn '{pid}' Hediffs: Expected {len(exp_hediffs)}, got {len(act_hediffs)}")

                for eh in exp_hediffs:
                    match = next((ah for ah in act_hediffs if ah.get("def") == eh.get("def") and ah.get("part") == eh.get("part")), None)
                    if not match:
                        hediff_errors.append(f"Pawn '{pid}' missing hediff '{eh.get('def')}[{eh.get('part')}]'")
                        errors.append(f"[HEDIFF_MISSING] Pawn '{pid}' missing hediff '{eh.get('def')}[{eh.get('part')}]'")
                    elif abs(float(eh.get("severity", 1.0)) - float(match.get("severity", 1.0))) > 0.05:
                        hediff_errors.append(f"Pawn '{pid}' hediff '{eh.get('def')}' severity mismatch: Expected {eh.get('severity')}, got {match.get('severity')}")
                        errors.append(f"[HEDIFF_SEVERITY_MISMATCH] Pawn '{pid}' hediff '{eh.get('def')}': Expected {eh.get('severity')}, got {match.get('severity')}")

                # Relations
                for er in p.get("relations", []):
                    rel_match = any(ar for ar in ap.get("relations", []) if ar.get("def") == er.get("def") and ar.get("otherPawn") == er.get("otherPawn"))
                    if not rel_match:
                        assignment_errors.append(f"Pawn '{pid}' missing relation '{er.get('def')} -> {er.get('otherPawn')}'")
                        errors.append(f"[RELATION_MISSING] Pawn '{pid}' missing relation '{er.get('def')} -> {er.get('otherPawn')}'")

        # 6. Animal Masters & Follow
        exp_animals = {a["id"]: a for a in expected.get("animals", [])}
        act_animals = {a["id"]: a for a in actual.get("animals", [])}
        for aid, a in exp_animals.items():
            if aid not in act_animals:
                assignment_errors.append(f"Animal '{aid}' missing")
                errors.append(f"[ANIMAL_MISSING] Animal '{aid}' missing")
            else:
                aa = act_animals[aid]
                if a.get("master") != aa.get("master"):
                    assignment_errors.append(f"Animal '{aid}' Master mismatch: Expected '{a.get('master')}', got '{aa.get('master')}'")
                    errors.append(f"[ANIMAL_MASTER_MISMATCH] Animal '{aid}' master: Expected '{a.get('master')}', got '{aa.get('master')}'")
                if a.get("followDrafted") != aa.get("followDrafted"):
                    assignment_errors.append(f"Animal '{aid}' followDrafted mismatch: Expected {a.get('followDrafted')}, got {aa.get('followDrafted')}")
                    errors.append(f"[ANIMAL_FOLLOW_MISMATCH] Animal '{aid}' followDrafted: Expected {a.get('followDrafted')}, got {aa.get('followDrafted')}")

        # 7. Buildings, Workbench Bills & Power
        exp_blds = {b["id"]: b for b in expected.get("buildings", [])}
        act_blds = {b["id"]: b for b in actual.get("buildings", [])}
        for bid, b in exp_blds.items():
            if bid in act_blds:
                ab = act_blds[bid]
                if abs(float(b.get("batteryStoredEnergy", 0.0)) - float(ab.get("batteryStoredEnergy", 0.0))) > 10.0:
                    dynamic_state_errors.append(f"Battery '{bid}' energy mismatch: Expected {b.get('batteryStoredEnergy')}, got {ab.get('batteryStoredEnergy')}")
                    errors.append(f"[POWER_SCALAR_MISMATCH] Battery '{bid}' energy: Expected {b.get('batteryStoredEnergy')}, got {ab.get('batteryStoredEnergy')}")

                exp_bills = b.get("bills", [])
                act_bills = ab.get("bills", [])
                if len(exp_bills) != len(act_bills):
                    bill_errors.append(f"Building '{bid}' bill count mismatch: Expected {len(exp_bills)}, got {len(act_bills)}")
                    errors.append(f"[BILL_COUNT_MISMATCH] Building '{bid}' bills: Expected {len(exp_bills)}, got {len(act_bills)}")
                for i in range(min(len(exp_bills), len(act_bills))):
                    eb, abill = exp_bills[i], act_bills[i]
                    if eb.get("recipe") != abill.get("recipe"):
                        bill_errors.append(f"Building '{bid}' bill[{i}] recipe mismatch: Expected {eb.get('recipe')}, got {abill.get('recipe')}")
                        errors.append(f"[BILL_RECIPE_MISMATCH] Building '{bid}' bill recipe: Expected {eb.get('recipe')}, got {abill.get('recipe')}")
                    if eb.get("targetCount") != abill.get("targetCount"):
                        bill_errors.append(f"Building '{bid}' bill[{i}] targetCount: Expected {eb.get('targetCount')}, got {abill.get('targetCount')}")
                        errors.append(f"[BILL_TARGETCOUNT_MISMATCH] Building '{bid}' targetCount: Expected {eb.get('targetCount')}, got {abill.get('targetCount')}")

        # 8. Zones: Cells & Crop
        exp_zones = {z["id"]: z for z in expected.get("zones", [])}
        act_zones = {z["id"]: z for z in actual.get("zones", [])}
        for zid, z in exp_zones.items():
            if zid not in act_zones:
                zone_errors.append(f"Zone '{zid}' missing")
                errors.append(f"[ZONE_MISSING] Zone '{zid}' missing")
            else:
                az = act_zones[zid]
                if set(z.get("cells", [])) != set(az.get("cells", [])):
                    zone_errors.append(f"Zone '{z.get('label')}' cells mismatch")
                    errors.append(f"[ZONE_CELLS_MISMATCH] Zone '{z.get('label')}' exact cells mismatch")
                if z.get("plantDefToGrow") != az.get("plantDefToGrow"):
                    zone_errors.append(f"Zone '{z.get('label')}' crop mismatch: Expected {z.get('plantDefToGrow')}, got {az.get('plantDefToGrow')}")
                    errors.append(f"[ZONE_CROP_MISMATCH] Zone '{z.get('label')}' crop: Expected {z.get('plantDefToGrow')}, got {az.get('plantDefToGrow')}")

        # 9. Designations
        exp_desigs = {(d.get("def"), d.get("target")) for d in expected.get("designations", [])}
        act_desigs = {(d.get("def"), d.get("target")) for d in actual.get("designations", [])}
        for ed in exp_desigs:
            if ed not in act_desigs:
                designation_errors.append(f"Designation '{ed[0]}' at '{ed[1]}' missing")
                errors.append(f"[DESIGNATION_MISMATCH] Designation '{ed[0]}' at '{ed[1]}' missing")

        # 10. Fires
        exp_fires = {f.get("pos"): f for f in expected.get("fires", [])}
        act_fires = {f.get("pos"): f for f in actual.get("fires", [])}
        for pos, f in exp_fires.items():
            if pos not in act_fires:
                dynamic_state_errors.append(f"Fire at '{pos}' missing")
                errors.append(f"[FIRE_MISSING] Fire at '{pos}' missing")
            elif abs(float(f.get("fireSize", 0.0)) - float(act_fires[pos].get("fireSize", 0.0))) > 0.05:
                dynamic_state_errors.append(f"Fire at '{pos}' size mismatch: Expected {f.get('fireSize')}, got {act_fires[pos].get('fireSize')}")
                errors.append(f"[FIRE_SIZE_MISMATCH] Fire at '{pos}': Expected {f.get('fireSize')}, got {act_fires[pos].get('fireSize')}")

        # 11. Plants
        exp_plants = {(p.get("pos"), p.get("def")): p for p in expected.get("plants", [])}
        act_plants = {(p.get("pos"), p.get("def")): p for p in actual.get("plants", [])}
        for k, p in exp_plants.items():
            if k in act_plants:
                ap = act_plants[k]
                if abs(float(p.get("growth", 0.0)) - float(ap.get("growth", 0.0))) > 0.02:
                    dynamic_state_errors.append(f"Plant at '{k[0]}' growth mismatch: Expected {p.get('growth')}, got {ap.get('growth')}")
                    errors.append(f"[PLANT_GROWTH_MISMATCH] Plant at '{k[0]}' growth: Expected {p.get('growth')}, got {ap.get('growth')}")

        # 12. Conditions
        exp_conds = {c.get("def"): c for c in expected.get("conditions", [])}
        act_conds = {c.get("def"): c for c in actual.get("conditions", [])}
        for cdef, c in exp_conds.items():
            if cdef not in act_conds:
                dynamic_state_errors.append(f"Condition '{cdef}' missing")
                errors.append(f"[CONDITION_MISSING] Condition '{cdef}' missing")
            elif c.get("duration") != act_conds[cdef].get("duration"):
                dynamic_state_errors.append(f"Condition '{cdef}' duration mismatch: Expected {c.get('duration')}, got {act_conds[cdef].get('duration')}")
                errors.append(f"[CONDITION_DURATION_MISMATCH] Condition '{cdef}' duration: Expected {c.get('duration')}, got {act_conds[cdef].get('duration')}")

        # 13. Global Dependencies
        exp_factions = set(expected.get("globalDependencies", {}).get("factionsReferenced", []))
        act_factions = set(actual.get("globalDependencies", {}).get("factionsReferenced", []))
        for f in exp_factions:
            if f not in act_factions:
                dependency_errors.append(f"Faction '{f}' missing from map reference set")
                errors.append(f"[DEPENDENCY_MISSING] Faction '{f}' missing in materialized context")

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
            "skillErrors": skill_errors,
            "hediffErrors": hediff_errors,
            "billErrors": bill_errors,
            "zoneErrors": zone_errors,
            "designationErrors": designation_errors,
            "dynamicStateErrors": dynamic_state_errors,
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
    print(f"  Containers: {len(census['containerHierarchy'])}, Zones: {len(census['zones'])}, Fires: {len(census['fires'])}, Plants: {len(census['plants'])}")

    if len(sys.argv) >= 3:
        out_json = Path(sys.argv[2])
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(census, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved Census to: {out_json}")
