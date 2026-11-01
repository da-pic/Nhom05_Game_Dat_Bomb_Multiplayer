"""Merge verified recovery sources and normalize citations without editing historical exports."""
from pathlib import Path
import copy
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-task09-2026-10-27'
CATALOG = ROOT / 'report/references/sources.json'
CITATION = re.compile(r'\[@(R\d{2})\]|\[(\d{1,2})\](?!\()')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert not (OUT / 'reference-map.json').exists(), 'Preserve this completed normalization; use a new revision.'
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    assert len(catalog['sources']) == 14
    previous = copy.deepcopy(catalog)
    old_numbers = {s['final_number']: s['id'] for s in catalog['sources']}
    staging = json.loads((ROOT / 'report/references/recovery-sources.json').read_text(encoding='utf-8'))
    entries = {}
    bibliography = (ROOT / 'report/REFERENCES.md').read_text(encoding='utf-8')
    for line in bibliography.splitlines():
        match = re.match(r'^\[\d+\] (.*) <!-- (R\d{2}) -->$', line)
        if match:
            entries[match[2]] = match[1]
    assert len(entries) == 14
    for source in catalog['sources']:
        source['verified_on'] = source.get('verified_on', previous['verified_on'])
        source['report_sections'] = list(source.get('report_sections', []))
    for staged in staging['sources']:
        if not staged['new_source']:
            source = next(s for s in catalog['sources'] if s['id'] == staged['id'])
            source['verification_history'] = [
                {'date': source['verified_on'], 'method': source['verification']},
                {'date': staged['verified_on'], 'method': staged['verification'], 'report_task': 'recovery-2'},
            ]
            source['verified_on'] = staged['verified_on']
            source['locators'] = list(dict.fromkeys(source['locators'] + staged['locators']))
            entries[source['id']] = entries[source['id']].replace('Accessed: Oct. 26, 2026.', 'Accessed: Oct. 27, 2026.')
            continue
        source = {k: copy.deepcopy(v) for k, v in staged.items()
                  if k not in ('new_source', 'old_final_number', 'planned_report_sections')}
        source.update(verified_content_url=source['url'], added_in_recovery_report_task=9,
                      report_sections=['5.6'], draft_number=None,
                      kind='official_api_documentation' if source['id'] in ('R18', 'R19') else 'official_documentation')
        if source['id'] in ('R18', 'R19'):
            source['version'] = 'Java SE 25'
        catalog['sources'].append(source)
        author = ', '.join(source['authors'])
        entries[source['id']] = (f'{author}, “{source["title"]},” *{source["publisher"]}*, n.d. '
                                f'[Online]. Available: [{source["title"]}]({source["url"]}). Accessed: Oct. 27, 2026.')
    ids = {s['id'] for s in catalog['sources']}
    order, occurrences, documents = [], [], []
    for path in sorted((ROOT / 'report/chapters').glob('*.md')):
        if int(path.name[:2]) > 17:
            continue
        text = path.read_text(encoding='utf-8')
        documents.append((path, text))
        fenced = False
        for lineno, line in enumerate(text.splitlines(), 1):
            if line.startswith('```'):
                fenced = not fenced
                continue
            if fenced:
                continue
            for match in CITATION.finditer(line):
                key = match[1] or old_numbers[int(match[2])]
                assert key in ids
                if key not in order:
                    order.append(key)
                occurrences.append({'id': key, 'chapter': path.name, 'line': lineno})
        assert not fenced
    assert len(order) == 19 and set(order) == ids
    numbers = {key: i for i, key in enumerate(order, 1)}
    assert all(numbers[key] == num for num, key in old_numbers.items()), 'Review before changing existing citation numbers'
    changed = []
    for path, before in documents:
        output, fenced = [], False
        for line in before.splitlines(keepends=True):
            if line.startswith('```'):
                fenced = not fenced
                output.append(line)
            elif fenced:
                output.append(line)
            else:
                output.append(CITATION.sub(lambda m: f'[{numbers[m[1] or old_numbers[int(m[2])]]}]', line))
        after = ''.join(output)
        if after != before:
            path.write_text(after, encoding='utf-8')
            changed.append(path.relative_to(ROOT).as_posix())
    for source in catalog['sources']:
        source['final_number'] = numbers[source['id']]
        source['cited_in_chapters'] = list(dict.fromkeys(row['chapter'] for row in occurrences if row['id'] == source['id']))
    catalog['verification_dates'] = ['2026-10-26', '2026-10-27']
    catalog['verified_on'] = '2026-10-27'
    catalog['verification_note'] = 'Per-source verified_on is authoritative; this date is the latest catalogue update, not a new verification of all 19 pages.'
    catalog['citation_policy']['normalized_in_recovery_report_task'] = 9
    catalog['citation_policy']['note'] = 'final_number is active; stable IDs retained. Historical staging/reports are preserved and are not the current bibliography.'
    dump(CATALOG, catalog)
    body = '\n\n'.join(f'[{numbers[key]}] {entries[key]} <!-- {key} -->' for key in order) + '\n'
    header = ('Có 19 nguồn được trích trong các chương, đánh số theo lần xuất hiện đầu tiên trong báo cáo 1–17.\n'
              'Ngày truy cập được ghi riêng theo nguồn (26 hoặc 27/10/2026); `n.d.` là chưa xác định ngày xuất bản.\n'
              'Java SE 25 và Socket.IO 4.x là phiên bản tài liệu, không phải ngày xuất bản.\n'
              'Kiểu trình bày số gần IEEE là lựa chọn của nhóm, không phải yêu cầu bắt buộc từ thầy.\n')
    (ROOT / 'report/REFERENCES.md').write_text(
        '# Tài liệu tham khảo — danh mục hiện hành\n\n' + header +
        'Đồng bộ với [mục 18](chapters/18_TAI_LIEU_THAM_KHAO.md) và [catalogue nguồn](references/sources.json).\n'
        'Mã R01–R19 giữ cố định; `final_number` là số trích dẫn hiện hành, `draft_number` chỉ phục vụ hồ sơ cũ.\n'
        'Hồ sơ staging recovery nhiệm vụ 2 được giữ nguyên cho truy vết; năm nguồn mới đã được hợp nhất ở đây.\n\n' + body, encoding='utf-8')
    (ROOT / 'report/chapters/18_TAI_LIEU_THAM_KHAO.md').write_text(
        '# 18. Tài liệu tham khảo — References\n\n'
        '> **Phân công: cả nhóm cung cấp nguồn; TV4 chuẩn hóa và đối chiếu citation.**\n\n' + header +
        'Nguồn chuẩn/API, bài viết tác giả và tài liệu framework được dùng đúng phạm vi; '
        'Socket.IO là công trình liên quan, không phải dependency của project.\n\n' + body, encoding='utf-8')
    dump(OUT / 'reference-map.json', {'task': 9, 'order': order, 'final_numbers': numbers,
         'old_numbers_preserved': True, 'normalization_changed_documents': changed,
         'sources_added': ['R15', 'R16', 'R17', 'R18', 'R19'],
         'reverified_existing_sources': [s['id'] for s in staging['sources'] if not s['new_source']],
         'occurrences': occurrences, 'historical_staging_preserved': True})
    print(json.dumps({'status': 'PASS', 'sources': len(order), 'old_numbers_preserved': True,
                      'normalized_documents': changed}, ensure_ascii=False))


if __name__ == '__main__':
    main()
