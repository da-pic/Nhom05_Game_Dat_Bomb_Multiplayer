"""Validate report task 7 against archived XML/CSV, without rerunning tests."""
import csv
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task07-2026-10-27'
RUN = ROOT / 'report/evidence/recovery-report-task03-20261027-200413'
NAMES = ['11_THIET_LAP_THUC_NGHIEM.md', '12_KET_QUA.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def totals(directory):
    nodes = [ET.parse(p).getroot() for p in sorted(directory.rglob('TEST-*.xml'))]
    return {key: sum(int(n.get(key, 0)) for n in nodes) for key in ['tests', 'failures', 'errors', 'skipped']}, nodes


def main():
    assert not (OUT / 'revision-manifest.json').exists(), 'Keep previous audit; create a new revision'
    old = json.loads((OUT / 'before-hashes.json').read_text(encoding='utf-8'))
    allowed = {'report/chapters/' + name for name in NAMES}
    for path, digest in old.items():
        if path not in allowed:
            assert sha(ROOT / path) == digest, path
    checks = json.loads((RUN / 'checksums.sha256.json').read_text(encoding='utf-8'))
    assert all(sha(RUN / path) == digest for path, digest in checks.items())
    inventory = json.loads((RUN / 'source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    actual, nodes = totals(RUN / 'surefire')
    summary = json.loads((RUN / 'junit-summary.json').read_text(encoding='utf-8'))
    assert actual == summary['totals'] == dict(tests=171, failures=0, errors=0, skipped=0)
    assert len(nodes) == summary['classes'] == 44
    selected_counts = dict(SessionRecoveryClientTest=9, RecoveryInputTest=2, ConnectCancellationTest=1,
                           RecoveryGameplayIntegrationTest=8, RecoveryWriterTest=1, SessionRecoveryTest=10,
                           BombClientIntegrationTest=3, LobbyLifecycleTest=13)
    for name, count in selected_counts.items():
        matches = [node for node in nodes if node.get('name').endswith('.' + name)]
        assert len(matches) == 1 and int(matches[0].get('tests')) == count
    with (RUN / 'case-results.csv').open(encoding='utf-8-sig', newline='') as stream:
        markers = [dict(kind=row['kind'], scenario=row['scenario'], values=json.loads(row['values_json'])) for row in csv.DictReader(stream)]
    assert len(markers) == 11
    assert sum(row['kind'] == 'RECOVERY_CASE' for row in markers) == 8
    by_scenario = {row['scenario']: row['values'] for row in markers if row['kind'] == 'RECOVERY_CASE'}
    assert by_scenario['real_grace']['observed_wait_ms'] == 15001
    assert by_scenario['multi_input_bomb'] == dict(cycles=3, full_replica_equal=3, delta_after_full=3, bombs=5)
    assert by_scenario['offline_gameplay'] == dict(lives=2, respawns=1, item_pickups=1, speed=88, timer_seconds=29)
    boundaries = [row['values'] for row in markers if row['kind'] == 'RECOVERY_BOUNDARY']
    assert boundaries == [dict(elapsed_nanos=14999999999, admitted=True), dict(elapsed_nanos=15000000000, admitted=False), dict(elapsed_nanos=15000000001, admitted=False)]
    attempts = []
    manifest = json.loads((RUN / 'run-manifest.json').read_text(encoding='utf-8'))
    for attempt in manifest['earlier_attempts']:
        values, _ = totals(ROOT / attempt['evidence'])
        assert values['tests'] == attempt['tests'] and values['failures'] == attempt['failures']
        attempts.append(dict(evidence=attempt['evidence'], context=attempt['context'], totals=values))
    assert manifest['exit_codes'] == dict(full=0, tv2=0, network=0)
    records, patch = [], []
    catalogue = json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))
    numbers = {row['final_number'] for row in catalogue['sources']}
    (OUT / 'after').mkdir(exist_ok=True)
    for name in NAMES:
        path = ROOT / 'report/chapters' / name
        before_path = OUT / 'before' / name
        assert sha(before_path) == old[path.relative_to(ROOT).as_posix()]
        before, after = [p.read_text(encoding='utf-8') for p in [before_path, path]]
        assert before != after
        chapter = str(int(name[:2]))
        headings = re.findall(r'^## (' + chapter + r'\.\d+)\.', after, re.M)
        assert headings == [f'{chapter}.{i}' for i in range(1, len(headings)+1)]
        tables = re.findall(r'^\*\*Bảng (' + chapter + r'\.\d+)\.', after, re.M)
        assert tables == [f'{chapter}.{i}' for i in range(1, len(tables)+1)]
        assert len(tables) == (9 if chapter == '11' else 17)
        fenced = False
        for line in after.splitlines():
            if line.startswith('```'):
                fenced = not fenced
            elif not fenced:
                assert all(int(n) in numbers for n in re.findall(r'\[(\d{1,2})\](?!\()', line))
        assert not fenced and '[@R' not in after
        if chapter == '12':
            for start, end in [('12.5', '12.6'), ('12.6', '12.7')]:
                section = lambda text: text.split('## ' + start + '. ', 1)[1].split('## ' + end + '. ', 1)[0]
                assert section(before) == section(after), 'Changed historical benchmark section ' + start
            for key, count in selected_counts.items():
                assert f'| {key} | {count}/{count} |' in after
            assert all(str(value) in after for value in [15001, 171])
        records.append(dict(path=path.relative_to(ROOT).as_posix(), before_sha256=sha(before_path), after_sha256=sha(path), tables=tables))
        shutil.copy2(path, OUT / 'after' / name)
        patch.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='before/' + name, tofile='after/' + name))
    local_links = 0
    docs = [ROOT / 'report/chapters' / name for name in NAMES] + [ROOT / 'report/session-recovery/README.md', ROOT / 'report/session-recovery/07_CAP_NHAT_THUC_NGHIEM_VA_KET_QUA.md', OUT / 'README.md']
    for doc in docs:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                assert (doc.parent / re.sub(r':\d+$', '', link.split('#')[0])).exists(), (doc, link)
                local_links += 1
    verified = dict(full_suite=actual, classes=len(nodes), selected_class_counts=selected_counts,
                    dedicated_executions=31, selected_including_shared=47, markers=markers,
                    earlier_attempts=attempts, exit_codes=manifest['exit_codes'],
                    maven_finished_at=manifest['maven_finished_at'], maven_total_time=manifest['maven_total_time'],
                    raw_evidence_checksum_files_verified=len(checks), note='Derived from archived evidence; no test or benchmark rerun')
    (OUT / 'verified-results.json').write_text(json.dumps(verified, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'chapter-changes.patch').write_text(''.join(patch), encoding='utf-8')
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    revision = dict(task=7, date='2026-10-27', timezone='Asia/Saigon', chapters=records,
                    new_tables=6, local_links_checked=local_links, java_sources_preserved=len(inventory),
                    other_chapters_preserved=17, chapters_6_to_10_preserved=True, figures_and_old_exports_preserved=True,
                    canonical_references_and_historical_manifest_preserved=True,
                    sections_12_5_and_12_6_preserved_verbatim=True, tests_rerun=False,
                    raw_evidence_unchanged=True, evidence_used=RUN.relative_to(ROOT).as_posix(),
                    validation='PASS: XML/CSV totals, attempt totals, raw checksums, source inventory, captions, headings, links, citations and preservation')
    (OUT / 'revision-manifest.json').write_text(json.dumps(revision, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    hashes = {p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'checksums.sha256.json'}
    (OUT / 'checksums.sha256.json').write_text(json.dumps(hashes, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', full_suite=actual, recovery_markers=len(markers), raw_files_verified=len(checks), local_links_checked=local_links, new_tables=6, java_sources_preserved=len(inventory)), ensure_ascii=False))


if __name__ == '__main__':
    main()
