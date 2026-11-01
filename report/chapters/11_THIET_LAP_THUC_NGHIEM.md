# 11. Thiết lập thực nghiệm — Experimental Setup

> **Phân công: TV4 chủ trì thiết kế, lưu bằng chứng và tổng hợp; TV1 phụ trách transport/session/room và lỗi kết nối; TV2 phụ trách runtime/movement, replica và full/delta; TV3 phụ trách bom/item/damage/result. Cả nhóm xác nhận cấu hình và giới hạn của từng lần chạy.**

Theo [Instruction, mục 8.11 và mục 9](../../phancong/Instruction.md), thực nghiệm cần mô tả phần cứng,
OS, ngôn ngữ/thư viện, cấu hình mạng, dữ liệu và kịch bản; kết quả phải có số liệu thực tế.
Thiết kế này đánh giá bốn câu hỏi: hệ thống thực hiện đúng contract gameplay hay không;
State Delta Compression giảm bao nhiêu byte trên cùng chuỗi trạng thái;
latency, ACK và lượng message thay đổi thế nào với workload và số client;
Session Recovery có giữ đúng phiên/trận, thiết lập lại baseline và xử lý lỗi/lifecycle theo contract không.
Các mục 11.1–11.6 giữ thiết kế và phạm vi benchmark ở baseline cũ; trạng thái đã chạy được ghi riêng theo nhóm.
Mục 11.7 bổ sung thiết lập recovery của phiên bản tích hợp mới. Không đổi nhãn CSV cũ thành số đo recovery.
Kết quả D0/D1, T1 và ba lượt reliability nằm tại [mục 12.4–12.6](12_KET_QUA.md);
kết quả recovery và các attempt ngày 27/10/2026 nằm tại mục 12.8.
Benchmark nhiều JVM/LAN có điều kiện vẫn không được tính là đã đo chỉ vì có process smoke hoặc test TCP cục bộ.

## 11.1. Revision, phần cứng, OS/JDK và cấu hình

### 11.1.1. Môi trường đã được ghi nhận

**Bảng 11.1. Môi trường khảo sát đã có bằng chứng và thông tin cần bổ sung.**

| Thuộc tính | Thông tin đã xác minh | Phạm vi sử dụng |
|---|---|---|
| Revision baseline | `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` | Nguồn của các phép đo D0/D1/network/reliability cũ; recovery dùng mốc riêng tại 11.7 |
| Hệ điều hành | Windows 11, build 10.0.22631, AMD64 | Máy khảo sát nhiệm vụ 1 |
| Bộ xử lý logic | 16 theo manifest khảo sát | Không suy thành 16 lõi vật lý hoặc 16 người chơi đạt tải |
| Tên CPU, lõi vật lý, RAM | Chưa có dữ liệu được xác minh trong hồ sơ | Phải bổ sung cho từng máy trước khi công bố kết quả hiệu năng |
| Runtime/compiler | Java/Javac 25.0.1; HotSpot 64-Bit | Phiên bản ghi trong manifest nhiệm vụ 1 |
| Maven | 3.9.12; dependency lấy từ local cache ở lần khảo sát | Đường cài Maven là cấu hình máy, không hard-code cho mọi thành viên |
| Build/test | Release 25, compiler plugin 3.13.0, Surefire 3.5.2, JUnit Jupiter 5.11.4 | Theo POM; JUnit là test dependency |
| Giao diện/giao tiếp | Swing/AWT, Java 2D, TCP socket | Runner headless không đánh giá trải nghiệm GUI |

Căn cứ: [manifest khảo sát](../evidence/task01-2026-10-26/manifest.json),
[hồ sơ môi trường/lệnh](../evidence/task01-2026-10-26/README.md) và [pom.xml](../../pom.xml).
Mục 11 không chạy lại suite hoặc benchmark. Truy vấn phần cứng ở lượt biên soạn này không lấy được CPU/RAM;
không dùng suy đoán để lấp khoảng trống. Khi chạy chính thức, bổ sung tên CPU, RAM vật lý, OS/JDK,
nguồn điện và topology thực tế cho server lẫn client. Không dùng thông số máy hiện tại để gán ngược cho CSV lịch sử.

### 11.1.2. Khóa cấu hình và artifact

Mỗi đợt đo ghi `git rev-parse HEAD`, `git status --short`, hash source/config liên quan,
hash JAR hoặc class inventory thực sự chạy, `java -version`, `javac -version`, `mvn -version` và toàn bộ lệnh.
Nếu có sửa source chưa commit, ghi dirty cùng diff hoặc bản sao source; chỉ ghi revision là chưa đủ để tái lập.
Giữ mặc định JVM trừ khi có lý do cụ thể; mọi heap/GC/system property override phải nằm trong manifest.
Hạn chế ứng dụng nền, dùng cùng chế độ nguồn điện và ghi các sự cố tải nền quan sát được.
Không cần cài framework/game engine hoặc database mới để thực hiện các phép đo này.

[classpath.cmd](../../scripts/classpath.cmd) ưu tiên JAR ở root rồi JAR trong target trước `target/demo-classes`.
Vì vậy build source mới xong chưa đủ để kết luận wrapper benchmark đang dùng class mới.
Đợt đo từ source ưu tiên chạy trực tiếp classpath `target/demo-classes` sau build thành công;
đợt đo bản phát hành dùng đúng JAR đã hash. Không trộn hai loại artifact trong một nhóm so sánh.
Không cần xóa artifact cũ để lựa chọn classpath đúng.

