# Evidence — cập nhật báo cáo nhiệm vụ 9

Ngày 27/10/2026, Asia/Saigon. Đây là hồ sơ biên tập phần 1–5, 18–19 và hợp nhất tài liệu tham khảo,
không phải lượt đo hay test mới. [Hồ sơ bàn giao](../../session-recovery/09_CAP_NHAT_TONG_QUAN_TAI_LIEU_PHU_LUC.md).

## Nội dung

- `before/`: các chương/danh mục nguồn trước sửa, lưu đủ đầu vào chuẩn hóa citation; đường dẫn giữ theo root repository.
- `before-hashes.json`: hash bảo vệ kế thừa sau nhiệm vụ 8.
- `after/`: bảy chương được sửa và hai file danh mục nguồn hiện hành sau khi audit đạt.
- `chapter-changes.patch`: diff bảy chương và hai file danh mục.
- `reference-map.json`: 19 stable ID/số hiện hành, occurrence và dấu vết hợp nhất năm nguồn mới.
- `revision-manifest.json`: kết quả kiểm tra biên tập, link/hash và phạm vi không thay đổi.
- `checksums.sha256.json`: hash các file trong bộ hồ sơ sau khi hoàn tất.
- Bản sao hai script chuẩn hóa nguồn và audit để truy vết cách tạo kết quả.

Nguồn mới kiểm tra qua tài liệu chính thức:
[Socket.IO recovery](https://socket.io/docs/v4/connection-state-recovery/),
[Socket.IO delivery](https://socket.io/docs/v4/delivery-guarantees/),
[OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html),
[ScheduledExecutorService SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html),
[ScheduledThreadPoolExecutor SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledThreadPoolExecutor.html).
Ngày truy cập và phiên bản được giữ riêng trong catalogue, không bịa ngày xuất bản.

## Bằng chứng kiểm thử được dẫn lại

Lượt [A5 recovery](../recovery-report-task03-20261027-200413/run-manifest.json) đạt 171/171 test,
44 class ngoài sandbox, với TV2 check và NetworkTest PASS. Raw XML/log/CSV và 219 source snapshot được giữ nguyên;
audit nhiệm vụ này chỉ xác nhận hash/summary. Các attempt smoke lỗi được giữ ở hồ sơ nhiệm vụ 3.
Benchmark delta/TCP baseline không được chạy lại hoặc gán kết quả cho recovery.

Phần 6–17, hình, manifest xuất bản và DOCX/PDF cũ được bảo vệ bằng hash.
Nhiệm vụ cập nhật 10 mới ghép và xuất bản báo cáo tương ứng với nội dung đã sửa.
