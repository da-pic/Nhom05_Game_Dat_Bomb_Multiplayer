# 15. Hạn chế — Limitations

> **Phân công: TV1 xác nhận session/room và chính sách disconnect; TV2 xác nhận đồng bộ/movement/client; TV3 xác nhận gameplay; TV4 tổng hợp phạm vi bằng chứng và công cụ đo.**

Các kết quả ở mục 12 cho thấy implementation đạt các kiểm tra đã thực hiện,
nhưng chưa bao phủ toàn bộ điều kiện sử dụng của một game multiplayer.
Chương này phân biệt chức năng chưa cung cấp, cơ chế còn giới hạn và phần chưa được đo/nghiệm thu.
Một nhóm chưa có bằng chứng không tự động được coi là lỗi chức năng; ngược lại, test PASS cũng không thay cho bằng chứng còn thiếu.

## 15.1. Hạn chế chức năng và reconnect

### 15.1.1. Recovery chỉ trong phiên/trận còn được giữ

Đường lobby hiện đã có recovery end-to-end và GUI bật auto reconnect; RECONNECT được ClientHandler nhận trước router.
Khả năng này có điều kiện: cùng tiến trình server còn giữ session/runtime, token/claim hợp lệ,
admission chưa hết grace và match còn active. Nó không cung cấp persistence hoặc failover sau server restart,
không lưu token bền để app mới khởi động tự tiếp tục phiên cũ.

Freeze chỉ dừng input/movement, nên người offline vẫn chịu damage/respawn/elimination và timer trận vẫn trôi.
Hết grace có thể ABORT cả match; queue không nhận freeze/unfreeze cũng không được giả vờ tiếp tục.
TIMEOUT/LAST_ALIVE trong grace khiến resume bị từ chối, không tạo lại world đã kết thúc.
Đây là giới hạn chính sách đã kiểm tra, không phải tuyên bố mọi mất kết nối đều được cứu hoặc người vắng mặt được bảo vệ.
Nguồn: [LobbyGameServer](../../src/main/java/com/bombit/server/app/LobbyGameServer.java),
[thiết kế đã xác minh](../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md) và kết quả mục 12.8.

### 15.1.2. Phản hồi gameplay và phạm vi client

PlantBombCommand được xử lý authoritative, nhưng callback BombCommandResult ở factory lobby hiện để rỗng.
Client thấy kết quả thành công qua entity/notice; chưa có response nghiệp vụ riêng gắn request placement
để phân biệt đầy đủ các lý do từ chối gameplay như hết quota hoặc ô đã có bom.
Không nhầm điều này với các ERROR ở gate schema/quyền/queue: chúng thuộc các lớp xử lý khác.
Metric plant_ack_ms vì vậy là thời gian quan sát bom trên replica, không phải ACK placement riêng.

Prediction hiện chỉ dành cho movement. Local correction chưa có lớp visual smoothing riêng;
renderer sử dụng vị trí sau reconcile, còn remote dùng lịch sử nội suy có giới hạn.
Đây là mức hiện thực hiện tại, chưa đủ để khẳng định chuyển động luôn mượt khi mạng biến động.
Khoảng cách debug trước reconcile cũng chưa phải residual sau replay hoặc sai số người dùng nhìn thấy.
Nguồn: [ReconciliationController](../../src/main/java/com/bombit/client/game/movement/ReconciliationController.java)
và phần triển khai client ở mục 10.5/10.7.

### 15.1.3. Giới hạn thiết kế đồng bộ và xử lý quá tải

**Bảng 15.1. Các giới hạn cơ chế hiện hành.**

| Mã | Cơ chế/giới hạn | Hệ quả trong phạm vi project | Bằng chứng/căn cứ |
|---|---|---|---|
| L01 | Recovery hữu hạn, chỉ khi session/runtime/match còn hợp lệ; freeze không miễn damage; expiry có thể ABORT | Không khôi phục sau restart hoặc cứu mọi trường hợp disconnect; peer còn lại không luôn tiếp tục trận | Lobby/SessionManager và 12.8 token/grace/gameplay/GAME_OVER |
| L02 | Chưa có response placement nghiệp vụ riêng | Client chưa nhận đủ lý do kết quả luật bom qua một reply theo request | Callback lobby rỗng, nguồn metric plant observation |
| L03 | Diff theo tile/record, quét/chụp state; chưa tự chọn full/delta theo byte | Player ACK đổi có thể buộc gửi record; delta không được bảo đảm nhỏ nhất | StateDeltaBuilder và D1 movement |
| L04 | Baseline commit sau enqueue nội bộ, không có receipt ACK snapshot theo từng client | Cần giữ thứ tự/chuỗi update và full-resync; enqueue chưa chứng minh remote đã áp dụng | GameLoop/replica và contract mục 9 |
| L05 | FIFO có thể dừng khi đầu queue là mẫu tiếp theo cùng player; queue/deadline hữu hạn | Có khả năng chờ; lỗi transport có thể recovery nhưng lifecycle queue đầy/hard drop/expiry có thể hủy lượt | Code loop, writer/client/recovery fault tests |
| L06 | Chưa đo/smoothing correction local; lịch sử nội suy remote hữu hạn | Có thể giữ endpoint hoặc hiệu chỉnh rõ khi dữ liệu thiếu/nhảy | Client controller code; chưa có phép đo UX |