## 11.2. Môi trường loopback, nhiều process và LAN nếu có

**Bảng 11.2. Topology và kết luận được phép rút ra.**

| Mã | Bố trí | Cách dùng | Giới hạn |
|---|---|---|---|
| T0 | State/codec trong một process, không socket | So sánh byte và tính đúng full/delta | Không đo TCP latency hoặc băng thông đường truyền |
| T1 | `--local`, một JVM chứa server và các client, TCP qua 127.0.0.1 | Nhóm benchmark chính có thể tái lập bằng runner hiện tại | Chia sẻ CPU/GC; không đại diện mạng LAN |
| T2 | Server JVM riêng, runner JVM riêng trên cùng máy | Kiểm tra ảnh hưởng phân process và process smoke | Vẫn dùng tài nguyên máy chung, vẫn là loopback |
| T3 | Server và client/runner ở nhiều máy qua LAN | Nhóm bổ sung khi có máy và biên bản thực tế | Phải ghi loại mạng, IP/port, Wi-Fi/Ethernet và bố trí máy |

T1 dùng ephemeral port khi runner tự tạo server. Benchmark T2/T3 thủ công dùng port được ghi trong manifest;
ví dụ lệnh bên dưới dùng 8888. Runner dùng TCP thật và luồng lobby/match hiện tại,
không thay world qua một đường debug để tạo số liệu mạng.
Process smoke và fixture recovery có thể dùng port 0 rồi đọc cổng được cấp; không gán port 8888 cho các lượt đó.
Không bật giả lập delay/loss trong nhóm chính. Nếu làm nhóm bổ sung có impairment,
ghi công cụ, cấu hình và tách label; runner chưa có tùy chọn tự tạo packet loss/delay.

Mỗi file CSV chỉ có một process ghi. Với distributed runner, host giữ room và công bố ROOM_ID,
guest dùng `--clients 1 --expected-clients N --room-id UUID`; mỗi máy lưu CSV riêng.
Chỉ gom những file có cùng run ID/roster/topology sau khi đối chiếu log.
Runner phân tán bắt đầu cửa sổ đo riêng từng process, không có barrier thời gian chung toàn máy;
không coi tổng các hàng đó là một cửa sổ server throughput được đồng bộ tuyệt đối.
Timestamp UTC giúp ghép hồ sơ, còn duration trong một process dùng nanoTime, không trừ timestamp hai máy để suy one-way delay.

## 11.3. Map, luật game, input workload và seed

### 11.3.1. Dữ liệu đầu vào

Không có dataset huấn luyện hoặc dữ liệu người dùng ngoài hệ thống.
Dataset thực nghiệm là cấu hình map/luật, roster, chuỗi input/sự kiện có mô tả,
snapshot và output test/CSV/log được tạo trong từng lần chạy.
Map gameplay chuẩn lấy từ [DefaultArenaMap](../../src/main/java/com/bombit/server/game/map/DefaultArenaMap.java):
17 × 15 ô, tile 32 pixel, bốn spawn cố định. Lưu hash factory/map cùng source để phát hiện đổi layout.
Hitbox/tốc độ ban đầu lấy theo PlayerMovementRules; mọi property override phải được lưu.

### 11.3.2. Cấu hình của benchmark hiện có

[NetworkBenchmark](../../src/main/java/com/bombit/tools/NetworkBenchmark.java) ở chế độ local khởi tạo
BombRules(3000, 1, 1), MatchRules với dropChance=0,75, cap bom/range/speed lần lượt 5/8/144,
speedIncrement=8, initialLives=3 và maxLives=99. Thời lượng trận local là
`seconds + warmup + 30` giây, không phải mặc định 180 giây của server lobby thông thường.
Chạy remote phải cấu hình và ghi luật ở process server; không suy runner tự đổi luật server từ CLI.

**Bảng 11.3. Workload và nhịp phát của runner.**

| Mode | Số client/người hỗ trợ trong nhóm chính | Input trong cửa sổ đo | Mục đích |
|---|---|---|---|
| transport | 1, 2, 4 client; không tạo match | PING khoảng mỗi 200 ms | RTT và chi phí message của tầng kết nối |
| idle | 2, 4 người | Có PING, không phát MOVE/đặt bom | Lưu lượng nền và snapshot của trận đứng yên |
| movement | 2, 4 người | MOVE khoảng mỗi 50 ms, đổi hướng sau mỗi 20 bước gửi | ACK input và lưu lượng khi player di chuyển |
| bombs | 2, 4 người | Mỗi client đặt một bom đầu cửa sổ; movement theo đường thoát rồi dừng | Bom/lửa được mọi peer quan sát, thời gian thấy bom authoritative |

Nhịp trên là lịch gửi mục tiêu của runner; scheduling có thể khiến số mẫu thực khác phép tính lý tưởng.
Warm-up runner chủ yếu poll/PING, chưa làm nóng đầy đủ workload movement/bombs.
Khi phân tích phải nêu giới hạn này, không gọi đó là steady-state warm-up đầy đủ cho mọi module.
Mode bombs không phải stress đặt bom liên tục và thường chỉ có một plant observation mỗi client mỗi lần chạy.
Idle cũng không đồng nghĩa không có snapshot: timer trận, full định kỳ hoặc thay đổi frame có thể tạo update.

