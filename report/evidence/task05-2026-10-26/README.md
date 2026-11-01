# Hồ sơ nhiệm vụ 5 — Kiến trúc hệ thống, mục 8

**Ngày đối chiếu:** 26/10/2026, Asia/Saigon.
**Đầu ra:** [chương 8](../../chapters/08_KIEN_TRUC_HE_THONG.md).
**HEAD:** `e333050997c5dbf78ec4b9b42a9bc9a73ce6a0d5`.
Nội dung kiến trúc dựa trên file workspace đã đọc, không chỉ tên package hoặc comment cũ.

## 1. Đầu ra và căn cứ

- Đủ mục 8.1–8.6 theo [mục lục](../../00_MUC_LUC_CHINH_THUC.md), có note phân công trước từng mục.
- Ba sơ đồ Mermaid và sáu bảng về thành phần, dữ liệu, thread, trách nhiệm và nhóm yêu cầu.
- [Instruction, mục 8.8](../../../phancong/Instruction.md) yêu cầu sơ đồ và giải thích client/server,
  service, database, network layer và processing components. Chương ghi rõ các service nội bộ cùng JVM,
  chưa có database gameplay; không thêm thành phần chỉ để đủ tên trong danh sách gợi ý.
- Dùng các mã FR/NFR ở [chương 6](../../chapters/06_DINH_NGHIA_BAI_TOAN.md).
- Không thêm nguồn ngoài hoặc thay số References. Sơ đồ do nhóm vẽ từ code, không phải hình sao chép.

## 2. Sơ đồ gốc

| Hình | File gốc | Ý nghĩa |
|---|---|---|
| 8.1 | [08_01_tong_the.mmd](../../figures/architecture/08_01_tong_the.mmd) | Ranh giới tiến trình và các thành phần chính |
| 8.2 | [08_02_thread_va_queue.mmd](../../figures/architecture/08_02_thread_va_queue.mmd) | Handoff qua command/outbound/writer queue đến UI |
| 8.3 | [08_03_luong_movement.mmd](../../figures/architecture/08_03_luong_movement.mmd) | Chuỗi input, tick, snapshot và biểu diễn client |

Nội dung ba code block trong chương phải khớp file `.mmd` tương ứng.
Hình là sơ đồ logic, không đo số thread/timing tại một lần chạy cụ thể.
Mũi tên trong hình 8.1 có cả gọi hàm và trao đổi dữ liệu, được chú thích ngay dưới hình.
Hình 8.2 mô tả đường lobby mặc định, không thay thế các API typed-listener/pull-queue tùy chọn.

Môi trường lượt này không tìm được `mmdc`, Node hoặc Graphviz `dot` trên PATH.
Đã rà cấu trúc Mermaid và đồng bộ nội dung, **chưa chạy renderer Mermaid để kiểm tra hình raster/vector**.
Markdown có thể hiển thị bằng môi trường hỗ trợ Mermaid; khi ghép DOCX ở nhiệm vụ 18 phải chuyển sơ đồ thành hình,
kiểm tra chữ/kích thước/ngắt trang và giữ caption. Không đưa code block Mermaid vào Word như thể đó là hình đã xuất.

## 3. Các điểm kiến trúc đã đối chiếu

Các đường dẫn Java tương đối với `src/main/java/com/bombit/`.

