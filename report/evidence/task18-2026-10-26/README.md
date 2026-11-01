# Nhiệm vụ 18 — Ghép, biên tập và xuất báo cáo

Ngày tổng hợp: **26/10/2026**. Phạm vi là tài liệu và công cụ xuất báo cáo; không sửa production code, test, POM hoặc kết quả đo gốc.

## File bàn giao

- [DOCX đủ 19 phần](../../final/NhomXX_BombItMultiplayer_Report.docx).
- [PDF xem trước cùng bản xuất](../../final/NhomXX_BombItMultiplayer_Report.pdf).
- [Markdown đã ghép và biên tập](../../final/BAO_CAO_DA_GHEP.md).
- [Danh sách nhóm cần xác nhận](../../final/CAN_XAC_NHAN_TRUOC_KHI_NOP.md), để riêng với báo cáo.

DOCX hiện có **131 trang, 19 chương, 12 hình, 76 chú thích bảng đánh số và 14 tài liệu tham khảo**. Có 78 bảng vật lý khi tính thêm hai bảng thông tin ở bìa. Mục lục chính, danh mục hình và danh mục bảng là ba trường TOC của Word đã được cập nhật và lưu kết quả; footer dùng PAGE/NUMPAGES.

## Ghép và biên tập

Thứ tự nội dung lấy từ `report/report-manifest.json`. Các file chương gốc được giữ nguyên hash sau nhiệm vụ 17. Bản xuất chuyển lời dẫn theo từng đợt viết thành văn báo cáo, thống nhất thuật ngữ và giữ ranh giới giữa kết quả đã đo, minh họa và việc chưa có bằng chứng. Các thay đổi biên tập được ghi ở [assembly-manifest.json](assembly-manifest.json).

Giữ số citation hiện hành theo `final_number`, 14 bookmark tài liệu tham khảo và liên kết citation. Số bảng/hình theo chương được giữ nhất quán giữa chú thích và danh mục. Liên kết source/log/CSV là tài liệu kiểm chứng bổ sung; nội dung và hình chính đã nằm trong DOCX.

Dàn trang A4, thân bài Times New Roman 12, giãn dòng 1,15; bảng điều chỉnh theo số cột, lặp hàng tiêu đề, hạn chế tách hàng qua trang. Chú thích hình/bảng có style riêng. Thông tin trường/lớp/giảng viên/nhóm/họ tên đầy đủ/MSSV còn thiếu được đánh dấu rõ, không suy đoán từ tên gọi trong phân công.

## Sơ đồ và công cụ

- [render_report_diagrams.py](../../experiments/render_report_diagrams.py): render chín sơ đồ Mermaid bằng Chrome headless và Mermaid 11 cục bộ; không gửi nội dung báo cáo lên dịch vụ render. PNG/SVG nằm trong `report/figures/rendered/`.
- Flowchart ngang được bố trí dọc để đọc trên A4. Actor ID `LOOP` đổi thành `GameThread` để tránh từ khóa Mermaid; nhãn hiển thị được giữ. Dấu chấm phẩy trong nhãn sequence đổi thành dấu phẩy. Sơ đồ thread/queue dài được chia hai panel A/B trong cùng hình; bản liên tục được giữ để đối chiếu. [diagram-manifest.json](diagram-manifest.json) ghi nguồn/kết quả.
- [build_final_docx.py](../../experiments/build_final_docx.py): ghép Markdown, hình, bảng, hyperlink, bookmark và trường Word.
- [paginate_report.ps1](../../experiments/paginate_report.ps1): mở Word ẩn bằng COM, cập nhật mục lục/trường, phân trang, lưu DOCX và xuất PDF. Chỉ đóng phiên Word do script tạo. [word-pagination.json](word-pagination.json) lưu số trang và nội dung TOC đã cập nhật.
- [review_final_report.py](../../experiments/review_final_report.py): kiểm tra OOXML, hình/bảng/bookmark/trường, đọc PDF và tạo ảnh xem trước. [document-review.json](document-review.json) lưu kết quả.

Thư viện Python phục vụ xuất/kiểm tra được cài riêng trong `target/report-docx-deps`; không sửa dependency ứng dụng. Mermaid tải về `target/report-render-assets/`. Cần các công cụ tương ứng khi tái xuất; không cần chúng để mở DOCX đã tạo.

## Kiểm tra bản xuất

- OOXML/ZIP đọc được, đủ Heading 1 từ 1 đến 19, 12 hình nhúng, 76 chú thích bảng, 14 bookmark nguồn và ba trường TOC có nội dung đã cập nhật.
- DOCX và PDF cùng 131 trang; các trang bắt đầu chương khớp với mục lục Word.
- Duyệt tự động toàn bộ PDF: không có trang trắng hoặc text vượt vùng an toàn đã đặt trong script. Không thấy thông báo lỗi field/bookmark của Word.
- Tạo ảnh cho 28 trang mẫu; xem các trang đại diện cho bìa, mục lục, danh mục, chương, sơ đồ và bảng/biểu đồ kết quả. Kiểm tra riêng bảng latency trang 105 và sơ đồ hai panel trang 46: đọc được, nằm trong lề. Đây là kiểm tra dàn trang, không thay nghiệm thu GUI/gameplay.
- Giữ nguyên bằng chứng task 12–14. Không chạy lại test/benchmark và không thêm kết quả thực nghiệm ở nhiệm vụ này. Kiểm tra hash nguồn và dữ liệu được ghi trong `final-artifacts.json`.

## Tái xuất

Chạy từ thư mục gốc dự án, với Python và Microsoft Word/Chrome phù hợp:

```powershell
python report/experiments/render_report_diagrams.py
python report/experiments/build_final_docx.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File report/experiments/paginate_report.ps1
python report/experiments/review_final_report.py
```

Chỉ cần render lại khi thay sơ đồ. Build lại DOCX sẽ ghi đè chỉnh sửa trực tiếp trong Word; nếu nhóm đã điền bìa, hãy lưu bản riêng hoặc cập nhật nội dung nguồn/công cụ trước khi tái xuất. Khi chỉ sửa bản DOCX, cập nhật toàn bộ mục lục/danh mục và số trang rồi kiểm tra lại PDF; số trang/hash hiện tại sẽ không còn đại diện cho bản đã sửa.

## Trạng thái trước nộp

Đã hoàn thành đầu ra nhiệm vụ 18. Còn phần xác nhận thuộc nhóm: số nhóm/tên file, thông tin bìa/MSSV, đóng góp thực tế và rà soát claim theo module. GUI/LAN/soak, metadata CPU/RAM đầy đủ, Compilatio và việc nộp bài chưa được thực hiện trong nhiệm vụ này. Các giới hạn đo được giữ trong báo cáo; không bắt nhóm chạy thêm để công bố phạm vi hiện tại.

Yêu cầu nộp được đối chiếu từ các file thầy cung cấp trong `phancong/`; danh sách xác nhận ghi rõ tên file, deadline và ngưỡng tương đồng. Chưa thể ghi nhận đạt Compilatio khi chưa có kết quả thật.
