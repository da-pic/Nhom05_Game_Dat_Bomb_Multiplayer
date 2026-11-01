"""Archive a new completed test run for report task 3 without replacing old evidence.

Run the three commands in the task document first. Pass their actual exit codes.
This collector checks log/XML consistency, source hashes and protected reports.
"""
import argparse
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args], cwd=ROOT, encoding='utf-8').strip()


def decode(path):
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full-exit', type=int, required=True)
    parser.add_argument('--tv2-exit', type=int, required=True)
    parser.add_argument('--network-exit', type=int, required=True)
    args = parser.parse_args()
    now = datetime.now(timezone(timedelta(hours=7)))
    out = ROOT / 'report/evidence' / ('recovery-report-task03-' + now.strftime('%Y%m%d-%H%M%S'))
    assert not out.exists()
    prior = ROOT / 'report/evidence/recovery-complete-task03-2026-10-27'
    inventory = json.loads((prior / 'source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inventory), 'Source changed since reviewed tests'
    protected = json.loads((ROOT / 'report/evidence/recovery-report-design-task02-2026-10-27/review-manifest.json').read_text(encoding='utf-8'))['protected_files']
    assert all(sha(ROOT / path) == value for path, value in protected.items())
    log_names = ['full', 'tv2', 'network']
    logs = {name: ROOT / f'target/report-recovery-task03-{name}.log' for name in log_names}
    texts = {name: decode(path) for name, path in logs.items()}
    suites, cases = [], []
    for path in sorted((ROOT / 'target/surefire-reports').glob('TEST-*.xml')):
        node = ET.parse(path).getroot()
        suite = dict(name=node.get('name'), seconds=float(node.get('time', 0)), xml=path.name,
                     **{key: int(node.get(key, 0)) for key in ('tests', 'failures', 'errors', 'skipped')})
        for case in node.findall('testcase'):
            result = 'ERROR' if case.find('error') is not None else 'FAIL' if case.find('failure') is not None else 'SKIP' if case.find('skipped') is not None else 'PASS'
            cases.append(dict(classname=case.get('classname'), name=case.get('name'), result=result, seconds=case.get('time'), xml=path.name))
        suites.append(suite)
    totals = {key: sum(s[key] for s in suites) for key in ('tests', 'failures', 'errors', 'skipped')}
    summaries = re.findall(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', texts['full'])
    assert summaries and tuple(map(int, summaries[-1])) == tuple(totals.values()), (summaries[-1:], totals)
    # Require all XML suites to occur in this log so stale reports cannot pad totals.
    assert all(f"Running {s['name']}" in texts['full'] for s in suites)
    assert len(cases) == totals['tests']
    markers = []
    for line in texts['full'].splitlines():
        if not line.startswith(('RECOVERY_CASE ', 'RECOVERY_BOUNDARY ')):
            continue
        fields = line.split()
        kind = fields.pop(0)
        scenario = fields.pop(0) if '=' not in fields[0] else 'grace_boundary'
        values = {}
        for item in fields:
            key, value = item.split('=', 1)
            values[key] = value == 'true' if value in ('true', 'false') else int(value) if value.isdigit() else value
        markers.append(dict(kind=kind, scenario=scenario, values=values, raw_line=line))
    assert len(markers) == 11, len(markers)
    passed = (args.full_exit == args.tv2_exit == args.network_exit == 0 and
              totals['failures'] == totals['errors'] == totals['skipped'] == 0 and
              '[INFO] BUILD SUCCESS' in texts['full'] and
              'PASS' in texts['tv2'] and 'PASS' in texts['network'])
    out.mkdir(parents=True)
    def save(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for name, path in logs.items():
        shutil.copy2(path, out / path.name)
    for name in ['m1-server-process.log', 'm1-client-a-process.log', 'm1-client-b-process.log',
                 'report-recovery-task03-javac.log']:
        path = ROOT / 'target' / name
        if path.exists():
            shutil.copy2(path, out / name)
    (out / 'surefire').mkdir()
    for suite in suites:
        shutil.copy2(ROOT / 'target/surefire-reports' / suite['xml'], out / 'surefire' / suite['xml'])
    save('junit-summary.json', dict(classes=len(suites), totals=totals, suites=suites))
    save('case-results.json', markers)
    for name, records in [('test-executions.csv', cases), ('class-results.csv', suites)]:
        with (out / name).open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    with (out / 'case-results.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['kind', 'scenario', 'values_json', 'raw_line'])
        writer.writerows([r['kind'], r['scenario'], json.dumps(r['values'], ensure_ascii=False), r['raw_line']] for r in markers)
    for row in inventory:
        source = ROOT / row['path']
        dest = out / 'source' / row['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    save('source-inventory.json', inventory)
    (out / 'tracked-source-vs-head.patch').write_text(git('diff', 'HEAD', '--', 'src')+'\n', encoding='utf-8')
    java = subprocess.run(['D:/JavaJDK/bin/java.exe', '-version'], capture_output=True, text=True)
    manifest = dict(collected_at=now.isoformat(), timezone='Asia/Saigon', head=git('rev-parse', 'HEAD'),
                    branch=git('branch', '--show-current'), git_status=git('status', '--porcelain=v1'),
                    source_files_verified=len(inventory), same_source_as_previous_technical_run=True,
                    environment=dict(os=platform.platform(), machine=platform.machine(), logical_cpus=os.cpu_count(),
                                     processor_identifier=os.environ.get('PROCESSOR_IDENTIFIER'),
                                     java_version=(java.stdout+java.stderr).strip(),
                                     maven='3.9.12', junit='5.11.4', surefire='3.5.2', network='127.0.0.1 TCP',
                                     cim_hardware_query='Access denied; no CIM hardware details claimed'),
                    commands=dict(full="mvn.cmd -o -Dmaven.repo.local=C:/Users/Chinh/.m2/repository test",
                                  tv2='cmd /c scripts/check-tv2.cmd',
                                  network='D:/JavaJDK/bin/java.exe -cp target/classes;target/test-classes com.bombit.integration.NetworkTest'),
                    exit_codes=dict(full=args.full_exit, tv2=args.tv2_exit, network=args.network_exit),
                    execution_context='Full suite and transport checks executed outside sandbox with approval',
                    earlier_attempts=[
                        dict(evidence='report/evidence/recovery-report-task03-attempt01-2026-10-27', context='sandbox', tests=171, failures=1),
                        dict(evidence='report/evidence/recovery-report-task03-smoke-recheck-2026-10-27', context='sandbox smoke-only', tests=1, failures=1),
                        dict(evidence='report/evidence/recovery-report-task03-attempt02-2026-10-27', context='sandbox after explicit production compilation', tests=171, failures=1),
                        dict(evidence='report/evidence/recovery-report-task03-smoke-unrestricted-2026-10-27', context='outside sandbox smoke-only', tests=1, failures=0)],
                    full_suite=totals, classes=len(suites), case_markers=len(markers), all_checks_passed=passed,
                    maven_total_time=re.findall(r'\[INFO\] Total time:\s*(.*)', texts['full'])[-1:],
                    maven_finished_at=re.findall(r'\[INFO\] Finished at:\s*(.*)', texts['full'])[-1:],
                    interactive_gui_lan_wifi_executed=False, recovery_latency_benchmark=False,
                    tcp_grace_seconds=15, controlled_gameplay_clock=True,
                    protected_files=protected, code_changed_for_this_report_task=False)
    save('run-manifest.json', manifest)
    save('checksums.sha256.json', {p.relative_to(out).as_posix(): sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    assert all(sha(ROOT / path) == value for path, value in protected.items())
    print(json.dumps(dict(evidence=out.relative_to(ROOT).as_posix(), totals=totals, classes=len(suites), markers=len(markers), all_checks_passed=passed), ensure_ascii=False))
    if not passed:
        raise SystemExit('Run archived with failures; investigate without rewriting evidence.')


if __name__ == '__main__':
    main()
