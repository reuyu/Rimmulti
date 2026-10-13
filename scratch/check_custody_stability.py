import json, re

with open('scratch/settlement_roundtrip_results.json') as f:
    d = json.load(f)

natural_defs = {'Granite', 'Slate', 'Limestone', 'Marble', 'Sandstone',
                'MineableSteel', 'MineableSilver', 'MineableJade', 'MineableUranium',
                'MineableComponentsIndustrial', 'ChunkGranite', 'ChunkLimestone', 'ChunkSlate'}

for phase_name, p_data in d['phases'].items():
    print(f'=== PHASE: {phase_name} ===')
    for test_key, test_val in p_data.items():
        if isinstance(test_val, dict) and 'errors' in test_val:
            errs = test_val['errors']
            custody_errs = []
            for e in errs:
                m = re.search(r"'([A-Za-z_]+)\d+'", e)
                if m and m.group(1) in natural_defs:
                    continue
                if 'Filth' in e:
                    continue
                custody_errs.append(e)
            print(f'  {test_key}: Total={len(errs)}, CustodyErrs={len(custody_errs)}')
            if custody_errs:
                for ce in custody_errs[:5]:
                    print('    Custody err:', ce)
