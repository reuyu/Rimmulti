import json, re

with open('scratch/settlement_roundtrip_results.json') as f:
    d = json.load(f)

for step_name in ['Step6_CensusCompare', 'Step10_CensusReferenceCompare']:
    step_errors = d['phases']['Phase2_RoundTrip'][step_name]['errors']
    defs = {}
    other = []
    for e in step_errors:
        m = re.search(r"'([A-Za-z_]+)\d+'", e)
        if m:
            dname = m.group(1)
            defs[dname] = defs.get(dname, 0) + 1
        else:
            other.append(e)

    print(f"=== {step_name} ({len(step_errors)} items) ===")
    for k, v in sorted(defs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {v}")
    if other:
        print(f"  Other: {len(other)}: {other[:5]}")
