"""Apply the user's per-section editorial requirements, without a global shortening policy."""
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

BASE = 'CHINH_NOI_DUNG_BAO_CAO_THEO_PHAN_CONG_2026-10-28'
MARKDOWN = ROOT / 'report/revisions' / (BASE+'.md')
DOCX = MARKDOWN.with_suffix('.docx')
EVIDENCE = ROOT / 'report/evidence/chinh-assignment-report-2026-10-28'
CHAPTERS = ROOT / 'report/chapters'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def section(text, number):
    match = re.search(r'(?m)^(#{2,4}) '+re.escape(number)+r'\. .*$', text)
    assert match, number
    remainder = text[match.end():]
    end = len(text)
    for next_heading in re.finditer(r'(?m)^#{2,4} (\d+(?:\.\d+)+)\. ', remainder):
        if not next_heading[1].startswith(number+'.'):
            end = match.end()+next_heading.start()
            break
    value = text[match.start():end]
    return re.sub(r'(?m)^> \*\*Phân công:.*\n?', '', value).strip()


def chapter(number):
    paths = list(CHAPTERS.glob(f'{number:02d}_*.md'))
    assert len(paths) == 1
    return paths[0].read_text(encoding='utf-8')


def main():
    assert not (EVIDENCE / 'revision-manifest.json').exists(), 'Use a fresh revision after a completed export.'
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    protected = {p.relative_to(ROOT).as_posix(): sha(p) for folder in ('src', 'report/chapters', 'report/final', 'report/references')
                 for p in (ROOT / folder).rglob('*') if p.is_file()}
    clean_path = ROOT / 'report/revisions/CHINH_NOI_DUNG_BAO_CAO_2026-10-28.md'
    clean = clean_path.read_text(encoding='utf-8')
    c7, c9, c10, c11, c12, c13, c14, c16 = [chapter(n) for n in (7, 9, 10, 11, 12, 13, 14, 16)]
    blocks = [section(clean, n) for n in ('5.2','5.3','6.1.2','6.1.3','6.2.3','6.3','7.1')]
    blocks.append('''## 7.3. Single-writer state, command queue và runtime theo phòng

Mỗi runtime có map, state, extension và một game thread riêng. Network chuyển intent vào command queue thay vì sửa Player hoặc GameMap trên luồng socket. Game thread áp dụng command rồi xuất snapshot bất biến qua outbound FIFO; consumer gửi không cần đọc world mutable.

Bước mô phỏng cố định được lựa chọn theo phân tích timestep [9]. Một tick xử lý command theo FIFO và giới hạn lấy mẫu, cập nhật movement, gọi extension rồi công bố snapshot. Khi trễ lịch, loop điều chỉnh mốc tick tiếp theo thay vì chạy bù toàn bộ. Nhịp tick là mục tiêu cấu hình, không phải bảo đảm thời gian thực.

**Thuật toán 7.1. Vòng cập nhật theo runtime.**

```text
onStart của extension
while runtime chạy:
    chuẩn bị tick; sampled = tập rỗng
    trong giới hạn command mỗi tick:
        xem head queue; dừng nếu hết command
        nếu head là mẫu movement mới thứ hai của player đã sampled: dừng đọc
        lấy command; áp lifecycle hoặc movement khi đủ điều kiện
        ghi player vào sampled nếu áp mẫu sequenced thành công
        chuyển command tới extension
    buộc player frozen dừng; cập nhật movement rồi gameplay
    tăng tick; tạo và công bố update theo chính sách full/delta
    chờ tới lịch tick tiếp theo
finally: onStop và cleanup
```

Peek và dừng tại head giữ FIFO toàn cục, nhưng có thể làm command của player khác phía sau đợi thêm tick. Rate limit và queue hữu hạn hỗ trợ kiểm soát tải, chưa bảo đảm không backlog hoặc công bằng tuyệt đối. Sequence, ACK và vị trí chỉ tiến theo command được mô phỏng, không theo số packet đã nhận.

Command disconnect/reconnect cũng đi qua game thread: giữ hoặc gỡ frozen theo vòng đời phiên, không để attach socket trực tiếp sửa world. Submit thất bại không đồng nghĩa lifecycle đã áp dụng; tầng điều phối phải xử lý nhánh lỗi. Các capacity, giới hạn tick và API lifecycle được trình bày tại mục 10.3.
''')
    movement = '\n\n'.join(['## 7.4. Movement/collision và đồng bộ chuyển động phía client'] + [section(c7, n) for n in ('7.4.1','7.4.2','7.4.3')])
    movement = movement.replace('Quãng đường mỗi trục được chia thành bước tối đa 1 pixel rồi kiểm tra vị trí chiếm chỗ;\ntrục X xử lý trước Y.',
                                'Quãng đường được kiểm tra theo từng bước nhỏ trên mỗi trục; cấu hình và thứ tự xử lý chi tiết nằm tại mục 10.4.3.')
    movement = movement.replace('Giới hạn 256 pending ngăn lịch sử tăng mãi, khi đầy báo lỗi cho caller;\nkhông có bảo đảm tự retry/resync mọi tình huống.',
                                'Pending có giới hạn để lịch sử không tăng mãi; khi không thể tiếp nhận input, client báo lỗi theo chính sách. Giới hạn cụ thể nằm ở mục 10.5.')
    movement = movement.replace('Project giữ tối đa 32 frame vị trí; render timeline lùi 2 tick và giới hạn mức tiến của timeline khi thiếu update.',
                                'Client giữ buffer vị trí có giới hạn, render lùi thời gian và chặn mức tiến timeline khi thiếu update; các tham số nằm ở mục 10.5.')
    blocks.append(movement)
    delta = '\n\n'.join(['## 7.5. State Delta Compression và phục hồi baseline'] + [section(c7, n) for n in ('7.5.1','7.5.2','7.5.3','7.5.4','7.5.5')])
    delta = re.sub(r'```mermaid\n.*?\n```', '![Tạo delta, pending và commit](../figures/rendered/07_02_delta_va_commit.png)', delta, flags=re.S)
    delta = delta.replace('wantFull := requested hoặc t=1 hoặc t chia hết 100 hoặc state=FINISHED',
                          'wantFull := requested hoặc tick đầu hoặc đến chu kỳ full hoặc state=FINISHED')
    delta = delta.replace('Nếu full khi đang phục hồi phiên: xóa pending cũ và interpolation, giữ sequence/counter\n    Ngược lại nếu respawn counter đổi: xóa pending trước hồi sinh',
                          'Nếu respawn counter đổi: xóa pending trước hồi sinh\n    Nếu recovery: áp dụng quy tắc reset và mở input ở mục 7.8')
    delta = re.sub(r'Khi đang phục hồi phiên, owner áp thêm gate trước thuật toán:.*?trước khi resume theo mục 7\.8\.',
                   'Session Recovery bổ sung gate đúng epoch/context và full đã áp dụng trước khi mở input như mục 7.8.', delta, flags=re.S)
    cost = section(c7, '7.5.6').split('**Bảng 7.4.', 1)[0].strip()
    delta += '\n\n'+cost+'\n\nChi phí biểu diễn binary/Base64 và phạm vi byte được xác định tại chương 9 và mục 11.5. Kết quả đo được trình bày riêng ở mục 12.5.'
    blocks.append(delta)
    blocks.append('''### 7.8.2. Freeze/unfreeze và baseline sau phục hồi

Callback disconnect của lobby submit PlayerDisconnectedCommand để game thread giữ player nhưng đưa vào tập frozen. Player bị buộc dừng trước movement update; gameplay extension vẫn xử lý bom, item, sát thương và timer. Command reconnect gỡ frozen và yêu cầu full trên cùng runtime, không tạo một lượt hoặc matchId mới.

Trong lúc phục hồi, đường nhận của player bị suspend; các delta/full cũ trong queue không được dùng làm nền mới. Tầng điều phối đặt barrier dựa trên tick đã công bố, yêu cầu runtime tạo full mới và chỉ đánh dấu initialized sau khi full vượt barrier được enqueue thành công. Đây là gate phía server; nó chưa chứng minh client đã nhận hoặc apply. Baseline dùng chung runtime nên full có thể được gửi tới cả roster.

Nếu queue không nhận command lifecycle, tầng điều phối xử lý theo nhánh kết thúc, không bỏ qua freeze/unfreeze rồi tiếp tục giả định phiên đã an toàn. Dữ liệu trong full phản ánh world hiện tại, bao gồm thay đổi gameplay xảy ra khi player offline; full không phải lịch sử để áp lại damage hoặc pickup.

### 7.8.3. Input và lịch sử chuyển động khi phục hồi

Ngay khi bắt đầu recovery, client khóa input, tăng input generation và clear tác vụ gửi chờ. Task đã được lấy khỏi queue còn kiểm tra generation/trạng thái trước send. InputController xóa phím giữ khi generation đổi, kể cả recovery hoàn tất giữa hai lần lấy mẫu; vì vậy intent từ kết nối cũ không tự xuất hiện như thao tác mới.

Client giữ controller/context, next sequence MOVE và counter request đặt bom. Pending prediction và interpolation cũ được xóa; replica đánh dấu cần full nhưng vẫn có thể giữ world cũ để vẽ trạng thái đang phục hồi. Cơ chế này không thu hồi lệnh đã tới server hoặc đảo ngược tác động đã được xử lý trước disconnect.

Sau ACK và metadata đúng phiên/trận/epoch, client cần áp dụng một full hợp lệ và xác nhận lastAppliedFullTick đúng update vừa xử lý, replica không còn needsFullState. Khi đó prediction được thiết lập lại từ PlayerData authoritative, sequence/request counter không lùi và input chỉ được mở nếu controller/match còn đủ điều kiện. Trạng thái còn sống tiếp tục được kiểm tra khi movement/đặt bom.

ACK phiên riêng lẻ, delta, full stale hoặc sai context không đủ hoàn tất recovery. Sau resume, client lấy mẫu thao tác mới thay vì replay mọi phím trong thời gian offline. Điều này khác reconciliation trên kết nối liên tục, vốn replay input pending chưa ACK; nó cũng không phát lại lịch sử gameplay hoặc kết quả trận bị bỏ lỡ.
''')
    blocks += [section(clean, n) for n in ('8.3','8.6')]
    blocks += ['## 9.4. MOVE, sequence/ACK, snapshot và full/delta/resync']
    blocks += [section(c9, n) for n in ('9.4.1','9.4.3','9.4.4','9.4.5')]
    blocks.append((ROOT / 'report/revisions/parts/CHINH_10_TRIEN_KHAI_2026-10-28.md').read_text(encoding='utf-8'))
    hud = section(c10, '10.7.1').replace(' — phần TV2', '')
    blocks.append(hud)
    setup = section(c11, '11.5')
    setup = setup.replace('### 11.5.2.',
        'Tỷ lệ giảm được tính bằng `100 × (1 − B_delta/B_full)` với B_full dương và hai tổng có cùng phạm vi byte. '
        'Giá trị âm thể hiện delta dùng nhiều dữ liệu hơn, không bị loại khỏi báo cáo. '
        'Kịch bản cần xét correctness replica trước khi nhận mức giảm byte; kết quả byte không tự chứng minh lợi ích latency.\n\n### 11.5.2.', 1)
    setup = setup.replace('D1 chỉ được công bố khi đã có harness lưu trace và kiểm tra equality replica sau mỗi tick.',
                          'Harness D1 lưu trace và kiểm tra equality replica sau mỗi tick như điều kiện chấp nhận kết quả.')
    setup += '''

### 11.5.3. Phạm vi byte và chi phí biểu diễn tile

Binary snapshot được bọc Base64 trong JSON. Với n byte binary, Base64 có padding dùng `4×ceil(n/3)` ký tự [13]; do đó hai chế độ phải được đo sau cùng lớp encode, tính cả count/header, match envelope và frame ứng dụng. Khi đánh giá toàn luồng cần tính notice/control theo cùng quy tắc ở cả hai nhánh; phép đo snapshot riêng không bao gồm các thành phần đó.

Theo layout tile hiện tại, full dùng một byte mỗi ô, còn một tile delta cần bốn byte x, bốn byte y và một byte loại nền. Với map 17×15, riêng giá trị full map là 255 byte; một ô đổi cần chín byte, 29 ô đổi cần 261 byte ở delta. Đây là tính toán layout, chưa gồm metadata/player/entity/frame và không phải số đo toàn packet. Nó cho thấy lý do không thể bảo đảm delta luôn nhỏ hơn full; implementation hiện chưa chọn loại packet nhỏ nhất bằng cách encode thử cả hai.
'''
    blocks.append(setup)
    runtime_results = section(c12, '12.2')
    runtime_results = runtime_results.replace('## 12.2. Movement/runtime/client synchronization',
        '## 12.2. Movement/runtime/client synchronization\n\nCác kết quả trong Bảng 12.3–12.4 thuộc suite baseline 133/133 JUnit ngày 26/10/2026. '
        'Lượt hồi quy sau tích hợp recovery ngày 27/10/2026 được nêu riêng ở cuối mục; hai mốc không được gộp thành một lượt kiểm thử.')
    runtime_results = runtime_results.replace('Kết quả lượt mới', 'Kết quả baseline 26/10/2026')
    runtime_results += '''

### 12.2.3. Hồi quy sau tích hợp recovery

Lượt sau sửa recovery đạt 171/171 JUnit trong 44 class ngoài sandbox. RuntimeContractTest và MovementFeatureTest đạt 1/1 mỗi lớp; MovementBalanceTest đạt 4/4, MovementDemoTest 8/8, RespawnPredictionTest 2/2 và DeltaCompressionTest 1/1. RecoveryInputTest đạt 2/2; RecoveryGameplayIntegrationTest có 8/8 test tích hợp, gồm kiểm tra state/counter/full→delta cùng các tình huống session/gameplay. Các lớp này là tập con trong 171 execution, không được cộng lại thành test chạy thêm.

Số đếm và XML được lưu tại [class-results.csv](../evidence/recovery-report-task03-20261027-200413/class-results.csv), [test-executions.csv](../evidence/recovery-report-task03-20261027-200413/test-executions.csv) và [surefire](../evidence/recovery-report-task03-20261027-200413/surefire/). Kết quả baseline được giữ tại [hồ sơ ngày 26/10](../evidence/task12-2026-10-26/README.md). Check main do wrapper JUnit gọi lại không tạo thêm một nhóm coverage độc lập.
'''
    blocks.append(runtime_results)
    results = section(c12, '12.5')
    method_start, method_end = results.index('### 12.5.1.'), results.index('### 12.5.2.')
    results = results[:method_start]+'''### 12.5.1. Lượt đo và bộ dữ liệu

Ngày 26/10/2026, D0 chạy năm process Java mới; D1 chạy năm process, mỗi process gồm sáu cấu hình, tổng cộng 35 scenario-run. D0 dùng snapshot v2 không match envelope, D1 dùng v5 có envelope. Hai nhánh full/delta nhận cùng state theo phương pháp ở mục 11.5. D0 có ba full trong B1, D1 có bảy full; phép đo này không phát sinh full do disconnect, queue đầy hoặc mất baseline.

Dữ liệu, manifest, log và trace nằm trong [hồ sơ thực nghiệm delta](../evidence/task13-2026-10-26/README.md). Kết quả là byte frame snapshot ứng dụng, không phải toàn traffic TCP/IP. Mỗi tỷ lệ giảm so hai nhánh trong cùng cấu hình; D0 và D1 khác phiên bản/số tick/player nên không so tổng byte trực tiếp như hai cách encode cùng workload.

'''+results[method_end:]
    blocks.append(results)
    blocks.append('''### 12.8.3. Tính đúng replica và điều khiển sau recovery

Kết quả `multi_input_bomb` trong [case-results.csv](../evidence/recovery-report-task03-20261027-200413/case-results.csv) xác nhận ba chu kỳ reconnect, ba full bằng replica peer ở cùng tick và ba lần delta tiếp tục sau full. Fixture tạo nhiều input/yêu cầu đặt bom trước ngắt; controller và bộ đếm được giữ để thao tác mới vẫn hợp lệ, yêu cầu cũ không bị dùng lại như một placement mới.

Equality full kiểm tra kích thước map, tile size, match state, toàn bộ tile/PlayerData và ACK, entity, MatchFrame và BombFrame tại cùng tick. Nó khác phép chuẩn hóa trong harness D1, nơi replica có thể giữ metadata tick/clock cũ ở tick không gửi. Full không gọi lại damage hoặc item effect; state gameplay phản ánh diễn biến thật của runtime trong khoảng mất kết nối.

RecoveryInputTest kiểm tra khóa input và clear phím theo generation; các assertion integration còn kiểm tra giữ cùng runtime/controller, counter và chuỗi full→delta. Bằng chứng này xác nhận các invariant trong fixture TCP cục bộ, không đại diện cho tỷ lệ phục hồi trên Wi-Fi/LAN thực tế hoặc một phân phối latency recovery. Các attempt sandbox có smoke failure và lượt ngoài sandbox PASS vẫn được lưu riêng ở [hồ sơ kiểm thử recovery](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md).
''')
    discussion = '''## 13.2. Lợi ích, chi phí và phạm vi hiệu quả delta

### 13.2.1. Vì sao hiệu quả phụ thuộc workload

Workload ít thay đổi hưởng lợi theo hai hướng: tránh truyền lại record không đổi và không phát packet ở tick không có thay đổi có ý nghĩa. Timer hoặc frame gameplay vẫn có thể làm phát update dù tile không đổi. Vì vậy, kết quả idle không chỉ đo mức tiết kiệm của tile diff.

Với movement liên tục, vị trí và ACK của nhiều player đổi ở mỗi bước lấy mẫu. Builder gửi lại cả PlayerData thay vì từng field riêng, nên phần player/metadata tiếp tục chiếm byte, trong khi map cố định được loại khỏi delta. Tăng roster làm phần player lớn hơn mà không tăng tương ứng phần map có thể bỏ; đây là lý do tỷ lệ giảm khác nhau giữa các cấu hình của mục 12.5. Nó không xác lập quy luật scale tuyến tính cho mọi map hoặc số người chơi.

Trace sự kiện có các mốc bom/block/item xác định và đoạn dài ít thay đổi sau sự kiện cuối. Mức giảm cao trong trace này vì vậy không đại diện cho đặt bom liên tục hoặc map/entity thay đổi dày. Việc so sánh phải giữ cùng đầu vào và xem cả số packet phát, không chỉ size của một delta được chọn.
'''
    discussion += '\n\n'+section(c13, '13.2.2')+'\n\n'+section(c13, '13.2.3')
    discussion += '''

## 13.3. Tick, FIFO, backlog và prediction correction

### 13.3.1. Thời gian chờ mô phỏng

PING/PONG và ACK input đi qua các đường xử lý khác nhau: phản hồi mạng không chứng minh input đã được mô phỏng, còn ACK trong snapshot chỉ phản ánh sequence server đã xử lý. Input có thể chờ queue, lịch tick và công bố snapshot trước khi được client quan sát. Kết quả mạng ở mục 12.6 chưa có trace từng pha để tách riêng các thời gian đó.

GameLoop giới hạn command/tick và chỉ áp một mẫu movement sequenced thành công/player. Nếu head queue là mẫu tiếp của player vừa được lấy mẫu, loop dừng đọc để giữ FIFO; command của người khác phía sau cũng chờ. Đây là khả năng gây backlog và giới hạn fairness, chưa phải bottleneck đã được chứng minh ở tải đã thử. Giới hạn tổng command/tick không có nghĩa cùng một player được mô phỏng từng ấy input trong một tick.
'''
    pressure = section(c13, '13.3.2')
    pressure = pressure.replace('Trong nhóm mạng đã đo, không có stale/resync nhưng còn tổng 14 MOVE pending cuối cửa sổ.\nĐó là giới hạn quan sát completion, chưa chứng minh message loss hoặc đã mất tính nhất quán.',
                                'Input còn pending ở cuối cửa sổ đo là một giới hạn quan sát completion, chưa đủ để kết luận message loss hoặc mất tính nhất quán.')
    discussion += '\n\n'+pressure+'\n\n'+section(c13, '13.3.3')
    blocks.append(discussion)
    blocks.append(section(c14, '14.2'))
    blocks.append('''## 14.5. Đóng góp runtime/client trong Session Recovery

Phần runtime/client nối cơ chế giữ phiên với trạng thái game đang chạy: freeze/unfreeze được thực hiện qua game thread; snapshot barrier yêu cầu một full mới sau khi nhận lại phiên; controller, sequence và request counter được giữ xuyên handoff. Input generation loại tác vụ/phím cũ, trong khi pending prediction/interpolation được thiết lập lại từ full authoritative.

Điều kiện hoàn tất nằm ở full đúng context đã apply, không chỉ socket nối được hoặc ACK phiên đã tới. Cách tổ chức này giữ cùng runtime/world và tránh dùng một delta không có nền để mở lại điều khiển. Các ca ở mục 12.8 kiểm tra nhiều input trước ngắt, cùng controller/counter, full bằng peer ở cùng tick rồi delta; RecoveryInputTest còn kiểm tra reset phím qua generation.

Đây là đóng góp tích hợp với session/transport, không phải một cơ chế replay toàn bộ input/event. Full bổ sung có chi phí và có thể gửi tới cả roster. Bộ test correctness không thay cho A/B về latency, byte hoặc tỷ lệ hoàn tất trận; các kết quả byte D1 trước recovery không tự chứng minh cơ chế phục hồi nhanh hoặc nhẹ hơn.
''')
    blocks.append(section(clean, '15.1.3'))
    future = section(c16, '16.2')
    future += '''

### 16.2.4. Chi phí bộ nhớ và chính sách giới hạn

Đánh giá cần tách retained/peak heap của baseline, pending update, outbound queue và lịch sử client. Capacity tính theo số phần tử chưa cho biết số byte giữ lại, vì update full/delta có kích thước khác nhau. Cần ghi queue depth/age, allocation và GC theo cùng workload/map/roster để xác định nguyên nhân trước khi giảm copy hoặc dùng lại buffer.

Bất kỳ tối ưu bộ nhớ nào cũng phải giữ snapshot đã xuất bản không thay đổi, consumer đọc đúng thứ tự và baseline không tiến trước enqueue. Thử nghiệm queue nhỏ hoặc client chậm cần kiểm tra cả fallback full và lifecycle recovery, không chỉ số byte hoặc số object giảm.
'''
    blocks.append(future)
    content = '\n\n'.join(blocks)
    content = re.sub(r'(?m)^> \*\*Phân công:.*\n?', '', content)
    content = content.replace('TV2 cung cấp', 'Core cung cấp').replace('TV3', 'gameplay extension').replace('TV4', 'tầng protocol')
    content = content.replace('API runtime và ranh giới dữ liệu TV2', 'API runtime và ranh giới dữ liệu')
    content = content.replace('Không nên dùng map tối giản', 'Map tối giản không được dùng')
    # References copied from chapter prose resolve to the canonical chapters from this file's directory.
    names = {p.name for p in CHAPTERS.glob('*.md')}
    content = re.sub(r'\]\(([^)]+)\)', lambda m: ']('+'../chapters/'+m[1]+')' if m[1].split('#')[0] in names else m[0], content)
    content = re.sub(r'\n{3,}', '\n\n', content).strip()+'\n'
    forbidden = ['Thao tác ghép', 'Phân công:', 'Chinh', 'Giang', 'Mai', 'Duy', 'ghi chú nội bộ', 'người ghép',
                 'chờ đối chiếu', 'TV1', 'TV2', 'TV3', 'TV4', 'giữ Bảng', 'Giữ Bảng', 'INSERT_']
    assert all(value not in content for value in forbidden), [value for value in forbidden if value in content]
    MARKDOWN.write_text(content, encoding='utf-8')
    # Restore the verified evidence checks, without executing Java or benchmarks.
    old_builder = ROOT / 'report/experiments/build_chinh_editorial_handoff.py'
    evidence = runpy.run_path(str(old_builder))['verify_evidence']()
    renderer_source = old_builder.read_text(encoding='utf-8')
    renderer = textwrap.dedent(renderer_source[renderer_source.index('    doc = Document()'):renderer_source.index('    # Structural and scope QA')])
    renderer = renderer.replace("'CHINH | NỘI DUNG CHỈNH SỬA ĐỂ GHÉP | 28/10/2026'", "'BOMB IT MULTIPLAYER'")
    renderer = renderer.replace("'Chinh — Nội dung chỉnh sửa báo cáo theo phân công mới'", "'Bomb It Multiplayer — Nội dung báo cáo'")
    renderer = renderer.replace("'Chinh — tên gọi theo phân công nội bộ'", "''")
    renderer = renderer.replace("'Chỉ phần sửa/bổ sung để ghép; không phải toàn bộ báo cáo'", "'Cơ sở lý thuyết, giải pháp, triển khai và đánh giá'")
    namespace = dict(globals(), content=content)
    exec(compile(renderer, '<assignment-report-renderer>', 'exec'), namespace)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(DOCX) as archive:
        assert archive.testzip() is None
        xml = etree.fromstring(archive.read('word/document.xml'))
        text = ' '.join(xml.xpath('//w:t/text()', namespaces=ns))
        assert all(value not in text for value in forbidden)
        for token in ('7.5.1.', '7.5.2.', '7.5.3.', '7.5.4.', '7.5.5.', '7.5.6.', '10.3.5.', '10.4.6.', '10.5.7.',
                      '11.5.3.', '12.5.2.', '12.5.3.', '12.5.4.', '12.5.5.', '13.2.2.', '13.3.3.', '14.2.2.', '16.2.4.',
                      '110076', '16411', '358780', '60648', '18.000', '171/171', '133/133'):
            assert token in text, token
        images = len(xml.xpath('//w:drawing', namespaces=ns))
        tables = len(xml.xpath('//w:tbl', namespaces=ns))
        assert images == 4, images
    for rel, digest in protected.items(): assert sha(ROOT / rel) == digest, rel
    links = 0
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if '://' not in target and not target.startswith('#'):
            assert (MARKDOWN.parent / target.split('#')[0]).exists(), target
            links += 1
    # Audit the policy per section. These records stay outside the paste-ready deliverable.
    policy = {
        '5.2-5.3': 'Retain the requested shorter theory, citations, comparison and hitbox concept.',
        '6': 'Requirements and consistency, without algorithms or class inventory.',
        '7.1': 'Shorter overview with the input-state-client figure.',
        '7.3': 'Retain ownership/FIFO/lifecycle rationale; shorten only the tick pseudocode and move capacities to implementation.',
        '7.4': 'Preserve movement/ACK/replay/respawn reasoning; implementation parameters in chapter 10, recovery detail in 7.8.',
        '7.5': 'Restore detailed diff, tombstones, pending, enqueue/commit, apply/resync, example and correctness argument; move evaluation to 11.',
        '8': 'Concise component responsibilities and ownership, no repeated diagrams.',
        '9': 'Preserve audited MOVE, ACK, tick/baseTick, snapshot/resync semantics without rewriting framing or unrelated packets.',
        '10': 'Condense module prose while retaining all 18 implementation subheadings and actual API/configuration/lifecycle details.',
        '11-12': 'Preserve measurement design, byte/equality scope, all seven size rows, packet counts, original charts and evidence paths.',
        '13': 'Preserve explanations, confounders, costs and prediction reasoning; do not repeat result tables/algorithms.',
        '14': 'Retain contribution boundary, inherited method and quantitative proof; runtime/client contribution to recovery only.',
        '15-16': 'Retain limitations and linked remedies, profiling/memory/baseline/fairness/correction/interpolation checks.'}
    measures = {}
    for number in ('5.2','5.3','7.5','10.3','10.4','10.5','11.5','12.2','12.5','13.2','13.3','14.2','16.2'):
        measures[number] = dict(previous_words=len(section(clean, number).split()), revised_words=len(section(content, number).split()))
    for number in ('7.5','11.5','12.2','12.5','14.2','16.2'):
        assert measures[number]['revised_words'] > measures[number]['previous_words']
    for number in ('10.3','10.4','10.5'):
        assert measures[number]['revised_words'] > measures[number]['previous_words']
    catalog = json.loads((ROOT / 'report/references/sources.json').read_text(encoding='utf-8'))
    sources = {s['final_number']:s for s in catalog['sources']}
    for number, url in re.findall(r'\[\[(\d+)\]\]\(([^)]+)\)', content):
        assert url in {sources[int(number)]['url'], sources[int(number)]['verified_content_url']}
    source_paths = [clean_path, old_builder, ROOT / 'report/revisions/parts/CHINH_10_TRIEN_KHAI_2026-10-28.md']
    dump(EVIDENCE / 'editorial-policy.json', policy)
    dump(EVIDENCE / 'section-comparison.json', measures)
    dump(EVIDENCE / 'evidence-verification.json', evidence)
    dump(EVIDENCE / 'revision-manifest.json', dict(status='PASS', date='2026-10-28',
        docx=DOCX.relative_to(ROOT).as_posix(), docx_sha256=sha(DOCX), markdown=MARKDOWN.relative_to(ROOT).as_posix(),
        markdown_sha256=sha(MARKDOWN), images=images, tables=tables, local_links_checked=links,
        preserved_input_files=len(protected), java_sources_verified=219, internal_notes_absent=True,
        blanket_shortening=False, per_section_policy_recorded=True, tests_rerun=False, full_report_reexported=False,
        source_inputs={p.relative_to(ROOT).as_posix():sha(p) for p in source_paths}))
    dump(EVIDENCE / 'checksums.sha256.json', {p.relative_to(ROOT).as_posix():sha(p) for p in
         [DOCX, MARKDOWN, Path(__file__), *EVIDENCE.glob('*.json')] if p.name != 'checksums.sha256.json'})
    print(json.dumps(dict(status='PASS', docx=str(DOCX), tables=tables, figures=images,
                         local_links=links, section_words=measures), ensure_ascii=True))


if __name__ == '__main__':
    main()
