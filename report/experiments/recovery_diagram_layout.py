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
