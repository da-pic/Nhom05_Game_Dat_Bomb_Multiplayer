# Nhiệm vụ 10 — Rà soát, ghép và xuất lại báo cáo

Revision ngày **27/10/2026**, Asia/Saigon. Bản xuất hiện hành tổng hợp đầy đủ phần 1–19 đã cập nhật
trong các nhiệm vụ 4–9, gồm State Delta Compression và Seamless Session Recovery.

## 1. File bàn giao

- [Báo cáo DOCX](../final/NhomXX_BombItMultiplayer_Report.docx): bản có thể chỉnh sửa, đủ 19 phần.
- [Báo cáo PDF](../final/NhomXX_BombItMultiplayer_Report.pdf): bản kiểm tra dàn trang cùng revision.
- [Markdown đã ghép](../final/BAO_CAO_DA_GHEP.md): nội dung đối chiếu, giữ Mermaid và liên kết nguồn của từng chương.
- [Danh sách nhóm cần xác nhận](../final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md): bìa/MSSV, đóng góp, phạm vi kết quả và yêu cầu nộp.
- [Manifest hiện hành](../report-manifest.json): thứ tự/hash chương, số hình/bảng/nguồn, thông tin bản xuất và hash DOCX/PDF.

Tên `NhomXX` chưa thay bằng số nhóm vì chưa có thông tin thật. Không tự điền trường/lớp/MSSV,
chữ ký, tỷ lệ đóng góp hoặc kết quả Compilatio.

## 2. Nội dung và cách ghép

Giữ 19 phần theo Instruction.md mục 8; phần phân công vẫn có trước các nội dung tương ứng.
Danh mục tham khảo có **19 nguồn**, đánh số theo lần xuất hiện: 1–14 giữ nguyên, 15–19 bổ sung cho recovery.
Có **15 hình, 86 bảng đánh số**; hai bảng bìa làm tổng số bảng Word là 88.
DOCX/PDF hiện hành có **167 trang**, đã kiểm tra không có trang nội dung trắng hoặc chữ vượt biên trang.
Mục lục, danh mục hình/bảng và trường số trang được cập nhật bằng Word trước khi xuất PDF.

Tất cả 12 khối Mermaid được đối chiếu với file nguồn và hình hiện hành; thêm ba biểu đồ kết quả thực nghiệm.
Hai sơ đồ reconnect dài (Hình 9.5/9.6) được chia thành ba phần mỗi hình trên trang ngang,
lặp lại tên participant để đọc được khi in. Danh mục vẫn tính mỗi sơ đồ là một hình;
tổng số panel ảnh nhúng là 19. Ảnh/SVG gốc không sửa; panel phục vụ dàn trang được lưu riêng trong evidence nhiệm vụ 10.

Không chạy lại script xuất bản cũ vào evidence nhiệm vụ 18. Bộ script mới ghi log/manifest/preview vào
[hồ sơ nhiệm vụ 10](../evidence/recovery-report-task10-2026-10-27/README.md).
Các câu nhắc “chưa ghép/xuất” ở bìa/phụ lục được sửa chỉ trong bản ghép; dữ liệu và giới hạn kết luận không thay đổi.
Phần 1–19 nguồn Markdown giữ nguyên revision đã duyệt, mọi khác biệt biên tập bản ghép có dấu vết hash.

## 3. Rà soát thực hiện

- Kiểm tra đủ 19 chương, thứ tự và tiêu đề, số nguồn và thứ tự citation, liên kết nguồn cục bộ và schema bảng.
- Đối chiếu DOCX với danh sách caption, bookmark 19 chương/19 nguồn, link nội bộ và đủ panel hình.
- Cập nhật ba bảng mục lục/danh mục bằng Microsoft Word, kiểm tra chúng chứa các tiêu đề/caption hiện hành.
- Kiểm tra PDF từng trang để phát hiện trang trống và nội dung vượt biên; lưu ảnh xem trước cho bìa, đầu chương, hình và các bảng recovery.
- Đối chiếu hash source, các chương, hình gốc và bằng chứng test/thực nghiệm; không chạy game/test hoặc benchmark mới.

Số trang cuối, danh sách trang xem trước và kết quả kiểm tra máy đọc nằm ở `document-review.json`
trong hồ sơ nhiệm vụ 10. Bản trước recovery được sao lưu tại `before/report/final`;
log/manifest/evidence lịch sử không bị ghi đè.

## 4. Nhóm cần làm trước khi nộp

Điền số nhóm, thông tin bìa và họ tên/MSSV; xác nhận đóng góp cá nhân với minh chứng thật.
Nếu muốn mở rộng claim sang GUI/LAN hoặc độ trễ recovery, cần chạy và lưu bằng chứng riêng;
không đổi các mục “chưa nghiệm thu/chưa đo” thành kết quả đã có.
Sau khi chỉnh bằng Word/Google Docs, cập nhật lại trường mục lục/danh mục/số trang và kiểm tra PDF mới.
Thực hiện Compilatio và các bước đóng gói/nộp theo Submission.md/Instruction.md.
Đợt này chỉ tạo báo cáo và kiểm tra bản xuất, không nộp bài hoặc push GitHub.
