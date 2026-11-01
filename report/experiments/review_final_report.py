"""Structural and paginated QA of the final report; export page samples for review."""
from pathlib import Path
import sys,json,re,zipfile,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'target/report-docx-deps'))
from lxml import etree
import pymupdf
from PIL import Image,ImageOps,ImageDraw
OUT=ROOT/'report/final';EVIDENCE=ROOT/'report/evidence/task18-2026-10-26'
PREVIEW=EVIDENCE/'preview';PREVIEW.mkdir(exist_ok=True)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
DOCX=OUT/'NhomXX_BombItMultiplayer_Report.docx'
PDF=OUT/'NhomXX_BombItMultiplayer_Report.pdf'
assembly=json.loads((EVIDENCE/'assembly-manifest.json').read_text(encoding='utf-8'))
word=json.loads((EVIDENCE/'word-pagination.json').read_text(encoding='utf-8-sig'))
errors=[];warnings=[]
with zipfile.ZipFile(DOCX) as archive:
    assert archive.testzip() is None
    document=etree.fromstring(archive.read('word/document.xml'))
    texts=document.xpath('//w:t/text()',namespaces=NS)
    text=' '.join(texts)
    headings=[]
    for p in document.xpath('//w:p',namespaces=NS):
        style=p.xpath('./w:pPr/w:pStyle/@w:val',namespaces=NS)
        if style and style[0]=='Heading1':headings.append(''.join(p.xpath('.//w:t/text()',namespaces=NS)))
    assert [int(re.match(r'(\d+)\.',h)[1]) for h in headings]==list(range(1,20)),headings
    assert len(document.xpath('//w:drawing',namespaces=NS))==12
    assert len(document.xpath('//w:tbl',namespaces=NS))==78
    bookmarks=document.xpath('//w:bookmarkStart/@w:name',namespaces=NS)
    for n in range(1,15):assert 'ref_'+str(n) in bookmarks
    for n in range(1,20):assert 'chapter_'+str(n) in bookmarks
    assert 'Đang cập nhật mục lục' not in text
    for marker in ['Error!','Bookmark not defined','No table of contents entries found','No table of figures entries found']:
        if marker in text:errors.append('Word field error: '+marker)
    for marker in ['133/133','84/84','45/45','35,98–97,54%','18.000','110076','16411']:
        assert marker in text,marker

assert word['toc_fields']==3 and word['inline_shapes']==12 and word['tables']==78
assert len(word.get('chapter_pages',[]))==19,word.get('chapter_pages')
toc_texts=word['toc_texts']
assert len(toc_texts)==3
for heading in headings:assert heading in toc_texts[0],heading
for caption in assembly['figures']:assert caption in toc_texts[1],caption
for caption in assembly['tables']:assert caption in toc_texts[2],caption

pdf=pymupdf.open(PDF)
assert len(pdf)==word['pages']
page_records=[]
selected={0,1,2,3,len(pdf)-1}
for chapter in word['chapter_pages']:
    page_index=int(chapter['page'])-1
    selected.add(page_index)
for index,page in enumerate(pdf):
    page_text=page.get_text()
    body=re.sub(r'BOMB IT MULTIPLAYER\s*\|\s*BÁO CÁO PROJECT|Trang\s*\d+\s*/\s*\d+','',page_text).strip()
    images=page.get_images()
    if len(body)<10 and not images:errors.append(f'Blank content page {index+1}')
    outside=[]
    for block in page.get_text('dict')['blocks']:
        if block.get('type')!=0:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if span['text'].strip() and (x0<12 or y0<12 or x1>page.rect.width-12 or y1>page.rect.height-12):
                    outside.append(span['text'])
    if outside:errors.append(f'Text outside safe page bounds {index+1}: '+repr(outside[:3]))
    for needle in ['Bảng 12.10.','Bảng 12.11.','Hình 8.2.','Hình 12.1.','Hình 12.3.']:
        if needle in page_text and index>8:selected.add(index)
    page_records.append(dict(page=index+1,text_characters=len(page_text),image_references=len(images),outside_bounds=outside))

for index in sorted(selected):
    page=pdf[index]
    pix=page.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False)
    pix.save(PREVIEW/f'page-{index+1:03d}.png')
thumbnails=sorted(PREVIEW.glob('page-*.png'))
columns=4;cellw,cellh=340,500
sheet=Image.new('RGB',(columns*cellw,math.ceil(len(thumbnails)/columns)*cellh),'#dfe3e8')
draw=ImageDraw.Draw(sheet)
for i,path in enumerate(thumbnails):
    x=(i%columns)*cellw;y=(i//columns)*cellh
    image=ImageOps.contain(Image.open(path).convert('RGB'),(cellw-12,cellh-30))
    sheet.paste(image,(x+6,y+24));draw.text((x+8,y+6),path.stem,fill='black')
sheet.save(EVIDENCE/'page-contact-sheet.png')
result=dict(pages=len(pdf),headings=headings,chapter_pages=word['chapter_pages'],figures=12,
    numbered_table_captions=76,actual_tables_including_cover=78,toc_fields=3,
    sampled_pages=[int(p.stem.split('-')[1]) for p in thumbnails],page_records=page_records,
    errors=errors,warnings=warnings,
    docx_sha256=hashlib.sha256(DOCX.read_bytes()).hexdigest(),pdf_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest())
(EVIDENCE/'document-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('page_records','headings','chapter_pages')},ensure_ascii=True,indent=2))
if errors:raise SystemExit(1)
