"""Audit task 8 prose/evidence consistency; no tests or benchmarks are executed."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task08-2026-10-27'
NAMES = ['13_THAO_LUAN.md', '14_DIEM_MOI_VA_DONG_GOP.md', '15_HAN_CHE.md', '16_HUONG_PHAT_TRIEN.md', '17_KET_LUAN.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'revision-manifest.json').exists(), 'Preserve prior audit; create a new revision if needed'
    old = json.loads((OUT / 'before-hashes.json').read_text(encoding='utf-8'))
    allowed = {'report/chapters/' + name for name in NAMES}
    for path, digest in old.items():
        if path not in allowed:
            assert sha(ROOT / path) == digest, path
    run = ROOT / 'report/evidence/recovery-report-task03-20261027-200413'
    raw_checks = json.loads((run / 'checksums.sha256.json').read_text(encoding='utf-8'))
    assert all(sha(run / path) == digest for path, digest in raw_checks.items())
    inventory = json.loads((run / 'source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    summary = json.loads((run / 'junit-summary.json').read_text(encoding='utf-8'))
    assert summary['totals'] == dict(tests=171, failures=0, errors=0, skipped=0) and summary['classes'] == 44
    numbers = {row['final_number'] for row in json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))['sources']}
    expected_tables = {13: 3, 14: 2, 15: 3, 16: 2, 17: 0}
    (OUT / 'after').mkdir(exist_ok=True)
    records, patch, texts = [], [], {}
    for name in NAMES:
        path = ROOT / 'report/chapters' / name
        before_path = OUT / 'before' / name
        assert sha(before_path) == old[path.relative_to(ROOT).as_posix()]
        before, after = [p.read_text(encoding='utf-8') for p in [before_path, path]]
        assert before != after
        chapter = int(name[:2])
        headings = re.findall(r'^## (' + str(chapter) + r'\.\d+)\.', after, re.M)
        assert headings == [f'{chapter}.{i}' for i in range(1, len(headings)+1)]
        subheads = re.findall(r'^### (' + str(chapter) + r'\.\d+\.\d+)\.', after, re.M)
        assert len(subheads) == len(set(subheads))
        tables = re.findall(r'^\*\*Bảng (' + str(chapter) + r'\.\d+)\.', after, re.M)
        assert tables == [f'{chapter}.{i}' for i in range(1, expected_tables[chapter]+1)]
        fenced = False
        for line in after.splitlines():
            if line.startswith('```'):
                fenced = not fenced
            elif not fenced:
                assert all(int(n) in numbers for n in re.findall(r'\[(\d{1,2})\](?!\()', line))
        assert not fenced and '[@R' not in after
        if chapter in (13, 14):
            start, end = (('13.2', '13.3') if chapter == 13 else ('14.2', '14.3'))
            section = lambda text: text.split('## ' + start + '. ', 1)[1].split('## ' + end + '. ', 1)[0]
            assert section(before) == section(after), 'Altered baseline quantitative section ' + start
        if chapter == 15:
            segment = lambda text: text.split('### 15.3.1.', 1)[1].split('### 15.3.3.', 1)[0]
            assert segment(before) == segment(after), 'Altered baseline metric limitations'
        for obsolete in ['Chưa có resume trận;', 'resume trận chưa được triển khai', 'Các thành phần này chưa tạo thành reconnect end-to-end', 'Route RECONNECT chưa được đăng ký trong ứng dụng']:
            assert obsolete not in after, (name, obsolete)
        texts[chapter] = after
        shutil.copy2(path, OUT / 'after' / name)
        records.append(dict(path=path.relative_to(ROOT).as_posix(), before_sha256=sha(before_path), after_sha256=sha(path),
                            before_lines=len(before.splitlines()), after_lines=len(after.splitlines()), tables=tables))
        patch.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='before/' + name, tofile='after/' + name))
    contributions = re.findall(r'^\| (C\d+) —', texts[14], re.M)
    limits = re.findall(r'^\| (L\d+) \|', texts[15], re.M)
    assert contributions == [f'C{i}' for i in range(1, 6)]
    assert limits == [f'L{i:02d}' for i in range(1, 14)]
    assert set(re.findall(r'\bL\d{2}\b', texts[16])).issubset(set(limits))
    assert 'Mở rộng và củng cố recovery đã triển khai' in texts[16]
    assert all(token in texts[17] for token in ['133/133', '84/84', '45/45', '171/171', '44 class', 'ngoài sandbox'])
    documents = [ROOT / 'report/chapters' / name for name in NAMES] + [ROOT / 'report/session-recovery/README.md', ROOT / 'report/session-recovery/08_CAP_NHAT_DANH_GIA_VA_KET_LUAN.md', OUT / 'README.md']
    links_checked = 0
    for doc in documents:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                assert (doc.parent / re.sub(r':\d+$', '', link.split('#')[0])).exists(), (doc, link)
                links_checked += 1
    (OUT / 'chapter-changes.patch').write_text(''.join(patch), encoding='utf-8')
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    revision = dict(task=8, date='2026-10-27', timezone='Asia/Saigon', chapters=records,
                    contributions=contributions, limitations=limits, new_tables=1, local_links_checked=links_checked,
                    java_sources_preserved=len(inventory), other_chapters_preserved=14, chapters_6_to_12_preserved=True,
                    figures_canonical_references_old_exports_and_manifest_preserved=True,
                    baseline_analysis_sections_preserved=['13.2', '14.2', '15.3.1-15.3.2'],
                    raw_evidence_files_verified=len(raw_checks), tests_rerun=False, new_measurements=False,
                    recovery_evidence=run.relative_to(ROOT).as_posix(),
                    validation='PASS: hashes, citations, headings, captions, C/L codes, links, baseline analysis and actual recovery summary')
    (OUT / 'revision-manifest.json').write_text(json.dumps(revision, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    checks = {p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'checksums.sha256.json'}
    (OUT / 'checksums.sha256.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', chapters=5, contributions=contributions, limitation_count=len(limits), local_links_checked=links_checked, source_files_preserved=len(inventory), raw_evidence_verified=len(raw_checks)), ensure_ascii=False))


if __name__ == '__main__':
    main()
