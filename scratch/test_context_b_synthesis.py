import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = Path(r"scratch/ComplexSettlementFixture.rws")
OUT_CONTEXT_B = Path(r"scratch/TargetSettlement_ContextB.rws")

def synthesize_context_b():
    print("=" * 80)
    print("SYNTHESIZING CONTEXT B: Target-Only Minimal Valid World")
    print("=" * 80)

    tree = ET.parse(SOURCE)
    root = tree.getroot()
    game = root.find("game")
    maps = game.find("maps")

    print(f"Original maps count: {len(maps)}")
    # Keep only Map 0 (the target settlement)
    target_map = maps[0]
    map_parent_id = target_map.findtext("mapInfo/parent")
    print(f"Target map uniqueID={target_map.findtext('uniqueID')}, parent={map_parent_id}")

    # Remove all other maps
    while len(maps) > 1:
        maps.remove(maps[1])
    print(f"Pruned maps count: {len(maps)}")

    # Prune WorldObjects to only those referenced by Map 0 or essential
    world_objects = game.find("world/worldObjects/worldObjects")
    if world_objects is not None:
        kept_objs = []
        for obj in world_objects:
            obj_id = obj.findtext("ID")
            # Keep the target settlement world object
            if f"WorldObject_{obj_id}" == map_parent_id or obj_id == "91":
                kept_objs.append(obj)
            # Or keep faction bases if essential
        print(f"Original world objects count: {len(world_objects)}")
        world_objects.clear()
        for ko in kept_objs:
            world_objects.append(ko)
        print(f"Pruned world objects count: {len(world_objects)}")

    # Save synthesized Context B save
    OUT_CONTEXT_B.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUT_CONTEXT_B, encoding="utf-8", xml_declaration=True)
    print(f"[SUCCESS] Wrote Context B save: {OUT_CONTEXT_B} ({OUT_CONTEXT_B.stat().st_size:,} bytes)")

if __name__ == "__main__":
    synthesize_context_b()
