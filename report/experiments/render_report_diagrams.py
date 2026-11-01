"""Render local Mermaid with local Chromium. Downloads are handled separately.
No report content is uploaded; browser runs headless with a dedicated workspace profile.
"""
from pathlib import Path
import json, math, subprocess, sys, html, re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'target/report-docx-deps'))
from lxml import html as lh
from lxml import etree
ASSETS=ROOT/'target/report-render-assets'
OUT=ROOT/'report/figures/rendered'
EVIDENCE=ROOT/'report/evidence/task18-2026-10-26'
for directory in (ASSETS,OUT,EVIDENCE):directory.mkdir(parents=True,exist_ok=True)
CHROME=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
SOURCES=sorted((ROOT/'report/figures').rglob('*.mmd'))
items=[]
for source in SOURCES:
    original=source.read_text(encoding='utf-8-sig')
    # Only orientation changes for print: same nodes/edges/labels.
    code=original.replace('flowchart LR','flowchart TB',1)
    # Mermaid 11 treats LOOP as a reserved sequence keyword; rename actor ID only.
    if code.startswith('sequenceDiagram'):
        code=re.sub(r'\bLOOP\b','GameThread',code).replace(';',',')
    items.append(dict(name=source.stem,source=str(source.relative_to(ROOT)),code=code,
                      orientation_override=code!=original))
settings=dict(startOnLoad=False,theme='neutral',securityLevel='strict',fontFamily='Arial',
    flowchart=dict(htmlLabels=False,nodeSpacing=25,rankSpacing=22,padding=10,useMaxWidth=False,
                   subGraphTitleMargin=dict(top=12,bottom=28)),
    sequence=dict(useMaxWidth=False,wrap=True,width=155,height=45,actorMargin=28,
                  messageMargin=28,noteMargin=10,actorFontSize=18,messageFontSize=18,noteFontSize=16))
page='''<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:white}svg{display:block}</style></head><body>
<script src="mermaid.min.js"></script><div id="status">PENDING</div><script>
(async()=>{try{mermaid.initialize(SETTINGS);let i=0;for(const item of ITEMS){
const rendered=await mermaid.render('mermaid'+i,item.code);let box=document.createElement('div');
box.setAttribute('data-name',item.name);box.innerHTML=rendered.svg;document.body.appendChild(box);
let raw=document.createElement('textarea');raw.hidden=true;raw.setAttribute('data-svg-name',item.name);raw.textContent=rendered.svg;document.body.appendChild(raw);i++;}
document.getElementById('status').textContent='READY';}catch(e){document.getElementById('status').textContent='ERROR '+e.stack;}})();
</script></body></html>'''.replace('SETTINGS',json.dumps(settings)).replace('ITEMS',json.dumps(items,ensure_ascii=False))
page_path=ASSETS/'all-diagrams.html';page_path.write_text(page,encoding='utf-8')
base=[str(CHROME),'--headless=new','--disable-gpu','--disable-background-networking','--no-first-run',
      '--no-default-browser-check','--allow-file-access-from-files',f'--user-data-dir={ROOT/"target/report-chrome-profile"}']
result=subprocess.run(base+['--virtual-time-budget=20000','--dump-dom',page_path.as_uri()],capture_output=True,timeout=100)
(EVIDENCE/'mermaid-browser.log').write_bytes(result.stderr)
(ASSETS/'rendered-dom.html').write_bytes(result.stdout)
if result.returncode:raise RuntimeError(f'Chrome exit {result.returncode}')
dom=lh.fromstring(result.stdout)
status=dom.get_element_by_id('status').text_content()
assert status=='READY',status
manifest=[]
for item in items:
    raw=dom.xpath(f'//textarea[@data-svg-name="{item["name"]}"]')[0].text_content()
    raw=re.sub(r'<br\s*>','<br/>',raw).replace('&nbsp;','&#160;')
    svg=etree.fromstring(raw.encode())
    view=svg.get('viewBox')
    x,y,w,h=map(float,view.split())
    svg_path=OUT/(item['name']+'.svg')
    svg_path.write_text(raw,encoding='utf-8')
    width=min(2400,max(1000,math.ceil(w*2)))
    height=math.ceil(h/w*width)+8
    single=ASSETS/(item['name']+'.html')
    single.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:white}svg{width:'+str(width)+'px;height:'+str(height-8)+'px;display:block}</style>'+raw,encoding='utf-8')
    png=OUT/(item['name']+'.png')
    shot=subprocess.run(base+[f'--window-size={width},{height}','--hide-scrollbars','--force-device-scale-factor=1',
                         '--virtual-time-budget=1000',f'--screenshot={png}',single.as_uri()],capture_output=True,timeout=45)
    assert shot.returncode==0 and png.exists(),shot.stderr.decode(errors='replace')
    if item['name']=='08_02_thread_va_queue':
        # Preserve the original continuous drawing, but use two reading panels for print.
        from PIL import Image,ImageDraw,ImageFont
        original=Image.open(png).convert('RGB');original.save(OUT/(item['name']+'_continuous.png'))
        pixels=original.convert('L'); candidates=[]
        for row in range(int(height*.42),int(height*.58)):
            ink=sum(1 for v in pixels.crop((0,row,width,row+1)).getdata() if v<245)
            if ink<25:candidates.append(row)
        cut=min(candidates,key=lambda value:abs(value-height/2)) if candidates else height//2
        top=original.crop((0,0,width,cut));bottom=original.crop((0,cut,width,height))
        sheet=Image.new('RGB',(width*2+40,max(top.height,bottom.height)+100),'white')
        sheet.paste(top,(0,70));sheet.paste(bottom,(width+40,70))
        draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',32)
        draw.text((20,14),'A. Theo mũi tên từ trên xuống',font=font,fill='#17324d')
        draw.text((width+60,14),'B. Tiếp nối phần A',font=font,fill='#17324d')
        draw.line((width+20,0,width+20,sheet.height),fill='#cbd2d9',width=2)
        sheet.save(png);width,height=sheet.size
    manifest.append(dict(**{k:v for k,v in item.items() if k!='code'},svg=str(svg_path.relative_to(ROOT)),png=str(png.relative_to(ROOT)),width=width,height=height,svg_viewbox=view))
(EVIDENCE/'diagram-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
