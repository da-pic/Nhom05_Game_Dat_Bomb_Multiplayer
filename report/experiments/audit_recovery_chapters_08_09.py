"""Audit task-5 prose, diagrams and preservation without rewriting prior evidence."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task05-2026-10-27'
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'revision-manifest.json').exists(), 'Preserve existing audit; use a new revision'
    old = json.loads((OUT / 'before-hashes.json').read_text(encoding='utf-8'))
    chapters = ['report/chapters/08_KIEN_TRUC_HE_THONG.md', 'report/chapters/09_THIET_KE_GIAO_TIEP_MANG.md']
    rendered = json.loads((OUT / 'diagram-manifest.json').read_text(encoding='utf-8'))
    assert len(rendered) == 5
    allowed = set(chapters)
    figure_paths = []
    for row in rendered:
        for key in ['source', 'svg', 'png']:
            path = row[key].replace('\\', '/')
            assert (ROOT / path).exists()
            allowed.add(path)
            figure_paths.append(path)
        root = ET.parse(ROOT / row['svg']).getroot()
        assert root.tag.endswith('svg') and root.get('viewBox')
        with Image.open(ROOT / row['png']) as image:
            assert image.size == (row['width'], row['height'])
            image.verify()
    continuous = 'report/figures/rendered/08_02_thread_va_queue_continuous.png'
    allowed.add(continuous)
    figure_paths.append(continuous)
    for path, digest in old.items():
        if path not in allowed:
            assert sha(ROOT / path) == digest, path
    inv = json.loads((ROOT / 'report/evidence/recovery-report-task03-20261027-200413/source-inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / row['path']) == row['sha256'] for row in inv)
    sources = {p.as_posix(): p.read_text(encoding='utf-8-sig').strip() for p in (ROOT / 'report/figures').rglob('*.mmd')}
    catalogue = json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))
    numbers = {row['final_number'] for row in catalogue['sources']}
    records, differences = [], []
    (OUT / 'after').mkdir(exist_ok=True)
    for name in chapters:
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        assert sha(path) != old[name]
        before = (OUT / 'before' / name).read_text(encoding='utf-8')
        differences.extend(difflib.unified_diff(before.splitlines(keepends=True), text.splitlines(keepends=True), fromfile='before/' + name, tofile='after/' + name))
        fenced = False
        for line in text.splitlines():
            if line.startswith('```'):
                fenced = not fenced
            elif not fenced:
                assert all(int(number) in numbers for number in re.findall(r'\[(\d{1,2})\](?!\()', line))
        assert not fenced and '[@R' not in text
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in link and not link.startswith('#'):
                assert (path.parent / re.sub(r':\d+$', '', link.split('#')[0])).exists(), (name, link)
        chapter = str(int(path.name[:2]))
        captions = {}
        for label in ['Bảng', 'Hình']:
            values = re.findall(r'^\*\*' + label + ' (' + chapter + r'\.\d+)\.', text, re.M)
            assert values == [f'{chapter}.{i}' for i in range(1, len(values)+1)], (name, label, values)
            captions[label] = values
        blocks = re.findall(r'```mermaid\n(.*?)\n```', text, re.S)
        assert len(blocks) == len(captions['Hình'])
        matches = []
        for block in blocks:
            candidates = [p for p, body in sources.items() if body == block.strip()]
            assert len(candidates) == 1, (name, candidates)
            matches.append(Path(candidates[0]).relative_to(ROOT).as_posix())
        records.append(dict(path=name, before_sha256=old[name], after_sha256=sha(path), captions=captions, mermaid_sources=matches))
    for name in chapters + figure_paths:
        path = ROOT / name
        dest = OUT / 'after' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    # Also keep textual changes for the two modified diagrams; added files are in after/.
    for name in figure_paths:
        if name.endswith('.mmd') and name in old:
            before = (OUT / 'before' / name).read_text(encoding='utf-8')
            after = (ROOT / name).read_text(encoding='utf-8')
            differences.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='before/' + name, tofile='after/' + name))
    (OUT / 'chapter-and-diagram-changes.patch').write_text(''.join(differences), encoding='utf-8')
    for doc in [ROOT / 'report/session-recovery/README.md', ROOT / 'report/session-recovery/05_CAP_NHAT_KIEN_TRUC_PROTOCOL_SO_DO.md', OUT / 'README.md']:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in link and not link.startswith('#'):
                assert (doc.parent / re.sub(r':\d+$', '', link.split('#')[0])).exists(), (doc, link)
    manifest = dict(task=5, date='2026-10-27', timezone='Asia/Saigon',
                    head=subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip(),
                    chapters=records, diagrams_rendered=5, existing_diagrams_updated=2, new_diagrams=3,
                    inline_mermaid_verified=10, images_visually_reviewed=5,
                    render_context='Local cached Mermaid, Chrome headless outside sandbox with approval, no upload',
                    unchanged_java_sources=len(inv), unchanged_other_chapters=17, chapters_6_7_preserved=True,
                    old_exports_and_canonical_references_preserved=True, tests_rerun=False,
                    source_test_evidence='report/evidence/recovery-report-task03-20261027-200413',
                    changed_or_added_files={name: sha(ROOT / name) for name in sorted(allowed)},
                    pending='Implementation chapter 10; export DOCX/PDF only after remaining revision tasks')
    (OUT / 'revision-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    shutil.copy2(ROOT / 'target/recovery-report-task05-render.log', OUT / 'render-run.log')
    for script in ['render_recovery_diagrams.py', 'audit_recovery_chapters_08_09.py']:
        shutil.copy2(ROOT / 'report/experiments' / script, OUT / script)
    checks = {p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'checksums.sha256.json'}
    (OUT / 'checksums.sha256.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', chapters=2, diagrams_rendered=5, matching_mermaid_blocks=10, unchanged_sources=len(inv), evidence_files=len(checks)), ensure_ascii=False))


if __name__ == '__main__':
    main()
