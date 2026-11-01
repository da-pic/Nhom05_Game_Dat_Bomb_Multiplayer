# Khảo sát báo cáo sau các bản sửa Session Recovery

Ngày 27/10/2026, Asia/Saigon. Chỉ đọc code và bằng chứng đã có; không chạy lại test.

- `survey-manifest.json`: HEAD/nhánh/working tree, hash các chương và bản xuất trước khảo sát.
- `source-inventory.json`: sao lưu inventory của lượt test cuối; đã đối chiếu toàn bộ 219 file Java hiện tại, không sai khác.
- `junit-summary.json`: sao lưu kết quả 171/171 của lượt test kỹ thuật 3, không phải lượt chạy mới.
- `chapter-candidates.json`: vị trí cần review, không coi mọi dòng là lỗi.
- `tracked-source-vs-head.patch`: thay đổi tracked trong src so với HEAD; file mới được nhận diện qua Git status và inventory, không nằm trong patch này.
- `historical-*`: bản khảo sát trước sửa kỹ thuật được bảo tồn, không còn là hiện trạng mới nhất.

Bằng chứng gốc: [recovery-complete-task03](../recovery-complete-task03-2026-10-27/README.md).
Hồ sơ hiện hành: [nhiệm vụ 1](../../session-recovery/01_KHAO_SAT_VA_DANH_SACH_CAN_SUA.md).
Không sửa log/XML gốc, code, 19 chương, bản DOCX/PDF hay trạng thái Git.
