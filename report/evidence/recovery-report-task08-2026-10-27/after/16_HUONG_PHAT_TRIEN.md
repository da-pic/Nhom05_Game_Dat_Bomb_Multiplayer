# 16. Hướng phát triển — Future Work

> **Phân công: mỗi thành viên đề xuất và kiểm chứng phần mình; TV4 tổng hợp thứ tự ưu tiên, protocol và phép đo liên module. Đây là đề xuất, chưa phải chức năng hoặc kết quả đã triển khai.**

Hướng phát triển được chọn từ hạn chế ở mục 15 và bằng chứng ở mục 12–13.
Ưu tiên đầu tiên là hoàn thiện nghiệm thu và khả năng quan sát trước khi mở rộng lời hứa hiệu năng hoặc thêm tính năng lớn.
Các tiêu chí dưới đây là điều kiện kiểm chứng đề xuất, không phải SLA hoặc lịch cam kết đã được nhóm phê duyệt.

## 16.1. Hoàn thiện và mở rộng chức năng

### 16.1.1. Hoàn thiện luồng chơi và phản hồi người dùng

Tổ chức nghiệm thu GUI hai/bốn người cho tạo/vào phòng, ready/start, chat, movement/STOP,
mất focus, placement, item/lives/shield/respawn, kết quả và replay.
Thêm thao tác mất transport/khôi phục: trạng thái chờ trên cùng cửa sổ, khoá/mở input/nút đúng lúc,
đóng app để huỷ recovery và trường hợp trận kết thúc khi player vắng mặt.
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
| P1 | L07/L08/L10 | Nghiệm thu GUI/LAN cả recovery, bổ sung CPU/RAM/topology và raw log | Biên bản thao tác, kết quả hai đầu, metadata đủ cho từng máy | Cả nhóm, TV4 ghép |
| P1 | L02 | Placement response theo request | Test kết quả luật/dedupe/match scope và kiểm tra client không hiểu enqueue là placement thành công | TV3/TV2/TV1/TV4 |
| P1 | L05/L10 và lỗi smoke lịch sử | Ghi enqueue/dequeue/tick/full-ready/deadline, tái hiện lỗi setup | Log phân biệt lỗi môi trường, handshake, setup và snapshot; giữ attempt fail/pass | TV2/TV4, TV1 hỗ trợ |
| P1 | L01/L11 | Nhóm chốt policy expiry/gameplay và mô hình đe doạ token; đánh giá TLS/rotation nếu mở rộng | Không mặc định token đúng là xác thực tài khoản; policy đổi có test hồi quy và phương án rollback | TV1/TV4, TV2/TV3 xác nhận tích hợp |
| P2 | L03/L04/L06 | Tối ưu đồng bộ/correction dựa trên profiling và trace | State đúng, byte/CPU/latency/UX được đo trên cùng workload trước–sau | TV2/TV4 |
| P2 | L12 | Đo từng pha recovery, overhead full/retry và tải reconnect đồng thời | Timestamp có mốc rõ, byte/latency/error/pending/cleanup cùng workload; giữ attempt thất bại | TV1/TV2/TV4 |
| P2 | L13 | Xem xét replay kết quả đã chốt hoặc thông báo bị lỡ | Match/result/event identity rõ, không mở lại trận hoặc áp lặp effect | TV1/TV3/TV4, TV2 kiểm tra state |
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
Smoothing phải reset khi respawn/match mới hoặc full sau recovery, không làm sai state collision hoặc hiển thị đi xuyên tường;
khi mất dữ liệu vẫn cần giới hạn ngoại suy/thời gian giữ endpoint.
So sánh bật/tắt cơ chế trên cùng trace delay/jitter, giữ nguyên authority server.

## 16.3. Mở rộng và củng cố recovery đã triển khai

Project đã có claim token/ownership, grace ticket, chuyển writer/socket, timeout ACK/full,
input/full gate và controller/counter giữ qua reconnect. Các ca race, expiry, full→delta và gameplay offline
đã được kiểm tra ở mục 12.8; hướng phát triển không còn là bật GUI hoặc bắt đầu thêm RECONNECT.
Những việc tiếp theo cần giữ các invariant này và mở rộng bằng chứng ở đúng phần còn thiếu.

Trước hết, nhóm cần xác nhận mức chấp nhận của policy hiện tại: offline vẫn chịu damage và hết grace có thể ABORT cả trận.
Nếu muốn chuyển sang forfeit, miễn damage hoặc một cách giữ ghế khác, phải đặc tả lại result/lifecycle
và kiểm tra hai client offline, GAME_OVER trong grace, queue đầy và replay lượt mới; không đổi luật chỉ trong báo cáo.
Nếu thêm trả kết quả đã chốt khi người vắng mặt trở lại, cần contract riêng cho identity/retention/ACK/dedupe,
không tái tạo runtime hoặc gửi một full RUNNING để giả tiếp tục trận đã kết thúc.

