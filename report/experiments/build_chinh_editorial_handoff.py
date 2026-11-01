"""Build only Chinh's revised passages as one editable DOCX; never rebuild the full report."""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))
from docx import Document
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from markdown_it import MarkdownIt
from PIL import Image
from lxml import etree

BASE = 'CHINH_CHINH_SUA_BAO_CAO_2026-10-28'
MARKDOWN = ROOT / 'report/revisions' / (BASE + '.md')
DOCX = MARKDOWN.with_suffix('.docx')
EVIDENCE = ROOT / 'report/evidence/chinh-editorial-handoff-2026-10-28'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def verify_evidence():
    verified = []
    for name in ('task12-2026-10-26', 'task13-2026-10-26', 'recovery-report-task03-20261027-200413'):
        directory = ROOT / 'report/evidence' / name
        rows = load(directory / 'checksums.sha256.json')
        if isinstance(rows, dict):
            for rel, digest in rows.items(): assert sha(directory / rel) == digest
        else:
            base = directory if name.startswith('task12') else ROOT
            for row in rows: assert sha(base / row['path']) == row['sha256'].lower()
        verified.append(dict(directory=directory.relative_to(ROOT).as_posix(), files=len(rows)))
    run = ROOT / 'report/evidence/recovery-report-task03-20261027-200413'
    inventory = load(run / 'source-inventory.json')
    assert len(inventory) == 219 and all(sha(ROOT / row['path']) == row['sha256'] for row in inventory)
    counts = {'RuntimeContractTest': 1, 'MovementFeatureTest': 1, 'MovementBalanceTest': 4, 'MovementDemoTest': 8,
              'RespawnPredictionTest': 2, 'DeltaCompressionTest': 1, 'RecoveryInputTest': 2, 'RecoveryGameplayIntegrationTest': 8}
    rows = list(csv.DictReader((run / 'class-results.csv').open(encoding='utf-8-sig', newline='')))
    selected = []
    for short, count in counts.items():
        matches = [row for row in rows if row['name'].split('.')[-1] == short]
        assert len(matches) == 1
        row = matches[0]
        assert int(row['tests']) == count and all(int(row[k]) == 0 for k in ('failures', 'errors', 'skipped'))
        assert (run / 'surefire' / row['xml']).exists()
        selected.append(row)
    summary = load(run / 'junit-summary.json')
    assert summary['totals'] == dict(tests=171, failures=0, errors=0, skipped=0) and summary['classes'] == 44
    markers = list(csv.DictReader((run / 'case-results.csv').open(encoding='utf-8-sig', newline='')))
    marker = next(json.loads(row['values_json']) for row in markers if row['scenario'] == 'multi_input_bomb')
    assert marker['cycles'] == marker['full_replica_equal'] == marker['delta_after_full'] == 3
    delta = ROOT / 'report/evidence/task13-2026-10-26'
    rows = list(csv.DictReader((delta / 'all-runs.csv').open(encoding='utf-8-sig', newline='')))
    assert len(rows) == 35
    d1 = [row for row in rows if row['scenario'] != 'D0-v2']
    assert len(d1) == 30 and sum(int(row['equality_ticks']) for row in d1) == 18000
    summaries = list(csv.DictReader((delta / 'summary.csv').open(encoding='utf-8-sig', newline='')))
    assert all(int(row['repetitions']) == 5 for row in summaries)
    d1_reductions = [float(row['reduction_percent']) for row in summaries if row['scenario'] != 'D0-v2']
    assert round(min(d1_reductions), 2) == 35.98 and round(max(d1_reductions), 2) == 97.54
    return dict(verified_sets=verified, java_inventory_verified=219, selected_class_results=selected,
                d1_equality_ticks=18000, d1_runs=30, all_delta_scenario_runs=35, multi_input_marker=marker)


