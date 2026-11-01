"""Assemble the 19 chapters into an editable DOCX. No game code/data mutation.
Dependencies are isolated in target/report-docx-deps. Word updates fields afterward.
"""
from pathlib import Path
import sys, re, json, hashlib, math
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'target/report-docx-deps'))
from docx import Document
from docx.shared import Cm, Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START, WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from markdown_it import MarkdownIt
from PIL import Image

REPORT=ROOT/'report';OUT=REPORT/'final';OUT.mkdir(exist_ok=True)
EVIDENCE=REPORT/'evidence/recovery-report-task10-2026-10-27';EVIDENCE.mkdir(parents=True,exist_ok=True)
md=MarkdownIt('commonmark').enable('table')
doc=Document()
sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(2.2);sec.bottom_margin=Cm(2.1);sec.left_margin=Cm(2.5);sec.right_margin=Cm(2.1)
sec.header_distance=Cm(.9);sec.footer_distance=Cm(1)
sec.different_first_page_header_footer=True
styles=doc.styles
for name in ['Normal','Body Text','List Bullet','List Number']:
    st=styles[name];st.font.name='Times New Roman';st.font.size=Pt(12)
    st.paragraph_format.line_spacing=1.15;st.paragraph_format.space_after=Pt(5)
for level,size in [(1,17),(2,14),(3,12.5),(4,12)]:
    st=styles[f'Heading {level}'];st.font.name='Times New Roman';st.font.size=Pt(size)
    st.font.color.rgb=RGBColor.from_string('17324D');st.font.bold=True
    st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(6)
    st.paragraph_format.keep_with_next=True
for name,size in [('Ownership',9.5),('Figure Caption',10.5),('Table Caption',10.5),('Code Block',9),('Reference',11),('Front Heading',16)]:
    st=styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    st.font.name='Consolas' if name=='Code Block' else 'Times New Roman';st.font.size=Pt(size)
    st.paragraph_format.space_after=Pt(5)
    st.paragraph_format.line_spacing=1.05 if name in ('Code Block','Reference') else 1.1
    if name in ('Figure Caption','Table Caption'):st.font.italic=True
    if name=='Table Caption':st.paragraph_format.keep_with_next=True
    if name=='Ownership':st.font.color.rgb=RGBColor.from_string('5D6670');st.paragraph_format.keep_with_next=True
    if name=='Front Heading':st.font.bold=True;st.font.color.rgb=RGBColor.from_string('17324D')
styles['Reference'].paragraph_format.left_indent=Cm(.65)
styles['Reference'].paragraph_format.first_line_indent=Cm(-.65)
styles['Code Block'].paragraph_format.left_indent=Cm(.2)
styles['Code Block'].paragraph_format.right_indent=Cm(.2)
header=sec.header.paragraphs[0];header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
header.add_run('BOMB IT MULTIPLAYER  |  BÁO CÁO PROJECT').font.size=Pt(9)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER

def field(paragraph,instruction,placeholder=''):
    r=OxmlElement('w:r');b=OxmlElement('w:fldChar');b.set(qn('w:fldCharType'),'begin');r.append(b);paragraph._p.append(r)
    r=OxmlElement('w:r');t=OxmlElement('w:instrText');t.set(qn('xml:space'),'preserve');t.text=instruction;r.append(t);paragraph._p.append(r)
    r=OxmlElement('w:r');s=OxmlElement('w:fldChar');s.set(qn('w:fldCharType'),'separate');r.append(s);paragraph._p.append(r)
    paragraph.add_run(placeholder)
    r=OxmlElement('w:r');e=OxmlElement('w:fldChar');e.set(qn('w:fldCharType'),'end');r.append(e);paragraph._p.append(r)
footer.add_run('Trang ');field(footer,' PAGE ');footer.add_run(' / ');field(footer,' NUMPAGES ')
settings=doc.settings.element
update=OxmlElement('w:updateFields');update.set(qn('w:val'),'true');settings.append(update)

