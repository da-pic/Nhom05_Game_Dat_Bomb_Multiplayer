# Hồ sơ nhiệm vụ báo cáo 8 — Triển khai TV1 và hạ tầng TV4

**Ngày đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [mục 10 — bản thảo từng phần](../../chapters/10_TRIEN_KHAI_HE_THONG.md).
**HEAD:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
Đây là nhiệm vụ **viết báo cáo số 8**, không phải mốc tích hợp gameplay TASK8 trong tài liệu kỹ thuật cũ.

## 1. Phạm vi đã viết và phần chờ theo kế hoạch

| Mục | Trạng thái bản thảo sau nhiệm vụ 8 |
|---|---|
| 10.1 | Đã viết công nghệ/POM, cây cấu trúc, bootstrap và script vận hành |
| 10.2 | Đã viết TCP/session/room/chat/heartbeat và shutdown |
| 10.3–10.5 | Giữ heading và ghi chú; phần TV2 viết ở nhiệm vụ 9 |
| 10.6 | Giữ heading và ghi chú; phần TV3 viết ở nhiệm vụ 10 |
| 10.7.1 | Map/player/HUD: TV2 bổ sung ở nhiệm vụ 9 |
| 10.7.2 | Bom/item/effect: TV3 bổ sung ở nhiệm vụ 10 |
| 10.7.3 | Đã viết bảng kết quả và UI chuyển lượt của TV1 |
| 10.8 | Đã viết codec/router/ClientNetwork/connection owner, metrics/runner và vận hành TV4 |

Các phần chưa viết không có nghĩa chưa tồn tại implementation trong code.
Nhiệm vụ này hoàn thành phạm vi phần viết được giao, chưa đánh dấu toàn chương 10 đã hoàn chỉnh.
Không đổi nội dung các phần lý thuyết/giải pháp đã viết hoặc copy toàn schema ở mục 9 vào Implementation.

Căn cứ: [mục lục chính thức](../../00_MUC_LUC_CHINH_THUC.md),
[Instruction, mục 8.10](../../../phancong/Instruction.md),
[phân công module](../../../docs/FILE_OWNERSHIP_NOTES.md) và code workspace.
Phân công không được dùng để xác nhận ai viết từng dòng hoặc phần trăm đóng góp cá nhân.
Không thêm nguồn ngoài hoặc đổi số References trong lượt mô tả implementation từ code này.

## 2. Căn cứ kỹ thuật và điểm đã đối chiếu

Đường dẫn Java tương đối với `src/main/java/com/bombit/`.

