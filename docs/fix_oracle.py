import xml.etree.ElementTree as ET
import sys

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
    
    # Check general properties across all things
    if list(root.iter('wornApparel')):
        for e in root.iter('wornApparel'):
            if list(e.iter('li')): found['apparel'] = True
            
    if list(root.iter('inventory')):
        for e in root.iter('inventory'):
            if list(e.iter('li')): found['inventory'] = True
            
    if list(root.iter('master')):
        for e in root.iter('master'):
            if e.text and e.text != 'null': found['assignment_master'] = True
            
    if list(root.iter('innerContainer')):
        for e in root.iter('innerContainer'):
            if list(e.iter('li')): found['nested_holder'] = True

    for e in root.iter('thing'):
        d = e.find('def')
        if d is not None:
            if d.text == 'TableSculpting' and e.find('billStack/bills/li') is not None:
                found['nonempty_bill'] = True
            if d.text == 'Battery' and e.find('storedPower') is not None:
                found['real_storedPower'] = True
            if d.text == 'Plant_Potato' or (d.text and 'Plant' in d.text):
                found['real_crop'] = True
            if e.find('health') is not None and e.findtext('health') == '100':
                found['building_health'] = True
            if e.find('stackCount') is not None and int(e.findtext('stackCount', '0')) > 1:
                found['quantity'] = True
            if e.find('id') is not None:
                found['identity'] = True
                
    missing = [k for k, v in found.items() if not v]
    return not missing, missing

if __name__ == '__main__':
    path = r'c:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\ENGINE02-20261002\BoundaryQA\Saves\BoundaryExport.rws'
    passed, missing = verify_oracle(path)
    print(f"Passed: {passed}, Missing: {missing}")
