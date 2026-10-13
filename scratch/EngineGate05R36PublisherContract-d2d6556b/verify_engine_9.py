#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import os

engine9_files = [
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs", "544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD", 276685),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs", "391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1", 170135),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052", 1774),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll", "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029", 326144),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb", "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE", 79220),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll", "9CBA7E69210DE90B069F269744F3140C4ADD802FD868AB0E0C71FB0E5F69D106", 308224),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb", "F05FE976EB522B6A5FC78338B0C35A8CC5341322BACB4CA6310F6AF3682933F5", 57776),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll", "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029", 326144),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb", "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE", 79220),
]

for p, s, b in engine9_files:
    with open(p, "rb") as f:
        data = f.read()
    actual_sha = hashlib.sha256(data).hexdigest().upper()
    actual_size = len(data)
    assert actual_sha == s, f"Engine file mismatch {p}: sha {actual_sha} vs {s}"
    assert actual_size == b, f"Engine file mismatch {p}: size {actual_size} vs {b}"
    print(f"OK: {os.path.basename(p)} ({actual_size} B)")

print("All 9 Engine baseline files 100% BIT-EXACT MATCH!")
