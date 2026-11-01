"""Create an explicit placement guide with isolated, complete report-content blocks."""
from pathlib import Path
import hashlib
import json
import re
import runpy
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

BASE = 'CHINH_VI_TRI_VA_NOI_DUNG_THAY_THE_2026-10-28'
MARKDOWN = ROOT / 'report/revisions' / (BASE+'.md')
DOCX = MARKDOWN.with_suffix('.docx')
EVIDENCE = ROOT / 'report/evidence/chinh-precise-placements-2026-10-28'
CHAPTERS = ROOT / 'report/chapters'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def bounds(text, number):
    match = re.search(r'(?m)^(#{2,4}) '+re.escape(number)+r'\. .*$', text)
    assert match, number
    end = len(text)
    for following in re.finditer(r'(?m)^#{2,4} (\d+(?:\.\d+)+)\. ', text[match.end():]):
        if not following[1].startswith(number+'.'):
            end = match.end()+following.start(); break
    raw = text[match.start():end]
    trailing_note = re.search(r'\n> \*\*Phân công:.*\s*$', raw, re.S)
    if trailing_note: end = match.start()+trailing_note.start()
    return match.start(), end


def section(text, number):
    a,b = bounds(text,number)
    return re.sub(r'(?m)^> \*\*Phân công:.*\n?', '', text[a:b]).strip()


def body(text): return text.split('\n',1)[1].strip()


def paragraph(text, start):
    found = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip().startswith(start)]
    assert len(found) == 1, (start,len(found))
    return found[0]


def table_row(text, key):
    found = [line for line in text.splitlines() if line.startswith('| '+key+' |')]
    assert len(found) == 1, key
    return found[0]


def excerpt(text, end=False):
    words = text.replace('\n',' ').split()
    return ' '.join(words[-18:] if end else words[:18])


