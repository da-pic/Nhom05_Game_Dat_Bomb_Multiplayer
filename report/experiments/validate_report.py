"""Audit the 19 Markdown chapters and active bibliography; no build/test/benchmark.
Run from root: python report/experiments/validate_report.py
Writes assembly manifest and task17 documentation validation evidence.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote, urldefrag

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"report"
EVIDENCE=REPORT/"evidence/task17-2026-10-26"
EVIDENCE.mkdir(parents=True,exist_ok=True)
def read(p):return p.read_text(encoding="utf-8-sig")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(p):return str(p.relative_to(ROOT)).replace("\\","/")
errors=[]
chapters=sorted((REPORT/"chapters").glob("*.md"))
assert [int(p.name[:2]) for p in chapters]==list(range(1,20))
catalogue=json.loads(read(REPORT/"references/sources.json"))
by_number={s["final_number"]:s for s in catalogue["sources"]}
assert sorted(by_number)==list(range(1,15))
assert catalogue["citation_policy"]["active_number_field"]=="final_number"
pattern=re.compile(r"\[(\d{1,2})\](?!\()")
first=[];citation_count=0;source_links={}
def outside_code(text):
    fenced=False
    for lineno,line in enumerate(text.splitlines(),1):
        if line.lstrip().startswith(("```","~~~")):fenced=not fenced
        elif not fenced:yield lineno,line

for path in chapters:
    text=read(path);number=int(path.name[:2])
    if not re.match(rf"# {number}\. ",text):errors.append(f"Chapter title mismatch: {path.name}")
    width=None
    for lineno,line in outside_code(text):
        if line.startswith("|"):
            current=line.count("|")
            if width is not None and width!=current:errors.append(f"Table width: {path.name}:{lineno}")
            width=current
        else:width=None
        if number<=17:
            for match in pattern.finditer(line):
                n=int(match[1]);citation_count+=1
                if n not in by_number:errors.append(f"Unknown citation {n}");continue
                if n not in first:first.append(n)
            for match in re.finditer(r"\[\[(\d+)\]\]\(([^)]+)\)",line):
                source=by_number[int(match[1])]
                allowed={urldefrag(source["url"])[0],urldefrag(source["verified_content_url"])[0]}
                if urldefrag(match[2])[0] not in allowed:errors.append(f"Citation URL mismatch: {path.name}:{lineno}")
    if number in (1,2,3,4,18,19):
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)",text):
            target=match[1]
            if target.startswith(("http:","https:","#")):continue
            local=(path.parent/unquote(target.split("#",1)[0])).resolve()
            if local.is_file():source_links[relative(local)]=sha(local)
assert first==list(range(1,15)),first

def entries(text):
    return {m[3]:(int(m[1]),m[2]) for m in re.finditer(r"(?m)^\[(\d+)\] (.+?) <!-- (R\d{2}) -->$",text)}
root_entries=entries(read(REPORT/"REFERENCES.md"))
chapter_entries=entries(read(REPORT/"chapters/18_TAI_LIEU_THAM_KHAO.md"))
assert root_entries==chapter_entries and len(root_entries)==14
assert {key for key in root_entries}=={s["id"] for s in catalogue["sources"]}
for key,(n,_) in root_entries.items():assert by_number[n]["id"]==key

# Reconstruct pre-normalization text using stable IDs, proving only citation digits changed.
audit=json.loads(read(EVIDENCE/"reference-map.json"))
inverse={r["final_number"]:r["draft_number"] for r in audit["mapping"]}
for change in audit["changed_chapters"]:
    path=ROOT/change["path"];text=read(path)
    assert hashlib.sha256(text.encode()).hexdigest()==change["after_sha256"]
    lines=[];fenced=False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```","~~~")):fenced=not fenced;lines.append(line)
        elif fenced:lines.append(line)
        else:lines.append(pattern.sub(lambda m:f"[{inverse[int(m[1])]}]",line))
    assert hashlib.sha256("".join(lines).encode()).hexdigest()==change["before_sha256"]

abstract=read(REPORT/"chapters/02_TOM_TAT.md")
for expected in ("110076","16411","85,09%","35,98–97,54%","18.000","133/133","84/84","45/45"):
    assert expected in abstract,expected
keyword_text=read(REPORT/"chapters/03_TU_KHOA.md").splitlines()[-1]
assert len(keyword_text.rstrip(".").split(";"))==6
appendix=read(REPORT/"chapters/19_PHU_LUC.md")
for section in "ABCDE":assert re.search(rf"(?m)^## {section}\. ",appendix)
examples=re.findall(r"```json\n(.*?)\n```",appendix,re.S)
assert len(examples)==3
for block in examples:
    obj=json.loads(block)
    assert obj["matchId"]=="00000000-0000-0000-0000-000000000013"

manifest=dict(status="19_chapter_drafts_ready_for_assembly_not_final_submission",task=17,
    chapter_order=[dict(number=int(p.name[:2]),path=relative(p),title=read(p).splitlines()[0][2:],sha256=sha(p)) for p in chapters],
    references=dict(catalogue="report/references/sources.json",chapter="report/chapters/18_TAI_LIEU_THAM_KHAO.md",active_number_field="final_number",sources=14,citation_occurrences=citation_count),
    figures=dict(mermaid_sources=[relative(p) for p in sorted((REPORT/"figures").rglob("*.mmd"))],png=[relative(p) for p in sorted((REPORT/"figures").rglob("*.png"))],note="Export Mermaid for DOCX; PNG/SVG/PDF result figures already exist. Generate TOC/list of figures/tables/page numbers during assembly."),
    needs_group_confirmation=["school/faculty","course/code/class","lecturer","group number","semester/academic year","full legal names and student IDs","individual contribution evidence/confirmation"],
    not_claimed=["GUI/LAN acceptance","CPU/RAM complete metadata","Compilatio result","submission completed"],
    next_task=18)
(REPORT/"report-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Validate local document links in all chapters and new index/evidence after manifest exists.
for path in chapters+[REPORT/"README.md",REPORT/"00_MUC_LUC_CHINH_THUC.md",REPORT/"02_TAI_LIEU_THAM_KHAO.md",EVIDENCE/"README.md"]:
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)",read(path)):
        target=match[1]
        if target.startswith(("http:","https:","#")):continue
        local=(path.parent/unquote(target.split("#",1)[0])).resolve()
        if not local.exists():errors.append(f"Broken link: {relative(path)} -> {target}")

status=subprocess.run(["git","-c",f"safe.directory={ROOT.as_posix()}","status","--short","--","src","scripts","pom.xml"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
if status:errors.append("Tracked source/test/script/POM changes present")
(EVIDENCE/"source-links.sha256.json").write_text(json.dumps([dict(path=p,sha256=h) for p,h in sorted(source_links.items())],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["19 ordered chapters present, with matching chapter numbers.",
    f"14 bibliography entries, all cited; {citation_count} citation occurrences; first appearances are 1-14.",
    "Numeric citation URLs match catalogue primary/verified URLs; REFERENCES.md and chapter 18 entries identical.",
    "Five edited chapters reconstructed with inverse mapping: only citation digits changed; historical evidence untouched.",
    "Abstract existing result figures checked; six keywords; Appendix A-E and three JSON examples parsed.",
    "Local links/table columns checked across all chapters; report assembly manifest generated.",
    "Cover identity and individual contribution confirmation remain explicitly missing; Mermaid export/TOC/DOCX are task18.",
    "No production/test/script/POM changes, game tests/build/benchmarks, raw evidence changes or DOCX export.",
    f"Errors: {len(errors)}"]+errors
(EVIDENCE/"validation.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("\n".join(lines))
if errors:raise SystemExit(1)