bookmark_id=0
def bookmark(p,name):
    global bookmark_id
    bookmark_id+=1
    start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(bookmark_id));start.set(qn('w:name'),name)
    end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(bookmark_id))
    p._p.insert(0,start);p._p.append(end)

edits=[]
task_names={1:'khảo sát ban đầu',2:'hồ sơ nguồn',3:'phần cơ sở lý thuyết',8:'phần hạ tầng',9:'phần TV2',10:'phần gameplay',11:'thiết kế thực nghiệm',12:'kiểm thử chức năng',13:'thực nghiệm delta',14:'thực nghiệm mạng/reliability',15:'phân tích đóng góp',16:'phần tổng kết',17:'chuẩn hóa bản thảo',18:'ghép báo cáo'}
def edit(text,chapter):
    before=text
    if chapter==1:
        text=text.replace(' — bản thảo nội dung cập nhật ngày 27/10/2026.', ' — nội dung cập nhật ngày 27/10/2026.')
        text=text.replace('Mục lục, danh mục hình/bảng và số trang cần được cập nhật khi ghép/xuất lại DOCX/PDF ở nhiệm vụ cập nhật 10.\nBản xuất trước đợt cập nhật Session Recovery vẫn là revision cũ, chưa thay cho nội dung các chương hiện tại.',
                          'Bản xuất gồm mục lục, danh mục hình/bảng và số trang đã cập nhật. Thông tin bìa còn chờ nhóm xác nhận.')
    if chapter==19:
        text=text.replace('Nhiệm vụ cập nhật 10 cần ghép các hình đó, dựng lại mục lục/danh mục, cập nhật trích dẫn và kiểm tra ngắt trang/caption\ntrên DOCX/PDF mới. Bản DOCX/PDF trước recovery chưa đại diện cho nội dung các chương đã sửa.',
                          'Các hình recovery đã được ghép vào DOCX/PDF cùng mục lục, danh mục và trích dẫn cập nhật.\nSau khi nhóm sửa bìa/nội dung, cần cập nhật lại trường Word và kiểm tra ngắt trang/caption trước khi nộp.')
    if before!=text:
        edits.append(dict(chapter=chapter,kind='resolved_current_export_status_only',
                          before_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=hashlib.sha256(text.encode()).hexdigest()))
    return text

figures=[];tables=[];pending_caption=None;current_path=None;current_chapter=0
mermaid_by_chapter={7:sorted((REPORT/'figures/approach').glob('*.mmd')),8:sorted((REPORT/'figures/architecture').glob('*.mmd')),9:sorted((REPORT/'figures/network').glob('*.mmd'))}
mermaid_index={7:0,8:0,9:0}

def hyperlink(p,label,url,bold=False,italic=False):
    element=OxmlElement('w:hyperlink')
    if url.startswith('#'):element.set(qn('w:anchor'),url[1:])
    else:element.set(qn('r:id'),doc.part.relate_to(url,RT.HYPERLINK,is_external=True))
    run=OxmlElement('w:r');props=OxmlElement('w:rPr')
    color=OxmlElement('w:color');color.set(qn('w:val'),'245785');props.append(color)
    if bold:props.append(OxmlElement('w:b'))
    if italic:props.append(OxmlElement('w:i'))
    run.append(props);t=OxmlElement('w:t');t.set(qn('xml:space'),'preserve');t.text=label;run.append(t);element.append(run);p._p.append(element)

def destination(href):
    if href.startswith(('http:','https:','#')):return href
    target=(current_path.parent/href.split('#')[0]).resolve()
    if target.parent==REPORT/'chapters':
        return '#chapter_'+str(int(target.name[:2]))
    import os
    return Path(os.path.relpath(target,OUT)).as_posix()

