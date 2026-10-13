"""Read-only recovery inventory; does not build or execute production/game code."""
from pathlib import Path
import hashlib, json, struct, uuid, datetime

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest().upper()

def mvid(p):
    # ECMA-335 Module table Mvid index, read as bytes; no assembly loading.
    b = p.read_bytes()
    u16 = lambda n: struct.unpack_from('<H', b, n)[0]
    u32 = lambda n: struct.unpack_from('<I', b, n)[0]
    pe = u32(0x3c); opt = pe + 24
    dirs = opt + (112 if u16(opt) == 0x20b else 96)
    sections = opt + u16(pe + 20)
    def offset(rva):
        for i in range(u16(pe + 6)):
            s = sections + 40 * i
            if u32(s + 12) <= rva < u32(s + 12) + max(u32(s + 8), u32(s + 16)):
                return rva - u32(s + 12) + u32(s + 20)
        raise ValueError('unmapped RVA')
    cli = offset(u32(dirs + 14 * 8)); md = offset(u32(cli + 8))
    pos = md + 16 + u32(md + 12); pos = (pos + 3) & ~3
    count = u16(pos + 2); pos += 4; streams = {}
    for _ in range(count):
        start, size = u32(pos), u32(pos + 4); end = b.index(0, pos + 8)
        name = b[pos + 8:end].decode('ascii'); streams[name] = md + start
        pos = (end + 4) & ~3
    t = streams.get('#~', streams.get('#-'))
    heap = b[t + 6]; valid = struct.unpack_from('<Q', b, t + 8)[0]
    row = t + 24 + 4 * valid.bit_count()
    string_width = 4 if heap & 1 else 2; guid_width = 4 if heap & 2 else 2
    idx = int.from_bytes(b[row + 2 + string_width:row + 2 + string_width + guid_width], 'little')
    return str(uuid.UUID(bytes_le=b[streams['#GUID'] + (idx - 1) * 16:streams['#GUID'] + idx * 16]))

def check(path, expected=None, expected_mvid=None):
    p = Path(path)
    if not p.is_absolute(): p = ROOT / p
    item = {'path': str(p), 'exists': p.is_file()}
    if not p.is_file(): item['status'] = 'MISSING'; return item
    item.update(bytes=p.stat().st_size, sha256=sha(p))
    if expected: item.update(expected_sha256=expected.upper(), status='MATCHED' if item['sha256'] == expected.upper() else 'CHANGED')
    else: item['status'] = 'OBSERVED_NO_PRIOR_HASH'
    if p.suffix.lower() == '.dll':
        try: item['mvid'] = mvid(p)
        except Exception as e: item['metadata_error'] = str(e)
    if expected_mvid: item.update(expected_mvid=expected_mvid, mvid_match=item.get('mvid') == expected_mvid)
    return item

def compare_inventory(base, inv):
    return [check(base / k, v['sha256']) for k, v in inv.items()]

def summary(rows):
    return {k: sum(r['status'] == k for r in rows) for k in sorted({r['status'] for r in rows})}

manifest = json.loads((ROOT / 'docs/RELEASE_MANIFEST_PIPELINE_REV5.json').read_text(encoding='utf-8-sig'))
pipeline = []
for group in ['BinaryArtifacts', 'ModifiedSourceFiles']:
    for value in manifest[group].values(): pipeline.append(check(value['RelativePath'], value['Sha256'], value.get('Mvid')))
v = manifest['E1Results']; pipeline.append(check(v['RelativePath'], v['Sha256']))
pipeline.append(check('docs/RELEASE_MANIFEST_PIPELINE_REV5.json', 'D609795D8B50ED98850B8C73E951EA7F8E9B21B6193E815CF4890B9E2BB7D9E6'))

qa = ROOT / 'QA-Transaction-Pipeline/PIPELINE01-REV5-20261006'
qa_inventory = compare_inventory(qa, json.loads((qa / 'qa-evidence-manifest.json').read_text(encoding='utf-8-sig')))
prior_freeze = json.loads((qa / 'freeze-after.json').read_text(encoding='utf-8-sig'))
freeze = compare_inventory(ROOT, prior_freeze)
for r in freeze:
    if r['status'] == 'MISSING':
        relocated = ROOT / 'docs' / Path(r['path']).name
        if relocated.exists(): r['relocated_document'] = check(relocated, r['expected_sha256'])

engine_results = ROOT / 'scratch/semantic_authority_gate_05_results.json'
engine = [check(engine_results, 'BE2C130AF5952CAE6370B02008E1905EAE060A6E0F89531BC50A2098495449A5'),
          check('scratch/run_semantic_authority_gate_05.py', '019CFB698EE54CF3AE92F6423C3FFBA46CE92FFD433604313B011D2503554DFD')]
e1 = json.loads(engine_results.read_text(encoding='utf-8-sig'))
for group in ['binaries', 'sourceFiles', 'fixtures']:
    for v in e1['provenance'][group].values(): engine.append(check(v['path'], v['sha256'], v.get('mvid')))
for p in [ROOT / 'scratch/WorkerBridgeMod/1.6/Assemblies', ROOT / 'scratch/WorkerBridgeMod/Source/bin/Release/net472', ROOT / 'scratch']:
    engine.append(check(p / 'WarEconomy.WorkerBridge.PoC.dll', '2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C', '12bb9237-1b3e-4b20-89a7-69ad729861e1'))
    if (p / 'WarEconomy.WorkerBridge.PoC.pdb').exists(): engine.append(check(p / 'WarEconomy.WorkerBridge.PoC.pdb'))

package = []
for v in json.loads((PKG / 'PACKAGE_MANIFEST.json').read_text(encoding='utf-8-sig'))['files']:
    row = check(PKG / v['path'], v['sha256'])
    if row['status'] == 'MISSING' and v['path'] == 'AGENTS.md': row['root_installation'] = check(ROOT / 'AGENTS.md', v['sha256'])
    package.append(row)
governance = [check(p) for p in sorted((ROOT / 'docs').glob('*.md')) if any(s in p.name for s in ['MASTER_', 'QA_DEFECT_', '요구사항', 'ADR-007'])]
report_pairs = []
for p in sorted((PKG / 'source_reports').glob('*.md')):
    local = ROOT / 'docs' / p.name.replace('(2)', '')
    report_pairs.append({'package': check(p), 'local': check(local, sha(p))})
identity = {'verified_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
            'root': str(ROOT), 'method': 'read-only SHA256/ECMA335 metadata/inventory; no runtime gate re-execution',
            'pipeline': pipeline, 'qa_inventory': qa_inventory, 'prior_production_freeze': freeze,
            'engine': engine, 'package_premerge': package, 'governance': governance, 'report_pairs': report_pairs,
            'summary': {k: summary(v) for k, v in [('pipeline', pipeline), ('qa_inventory', qa_inventory), ('prior_production_freeze', freeze), ('engine', engine), ('package_premerge', package)]}}
(OUT / 'local_identity_verification.json').write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(identity['summary'], ensure_ascii=False, indent=2))
for k in ['pipeline', 'qa_inventory', 'prior_production_freeze', 'engine', 'package_premerge']:
    for r in identity[k]:
        if r['status'] in ['MISSING', 'CHANGED']: print(k, json.dumps(r, ensure_ascii=False))
