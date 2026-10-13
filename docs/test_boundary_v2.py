import sys, os, time, shutil, json, threading
import xml.etree.ElementTree as ET
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent / 'QA-Tactical-Engine/ENGINE02-20261002'
sys.path.append(str(ROOT))
import helpers as h

# Use the baseline fixture that exists
FIXTURE_PATH = ROOT / 'OriginalSave/POC_TAC_ENGINE_02_MultiMap_Complex.rws'
if not FIXTURE_PATH.exists():
    FIXTURE_PATH = h.SCRATCH / 'OriginalSave/POC_TAC_ENGINE_02_MultiMap_Complex.rws'

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
        'nested_holder': False,
        'quantity': False,
        'identity': False,
    }
    
    if list(root.iter('wornApparel')):
        for e in root.iter('wornApparel'):
            if list(e.iter('li')): found['apparel'] = True
            
    if list(root.iter('inventory')):
        for e in root.iter('inventory'):
            if list(e.iter('li')): found['inventory'] = True
            
    if list(root.iter('innerContainer')):
        for e in root.iter('innerContainer'):
            if list(e.iter('li')): found['nested_holder'] = True

    for e in root.iter('thing'):
        if e.find('health') is not None and e.findtext('health') == '100':
            found['building_health'] = True
        if e.find('stackCount') is not None and int(e.findtext('stackCount', '0')) > 1:
            found['quantity'] = True
        if e.find('id') is not None:
            found['identity'] = True
                
    missing = [k for k, v in found.items() if not v]
    return not missing, missing

def mutate_and_check(base_path, test_name, mutator_func):
    mutated = ROOT / f'Mutated_{test_name}.rws'
    shutil.copy(base_path, mutated)
    tree = ET.parse(mutated)
    mutator_func(tree.getroot())
    tree.write(mutated, encoding='utf-8', xml_declaration=True)
    
    passed, missing = verify_oracle(mutated)
    log(f'mutated_{test_name}_oracle', not passed) # True means it correctly detected failure

def track2_fail_by_mutation(exported_path):
    def m_apparel(r):
        for e in r.iter('wornApparel'): e.clear()
    def m_inventory(r):
        for e in r.iter('inventory'):
            ic = e.find('innerContainer')
            if ic is not None: ic.clear()
    def m_building(r):
        for e in r.iter('health'): e.text = '999'
    def m_nested(r):
        for e in r.iter('innerContainer'): e.clear()
    def m_quantity(r):
        for e in r.iter('stackCount'): e.text = '1'
    def m_identity(r):
        for e in r.iter('id'): e.text = 'CorruptedID_123'

    mutate_and_check(exported_path, 'apparel', m_apparel)
    mutate_and_check(exported_path, 'inventory', m_inventory)
    mutate_and_check(exported_path, 'building', m_building)
    mutate_and_check(exported_path, 'nested', m_nested)
    mutate_and_check(exported_path, 'quantity', m_quantity)
    mutate_and_check(exported_path, 'identity', m_identity)

def setup_profile(name):
    # helpers.prepare creates a profile dir and copies save
    return h.prepare(name, FIXTURE_PATH)

