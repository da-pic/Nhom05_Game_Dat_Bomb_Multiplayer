"""Audit report-only task 4; preserve chapter edits separately from old exports."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task04-2026-10-27'
NAMES = ['06_DINH_NGHIA_BAI_TOAN.md', '07_GIAI_PHAP_DE_XUAT.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'revision-manifest.json').exists(), 'Keep existing audit; create another revision for further edits'
    protected = json.loads((OUT / 'before-hashes.json').read_text(encoding='utf-8'))
    changed = {'report/chapters/' + name for name in NAMES}
    for path, digest in protected.items():
        if path not in changed:
            assert sha(ROOT / path) == digest, path
    inventory = json.loads((ROOT / 'report/evidence/recovery-report-task03-20261027-200413/source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    refs = json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))
    reference_numbers = {row['final_number'] for row in refs['sources']}
    records, patch = [], []
    (OUT / 'after').mkdir(exist_ok=True)
    for name in NAMES:
        path = ROOT / 'report/chapters' / name
        before_path = OUT / 'before' / name
        before, after = [p.read_text(encoding='utf-8') for p in (before_path, path)]
        assert sha(before_path) == protected[path.relative_to(ROOT).as_posix()]
        assert before != after
        shutil.copy2(path, OUT / 'after' / name)
        patch.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='before/' + name, tofile='after/' + name))
        fenced = False
        for line in after.splitlines():
            if line.startswith('```'):
                fenced = not fenced
            if not fenced:
                for number in re.findall(r'\[(\d{1,2})\](?!\()', line):
                    assert int(number) in reference_numbers, (name, number)
        assert not fenced, 'Unbalanced code fence'
        links = re.findall(r'\]\(([^)]+)\)', after)
        for link in links:
            if '://' not in link and not link.startswith('#'):
                target = re.sub(r':\d+$', '', link.split('#')[0])
                assert (path.parent / target).exists(), (name, link)
        chapter = name[:2].lstrip('0')
        captions = {}
        for label in ['Bảng', 'Hình', 'Thuật toán']:
            values = re.findall(r'^\*\*' + label + r' (' + chapter + r'\.\d+)\.', after, re.M)
            assert len(values) == len(set(values)), (name, label, values)
            assert values == [f'{chapter}.{i}' for i in range(1, len(values)+1)], (name, label, values)
            captions[label] = values
        if chapter == '6':
            codes = re.findall(r'^\| (FR\d+) \|', after, re.M)
            assert codes == [f'FR{i:02d}' for i in range(1, 16)]
            assert '### 6.2.7.' in after and 'NFR07' in after and 'A04' in after
        else:
            assert '## 7.8.' in after and '### 7.4.4.' in after
            assert all(token in after for token in ['WAITING_ACK', 'WAITING_FULL', '14.000', '2.500', '4.000', '1.500'])
        assert '[@R' not in after, 'Unresolved citation placeholders'
        records.append(dict(path=path.relative_to(ROOT).as_posix(), before_sha256=sha(before_path), after_sha256=sha(path),
                            before_lines=len(before.splitlines()), after_lines=len(after.splitlines()),
                            local_links_checked=sum('://' not in link for link in links), captions=captions))
    for doc in [ROOT / 'report/session-recovery/04_CAP_NHAT_PHAN_6_7.md', ROOT / 'report/session-recovery/README.md']:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                assert (doc.parent / re.sub(r':\d+$', '', link.split('#')[0])).exists(), (doc, link)
    (OUT / 'chapter-changes.patch').write_text(''.join(patch), encoding='utf-8')
    git_args = ['git', '-c', f'safe.directory={ROOT.as_posix()}']
    manifest = dict(date='2026-10-27', timezone='Asia/Saigon', task=4,
                    base_commit=subprocess.check_output(git_args+['rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip(),
                    chapters=records, unchanged_java_sources=len(inventory), unchanged_other_chapters=17,
                    unchanged_final_exports=4, unchanged_canonical_references=True,
                    historical_report_manifest_unchanged=True, tests_rerun=False,
                    evidence_used='report/evidence/recovery-report-task03-20261027-200413',
                    validation='PASS: links, citations, fences, FR numbering, caption sequences, source and unrelated report hashes',
                    pending='Update chapters 8-9 next; remaining chapters and DOCX/PDF still describe prior report revision.')
    (OUT / 'revision-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'checksums.sha256.json').write_text(json.dumps({p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'checksums.sha256.json'}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == '__main__':
    main()