| Nội dung | Nguồn code | Kết luận dùng trong chương |
|---|---|---|
| Bootstrap | `server/app/ServerApplication.java`, `client/app/ClientApplication.java` | Mặc định lobby; demo/headless là nhánh khác |
| Composition server | `server/app/LobbyGameServer.java` | Điều phối room/runtime, context, pump, kết quả và callback lifecycle |
| Transport/reader | `server/network/Server.java`, `ClientHandler.java`, `dispatch/MessageRouter.java` | Reader pool; router gọi handler đồng bộ, không có dispatcher worker độc lập |
| Writer/cleanup | `server/network/SessionWriter.java`, `ConnectionManager.java` | Producer encode rồi enqueue; thread writer ghi socket; callback lỗi qua cleanup executor |
| Session/room | `server/session/SessionManager.java`, `server/room/RoomManager.java`, `server/integration/RoomCleanupSink.java` | Hạ tầng có API/metadata legacy nhưng lobby hiện hủy trận và bỏ ghế khi disconnect |
| Runtime factory | `server/game/runtime/GameRuntimeManager.java`, `GameRuntime.java` | Map/state/extension riêng; lobby inject gameplay đầy đủ; API không trả GameState cho network |
| Game loop | `server/game/core/GameLoop.java` | Owner state, FIFO, movement, extension, builder và queue snapshot; lịch tick không có accumulator catch-up đầy đủ |
| Delta handoff | `server/game/movement/StateDeltaBuilder.java`, `GameStateUpdate.java` | Commit sau enqueue; latest có thể là delta; notices là handoff nội bộ |
| Gameplay | `server/game/runtime/GameplayExtension.java`, `MatchGameplayExtension.java` và các adapter | Hook trên game thread; nổ/damage trước item và kết quả; không dùng scheduler riêng sửa world |
| Hai GameEventSink | `server/game/event/GameEventSink.java`, `server/integration/GameEventSink.java` | Domain publish khác callback session lifecycle |
| Owner kết nối client | `client/app/DemoClientConnection.java`, `client/lobby/LobbyWindow.java` | Tên Demo nhưng dùng ở lobby mặc định; permanent listener trước CONNECT, dispatch tuần tự, subscribe=false |
| Client transport | `client/network/ClientNetwork.java` | Listener trên reader; send có khóa và có thể chặn; pull queue bị tắt trong owner mặc định |
| Replica và đồng bộ client | `client/game/movement/MovementClientController.java` và controllers | State thuộc UI executor; worker gửi riêng; resync/respawn xử lý theo context |
| Render và kết quả | `client/game/movement/MovementGameWindow.java`, `client/game/bomb/BombScene.java`, `client/lobby/LobbyWindow.java` | Local prediction, remote interpolation; visuals từ snapshot, notices không replay world effect; đóng lượt giữ TCP |

Lưu ý đọc đường dẫn ở bảng: `dispatch`, `room`, `session` cùng dưới `server/`; tên rút gọn đi cùng file đầu của nhóm.
Các link code trong chương được kiểm tra tồn tại. Hash các file Java được dẫn trực tiếp trong chương nằm ở
[source-links.sha256.json](source-links.sha256.json); đây là kiểm kê đường dẫn có link, không phải toàn bộ dependency của kiến trúc.

## 4. Giới hạn kết luận và kiểm tra

- State cách ly theo room không đồng nghĩa mọi tài nguyên độc lập: CPU/pool/lobby locks vẫn dùng chung.
- `createUpdate()` không bảo đảm full và không thay outbound FIFO. Commit baseline chưa phải receipt ACK của client.
- Client tái sử dụng model/movement và codec trong package `server.game`; không nhận là đã có thư viện common tách hoàn toàn.
- Queue writer chứa tối đa 256 frame **chờ** theo dung lượng queue trong code; byte budget còn tính frame đang ghi.
  Không lấy con số này làm giới hạn số người dùng hoặc kết quả benchmark.
- Đóng window, controller, connection và server có owner/phạm vi khác nhau; shutdown không được mô tả thành một lệnh dispose duy nhất.
- Có thiết kế cleanup không chứng minh mọi race đã hết; lỗi process smoke và khoảng trống GUI/LAN/soak từ nhiệm vụ 1 vẫn được giữ nguyên.

Kết quả kiểm tra tài liệu: [validation.txt](validation.txt).
Không sửa source/test hoặc chạy lại game test trong nhiệm vụ viết kiến trúc này.

**Tiếp theo:** nhiệm vụ 6 viết mục 9 — Thiết kế giao tiếp mạng, đi sâu schema, framing, scope, sequence và lỗi;
không lặp lại toàn bộ sơ đồ thành phần của mục 8.
