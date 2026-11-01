## Test
### 1. Kiểm thử chức năng

```powershell
$mvnPath = (Get-ChildItem -Path "C:\Program Files" -Filter "mvn.cmd" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).DirectoryName
$env:Path += ";$mvnPath"
mvn clean
mvn test
```

### 2. Benchmark Hiệu năng Mạng

Mô phỏng 2 và 4 người chơi liên tục gửi lệnh di chuyển/đặt bom để đo độ trễ (RTT) và thông lượng (Throughput) của Server.

Biên dịch cả mã chính và công cụ benchmark trong test source trước khi chạy:

```powershell
mvn -DskipTests test-compile
```

```powershell
java -cp "target\classes;target\test-classes" com.bombit.tools.NetworkBenchmark --local --mode suite --seconds 10 --warmup 2 --label "single_jvm_loopback" --csv target\network-benchmark.csv
```

### Gameplay Stress Test

Kịch bản tăng dần số client theo các mốc 112, 120, 122 và 124. Mỗi client vào trận, gửi lệnh di chuyển và đặt bom. Mức tải đạt khi RTT P95 không vượt 150 ms, MOVE ACK loss không quá 1%, MOVE ACK P95 không quá 200 ms và tick rate nằm trong khoảng 18–22 Hz.

```powershell
java -Xss512k -cp "target\classes;target\test-classes" com.bombit.tools.NetworkBenchmark --local --mode stresstest --stress-levels 120,122,124,126,128 --move-rate 20 --warmup 5 --seconds 180 --max-rtt-p95-ms 150 --max-cpu-percent 95 --csv target\network-stresstest-full-120-128-180s.csv
```

Mỗi dòng trong `target\network-stresstest-full-120-128-180s.csv` là một mốc tải. `PASS` nghĩa là đạt các ngưỡng trên; khi gặp `FAIL`, mức client cao nhất trước đó có trạng thái `PASS` là mức tối đa đạt trong lượt đo. Server và các client mô phỏng cùng chạy trong một JVM trên loopback.

### 3. Nén Trạng Thái (State Delta Compression)

**Bước 1: Mở cấu hình chạy**

Trong IntelliJ, mở menu cấu hình Run/Debug ở cạnh nút Run rồi chọn **Edit Configurations...**. Có thể mở mục **Run** trên thanh menu và chọn **Edit Configurations...**.

**Bước 2: Chọn DeltaCompressionCheck**

Trong danh sách bên trái, chọn cấu hình **DeltaCompressionCheck** thuộc nhóm **Application**.

**Bước 3: Bật lưu console output**

Ở khung bên phải, mở **Modify options** và bật **Logs** (hoặc **Save console output to file**, tùy phiên bản IntelliJ). Tích chọn **Save console output to file**.

**Bước 4: Chọn đường dẫn file kết quả**

Điền `target/delta-compression-results.csv` vào ô đường dẫn lưu log.

**Bước 5: Lưu cấu hình và chạy**

Nhấn **Apply**, rồi **OK**. Chạy cấu hình **DeltaCompressionCheck** bằng nút Run.

### 4. Kiểm thử tốc độ lệnh ở nhiều phòng (Multi-room Command Rate Stress Test)

Chạy một dòng lệnh trong PowerShell để kiểm tra lần lượt 10, 50 và 100 client. Benchmark phân bố client thành khoảng 3, 13 và 25 phòng; mỗi lượt tăng tốc độ MOVE từ 20 lệnh/giây/người. Mỗi mức client được ghi vào một CSV riêng trong `target`.

```powershell
foreach($n in 10,50,100){$csv="target\network-command-rate-$n.csv";java -Xss512k -cp "target\classes;target\test-classes" com.bombit.tools.NetworkBenchmark --local --mode commandrate --clients $n --command-rates 20,30,40,50,60,80,100 --warmup 2 --seconds 10 --max-rtt-p95-ms 150 --max-ack-p95-ms 200 --max-ack-loss-percent 1 --min-tick-hz 18 --csv $csv}
```

Mỗi lượt dừng ở mức đầu tiên có `ANOMALY`; các mức client tiếp theo trong vòng lặp vẫn tiếp tục chạy. `ANOMALY` là kết quả đo theo ngưỡng, không phải lỗi biên dịch. Benchmark chạy server và client mô phỏng cùng JVM trên loopback.

