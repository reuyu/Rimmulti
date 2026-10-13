"""Read-only A completion identity/file checks. Never executes reported artifacts."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / 'Dispatcher'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest().upper()


def inspect_preservation(task):
    """Check Master-owned baselines; an Engine repair may change named current paths."""
    freeze = ROOT / 'docs/WarEconomy_Master_Handoff_20261006/bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json'
    manifest = json.loads(freeze.read_text(encoding='utf-8-sig'))
    policy = task.get('preservation_policy', {})
    engine_repair = policy.get('kind') == 'ENGINE_REPAIR_ARCHIVED_BASELINE'
    allowed = {Path(p).resolve() for p in policy.get('allowed_changed_engine_paths', [])} if engine_repair else set()
    errors, authorized_changes, archive_checks, pipeline_checks, prior_checks = [], [], [], [], []
    for name, item in manifest['files'].items():
        current = Path(name)
        actual = digest(current) if current.is_file() else 'MISSING'
        if actual != item['sha256'].upper():
            if engine_repair and current.resolve() in allowed and current.is_file():
                authorized_changes.append({'path': name, 'before_sha256': item['sha256'], 'actual_sha256': actual})
            else:
                errors.append('unapproved Engine baseline change: ' + name)
    if engine_repair:
        manifests = [('engine_archive_manifest', 'engine_archive_manifest_sha256'),
                     ('pipeline_manifest', 'pipeline_manifest_sha256')]
        if policy.get('prior_candidate_freeze_manifest'):
            manifests.append(('prior_candidate_freeze_manifest', 'prior_candidate_freeze_manifest_sha256'))
        for field, hash_field in manifests:
            p = Path(policy[field])
            if not p.is_absolute() or not p.resolve().is_relative_to(ROOT) or not p.is_file():
                errors.append('missing/out-of-project Master preservation manifest: ' + field)
                continue
            if digest(p) != policy[hash_field]:
                errors.append('Master preservation manifest hash changed: ' + field)
                continue
            data = json.loads(p.read_text(encoding='utf-8-sig'))
            for row in data['files']:
                keys = (['archive_path'] if field == 'engine_archive_manifest' else
                        ['frozen_path'] if field == 'prior_candidate_freeze_manifest' else
                        ['original_path', 'frozen_path'])
                for key in keys:
                    f = Path(row[key])
                    if not f.is_absolute() or not f.resolve().is_relative_to(ROOT) or not f.is_file():
                        errors.append('missing/out-of-project preserved file: ' + str(f))
                        continue
                    actual = digest(f)
                    matched = actual == row['sha256'].upper()
                    collection = (archive_checks if field == 'engine_archive_manifest' else
                                  prior_checks if field == 'prior_candidate_freeze_manifest' else pipeline_checks)
                    collection.append({'path': str(f), 'matched': matched})
                    if not matched:
                        errors.append('preserved file hash changed: ' + str(f))
        # Later repairs preserve every rejected predecessor, not just one lineage.
        for entry in policy.get('additional_preserved_candidate_manifests', []):
            p = Path(entry['path'])
            if not p.is_absolute() or not p.resolve().is_relative_to(ROOT) or not p.is_file():
                errors.append('missing/out-of-project additional preservation manifest')
                continue
            if digest(p) != entry['sha256']:
                errors.append('additional preservation manifest hash changed: ' + str(p))
                continue
            data = json.loads(p.read_text(encoding='utf-8-sig'))
            for row in data['files']:
                f = Path(row['frozen_path'])
                if not f.is_absolute() or not f.resolve().is_relative_to(ROOT) or not f.is_file():
                    errors.append('missing/out-of-project additional frozen file: ' + str(f))
                    continue
                matched = digest(f) == row['sha256'].upper()
                prior_checks.append({'path': str(f), 'matched': matched, 'additional_lineage': True})
                if not matched:
                    errors.append('additional preserved file hash changed: ' + str(f))
    qa_checks = []
    # Narrower task scope can preserve current source after historical repairs.
    for row in policy.get('fixed_current_files', []):
        p = Path(row['path'])
        if not p.is_file() or digest(p) != row['sha256']:
            errors.append('task-scoped fixed current file changed: ' + str(p))
    for row in policy.get('fixed_current_prefixes', []):
        p = Path(row['path'])
        if not p.is_file():
            errors.append('task-scoped fixed source missing: ' + str(p))
            continue
        data = p.read_bytes()
        marker = row['marker'].encode('utf-8')
        if data.count(marker) != 1 or hashlib.sha256(data.split(marker, 1)[0]).hexdigest().upper() != row['sha256']:
            errors.append('task-scoped fixed source region changed: ' + str(p))
    for entry in policy.get('qa_preserved_manifests', []):
        p = Path(entry['path'])
        if not p.is_absolute() or not p.resolve().is_relative_to(ROOT) or not p.is_file():
            errors.append('missing/out-of-project QA preservation manifest')
            continue
        if digest(p) != entry['sha256']:
            errors.append('QA preservation manifest hash changed: ' + str(p))
            continue
        data = json.loads(p.read_text(encoding='utf-8-sig'))
        rows = data['files']
        if isinstance(rows, dict):
            rows = [{'path': name, **row} for name, row in rows.items()]
        for row in rows:
            f = Path(row['path'])
            if not f.is_absolute() or not f.resolve().is_relative_to(ROOT) or not f.is_file():
                errors.append('missing/out-of-project preserved QA file: ' + str(f))
                continue
            matched = digest(f) == row['sha256'].upper()
            qa_checks.append({'path': str(f), 'matched': matched, 'manifest': str(p)})
            if not matched:
                errors.append('preserved QA file hash changed: ' + str(f))
    return {'preservation_errors': errors, 'authorized_engine_changes': authorized_changes,
            'qa_preservation_checks': qa_checks,
            'engine_archive_checks': archive_checks, 'pipeline_preservation_checks': pipeline_checks,
            'prior_candidate_checks': prior_checks}


def inspect():
    board = json.loads((DIR / 'MASTER_A_TASKS.json').read_text(encoding='utf-8-sig'))
    active = [t for t in board['tasks'] if t['status'] in
              ['SENT', 'ACKNOWLEDGED', 'IN_PROGRESS', 'DELIVERY_UNCERTAIN',
               'SENT_IN_PROGRESS_ACK_PENDING', 'SENT_ACK_VERIFIED_IN_PROGRESS']]
    if not active:
        return {'status': 'NO_ACTIVE_A_TASK'}
    if len(active) != 1:
        return {'status': 'STATE_CONFLICT', 'active_count': len(active)}
    task = active[0]
    output = {'dispatch_id': task['dispatch_id'], 'task_status': task['status']}
    errors = []
    ack_path = Path(task['ack_path'])
    if ack_path.exists():
        try:
            ack = json.loads(ack_path.read_text(encoding='utf-8-sig'))
            ack_errors = [key for key in ['dispatch_id', 'wp_id', 'wp_revision']
                          if ack.get(key) != task.get(key)]
            output['ack'] = {'sha256': digest(ack_path), 'status': ack.get('status'),
                             'identity_errors': ack_errors}
        except (OSError, ValueError) as exc:
            output['ack'] = {'error': str(exc)}
    path = Path(task['completion_path'])
    if not path.exists():
        return dict(output, status='AWAITING_COMPLETION')
    output.update(completion_path=str(path), completion_sha256=digest(path))
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    for key in ['dispatch_id', 'wp_id', 'wp_revision']:
        if data.get(key) != task.get(key):
            errors.append('identity mismatch: ' + key)
    for key in ['result_id', 'completed_at', 'summary']:
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append('missing string: ' + key)
    if data.get('schema_version') != 1 or data.get('producer') != 'A' or data.get('report_kind') != 'E1':
        errors.append('schema/producer/report_kind mismatch')
    if data.get('status') not in ['COMPLETED', 'BLOCKED', 'FAILED']:
        errors.append('status is not terminal')
    try:
        completed = datetime.datetime.fromisoformat(data.get('completed_at', ''))
        created = datetime.datetime.fromisoformat(task['created_at'])
        if completed.tzinfo is None or completed < created:
            errors.append('completed_at timezone/order mismatch')
    except (ValueError, TypeError):
        errors.append('invalid completed_at')
    artifacts = data.get('artifacts')
    if not isinstance(artifacts, list):
        artifacts = []
        errors.append('artifacts must be an array')
    roles = set()
    checks = []
    for entry in artifacts:
        if not isinstance(entry, dict):
            errors.append('invalid artifact entry')
            continue
        role = entry.get('role')
        if not isinstance(role, str):
            errors.append('invalid artifact role')
            continue
        roles.add(role)
        value = entry.get('path')
        if not isinstance(value, str):
            errors.append('missing artifact path: ' + role)
            continue
        artifact = Path(value)
        # Never follow reported network paths or read outside this project.
        if not artifact.is_absolute() or value.startswith(('\\\\', '//')) or not artifact.resolve().is_relative_to(ROOT):
            errors.append('out-of-project artifact path: ' + role)
            continue
        if not artifact.is_file():
            errors.append('missing artifact: ' + role)
            continue
        actual = digest(artifact)
        matched = actual == str(entry.get('sha256', '')).upper()
        checks.append({'role': role, 'path': str(artifact), 'actual_sha256': actual, 'matched': matched})
        if not matched:
            errors.append('artifact hash mismatch: ' + role)
    if data.get('status') == 'COMPLETED':
        required = {'implementation_report', 'release_manifest', 'harness', 'results',
                    'raw_evidence', 'candidate_binary', 'source', 'pdb',
                    'engine_freeze_before', 'engine_freeze_after'}
        errors.extend('missing artifact role: ' + role for role in sorted(required - roles))
        # The issued instructions allow prose or a list for limitations.
        if not isinstance(data.get('limitations'), (str, list)) or not data.get('e1_verdict'):
            errors.append('missing limitations/e1_verdict')
    elif not data.get('reason'):
        errors.append('missing terminal failure reason')
    preservation = inspect_preservation(task)
    errors.extend(preservation['preservation_errors'])
    output.update(result_id=data.get('result_id'), reported_status=data.get('status'),
                  reported_e1_verdict=data.get('e1_verdict'), artifact_checks=checks,
                  evidence_errors=errors, engine_freeze_errors=preservation['preservation_errors'],
                  status='EVIDENCE_INCOMPLETE' if errors else 'READY_FOR_MASTER_REVIEW',
                  master_verdict=None)
    output.update(preservation)
    return output


if __name__ == '__main__':
    try:
        print(json.dumps(inspect(), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'READ_ERROR', 'error': str(exc)}))
