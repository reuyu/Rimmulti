"""QA-only offline audit of captured native observations; does not launch or modify candidate."""
from pathlib import Path
import datetime, hashlib, json, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parent.parent / 'QA_Tactical_Worker_Hardening_Independent_Review.md'
def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest().upper()
def capture(node):
    if node is None:
        return None
    return {'attributes': dict(node.attrib), 'text': (node.text or '').strip()}
def pawn(node):
    if node is None:
        return None
    return {'identity_and_ownership': dict(node.attrib),
            **{tag: sorted([dict(x.attrib) for x in node.findall(tag)], key=lambda x: json.dumps(x, sort_keys=True))
               for tag in ['weapon', 'apparel', 'inventory', 'hediff', 'training']}}
def selected(root):
    m = root.find("map[@index='0']")
    result = {'pawn': pawn(m.find("pawn[@id='Human302']")),
              'animal': pawn(m.find("pawn[@id='LabradorRetriever207367']")),
              'rice': capture(m.find("plant[@id='Plant_Rice207368']")),
              'battery': capture(m.find("building[@id='Battery509102']")),
              'bed': {'state': capture(m.find("building[@id='Bed509104']")),
                      'owners': [x.text for x in m.findall("building[@id='Bed509104']/owner")]},
              'bills': [dict(x.attrib) for x in m.findall("building[@id='TableSculpting509106']/bill")],
              'corpse_containers': []}
    for c in m.findall('building'):
        if 'contained' in c.attrib:
            result['corpse_containers'].append({'container': dict(c.attrib),
                'corpses': [{'id': body.get('id'), 'inner_pawn': pawn(body.find('pawn'))} for body in c.findall('corpse')]})
    result['corpse_containers'].sort(key=lambda x: x['container']['id'])
    return result

roots = {name: ET.parse(ROOT / profile / file).getroot() for name, profile, file in [
    ('ready', 'ValidatedBoundary', 'ready.xml'), ('final_live', 'ValidatedBoundary', 'final-live.xml'),
    ('fresh_reload', 'ValidatedFreshReload', 'reload-live.xml')]}
records = {name: selected(root) for name, root in roots.items()}
original = ET.parse(ROOT/'ValidatedBoundary/Saves/Input.rws').getroot()
source_pawn = next(x for x in original.findall('.//thing') if x.findtext('id') == 'Human302')
input_inventory = [{'id': x.findtext('id'), 'def': x.findtext('def'), 'count': x.findtext('stackCount')}
                   for x in source_pawn.findall('inventory/innerContainer/innerList/li')]
audit = {'scope': 'Selected captured native entities; excludes transient driver/cache normalization. Not a complete graph oracle.',
         'input_inventory': input_inventory, 'records': records,
         'final_to_fresh_reload_equal': {k: records['final_live'][k] == records['fresh_reload'][k] for k in records['final_live']}}
write_json(ROOT/'fixture-live-reload-audit.json', audit)

freeze = read_json(ROOT/'freeze-verification-after.json')
protected = read_json(ROOT/'protected-inputs-after.json')
processes = read_json(ROOT/'all-owned-processes-final.json')
cleanup = read_json(ROOT/'junction-cleanup.json')
controls = read_json(ROOT/'control-results.json')
oracle = read_json(ROOT/'validated-oracle-negative-results.json')
targeted = read_json(ROOT/'targeted-boundary-results.json')
report = REPORT.read_text(encoding='utf-8')

errors = []
links = []
for link in re.findall(r'\]\((C:/[^)]+)\)', report):
    match = re.match(r'^(.*?):(\d+)$', link)
    path = Path(match.group(1) if match else link)
    expected_generated = path.name in ['artifact-manifest.json', 'report-verification.json'] and path.parent == ROOT
    exists = path.is_file() or expected_generated
    line_valid = True
    if match and exists:
        line_valid = int(match.group(2)) <= len(path.read_text(encoding='utf-8-sig').splitlines())
    links.append({'target': link, 'exists_or_generated': exists, 'line_valid': line_valid})
    if not exists or not line_valid:
        errors.append('Invalid report link '+link)
