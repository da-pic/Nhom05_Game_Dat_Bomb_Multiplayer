# Kiểm thử sửa server Session Recovery — nhiệm vụ kỹ thuật 1

Ngày: **27/10/2026**, Asia/Saigon. Source nền `492c03127f15a25f4fc685fd004eafe424d53f9f` cộng working-tree changes, chưa commit. Xem [run-manifest.json](run-manifest.json) để biết file/hash chính xác, [tracked-changes.patch](tracked-changes.patch) và bản sao file mới/thay đổi trong [source/](source/).

## Kết quả

- Full JUnit: **147/147 đạt, 40 class, 0 failure/error/skipped**, BUILD SUCCESS; Maven 47,001 s. Có 12 testcase mới so với 135 test trước sửa: 7 SessionRecoveryTest, 1 RecoveryWriterTest, 4 LobbyLifecycleTest.
- Check TV2 độc lập: exit 0, các nhóm PASS, giữ kiểm tra delta/FIFO/runtime/movement.
- NetworkTest main: exit 0, PASS codec/framing/validation/router/metrics/TCP loopback.
- `git diff --check` không có lỗi whitespace (Git có thể cảnh báo chuẩn hoá LF/CRLF theo cấu hình Windows).
- Không chạy GUI/LAN/soak hoặc benchmark recovery latency. Không dùng các lượt test này để cập nhật kết luận trong báo cáo cũ.

## Các attempt được giữ

| Log | Kết quả và điều rút ra |
|---|---|
| `server-recovery-focused.log` | 19 test, 1 failure: test auto client gửi MOVE sau ACK trước full; lộ thiếu readiness của client hiện tại |
| `server-recovery-focused-2.log` | 21 test, 1 error: nhánh từ chối token đóng socket trước khi gửi ERROR; khôi phục preflight nhưng giữ kiểm tra nguyên tử trong reconnect |
| `server-recovery-focused-3.log` | 22 test, 1 failure: assertion test chỉ tìm ACK trong danh sách delta, bỏ sót full snapshot; sửa predicate đọc cả hai loại |
| `server-recovery-focused-4.log` | 22/22 đạt; test TCP riêng xác nhận NOT_READY trước full và input được ACK sau full |
| `server-recovery-full-tests.log` | Sau bổ sung test shutdown/heartbeat/queue unfreeze: 147/147 đạt, 40 class |
| `server-recovery-tv2.log` | Check TV2 độc lập PASS |
| `server-recovery-network.log` | NetworkTest main PASS |

Không sửa timeout để ép đạt. Test auto client cũ nay chờ replica tick mới; không khẳng định đã sửa readiness của production client. Phần client/GUI giữ cho nhiệm vụ kỹ thuật 2.

## Phạm vi assertion mới

- Deadline được kiểm tra dù expiry executor chưa chạy; fake clock kiểm tra đúng mốc 15 giây.
- Timer cũ không xoá session vừa resume hoặc cửa sổ grace lần hai; expiry hợp lệ dọn phiên/timer.
- Callback reader/writer cũ không ngắt/hard-drop socket thay thế.
- Chỉ một handoff đang thực hiện; request chồng nhau bị từ chối, socket thua được đóng.
- Writer setup thất bại hoặc shutdown giữa handoff không làm sống lại session/giữ socket rò rỉ.
- Writer thay thế vẫn truyền packet TCP; release theo socket cũ không xoá writer mới.
- Token sai không làm mất owner; takeover TCP còn sống giữ identity/match và gửi full thực.
- Queue đầy khi freeze hoặc unfreeze kết thúc lượt ABORTED có cleanup rõ ràng.
- Metadata trước full; input trước full nhận NOT_READY, sau full được xử lý. Server chỉ biết enqueue full thành công, không có ACK mới xác nhận client áp dụng snapshot.

Hướng dẫn và note kỹ thuật: [SESSION_RECOVERY_SERVER.md](../../../docs/SESSION_RECOVERY_SERVER.md). XML của full suite ở [surefire/](surefire/), danh sách case trong [junit-summary.json](junit-summary.json).

Giữ nguyên 19 chương báo cáo và cả bốn file bản xuất cũ theo hash task18. Giữ nguyên gameplay damage/timer và chính sách hết grace có thể ABORTED. Các giới hạn FIFO/backlog, client readiness/retry, token không rotate và GUI/LAN chưa nghiệm thu được ghi trong tài liệu kỹ thuật.
