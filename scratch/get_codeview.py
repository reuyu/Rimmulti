import struct
from pathlib import Path

def get_codeview_guid(dll_path):
    data = Path(dll_path).read_bytes()
    # Search for RSDS magic
    pos = data.find(b'RSDS')
    if pos != -1:
        guid_bytes = data[pos+4:pos+20]
        d1, d2, d3 = struct.unpack('<IHH', guid_bytes[:8])
        d4 = guid_bytes[8:16]
        guid_str = f"{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}"
        age = struct.unpack('<I', data[pos+20:pos+24])[0]
        pdb_path = data[pos+24:].split(b'\0')[0].decode('utf-8', errors='ignore')
        return guid_str, age, pdb_path
    return None, None, None

for conf, p in [
    ("Debug", r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
    ("Release", r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll")
]:
    guid, age, pdb = get_codeview_guid(p)
    print(f"{conf}: CodeView GUID={guid}, age={age}, pdb={pdb}")