Các giới hạn L03–L05 là đánh đổi của thiết kế đã chọn, không được dùng để suy một bottleneck CPU hoặc tỷ lệ lỗi chưa đo.
Một game thread mỗi room giúp tách state nhưng các room vẫn chia sẻ tài nguyên process/server;
chưa có cơ sở tuyên bố scale tuyến tính theo số phòng.
Các invariant được bảo vệ trong test không đồng nghĩa delivery exactly-once hoặc phục hồi trong suốt cho mọi lỗi.

## 15.2. GUI/LAN/tải/soak chưa nghiệm thu

**Bảng 15.2. Khoảng trống nghiệm thu và khả năng khái quát kết quả.**

| Mã | Phần chưa hoàn tất | Bằng chứng hiện có | Kết luận chưa được phép rút ra |
|---|---|---|---|
| L07 | GUI có người thao tác hai/bốn người, focus/HUD và phục hồi | Test controller/component, Swing EDT/input gate, renderer BufferedImage và auto TCP client | Chưa nghiệm thu trực tiếp cửa sổ/overlay/nút hoặc trải nghiệm hồi phục thực tế |
| L08 | LAN/Internet, Wi-Fi/rút cáp vật lý, jitter/loss có kiểm soát | TCP loopback; smoke ba process; recovery đóng transport trong fixture | Chưa có reliability/latency/bandwidth recovery trên mạng thật; đóng socket không thay mọi kiểu mất mạng |
| L09 | Nhiều room đồng thời, tải vượt bốn client và soak dài hạn | Workload 1/2/4 client, fixture room isolation và vòng lifecycle | Chưa biết tải tối đa, điểm bão hòa hoặc xu hướng tài nguyên theo giờ |
| L10 | Profiling, phần cứng đầy đủ và độ trễ nội bộ | Raw CSV có OS/JDK/16 processor logic; queue/thread assertions | Chưa xác minh CPU model/RAM; chưa phân rã queue/tick/encode/GC hoặc chứng minh không có leak |

45 scenario-run mạng có cửa sổ yêu cầu 10 giây, warm-up 2 giây.
Năm run mỗi cấu hình giúp quan sát độ lặp ở điều kiện đó nhưng không thay một đợt vận hành dài hạn.
Ba lượt reliability có 84 lần thực thi test; 20 lượt trận/10 chu kỳ server trong fixture vẫn là kiểm tra hữu hạn.
Không có profiler hoặc theo dõi heap kéo dài để suy từ thread cleanup thành bộ nhớ luôn ổn định.

Nhóm đo mạng dùng server/client chung JVM, có chung CPU/GC và thứ tự mode cố định.
Warm-up chủ yếu poll/PING; các đường MOVE/bom chưa được làm nóng đầy đủ trước cửa sổ riêng.
Vì vậy các khác biệt nhỏ giữa hai/bốn client có thể chịu ảnh hưởng scheduling hoặc điều kiện chạy,
không đủ để xác lập quan hệ nhân quả hoặc kết luận hệ thống phục vụ nhiều client nhanh hơn.

## 15.3. Giới hạn số liệu lịch sử, fixture và công cụ đo

### 15.3.1. Giới hạn đối chứng full/delta

D0 là fixture v2 một player, map trống, 200 tick; D1 dùng v5/envelope, arena và 2/4 player, 600 tick.
Chỉ so full với delta trong cùng trace, không so chéo hai bộ như cùng workload.
D1 dựng trực tiếp sự kiện bom/block/item, không chạy toàn luật gameplay hoặc mô phỏng pickup hợp lệ.
State equality D1 chuẩn hóa ordering và bỏ tick/serverTimeMillis của BombFrame, không kiểm tra notice.

Idle không phát MOVE, khác GUI còn gửi mẫu đứng yên có sequence/ACK mới.
Trace sự kiện có nhiều tick ít thay đổi sau sự kiện cuối. Hai điều kiện này làm lợi ích bỏ tick rỗng nổi bật.
Chưa có ablation tách riêng diff với skip, trace tự nhiên của nhiều người, thay đổi map dày đặc hoặc resync lặp.
Năm lần size xác định bằng nhau không tạo bằng chứng phân bố latency/bandwidth mạng.
Nguồn: [thực nghiệm codec](../evidence/task13-2026-10-26/README.md) và thảo luận mục 13.2.

### 15.3.2. Ranh giới metric mạng

