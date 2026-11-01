"""Audit task 9 report prose, source catalogue and immutable evidence; runs no Java tests."""
from pathlib import Path
import csv
import difflib
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task09-2026-10-27'
CHAPTERS = [
    '01_TEN_DE_TAI.md', '02_TOM_TAT.md', '03_TU_KHOA.md', '04_GIOI_THIEU.md',
    '05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md', '18_TAI_LIEU_THAM_KHAO.md', '19_PHU_LUC.md',
]
ALLOWED = ['report/chapters/' + name for name in CHAPTERS] + ['report/REFERENCES.md', 'report/references/sources.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return path.read_text(encoding='utf-8')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert not (OUT / 'revision-manifest.json').exists(), 'Preserve completed audit; create a new revision.'
    old = json.loads(read(OUT / 'before-hashes.json'))
    for rel, digest in old.items():
        if rel not in ALLOWED:
            assert sha(ROOT / rel) == digest, ('Unexpected protected-file change', rel)
    for rel in ALLOWED:
        assert sha(OUT / 'before' / rel) == old[rel], ('Incorrect backup', rel)
    run = ROOT / 'report/evidence/recovery-report-task03-20261027-200413'
    raw = json.loads(read(run / 'checksums.sha256.json'))
    assert len(raw) == 280 and all(sha(run / rel) == digest for rel, digest in raw.items())
    inventory = json.loads(read(run / 'source-inventory.json'))
    assert len(inventory) == 219 and all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    summary = json.loads(read(run / 'junit-summary.json'))
    assert summary['classes'] == 44 and summary['totals'] == dict(tests=171, failures=0, errors=0, skipped=0)
    executions = list(csv.DictReader((run / 'test-executions.csv').open(encoding='utf-8-sig', newline='')))
    assert len(executions) == 171 and all(row['result'] == 'PASS' for row in executions)
    dedicated = {'SessionRecoveryClientTest', 'RecoveryInputTest', 'ConnectCancellationTest',
                 'RecoveryGameplayIntegrationTest', 'RecoveryWriterTest', 'SessionRecoveryTest'}
    assert sum(row['classname'].split('.')[-1] in dedicated for row in executions) == 31
    appendix = read(ROOT / 'report/chapters/19_PHU_LUC.md')
    test_names = set(re.search(r"'-Dtest=([^']+)'", appendix)[1].split(','))
    assert test_names == dedicated
    for name in dedicated:
        assert len(list((ROOT / 'src/test').rglob(name + '.java'))) == 1
    markers = list(csv.DictReader((run / 'case-results.csv').open(encoding='utf-8-sig', newline='')))
    real_grace = [json.loads(row['values_json']) for row in markers if row['scenario'] == 'real_grace']
    assert len(real_grace) == 1 and real_grace[0]['observed_wait_ms'] == 15001
    catalog = json.loads(read(ROOT / 'report/references/sources.json'))
    sources = catalog['sources']
    ids = {s['id'] for s in sources}
    assert ids == {f'R{i:02d}' for i in range(1, 20)} and len(sources) == 19
    assert len({s['url'] for s in sources}) == 19
    by_number = {s['final_number']: s for s in sources}
    assert set(by_number) == set(range(1, 20))
    refmap = json.loads(read(OUT / 'reference-map.json'))
    all_chapters = sorted((ROOT / 'report/chapters').glob('*.md'))
    assert len(all_chapters) == 19
    order, occurrences, local_links = [], {}, 0
    for path in all_chapters:
        text = read(path)
        chapter = int(path.name[:2])
        assert text.startswith(f'# {chapter}. ')
        assert '[@R' not in text
        fenced = False
        if chapter <= 17:
            for line in text.splitlines():
                if line.startswith('```'):
                    fenced = not fenced
                    continue
                if not fenced:
                    for token in re.findall(r'\[(\d{1,2})\](?!\()', line):
                        number = int(token)
                        assert number in by_number, (path.name, token)
                        if number not in order:
                            order.append(number)
                        occurrences.setdefault(number, set()).add(path.name)
            assert not fenced, path.name
    assert order == list(range(1, 20)), order
    assert refmap['order'] == [by_number[n]['id'] for n in order]
    assert refmap['old_numbers_preserved'] and refmap['normalization_changed_documents'] == [ALLOWED[4]]
    assert all(set(source['cited_in_chapters']) == occurrences[source['final_number']] for source in sources)
    entries = []
    for rel in ['report/REFERENCES.md', 'report/chapters/18_TAI_LIEU_THAM_KHAO.md']:
        lines = re.findall(r'^\[(\d+)\] (.*) <!-- (R\d{2}) -->$', read(ROOT / rel), re.M)
        assert [int(row[0]) for row in lines] == order
        for number, body, key in lines:
            source = by_number[int(number)]
            assert source['id'] == key and source['url'] in body
            day = '27' if source['verified_on'] == '2026-10-27' else '26'
            assert f'Accessed: Oct. {day}, 2026.' in body
        entries.append(lines)
    assert entries[0] == entries[1]
    texts = {int(name[:2]): read(ROOT / 'report/chapters' / name) for name in CHAPTERS}
    assert all(word in texts[2] for word in ['State Delta Compression', 'Seamless Session Recovery', '171/171',
                                           '44 class', 'ngoài sandbox', '35,98–97,54%', '18.000', '45/45'])
    keyword_lines = [line for line in texts[3].splitlines() if ';' in line and not line.startswith('>')]
    assert len(keyword_lines) == 1 and len(keyword_lines[0].split(';')) == 6
    assert '[2], [4], [5]' in texts[5] and '[2]–[5]' not in texts[5]
    assert re.findall(r'^\*\*Bảng (5\.\d+)\.', texts[5], re.M) == [f'5.{i}' for i in range(1, 5)]
    assert all(f'### 5.6.{i}.' in texts[5] for i in range(1, 5))
    assert re.findall(r'^\*\*Bảng ([A-E]\.\d+)\.', texts[19], re.M) == ['A.1', 'B.1', 'C.1', 'C.2', 'E.1']
    assert '### D.3.' in texts[19] and '### B.4.' in texts[19]
    obsolete = ['Bản hiện hành chưa cung cấp chức năng reconnect', 'RECONNECT có mã 0043 nhưng chưa có flow resume',
                'soak dài hạn hoặc resume trận', 'resume đã triển khai.', 'Có 14 nguồn']
    assert all(token not in text for token in obsolete for text in texts.values())
    documents = [ROOT / rel for rel in ALLOWED if rel.endswith('.md')] + [
        ROOT / 'report/session-recovery/README.md',
        ROOT / 'report/session-recovery/09_CAP_NHAT_TONG_QUAN_TAI_LIEU_PHU_LUC.md', OUT / 'README.md',
    ]
    for doc in documents:
        text = read(doc)
        assert '\ufffd' not in text, doc
        assert sum(line.startswith('```') for line in text.splitlines()) % 2 == 0, doc
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                path = re.sub(r':\d+$', '', target.split('#')[0])
                assert (doc.parent / path).exists(), (doc, target)
                local_links += 1
    patch, records = [], []
    for rel in ALLOWED:
        path, before_path = ROOT / rel, OUT / 'before' / rel
        before, after = read(before_path), read(path)
        assert before != after, rel
        after_path = OUT / 'after' / rel
        after_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, after_path)
        patch.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                         fromfile='before/' + rel, tofile='after/' + rel))
        records.append({'path': rel, 'before_sha256': sha(before_path), 'after_sha256': sha(path),
                        'before_lines': len(before.splitlines()), 'after_lines': len(after.splitlines())})
    (OUT / 'chapter-changes.patch').write_text(''.join(patch), encoding='utf-8')
    for script in [Path(__file__), ROOT / 'report/experiments/finalize_recovery_references.py']:
        shutil.copy2(script, OUT / script.name)
    revision = dict(task=9, date='2026-10-27', timezone='Asia/Saigon', chapters=[r for r in records if '/chapters/' in r['path']],
                    canonical_references=[r for r in records if '/chapters/' not in r['path']], source_count=19,
                    citation_order=refmap['order'], old_numbers_preserved=True, citation_occurrences=sum(map(len, occurrences.values())),
                    local_links_checked=local_links, chapters_6_to_17_preserved=True, chapter_count=19,
                    keywords=6, new_tables=['5.4'], java_sources_preserved=219, raw_evidence_files_verified=280,
                    dedicated_recovery_executions=31, recovery_summary_verified=dict(tests=171, classes=44),
                    tests_rerun=False, new_measurements=False, docx_pdf_exports_regenerated=False,
                    figures_old_exports_merged_markdown_and_export_manifest_preserved=True,
                    validation='PASS: protected hashes, evidence summary, canonical source mapping, citations, headings, captions, test names and local links')
    dump(OUT / 'revision-manifest.json', revision)
    dump(OUT / 'checksums.sha256.json', {p.relative_to(OUT).as_posix(): sha(p)
         for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'checksums.sha256.json'})
    print(json.dumps({'status': 'PASS', 'chapters_updated': 7, 'references': 19, 'keywords': 6,
                      'local_links_checked': local_links, 'java_sources_preserved': 219,
                      'raw_evidence_files_verified': 280, 'chapters_6_to_17_preserved': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
