"""QA recovery only: read files/metadata, write QA-owned inventory; no game/build."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import struct
import uuid

ROOT = Path(r"C:\Users\user\Desktop\RimMulti")
PKG = ROOT / "docs/WarEconomy_Master_Handoff_20261006"
OUT = PKG / "coordination"

# Reuse only reviewed byte readers, never the original inventory's top-level writes.
reader = PKG / "bootstrap/verify_local_identity.py"
tree = ast.parse(reader.read_text(encoding="utf-8-sig"))
definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("sha", "mvid")]
exec(compile(ast.Module(body=definitions, type_ignores=[]), str(reader), "exec"))

def metadata_streams(data, base=0):
    u16 = lambda n: struct.unpack_from("<H", data, n)[0]
    u32 = lambda n: struct.unpack_from("<I", data, n)[0]
    assert data[base:base+4] == b"BSJB"
    pos = (base + 16 + u32(base + 12) + 3) & ~3
    count = u16(pos + 2)
    pos += 4
    streams = {}
    for _ in range(count):
        start, size = u32(pos), u32(pos + 4)
        end = data.index(0, pos + 8)
        name = data[pos + 8:end].decode("ascii")
        streams[name] = (base + start, size)
        pos = (end + 4) & ~3
    return streams

def codeview_guid(path):
    b = path.read_bytes()
    u16 = lambda n: struct.unpack_from("<H", b, n)[0]
    u32 = lambda n: struct.unpack_from("<I", b, n)[0]
    pe = u32(0x3c)
    opt = pe + 24
    dirs = opt + (112 if u16(opt) == 0x20b else 96)
    sections = opt + u16(pe + 20)
    def offset(rva):
        for i in range(u16(pe + 6)):
            s = sections + 40*i
            if u32(s+12) <= rva < u32(s+12)+max(u32(s+8), u32(s+16)):
                return rva-u32(s+12)+u32(s+20)
        raise ValueError("unmapped RVA")
    size = u32(dirs + 6*8 + 4)
    debug = offset(u32(dirs + 6*8))
    for pos in range(debug, debug+size, 28):
        if u32(pos+12) == 2:
            raw = u32(pos+24)
            if b[raw:raw+4] == b"RSDS":
                return str(uuid.UUID(bytes_le=b[raw+4:raw+20]))
    raise ValueError("RSDS absent")

def portable_pdb(path):
    b = path.read_bytes()
    streams = metadata_streams(b)
    pdb_base = streams["#Pdb"][0]
    guid = str(uuid.UUID(bytes_le=b[pdb_base:pdb_base+16]))
    tables = streams["#~"][0]
    heap = b[tables+6]
    valid = struct.unpack_from("<Q", b, tables+8)[0]
    pos = tables+24
    counts = {}
    for table in range(64):
        if valid & (1 << table):
            counts[table] = struct.unpack_from("<I", b, pos)[0]
            pos += 4
    assert not any(counts.get(i, 0) for i in range(48)), "unexpected earlier tables"
    blob_width = 4 if heap & 4 else 2
    guid_width = 4 if heap & 2 else 2
    blobs = streams["#Blob"][0]
    guids = streams["#GUID"][0]
    def compressed(buf, off):
        first = buf[off]
        if first < 128:
            return first, off+1
        if first < 192:
            return ((first & 63) << 8) | buf[off+1], off+2
        if first < 224:
            return ((first & 31) << 24) | (buf[off+1] << 16) | (buf[off+2] << 8) | buf[off+3], off+4
        raise ValueError("invalid compressed integer")
    def blob(index):
        length, off = compressed(b, blobs+index)
        return b[off:off+length]
    def index(width):
        nonlocal pos
        value = int.from_bytes(b[pos:pos+width], "little")
        pos += width
        return value
    documents = []
    for _ in range(counts.get(48, 0)):
        name_index = index(blob_width)
        algorithm_index = index(guid_width)
        hash_index = index(blob_width)
        index(guid_width)
        encoded = blob(name_index)
        separator = chr(encoded[0])
        off, pieces = 1, []
        while off < len(encoded):
            part_index, off = compressed(encoded, off)
            pieces.append(blob(part_index).decode("utf-8"))
        name = separator.join(pieces)
        algorithm = str(uuid.UUID(bytes_le=b[guids+(algorithm_index-1)*16:guids+algorithm_index*16]))
        assert algorithm == "8829d00f-11b8-4213-878b-770e8597ac16", "unsupported hash algorithm"
        p = Path(name)
        expected = blob(hash_index).hex().upper()
        actual = sha(p) if p.is_file() else None
        documents.append(dict(path=name, algorithm=algorithm, pdb_hash=expected, actual_sha256=actual, matched=expected==actual))
    return dict(guid=guid, documents=documents)

manifest_path = PKG / "bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
files = []
for name, expected in manifest["files"].items():
    p = Path(name)
    row = dict(path=str(p), exists=p.is_file(), expected_sha256=expected["sha256"], expected_bytes=expected["bytes"])
    if p.is_file():
        row.update(bytes=p.stat().st_size, sha256=sha(p))
        row["status"] = "MATCHED" if row["sha256"]==row["expected_sha256"] and row["bytes"]==row["expected_bytes"] else "CHANGED"
        if p.suffix.lower()==".dll":
            try:
                row["mvid"] = mvid(p)
            except Exception as exc:
                row["metadata_error"] = str(exc)
    else:
        row["status"] = "MISSING"
    files.append(row)

binary = ROOT / "scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll"
pdb = ROOT / "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb"
pdb_info = portable_pdb(pdb)
pdb_info.update(path=str(pdb), sha256=sha(pdb), binary_codeview_guid=codeview_guid(binary))
pdb_info["binary_guid_matched"] = pdb_info["guid"] == pdb_info["binary_codeview_guid"]

report_comparisons = []
for name, expected in [
    ("scratch/run_semantic_authority_gate_05.py", "019CFB698EE54CF3AE92F6423C3FFBA46CE92FFD433604313B011D2503554DFD"),
    ("scratch/semantic_authority_gate_05_results.json", "BE2C130AF5952CAE6370B02008E1905EAE060A6E0F89531BC50A2098495449A5"),
]:
    p = ROOT/name
    actual = sha(p)
    report_comparisons.append(dict(path=str(p), expected_report_sha256=expected, actual_sha256=actual, status="MATCHED" if expected==actual else "CHANGED", interpretation="existing E1 report mismatch; cause not established"))

old_e2_search = []
for base in [ROOT/"QA-Tactical-Engine", ROOT/"docs"]:
    for p in base.rglob("*"):
        if p.is_file() and any(term in str(p).lower() for term in ("semantic-authority05", "semantic-gate05", "gate_05", "gate05")):
            old_e2_search.append(str(p))

result = dict(
    verified_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
    root=str(ROOT), method="read-only SHA256/PE MVID/CodeView and portable PDB document hashes; no assembly execution",
    prior_manifest=str(manifest_path), prior_manifest_sha256=sha(manifest_path),
    files=files, freeze_summary={s:sum(r["status"]==s for r in files) for s in ("MATCHED", "CHANGED", "MISSING")},
    selected_binary=dict(path=str(binary), sha256=sha(binary), mvid=mvid(binary)),
    matching_pdb=pdb_info, e1_report_comparisons=report_comparisons,
    old_e2_search=dict(roots=[str(ROOT/"QA-Tactical-Engine"),str(ROOT/"docs")], matching_paths=old_e2_search, independent_gate05_completed_report_found=False, limitations="path/name based local search; no assertion about unlisted/remote/archived artifacts"),
    runtime_started=False, build_performed=False, production_or_candidate_modified=False,
)
OUT.mkdir(exist_ok=True)
target = OUT / "SOL_RECOVERY_IDENTITY_20261007.json"
target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(dict(inventory=str(target), sha256=sha(target), freeze_summary=result["freeze_summary"], selected_binary=result["selected_binary"], pdb_guid_match=pdb_info["binary_guid_matched"], pdb_documents_matched=sum(d["matched"] for d in pdb_info["documents"]), pdb_documents_total=len(pdb_info["documents"]), report_mismatches=len([r for r in report_comparisons if r["status"]=="CHANGED"])), ensure_ascii=False, indent=2))
