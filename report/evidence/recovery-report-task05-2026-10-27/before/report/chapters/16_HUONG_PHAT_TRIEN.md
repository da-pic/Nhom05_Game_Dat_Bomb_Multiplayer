# 16. Hướng phát triển — Future Work

> **Phân công: mỗi thành viên đề xuất và kiểm chứng phần mình; TV4 tổng hợp thứ tự ưu tiên, protocol và phép đo liên module. Đây là đề xuất, chưa phải chức năng hoặc kết quả đã triển khai.**

Hướng phát triển được chọn từ hạn chế ở mục 15 và bằng chứng ở mục 12–13.
Ưu tiên đầu tiên là hoàn thiện nghiệm thu và khả năng quan sát trước khi mở rộng lời hứa hiệu năng hoặc thêm tính năng lớn.
Các tiêu chí dưới đây là điều kiện kiểm chứng đề xuất, không phải SLA hoặc lịch cam kết đã được nhóm phê duyệt.

## 16.1. Hoàn thiện và mở rộng chức năng

### 16.1.1. Hoàn thiện luồng chơi và phản hồi người dùng

Tổ chức nghiệm thu GUI hai/bốn người cho tạo/vào phòng, ready/start, chat, movement/STOP,
mất focus, placement, item/lives/shield/respawn, kết quả và replay.
Mỗi lượt cần run/match ID, người kiểm tra, ảnh/video và log hai đầu; lỗi UI phải được đối chiếu với state authoritative.
Chỉ sau nghiệm thu mới kết luận các thao tác đã hoạt động với người dùng thật trong topology tương ứng.

Một cải tiến chức năng cụ thể là response placement có request ID và mã kết quả nghiệp vụ rõ ràng.
Cần phân biệt request đã qua gate/được enqueue với bom thật sự được luật gameplay chấp nhận,
giữ dedupe khi nhận lại request và không tạo bom dự đoán chỉ để che độ trễ.
TV3 cung cấp kết quả luật, TV2 nối command/runtime, TV1/TV4 thống nhất contract/gửi phản hồi và client hiển thị.
Phải kiểm tra cả thành công, quota, ô có bom, player chết, request lặp và match cũ trước khi nhận tính năng.

### 16.1.2. Thứ tự ưu tiên và điều kiện kiểm chứng

**Bảng 16.1. Các nhóm công việc đề xuất gắn với hạn chế.**

| Ưu tiên | Hạn chế liên quan | Công việc | Điều kiện kiểm chứng đề xuất | Phụ trách |
|---|---|---|---|---|
| P1 | L07/L08/L10 | Nghiệm thu GUI/LAN, bổ sung CPU/RAM/topology và raw log | Biên bản thao tác, kết quả hai đầu, metadata đủ cho từng máy | Cả nhóm, TV4 ghép |
| P1 | L02 | Placement response theo request | Test kết quả luật/dedupe/match scope và kiểm tra client không hiểu enqueue là placement thành công | TV3/TV2/TV1/TV4 |
| P1 | L05/L10 và lỗi smoke lịch sử | Ghi enqueue/dequeue/tick/full-ready/deadline, tái hiện lỗi setup | Log phân biệt lỗi môi trường, handshake, setup và snapshot; giữ attempt fail/pass | TV2/TV4, TV1 hỗ trợ |
| P2 | L03/L04/L06 | Tối ưu đồng bộ/correction dựa trên profiling và trace | State đúng, byte/CPU/latency/UX được đo trên cùng workload trước–sau | TV2/TV4 |
| P2 | L01 | Thiết kế resume có xác thực và generation | Qua ma trận race/resume/full-baseline và luật hết hạn đã thống nhất | TV1/TV2/TV4, TV3 xác nhận gameplay |
| P3 | L09/L10 | Tải nhiều room và vận hành dài hạn | Có đường cong tải, queue/tick/tài nguyên và cleanup sau chạy | TV4, owner từng module |

P1/P2/P3 là thứ tự ưu tiên tương đối của đề xuất, không phải xác nhận đã làm hoặc ước lượng số ngày.
Mở rộng map/chế độ chơi chỉ nên theo sau các bước trên và giữ test contract theo kích thước/luật mới;
không coi việc thêm nội dung đồ họa là thay thế đóng góp kỹ thuật đã xác định ở mục 14.

## 16.2. Tối ưu đồng bộ/client correction và tài nguyên

### 16.2.1. Đo trước khi đổi format hoặc lịch gửi

Bổ sung timestamp enqueue/dequeue, thời gian từng phần tick, kích thước từng nhóm field,
encode/decode duration, allocation/GC và queue occupancy.
Thu trace người chơi thật và trace đứng yên vẫn gửi input để tách tác dụng của ACK khỏi thay đổi vị trí.
Xuất raw RTT/ACK sample và correction theo cùng mốc mô phỏng để có thể tính phân bố phù hợp,
thay vì suy pooled p95 từ các thống kê đã tổng hợp.

Các hướng cần thử gồm dirty tracking để tránh quét toàn map, field-level delta cho PlayerData,
hoặc chọn full khi encode delta lớn hơn full.
Mỗi hướng cần đối chứng cùng trace và cùng lớp đếm byte, tính cả full/resync;
đo thêm CPU/bộ nhớ để tránh đổi ít byte hơn lấy chi phí mô phỏng vượt ngân sách tick.
Nếu đổi precision/quantization phải đặt tiêu chí sai số có ý nghĩa cho collision/gameplay và kiểm tra replica,
không giảm độ chính xác chỉ để làm biểu đồ byte tốt hơn.

### 16.2.2. Bảo toàn input và baseline

