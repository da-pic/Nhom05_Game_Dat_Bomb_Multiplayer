# Evidence cập nhật chương 6–7 — nhiệm vụ 4

Ngày 27/10/2026, Asia/Saigon. Đây là đợt biên tập báo cáo, không phải lượt test mới.

- `before/`, `after/`: snapshot hai chương trước/sau sửa.
- `before-hashes.json`: hash các file được bảo toàn ở mốc trước biên tập; chỉ hai chương 6–7 được phép đổi trong danh sách này.
- `chapter-changes.patch`: diff nội dung chương, không chứa thay đổi production/test.
- `revision-manifest.json`: hash trước/sau, số bảng/hình/thuật toán và kết quả kiểm tra liên kết/citation/FR.
- `checksums.sha256.json`: checksum bộ evidence, không gồm chính file checksum.

219 file Java trùng inventory của [lượt test nhiệm vụ 3](../recovery-report-task03-20261027-200413/README.md).
17 chương khác, 4 file bản xuất cuối, References canonical và report manifest của bản xuất cũ giữ nguyên.
Không đổi trạng thái hay log test lịch sử để hợp với nội dung mới; số liệu 171/171 là từ lượt test mới đã lưu ở nhiệm vụ 3, không phải từ lần biên tập này.

Hồ sơ: [04_CAP_NHAT_PHAN_6_7.md](../../session-recovery/04_CAP_NHAT_PHAN_6_7.md).
Công cụ audit: [audit_recovery_chapters_06_07.py](../../experiments/audit_recovery_chapters_06_07.py).
Audit cố ý từ chối ghi đè manifest đã có; tạo revision mới nếu tiếp tục sửa.

DOCX/PDF và manifest xuất bản cũ chưa chứa chương mới. Các chương tiếp theo sẽ được cập nhật theo thứ tự; nhiệm vụ 10 mới ghép, kiểm tra toàn bài và tái xuất.