def main():
    assert not (EVIDENCE/'revision-manifest.json').exists(), 'Keep a finalized revision; use a fresh output later.'
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    paths = {int(p.name[:2]):p for p in CHAPTERS.glob('*.md')}
    original = {n:p.read_text(encoding='utf-8') for n,p in paths.items()}
    revised_path = ROOT/'report/revisions/CHINH_NOI_DUNG_BAO_CAO_THEO_PHAN_CONG_2026-10-28.md'
    revised = revised_path.read_text(encoding='utf-8')
    protected = {p.relative_to(ROOT).as_posix():sha(p) for folder in ('src','report/chapters','report/final','report/references')
                 for p in (ROOT/folder).rglob('*') if p.is_file()}
    operations = []

    def add(kind, chapter, target, where, scope, keep, content='', old='', replacement=None, before='', after='', rows_only=False):
        assert kind in ('REPLACE_SECTION','REPLACE_PARAGRAPH','REPLACE_ROWS','REPLACE_HEADER_CELL','INSERT_PARAGRAPH','INSERT_SECTION','DELETE_PARAGRAPH','KEEP')
        item = dict(id=f'S{len(operations)+1:02d}',kind=kind,chapter=chapter,target=target,where=where,
                    scope=scope,keep=keep,content=content,old=old,replacement=replacement,before=before,after=after,rows_only=rows_only)
        if old: assert original[chapter].count(old) == 1, (target,'old anchor')
        if before: assert original[chapter].count(before) == 1, (target,'before anchor')
        if after: assert original[chapter].count(after) == 1, (target,'after anchor')
        if kind=='REPLACE_SECTION': bounds(original[chapter],target)
        operations.append(item)

    def replace_section(n,target,keep,extra=''):
        a,b = bounds(original[n],target)
        old = original[n][a:b]
        next_heading = re.search(r'(?m)^#{2,4} \d+(?:\.\d+)+\. .*$',original[n][b:])
        end_label = next_heading[0].lstrip('# ') if next_heading else 'hết phần này của chương'
        add('REPLACE_SECTION',n,target,f'Chương {n} → mục {target}',
            f'THAY TOÀN BỘ mục {target}: từ tiêu đề “{old.splitlines()[0].lstrip("# ")}” đến ngay trước “{end_label}”. '
            'Bao gồm các mục con, bảng/hình và đoạn văn nằm trong phạm vi đó; không xóa tiêu đề kế tiếp hoặc ghi chú phân công của mục kế tiếp. '+extra,
            keep,section(revised,target))

    replace_section(5,'5.2','Giữ 5.1, 5.3 và các mục khác ngoài phạm vi. Mục mới 5.2.4 nằm bên trong phần thay thế này.',
                    'Bản mới có 5.2.1–5.2.4; không tạo thêm một mục 5.2 thứ hai.')
    old_hitbox = paragraph(original[5],'Nhân vật có hitbox hình chữ nhật.')
    add('DELETE_PARAGRAPH',5,'5.4.1','Chương 5 → 5.4.1 → đoạn hitbox/collision',
        'XÓA CHỈ đoạn cũ được định vị bên dưới sau khi đã đưa nguyên lý vào 5.2.4 và chi tiết vào 10.4.3. Không xóa toàn bộ 5.4.1.',
        'Giữ đoạn mô hình tile/entity trước nó; giữ 5.4.2 về timer/bom và 5.4.3 về state/event để các chủ phần xử lý theo phân công.',old=old_hitbox)
    replace_section(5,'5.3','Giữ 5.4 trở đi. Bảng 5.1 đã nằm đầy đủ trong nội dung thay thế; không giữ thêm bản Bảng 5.1 cũ bên dưới.',
                    'Bản mới gồm 5.3.1–5.3.4; chỉ phần lý thuyết được rút theo yêu cầu.')

    input_header='| Nhóm input | Nội dung | Nơi phát sinh | Điều kiện xử lý |\n|---|---|---|---|'
    input_rows=[
        '| Di chuyển | Hướng UP/DOWN/LEFT/RIGHT, trạng thái đi/dừng và sequence | Client lấy mẫu điều khiển | Đúng match, player còn sống và không frozen; server kiểm tra vật cản và quyết định vị trí |',
        '| Phục hồi đồng bộ | Yêu cầu full khi replica chưa có nền hoặc delta không khớp baseline | Client | Đúng match; tuân theo gate/tần suất; full hợp lệ thiết lập lại nền, không rewind server theo tick client |']
    old_inputs=[table_row(original[6],key) for key in ('Di chuyển','Phục hồi đồng bộ')]
    add('REPLACE_ROWS',6,'6.1.2 / Bảng 6.1','Chương 6 → 6.1.2 → Bảng 6.1 → hai dòng “Di chuyển”, “Phục hồi đồng bộ”',
        'CHỈ THAY hai dòng dữ liệu tương ứng, đủ bốn cột theo thứ tự bảng gốc. Hai dòng không liền nhau: dán từng dòng vào đúng dòng có cùng tên; không chọn gộp phần nằm giữa.',
        'Giữ tiêu đề 6.1.2, header Bảng 6.1 và tất cả dòng khác, gồm dòng đặt bom, phục hồi phiên, kết nối/lobby và cấu hình.',
        input_header+'\n'+'\n'.join(input_rows),replacement=list(zip(old_inputs,input_rows)),rows_only=True)
    old_input_text=paragraph(original[6],'Trong giao diện hiện tại, input di chuyển')
    add('REPLACE_PARAGRAPH',6,'6.1.2','Chương 6 → 6.1.2 → đoạn ngay sau Bảng 6.1',
        'CHỈ THAY đoạn văn cũ được định vị bên dưới, không thay bảng và không thay toàn bộ mục 6.1.2.',
        'Giữ mọi dữ liệu đầu vào của các chức năng khác.',
        body(section(revised,'6.1.2'))+'\n\nInput là ý định thao tác, không phải tọa độ đích hoặc tốc độ do client tự quyết định. Schema message được trình bày ở chương 9.',old=old_input_text)
    output_header='| Nhóm output | Nội dung cần cung cấp | Người nhận/mục đích |\n|---|---|---|'
    output_row='| Đồng bộ gameplay | Full/delta của map, player, entity, tick/baseTick và sequence input cuối server đã xử lý | Client tái dựng replica, reconcile local và nội suy remote; dữ liệu hiển thị không thay quyền quyết định server |'
    old_output_row=table_row(original[6],'Đồng bộ gameplay')
    add('REPLACE_ROWS',6,'6.1.3 / Bảng 6.2','Chương 6 → 6.1.3 → Bảng 6.2 → dòng “Đồng bộ gameplay”',
        'CHỈ THAY một dòng dữ liệu, đủ ba cột. Không thay toàn bộ mục 6.1.3 hoặc Bảng 6.2.',
        'Giữ output lobby, session/recovery, diễn biến gameplay và kết quả cuối lượt.',
        output_header+'\n'+output_row,replacement=[(old_output_row,output_row)],rows_only=True)
    old_output_text=paragraph(original[6],'Tính đúng của output không chỉ')
    consistency=paragraph(section(revised,'6.3'),'Tính nhất quán ở đây')
    add('REPLACE_PARAGRAPH',6,'6.1.3','Chương 6 → 6.1.3 → đoạn kết ngay sau Bảng 6.2',
        'CHỈ THAY đoạn kết cũ được định vị bên dưới.',
        'Giữ tiêu đề, Bảng 6.2 và các nhóm output khác.',
        body(section(revised,'6.1.3'))+'\n\nOutput phải thuộc đúng room/match, phản ánh input đã xử lý và không áp lặp effect gameplay. '+consistency,old=old_output_text)
    replace_section(6,'6.2.3','Giữ toàn bộ các mục khác của 6.2, nhất là 6.2.4–6.2.7 về bom/item/kết thúc/recovery.')

    fr_keys=('FR04','FR05','FR10','FR11')
    old_fr=[table_row(original[6],key) for key in fr_keys]
    fr_new=[
        '| FR04 | Khởi tạo và cách ly trận | Roster/spawn và match identity đúng; mỗi trận có runtime/state riêng; thay đổi hoặc dừng một trận không sửa trực tiếp state trận khác; không nhận thêm người giữa trận | TV2, TV1, TV4 |',
        '| FR05 | Di chuyển và dừng | Server xử lý hướng/đi-dừng, vật cản và biên; player chết hoặc frozen không tiếp tục movement; vị trí dự đoán không thay kết quả authoritative | TV2 |',
        '| FR10 | Đồng bộ full/delta và phục hồi baseline | Full khởi tạo đúng; delta chỉ áp khi baseline hợp lệ; loại stale/sai match/epoch; thiếu nền yêu cầu full; full sau recovery thiết lập nền để tiếp tục delta mà không lặp effect | TV2, TV4 |',
        '| FR11 | Điều khiển và biểu diễn client | Prediction/reconciliation dùng sequence/ACK; nội suy remote; respawn loại lịch sử cũ nhưng không lùi sequence; HUD/gameplay lấy state server; render không quyết định damage/kết quả | TV2, TV3 |']
    add('REPLACE_ROWS',6,'6.3 / Bảng 6.5','Chương 6 → 6.3 → Bảng 6.5 → các dòng FR04, FR05, FR10, FR11',
        'CHỈ THAY bốn dòng có mã trên, đủ bốn cột. Các dòng không liền nhau: dán riêng vào từng mã; không xóa các dòng xen giữa.',
        'Giữ header, cột phụ trách như đã có và toàn bộ FR01–FR03, FR06–FR09, FR12–FR15. Không thay cả bảng hoặc cả mục 6.3.',
        '| Mã | Yêu cầu | Tiêu chí kiểm chứng chính | Phụ trách |\n|---|---|---|---|\n'+'\n'.join(fr_new),replacement=list(zip(old_fr,fr_new)),rows_only=True)
    fr15=table_row(original[6],'FR15')
    cells=[c.strip() for c in fr15.strip('|').split('|')]
    addition='Giữ sequence MOVE/request counter trong cùng match; client chỉ mở input sau full đúng context đã áp; không phát lại phím cũ hoặc áp lại effect gameplay.'
    cells[2]+=' '+addition
    add('INSERT_PARAGRAPH',6,'6.3 / FR15','Chương 6 → Bảng 6.5 → dòng FR15 → ô “Tiêu chí kiểm chứng chính”',
        'BỔ SUNG câu dưới đây ở cuối ô tiêu chí của FR15. Không tạo dòng FR15 thứ hai và không thay phần tiêu chí session/token/deadline đã có.',
        'Giữ nguyên cột mã, yêu cầu, phụ trách và toàn bộ nội dung token/grace/ownership ở đầu ô.',addition,
        old=fr15,replacement='| '+' | '.join(cells)+' |')

    replace_section(7,'7.1','Giữ 7.2. Hình 7.1 được giữ trong bản mới; Bảng 7.1 cũ không còn trong phần 7.1 thay thế để tránh lặp các cơ chế ở các mục sau.')
    replace_section(7,'7.3','Giữ 7.2 và 7.4 trở đi. Bản mới rút mã giả tick, vẫn giữ giải thích single-writer/FIFO/lifecycle; cấu hình cụ thể nằm ở 10.3.')
    replace_section(7,'7.4','Giữ 7.3 và 7.5. Bản mới gồm 7.4.1–7.4.3.',
        'Mục 7.4.4 cũ bị bỏ khỏi vị trí này vì nội dung được chèn vào 7.8.3 trong bước riêng bên dưới; chỉ hoàn tất chuyển sau khi đã chèn phần đó. Thông số triển khai được giữ ở 10.4/10.5.')
    replace_section(7,'7.5','Giữ 7.6, 7.7, 7.8 và các ghi chú của chúng.',
        'Bản mới giữ 7.5.1–7.5.6, Bảng 7.2–7.3 và Hình 7.2. 7.5.7 cũ chuyển vào 11.5.1; ví dụ byte Bảng 7.4 được chuyển thành diễn giải phạm vi đo ở 11.5.3. Không để lại hai bản của các phần đã chuyển.')
    old_lobby=paragraph(original[7],'Lobby xác minh match còn active, submit PlayerReconnectedCommand')
    add('REPLACE_PARAGRAPH',7,'7.8.2','Chương 7 → 7.8.2 “Chuyển ownership và tạo full mới” → đoạn bắt đầu “Lobby xác minh match còn active…”',
        'CHỈ THAY đúng đoạn được định vị bên dưới bằng các đoạn runtime/baseline mới. Không thay tiêu đề hoặc toàn bộ 7.8.2.',
        'Giữ nguyên đoạn trước về claim/socket/writer/CONNECT_ACK của Mai; giữ đoạn sau bắt đầu “Do baseline chung theo match…” và phần từ chối khi match kết thúc.',
        body(section(revised,'7.8.2')),old=old_lobby)
    algo_marker='**Thuật toán 7.5. Phục hồi client với gate full state.**'
    add('INSERT_PARAGRAPH',7,'7.8.3','Chương 7 → 7.8.3 “State machine client và deadline” → ngay trước Thuật toán 7.5',
        'CHÈN các đoạn dưới đây sau phần giải thích budget/deadline và trước tiêu đề Thuật toán 7.5. Không dán lại tiêu đề 7.8.3.',
        'Giữ state machine, Bảng 7.7, các deadline, Thuật toán 7.5 và phần xử lý lỗi đang có. Đây là nơi nhận nội dung 7.4.4 cũ; không giữ bản 7.4.4 trùng ở phía trên.',
        body(section(revised,'7.8.3')),before=algo_marker)

    short_arch=section(revised,'8.3')
    short_arch=short_arch.replace('| Thành phần |', '**Bảng 8.2. Trách nhiệm model, state, runtime và movement.**\n\n| Thành phần |',1)
    a,b=bounds(original[8],'8.3')
    add('REPLACE_SECTION',8,'8.3','Chương 8 → toàn bộ mục 8.3',
        'THAY TOÀN BỘ 8.3, gồm 8.3.1–8.3.3 và Bảng 8.2 cũ, đến trước 8.4. Bản mới chỉ còn trách nhiệm thành phần ngắn gọn, bảng vẫn mang nhãn 8.2.',
        'Giữ 8.1, 8.2, 8.4–8.7. Không xóa hoặc thay sơ đồ/bảng ở 8.6.',short_arch)
    pending=paragraph(original[8],'Giới hạn pending dispatch của owner client')
    add('INSERT_PARAGRAPH',8,'8.6.1','Chương 8 → 8.6.1 “Các ranh giới bàn giao dữ liệu” → sau Bảng 8.5',
        'CHÈN MỘT ĐOẠN ngay sau dòng dữ liệu cuối của Bảng 8.5 và trước đoạn “Giới hạn pending dispatch của owner client…”. Không dán tiêu đề 8.6 từ file trước.',
        'KHÔNG thay toàn bộ 8.6 hoặc 8.6.1. Giữ nguyên Hình 8.2, Bảng 8.5, các đoạn khác của 8.6.1 và toàn bộ 8.6.2–8.6.5.',
        body(section(revised,'8.6')),before=pending)
    add('KEEP',9,'9.4','Chương 9 → 9.4.1, 9.4.3, 9.4.4, 9.4.5',
        'GIỮ NGUYÊN. Nội dung trong file trước ở các mục này là bản đối chiếu lại ngữ nghĩa, không phải yêu cầu xóa hoặc thay cả 9.4. Không có khối nội dung mới cần dán.',
        'Giữ MOVE/ACK, tick/baseTick, full/delta/resync và gate recovery hiện tại; 9.4.2 về layout/version vẫn do Giang tổng hợp. Giữ các bảng/schema của chương 9.')

    replace_section(10,'10.3','Giữ 10.1–10.2 và 10.4 trở đi.',
                    'Thay cả 10.3.1–10.3.5, kể cả Bảng 10.5, bằng bản module đã biên tập đầy đủ bên dưới.')
    replace_section(10,'10.4','Giữ 10.3 và 10.5 trở đi. Không sửa module bom/item ở 10.6.',
                    'Thay cả 10.4.1–10.4.6; các thông số collision được đặt tại 10.4.3 trong bản này.')
    replace_section(10,'10.5','Giữ 10.4 và 10.6–10.8.',
                    'Thay cả 10.5.1–10.5.7 và Bảng 10.6. Không thay phần ClientNetwork/application owner do Giang quản lý ở 10.8.')
    add('KEEP',10,'10.7.1','Chương 10 → 10.7.1 “Grid, nhân vật và HUD”',
        'GIỮ NGUYÊN sau kiểm tra. Nội dung player/HUD trong file trước không yêu cầu thay cả 10.7. Không có khối mới cần dán.',
        'Giữ 10.7.1 và toàn bộ 10.7.2 về bom/item/effect, 10.7.3 về results/lobby UI.')

    replace_section(11,'11.5.1','Giữ tiêu đề 11.5, Bảng 11.5 và 11.5.2; phần môi trường/metric/số lần chạy khác vẫn giữ.',
                    'Đây là nơi gộp phương pháp đối chứng từ 7.5.7 cũ. Không tạo một mục đánh giá thứ hai ở chương 7.')
    old_d1='D1 chỉ được công bố khi đã có harness lưu trace và kiểm tra equality replica sau mỗi tick.'
    add('REPLACE_PARAGRAPH',11,'11.5.2','Chương 11 → 11.5.2 → đúng một câu về trạng thái công cụ D1',
        'CHỈ THAY câu được định vị bên dưới, không thay đoạn còn lại hoặc toàn bộ 11.5.2.',
        'Giữ Bảng 11.5, cấu hình D0/D1, trace, RNG, CSV và các điều kiện correctness khác.',
        'Harness D1 lưu trace và kiểm tra equality replica sau mỗi tick như điều kiện chấp nhận kết quả.',old=old_d1)
    end11=paragraph(original[11],'Mỗi tick có dòng `tick,full_frame_bytes,delta_frame_bytes,kind,base_tick`')
    assert 'Equality replica là điều kiện chấp nhận phép đo:' in end11
    add('INSERT_SECTION',11,'11.5.3','Chương 11 → cuối 11.5.2, sau đoạn kết về equality replica và trước 11.6',
        'CHÈN mục mới 11.5.3 với tiêu đề và nội dung bên dưới. Không thay 11.5.2 hoặc 11.6.',
        'Giữ toàn bộ phương pháp đang có; đây là nơi nhận diễn giải byte/layout từ 7.5.6 và ví dụ Bảng 7.4 cũ.',section(revised,'11.5.3'),after=end11)

    heading1221=section(original[12],'12.2.1').splitlines()[0]
    baseline_intro=paragraph(section(revised,'12.2'),'Các kết quả trong Bảng 12.3–12.4')
    add('INSERT_PARAGRAPH',12,'12.2','Chương 12 → sau tiêu đề 12.2 và trước 12.2.1',
        'CHÈN đoạn xác định mốc baseline bên dưới. Không thay tiêu đề, 12.2.1, 12.2.2 hoặc các bảng test.',
        'Giữ Bảng 12.3–12.4 và toàn bộ kết quả assertion/chứng cứ cũ.',baseline_intro,before=heading1221)
    header123=next(line for line in original[12].splitlines() if line.startswith('| Nguồn test/check |'))
    header124=next(line for line in original[12].splitlines() if line.startswith('| Nguồn | Tình huống | Kết quả lượt mới'))
    add('REPLACE_HEADER_CELL',12,'Bảng 12.3 / cột 4','Chương 12 → Bảng 12.3 → ô header cột 4',
        'CHỈ THAY chữ “Kết quả lượt mới” trong ô header cột 4 bằng chuỗi dưới đây. Không thay các dòng dữ liệu.',
        'Giữ ba cột khác và tất cả giá trị test/fixture.', 'Kết quả baseline 26/10/2026',old=header123,
        replacement=header123.replace('Kết quả lượt mới','Kết quả baseline 26/10/2026'))
    add('REPLACE_HEADER_CELL',12,'Bảng 12.4 / cột 3','Chương 12 → Bảng 12.4 → ô header cột 3',
        'CHỈ THAY chữ “Kết quả lượt mới và phạm vi” trong ô header cột 3 bằng chuỗi dưới đây.',
        'Giữ hai cột khác và tất cả dòng dữ liệu.', 'Kết quả baseline 26/10/2026 và phạm vi',old=header124,
        replacement=header124.replace('Kết quả lượt mới và phạm vi','Kết quả baseline 26/10/2026 và phạm vi'))
    end1222=paragraph(original[12],'Fixture delta kiểm tra build không commit')
    add('INSERT_SECTION',12,'12.2.3','Chương 12 → sau đoạn kết của 12.2.2, trước ghi chú phân công và tiêu đề 12.3',
        'CHÈN mục mới 12.2.3 với tiêu đề và nội dung đầy đủ. Không thay bảng baseline bằng số 171/171.',
        'Giữ 12.2.1–12.2.2 và toàn bộ 12.3 về gameplay.',section(revised,'12.2.3'),after=end1222)
    replace_section(12,'12.5.1','Giữ 12.5.2–12.5.5 nguyên trạng, gồm Bảng 12.8/12.9, Hình 12.1/12.2, đủ bảy cấu hình, số packet/skip và giới hạn phép đo.',
                    'Chỉ thay mục con 12.5.1 để dẫn phương pháp về 11.5; KHÔNG thay toàn bộ 12.5 bằng hai đoạn này.')
    add('KEEP',12,'12.5.2–12.5.5','Chương 12 → các mục 12.5.2, 12.5.3, 12.5.4, 12.5.5',
        'GIỮ NGUYÊN. Các phần này trong file trước được giữ lại để bảo toàn chi tiết, không phải nội dung thay thế mới cần dán thêm.',
        'Giữ trace/equality, hai bảng byte/packet, hai biểu đồ, mọi con số và hạn chế đo. Không xóa chúng khi thay 12.5.1.')
    other_tests=paragraph(original[12],'Các test client/server khác còn xác nhận')
    add('INSERT_PARAGRAPH',12,'12.8.3','Chương 12 → 12.8.3 → sau đoạn nêu case-results và trước “Các test client/server khác còn xác nhận…”',
        'CHÈN phần giải thích state/input phía client bên dưới. Không dán lại tiêu đề 12.8.3 và không thay toàn bộ mục.',
        'Giữ Bảng 12.16 với toàn bộ R01–R14; giữ token/grace/gameplay offline của Mai/Duy và các đoạn writer/cleanup/lỗi khác.',
        body(section(revised,'12.8.3')),before=other_tests)

    replace_section(13,'13.2','Giữ 13.1 và 13.3–13.6.',
                    'Thay 13.2.1–13.2.3 bằng phần giải thích workload/chi phí; Bảng 13.2 cũ không được lặp lại trong bản mới. Bảng kết quả chi tiết ở chương 12 vẫn giữ.')
    replace_section(13,'13.3','Giữ 13.2 và các mục 13.4–13.6 về gameplay/recovery/giới hạn chung.',
                    'Thay cả 13.3.1–13.3.3, không thay toàn bộ chương 13.')
    add('KEEP',14,'14.2','Chương 14 → 14.2.1–14.2.2',
        'GIỮ NGUYÊN sau đối chiếu. Phần 14.2 trong file trước giữ lại contract, phạm vi kế thừa và bằng chứng, không phải yêu cầu rút còn một đoạn.',
        'Giữ đầy đủ 14.2.1–14.2.2, số byte/tỷ lệ/equality/citation; không thay 14.1 hoặc 14.3–14.5.')
    first_c5=paragraph(original[14],'C5 bổ sung đường phục hồi trong active match')
    c5_body=body(section(revised,'14.5'))
    add('INSERT_PARAGRAPH',14,'14.5','Chương 14 → 14.5 → sau đoạn mở đầu “C5 bổ sung đường phục hồi…” và trước “Mục 12.8 cung cấp test…”',
        'CHÈN các đoạn riêng về runtime/client. Không dán lại tiêu đề 14.5 và KHÔNG thay toàn bộ phần Session Recovery bằng nội dung này.',
        'Giữ đoạn mở đầu session/token/claim, các đoạn bằng chứng, baseline không recovery, giới hạn bảo mật và phần đóng góp của Mai/Giang.',
        c5_body,after=first_c5)

    lkeys=('L03','L04','L05','L06')
    old_limits=[table_row(original[15],key) for key in lkeys]
    new_limits=[
        '| L03 | Diff quét/chụp state, gửi cả record; chưa tự chọn full/delta nhỏ nhất và chưa đo chi phí CPU/bộ nhớ | Byte giảm chưa chứng minh CPU/GC/RAM giảm; nhiều record đổi có thể kém lợi; baseline/pending/queue vẫn giữ dữ liệu | StateDeltaBuilder, full–delta mục 12.5; chưa có profiling CPU/GC/retained heap |',
        '| L04 | Baseline commit sau enqueue chung runtime, chưa có receipt ACK snapshot từng receiver | Phải giữ chuỗi delta và fallback full; enqueue chưa chứng minh remote apply; recovery có thể phát full tới cả roster | GameLoop, ClientWorldState, snapshot barrier và mục 9.4/12.8 |',
        '| L05 | FIFO có thể dừng ở mẫu sequenced thứ hai của cùng player; queue và deadline hữu hạn | Input có thể chờ thêm tick; chưa chứng minh fairness/tải tối đa; lifecycle queue đầy hoặc hết grace có thể ABORT | GameLoop/runtime tests và recovery fault tests; chưa có trace queue age/tick overrun theo tải |',
        '| L06 | Chưa có correction smoothing riêng; buffer nội suy hữu hạn và giữ endpoint khi thiếu mẫu | State đúng vẫn có thể giật/đứng hình hoặc thêm độ trễ; chưa có số đo UX/frame time/correction cùng mốc mô phỏng | Prediction/Reconciliation/InterpolationController; respawn/input tests; chưa nghiệm thu UX định lượng |']
    add('REPLACE_ROWS',15,'15.1.3 / Bảng 15.1','Chương 15 → 15.1.3 → Bảng 15.1 → các dòng L03–L06',
        'CHỈ THAY bốn dòng L03, L04, L05, L06, đủ bốn cột của bảng gốc. Không thay cả Bảng 15.1 hoặc cả mục 15.1.3.',
        'Giữ L01 về session/recovery của Mai, L02 về placement của Duy, các đoạn kết của 15.1.3 và toàn bộ 15.2–15.4.',
        '| Mã | Cơ chế/giới hạn | Hệ quả trong phạm vi project | Bằng chứng/căn cứ |\n|---|---|---|---|\n'+'\n'.join(new_limits),
        replacement=list(zip(old_limits,new_limits)),rows_only=True)
    add('KEEP',16,'16.2.1–16.2.3','Chương 16 → 16.2.1, 16.2.2, 16.2.3',
        'GIỮ NGUYÊN sau rà soát: các đề xuất profiling/delta/input/baseline/correction đã có đủ nội dung. Không thay cả 16.2 bằng bảng tóm tắt.',
        'Giữ các mục 16.1, 16.3 và 16.4 của nhóm; chỉ thêm phần bộ nhớ ở bước kế tiếp.')
    last_future=paragraph(original[16],'Đo error trước/sau replay tại cùng thời điểm thích hợp')
    add('INSERT_SECTION',16,'16.2.4','Chương 16 → sau đoạn cuối 16.2.3, trước tiêu đề 16.3',
        'CHÈN mục mới 16.2.4 về bộ nhớ và chính sách giới hạn. Không thay 16.2.1–16.2.3 hoặc 16.3.',
        'Giữ mọi hướng phát triển session/token/protocol/gameplay và nghiệm thu LAN/WAN/soak của các phần khác.',
        section(revised,'16.2.4'),after=last_future)

    # Verify every edit against the actual source, then apply virtually to detect wrong anchors or over-wide scope.
    working=dict(original)
    for op in operations:
        n=op['chapter']; t=working[n]; kind=op['kind']
        if kind=='REPLACE_SECTION':
            a,b=bounds(t,op['target']); t=t[:a]+op['content'].rstrip()+'\n\n'+t[b:]
        elif kind in ('REPLACE_PARAGRAPH','DELETE_PARAGRAPH','REPLACE_HEADER_CELL'):
            assert t.count(op['old'])==1
            value=op['replacement'] if op['replacement'] is not None else op['content']
            t=t.replace(op['old'],value,1)
        elif kind=='REPLACE_ROWS':
            for old,new in op['replacement']:
                assert t.count(old)==1; t=t.replace(old,new,1)
        elif kind in ('INSERT_PARAGRAPH','INSERT_SECTION'):
            if op['old']:
                assert t.count(op['old'])==1; t=t.replace(op['old'],op['replacement'],1)
            elif op['before']:
                assert t.count(op['before'])==1; t=t.replace(op['before'],op['content'].rstrip()+'\n\n'+op['before'],1)
            else:
                assert t.count(op['after'])==1; t=t.replace(op['after'],op['after']+'\n\n'+op['content'].rstrip(),1)
        working[n]=t
    # Critical shared subsections and foreign table rows must be untouched by this plan.
    for n,ids in [(7,['7.2','7.6','7.7','7.8.1','7.8.4']),
                  (8,['8.1','8.2','8.4','8.5','8.6.2','8.6.3','8.6.4','8.6.5','8.7']),
                  (9,['9.4']), (10,['10.2','10.6','10.7.2','10.7.3','10.8']),
                  (12,['12.3','12.4','12.5.2','12.5.3','12.5.4','12.5.5','12.6','12.7','12.8.4','12.8.5']),
                  (14,['14.1','14.2','14.3','14.4']), (15,['15.2','15.3','15.4']), (16,['16.1','16.2.1','16.2.2','16.2.3','16.3','16.4'])]:
        for number in ids: assert section(working[n],number)==section(original[n],number),(n,number)
    for key in ('L01','L02'): assert table_row(working[15],key)==table_row(original[15],key)
    for key in ('FR01','FR02','FR03','FR06','FR07','FR08','FR09','FR12','FR13','FR14'):
        assert table_row(working[6],key)==table_row(original[6],key)
    assert not any(op['kind']=='REPLACE_SECTION' and op['target'] in ('8.6','8.6.1','7.8.2','7.8.3','14.5','15.1.3','16.2') for op in operations)
    assert any(op['target']=='8.6.1' and op['kind']=='INSERT_PARAGRAPH' and 'sau Bảng 8.5' in op['where'] for op in operations)
    assert '### 7.4.4.' not in working[7] and '### 7.5.7.' not in working[7]
    for n,number in [(11,'11.5.3'),(12,'12.2.3'),(16,'16.2.4')]:
        assert len(re.findall(r'(?m)^#{2,4} '+re.escape(number)+r'\. ',working[n]))==1
    # Notes and report text have visibly distinct boundaries. Review-only entries contain no copy block.
    names={'REPLACE_SECTION':'THAY TOÀN BỘ MỤC','REPLACE_PARAGRAPH':'CHỈ THAY ĐOẠN/CÂU',
           'REPLACE_ROWS':'CHỈ THAY DÒNG BẢNG','REPLACE_HEADER_CELL':'CHỈ THAY Ô HEADER',
           'INSERT_PARAGRAPH':'CHÈN ĐOẠN/CÂU','INSERT_SECTION':'THÊM MỤC CON','DELETE_PARAGRAPH':'CHỈ XÓA ĐOẠN','KEEP':'GIỮ NGUYÊN — KHÔNG DÁN'}
    output=['# VỊ TRÍ VÀ NỘI DUNG THAY THẾ — PHẦN CHINH','',
            'Mỗi khối ghi rõ ranh giới thao tác. Chỉ copy phần nằm giữa **BẮT ĐẦU NỘI DUNG BÁO CÁO** và **KẾT THÚC NỘI DUNG BÁO CÁO**. '
            'Phần vị trí/phạm vi/giữ nguyên là chỉ dẫn riêng, không dán vào báo cáo. Khối “giữ nguyên” không có nội dung thay thế.', '',
            'Các vị trí được kiểm tra theo hệ thống mục trong bản chương nguồn của báo cáo. '
            'Không hiểu tiêu đề một mục lớn là yêu cầu xóa tất cả mục con: loại thao tác và ranh giới ghi tại từng khối mới là phạm vi áp dụng.', '',
            '| Khối | Vị trí | Thao tác |','|---|---|---|']
    for op in operations: output.append(f'| {op["id"]} | {op["target"]} | {names[op["kind"]]} |')
    for op in operations:
        source_link='../chapters/'+paths[op['chapter']].name
        output+=['',f'# {op["id"]} — {op["target"]}', '',f'> **Vị trí:** {op["where"]}.', '',
                 f'> **Thao tác:** {op["scope"]}', '',f'> **Phần phải giữ:** {op["keep"]}', '',
                 f'> **Đối chiếu mục gốc:** [{paths[op["chapter"]].name}]({source_link}).', '']
        if op['old'] and op['kind'] in ('REPLACE_PARAGRAPH','DELETE_PARAGRAPH'):
            output += [f'> **Tìm đúng phần cũ:** bắt đầu “{excerpt(op["old"])}”; kết thúc “{excerpt(op["old"],True)}”.','']
        if op['before']: output += [f'> **Chèn ngay trước:** “{excerpt(op["before"])}”.','']
        if op['after']: output += [f'> **Chèn ngay sau đoạn kết thúc:** “{excerpt(op["after"],True)}”.','']
        if op['rows_only']: output += ['> **Cách copy bảng:** DOCX bên dưới chỉ có các hàng dữ liệu, không có header mới. Thứ tự cột giữ giống bảng gốc; dán từng hàng vào đúng mã/tên được chỉ định.','']
        if op['content']:
            output += ['> **BẮT ĐẦU NỘI DUNG BÁO CÁO**','']
            if op['rows_only']: output += ['<!-- ROWS_ONLY -->','']
            output += [op['content'].strip(),'','> **KẾT THÚC NỘI DUNG BÁO CÁO**','']
        elif op['kind']=='KEEP': output += ['> **Không có nội dung mới cần copy/paste cho khối này.**','']
        else: output += ['> **Chỉ xóa đúng phần đã định vị; không có đoạn thay thế ở vị trí cũ.**','']
    content='\n'.join(output)+'\n'
    MARKDOWN.write_text(content,encoding='utf-8')
    # Render with shaded instruction notes and headerless row-replacement tables.
    renderer_path=ROOT/'report/experiments/build_chinh_editorial_handoff.py'
    script=renderer_path.read_text(encoding='utf-8')
    renderer=textwrap.dedent(script[script.index('    doc = Document()'):script.index('    # Structural and scope QA')])
    renderer=renderer.replace("'CHINH | NỘI DUNG CHỈNH SỬA ĐỂ GHÉP | 28/10/2026'", "'VỊ TRÍ THAY THẾ | NỘI DUNG BÁO CÁO'")
    renderer=renderer.replace("'Chinh — Nội dung chỉnh sửa báo cáo theo phân công mới'", "'Chinh — Vị trí và nội dung thay thế chính xác'")
    renderer=renderer.replace("'Chinh — tên gọi theo phân công nội bộ'", "''")
    renderer=renderer.replace("i = 0; lists = []; quotes = 0", "i = 0; lists = []; quotes = 0; rows_only = False")
    marker="    if kind == 'table_open':"
    assert marker in renderer
    renderer=renderer.replace(marker,"    if kind == 'html_block' and token.content.strip() == '<!-- ROWS_ONLY -->':\n        rows_only = True; i += 1; continue\n"+marker)
    renderer=renderer.replace("        table = doc.add_table(rows=len(rows), cols=len(rows[0])); table.style = 'Table Grid'",
        "        if rows_only: rows = rows[1:]\n        table = doc.add_table(rows=len(rows), cols=len(rows[0])); table.style = 'Table Grid'")
    renderer=renderer.replace('if ri == 0:', 'if ri == 0 and not rows_only:')
    renderer=renderer.replace("        doc.add_paragraph(); i += 1; continue", "        rows_only = False\n        doc.add_paragraph(); i += 1; continue")
    renderer=renderer.replace('doc.save(DOCX)', '''
for paragraph in doc.paragraphs:
    if paragraph.style.name == 'Handoff Note':
        shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'EEF3FA'); paragraph._p.get_or_add_pPr().append(shade)
    if paragraph.style.name == 'Heading 1' and paragraph.text.startswith('S'):
        paragraph.paragraph_format.space_before=Pt(18)
doc.save(DOCX)''')
    namespace=dict(globals(),content=content)
    exec(compile(renderer,'<precise-placement-renderer>','exec'),namespace)
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(DOCX) as archive:
        assert archive.testzip() is None
        tree=etree.fromstring(archive.read('word/document.xml'))
        text=' '.join(tree.xpath('//w:t/text()',namespaces=ns))
        copies=sum(bool(op['content']) for op in operations)
        assert text.count('BẮT ĐẦU NỘI DUNG BÁO CÁO')==copies+1
        assert text.count('KẾT THÚC NỘI DUNG BÁO CÁO')==copies+1
        for op in operations: assert op['id']+' — '+op['target'] in text
        assert 'KHÔNG thay toàn bộ 8.6 hoặc 8.6.1' in text
        assert len(tree.xpath('//w:drawing',namespaces=ns))==2  # 7.1/7.2; existing result charts are explicitly retained.
        xml_tables=tree.xpath('//w:tbl',namespaces=ns)
        # Replacement-only tables contain data rows, not an extra column-header row to paste by mistake.
        for op in [o for o in operations if o['rows_only']]:
            first_key=op['content'].splitlines()[2].split('|')[1].strip()
            found=[t for t in xml_tables if t.xpath('.//w:tr[1]/w:tc[1]//w:t/text()',namespaces=ns)==[first_key]]
            assert len(found)==1,(op['id'],first_key)
            assert len(found[0].xpath('./w:tr',namespaces=ns))==len(op['replacement'])
    for rel,digest in protected.items(): assert sha(ROOT/rel)==digest,rel
    evidence=runpy.run_path(str(renderer_path))['verify_evidence']()
    # Persist the verified plan and virtual result only as audit inputs; never overwrite canonical chapters.
    dump(EVIDENCE/'placement-plan.json',operations)
    dump(EVIDENCE/'evidence-verification.json',evidence)
    dump(EVIDENCE/'virtual-application.json',dict(
        applied_without_missing_or_duplicate_anchors=True,
        canonical_chapters_written=False,
        chapter_after_sha256={str(n):hashlib.sha256(t.encode()).hexdigest() for n,t in working.items()},
        shared_8_6_children_2_to_5_preserved=True, table_15_1_L01_L02_preserved=True,
        review_only_9_4_and_14_2_preserved=True, result_tables_and_charts_12_5_preserved=True))
    result=dict(status='PASS',date='2026-10-28',docx=DOCX.relative_to(ROOT).as_posix(),docx_sha256=sha(DOCX),
        markdown=MARKDOWN.relative_to(ROOT).as_posix(),markdown_sha256=sha(MARKDOWN),
        operations=len(operations),paste_blocks=copies,
        operation_counts={kind:sum(op['kind']==kind for op in operations) for kind in names},
        precise_source_anchors_verified=True,virtual_application_verified=True,notes_outside_paste_blocks=True,
        original_chapters_preserved=True,full_report_reexported=False,java_tests_rerun=False,protected_files=len(protected))
    dump(EVIDENCE/'revision-manifest.json',result)
    dump(EVIDENCE/'checksums.sha256.json',{p.relative_to(ROOT).as_posix():sha(p) for p in
        [DOCX,MARKDOWN,Path(__file__),*EVIDENCE.glob('*.json')] if p.name!='checksums.sha256.json'})
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__': main()
