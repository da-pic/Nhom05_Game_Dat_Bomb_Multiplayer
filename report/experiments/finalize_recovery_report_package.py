"""Finalize audited recovery report artifacts and indexes; preserve code and historical evidence."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'report'
OUT = REPORT / 'final'
EVIDENCE = REPORT / 'evidence/recovery-report-task10-2026-10-27'
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert not (EVIDENCE / 'final-artifacts.json').exists(), 'Preserve this finalized export; use a new revision.'
    review = read(EVIDENCE / 'document-review.json')
    assert not review['errors'] and not review['warnings']
    docx = OUT / 'NhomXX_BombItMultiplayer_Report.docx'
    pdf = docx.with_suffix('.pdf')
    assert sha(docx) == review['docx_sha256'] and sha(pdf) == review['pdf_sha256']
    protected = read(EVIDENCE / 'protected-hashes.json')
    for rel, digest in protected.items():
        assert sha(ROOT / rel) == digest, ('Protected input changed', rel)
    # Completed historical result sets are immutable, even though the current report is replaced.
    preserved = []
    for task in (12, 13, 14):
        path = REPORT / f'evidence/task{task:02}-2026-10-26/checksums.sha256.json'
        rows = read(path)
        base = path.parent if task == 12 else ROOT
        for row in rows:
            assert sha(base / row['path']) == row['sha256'].lower(), row['path']
        preserved.append(dict(evidence=path.parent.relative_to(ROOT).as_posix(), files=len(rows)))
    run = REPORT / 'evidence/recovery-report-task03-20261027-200413'
    rows = read(run / 'checksums.sha256.json')
    assert len(rows) == 280
    for rel, digest in rows.items(): assert sha(run / rel) == digest, rel
    preserved.append(dict(evidence=run.relative_to(ROOT).as_posix(), files=len(rows)))
    inventory = read(run / 'source-inventory.json')
    assert len(inventory) == 219 and all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    for task in range(4, 10):
        directory = REPORT / f'evidence/recovery-report-task{task:02}-2026-10-27'
        rows = read(directory / 'checksums.sha256.json')
        for rel, digest in rows.items(): assert sha(directory / rel) == digest, (task, rel)
        preserved.append(dict(evidence=directory.relative_to(ROOT).as_posix(), files=len(rows)))
    # Source chapters and final/ share the same depth. Chapter-to-chapter links need their directory in the merged file.
    merged_path = OUT / 'BAO_CAO_DA_GHEP.md'
    merged = merged_path.read_text(encoding='utf-8')
    names = {p.name for p in (REPORT / 'chapters').glob('*.md')}
    adjusted = []
    def destination(match):
        target = match[1]
        if target.split('#')[0] in names:
            adjusted.append(target)
            return '](' + '../chapters/' + target + ')'
        return match[0]
    merged = re.sub(r'\]\(([^)]+)\)', destination, merged)
    merged_path.write_text(merged, encoding='utf-8')
    manifest = read(REPORT / 'report-manifest.json')
    for row in manifest['chapter_order']: assert sha(ROOT / row['path']) == row['sha256']
    pages = review['pages']
    manifest.update(status='recovery_report_exported_pending_group_confirmation', task='recovery-report-10', original_report_task=18, recovery_update_task=10,
                    report_updated_on='2026-10-27', next_task=None,
                    final_export=dict(docx=docx.relative_to(ROOT).as_posix(), pdf_preview=pdf.relative_to(ROOT).as_posix(),
                        merged_markdown=merged_path.relative_to(ROOT).as_posix(),
                        confirmation_checklist='report/final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md',
                        evidence=EVIDENCE.relative_to(ROOT).as_posix(), pages=pages, chapters=19, figures=15,
                        numbered_table_captions=86, actual_tables_including_cover=88, references=19,
                        embedded_image_panels=19, landscape_panel_pages=review['landscape_panel_pages'],
                        toc_fields_updated=3, docx_sha256=sha(docx), pdf_sha256=sha(pdf),
                        group_confirmation_pending=True, compilatio_performed=False, submitted=False),
                    novelty_covered=['State Delta Compression', 'Seamless Session Recovery'])
    manifest['figures']['note'] = 'Twelve current Mermaid diagrams and three benchmark figures embedded; two long recovery sequences each use three landscape panels. Original figures preserved.'
    dump(REPORT / 'report-manifest.json', manifest)
    # Replace the obsolete hand-written outline with titles actually present in the current chapters.
    index = ['# Mục lục báo cáo hiện hành — Bomb It Multiplayer', '',
             '**Revision 27/10/2026.** Giữ đủ 19 phần theo [Instruction.md, mục 8](../phancong/Instruction.md).',
             f'Bản xuất hiện hành: **{pages} trang, 15 hình, 86 bảng đánh số, 19 nguồn tham khảo**.',
             '[DOCX](final/NhomXX_BombItMultiplayer_Report.docx) · [PDF](final/NhomXX_BombItMultiplayer_Report.pdf) · '
             '[Manifest/hash](report-manifest.json) · [Checklist trước nộp](final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md).', '',
             'Nội dung bao gồm Delta Compression và Session Recovery có điều kiện trong lobby.',
             'Phân công ghi trước từng nội dung trong các chương; họ tên/MSSV và đóng góp cá nhân còn chờ nhóm xác nhận.',
             'Các tiểu mục dưới đây lấy trực tiếp từ chương nguồn; số trang chính thức nằm trong mục lục Word/PDF.', '']
    for row in manifest['chapter_order']:
        path = ROOT / row['path']
        text = path.read_text(encoding='utf-8')
        index += [f'## [{row["title"]}](chapters/{path.name})', '']
        for line in text.splitlines():
            if line.startswith('## '): index.append('- ' + line[3:])
        index.append('')
    (REPORT / '00_MUC_LUC_CHINH_THUC.md').write_text('\n'.join(index)+'\n', encoding='utf-8')
    readme = REPORT / 'README.md'
    text = readme.read_text(encoding='utf-8')
    text = text.replace('— đủ 19 phần, 15 hình, 86 bảng đánh số, 19 nguồn;',
                        f'— {pages} trang, đủ 19 phần, 15 hình, 86 bảng đánh số, 19 nguồn;')
    text = text.replace('- [Nhiệm vụ 1 — Hồ sơ khảo sát]',
                        'Các liên kết nhiệm vụ 1–18 bên dưới giữ mô tả ở mốc biên soạn ban đầu; '
                        'nội dung chương hiện đã cập nhật theo recovery. Xem hồ sơ cập nhật 1–10 để biết thay đổi mới.\n\n'
                        '- [Nhiệm vụ 1 — Hồ sơ khảo sát]', 1)
    readme.write_text(text, encoding='utf-8')
    link_count = 0
    documents = list(OUT.glob('*.md')) + [readme, REPORT / '00_MUC_LUC_CHINH_THUC.md',
        REPORT / 'session-recovery/README.md', REPORT / 'session-recovery/10_GHEP_VA_XUAT_BAO_CAO_CUOI.md', EVIDENCE / 'README.md']
    for path in documents:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).exists(), (path, target)
                link_count += 1
    # Old exports are independently accessible; historical checksums still describe their original content.
    before = EVIDENCE / 'before/report/final'
    assert sha(before / docx.name) == '9cd0cfced68db9f34de08b47d5b40a3a4730f80874caf578a282b32c89483311'
    assert sha(before / pdf.name) == 'ccf56877d69de6b8f9d8e6148ed1826e7d7464fb9360e1b6af3ff4ae2e621006'
    scripts = ['prepare_recovery_final_export.py', 'build_recovery_final_docx.py', 'recovery_diagram_layout.py',
               'paginate_recovery_report.ps1', 'review_recovery_final_report.py', 'finalize_recovery_report_package.py']
    for name in scripts: shutil.copy2(REPORT / 'experiments' / name, EVIDENCE / name)
    head = subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'status', '--short'], cwd=ROOT, text=True)
    (EVIDENCE / 'git-status.txt').write_text(status, encoding='utf-8')
    files = [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(OUT.iterdir()) if p.is_file()]
    result = dict(task='recovery-report-10', date='2026-10-27', revision=head,
                  source_working_tree_note='Includes earlier uncommitted technical recovery fixes; 219 Java hashes match tested inventory.',
                  final_files=files, pages=pages, chapters=19, figures=15, numbered_table_captions=86, references=19,
                  actual_tables_including_cover=88, image_panels=19, toc_fields=3,
                  chapter_hashes_verified=19, protected_input_files_verified=len(protected), java_sources_preserved=219,
                  preserved_evidence=preserved, old_exports_archived=True, final_local_links_checked=link_count,
                  merged_markdown_chapter_links_adjusted=len(adjusted), review_errors=[], review_warnings=[],
                  visual_review='Cover, TOC, all figure pages, recovery table samples, references and appendix reviewed through rendered page samples.',
                  python=platform.python_version(), packages={name: importlib.metadata.version(name) for name in
                    ['python-docx', 'lxml', 'markdown-it-py', 'pymupdf', 'Pillow']},
                  word_version=read(EVIDENCE / 'word-pagination.json')['word_version'],
                  tests_or_benchmarks_run=False, compilatio_performed=False, submitted=False, pushed=False)
    dump(EVIDENCE / 'final-artifacts.json', result)
    # Include the actual deliverables and export scripts alongside evidence checksums.
    paths = set(p for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'checksums.sha256.json')
    paths.update(p for p in OUT.iterdir() if p.is_file())
    paths.update([REPORT / 'report-manifest.json', readme, REPORT / '00_MUC_LUC_CHINH_THUC.md',
                  REPORT / 'session-recovery/README.md', REPORT / 'session-recovery/10_GHEP_VA_XUAT_BAO_CAO_CUOI.md'])
    paths.update(REPORT / 'experiments' / name for name in scripts)
    dump(EVIDENCE / 'checksums.sha256.json', [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in sorted(paths)])
    print(json.dumps(dict(status='PASS', pages=pages, chapters=19, figures=15, tables=86, references=19,
          source_preserved=219, evidence_files_verified=sum(row['files'] for row in preserved), final_links=link_count,
          docx=str(docx), pdf=str(pdf)), ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
