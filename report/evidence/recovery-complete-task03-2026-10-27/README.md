# Kiểm thử recovery hoàn chỉnh — nhiệm vụ kỹ thuật 3

Ngày: **27/10/2026**, Asia/Saigon. Commit nền `492c03127f15a25f4fc685fd004eafe424d53f9f` cộng các thay đổi trong working tree của ba nhiệm vụ kỹ thuật; chưa tự commit/push. [run-manifest.json](run-manifest.json) và [source-inventory.json](source-inventory.json) ghi trạng thái và hash để phân biệt với các bộ test cũ.

## Kết quả

- Full suite: **171/171 test, 44 class**, 0 failure/error/skipped; `recovery-complete-full-tests.log` ghi BUILD SUCCESS, khoảng **1 phút 12 giây**.
- Nhóm sau sửa lỗi: **22/22** trong `recovery-complete-focused-3.log` (8 integration + 10 SessionRecoveryTest + 3 SessionManagerTest + 1 SessionFaultTest).
- Check TV2 và NetworkTest main: exit 0, PASS (`recovery-complete-tv2.log`, `recovery-complete-network.log`).
- Tăng 11 testcase so với mốc client 160: 8 case trong lớp integration mới, 3 case biên trong lớp session có sẵn. Không cộng ba lần reconnect trong một case thành ba testcase mới.
- Có TCP grace mặc định 15 giây thực; clock giả chỉ điều khiển gameplay hoặc test biên manager riêng. Không rút ngắn grace TCP để ép chạy nhanh.

## Nội dung đã kiểm chứng

| Nhóm | Bằng chứng |
|---|---|
| Nhiều input/bom, reconnect lặp | 4 bom trước ngắt, ba vòng recovery; thêm được bom 5; duplicate request không tạo lại command; runtime/identity giữ nguyên |
| Full rồi delta | Ba lần equality của replica tại cùng tick, gồm kích thước/map/tileSize/match state, player/ACK, entity, HUD và BombFrame; sau mỗi full ghép được delta, không baseline gap |
| Gameplay offline | Bom nổ, block phá, item sinh; mạng 3→2/respawn 1; timer 30→29; full khôi phục đúng; SPEED_UP nhặt một lần và full sau đó không cộng effect lại |
| Token/handshake | Token sai dạng UUID hợp lệ, identity lạ và thiếu trường bị từ chối; owner hợp lệ vẫn tiếp tục được |
| Hai player offline | Runtime không bị dừng ngay; cả hai trở lại cùng runtime và có thể gửi input |
| GAME_OVER trong grace | TIMEOUT/LAST_ALIVE không bị reconnect làm sống lại; socket/session/timer được dọn; từ chối theo nghiệp vụ không gắn system failure |
| Grace 15 giây | ABORTED, gỡ ghế, chuyển host, WAITING, runtime/worker dừng, token quá hạn bị từ chối |
| Client ứng dụng | Ba vòng auto reconnect giữ controller/context/listener count, tiếp tục sequence và counter đặt bom |
| Cleanup | Mỗi fixture xác nhận accept/runtime/snapshot/transport/executor đã dừng, maps/session/timer/connection không tồn dư |

Chi tiết từng assertion và giới hạn: [SESSION_RECOVERY_VALIDATION.md](../../../docs/SESSION_RECOVERY_VALIDATION.md).

## Các file bằng chứng

- [junit-summary.json](junit-summary.json), [surefire/](surefire/): tổng và 44 XML của lượt full cuối.
- [case-results.csv](case-results.csv), [case-results.json](case-results.json): 8 dòng case integration và 3 dòng clock boundary từ stdout của lượt full; không phải 11 benchmark latency.
- [source/](source/): sáu file trực tiếp thuộc nhiệm vụ này, gồm test mới, test session mở rộng và sửa production cho việc phân loại từ chối.
- [task03-changes.patch](task03-changes.patch): so với snapshot server trước đó, đã được kiểm tra còn nguyên ở nhiệm vụ client; file mới so với nội dung rỗng. Khác với `git diff HEAD`, patch này không lặp lại mọi sửa server từ nhiệm vụ 1.
- [source-inventory.json](source-inventory.json): hash 219 file Java main/test của cây source lúc nghiệm thu; không đồng nghĩa 219 JUnit case.
- [run-manifest.json](run-manifest.json), `checksums.sha256.json`: revision/working tree/hash/log và kiểm tra toàn vẹn.

## Attempt lỗi được giữ

1. `recovery-complete-focused.log`: lỗi compile test do hai package có cùng tên enum Direction/TileType; sửa import model tường minh. Chưa chạy test nên không cộng lượt này vào số testcase.
2. `recovery-complete-focused-2.log`: 18 test, 2 failure ở hai nhánh GAME_OVER vì từ chối hợp lệ bị ghi thành system failure. XML trước sửa trong [attempt-2/](attempt-2/).
3. `recovery-complete-focused-3.log`: sau tách SessionRecoveryRejectedException, 22/22 đạt. Lỗi nội bộ thực vẫn được ghi nhận qua test writer failure/callback fault.
4. `recovery-complete-full-tests.log`: 171/171 đạt sau tăng assertion so sánh toàn bộ replica dimensions/match state và kiểm tra lỗi writer thực vẫn được giữ.

Không sửa timeout assertion hoặc dữ liệu thực nghiệm cũ để làm test đạt. Sửa production chỉ gồm loại exception từ chối có chủ đích và nhánh catch phân loại/rollback; không đổi gameplay, grace hay protocol payload.

## Giới hạn và bảo toàn

Đây là TCP loopback trong một máy, dùng gameplay clock điều khiển được. Chưa nghiệm thu GUI bằng người dùng, Wi-Fi/LAN nhiều máy, tải tối đa hoặc soak; không công bố recovery latency/SLA. Các case đã liệt kê có assertion, không khẳng định mọi lỗi mạng đều được bao phủ.

Hash 14 file của nhiệm vụ client được giữ nguyên; 19 chương và bốn file bản xuất báo cáo cũ được giữ nguyên. Metadata failure của manager chỉ thay đổi cho nhánh từ chối đúng nghiệp vụ; không xoá diagnostic của lỗi thực. Reconnect sau khi match đã chốt không replay lịch sử kết quả cho player offline và không bắt đầu lại trận.

Công cụ tổng hợp: [collect_recovery_validation.py](../../experiments/collect_recovery_validation.py). Nó chỉ đọc log/XML hiện có, không chạy test. Chạy lại sẽ ghi đè bộ tổng hợp theo target/source hiện tại; khi code/run thay đổi nên tạo evidence mới để giữ mốc này.