Đường local dùng Random không có seed CLI và không xuất trace input thô.
Giữ nguyên cách chạy hiện có khi báo cáo benchmark hệ thống, ghi seed là không điều khiển/không được lưu;
không khẳng định hai lần chạy có chuỗi drop giống nhau.
Các test gameplay cần đối chứng chính xác dùng policy/clock được inject theo fixture.
Phép so sánh codec ở 11.5 dùng **cùng chuỗi state** cho cả hai nhánh, không phụ thuộc hai trận ngẫu nhiên độc lập.

## 11.4. Kịch bản chức năng và lỗi

**Bảng 11.4. Ma trận kiểm chứng chức năng và fault handling.**

| Mã | Kịch bản/điều kiện | Điều kiện kiểm tra | Phụ trách và loại bằng chứng |
|---|---|---|---|
| F01 | CONNECT, room, host/ready/start, chat và leave | State transition/roster đúng; message không sang phòng khác | TV1; JUnit/TCP log |
| F02 | Hai runtime và nhiều producer submit | State tách room, FIFO enqueue, queue có giới hạn, không hỏng dữ liệu | TV2; RuntimeContractTest và log check |
| F03 | MOVE/STOP tại tường, block, biên và bom | Không đi xuyên; player chết không di chuyển; ACK không lùi | TV2; movement/collision test |
| F04 | Full/delta, thêm/xóa player/entity, bỏ một update ở replica | Snapshot không bị sửa; baseline lệch được phát hiện; full phục hồi world | TV2/TV4; codec/replica assertions |
| F05 | Prediction/replay, interpolation và respawn | Bỏ input đã ACK, không replay input trước respawn hoặc kéo nhân vật qua map | TV2; controller test; GUI bổ sung |
| F06 | Placement lỗi, fuse, chain và block chung batch | Đúng quota/ô, bom không nổ hai lần, tia không xuyên block vừa phá trong batch | TV3; BombSystem/BombRuntimeIntegration test |
| F07 | Damage/lives/shield/item/result | Một damage/player/batch, pickup không lặp, cap và ranking/reason đúng | TV3; MatchGameplay/ExtendedItems test |
| F08 | Frame sai/cắt dở, timeout, client chậm và disconnect | Bị từ chối/cleanup theo contract; không treo vô hạn hoặc làm hỏng phòng khác | TV1/TV4; transport/writer/lifecycle test |
| F09 | Start/stop lặp và kết thúc trận | Runtime/reader/writer/worker được giải phóng theo timeout test | TV2/TV4; thread/cleanup assertion |
| F10 | GUI hai/bốn người, mất focus, bom/item/HUD và trở lại phòng | Input/render theo snapshot, kết quả khớp server | Cả nhóm; biên bản người kiểm tra, ảnh/video và log cùng run |
| F11 | Phục hồi phiên active match trong grace và full→delta | Đúng token/context, giữ runtime/controller, input chỉ mở sau full, cleanup/từ chối đúng policy | TV1/TV2/TV3/TV4; nhóm recovery riêng ở 11.7 |

Các mã F là nhóm kịch bản, không thay số lượng JUnit test. Tên test/API cụ thể đã được truy vết ở
[hồ sơ khảo sát](../01_HO_SO_KHAO_SAT.md) và chương 10.
Không lấy việc lớp test tồn tại làm kết quả pass.
Bỏ update ở fixture F04 là fault injection tại tầng replica, không phải bằng chứng TCP tự làm mất message.
Baseline cũ không có tiêu chí recovery end-to-end; bản tích hợp bổ sung F11 theo FR15/NFR07 ở mục 6.
Soft disconnect còn trong grace giữ match; leave/hard drop/expiry hoặc lỗi queue lifecycle vẫn có thể ABORT lượt.

Kế hoạch chạy full suite một lần và từng check/main riêng một lần để ghi nhận tổng quan.
Các nhóm concurrency/lifecycle/fault có tính thời gian được chạy thêm ba lần độc lập với log riêng;
báo cả ba kết quả, không chỉ chọn lần đạt. Nếu full suite dừng khiến các bước check/main phía sau không chạy,
chạy riêng để thu bằng chứng và giữ trạng thái full suite thất bại.
Lỗi process smoke lịch sử phải được giữ cùng các lượt xác minh mới; mốc recovery có cả attempt sandbox lỗi
và lượt ngoài sandbox đạt, không quy mọi failure này thành lỗi handshake recovery hoặc tự nhận đã sửa nguyên nhân.
Không tự tăng timeout, sửa test hoặc đổi source trong một đợt đo để làm kết quả đẹp hơn.

## 11.5. Đối chứng full mỗi tick so với delta + full định kỳ

### 11.5.1. Hai nhánh so sánh và phạm vi byte

Nhánh B0 gửi FULL_STATE ở mọi tick. Nhánh B1 dùng StateDeltaBuilder, full tại tick 1 và mỗi 100 tick,
delta khi có thay đổi, không phát packet khi builder trả null; full do resync được tính nếu kịch bản có resync.
Hai nhánh nhận cùng state ở cùng tick, cùng phiên bản codec và cùng nội dung gameplay.
Commit baseline B1 theo đúng điều kiện xuất bản của harness; không bỏ các full định kỳ khỏi tổng byte.
Kết quả này đo cả lợi ích chọn dữ liệu thay đổi và việc bỏ update rỗng, không gán toàn bộ mức giảm riêng cho tile diff.

