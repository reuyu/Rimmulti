import xml.etree.ElementTree as ET
import pathlib

file_path = r'C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch\OriginalSave\POC_TAC_ENGINE_02_MultiMap_Complex.rws'
tree = ET.parse(file_path)
root = tree.getroot()

print("Parsed successfully.")
found = {
    'Thing/load IDs': False,
    'Verb IDs': False,
    'Hediff/body part': False,
    'animal master': False,
    'real crop': False,
    'nonempty bill': False,
    'real storedPower': False,
    'nested container': False,
    'corpse/holder': False
}

for e in root.iter():
    if e.tag == 'id' and e.text:
        found['Thing/load IDs'] = True
    if e.tag == 'loadID' and e.text and 'Verb' in e.text:
        found['Verb IDs'] = True
    if e.tag == 'hediffs' and len(e) > 0:
        found['Hediff/body part'] = True
    if e.tag == 'master' and e.text:
        found['animal master'] = True
    if e.tag == 'def' and 'Plant' in e.text:
        found['real crop'] = True
    if e.tag == 'bills' and len(list(e)) > 0:
        found['nonempty bill'] = True
    if e.tag == 'storedPower' and e.text:
        found['real storedPower'] = True
    if e.tag == 'innerContainer' and len(list(e)) > 0:
        found['nested container'] = True
    if e.tag == 'def' and 'Corpse' in e.text:
        found['corpse/holder'] = True

for k, v in found.items():
    print(f"{k}: {v}")
