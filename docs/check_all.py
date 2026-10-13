import sys, os, time, shutil, json, threading
import xml.etree.ElementTree as ET
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent / 'QA-Tactical-Engine/ENGINE02-20261002'
sys.path.append(str(ROOT))
import helpers as h

DEV_SCRATCH = pathlib.Path(r'C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch')
DEV_FIX = DEV_SCRATCH / 'Harden_Manifest/Saves/EngineComplexFixture.rws'
DEV_CONFIG = DEV_SCRATCH / 'Harden_Manifest/Config/ModsConfig.xml'

RESULTS = {}

def log(key, val):
    RESULTS[key] = val
    print(f"[{key}] {val}", flush=True)

def verify_fixture(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ids = []
    for thing in root.iter('thing'):
        i = thing.find('id')
        if i is not None and i.text: ids.append(i.text)
        
    id_counts = Counter(ids)
    dup_ids = [k for k, v in id_counts.items() if v > 1]
    
    found = {
        'weapon': False,
        'apparel': False,
        'inventory': False,
        'hediff': False,
        'installed_part': False,
        'bed_assignment': False,
        'animal_master': False,
        'nonempty_bill': False,
        'storedPower': False,
        'real_crop': False,
        'corpse_container': False
    }
    
    # We must check that the tags are not empty (have children or text)
    for e in root.iter('equipment'):
        if list(e): found['weapon'] = True
    for e in root.iter('wornApparel'):
        for li in e.iter('li'): found['apparel'] = True
    for e in root.iter('inventory'):
        for li in e.iter('li'): found['inventory'] = True
    for e in root.iter('hediffs'):
        for li in e.iter('li'):
            found['hediff'] = True
            if li.get('Class') == 'Hediff_AddedPart': found['installed_part'] = True
    
    for e in root.iter('assignedPawns'):
        if list(e): found['bed_assignment'] = True
    for e in root.iter('master'):
        if e.text and e.text != 'null': found['animal_master'] = True
    for e in root.iter('bills'):
        if list(e): found['nonempty_bill'] = True
    for e in root.iter('storedPower'):
        if e.text: found['storedPower'] = True
    for e in root.iter('growth'):
        if e.text: found['real_crop'] = True
    
    for e in root.iter('innerContainer'):
        for li in e.iter('li'):
            if li.findtext('def') == 'Corpse_Human': found['corpse_container'] = True
            
    return dup_ids, found

def mutate_and_check(base_path, test_name, mutator_func):
    mutated = ROOT / f'Mutated_{test_name}.rws'
    shutil.copy(base_path, mutated)
    tree = ET.parse(mutated)
    mutator_func(tree.getroot())
    tree.write(mutated, encoding='utf-8', xml_declaration=True)
    _, found = verify_fixture(mutated)
    
    pass_map = {
        'apparel': not found['apparel'],
        'inventory': not found['inventory'],
        'weapon': not found['weapon'],
        'hediff': not found['hediff'],
        'bed': not found['bed_assignment'],
        'master': not found['animal_master'],
        'bill': not found['nonempty_bill'],
        'power': not found['storedPower'],
        'crop': not found['real_crop'],
        'corpse': not found['corpse_container']
    }
    
    log(f'mutated_{test_name}_oracle', pass_map.get(test_name, False))

def track5_oracle():
    def m_apparel(r):
        for e in r.iter('wornApparel'): e.clear()
    def m_inventory(r):
        for e in r.iter('inventory'): e.clear()
    def m_weapon(r):
        for e in r.iter('equipment'): e.clear()
    def m_hediff(r):
        for e in r.iter('hediffs'): e.clear()
    def m_bed(r):
        for e in r.iter('assignedPawns'): e.clear()
    def m_master(r):
        for e in r.iter('master'): e.text = 'null'
    def m_bill(r):
        for e in r.iter('bills'): e.clear()
    def m_power(r):
        for e in r.iter('storedPower'): e.clear()
    def m_crop(r):
        for e in r.iter('growth'): e.clear()
    def m_corpse(r):
        for e in r.iter('innerContainer'):
            for il in list(e):
                for li in list(il):
                    if li.findtext('def') == 'Corpse_Human':
                        il.remove(li)

    mutate_and_check(DEV_FIX, 'apparel', m_apparel)
    mutate_and_check(DEV_FIX, 'inventory', m_inventory)
    mutate_and_check(DEV_FIX, 'weapon', m_weapon)
    mutate_and_check(DEV_FIX, 'hediff', m_hediff)
    mutate_and_check(DEV_FIX, 'bed', m_bed)
    mutate_and_check(DEV_FIX, 'master', m_master)
    mutate_and_check(DEV_FIX, 'bill', m_bill)
    mutate_and_check(DEV_FIX, 'power', m_power)
    mutate_and_check(DEV_FIX, 'crop', m_crop)
    mutate_and_check(DEV_FIX, 'corpse', m_corpse)

def get_xml_element_string(path, tag_name):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        el = root.find(f".//{tag_name}")
        if el is not None:
            return ET.tostring(el, encoding='unicode')
    except: pass
    return ""

def run_tests():
    # --- Check 4 & 5 ---
    dup_ids, found = verify_fixture(DEV_FIX)
    log('check4_fixture_trust', {
        'duplicates_ids': len(dup_ids),
        'found_dimensions': found
    })
    track5_oracle()
    
    # Setup Worker
    p = h.prepare("HardenTest", DEV_FIX)
    shutil.copy2(DEV_CONFIG, p / 'Config/ModsConfig.xml')
    
    # Create bad save for Check 1
    bad_save = p / "Saves" / "BadSave.rws"
    shutil.copy2(DEV_FIX, bad_save)
    tree = ET.parse(bad_save)
    mods = tree.getroot().find('meta/modIds')
    if mods is not None: ET.SubElement(mods, 'li').text = 'qa.actually.missing.dependency'
    tree.write(bad_save, encoding='utf-8', xml_declaration=True)
    
    import subprocess
    args = [str(h.EXE), "-batchmode", f"-savedatafolder={p}", f"-logfile={p/'player.log'}", "-bridgeport=29600"]
    si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = 0
    p_proc = subprocess.Popen(args, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(ROOT))
    h.owned.append(p_proc)
    
    b = None
    for _ in range(180):
        try:
            b = h.Bridge(29600)
            b.send("HELLO")
            break
        except Exception: time.sleep(0.5)

    # --- Check 1: Manifest / LOAD Boundary ---
    # We do NOT call VALIDATE_MANIFEST
    res_bad = b.send("LOAD_SAVE BadSave")
    time.sleep(2)
    st_bad = b.send("STATUS")
    res_export = "no_export_attempted"
    if "LOAD_FAILED" in st_bad:
        try:
            res_export = b.send("EXPORT_SAVE ExportBad")
        except Exception as e: res_export = str(e)
        
    log('check1_bad_save', {
        'load_response': res_bad,
        'status': st_bad,
        'export_response': res_export
    })
    
    # Check 6: Load-Time Fence
    res_good = b.send("LOAD_SAVE Input")
    st_good = []
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = b.send("STATUS")
        st_good.append(st)
        if "READY" in st: break
        time.sleep(0.05)
        
    log('check6_load_fence', {
        'response': res_good,
        'states': list(set(st_good)) # Just to see unique states
    })
    
    # --- Check 2: Global / World Dispatch Regression ---
    b.send("EXPORT_SAVE Before")
    b.send("STEP_TICKS 1000 20")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 10:
        st = b.send("STATUS")
        if "RemainingStep=0" in st: break
        time.sleep(0.1)
    b.send("EXPORT_SAVE After")
    
    time.sleep(2) # ensure file writes
    before_path = p / "Saves/Before.rws"
    after_path = p / "Saves/After.rws"
    
    diffs = {}
    for tag in ['world', 'history', 'components', 'game']:
        before_xml = get_xml_element_string(before_path, tag)
        after_xml = get_xml_element_string(after_path, tag)
        diffs[tag] = "MATCH" if before_xml == after_xml else "MISMATCH"
        
    log('check2_global_dispatch', diffs)
    
    # --- Check 3: Unsafe Tick Path ---
    try: res_run = b.send("RUN_TICKS 50000")
    except Exception as e: res_run = str(e)
    try: res_step_huge = b.send("STEP_TICKS 1000 50000")
    except Exception as e: res_step_huge = str(e)
    
    b_starve = h.Bridge(29600)
    b.send("STEP_TICKS 5000 20") # Non-blocking on main thread, but keeps worker busy
    
    # Try concurrent STATUS
    time.sleep(0.2)
    t_status_start = time.monotonic()
    st_starve = b_starve.send("STATUS")
    latency = time.monotonic() - t_status_start
    
    b_starve.send("CANCEL_SIMULATION")
    time.sleep(0.2)
    st_after_cancel = b_starve.send("STATUS")
    b_starve.close()
    
    log('check3_unsafe_path', {
        'run_50000': res_run,
        'step_huge': res_step_huge,
        'concurrent_status_latency_ms': latency * 1000,
        'after_cancel': st_after_cancel
    })
    
    # --- Check 7: Start Debt ---
    b.send("EXPORT_SAVE DebtPrep")
    b.send("START_SIMULATION 60")
    debt_samples = []
    t0 = time.monotonic()
    while time.monotonic() - t0 < 0.5:
        st = b.send("STATUS")
        # Parse TicksGame=XYZ
        import re
        m = re.search(r'TicksGame=(\d+)', st)
        if m: debt_samples.append(int(m.group(1)))
        time.sleep(0.01)
    b.send("PAUSE_SIMULATION")
    
    increments = []
    for i in range(1, len(debt_samples)):
        inc = debt_samples[i] - debt_samples[i-1]
        if inc > 0: increments.append(inc)
        
    log('check7_start_debt', increments)
    
    h.shutdown(p_proc, b, p)

    with open(ROOT / 'check_all_results.json', 'w') as f:
        json.dump(RESULTS, f, indent=2)
    print("All Checks Complete")

if __name__ == '__main__':
    run_tests()
