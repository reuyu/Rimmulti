import struct

def get_mvid_from_pe(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # PE signature offset at 0x3C
    e_lfanew = struct.unpack_from('<I', data, 0x3C)[0]
    pe_sig = data[e_lfanew:e_lfanew+4]
    if pe_sig != b'PE\x00\x00':
        raise ValueError("Not a valid PE file")
    
    coff_header_offset = e_lfanew + 4
    num_sections = struct.unpack_from('<H', data, coff_header_offset + 2)[0]
    opt_header_size = struct.unpack_from('<H', data, coff_header_offset + 16)[0]
    opt_header_offset = coff_header_offset + 20
    
    magic = struct.unpack_from('<H', data, opt_header_offset)[0]
    if magic == 0x10B: # PE32
        clr_rva_offset = opt_header_offset + 208
    elif magic == 0x20B: # PE32+
        clr_rva_offset = opt_header_offset + 224
    else:
        raise ValueError("Unknown PE magic")
    
    clr_rva, clr_size = struct.unpack_from('<II', data, clr_rva_offset)
    if clr_rva == 0 or clr_size == 0:
        raise ValueError("No CLR header found")
    
    # Section headers
    sections_offset = opt_header_offset + opt_header_size
    def rva_to_offset(rva):
        for i in range(num_sections):
            sec_offset = sections_offset + i * 40
            sec_name, sec_vsize, sec_va, sec_raw_size, sec_raw_ptr = struct.unpack_from('<8sIIII', data, sec_offset)
            if sec_va <= rva < sec_va + max(sec_vsize, sec_raw_size):
                return sec_raw_ptr + (rva - sec_va)
        raise ValueError(f"RVA 0x{rva:X} not found in sections")
    
    clr_header_offset = rva_to_offset(clr_rva)
    # Metadata RVA is at offset 8 of CLR header (4 bytes size, 4 bytes major/minor, 4 bytes RVA)
    md_rva, md_size = struct.unpack_from('<II', data, clr_header_offset + 8)
    md_offset = rva_to_offset(md_rva)
    
    # Metadata root
    # signature 0x424A5342 (BSJB)
    sig = struct.unpack_from('<I', data, md_offset)[0]
    if sig != 0x424A5342:
        raise ValueError("Invalid metadata root signature")
    
    v_len = struct.unpack_from('<I', data, md_offset + 12)[0]
    streams_header_offset = md_offset + 16 + v_len
    # align to 4 bytes if needed, but in CLI spec, v_len string is rounded up to next 4 byte boundary
    # Actually, length is in v_len, then string bytes (aligned)
    # Let's align:
    streams_header_offset = md_offset + 16 + ((v_len + 3) & ~3)
    
    flags, num_streams = struct.unpack_from('<HH', data, streams_header_offset)
    stream_headers = streams_header_offset + 4
    
    guid_offset = None
    curr = stream_headers
    for _ in range(num_streams):
        s_offset, s_size = struct.unpack_from('<II', data, curr)
        curr += 8
        s_name = bytearray()
        while data[curr] != 0:
            s_name.append(data[curr])
            curr += 1
        curr += 1 # null term
        curr = (curr + 3) & ~3 # 4-byte aligned
        
        name_str = s_name.decode('ascii')
        if name_str == '#GUID':
            guid_offset = md_offset + s_offset
            break
            
    if guid_offset is None:
        raise ValueError("#GUID stream not found")
        
    # First GUID in #GUID stream is MVID (16 bytes)
    # GUID format: Data1 (4B le), Data2 (2B le), Data3 (2B le), Data4 (8B be)
    d1, d2, d3 = struct.unpack_from('<IHH', data, guid_offset)
    d4 = data[guid_offset+8:guid_offset+16]
    mvid = f"{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}"
    return mvid

debug_path = r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
release_path = r'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll'

print('Debug MVID:  ', get_mvid_from_pe(debug_path))
print('Release MVID:', get_mvid_from_pe(release_path))
