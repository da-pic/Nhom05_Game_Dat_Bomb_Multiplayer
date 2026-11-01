"""Inventory this report audit without editing production source or historical measurements.

Re-running updates the manifest to the then-current workspace. Preserve a copy before
using this script for another date/revision; it is not a command for rerunning tests.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import collections
import csv
import hashlib
import json
import os
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
    return {'exit_code': result.returncode, 'output': (result.stdout + result.stderr).strip()}

files = sorted({
    *ROOT.joinpath('src/main').rglob('*'),
    *ROOT.joinpath('src/test').rglob('*'),
    *ROOT.joinpath('scripts').rglob('*'),
    ROOT / 'pom.xml', ROOT / '.gitignore',
})
files = [p for p in files if p.is_file()]
with (OUT / 'source-inventory.csv').open('w', encoding='utf-8', newline='') as output:
    writer = csv.DictWriter(output, fieldnames=['path', 'bytes', 'sha256'])
    writer.writeheader()
    for path in files:
        writer.writerow({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'sha256': digest(path)})

historical = []
for path in sorted(ROOT.joinpath('docs/measurements').glob('*.csv')):
    with path.open(encoding='utf-8-sig', newline='') as source:
        rows = list(csv.DictReader(source))
    historical.append({
        'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path), 'rows': len(rows),
        'scenarios': dict(collections.Counter(r['scenario'] for r in rows)),
        'statuses': dict(collections.Counter(r['status'] for r in rows)),
        'run_ids': sorted({r['run_id'] for r in rows}),
        'revisions': sorted({r['revision'] for r in rows}),
        'scopes': sorted({r['scope'] for r in rows}),
        'note': 'Historical data; not measured again in report task 1.',
    })

counts = {
    'production_java_files': sum(p.suffix == '.java' and p.is_relative_to(ROOT / 'src/main') for p in files),
    'test_java_files': sum(p.suffix == '.java' and p.is_relative_to(ROOT / 'src/test') for p in files),
    'inventory_files': len(files),
}

first = json.loads((OUT / 'junit-first-run-summary.json').read_text(encoding='utf-8'))
retry = (OUT / 'process-test-retry.log').read_text(encoding='utf-8-sig')
retry_summary = re.findall(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', retry)[-1]
tv2_log = (OUT / 'tv2-checks.log').read_text(encoding='utf-8-sig')
tv2_passes = [line for line in tv2_log.splitlines() if line.startswith('PASS:')]

relevant = [ROOT / 'README.md', ROOT / 'docs/protocol.md', ROOT / 'docs/NETWORK_MEASUREMENTS.md',
            ROOT / 'docs/TECHNICAL_REPORT.md', ROOT / 'docs/JDK25_MIGRATION.md',
            ROOT / 'docs/RECONNECT_ASSESSMENT.md', ROOT / 'docs/FILE_OWNERSHIP_NOTES.md',
            ROOT / 'docs/TEAM_OWNERSHIP.md', ROOT / 'docs/PROJECT_STATUS_AUDIT.md']
relevant += sorted(ROOT.joinpath('phancong').glob('*.md'))

manifest = {
    'report_task': 1,
    'captured_at': datetime.now(timezone(timedelta(hours=7))).isoformat(),
    'timezone': 'Asia/Saigon',
    'revision': command(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'rev-parse', 'HEAD']),
    'tracked_code_status': command(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'status', '--short', '--', 'src', 'pom.xml', 'scripts']),
    'environment': {'os': platform.platform(), 'machine': platform.machine(), 'logical_processors': os.cpu_count(),
                    'java': command(['D:/JavaJDK/bin/java.exe', '-version']),
                    'javac': command(['D:/JavaJDK/bin/javac.exe', '-version']),
                    'declared_maven_release': '25', 'maven_version_used': '3.9.12', 'dependency_resolution': 'offline local cache'},
    'counts': counts,
    'full_junit': {'exit_code': 1, 'classes': first['test_classes'], **first['totals']},
    'focused_retry': {'exit_code': 1, **dict(zip(['tests','failures','errors','skipped'], map(int, retry_summary)))},
    'tv2_check': {'exit_code': 0, 'pass_lines': tv2_passes},
    'network_main': {'exit_code': 0, 'output': (OUT / 'network-main.log').read_text(encoding='utf-8-sig').strip()},
    'historical_measurements': historical,
    'document_sources': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)} for p in relevant if p.exists()],
    'audit_artifacts': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)}
                        for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'manifest.json'],
    'scope': {'production_source_modified': False, 'tests_modified': False, 'fresh_gui_acceptance': False,
              'fresh_lan_measurements': False, 'new_performance_benchmark': False,
              'note': 'Audit includes current automated regression and existing evidence review, not final acceptance.'},
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'counts': counts, 'full_junit': manifest['full_junit'], 'retry': manifest['focused_retry'],
                  'historical_csv_files': len(historical)}, ensure_ascii=False))