## Experimental Results

1.Kiểm thử Chức năng
| Nguồn test (Test Class) | Kịch bản chính | Điều kiện đạt theo assertion | Kết quả lượt test |
| --- | --- | --- | --- |
| SessionRecoveryClientTest | Phục hồi phiên kết nối phía Client. | Giao diện và dữ liệu local khôi phục đúng trạng thái; không crash app. | 10/10 đạt |
| RecoveryInputTest | Thao tác nhập liệu trong quá trình đứt mạng. | Tín hiệu phím đưa vào bộ đệm và gửi thành công sau khi reconnect. | 2/2 đạt |
| RespawnPredictionTest | Thuật toán dự đoán vị trí hồi sinh (Prediction). | Tọa độ nhân vật hiển thị ở client khớp với kết quả từ server. | 2/2 đạt |
| ClientStabilityTest | Kiểm tra độ ổn định kết nối phía client. | Không văng lỗi (Exception) khi nhận luồng dữ liệu liên tục. | 7/7 đạt |
| ConnectCancellationTest | Hủy tiến trình kết nối mạng chủ động. | Socket đóng an toàn, tài nguyên bộ nhớ được giải phóng sạch. | 1/1 đạt |
| BombPresentationStateTest | Trạng thái hiển thị hoạt ảnh của bom. | Animation chuyển đổi đúng theo vòng đời nổ/hủy của bom. | 1/1 đạt |
| BombSceneTest | Hiển thị màn hình Scene chứa bom. | Chuyển cảnh và render lưới bom thành công không bị treo UI. | 2/2 đạt |
| Java2DRendererTest | Bộ vẽ đồ họa Java2D cơ bản. | Các object đồ họa xuất ra đúng ma trận tọa độ pixel. | 2/2 đạt |
| ItemClientStateTest | Trạng thái hiển thị vật phẩm (Item) ở client. | Item biến mất trên UI ngay khi có tín hiệu nhặt thành công. | 1/1 đạt |
| TileGridRendererTest | Render lưới bản đồ tĩnh (Tile Grid). | Vẽ chuẩn kích thước grid gốc, không vỡ khung hình. | 1/1 đạt |
| ModeSelectionPanelTest | Màn hình giao diện chọn chế độ chơi. | Giao diện nạp đủ danh sách mode và phản hồi đúng sự kiện click. | 2/2 đạt |
| MatchResultsPanelTest | Màn hình tổng kết quả trận đấu. | Hiển thị đúng dữ liệu thứ hạng, số kill và điểm số. | 1/1 đạt |
| TeamGuiPresentationTest | Giao diện HUD của các đội chơi (Team). | Tên, màu sắc và thanh máu của team render chính xác trên HUD. | 3/3 đạt |
| EffectiveRulesTest | Thiết lập các ràng buộc luật chơi hiệu lực. | Thời gian > 0, số mạng >= 1; các ruleset bắt buộc phải hợp lệ. | 13/13 đạt |
| MatchFormatContractTest | Hợp đồng định dạng dữ liệu ván đấu. | DTO payload tuân thủ nghiêm ngặt chuẩn contract khai báo. | 4/4 đạt |
| BombProtocolTest | Giao thức đóng gói/mở gói tin bom. | Object byte serialize/deserialize bảo toàn 100% dữ liệu gốc. | 4/4 đạt |
| GameplayProtocolTest | Giao thức thao tác điều khiển gameplay. | Gói tin phím bấm/di chuyển được mã hóa đúng chuẩn giao thức. | 3/3 đạt |
| IntegrationContractTest | Hợp đồng liên lạc tích hợp client-server. | Các API giao tiếp qua lại thỏa mãn định dạng ràng buộc. | 8/8 đạt |
| LobbyContractTest | Ràng buộc giao thức của Sảnh (Lobby). | Gói tin tạo/thoát sảnh parse đúng thành object quản lý. | 4/4 đạt |
| ParadoxProtocolTest | Giao thức riêng của chế độ nghịch lý Paradox. | Dữ liệu nhảy vọt thời gian (timeline) encode đúng payload. | 5/5 đạt |
| ProtocolV3Test | Core mã hóa giao thức nhị phân V3. | Chuỗi byte sinh ra chuẩn format V3, tương thích ngược an toàn. | 5/5 đạt |
| SnapshotV6Test | Đóng gói map Snapshot chuẩn V6. | Cấu trúc map lớn được serialize đầy đủ mà không mất object. | 4/4 đạt |
| TeamMatchResultProtocolTest | Giao thức gửi kết quả chế độ Team. | Điểm số và thông tin xếp hạng team mã hóa không sai lệch. | 2/2 đạt |
| AllMatchFormatsIntegrationTest | Tích hợp chạy thử tất cả format trận. | Server khởi chạy được mọi format game mà không ném lỗi. | 1/1 đạt |
| BombClientIntegrationTest | Tích hợp giao tiếp bom hai chiều. | Client gửi đặt bom -> Server xác nhận -> Bom nổ đồng bộ tốt. | 3/3 đạt |
| ConfiguredLobbyIntegrationTest | Tích hợp sảnh có nạp file cấu hình. | Sảnh load chính xác file custom ruleset từ bộ nhớ. | 1/1 đạt |
| CurrentLobbyProtocolTest | Luồng giao thức sảnh hiện tại. | Client và server bắt tay (handshake) vào sảnh thành công. | 4/4 đạt |
| LobbyLifecycleTest | Vòng đời hoạt động của Sảnh. | State machine chạy chuẩn: tạo, join, play, hủy và xóa memory. | 15/15 đạt |
| MatchFormatLobbyIntegrationTest | Tích hợp format luật chơi vào Sảnh. | Sảnh áp dụng chính xác luật (ví dụ: giới hạn time) vào game. | 4/4 đạt |
| MatchLifecycleIntegrationTest | Vòng đời thực tế của một trận đấu. | Start, vòng lặp, end game xử lý đúng theo luồng sự kiện. | 5/5 đạt |
| MovementDemoProcessTest | Trình giả lập quá trình di chuyển. | Process mô phỏng di chuyển mượt mà qua các frame. | 1/1 đạt |
| MovementDemoTest | Pass các case di chuyển cơ bản (Demo). | Không bị kẹt tường, đi đúng tốc độ tính toán. | 8/8 đạt |
| ParadoxRecoveryIntegrationTest | Phục hồi mạng giữa chừng khi chơi Paradox. | Tái tạo lại state lịch sử chính xác; không sinh rác bộ nhớ. | 9/9 đạt |
| ParadoxTimelineIntegrationTest | Tích hợp trục thời gian Paradox. | Checkpoint lưu trữ đúng vị trí để rollback không sai lệch. | 1/1 đạt |
| RecoveryGameplayIntegrationTest | Các case phục hồi gameplay phức tạp. | Replay kết quả đúng; reject handshake nếu sai token; xử lý orphan client. | 8/8 đạt |
| ShadowLobbyIntegrationTest | Tích hợp Sảnh có chế độ Shadow. | Sảnh khởi tạo và nhận cờ cấu hình khuất bóng thành công. | 4/4 đạt |
| StabilityLifecycleTest | Stress test vòng đời hệ thống. | Chạy liên tục nhiều luồng không xảy ra hiện tượng memory leak. | 3/3 đạt |
| ChatFaultTest | Chịu lỗi hệ thống kênh Chat. | Spam tin rác hoặc gửi format dị thường không làm sập phòng. | 1/1 đạt |
| BombGameplayTest | Core kịch bản đặt và nổ bom. | Kích nổ bom đúng block/giới hạn; pass 10 nhánh luật fixture. | 10/10 đạt |
| BombSchedulerTest | Bộ đếm ngược thời gian bom nổ. | Lập lịch nổ kích hoạt chuẩn xác từng mili-giây. | 1/1 đạt |
| BombSystemTest | Cơ chế nâng cao: Trùng ô, chain reaction. | Bom nổ dây chuyền đúng mạch; block dừng tia lửa điện chuẩn. | 4/4 đạt |
| ItemSystemTest | Cơ chế sinh vật phẩm (Spawn/Pickup). | Item rơi ra ngẫu nhiên và kích hoạt tác dụng chuẩn xác. | 2/2 đạt |
| ArenaGeneratorTest | Thuật toán sinh bản đồ tự động. | Phân bổ hòm/tường không tạo ra dead-end không thể vượt qua. | 3/3 đạt |
| ClassicModeFactoryTest | Khởi tạo map cho chế độ Cổ điển. | Factory sinh ra đúng số liệu cấu trúc chuẩn của mode Cổ điển. | 3/3 đạt |
| ModeRegistryTest | Đăng ký các bộ luật chơi với hệ thống. | Toàn bộ các class chế độ chơi được Load vào memory hợp lệ. | 9/9 đạt |
| ParadoxAuthoritativeTest | Cấp phép thẩm quyền trong mode Paradox. | Server làm nguồn gốc duy nhất, chống client tự ý dịch thời gian. | 6/6 đạt |
| ParadoxFoundationTest | Nền tảng cấu trúc mode Paradox. | Engine theo dõi trục thời gian (timeline) khởi tạo an toàn. | 6/6 đạt |
| ParadoxGameplayCheckpointTest | Thuật toán sao lưu state Paradox. | Trạng thái lưu/rollback không làm mất entity hay sai vật lý. | 8/8 đạt |
| ShadowFoundationTest | Nền tảng chế độ khuất tầm nhìn (Shadow). | Engine che giấu thông tin (Fog of war) được build thành công. | 4/4 đạt |
| ShadowGameplayTest | Logic gameplay ảnh hưởng bởi bóng tối. | Entity nấp sau tường không thể bị nhận diện bởi đối thủ. | 9/9 đạt |
| ShadowScanTest | Thuật toán quét/Raycast Shadow. | Quét radar phát hiện đúng vật cản để xác định góc tối. | 5/5 đạt |
| ShadowSynchronizationTest | Đồng bộ trạng thái Shadow xuống Client. | Chỉ gửi các entity thuộc vùng sáng khả kiến tới từng client. | 7/7 đạt |
| ShadowUiTest | Xử lý hiển thị UI vùng tối trên màn hình. | Vùng đen che giấu bản đồ render trơn tru không gãy ảnh. | 5/5 đạt |
| ShadowVisibilityTest | Quản lý vòng đời thực thể khi vào vùng tối. | Cắt luồng update dữ liệu của object lập tức khi nó rời khỏi FOV. | 5/5 đạt |
| DeltaCompressionTest | Nén dung lượng dữ liệu bằng Delta. | Size gói tin nén giảm ~85.09% so với nguyên bản; packet đi đủ. | 1/1 đạt |
| MovementFeatureTest | Tổ hợp tính năng lưới di chuyển (Move). | Prediction, nội suy, xử lý va chạm và luồng TCP chạy mượt mà. | 1/1 đạt |
| BombRuntimeIntegrationTest | Chạy thực tế luồng bom trên server tick. | Thread xử lý bom không xung đột với thread game cập nhật map. | 4/4 đạt |
| ConfiguredRuntimeTest | Cấu hình vòng lặp Tick-rate server. | Máy chủ duy trì đúng TPS (Ticks per second) theo setting truyền vào. | 8/8 đạt |
| ExtendedItemsTest | Xử lý các hiệu ứng Item nâng cao. | Khiên (Shield) không cộng dồn sai; item hồi sinh chặn đánh lừa. | 6/6 đạt |
| MatchGameplayTest | Luồng xử lý thi đấu chung. | Tranh chấp nhặt item một người thắng; xác định đúng Winner. | 5/5 đạt |
| MovementBalanceTest | Cơ chế giới hạn lạm dụng di chuyển. | Tốc độ kịch trần (Max speed) ngăn ngừa hack speed bên client. | 4/4 đạt |
| ParadoxRuntimeTest | Vòng lặp runtime riêng cho Paradox. | Event timeline được tiêm (inject) vào đúng tick của server. | 2/2 đạt |
| RuntimeContractTest | Đảm bảo hợp đồng an toàn đa luồng. | Chuẩn FIFO, queue limit; dọn dẹp bộ nhớ (cleanup) thread an toàn. | 1/1 đạt |
| TeamMatchGameplayTest | Trận đấu chế độ chia Đội chơi (Team). | Điểm số cộng/trừ chia đúng phe phái; loại đội thua chính xác. | 10/10 đạt |
| RecoveryWriterTest | Cơ chế ghi file/buffer bản vá phục hồi. | Ghi đệm IO packet phục hồi không bị ném lỗi bộ nhớ tràn. | 1/1 đạt |
| ServerTransportTest | Tầng giao vận (Transport) kết nối. | Gửi/nhận packet Inbound/Outbound đa luồng trơn tru. | 10/10 đạt |
| SessionWriterTest | Dữ liệu stream từ Session gửi đi. | Đảm bảo luồng byte ghi xuống socket theo đúng thứ tự (order). | 3/3 đạt |
| TransportStabilityTest | Ổn định giao vận mức cao. | Chịu tải liên tục không rớt socket hay ngắt mạng nội bộ. | 6/6 đạt |
| MatchFormatRoomTest | Logic format thiết lập vào Phòng. | Phòng chặn các cấu hình lậu sai định dạng format quy định. | 2/2 đạt |
| RoomConfigurationV3Test | Engine nạp cấu hình phòng V3. | Parse file cấu hình phức tạp V3 thành object không mất dữ liệu. | 2/2 đạt |
| RoomManagerTest | Bộ quản lý tập trung các Phòng chờ. | Cấp phát Room ID ngẫu nhiên không trùng lắp (Collision). | 1/1 đạt |
| ShadowRoomTest | Sảnh chuyên dụng biệt lập cho Shadow mode. | Sảnh phân nhánh mạng riêng, cắt luồng nhìn thấy toàn map. | 2/2 đạt |
| SessionFaultTest | Chịu lỗi khi kết nối đứt đột ngột. | Cô lập người chơi rớt mạng; máy chủ game không bị sập lây. | 1/1 đạt |
| SessionManagerTest | Trình quản lý toàn bộ Phiên đăng nhập. | Đăng ký token và thu hồi token đúng logic, không giữ session ma. | 4/4 đạt |
| SessionRecoveryTest | Logic ân hạn (Grace Period) đứt kết nối. | Cấp quyền (admitted=true) nếu đúng hạn; từ chối (false) nếu trễ. | 13/13 đạt |
| NetworkBenchmarkTest | Công cụ Benchmark sức chịu tải. | Cân bằng đủ 4 clients bom đồng thời, băng thông phản hồi cao. | 4/4 đạt |