Thước đo chính là tổng độ dài frame ứng dụng sau encode: 4 byte length + 2 byte type + payload UTF-8,
bao gồm binary snapshot đã Base64/JSON và match envelope nếu harness có dùng.
Không gọi số này là tổng byte trên dây TCP/IP: chưa gồm header mạng, ACK TCP, retransmission hoặc mã hóa tầng khác.
Nếu cần so sánh riêng binary payload, ghi thành cột bổ sung và giữ phạm vi đo hai nhánh giống nhau.

### 11.5.2. Fixture hiện có và mở rộng được thiết kế

**Bảng 11.5. Phép đo delta và mức sẵn sàng của công cụ.**

| Mã | Chuỗi đầu vào | Phạm vi đo | Trạng thái công cụ |
|---|---|---|---|
| D0 | 200 tick; map trống 17 × 15, một player; di chuyển tick 1–80, thêm bom tick 40, xóa tick 100, thêm item tick 120 | Snapshot v2 + PacketEncoder, không match envelope/BombFrame/MatchFrame | Có trong DeltaCompressionCheck |
| D1 | 600 tick, 2/4 player, arena; các trace idle, movement và bomb/block/item được lưu cố định | Snapshot v5 + match envelope giống đường gameplay | Harness báo cáo đã được hiện thực và đo ở [mục 12.5](12_KET_QUA.md); không thay runtime production |

[DeltaCompressionCheck](../../src/test/java/com/bombit/server/game/movement/DeltaCompressionCheck.java)
đồng thời kiểm tra codec, baseline, xóa entity/player và full phục hồi trước vòng đo D0.
Vòng đo D0 không phá block và không mô phỏng đầy đủ lives/shield/notice của trận hiện tại;
200 tick tương ứng 10 giây **thời gian mô phỏng**, không phải benchmark chạy đủ 10 giây đồng hồ.
Không suy trực tiếp mức tiết kiệm D0 thành mức tiết kiệm bandwidth v5 ở LAN.

D0 chạy năm lần bằng process mới để kiểm tra output byte có lặp lại;
đây là fixture xác định nên năm số bằng nhau không tạo bằng chứng biến thiên thống kê về mạng.
D1 chỉ được công bố khi đã có harness lưu trace và kiểm tra equality replica sau mỗi tick.
Trace cần ghi player input/ACK, map change, entity add/remove, BombFrame/MatchFrame và thời điểm sự kiện;
nhánh full/delta phải đọc cùng trace, dùng cùng match ID hoặc envelope cùng chiều dài.
Nếu sinh trace bằng RNG, lưu thuật toán, seed và trace thực tế. Không sửa bộ sinh state khác nhau cho hai nhánh.

Mỗi tick có dòng `tick,full_frame_bytes,delta_frame_bytes,kind,base_tick` ở harness D1;
D0 hiện chỉ xuất ba cột đầu và dòng PASS cuối, nên lưu stdout nguyên trạng như log rồi tách đúng các dòng số thành CSV.
Không đọc toàn stdout D0 như một file CSV thuần hoặc tự bịa kind/base_tick cho fixture hiện có.
Equality replica là điều kiện chấp nhận phép đo: giảm byte mà world cuối/từng tick sai thì không được nhận là cải tiến đạt.

## 11.6. Metric, đơn vị, công cụ, số lần lặp và cách tái lập

### 11.6.1. Định nghĩa metric và cửa sổ quan sát

**Bảng 11.6. Metric và cách diễn giải.**

| Metric | Định nghĩa/đơn vị | Công cụ hoặc bằng chứng | Giới hạn |
|---|---|---|---|
| Byte full/delta | `F = Σ full_frame_bytes`, `D = Σ delta_frame_bytes`, byte | D0/D1 sau PacketEncoder | Null update tính 0; giữ cả full định kỳ |
| Tỷ lệ giảm | `100 × (1 − D/F)` %, khi F > 0 | Tính từ tổng byte cùng trace | Không lấy trung bình tỷ lệ giảm từng packet |
| Snapshot rate | `(full_snapshots + delta_snapshots) / T`, message/s | CSV runner, T là window_seconds thực đo | Snapshot nhận/được poll, không bảo đảm mọi snapshot đã APPLIED |
| Message rate | `tx_packets/T`, `rx_packets/T`, message/s | CSV theo peer | Message ứng dụng, không phải số TCP segment |
| Throughput ứng dụng | `tx_bytes/T`, `rx_bytes/T`, byte/s | CSV theo peer | Có framing/envelope, chưa tính TCP/IP |
| Ping RTT | Thời gian startPing đến xử lý PONG trên cùng client, ms | LatencyMonitor, mean/min/p95/max và sample count | Bao gồm poll/scheduling, không chia đôi để tuyên bố one-way latency |
| Input ACK delay | Từ ghi timestamp gửi MOVE đến poll snapshot APPLIED có ACK ≥ sequence, ms | move_ack_samples/mean/p95 | Một snapshot có thể xác nhận nhiều input; không phải render latency |
| Plant observation | Từ yêu cầu đặt bom đến replica thấy bom của local session, ms | plant_ack_ms | Không có ACK placement packet riêng; ít mẫu ở mode bombs |
| Pending cuối cửa sổ | pending_ping_end, pending_move_end, số request | CSV runner | Chưa hoàn tất ở mốc kết thúc, không tự kết luận packet loss |
| Stale/resync | Số snapshot cũ/yêu cầu full trong cửa sổ | stale_snapshots, resync_requests | Phân tích nguyên nhân, không thay bằng tỷ lệ loss mạng |
| Tính đúng | Pass/fail assertion, equality replica và đúng result | Log test/harness | Không suy từ throughput cao |
| Cleanup/error | status, error, cleanup_ok và exit code | CSV/log/thread assertion | Local kiểm tra server; remote runner không tự chứng minh server đã dừng sạch |