def main():
    assert not (EVIDENCE / 'revision-manifest.json').exists(), 'Preserve a completed handoff; use another revision.'
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    protected = {p.relative_to(ROOT).as_posix(): sha(p) for folder in ('src', 'report/chapters', 'report/final', 'report/references')
                 for p in (ROOT / folder).rglob('*') if p.is_file()}
    before = MARKDOWN.read_text(encoding='utf-8')
    short = (ROOT / 'report/revisions/2026-10-28_RUT_GON_5_2_5_3.md').read_text(encoding='utf-8')
    short = short.split('### 5.3.4.', 1)[0].rstrip()
    addition = '''### 5.2.4. Hitbox và va chạm trên tile map

Hitbox là vùng hình học đại diện phần không gian nhân vật chiếm chỗ. Va chạm phải xét toàn vùng này với vật cản và biên bản đồ, không chỉ ô chứa một điểm đại diện. Mô hình của Bomb It dùng hitbox chữ nhật trên lưới tile; chi tiết xử lý biên và bước di chuyển trình bày tại 10.4.3.

'''
    short = short.replace('> **Phân công: TV2 phụ trách mục 5.3;', addition + '> **Phân công: TV2 phụ trách mục 5.3;', 1)
    short += '\n\n**5.3.4:** giữ Bảng 5.1 và lời kết ngắn trong bản rút gọn đã có, không thêm bảng so sánh trùng.\n'
    catalog = load(ROOT / 'report/references/sources.json')
    sources = {row['final_number']: row for row in catalog['sources']}
    content = before.replace('<!-- INSERT_SHORT_THEORY -->', short)
    used = sorted(set(int(n) for n in re.findall(r'\[(\d{1,2})\](?!\()', content)))
    bibliography = (ROOT / 'report/REFERENCES.md').read_text(encoding='utf-8')
    entries = {int(m[1]): m[0] for m in re.finditer(r'^\[(\d+)\] .*? <!-- R\d{2} -->$', bibliography, re.M)}
    assert used == [2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
    content = content.replace('<!-- INSERT_USED_REFERENCES -->', '\n\n'.join(entries[n] for n in used))
    # The reused theory excerpt sits inside handoff section 1, rather than introducing two extra top-level sections.
    content = re.sub(r'(?m)^#{2,4} (5\.[23](?:\.\d+)?\.) ',
                     lambda m: '#' * min(4, len(m[1].rstrip('.').split('.')) + 1) + ' ' + m[1] + ' ', content)
    assert '<!-- INSERT_' not in content
    MARKDOWN.write_text(content, encoding='utf-8')
    evidence = verify_evidence()
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21); section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0); section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.3); section.right_margin = Cm(2.0)
    for name in ('Normal', 'List Bullet', 'List Number'):
        style = doc.styles[name]; style.font.name = 'Times New Roman'; style.font.size = Pt(12)
        style.paragraph_format.line_spacing = 1.1; style.paragraph_format.space_after = Pt(6)
    for level, size in ((1, 17), (2, 14), (3, 12.5), (4, 12)):
        style = doc.styles[f'Heading {level}']; style.font.name = 'Times New Roman'; style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string('17324D'); style.paragraph_format.keep_with_next = True
    code = doc.styles.add_style('Handoff Code', WD_STYLE_TYPE.PARAGRAPH)
    code.font.name = 'Consolas'; code.font.size = Pt(9)
    code.paragraph_format.space_after = Pt(2); code.paragraph_format.line_spacing = 1.0
    note = doc.styles.add_style('Handoff Note', WD_STYLE_TYPE.PARAGRAPH)
    note.font.name = 'Times New Roman'; note.font.size = Pt(10)
    note.font.color.rgb = RGBColor.from_string('596579'); note.paragraph_format.space_after = Pt(7)
    header = section.header.paragraphs[0]; header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.add_run('CHINH | NỘI DUNG CHỈNH SỬA ĐỂ GHÉP | 28/10/2026').font.size = Pt(9)
    footer = section.footer.paragraphs[0]; footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run('Trang ')
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE'); footer._p.append(field)
    update = OxmlElement('w:updateFields'); update.set(qn('w:val'), 'true'); doc.settings.element.append(update)
    tokens = MarkdownIt('commonmark').enable('table').parse(content)
    image_count = 0

    def hyperlink(paragraph, label, target, size=None):
        element = OxmlElement('w:hyperlink')
        element.set(qn('r:id'), doc.part.relate_to(target, RT.HYPERLINK, is_external=True))
        run = OxmlElement('w:r'); props = OxmlElement('w:rPr')
        color = OxmlElement('w:color'); color.set(qn('w:val'), '245785'); props.append(color)
        if size:
            font_size = OxmlElement('w:sz'); font_size.set(qn('w:val'), str(int(size*2))); props.append(font_size)
        run.append(props); text = OxmlElement('w:t'); text.text = label; run.append(text)
        element.append(run); paragraph._p.append(element)

    def inline(paragraph, children, size=None):
        bold = italic = False; href = None
        for token in children or []:
            if token.type == 'strong_open': bold = True
            elif token.type == 'strong_close': bold = False
            elif token.type == 'em_open': italic = True
            elif token.type == 'em_close': italic = False
            elif token.type == 'link_open': href = token.attrGet('href')
            elif token.type == 'link_close': href = None
            elif token.type in ('softbreak', 'hardbreak'): paragraph.add_run(' ' if token.type == 'softbreak' else '\n')
            elif token.type in ('text', 'code_inline'):
                if href: hyperlink(paragraph, token.content, href, size); continue
                run = paragraph.add_run(token.content); run.bold = bold; run.italic = italic
                if size: run.font.size = Pt(size)
                if token.type == 'code_inline': run.font.name = 'Consolas'; run.font.size = Pt(size or 10)

    i = 0; lists = []; quotes = 0
    while i < len(tokens):
        token = tokens[i]; kind = token.type
        if kind in ('bullet_list_open', 'ordered_list_open'): lists.append(kind); i += 1; continue
        if kind in ('bullet_list_close', 'ordered_list_close'): lists.pop(); i += 1; continue
        if kind == 'blockquote_open': quotes += 1; i += 1; continue
        if kind == 'blockquote_close': quotes -= 1; i += 1; continue
        if kind == 'heading_open':
            paragraph = doc.add_paragraph(style=f'Heading {min(int(token.tag[1:]), 4)}')
            inline(paragraph, tokens[i+1].children); i += 3; continue
        if kind == 'paragraph_open':
            children = tokens[i+1].children or []
            images = [t for t in children if t.type == 'image']
            if images:
                for image in images:
                    path = (MARKDOWN.parent / image.attrGet('src')).resolve()
                    assert path.exists()
                    with Image.open(path) as picture: w, h = picture.size
                    paragraph = doc.add_paragraph(); paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    paragraph.paragraph_format.keep_with_next = True
                    paragraph.add_run().add_picture(str(path), width=Inches(min(6.35, 7*w/h))); image_count += 1
            else:
                raw = tokens[i+1].content
                style = 'Handoff Note' if quotes or raw.startswith('**Thao tác ghép') else ('List Number' if lists and lists[-1] == 'ordered_list_open' else 'List Bullet') if lists else 'Normal'
                paragraph = doc.add_paragraph(style=style); inline(paragraph, children)
            i += 3; continue
        if kind == 'fence':
            for line in token.content.rstrip().splitlines(): doc.add_paragraph(line or ' ', style='Handoff Code')
            i += 1; continue
        if kind == 'table_open':
            rows = []; row = []; i += 1
            while tokens[i].type != 'table_close':
                if tokens[i].type == 'tr_open': row = []
                elif tokens[i].type == 'inline': row.append(tokens[i].children or [])
                elif tokens[i].type == 'tr_close': rows.append(row)
                i += 1
            assert len(set(len(row) for row in rows)) == 1
            table = doc.add_table(rows=len(rows), cols=len(rows[0])); table.style = 'Table Grid'
            for ri, row in enumerate(rows):
                for ci, children in enumerate(row):
                    paragraph = table.cell(ri, ci).paragraphs[0]
                    paragraph.paragraph_format.space_after = Pt(3); paragraph.paragraph_format.line_spacing = 1.0
                    inline(paragraph, children, 9.5)
                    if ri == 0:
                        paragraph.paragraph_format.keep_with_next = True
                        for run in paragraph.runs: run.bold = True
                props = table.rows[ri]._tr.get_or_add_trPr()
                props.append(OxmlElement('w:cantSplit'))
                if ri == 0: props.append(OxmlElement('w:tblHeader'))
            doc.add_paragraph(); i += 1; continue
        i += 1
    doc.core_properties.title = 'Chinh — Nội dung chỉnh sửa báo cáo theo phân công mới'
    doc.core_properties.author = 'Chinh — tên gọi theo phân công nội bộ'
    doc.core_properties.subject = 'Chỉ phần sửa/bổ sung để ghép; không phải toàn bộ báo cáo'
    doc.save(DOCX)
    # Structural and scope QA against the actual saved DOCX.
    with zipfile.ZipFile(DOCX) as archive:
        assert archive.testzip() is None
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        document = etree.fromstring(archive.read('word/document.xml'))
        extracted = ' '.join(document.xpath('//w:t/text()', namespaces=ns))
        assert len(document.xpath('//w:drawing', namespaces=ns)) == image_count == 1
        headings = [''.join(p.xpath('.//w:t/text()', namespaces=ns)) for p in document.xpath('//w:p[w:pPr/w:pStyle[@w:val="Heading2"]]', namespaces=ns)]
        assert [int(re.match(r'(\d+)\.', h)[1]) for h in headings] == list(range(1, 13))
        for marker in ['5.2.4.', '7.1.', '7.3.', '7.4.', '7.5.', '7.8', '8.3.', '8.6', '9.4', '10.3.', '10.4.', '10.5.',
                       '10.7.1', '11.5', '12.2', '12.5', '12.8', '13.2.', '13.3.', '14.2.', '14.5', '15–16', '18.000/18.000', '171/171']:
            assert marker in extracted, marker
        assert 'INSERT_' not in extracted
        assert len(document.xpath('//w:tbl', namespaces=ns)) == 7
    links = 0
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if '://' not in target and not target.startswith('#'):
            assert (MARKDOWN.parent / target.split('#')[0]).exists(), target
            links += 1
    for rel, digest in protected.items(): assert sha(ROOT / rel) == digest, rel
    # Cite the existing numbering, and verify that copied entries/linked primary URLs agree with the catalogue.
    for number, url in re.findall(r'\[\[(\d+)\]\]\(([^)]+)\)', content):
        row = sources[int(number)]; assert url in {row['url'], row['verified_content_url']}
    for n in used: assert f'[{n}] ' in content and sources[n]['url'] in content
    dump(EVIDENCE / 'protected-inputs.json', protected)
    dump(EVIDENCE / 'evidence-verification.json', evidence)
    dump(EVIDENCE / 'revision-manifest.json', dict(date='2026-10-28', status='PASS',
        deliverable=DOCX.relative_to(ROOT).as_posix(), docx_sha256=sha(DOCX), markdown=MARKDOWN.relative_to(ROOT).as_posix(),
        markdown_sha256=sha(MARKDOWN), handoff_sections=12, tables=7, figures=1, retained_citation_numbers=used,
        local_links_checked=links, source_and_canonical_report_files_preserved=len(protected), tests_rerun=False,
        original_chapters_rewritten=False, full_report_reexported=False, portable_relative_paths=True,
        validation='PASS: DOCX ZIP/XML, scope markers, selected XML counts, hashes, delta CSV, reference mapping and local links'))
    dump(EVIDENCE / 'checksums.sha256.json', {p.relative_to(ROOT).as_posix(): sha(p) for p in
         [DOCX, MARKDOWN, Path(__file__), *EVIDENCE.glob('*.json')] if p.name != 'checksums.sha256.json'})
    print(json.dumps(dict(status='PASS', docx=str(DOCX), handoff_sections=12, citations=used, local_links=links,
                          verified_java_sources=219, tables=7, figures=1), ensure_ascii=True))


if __name__ == '__main__':
    main()