2.Benchmark Hiệu năng Mạng

| **Kịch bản Test**          | **Số Client** | **Độ trễ mạng (Ping P95 - ms)** | **Độ trễ di chuyển (Move ACK P95 - ms)** | **Độ trễ đặt bom (Plant ACK - ms)** | **Thời gian xử lý di chuyển (ms)** | **Thời gian xử lý đặt bom (ms)** | **Tốc độ truyền (Băng thông Gửi - B/s)** | **Tốc độ nhận (Băng thông Nhận - B/s)** |
| -------------------------- | ------------- | ------------------------------- | ---------------------------------------- | ----------------------------------- | ---------------------------------- | -------------------------------- | ---------------------------------------- | --------------------------------------- |
| **Transport (Truyền tải)** | 1             | 4.129                           | -                                        | -                                   | -                                  | -                                | 94.99                                    | 94.99                                   |
| **Transport (Truyền tải)** | 2             | 8.315                           | -                                        | -                                   | -                                  | -                                | 95.00                                    | 95.00                                   |
| **Transport (Truyền tải)** | 4             | 4.357                           | -                                        | -                                   | -                                  | -                                | 94.99                                    | 94.99                                   |
| **Idle (Trạng thái rảnh)** | 2             | 3.787                           | -                                        | -                                   | -                                  | -                                | 95.00                                    | 486.99                                  |
| **Idle (Trạng thái rảnh)** | 4             | 3.547                           | -                                        | -                                   | -                                  | -                                | 94.98                                    | 583.70                                  |
| **Movement (Di chuyển)**   | 2             | 18.084                          | 64.114                                   | -                                   | **49.493**                         | -                                | 1,728.91                                 | 6,430.74                                |
| **Movement (Di chuyển)**   | 4             | 17.120                          | 76.549                                   | -                                   | **61.477**                         | -                                | 1,749.57                                 | 9,868.00                                |
| **Bombs (Đặt bom)**        | 2             | 21.753                          | 70.958                                   | 66.054                              | **54.976**                         | **50.072**                       | 1,781.31                                 | 6,765.95                                |
| **Bombs (Đặt bom)**        | 4             | 17.685                          | 77.531                                   | 49.161                              | **62.589**                         | **34.219**                       | 1,789.33                                 | 10,288.42                               |

