import os, struct, uuid

def read_codeview(dll_path):
    with open(dll_path, 'rb') as f:
        data = f.read()
    
    # Check MZ
    if data[:2] != b'MZ':
        return None
    pe_offset = struct.unpack_from('<I', data, 0x3C)[0]
    if data[pe_offset:pe_offset+4] != b'PE\x00\x00':
        return None
    
    # Optional header
    magic = struct.unpack_from('<H', data, pe_offset + 24)[0]
    is_64 = (magic == 0x20B)
    
    # Data directories
    if is_64:
        debug_dir_rva = struct.unpack_from('<I', data, pe_offset + 24 + 112 + 6*8)[0]
        debug_dir_size = struct.unpack_from('<I', data, pe_offset + 24 + 112 + 6*8 + 4)[0]
    else:
        debug_dir_rva = struct.unpack_from('<I', data, pe_offset + 24 + 96 + 6*8)[0]
        debug_dir_size = struct.unpack_from('<I', data, pe_offset + 24 + 96 + 6*8 + 4)[0]
        
    if debug_dir_rva == 0 or debug_dir_size == 0:
        return None
        
    # Section headers to convert RVA to file offset
    num_sections = struct.unpack_from('<H', data, pe_offset + 6)[0]
    opt_header_size = struct.unpack_from('<H', data, pe_offset + 20)[0]
    section_offset = pe_offset + 24 + opt_header_size
    
    def rva_to_offset(rva):
        for i in range(num_sections):
            sec = section_offset + i * 40
            v_size, v_addr, r_size, r_offset = struct.unpack_from('<IIII', data, sec + 8)
            if v_addr <= rva < v_addr + max(v_size, r_size):
                return r_offset + (rva - v_addr)
        return None

    debug_file_offset = rva_to_offset(debug_dir_rva)
    if debug_file_offset is None:
        return None
        
    entries = debug_dir_size // 28
    for i in range(entries):
        e_off = debug_file_offset + i * 28
        e_type, e_size, e_rva, e_ptr = struct.unpack_from('<IIII', data, e_off + 12)
        if e_type == 2: # IMAGE_DEBUG_TYPE_CODEVIEW
            cv_data = data[e_ptr:e_ptr+e_size]
            if cv_data[:4] == b'RSDS':
                guid_bytes = cv_data[4:20]
                # GUID: Data1 (4B LE), Data2 (2B LE), Data3 (2B LE), Data4 (8B BE)
                d1, d2, d3 = struct.unpack_from('<IHH', guid_bytes, 0)
                d4 = guid_bytes[8:]
                guid_str = f'{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}'
                age = struct.unpack_from('<I', cv_data, 20)[0]
                pdb_path = cv_data[24:].split(b'\x00')[0].decode('utf-8', errors='replace')
                return {'guid': guid_str, 'age': age, 'pdb_path': pdb_path}
    return None

dlls = [
    r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
    r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
    r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
]

for d in dlls:
    info = read_codeview(d)
    print(d)
    print('  CodeView:', info)
