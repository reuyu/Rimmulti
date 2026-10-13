import os, struct, uuid

def parse_pe(path):
    with open(path, "rb") as f:
        data = f.read()

    # DOS header
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    pe_sig = data[e_lfanew:e_lfanew+4]
    if pe_sig != b"PE\x00\x00":
        return None

    coff_offset = e_lfanew + 4
    num_sections = struct.unpack_from("<H", data, coff_offset + 2)[0]
    opt_header_size = struct.unpack_from("<H", data, coff_offset + 16)[0]
    opt_offset = coff_offset + 20

    magic = struct.unpack_from("<H", data, opt_offset)[0]
    if magic == 0x10B: # PE32
        rva_dbg = struct.unpack_from("<I", data, opt_offset + 144)[0]
        size_dbg = struct.unpack_from("<I", data, opt_offset + 148)[0]
        rva_cli = struct.unpack_from("<I", data, opt_offset + 208)[0]
    elif magic == 0x20B: # PE32+
        rva_dbg = struct.unpack_from("<I", data, opt_offset + 160)[0]
        size_dbg = struct.unpack_from("<I", data, opt_offset + 164)[0]
        rva_cli = struct.unpack_from("<I", data, opt_offset + 224)[0]
    else:
        return None

    section_table_offset = opt_offset + opt_header_size
    sections = []
    for i in range(num_sections):
        sec_off = section_table_offset + i * 40
        sec_name = data[sec_off:sec_off+8].rstrip(b"\x00").decode("latin1")
        vsize, va, rsize, rptr = struct.unpack_from("<IIII", data, sec_off + 8)
        sections.append((va, vsize, rptr, rsize))

    def rva_to_file_offset(rva):
        for va, vsize, rptr, rsize in sections:
            if va <= rva < va + max(vsize, rsize):
                return rptr + (rva - va)
        return None

    # CodeView Debug info
    cv_guid = None
    cv_age = None
    cv_path = None
    if rva_dbg and size_dbg:
        dbg_off = rva_to_file_offset(rva_dbg)
        if dbg_off:
            num_entries = size_dbg // 28
            for i in range(num_entries):
                entry_off = dbg_off + i * 28
                dtype, dsize, drva, dptr = struct.unpack_from("<IIII", data, entry_off + 12)
                if dtype == 2: # IMAGE_DEBUG_TYPE_CODEVIEW
                    cv_off = dptr if dptr else rva_to_file_offset(drva)
                    if cv_off and data[cv_off:cv_off+4] == b"RSDS":
                        raw_guid = data[cv_off+4:cv_off+20]
                        # Guid formatting
                        d1, d2, d3 = struct.unpack_from("<IHH", raw_guid, 0)
                        d4 = raw_guid[8:]
                        cv_guid = f"{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}"
                        cv_age = struct.unpack_from("<I", data, cv_off + 20)[0]
                        cv_path = data[cv_off+24:cv_off+dsize].rstrip(b"\x00").decode("latin1", errors="replace")

    # MVID from CLI metadata
    mvid = None
    if rva_cli:
        cli_off = rva_to_file_offset(rva_cli)
        if cli_off:
            meta_rva, meta_size = struct.unpack_from("<II", data, cli_off + 8)
            meta_off = rva_to_file_offset(meta_rva)
            if meta_off and data[meta_off:meta_off+4] == b"BSJB":
                vlen = struct.unpack_from("<I", data, meta_off + 12)[0]
                streams_off = meta_off + 16 + vlen
                # pad vlen to 4 bytes
                pad = (4 - (vlen % 4)) % 4
                streams_off = meta_off + 16 + vlen + pad + 2 # flags(2)
                num_streams = struct.unpack_from("<H", data, streams_off)[0]
                cur = streams_off + 2
                guid_offset = None
                for _ in range(num_streams):
                    soffset, ssize = struct.unpack_from("<II", data, cur)
                    cur += 8
                    sname = []
                    while True:
                        ch = data[cur:cur+1]
                        cur += 1
                        if ch == b"\x00":
                            break
                        sname.append(ch)
                    sname = b"".join(sname).decode("latin1")
                    # pad stream name to 4 bytes
                    pad = (4 - ((len(sname) + 1) % 4)) % 4
                    cur += pad
                    if sname == "#GUID":
                        guid_offset = meta_off + soffset
                if guid_offset:
                    raw_guid = data[guid_offset:guid_offset+16]
                    d1, d2, d3 = struct.unpack_from("<IHH", raw_guid, 0)
                    d4 = raw_guid[8:]
                    mvid = f"{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}"

    return {
        "mvid": mvid,
        "codeview_guid": cv_guid,
        "codeview_age": cv_age,
        "codeview_path": cv_path
    }

for cfg in ["Debug", "Release"]:
    p = os.path.join(r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin", cfg, r"net472\WarEconomy.WorkerBridge.PoC.dll")
    res = parse_pe(p)
    print(cfg, res)
