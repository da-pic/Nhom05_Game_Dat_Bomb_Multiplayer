# Chỉnh lại nội dung theo yêu cầu riêng của từng mục

Ngày 28/10/2026. Đầu ra: [DOCX](../../revisions/CHINH_NOI_DUNG_BAO_CAO_THEO_PHAN_CONG_2026-10-28.docx)
và [Markdown](../../revisions/CHINH_NOI_DUNG_BAO_CAO_THEO_PHAN_CONG_2026-10-28.md).
Nội dung để copy/paste vào các mục thuộc Chinh, không có phân công hoặc hướng dẫn ghép bên trong file.

Lần sửa này bỏ chính sách rút ngắn đồng loạt của bản trước. Yêu cầu rút được áp dụng riêng cho lý thuyết 5.2–5.3,
luồng 7.1, mã giả tick 7.3, trách nhiệm thành phần chương 8 và module triển khai chương 10.
7.4 chuyển thông số về 10, phần recovery về 7.8; 7.5 chuyển phương pháp đo về 11 thay vì xóa mất thông tin.
Các phần delta, thực nghiệm/kết quả, thảo luận/đóng góp và hạn chế/hướng phát triển giữ chi tiết cần thiết theo vai trò.

Đã khôi phục bảng diff/tombstone, ví dụ baseline, thuật toán enqueue/commit/apply và lập luận correctness;
giữ toàn bộ bảy hàng số liệu full–delta, số packet/skip, hai biểu đồ và giới hạn harness;
đưa lại các giải thích ACK, FIFO/backlog, respawn, correction, chi phí CPU/bộ nhớ và phép đo cần có.
Triển khai có đủ 18 tiểu mục 10.3.1–10.5.7, khoảng 2.825 đơn vị từ phân cách bằng khoảng trắng,
so với gần 3.992 trong bản chương nguồn và 846 trong bản bị rút quá mức trước đó.

`editorial-policy.json` ghi cách xử lý từng mục; `section-comparison.json` ghi độ dài trước/sau để kiểm tra
các phần cần chi tiết không bị biến thành bản tóm tắt. Các file này chỉ ở hồ sơ kiểm tra, không chèn vào DOCX.
`evidence-verification.json` xác minh raw/CSV/XML và source inventory; không chạy Java test hoặc benchmark mới.
`revision-manifest.json`/`checksums.sha256.json` ghi hash file và phạm vi bảo toàn.

Kiểm tra DOCX ZIP/XML, số hình/bảng, mục nội dung, citation/URL, liên kết cục bộ và không có ghi chú phân công;
các chương nguồn, source game và bản DOCX/PDF đầy đủ 167 trang trước đó được giữ nguyên.