def inline(p,children,table_font=None):
    bold=False;italic=False;href=None
    for token in children or []:
        typ=token.type
        if typ=='strong_open':bold=True;continue
        if typ=='strong_close':bold=False;continue
        if typ=='em_open':italic=True;continue
        if typ=='em_close':italic=False;continue
        if typ=='link_open':href=destination(token.attrGet('href'));continue
        if typ=='link_close':href=None;continue
        if typ in ('softbreak','hardbreak'):
            p.add_run(' ' if typ=='softbreak' else '\n');continue
        if typ=='html_inline':
            if '<br' in token.content:p.add_run('\n')
            continue
        if typ=='image':
            add_image((current_path.parent/token.attrGet('src')).resolve());continue
        if typ not in ('text','code_inline'):continue
        text=token.content
        if href:hyperlink(p,text,href,bold,italic);continue
        # Plain numbered references become internal links; leave code/indexes alone.
        pieces=re.split(r'(\[\d{1,2}\])',text) if typ=='text' and current_chapter!=18 else [text]
        for piece in pieces:
            if re.fullmatch(r'\[\d{1,2}\]',piece) and current_chapter!=18:
                hyperlink(p,piece,'#ref_'+piece[1:-1],bold,italic);continue
            run=p.add_run(piece);run.bold=bold;run.italic=italic
            if typ=='code_inline':run.font.name='Consolas';run.font.size=Pt(table_font or 10)
            elif table_font:run.font.size=Pt(table_font)

def caption(text,figure=False):
    p=doc.add_paragraph(style='Figure Caption' if figure else 'Table Caption')
    p.add_run(text)
    p.paragraph_format.keep_together=True
    if figure:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    (figures if figure else tables).append(text)
    return p

def add_image(path):
    with Image.open(path) as image:w,h=image.size
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(3)
    # Fits one printable page, preserving aspect ratio. Wide/complex SVGs are retained separately.
    width=min(6.46,8.55*w/h)
    p.add_run().add_picture(str(path),width=Inches(width))

# Included in the recovery DOCX builder by prepare_recovery_final_export.py.
# Preserve Mermaid/PNG originals; layout crops are stored with this export's evidence.
def add_diagram(source, full_caption):
    path=REPORT/'figures/rendered'/f'{source.stem}.png'
    if source.stem not in ('09_05_reconnect_full_delta','09_06_reconnect_tu_choi_va_het_han'):
        add_image(path)
        caption(full_caption,True)
        return
    from PIL import ImageOps
    original=Image.open(path).convert('RGB')
    w,h=original.size
    # Cut at blank horizontal gaps near thirds. Lifelines may cross the cut;
    # message text/arrows must stay intact, and actor headers repeat on each panel.
    gray=original.convert('L')
    cuts=[0]
    for fraction in (1/3,2/3):
        target=int(h*fraction)
        candidates=[]
        for y in range(target-80,target+81):
            strip=gray.crop((0,y-12,w,y+12))
            dark=sum(1 for value in strip.getdata() if value<160)
            candidates.append((dark+abs(y-target)*2,y))
        cuts.append(min(candidates)[1])
    cuts.append(h)
    header_height=120 if source.stem.startswith('09_05') else 110
    assets=EVIDENCE/'layout-assets';assets.mkdir(exist_ok=True)
    section=doc.add_section(WD_SECTION_START.NEW_PAGE)
    section.orientation=WD_ORIENT.LANDSCAPE;section.page_width=Cm(29.7);section.page_height=Cm(21)
    section.different_first_page_header_footer=False
    figure_id=re.match(r'Hình (\d+\.\d+)',full_caption)[1]
    for i,(start,end) in enumerate(zip(cuts,cuts[1:]),1):
        if i>1:doc.add_page_break()
        label=doc.add_paragraph()
        label.alignment=WD_ALIGN_PARAGRAPH.CENTER
        label.paragraph_format.keep_with_next=True
        run=label.add_run(f'Hình {figure_id} — phần {i}/3'+(' (tiếp)' if i>1 else ''))
        run.italic=True;run.font.size=Pt(10)
        cropped=original.crop((0,start,w,end))
        if i>1:
            combined=Image.new('RGB',(w,cropped.height+header_height+10),'white')
            combined.paste(original.crop((0,0,w,header_height)),(0,0))
            combined.paste(cropped,(0,header_height+10));cropped=combined
        output=assets/f'{source.stem}_panel_{i}.png';cropped.save(output)
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after=Pt(1)
        p.paragraph_format.keep_with_next=(i==1)
        # Leave room for actor header, panel label and the full caption on panel one.
        max_height=5.55 if i==1 else 5.9
        width=min(9.3,max_height*cropped.width/cropped.height)
        p.add_run().add_picture(str(output),width=Inches(width))
        if i==1:caption(full_caption,True)
    section=doc.add_section(WD_SECTION_START.NEW_PAGE)
    section.orientation=WD_ORIENT.PORTRAIT;section.page_width=Cm(21);section.page_height=Cm(29.7)
    section.different_first_page_header_footer=False