checks = {
    'freeze_7_of_7': len(freeze) == 7 and all(x['Match'] for x in freeze),
    'protected_81_of_81': len(protected) == 81 and all(x['Match'] for x in protected),
    'all_9_owned_process_pids_absent': len(processes) == 9 and all(not x['LiveNow'] and x['LookupMethod']=='Get-Process' for x in processes),
    'observer_junction_removed_target_preserved': not cleanup['LinkStillExists'] and cleanup['TargetPreserved'],
    '45_concurrent_samples_active': len(controls['parallel_status_slice_cancel']['samples']) == 45 and controls['parallel_status_slice_cancel']['all_samples_active'],
    'quarantined_run_zero_effect': controls['run_quarantine']['G_delta'] == controls['run_quarantine']['L_delta'] == 0,
    'exact_negative_oracle_all_effective': all(x['changed_oracle_input'] for x in oracle['negatives'].values()),
    'nine_false_negative_dimensions': sum(x['actual']['all_dimensions_pass'] for k,x in oracle['negatives'].items() if k != 'inventory_omitted_from_predicate') == 9,
    'inventory_false_negative': oracle['negatives']['inventory_omitted_from_predicate']['actual']['all_dimensions_pass'],
    'fresh_recipe_loss_reproduced': targeted['fresh_missing_recipe']['ready'] and targeted['fresh_missing_recipe']['original_bill_count']==1 and targeted['fresh_missing_recipe']['exported_bill_count']==0,
    'server_timeout_zero_effect': targeted['server_30s_timeout']['G_delta']==targeted['server_30s_timeout']['L_delta']==0,
    'detached_client_request_79_steps': targeted['client_timeout_and_disconnect']['completed']['TicksSim']==79,
    'five_start_debt_cases_first_frame_one': all(controls[k]['first_frame_counts']==[1]*8 and controls[k]['max_frame_calls']==1 for k in ['start_after_long_load','start_after_export','start_after_idle','pause_resume','cancel_restart']),
    'required_evidence_labels_seven_sections': all(report.count('**'+label+':**') >= 7 for label in ['CLAIM','SETUP','ORACLE','EVIDENCE','SCOPE','DOES NOT PROVE']) and report.count('**OBSERVED') >= 7,
    'no_japanese_prose': not re.search(r'[ぁ-んァ-ン]', report),
    'all_report_links_valid': not errors,
}
verdicts = {'QA-ENGINE-002':'STILL FAILING','QA-ENGINE-003':'PARTIAL','QA-ENGINE-004':'STILL FAILING','QA-ENGINE-005':'STILL FAILING','QA-ENGINE-006':'STILL FAILING','QA-ENGINE-007':'CONFIRMED RESOLVED','QA-ENGINE-008':'CONFIRMED RESOLVED'}
for key, value in verdicts.items():
    checks[key+'_matrix_exactly_one'] = len(re.findall(r'^\| '+key+r' \| \*\*'+value+r'\*\* \|',report,re.M)) == 1
for key,value in checks.items():
    if not value:
        errors.append('Failed packaging/audit check: '+key)
verification = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'scope': 'Evidence packaging cross-checks; passing this does not mean candidate gate passes.',
                'qa_gate':'FAIL', 'adr_002_recommendation':'PROVISIONAL 유지', 'defect_verdicts': verdicts,
                'checks': checks, 'report_links': links, 'errors':errors, 'report_sha256': sha(REPORT)}
write_json(ROOT/'report-verification.json', verification)
entries = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.name=='artifact-manifest.json' or '__pycache__' in path.parts or 'obj' in path.parts:
        continue
    entries.append({'relative_path':str(path.relative_to(ROOT)), 'size_bytes':path.stat().st_size,'sha256':sha(path)})
write_json(ROOT/'artifact-manifest.json', {'utc':verification['utc'],
    'manifest_excludes':'This manifest itself, obj and __pycache__; includes QA observer DLLs and captured inputs/exports/logs/scripts.',
    'report': {'path':str(REPORT),'size_bytes':REPORT.stat().st_size,'sha256':sha(REPORT)},
    'canonical_inputs': [{'path': str(ROOT.parent.parent/x),'sha256':sha(ROOT.parent.parent/x)} for x in ['요구사항_명세서.md','ADR-001_Authenticated_Authority_and_Persistent_State.md','ADR-002_Tactical_and_Offline_Combat_Authority.md','ADR-006A_Temporal_Authority_ACCEPTED.md']],
    'file_count':len(entries),'total_bytes':sum(x['size_bytes'] for x in entries),'files':entries})
print(json.dumps({'packaging_errors':errors,'selected_final_fresh_equality':audit['final_to_fresh_reload_equal'],
                  'artifact_count':len(entries),'artifact_bytes':sum(x['size_bytes'] for x in entries),
                  'report_sha256':sha(REPORT)}, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
