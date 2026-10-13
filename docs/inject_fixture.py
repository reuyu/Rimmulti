import xml.etree.ElementTree as ET
import pathlib, shutil

ROOT = pathlib.Path(r'c:\Users\user\Desktop\RimMulti')
FIX = r'C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch\OriginalSave\POC_TAC_ENGINE_02_MultiMap_Complex.rws'
OUT = ROOT / 'QA-Tactical-Engine/ENGINE02-20261002/BoundaryFixture.rws'

tree = ET.parse(FIX)
root = tree.getroot()

for thing in root.iter('thing'):
    d = thing.find('def')
    if d is not None and d.text == 'TableSculpting':
        bills = thing.find('billStack/bills')
        if bills is not None:
            li = ET.SubElement(bills, 'li', {'Class': 'Bill_Production'})
            ET.SubElement(li, 'recipe').text = 'Make_SculptureSmall'
            ET.SubElement(li, 'id').text = 'Bill_Production_999'
            ET.SubElement(li, 'suspended').text = 'False'
            # Add a basic filter
            filter = ET.SubElement(li, 'ingredientFilter')
            ET.SubElement(filter, 'disallowedThingDefs')
    
    if d is not None and d.text == 'Battery':
        ET.SubElement(thing, 'storedPower').text = '314.15'

tree.write(OUT, encoding='utf-8', xml_declaration=True)
print(f"Created {OUT}")