Hai cột “Thời gian xử lý” là **ước tính phần trễ còn lại sau khi trừ Ping TB (`rtt_mean_ms`)**: thời gian xử lý di chuyển = Move ACK P95 trung bình trừ Ping TB trung bình; thời gian xử lý đặt bom = Plant ACK trung bình trừ Ping TB trung bình. CSV không đo trực tiếp thời gian xử lý nội bộ server; các giá trị này chỉ là phép ước tính, không nên diễn giải như thời gian CPU/server thuần túy. Plant ACK là thời gian từ khi client gửi lệnh đặt bom đến khi client thấy bom trong snapshot.

3.Nén Trạng Thái (State Delta Compression) 
| Chỉ số Đo lường (Metrics) | Không tối ưu (Full State) | Đã tối ưu (Delta Compression) | Tỉ lệ Cải thiện |
| --- | --- | --- | --- |
| Tổng dung lượng truyền tải | 110,076 Bytes | 16,411 Bytes | Giảm ~85.1% |
| Dung lượng trung bình / tick | ~550.4 Bytes | ~82.1 Bytes | Giảm ~85.1% |
| Dung lượng lớn nhất / tick (Max) | 561 Bytes | 561 Bytes (Chỉ ở tick Reconnect) | Giữ nguyên giới hạn trên |
| Mức tiêu hao khi Đứng yên (Idle) | 525 - 561 Bytes | 0 Bytes | Tiết kiệm tuyệt đối (100%) |
| Mức tiêu hao khi có sự kiện (Mode) | 525 - 561 Bytes | 185 Bytes (Phổ biến nhất) | Giảm ~66% |
| Số lần rảnh rỗi (0 Bytes) | 0 / 200 ticks (0%) | 117 / 200 ticks (58.5%) | Tối ưu tài nguyên cực tốt |