def run_tests():
    # --- Track 5: Load Boundary ---
    p = setup_profile("BoundaryQA_V2")
    # Need to add probe mod to profile
    cfg = ET.parse(p / 'Config/ModsConfig.xml')
    mods = cfg.getroot().find('activeMods')
    if mods is not None:
        ET.SubElement(mods, 'li').text = 'qacodex.engine02.probe'
        cfg.write(p / 'Config/ModsConfig.xml', encoding='utf-8', xml_declaration=True)

    port_engine = 29500
    port_probe = 30500
    
    # We must start the engine via subprocess directly if helpers.launch waits for HELLO blockingly
    # Actually, helpers.launch waits for HELLO then returns the process and bridge. We can use it.
    import subprocess
    args = [str(h.EXE), "-batchmode", f"-savedatafolder={p}", f"-logfile={p/'player.log'}", f"-bridgeport={port_engine}", f"-qaport={port_probe}"]
    si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = 0
    p_proc = subprocess.Popen(args, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(ROOT))
    h.owned.append(p_proc)
    
    # Wait for bridge
    b = None
    for _ in range(180):
        if p_proc.poll() is not None: raise RuntimeError("Worker exited")
        try:
            b = h.Bridge(port_engine)
            b.send("HELLO")
            break
        except Exception:
            time.sleep(0.5)
            
    # Probe bridge
    probe_b = None
    for _ in range(60):
        try:
            probe_b = h.Bridge(port_probe)
            break
        except Exception:
            time.sleep(0.5)

    # Begin Load Boundary Test
    states_captured = []
    
    def poll_status():
        t0 = time.monotonic()
        while time.monotonic() - t0 < 30:
            try:
                st = b.send("STATUS")
                sn = probe_b.send("SNAP") if probe_b else ""
                states_captured.append({
                    "time_ms": round((time.monotonic() - t0) * 1000, 1),
                    "status": st,
                    "snap": sn
                })
                if "READY" in st: break
            except Exception: pass
            time.sleep(0.05)

    poller = threading.Thread(target=poll_status)
    poller.start()
    
    time.sleep(0.1) # ensure poller starts
    b.send("LOAD_SAVE Input")
    poller.join()
    
    log('track5_load_boundary', states_captured)

    # --- Track 1: Export ---
    b.send("EXPORT_SAVE BoundaryExport")
    export_path = p / "Saves" / "BoundaryExport.rws"
    time.sleep(2)
    
    # --- Track 2: Oracle ---
    track2_fail_by_mutation(export_path)

    # --- Track 4: Execution Bounds (Starvation) ---
    b_starve = h.Bridge(port_engine)
    starve_log = []
    def long_run():
        t_issue = time.monotonic()
        try:
            b.send("RUN_TICKS 50000") # Connection A blocking
        except Exception as e:
            pass
        starve_log.append({"event": "RUN_COMPLETE", "duration": time.monotonic() - t_issue})
        
    t_run = threading.Thread(target=long_run)
    t_run.start()
    
    time.sleep(0.5)
    t_issue_b = time.monotonic()
    try:
        st = b_starve.send("STATUS") # Connection B checking
        starve_log.append({"event": "STATUS_RESPONSE", "delay": time.monotonic() - t_issue_b, "state": st})
    except Exception as e:
        starve_log.append({"event": "STATUS_ERROR", "delay": time.monotonic() - t_issue_b, "error": str(e)})

    t_run.join()
    
    # Oversized slice test
    t_slice = time.monotonic()
    b.send("STEP_TICKS 1000 10000")
    starve_log.append({"event": "OVERSIZED_SLICE_DURATION", "duration": time.monotonic() - t_slice})

    log('track4_execution_bounds', starve_log)
    
    b_starve.close()
    if probe_b: probe_b.close()
    h.shutdown(p_proc, b, p)

    # --- Track 3: Dependency Negatives ---
    p2 = setup_profile("Negatives_V2")
    args2 = [str(h.EXE), "-batchmode", f"-savedatafolder={p2}", f"-logfile={p2/'player.log'}", f"-bridgeport=29501"]
    p2_proc = subprocess.Popen(args2, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(ROOT))
    h.owned.append(p2_proc)
    
    b2 = None
    for _ in range(180):
        try:
            b2 = h.Bridge(29501)
            b2.send("HELLO")
            break
        except: time.sleep(0.5)

    neg_path = p2 / "Saves" / "Input.rws"
    tree = ET.parse(neg_path)
    r = tree.getroot()
    mods = r.find('meta/modIds')
    if mods is not None:
        ET.SubElement(mods, 'li').text = 'qa.missing.mod.critical'
    for e in r.iter('def'):
        if e.text == 'TableSculpting': e.text = 'QA_MissingThingDef'
    tree.write(neg_path, encoding='utf-8', xml_declaration=True)

    b2.send("LOAD_SAVE Input")
    neg_states = []
    t_neg = time.monotonic()
    reached_ready = False
    while time.monotonic() - t_neg < 20:
        st = b2.send("STATUS")
        neg_states.append(st)
        if "READY" in st:
            reached_ready = True
            break
        if "FAILED" in st:
            break
        time.sleep(0.3)
        
    log('track3_dependency_negatives', {
        'reached_ready': reached_ready,
        'states': neg_states
    })
    
    h.shutdown(p2_proc, b2, p2)

    with open(ROOT / 'test_boundary_v2_results.json', 'w') as f:
        json.dump(RESULTS, f, indent=2)
    print("Done")

if __name__ == '__main__':
    run_tests()
