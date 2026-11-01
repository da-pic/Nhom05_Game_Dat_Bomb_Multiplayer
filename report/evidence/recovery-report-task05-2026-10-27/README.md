# Evidence cập nhật kiến trúc/protocol/sơ đồ — nhiệm vụ 5

Ngày 27/10/2026, Asia/Saigon. Biên tập phần 8–9 theo code và kết quả kiểm thử đã có; không chạy thêm test game.

- `before/` và `before-hashes.json`: snapshot/hash chương, bản xuất và hình trước sửa; phần 6–7 tại mốc này đã là bản nhiệm vụ 4.
- `after/`: snapshot phần 8–9, năm source Mermaid và SVG/PNG mới/cập nhật; có ảnh continuous cho Hình 8.2 ngoài bản hai panel.
- `chapter-and-diagram-changes.patch`: diff chương và source hình đã có; source hình mới nằm trong after/.
- `diagram-manifest.json`: năm hình xuất bằng Mermaid/Chrome cục bộ, kích thước/viewBox và đường dẫn output.
- `render-run.log`, `mermaid-browser.log`: log xuất hình. Không upload nội dung báo cáo lên Internet.
- `revision-manifest.json`: hash chương/hình hiện hành, caption, mapping 10 block Mermaid tới file .mmd và phạm vi bảo toàn.
- `checksums.sha256.json`: checksum bộ evidence, ngoại trừ chính file checksum.
- Hai script render/audit được lưu cùng để đối chiếu cách tạo kết quả.

Đã render thành công và xem trực quan năm ảnh. Hình 8.1/8.2 được cập nhật; Hình 8.4/9.5/9.6 mới.
Các sơ đồ không đổi và hình trong DOCX/PDF xuất trước đó được giữ theo lịch sử; bản xuất cuối chưa được dựng lại.
Sequence dài cần rà kích thước chữ/phân trang trong nhiệm vụ ghép/xuất.

Nguồn thiết kế: [nhiệm vụ 2](../../session-recovery/02_XAC_MINH_THIET_KE_VA_NGUON.md).
Bằng chứng thực chạy kế thừa: [171/171 ngoài sandbox, nhiệm vụ 3](../recovery-report-task03-20261027-200413/README.md).
Hồ sơ biên tập: [nhiệm vụ 5](../../session-recovery/05_CAP_NHAT_KIEN_TRUC_PROTOCOL_SO_DO.md).

219 source Java, 17 chương khác (gồm 6–7 đã sửa), References canonical, report manifest lịch sử và 4 bản xuất cuối giữ nguyên.
Không thay source, commit/push hoặc ghi đè bằng chứng các nhiệm vụ trước để hợp với chương mới.