4. Kiểm thử tốc độ lệnh ở nhiều phòng (Multi-room Command Rate Stress Test)

| Client | Phòng | Tốc độ thực tế (lệnh/người/giây) | Lệnh gửi | Đã ACK | Chưa ACK khi kết thúc | MOVE ACK P95 (ms) | RTT P95 (ms) | Tick TB (Hz) | Kết quả | CSV thô |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| 10 | 3 | 19.986 | 2,000 | 2,000 | 0 | 32.405 | 6.519 | 19.986 | PASS | [network-command-rate-10.csv](statics/results/network-command-rate-10.csv) |
| 10 | 3 | 29.987 | 3,000 | 2,200 | 800 | 3,511.083 | 6.276 | 20.091 | ANOMALY | [network-command-rate-10.csv](statics/results/network-command-rate-10.csv) |
| 50 | 13 | 19.993 | 10,000 | 10,000 | 0 | 71.152 | 5.934 | 20.025 | PASS | [network-command-rate-50.csv](statics/results/network-command-rate-50.csv) |
| 50 | 13 | 29.996 | 15,000 | 10,992 | 4,008 | 3,500.687 | 6.203 | 20.057 | ANOMALY | [network-command-rate-50.csv](statics/results/network-command-rate-50.csv) |
| 100 | 25 | 19.991 | 20,000 | 20,000 | 0 | 70.709 | 6.122 | 20.114 | PASS | [network-command-rate-100.csv](statics/results/network-command-rate-100.csv) |
| 100 | 25 | 29.990 | 30,000 | 21,992 | 8,008 | 3,504.116 | 6.149 | 20.090 | ANOMALY | [network-command-rate-100.csv](statics/results/network-command-rate-100.csv) |
| 122 | 31 | 19.989 | 24,400 | 24,400 | 0 | 72.905 | 5.908 | 20.143 | PASS | [network-command-rate-multiplayer.csv](statics/results/network-command-rate-multiplayer.csv) |
| 122 | 31 | 29.993 | 36,600 | 26,832 | 9,768 | 3,505.975 | 5.920 | 20.089 | ANOMALY | [network-command-rate-multiplayer.csv](statics/results/network-command-rate-multiplayer.csv) |

