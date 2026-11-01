"""Check DOCX/PDF structure, fields and pagination; save visual samples of current export."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))
from lxml import etree
import pymupdf
from PIL import Image, ImageOps, ImageDraw

OUT = ROOT / 'report/final'
EVIDENCE = ROOT / 'report/evidence/recovery-report-task10-2026-10-27'
PREVIEW = EVIDENCE / 'preview-final'
PREVIEW.mkdir(exist_ok=True)
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assembly = read(EVIDENCE / 'assembly-manifest.json')
    inputs = read(EVIDENCE / 'input-review.json')
    word = read(EVIDENCE / 'word-pagination.json')
    docx = OUT / 'NhomXX_BombItMultiplayer_Report.docx'
    pdf_path = docx.with_suffix('.pdf')
    errors, warnings = [], []
    with zipfile.ZipFile(docx) as archive:
        assert archive.testzip() is None
        document = etree.fromstring(archive.read('word/document.xml'))
        texts = document.xpath('//w:t/text()', namespaces=NS)
        text = ' '.join(texts)
        headings = []
        captions = {'FigureCaption': [], 'TableCaption': []}
        for p in document.xpath('//w:p', namespaces=NS):
            styles = p.xpath('./w:pPr/w:pStyle/@w:val', namespaces=NS)
            value = ''.join(p.xpath('.//w:t/text()', namespaces=NS))
            if styles and styles[0] == 'Heading1': headings.append(value)
            if styles and styles[0] in captions: captions[styles[0]].append(value)
        assert [int(re.match(r'(\d+)\.', h)[1]) for h in headings] == list(range(1, 20))
        normalized = lambda values: [re.sub(r'\s+', ' ', value).strip() for value in values]
        assert normalized(captions['FigureCaption']) == normalized(inputs['figures']) == normalized(assembly['figures'])
        assert normalized(captions['TableCaption']) == normalized(inputs['tables']) == normalized(assembly['tables'])
        drawings = len(document.xpath('//w:drawing', namespaces=NS))
        tables = len(document.xpath('//w:tbl', namespaces=NS))
        assert drawings == 19, drawings  # 15 figures, plus four continuation panels.
        assert tables == 88 == inputs['actual_tables_including_cover'], tables
        bookmarks = document.xpath('//w:bookmarkStart/@w:name', namespaces=NS)
        for n in range(1, 20):
            assert 'ref_' + str(n) in bookmarks and 'chapter_' + str(n) in bookmarks
        anchors = document.xpath('//w:hyperlink[not(@r:id)]/@w:anchor', namespaces=NS)
        assert all(anchor in bookmarks for anchor in anchors), sorted(set(anchors)-set(bookmarks))
        assert 'Đang cập nhật mục lục' not in text
        for marker in ['Error!', 'Bookmark not defined', 'No table of contents entries found', 'No table of figures entries found']:
            if marker in text: errors.append('Word field error: ' + marker)
        for marker in ['133/133', '84/84', '45/45', '35,98–97,54%', '18.000', '171/171', 'Session Recovery']:
            assert marker in text, marker
        for obsolete in ['Có 14 nguồn', 'RECONNECT có mã 0043 nhưng chưa có flow resume', 'reconnect resume trận chưa bật']:
            assert obsolete not in text, obsolete
        sections = document.xpath('//w:sectPr/w:pgSz', namespaces=NS)
        assert sum(s.get('{'+NS['w']+'}orient') == 'landscape' for s in sections) == 2
    assert word['toc_fields'] == 3 and word['inline_shapes'] == drawings and word['tables'] == tables
    assert len(word['chapter_pages']) == 19 and len(word['toc_texts']) == 3
    for heading in headings: assert heading in word['toc_texts'][0], heading
    for caption in assembly['figures']: assert caption in word['toc_texts'][1], caption
    for caption in assembly['tables']: assert caption in word['toc_texts'][2], caption
    pdf = pymupdf.open(pdf_path)
    assert len(pdf) == word['pages']
    selected = {0, 1, 2, 3, len(pdf)-1}
    selected.update(int(row['page'])-1 for row in word['chapter_pages'])
    page_records, panel_pages, figure_pages = [], [], []
    for i, page in enumerate(pdf):
        page_text = page.get_text()
        images = page.get_images()
        body = re.sub(r'BOMB IT MULTIPLAYER\s*\|\s*BÁO CÁO PROJECT|Trang\s*\d+\s*/\s*\d+', '', page_text).strip()
        if len(body) < 10 and not images: errors.append(f'Blank content page {i+1}')
        outside = []
        for block in page.get_text('dict')['blocks']:
            if block.get('type') != 0: continue
            for line in block['lines']:
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    if span['text'].strip() and (x0 < 12 or y0 < 12 or x1 > page.rect.width-12 or y1 > page.rect.height-12):
                        outside.append(span['text'])
        if outside: errors.append(f'Text outside safe bounds page {i+1}: {outside[:3]!r}')
        if images:
            selected.add(i); figure_pages.append(i+1)
        if 'phần ' in page_text and ('Hình 9.5' in page_text or 'Hình 9.6' in page_text) and page.rect.width > page.rect.height:
            panel_pages.append(i+1)
        for marker in ['Bảng 12.14.', 'Bảng 12.15.', 'Bảng 12.16.', 'Bảng 12.17.', 'Bảng 15.3.', 'Bảng 5.4.']:
            if marker in page_text and i > 8: selected.add(i)
        page_records.append(dict(page=i+1, text_characters=len(page_text), image_references=len(images),
                                 width=round(page.rect.width, 2), height=round(page.rect.height, 2), outside_bounds=outside))
    assert len(panel_pages) == 6, panel_pages
    for chapter in word['chapter_pages']:
        index = int(chapter['page'])-1
        number = re.match(r'(\d+)\.', chapter['title'])[1]
        assert re.search(r'^'+number+r'\.', pdf[index].get_text(), re.M), chapter
    for i in sorted(selected):
        pix = pdf[i].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3), alpha=False)
        pix.save(PREVIEW / f'page-{i+1:03d}.png')
    samples = sorted(PREVIEW.glob('page-*.png'))
    sheets = []
    # Several compact contact sheets are easier to inspect than one very tall image.
    for batch in range(math.ceil(len(samples)/16)):
        subset = samples[batch*16:(batch+1)*16]
        columns, cw, ch = 4, 340, 490
        sheet = Image.new('RGB', (columns*cw, math.ceil(len(subset)/columns)*ch), '#dfe3e8')
        draw = ImageDraw.Draw(sheet)
        for j, path in enumerate(subset):
            x, y = (j%columns)*cw, (j//columns)*ch
            im = ImageOps.contain(Image.open(path).convert('RGB'), (cw-12, ch-30))
            sheet.paste(im, (x+6, y+24)); draw.text((x+8, y+6), path.stem, fill='black')
        dest = EVIDENCE / f'final-contact-sheet-{batch+1:02d}.png'; sheet.save(dest)
        sheets.append(dest.relative_to(ROOT).as_posix())
    result = dict(pages=len(pdf), headings=headings, chapter_pages=word['chapter_pages'], figures=15,
                  embedded_image_panels=drawings, numbered_table_captions=86, actual_tables_including_cover=tables,
                  references=19, toc_fields=3, landscape_panel_pages=panel_pages, figure_pages=figure_pages,
                  sampled_pages=[int(p.stem.split('-')[1]) for p in samples], contact_sheets=sheets,
                  page_records=page_records, errors=errors, warnings=warnings,
                  docx_sha256=sha(docx), pdf_sha256=sha(pdf_path))
    (EVIDENCE / 'document-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('page_records', 'headings', 'chapter_pages')}, ensure_ascii=True, indent=2))
    if errors: raise SystemExit(1)


if __name__ == '__main__':
    main()
