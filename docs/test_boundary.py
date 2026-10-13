import sys, os, time, shutil, json
import xml.etree.ElementTree as ET
import pathlib

# Setup paths
ROOT = pathlib.Path(__file__).resolve().parent / 'QA-Tactical-Engine/ENGINE02-20261002'
sys.path.append(str(ROOT))
import helpers as h

FIXTURE_PATH = ROOT / 'BoundaryFixture.rws'
RESULTS = {}

def log(key, val):
    RESULTS[key] = val
    print(f"[{key}] {val}", flush=True)

def verify_oracle(path):
    tree = ET.parse(path)
    root = tree.getroot()
    found = {
        'apparel': False,
        'inventory': False,
        'building_health': False,
        'assignment_master': False,
        'nested_holder': False,
        'quantity': False,
        'identity': False,
        'real_crop': False,
        'nonempty_bill': False,
        'real_storedPower': False
    }
    for e in root.iter('thing'):
        d = e.find('def')
        if d is not None:
            if d.text == 'TableSculpting' and e.find('billStack/bills/li') is not None:
                found['nonempty_bill'] = True
            if d.text == 'Battery' and e.find('storedPower') is not None and e.findtext('storedPower') == '314.15':
                found['real_storedPower'] = True
            if d.text == 'Plant_Potato' or (d.text and 'Plant' in d.text):
                found['real_crop'] = True
            if d.text == 'Human':
                if e.find('id') is not None: found['identity'] = True
                if e.find('apparel/wornApparel/li') is not None: found['apparel'] = True
                if e.find('inventory/innerContainer/li') is not None: found['inventory'] = True
            if d.text == 'Wolf_Timber' or d.text == 'Dog':
                if e.find('master') is not None: found['assignment_master'] = True
            if e.find('health') is not None and e.findtext('health') == '100':
                found['building_health'] = True
            if e.find('innerContainer/li') is not None:
                found['nested_holder'] = True
            if e.find('stackCount') is not None and int(e.findtext('stackCount', '0')) > 1:
                found['quantity'] = True
    
    # if anything missing, return false, plus what is missing
    missing = [k for k, v in found.items() if not v]
    if missing:
        return False, missing
    return True, []

def mutate_and_check(base_path, test_name, mutator_func):
    mutated = ROOT / f'Mutated_{test_name}.rws'
    shutil.copy(base_path, mutated)
    tree = ET.parse(mutated)
    mutator_func(tree.getroot())
    tree.write(mutated, encoding='utf-8', xml_declaration=True)
    
    passed, missing = verify_oracle(mutated)
    log(f'mutated_{test_name}_oracle', not passed)
    return not passed

def track2_fail_by_mutation(exported_path):
    def m_apparel(r):
        for e in r.iter('wornApparel'): e.clear()
    def m_inventory(r):
        for e in r.iter('inventory'):
            ic = e.find('innerContainer')
            if ic is not None: ic.clear()
    def m_building(r):
        for e in r.iter('health'): e.text = '999'
    def m_assignment(r):
        for e in r.iter('master'): e.text = 'null'
    def m_nested(r):
        for e in r.iter('innerContainer'): e.clear()
    def m_quantity(r):
        for e in r.iter('stackCount'): e.text = '1'
    def m_identity(r):
        for e in r.iter('id'): e.text = 'CorruptedID_123'

    mutate_and_check(exported_path, 'apparel', m_apparel)
    mutate_and_check(exported_path, 'inventory', m_inventory)
    mutate_and_check(exported_path, 'building', m_building)
    mutate_and_check(exported_path, 'assignment', m_assignment)
    mutate_and_check(exported_path, 'nested', m_nested)
    mutate_and_check(exported_path, 'quantity', m_quantity)
    mutate_and_check(exported_path, 'identity', m_identity)

def run_tests():
    # Track 1 & 5
    p = h.prepare("BoundaryQA", FIXTURE_PATH)
    p_proc, b = h.launch(p, 29400)
    
    t0 = time.monotonic()
    resp_load = b.send("LOAD_SAVE Input")
    states = []
    t_start = time.monotonic()
    playing_time = None
    ready_time = None
    fence_time = None
    
    while time.monotonic() - t_start < 60:
        st = b.send("STATUS")
        states.append(st)
        if "Playing" in st and playing_time is None:
            playing_time = time.monotonic() - t0
        if "Fence" in st and fence_time is None:
            fence_time = time.monotonic() - t0
        if "READY" in st:
            ready_time = time.monotonic() - t0
            break
        time.sleep(0.3)
    
    log('track5_load_boundary', {
        'before_load': 0,
        'first_playing': round(playing_time * 1000, 1) if playing_time else None,
        'fence_activation': round(fence_time * 1000, 1) if fence_time else None,
        'ready': round(ready_time * 1000, 1) if ready_time else None,
        'states': states
    })
    
    # Export for Track 1/2
    b.send("EXPORT_SAVE BoundaryExport")
    export_path = p / "Saves" / "BoundaryExport.rws"
    
    # Give some time for file write
    time.sleep(2)
    passed, missing = verify_oracle(export_path)
    log('track1_fixture_trust', {'passed': passed, 'missing': missing})
    
    # Track 2
    track2_fail_by_mutation(export_path)
    
    # Track 4 Execution Bounds
    # large RUN-equivalent request
    t_start = time.monotonic()
    b.send("RUN_TICKS 10000")
    log('track4_large_run', round((time.monotonic() - t_start)*1000, 1))
    
    # queue flood
    b.send("PAUSE_SIMULATION")
    q_start = time.monotonic()
    for _ in range(50):
        b.send("STATUS")
    log('track4_queue_flood_ms', round((time.monotonic() - q_start)*1000, 1))
    
    # stale queued request
    b.send("LOAD_SAVE StaleQueuedRequest") # Should fail but be handled
    
    h.shutdown(p_proc, b, p)

    # Track 3 Dependency Negatives
    # Missing Mod package
    p2 = h.prepare("Negatives", FIXTURE_PATH)
    p2_proc, b2 = h.launch(p2, 29401)
    # We alter the save to have a missing mod
    neg_path = p2 / "Saves" / "Input.rws"
    tree = ET.parse(neg_path)
    r = tree.getroot()
    # add fake mod
    mods = r.find('meta/modIds')
    if mods is not None:
        ET.SubElement(mods, 'li').text = 'qa.missing.mod'
    # missing thing def
    for e in r.iter('def'):
        if e.text == 'TableSculpting': e.text = 'QA_MissingThingDef'
    tree.write(neg_path, encoding='utf-8', xml_declaration=True)
    
    res = b2.send("LOAD_SAVE Input")
    st2 = []
    t_start = time.monotonic()
    while time.monotonic() - t_start < 20:
        st = b2.send("STATUS")
        st2.append(st)
        if "FAILED" in st or "READY" in st: break
        time.sleep(0.5)
        
    log('track3_dependency_negatives', {
        'response': res,
        'states': st2,
        'reached_ready': any('READY' in s for s in st2)
    })
    h.shutdown(p2_proc, b2, p2)

    with open('test_boundary_results.json', 'w') as f:
        json.dump(RESULTS, f, indent=2)
    print("Done")

if __name__ == '__main__':
    run_tests()