def add_table(rows):
    count=max(len(row) for row in rows)
    table=doc.add_table(rows=len(rows),cols=count);table.style='Table Grid';table.autofit=False
    font=9.1 if count>=6 else 9.7 if count>=5 else 10.2
    weights=[]
    for col in range(count):
        values=[''.join(t.content for t in row[col]) for row in rows if col<len(row)]
        numeric=all(re.fullmatch(r'[\d\s.,%/()–—+×:;-]+',v or '—') for v in values[1:])
        weights.append(.65 if numeric else min(2.3,max(.9,math.sqrt(max(map(len,values),default=10))/4)))
    total=sum(weights)
    for col,weight in enumerate(weights):table.columns[col].width=Inches(6.46*weight/total)
    for i,row in enumerate(rows):
        for j,children in enumerate(row):
            cell=table.cell(i,j);cell.width=table.columns[j].width
            p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.0
            inline(p,children,font)
            for run in p.runs:run.font.size=Pt(font)
            if i==0:
                p.paragraph_format.keep_with_next=True
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EFF5');cell._tc.get_or_add_tcPr().append(shade)
                for run in p.runs:run.bold=True
        if i==0:
            repeat=OxmlElement('w:tblHeader');table.rows[i]._tr.get_or_add_trPr().append(repeat)
        no_split=OxmlElement('w:cantSplit');table.rows[i]._tr.get_or_add_trPr().append(no_split)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)

def frontmatter():
    for title,instruction in [('MỤC LỤC',' TOC \\o "1-2" \\h \\z \\u '),('DANH MỤC HÌNH',' TOC \\t "Figure Caption,1" \\h \\z '),('DANH MỤC BẢNG',' TOC \\t "Table Caption,1" \\h \\z ')]:
        doc.add_page_break();doc.add_paragraph(title,style='Front Heading')
        field(doc.add_paragraph(),instruction,'Đang cập nhật mục lục...')

