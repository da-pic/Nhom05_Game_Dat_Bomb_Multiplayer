# Evidence biên tập Setup/Results — nhiệm vụ 7

Ngày 27/10/2026, Asia/Saigon. Không chạy lại test, không tạo phép đo mới; tổng hợp bằng chứng thực chạy đã lưu.

- `before/`, `after/`: hai chương 11–12 trước/sau cập nhật.
- `before-hashes.json`: mốc báo cáo/hình sau nhiệm vụ 6; chỉ chương 11–12 được đổi trong danh sách này.
- `chapter-changes.patch`: thay đổi nội dung; phần 12.5/12.6 được kiểm tra giữ nguyên văn.
- `verified-results.json`: số liệu được tính/đối chiếu từ XML/CSV gốc, không thay thế raw data.
- `revision-manifest.json`: hash/chapter, caption/link/citation và phạm vi bảo toàn.
- `checksums.sha256.json`: checksum bộ evidence, không gồm chính file checksum.

Nguồn số liệu mới: [lượt kiểm thử recovery nhiệm vụ 3](../recovery-report-task03-20261027-200413/README.md).
Giữ cả full/smoke sandbox thất bại và lượt ngoài sandbox đạt; chưa kết luận chính xác nguyên nhân policy môi trường.
Snapshot/source/checksum gốc vẫn giữ nguyên. Biên tập không làm tăng số lượt test hoặc benchmark.

Hồ sơ: [07_CAP_NHAT_THUC_NGHIEM_VA_KET_QUA.md](../../session-recovery/07_CAP_NHAT_THUC_NGHIEM_VA_KET_QUA.md).
Công cụ kiểm tra: [audit_recovery_setup_results.py](../../experiments/audit_recovery_setup_results.py).
DOCX/PDF và manifest xuất bản cũ chưa chứa sửa chương lần này; bước ghép/xuất sẽ thực hiện sau.