Tối ưu mẫu đứng yên có thể giảm ACK update, nhưng phải định nghĩa lại rõ contract lấy mẫu, STOP và replay.
Không chỉ xóa input không giữ phím vì server hiện dựa vào mẫu có sequence để tiến bước/ACK theo tick.
Tương tự, nếu thay FIFO bằng cơ chế công bằng hơn theo player cần xác định thứ tự liên loại command
và kiểm tra lại MOVE/plant/disconnect cùng tick, tránh đổi ý nghĩa gameplay ngoài dự kiến.

Nếu xét baseline riêng từng receiver hoặc cơ chế coalesce snapshot,
phải bảo đảm delta chỉ tham chiếu nền receiver có thể dùng, có fallback full và test queue drop/backpressure.
Không bỏ một delta giữa chuỗi rồi tiếp tục gửi delta phụ thuộc nó.
Các lựa chọn này là hướng thử nghiệm, chưa chứng minh tốt hơn baseline xuất bản chung hiện tại.

### 16.2.3. Correction và khả năng quan sát client

Đo error trước/sau replay tại cùng thời điểm thích hợp, số lần correction, frame time và đoạn video tương ứng.
Sau đó mới thử visual smoothing local hoặc buffer nội suy thích ứng.
Smoothing phải reset khi respawn/match mới, không làm sai state collision hoặc hiển thị đi xuyên tường;
khi mất dữ liệu vẫn cần giới hạn ngoại suy/thời gian giữ endpoint.
So sánh bật/tắt cơ chế trên cùng trace delay/jitter, giữ nguyên authority server.

## 16.3. Reconnect có xác thực/generation an toàn

Resume là thay đổi nhiều lớp, không chỉ thêm handler RECONNECT.
Đề xuất cần bắt đầu bằng việc nhóm chốt chính sách giữ ghế/world trong grace,
player bị đứng yên hay vẫn chịu damage, khi nào hết hạn và xử lý kết quả nếu trận kết thúc trong lúc mất kết nối.
Chính sách này sẽ thay một phần hành vi ABORTED hiện tại nên phải được đặc tả và test cùng gameplay.

Thiết kế phiên cần xác thực quyền nhận lại player, quy định hạn/đổi token, request lặp và reconnect đồng thời.
Không tin player ID client tự khai làm bằng chứng sở hữu phiên.
Socket/writer mới cần gắn với connection generation; EOF/write failure/timer muộn của generation cũ
không được xóa phiên mới hoặc tiếp tục gửi dữ liệu như owner hiện tại.

Sau khi attach thành công, server cung cấp match context hiện tại và full state phù hợp.
Client chỉ bật input sau khi có nền hợp lệ; sequence/ACK/request dedupe được tiếp nối theo match,
không reset về 1 như lượt mới hoặc replay lại placement/damage/pickup.
Nếu trận đã kết thúc, trả kết quả đã chốt thay vì mở lại world.

**Bảng 16.2. Ma trận kiểm tra tối thiểu đề xuất cho resume.**

| Nhóm | Tình huống | Điều kiện cần xác nhận |
|---|---|---|
| Quyền/đồng thời | Token sai/hết hạn/dùng lại; hai reconnect cùng lúc | Không chiếm ghế; chỉ owner được nhận theo policy |
| Generation | Socket cũ EOF, writer cũ fail hoặc expiry timer cũ chạy sau attach | Không đóng/xóa connection generation mới |
| Deadline | Trước/sau grace; reconnect khi GAME_OVER đã chốt | State/ghế/kết quả tuân theo chính sách, không hồi sinh trận đã kết thúc |
| Input | MOVE đã/chưa ACK, request placement lặp, match cũ | Không dùng lại sequence sai hoặc áp dụng command hai lần |
| World | Còn bom/item/lửa, shield/respawn đang đổi | Full baseline hợp lệ, không cộng effect lại; input chỉ mở sau sync |
| Cleanup | Resume lỗi giữa handshake/attach/full | Không để hai writer active, ghost player hoặc tài nguyên không có owner |

Căn cứ phạm vi: [RECONNECT_ASSESSMENT](../../docs/RECONNECT_ASSESSMENT.md).
Các dòng trong bảng là tiêu chí tương lai; API legacy và test session hiện tại chưa chứng minh chúng đã đạt.

## 16.4. Đánh giá nhiều máy, tải lớn hơn và vận hành dài hạn

Mở rộng theo thứ tự loopback nhiều JVM → LAN nhiều máy → môi trường có delay/jitter có kiểm soát.
Mỗi topology cần metadata phần cứng, nguồn điện, kết nối, server/client version và công cụ tạo tải;
không trộn nhiều process cùng máy vào số liệu LAN hoặc trừ timestamp hai máy để suy one-way delay khi chưa kiểm soát clock.
Giữ baseline full/delta và metric definition cố định nếu mục tiêu là so sánh tác động mạng của compression.

Tăng tải bằng nhiều room với roster hợp lệ trước khi thay cap bốn người của một match.
Theo dõi tick overrun, queue depth/rejection, writer backlog, CPU/RAM/GC,
RTT/ACK cả mẫu hoàn tất lẫn request timeout/pending, error và cleanup sau đợt chạy.
Điểm bão hòa cần được xác định bằng tiêu chí rõ ràng, không suy từ giới hạn queue hoặc số thread cấu hình.

Soak phải lưu duration, số vòng, xu hướng tài nguyên và sự kiện lỗi theo thời gian;
test đóng/mở nhanh không thay phép đo này.
Đợt đánh giá cũng nên làm nóng workload thực, đổi thứ tự chạy có kiểm soát và tăng số run khi biến thiên yêu cầu.
Mọi sửa lỗi hoặc thay property tạo một batch mới có revision/artifact hash riêng,
giữ nguyên attempt cũ để so sánh và không chỉ chọn các lượt đạt.