merged=[]
manifest=json.loads((REPORT/'report-manifest.json').read_text(encoding='utf-8'))
for entry in manifest['chapter_order']:
    current_path=ROOT/entry['path'];current_chapter=entry['number']
    text=edit(current_path.read_text(encoding='utf-8-sig'),current_chapter)
    merged.append(text)
    tokens=md.parse(text);index=0;quote=0;list_depth=0;list_kind=[]
    while index<len(tokens):
        token=tokens[index];typ=token.type
        if typ=='blockquote_open':quote+=1;index+=1;continue
        if typ=='blockquote_close':quote-=1;index+=1;continue
        if typ in ('bullet_list_open','ordered_list_open'):list_depth+=1;list_kind.append(typ);index+=1;continue
        if typ in ('bullet_list_close','ordered_list_close'):list_depth-=1;list_kind.pop();index+=1;continue
        if typ=='heading_open':
            level=int(token.tag[1]);content=tokens[index+1]
            if level==1:
                p=doc.add_paragraph(style='Heading 1');bookmark(p,'chapter_'+str(current_chapter))
                if current_chapter not in (1,3):p.paragraph_format.page_break_before=True
            else:p=doc.add_paragraph(style=f'Heading {min(level,4)}')
            inline(p,content.children);index+=3;continue
        if typ=='paragraph_open':
            content=tokens[index+1];plain=content.content.strip()
            clean=re.sub(r'^\*+|\*+$','',plain)
            if re.match(r'^\*?Hình \d+\.\d+\.',clean):
                display=re.sub(r'^\*+|\*+$','',plain).replace('\n',' ')
                if index+3<len(tokens) and tokens[index+3].type=='fence' and tokens[index+3].info=='mermaid':pending_caption=display
                else:caption(display,True)
            elif re.match(r'^Bảng [\dA-E]+\.\d+\.',clean):caption(clean)
            elif all(child.type=='image' for child in content.children or []):
                for child in content.children:add_image((current_path.parent/child.attrGet('src')).resolve())
            else:
                style='Ownership' if quote else ('List Number' if list_kind and list_kind[-1]=='ordered_list_open' else 'List Bullet') if list_depth else 'Reference' if current_chapter==18 and re.match(r'^\[\d+\]',plain) else 'Normal'
                p=doc.add_paragraph(style=style)
                if current_chapter==18 and re.match(r'^\[(\d+)\]',plain):bookmark(p,'ref_'+re.match(r'^\[(\d+)\]',plain)[1])
                inline(p,content.children)
            index+=3;continue
        if typ=='fence':
            if token.info=='mermaid':
                source=mermaid_by_chapter[current_chapter][mermaid_index[current_chapter]]
                mermaid_index[current_chapter]+=1
                assert source.read_text(encoding='utf-8-sig').strip()==token.content.strip(),source
                assert pending_caption,source
                add_diagram(source, pending_caption)
                pending_caption=None
            else:
                for line in token.content.rstrip().splitlines():
                    p=doc.add_paragraph(style='Code Block');p.add_run(line or ' ')
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F2F4F6');p._p.get_or_add_pPr().append(shade)
            index+=1;continue
        if typ=='table_open':
            rows=[];row=None;index+=1
            while tokens[index].type!='table_close':
                if tokens[index].type=='tr_open':row=[]
                elif tokens[index].type=='inline':row.append(tokens[index].children or [])
                elif tokens[index].type=='tr_close':rows.append(row)
                index+=1
            add_table(rows);index+=1;continue
        index+=1
    if current_chapter==1:frontmatter()

assert all(mermaid_index[n]==len(mermaid_by_chapter[n]) for n in mermaid_index)
assert len(figures)==15,(len(figures),figures)
assert len(set(re.match(r'(?:Hình|Bảng) ([\dA-E]+\.\d+)',s)[1] for s in figures))==len(figures)
assert len(tables)==len(set(re.match(r'Bảng ([\dA-E]+\.\d+)',s)[1] for s in tables))
doc.core_properties.title='Bomb It Multiplayer — Đồng bộ trạng thái theo delta và phục hồi phiên chơi'
doc.core_properties.subject='Báo cáo project ứng dụng mạng, đủ 19 phần'
doc.core_properties.author='Nhóm Bomb It Multiplayer — cần xác nhận thông tin bìa'
doc.core_properties.keywords='TCP; multiplayer; state delta compression; session recovery; server authoritative'
doc.core_properties.comments='Thông tin bìa và đóng góp cá nhân cần nhóm xác nhận. Không có kết quả Compilatio hoặc nghiệm thu GUI/LAN.'
output=OUT/'NhomXX_BombItMultiplayer_Report.docx';doc.save(output)
(OUT/'BAO_CAO_DA_GHEP.md').write_text('\n\n'.join(merged),encoding='utf-8')
audit=dict(docx=str(output.relative_to(ROOT)),chapters=19,figures=figures,tables=tables,
    figure_count=len(figures),table_count=len(tables),mermaid_diagrams=mermaid_index,editorial_edits=edits,
    note='Current 19 source chapters preserved. Only obsolete export-status sentences resolved in assembly; long recovery sequences split into landscape panels for readability.')
(EVIDENCE/'assembly-manifest.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(output=str(output),figures=len(figures),tables=len(tables),paragraphs=len(doc.paragraphs)),ensure_ascii=False))
