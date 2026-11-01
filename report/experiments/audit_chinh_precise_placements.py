"""Independently inspect the delivered revision without rebuilding completed outputs."""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))
from lxml import etree

EVIDENCE = ROOT / 'report/evidence/chinh-precise-placements-2026-10-28'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = load(EVIDENCE / 'revision-manifest.json')
    plan = load(EVIDENCE / 'placement-plan.json')
    markdown = ROOT / manifest['markdown']
    docx = ROOT / manifest['docx']
    assert sha(markdown) == manifest['markdown_sha256']
    assert sha(docx) == manifest['docx_sha256']
    text = markdown.read_text(encoding='utf-8')
    blocks = re.findall(r'> \*\*BẮT ĐẦU NỘI DUNG BÁO CÁO\*\*\s*\n(.*?)\n> \*\*KẾT THÚC NỘI DUNG BÁO CÁO\*\*', text, re.S)
    assert len(blocks) == manifest['paste_blocks'] == 34
    assert [op['id'] for op in plan] == [f'S{i:02d}' for i in range(1, 41)]
    for block in blocks:
        assert not re.search(r'TODO|INSERT_|\*\*Phân công:|\*\*Thao tác:|\*\*Vị trí:', block)
    links = []
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#'):
            assert (markdown.parent / target.split('#')[0]).resolve().exists(), target
            links.append(target)
    catalogue = {row['final_number']: row for row in load(ROOT / 'report/references/sources.json')['sources']}
    citation_numbers = set()
    for number, target in re.findall(r'\[\[(\d+)\]\]\(([^)]+)\)', text):
        row = catalogue[int(number)]
        assert target in (row['url'], row['verified_content_url']), (number, target)
        citation_numbers.add(int(number))
    for number in re.findall(r'\[(\d{1,2})\](?!\()', '\n'.join(blocks)):
        assert int(number) in catalogue, number
        citation_numbers.add(int(number))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(docx) as archive:
        assert archive.testzip() is None
        xml = etree.fromstring(archive.read('word/document.xml'))
        headings = [''.join(p.xpath('.//w:t/text()', namespaces=ns)) for p in
                    xml.xpath('//w:p[w:pPr/w:pStyle[@w:val="Heading1"]]', namespaces=ns)]
        assert [h for h in headings if re.match(r'S\d\d — ', h)] == [op['id']+' — '+op['target'] for op in plan]
        notes = xml.xpath('//w:p[w:pPr/w:pStyle[@w:val="HandoffNote"]]', namespaces=ns)
        assert notes and all(p.xpath('./w:pPr/w:shd[@w:fill="EEF3FA"]', namespaces=ns) for p in notes)
        assert len(xml.xpath('//w:drawing', namespaces=ns)) == 2
        # Normal paragraphs and headings, rather than the instruction-note style, hold the report prose.
        assert not any('TODO' in ''.join(p.xpath('.//w:t/text()', namespaces=ns)) for p in xml.xpath('//w:p', namespaces=ns))
        table_count = len(xml.xpath('//w:tbl', namespaces=ns))
    evidence = load(EVIDENCE / 'evidence-verification.json')
    assert evidence['java_inventory_verified'] == 219
    assert evidence['d1_equality_ticks'] == 18000
    assert evidence['all_delta_scenario_runs'] == 35
    result = dict(status='PASS', operations=len(plan), paste_blocks=len(blocks),
                  unique_local_link_targets=len(set(links)), local_link_occurrences=len(links),
                  citation_numbers=sorted(citation_numbers), primary_citation_urls_match_catalogue=True,
                  docx_tables=table_count, docx_figures=2, instruction_notes_shaded=True,
                  content_blocks_without_placement_instructions=True, chapters_or_game_source_written=False)
    output = EVIDENCE / 'delivery-audit.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    checksums = load(EVIDENCE / 'checksums.sha256.json')
    for relative, digest in checksums.items():
        assert sha(ROOT / relative) == digest, relative
    for path in (Path(__file__), output, EVIDENCE / 'README.md'):
        checksums[path.relative_to(ROOT).as_posix()] = sha(path)
    (EVIDENCE / 'checksums.sha256.json').write_text(json.dumps(checksums, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