| Nội dung | Nguồn code/tài liệu | Cách mô tả trong chương |
|---|---|---|
| Java/dependency/plugin | `pom.xml` tại root | Release 25, UTF-8, compiler 3.13.0, Surefire 3.5.2, JUnit 5.11.4 test scope; không suy baseline 17 từ docs cũ |
| Entry point | `server/app/ServerApplication.java`, `client/app/ClientApplication.java` | Mặc định lobby; profile demo/headless là nhánh khác |
| Build/run/test/package | `scripts/build.ps1`, `build-demo.cmd`, `run-server.cmd`, `run-client.cmd`, `classpath.cmd`, `java-env.cmd`, `test.cmd`, `package.ps1`, `run-benchmark.cmd` | Chỉ đọc script; classpath ưu tiên root JAR rồi target JAR rồi demo-classes; không chạy build/test/package |
| Accept/pool/admission | `server/network/Server.java` | Pool 32 + queue 32, retained session 256; các giới hạn không phải benchmark tải đạt |
| Reader/ownership/deadline | `server/network/ClientHandler.java` | Capture socket; deadline toàn frame; gate CONNECT, route, exception mapping và finally cleanup |
| Writer/cleanup | `server/network/SessionWriter.java`, `ConnectionManager.java` | Producer encode, worker write/flush; 256 frame chờ, 4 MiB có frame đang ghi; failure callback qua cleanup executor |
| Message/broadcast | `server/network/OutboundMessage.java`, `BroadcastSender.java` | Clone byte; chuyển qua writer; không đảm bảo delivery cho mọi thành viên |
| Session state | `server/session/Session.java`, `SessionState.java`, `SessionManager.java` | UUID phiên khác gameplay ID; trạng thái tạm CONNECTED, handshake, disconnect/expiry; legacy reconnect khác sản phẩm resume |
| Room/Start | `server/room/Room.java`, `RoomManager.java`, `server/app/LobbyGameServer.java` | setReady khác toggle; startMatch lobby khác startGame legacy; không có room/player state trong router |
| Chat | `server/chat/ChatHandler.java` | Queue 256 ở cấu hình Server; worker kiểm tra lại sender membership khi consume |
| Heartbeat | `server/heartbeat/HeartbeatManager.java`, `server/dispatch/SessionHandlers.java` | Route PING ở SessionHandlers; HeartbeatManager sweep timeout, onPing là API khác chưa dùng cho route này |
| Codec/router | `common/protocol/PacketEncoder.java`, `PacketDecoder.java`, `LobbyJson.java`, `MatchEnvelopeCodec.java`, `server/dispatch/MessageRouter.java` | Các tầng validation khác nhau; router gọi handler trên thread caller; canonical body không phải JSON tùy ý |
| ClientNetwork | `client/network/ClientNetwork.java` | Send có thể block; reader callback chưa ở EDT; pull mode tùy chọn; disconnect và close khác phạm vi |
| Client owner/lobby/results | `client/app/DemoClientConnection.java`, `client/lobby/LobbyWindow.java`, `MatchResultsPanel.java` | Tên Demo vẫn dùng cho lobby; listener trước CONNECT; subscribe=false, UI tuần tự; kết thúc lượt khác đóng TCP |
| Monitor | `metrics/LatencyMonitor.java`, `ThroughputMonitor.java` | Mẫu RTT giới hạn khác pending map; empty sample trả 0 cần sample count; không cộng trùng monitor và runner counter |
| Runner/CSV | `tools/NetworkBenchmark.java`, `BenchmarkCsv.java` | Mode/config và metadata; plant_ack_ms suy từ replica thấy bom, không có ACK placement riêng; mỗi process/file |

Các tên rút gọn nằm cùng thư mục với file đầu nhóm. Hash file có link trực tiếp trong chương được ghi tại
[source-links.sha256.json](source-links.sha256.json), gồm cả POM/script; không phải full dependency inventory.

## 3. Các giới hạn được giữ khi viết

- Chưa chạy lại suite/GUI/LAN/benchmark hoặc tái đóng gói. Script và test class là công cụ hiện có, chưa phải kết quả mới.
- Nhiệm vụ 1 ghi nhận process smoke failure. Không suy toàn suite xanh từ việc code và script đã tích hợp.
- Metadata source revision/dirty của build không xác nhận mọi tài liệu chưa tracked đã được commit hoặc được đưa vào bản nộp.
- Client dùng JDK Swing cần môi trường đồ họa; không tự thêm web frontend, game engine, DB hay JSON framework vào mô tả.
- SessionManager còn API reconnect, RoomManager còn start/toggle legacy, HeartbeatManager còn onPing;
  không dùng tên API để gán sai đường gọi production.
- Limit reader/session/queue/chat/monitor được ghi theo code; không đổi thành chỉ tiêu số người dùng hoặc SLA đạt.
- Kết quả UI dùng MatchResult đã decode, không tự tính winner/rank; phần tính gameplay thuộc TV3 ở nhiệm vụ 10.

## 4. Kiểm tra và bước tiếp theo

Kiểm tra heading đã viết/chờ, số bảng, link, POM versions và hash ở [validation.txt](validation.txt).
Không có hình mới cần xuất ở nhiệm vụ này; sơ đồ kiến trúc/protocol đã có ở mục 8/9.
Khi ghép chương sau nhiệm vụ 9/10, cập nhật số bảng theo thứ tự và bỏ placeholder/ghi chú tiến độ đầu chương.

**Tiếp theo:** nhiệm vụ 9 — viết Implementation phần TV2 server và client movement,
bổ sung 10.3–10.5 và 10.7.1 vào cùng file chương 10.