Về quyền tiếp quản, đánh giá token secrecy, TLS, rotation/revocation và quan hệ với tài khoản nếu sau này có đăng nhập.
Không rotation chỉ vì một request đến trước đã gửi ACK nếu việc đó khiến owner hợp lệ mất khả năng retry;
handoff lỗi giữa chừng và cửa sổ chuyển token cần được thiết kế/test như một giao dịch nhiều bước.
Các đề xuất bảo mật này chưa được triển khai và không biến hệ thống hiện tại thành mô hình đã đạt chứng nhận security.

Về thời gian, ghi các mốc detect/attempt/ACK/metadata/full-applied/input-ready trên cùng process hoặc correlation có định nghĩa.
Thử DNS chậm, server không trả ACK/full, EDT chậm, jitter và nhiều reconnect đồng thời để đo cả timeout/failure,
không chỉ percentile của những lần thành công. Kiểm tra thêm cách so deadline quanh wrap-around;
không dùng độ chính xác nanosecond của fixture clock làm bằng chứng độ chính xác scheduler OS.

**Bảng 16.2. Recovery đã có và các phần cần mở rộng kiểm chứng.**

| Nhóm | Hiện trạng đã có bằng chứng | Việc tiếp theo và tiêu chí đề xuất |
|---|---|---|
| Quyền/đồng thời | Token sai và claim chồng bị từ chối; owner hợp lệ resume được | TLS/rotation/revocation và token bị lộ theo threat model; không làm hỏng retry hoặc chiếm phiên trái policy |
| Ownership/generation | Socket/writer/timer/heartbeat cũ không phá lần nối mới trong test | Reconnect burst nhiều room và soak; theo dõi owner/thread/timer để tìm interleaving ngoài fixture |
| Deadline | Biên manager 15 s, expiry TCP thật; budget ACK/full ở client | DNS/EDT/jitter, timestamp từng pha, thử wrap-around; chỉ công bố SLA khi có tiêu chí và dữ liệu phù hợp |
| Input/counter | Bỏ pending cũ, giữ sequence/plant counter, khoá input tới full | Nghiệm thu phím/Space trên GUI/mạng thật; phân biệt lệnh đã tới trước ngắt với input bị bỏ, không hứa replay mọi lệnh |
| World/gameplay | Full bằng peer cùng tick rồi delta; bom/damage/item/respawn/timer offline | Thêm tổ hợp map/shield/chain/lửa và policy mới nếu chọn; full không áp effect lặp |
| Kết quả/cleanup | Match kết thúc không tái tạo; rollback/tài nguyên đạt assertion | Contract replay kết quả nếu làm; lỗi giữa các bước và quá tải kéo dài phải giữ cleanup/không ghost owner |

Căn cứ hiện trạng: [thiết kế xác minh](../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md)
và [kết quả thực chạy](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md).
Cột “việc tiếp theo” là đề xuất chưa được nghiệm thu hoặc chưa triển khai; không nhận lại toàn bộ ma trận đã đạt như công việc tương lai.

## 16.4. Đánh giá nhiều máy, tải lớn hơn và vận hành dài hạn

Mở rộng theo thứ tự loopback nhiều JVM → LAN nhiều máy → môi trường có delay/jitter có kiểm soát.
Mỗi topology cần metadata phần cứng, nguồn điện, kết nối, server/client version và công cụ tạo tải;
không trộn nhiều process cùng máy vào số liệu LAN hoặc trừ timestamp hai máy để suy one-way delay khi chưa kiểm soát clock.
Giữ baseline full/delta và metric definition cố định nếu mục tiêu là so sánh tác động mạng của compression.
Với recovery, thiết kế thêm workload ngắt/kết nối lại có lịch rõ, không gộp RTT bình thường với thời gian chờ resume.
Nếu đối chứng bật/tắt recovery, phải tính cả match bị ABORT và các attempt không thành công,
chọn metric thể hiện quyền tiếp tục trận thay vì chỉ đo độ trễ của những phiên sống sót.

Tăng tải bằng nhiều room với roster hợp lệ trước khi thay cap bốn người của một match.
Theo dõi tick overrun, queue depth/rejection, writer backlog, CPU/RAM/GC,
RTT/ACK cả mẫu hoàn tất lẫn request timeout/pending, error và cleanup sau đợt chạy.
Điểm bão hòa cần được xác định bằng tiêu chí rõ ràng, không suy từ giới hạn queue hoặc số thread cấu hình.

Soak phải lưu duration, số vòng, xu hướng tài nguyên và sự kiện lỗi theo thời gian;
test đóng/mở nhanh không thay phép đo này.
Đợt đánh giá cũng nên làm nóng workload thực, đổi thứ tự chạy có kiểm soát và tăng số run khi biến thiên yêu cầu.
Mọi sửa lỗi hoặc thay property tạo một batch mới có revision/artifact hash riêng,
giữ nguyên attempt cũ để so sánh và không chỉ chọn các lượt đạt.
