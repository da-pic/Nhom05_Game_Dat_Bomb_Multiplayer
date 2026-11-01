# 11. Thiết lập thực nghiệm — Experimental Setup

> **Phân công: TV4 chủ trì thiết kế, lưu bằng chứng và tổng hợp; TV1 phụ trách transport/session/room và lỗi kết nối; TV2 phụ trách runtime/movement, replica và full/delta; TV3 phụ trách bom/item/damage/result. Cả nhóm xác nhận cấu hình và giới hạn của từng lần chạy.**

Theo [Instruction, mục 8.11 và mục 9](../../phancong/Instruction.md), thực nghiệm cần mô tả phần cứng,
OS, ngôn ngữ/thư viện, cấu hình mạng, dữ liệu và kịch bản; kết quả phải có số liệu thực tế.
Thiết kế này đánh giá ba câu hỏi: hệ thống thực hiện đúng contract gameplay hay không;
State Delta Compression giảm bao nhiêu byte trên cùng chuỗi trạng thái;
latency, ACK và lượng message thay đổi thế nào với workload và số client.
Các bảng kịch bản, thời lượng và số lần lặp dưới đây là **kế hoạch thu thập**, chưa phải kết quả đã chạy.
Kết quả khảo sát và CSV lịch sử được giữ riêng, không đổi nhãn thành thực nghiệm mới.
Kết quả thực hiện nhóm codec D0/D1, T1 và ba lượt reliability được báo cáo tại
[mục 12.4–12.6](12_KET_QUA.md); các nhóm nhiều JVM/LAN có điều kiện không được tính là đã đo.

## 11.1. Revision, phần cứng, OS/JDK và cấu hình

### 11.1.1. Môi trường đã được ghi nhận

**Bảng 11.1. Môi trường khảo sát đã có bằng chứng và thông tin cần bổ sung.**

| Thuộc tính | Thông tin đã xác minh | Phạm vi sử dụng |
|---|---|---|
| Revision khảo sát | `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5` | Mốc source, không thay hash artifact và trạng thái working tree |
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

T1 dùng ephemeral port khi runner tự tạo server. T2/T3 dùng port cố định được ghi trong manifest;
ví dụ lệnh bên dưới dùng 8888. Runner dùng TCP thật và luồng lobby/match hiện tại,
không thay world qua một đường debug để tạo số liệu mạng.
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

Các mã F là nhóm kịch bản, không thay số lượng JUnit test. Tên test/API cụ thể đã được truy vết ở
[hồ sơ khảo sát](../01_HO_SO_KHAO_SAT.md) và chương 10.
Không lấy việc lớp test tồn tại làm kết quả pass.
Bỏ update ở fixture F04 là fault injection tại tầng replica, không phải bằng chứng TCP tự làm mất message.
Reconnect resume trận không nằm trong tiêu chí nghiệm thu vì đường sản phẩm chưa bật tính năng đó;
disconnect/leave có thể kết thúc lượt ABORTED như contract hiện tại.

Kế hoạch chạy full suite một lần và từng check/main riêng một lần để ghi nhận tổng quan.
Các nhóm concurrency/lifecycle/fault có tính thời gian được chạy thêm ba lần độc lập với log riêng;
báo cả ba kết quả, không chỉ chọn lần đạt. Nếu full suite dừng khiến các bước check/main phía sau không chạy,
chạy riêng để thu bằng chứng và giữ trạng thái full suite thất bại.
Lỗi process smoke đã ghi nhận ở nhiệm vụ 1 cần hiện diện trong Results nếu chưa có lượt xác minh mới giải quyết nó.
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

**Bảng 11.7. Kế hoạch số lần chạy, chưa phải số lần đã hoàn thành.**

| Nhóm | Cấu hình | Lặp độc lập | Cửa sổ/chú ý |
|---|---|---:|---|
| TCP T1 | 9 ô: transport 1/2/4; idle/movement/bombs 2/4 | 5/ô | Warm-up 2 s; đo 10 s; process runner mới cho mỗi vòng suite |
| TCP T2 | Cùng 9 ô, khi đủ thời gian triển khai server process riêng | 5/ô | 2 s + 10 s; tách label với T1 |
| LAN T3 | Ưu tiên movement/bombs 2/4; thêm transport nếu thực hiện | 5/ô thực sự đo | Ghi số máy và runner/peer ở mỗi máy |
| D0 | Fixture 200 tick hiện có | 5 | Kiểm tra byte lặp lại; không coi là năm thử nghiệm latency |
| D1 | 2/4 player × idle/movement/bomb-block-item | 5/trace sau khi có harness | 600 tick; trace xác định, full mỗi 100 tick |
| F01–F09 | Suite/check tổng và nhóm concurrency/fault/lifecycle | 1 tổng; 3 lần nhóm nhạy thời gian | Ghi từng attempt, lỗi và exit code |
| F10 | GUI hai người và bốn người nếu thực hiện | 3 lượt/kịch bản | Biên bản người kiểm tra, không chỉ ảnh màn hình |

T1 chính có 45 scenario-run; vì CSV có một hàng cho mỗi client, năm vòng suite đầy đủ dự kiến 125 hàng,
không phải 125 lần chạy độc lập. Một suite gồm 9 scenario tuần tự, mỗi scenario local tạo server/client mới;
chúng không phải 9 scenario chạy song song. Thứ tự suite cố định là một hạn chế cần ghi nhận.
Các nhóm T2/T3/D1 là bổ sung có điều kiện; không tính số dự kiến vào Results nếu chưa chạy.
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
Những dữ liệu đó có thể được trình bày với đúng ngày/revision ở Results, nhưng chưa đáp ứng số lần lặp mới trong bảng 11.7.
Chương 12 sẽ tách dữ liệu đã thu, lỗi còn tồn tại và nhóm chưa thực hiện khỏi thiết kế thực nghiệm này.
