# Nhiệm vụ 6 — Cập nhật Implementation theo Session Recovery thực tế

**Hoàn thành ngày 27/10/2026, Asia/Saigon.** Đã sửa trực tiếp [phần 10 — Triển khai hệ thống](../chapters/10_TRIEN_KHAI_HE_THONG.md).
Đối chiếu source Java hiện tại với inventory của lượt kiểm thử nhiệm vụ 3; không thay code hoặc chạy thêm test game.

## 1. Nội dung đã cập nhật

| Vị trí | Thay đổi triển khai được mô tả |
|---|---|
| 10.1.3 | ServerApplication bật seamless recovery; LobbyWindow bật auto reconnect; tách constructor/profile tổng quát và M1 |
| 10.2.1–10.2.3 | API handler/manager/writer; pending nhận CONNECT/RECONNECT; expectedSocket, releasePreservingSocket và writer thay thế |
| 10.2.4 | SessionState thực tế, monitor session, DisconnectWindow, elapsed deadline, task cancellation và timer cũ |
| 10.2.5–10.2.7 | Soft disconnect giữ runtime; expiry/leave có thể ABORT; heartbeat kiểm tra lại ownership/liveness dưới khoá |
| **10.2.8 mới** | Claim/preflight, provisional session, beforeResume, rollback, expected rejection và suspended/initialized/recoveryFullAfter trong pump |
| 10.3–10.4 | Command freeze/unfreeze đã nối callback; giữ runtime/matchId, request full qua loop và dùng lại snapshot codec |
| 10.5 | Controller/input generation, requireFullState, bỏ pending cũ, reset prediction/interpolation và giữ sequence/counter |
| **10.5.7 mới** | suspendForRecovery, prepareRecoveryOnUi, resumeAfterRecovery, lastAppliedFullTick và readiness thực tế |
| 10.6 | Extension nhận lifecycle, chặn plant mới khi disconnected nhưng bom/damage/item/timer vẫn chạy |
| 10.7 | Overlay trạng thái chờ, khoá Space/input, giữ window; typed state listener, guard owner và khoá nút lobby/chat/End |
| 10.8.3–10.8.4 | RECONNECT trước router, timeout connect overload, candidate socket/cancel, phân biệt disconnect với close |
| 10.8.5 | Recovery object/epoch, attempt/retry/watchdog, ACK/metadata/full apply gate, ERROR, resync/control stale task và finishClose ngoài khoá |
| 10.8.7 | Dẫn lượt mới 171/171 ngoài sandbox; giữ attempt lỗi, giới hạn GUI/LAN và phạm vi hook kiểm thử |

Các bảng 10.1–10.10 giữ số và vị trí logic; không tạo hình hoặc đánh lại số hình ở bước này.
Không sao chép lại toàn bộ schema/mã giả ở phần 7/9: phần 10 tập trung vào class, field, phương thức và ownership cụ thể.

## 2. API/field được đối chiếu với source

| Thành phần | Tên tiêu biểu đã xác minh | Nội dung cần hiểu đúng |
|---|---|---|
| SessionManager | canReconnect, reconnect, discardProvisional, handleHeartbeatTimeout, expire, recovering, DisconnectWindow | Preflight khác claim; callback ngoài khoá; deadline xét lại; lỗi thật khác từ chối nghiệp vụ |
| ConnectionManager/ClientHandler | open, releasePreservingSocket, release; beforeResume | Bỏ session/writer tạm nhưng giữ socket, late cleanup không xoá writer mới |
| LobbyGameServer | onPlayerDisconnected/onPlayerReconnected, suspended, initialized, recoveryFullAfter, pump | Queue nhận lifecycle và enqueue full không tương đương client đã áp full |
| GameLoop/BombGameplayExtension | frozen, processCommand, disconnected | Network không sửa world; freeze không pause gameplay |
| MovementClientController | suspendForRecovery, prepareRecoveryOnUi, resumeAfterRecovery, lastAppliedFullTick, inputGeneration | Giữ controller/plantRequest; bỏ task cũ; gate theo apply |
| Prediction/Input/Interpolation | resetAfterRecovery, refreshGeneration, clear | Giữ sequence; clear phím kể cả recovery giữa hai mẫu; bỏ lịch sử cũ |
| ClientNetwork | connect(host,port,timeoutMillis), connecting, disconnect, close | Resolve/connect ngoài monitor; close được candidate; timeout connect không bao trọn DNS |
| DemoClientConnection | connectionLost, attempt, retry, checkRecoveryTimeouts, beginClose/finishClose, wireEpoch | Watchdog riêng, deadline tổng không reset; ACK/full khác nhau; đóng/join ngoài recoveryLock |
| LobbyWindow/MovementGameWindow | setRecoveryStateListener, updateButtons, setRecoveryStatus, isInputReady | Trạng thái UI không chỉ suy từ chuỗi status; không tái tạo cửa sổ qua handoff |

Một số phương thức/field là private hoặc package-private; đây là mô tả nội bộ implementation, không tuyên bố tất cả là API công khai cho module khác.
`isInputReady` kiểm tra controller/world/match RUNNING; trạng thái sống được prediction/movement và plantBomb kiểm tra riêng.
Đã mô tả đúng thứ tự ClientNetwork đặt TCP_NODELAY rồi xác minh ownership trước khởi động reader/watchdog.

## 3. Bằng chứng và giới hạn

Thiết kế: [nhiệm vụ 2](02_XAC_MINH_THIET_KE_VA_NGUON.md).
Kết quả thực tế kế thừa: [nhiệm vụ 3](03_KET_QUA_KIEM_THU_THUC_TE.md), full ngoài sandbox 171/171, 44 class, TV2/TCP PASS.
Không nhận là lượt kiểm thử mới của nhiệm vụ viết này; không đổi số liệu delta/network/reliability cũ.
GUI đã tích hợp trong code và có test EDT/input/TCP; chưa nghiệm thu người thao tác GUI/LAN/Wi-Fi vật lý hoặc benchmark recovery latency.

Đã bỏ các nhận định cũ trong phần 10 rằng reconnect chỉ là API legacy, thiếu router nên chưa có resume,
hoặc disconnect luôn bỏ ghế ngay. Các API legacy khác vẫn được giữ mô tả nếu đúng source; không thay từ “legacy” hàng loạt.

## 4. Bảo toàn và đầu ra

- Chỉ chương 10 thay đổi trong 19 chương; giữ nguyên phần 6–9 vừa sửa và 14 chương còn lại.
- Giữ nguyên source Java, toàn bộ sơ đồ/ảnh nhiệm vụ 5, References canonical, report manifest của bản xuất cũ và DOCX/PDF.
- Snapshot trước/sau, diff, hash và kiểm tra nằm ở [evidence nhiệm vụ 6](../evidence/recovery-report-task06-2026-10-27/README.md).
- Kiểm tra link, citation, số bảng/heading và tên phương thức/field liên quan; chưa dựng lại báo cáo cuối nên mục lục/DOCX/PDF còn thuộc bản trước cập nhật.

**Tiếp theo:** “Cập nhật báo cáo — nhiệm vụ 7: Sửa phần 11–12 theo môi trường và kết quả kiểm thử Session Recovery thực tế.”
