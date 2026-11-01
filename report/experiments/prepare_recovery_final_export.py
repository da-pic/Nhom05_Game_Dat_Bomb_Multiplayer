"""Prepare current report inputs and a recovery-aware builder, preserving historical scripts."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'report'
EVIDENCE = REPORT / 'evidence/recovery-report-task10-2026-10-27'
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))
from markdown_it import MarkdownIt


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert not (EVIDENCE / 'final-artifacts.json').exists(), 'Preserve a completed export; use a new revision.'
    parser = MarkdownIt('commonmark').enable('table')
    chapters = sorted((REPORT / 'chapters').glob('*.md'))
    assert [int(p.name[:2]) for p in chapters] == list(range(1, 20))
    catalog = json.loads((REPORT / 'references/sources.json').read_text(encoding='utf-8'))
    sources = {s['final_number']: s for s in catalog['sources']}
    assert set(sources) == set(range(1, 20))
    figures, tables, first, diagrams, links, widths = [], [], [], [], 0, []
    for path in chapters:
        number = int(path.name[:2])
        text = path.read_text(encoding='utf-8')
        assert text.startswith(f'# {number}. ')
        tokens = parser.parse(text)
        current_table_widths = []
        for i, token in enumerate(tokens):
            if token.type == 'paragraph_open':
                plain = re.sub(r'^\*+|\*+$', '', tokens[i+1].content.strip())
                if re.match(r'^Hình \d+\.\d+\.', plain):
                    figures.append(plain)
                if re.match(r'^Bảng [\dA-E]+\.\d+\.', plain):
                    tables.append(plain)
            if token.type == 'fence' and token.info == 'mermaid':
                candidates = [p for p in (REPORT / 'figures').rglob('*.mmd')
                              if p.read_text(encoding='utf-8-sig').strip() == token.content.strip()]
                assert len(candidates) == 1, (path, token.map)
                source = candidates[0]
                png = REPORT / 'figures/rendered' / (source.stem + '.png')
                assert png.exists()
                diagrams.append(dict(source=source.relative_to(ROOT).as_posix(), source_sha256=sha(source),
                                     png=png.relative_to(ROOT).as_posix(), png_sha256=sha(png)))
            if token.type == 'table_open':
                current_table_widths = []
            if token.type == 'tr_open':
                count = 0
                for cell in tokens[i+1:]:
                    if cell.type == 'tr_close': break
                    if cell.type in ('th_open', 'td_open'): count += 1
                current_table_widths.append(count)
            if token.type == 'table_close':
                assert len(set(current_table_widths)) == 1, (path.name, current_table_widths)
                widths.append(current_table_widths[0])
        fenced = False
        for line in text.splitlines():
            if line.startswith('```'):
                fenced = not fenced
                continue
            if not fenced and number <= 17:
                for value in re.findall(r'\[(\d{1,2})\](?!\()', line):
                    n = int(value)
                    assert n in sources
                    if n not in first: first.append(n)
                for n, url in re.findall(r'\[\[(\d+)\]\]\(([^)]+)\)', line):
                    source = sources[int(n)]
                    assert url.split('#')[0] in {source['url'].split('#')[0], source['verified_content_url'].split('#')[0]}
        assert not fenced
        for href in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in href and not href.startswith('#'):
                assert (path.parent / href.split('#')[0]).exists(), (path.name, href)
                links += 1
    assert first == list(range(1, 20))
    assert len(figures) == 15 and len(diagrams) == 12
    assert len(tables) == len(set(re.match(r'Bảng ([\dA-E]+\.\d+)', t)[1] for t in tables))
    assert len(figures) == len(set(re.match(r'Hình (\d+\.\d+)', t)[1] for t in figures))
    manifest = json.loads((REPORT / 'report-manifest.json').read_text(encoding='utf-8'))
    manifest.update(status='recovery_report_ready_for_final_export', recovery_update_task=10,
                    chapter_order=[dict(number=int(p.name[:2]), path=p.relative_to(ROOT).as_posix(),
                                        title=p.read_text(encoding='utf-8').splitlines()[0][2:], sha256=sha(p)) for p in chapters],
                    references=dict(catalogue='report/references/sources.json', chapter='report/chapters/18_TAI_LIEU_THAM_KHAO.md',
                                    active_number_field='final_number', sources=19, citation_order=first),
                    figures=dict(mermaid_sources=[d['source'] for d in diagrams], count=15,
                                 note='Twelve current Mermaid diagrams plus three measured-result figures; diagram originals preserved.'),
                    previous_export=dict(evidence='report/evidence/task18-2026-10-26',
                                         archived_at='report/evidence/recovery-report-task10-2026-10-27/before/report/final'),
                    next_task=None)
    dump(REPORT / 'report-manifest.json', manifest)
    dump(EVIDENCE / 'input-review.json', dict(chapters=19, figures=figures, tables=tables,
         numbered_tables=len(tables), actual_tables_including_cover=len(widths), diagrams=diagrams,
         sources=19, citation_order=first, local_links_checked=links,
         validation='PASS: source hashes, 19 chapters, active citations/URLs, diagram matching, local links and tables'))
    # Copy the proven builder, changing only the current revision's export behavior.
    script = (REPORT / 'experiments/build_final_docx.py').read_text(encoding='utf-8')
    script = script.replace("EVIDENCE=REPORT/'evidence/task18-2026-10-26'", "EVIDENCE=REPORT/'evidence/recovery-report-task10-2026-10-27'")
    script = script.replace('from docx.enum.text import WD_ALIGN_PARAGRAPH',
                            'from docx.enum.text import WD_ALIGN_PARAGRAPH\nfrom docx.enum.section import WD_SECTION_START, WD_ORIENT')
    start = script.index('def edit(text,chapter):')
    end = script.index('\nfigures=[];', start)
    script = script[:start] + '''def edit(text,chapter):
    before=text
    if chapter==1:
        text=text.replace(' — bản thảo nội dung cập nhật ngày 27/10/2026.', ' — nội dung cập nhật ngày 27/10/2026.')
        text=text.replace('Mục lục, danh mục hình/bảng và số trang cần được cập nhật khi ghép/xuất lại DOCX/PDF ở nhiệm vụ cập nhật 10.\\nBản xuất trước đợt cập nhật Session Recovery vẫn là revision cũ, chưa thay cho nội dung các chương hiện tại.',
                          'Bản xuất gồm mục lục, danh mục hình/bảng và số trang đã cập nhật. Thông tin bìa còn chờ nhóm xác nhận.')
    if chapter==19:
        text=text.replace('Nhiệm vụ cập nhật 10 cần ghép các hình đó, dựng lại mục lục/danh mục, cập nhật trích dẫn và kiểm tra ngắt trang/caption\\ntrên DOCX/PDF mới. Bản DOCX/PDF trước recovery chưa đại diện cho nội dung các chương đã sửa.',
                          'Các hình recovery đã được ghép vào DOCX/PDF cùng mục lục, danh mục và trích dẫn cập nhật.\\nSau khi nhóm sửa bìa/nội dung, cần cập nhật lại trường Word và kiểm tra ngắt trang/caption trước khi nộp.')
    if before!=text:
        edits.append(dict(chapter=chapter,kind='resolved_current_export_status_only',
                          before_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=hashlib.sha256(text.encode()).hexdigest()))
    return text
''' + script[end:]
    # Plain numeric links in bibliography are labels, not secondary reference links.
    script = script.replace("assert len(figures)==12,(len(figures),figures)", "assert len(figures)==15,(len(figures),figures)")
    # A page-break-only paragraph can spill onto an otherwise empty page after a full table.
    # Put the break on the heading itself; Keywords follows Abstract on the same page.
    old_heading = "if current_chapter>1:doc.add_page_break()\n                p=doc.add_paragraph(style='Heading 1');bookmark(p,'chapter_'+str(current_chapter))"
    new_heading = "p=doc.add_paragraph(style='Heading 1');bookmark(p,'chapter_'+str(current_chapter))\n                if current_chapter not in (1,3):p.paragraph_format.page_break_before=True"
    assert old_heading in script
    script = script.replace(old_heading,new_heading)
    # Keep a repeated header with the first data row, rather than leaving only a header at the page foot.
    header_line = "if i==0:\n                shade=OxmlElement('w:shd')"
    assert header_line in script
    script = script.replace(header_line, "if i==0:\n                p.paragraph_format.keep_with_next=True\n                shade=OxmlElement('w:shd')")
    script = script.replace("doc.core_properties.title='Bomb It Multiplayer — Thiết kế và đánh giá đồng bộ trạng thái theo delta'",
                            "doc.core_properties.title='Bomb It Multiplayer — Đồng bộ trạng thái theo delta và phục hồi phiên chơi'")
    script = script.replace("'TCP; multiplayer; state delta compression; prediction; reconciliation'",
                            "'TCP; multiplayer; state delta compression; session recovery; server authoritative'")
    old = "add_image(REPORT/'figures/rendered'/f'{source.stem}.png')\n                assert pending_caption,source\n                caption(pending_caption,True);pending_caption=None"
    new = "assert pending_caption,source\n                add_diagram(source, pending_caption)\n                pending_caption=None"
    assert old in script
    script = script.replace(old, new)
    marker = '\ndef add_table(rows):'
    assert marker in script
    layout = (REPORT / 'experiments/recovery_diagram_layout.py').read_text(encoding='utf-8')
    script = script.replace(marker, '\n' + layout + marker)
    script = script.replace("note='Source chapter Markdown preserved; editorial phrasing applied only to exported assembly. Word pagination and field update follow.'",
                            "note='Current 19 source chapters preserved. Only obsolete export-status sentences resolved in assembly; long recovery sequences split into landscape panels for readability.'")
    (REPORT / 'experiments/build_recovery_final_docx.py').write_text(script, encoding='utf-8')
    print(json.dumps(dict(status='PASS', chapters=19, references=19, figures=len(figures),
                          tables=len(tables), actual_tables=len(widths), links=links), ensure_ascii=False))


if __name__ == '__main__':
    main()
