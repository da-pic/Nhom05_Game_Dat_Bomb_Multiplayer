"""Refresh report task 1 from existing evidence; never run tests or edit chapters."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report/evidence/recovery-report-refresh-task01-2026-10-27'
DOC = ROOT / 'report/session-recovery'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *args], cwd=ROOT, encoding='utf-8').strip()


def main():
    # A second invocation must not overwrite this historical survey.
    if OUT.exists():
        raise SystemExit('Evidence already exists; use a new output directory for another survey.')
    prior = ROOT / 'report/evidence/recovery-complete-task03-2026-10-27'
    inventory = json.loads((prior / 'source-inventory.json').read_text(encoding='utf-8'))
    mismatches = [row['path'] for row in inventory if digest(ROOT / row['path']) != row['sha256']]
    if mismatches:
        raise SystemExit(f'Source differs from tested inventory: {mismatches}')
    protected = list((ROOT / 'report/chapters').glob('*.md')) + list((ROOT / 'report/final').glob('*'))
    protected = [p for p in protected if p.is_file()]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
    status = git('status', '--porcelain=v1')
    OUT.mkdir(parents=True)
    for name in ['README.md', '01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md', '01_VI_TRI_CAN_DOI_CHIEU.md']:
        shutil.copy2(DOC / name, OUT / ('historical-' + name))
    pattern = re.compile(r'reconnect|resume|disconnect|phục hồi|mất kết nối|mất mạng|ngắt kết nối|đứt kết nối|133|e333050|ABORTED', re.I)
    candidates = []
    for chapter in sorted((ROOT / 'report/chapters').glob('*.md')):
        heading = ''
        for number, line in enumerate(chapter.read_text(encoding='utf-8').splitlines(), 1):
            if line.startswith('#'):
                heading = line
            if pattern.search(line):
                candidates.append(dict(path=chapter.relative_to(ROOT).as_posix(), line=number, heading=heading, text=line))
    index = ['# Vị trí cần đối chiếu khi cập nhật recovery', '',
             'Khảo sát lại ngày 27/10/2026 sau ba nhiệm vụ kỹ thuật. Các chương chưa được sửa.',
             f'Có **{len(candidates)} dòng ứng viên** theo từ khoá; đây không phải số lỗi. Cần đọc cả đoạn và phân biệt nhận định hiện trạng với số liệu lịch sử.', '']
    for row in candidates:
        label = row['path'].split('/')[-1]
        snippet = row['text'].replace('|', '\\|')
        index += [f"- [{label}:{row['line']}](../chapters/{label}:{row['line']}) — {row['heading']}", f'  {snippet}', '']
    (DOC / '01_VI_TRI_CAN_DOI_CHIEU.md').write_text('\n'.join(index), encoding='utf-8')
    manifest = dict(date='2026-10-27', timezone='Asia/Saigon', head=git('rev-parse', 'HEAD'),
                    branch=git('branch', '--show-current'), git_status=status,
                    tested_source_inventory='report/evidence/recovery-complete-task03-2026-10-27/source-inventory.json',
                    java_files_verified=len(inventory), source_mismatches=mismatches,
                    tests_rerun=False, candidate_lines=len(candidates), protected_files=before)
    (OUT / 'survey-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    shutil.copy2(prior / 'source-inventory.json', OUT / 'source-inventory.json')
    shutil.copy2(prior / 'junit-summary.json', OUT / 'junit-summary.json')
    (OUT / 'chapter-candidates.json').write_text(json.dumps(candidates, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'tracked-source-vs-head.patch').write_text(git('diff', 'HEAD', '--', 'src')+'\n', encoding='utf-8')
    # The tracked patch excludes new files; the inventory covers all main/test Java sources.
    (OUT / 'README.md').write_text('''# Khảo sát báo cáo sau các bản sửa Session Recovery

Ngày 27/10/2026, Asia/Saigon. Chỉ đọc code và bằng chứng đã có; không chạy lại test.

- `survey-manifest.json`: HEAD/nhánh/working tree, hash các chương và bản xuất trước khảo sát.
- `source-inventory.json`: sao lưu inventory của lượt test cuối; đã đối chiếu toàn bộ 219 file Java hiện tại, không sai khác.
- `junit-summary.json`: sao lưu kết quả 171/171 của lượt test kỹ thuật 3, không phải lượt chạy mới.
- `chapter-candidates.json`: vị trí cần review, không coi mọi dòng là lỗi.
- `tracked-source-vs-head.patch`: thay đổi tracked trong src so với HEAD; file mới được nhận diện qua Git status và inventory, không nằm trong patch này.
- `historical-*`: bản khảo sát trước sửa kỹ thuật được bảo tồn, không còn là hiện trạng mới nhất.

Bằng chứng gốc: [recovery-complete-task03](../recovery-complete-task03-2026-10-27/README.md).
Hồ sơ hiện hành: [nhiệm vụ 1](../../session-recovery/01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md).
Không sửa log/XML gốc, code, 19 chương, bản DOCX/PDF hay trạng thái Git.
''', encoding='utf-8')
    after = {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
    assert before == after
    assert status == git('status', '--porcelain=v1')
    print(json.dumps(dict(java_files_verified=len(inventory), candidate_lines=len(candidates), protected_files=len(before), git_status_unchanged=True), ensure_ascii=False))


if __name__ == '__main__':
    main()
