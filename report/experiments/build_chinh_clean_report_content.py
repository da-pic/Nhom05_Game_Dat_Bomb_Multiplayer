"""Create paste-ready report passages, without assignment/editorial instructions."""
from pathlib import Path
import hashlib
import json
import re
import sys
import textwrap
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'target/report-docx-deps'))
from docx import Document
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from markdown_it import MarkdownIt
from PIL import Image
from lxml import etree

MARKDOWN = ROOT / 'report/revisions/CHINH_NOI_DUNG_BAO_CAO_2026-10-28.md'
DOCX = MARKDOWN.with_suffix('.docx')
EVIDENCE = ROOT / 'report/evidence/chinh-clean-content-2026-10-28-final'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (EVIDENCE / 'revision-manifest.json').exists(), 'Keep the completed revision; use a new output for later edits.'
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'report/revisions/CHINH_CHINH_SUA_BAO_CAO_2026-10-28.md'
    protected = {p.relative_to(ROOT).as_posix(): sha(p) for folder in ('src', 'report/chapters', 'report/final')
                 for p in (ROOT / folder).rglob('*') if p.is_file()}
    text = original.read_text(encoding='utf-8')
    text = text[text.index('### 5.2.'):text.index('## 12. Nguồn,')]
    text = re.sub(r'^## \d+\. .*\n', '', text, flags=re.M)
    text = re.sub(r'^\*\*Thao tác ghép.*\n', '', text, flags=re.M)
    text = re.sub(r'^> \*\*Phân công:.*\n', '', text, flags=re.M)
    short = (ROOT / 'report/revisions/2026-10-28_RUT_GON_5_2_5_3.md').read_text(encoding='utf-8')
    comparison = short[short.index('### 5.3.4.'):].strip()
    text = re.sub(r'^\*\*5\.3\.4:\*\*.*$', lambda _: comparison, text, flags=re.M)
    text = text.replace(
        '*Giữ Hình 7.1 hiện có. Đường resync đi qua tầng xử lý yêu cầu để đặt cờ full; client không gọi trực tiếp builder. Giang duyệt routing và lớp mạng khi ghép.*',
        '*Hình 7.1. Luồng input → state → client trong giải pháp đề xuất.*\n\n'
        'Yêu cầu resync được tiếp nhận qua tầng xử lý yêu cầu để đặt cờ tạo full; client không gọi trực tiếp builder.')
    text = text.replace('### Nội dung bổ sung vào input/output\n\n'
        '- **Input:** hướng, trạng thái đi/dừng và sequence do client tạo; yêu cầu đồng bộ lại khi client thiếu nền trạng thái hợp lệ.\n'
        '- **Output:** vị trí/trạng thái authoritative, sequence input cuối server đã xử lý, full snapshot hoặc delta có mốc nền, cùng dữ liệu cần cho hiển thị client.\n\n',
        '### 6.1.2. Dữ liệu đầu vào cho movement và đồng bộ\n\n'
        'Dữ liệu đầu vào gồm hướng, trạng thái đi/dừng và sequence của input, cùng yêu cầu đồng bộ lại khi client thiếu nền trạng thái hợp lệ.\n\n'
        '### 6.1.3. Dữ liệu đầu ra cho movement và đồng bộ\n\n'
        'Server công bố vị trí/trạng thái authoritative, sequence input cuối đã xử lý và full snapshot hoặc delta có mốc nền. Client sử dụng dữ liệu này để tái dựng world, hiệu chỉnh nhân vật local và hiển thị remote.\n\n'
        '## 6.3. Yêu cầu chức năng về movement và đồng bộ\n\n')
    text = text.replace('| Mã giữ nguyên | Nội dung yêu cầu thay thế |', '| Mã | Yêu cầu chức năng |')
    text = text.replace('FR15 — phần Chinh phối hợp', 'FR15')
    text = text.replace('thông số bước và quy tắc kiểm tra mép hitbox chuyển sang 10.4.3.',
                        'thông số bước và quy tắc kiểm tra mép hitbox được trình bày tại mục 10.4.3.')
    text = text.replace('Dung lượng buffer và độ lùi chuyển sang 10.5.',
                        'Dung lượng buffer và độ lùi hiển thị được trình bày tại mục 10.5.')
    text = text.replace('### Đoạn cho 7.8.2 — Freeze/unfreeze và nền đồng bộ', '### 7.8.2. Freeze/unfreeze và nền đồng bộ')
    text = text.replace('### Đoạn cho 7.8.3 — Input và dữ liệu client sau recovery', '### 7.8.3. Input và dữ liệu client sau recovery')
    text = text.replace('Gameplay vẫn được extension cập nhật trong khoảng mất mạng; xác nhận luật và tình huống offline thuộc phần Duy.',
                        'Gameplay vẫn được extension cập nhật trong khoảng mất mạng; bom, sát thương và timer không dừng theo trạng thái kết nối của player.')
    text = text.replace('### Đoạn gửi cho 8.6 — Thread và quyền sửa state', '## 8.6. Thread và quyền sửa state')
    text = text.replace('- **MOVE và sequence/ACK:**', '## 9.4. MOVE, sequence/ACK và đồng bộ snapshot\n\n### 9.4.1. MOVE và sequence/ACK\n\n')
    text = text.replace('- **Tick/baseTick:**', '### 9.4.2. Tick và baseTick\n\n')
    text = text.replace('- **Snapshot và xóa:**', '### 9.4.3. Snapshot và biểu diễn xóa\n\n')
    text = text.replace('- **Resync:**', '### 9.4.4. Phục hồi baseline\n\n')
    text = text.replace('- **Recovery:**', '### 9.4.5. Điều kiện áp dụng full khi recovery\n\n')
    text = re.sub(r'^Nguồn duyệt:.*$', '', text, flags=re.M)
    text = text.replace('Đây là phần chi tiết nhận từ 5.4, không giữ mô tả pixel ở chương lý thuyết.', '')
    text = text.replace('Framing và match envelope do hạ tầng Giang ghép ở chương 9/10.8.',
                        'Framing và match envelope do tầng protocol xử lý như trình bày tại chương 9 và mục 10.8.')
    text = text.replace('### Đoạn Chinh duyệt cho 10.7.1 — Player và HUD', '### 10.7.1. Player và HUD')
    text = text.replace('### Nội dung cho 11.5 — Thiết kế đối chứng full–delta', '## 11.5. Thiết kế đối chứng full–delta')
    text = text.replace('### Nội dung thay phần diễn giải 12.2 — Movement/runtime/replica', '## 12.2. Movement, runtime và replica')
    text = text.replace('| Class trong lượt A5 | Execution đạt | Nội dung Chinh nhận trách nhiệm |',
                        '| Lớp kiểm thử | Số test đạt | Phạm vi kiểm chứng |')
    text = text.replace('RecoveryGameplayIntegrationTest — dùng chung', 'RecoveryGameplayIntegrationTest')
    text = text.replace('Chinh nhận phần cùng runtime/controller/counter, equality full và delta sau full; không nhận toàn bộ luật gameplay/session là phần cá nhân',
                        'Giữ runtime/controller/counter, đối chiếu full và tiếp tục delta sau full trong fixture recovery')
    text = text.replace('Lượt A5 sau sửa recovery ngày 27/10/2026 có 171/171 JUnit trong 44 class đạt ngoài sandbox; các lớp trong bảng dưới là tập con, không phải test chạy thêm.',
                        'Lượt kiểm thử sau sửa recovery ngày 27/10/2026 đạt 171/171 JUnit trong 44 class ngoài sandbox. Các lớp trong bảng dưới là tập con của lượt chạy này.')
    text = text.replace('Check main được wrapper JUnit gọi lại không tạo thêm coverage độc lập. Các test tích hợp dùng chung không được đếm thêm lần nữa ở mỗi chương hoặc mỗi thành viên. Manifest/XML/CSV ở bộ E2 dưới đây là nguồn số đếm; suite baseline 133/133 thuộc E3, không được thay đồng loạt bằng 171/171.',
                        'Một số lớp JUnit gọi lại check main tương ứng, nên chạy check riêng không tạo thêm coverage độc lập. '
                        'Số đếm từng lớp và XML được lưu trong [class-results.csv](../evidence/recovery-report-task03-20261027-200413/class-results.csv) '
                        'và [surefire](../evidence/recovery-report-task03-20261027-200413/surefire/). '
                        'Suite baseline 133/133 trước recovery thuộc revision khác, được lưu riêng trong [hồ sơ baseline](../evidence/task12-2026-10-26/junit-summary.json).')
    text = text.replace('### Nội dung thay phần diễn giải 12.5 — Kết quả full–delta', '## 12.5. Kết quả full–delta')
    text = text.replace('E1 lưu đủ năm lần cho mỗi cấu hình:', 'Mỗi cấu hình được chạy năm lần:')
    text = text.replace('Giữ Bảng 12.8/12.9 và Hình 12.1/12.2 làm nơi công bố số chi tiết; không coi các phép so sánh này là JUnit mới hoặc bằng chứng giảm latency tương ứng.',
                        'Các phép đối chiếu này thuộc harness, không phải JUnit mới hoặc phép đo latency. '
                        'Tổng byte và kết quả từng lần được lưu trong [summary.csv](../evidence/task13-2026-10-26/summary.csv) '
                        'và [all-runs.csv](../evidence/task13-2026-10-26/all-runs.csv).')
    text = text.replace('### Nội dung phối hợp 12.8 — Correctness sau recovery', '### 12.8.3. Tính đúng của state và input sau recovery')
    text = text.replace('Marker `multi_input_bomb` ở E2',
                        'Kết quả `multi_input_bomb` trong [case-results.csv](../evidence/recovery-report-task03-20261027-200413/case-results.csv)')
    text = text.replace('Chinh nhận phần state/input/baseline; token/grace và luật bom/damage/offline do Mai/Duy xác nhận. Không suy ba chu kỳ thành tỷ lệ phục hồi thành công trên mạng thật.',
                        'Kết quả xác nhận các invariant state/input/baseline trong fixture cục bộ; ba chu kỳ không đại diện cho tỷ lệ phục hồi thành công trên mạng thật.')
    start = text.index('### Bằng chứng cần gửi cùng phần Chinh')
    end = text.index('### 13.2.', start)
    text = text[:start] + text[end:]
    text = text.replace('Bằng chứng E1 và mục 12.5', 'Kết quả thực nghiệm ở mục 12.5')
    text = text.replace('Không lấy số lượng class hoặc dòng code làm thước đo novelty.',
                        'Đóng góp được đánh giá qua hành vi đồng bộ và kết quả kiểm chứng, thay vì số lượng lớp hoặc dòng code.')
    text = text.replace('### Đoạn Chinh bổ sung cho 14.5', '## 14.5. Phục hồi runtime và trạng thái client')
    text = text.replace('Các assertion full→delta và input/counter ở E2',
                        'Các assertion full→delta và input/counter trong RecoveryGameplayIntegrationTest')
    start = text.index('| Hạn chế hiện tại |')
    table_end = text.index('\n\n', start)
    rows = [line.strip().strip('|').split('|') for line in text[start:table_end].splitlines()[2:]]
    rows = [[cell.strip() for cell in row] for row in rows]
    assert len(rows) == 7 and all(len(row) == 3 for row in rows)
    limitations = ['## 15.1.3. Hạn chế đồng bộ, tài nguyên và hiển thị', '',
                   '| Hạn chế | Ảnh hưởng và giới hạn kết luận |', '|---|---|']
    future = ['## 16.2. Tối ưu đồng bộ, tài nguyên và hiển thị', '',
              '| Hướng phát triển | Tiêu chí kiểm chứng |', '|---|---|']
    for limitation, impact, action in rows:
        limitations.append(f'| {limitation} | {impact} |')
        future.append(f'| {limitation} | {action} |')
    future[4:] = [line.replace('| Delta so theo tile/record, chưa tự chọn full theo size (L03) |', '| Tối ưu lựa chọn dữ liệu/full–delta |')
                  .replace('| Chưa đo CPU/GC và thời gian capture/diff/encode |', '| Đánh giá chi phí CPU/GC |')
                  .replace('| Baseline/pending và queue giữ dữ liệu trong bộ nhớ |', '| Kiểm soát chi phí bộ nhớ |')
                  .replace('| Commit theo queue chung, chưa ACK snapshot từng receiver (L04) |', '| Mở rộng chính sách baseline khi cần |')
                  .replace('| FIFO và lấy mẫu có thể gây backlog (L05) |', '| Đánh giá lịch xử lý command |')
                  .replace('| Chưa correction smoothing riêng (L06) |', '| Làm mượt correction local |')
                  .replace('| Buffer nội suy hữu hạn, giữ endpoint khi thiếu mẫu (L06) |', '| Nội suy thích ứng |') for line in future[4:]]
    text = (text[:start] + '\n'.join(limitations) + '\n\n' +
        'Các kết quả hiện tại chưa định lượng chi phí CPU/GC, bộ nhớ baseline/queue hoặc chất lượng hiển thị. '
        'Kiểm thử runtime và replica đạt không thay thế cho các phép đo này.\n\n' + '\n'.join(future) + '\n\n' +
        'Các hướng phát triển cần được đánh giá trên cùng workload và môi trường xác định, '
        'đồng thời giữ invariant sequence/ACK, baseline và vòng đời respawn/recovery.\n')
    text = text.replace('bàn giao notices', 'chuyển notices sang tầng gửi')
    text = text.replace('bàn giao', 'chuyển giao')
    text = text.replace('TV2 khai báo contract đặt bom, extension của TV3 thực thi gameplay.',
                        'Core khai báo contract đặt bom, còn gameplay extension thực thi luật đặt bom.')
    text = text.replace('| Class | Điểm triển khai cần giữ |', '| Class | Trách nhiệm và lựa chọn triển khai |')
    text = text.replace('Không nhận đã thu hồi được lệnh vốn tới server trước disconnect.',
                        'Cơ chế này không thu hồi được lệnh đã tới server trước disconnect.')
    text = text.replace('Những nội dung đó giữ trạng thái chưa đo, không bổ sung số ước lượng như kết quả thật.',
                        'Phạm vi kết luận vì vậy giới hạn ở tính đúng replica và dung lượng snapshot trên các trace đã đo.')
    text = text.replace('Đây là phần phối hợp với session/transport, không phải một đóng góp recovery độc lập được cộng thêm lần nữa hoặc cam kết replay toàn bộ thao tác offline.',
                        'Cơ chế runtime/client kết hợp với session và transport để tái lập khả năng điều khiển trên nền state hợp lệ; '
                        'nó không phát lại toàn bộ thao tác trong thời gian offline.')
    for lower, upper in [(' MOVE gửi', 'MOVE gửi'), (' tick đánh dấu', 'Tick đánh dấu'),
                         (' record không xuất hiện', 'Record không xuất hiện'), (' thiếu nền giữ', 'Thiếu nền giữ')]:
        text = re.sub(r'(?m)^' + re.escape(lower), upper, text)
    text = text.replace(' đúng epoch/ACK/metadata vẫn cần full đã áp thành công;',
                        'Sau khi xác nhận đúng epoch, ACK và metadata, client vẫn cần full đã áp thành công;')
    text = text.replace('**Thuật toán 7.1 — Tick rút gọn**', '**Thuật toán 7.1. Vòng cập nhật theo runtime.**')
    text = text.replace('**Thuật toán 7.2 — Tạo full/delta rút gọn**', '**Thuật toán 7.2. Tạo full/delta.**')
    text = text.replace('**Thuật toán 7.3 — Ranh giới công bố**', '**Thuật toán 7.3. Công bố update.**')
    text = text.replace('**Thuật toán 7.4 — Áp dụng replica rút gọn**', '**Thuật toán 7.4. Áp dụng replica.**')
    # Normalize heading depth from the destination section number; these are report headings, not handoff groups.
    text = re.sub(r'(?m)^#{2,4} (\d+(?:\.\d+)+\.) ',
                  lambda m: '#' * min(4, len(m[1].rstrip('.').split('.'))) + ' ' + m[1] + ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()+'\n'
    # Put input/output before movement rules in the final reading order.
    a, b = text.index('### 6.2.3.'), text.index('### 6.1.2.')
    c = text.index('## 6.3.', b)
    movement, io = text[a:b], text[b:c]
    text = text[:a] + io + movement + text[c:]
    forbidden = ['Thao tác ghép', 'Phân công:', 'Chinh', 'Giang', 'Mai', 'Duy', 'bàn giao',
                 'chờ đối chiếu', 'Giữ Bảng', 'Giữ Hình', 'phần diễn giải', 'nội bộ', 'tài liệu này',
                 'đoạn sau', 'người ghép', 'chuyển sang', 'E1', 'E2', 'E3', 'INSERT_', 'TV1', 'TV2', 'TV3', 'TV4', 'Điểm triển khai cần giữ']
    assert all(value not in text for value in forbidden), [value for value in forbidden if value in text]
    assert text.startswith('## 5.2.')
    MARKDOWN.write_text(text, encoding='utf-8')
    # Reuse only the existing Markdown-to-DOCX rendering code. No handoff assembly or historical evidence is rerun.
    script = (ROOT / 'report/experiments/build_chinh_editorial_handoff.py').read_text(encoding='utf-8')
    renderer = script[script.index('    doc = Document()'):script.index('    # Structural and scope QA')]
    renderer = textwrap.dedent(renderer)
    renderer = renderer.replace("'CHINH | NỘI DUNG CHỈNH SỬA ĐỂ GHÉP | 28/10/2026'", "'BOMB IT MULTIPLAYER'")
    renderer = renderer.replace("'Chinh — Nội dung chỉnh sửa báo cáo theo phân công mới'", "'Bomb It Multiplayer — Nội dung báo cáo'")
    renderer = renderer.replace("'Chinh — tên gọi theo phân công nội bộ'", "''")
    renderer = renderer.replace("'Chỉ phần sửa/bổ sung để ghép; không phải toàn bộ báo cáo'", "'Cơ sở lý thuyết, giải pháp, triển khai và đánh giá'")
    context = dict(globals(), content=text)
    exec(compile(renderer, '<report-content-renderer>', 'exec'), context)
    with zipfile.ZipFile(DOCX) as archive:
        assert archive.testzip() is None
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tree = etree.fromstring(archive.read('word/document.xml'))
        body = ' '.join(tree.xpath('//w:t/text()', namespaces=ns))
        assert all(value not in body for value in forbidden)
        assert '5.3.4.' in body and 'Bảng 5.1.' in body
        for number in ('6.1.2.', '6.1.3.', '6.2.3.', '6.3.', '7.1.', '7.3.', '7.4.', '7.5.', '7.8.2.', '7.8.3.',
                       '8.3.', '8.6.', '9.4.', '10.3.', '10.4.', '10.5.', '10.7.1.', '11.5.', '12.2.', '12.5.',
                       '12.8.3.', '13.2.', '13.3.', '14.2.', '14.5.', '15.1.3.', '16.2.'):
            assert number in body, number
        tables = len(tree.xpath('//w:tbl', namespaces=ns))
        assert tables == 8, tables
        assert len(tree.xpath('//w:drawing', namespaces=ns)) == 1
        for name in ('header1.xml', 'footer1.xml'):
            value = archive.read('word/'+name).decode('utf-8')
            assert all(token not in value for token in ['Chinh', 'NỘI DUNG CHỈNH SỬA', 'nội bộ'])
    for rel, digest in protected.items(): assert sha(ROOT / rel) == digest, rel
    links = 0
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#'):
            assert (MARKDOWN.parent / target).exists(), target
            links += 1
    citations = sorted({int(n) for n in re.findall(r'\[(\d{1,2})\](?!\()', text)})
    assert citations == [2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
    result = dict(status='PASS', date='2026-10-28', docx=DOCX.relative_to(ROOT).as_posix(), docx_sha256=sha(DOCX),
                  markdown=MARKDOWN.relative_to(ROOT).as_posix(), markdown_sha256=sha(MARKDOWN),
                  internal_assignment_notes_removed=True, paste_ready_section_headings=True, tables=tables, figures=1,
                  references_preserved=citations, local_links_checked=links, protected_files_preserved=len(protected),
                  previous_handoff_preserved=True, tests_rerun=False, full_report_reexported=False)
    (EVIDENCE / 'revision-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
