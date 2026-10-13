with open("scratch/TargetSettlement_Clean_ContextB.rws", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

for pos in [2219545, 2243545, 2276859]:
    chunk = text[pos:pos+1500]
    name_m = chunk.split("<name Class=\"NameTriple\">")[1].split("</name>")[0] if "<name Class=\"NameTriple\">" in chunk else "Unknown"
    id_m = chunk.split("<id>")[1].split("</id>")[0] if "<id>" in chunk else "Unknown"
    print(f"Map Pawn at {pos}: ID={id_m}, Name={name_m.replace(chr(10), ' ').replace(chr(9), ' ')}")
    if "<def>Shooting</def>" in chunk:
        shoot_part = chunk.split("<def>Shooting</def>")[1][:100]
        print("  Shooting:", shoot_part.replace("\n", "").replace("\t", ""))
