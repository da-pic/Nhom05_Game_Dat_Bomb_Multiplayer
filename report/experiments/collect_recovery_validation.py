"""Collect existing run outputs; this script does not run tests or change application code."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv
import difflib
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-complete-task03-2026-10-27'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args],
                                   cwd=ROOT, encoding='utf-8').strip()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    logs = []
    for path in sorted((ROOT / 'target').glob('recovery-complete-*.log')):
        shutil.copy2(path, OUT / path.name)
        logs.append({'path': path.name, 'sha256': sha(path)})
    suites = []
    for path in sorted((ROOT / 'target/surefire-reports').glob('TEST-*.xml')):
        node = ET.parse(path).getroot()
        suites.append({'name': node.get('name'), **{k: int(node.get(k, 0)) for k in
                       ('tests', 'failures', 'errors', 'skipped')}, 'timestamp': node.get('timestamp'),
                       'cases': [c.get('name') for c in node.findall('testcase')]})
        dest = OUT / 'surefire' / path.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(path, dest)
    totals = {k: sum(s[k] for s in suites) for k in ('tests', 'failures', 'errors', 'skipped')}
    assert totals == {'tests': 171, 'failures': 0, 'errors': 0, 'skipped': 0}, totals
    assert len(suites) == 44
    save('junit-summary.json', {'classes': 44, 'totals': totals, 'suites': suites})

    # Windows PowerShell > may produce UTF-16; preserve raw log and decode by BOM for CSV only.
    raw = (ROOT / 'target/recovery-complete-full-tests.log').read_bytes()
    lines = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig').splitlines()
    markers = []
    for line in lines:
        if not line.startswith(('RECOVERY_CASE ', 'RECOVERY_BOUNDARY ')):
            continue
        parts = line.split()
        kind = parts.pop(0)
        scenario = parts.pop(0) if '=' not in parts[0] else 'grace_boundary'
        fields = {}
        for field in parts:
            key, value = field.split('=', 1)
            if value in ('true', 'false'):
                value = value == 'true'
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
            fields[key] = value
        markers.append({'kind': kind, 'scenario': scenario, 'fields': fields,
                        'source_log': 'recovery-complete-full-tests.log'})
    assert len(markers) == 11, len(markers)
    save('case-results.json', {'records': markers, 'note': '8 integration cases and 3 controlled-clock cases, not network benchmarks'})
    with (OUT / 'case-results.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['kind', 'scenario', 'fields_json', 'source_log'])
        for row in markers:
            writer.writerow([row['kind'], row['scenario'], json.dumps(row['fields'], ensure_ascii=False), row['source_log']])

    paths = ['src/main/java/com/bombit/server/session/SessionRecoveryRejectedException.java',
             'src/main/java/com/bombit/server/session/SessionManager.java',
             'src/main/java/com/bombit/server/app/LobbyGameServer.java',
             'src/test/java/com/bombit/integration/RecoveryGameplayIntegrationTest.java',
             'src/test/java/com/bombit/server/session/SessionRecoveryTest.java',
             'docs/SESSION_RECOVERY_VALIDATION.md']
    files, delta = [], []
    prior_server = ROOT / 'report/evidence/recovery-server-task01-2026-10-27/source'
    for rel in paths:
        path = ROOT / rel
        dest = OUT / 'source' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        files.append({'path': rel, 'sha256': sha(path)})
        before = prior_server / rel
        delta.extend(difflib.unified_diff(before.read_text(encoding='utf-8').splitlines(keepends=True)
                     if before.exists() else [], path.read_text(encoding='utf-8').splitlines(keepends=True),
                     fromfile='before-task03/' + rel, tofile='after-task03/' + rel))
    (OUT / 'task03-changes.patch').write_text(''.join(delta), encoding='utf-8')
    prior_client = load(ROOT / 'report/evidence/recovery-client-task02-2026-10-27/run-manifest.json')
    for row in prior_client['client_task_files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    old = load(ROOT / 'report/evidence/task18-2026-10-26/final-artifacts.json')
    for row in old['final_files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    for row in load(ROOT / 'report/report-manifest.json')['chapter_order']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    inventory = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in sorted((ROOT / 'src').rglob('*.java'))]
    save('source-inventory.json', inventory)
    save('run-manifest.json', {
        'date': datetime.now(timezone(timedelta(hours=7))).isoformat(), 'base_commit': git('rev-parse', 'HEAD'),
        'branch': git('branch', '--show-current'), 'working_tree_status': git('status', '--short'),
        'task_files': files, 'full_suite': totals, 'classes': 44, 'new_test_executions': 11,
        'new_integration_cases': 8, 'new_boundary_cases': 3, 'controlled_gameplay_clock': True,
        'tcp_grace_seconds': 15, 'lan_wifi_or_interactive_gui_executed': False,
        'source_inventory_count': len(inventory), 'prior_client_files_preserved': len(prior_client['client_task_files']),
        'report_chapters_preserved': 19, 'final_report_files_preserved': 4,
        'tv2_exit_code': 0, 'network_main_exit_code': 0, 'logs': logs, 'commit_created': False,
    })
    print(json.dumps({'full_suite': totals, 'classes': 44, 'case_markers': len(markers),
                      'source_files_hashed': len(inventory), 'reports_unchanged': True}))


if __name__ == '__main__':
    main()
