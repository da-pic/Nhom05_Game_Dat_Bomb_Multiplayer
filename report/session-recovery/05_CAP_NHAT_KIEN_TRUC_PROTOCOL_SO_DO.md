# Nhiệm vụ 5 — Cập nhật kiến trúc, protocol và sơ đồ reconnect

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã sửa trực tiếp [phần 8](../chapters/08_KIEN_TRUC_HE_THONG.md)
và [phần 9](../chapters/09_THIET_KE_GIAO_TIEP_MANG.md), đồng bộ với phần 6–7 đã cập nhật.
Đây là biên tập tài liệu từ code và evidence hiện có, không sửa production/test hoặc chạy thêm kiểm thử game.

## 1. Phần 8 — Kiến trúc hệ thống

- Sửa sơ đồ tổng thể để có recovery watchdog/control worker phía client và RECONNECT trước router phía server.
- Cập nhật trách nhiệm SessionManager/Session, ClientHandler/ConnectionManager, callback lobby và snapshot pump.
- Làm rõ session tạm khi accept, handoff writer/socket về identity cũ, ticket expiry, captured socket và callback ngoài khoá session.
- Cập nhật command lifecycle/frozen trong runtime; giữ game thread làm owner world và gameplay vẫn update.
- Mô tả giữ controller/context, epoch và input generation; phân biệt gate enqueue full phía server với gate apply full phía client.
- Sửa thread/queue, lỗi/cleanup, mapping FR15; thêm mục **8.7**, **Bảng 8.7** về owner và **Hình 8.4** về state machine client.

## 2. Phần 9 — Giao tiếp mạng

- Bổ sung RECONNECT `0x0043` vào bảng control và schema thực tế: playerId UUID + reconnectToken UUID, không match envelope/protocolVersion riêng.
- Giải thích kiểm tra protocolVersion trong ACK, quyền claim lại dưới khoá và nhánh xử lý trước MessageRouter.
- Bỏ kết luận cũ “router chưa đăng ký RECONNECT nên chưa có resume”. Giữ đúng NETWORK_LOST chỉ là mã khai báo trong đường khảo sát và PLAYER_DISCONNECTED ở nhánh hạ tầng khác.
- Làm rõ metadata cùng context, full barrier, full mới→delta, sequence/request counter giữ qua recovery, không replay input/event lịch sử.
- Thêm mục **9.4.5** về full gate; cập nhật bảng timeout/lỗi, queue lifecycle đầy, token sai, admission expiry, match đã kết thúc và ERROR best effort.
- Thêm **Hình 9.5** thành công và **Hình 9.6** từ chối/hết grace/GAME_OVER; sửa mô tả nhánh disconnect cạnh Hình 9.4 để soft disconnect không bị hiểu là ABORT tức thời.

## 3. Năm sơ đồ đã đồng bộ và xuất ảnh

| Hình | Source Mermaid | PNG xem nhanh | Trạng thái |
|---|---|---|---|
| 8.1 | [Tổng thể](../figures/architecture/08_01_tong_the.mmd) | [PNG](../figures/rendered/08_01_tong_the.png) | Cập nhật |
| 8.2 | [Thread và queue](../figures/architecture/08_02_thread_va_queue.mmd) | [PNG hai panel](../figures/rendered/08_02_thread_va_queue.png) | Cập nhật; có bản continuous |
| 8.4 | [State machine client](../figures/architecture/08_04_trang_thai_recovery.mmd) | [PNG](../figures/rendered/08_04_trang_thai_recovery.png) | Mới |
| 9.5 | [Reconnect full→delta](../figures/network/09_05_reconnect_full_delta.mmd) | [PNG](../figures/rendered/09_05_reconnect_full_delta.png) | Mới |
| 9.6 | [Từ chối và hết hạn](../figures/network/09_06_reconnect_tu_choi_va_het_han.mmd) | [PNG](../figures/rendered/09_06_reconnect_tu_choi_va_het_han.png) | Mới |

Mỗi hình có SVG cùng tên ở thư mục rendered. Mermaid trong chương và file .mmd đã được kiểm tra trùng nội dung.
Renderer dùng Mermaid/Chrome headless cục bộ đã có sẵn; không gửi nội dung báo cáo lên dịch vụ bên ngoài.
Đã kiểm tra trực quan năm PNG; sửa CSS xuất ảnh state machine để tránh max-width làm ảnh có khoảng trắng dư.
Các sequence dài cần rà kích thước chữ/phân trang khi ghép DOCX ở nhiệm vụ 10; SVG là bản vector để bố trí lại khi cần.

## 4. Những điểm đã đối chiếu kỹ

| Điểm dễ mô tả sai | Nội dung đã sửa đúng |
|---|---|
| ACK bằng hoàn tất recovery | ACK chỉ xác nhận phiên; metadata và full apply mới cho phép mở input |
| Gửi full nghĩa client đã nhận | Enqueue/initialized ở server khác apply/lastAppliedFullTick ở client; không có receipt ACK-full |
| Token đúng luôn được vào lại | Còn phụ thuộc claim/deadline/ownership/active match; callback có thể từ chối sau enqueue ACK |
| Mất mạng luôn có message báo trước | EOF/I/O/heartbeat có thể là bằng chứng duy nhất; ERROR/thông báo cuối không bảo đảm đến |
| Hết 15 s là full chắc chắn tới client | 15 s là deadline admission từ server xử lý disconnect; client có budget/timeout riêng |
| Full sau resume tạo match mới | Giữ room/match/roster/controller; không CREATE/JOIN/START lại |
| Grace bảo vệ khỏi gameplay | Chỉ freeze điều khiển; damage/respawn/item/timer/GAME_OVER vẫn chạy |
| Recovery thay mọi lần resync | RECONNECT phục hồi quyền phiên; REQUEST_FULL_STATE phục hồi baseline của phiên được tiếp nhận |
| CONNECTED luôn có gameplay | Enum này cũng dùng sau ACK ban đầu hoặc GAME_OVER; readiness còn cần context/controller/replica |

Nguồn xác minh: [nhiệm vụ 2](02_XAC_MINH_THIET_KE_VA_NGUON.md), [kết quả nhiệm vụ 3](03_KET_QUA_KIEM_THU_THUC_TE.md),
source inventory 219 Java file của lượt full 171/171 ngoài sandbox. Không suy ra GUI/LAN/Wi-Fi/soak hoặc SLA đã được nghiệm thu.

## 5. Bảo toàn và việc tiếp theo

Đã lưu trước/sau chương và hình, diff, checksum và manifest kiểm tra tại [evidence nhiệm vụ 5](../evidence/recovery-report-task05-2026-10-27/README.md).
Giữ nguyên phần 6–7 vừa sửa, 15 chương còn lại, References canonical, report manifest xuất bản cũ, DOCX/PDF và source Java.
Các ảnh 8.1/8.2 hiện là bản mới; bản ảnh cũ và source trước sửa được lưu trong evidence nhiệm vụ này.
Manifest/hình của lần xuất task18 giữ như lịch sử, không giả rằng DOCX/PDF cũ đã chứa sơ đồ mới.

**Tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 6: Sửa phần Implementation — mục 10 — theo Session Recovery đã xác minh.”
Các phần còn lại và file xuất cuối sẽ được sửa theo thứ tự đã chia; toàn bộ báo cáo chưa đồng bộ hoàn toàn ở bước này.
