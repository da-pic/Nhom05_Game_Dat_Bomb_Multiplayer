"""Export the local multi-mode implementation plan and validate its handoff structure."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'target/report-docx-deps'))
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from markdown_it import MarkdownIt
from lxml import etree

SOURCE=ROOT/'report/plans/KE_HOACH_MO_RONG_GAME_2026-10-29.md'
OUTPUT=SOURCE.with_suffix('.docx')
AUDIT=ROOT/'report/plans/evidence-2026-10-29'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    protected={p.relative_to(ROOT).as_posix():sha(p) for root in ('src','scripts','report/chapters','report/final')
               for p in (ROOT/root).rglob('*') if p.is_file()}
    protected['.gitignore']=sha(ROOT/'.gitignore')
    content=SOURCE.read_text(encoding='utf-8')
    matches=list(re.finditer(r'(?m)^### NV(\d{2}) — (.+)$',content))
    assert [int(m[1]) for m in matches]==list(range(1,46))
    cards=[]
    for index,match in enumerate(matches):
        end=matches[index+1].start() if index+1<len(matches) else content.index('## 7. Chuẩn bằng chứng')
        block=content[match.start():end]
        for field in ('Mục tiêu','Công việc','Phạm vi','Nghiệm thu','Bàn giao'):
            assert re.search(r'\*\*'+field+r'(?: dự kiến)?:\*\*',block),(match[1],field)
        cards.append(dict(id='NV'+match[1],title=match[2],status='CHƯA THỰC HIỆN'))
    task_rows=re.findall(r'(?m)^\| (\d{2}) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$',content)
    assert len(task_rows)==45
    for number,title,dependency,owner in task_rows:
        assert all(int(n)<int(number) for n in re.findall(r'\d{2}',dependency)),(number,dependency)
        cards[int(number)-1].update(dependencies=dependency.strip(),owner=owner.strip())
    for marker in ('MapTheme.CLASSIC','RecipientStream','WorldFrame','timelineEpoch','authorityEpoch',
                   'NV42–NV45','30 giây','29 giây','B0 full world','B1 full view','B2 delta view'):
        assert marker in content,marker
    local_links=[]
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if '://' not in target and not target.startswith('#'):
            assert (SOURCE.parent/target).resolve().exists(),target
            local_links.append(target)
    doc=Document()
    page=doc.sections[0]
    page.page_width=Cm(21);page.page_height=Cm(29.7)
    page.top_margin=Cm(1.8);page.bottom_margin=Cm(1.8)
    page.left_margin=Cm(2.2);page.right_margin=Cm(1.8)
    for name in ('Normal','List Bullet','List Number'):
        style=doc.styles[name];style.font.name='Times New Roman';style.font.size=Pt(11.5)
        style.paragraph_format.line_spacing=1.1;style.paragraph_format.space_after=Pt(5)
    for level,size in ((1,19),(2,15),(3,12.5),(4,12)):
        style=doc.styles['Heading '+str(level)];style.font.name='Times New Roman';style.font.size=Pt(size)
        style.font.color.rgb=RGBColor.from_string('17324D');style.paragraph_format.keep_with_next=True
        style.paragraph_format.space_before=Pt(12);style.paragraph_format.space_after=Pt(6)
    code=doc.styles.add_style('Plan Code',WD_STYLE_TYPE.PARAGRAPH)
    code.font.name='Consolas';code.font.size=Pt(9)
    code.paragraph_format.line_spacing=1;code.paragraph_format.space_after=Pt(1)
    note=doc.styles.add_style('Plan Note',WD_STYLE_TYPE.PARAGRAPH)
    note.font.name='Times New Roman';note.font.size=Pt(11)
    note.font.color.rgb=RGBColor.from_string('34506A')
    header=page.header.paragraphs[0];header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    header.add_run('BOMB IT • KẾ HOẠCH MỞ RỘNG • 29/10/2026').font.size=Pt(8)
    footer=page.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run('Trang ')
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    doc.core_properties.title='Kế hoạch mở rộng Bomb It Multiplayer — Classic và các mode sáng tạo'
    doc.core_properties.subject='45 nhiệm vụ triển khai theo giai đoạn; chưa phải tính năng đã hoàn thành'
    doc.core_properties.author='Nhóm Bomb It Multiplayer'

    def hyperlink(paragraph,label,target):
        from docx.opc.constants import RELATIONSHIP_TYPE
        link=OxmlElement('w:hyperlink')
        link.set(qn('r:id'),doc.part.relate_to(target,RELATIONSHIP_TYPE.HYPERLINK,is_external=True))
        run=OxmlElement('w:r');props=OxmlElement('w:rPr')
        color=OxmlElement('w:color');color.set(qn('w:val'),'245785');props.append(color)
        run.append(props);text=OxmlElement('w:t');text.text=label;run.append(text);link.append(run);paragraph._p.append(link)

    def inline(paragraph,children,size=None):
        bold=italic=False;href=None
        for token in children or []:
            if token.type=='strong_open':bold=True
            elif token.type=='strong_close':bold=False
            elif token.type=='em_open':italic=True
            elif token.type=='em_close':italic=False
            elif token.type=='link_open':href=token.attrGet('href')
            elif token.type=='link_close':href=None
            elif token.type in ('softbreak','hardbreak'):paragraph.add_run(' ' if token.type=='softbreak' else '\n')
            elif token.type in ('text','code_inline'):
                if href:hyperlink(paragraph,token.content,href);continue
                run=paragraph.add_run(token.content);run.bold=bold;run.italic=italic
                if size:run.font.size=Pt(size)
                if token.type=='code_inline':run.font.name='Consolas';run.font.size=Pt(min(size or 10,10))

    tokens=MarkdownIt('commonmark').enable('table').parse(content)
    i=0;lists=[];quotes=0;tables=0
    while i<len(tokens):
        token=tokens[i];kind=token.type
        if kind in ('bullet_list_open','ordered_list_open'):lists.append(kind);i+=1;continue
        if kind in ('bullet_list_close','ordered_list_close'):lists.pop();i+=1;continue
        if kind=='blockquote_open':quotes+=1;i+=1;continue
        if kind=='blockquote_close':quotes-=1;i+=1;continue
        if kind=='heading_open':
            p=doc.add_paragraph(style='Heading '+str(min(int(token.tag[1:]),4)))
            inline(p,tokens[i+1].children);i+=3;continue
        if kind=='paragraph_open':
            style='Plan Note' if quotes else ('List Number' if lists and lists[-1]=='ordered_list_open' else 'List Bullet') if lists else 'Normal'
            p=doc.add_paragraph(style=style);inline(p,tokens[i+1].children);i+=3;continue
        if kind=='fence':
            for line in token.content.rstrip().splitlines():doc.add_paragraph(line or ' ',style='Plan Code')
            i+=1;continue
        if kind=='table_open':
            rows=[];row=[];i+=1
            while tokens[i].type!='table_close':
                if tokens[i].type=='tr_open':row=[]
                elif tokens[i].type=='inline':row.append(tokens[i].children or [])
                elif tokens[i].type=='tr_close':rows.append(row)
                i+=1
            assert len({len(r) for r in rows})==1
            table=doc.add_table(rows=len(rows),cols=len(rows[0]));table.style='Table Grid'
            for ri,row in enumerate(rows):
                for ci,children in enumerate(row):
                    p=table.cell(ri,ci).paragraphs[0];p.paragraph_format.space_after=Pt(3)
                    p.paragraph_format.line_spacing=1;inline(p,children,9.5)
                    if ri==0:
                        for run in p.runs:run.bold=True
                        fill=OxmlElement('w:shd');fill.set(qn('w:fill'),'EAF0F6');table.cell(ri,ci)._tc.get_or_add_tcPr().append(fill)
                props=table.rows[ri]._tr.get_or_add_trPr();props.append(OxmlElement('w:cantSplit'))
                if ri==0:props.append(OxmlElement('w:tblHeader'))
            doc.add_paragraph();tables+=1;i+=1;continue
        i+=1
    doc.save(OUTPUT)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        xml=etree.fromstring(archive.read('word/document.xml'))
        headings=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in xml.xpath('//w:p[w:pPr/w:pStyle[@w:val="Heading3"]]',namespaces=ns)]
        assert [re.match(r'NV\d{2}',h)[0] for h in headings if re.match(r'NV\d{2}',h)]==[x['id'] for x in cards]
        assert len(xml.xpath('//w:tbl',namespaces=ns))==tables
        all_text=' '.join(xml.xpath('//w:t/text()',namespaces=ns))
        assert all(marker in all_text for marker in ('Classic','Shadow Relay','Circuit','Paradox','Worker failover','CHƯA THỰC HIỆN'))
        assert 'TODO' not in all_text and 'INSERT_' not in all_text
    for relative,digest in protected.items():assert sha(ROOT/relative)==digest,relative
    AUDIT.mkdir(parents=True,exist_ok=True)
    dump(AUDIT/'task-index.json',cards)
    dump(AUDIT/'protected-inputs.json',protected)
    head=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],cwd=ROOT).decode().strip()
    result=dict(status='PASS',date='2026-10-29',source_head=head,tasks=len(cards),
        deliverables=[SOURCE.relative_to(ROOT).as_posix(),OUTPUT.relative_to(ROOT).as_posix()],
        tables=tables,local_links_checked=len(local_links),all_tasks_have_five_handoff_fields=True,
        task_dependencies_precede_the_task=True,docx_zip_xml_verified=True,
        protected_inputs_preserved=len(protected),game_code_changed=False,tests_rerun=False,
        gitignore_changed=False,committed=False,pushed=False)
    dump(AUDIT/'manifest.json',result)
    dump(AUDIT/'checksums.json',{p.relative_to(ROOT).as_posix():sha(p) for p in
        (SOURCE,OUTPUT,Path(__file__),AUDIT/'task-index.json',AUDIT/'protected-inputs.json',AUDIT/'manifest.json')})
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':main()