Ở các lượt đo này, 20 lệnh/người/giây đạt ngưỡng với 10, 50, 100 và 122 client. Mức 30 lệnh/người/giây vượt ngưỡng MOVE ACK P95 200 ms; số “chưa ACK” là lệnh chưa được xác nhận sau cửa sổ đo và một giây chờ, không khẳng định chúng mất vĩnh viễn. CPU/RAM không được đo riêng cho server vì server và load generator cùng JVM.


## Novelty and Contributions
| Contribution | Description | Evidence |
| --- | --- | --- |
| State Delta Compression(Nén dữ liệu trạng thái) | Cách tiếp cận thông thường (Baseline): Gửi toàn bộ mảng tọa độ bản đồ 20 lần/giây (Full State Snapshot - tốn ~550 bytes/gói).Cải tiến của Project: Thuật toán so sánh trạng thái và chỉ đóng gói dữ liệu của các ô có sự thay đổi (Delta). | Bằng chứng từ Experiment (File delta-compression-results.csv): <br>Ở trạng thái nhàn rỗi (Idle): Không tiêu tốn băng thông (0 bytes) trong 58.5% thời gian.<br>Khi tải nặng: Dung lượng phổ biến chỉ là 185 bytes/gói.<br>Kết quả chung: Tiết kiệm được 85.09% tổng băng thông mạng.<br>Bằng chứng Implementation: 1/1 Unit Test Pass (Class DeltaCompressionTest) với kết quả logs: full=110076 bytes, delta=16411 bytes, saved=85.09%. |
| Seamless Session Recovery(Phục hồi phiên chơi liền mạch) | Cách tiếp cận thông thường (Baseline): Lập tức ngắt kết nối (Kick) và xóa dữ liệu nhân vật khỏi phòng chơi ngay khi Client mất mạng.Cải tiến của Project: Áp dụng cơ chế chịu lỗi (Fault Tolerance) để giải quyết đứt cáp/lag Wi-Fi. Khi rớt mạng, Session chuyển sang `DISCONNECTED`, nhân vật được đóng băng trong thời gian ân hạn; cấu hình mặc định của server là 30 giây. Nếu Client reconnect bằng SessionID/token hợp lệ, Server gửi `FULL_STATE_SYNC` để đồng bộ lại trạng thái và cho chơi tiếp. | Bằng chứng cài đặt (Implementation & Automated Tests):<br>Kiểm thử biên thời gian ân hạn (`SessionRecoveryTest` - 13/13 cases): kiểm tra grace period 15 giây và 30 giây, chấp nhận ngay trước hạn và từ chối tại/sau hạn; cấu hình production mặc định là 30 giây.<br>Kiểm thử tích hợp (`RecoveryGameplayIntegrationTest` - 8/8 cases): kiểm tra reconnect nhiều lần, full state, input tiếp tục và khôi phục gameplay. Các kịch bản mất kết nối nhiều lần và cả hai người chơi cùng offline cũng được kiểm tra. |
| Shadow (đồng bộ theo quyền quan sát) | Server lọc trạng thái theo đội và tầm nhìn trước khi gửi. Mỗi người nhận có snapshot/baseline riêng; client thêm, cập nhật hoặc loại entity khi vùng quan sát thay đổi. Reconnect nhận full sync theo đội và tầm nhìn hiện tại. Lọc dữ liệu giúp kiểm soát thông tin; chưa thể kết luận giảm byte hoặc CPU nếu chưa đo. | `ShadowSynchronizationTest` (7/7), `ShadowVisibilityTest` (5/5), `ShadowLobbyIntegrationTest` (4/4). |
| Paradox (đồng bộ khi chuyển timeline) | Server khôi phục checkpoint authoritative, tăng timeline epoch để loại command cũ, reset baseline và buffer client, rồi gửi full state trước khi mở lại input. Reconnect và yêu cầu rewind đồng thời được xử lý theo timeline hiện tại. Rewind là cơ chế gameplay; phục hồi khi server sập thuộc Session Recovery. | `ParadoxAuthoritativeTest` (6/6), `ParadoxTimelineIntegrationTest` (1/1), `ParadoxRecoveryIntegrationTest` (9/9). |