Byte được đếm ở frame ứng dụng, không gồm TCP/IP, retransmission hoặc traffic tầng dưới.
Số packet trong CSV là message ứng dụng, không phải TCP segment.
Mean RTT/ACK được tính trên mẫu hoàn tất; tổng 14 MOVE pending ở cuối cửa sổ chưa có completion quan sát được.
Không dùng số pending hoặc zero FAIL để suy packet-loss rate.
P95 tổng hợp theo run là worst-peer p95, không phải pooled p95 vì raw latency sample chưa được xuất.
Plant observation chỉ có một yêu cầu/client/run, chưa đủ mô tả phân bố placement dưới tải dày.

Benchmark mạng không có nhánh TCP full-every-tick đối chứng;
do đó chưa chứng minh giảm byte ở harness dẫn tới giảm RTT/ACK hay CPU trong hệ thống.
Các phạm vi này được giữ riêng trong [kết quả mạng](../evidence/task14-2026-10-26/README.md).

### 15.3.3. Revision, lỗi lịch sử và tính tái lập

CSV lịch sử ở revision khác được giữ riêng với lần đo mới.
Suite khảo sát nhiệm vụ 1 có một smoke failure và retry riêng cũng fail;
suite nhiệm vụ 12 cùng ba lượt reliability mới đều pass smoke với source không đổi.
Chưa xác minh nguyên nhân lỗi cũ nên không gọi kết quả mới là bằng chứng một bản sửa đã giải quyết flakiness.
Đợt recovery ngày 27/10 có hai full và một smoke sandbox bị lỗi cùng ca process smoke,
còn smoke riêng/full ngoài sandbox đạt với cùng source và timeout. Không kết luận chính xác policy sandbox
hoặc lỗi firewall/production gây ra khác biệt; giữ toàn bộ attempt thay vì chỉ chọn lượt 171/171.

Lỗi repository, execution policy và truyền JAVA_HOME trong bước chuẩn bị được lưu riêng,
không tính thành failure của test chưa chạy hoặc âm thầm bỏ khỏi hồ sơ.
Manifest/hash hỗ trợ xác định source/artifact, nhưng bản sao file/log vẫn cần được giữ khi đóng gói để người khác kiểm tra.
Phạm vi bằng chứng hiện tại được công bố ở mục 12.7–12.8; các giới hạn trên là căn cứ cho hướng phát triển mục 16.

## 15.4. Giới hạn riêng của phục hồi phiên và bằng chứng mới

**Bảng 15.3. Các giới hạn bổ sung cho Session Recovery.**

| Mã | Giới hạn | Hệ quả | Căn cứ và phần cần kiểm chứng thêm |
|---|---|---|---|
| L11 | Token chưa rotation, kênh chưa TLS, không có xác thực tài khoản | Token sai bị từ chối không đồng nghĩa chống lộ/đánh cắp token; người có token hợp lệ có thể takeover theo policy | SessionManager/codec/transport; cần mô hình đe doạ và test security nếu mở rộng |
| L12 | Chưa đo latency/overhead recovery hoặc tải reconnect đồng thời | Không công bố SLA, percentile, tỷ lệ thành công ngoài thực tế hoặc lợi ích hiệu năng A/B | 12.8 chỉ kiểm tra correctness; DNS/scheduler/EDT/queue còn cần mốc đo riêng |
| L13 | Phục hồi world hiện tại, bỏ pending input cũ và không replay lịch sử GAME_OVER/notices | Không bảo đảm mọi lệnh/thông báo đã tới hoặc sẽ phát lại; không có exactly-once tổng quát | Client owner/replica và các test gate/counter; replay kết quả/event là hướng riêng chưa làm |

Budget tổng 14 s của client và grace 15 s của server có điểm bắt đầu khác nhau.
Watchdog chạy theo lịch, connect timeout không tự bao trọn DNS và các so sánh absolute nanoTime deadline phía client
chưa có test wrap-around; không diễn giải chúng thành deadline hard real-time trên mọi môi trường.
Test biên nanosecond dùng clock được tiêm, không chứng minh scheduler OS có độ chính xác nanosecond.

Full sau reconnect có thể phát tới cả roster vì baseline dùng chung. Phép đo D1 trước đây không chứa workload
reconnect này, nên chưa biết byte/CPU tăng bao nhiêu hoặc client chờ bao lâu khi nhiều phiên cùng hồi phục.
Sáu lớp recovery chuyên biệt có 31 execution trong suite 171, không phải 171 lỗi mạng độc lập đã kiểm chứng.
Một trường hợp expiry ghi 15001 ms là chờ kết thúc grace theo fixture, không phải recovery latency.

Các hạn chế trên không phủ nhận assertion đã đạt về giữ phiên/full→delta/cleanup;
chúng giới hạn mức khái quát từ kiểm thử cục bộ tới sử dụng thực tế.
Nguồn: [setup và kết quả mới](../session-recovery/03_KET_QUA_KIEM_THU_THUC_TE.md).
