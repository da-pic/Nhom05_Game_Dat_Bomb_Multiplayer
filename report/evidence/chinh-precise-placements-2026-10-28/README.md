# Kiểm tra vị trí và nội dung thay thế — phần Chinh

Ngày bàn giao: 28/10/2026.

- [DOCX](../../revisions/CHINH_VI_TRI_VA_NOI_DUNG_THAY_THE_2026-10-28.docx) chứa 40 khối thao tác và 34 khối nội dung để dán. Chỉ dẫn vị trí/phạm vi được tách khỏi văn bản báo cáo bằng kiểu nền riêng và mốc bắt đầu/kết thúc.
- [Markdown](../../revisions/CHINH_VI_TRI_VA_NOI_DUNG_THAY_THE_2026-10-28.md) là nguồn tương ứng. Các bảng thay riêng dòng được xuất vào DOCX không kèm hàng header mới.
- [Kế hoạch thao tác](placement-plan.json) ghi vị trí, nội dung cũ hoặc mốc chèn chính xác cho từng khối. [Manifest](revision-manifest.json) ghi số lượng và hash sản phẩm.
- [Kiểm tra áp dụng trong bộ nhớ](virtual-application.json) xác nhận các mốc nguồn không bị thiếu/trùng; các phần chung hoặc của thành viên khác được giữ. Không ghi đè chương nguồn. Riêng 8.6 chỉ thêm một đoạn trong 8.6.1 sau Bảng 8.5; giữ Hình 8.2, Bảng 8.5 và 8.6.2–8.6.5.
- [Đối chiếu bằng chứng](evidence-verification.json) xác minh checksum 53 tệp baseline chức năng, 92 tệp thực nghiệm delta và 280 tệp kiểm thử recovery; đối chiếu 219 tệp Java, kết quả từng lớp JUnit, 35 scenario-run delta, 18.000 tick equality và marker ba chu kỳ recovery.

DOCX được kiểm tra cấu trúc ZIP/XML, đủ khối nội dung, hai hình của chương 7 và bốn bảng thay riêng dòng đúng số hàng. Các bảng số liệu và hai biểu đồ kết quả full–delta ở chương 12 được chỉ rõ giữ nguyên, không chép lặp vào tài liệu sửa đổi.

Đây là tài liệu sửa đổi riêng của Chinh, không phải lần xuất lại toàn bộ báo cáo. Không sửa mã Java, không chạy lại test/benchmark và không cập nhật DOCX/PDF tại `report/final/`. Các tệp báo cáo, tài liệu tham khảo và mã nguồn được bảo vệ bằng hash trong quá trình tạo bản này.
