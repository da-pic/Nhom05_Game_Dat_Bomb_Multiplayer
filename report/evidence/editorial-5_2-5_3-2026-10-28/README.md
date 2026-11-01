# Rút gọn mục 5.2–5.3 — phần Chinh

Ngày 28/10/2026. Theo yêu cầu biên tập và đoạn văn được gửi kèm, đã sửa trực tiếp
[chương 5](../../chapters/05_CO_SO_LY_THUYET_VA_CONG_TRINH_LIEN_QUAN.md) và cung cấp
[bản riêng](../../revisions/2026-10-28_RUT_GON_5_2_5_3.md) để đưa vào tài liệu nhóm.

- Rút phần nguyên lý game loop/concurrency, full–delta và hỗ trợ phía client; bỏ các chi tiết lớp/API, replay từng bước và diễn giải trùng với chương 7/10.
- Giữ nguyên các tiêu đề 5.2.1–5.2.3, 5.3.1–5.3.4, nội dung Bảng 5.1 và số trích dẫn.
- Độ dài hai mục giảm từ 1.625 xuống 766 đơn vị phân cách bằng khoảng trắng, tương đương 52,9%; đây là phép đếm văn bản, không phải số từ ngôn ngữ học tiếng Việt.
- Kiểm tra phần trước 5.2 và từ ghi chú phân công 5.4 trở đi giữ nguyên byte; các chương khác và file xuất cuối giữ nguyên hash.
- Kiểm tra thứ tự lần xuất hiện của nguồn vẫn là 1–19; URL các citation trong phần sửa khớp catalogue.

`before-chapter05.md`, `after-chapter05.md`, `changes.patch` và `revision.json` lưu nội dung và kết quả đối chiếu.
`before-report-manifest.json` giữ manifest bản xuất trước khi đánh dấu có chỉnh sửa đang chờ ghép.
Không chạy test hoặc sửa code, không ghi đè DOCX/PDF đã xuất; manifest hiện hành đánh dấu cần xuất lại sau khi chốt biên tập.
