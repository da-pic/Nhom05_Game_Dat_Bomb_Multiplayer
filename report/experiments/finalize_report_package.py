"""Record final report artifacts and verify preserved evidence without running the game."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'report/evidence/task18-2026-10-26'
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    review = read(EVIDENCE / 'document-review.json')
    assert not review['errors'] and not review['warnings'], review
    docx = ROOT / 'report/final/NhomXX_BombItMultiplayer_Report.docx'
    pdf = docx.with_suffix('.pdf')
    assert digest(docx) == review['docx_sha256']
    assert digest(pdf) == review['pdf_sha256']
    manifest_path = ROOT / 'report/report-manifest.json'
    manifest = read(manifest_path)
    for row in manifest['chapter_order']:
        assert digest(ROOT / row['path']) == row['sha256'], row['path']

    preserved = []
    for task in (12, 13, 14):
        checksum_path = ROOT / f'report/evidence/task{task:02}-2026-10-26/checksums.sha256.json'
        rows = read(checksum_path)
        # Task 12 records paths relative to its evidence directory; later tasks use repo paths.
        base = checksum_path.parent if task == 12 else ROOT
        for row in rows:
            assert digest(base / row['path']) == row['sha256'].lower(), row['path']
        preserved.append({'task': task, 'files_verified': len(rows), 'mismatches': []})

    for name in ('docx-dependencies-install.log', 'docx-dependencies-install-sandbox.log'):
        source = ROOT / 'report' / name
        destination = EVIDENCE / name
        if source.exists():
            assert not destination.exists(), destination
            source.rename(destination)

    final_paths = sorted((ROOT / 'report/final').glob('*'))
    final_files = [
        {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)}
        for p in final_paths if p.is_file()
    ]
    manifest.update({
        'status': 'docx_assembled_pending_group_confirmation', 'task': 18, 'next_task': None,
        'final_export': {
            'docx': docx.relative_to(ROOT).as_posix(), 'pdf_preview': pdf.relative_to(ROOT).as_posix(),
            'merged_markdown': 'report/final/BAO_CAO_DA_GHEP.md',
            'confirmation_checklist': 'report/final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md',
            'evidence': EVIDENCE.relative_to(ROOT).as_posix(), 'pages': review['pages'],
            'chapters': len(review['headings']), 'figures': review['figures'],
            'numbered_table_captions': review['numbered_table_captions'], 'references': 14,
            'toc_fields_updated': review['toc_fields'],
            'docx_sha256': digest(docx), 'pdf_sha256': digest(pdf),
            'group_confirmation_pending': True, 'compilatio_performed': False, 'submitted': False,
        },
    })
    manifest['figures']['note'] = (
        'Nine Mermaid diagrams rendered locally to report/figures/rendered; '
        'three experiment PNGs embedded. TOC/list of figures/list of tables/page fields updated in Word.'
    )
    write(manifest_path, manifest)
    revision = subprocess.check_output(
        ['git', '-c', f'safe.directory={ROOT.as_posix()}', 'rev-parse', 'HEAD'], cwd=ROOT, text=True
    ).strip()
    tracked_changes = subprocess.check_output(
        ['git', '-c', f'safe.directory={ROOT.as_posix()}', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True
    ).splitlines()
    assert not tracked_changes, tracked_changes
    packages = {name: importlib.metadata.version(name) for name in
                ('python-docx', 'lxml', 'markdown-it-py', 'pymupdf')}
    output = {
        'task': 18, 'date': '2026-10-26', 'revision': revision,
        'tracked_changes_vs_HEAD': tracked_changes, 'final_files': final_files,
        'chapter_source_hashes_verified': len(manifest['chapter_order']), 'preserved_evidence': preserved,
        'review_errors': review['errors'], 'review_warnings': review['warnings'],
        'pages': review['pages'], 'chapters': len(review['headings']),
        'figures': review['figures'], 'numbered_table_captions': review['numbered_table_captions'],
        'actual_tables_including_cover': review['actual_tables_including_cover'],
        'toc_fields': review['toc_fields'], 'sampled_preview_pages': review['sampled_pages'],
        'python': platform.python_version(), 'packages': packages,
        'word_version': '16.0', 'chrome_version': '155.0.8059.85', 'mermaid_major_version': 11,
        'mermaid_bundle_sha256': digest(ROOT / 'target/report-render-assets/mermaid.min.js'),
        'new_game_tests_or_benchmarks_run': False,
        'compilatio_performed': False, 'submitted': False,
    }
    write(EVIDENCE / 'final-artifacts.json', output)
    evidence_files = [p for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'checksums.sha256.json']
    files = set(evidence_files + final_paths + [manifest_path, ROOT / 'report/README.md',
                ROOT / 'report/00_MUC_LUC_CHINH_THUC.md'])
    files.update((ROOT / 'report/figures/rendered').glob('*'))
    for name in ('render_report_diagrams.py', 'build_final_docx.py', 'paginate_report.ps1',
                 'review_final_report.py', 'finalize_report_package.py'):
        files.add(ROOT / 'report/experiments' / name)
    write(EVIDENCE / 'checksums.sha256.json', [
        {'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)}
        for p in sorted(files) if p.is_file()
    ])
    print(json.dumps({'pages': review['pages'], 'chapters': len(review['headings']),
                      'errors': [], 'source_chapters_preserved': 19,
                      'preserved_evidence_files': sum(r['files_verified'] for r in preserved),
                      'final_files': final_files}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
