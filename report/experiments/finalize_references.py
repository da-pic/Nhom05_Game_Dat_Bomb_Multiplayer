"""Normalize numbered citations in report chapters 1-17 by first appearance.
Stable Rxx keys and old draft_number remain in catalogue; raw evidence untouched.
Run from root: python report/experiments/finalize_references.py
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "report"
EVIDENCE = REPORT / "evidence/task17-2026-10-26"
EVIDENCE.mkdir(parents=True, exist_ok=True)
catalogue_path = REPORT / "references/sources.json"
catalogue = json.loads(catalogue_path.read_text(encoding="utf-8-sig"))
sources = catalogue["sources"]
active = catalogue["citation_policy"].get("active_number_field", "draft_number")
by_number = {int(s[active]): s["id"] for s in sources}
by_id = {s["id"]: s for s in sources}
old_refs = (REPORT / "REFERENCES.md").read_text(encoding="utf-8-sig")
entries = {}
for match in re.finditer(r"(?m)^\[(\d+)\] (.+?) <!-- (R\d{2}) -->$", old_refs):
    entries[match[3]] = match[2]
assert len(entries) == len(sources) == 14
paths = sorted(p for p in (REPORT / "chapters").glob("*.md") if 1 <= int(p.name[:2]) <= 17)
assert len(paths) == 17
pattern = re.compile(r"\[(\d{1,2})\](?!\()")
order, occurrences = [], []

def process(text, callback):
    # Numeric array indexes in code and numeric Markdown-link labels are not citations.
    output = []
    fenced = False
    for lineno, line in enumerate(text.splitlines(keepends=True), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            output.append(line)
        elif fenced:
            output.append(line)
        else:
            output.append(pattern.sub(lambda m: callback(m, lineno), line))
    return "".join(output)

for path in paths:
    def discover(match, lineno):
        number = int(match[1])
        assert number in by_number, (path, lineno, number)
        key = by_number[number]
        if key not in order:order.append(key)
        occurrences.append(dict(source_id=key,chapter=path.name,line=lineno,previous_number=number))
        return match[0]
    process(path.read_text(encoding="utf-8-sig"), discover)
assert set(order) == set(by_id), "Only cited sources belong in final bibliography"
final = {key: i+1 for i,key in enumerate(order)}
changes = []
for path in paths:
    before = path.read_text(encoding="utf-8-sig")
    after = process(before, lambda m, _: f"[{final[by_number[int(m[1])]]}]")
    if after != before:
        path.write_text(after, encoding="utf-8")
        changes.append(dict(path=str(path.relative_to(ROOT)).replace("\\","/"),
            before_sha256=hashlib.sha256(before.encode()).hexdigest(),
            after_sha256=hashlib.sha256(after.encode()).hexdigest()))
for source in sources:
    source["final_number"] = final[source["id"]]
    source["cited_in_chapters"] = sorted({r["chapter"] for r in occurrences if r["source_id"] == source["id"]})
catalogue["citation_policy"].update(active_number_field="final_number",
    normalized_in_report_task=17,
    note="final_number is active for chapters and References; draft_number retained for historical evidence. Renormalize together if first citation order changes.")
catalogue_path.write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
bibliography="\n\n".join(f"[{final[key]}] {entries[key]} <!-- {key} -->" for key in order)+"\n"
(REPORT / "REFERENCES.md").write_text(
    "# Tài liệu tham khảo — danh mục hiện hành\n\n"
    "Có 14 nguồn được trích trong các chương, đánh số theo lần xuất hiện đầu tiên trong báo cáo 1–17.\n"
    "Đồng bộ với [mục 18](chapters/18_TAI_LIEU_THAM_KHAO.md). Ngày xác minh/truy cập: 26/10/2026.\n"
    "`n.d.` nghĩa là chưa xác định ngày xuất bản; Java SE 25 là phiên bản API.\n"
    "Kiểu trình bày số gần IEEE là lựa chọn của nhóm, không phải quy định bắt buộc từ thầy.\n"
    "Mã R01–R14 giữ cố định; catalogue dùng final_number, draft_number chỉ còn để đọc hồ sơ cũ.\n\n"
    +bibliography,encoding="utf-8")
(REPORT / "chapters/18_TAI_LIEU_THAM_KHAO.md").write_text(
    "# 18. Tài liệu tham khảo — References\n\n"
    "> **Phân công: cả nhóm cung cấp nguồn; TV4 chuẩn hóa và đối chiếu citation.**\n\n"
    "Danh mục chỉ giữ nguồn được trích trong nội dung, theo thứ tự xuất hiện đầu tiên.\n"
    "`n.d.` chỉ ngày xuất bản chưa xác định; ngày truy cập là 26/10/2026.\n\n"
    +bibliography,encoding="utf-8")
audit=dict(task=17,active_number_field="final_number",
    mapping=[dict(source_id=key,draft_number=by_id[key]["draft_number"],final_number=final[key],title=by_id[key]["title"]) for key in order],
    occurrences=[dict(**r,final_number=final[r["source_id"]]) for r in occurrences],
    changed_chapters=changes,raw_evidence_edited=False)
audit_path=EVIDENCE / "reference-map.json"
if audit_path.exists():
    # Preserve the original migration audit when checking an already normalized report.
    assert json.loads(audit_path.read_text(encoding="utf-8"))["mapping"] == audit["mapping"]
else:
    audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(dict(mapping=audit["mapping"],citation_occurrences=len(occurrences),changed_chapters=len(changes)),ensure_ascii=False,indent=2))
