# Evidence — xuất lại báo cáo sau Session Recovery

Ngày 27/10/2026, Asia/Saigon. [Hồ sơ bàn giao](../../session-recovery/10_GHEP_VA_XUAT_BAO_CAO_CUOI.md).
Đây là đợt ghép/kiểm tra tài liệu, không có phép đo game hoặc test Java mới.

## Đầu vào và công cụ

- `before/`: bản xuất DOCX/PDF/Markdown/checklist và các index/manifest trước đợt xuất lại.
- `protected-hashes.json`: bảo vệ source, chương, danh mục tham khảo, script game và hình gốc.
- `input-review.json`: đủ 19 chương, 19 nguồn, 15 caption hình, 86 caption bảng và 394 liên kết cục bộ.
- `assembly-manifest.json`: caption, thứ tự sơ đồ, thay đổi câu ghi trạng thái xuất bản trong bản ghép.
- `layout-assets/`: ba phần dàn trang cho mỗi sơ đồ recovery dài; không thay ảnh/SVG gốc.
- `word-pagination.json`: số trang, mục lục/danh mục đã cập nhật, số bảng/ảnh và vị trí đầu chương do Word ghi.
- `document-review.json`: kiểm tra cấu trúc DOCX/PDF, bookmark/caption, biên trang và ảnh xem trước.
- `preview-final/` và `final-contact-sheet-*.png`: trang mẫu của bản cuối để kiểm tra trực quan.
- `layout-attempt01-review.json`, `preview/` và `page-contact-sheet-*.png`: lượt review ban đầu phát hiện trang trắng 120; đã sửa ngắt chương và chạy lại. Không dùng ảnh trung gian làm preview bản cuối.
- `final-artifacts.json`, `checksums.sha256.json`: revision, kết quả kiểm tra bảo toàn và hash bộ file bàn giao.

Script xuất cũ giữ nguyên. Bản sao các script mới được lưu cùng bộ hồ sơ sau khi kiểm tra hoàn tất.
Word chạy ẩn; sandbox không khởi tạo được COM (80070520) nên bước pagination/export chạy ngoài sandbox
theo quyền được cấp. Không cài thêm dependency hoặc dùng dịch vụ chuyển đổi tài liệu bên ngoài.
Lần xuất sau sửa ngắt trang đã hoàn tất DOCX/PDF nhưng bước lấy tiêu đề từ bookmark rỗng trả về null;
đã lấy tiêu đề từ manifest nguồn và chạy metadata-only để đối chiếu số trang. Kiểm tra cuối dùng hash đúng bản đã xuất.

## Phạm vi xác minh

Kiểm tra đủ nội dung/caption/citation và trường Word, mở PDF kiểm tra số trang/biên,
xem các trang mẫu. Các mục GUI/LAN/Compilatio và thông tin bìa còn thiếu được giữ ở checklist.
Hồ sơ trước recovery có 131 trang/12 hình/76 bảng/14 nguồn; đây là revision khác, được sao lưu trước thay thế bản hiện hành.
Kết quả 171/171 recovery và số đo delta/TCP baseline được dẫn lại đúng nguồn, không tạo ra một lần đo mới.
