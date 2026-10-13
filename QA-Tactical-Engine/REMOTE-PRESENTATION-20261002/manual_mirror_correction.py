from harness import *
import copy, harness

session = Path(json.loads((ROOT / 'current-manual-session.json').read_text(encoding='utf-8-sig'))['path'])
harness.ROOT = session
before = send(31701, 'SNAP')
live = ET.fromstring(before['response'])
selected = live.find("pawn[@id='Human302']")
if live.get('map') != '0' or selected is None or selected.get('selected') != 'true':
    raise RuntimeError('Required own Pawn is not selected on fixture map 0')
canonical = worker(cmd('GET_SNAPSHOT', Generation=1))
bad = copy.deepcopy(canonical['parsed'])
target = next(p for p in bad['Snapshot']['Pawns'] if p['PawnId'] == 'Human302')
target['PosX'] += 4
def reconcile(response):
    return send(31701, 'RECONCILE ' + base64.b64encode(json.dumps(response).encode()).decode())
write('selected-mirror-before.json', before)
write('selected-mirror-canonical-before.json', canonical)
write('selected-mirror-perturbed.json', reconcile(bad))
time.sleep(5)
restored = worker(cmd('GET_SNAPSHOT', Generation=1))
write('selected-mirror-restored.json', reconcile(restored['parsed']))
time.sleep(2)
after = send(31701, 'SNAP')
write('selected-mirror-after.json', after)
write('selected-mirror-worker-after.json', worker(cmd('GET_SNAPSHOT', Generation=1)))
r = ET.fromstring(after['response'])
print(json.dumps({'pawn': r.find("pawn[@id='Human302']").attrib,
                 'grid': r.find("grid[@pawn='Human302']").attrib,
                 'duplicates': r.get('duplicateSpawnedThingIds'),
                 'drawCalls': r.get('drawCalls'), 'guiCalls': r.get('guiCalls')}, indent=2))