T trong các tỷ suất là thời gian đo thực tế bằng nanoTime, không lấy cố định `--seconds` nếu process bị trễ.
Byte runner đếm ở send/poll ứng dụng, không phải timestamp capture NIC.
Mẫu nằm sát cuối cửa sổ có thể còn pending; giữ số pending để tránh chỉ báo latency của các request hoàn tất nhanh.
Nếu một peer không có RTT/ACK sample, ghi thiếu dữ liệu hoặc FAIL theo runner, không thay bằng 0 ms.
P95 trong LatencyMonitor dùng nearest-rank: sắp n mẫu và chọn vị trí `ceil(0,95n)`, đánh số từ 1.

Không cộng cả TX phía client với RX phía server để báo lượng traffic duy nhất của cùng message.
Trong nhóm này tổng TX hoặc tổng RX của client là metric tổng hợp riêng có tên rõ ràng.
Trung bình mean giữa peer chỉ hợp lệ khi ghi đó là mean theo peer;
muốn pooled mean cần trọng số số mẫu, còn pooled p95 cần raw sample.
CSV hiện chỉ có thống kê tổng hợp, nên không tái dựng pooled p95 bằng cách lấy trung bình các p95.
Chỉ số correction local, frame time/FPS, CPU/RAM và queue rejection không tự có trong CSV runner hiện tại;
nếu đo bổ sung cần instrumentation/log riêng và tách khỏi các cột sẵn có.

### 11.6.2. Số lần chạy và quy tắc tổng hợp

**Bảng 11.7. Thiết kế số lần chạy và trạng thái theo từng mốc bằng chứng.**

| Nhóm | Cấu hình | Thiết kế số lặp | Cửa sổ/chú ý và trạng thái |
|---|---|---:|---|
| TCP T1 | 9 ô: transport 1/2/4; idle/movement/bombs 2/4 | 5/ô | Warm-up 2 s; đo 10 s; đã có 45 scenario-run ở baseline cũ |
| TCP T2 | Cùng 9 ô với server process riêng | 5/ô nếu đo | Chưa thực hiện benchmark này; process smoke không thay thế |
| LAN T3 | Ưu tiên movement/bombs 2/4 | 5/ô thực sự đo | Chưa thực hiện; cần bố trí máy/mạng và log tương ứng |
| D0 | Fixture 200 tick | 5 | Đã có năm lượt xác định ở mốc delta cũ; không phải năm mẫu latency |
| D1 | 2/4 player × idle/movement/bomb-block-item | 5/trace | Đã có 30 lượt ở mốc delta cũ, 600 tick/trace, full mỗi 100 tick |
| F01–F09 | Suite/check và concurrency/fault/lifecycle baseline | 1 tổng; 3 lần nhóm nhạy thời gian | Đã có suite 133 và 84 execution reliability theo revision cũ |
| F10 | GUI hai/bốn người | 3 lượt/kịch bản nếu nghiệm thu | Chưa có biên bản người thao tác; không nhận là đã chạy |
| F11 / recovery | Suite và nhóm recovery trên working tree đã sửa | Một lượt full cuối; giữ tất cả attempt chẩn đoán | Đã chạy tại nhiệm vụ recovery 3; không thiết kế thành năm benchmark latency, xem 11.7/12.8 |

T1 chính có 45 scenario-run; vì CSV có một hàng cho mỗi client, năm vòng suite đầy đủ dự kiến 125 hàng,
không phải 125 lần chạy độc lập. Một suite gồm 9 scenario tuần tự, mỗi scenario local tạo server/client mới;
chúng không phải 9 scenario chạy song song. Thứ tự suite cố định là một hạn chế cần ghi nhận.
T2/T3 và F10 là nhóm còn có điều kiện; D1 đã được đo trong đợt delta ở baseline riêng.
Không tính số dự kiến vào Results và không chuyển số lặp của nhóm cũ sang số lặp recovery.
Năm lần lặp là lựa chọn thiết kế của nhóm để quan sát độ ổn định, không phải con số bắt buộc do giảng viên đưa ra.

Cho mỗi ô, báo số attempt, số thành công/thất bại và cleanup trước khi tổng hợp latency/byte.
Với dữ liệu hiệu năng hợp lệ, báo median và min–max của metric theo lần chạy, kèm từng hàng gốc.
Có thể tính một chỉ số tổng hợp peer trong từng run trước khi lấy median qua năm run, nhưng phải nêu công thức.
Không coi các ping, peer hoặc tick cùng run là các lần lặp độc lập.
Giữ FAIL trong dữ liệu; lần chạy lại dùng attempt ID mới và không ghi đè.
Nếu thay code/cấu hình để sửa lỗi, tạo đợt đo mới, chạy lại hai nhánh đối chứng và ghi lý do thay đổi.

### 11.6.3. Lệnh tái lập và kiểm soát classpath

Các ví dụ sau dành cho PowerShell ở root repository, **chưa được thực thi trong nhiệm vụ viết này**.
Máy cần JDK 25 và Maven đã cài; JAVA_HOME/BOMBIT_MVN cấu hình theo máy.
[scripts/test.cmd](../../scripts/test.cmd) chạy Maven rồi Check TV2/NetworkTest main khi các bước trước đạt;
[scripts/check-tv2.cmd](../../scripts/check-tv2.cmd) có thể chạy riêng để biên dịch check và xuất D0.

```powershell
# Lưu output và exit code vào thư mục run trước khi phân tích.
cmd /c scripts\test.cmd
cmd /c scripts\check-tv2.cmd

# Build production từ source; chỉ đo sau khi build trả exit code 0.
cmd /c scripts\build-demo.cmd
```

Ví dụ một vòng suite T1, với classpath chỉ định rõ để không lấy nhầm JAR cũ:

```powershell
$experimentJava = if ($env:JAVA_HOME) {
    Join-Path $env:JAVA_HOME 'bin/java.exe'
} else { 'java' }
$experimentRevision = git rev-parse HEAD
$experimentRun = 'T1-r01'  # Đổi r01..r05; lưu dirty/diff riêng trong manifest.
$experimentDir = Join-Path 'report/evidence/experiments' $experimentRun
New-Item -ItemType Directory -Force -Path $experimentDir | Out-Null
& $experimentJava -cp 'target/demo-classes' com.bombit.tools.NetworkBenchmark `
    --local --mode suite --seconds 10 --warmup 2 `
    --label 'single-jvm-loopback' --revision $experimentRevision --run-id $experimentRun `
    --csv (Join-Path $experimentDir 'runner.csv') *> (Join-Path $experimentDir 'runner.log')
$LASTEXITCODE | Set-Content (Join-Path $experimentDir 'exit-code.txt')
```

Tạo r02–r05 bằng các process Java mới và thư mục mới, giữ log nguyên trạng.
Không chạy lại với cùng thư mục/ID rồi để append tạo bộ dữ liệu không phân biệt attempt.
CLI runner hiện giới hạn seconds 1–300, warmup 0–30; bombs/suite cần ít nhất 4 giây đo,
gameplay cần 2/4 người. Thiết kế 10 giây nằm trong các giới hạn này.
[run-benchmark.cmd](../../scripts/run-benchmark.cmd) là wrapper tương đương nếu đã xác nhận đúng artifact/classpath.

D0 có thể lấy từ `target/delta-compression-results.csv` do check-tv2 tạo, nhưng phải sao lưu trước lần check tiếp theo.
Sau check compile thành công, chạy riêng fixture để lưu mỗi attempt:

```powershell
& $experimentJava -cp 'target/tv2-check' `
    com.bombit.server.game.movement.DeltaCompressionCheck `
    *> (Join-Path $experimentDir 'delta-raw.log')
$LASTEXITCODE | Set-Content (Join-Path $experimentDir 'delta-exit-code.txt')
```

D0 dùng thư mục/ID riêng thay cho T1-r01 trong ví dụ.
Để thực hiện T2, khởi chạy ServerApplication trong process riêng rồi bỏ `--local`,
truyền `--host 127.0.0.1 --port 8888 --clients N --mode MODE` cho runner.
T3 thay host bằng IP LAN và lưu log server/runner từng máy; nếu chia peer ra nhiều runner, dùng expected-clients/room-id như 11.2.
Đây là hướng dẫn bố trí, không xác nhận server remote/LAN đã được chạy.

### 11.6.4. Hồ sơ bằng chứng và điều kiện chấp nhận

Mỗi run lưu ngoài `target` để không mất khi clean. Cấu trúc đề xuất:

```text
report/evidence/experiments/<batch>/<run-id>/<machine-id>/
    manifest.json           revision, dirty, artifact/source hash, hardware, topology, rules
    commands.txt            cwd, lệnh đầy đủ, giờ bắt đầu/kết thúc
    runner.csv              một process sở hữu file
    runner.log              stdout/stderr nguyên trạng
    server.log              nếu server là process do máy này sở hữu
    exit-code.txt
    delta-raw.log           chỉ với nhóm D
    trace.csv               chỉ khi harness D1 đã xuất trace
    screenshots/            nếu nghiệm thu GUI
    checksums.sha256        hash các file evidence sau khi kết thúc
```

Tên `<batch>/<run-id>/<machine-id>` tránh trộn nguồn giữa máy và lần lặp;
ví dụ ngắn T1-r01 ở trên có thể đặt bên trong batch tương ứng khi tổ chức đợt đo.
Manifest ghi loại run, mode, số client thực tế, seed hoặc lý do không có seed, cấu hình luật,
thời lượng yêu cầu/thực đo, sample count, trạng thái và file gốc.
Raw CSV giữ nguyên; dữ liệu tổng hợp và script phân tích nằm thư mục khác, có hash và lệnh chạy riêng.
CSV theo [BenchmarkCsv](../../src/main/java/com/bombit/tools/BenchmarkCsv.java) là UTF-8, header cố định;
không ghép trực tiếp file khác header hoặc gộp hàng từ nhiều revision mà bỏ metadata.

Một run hiệu năng chỉ hợp lệ khi setup đúng roster/topology, có mẫu phù hợp, không mất baseline chưa phục hồi,
không có lỗi runtime/runner và cleanup đạt theo phạm vi công cụ kiểm tra.
Lần FAIL vẫn được lưu để phân tích reliability, không xóa khỏi mẫu attempt.
Remote runner chỉ xác minh cleanup client do nó sở hữu; server cần log/assertion riêng.
Đối chứng D cần thêm equality replica từng tick và cùng trace/codec/byte scope.
GUI cần người kiểm tra ký nhận kết quả quan sát, không suy từ headless PASS.

Hồ sơ nhiệm vụ 1 ghi nhận 133 JUnit test với 132 pass, 1 process smoke failure,
các check/main được chạy riêng; CSV ngày 22/10 thuộc revision lịch sử khác.
Đó là mốc khảo sát ban đầu, không thay cho các lượt đo/thử đã lưu riêng theo nhóm trong Bảng 11.7.
Chương 12 sẽ tách dữ liệu đã thu, lỗi còn tồn tại và nhóm chưa thực hiện khỏi thiết kế thực nghiệm này.

## 11.7. Thiết lập kiểm thử Session Recovery trên phiên bản tích hợp

### 11.7.1. Phiên bản, môi trường và loại bằng chứng

**Bảng 11.8. Môi trường của lượt kiểm thử recovery mới.**

| Thuộc tính | Giá trị đã lưu | Cách sử dụng |
|---|---|---|
| HEAD / nhánh | `492c03127f15a25f4fc685fd004eafe424d53f9f`, integration/session-recovery | Phải đọc cùng working tree và inventory, không gán 171 ca cho riêng HEAD |
| Source thực tế | 219 file Java main/test trùng inventory lượt test, có snapshot và tracked diff | Có cả file mới chưa commit; số file không phải số test |
| Hệ điều hành | Windows 11, build 10.0.22631, AMD64 | Máy cục bộ, không dùng thông số này để gán ngược cho mọi benchmark cũ |
| CPU đọc được | 16 logical CPU; processor identifier AMD64 Family 25 Model 116 Stepping 1, AuthenticAMD | Không suy tên thương mại/lõi vật lý/RAM; CIM bị từ chối |
| Runtime/build | Oracle JDK 25.0.1, Maven 3.9.12 offline; JUnit 5.11.4, Surefire 3.5.2 | Dùng cache dependency sẵn có; không thêm framework |
| Network | TCP loopback 127.0.0.1, port động | Socket/codec/reader/writer thật; không phải rút cáp hoặc LAN nhiều máy |
| Điều kiện thực thi cuối | Ngoài sandbox, đã được cho phép | Các attempt trong sandbox được giữ riêng, không xoá failure |
| Profile recovery | LobbyGameServer bật seamless recovery; auto client bật auto reconnect trong fixture tương ứng | Không gán recovery cho demo M1 hoặc mọi constructor mặc định |

Nguồn: [run-manifest](../evidence/recovery-report-task03-20261027-200413/run-manifest.json),
[source inventory](../evidence/recovery-report-task03-20261027-200413/source-inventory.json)
và [snapshot source](../evidence/recovery-report-task03-20261027-200413/source/).
Đây là thiết lập lượt mới ngày 27/10/2026, khác các run ngày 26/10/2026 ở phần trước.

### 11.7.2. Fixture và cách gây gián đoạn

RecoveryGameplayIntegrationTest tạo server thật với hai peer ClientNetwork/ClientWorldState,
map 17×15 tile 32, tường biên và một block tại (2,1). BombRules dùng fuse 1000 ms, range 1, quota 5;
MatchRules dùng trần quota/range/speed 5/8/144, speed increment 8, max lives 99 và initial lives 3 hoặc 1 theo case.
Thời lượng trận fixture là 30 s hoặc 5 s; policy drop trả SPEED_UP cố định để tái lập.
Đây không phải map/luật mặc định 180 s và fuse 3000 ms của sản phẩm.

Peer chủ động đóng transport để tạo unexpected disconnect rồi mở socket mới gửi RECONNECT;
không gửi LEAVE_ROOM/DISCONNECT như một yêu cầu rời trận có chủ ý.
Fixture chờ server quan sát DISCONNECTED trước bước kiểm chứng offline; PING 500 ms giữ peer còn nối sống
trong case chờ grace thực, khác nhịp heartbeat 2000 ms của client ứng dụng mặc định.
Ca auto-client riêng dùng DemoClientConnection và controller thực để kiểm tra ba lần tự phục hồi,
không thay mọi peer raw của fixture bằng một thao tác GUI thủ công.

Clock monotonic của gameplay được điều khiển bằng AtomicLong để gây nổ/timeout khi player đang offline.
Clock session trong case TCP expiry vẫn chạy thật với grace mặc định 15 s; chỉ unit test biên manager
tiêm clock/scheduler để kiểm tra 15 s−1 ns, đúng 15 s và 15 s+1 ns.
Không chờ thực 30 s để gọi đây là một trận đầy đủ 30 s wall-clock, và không nói mọi test timeout đều dùng 15 s thật.

### 11.7.3. Kịch bản, metric và tiêu chí chấp nhận

**Bảng 11.9. Ma trận recovery được dùng trong lượt kiểm thử mới.**

| Nhóm | Tác động thử | Tiêu chí chấp nhận | Yêu cầu liên quan |
|---|---|---|---|
| R01–R03 | Nhiều MOVE, 4 bom trước ngắt, 3 reconnect; peer khác vẫn gửi input | Giữ identity/runtime, player offline dừng movement; full bằng peer cùng tick rồi delta; thêm được bom 5, request trùng không lặp | FR05/06/10/15 |
| R04–R06 | Bom nổ và block/item/respawn/timer đổi khi offline; resume rồi pickup/thêm full | Full phản ánh world hiện tại; damage/pickup không áp lặp | FR07–FR11/15 |
| R07–R08 | Token sai/ID lạ/thiếu trường; cả hai player offline rồi về | Request sai không phá owner hợp lệ; cùng runtime, không ghost session/timer | FR14/15, NFR07 |
| R09–R10 | TIMEOUT hoặc LAST_ALIVE trong grace | Peer nhận kết quả, runtime dừng; reconnect không tạo lại trận/player | FR12/13/15 |
| R11–R12 | Hết grace 15 s thật; ba biên clock điều khiển | Từ chối đúng deadline; ABORT/ghế/host/WAITING/cleanup đúng policy | FR13–FR15, NFR07 |
| R13–R14 | App client auto recovery 3 vòng và teardown từng fixture | Cùng controller/counter/listener; dừng thread/worker/transport/timer thuộc fixture | FR11/15, NFR07 |
| Client gate/fault | Thiếu ACK/full, ngắt nhiều pha, callback UI cũ, giữ phím, cancel connect | Không mở input sớm/ghi đè world mới, budget tổng không reset; close được | FR10/11/15, NFR03/07 |
| Server race/fault | Timer/socket/heartbeat cũ, claim chồng, shutdown/writer fault, queue lifecycle đầy | Đúng ownership/ticket/rollback; lỗi thật được ghi; không giả freeze/unfreeze thành công | FR14/15, NFR06/07 |

Các mã R là nhóm kịch bản theo [thiết kế test](../session-recovery/03_THIET_KE_KIEM_THU.md), không phải số execution độc lập.
R01/R02/R03 cùng một test; R04/R05/R06 cùng một test; TIMEOUT/LAST_ALIVE là hai execution parameterized.
Equality full so cùng tick gồm dimensions/tileSize/match state, map, toàn bộ PlayerData/ACK,
entity, MatchFrame/HUD và BombFrame theo biểu diễn chuẩn hoá trong test. Không chỉ so vị trí hoặc số entity.

Metric của đợt này là số execution pass/fail/error/skipped và các assertion nghiệp vụ/cleanup.
`observed_wait_ms` của case expiry bắt đầu sau khi test đã quan sát DISCONNECTED và kết thúc khi nhận GAME_OVER;
không bằng mốc tạo ticket server và không phải recovery latency. Time của JUnit/Maven gồm setup/chờ/teardown,
không dùng làm P50/P95 thời gian phục hồi, throughput hoặc chi phí byte của full khi reconnect.

### 11.7.4. Lượt chạy, tái lập và bảo toàn dữ liệu

Đợt thực hiện có hai full suite trong sandbox đều có một failure process smoke M1,
một smoke chạy riêng trong sandbox cũng lỗi; sau đó smoke riêng và full suite ngoài sandbox đạt.
Đã biên dịch production lại từ cùng source giữa các attempt để loại trừ class cũ, không đổi source/assertion/timeout.
Không thiết kế đây thành một loạt mẫu thống kê recovery: các attempt khác phạm vi và môi trường,
các vòng reconnect lồng trong testcase cũng không phải các run độc lập.

Lượt full cuối có log/XML của tất cả class; TV2 checks và NetworkTest main chạy riêng và lưu exit code riêng.
Collector đối chiếu tổng XML với log full và tên suite, tách 11 marker stdout, lưu 171 dòng execution CSV,
source snapshot/hash, manifest và checksum ngoài target. Log raw PowerShell có thể là UTF-16LE;
CSV tổng hợp là UTF-8 có BOM. Không ghi đè các log thất bại trước khi chạy lại.

Lệnh tái lập ở root, cấu hình đường Maven/JDK theo máy và lưu log/exit code vào thư mục run mới:

```powershell
$env:JAVA_HOME='D:/JavaJDK' # Giá trị của máy đã đo; thay theo máy tái lập.
$recoveryMaven = if ($env:BOMBIT_MVN) { $env:BOMBIT_MVN } else { 'mvn.cmd' }
& $recoveryMaven '-o' test
# Ghi ngay $LASTEXITCODE; offline chỉ dùng được khi dependency đã có trong local repository.
cmd /c scripts\check-tv2.cmd
& (Join-Path $env:JAVA_HOME 'bin/java.exe') -cp 'target/classes;target/test-classes' `
    com.bombit.integration.NetworkTest
```

Máy đã đo truyền thêm `-Dmaven.repo.local=C:/Users/Chinh/.m2/repository` và dùng Maven binary có trong wrapper cache.
Muốn chạy riêng nhóm phục hồi, Surefire có thể chọn SessionRecoveryTest, RecoveryWriterTest,
SessionRecoveryClientTest, RecoveryInputTest, ConnectCancellationTest, RecoveryGameplayIntegrationTest
và các lớp tích hợp chung; kết quả chạy riêng phải mang run ID riêng, không ghép XML vào full suite cũ.
Thông tin môi trường/attempt và lệnh cụ thể được lưu tại [evidence lượt mới](../evidence/recovery-report-task03-20261027-200413/README.md).

Không có đối chứng recovery=true/false về latency/byte trong đợt này. Những fixture policy khác nhau kiểm tra
luật tương ứng, không tự tạo một A/B benchmark chứng minh recovery cải thiện X%.
Chưa thực hiện GUI thủ công, LAN/Wi-Fi vật lý, network impairment có kiểm soát, tải tối đa hoặc soak recovery.
Các giới hạn này phải đi cùng kết quả ở mục 12.8.
